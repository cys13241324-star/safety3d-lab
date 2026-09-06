# -*- coding: utf-8 -*-
"""클래스가 마크업과 CSS 양쪽에 붙어 있는가 — 페이지 여섯 전부.

    python tools/classcheck.py              여섯 페이지
    python tools/classcheck.py reigns.html  한 장만
    python tools/classcheck.py --dead       안 쓰는 규칙까지 (헛걸림이 많다)
    python tools/classcheck.py --list       잡힌 이름을 전부 편다

**기본은 「쓰는데 규칙이 없다」만 낸다.** 그쪽은 탐지가 정확하다 — 마크업에 적힌
이름과 CSS 에 적힌 이름을 맞대 보면 되기 때문이다.

반대쪽(「규칙만 있고 안 쓴다」)은 `--dead` 로 따로 켠다. 손으로 쓴 페이지는
클래스를 스크립트가 이런저런 방식으로 달아서(삼항 · 템플릿 문자열 · 계산된 이름)
여기서 다 못 본다. `reigns.html` 의 `.ok` 와 `.no` 가 그 예다 — 실제로 쓰는데
「안 쓴다」고 걸린다. 지어낸 페이지(`focus.html`)에서는 양쪽 다 믿을 만하다.

클래스는 세 군데에서 나온다. 마크업, 스크립트가 이어 붙이는 문자열
(`'chip' + (x.k === '공식형' ? ' f' : '')`), 그리고 JSON 안에 실려 오는 HTML.
한 군데만 훑으면 멀쩡한 것을 「안 쓴다」고 잡는다.

스타일이 아니라 **스크립트 손잡이**로만 쓰는 이름이 있다(`.bTheme` 은 형제
페이지도 규칙 없이 `querySelectorAll` 로만 잡는다). 선택자로 쓰였으면 규칙이
없는 것이 정상이라 빼고 센다.

경고다 — 종료코드는 항상 0. 잡힌 것은 보고 판단한다. 특히 `.katex` 처럼 바깥
스타일시트가 주는 이름과, 조건에 따라 붙는 이름은 여기서 걸릴 수 있다.
"""
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

BS = chr(92)
HERE = pathlib.Path(__file__).parent.resolve()
LAB = HERE.parent
PAGES = ["index.html", "lab.html", "memo.html", "palace.html",
         "game.html", "reigns.html", "focus.html"]
NAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
# 바깥에서 오는 이름 — 여기서 규칙이 없는 것이 정상이다
OUTSIDE = ("katex", "mord", "mrel", "mbin", "mopen", "mclose", "mpunct")


def names_in(text, out):
    """class="a b" · class='a b' · JSON 안의 class=\\"a b\\" · className = 'a b' 를 다 본다."""
    pats = (r"""class=["']([^"']*)["']""",
            r"""class=""" + BS + BS + r'"([^' + BS + BS + r'"]*)' + BS + BS + r'"',
            r"""className\s*[+]?=\s*["']([^"']*)["']""")
    for pat in pats:
        for m in re.finditer(pat, text or ""):
            for w in m.group(1).split():
                if NAME.match(w):
                    out.add(w)


def scan(path, verbose=False):
    s = path.read_text(encoding="utf-8")
    css = "".join(re.findall(r"<style>(.*?)</style>", s, re.S))
    if not css:
        print("  %-14s <style> 가 없다" % path.name)
        return 0

    used = set()
    names_in(s, used)
    # JSON 으로 실려 오는 HTML 안에도 클래스가 있다
    for m in re.finditer(r"<script[^>]*type=\"application/json\"[^>]*>(.*?)</script>",
                         s, re.S):
        names_in(m.group(1), used)
    for m in re.finditer(r"window" + BS + r".__[A-Z]+=(.*?);</script>", s, re.S):
        names_in(m.group(1), used)          # 이스케이프된 채로 한 번
        try:                                 # 풀어서 한 번 더
            names_in(json.dumps(json.loads(m.group(1)), ensure_ascii=False)
                     .encode().decode("unicode_escape"), used)
        except Exception:
            pass
    # classList.add('x') / 이어 붙이는 ' f'
    for m in re.finditer(r"classList" + BS + r".(?:add|toggle|remove)" + BS + r"(" +
                         r"\s*['\"]([^'\"]+)", s):
        if NAME.match(m.group(1)):
            used.add(m.group(1))
    for m in re.finditer(r"['\"]\s([a-zA-Z][a-zA-Z0-9_-]*)['\"]\s*:", s):
        used.add(m.group(1))

    ruled = set(re.findall(r"" + BS + r".([a-zA-Z][a-zA-Z0-9_-]*)", css))
    hooks = {n for n in used if ("'." + n + "'") in s or ('".' + n + '"') in s}

    naked = sorted(n for n in used
                   if n not in ruled and n not in hooks
                   and not n.startswith(OUTSIDE))
    dead = sorted(r for r in ruled if r not in used and not r.startswith(OUTSIDE))

    shown = naked + (dead if SHOW_DEAD else [])
    mark = "  " if not shown else "!!"
    print("%s%-14s 쓰는 이름 %3d · 규칙 %3d   규칙 없음 %2d%s"
          % (mark, path.name, len(used), len(ruled), len(naked),
             " · 안 쓰는 규칙 %2d" % len(dead) if SHOW_DEAD else ""))
    if naked:
        print("      규칙 없음: " + " · ".join(naked if verbose else naked[:10])
              + ("" if verbose or len(naked) <= 10 else " …"))
    if dead and SHOW_DEAD:
        print("      안 쓰는 규칙: " + " · ".join(dead if verbose else dead[:10])
              + ("" if verbose or len(dead) <= 10 else " …"))
    return len(shown)


SHOW_DEAD = False


def main():
    global SHOW_DEAD
    SHOW_DEAD = "--dead" in sys.argv[1:]
    a = [x for x in sys.argv[1:] if x not in ("--list", "--dead")]
    verbose = "--list" in sys.argv[1:]
    targets = [LAB / x for x in (a or PAGES)]
    print("클래스 짝 검사 — 쓰는데 규칙이 없는가 · 규칙만 있고 안 쓰는가\n")
    total = 0
    for p in targets:
        if not p.exists():
            print("  %-14s 없다" % p.name)
            continue
        total += scan(p, verbose)
    print("\n" + ("=== 검사 통과 ===" if not total
                  else "=== 잡힌 것 %d건 — 보고 판단할 것 ===" % total))


if __name__ == "__main__":
    main()
