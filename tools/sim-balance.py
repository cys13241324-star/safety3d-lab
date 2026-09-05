# -*- coding: utf-8 -*-
"""
「안전관리자의 하루」 (reigns.html) 밸런스 몬테카를로 시뮬레이터.

reigns.html 원문을 직접 파싱해 DECK / FALLOUT / FLAVOR 의 d(효과)·ok·tag·req 를 읽고,
next() / choose() / buildReport() / finish() 의 규칙을 그대로 옮겨 구현한다.
카드 수치는 손으로 옮겨 적지 않고 파일에서 읽는다.

실행:
  python sim-balance.py current  20000   # ① 현행 실측
  python sim-balance.py grid      2000   # ② 파라미터 탐색
  python sim-balance.py new      20000   # ③ 재설계 검증
  python sim-balance.py exploit  20000   # ⑥ 무학습 공략 경로 점검
  python sim-balance.py emit                # 재설계 수치를 카드별로 출력
"""
import io, os, re, sys, math, random
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from collections import Counter, defaultdict

HTML = r"C:\Users\co132\Desktop\project\산업안전기사-github\safety3d-lab\reigns.html"

# ---------------------------------------------------------------- 파싱
def section(src, name):
    i = src.index("var %s = [" % name)
    j = src.index("\n  ];", i)
    return src[i:j]

def split_cards(sec):
    idxs = [m.start() for m in re.finditer(r"\n  \{", sec)]
    return [sec[s:(idxs[n+1] if n+1 < len(idxs) else len(sec))] for n, s in enumerate(idxs)]

def opt(block, which):
    i = block.index("\n   %s:{" % which)
    seg = block[i:]
    nx = seg.find("\n   b:{", 1)
    if which == "a" and nx > 0:
        seg = seg[:nx]
    d = [int(x) for x in re.search(r"d:\[([-0-9,\s]+)\]", seg).group(1).split(",")]
    ok = int(re.search(r"ok:(\d)", seg).group(1))
    tg = re.search(r"tag:'([A-Za-z]+)'", seg)
    cl = re.search(r"clear:(\d)", seg)
    return {"d": d, "ok": ok, "tag": tg.group(1) if tg else None,
            "clear": int(cl.group(1)) if cl else 0}

def parse():
    with io.open(HTML, encoding="utf-8") as f:
        src = f.read()
    deck, fallout, flavor = [], [], []
    for b in split_cards(section(src, "DECK")):
        deck.append({"k": re.search(r"k:'([A-Za-z]+)'", b).group(1),
                     "s": re.search(r"s:'([^']+)'", b).group(1),
                     "law": True, "a": opt(b, "a"), "b": opt(b, "b")})
    for b in split_cards(section(src, "FALLOUT")):
        fallout.append({"req": re.search(r"req:'([A-Za-z]+)'", b).group(1),
                        "k": None, "s": "사고", "law": True,
                        "a": opt(b, "a"), "b": opt(b, "b")})
    for b in split_cards(section(src, "FLAVOR")):
        flavor.append({"k": None, "s": "현장", "law": False,
                       "a": opt(b, "a"), "b": opt(b, "b")})
    return deck, fallout, flavor

DECK, FALLOUT, FLAVOR = parse()
FO_BY_REQ = {}
for c in FALLOUT:
    FO_BY_REQ.setdefault(c["req"], c)
COVERED = set(FO_BY_REQ.keys())
SEV = dict((c["k"], -c["b"]["d"][0]) for c in DECK)     # 위반 시 안전 손실

# ---------------------------------------------------------------- 규칙
class Rules(object):
    def __init__(self, **kw):
        self.start        = [62, 58, 60, 60]
        self.days         = 60
        self.report_every = 5
        self.ripe_days    = 3
        self.acc_p        = 0.45
        self.flavor_p     = 0.16
        self.drift        = [0, 0, 0, 0]   # 하루 넘길 때 자동 증감
        self.generic_fo   = False          # 전용 사고카드 없는 태그도 사고가 터지는가
        self.sa           = 1.0            # 준수: 안전 이득 배율
        self.cc           = 1.0            # 준수: 공정·예산 비용 배율
        self.ga           = 1.0            # 준수: 감독 이득 배율
        self.vs           = 1.0            # 위반: 안전 손실 배율
        self.vg           = 1.0            # 위반: 공정·예산 이득 배율
        self.vga          = 1.0            # 위반: 감독 손실 배율
        self.rep_a        = {"d": [6, -5, -6, 9], "ok": 1, "tag": None, "clear": 2}
        self.rep_b        = {"d": [-5, 8, 5, -7], "ok": 0, "tag": None, "clear": 0}
        # 커밋 b9250ee: 씨앗은 무조건 소비되고, 전용 사고카드가 없으면 genericFallout 이 생성된다.
        # insp(50%)에 따라 감독 항이 갈린다.  b 는 태그를 다시 심어 3일 뒤 재발한다.
        # 100 클램프 처방 비교용
        #  'clamp' 현행 · 'death' 상한 초과도 패배(ReignsAgent식) · 'spill' 초과분 이월
        self.cap_mode     = "clamp"
        self.spill        = {0: 2, 3: 1}   # 안전 초과분→예산, 감독 초과분→공정
        self.spill_ratio  = 1.0
        self.rep_cost_per_seed = 0   # 사실대로 보고할 때 미조치 위험 1건당 추가 예산 비용
        self.consume_seed = False          # False = 결함 버전(전용카드 없으면 씨앗이 남는다)
        self.generic_fo   = False          # True = genericFallout 생성
        self.gfo_a_i      = [7, -7, -8,  7]
        self.gfo_a_n      = [7, -7, -8,  4]
        self.gfo_b_i      = [-13, 3, -2, -12]
        self.gfo_b_n      = [-13, 3, -2,  -8]
        self.__dict__.update(kw)

