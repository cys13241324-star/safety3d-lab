# -*- coding: utf-8 -*-
"""이름표가 물건 위에 앉았는가.   사용법: python tools/onobj.py [reigns.html]

   방 같은 큰 배경면은 글자를 얹어도 읽히므로 넓이로 걸러 낸다 —
   4000 px² 이하의 '물건'만 본다."""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import os
P = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reigns.html")
s = io.open(P, encoding="utf-8").read()
i = s.index("var SC = {")
j = s.index("\n  };", i)
sc = s[i:j]
NUM = r"-?\d*\.?\d+"
ASC, DESC = 9.0, 2.5
MAX_AREA = 4000.0

scenes = []
for m in re.finditer(r"\n  ([a-z0-9_]+):\s", sc):
    scenes.append((m.group(1), m.start()))
scenes.append(("~end", len(sc)))


def width(t):
    return sum(9.4 if ord(ch) > 0x2000 else 6.3 for ch in t)


def labels(body):
    out = []
    for m in re.finditer(r"TX\((%s),\s*(%s),\s*'([^']*)'" % (NUM, NUM), body):
        x, y, t = float(m.group(1)), float(m.group(2)), m.group(3)
        if t:
            out.append((x, y - ASC, x + width(t), y + DESC, t))
    for m in re.finditer(r"Dh\((%s),\s*(%s),\s*(%s),\s*'([^']*)'" % (NUM, NUM, NUM), body):
        x1, x2, y, t = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        if t:
            cx, w, ly = (x1 + x2) / 2, width(t), y - 8
            out.append((cx - w / 2, ly - ASC, cx + w / 2, ly + DESC, t))
    for m in re.finditer(r"Dv\((%s),\s*(%s),\s*(%s),\s*'([^']*)',\s*(\d)" % (NUM, NUM, NUM), body):
        y1, y2, x, t, left = (float(m.group(1)), float(m.group(2)), float(m.group(3)),
                              m.group(4), m.group(5) == "1")
        if t:
            w, ly = width(t), (y1 + y2) / 2 + 4
            lx = x - 7 - w if left else x + 7
            out.append((lx, ly - ASC, lx + w, ly + DESC, t))
    return out


def solids(body):
    """색이 찬 '물건'의 사각 범위. 방 같은 큰 배경면은 넓이로 뺀다."""
    out = []

    def add(x, y, w, h, what):
        if w > 0 and h > 0 and w * h <= MAX_AREA:
            out.append((x, y, x + w, y + h, what))

    for m in re.finditer(r"R\((%s),\s*(%s),\s*(%s),\s*(%s),\s*'(#[0-9A-Fa-f]{6})'" % (NUM, NUM, NUM, NUM), body):
        add(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), "R")
    for m in re.finditer(r"R\((%s),\s*(%s),\s*(%s),\s*(%s)\)" % (NUM, NUM, NUM, NUM), body):
        add(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), "R")
    for m in re.finditer(r'<rect x="(%s)" y="(%s)" width="(%s)" height="(%s)"[^>]*fill="#' % (NUM, NUM, NUM, NUM), body):
        add(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), "rect")
    for m in re.finditer(r"C\((%s),\s*(%s),\s*(%s),\s*'(#[0-9A-Fa-f]{6})'" % (NUM, NUM, NUM), body):
        cx, cy, r = (float(m.group(k)) for k in (1, 2, 3))
        add(cx - r, cy - r, 2 * r, 2 * r, "C")
    for m in re.finditer(r"TANK\((%s),\s*(%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM, NUM), body):
        add(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), "TANK")
    for m in re.finditer(r"DRUM\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        x, y, k = (float(m.group(t)) for t in (1, 2, 3))
        add(x - 9 * k, y - 22 * k, 18 * k, 22 * k, "DRUM")
    for m in re.finditer(r"DOC\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        x, y, k = (float(m.group(t)) for t in (1, 2, 3))
        add(x - 11 * k, y - 15 * k, 22 * k, 28 * k, "DOC")
    for m in re.finditer(r"(?:W|P)\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        x, y, k = (float(m.group(t)) for t in (1, 2, 3))
        add(x - 8 * k, y - 31 * k, 16 * k, 31 * k, "사람")
    return out


bad = []
for n, (name, a) in enumerate(scenes[:-1]):
    body = sc[a:scenes[n + 1][1]]
    ls, ss = labels(body), solids(body)
    for (lx0, ly0, lx1, ly1, t) in ls:
        for (sx0, sy0, sx1, sy1, what) in ss:
            w = min(lx1, sx1) - max(lx0, sx0)
            h = min(ly1, sy1) - max(ly0, sy0)
            if w > 0 and h > 0 and w * h > 30:
                bad.append((name, what, round(w * h), t))
                break

print("이름표가 물건 위에 앉은 곳: %d건 (물건 %g px² 이하만 봄)" % (len(bad), MAX_AREA))
for name, what, ov, t in bad:
    print("  %-13s %-5s %4d px²   %s" % (name, what, ov, t))
print()
print("이 검사는 **경고**다. 계기판 안의 숫자처럼 일부러 물건 위에 얹는 이름표도")
print("있으므로 종료코드는 항상 0 이다. 잡힌 것은 보고 판단한다.")
