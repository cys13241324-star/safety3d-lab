# -*- coding: utf-8 -*-
"""`focus.html` 이 성한지 본다 — 지어낸 파일이라 눈으로는 못 본다.

    python tools/focuscheck.py

`build_focus.py` 가 3.6 MB 짜리 한 장을 만든다. 회차 원문에서 해설을 그대로
실어 오고, 링크를 세 갈래로 달고, 표 스타일을 걷어 낸다. 그 과정에서 조용히
망가질 수 있는 자리를 일곱 가지로 나눠 본다.

  ① 자료      window.__D 가 JSON 으로 읽히는가 · 주제 수와 가중합이 맞는가
  ② 해설      태그가 짝을 이루는가 (1,966 개 전수)
  ③ 링크      회차 파일 · 암기 묶음 id · 3D 주제 키가 대상에 실재하는가
  ④ 스타일    걷어야 할 인라인이 남았는가 · text-align 은 살아 있는가
  ⑤ 스크립트  괄호가 닫히는가
  ⑥ CSS       덮어쓰기 규칙이 들어 있는가
  ⑦ 클래스 짝  마크업과 CSS 가 서로 붙어 있는가
  ⑧ 내용      링크를 따라가 그 문항이 정말 그 주제인가 (--deep · 몇 초 걸린다)

⑦ 은 화면을 못 보는 자리에서 눈 대신 쓰는 것이다. 클래스를 썼는데 규칙이 없으면
붙이려던 모양이 안 붙고, 규칙만 있고 안 쓰면 지우다 만 것이거나 이름을 잘못 적은
것이다. 스타일이 아니라 스크립트 손잡이로만 쓰는 이름(.bTheme)은 규칙이 없는
것이 정상이라, 선택자로 쓰였는지를 보고 가른다.

경고다 — 종료코드는 항상 0. 잡힌 것은 보고 판단한다.
"""
import collections
import json
import os
import pathlib
import re
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

BS = chr(92)
HERE = pathlib.Path(__file__).parent.resolve()
LAB = HERE.parent
CBT = next((p for p in (LAB.parent / "sanup-safety-cbt",
                        LAB.parent.parent / "sanup-safety-cbt")
            if p.exists()), LAB.parent / "sanup-safety-cbt")
VOID = {"br", "img", "hr", "input", "meta", "link"}
bad = 0


def say(ok, msg):
    global bad
    if not ok:
        bad += 1
    print("  %s %s" % ("·" if ok else "!!", msg))


def tags_ok(h):
    """여는 태그와 닫는 태그가 짝을 이루는가."""
    st = []
    for m in re.finditer(r"<\s*(/?)([a-zA-Z][" + BS + r"w]*)[^>]*?(/?)>", h or ""):
        close, tag, self_ = m.group(1), m.group(2).lower(), m.group(3)
        if tag in VOID or self_:
            continue
        if close:
            if st and st[-1] == tag:
                st.pop()
            else:
                return False
        else:
            st.append(tag)
    return not st


def balance(t):
    """인라인 스크립트의 괄호. 정규식 리터럴은 먼저 지운다 — 안의 따옴표에 걸린다."""
    t = re.sub(r"/" + BS + r"[[^" + BS + r"]" + BS + r"n]*" + BS + r"][gimsuy]*",
               " RE ", t)
    st, i = [], 0
    while i < len(t):
        c = t[i]
        if c in "'\"":
            q = c
            i += 1
            while i < len(t) and t[i] != q:
                if t[i] == BS:
                    i += 1
                i += 1
        elif c == "/" and i + 1 < len(t) and t[i + 1] == "/":
            while i < len(t) and t[i] != "\n":
                i += 1
        elif c == "/" and i + 1 < len(t) and t[i + 1] == "*":
            j = t.find("*/", i)
            if j < 0:
                return "닫히지 않은 주석"
            i = j + 1
        elif c in "([{":
            st.append(c)
        elif c in ")]}":
            if not st:
                return "여는 짝 없이 닫힘"
            st.pop()
        i += 1
    return "" if not st else "안 닫힌 괄호 " + "".join(st)


CANON = {"화학설비위험방지": "화학설비위험방지기술", "기계위험방지": "기계위험방지기술",
         "전기위험방지": "전기위험방지기술", "인간공학": "인간공학 및 시스템안전공학"}