def rd(x):
    """0에서 멀어지는 쪽 반올림 (효과가 0으로 뭉개지지 않게)."""
    if x == 0: return 0
    v = int(round(abs(x)))
    if v == 0: v = 1
    return v if x > 0 else -v

def scaled(choice, R, kind):
    d = list(choice["d"])
    if kind in ("deck", "flavor"):
        if choice["ok"]:
            d[0] = rd(d[0] * R.sa)
            d[1] = rd(d[1] * R.cc); d[2] = rd(d[2] * R.cc)
            d[3] = rd(d[3] * R.ga)
        else:
            d[0] = rd(d[0] * R.vs)
            d[1] = rd(d[1] * R.vg); d[2] = rd(d[2] * R.vg)
            d[3] = rd(d[3] * R.vga)
    return d

# ---------------------------------------------------------------- 정책
# 재설계안에서는 준수 선택지의 좌우 위치를 무작위화하므로,
# "규정을 안다"는 것은 곧 "준수 선택지를 알아본다"는 뜻이 된다.
# 지식 수준을 적중확률 p 로 모형화한다. p=1 완전 숙지 / p=0.5 전혀 모름(찍기) / p=0 항상 위반.

def p_always_a(card, g, R):  return "a"
def p_always_b(card, g, R):  return "b"
def p_random(card, g, R):    return "a" if random.random() < .5 else "b"

def p_greedy(card, g, R):
    best, bk = None, "a"
    for k in ("a", "b"):
        d = scaled(card[k], R, card["kind"])
        nx = [max(0, min(100, g[i] + d[i])) for i in range(4)]
        key = (min(nx), sum(nx))
        if best is None or key > best:
            best, bk = key, k
    return bk

def make_know(p, careful=False):
    """적중확률 p 로 준수 선택지를 알아보는 사람.
       careful=True 면 (ㄱ)사고 카드는 항상 정석 대응하고
                      (ㄴ)공정·예산이 바닥나면 경미한(안전손실 작은) 규정 하나를 의도적으로 미룬다."""
    def f(card, g, R):
        if card["kind"] == "report":
            return "a"                       # 본사 보고는 사실대로 (지식 문제 아님)
        if careful and card["kind"] == "fo":
            return "a"                       # 사고 대응은 상식
        if careful and card["kind"] == "deck":
            if min(g[1], g[2]) <= 16 and SEV.get(card["k"], 99) <= 8 and g[0] > 30:
                return "b"                   # 알면서 미루는 계산된 예외
        return "a" if random.random() < p else "b"
    return f

def p_bal(card, g, R):
    """코디네이터 하네스의 BAL 정책: 가장 낮은 게이지가 안전·감독이면 좌(준수),
       공정·예산이면 우(위반). 규정 지식이 전혀 필요 없는 게이지 휴리스틱."""
    lo = min(range(4), key=lambda i: g[i])
    return "a" if lo in (0, 3) else "b"

def p_adaptive(card, g, R):
    """규정은 알지만 위험도는 안 따짐: 공정·예산이 궁하면 카드 가리지 않고 위반."""
    if card["kind"] == "report": return "a"
    if min(g[1], g[2]) <= 32: return "b"
    return "a" if random.random() < 0.90 else "b"

def p_informed(card, g, R):
    return make_know(0.90, careful=True)(card, g, R)

POLICIES = [("ⓐ 항상 준수", p_always_a),
            ("ⓑ 항상 위반", p_always_b),
            ("ⓒ 무작위", p_random),
            ("ⓓ 탐욕(오라클)", p_greedy),
            ("ⓔ 적응형(규정만 앎)", p_adaptive),
            ("ⓕ BAL 약한쪽 살리기", p_bal)]

