# -*- coding: utf-8 -*-
"""페이지 여섯이 서로 제대로 이어지는지 본다.

    python tools/linkcheck.py

페이지마다 파일 하나로 도는 사이트라 링크가 깨져도 빌드가 알려 주지 않는다.
세 가지를 본다.

  ① 같은 저장소 링크 — 가리키는 파일이 있는가
  ② 해시 — `#topic=` 은 `lab.html` 의 topics 에, `#g=` 는 `memo.html` 의 묶음 id 에,
     `#q<번호>` 는 그 회차 문항 수 안에 드는가
  ③ 회차 저장소 링크 — `sanup-safety-cbt` 의 그 파일이 있는가

경고다 — 종료코드는 항상 0.
"""
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
PAGES = ["index.html", "lab.html", "memo.html", "palace.html",
         "game.html", "reigns.html", "focus.html"]
bad = 0


def say(ok, msg):
    global bad
    if not ok:
        bad += 1
    print("  %s %s" % ("·" if ok else "!!", msg))


def lab_topics():
    s = (LAB / "lab.html").read_text(encoding="utf-8")
    keys = set()
    for t in re.findall(r"topics\s*:\s*\[([^\]]*)\]", s):
        keys |= set(re.findall(r"'([^']+)'", t))
    return keys


def memo_ids():
    s = (LAB / "memo.html").read_text(encoding="utf-8")
    m = re.search(r'<script[^>]*id="bank"[^>]*>(.*?)</script>', s, re.S)
    if not m:
        return set()
    return {g["id"] for g in json.loads(m.group(1))["methods"]}


def round_counts():
    """회차마다 문항이 몇 개인지 — #q<번호> 가 그 안에 드는지 보려면 필요하다."""
    out = {}
    for f in sorted(CBT.glob("CBT_*/*_CBT.html")):
        m = re.search(r"CBT_(\d{4})_(\d)회", str(f))
        if not m:
            continue
        s = f.read_text(encoding="utf-8", errors="ignore")
        mm = re.search(r'"q"\s*:\s*\[', s)
        n = 0
        if mm:
            d = 0
            for j in range(mm.end() - 1, len(s)):
                if s[j] in "[{":
                    d += 1
                elif s[j] in "]}":
                    d -= 1
                    if d == 0:
                        break
            n = s[mm.end() - 1:j + 1].count('{"n":') or s[mm.end() - 1:j + 1].count('{ "n"')
        out[(m.group(1), m.group(2))] = n or 120
    return out


def main():
    tops, gids, rc = lab_topics(), memo_ids(), round_counts()
    print("lab 주제 %d · memo 묶음 %d · 회차 %d\n" % (len(tops), len(gids), len(rc)))

    print("① 같은 저장소 링크")
    for name in PAGES:
        p = LAB / name
        if not p.exists():
            say(False, "%s 이(가) 없다" % name)
            continue
        s = p.read_text(encoding="utf-8")
        hrefs = set(re.findall(r'href="([a-z0-9_]+\.html)[^"]*"', s))
        miss = [h for h in hrefs if not (LAB / h).exists()]
        say(not miss, "%-13s → %s%s"
            % (name, " · ".join(sorted(hrefs)) or "(없음)",
               "   없는 대상 " + str(miss) if miss else ""))

    print("\n② 해시")
    # 소스에 그대로 적힌 것
    for name in PAGES:
        s = (LAB / name).read_text(encoding="utf-8")
        t = set(re.findall(r"#topic=([a-z0-9_]+)", s)) - {""}
        g = set(re.findall(r"#g=([0-9-]+)", s))
        if t:
            say(not (t - tops), "%-13s #topic= %d종 — 없는 것 %s"
                % (name, len(t), sorted(t - tops) or "0개"))
        if g:
            say(not (g - gids), "%-13s #g= %d종 — 없는 것 %s"
                % (name, len(g), sorted(g - gids) or "0개"))

    # 해시를 JS 로 조립하는 두 곳은 소스에 리터럴이 없다. 표를 직접 꺼내 본다.
    s = (LAB / "reigns.html").read_text(encoding="utf-8")
    m = re.search(r"var LAB3D = \{(.*?)\};", s, re.S)
    if m:
        keys = set(re.findall(r"([a-z0-9_]+)\s*:", m.group(1)))
        say(not (keys - tops), "reigns LAB3D %d종 — lab 에 없는 것 %s"
            % (len(keys), sorted(keys - tops) or "0개"))
        deck = s[s.index("var DECK = ["):]
        deck = deck[:deck.index("\n  ];")]
        cards = set(re.findall(r"\n  \{k:'([^']+)'", deck))
        say(not (keys - cards), "reigns LAB3D 가 덱에 없는 키를 가리키는가 — %s"
            % (sorted(keys - cards) or "아니오"))
    else:
        say(False, "reigns 의 LAB3D 표를 못 찾았다")

    p = LAB / "focus.html"
    if p.exists():
        s = p.read_text(encoding="utf-8")
        mm = re.search(r"window\.__D=(.*?);</script>", s, re.S)
        if mm:
            T = json.loads(mm.group(1))["t"]
            t3 = {x["t3"] for x in T if x["t3"]}
            gg = {x["g"] for x in T if x["g"]}
            say(not (t3 - tops), "focus #topic= %d종 — 없는 것 %s"
                % (len(t3), sorted(t3 - tops) or "0개"))
            say(not (gg - gids), "focus #g= %d종 — 없는 것 %s"
                % (len(gg), sorted(gg - gids) or "0개"))

    print("\n③ 회차 저장소 링크")
    s = (LAB / "focus.html").read_text(encoding="utf-8")
    urls = set(re.findall(r'https://[^"\\ ]+/sanup-safety-cbt/[^"\\ ]+#q\d+', s))
    missf, missq = set(), []
    for u in urls:
        m = re.match(r"https://[^/]+/sanup-safety-cbt/(.+?)/(.+?)#q(\d+)$", u)
        if not m:
            missf.add(u)
            continue
        folder = urllib.parse.unquote(m.group(1))
        fname = urllib.parse.unquote(m.group(2))
        if not (CBT / folder / fname).exists():
            missf.add(folder + "/" + fname)
            continue
        mm = re.search(r"CBT_(\d{4})_(\d)회", folder)
        n = rc.get((mm.group(1), mm.group(2)), 120) if mm else 120
        if int(m.group(3)) > n:
            missq.append("%s #q%s (문항 %d개)" % (folder, m.group(3), n))
    say(not missf, "가리키는 파일 — 없는 것 %d개" % len(missf))
    say(not missq, "문항 번호가 범위를 넘는 것 %d개%s"
        % (len(missq), "  " + str(missq[:3]) if missq else ""))
    print("  · 회차 링크 %d개를 훑었다" % len(urls))

    print("\n" + ("=== 검사 통과 ===" if not bad else "=== 잡힌 것 %d건 ===" % bad))


if __name__ == "__main__":
    main()
