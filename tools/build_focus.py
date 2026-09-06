# -*- coding: utf-8 -*-
"""`focus.html` — 빈출 지도를 CBT 회차와 암기 은행에서 지어낸다.

    python tools/build_focus.py

다른 페이지가 전부 암기·체험(3D 실습장 · 암기 은행 · 순찰로 · 게임)인데, 시험이
**무엇을 자주 내는지**를 쓰는 페이지가 하나도 없었다. CBT 문항에는 `subject` ·
`mid`(주제) · `fq`(출제빈도)가 이미 붙어 있으므로 순위는 지어내지 않는다.

24회차 2,880문항 → 고유 주제 1,966개. 상위 200개가 기출의 37 %, 326개가 47 %다.
그래서 이 페이지의 진도는 **외운 개수가 아니라 덮은 기출 비중**으로 잰다.

## 잇는 방법 — 낱말이 아니라 문항을 경유한다

주제 이름으로 페이지를 이으려 하면 26 % 밖에 안 붙는다. 그런데 **CBT 문항 번호가
양쪽에 다 있다.** CBT 는 `q[].card → cards[].mid` 로 문항마다 주제를 달아 두었고,
암기 은행은 `methods[].qs[].src` 에 `2023-3-14`(연도-회차-번호) 로 같은 문항을
달아 두었다. 그 둘의 교집합이 2,880 문항 전부다. 문항을 징검다리로 삼으면

    주제 → 기출 문항   1,966 / 1,966  (100 %)
    주제 → 암기 묶음   1,966 / 1,966  (100 %)
    주제 → 3D 실습장     944 / 1,966  ( 48 %)   묶음에 topic3d 가 붙은 만큼

퍼지 매칭이 한 군데도 없다. 이름이 바뀌어도 문항 번호는 안 바뀌므로 잘 버틴다.

`deckcov.py` 와 같은 자료를 읽는다. 그쪽은 덱이 기출을 덮는지를 재고, 이쪽은
사람이 기출을 덮는지를 잰다.
"""
import collections
import json
import pathlib
import re
import sys
import urllib.parse

import figs_focus

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

HERE = pathlib.Path(__file__).parent.resolve()
LAB = HERE.parent
CBT = next((p for p in (LAB.parent / "sanup-safety-cbt",
                        LAB.parent.parent / "sanup-safety-cbt")
            if p.exists()), LAB.parent / "sanup-safety-cbt")
OUT = LAB / "focus.html"

# 회차 저장소는 다른 Pages 사이트라 상대경로가 닿지 않는다. 절대 주소를 쓴다.
CBT_BASE = "https://cys13241324-star.github.io/sanup-safety-cbt/"
VER = "09041852"        # 형제 페이지가 쓰는 캐시 무효화 값

CANON = {"화학설비위험방지": "화학설비위험방지기술",
         "기계위험방지": "기계위험방지기술",
         "전기위험방지": "전기위험방지기술",
         "인간공학": "인간공학 및 시스템안전공학"}

# 3D 실습장은 주제가 21개뿐이라 손으로 짠 규칙이 기계보다 정확하다.
# 암기 묶음의 `topic3d` 를 쓰면 묶음 단위라 「기계설비의 위험점 → 지게차」 처럼
# 엉뚱한 데로 보내고, 그나마 절반은 실습장에 없는 키(forklift·boiler…)를 가리킨다.
# 위에서부터 먼저 걸리는 것을 쓰므로 좁은 규칙을 앞에 둔다.
LAB3D = [
    ("roller", "롤러기 급정지장치", ["롤러기", "급정지장치"]),
    ("grinder", "연삭기 덮개 노출각도", ["연삭기", "연삭숫돌", "숫돌"]),
    ("press", "프레스 방호장치 안전거리", ["프레스", "양수기동", "광전자식"]),
    ("wirerope", "양중기 와이어로프 안전계수", ["와이어로프", "양중기", "권과방지", "달기구"]),
    ("elcb", "감전방지용 누전차단기", ["누전차단기", "감전방지용"]),
    ("approach", "충전전로 접근한계거리", ["충전전로", "접근한계", "활선"]),
    ("powerline", "가공전선로 이격거리", ["가공전선로", "가공전선"]),
    ("gasweld", "가스집합 용접장치", ["가스집합", "아세틸렌", "용접장치", "도관"]),
    ("chemdist", "화학설비 안전거리", ["화학설비"]),
    ("fall", "추락방호망", ["추락방호망", "방망사", "방망"]),
    ("net", "낙하물 방지망", ["낙하물", "방호선반", "방지망"]),
    ("rail", "안전난간", ["안전난간", "난간"]),
    ("ladder", "사다리식 통로", ["사다리"]),
    ("ramp", "가설통로 (경사로)", ["가설통로", "경사로"]),
    ("plank", "작업발판", ["작업발판", "통로발판"]),
    ("scaffold", "강관비계", ["강관비계", "강관틀", "비계"]),
    ("stairs", "계단·계단참", ["계단"]),
    ("shore", "거푸집 동바리 (파이프 서포트)", ["거푸집", "동바리", "서포트", "측압"]),
    ("trench", "굴착면 기울기", ["굴착면", "기울기", "흙막이", "굴착작업"]),
    ("lux", "작업면 조도", ["조도", "채광"]),
    ("vdt", "VDT 작업 자세", ["VDT", "영상표시단말기"]),
]


def lab_topic(mid):
    for k, name, words in LAB3D:
        for w in words:
            if w in mid:
                return k, name
    return "", ""
SHORT = {"안전관리론": "안전관리",
         "인간공학 및 시스템안전공학": "인간공학",
         "기계위험방지기술": "기계",
         "전기위험방지기술": "전기",
         "화학설비위험방지기술": "화학",
         "건설안전기술": "건설"}
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
ORDER = ["안전관리론", "인간공학 및 시스템안전공학", "기계위험방지기술",
         "전기위험방지기술", "화학설비위험방지기술", "건설안전기술"]


def block(s, name, op="{"):
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


def load_cbt():
    """회차를 읽어 주제별 출제빈도와, 주제 → 문항(연도·회차·번호)을 만든다."""
    seen, topics = set(), {}
    src2mid, nq = {}, 0
    for f in sorted(CBT.glob("CBT_*/*_CBT.html")):
        m = re.search(r"CBT_(\d{4})_(\d)회", str(f))
        if not m:
            continue
        y, r = m.group(1), m.group(2)
        if (y, r) in seen:
            continue
        b = block(f.read_text(encoding="utf-8", errors="ignore"), "D")
        if not b:
            continue
        try:
            D = json.loads(b)
        except ValueError:
            continue
        seen.add((y, r))
        cards = D.get("cards") or {}
        nq += len(D.get("q") or [])
        for q in (D.get("q") or []):
            c = cards.get(q.get("card"))
            if not c:
                continue
            mid = (c.get("mid") or "").strip()
            if not mid:
                continue
            subj = CANON.get((c.get("subject") or "").strip(),
                             (c.get("subject") or "").strip())
            key = (subj, mid)
            e = topics.setdefault(key, {"fq": 0, "q": [], "qa": [],
                                        "kind": c.get("kind", ""),
                                        "ch": c.get("chapter", ""),
                                        "front": "", "back": ""})
            e["q"].append((y, r, q.get("n")))
            e["qa"].append((y, r, q.get("n"), q.get("t") or "", q.get("sol") or ""))
            if not e["front"]:
                e["front"] = c.get("front") or ""
            if len(c.get("back") or "") > len(e["back"]):
                e["back"] = c.get("back") or ""
            src2mid["%s-%s-%s" % (y, r, q.get("n"))] = key
        # fq 는 문항이 아니라 카드에 붙은 값이라 따로 센다
        for c in cards.values():
            mid = (c.get("mid") or "").strip()
            if not mid:
                continue
            subj = CANON.get((c.get("subject") or "").strip(),
                             (c.get("subject") or "").strip())
            if (subj, mid) in topics:
                topics[(subj, mid)]["fq"] += int(c.get("fq") or 1)
    return topics, src2mid, sorted(seen), nq