PSWEEP = [("p=1.00 완전숙지", make_know(1.00, True)),
          ("p=0.95 거의숙지", make_know(0.95, True)),
          ("p=0.90 신중한 유식자", make_know(0.90, True)),
          ("p=0.85 어중간", make_know(0.85, True)),
          ("p=0.80 절반숙지", make_know(0.80, True)),
          ("p=0.70 얕은지식", make_know(0.70, True)),
          ("p=0.50 무작위(무학습)", make_know(0.50, True)),
          ("p=0.30 감으로", make_know(0.30, True)),
          ("p=0.00 항상위반", make_know(0.00, True))]

# ---------------------------------------------------------------- 엔진
def run_one(policy, R, track=None):
    g = list(R.start); day = 1
    used, fl_used, seeds = set(), set(), []
    okc = viol = comply = acc = 0
    last_report = 0
    while True:
        if day > R.days:
            return dict(days=R.days, win=True, cause=None, g=g, ok=okc,
                        viol=viol, comply=comply, acc=acc, seeds=len(seeds))
        if track is not None:
            track[day].append(list(g))

        card = None; kind = None
        if day % R.report_every == 0 and last_report != day:
            last_report = day
            card = {"kind": "report", "k": None, "s": "보고", "law": False,
                    "a": R.rep_a, "b": R.rep_b}; kind = "report"
        if card is None:
            ripe = [s for s in seeds if day - s[1] >= R.ripe_days]
            if ripe and random.random() < R.acc_p:
                s = random.choice(ripe)
                if R.consume_seed:
                    seeds.remove(s)            # 커밋 b9250ee: 씨앗은 무조건 소비
                if s[0] in FO_BY_REQ:
                    c = FO_BY_REQ[s[0]]
                    card = {"kind": "fo", "k": s[0], "s": "사고", "law": True,
                            "a": c["a"], "b": c["b"]}
                    if not R.consume_seed: seeds.remove(s)
                elif R.generic_fo:
                    insp = random.random() < 0.5
                    card = {"kind": "fo", "k": s[0], "s": "사고", "law": True,
                            "a": {"d": (R.gfo_a_i if insp else R.gfo_a_n),
                                  "ok": 1, "tag": None, "clear": 0},
                            "b": {"d": (R.gfo_b_i if insp else R.gfo_b_n),
                                  "ok": 0, "tag": s[0], "clear": 0}}   # b 는 태그 재삽입
                    if not R.consume_seed: seeds.remove(s)
                if card is not None: kind = "fo"; acc += 1
        if card is None and random.random() < R.flavor_p:
            avail = [i for i in range(len(FLAVOR)) if i not in fl_used]
            if avail:
                i = random.choice(avail); fl_used.add(i)
                c = FLAVOR[i]
                card = {"kind": "flavor", "k": None, "s": "현장", "law": False,
                        "a": c["a"], "b": c["b"]}; kind = "flavor"
        if card is None:
            pool = [i for i in range(len(DECK)) if i not in used]
            if not pool: used = set(); pool = list(range(len(DECK)))
            i = random.choice(pool); used.add(i)
            c = DECK[i]
            card = {"kind": "deck", "k": c["k"], "s": c["s"], "law": True,
                    "a": c["a"], "b": c["b"]}; kind = "deck"

        ch = card[policy(card, g, R)]
        d = scaled(ch, R, kind)
        over = -1
        for i in range(4):
            v = g[i] + d[i]
            if v > 100:
                if R.cap_mode == "death" and over < 0: over = i
                elif R.cap_mode == "spill" and i in R.spill:
                    j = R.spill[i]
                    g[j] = min(100, g[j] + int(round((v - 100) * R.spill_ratio)))
                v = 100
            g[i] = max(0, v)
        if over >= 0:
            return dict(days=day, win=False, cause=4 + over, g=g, ok=okc,
                        viol=viol, comply=comply, acc=acc, seeds=len(seeds))
        if ch["ok"]: okc += 1
        if card["law"]:
            if ch["ok"]: comply += 1
            else: viol += 1
        if ch["tag"]: seeds.append((ch["tag"], day))
        if kind == "report" and ch["ok"] and R.rep_cost_per_seed and seeds:
            g[2] = max(0, g[2] - R.rep_cost_per_seed * len(seeds))
        if kind == "report" and ch["clear"]: seeds = seeds[ch["clear"]:]

        dead = next((i for i, v in enumerate(g) if v <= 0), -1)
        if dead >= 0:
            return dict(days=day, win=False, cause=dead, g=g, ok=okc,
                        viol=viol, comply=comply, acc=acc, seeds=len(seeds))
        day += 1
        if any(R.drift):
            for i in range(4):
                g[i] = max(0, min(100, g[i] + R.drift[i]))
            dead = next((i for i, v in enumerate(g) if v <= 0), -1)
            if dead >= 0:
                return dict(days=day, win=False, cause=dead, g=g, ok=okc,
                            viol=viol, comply=comply, acc=acc, seeds=len(seeds))

