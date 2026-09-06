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
            e = topics.setdefault(key, {"fq": 0, "q": [], "kind": c.get("kind", ""),
                                        "ch": c.get("chapter", ""),
                                        "front": "", "back": ""})
            e["q"].append((y, r, q.get("n")))
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
        data.append({"i": i, "s": subj, "m": mid, "q": v["fq"], "k": v["kind"],
                     "c": v["ch"], "f": slim(v["front"]), "b": slim(v["back"]),
                     "n": [["%s %s회 #%s" % (y, r, n), cbt_url(y, r, n)] for y, r, n in qs],
                     "g": g[0], "gt": g[1], "t3": t3, "t3n": t3n})

    per = collections.Counter()
    for d in data:
        per[d["s"]] += d["q"]
    marks = [(n, round(sum(d["q"] for d in data[:n]) / tot * 100, 1))
             for n in (50, 100, 200, 326, 500, 800)]

    payload = json.dumps({"t": data, "tot": tot, "nq": nq, "nr": len(rounds),
                          "per": dict(per), "order": ORDER, "short": SHORT,
                          "ver": VER},
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
.perSub{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:8px;margin-top:16px}
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
li{background:var(--panel);border:1px solid var(--line-soft);border-radius:10px;overflow:hidden}
li.done{border-color:var(--ok);background:var(--ok-soft)}
.hd{display:grid;grid-template-columns:44px 52px 1fr auto;gap:10px;align-items:center;padding:10px 12px;cursor:pointer}
.rk{font-family:var(--mono);font-size:12px;color:var(--dim);text-align:right}
.fq{font-family:var(--mono);font-size:12.5px;color:var(--warn);white-space:nowrap}
.fq b{font-size:15px;font-weight:600}
.ttl{min-width:0}
.ttl .m{font-weight:500;overflow-wrap:anywhere}
.ttl .sub{font-size:11.5px;color:var(--dim);margin-top:2px}
.chip{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:4px;background:var(--panel2);border:1px solid var(--line-soft);color:var(--muted);margin-right:5px}
.chip.f{color:var(--accent);border-color:var(--accent)}
.ck{width:26px;height:26px;border-radius:6px;border:1.5px solid var(--line);background:transparent;color:transparent;cursor:pointer;font-size:15px;line-height:1;flex:none}
li.done .ck{border-color:var(--ok);color:var(--ok)}
.bd{display:none;padding:0 14px 14px 14px;border-top:1px solid var(--line-soft)}
li.open .bd{display:block}
.bd .q{font-weight:600;margin:12px 0 8px}
.bd .a{color:var(--muted);font-size:14px;line-height:1.7}
.bd .a strong{color:var(--text)}
.bd .a u{text-decoration:none;border-bottom:1px solid var(--warn-line);color:var(--text)}
.bd .a ul{list-style:disc;padding-left:20px;margin:6px 0}
/* 회차 원문이 밝은 화면을 전제로 한 인라인 색을 달고 온다(th 배경 #f1f5f9,
   테두리 #cbd5e1). 어두운 판에서 흰 바탕에 흰 글씨가 되므로 덮어쓴다. */
.bd .a table{border-collapse:collapse!important;margin:10px 0!important;font-size:13px!important}
.bd .a td,.bd .a th{border:1px solid var(--line-soft)!important;padding:5px 9px!important;vertical-align:middle}
.bd .a th{background:var(--panel2)!important;color:var(--text)}
.bd .a td{color:var(--muted)}
.bd .a td u,.bd .a th u{color:var(--text)}
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
.empty{text-align:center;color:var(--dim);padding:40px 0}
footer{margin-top:36px;color:var(--dim);font-family:var(--mono);font-size:11.5px;line-height:1.7}
@media (max-width:560px){
  .wrap{padding:20px 12px 80px}
  h1{font-size:26px}
  .hd{grid-template-columns:38px 46px 1fr auto;gap:8px;padding:9px 10px}
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
    <div class="perSub" id="perSub"></div>
  </section>

  <div class="ctl">
    <div class="tabs" id="subTabs"></div>
  </div>
  <div class="ctl">
    <div class="tabs" id="kindTabs"></div>
    <input type="search" id="q" placeholder="주제 검색" aria-label="주제 검색">
    <span class="cnt" id="cnt"></span>
  </div>

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

  function render(){
    var rows = filtered(), part = rows.slice(0, shown), h = '';
    for (var i = 0; i < part.length; i++) {
      var x = part[i], d = !!done[x.m];
      h += '<li class="' + (d ? 'done' : '') + '" data-m="' + esc(x.m) + '">'
        + '<div class="hd" role="button" tabindex="0" aria-expanded="false">'
        +   '<span class="rk mono">' + (x.i + 1) + '</span>'
        +   '<span class="fq mono"><b>' + x.q + '</b>회</span>'
        +   '<span class="ttl"><span class="m">' + esc(x.m) + '</span>'
        +     '<span class="sub"><span class="chip">' + esc(D.short[x.s] || x.s) + '</span>'
        +     '<span class="chip' + (x.k === '공식형' ? ' f' : '') + '">' + esc(x.k) + '</span>'
        +     esc(x.c) + ' · ' + x.n.length + '문항 출제</span></span>'
        +   '<button class="ck" type="button" aria-label="외웠음 표시" aria-pressed="' + d + '">✓</button>'
        + '</div>'
        + '<div class="bd"><div class="q">' + x.f + '</div><div class="a">' + x.b + '</div>'
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
      li.classList.toggle('open');
      li.querySelector('.hd').setAttribute('aria-expanded', !wasOpen);
      if (!wasOpen) typeset(li.querySelector('.bd'));
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
