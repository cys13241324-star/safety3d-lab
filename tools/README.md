# tools

## harness.js — 게임 로직 시험대

`reigns.html` 의 `<script>` 블록을 그대로 꺼내 **JScript 로 실행**한다.
DOM 을 흉내 내고 좌우 선택 핸들러를 실제로 눌러서, 판이 끝까지 도는지와
밸런스가 어떻게 나오는지를 잰다. Node 없이 Windows 에서 바로 돌아간다.

```
cscript //Nologo tools\harness.js reigns.html 300
```

두 번째 인자는 정책당 판 수(기본 60). 네 가지 정책을 비교한다.

| 정책 | 규칙 |
|---|---|
| always comply | 늘 왼쪽 — 모든 카드에서 규정을 지키는 쪽 |
| balance the weakest | 안전·감독이 가장 낮으면 준수, 공정·예산이 가장 낮으면 위반 |
| coin flip | 무작위 |
| always cut corners | 늘 오른쪽 |

생존 일수 분포·60일 도달률·종료 사유를 내고, 이어하기 저장분이
화면 상태와 일치하는지까지 확인한다.

파일은 **ASCII 로만** 써야 한다. WSH 는 `.js` 를 ANSI 로 읽어서
한글 주석이 들어가면 파싱이 깨진다. 게임 쪽 한글은 ADODB.Stream 으로
UTF-8 로 읽어 eval 하므로 문제없다.
