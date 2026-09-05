# -*- coding: utf-8 -*-
"""장면의 글자를 검사한다.   사용법: python tools/artlint.py [reigns.html]

   ① 판(320×132) 밖으로 나가는가 — 10.5 px 글자의 윗머리·아랫꼬리까지 본다
   ② 카드가 자동으로 붙이는 캡션 자리(좌하단)를 침범하는가
   ③ 이름표끼리 겹치는가 — 지금까지 눈으로만 잡던 것
   TX(x, y, '글') · Dh(x1, x2, y, '글') · Dv(y1, y2, x, '글', left) 를 본다."""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import os
P = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reigns.html")
s = io.open(P, encoding="utf-8").read()
i = s.index("var SC = {")
j = s.index("\n  };", i)
sc = s[i:j]

TOP, BOTTOM, RIGHT, LEFT = 18, 130, 318, 4   # BOTTOM 은 글자 상자의 아래끝
CAP_Y0, CAP_Y1, CAP_X = 110, 128, 150      # 캡션 자리 (left:12 bottom:8)
ASC, DESC = 9.0, 2.5                       # 글자 윗머리 · 아랫꼬리

scenes = []
for m in re.finditer(r"\n  ([a-z0-9_]+):\s", sc):
    scenes.append((m.group(1), m.start()))
scenes.append(("~end", len(sc)))


def width(t):
    # 한글은 넓고 숫자·영문은 좁다. monospace 10.5px 기준 대략치.
    return sum(9.4 if ord(ch) > 0x2000 else 6.3 for ch in t)


def boxes(body):
    """이름표마다 (왼쪽, 위, 오른쪽, 아래, 글, 종류, 기준선y) 를 낸다."""
    out = []
    for m in re.finditer(r"TX\((-?[\d.]+),\s*(-?[\d.]+),\s*'([^']*)'", body):
        x, y, t = float(m.group(1)), float(m.group(2)), m.group(3)
        out.append((x, y - ASC, x + width(t), y + DESC, t, "TX", y))
    for m in re.finditer(r"Dh\((-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*'([^']*)'", body):
        x1, x2, y, t = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        cx, w, ly = (x1 + x2) / 2, width(t), y - 8
        out.append((cx - w / 2, ly - ASC, cx + w / 2, ly + DESC, t, "Dh", ly))
    for m in re.finditer(r"Dv\((-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*'([^']*)',\s*(\d)", body):
        y1, y2, x, t, left = (float(m.group(1)), float(m.group(2)), float(m.group(3)),
                              m.group(4), m.group(5) == "1")
        w, ly = width(t), (y1 + y2) / 2 + 4
        lx = x - 7 - w if left else x + 7
        out.append((lx, ly - ASC, lx + w, ly + DESC, t, "Dv", ly))
    # 상세원의 배율(위)·측정값(아래) 이름표. 좌표가 계산식이라 위의 정규식엔 안 걸린다.
    for mm_ in re.finditer(r"DET\(\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),"
                           r"\s*(-?[\d.]+),\s*(-?[\d.]+),", body):
        cx, cy, r = float(mm_.group(3)), float(mm_.group(4)), float(mm_.group(5))
        k, d = mm_.end(), 1
        while k < len(body) and d:
            d += (body[k] == "(") - (body[k] == ")")
            k += 1
        args, depth, cur, q = [], 0, "", False
        for ch in body[mm_.end():k - 1]:
            if ch == "'":
                q = not q
            if not q and ch in "([":
                depth += 1
            elif not q and ch in ")]":
                depth -= 1
            if ch == "," and depth == 0 and not q:
                args.append(cur); cur = ""
            else:
                cur += ch
        args.append(cur)
        # DET(fx, fy, cx, cy, r, inner, tag, foot) — 여섯째부터가 이름표
        for idx, ly in ((6, cy - r - 5), (7, cy + r + 13)):
            if idx >= len(args):
                continue
            g = re.search(r"'([^']*)'", args[idx])
            if not g or not g.group(1):
                continue
            t = g.group(1)
            w = width(t)
            out.append((cx - w / 2, ly - 9.0, cx + w / 2, ly + DESC, t, "DET", ly))
    return [b for b in out if b[4]]        # 빈 이름표는 뺀다