# ---------------------------------------------------------------- 집계
def pctl(v, q):
    v = sorted(v); k = (len(v) - 1) * q / 100.0
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (k - lo)

def batch(name, policy, R, N, seed=12345, track=False):
    random.seed(seed)
    tr = defaultdict(list) if track else None
    days, wins, cause = [], 0, Counter()
    accs, viols, comps = [], [], []
    for _ in range(N):
        r = run_one(policy, R, tr)
        days.append(r["days"]); wins += r["win"]
        if not r["win"]: cause[r["cause"]] += 1
        accs.append(r["acc"]); viols.append(r["viol"]); comps.append(r["comply"])
    dead = max(1, N - wins)
    out = dict(name=name, mean=sum(days)/float(N), med=pctl(days, 50),
               p10=pctl(days, 10), p90=pctl(days, 90), win=100.0*wins/N,
               cause=[100.0*cause[i]/dead for i in range(8)],
               acc=sum(accs)/float(N), viol=sum(viols)/float(N),
               comp=sum(comps)/float(N))
    if tr:
        out["traj"] = dict((d, [sum(x[i] for x in v)/len(v) for i in range(4)])
                           for d, v in tr.items())
    ds = sorted(days)
    out["curve"] = dict((d, 100.0 * sum(1 for x in ds if x >= d) / N)
                        for d in (5, 10, 15, 20, 25, 30, 40, 50, 60))
    return out

def curve_table(rows, title):
    ks = (5, 10, 15, 20, 25, 30, 40, 50, 60)
    print("\n-- %s · 생존 곡선 P(생존일수 ≥ D) --" % title)
    print("%-26s %s" % ("정책", " ".join("%6s" % ("D%d" % d) for d in ks)))
    for r in rows:
        print("%-26s %s" % (r["name"], " ".join("%5.1f%%" % r["curve"][d] for d in ks)))

def table(rows, title):
    print("\n== %s ==" % title)
    print("%-24s %7s %6s %5s %5s %9s | %s" %
          ("정책", "평균일", "중앙", "p10", "p90", "60일도달", "사망원인% 안전/공정/예산/감독"))
    print("-" * 104)
    for r in rows:
        print("%-24s %7.2f %6.1f %5.1f %5.1f %8.2f%% | %5.1f %5.1f %5.1f %5.1f" %
              (r["name"], r["mean"], r["med"], r["p10"], r["p90"], r["win"],
               r["cause"][0], r["cause"][1], r["cause"][2], r["cause"][3]))

def show_traj(r):
    print("\n-- 게이지 평균 궤적 (%s · 그 날까지 살아남은 판만) --" % r["name"])
    print("%5s %7s %7s %7s %7s" % ("일차", "안전", "공정", "예산", "감독"))
    for d in [1, 5, 10, 15, 20, 25, 30, 40, 50, 60]:
        if d in r.get("traj", {}):
            t = r["traj"][d]
            print("%5d %7.1f %7.1f %7.1f %7.1f" % (d, t[0], t[1], t[2], t[3]))

# ---------------------------------------------------------------- 규칙 정의
CUR_OLD = Rules()                                   # 결함 버전 (커밋 b9250ee 이전)
CUR     = Rules(consume_seed=True, generic_fo=True) # 현행 수정판 (커밋 b9250ee)

NEW = Rules(
    # --- 재설계: 현행 카드 배열과 시작값은 그대로 두고 규칙 세 가지만 바꾼다 ---
    start        = [62, 58, 60, 60],   # 변경 없음
    days         = 60,                 # 변경 없음
    report_every = 5,                  # 변경 없음
    ripe_days    = 3, acc_p = 0.45,    # 변경 없음
    flavor_p     = 0.16,               # 변경 없음
    consume_seed = True, generic_fo = True,   # 커밋 b9250ee (이미 적용됨)
    # (1) 100 클램프 폐지 → 초과분 이월: 안전 초과분은 예산으로, 감독 초과분은 공정으로
    cap_mode     = "spill",
    spill        = {0: 2, 3: 1},
    spill_ratio  = 1.0,
    # (2) 하루가 지날 때 공정·예산 자연 감소
    drift        = [0, -1, -1, 0],
    # (3) 준수 선택의 공정·예산 비용 ×1.22 (반올림)
    cc           = 1.22,
)

