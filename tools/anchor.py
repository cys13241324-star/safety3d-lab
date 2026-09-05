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


# ── 사람 키 — W/P 글리프의 전체 높이는 31 단위다(안전모 꼭대기 -31 ~ 발끝 0).
#    판의 px/m 를 알면 그린 사람이 몇 미터인지 역산된다.
GLYPH, LO, HI_ = 31.0, 1.45, 1.95
BAND = (12.0, 60.0)          # 사람 크기를 잴 만한 축척 대역
UNIT = {"mm": .001, "cm": .01, "m": 1.0}
LEN = re.compile(r"([\d.]+)\s*(mm|cm|m)(?![\w/㎥㎠])")


def det_spans(body):
    out = []
    for mm_ in re.finditer(r"DET\(", body):
        k, d = mm_.end(), 1
        while k < len(body) and d:
            d += (body[k] == "(") - (body[k] == ")")
            k += 1
        out.append((mm_.start(), k))
    return out


tall = []
for n, (name, a0) in enumerate(scenes[:-1]):
    body = sc[a0:scenes[n + 1][1]]
    skip = det_spans(body)
    pxm = []
    for pat in (r"Dh\((%s),\s*(%s),\s*(%s),\s*'([^']*)'" % (NUM, NUM, NUM),
                r"Dv\((%s),\s*(%s),\s*(%s),\s*'([^']*)'" % (NUM, NUM, NUM)):
        for mm_ in re.finditer(pat, body):
            if any(x <= mm_.start() < y for x, y in skip):
                continue
            g = LEN.search(mm_.group(4))
            if not g:
                continue
            px = abs(float(mm_.group(2)) - float(mm_.group(1)))
            me = float(g.group(1)) * UNIT[g.group(2)]
            if me > 0 and px > 0:
                pxm.append(px / me)
    if not pxm:
        continue
    pxm.sort()
    med = pxm[len(pxm) // 2]
    if not (BAND[0] <= med <= BAND[1]):
        continue
    for mm_ in re.finditer(r"(?:W|P)\((%s),\s*(%s),\s*(%s)" % (NUM, NUM, NUM), body):
        s_ = float(mm_.group(3))
        h = GLYPH * s_ / med
        if h < LO or h > HI_:
            tall.append((name, s_, med, h, 1.7 * med / GLYPH))

print("치수 끝이 허공인 곳: %d건 (허용오차 %g px) · 사람 키가 어긋난 곳: %d건"
      % (len(loose), TOL, len(tall)))
for name, why, t in loose:
    print("  %-13s %-34s %s" % (name, why, t))
for name, s_, med, h, want in tall:
    print("  %-13s 배율 %.2f · %.0f px/m → 키 %.2f m   (1.7 m 이려면 %.2f)"
          % (name, s_, med, h, want))

sys.exit(1 if (loose or tall) else 0)