bad = []
for n, (name, a) in enumerate(scenes[:-1]):
    body = sc[a:scenes[n + 1][1]]
    bs = boxes(body)
    for (x0, y0, x1, y1, t, kind, ly) in bs:
        if ly < TOP:
            bad.append((name, "%s y=%g 윗머리 잘림" % (kind, ly), t))
        if y1 > BOTTOM:
            bad.append((name, "%s y=%g 판 아래로" % (kind, ly), t))
        if x1 > RIGHT:
            bad.append((name, "%s 오른쪽 %d px 넘침" % (kind, round(x1 - RIGHT)), t))
        if x0 < LEFT:
            bad.append((name, "%s 왼쪽 %d px 넘침" % (kind, round(LEFT - x0)), t))
        if CAP_Y0 <= ly <= CAP_Y1 and x0 < CAP_X:
            bad.append((name, "%s 캡션 자리 침범" % kind, t))
    for p in range(len(bs)):
        for q in range(p + 1, len(bs)):
            ax0, ay0, ax1, ay1, at = bs[p][:5]
            bx0, by0, bx1, by1, bt = bs[q][:5]
            w = min(ax1, bx1) - max(ax0, bx0)
            h = min(ay1, by1) - max(ay0, by0)
            if w > 0 and h > 0 and w * h > 12:
                bad.append((name, "이름표 겹침 %d px²" % round(w * h), "%s ⨯ %s" % (at, bt)))


# ── 축척 — 한 판 안의 치수선이 같은 px/m 를 가리키는가 (감사 기준 「가」)
UNIT = {"mm": .001, "cm": .01, "m": 1.0}
LEN = re.compile(r"([\d.]+)\s*(mm|cm|m)(?![\w/㎥㎠])")
SCALE_TOL = 1.6


def det_spans(body):
    """DET( ... ) 의 괄호 범위. 그 안의 치수는 일부러 다른 배율이라 뺀다."""
    out = []
    for mm_ in re.finditer(r"DET\(", body):
        k, d = mm_.end(), 1
        while k < len(body) and d:
            d += (body[k] == "(") - (body[k] == ")")
            k += 1
        out.append((mm_.start(), k))
    return out


scale = []
for n, (name, a0) in enumerate(scenes[:-1]):
    body = sc[a0:scenes[n + 1][1]]
    skip = det_spans(body)
    got = []
    for pat in (r"Dh\((-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*'([^']*)'",
                r"Dv\((-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*'([^']*)'"):
        for mm_ in re.finditer(pat, body):
            if any(x <= mm_.start() < y for x, y in skip):
                continue
            g = LEN.search(mm_.group(4))
            if not g:
                continue
            px = abs(float(mm_.group(2)) - float(mm_.group(1)))
            metres = float(g.group(1)) * UNIT[g.group(2)]
            if metres > 0 and px > 0:
                got.append((px / metres, mm_.group(4)))
    # 약속 3 — 6 px 미만 치수선은 읽을 수 없다. 지시선이나 상세원으로 뺀다.
    for pat in (r"Dh\((-?[\d.]+),\s*(-?[\d.]+),", r"Dv\((-?[\d.]+),\s*(-?[\d.]+),"):
        for mm_ in re.finditer(pat, body):
            if any(x <= mm_.start() < y for x, y in skip):
                continue
            ln = abs(float(mm_.group(2)) - float(mm_.group(1)))
            if ln < 6:
                bad.append((name, "치수선 %.0f px — 6 px 미만" % ln,
                            "지시선이나 상세원(DET)으로 뺀다"))
    if len(got) >= 2:
        lo = min(g[0] for g in got)
        hi = max(g[0] for g in got)
        if hi / lo > SCALE_TOL:
            scale.append((name, hi / lo, got))

print("장면 %d개 검사 · 이름표 문제 %d건 · 축척 어긋남 %d건"
      % (len(scenes) - 1, len(bad), len(scale)))
for name, why, t in bad:
    print("  %-13s %-24s %s" % (name, why, t))
for name, r, got in scale:
    print("  %-13s 축척 %.1f배 어긋남      %s"
          % (name, r, " · ".join("%s → %.0f px/m" % (t, p) for p, t in got)))
    print("  %-13s   (한 판에 px/m 이 둘이면 잘못 그렸거나, 상세원으로 떼거나, 파단선으로 끊어야 한다)" % "")

sys.exit(1 if (bad or scale) else 0)