def load_memo():
    """암기 은행에서 문항 → 묶음(id · 제목 · 3D 주제) 을 만든다."""
    p = LAB / "memo.html"
    s = p.read_text(encoding="utf-8")
    m = re.search(r'<script[^>]*id="bank"[^>]*>(.*?)</script>', s, re.S)
    if not m:
        return {}
    B = json.loads(m.group(1))
    out = {}
    for g in B.get("methods", []):
        meta = (g.get("id", ""), g.get("title", ""), g.get("topic3d") or "")
        for it in (g.get("qs") or []):
            if isinstance(it, dict) and it.get("src"):
                out[it["src"]] = meta
    return out


# 회차 원문의 표는 셀마다 인라인 style 을 달고 온다. 28,226 곳에 2.4 MB 다.
# 그 가운데 테두리·여백·배경은 어차피 이 페이지 CSS 가 !important 로 덮으므로
# 실어 보낼 까닭이 없다. **text-align 만은 남긴다** — center 11,192 · left 12,225 로
# 섞여 있어 한 값으로 몰면 표가 어그러진다.
DROP = re.compile(r"(?:border|padding|vertical-align|background|border-collapse"
                  r"|font-size|margin|font-weight)\s*:[^;\"]*;?")
CELL = re.compile(r'(<(?:td|th)\b[^>]*?)\sstyle="([^"]*)"')


def slim(html):
    """해설에서 덮어쓸 인라인 style 을 걷는다. 뜻이 바뀌는 것은 남긴다."""
    if not html:
        return html

    def cell(m):
        rest = DROP.sub("", m.group(2)).strip().strip(";")
        return m.group(1) + (' style="%s"' % rest if rest else "")

    html = CELL.sub(cell, html)
    # 표 자체의 style 은 셋 다 덮으므로 통째로 뗀다
    html = re.sub(r'<table\b[^>]*?\sstyle="[^"]*"', "<table", html)
    # 가로 스크롤 감싸개와 소제목은 클래스로 바꾼다
    html = html.replace('<div style="overflow-x:auto">', '<div class="tw">')
    html = html.replace('<div style="margin:12px 0 2px;font-weight:700">',
                        '<div class="ch">')
    return html


# 해설이 같은 말을 세 번 한다. 회차 원문이 「해설 → 암기 → 관련이론 → 표」를 이어
# 붙여 오는데, **관련이론 산문이 바로 뒤 표를 글로 옮긴 것**인 경우가 많다.
# 표의 첫 칸 이름이 그 문단에 다 들어 있으면 그 문단은 표를 되풀이한 것이다.
# 지우지는 않는다 — 접어 두고 「글로 된 요약」이라 이름을 붙인다.
TABLE_AT = re.compile(r'<div class="ch">.*?</div>\s*<div class="tw"><table>(.*?)</table>', re.S)
ROW1 = re.compile(r"<tr><td[^>]*>(.*?)</td>", re.S)


# 해설 맨 앞의 `<ul><li>…</li></ul>` 은 **이 주제를 쓰는 여러 문항의 답 설명**을
# 이어 붙인 것이다. 한 문항 안에서는 멀쩡하지만 한자리에 모으면 주어를 잃는다 —
# 「접선물림점이다.」 만 남으면 무엇이 접선물림점인지 알 길이 없다.
#
# 그런데 그 조각은 어느 문항 `sol` 의 앞부분이다(1,143 개 중 1,136 개, 99.4 %).
# 그러니 잃어버린 문제를 되돌려 줄 수 있다. 붙지 않는 것은 그대로 둔다.
UL_HEAD = re.compile(r"^\s*<ul>(.*?)</ul>", re.S)
LI = re.compile(r"<li>(.*?)</li>", re.S)


def _flat(x):
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", x or ""))


def pair_questions(html, qa, url_of):
    """조각마다 그 답이 붙어 있던 문제를 되돌려 준다."""
    m = UL_HEAD.match(html or "")
    if not m:
        return html
    items = LI.findall(m.group(1))
    if not items:
        return html
    flat = [(y, r, n, t, _flat(sol)) for y, r, n, t, sol in qa]
    out, used = [], set()
    for li in items:
        key = _flat(li)[:60]
        hit = None
        for y, r, n, t, sol in flat:
            if key and sol.startswith(key) and (y, r, n) not in used:
                hit = (y, r, n, t)
                used.add((y, r, n))
                break
        if hit:
            y, r, n, t = hit
            out.append(
                '<div class="qa"><div class="qq">'
                '<a href="%s" target="_blank" rel="noopener">%s %s회 #%s ↗</a>'
                '<span>%s</span></div><div class="qs">%s</div></div>'
                % (url_of(y, r, n), y, r, n, t, li))
        else:
            out.append('<div class="qa"><div class="qs">%s</div></div>' % li)
    # 접어 둔다. 「글이 너무 많다」의 절반이 여기였다 — 문항은 확인용이지 첫 줄이
    # 아니다. 몇 개인지는 접힌 채로도 보인다.
    body = ('<details class="qaset"><summary>실제 문항 %d개에서 짚은 곳</summary>'
            '%s</details>' % (len(items), "".join(out)))
    return body + html[m.end():]


def fold_repeat(html):
    if not html or "<table" not in html:
        return html
    m = TABLE_AT.search(html)
    if not m:
        return html
    labels = [re.sub(r"<[^>]+>", "", x).strip() for x in ROW1.findall(m.group(1))]
    labels = [x for x in labels if len(x) >= 2]
    if len(labels) < 3:
        return html
    # 표 바로 앞 문단
    head = html[:m.start()]
    pm = list(re.finditer(r"<p>(.*?)</p>", head, re.S))
    if not pm:
        return html
    last = pm[-1]
    txt = re.sub(r"<[^>]+>", "", last.group(1))
    if last.end() < len(head) - 40:          # 표에 붙어 있지 않으면 딴 이야기다
        return html
    hit = sum(1 for L in labels if L in txt)
    if hit < len(labels) * 0.8:              # 표를 되풀이한 것이 아니다
        return html
    folded = ('<details class="dup"><summary>글로 된 요약 — 아래 표와 같은 내용</summary>'
              + last.group(0) + "</details>")
    return html[:last.start()] + folded + html[last.end():]


# 해설이 오는 순서는 회차 원문의 순서(해설 → 암기 → 이론 → 표)이지 **읽는 순서**가
# 아니다. 수험생이 실제로 하는 일은 이렇다 — 무엇으로 갈리는지 잡고 → 외울 것을
# 외우고 → 진짜 문제로 확인한다. 그래서 다시 세운다.
#
#   ① 암기   1,956 주제(99 %)에 있다. 가장 값어치 있는 한 줄인데 맨 밑에 있었다.
#   ② 그림
#   ③ 표     1,603 주제(82 %). 갈리는 자리를 한눈에 보여 준다.
#   ④ 산문
#   ⑤ 문항   증거는 뒤에 둔다.
MNEM = re.compile(r"<p><strong>◈\s*암기</strong>(.*?)</p>", re.S)
TBL = re.compile(r'<div class="ch">.*?</div>\s*<div class="tw">.*?</table></div>', re.S)
QASET = re.compile(r'<details class="qaset">.*?</details>', re.S)
DUP = re.compile(r'<details class="dup">.*?</details>', re.S)


def restructure(html):
    if not html:
        return html
    mn = ""
    m = MNEM.search(html)
    if m:
        mn = ('<div class="mnem"><span>암기</span><p>%s</p></div>' % m.group(1).strip())
        html = html[:m.start()] + html[m.end():]
    tbl = "".join(TBL.findall(html))
    html = TBL.sub("", html)
    qa = "".join(QASET.findall(html))
    html = QASET.sub("", html)
    dup = "".join(DUP.findall(html))
    html = DUP.sub("", html)
    rest = html.strip()
    if rest:
        rest = '<div class="prose">%s</div>' % rest
    return mn + tbl + rest + dup + qa


