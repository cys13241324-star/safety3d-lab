# -*- coding: utf-8 -*-
"""그림이 성한지 본다 — viewBox 밖으로 나간 좌표 · 겹치는 id · 태그 균형.

    python tools/figcheck.py

`figs_focus.py` 의 그림은 손으로 좌표를 적어 만든다. 그리는 자리에서는 화면을
볼 수 없으므로, 눈 대신 세 가지를 센다.

  · **밖으로 나간 좌표** — viewBox(120×92)를 벗어나면 잘린다. 속성값과 path 의
    M·L 좌표를 둘 다 본다.
  · **겹치는 id** — `<marker>` 는 `url(#id)` 로 부르는데 id 는 문서 전체에서
    유일해야 한다. 그림 여섯이 같은 id 를 쓰면 첫 번째 것만 붙는다.
  · **태그 균형**
  · **글자가 그림 밖으로 나갔는가** — 좌표가 안에 있어도 글자는 밖으로 흐른다.
    한글은 글자당 약 1.0em, 로마자·숫자는 약 0.55em 으로 잡아 폭을 셈하고
    text-anchor 를 따라 왼쪽·오른쪽 끝을 낸다.

경고다 — 종료코드는 항상 0.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve()))
sys.stdout.reconfigure(encoding="utf-8")
import figs_focus as F  # noqa: E402

SELF = {"path", "circle", "rect", "ellipse", "line", "polygon", "polyline",
        "br", "img", "hr", "use", "stop"}
allids = []
for name in F.FIGS:
    h = F.fig_for(name)
    # 태그 균형
    st, ok = [], True
    for m in re.finditer(r"<\s*(/?)([a-zA-Z][\w]*)[^>]*?(/?)>", h):
        cl, tag, sf = m.group(1), m.group(2).lower(), m.group(3)
        if sf or (tag in SELF and not cl):
            continue
        if tag in SELF:
            continue
        if cl:
            if st and st[-1] == tag:
                st.pop()
            else:
                ok = False
                break
        else:
            st.append(tag)
    # 좌표
    out = []
    for m in re.finditer(r'\b(cx|cy|x|y|x1|x2|y1|y2)="(-?[\d.]+)"', h):
        a, v = m.group(1), float(m.group(2))
        lim = 120 if a in ("cx", "x", "x1", "x2") else 92
        if v < -6 or v > lim + 8:
            out.append((a, v))
    # path 안의 좌표도 본다
    for d in re.findall(r'\bd="([^"]+)"', h):
        for nx, ny in re.findall(r"[ML]\s*(-?[\d.]+)\s+(-?[\d.]+)", d):
            if not (-6 <= float(nx) <= 128) or not (-6 <= float(ny) <= 100):
                out.append(("d", (nx, ny)))
    ids = re.findall(r'id="([^"]+)"', h)
    allids += ids
    print("  %-16s %5d자 · figure %d · 태그 %s · 밖 좌표 %s"
          % (name, len(h), h.count("<figure"),
             "OK" if ok and not st else "어긋남", out[:3] or "없음"))
dup = [i for i in set(allids) if allids.count(i) > 1]
print("\n문서 전체 id 중복:", dup or "없음")

def wide(t, size):
    """글자 폭을 어림한다. 한글은 한 칸, 그 밖은 반 칸으로 친다."""
    w = 0.0
    for ch in t:
        if ch == " ":
            w += 0.28
        elif ord(ch) > 0x2000:
            w += 1.0
        else:
            w += 0.55
    return w * size


TXT = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)"[^>]*?font-size="([\d.]+)"'
                 r'[^>]*?text-anchor="(\w+)"[^>]*?>(.*?)</text>', re.S)
over = []
for name in F.FIGS:
    for m in TXT.finditer(F.fig_for(name)):
        x, size = float(m.group(1)), float(m.group(3))
        anchor, t = m.group(4), re.sub(r"<[^>]+>", "", m.group(5))
        w = wide(t, size)
        lo = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        if lo < -1 or lo + w > 121:
            over.append((name, t, round(lo, 1), round(lo + w, 1)))
print("")
print("글자가 그림 밖으로 — %d건" % len(over))
for n, t, a, b in over[:14]:
    print("   · %-16s %-24s %s ~ %s" % (n, t[:24], a, b))