# ---------------------------------------------------------------- 모드
def facts():
    print("카드 수: DECK %d · FALLOUT %d · FLAVOR %d" % (len(DECK), len(FALLOUT), len(FLAVOR)))
    print("과목 분포: %s" % dict(Counter(c["s"] for c in DECK)))
    print("전용 사고카드 있는 태그 %d개: %s" % (len(COVERED), ", ".join(sorted(COVERED))))
    nc = sorted(set(SEV) - COVERED)
    print("전용 사고카드 없는 태그 %d개(현행에선 씨앗이 영영 안 터짐): %s" % (len(nc), ", ".join(nc)))
    for lab, key in (("준수(a)", "a"), ("위반(b)", "b")):
        print("%s 효과 평균 %s" % (lab, [round(sum(c[key]["d"][i] for c in DECK)/len(DECK), 2) for i in range(4)]))
    sv = sorted(SEV.items(), key=lambda x: x[1])
    print("위반 시 안전손실 최소 5: %s" % sv[:5])
    print("위반 시 안전손실 최대 5: %s" % sv[-5:])

def mode_current(N):
    facts()
    TRK = ("ⓐ 항상 준수", "ⓓ 탐욕(오라클)", "ⓒ 무작위")
    old = [batch(n, p, CUR_OLD, N, track=(n in TRK)) for n, p in POLICIES]
    new = [batch(n, p, CUR,     N, track=(n in TRK)) for n, p in POLICIES]
    table(old, "①-A 결함 버전 (커밋 b9250ee 이전 · 씨앗 30종이 안 터짐) N=%d/정책" % N)
    table(new, "①-B 현행 수정판 (커밋 b9250ee · 씨앗 무조건 소비 + genericFallout) N=%d/정책" % N)
    print("\n-- 수정 전후 60일 도달률 / 평균 생존일 대비 --")
    print("%-24s %14s %14s %14s %14s" % ("정책", "도달률(결함)", "도달률(수정)", "평균일(결함)", "평균일(수정)"))
    for a, b in zip(old, new):
        print("%-24s %13.2f%% %13.2f%% %14.2f %14.2f" % (a["name"], a["win"], b["win"], a["mean"], b["mean"]))
    curve_table(old, "①-A 결함 버전")
    curve_table(new, "①-B 현행 수정판")
    for r in new:
        if "traj" in r: show_traj(r)
    print("\n-- 현행 수정판 · 판당 사고 / 기준미달 / 기준충족 --")
    for a, b in zip(old, new):
        print("%-24s 사고 %5.2f→%5.2f  미달 %5.2f→%5.2f  충족 %5.2f→%5.2f" %
              (b["name"], a["acc"], b["acc"], a["viol"], b["viol"], a["comp"], b["comp"]))

def mode_new(N):
    rows = [batch(n + "*", p, NEW, N, track=(n in ("ⓐ 항상 준수", "ⓒ 무작위")))
            for n, p in POLICIES]
    table(rows, "③ 재설계 규칙 검증 실측 (N=%d/정책)" % N)
    for r in rows:
        if "traj" in r: show_traj(r)
    print("\n-- 판당 사고 발생 수 / 기준미달 수 / 기준충족 수 --")
    for r in rows:
        print("%-24s 사고 %5.2f  미달 %5.2f  충족 %5.2f" % (r["name"], r["acc"], r["viol"], r["comp"]))

def mode_grid(N):
    P1, P9, P5, P0 = (make_know(1.0, True), make_know(0.90, True),
                      make_know(0.50, True), make_know(0.0, True))
    best = []
    for sa in (0.12, 0.22):
        for vs in (1.0, 1.2, 1.4):
            for d0 in (0, -1, -2):
                for s0 in (52, 58, 64, 70):
                    for d12 in (4,):
                        s12 = 54
                        R = Rules(start=[s0, s12, s12 + 2, 62],
                                  drift=[d0, d12, d12, 0],
                                  sa=sa, cc=1.0, ga=0.30, vs=vs, vg=1.0, vga=1.0,
                                  consume_seed=True, generic_fo=True, acc_p=0.55, ripe_days=3,
                                  rep_a={"d": [1, -4, -5, 4], "ok": 1, "tag": None, "clear": 2},
                                  rep_b={"d": [-6, 7, 6, -9], "ok": 0, "tag": None, "clear": 0},
                                  gfo_a_i=[3, -7, -8, 7], gfo_a_n=[3, -7, -8, 4],
                                  gfo_b_i=[-13, 3, -2, -12], gfo_b_n=[-13, 3, -2, -8])
                        w1 = batch("1", P1, R, N, seed=7)["win"]
                        w9 = batch("9", P9, R, N, seed=7)["win"]
                        w5 = batch("5", P5, R, N, seed=7)["win"]
                        w0 = batch("0", P0, R, N, seed=7)["win"]
                        score = abs(w9 - 62) + max(0, w5 - 10) * 3 + max(0, w0 - 5) * 3 + max(0, 88 - w1) * 0.8
                        best.append((score, sa, vs, d0, s0, d12, w1, w9, w5, w0))
    best.sort(key=lambda x: x[0])
    print("\n== ② 파라미터 탐색 (N=%d/정책, 상위 18) ==" % N)
    print("%6s %5s %5s %4s %4s %4s | %8s %8s %8s %8s" %
          ("점수", "sa", "vs", "d0", "s0", "d12", "p=1.0", "p=0.90", "p=0.50", "p=0.00"))
    for r in best[:18]:
        print("%6.1f %5.2f %5.2f %4d %4d %4d | %7.1f%% %7.1f%% %7.1f%% %7.1f%%" % r)

