# -*- coding: utf-8 -*-
"""hit 이 f 의 <em> 개수를 넘지 않는지 본다.

   hit 은 「이 카드가 실제로 물은 값」의 자리번호다. f 를 고쳐 쓰면서 <em> 개수가
   줄면 hit 이 허공을 가리키게 되는데, 화면에는 아무 표시도 안 붙을 뿐 오류가 나지
   않아 눈으로는 못 잡는다. 카드 데이터를 손볼 때마다 돌린다.

   쓰기: python tools/hitcheck.py [reigns.html]
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

FF = re.compile(r"\bf:'((?:[^'\\]|\\.)*)'")
HH = re.compile(r"hit:\[([^\]]*)\]")

bad = 0
seen = 0
body = src[src.index("var DECK = ["):]
body = body[:body.index("\n  ];")]
for m in re.finditer(r"^  \{k:'([^']+)',", body, re.M):
    start = m.start()
    nxt = body.find("\n  {k:'", start + 1)
    chunk = body[start:nxt if nxt > 0 else len(body)]
    fm, hm = FF.search(chunk), HH.search(chunk)
    if not fm or not hm:
        continue
    seen += 1
    ems = len(re.findall(r"<em>", fm.group(1)))
    hits = [int(x) for x in hm.group(1).split(",") if x.strip()]
    if hits and max(hits) >= ems:
        print("  %-12s hit=%s 인데 <em>은 %d개뿐" % (m.group(1), hits, ems))
        bad += 1

print("hit 을 단 카드 %d장 · 자리번호가 허공을 가리키는 곳: %d건" % (seen, bad))
sys.exit(1 if bad else 0)
