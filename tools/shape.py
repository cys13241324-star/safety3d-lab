# -*- coding: utf-8 -*-
"""카드 값이 덱의 생성 규칙을 따르는지 본다.

   덱은 두 모양으로만 만들어져 있다(systems.md ③).

     P형  준수 [안전 +, 공정 **+**, 공사비 **−**, 감독 +]
          위반 [안전 −, 공정 **−**, 공사비 **+**, 감독 −]
     B형  준수 [안전 +, 공정 **−**, 공사비 **+**, 감독 +]
          위반 [안전 −, 공정 **+**, 공사비 **−**, 감독 −]

   즉 **준수는 공정과 공사비 중 하나를 내주고 하나를 얻는다.** 둘 다 내주는
   카드를 만들면 그 카드만 유난히 무거워진다.

   실제로 안전관리론 세 장을 그렇게 썼더니 판당 여덟 번쯤 뽑히면서
   완주율이 50 → 36 %로 내려갔다. 눈으로는 안 보이는 종류의 어긋남이라
   기계에 맡긴다.

   세 종류를 낸다.
     · 준수가 공정·공사비를 둘 다 깎는가 (또는 둘 다 주는가)
     · 안전과 감독의 부호가 준수/위반에서 뒤집혀 있는가
     · 위반의 안전 손실이 준수의 안전 이득보다 작은가 — 어겨도 남는 장사다

   법령 카드(law 가 있는 것)만 본다. 기습·현장·상황 카드는 저마다 결이 달라
   이 규칙을 따르지 않는 것이 정상이다.

   경고다 — 종료코드는 항상 0. 잡힌 것은 보고 판단한다.
   쓰기: python tools/shape.py [reigns.html]
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "reigns.html")
src = io.open(path, encoding="utf-8").read()

body = src[src.index("var DECK = ["):]
body = body[:body.index(chr(10) + "  ];")]

LAWF = re.compile(r"law:'([^']*)'")
AD = re.compile(r"\ba:\{[^}]*?\bd:\[\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\]", re.S)
BD = re.compile(r"\bb:\{[^}]*?\bd:\[\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\]", re.S)

both, flip, cheap, seen = [], [], [], 0
for m in re.finditer(r"^  \{k:'([^']+)',", body, re.M):
    key = m.start()
    nxt = body.find("\n  {k:'", key + 1)
    chunk = body[key:nxt if nxt > 0 else len(body)]
    k = m.group(1)
    lm = LAWF.search(chunk)
    if not lm or not lm.group(1):
        continue                      # 법령 카드만 본다
    am, bm = AD.search(chunk), BD.search(chunk)
    if not am or not bm:
        continue
    a = [int(x) for x in am.groups()]
    b = [int(x) for x in bm.groups()]
    seen += 1
    # ① 준수가 공정·공사비를 둘 다 깎거나 둘 다 주는가
    if (a[1] < 0 and a[2] < 0) or (a[1] > 0 and a[2] > 0):
        both.append((k, a, b))
    # ② 안전·감독의 부호가 뒤집혀 있는가
    if a[0] <= 0 or a[3] < 0 or b[0] >= 0:
        flip.append((k, a, b))
    # ③ 어겨도 남는 장사인가
    elif abs(b[0]) < a[0]:
        cheap.append((k, a, b))

print("법령 카드 %d장 검사" % seen)
print("")


def show(title, rows, note):
    print("%s: %d건" % (title, len(rows)))
    if rows:
        print("  %s" % note)
        for k, a, b in rows:
            print("  %-12s 준수 %-18s 위반 %s" % (k, a, b))
    print("")


show("준수가 공정·공사비를 둘 다 깎거나 둘 다 주는 곳", both,
     "P형은 공정을 주고 공사비를 내주고, B형은 그 반대다. 둘 다면 그 카드만 무겁다")
show("안전·감독의 부호가 규칙과 다른 곳", flip,
     "준수는 안전과 감독을 올리고 위반은 안전을 깎는다 — 이건 예외가 없다")
show("어겨도 남는 장사인 곳", cheap,
     "위반의 안전 손실이 준수의 안전 이득보다 작으면 어기는 쪽이 이득이다")
