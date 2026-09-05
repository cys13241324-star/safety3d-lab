# -*- coding: utf-8 -*-
"""그림 검사를 한 번에 돌린다.   사용법: python tools/check.py [reigns.html]

   artlint   판 밖 · 캡션 자리 · 이름표끼리 · 축척 · 6 px 규칙   (실패하면 종료 1)
   anchor    치수 부착 · 사람 키                                  (실패하면 종료 1)
   lawcheck  인용한 조문이 실재하는가 · 그 조문에 그 숫자가 있는가  (없는 조문이면 종료 1)
   hitcheck  hit 자리번호가 f 의 <em> 안을 가리키는가              (실패하면 종료 1)
   onobj     이름표가 물건 위에                                   (경고, 항상 0)

   이 검사들이 보지 않는 것: **형상** — 그린 것이 규정이 말하는 물건으로
   읽히는가. 그건 tools 로는 안 되고 격자에 늘어놓고 봐야 안다."""
import os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = sys.argv[1:] if len(sys.argv) > 1 else []
bad = 0
for name, hard in (("artlint", True), ("anchor", True), ("lawcheck", True), ("hitcheck", True), ("onobj", False)):
    print("── %s" % name)
    r = subprocess.run([sys.executable, os.path.join(HERE, name + ".py")] + TARGET,
                       capture_output=True, text=True, encoding="utf-8")
    print((r.stdout or "").rstrip())
    if r.stderr.strip():
        print(r.stderr.rstrip())
    if hard and r.returncode:
        bad += 1
print()
print("=== 검사 %s ===" % ("실패" if bad else "통과"))
sys.exit(1 if bad else 0)
