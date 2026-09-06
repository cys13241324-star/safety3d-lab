# -*- coding: utf-8 -*-
"""덱이 기출을 얼마나 덮는가 — CBT 회차의 주제·출제빈도를 기준으로 잰다.

    python tools/deckcov.py              과목 배분 + 빈출 문턱별 커버율
    python tools/deckcov.py --miss       빈출인데 덱에 없는 주제 (다음에 쓸 카드)
    python tools/deckcov.py --miss 15    문턱을 15로 (기본 10)
    python tools/deckcov.py --have       덱에 걸린 주제 — 판정을 눈으로 검증할 때
    python tools/deckcov.py --cards      덱 카드별로 무엇을 덮고 있나

`sim-balance.py` 는 판이 재미있는지를 재고, 이 도구는 판이 **시험에 쓸모 있는지**를
잰다. 밸런스는 서른 번 넘게 쟀는데 커버리지는 한 번도 재지 않았다.

기준은 `../sanup-safety-cbt/CBT_*/*_CBT.html` 의 `D.cards` 다. 회차마다 문항에
`subject`(과목) · `mid`(주제) · `fq`(출제빈도)가 이미 붙어 있으므로 우리가
주제를 새로 매기지 않는다. 24회차 2,880문항에서 고유 주제 1,966개가 나온다.

**주의 — 거르개이지 증명이 아니다.** 낱말 겹침으로 재므로 「덮었다」는 같은 주제를
다룬 카드가 있다는 뜻이지 그 카드가 기출을 대신한다는 뜻이 아니다. 「없다」로 나온
것 가운데도 다른 말로 이미 다룬 것이 있을 수 있다. 목록을 눈으로 훑을 것.

덱 115장으로 주제 1,966개를 덮는 산술 상한은 5.8% 다. 그러니 **전체 커버율은
읽을 것이 못 된다.** 볼 것은 `fq` 가 높은 구간의 커버율이다.
"""
import collections
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

HERE = pathlib.Path(__file__).parent.resolve()
LAB = HERE.parent
CBT = next((p for p in (LAB.parent / "sanup-safety-cbt",
                        LAB.parent.parent / "sanup-safety-cbt")
            if p.exists()), LAB.parent / "sanup-safety-cbt")
REIGNS = LAB / "reigns.html"

# 덱과 CBT 가 같은 과목을 다르게 적는다. 한 이름으로 모은다.
CANON = {"화학설비위험방지": "화학설비위험방지기술",
         "기계위험방지": "기계위험방지기술",
         "전기위험방지": "전기위험방지기술",
         "인간공학": "인간공학 및 시스템안전공학"}

STOP = set("그 및 의 에 를 을 은 는 이 가 와 과 등 시 대한 관한 있는 없는 하는 되는".split())


def canon(s):
    s = (s or "").strip()
    return CANON.get(s, s)


def block(s, name, op="{"):
    """`const NAME = {…}` 한 덩어리를 괄호 균형으로 떠 온다."""
    m = re.search(r"(?:const|let|var)\s+" + name + r"\s*=\s*" + re.escape(op), s)
    if not m:
        return None
    st = m.end() - 1
    d = 0
    for j in range(st, len(s)):
        if s[j] in "[{":
            d += 1
        elif s[j] in "]}":
            d -= 1
            if d == 0:
                return s[st:j + 1]
    return None