def mode_psweep(N):
    rows = [batch(n, f, NEW, N, track=(n.startswith("p=0.90") or n.startswith("p=1.00")))
            for n, f in PSWEEP]
    table(rows, "③-2 지식 수준(적중확률 p)별 실측 · 재설계 규칙 (N=%d)" % N)
    for r in rows:
        if "traj" in r: show_traj(r)
    print("\n-- 판당 사고 / 기준미달 / 기준충족 --")
    for r in rows:
        print("%-24s 사고 %5.2f  미달 %5.2f  충족 %5.2f" % (r["name"], r["acc"], r["viol"], r["comp"]))

def mode_psweep_cur(N):
    rows = [batch(n, f, CUR, N) for n, f in PSWEEP]
    table(rows, "①-2 지식 수준(적중확률 p)별 실측 · 현행 규칙 (N=%d)" % N)

# ---- ⑥ 무학습 공략 경로 ----
def p_left(card, g, R):  return "a"      # 사이드 고정 전: 왼쪽 = 항상 준수
def make_alt(k):
    st = {"n": 0}
    def f(card, g, R):
        st["n"] += 1
        return "a" if (st["n"] % k) else "b"
    return f
def p_minmax_noknow(card, g, R):
    """게이지 숫자만 보고 규정은 모름: 가장 낮은 게이지를 살릴 확률이 높은 쪽을 '찍는' 사람.
       규정 지식이 없으니 어느 쪽이 준수인지 모르고, 50%로 잘못 고른다."""
    k = p_greedy(card, g, R)
    if random.random() < 0.5:
        k = "a" if k == "b" else "b"
    return k

def mode_exploit(N):
    pols = [("좌측 고정(=현행 항상준수)", p_left),
            ("2장에 1장 위반", make_alt(2)),
            ("3장에 1장 위반", make_alt(3)),
            ("4장에 1장 위반", make_alt(4)),
            ("5장에 1장 위반", make_alt(5)),
            ("6장에 1장 위반", make_alt(6)),
            ("8장에 1장 위반", make_alt(8)),
            ("게이지만 보고 찍기", p_minmax_noknow)]
    for lab, R in (("현행", CUR), ("재설계", NEW)):
        rows = [batch(n, p, R, N) for n, p in pols]
        table(rows, "⑥ 무학습 반복 공략 — %s 규칙 (N=%d)" % (lab, N))

def mode_emit():
    print("재설계 배율을 카드별 d 값으로 환산 (reigns.html DECK 에 그대로 대입)")
    print("%-11s %-16s %-24s %-24s" % ("k", "과목", "a.d (준수)", "b.d (위반)"))
    for c in DECK:
        a = scaled(c["a"], NEW, "deck"); b = scaled(c["b"], NEW, "deck")
        print("%-11s %-16s %-24s %-24s" % (c["k"], c["s"], a, b))
    print("\nFLAVOR")
    for i, c in enumerate(FLAVOR):
        print("  #%d a=%s b=%s" % (i, scaled(c["a"], NEW, "flavor"), scaled(c["b"], NEW, "flavor")))
    print("\nFALLOUT (그대로 유지) · 범용 사고카드 a=%s b=%s" % (NEW.gfo_a["d"], NEW.gfo_b["d"]))
    print("보고 카드 a=%s b=%s" % (NEW.rep_a["d"], NEW.rep_b["d"]))