def _bank(src):
    """회차 파일에서 D 객체 한 덩어리를 떠 온다."""
    m = re.search(r"(?:const|let|var)" + BS + r"s+D" + BS + r"s*=" + BS + r"s*{", src)
    if not m:
        return None
    st, d = m.end() - 1, 0
    for j in range(st, len(src)):
        if src[j] in "[{":
            d += 1
        elif src[j] in "]}":
            d -= 1
            if d == 0:
                try:
                    return json.loads(src[st:j + 1])
                except ValueError:
                    return None
    return None


def deep(T):
    """링크를 실제로 따라간다 — 구조가 아니라 **내용**이 맞는지.

    ③ 은 가리키는 파일이 있는지까지만 본다. 그 번호의 문항이 정말 그 주제인지는
    회차를 열어 봐야 안다. 24회차를 다 읽으므로 몇 초 걸린다.
    """
    print("")
    print("⑧ 링크를 따라간 내용 (--deep)")
    rounds = {}
    for f in sorted(CBT.glob("CBT_*/*_CBT.html")):
        m = re.search(r"CBT_(" + BS + r"d{4})_(" + BS + r"d)회", str(f))
        if not m or (m.group(1), m.group(2)) in rounds:
            continue
        D2 = _bank(f.read_text(encoding="utf-8", errors="ignore"))
        if D2:
            rounds[(m.group(1), m.group(2))] = D2

    n = wrong = miss = 0
    ex = []
    for x in T:
        for label, url in x["n"]:
            n += 1
            m = re.match(r"https://[^/]+/sanup-safety-cbt/(.+?)/(.+?)#q(" + BS + r"d+)$", url)
            rm = re.search(r"CBT_(" + BS + r"d{4})_(" + BS + r"d)회",
                           urllib.parse.unquote(m.group(1)))
            D2 = rounds.get((rm.group(1), rm.group(2)))
            if not D2:
                miss += 1
                continue
            q = next((z for z in D2["q"] if str(z.get("n")) == m.group(3)), None)
            c = (D2.get("cards") or {}).get(q.get("card")) if q else None
            if not c:
                miss += 1
                continue
            subj = CANON.get((c.get("subject") or "").strip(),
                             (c.get("subject") or "").strip())
            if (c.get("mid") or "").strip() != x["m"] or subj != x["s"]:
                wrong += 1
                if len(ex) < 5:
                    ex.append("%s -> %s (그 문항은 %s)" % (x["m"], label, c.get("mid")))
    say(not wrong and not miss,
        "링크 %d개를 따라갔다 — 주제·과목이 어긋난 것 %d · 문항을 못 찾은 것 %d"
        % (n, wrong, miss))
    for e in ex:
        print("      " + e)

    re2 = {}
    for D2 in rounds.values():
        for c in (D2.get("cards") or {}).values():
            mid = (c.get("mid") or "").strip()
            if not mid:
                continue
            subj = CANON.get((c.get("subject") or "").strip(),
                             (c.get("subject") or "").strip())
            re2[(subj, mid)] = re2.get((subj, mid), 0) + int(c.get("fq") or 1)
    d = [x for x in T if re2.get((x["s"], x["m"])) != x["q"]]
    say(not d, "출제빈도를 다시 세어 어긋난 주제 %d개" % len(d))