def cbt_url(y, r, n):
    folder = "CBT_%s_%s회" % (y, r)
    fname = "%s_%s회_학습.html" % (y, r)
    return (CBT_BASE + urllib.parse.quote(folder) + "/"
            + urllib.parse.quote(fname) + "#q%s" % n)


def build():
    topics, src2mid, rounds, nq = load_cbt()
    memo = load_memo()

    rows = sorted(topics.items(), key=lambda kv: (-kv[1]["fq"], kv[0][0], kv[0][1]))
    tot = sum(v["fq"] for v in topics.values())

    data, ngm, ng3 = [], 0, 0
    for i, ((subj, mid), v) in enumerate(rows):
        qs = sorted(set(v["q"]), key=lambda t: (-int(t[0]), -int(t[1]), int(t[2])))
        # 이 주제의 문항들이 가장 많이 속한 묶음을 고른다
        c = collections.Counter(memo[k] for k in
                                ("%s-%s-%s" % q for q in qs) if k in memo)
        g = c.most_common(1)[0][0] if c else ("", "", "")
        t3, t3n = lab_topic(mid)
        if g[0]:
            ngm += 1
        if t3:
            ng3 += 1
        yc = collections.Counter(int(y) for y, r, n in qs)
        data.append({"i": i, "s": subj, "m": mid, "q": v["fq"], "k": v["kind"],
                     "c": v["ch"], "f": slim(v["front"]),
                     "b": restructure(fold_repeat(pair_questions(slim(v["back"]), v["qa"], cbt_url))),
                     "fig": figs_focus.fig_for(mid),
                     "n": [["%s %s회 #%s" % (y, r, n), cbt_url(y, r, n)] for y, r, n in qs],
                     "y": [yc.get(yy, 0) for yy in YEARS],
                     "g": g[0], "gt": g[1], "t3": t3, "t3n": t3n})

    per = collections.Counter()
    for d in data:
        per[d["s"]] += d["q"]
    marks = [(n, round(sum(d["q"] for d in data[:n]) / tot * 100, 1))
             for n in (50, 100, 200, 326, 500, 800)]
    # 누적 곡선. 1,966 점을 다 실을 까닭이 없어 120 점으로 고르게 줄인다.
    acc, cum = 0, []
    step = max(1, len(data) // 120)
    for i, d in enumerate(data):
        acc += d["q"]
        if i % step == 0 or i == len(data) - 1:
            cum.append([i + 1, round(acc / tot * 100, 2)])

    payload = json.dumps({"t": data, "tot": tot, "nq": nq, "nr": len(rounds),
                          "per": dict(per), "order": ORDER, "short": SHORT,
                          "ver": VER, "years": YEARS, "cum": cum,
                          "qmax": max(d["q"] for d in data),
                          "marks": [list(m) for m in marks]},
                         ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/").replace("<!--", "<\\!--")

    doc = (TEMPLATE
           .replace("__NROUND__", str(len(rounds)))
           .replace("__NQ__", format(nq, ","))
           .replace("__NTOPIC__", format(len(data), ","))
           .replace("__M200__", str(marks[2][1]))
           .replace("__M326__", str(marks[3][1]))
           .replace("__NG3__", format(ng3, ","))
           .replace("__DATA__", payload))
    OUT.write_text(doc, encoding="utf-8")

    print("%s — %.1f MB" % (OUT.name, OUT.stat().st_size / 1024 / 1024))
    print("  회차 %d · 문항 %d · 주제 %d · 가중합 %d" % (len(rounds), nq, len(data), tot))
    print("  파레토: " + " · ".join("상위%d→%.1f%%" % m for m in marks))
    print("  이어짐 — 기출 %d(100%%) · 암기 묶음 %d(%.0f%%) · 3D %d(%.0f%%)"
          % (len(data), ngm, ngm / len(data) * 100, ng3, ng3 / len(data) * 100))


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>산업안전기사 빈출 지도</title>
<script>(function(){try{var t=localStorage.getItem('safety_theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<style>
:root{--bg:#0A1018;--panel:#0F1622;--panel2:#182234;--line:#33425C;--line-soft:#1E2938;--text:#E8EEF8;--muted:#8C99B0;--dim:#8290AC;--accent:#7FA6E0;--accent-ink:#0B111C;--ok:#5CC08A;--ok-soft:rgba(92,192,138,.16);--bad:#F07056;--warn:#E3B54D;--warn-soft:rgba(227,181,77,.10);--warn-line:rgba(227,181,77,.45);--on-accent:#1A1200;--tint:rgba(255,255,255,.05);--sans:"IBM Plex Sans KR","Pretendard","Malgun Gothic",sans-serif;--mono:"IBM Plex Mono",Consolas,monospace;--display:"Gothic A1","IBM Plex Sans KR",sans-serif;color-scheme:dark}
:root[data-theme="light"]{color-scheme:light;--bg:#F4F6FA;--panel:#FFFFFF;--panel2:#EAEEF5;--line:#C6D0DE;--line-soft:#E0E6EF;--text:#14202E;--muted:#4A5568;--dim:#66738A;--accent:#2F5FA8;--accent-ink:#FFFFFF;--ok:#1F6B45;--ok-soft:rgba(31,107,69,.12);--bad:#A8391F;--warn:#8F6512;--warn-soft:rgba(143,101,18,.10);--warn-line:rgba(143,101,18,.35);--on-accent:#FFFFFF;--tint:rgba(0,0,0,.04)}
*{box-sizing:border-box}
:focus-visible{outline:2px solid var(--warn);outline-offset:2px}
button,a,select,input,[role=button]{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:15px;line-height:1.55;min-height:100vh}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.wrap{max-width:940px;margin:0 auto;padding:34px 18px 90px}
.topRow{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:14px}
.back{color:var(--muted);text-decoration:none;font-size:13.5px}
.back:hover{color:var(--text)}
.b{font:inherit;font-size:13.5px;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:transparent;color:var(--text);cursor:pointer}
.b:hover{border-color:var(--muted)}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}
h1{font-family:var(--display);font-weight:700;font-size:32px;letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance}
.hazard{height:6px;max-width:300px;border-radius:3px;margin:10px 0 16px;background:var(--warn-line)}
.lede{color:var(--muted);margin:0 0 22px;max-width:64ch}
.lede b{color:var(--text);font-weight:600}

.prog{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:0 0 20px}
.prog .big{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:4px}
.prog .pc{font-family:var(--mono);font-size:38px;font-weight:600;color:var(--warn);line-height:1}
.prog .cap{color:var(--muted);font-size:13.5px}
.bar{height:12px;border-radius:6px;background:var(--panel2);border:1px solid var(--line-soft);overflow:hidden;margin:12px 0 6px;position:relative}
.bar i{display:block;height:100%;background:var(--warn);width:0;transition:width .3s}
.bar u{position:absolute;top:0;bottom:0;width:1px;background:var(--line);text-decoration:none}
.ticks{display:flex;justify-content:space-between;font-family:var(--mono);font-size:10.5px;color:var(--dim)}
/* 누적 곡선. 한 계열뿐이라 범례가 없다 — 캡션이 무엇을 그렸는지 말한다.
   선 2px · 채움은 같은 색 10 % · 격자는 실선 hairline 으로 뒤로 물린다. */
.pareto{margin:18px 0 0;padding:0}
.pareto figcaption{font-size:12px;color:var(--muted);margin:0 0 8px}
.pwrap{overflow-x:auto}
.pareto svg{display:block;width:100%;min-width:320px;height:auto;overflow:visible}
.pareto .grid{stroke:var(--line-soft);stroke-width:1;fill:none}
.pareto .axis{fill:var(--dim);font-family:var(--mono);font-size:9.5px}
.pareto .fill{fill:var(--warn);opacity:.10}
.pareto .line{fill:none;stroke:var(--warn);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.pareto .mk{stroke:var(--line);stroke-width:1;fill:none}
.pareto .dot{fill:var(--warn);stroke:var(--panel);stroke-width:2}
.pareto .lbl{fill:var(--text);font-size:10.5px;font-family:var(--mono)}
.pareto .you{stroke:var(--ok);stroke-width:1.5;fill:none;stroke-dasharray:none}
.pareto .youl{fill:var(--ok);font-size:10px;font-family:var(--mono)}
.pareto .hit{fill:transparent;cursor:crosshair}
.pareto .cross{stroke:var(--dim);stroke-width:1;fill:none;opacity:0}
.pareto .cdot{fill:var(--text);stroke:var(--panel);stroke-width:2;opacity:0}
.legend{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;margin:0 0 10px;padding:9px 12px;border:1px solid var(--line-soft);border-radius:8px;background:var(--panel);font-size:12px;color:var(--dim);line-height:1.6}
.legend b{color:var(--muted);font-weight:600}
.legend em{font-style:normal;color:var(--warn)}
.phint{margin-top:6px;font-size:12px;color:var(--muted)}
.phint b{color:var(--warn);font-family:var(--mono);font-weight:600}
.perSub{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:8px;margin-top:16px}
.next{margin-top:16px;padding-top:14px;border-top:1px dashed var(--line-soft)}
.next .lb{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-bottom:8px}
.next .row{display:flex;flex-wrap:wrap;gap:8px}
.next button{font:inherit;font-size:12.5px;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:transparent;color:var(--text);cursor:pointer;text-align:left;line-height:1.35}
.next button:hover{border-color:var(--warn)}
.next button b{font-family:var(--mono);font-weight:600;color:var(--warn);display:block;font-size:14px}
.next button em{font-style:normal;color:var(--dim);font-size:11px}
.next .done{color:var(--ok);font-size:12.5px}
.plan{margin-top:14px;padding-top:12px;border-top:1px dashed var(--line-soft)}
.plan .lb{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-bottom:8px}
.plan .row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:13px;color:var(--muted)}
.plan label{color:var(--dim);font-size:12.5px}
.plan input[type=date]{font:inherit;font-size:13px;padding:6px 10px;border-radius:7px;border:1px solid var(--line);background:var(--panel);color:var(--text)}
.plan b{color:var(--warn);font-family:var(--mono);font-weight:600}
.plan .warn{color:var(--bad)}
.ps{background:var(--panel2);border:1px solid var(--line-soft);border-radius:8px;padding:9px 11px}
.ps .n{font-size:12px;color:var(--muted);margin-bottom:5px}
.ps .v{font-family:var(--mono);font-size:15px;font-weight:600}
.ps .sb{height:4px;border-radius:2px;background:var(--line-soft);margin-top:6px;overflow:hidden}
.ps .sb i{display:block;height:100%;background:var(--accent);width:0}

.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 12px}
.tabs{display:flex;flex-wrap:wrap;gap:6px}
.tab{font:inherit;font-size:13px;padding:6px 11px;border-radius:20px;border:1px solid var(--line);background:transparent;color:var(--muted);cursor:pointer}
.tab[aria-pressed=true]{background:var(--warn-soft);border-color:var(--warn-line);color:var(--text)}
input[type=search]{font:inherit;font-size:14px;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--text);min-width:180px;flex:1 1 180px}
.cnt{font-family:var(--mono);font-size:12.5px;color:var(--dim);margin-left:auto;white-space:nowrap}

ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
li{background:var(--panel);border:1px solid var(--line-soft);border-radius:10px;
  overflow:clip}  /* hidden 이면 스크롤 컨테이너가 생겨 안쪽 sticky 가 안 붙는다 */
li.done{border-color:var(--ok);background:var(--ok-soft)}
li.open{border-color:var(--line);background:var(--panel)}
/* 해설이 길면(90퍼센트 지점 647자 + 표) 스크롤 중에 무슨 주제였는지 사라진다.
   펼친 행의 제목만 위에 붙여 둔다. */
li.open .hd{border-bottom:1px solid var(--line-soft);position:sticky;top:0;z-index:2;
  background:var(--panel)}
li.open.done{border-color:var(--ok)}
.hd{display:grid;grid-template-columns:40px 58px 1fr auto;gap:10px;align-items:center;padding:10px 12px;cursor:pointer}
.rk{font-family:var(--mono);font-size:12px;color:var(--dim);text-align:right}
.fq{font-family:var(--mono);font-size:12.5px;color:var(--warn);white-space:nowrap}
.fq b{font-size:15px;font-weight:600}
.ttl{min-width:0}
.ttl .m{font-size:14.5px;font-weight:500;color:var(--text);overflow-wrap:anywhere;line-height:1.4}
.ttl .sub{font-size:11.5px;color:var(--dim);margin-top:2px}
/* 행 안의 두 그림. 숫자만 늘어놓으면 눈이 못 훑는다.
   ㆍ빈도 막대 — 길이 하나로 위아래 차이를 본다
   ㆍ연도 칸 — 2021~2026 여섯 칸. **아직도 나오는 주제인지**가 여기서 보인다 */
.fqwrap{display:flex;flex-direction:column;gap:3px}
.fqbar{height:4px;border-radius:0 2px 2px 0;background:var(--warn);opacity:.85;min-width:2px}
.yrs{display:inline-flex;align-items:flex-end;gap:2px;height:11px;margin-left:7px;vertical-align:-1px}
.yrs i{width:3px;background:var(--line);border-radius:1px 1px 0 0}
.yrs i.on{background:var(--accent)}
.yrs i.hot{background:var(--warn)}
.chip{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:4px;background:var(--panel2);border:1px solid var(--line-soft);color:var(--muted);margin-right:5px}
.chip.f{color:var(--accent);border-color:var(--accent)}
.ck{width:26px;height:26px;border-radius:6px;border:1.5px solid var(--line);background:transparent;color:transparent;cursor:pointer;font-size:15px;line-height:1;flex:none}
li.done .ck{border-color:var(--ok);color:var(--ok)}
.bd{display:none;padding:2px 16px 16px 16px}
li.open .bd{display:block}
/* 그림. 여섯이 나란히 서고 좁으면 두 줄, 더 좁으면 한 줄로 접힌다. */
.figset{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:10px;margin:12px 0 4px}
.hz{margin:0;padding:9px 8px 7px;border:1px solid var(--line-soft);border-radius:9px;
  background:var(--panel2)}
.hz svg{display:block;width:100%;height:auto}
.hz figcaption{margin-top:5px;text-align:center;line-height:1.35}
.hz figcaption b{display:block;font-size:12.5px;color:var(--text);font-weight:600}
.hz figcaption span{font-size:11px;color:var(--dim);font-family:var(--mono)}
/* 그림 하나에 숫자 몇 개가 딸리는 꼴. 그림은 왼쪽, 숫자는 오른쪽. */
.figset.one{grid-template-columns:minmax(180px,1fr) minmax(200px,1.2fr)}
.numset{display:flex;flex-direction:column;gap:5px;align-content:start}
.nb{display:grid;grid-template-columns:1fr auto;gap:4px 10px;align-items:baseline;
  padding:7px 10px;border:1px solid var(--line-soft);border-radius:7px;background:var(--panel2)}
.nb b{font-size:12.5px;font-weight:500;color:var(--muted)}
.nb i{font-style:normal;font-family:var(--mono);font-size:13px;font-weight:600;color:var(--warn)}
.nb em{grid-column:1/-1;font-style:normal;font-size:11px;color:var(--dim)}
@media (max-width:560px){.figset.one{grid-template-columns:1fr}}
/* 표를 글로 옮긴 문단은 접어 둔다 — 지우지는 않는다 */
/* 문항이 짚은 곳. 조각마다 그 답이 붙어 있던 문제를 앞에 세운다. */
.qaset{margin:16px 0 4px;border-top:1px solid var(--line-soft);padding-top:12px}
.qaset>summary{font-size:12.5px;color:var(--dim);cursor:pointer;list-style:none}
.qaset>summary::-webkit-details-marker{display:none}
.qaset>summary::before{content:'▸ ';color:var(--dim)}
.qaset[open]>summary{margin-bottom:10px}
.qaset[open]>summary::before{content:'▾ '}
.qaset>summary:hover{color:var(--muted)}
.qa{margin:0 0 8px;padding:9px 11px;border:1px solid var(--line-soft);border-radius:8px;
  background:var(--panel2)}
.qq{display:flex;flex-wrap:wrap;gap:4px 8px;align-items:baseline;margin-bottom:6px}
.qq a{font-family:var(--mono);font-size:11px;color:var(--dim);text-decoration:none;
  border:1px solid var(--line-soft);border-radius:5px;padding:1px 6px;white-space:nowrap}
.qq a:hover{border-color:var(--warn);color:var(--text)}
.qq span{font-size:13px;color:var(--text);font-weight:500}
.qs{font-size:13.5px;color:var(--muted);line-height:1.65}
.qs strong{color:var(--text)}
.qs u{text-decoration:none;border-bottom:1px solid var(--warn-line);color:var(--text)}
.dup{margin:10px 0;border-left:2px solid var(--line-soft);padding-left:10px}
.dup summary{font-size:12px;color:var(--dim);cursor:pointer;list-style:none}
.dup summary::-webkit-details-marker{display:none}
.dup summary::before{content:'▸ ';color:var(--dim)}
.dup[open] summary::before{content:'▾ '}
.dup p{margin:8px 0 0;color:var(--muted);font-size:13.5px}
/* ── 해설의 위계 ───────────────────────────────────────────────────────
   보이는 것이 다 같은 무게면 어디를 볼지 알 수 없다. 굵게 쓰는 자리는 하나다.

   ① 암기   1,956 주제(99 %)에 있는 한 줄. **이 판에서 유일하게 큰 것.**
   ② 표     갈리는 자리. 값에 표시가 붙는다.
   ③ 산문   받쳐 주는 말. 물린다.
   ④ 문항   접어 둔다 — 확인용이지 첫 줄이 아니다.

   원문의 <strong> 은 용어, <u> 는 **외울 값**이다(각각 11,870 · 16,492 곳).
   뜻이 이미 나뉘어 있는데 둘 다 밋밋하게 두고 있었다. <u> 를 살린다. */
/* 재 보니 해설 한 줄이 65자였다(872px / 13.5px). 한국어는 45~50자에서
   눈이 다음 줄 첫 글자를 놓치지 않는다. 글에만 폭을 준다 — 표와 그림은
   가로가 넓을수록 좋으므로 그대로 전체 폭을 쓴다. */
.bd{--measure:620px}
.bd .q{font-size:16px;font-weight:600;margin:13px 0 2px;line-height:1.5;color:var(--text);
  max-width:var(--measure)}
.bd .chp{font-size:11.5px;color:var(--dim);margin:12px 0 0}

.mnem{display:grid;grid-template-columns:auto 1fr;gap:11px;align-items:start;
  margin:14px 0 16px;padding:12px 15px 12px 13px;border-left:3px solid var(--warn);
  border-radius:0 10px 10px 0;background:var(--warn-soft);max-width:690px}
.mnem>span{font-size:11.5px;font-weight:600;color:var(--warn);padding-top:3px;white-space:nowrap}
.mnem p{margin:0;font-size:15px;line-height:1.75;color:var(--text)}
.mnem u{text-decoration:none;border-bottom:2px solid var(--warn);padding-bottom:1px}
.mnem strong{font-weight:600}

/* 외울 값에 표시를 붙인다. 밑줄 한 줄은 글 무더기 안에서 안 보인다. */
.bd .a u{text-decoration:none;background:var(--warn-soft);color:var(--text);
  padding:1px 4px;margin:0 -1px;border-radius:4px;
  -webkit-box-decoration-break:clone;box-decoration-break:clone}
.bd .a strong{color:var(--text);font-weight:600}

.prose{margin:12px 0 0;font-size:13.5px;line-height:1.75;color:var(--dim);max-width:var(--measure)}
.prose p{margin:0 0 7px}
.prose strong{color:var(--muted)}
.prose u{background:none;padding:0;color:var(--muted);
  border-bottom:1px solid var(--line)}

.bd .a .ch{margin:16px 0 6px;font-weight:600;color:var(--text);font-size:13.5px}
.bd .a{color:var(--muted);font-size:14px;line-height:1.7}
.bd .a strong{color:var(--text)}
.bd .a u{text-decoration:none;border-bottom:1px solid var(--warn-line);color:var(--text)}
.bd .a ul{list-style:disc;padding-left:20px;margin:6px 0}
.bd .a>p,.bd .a ul,.bd .a ol{max-width:var(--measure)}
/* 회차 원문이 밝은 화면을 전제로 한 인라인 색을 달고 온다(th 배경 #f1f5f9,
   테두리 #cbd5e1). 어두운 판에서 흰 바탕에 흰 글씨가 되므로 덮어쓴다. */
.bd .a table{border-collapse:collapse!important;margin:10px 0!important;font-size:13px!important}
.bd .a td,.bd .a th{border:1px solid var(--line-soft)!important;padding:5px 9px!important;vertical-align:middle}
.bd .a th{background:var(--panel2)!important;color:var(--text)}
.bd .a td{color:var(--muted)}
.bd .a td u,.bd .a th u{color:var(--text);background:var(--warn-soft);padding:1px 5px;border-radius:4px;font-weight:500}
.bd .a .tw{overflow-x:auto;max-width:100%}
.bd .a .ch{margin:12px 0 2px;font-weight:700;color:var(--text)}

/* 이어가기 */
.go{margin-top:14px;padding-top:12px;border-top:1px dashed var(--line-soft)}
.go .lb{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-bottom:7px}
.go .qs{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:9px}
.go .qs a{font-family:var(--mono);font-size:11.5px;padding:3px 8px;border-radius:5px;border:1px solid var(--line-soft);background:var(--panel2);color:var(--muted);text-decoration:none;white-space:nowrap}
.go .qs a:hover{border-color:var(--warn);color:var(--text)}
.go .jump{display:flex;flex-wrap:wrap;gap:6px}
.go .jump a{font-size:12.5px;padding:6px 11px;border-radius:7px;border:1px solid var(--line);color:var(--text);text-decoration:none;display:inline-flex;gap:6px;align-items:center}
.go .jump a:hover{border-color:var(--warn)}
.go .jump a em{font-style:normal;color:var(--dim);font-size:11.5px}

.more{display:block;width:100%;margin:16px 0 0;padding:11px;border-radius:8px;border:1px solid var(--line);background:transparent;color:var(--text);font:inherit;cursor:pointer}
.more:hover{border-color:var(--warn)}
/* 1,966개가 구분선 없이 이어져 있었다. 어디까지 왔는지 알 수 없다는 뜻이다.
   빈도 구간이 바뀌는 자리에 띠를 놓아 스크롤 위치 자체가 말을 하게 한다. */
li.band{background:none;border:none;border-radius:0;display:flex;align-items:baseline;
  gap:9px;margin:12px 2px 2px;padding:0}
li.band:first-child{margin-top:0}
li.band b{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--warn)}
li.band span{font-size:11.5px;color:var(--dim)}
li.band i{flex:1;height:1px;background:var(--line-soft)}
.empty{text-align:center;color:var(--dim);padding:40px 0}
footer{margin-top:36px;color:var(--dim);font-family:var(--mono);font-size:11.5px;line-height:1.7}
@media (max-width:560px){
  .wrap{padding:20px 12px 80px}
  h1{font-size:26px}
  .hd{grid-template-columns:32px 50px 1fr auto;gap:8px;padding:9px 10px}
  .prog{padding:16px}
  .prog .pc{font-size:32px}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="topRow">
    <a class="back" href="index.html">← 학습실</a>
    <button class="b bTheme" type="button">밝은 모드</button>
  </div>

  <p class="eyebrow">출제빈도 · 기출 __NROUND__회차</p>
  <h1>빈출 지도</h1>
  <div class="hazard"></div>
  <p class="lede">기출 __NROUND__회차 __NQ__문항에서 주제 __NTOPIC__개를 뽑아 <b>출제빈도 순</b>으로 세웠습니다.
  외운 것을 체크하면 그것이 기출의 몇 %를 덮는지 계산합니다. 진도는 개수가 아니라 <b>덮은 출제비중</b>으로 잽니다.
  주제마다 그 문제가 실제로 나온 회차, 암기 은행의 묶음, 3D 실습장으로 바로 건너갑니다.</p>

  <section class="prog" aria-label="진도">
    <div class="big">
      <span class="pc mono" id="pc">0.0%</span>
      <span class="cap" id="cap">아직 체크한 주제가 없습니다</span>
    </div>
    <div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" id="barw">
      <i id="bar"></i><u style="left:37%"></u><u style="left:47.3%"></u>
    </div>
    <div class="ticks"><span>0%</span><span>상위 200주제 = 37%</span><span>326주제 = 47%</span><span>100%</span></div>

    <figure class="pareto">
      <figcaption>빈도 순으로 쌓은 누적 기출 비중 — 앞이 가파르다</figcaption>
      <div class="pwrap"><svg id="pareto" viewBox="0 0 640 172" role="img"
        aria-label="주제를 출제빈도 순으로 쌓았을 때의 누적 기출 비중. 상위 200개가 37 %, 326개가 47 %."></svg></div>
      <div class="phint" id="phint">상위 <b>200</b>개가 기출의 <b>37 %</b></div>
    </figure>

    <div class="perSub" id="perSub"></div>
    <div class="next" id="next"></div>
    <div class="plan" id="plan">
      <div class="lb">시험까지</div>
      <div class="row">
        <label for="dday">시험일</label>
        <input type="date" id="dday" aria-describedby="planOut">
        <span id="planOut">날짜를 넣으면 하루 몇 개씩 해야 하는지 계산합니다.</span>
      </div>
    </div>
  </section>

  <div class="ctl">
    <div class="tabs" id="subTabs"></div>
  </div>
  <div class="ctl">
    <div class="tabs" id="kindTabs"></div>
    <input type="search" id="q" placeholder="주제 검색" aria-label="주제 검색">
    <span class="cnt" id="cnt"></span>
  </div>

  <p class="legend"><span class="yrs" aria-hidden="true"><i class="on" style="height:5px"></i><i class="on" style="height:8px"></i><i style="height:1px"></i><i class="hot" style="height:6px"></i><i class="hot" style="height:11px"></i><i class="hot" style="height:4px"></i></span>
    행 오른쪽 여섯 칸은 <b>2021 → 2026</b> 해마다 몇 번 나왔는지입니다. 낮은 칸은 그해 안 나온 것이고,
    <em>진한 칸</em>이 2025·2026 입니다 — <b>아직도 나오는 주제인지</b>가 여기서 보입니다.</p>

  <ol id="list"></ol>
  <button class="more" id="more" type="button" hidden>더 보기</button>
  <p class="empty" id="empty" hidden>해당하는 주제가 없습니다.</p>

  <footer>
    기출 __NROUND__회차 __NQ__문항 · 고유 주제 __NTOPIC__개 · 상위 200주제가 기출의 __M200__%, 326주제가 __M326__%<br>
    순위는 CBT 문항에 붙은 출제빈도를 합산한 것입니다. 회차·암기 묶음은 문항 번호로 이었고, 3D 실습장은 __NG3__개 주제에 붙습니다.<br>
    체크는 이 브라우저에만 남습니다. © addto press. 기출 문항과 해설의 저작권은 출판사에 있습니다.
  </footer>
</div>

<script>window.__D=__DATA__;</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
<script>
(function(){
  var D = window.__D, T = D.t, KEY = 'safety_focus_v1', PAGE = 60;
  var MEMO = 'memo.html?v=' + D.ver, LAB = 'lab.html?v=' + D.ver;
  var done = {}, subj = '', kind = '', kw = '', shown = PAGE, onlyTodo = false;
  try { done = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e) { done = {}; }
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(done)); } catch(e){} }

  var list = document.getElementById('list'), moreB = document.getElementById('more'),
      empty = document.getElementById('empty'), cntEl = document.getElementById('cnt');

  function renderProg(){
    var got = 0, per = {};
    for (var i = 0; i < T.length; i++) {
      if (done[T[i].m]) { got += T[i].q; per[T[i].s] = (per[T[i].s] || 0) + T[i].q; }
    }
    var pc = D.tot ? got / D.tot * 100 : 0, n = Object.keys(done).length;
    document.getElementById('pc').textContent = pc.toFixed(1) + '%';
    document.getElementById('cap').textContent = n
      ? n.toLocaleString() + '개 체크 — 기출 ' + D.nq.toLocaleString() + '문항 가운데 이만큼을 덮습니다'
      : '아직 체크한 주제가 없습니다';
    document.getElementById('bar').style.width = Math.min(100, pc) + '%';
    document.getElementById('barw').setAttribute('aria-valuenow', pc.toFixed(1));
    var h = '';
    D.order.forEach(function(s){
      var tot = D.per[s] || 0, g = per[s] || 0, r = tot ? g / tot * 100 : 0;
      h += '<div class="ps"><div class="n">' + (D.short[s] || s) + '</div>'
         + '<div class="v mono">' + r.toFixed(0) + '%</div>'
         + '<div class="sb"><i style="width:' + r.toFixed(1) + '%"></i></div></div>';
    });
    document.getElementById('perSub').innerHTML = h;
    renderNext(pc);
    renderPlan();
    drawPareto(pc);
  }

  /* 「다음 N개를 더 하면 몇 %p」 — 목록이 빈도 순이라 안 외운 것의 앞쪽이 곧 다음 차례다.
     외운 개수로는 얼마나 남았는지 가늠이 안 되므로 늘어날 기출 비중으로 적는다. */
  /* ── 누적 곡선 ────────────────────────────────────────────────────────────
     x 는 주제 순위(1..1966)를 그대로 선형으로 둔다. 로그로 펴면 앞쪽이 편해
     보이지만, **앞이 가파르다는 것 자체가 이 그림의 말**이라 펴면 안 된다.
     한 계열뿐이므로 범례는 없고, 값표는 200·326 두 자리에만 단다. */
  var PL = {l:44, r:620, t:16, b:130};
  function px(i){ return PL.l + (i - 1) / (T.length - 1) * (PL.r - PL.l); }
  function py(v){ return PL.b - v / 100 * (PL.b - PL.t); }

  function drawPareto(pc){
    var svg = document.getElementById('pareto');
    if(!svg || !D.cum || !D.cum.length) return;
    var C = D.cum, h = '';
    /* 격자 — 뒤로 물린 실선 */
    [25, 50, 75, 100].forEach(function(v){
      h += '<path class="grid" d="M' + PL.l + ' ' + py(v).toFixed(1)
         + 'H' + PL.r + '"/>'
         + '<text class="axis" x="' + (PL.l - 6) + '" y="' + (py(v) + 3.5).toFixed(1)
         + '" text-anchor="end">' + v + '%</text>';
    });
    /* 채움과 선 */
    var d = 'M' + px(C[0][0]).toFixed(1) + ' ' + py(C[0][1]).toFixed(1);
    for(var i = 1; i < C.length; i++){
      d += 'L' + px(C[i][0]).toFixed(1) + ' ' + py(C[i][1]).toFixed(1);
    }
    h += '<path class="fill" d="' + d + 'L' + PL.r + ' ' + PL.b + 'H' + PL.l + 'Z"/>';
    h += '<path class="line" d="' + d + '"/>';
    /* 값표는 두 자리만 — 흩뿌리면 안 읽힌다 */
    /* 두 값표가 곡선 위 가까운 데 앉아 서로 4px 까지 붙는다. 하나는 점 아래로,
       하나는 위로 갈라 28px 를 벌린다. 글자는 겹치면 둘 다 못 읽는다. */
    (D.marks || []).forEach(function(m){
      if(m[0] !== 200 && m[0] !== 326) return;
      var x = px(m[0]), y = py(m[1]), below = (m[0] === 200);
      h += '<path class="mk" d="M' + x.toFixed(1) + ' ' + PL.b + 'V' + y.toFixed(1) + '"/>'
         + '<circle class="dot" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="4"/>'
         + '<text class="lbl" x="' + (x + 9).toFixed(1) + '" y="'
         + (below ? y + 16 : y - 8).toFixed(1)
         + '">' + m[0] + '개 · ' + m[1] + '%</text>';
    });
    /* 지금 덮은 만큼을 가로줄로 */
    if(pc > 0.05){
      var yy = py(Math.min(100, pc));
      h += '<path class="you" d="M' + PL.l + ' ' + yy.toFixed(1) + 'H' + PL.r + '"/>'
         + '<text class="youl" x="' + PL.r + '" y="' + (yy - 6).toFixed(1)
         + '" text-anchor="end">지금 ' + pc.toFixed(1) + '%</text>';
    }
    /* x 축 눈금 */
    [1, 500, 1000, 1500, T.length].forEach(function(v){
      h += '<text class="axis" x="' + px(v).toFixed(1) + '" y="' + (PL.b + 16)
         + '" text-anchor="middle">' + (v === 1 ? '1위' : v.toLocaleString()) + '</text>';
    });
    h += '<text class="axis" x="' + PL.l + '" y="' + (PL.b + 32) + '">주제 순위 (빈도 순)</text>';
    /* 짚어 보기 */
    h += '<path class="cross" id="pcx" d="M0 ' + PL.t + 'V' + PL.b + '"/>'
       + '<circle class="cdot" id="pcd" r="4"/>'
       + '<rect class="hit" id="phit" x="' + PL.l + '" y="' + PL.t + '" width="'
       + (PL.r - PL.l) + '" height="' + (PL.b - PL.t) + '"/>';
    svg.innerHTML = h;
    wirePareto();
  }

  function wirePareto(){
    var svg = document.getElementById('pareto'), hit = document.getElementById('phit');
    if(!hit) return;
    var cx = document.getElementById('pcx'), cd = document.getElementById('pcd'),
        hint = document.getElementById('phint'), C = D.cum;
    function at(e){
      var r = svg.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width * 640;
      var i = Math.round((x - PL.l) / (PL.r - PL.l) * (T.length - 1)) + 1;
      i = Math.max(1, Math.min(T.length, i));
      var j = 0;
      while(j < C.length - 1 && C[j + 1][0] < i) j++;
      var v = C[j][1];
      cx.setAttribute('d', 'M' + px(i).toFixed(1) + ' ' + PL.t + 'V' + PL.b);
      cx.style.opacity = 1;
      cd.setAttribute('cx', px(i).toFixed(1));
      cd.setAttribute('cy', py(v).toFixed(1));
      cd.style.opacity = 1;
      hint.innerHTML = '상위 <b>' + i.toLocaleString() + '</b>개가 기출의 <b>'
                     + v.toFixed(1) + ' %</b>';
    }
    hit.addEventListener('mousemove', at);
    hit.addEventListener('touchmove', function(e){ if(e.touches[0]) at(e.touches[0]); });
    hit.addEventListener('mouseleave', function(){
      cx.style.opacity = 0; cd.style.opacity = 0;
      hint.innerHTML = '상위 <b>200</b>개가 기출의 <b>37 %</b>';
    });
  }

  function renderNext(pc){
    var todo = [];
    for (var i = 0; i < T.length && todo.length < 200; i++) {
      if (!done[T[i].m]) todo.push(T[i]);
    }
    var box = document.getElementById('next');
    if (!todo.length) {
      box.innerHTML = '<div class="done">1,966개를 다 표시했습니다.</div>';
      return;
    }
    var h = '<div class="lb">다음 목표</div><div class="row">';
    [10, 25, 50, 100].forEach(function(n){
      if (todo.length < n && n !== 10) return;
      var take = todo.slice(0, Math.min(n, todo.length)), w = 0;
      for (var i = 0; i < take.length; i++) w += take[i].q;
      var gain = w / D.tot * 100;
      h += '<button type="button" data-n="' + take.length + '">'
         + '<b>+' + gain.toFixed(1) + '%p</b>'
         + take.length + '개 더 · 누적 <em>' + (pc + gain).toFixed(1) + '%</em></button>';
    });
    box.innerHTML = h + '</div>';
  }

  function filtered(){
    var q = kw.trim().toLowerCase();
    return T.filter(function(x){
      if (subj && x.s !== subj) return false;
      if (kind && x.k !== kind) return false;
      if (onlyTodo && done[x.m]) return false;
      if (q && (x.m + ' ' + x.c + ' ' + x.f).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
  }

  function esc(s){ return (s || '').replace(/[<>&"]/g, function(c){
    return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]; }); }

  /* 2021~2026 여섯 칸. 높이는 그해 출제 수, 색은 최근일수록 진하게.
     빈 해는 1px 밑줄만 남겨 「그 해엔 안 나왔다」를 말한다. */
  function yrsHtml(x){
    if(!x.y) return '';
    var mx = Math.max.apply(null, x.y) || 1, h = '<span class="yrs" aria-hidden="true">';
    for(var i = 0; i < x.y.length; i++){
      var v = x.y[i], ht = v === 0 ? 1 : Math.round(3 + v / mx * 8), st = ' style="height:';
      /* 클래스 이름을 변수에 담아 이어 붙이면 파일에 `class="on"` 이 한 번도 안
         적힌다. 검사기도 사람도 그것을 못 찾는다. 그대로 적는다. */
      if(v === 0)                  h += '<i' + st + '1px"></i>';
      else if(D.years[i] >= 2025)  h += '<i class="hot"' + st + ht + 'px"></i>';
      else                         h += '<i class="on"' + st + ht + 'px"></i>';
    }
    return h + '</span>';
  }

  function goHtml(x){
    var h = '<div class="go"><div class="lb">이어가기</div><div class="qs">';
    for (var i = 0; i < x.n.length; i++) {
      h += '<a href="' + esc(x.n[i][1]) + '" target="_blank" rel="noopener">'
         + esc(x.n[i][0]) + ' ↗</a>';
    }
    h += '</div><div class="jump">';
    if (x.g) {
      h += '<a href="' + MEMO + '#g=' + esc(x.g) + '">암기 은행'
         + (x.gt ? ' <em>' + esc(x.gt) + '</em>' : '') + ' →</a>';
    }
    if (x.t3) {
      h += '<a href="' + LAB + '#topic=' + esc(x.t3) + '">3D 실습장'
         + (x.t3n ? ' <em>' + esc(x.t3n) + '</em>' : '') + ' →</a>';
    }
    return h + '</div></div>';
  }

  /* 빈도 구간. 30~15회가 13개뿐인데 1~2회 1,640개와 같은 무게로 이어져
     있었다. 경계에 이름을 붙인다. T 는 이미 빈도 내림차순이므로 거르기가
     걸려도 순서가 흐트러지지 않는다. */
  var BAND = [[15, '자주'], [8, '꾸준히'], [3, '가끔'], [0, '드물게']];
  function bandOf(q){
    for (var i = 0; i < BAND.length; i++) if (q >= BAND[i][0]) return i;
    return BAND.length - 1;
  }
  function bandHtml(bi, rows){
    var lo = BAND[bi][0], hi = bi ? BAND[bi - 1][0] - 1 : null, n = 0;
    for (var i = 0; i < rows.length; i++) if (bandOf(rows[i].q) === bi) n++;
    var range = hi ? (lo || 1) + '~' + hi + '회' : lo + '회 이상';
    return '<li class="band" aria-hidden="true"><b>' + BAND[bi][1] + '</b>'
         + '<span>' + range + ' · ' + n.toLocaleString() + '개</span><i></i></li>';
  }

  function render(){
    var rows = filtered(), part = rows.slice(0, shown), h = '', band = -1;
    for (var i = 0; i < part.length; i++) {
      var x = part[i], d = !!done[x.m], b = bandOf(x.q);
      if (b !== band) { h += bandHtml(b, rows); band = b; }
      h += '<li class="' + (d ? 'done' : '') + '" data-m="' + esc(x.m) + '">'
        + '<div class="hd" role="button" tabindex="0" aria-expanded="false">'
        +   '<span class="rk mono">' + (x.i + 1) + '</span>'
        +   '<span class="fqwrap"><span class="fq mono"><b>' + x.q + '</b>회</span>'
        +     '<span class="fqbar" style="width:' + Math.max(6, x.q / D.qmax * 100).toFixed(0) + '%"></span></span>'
        +   '<span class="ttl"><span class="m">' + esc(x.m) + '</span>'
        +     '<span class="sub"><span class="chip">' + esc(D.short[x.s] || x.s) + '</span>'
        +     '<span class="chip' + (x.k === '공식형' ? ' f' : '') + '">' + esc(x.k) + '</span>'
        +     yrsHtml(x) + '</span></span>'
        +   '<button class="ck" type="button" aria-label="외웠음 표시" aria-pressed="' + d + '">✓</button>'
        + '</div>'
        + '<div class="bd"><p class="chp">' + esc(x.c) + '</p>'
        +   '<div class="q">' + x.f + '</div>'
        +   (x.fig || '')
        +   '<div class="a">' + x.b + '</div>'
        +   goHtml(x)
        + '</div></li>';
    }
    list.innerHTML = h;
    empty.hidden = rows.length > 0;
    moreB.hidden = rows.length <= shown;
    moreB.textContent = '더 보기 (' + (rows.length - shown).toLocaleString() + '개 남음)';
    var w = 0; for (var j = 0; j < rows.length; j++) w += rows[j].q;
    cntEl.textContent = rows.length.toLocaleString() + '개 · 기출 비중 '
                      + (D.tot ? (w / D.tot * 100).toFixed(1) : 0) + '%';
  }

  function typeset(el){
    if (!window.renderMathInElement) return;
    try {
      window.renderMathInElement(el, {
        delimiters: [{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],
        throwOnError: false
      });
    } catch(e){}
  }

  function mkTabs(id, items, get, set){
    var box = document.getElementById(id), h = '';
    items.forEach(function(it){
      h += '<button class="tab" type="button" data-v="' + esc(it[0]) + '" aria-pressed="'
         + (get() === it[0]) + '">' + esc(it[1]) + '</button>';
    });
    box.innerHTML = h;
    box.addEventListener('click', function(e){
      var b = e.target.closest('.tab'); if (!b) return;
      set(b.dataset.v); shown = PAGE;
      box.querySelectorAll('.tab').forEach(function(t){
        t.setAttribute('aria-pressed', t.dataset.v === get());
      });
      render();
    });
  }

  var subTabs = [['', '전체']].concat(D.order.map(function(s){ return [s, D.short[s] || s]; }));
  mkTabs('subTabs', subTabs, function(){ return subj; }, function(v){ subj = v; });
  mkTabs('kindTabs', [['', '모든 유형'], ['단답형', '단답형'], ['공식형', '공식형'], ['용어형', '용어형'],
                      ['__todo', '안 외운 것만']],
         function(){ return onlyTodo ? '__todo' : kind; },
         function(v){ if (v === '__todo') { onlyTodo = !onlyTodo; } else { kind = v; onlyTodo = false; } });

  document.getElementById('q').addEventListener('input', function(e){
    kw = e.target.value; shown = PAGE; render();
  });
  moreB.addEventListener('click', function(){ shown += PAGE; render(); });

  /* 시험까지 며칠 남았고 하루 몇 개씩 해야 하는지. 「다음 10개」가 얼마를 벌어
     주는지는 알려 줘도, 그것을 언제까지 몇 번 해야 하는지는 안 알려 준다. */
  var DDAY = 'safety_focus_dday';
  function renderPlan(){
    var el = document.getElementById('planOut'), inp = document.getElementById('dday');
    var v = inp.value;
    if(!v){ el.textContent = '날짜를 넣으면 하루 몇 개씩 해야 하는지 계산합니다.'; return; }
    var t = new Date(v + 'T00:00:00'), now = new Date();
    now.setHours(0,0,0,0);
    var days = Math.round((t - now) / 86400000);
    var todo = 0, w = 0;
    for(var i = 0; i < T.length; i++){ if(!done[T[i].m]){ todo++; w += T[i].q; } }
    if(days < 0){ el.innerHTML = '<span class="warn">시험일이 지났습니다.</span>'; return; }
    if(days === 0){ el.innerHTML = '<b>오늘</b>입니다. 남은 ' + todo.toLocaleString() + '개는 오늘 몫이 아닙니다 — 체크한 것만 보고 가십시오.'; return; }
    var per = Math.ceil(todo / days);
    var g326 = Math.max(0, 326 - (T.length - todo));
    var msg = '<b>' + days + '일</b> 남았습니다. 남은 ' + todo.toLocaleString() + '개를 다 하려면 하루 <b>' + per.toLocaleString() + '개</b>';
    if(g326 > 0){
      msg += ' · 상위 326개(기출 47 %)까지만 하면 하루 <b>' + Math.ceil(g326 / days) + '개</b>';
    } else {
      msg += ' · 상위 326개는 이미 넘었습니다';
    }
    el.innerHTML = msg;
  }
  (function(){
    var inp = document.getElementById('dday');
    try{ var v = localStorage.getItem(DDAY); if(v) inp.value = v; }catch(e){}
    inp.addEventListener('change', function(){
      try{ localStorage.setItem(DDAY, inp.value); }catch(e){}
      renderPlan();
    });
  }());

  document.getElementById('next').addEventListener('click', function(e){
    var b = e.target.closest('button'); if (!b) return;
    onlyTodo = true; kind = ''; subj = ''; kw = '';
    document.getElementById('q').value = '';
    shown = Math.max(PAGE, Number(b.dataset.n) || PAGE);
    document.querySelectorAll('#subTabs .tab').forEach(function(t){
      t.setAttribute('aria-pressed', t.dataset.v === '');
    });
    document.querySelectorAll('#kindTabs .tab').forEach(function(t){
      t.setAttribute('aria-pressed', t.dataset.v === '__todo');
    });
    render();
    document.getElementById('list').scrollIntoView({block:'start'});
  });

  list.addEventListener('click', function(e){
    if (e.target.closest('.go')) return;          /* 이어가기 링크는 그대로 */
    var li = e.target.closest('li'); if (!li) return;
    if (e.target.closest('.ck')) {
      var m = li.dataset.m;
      if (done[m]) delete done[m]; else done[m] = 1;
      save(); li.classList.toggle('done');
      li.querySelector('.ck').setAttribute('aria-pressed', !!done[m]);
      renderProg();
      return;
    }
    if (e.target.closest('.hd')) {
      var wasOpen = li.classList.contains('open');
      /* 둘을 동시에 펼치면 화면에 벽이 둘이다. 앞엣것을 닫는다. */
      var open = list.querySelectorAll('li.open');
      for (var i = 0; i < open.length; i++) {
        if (open[i] === li) continue;
        open[i].classList.remove('open');
        open[i].querySelector('.hd').setAttribute('aria-expanded', 'false');
      }
      li.classList.toggle('open');
      li.querySelector('.hd').setAttribute('aria-expanded', !wasOpen);
      if (!wasOpen) {
        typeset(li.querySelector('.bd'));
        /* 위엣것이 접히면서 페이지가 위로 당겨진다. 제목을 다시 눈앞에 놓는다. */
        var top = li.getBoundingClientRect().top;
        if (top < 0 || top > window.innerHeight - 120) {
          li.scrollIntoView({block: 'start', behavior: 'smooth'});
        }
      }
    }
  });
  list.addEventListener('keydown', function(e){
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var hd = e.target.closest('.hd'); if (!hd) return;
    e.preventDefault(); hd.click();
  });

  (function(){
    function cur(){ return document.documentElement.getAttribute('data-theme') || 'dark'; }
    function sync(){
      document.querySelectorAll('.bTheme').forEach(function(b){
        var d = cur() === 'dark';
        b.textContent = d ? '밝은 모드' : '어두운 모드';
        b.setAttribute('aria-pressed', d);
      });
    }
    document.querySelectorAll('.bTheme').forEach(function(b){
      b.addEventListener('click', function(){
        var t = cur() === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', t);
        try { localStorage.setItem('safety_theme', t); } catch(e){}
        sync();
      });
    });
    sync();
  }());

  renderProg(); render();
}());
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