# ================================================================
# ④ 카드 단위 부호 설계 (코디네이터 요청)
#   현행: 준수 = 안전↑감독↑ / 공정↓예산↓  가 55장 전부 동일.
#   재설계: 카드를 네 부류로 나눠 부호 패턴 자체를 다르게 준다.
#     N 고전형   — 현행 그대로. 안전을 사고 일정·돈을 낸다.
#     P 공정회수형 — 제대로 하면 재작업·수정지시가 사라져 "공정이 오른다".
#                  어기면 되레 재작업으로 공정이 깎인다.
#     B 예산회수형 — 사전 점검·교체가 고장·불량·재시공 비용을 막아 "예산이 오른다".
#                  어기면 고장 수리비로 예산이 크게 깎인다.
#     F 제재형    — 어기면 과태료·작업중지·시정명령으로 예산과 감독이 함께 깎인다.
#                  (준수는 현행과 같은 비용)
# ================================================================
CLASS = {
  # ---- P형 「일이 빨라진다」 : 준수하면 공정 +, 어기면 재작업으로 공정 -
  #      가설구조물·발판·통로·조도·작업공간·인간공학. 규격대로 서면 작업이 붙고,
  #      안 서면 뜯고 다시 하거나 사람이 비켜 다니느라 일정이 밀린다.
  "net": "P", "fall": "P", "rail": "P", "ladder": "P", "plank": "P",
  "scaffold": "P", "stairs": "P", "trench": "P", "shore": "P", "ramp": "P",
  "horse": "P", "mobscaf": "P", "frame": "P", "pile": "P", "gangway": "P",
  "lux": "P", "vdt": "P", "noise": "P", "carry": "P", "panelspace": "P",
  # ---- B형 「돈이 굳는다」 : 준수하면 예산 +, 어기면 과태료·작업중지·수리비로 예산 --
  #      기계 검사·교체·규격, 전기·화학 이격·환기·방폭. 미리 하면 고장과 제재를 산다.
  "roller": "B", "grinder": "B", "press": "B", "sawblade": "B", "forklift": "B",
  "robot": "B", "boiler": "B", "rotor": "B", "wirerope": "B",
  "elcb": "B", "welder": "B", "approach": "B", "powerline": "B", "exgap": "B",
  "confined": "B", "chemdist": "B", "gasweld": "B", "staticflow": "B",
  "weather": "B", "caisson": "B",
}

class Sign(object):
    """부호 설계 파라미터.  P형/B형 각각 준수·위반의 네 항을 명시적으로 잡는다."""
    def __init__(self, **kw):
        self.pay   = 0.60   # 준수의 안전·감독 이득 배율 (돈·일정을 벌면 안전 이득은 줄인다)
        self.pP    = 4      # P형 준수: 공정 +pP
        self.pB    = 4      # B형 준수: 예산 +pB
        self.pC    = 3      # 준수의 반대쪽 비용 (P형은 예산 -pC, B형은 공정 -pC)
        self.pP2   = 3      # P형 위반: 공정 -pP2 (재작업)
        self.pB2   = 8      # B형 위반: 예산 -pB2 (과태료·작업중지·수리)
        self.pV    = 4      # 위반이 벌어 주는 반대쪽 (P형은 예산 +pV, B형은 공정 +pV)
        self.pFg   = 0      # B형 위반: 감독 추가 감점
        self.__dict__.update(kw)

def apply_sign(deck, S):
    out = []
    for c in deck:
        o_a = c["a"]["d"]; o_b = c["b"]["d"]; cl = CLASS.get(c["k"], "P")
        sa = rd(o_a[0] * S.pay); ga = rd(o_a[3] * S.pay)
        vs = o_b[0]; vg = o_b[3]
        if cl == "P":
            a = [sa,  S.pP, -S.pC, ga]
            b = [vs, -S.pP2, S.pV, vg]
        else:
            a = [sa, -S.pC,  S.pB, ga]
            b = [vs,  S.pV, -S.pB2, vg - S.pFg]
        out.append({"k": c["k"], "s": c["s"], "law": True, "cls": cl,
                    "a": {"d": a, "ok": 1, "tag": None, "clear": 0},
                    "b": {"d": b, "ok": 0, "tag": c["b"]["tag"], "clear": 0}})
    return out

def use_deck(d):
    global DECK
    DECK = d

def mode_sign(N):
    orig = DECK[:]
    print("== 4 카드 단위 부호 설계 · 부류별 장수 %s ==" %
          dict(Counter(CLASS.get(c["k"], "P") for c in orig)))
    POL = [("규정100%", p_always_a), ("규정95%", make_know(.95, True)),
           ("규정90%", make_know(.90, True)), ("규정85%", make_know(.85, True)),
           ("규정70%", make_know(.70, True)), ("규정55%", make_know(.55, True)),
           ("게이지만", p_bal), ("무작위", p_random), ("항상위반", p_always_b)]
    hdr = "%-32s %s" % ("설정", " ".join("%7s" % n for n, _ in POL))
    print(hdr)
    base = dict(consume_seed=True, generic_fo=True)
    def run(tag, S, R):
        use_deck(apply_sign(orig, S))
        ws = [batch(n, f, R, N, seed=2024)["win"] for n, f in POL]
        use_deck(orig)
        print("%-32s %s" % (tag, " ".join("%6.1f%%" % w for w in ws)))
        return ws
    REPS = {
      "보고 현행 [6,-5,-6,9]":  ({"d": [6, -5, -6, 9], "ok": 1, "tag": None, "clear": 2},
                              {"d": [-5, 8, 5, -7], "ok": 0, "tag": None, "clear": 0}),
      "보고 조치예산 [4,-4,4,8]": ({"d": [4, -4, 4, 8], "ok": 1, "tag": None, "clear": 2},
                              {"d": [-6, 7, -3, -9], "ok": 0, "tag": None, "clear": 0}),
      "보고 조치예산 [4,-2,2,8]": ({"d": [4, -2, 2, 8], "ok": 1, "tag": None, "clear": 2},
                              {"d": [-6, 6, -3, -9], "ok": 0, "tag": None, "clear": 0}),
    }
    for rlab, (ra, rb) in REPS.items():
        print("")
        for pP in (3, 4, 5):
            for pC in (2, 3, 4):
                run("%s pP=%d pC=%d" % (rlab, pP, pC),
                    Sign(pP=pP, pB=pP, pC=pC), Rules(rep_a=ra, rep_b=rb, **base))

