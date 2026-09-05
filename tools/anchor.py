# -*- coding: utf-8 -*-
"""감사 기준 「나」   사용법: python tools/anchor.py [reigns.html]
   — 치수선의 두 끝이 실제로 무언가를 잡고 있는가.
   장면에서 그려진 좌표를 모두 모아, 치수선 양끝이 그중 하나에 닿는지 본다."""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import os
P = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reigns.html")
s = io.open(P, encoding="utf-8").read()
i = s.index("var SC = {")
j = s.index("\n  };", i)
sc = s[i:j]
TOL = 3.0

scenes = []
for m in re.finditer(r"\n  ([a-z0-9_]+):\s", sc):
    scenes.append((m.group(1), m.start()))
scenes.append(("~end", len(sc)))

NUM = r"-?\d*\.?\d+"
PATH_CMD = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")


def path_points(d):
    """path 의 d 를 훑어 절대 좌표를 낸다. 곡선은 끝점만."""
    pts, cx, cy, sx, sy = [], 0.0, 0.0, 0.0, 0.0
    for cmd, arg in PATH_CMD.findall(d):
        v = [float(x) for x in re.findall(NUM, arg)]
        up = cmd.isupper()
        c = cmd.upper()
        k = 0
        if c == "M":
            while k + 1 < len(v) + 1 and k + 2 <= len(v):
                cx, cy = (v[k], v[k + 1]) if up else (cx + v[k], cy + v[k + 1])
                if k == 0:
                    sx, sy = cx, cy
                pts.append((cx, cy)); k += 2
        elif c == "L":
            while k + 2 <= len(v):
                cx, cy = (v[k], v[k + 1]) if up else (cx + v[k], cy + v[k + 1])
                pts.append((cx, cy)); k += 2
        elif c == "H":
            for x in v:
                cx = x if up else cx + x
                pts.append((cx, cy))
        elif c == "V":
            for y in v:
                cy = y if up else cy + y
                pts.append((cx, cy))
        elif c in "CSQT":
            step = {"C": 6, "S": 4, "Q": 4, "T": 2}[c]
            while k + step <= len(v):
                ex, ey = v[k + step - 2], v[k + step - 1]
                cx, cy = (ex, ey) if up else (cx + ex, cy + ey)
                pts.append((cx, cy)); k += step
        elif c == "A":
            while k + 7 <= len(v):
                ex, ey = v[k + 5], v[k + 6]
                cx, cy = (ex, ey) if up else (cx + ex, cy + ey)
                pts.append((cx, cy)); k += 7
        elif c == "Z":
            cx, cy = sx, sy
    return pts


def anchors(body):
    """장면에서 실제로 그려진 x · y 좌표를 모은다."""
    xs, ys = set(), set()
    if "GND" in body:
        ys.add(108.0)
    for d in re.findall(r"'(M[^']*)'", body):
        for x, y in path_points(d):
            xs.add(round(x, 1)); ys.add(round(y, 1))
    for m in re.finditer(r'd="(M[^"]*)"', body):
        for x, y in path_points(m.group(1)):
            xs.add(round(x, 1)); ys.add(round(y, 1))
    for m in re.finditer(r"R\((%s),\s*(%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM, NUM), body):
        x, y, w, h = (float(m.group(k)) for k in (1, 2, 3, 4))
        xs.update((x, x + w)); ys.update((y, y + h))
    for m in re.finditer(r'<rect x="(%s)" y="(%s)" width="(%s)" height="(%s)"' % (NUM, NUM, NUM, NUM), body):
        x, y, w, h = (float(m.group(k)) for k in (1, 2, 3, 4))
        xs.update((x, x + w)); ys.update((y, y + h))
    for m in re.finditer(r"C\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        cx, cy, r = (float(m.group(k)) for k in (1, 2, 3))
        xs.update((cx, cx - r, cx + r)); ys.update((cy, cy - r, cy + r))
    for m in re.finditer(r'<circle cx="(%s)" cy="(%s)" r="(%s)"' % (NUM, NUM, NUM), body):
        cx, cy, r = (float(m.group(k)) for k in (1, 2, 3))
        xs.update((cx, cx - r, cx + r)); ys.update((cy, cy - r, cy + r))
    for m in re.finditer(r"TANK\((%s),\s*(%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM, NUM), body):
        x, y, w, h = (float(m.group(k)) for k in (1, 2, 3, 4))
        xs.update((x, x + w)); ys.update((y, y + h))
    for m in re.finditer(r"(?:W|P)\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        x, y, sc_ = (float(m.group(k)) for k in (1, 2, 3))
        xs.add(x); ys.update((y, y - 26 * sc_, y - 18 * sc_))
    for m in re.finditer(r"DRUM\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        x, y, sc_ = (float(m.group(k)) for k in (1, 2, 3))
        xs.update((x, x - 9 * sc_, x + 9 * sc_)); ys.update((y, y - 22 * sc_))
    for m in re.finditer(r"DOC\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        x, y, sc_ = (float(m.group(k)) for k in (1, 2, 3))
        xs.update((x, x - 11 * sc_, x + 11 * sc_)); ys.update((y, y - 15 * sc_, y + 13 * sc_))
    for m in re.finditer(r"(?:PANEL|MACH)\((%s),\s*(%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM, NUM), body):
        x, y, w, h = (float(m.group(k)) for k in (1, 2, 3, 4))
        xs.update((x, x + w)); ys.update((y, y + h))
    for m in re.finditer(r"PG\('([^']*)'", body):
        v = [float(t) for t in re.findall(NUM, m.group(1))]
        for k in range(0, len(v) - 1, 2):
            xs.add(v[k]); ys.add(v[k + 1])
    return xs, ys


def near(v, pool):
    return any(abs(v - p) <= TOL for p in pool)


loose = []
for n, (name, a) in enumerate(scenes[:-1]):
    body = sc[a:scenes[n + 1][1]]
    xs, ys = anchors(body)
    for m in re.finditer(r"Dh\((%s),\s*(%s),\s*(%s),\s*'([^']*)'" % (NUM, NUM, NUM), body):
        x1, x2, t = float(m.group(1)), float(m.group(2)), m.group(4)
        miss = [v for v in (x1, x2) if not near(v, xs)]
        if miss:
            loose.append((name, "Dh 끝 %s 이 아무것도 안 잡음"
                          % " · ".join("x=%g" % v for v in miss), t))
    for m in re.finditer(r"Dv\((%s),\s*(%s),\s*(%s),\s*'([^']*)'" % (NUM, NUM, NUM), body):
        y1, y2, t = float(m.group(1)), float(m.group(2)), m.group(4)
        miss = [v for v in (y1, y2) if not near(v, ys)]
        if miss:
            loose.append((name, "Dv 끝 %s 이 아무것도 안 잡음"
                          % " · ".join("y=%g" % v for v in miss), t))

print("치수 끝이 허공인 곳: %d건 (허용오차 %g px)" % (len(loose), TOL))
for name, why, t in loose:
    print("  %-13s %-34s %s" % (name, why, t))

sys.exit(1 if loose else 0)