def main():
    p = LAB / "focus.html"
    if not p.exists():
        print("focus.html 이 없다. python tools/build_focus.py 먼저.")
        return
    s = p.read_text(encoding="utf-8")
    mb = len(s.encode()) / 1024 / 1024
    print("focus.html %.2f MB\n" % mb)

    # ① 자료
    print("① 자료")
    m = re.search(r"window" + BS + r".__D=(.*?);</script>", s, re.S)
    if not m:
        say(False, "window.__D 를 못 찾았다")
        return
    try:
        D = json.loads(m.group(1))
    except ValueError as e:
        say(False, "JSON 이 깨졌다: %s" % str(e)[:80])
        return
    T = D["t"]
    say(True, "주제 %d개 · 회차 %d · 문항 %d · 가중합 %d"
        % (len(T), D["nr"], D["nq"], D["tot"]))
    say(sum(x["q"] for x in T) == D["tot"], "가중합이 주제별 합과 맞는가")
    say(all(x["f"].strip() and x["b"].strip() for x in T), "질문·해설이 빈 주제가 없는가")
    say(T == sorted(T, key=lambda x: -x["q"]) or
        all(T[i]["q"] >= T[i + 1]["q"] for i in range(len(T) - 1)),
        "빈도 내림차순으로 서 있는가")

    # ② 해설
    print("\n② 해설 태그")
    nb = sum(1 for x in T if not (tags_ok(x["f"]) and tags_ok(x["b"])))
    say(nb == 0, "태그가 어긋난 주제 %d개" % nb)

    # ③ 링크
    print("\n③ 링크")
    miss = set()
    for x in T:
        for _, u in x["n"]:
            mm = re.match(r"https://[^/]+/sanup-safety-cbt/(.+?)/(.+?)#q" + BS + r"d+$", u)
            if not mm:
                miss.add(u)
                continue
            f = CBT / urllib.parse.unquote(mm.group(1)) / urllib.parse.unquote(mm.group(2))
            if not f.exists():
                miss.add(str(f))
    say(not miss, "회차 파일 — 없는 대상 %d개" % len(miss))

    memo = LAB / "memo.html"
    if memo.exists():
        mm = re.search(r'<script[^>]*id="bank"[^>]*>(.*?)</script>',
                       memo.read_text(encoding="utf-8"), re.S)
        ids = {g["id"] for g in json.loads(mm.group(1))["methods"]} if mm else set()
        used = {x["g"] for x in T if x["g"]}
        say(not (used - ids), "암기 묶음 id %d종 — memo 에 없는 것 %d개"
            % (len(used), len(used - ids)))

    lab = LAB / "lab.html"
    if lab.exists():
        ls = lab.read_text(encoding="utf-8")
        keys = set()
        for t in re.findall(r"topics" + BS + r"s*:" + BS + r"s*" + BS + r"[([^" + BS + r"]]*)" + BS + r"]", ls):
            keys |= set(re.findall(r"'([^']+)'", t))
        used3 = {x["t3"] for x in T if x["t3"]}
        say(not (used3 - keys), "3D 주제 키 %d종 — lab 에 없는 것 %s"
            % (len(used3), sorted(used3 - keys) or "0개"))

    # ④ 스타일
    print("\n④ 표 스타일")
    left = collections.Counter()
    for x in T:
        for st_ in re.findall(r'style="([^"]*)"', x["b"] or ""):
            for d in st_.split(";"):
                if d.strip():
                    left[d.split(":")[0].strip()] += 1
    extra = {k: v for k, v in left.items() if k != "text-align"}
    say(not extra, "걷어야 할 인라인이 남았는가 — %s" % (extra or "없음"))
    say(left.get("text-align", 0) > 0, "text-align 은 살아 있는가 (%d개)" % left.get("text-align", 0))
    tw = sum(x["b"].count('class="tw"') for x in T)
    tb = sum(x["b"].count("<table") for x in T)
    say(tw == tb, "가로 스크롤 감싸개 %d개 = 표 %d개" % (tw, tb))

    # ⑤ 스크립트
    print("\n⑤ 스크립트")
    blocks = re.findall(r"<script>(.*?)</script>", s, re.S)
    r = balance(blocks[-1]) if blocks else "스크립트가 없다"
    say(not r, "괄호 균형 — %s" % (r or "OK"))

    # ⑥ CSS
    print("\n⑥ CSS 덮어쓰기")
    css = s[s.find("<style>"):s.find("</style>")]
    for k, why in ((".bd .a th{background:var(--panel2)!important", "표 머리 배경"),
                   ("border:1px solid var(--line-soft)!important", "표 테두리"),
                   (".bd .a .tw{", "가로 스크롤"),
                   (".bd .a .ch{", "해설 소제목"),
                   # 이 사이트는 어두운 판이 기본이고 밝은 판을 덮어쓴다(index.html 과 같다).
                   # 그래서 찾을 것은 dark 가 아니라 light 다.
                   (':root[data-theme="light"]', "밝은 판 덮어쓰기")):
        say(k in css, "%s 규칙" % why)
    # 테마 기억은 <head> 부트 스크립트에 있다. 본문 전체에서 본다.
    say("safety_theme" in s, "형제 페이지와 같은 테마 기억(safety_theme)")

    # ⑦ 그림은 **문서 전체**에서 봐야 한다. figcheck.py 는 그림을 한 번씩만
    # 보는데, 한 주제 이름이 과목 둘에 걸리면(「사다리식 통로의 구조」가 건설과
    # 기계에 있다) 같은 그림이 두 번 찍히고 그때서야 id 가 겹친다.
    print("\n⑦ 그림")
    figs = [x for x in T if x.get("fig")]
    say(True, "그림이 붙은 주제 %d개 · 기출 비중 %.1f %%"
        % (len(figs), sum(x["q"] for x in figs) / D["tot"] * 100))
    body = "".join(x["fig"] for x in figs)
    ids = re.findall(r'<marker id="([A-Za-z0-9_]+)"', body)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    say(not dup, "화살촉 id %d개 — 겹치는 것 %s" % (len(ids), dup or "없음"))
    used = set(re.findall(r"url\(#([A-Za-z0-9_]+)\)", body))
    say(not (used - set(ids)), "가리키는 곳이 없는 url(#id) — %s"
        % (sorted(used - set(ids)) or "없음"))
    svg = body.count("<svg")
    say(svg == body.count("</svg>") and svg == body.count("<figure"),
        "svg %d개 = figure %d개" % (svg, body.count("<figure")))

    # ⑧ 마크업과 CSS 가 서로 붙어 있는가
    print("\n⑧ 클래스 짝")
    # 클래스는 세 군데에서 나온다 — 마크업 · 스크립트가 짜는 문자열 · 해설 HTML.
    # 해설은 JSON 안에 있어 파일 본문을 훑는 것만으로는 안 잡힌다.
    # perSub·topRow 처럼 대문자가 섞인 이름이 있다. 소문자만 받으면 앞부분에서 잘린다.
    NAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
    names = set()

    def eat(txt):
        for m in re.finditer(r"""class=["']([^"']*)["']""", txt or ""):
            for w in m.group(1).split():
                if NAME.match(w):
                    names.add(w)

    eat(s)
    for x in T:
        # 마크업을 실어 오는 필드를 다 본다. 새 필드를 더하면 여기도 더해야 한다 —
        # fig 를 더하고 잊었더니 figset·hz 가 「안 쓰는 규칙」으로 잡혔다.
        for k in ("b", "f", "fig"):
            eat(x.get(k))
    # 스크립트가 `'chip' + ' f'` 처럼 이어 붙이는 것과 classList 로 다는 것
    for m in re.finditer(r"classList" + BS + r".(?:add|toggle|remove)" + BS + r"(\s*['\"]([^'\"]+)", s):
        if NAME.match(m.group(1)):
            names.add(m.group(1))
    for m in re.finditer(r"['\"]\s([a-zA-Z][a-zA-Z0-9_-]*)['\"]\s*:", s):   # ? ' f' : ''
        names.add(m.group(1))

    ruled = set(re.findall(r"" + BS + r".([a-zA-Z][a-zA-Z0-9_-]*)", css))
    dead = sorted(r for r in ruled if r not in names)
    say(not dead, "규칙만 있고 아무 데서도 안 쓰는 클래스 %d개%s"
        % (len(dead), "  " + str(dead[:8]) if dead else ""))
    # 스타일이 아니라 **스크립트 손잡이**로만 쓰는 이름이 있다(.bTheme 처럼
    # index.html 도 규칙 없이 querySelectorAll 로만 잡는다). 선택자로 쓰였으면
    # 규칙이 없는 것이 정상이다.
    hooks = {m for m in names if ("'." + m + "'") in s or ('".' + m + '"') in s}
    naked = sorted(n for n in names
                   if n not in ruled and n not in hooks and not n.startswith("katex"))
    say(not naked, "쓰는데 규칙이 없는 클래스 %d개%s"
        % (len(naked), "  " + str(naked[:8]) if naked else ""))

    if "--deep" in sys.argv[1:]:
        deep(T)

    print("\n" + ("=== 검사 통과 ===" if not bad else "=== 잡힌 것 %d건 — 보고 판단할 것 ===" % bad))


if __name__ == "__main__":
    main()