def mode_sign2(N):
    orig = DECK[:]
    POL = [("규정100%", p_always_a), ("규정95%", make_know(.95, True)),
           ("규정90%", make_know(.90, True)), ("규정85%", make_know(.85, True)),
           ("규정70%", make_know(.70, True)), ("규정55%", make_know(.55, True)),
           ("게이지만", p_bal), ("무작위", p_random), ("항상위반", p_always_b)]
    print("%-36s %s" % ("설정", " ".join("%7s" % n for n, _ in POL)))
    base = dict(consume_seed=True, generic_fo=True)
    ra = {"d": [6, -5, -6, 9], "ok": 1, "tag": None, "clear": 2}
    rb = {"d": [-5, 8, 5, -7], "ok": 0, "tag": None, "clear": 0}
    for pP in (4, 5):
        for dr in (0, -1):
            for pB2 in (8, 12):
                S = Sign(pP=pP, pB=pP, pC=2, pB2=pB2, pV=4)
                R = Rules(drift=[0, dr, dr, 0], rep_a=ra, rep_b=rb, **base)
                use_deck(apply_sign(orig, S))
                ws = [batch(n, f, R, N, seed=2024)["win"] for n, f in POL]
                use_deck(orig)
                print("%-36s %s" % ("pP=pB=%d pC=2 pB2=%d drift=%d" % (pP, pB2, dr),
                                    " ".join("%6.1f%%" % w for w in ws)))

def mode_final(N):
    """최종안 정밀 측정."""
    orig = DECK[:]
    S = SIGN_FINAL
    R = RULES_FINAL
    use_deck(apply_sign(orig, S))
    POL = [("규정 100%", p_always_a), ("규정 95%", make_know(.95, True)),
           ("규정 90%", make_know(.90, True)), ("규정 85%", make_know(.85, True)),
           ("규정 80%", make_know(.80, True)), ("규정 70%", make_know(.70, True)),
           ("규정 55%", make_know(.55, True)),
           ("게이지만(좌우고정 가정)", p_bal), ("무작위=좌우섞기 후 무지식", p_random),
           ("항상 위반", p_always_b)]
    rows = [batch(n, f, R, N, seed=777, track=(n in ("규정 100%", "규정 90%"))) for n, f in POL]
    table(rows, "③ 최종안 검증 실측 (N=%d/정책)" % N)
    curve_table(rows, "최종안")
    for r in rows:
        if "traj" in r: show_traj(r)
    print("")
    print("-- 판당 사고 / 기준미달 / 기준충족 --")
    for r in rows:
        print("%-26s 사고 %5.2f  미달 %5.2f  충족 %5.2f" % (r["name"], r["acc"], r["viol"], r["comp"]))
    d = DECK
    print("")
    print("-- 최종안 부호 통계 (코디네이터 표와 같은 형식) --")
    for lab, key in (("준수(a)", "a"), ("위반(b)", "b")):
        m = [round(sum(c[key]["d"][i] for c in d) / len(d), 2) for i in range(4)]
        up = [sum(1 for c in d if c[key]["d"][i] > 0) for i in range(4)]
        print("%s 평균 [안전,공정,예산,감독] = %s · 오르는 카드 %s / %d" % (lab, m, up, len(d)))
    use_deck(orig)

def mode_emit2():
    """최종안 카드별 d 값 출력 (reigns.html 에 그대로 대입)."""
    orig = DECK[:]
    nd = apply_sign(orig, SIGN_FINAL)
    print("k           과목               부류  a.d (준수)            b.d (위반)")
    for c in nd:
        print("%-11s %-16s %-4s %-21s %-21s" %
              (c["k"], c["s"], c["cls"], str(c["a"]["d"]), str(c["b"]["d"])))


SIGN_FINAL = Sign(pP=5, pB=5, pC=2, pB2=12, pV=4, pay=0.45)
RULES_FINAL = Rules(consume_seed=True, generic_fo=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "current"
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    {"current": mode_current, "new": mode_new, "grid": mode_grid,
     "exploit": mode_exploit, "sign": mode_sign, "sign2": mode_sign2, "final": mode_final, "emit2": lambda n: mode_emit2(), "psweep": mode_psweep, "psweepcur": mode_psweep_cur}.get(mode, lambda n: mode_emit())(N)