def toks(x):
    x = re.sub(r"<[^>]+>", " ", x or "")
    return {w for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", x) if w not in STOP}


def load_topics():
    """CBT 회차 → 주제별 출제빈도. 같은 회차가 두 벌 있으면 한 번만 센다."""
    seen, topics = set(), {}
    nq = 0
    for f in sorted(CBT.glob("CBT_*/*_CBT.html")):
        m = re.search(r"CBT_(\d{4})_(\d)회", str(f))
        rid = m.group(0) if m else f.name
        if rid in seen:
            continue
        b = block(f.read_text(encoding="utf-8", errors="ignore"), "D")
        if not b:
            continue
        try:
            D = json.loads(b)
        except ValueError:
            continue
        seen.add(rid)
        nq += len(D.get("q") or [])
        for c in (D.get("cards") or {}).values():
            mid = (c.get("mid") or "").strip()
            if not mid:
                continue
            e = topics.setdefault((canon(c.get("subject")), mid),
                                  {"fq": 0, "rounds": set(), "kind": c.get("kind", "")})
            e["fq"] += int(c.get("fq") or 1)
            e["rounds"].add(rid)
    return topics, len(seen), nq


def load_deck():
    s = REIGNS.read_text(encoding="utf-8")
    body = block(s, "DECK", "[")
    out, depth, st = [], 0, None
    for i, ch in enumerate(body):
        if ch == "{":
            if depth == 0:
                st = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(body[st:i + 1])

    def fld(c, n):
        m = re.search(n + r"\s*:\s*'((?:[^'\\]|\\.)*)'", c)
        return m.group(1) if m else ""

    return [dict(k=fld(c, "k"), s=canon(fld(c, "s")), law=fld(c, "law"),
                 t=fld(c, "t"), f=fld(c, "f")) for c in out]


def grade(topics, deck):
    """주제마다 가장 가까운 카드와 겹침 점수. 같은 과목이면 조금 얹는다."""
    dt = [(c, toks(c["t"] + " " + c["f"] + " " + c["law"] + " " + c["k"])) for c in deck]
    rows = []
    for (subj, mid), e in topics.items():
        mt = toks(mid)
        best, bs = None, 0.0
        for c, t in dt:
            if not (mt and t):
                continue
            inter = mt & t
            if not inter:
                continue
            sc = len(inter) / len(mt) + (0.15 if c["s"] == subj else 0)
            if sc > bs:
                bs, best = sc, c
        rows.append(dict(subj=subj, mid=mid, fq=e["fq"], rounds=len(e["rounds"]),
                         kind=e["kind"], score=round(bs, 3),
                         card=(best or {}).get("k", "")))
    return rows


def summary(rows, deck, nround, nq):
    tq = sum(r["fq"] for r in rows)
    cq = collections.Counter()
    for r in rows:
        cq[r["subj"]] += r["fq"]
    cd = collections.Counter(c["s"] for c in deck)
    td = sum(cd.values())
    print("CBT %d회차 %d문항 · 고유 주제 %d개 · 덱 %d장"
          % (nround, nq, len(rows), len(deck)))
    print()
    print("=" * 80)
    print("1. 과목 배분 — 기출(출제빈도 가중) vs 덱")
    print("=" * 80)
    print("%-22s%12s%8s%7s%8s%9s" % ("과목", "기출(가중)", "비중", "덱", "비중", "차"))
    for s_ in sorted(cq, key=lambda x: -cq[x]):
        a, b = cq[s_] / tq * 100, cd.get(s_, 0) / td * 100
        flag = "  ← 쏠림" if b - a > 6 else ("  ← 얇다" if a - b > 6 else "")
        print("%-22s%12d%7.1f%%%7d%7.1f%%%+8.1fp%s"
              % (s_, cq[s_], a, cd.get(s_, 0), b, b - a, flag))

    print()
    print("=" * 80)
    print("2. 빈출 문턱별 커버율 — 전체 커버율은 읽을 것이 못 된다")
    print("=" * 80)
    print("  덱 %d장 ÷ 주제 %d개 = 산술 상한 %.1f%%\n"
          % (len(deck), len(rows), len(deck) / len(rows) * 100))
    print("%-12s%10s%10s%10s%13s" % ("문턱", "주제", "덮은 것", "커버율", "기출 비중"))
    for t in (1, 3, 5, 8, 10, 15, 20):
        sel = [r for r in rows if r["fq"] >= t]
        cov = [r for r in sel if r["score"] >= 0.6]
        if not sel:
            continue
        print("%-12s%10d%10d%9.0f%%%12.0f%%"
              % ("fq≥%d" % t, len(sel), len(cov), len(cov) / len(sel) * 100,
                 sum(r["fq"] for r in sel) / tq * 100))
    print("\n  빈출일수록 커버율이 낮으면 순서가 뒤집힌 것이다 — `--miss` 로 목록을 본다.")


def miss(rows, thr, have=False):
    sel = [r for r in rows if r["fq"] >= thr and
           ((r["score"] >= 0.6) if have else (r["score"] < 0.6))]
    head = "덱이 덮은 주제" if have else "빈출인데 덱에 없는 주제 — 다음에 쓸 카드"
    print("%s (fq≥%d)" % (head, thr))
    print("=" * 80)
    tot = sum(1 for r in rows if r["fq"] >= thr)
    print("  fq≥%d 주제 %d개 중 %d개\n" % (thr, tot, len(sel)))
    by = collections.defaultdict(list)
    for r in sel:
        by[r["subj"]].append(r)
    for s_ in sorted(by, key=lambda x: -sum(r["fq"] for r in by[x])):
        rs = sorted(by[s_], key=lambda r: -r["fq"])
        print("  ■ %s — %d개 (가중 %d)" % (s_, len(rs), sum(r["fq"] for r in rs)))
        for r in rs:
            tail = ("→ %s" % r["card"]) if have else r["kind"]
            print("     fq%-4d %2d회차  %-38s%s" % (r["fq"], r["rounds"], r["mid"][:38], tail))
        print()


def cards(rows, deck):
    print("덱 카드별로 무엇을 덮고 있나")
    print("=" * 80)
    by = collections.defaultdict(list)
    for r in rows:
        if r["score"] >= 0.6:
            by[r["card"]].append(r)
    hit = set(by)
    print("  덱 %d장 중 %d장이 기출 주제에 걸렸다. 나머지 %d장은 매칭 실패이거나"
          % (len(deck), len(hit), len(deck) - len(hit)))
    print("  기출에 없는 주제를 다룬다 — 어느 쪽인지는 눈으로 봐야 한다.\n")
    for c in sorted(deck, key=lambda c: -sum(r["fq"] for r in by.get(c["k"], []))):
        rs = sorted(by.get(c["k"], []), key=lambda r: -r["fq"])
        w = sum(r["fq"] for r in rs)
        if rs:
            print("  %-12s%-22s 주제 %2d · 가중 %3d   %s"
                  % (c["k"], c["s"][:20], len(rs), w,
                     " · ".join(r["mid"][:16] for r in rs[:3])))
    print("\n  걸린 것이 없는 카드")
    none = [c for c in deck if c["k"] not in hit]
    for i in range(0, len(none), 6):
        print("    " + " · ".join(c["k"] for c in none[i:i + 6]))


if __name__ == "__main__":
    a = sys.argv[1:]
    topics, nround, nq = load_topics()
    if not topics:
        raise SystemExit("CBT 회차를 못 읽었다: %s" % CBT)
    deck = load_deck()
    rows = grade(topics, deck)
    if a and a[0] in ("--miss", "--have"):
        thr = int(a[1]) if len(a) > 1 else 10
        miss(rows, thr, have=(a[0] == "--have"))
    elif a and a[0] == "--cards":
        cards(rows, deck)
    else:
        summary(rows, deck, nround, nq)
