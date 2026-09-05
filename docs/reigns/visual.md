# 「안전관리자의 하루」 시각 설계 사양

대상: `safety3d-lab/reigns.html`
판 규격: `viewBox="0 0 320 132"`, 지면선 `GY = 108`
토큰·서체는 형제 페이지와 동일값 유지(`#0A1018 / #E3B54D / #5CC08A / #F07056 / #7FA6E0 / #B58FE0`, Gothic A1 800 · IBM Plex Sans KR · IBM Plex Mono).

---

## ① 장면 감사표

감사 기준 네 가지.
**(가) 축척** — 한 판 안에서 두 개 이상의 px/m 가 섞였는가.
**(나) 치수 부착** — 치수선의 두 끝이 실제 그 규정이 걸리는 두 지점에 닿아 있는가.
**(다) 형상** — 부재가 규정이 말하는 물건으로 읽히는가.
**(라) 판 밖 · 겹침** — 0~320 / 0~132 밖으로 나가거나 캡션·경고 삼각형과 겹치는가.

### 다시 그려야 하는 것

| 키 | 문제 | 조치 |
|---|---|---|
| `trench` | **그림이 규정과 반대다.** 경사선 `M96 100L164 20` 은 수직 80 : 수평 68 = **1 : 0.85**. 라벨은 `1 : 1.8`. 카드가 "1:0.8로 깎았다(위반)"을 다루는데 그림이 그 위반을 그려 놓고 정답 라벨을 붙였다. 게다가 `M96 100L164 20H320V132H0V100` 는 `fill="none"`·stroke 없음 → 화면에 아무것도 남기지 않는 죽은 코드 | 1:1.8 로 다시 작도(수직 60 : 수평 108). 비탈면에 **기울기 삼각형**(수직 1 / 수평 1.8)을 얹고, 위반값 1:0.8 을 붉은 파선 유령선으로 겹쳐 차이를 보인다 |
| `panelspace` | 축척 붕괴. `Dh(40,200,84,'70 cm')` → 160 px = 70 cm(229 px/m)인데 같은 판의 근로자는 24 px = **0.10 m**. 10 cm짜리 사람이 70 cm 통로에 서 있다 | 44 px/m 고정. 70 cm = 31 px, 근로자 75 px. 좁아서 어깨가 닿는 게 보이게 |
| `rail` | 난간 상부대가 근로자 머리 위 40 px 에 있다(사람 23 px, 난간 60 px). 90 cm 난간은 허리 높이여야 뜻이 산다. 발끝막이판 10 px 은 같은 판에서 15 cm 에 해당 | 44 px/m. 상부대 40 px(=90 cm)이 근로자 키 75 px 의 53 % 지점에 오게. 발끝막이판 4.4 px 은 치수선 대신 지시선 |
| `shore` | `2 m마다`(수평연결재의 **수직** 간격)를 기둥 사이 **가로** 치수선으로 그렸다 — 뜻이 반대. 80 px=3.5 m 와 70 px=2 m 가 한 판에 공존. `'#2A3purple'` 문자열을 `.replace()` 로 덮는 코드 잔재 | 17 px/m. 수평연결재를 2 m(34 px) 간격의 **가로 부재 두 줄**로 그리고 그 사이를 세로 치수로. 이음부는 슬리브+볼트 4개가 보이게 |
| `scaffold` | 50 px 을 `1.85 m`, 56 px 을 `벽이음 5 m` 로 적었다. 길이가 거의 같은 두 치수선에 1.85 와 5 가 붙어 있어 읽는 사람이 축척을 잃는다 | 격자 프리미티브로 다시. 기둥 21 px = 1.85 m, 띠장 23 px = 2 m, 벽이음은 같은 축척의 세로 치수 |
| `ladder` | 그린 각도 58.5°(라벨 75°). 상단 돌출부 `M96 20L110 -3` 이 **판 위로 잘려 나간다**(y = −3). `Dv(4,20,140,'60 cm 돌출')` 은 그 잘린 부재가 아닌 빈 공간을 잰다 | 75° 실각도 작도(수직 78 : 수평 20.9). 돌출 60 cm 는 사다리 방향 **사선 치수**. 발치에 각도 호 |
| `plank` | 발판 **폭 40 cm** 를 입면도에서 널의 **길이**(110 px)에 붙였다. 입면에서는 폭이 보이지 않는다 | **평면도**로 전환. 폭이 화면 세로가 되어 40 cm 치수가 제 뜻을 갖는다. 틈 3 cm 는 지시선, 지지물 2개는 파선 |
| `horse` | 그린 각도 57°(라벨 75°), 각도 호 없음. `폭 40 cm` 를 발판 길이 128 px 에 붙였다 → 320 px/m 와 높이 2 m 의 30 px/m 가 100배 차이 | 26 px/m. 다리 75° 실각도 + 각도 호. 폭은 사판(斜板) 프리미티브의 깊이변에 사선 치수 |
| `stairs` | 세 축척 공존 — 60 px=1.2 m(50 px/m), 80 px=3 m(26.7 px/m), 32 px=1 m(32 px/m). 계단참 사각형이 계단 폴리라인과 어긋나 떠 있다. `폭 1 m` 를 디딤판 **너비(run)** 에 붙였다(폭은 진행방향 직각) | 20 px/m. 계단참을 단 위에 정확히 앉히고, 폭 1 m 는 **상세원 안의 평면 조각**으로 |
| `sawblade` | `Dh(168,180,36,'12 mm')` 이 y=36 에 있는데 그 높이의 톱날 가장자리는 x=130 — 치수선이 아무것도 잡고 있지 않다. 분할날이 `a40 40 0 0 1 0 48` 초승달로 그려져 날로 안 읽힌다. `M180 44V108` 은 테이블 밑까지 내려간 정체불명의 선 | 톱날 원주를 따르는 두께 있는 분할날. 12 mm 와 1.1배는 **5배 상세원**에서 |
| `powerline` | `Dv(38,48,208,'3 m')` = 10 px 짜리 토막인데 위 끝도 아래 끝도 전선·붐 끝 어디에도 닿지 않는다 | 13 px/m. 3 m = 39 px 로 전선 처짐 곡선과 붐 끝을 실제로 잇는다. 전선 둘레에 이격 포락선 파선 |
| `approach` | 접근한계는 충전부↔**신체 최근접부**인데 치수선이 근로자 몸통 중심에 닿는다. 사람 24 px = 0.55 m | 30 px/m, 손 뻗은 자세. 치수선 끝을 손끝에 |
| `exgap` | 화염 호가 x=154 에서 끊겨 틈(x=160)에 닿지 않는다. 화염이 틈을 지나며 꺼진다는 개념 자체가 그려지지 않음. 치수선은 아무것도 없는 y=118 에 | 본체는 폭발+접합면, **40배 상세원**에서 화염이 틈에 들어가 소멸하는 모습 |
| `press` | `D` 를 프레임과 **허공에 뜬 근로자**(y=96, 지면 108) 사이에서 쟀다. D 는 방호장치(광전자식 센서면)↔위험한계 거리인데 센서가 그려져 있지 않다 | 30 px/m. 광선식 센서면(붉은 파선 3줄) 추가, D 를 센서면↔금형 위험한계로 |
| `forklift` | 좌석이 없는데 `0.903 m`(좌석 윗면~상부틀)를 떠 있는 글자로 적었다. 헤드가드 개구부 셋의 폭이 18/24/22 px 로 제각각인데 그중 하나에만 `16 cm 미만` | 26 px/m. 좌석과 앉은 운전자 추가 → 0.903 m 에 실제 치수선. 16 cm 는 상세원 |
| `roller` | 아래 롤러 중심 y=104, r=26 → **바닥 아래 22 px 이 묻힌다**. 근로자 20 px = 0.5 m | 40 px/m. 롤러를 지면 위로, 손 조작식 급정지 조작부를 1.8 m(72 px)에. 사람 68 px 이라 조작부가 머리 바로 위 = 규정이 상한임이 보인다 |
| `pile` | `버팀대 3개 이상` 인데 셋째 선 `M100 24L100 108` 이 기둥과 겹쳐 **둘로만 보인다** | 셋째 버팀대를 앞쪽(오블리크)으로 빼고, 평면 상세원에서 120° 3방향을 명시 |
| `carry` | 상자가 근로자에게서 30 px 떨어져 공중에 떠 있고, 자세는 곧게 선 막대사람이라 `무릎 굽혀` 와 정반대 | 웅크린 자세 + 몸에 붙인 상자. 옆에 굽힌 허리(오답) 유령을 붉은 파선으로 |
| `staticflow` | 규정의 핵심인 **접지가 글자로만** 있고 그림에 없다 | 접지 기호 + 본딩선 + 딥파이프. 유속 화살표에 1 m/s |
| `vdt` | 시선 기준 수평선이 없어 `10~15°` 를 읽을 수 없다(그린 각 6.6°). 선 자세 글리프를 앉은 사람으로 쓰고 있다 | 앉은 자세 + 눈높이 수평 파선 + 12.5° 호. 눈~화면 40 cm 는 가로 치수 |
| `net` | 그린 각 14.7°(규정 20~30°, 각도 표기 없음). 낙하물 파선이 망에 닿기 전 허공에서 끊긴다. `2 m` 치수선이 망에서 26 px 떨어진 y=96 에 홀로 있다 | 26 px/m 근경 + 벽에 **파단선**을 넣어 10 m 간격을 정직하게 표기. 20~30° 허용 부채꼴 안에 망을 넣고 낙하물이 망에 떨어지게 |
| `fall` | `Dv(34,108,30,'10 m 이하')` 가 슬래브~**지면**을 잰다. 규정은 작업면~망 설치지점. 그린 처짐은 17.5 %(라벨 12 %). 추락 파선이 망 20 px 앞에서 끊김 | 처짐 = 스팬의 12 % 로 실제 작도, 수직거리는 **파단 치수선**으로 작업면↔망 사이만 |
| `frame` | **장면이 아예 없다.** `DECK` 에 `k:'frame'`(강관틀비계) 카드가 있는데 `SC.frame` 이 없어 `SC.site`(현장 사무동)로 떨어진다. 주틀 간격 1.8 m 카드에 사무실 그림이 뜬다 | 신규 작도 |

### 유지하되 한 줄만 고치는 것

| 키 | 조치 |
|---|---|
| `gangway` | 선체 바닥 y=86 이 수면 y=96 위에 떠 있다 → 선체를 수면까지 내리고, 규정의 본체인 **안전망**(현재 글자만)을 현문사다리 아래 처짐 곡선으로 추가 |
| `elcb` | 누설전류 파선 `M186 60H140` 이 허공에서 끝난다 → 공구·근로자·젖은 바닥·접지기호까지 잇는다 |
| `welder` | 케이블 시점 (124,88)이 손(≈110,97)에서 벗어나고 종점 x=196 이 용접기 x=200 에 4 px 못 미친다 → 양 끝을 붙인다 |
| `rotor` | 좌우 베어링 사이에 **축이 없다** → `bar(54,64,266,64,5)` 추가, 림에 원주속도 접선 화살표 |
| `wirerope` | 매단 하중이 지면(y=96~108)에 놓여 있다 → y=70~92 로 띄우고, 소선 절단은 상세원에서 10가닥 중 1가닥 |
| `boiler` | 압력계에 눈금·설정점이 없어 "최고사용압력 이하 작동"을 읽을 수 없다 → 눈금 + 최고사용압력 위치의 붉은 호 |
| `grinder` | 노출각 부채꼴에 각도 호·라벨이 없다 → `ang()` 로 125° 명시, 워크레스트 3 mm 는 상세원 |
| `robot` | 울타리 가로 눈금(8 px)이 울타리로 안 읽힌다 → 세로 살대. 30 px/m 로 두면 울타리 54 px > 사람 51 px 이라 "1.8 m 이상"이 눈으로 확인된다 |
| `confined` | 사다리가 수직구 폭 전체를 채워 근로자와 겹친다 → 사다리를 좌측 벽으로, 가스층에 측정기와 지시선 |
| `caisson` | 규정의 `1.8 m`(바닥~천장)가 그림에 없다 → 세로 치수 추가 |
| `gasweld` | 토치(화기)를 "5 m 이격" 치수선 한가운데 그려 두 화기가 겹친다 → 토치는 위로 빼고 호스로 연결, 용기에 온도계(40 ℃) |
| `chemdist`, `lux`, `noise`, `weather`, `mobscaf`, `site`, `report` | 축척·치수 부착 문제 없음. `noise` 는 근로자에 귀덮개, `weather` 는 풍속계 컵, `mobscaf` 는 구름방지장치만 추가 |

### 코드 위생 (전체 공통)

- `SC.press` 의 `R(96,30,128,20,'#2A3away','none').replace('#2A3away','#33425C')`, `SC.shore` 의 `'#2A3purple'` — 오타를 `.replace()` 로 덮은 잔재. 색은 전부 클래스로 뺀다.
- 하드코딩 `#1E293C`, `#243044`, `#161F2E`, `#0F1725`, `#0D1420`, `#0F1B2A`, `#2C4A63` 총 7종 — 밝은 모드에서 전부 무너진다(⑤ 참조).
- `role="img"` 에 `aria-label` 이 없다. `c.f` 에서 태그를 지워 넣는다.
- `.cap`(좌하단 캡션)은 `#card .subj` 와 `#sheet .std` 가 이미 말하는 것을 세 번째로 반복하면서 지면 밴드의 치수 자리를 먹는다. **삭제**하고 과목 줄 옆 칩으로 옮긴다. 판에서 비워 두는 곳은 사고 경고 삼각형 자리 `x 284~316 · y 6~42` 하나뿐이 된다.

---

## ③ 드로잉 시스템 (먼저 붙여 넣을 것)

②의 장면 코드가 전부 이 프리미티브 위에 서 있으므로 순서를 바꿔 먼저 적는다.
`var ST = '#5A6B87' …` 로 시작하는 색 상수 줄과 `W / Dh / Dv / L / R / TX / GND / WALL` 블록을 통째로 아래로 교체한다.

### 시스템이 지키는 다섯 가지 약속

1. **한 판에 축척 하나.** 장면마다 `k`(px per metre)를 맨 위에 선언하고 모든 길이를 `k` 로 만든다. 두 축척이 필요하면 나누지 말고 **상세원**(`detail`)을 쓴다.
2. **사람이 자를 대신한다.** `man(x, k)` 는 키를 항상 `1.7 × k` 로 그린다. 임의 배율 인자는 없앤다. 난간 90 cm 가 사람 허리에 오는지가 그 장면의 검산이다.
3. **6 px 미만 치수는 치수선을 쓰지 않는다.** 지시선(`lead`)이나 상세원으로 뺀다. 발끝막이판 10 cm, 워크레스트 3 mm, 안전간극 0.5 mm 가 여기 해당한다.
4. **한계 규정은 준수 상태를 그리고 라벨에 한계를 적는다.** "5 m 이하"면 4 m 를 그리고 `≤5 m` 를 적는다. 위반을 보여야 하는 카드는 준수선 위에 **붉은 파선 유령**을 덧그려 차이를 만든다.
5. **치수선의 두 끝은 반드시 실물에 닿는다.** 떨어져야 하면 `ext` 인자로 연장선을 그어 잇는다. 허공에 뜬 치수선은 없다.

### 좌표 · 판

```js
/* ===== 판 규격 ===== */
var VW = 320, VH = 132, GY = 108;      // 폭 · 높이 · 지면선
/* 비워 두는 곳: 사고 경고 삼각형 x 284~316 / y 6~42 — 그 밖은 전부 그림 자리 */

function r2(v){ return Math.round(v * 100) / 100; }
function A(o){ var s = '', k;
  for(k in o){ if(o[k] !== null && o[k] !== undefined && o[k] !== '') s += ' ' + k + '="' + o[k] + '"'; }
  return s; }
function el(n, o, inner){ return '<' + n + A(o) + (inner !== undefined ? '>' + inner + '</' + n + '>' : '/>'); }

/* 해칭 패턴 — 굴착 흙 단면. artFor 가 판마다 한 번 낸다 */
var DEFS = '<defs><pattern id="kx" width="7" height="7" patternUnits="userSpaceOnUse" ' +
  'patternTransform="rotate(45)"><path d="M0 0V7" class="k-hatch" stroke-width=".9"/></pattern></defs>';

/* 축척 도우미: k = px per metre */
function P(k){ return {
  k : k,
  m : function(v){ return r2(v * k); },        // 미터 → px 길이
  up: function(v){ return r2(GY - v * k); }    // 지면 위 높이(m) → y 좌표
}; }
```

색 문자열 상수(`ST`, `DM`, `HI`, `BD`, `SK`)는 전부 없앤다. 프리미티브는 색을 모르고 **클래스만** 붙인다(⑤에서 CSS 변수와 연결).

### 배경 · 지형

```js
function ground(kind){                          // 'earth'(기본) | 'water' | 'none'
  if(kind === 'none') return el('path', {d:'M0 ' + GY + 'H' + VW, class:'k-line', 'stroke-width':1.4});
  var d = '', i;
  if(kind === 'water'){ for(i = 0; i < VW; i += 20) d += 'M' + i + ' ' + (GY + 8) + 'q10 -4 20 0'; }
  return el('rect', {x:0, y:GY, width:VW, height:VH - GY, class:kind === 'water' ? 'k-water' : 'k-earth'}) +
    (d ? el('path', {d:d, class:'k-dim', 'stroke-width':1}) : '') +
    el('path', {d:'M0 ' + GY + 'H' + VW, class:'k-line', 'stroke-width':1.4});
}
function soil(pts){ return el('path', {d:'M' + pts.join('L') + 'Z', class:'k-soil'}); }  // 해칭 흙덩이
function wall(x, w, y0, y1){
  var a = y0 === undefined ? 2 : y0;
  return el('rect', {x:x, y:a, width:w, height:(y1 === undefined ? GY : y1) - a, class:'k-solid'}); }
function slab(x, y, w, h){ return el('rect', {x:x, y:y, width:w, height:h || 8, class:'k-solid'}); }
function plate(x, y, w, h){ return el('rect', {x:x, y:y, width:w, height:h || 6, class:'k-plate'}); }
function band(x, y, w, h, cls){ return el('rect', {x:x, y:y, width:w, height:h, class:cls || 'k-bad-band'}); }
function brk(x1, x2, y){                         // 파단선(중략)
  var m = (x1 + x2) / 2;
  return el('path', {d:'M' + x1 + ' ' + (y - 3) + 'H' + (m - 5) + 'L' + (m + 5) + ' ' + (y + 3) + 'H' + x2,
    class:'k-line', 'stroke-width':1.2}); }
```

### 부재

```js
function bar(x1, y1, x2, y2, w, cls){            // 강관 · 기둥 · 부재 한 개
  return el('path', {d:'M' + x1 + ' ' + y1 + 'L' + x2 + ' ' + y2,
    class:cls || 'k-line', 'stroke-width':w || 2.4, 'stroke-linecap':'round'}); }

function grid(x, y, w, h, nx, ny, cls){          // 비계 격자 — 한 줄로 비계 한 틀
  var d = '', i, p;
  for(i = 0; i <= nx; i++){ p = r2(x + w * i / nx); d += 'M' + p + ' ' + y + 'V' + (y + h); }
  for(i = 0; i <= ny; i++){ p = r2(y + h * i / ny); d += 'M' + x + ' ' + p + 'H' + (x + w); }
  return el('path', {d:d, class:cls || 'k-line', 'stroke-width':1.8}); }

function frames(x, y, w, h, n){                  // 강관틀비계 주틀 n개 + 교차가새
  var d = '', i, a, b;
  for(i = 0; i < n; i++){ a = r2(x + w * i); b = r2(a + w * 0.72);
    d += 'M' + a + ' ' + y + 'V' + (y + h) + 'M' + b + ' ' + y + 'V' + (y + h) +
         'M' + a + ' ' + y + 'H' + b + 'M' + a + ' ' + r2(y + h / 2) + 'H' + b;
    if(i < n - 1) d += 'M' + b + ' ' + (y + h) + 'L' + r2(a + w) + ' ' + y +
                       'M' + b + ' ' + y + 'L' + r2(a + w) + ' ' + (y + h); }
  return el('path', {d:d, class:'k-line', 'stroke-width':1.6}); }

function deck(x, y, w, d, th){                   // 사판 — 폭(깊이)이 보이는 발판. (x,y)=앞쪽 왼쪽 위
  th = th || 5;
  var sx = r2(d * 0.62), sy = r2(-d * 0.78);
  return el('path', {d:'M' + x + ' ' + y + 'h' + w + 'l' + sx + ' ' + sy + 'h' + (-w) + 'Z', class:'k-plate'}) +
    el('path', {d:'M' + x + ' ' + y + 'v' + th + 'h' + w + 'v' + (-th), class:'k-plate'}) +
    el('path', {d:'M' + (x + w) + ' ' + y + 'v' + th + 'l' + sx + ' ' + sy, class:'k-line', 'stroke-width':1}); }

function ladderRun(x1, y1, x2, y2, sep, n){      // 사다리. sep=레일 간격, n=칸 수
  var dx = x2 - x1, dy = y2 - y1, L = Math.sqrt(dx * dx + dy * dy),
      nx = r2(-dy / L * sep / 2), ny = r2(dx / L * sep / 2), d, i, cx, cy, t;
  d = 'M' + r2(x1 + nx) + ' ' + r2(y1 + ny) + 'L' + r2(x2 + nx) + ' ' + r2(y2 + ny) +
      'M' + r2(x1 - nx) + ' ' + r2(y1 - ny) + 'L' + r2(x2 - nx) + ' ' + r2(y2 - ny);
  for(i = 1; i < n; i++){ t = i / n; cx = x1 + dx * t; cy = y1 + dy * t;
    d += 'M' + r2(cx + nx) + ' ' + r2(cy + ny) + 'L' + r2(cx - nx) + ' ' + r2(cy - ny); }
  return el('path', {d:d, class:'k-line', 'stroke-width':1.8, 'stroke-linecap':'round'}); }

function mesh(x, y, len, deg){                   // 방지망: 로프 + 그물코. 끝점·보간을 함께 돌려준다
  var a = deg * Math.PI / 180, ex = r2(x + len * Math.cos(a)), ey = r2(y - len * Math.sin(a)),
      n = Math.max(3, Math.round(len / 9)), d = '', i, t, px, py;
  for(i = 1; i < n; i++){ t = i / n; px = r2(x + (ex - x) * t); py = r2(y + (ey - y) * t);
    d += 'M' + px + ' ' + py + 'l' + r2(5 * Math.sin(a)) + ' ' + r2(5 * Math.cos(a)); }
  return { x:ex, y:ey,
    g: el('path', {d:d, class:'k-dim', 'stroke-width':1}) +
       el('path', {d:'M' + x + ' ' + y + 'L' + ex + ' ' + ey, class:'k-hi',
         'stroke-width':2.2, 'stroke-linecap':'round'}),
    yAt: function(qx){ return r2(y + (ey - y) * ((qx - x) / (ex - x))); } }; }

function sagNet(x1, y1, x2, y2, sag, cls){       // 처진 망 · 전선. sag = 실제 처짐 px
  var mx = r2((x1 + x2) / 2), my = r2((y1 + y2) / 2 + sag * 2);
  return { low: r2((y1 + y2) / 2 + sag), mx: mx,
    g: el('path', {d:'M' + x1 + ' ' + y1 + 'Q' + mx + ' ' + my + ' ' + x2 + ' ' + y2,
      class:cls || 'k-hi', 'stroke-width':2.2, fill:'none'}) }; }

function vessel(x, y, w, h, r){
  return el('rect', {x:x, y:y, width:w, height:h, rx:r === undefined ? 8 : r, class:'k-solid'}); }
function cyl(x, y, w, h){ return el('rect', {x:x, y:y, width:w, height:h, rx:r2(w / 2), class:'k-solid'}); }
function pipe(x1, y1, x2, y2, w){
  var dx = x2 - x1, dy = y2 - y1, L = Math.sqrt(dx * dx + dy * dy),
      nx = r2(-dy / L * w / 2), ny = r2(dx / L * w / 2);
  return el('path', {d:'M' + r2(x1 + nx) + ' ' + r2(y1 + ny) + 'L' + r2(x2 + nx) + ' ' + r2(y2 + ny) +
    'M' + r2(x1 - nx) + ' ' + r2(y1 - ny) + 'L' + r2(x2 - nx) + ' ' + r2(y2 - ny),
    class:'k-line', 'stroke-width':1.4}); }
function wheel(cx, cy, r){
  return el('circle', {cx:cx, cy:cy, r:r, class:'k-plate'}) +
    el('circle', {cx:cx, cy:cy, r:r2(r * 0.35), class:'k-line', fill:'none', 'stroke-width':1.2}); }
function earth(x, y){                            // 접지 기호 — 정전기 · 감전 장면의 필수 부재
  return el('path', {d:'M' + x + ' ' + (y - 10) + 'V' + y + 'M' + (x - 8) + ' ' + y + 'h16M' +
    (x - 5) + ' ' + (y + 3.5) + 'h10M' + (x - 2.5) + ' ' + (y + 7) + 'h5',
    class:'k-hi', 'stroke-width':1.4, 'stroke-linecap':'round'}); }
```

### 사람 — 축척의 기준자

```js
var POSE = {
  stand : 'M0-14v9M0-11l-5.5 4M0-11l5.5 4M0-5l-4.5 6M0-5l4.5 6',
  narrow: 'M0-14v9M0-11l-3 6M0-11l3 6M0-5l-3 6M0-5l3 6',               // 팔 붙인 자세(좁은 공간)
  reach : 'M0-14v9M0-11l7-2M0-11l-5 4M0-5l-4.5 6M0-5l4.5 6',           // 오른쪽으로 손 뻗음
  carry : 'M0-13v7M0-11l5 3 2-3M0-11l-1 3M0-6l-5 5 1 5M0-6l5 5-1 5',   // 웅크려 몸에 붙여 들기
  stoop : 'M-1-13l4 5M2-8l4 3M2-8l-3 4M-1-3l-3 4M-1-3l4 4',            // 허리 굽힘(오답 대비용)
  sit   : 'M0-14v8M0-11l6 3M0-11l-4 4M0-6h7M7-6v7M0-6v7'
};
function man(x, k, pose, gy, flip){              // 키 = 1.7 × k 로 고정. 임의 배율 인자 없음
  var s = r2(1.7 * k / 24),
      t = 'translate(' + r2(x) + ',' + (gy === undefined ? GY : r2(gy)) + ') scale(' +
          (flip ? -s : s) + ',' + s + ')';
  return el('g', {transform:t},
    el('path', {d:'M-5.5-23a5.5 5 0 0 1 11 0z', class:'k-hi-f'}) +
    el('path', {d:'M-7.5-23h15', class:'k-hi', 'stroke-width':1.6, 'stroke-linecap':'round'}) +
    el('circle', {cx:0, cy:-18, r:3.1, class:'k-skin'}) +
    el('path', {d:POSE[pose || 'stand'], class:'k-body', 'stroke-width':2.6,
      'stroke-linecap':'round', 'stroke-linejoin':'round'})); }
function manDown(x, k, gy){                      // 쓰러진 사람
  return el('g', {transform:'translate(' + x + ',' + (gy === undefined ? GY : gy) + ') rotate(-78)'},
    man(0, k, 'stand', 0)); }
function manFall(x, y, k){                       // 추락 중
  return el('g', {transform:'translate(' + x + ',' + y + ') rotate(24)'}, man(0, k, 'reach', 0)); }
```

`man` 을 부르는 순간 그 장면의 축척이 검증된다. 난간이 사람 허리에 오지 않으면 `k` 나 부재 좌표 중 하나가 틀린 것이다.

### 치수 · 각도 · 주석

```js
function dimH(x1, x2, y, t, ext){                // ext = [y1,y2] 실물까지 잇는 연장선
  return (ext ? el('path', {d:'M' + x1 + ' ' + ext[0] + 'V' + ext[1] + 'M' + x2 + ' ' + ext[0] + 'V' + ext[1],
      class:'k-hi-th', 'stroke-width':.8, 'stroke-dasharray':'2 2'}) : '') +
    el('path', {d:'M' + x1 + ' ' + (y - 4) + 'v8M' + x2 + ' ' + (y - 4) + 'v8M' + x1 + ' ' + y + 'H' + x2,
      class:'k-hi k-draw', 'stroke-width':1.1, pathLength:1}) +
    el('text', {x:r2((x1 + x2) / 2), y:y - 7, 'text-anchor':'middle', class:'k-t-hi'}, t); }

function dimV(y1, y2, x, t, left, ext){          // ext = [x1,x2]
  return (ext ? el('path', {d:'M' + ext[0] + ' ' + y1 + 'H' + ext[1] + 'M' + ext[0] + ' ' + y2 + 'H' + ext[1],
      class:'k-hi-th', 'stroke-width':.8, 'stroke-dasharray':'2 2'}) : '') +
    el('path', {d:'M' + (x - 4) + ' ' + y1 + 'h8M' + (x - 4) + ' ' + y2 + 'h8M' + x + ' ' + y1 + 'V' + y2,
      class:'k-hi k-draw', 'stroke-width':1.1, pathLength:1}) +
    el('text', {x:left ? x - 7 : x + 7, y:r2((y1 + y2) / 2 + 3.4),
      'text-anchor':left ? 'end' : 'start', class:'k-t-hi'}, t); }

function dimVB(y1, y2, x, t, left, ext){         // 중략(파단) 세로 치수 — 10 m 같은 큰 값에
  var m = r2((y1 + y2) / 2);
  return (ext ? el('path', {d:'M' + ext[0] + ' ' + y1 + 'H' + ext[1] + 'M' + ext[0] + ' ' + y2 + 'H' + ext[1],
      class:'k-hi-th', 'stroke-width':.8, 'stroke-dasharray':'2 2'}) : '') +
    el('path', {d:'M' + (x - 4) + ' ' + y1 + 'h8M' + (x - 4) + ' ' + y2 + 'h8M' + x + ' ' + y1 + 'V' +
      r2(m - 6) + 'M' + x + ' ' + r2(m + 6) + 'V' + y2, class:'k-hi k-draw', 'stroke-width':1.1, pathLength:1}) +
    el('path', {d:'M' + (x - 5) + ' ' + r2(m - 2) + 'l10-5M' + (x - 5) + ' ' + r2(m + 6) + 'l10-5',
      class:'k-hi', 'stroke-width':1}) +
    el('text', {x:left ? x - 7 : x + 7, y:r2(m + 20), 'text-anchor':left ? 'end' : 'start',
      class:'k-t-hi'}, t); }

function dimD(x1, y1, x2, y2, t, off){           // 사선 치수 — 사다리 돌출, 망 내민 길이, 비탈 길이
  off = off === undefined ? 9 : off;
  var dx = x2 - x1, dy = y2 - y1, L = Math.sqrt(dx * dx + dy * dy),
      nx = r2(-dy / L * off), ny = r2(dx / L * off),
      ax = r2(x1 + nx), ay = r2(y1 + ny), bx = r2(x2 + nx), by = r2(y2 + ny),
      mx = r2((ax + bx) / 2), my = r2((ay + by) / 2 - 4),
      a = Math.atan2(dy, dx) * 180 / Math.PI;
  if(a > 90) a -= 180;
  if(a < -90) a += 180;
  return el('path', {d:'M' + x1 + ' ' + y1 + 'L' + ax + ' ' + ay + 'M' + x2 + ' ' + y2 + 'L' + bx + ' ' + by,
      class:'k-hi-th', 'stroke-width':.8}) +
    el('path', {d:'M' + ax + ' ' + ay + 'L' + bx + ' ' + by, class:'k-hi k-draw',
      'stroke-width':1.1, pathLength:1}) +
    el('text', {x:mx, y:my, 'text-anchor':'middle', class:'k-t-hi',
      transform:'rotate(' + r2(a) + ' ' + mx + ' ' + my + ')'}, t); }

function ang(cx, cy, r, a1, a2, t, cls){         // 각도 호 + 라벨 (수학 각도, 반시계 +)
  var p = function(a){ a = a * Math.PI / 180;
        return r2(cx + r * Math.cos(a)) + ' ' + r2(cy - r * Math.sin(a)); },
      mid = (a1 + a2) / 2 * Math.PI / 180, lr = r + 12;
  return el('path', {d:'M' + p(a1) + 'A' + r + ' ' + r + ' 0 ' + (Math.abs(a2 - a1) > 180 ? 1 : 0) + ' ' +
      (a2 > a1 ? 0 : 1) + ' ' + p(a2), class:(cls || 'k-hi') + ' k-draw', 'stroke-width':1.2, pathLength:1}) +
    el('text', {x:r2(cx + lr * Math.cos(mid)), y:r2(cy - lr * Math.sin(mid) + 3.4),
      'text-anchor':'middle', class:'k-t-hi'}, t); }

function sector(cx, cy, r, a1, a2, cls){         // 허용 각도 범위 부채꼴
  var p = function(a){ a = a * Math.PI / 180;
        return r2(cx + r * Math.cos(a)) + ' ' + r2(cy - r * Math.sin(a)); };
  return el('path', {d:'M' + cx + ' ' + cy + 'L' + p(a1) + 'A' + r + ' ' + r + ' 0 0 ' +
    (a2 > a1 ? 0 : 1) + ' ' + p(a2) + 'Z', class:cls || 'k-hi-f2'}); }

function slope(x, y, run, rise, t1, t2, flip){   // 기울기 삼각형 1:n. (x,y)=직각 꼭짓점
  var sx = flip ? -1 : 1, ex = r2(x + sx * run), ty = r2(y - rise);
  return el('path', {d:'M' + x + ' ' + y + 'V' + ty + 'L' + ex + ' ' + y + 'Z', class:'k-hi-f2'}) +
    el('path', {d:'M' + x + ' ' + y + 'V' + ty + 'M' + x + ' ' + y + 'H' + ex,
      class:'k-hi k-draw', 'stroke-width':1.2, pathLength:1}) +
    note(r2(x - sx * 5), r2(y - rise / 2 + 3.4), t1, 'k-t-hi', flip ? 'start' : 'end') +
    note(r2(x + sx * run / 2), y + 12, t2, 'k-t-hi', 'middle'); }

function note(x, y, t, cls, anchor, sz){
  return el('text', {x:x, y:y, 'text-anchor':anchor || 'start', class:cls || 'k-t-dim',
    'font-size':sz || null}, t); }

function lead(x1, y1, x2, y2, t, cls, anchor){   // 지시선 — 6 px 미만 치수 · 부재 명칭
  var c = cls || 'k-hi';
  return el('circle', {cx:x1, cy:y1, r:1.8, class:c === 'k-bad' ? 'k-bad-f' : 'k-hi-f'}) +
    el('path', {d:'M' + x1 + ' ' + y1 + 'L' + x2 + ' ' + y2, class:c, 'stroke-width':.9}) +
    note(x2 + (anchor === 'end' ? -4 : 4), r2(y2 + 3.4), t,
      c === 'k-bad' ? 'k-t-bad' : 'k-t-hi', anchor || 'start'); }

function arrow(x1, y1, x2, y2, cls, w){
  var a = Math.atan2(y2 - y1, x2 - x1), h = 5.5;
  return el('path', {d:'M' + x1 + ' ' + y1 + 'L' + x2 + ' ' + y2 +
    'M' + x2 + ' ' + y2 + 'L' + r2(x2 - h * Math.cos(a - .42)) + ' ' + r2(y2 - h * Math.sin(a - .42)) +
    'M' + x2 + ' ' + y2 + 'L' + r2(x2 - h * Math.cos(a + .42)) + ' ' + r2(y2 - h * Math.sin(a + .42)),
    class:cls || 'k-hi', 'stroke-width':w || 1.6, 'stroke-linecap':'round'}); }

function detail(cx, cy, r, sx, sy, sr, inner, label){   // 확대 상세원. inner 좌표는 원 중심 기준
  return el('circle', {cx:sx, cy:sy, r:sr, class:'k-dim-s'}) +
    el('path', {d:'M' + sx + ' ' + sy + 'L' + cx + ' ' + cy, class:'k-dim',
      'stroke-width':.8, 'stroke-dasharray':'3 3'}) +
    el('circle', {cx:cx, cy:cy, r:r, class:'k-detail'}) +
    el('g', {transform:'translate(' + cx + ',' + cy + ')'}, inner) +
    (label ? note(cx, r2(cy + r + 10), label, 'k-t-hi', 'middle', 9.5) : ''); }

function warnTri(x, y, s){
  return el('g', {transform:'translate(' + x + ',' + y + ') scale(' + (s || 1) + ')'},
    el('path', {d:'M0 0l13 23h-26z', class:'k-bad', 'stroke-width':2, 'stroke-linejoin':'round'}) +
    el('path', {d:'M0 9v6M0 18v2', class:'k-bad', 'stroke-width':2, 'stroke-linecap':'round'})); }
```

### 장면 진입점 교체

`SC` 의 값이 문자열이었지만 이제 **함수**도 받는다(축척 지역변수 `k` 를 두기 위해). `artFor` 를 통째로 바꾼다.

```js
function artFor(c){
  var key = c.art || c.k || c.req || 'site',
      body = SC[key] || SC.site;
  if(typeof body === 'function') body = body();
  var hurt = c.s === '사고'
    ? el('rect', {x:0, y:0, width:VW, height:VH, class:'k-hitwash'}) + warnTri(300, 12)
    : '';
  return '<svg viewBox="0 0 ' + VW + ' ' + VH + '" preserveAspectRatio="xMidYMid meet" role="img" ' +
    'aria-label="' + (c.f ? c.f.replace(/<[^>]+>/g, '').replace(/"/g, '') : (c.s || '작업 장면')) + '">' +
    DEFS + body + hurt + '</svg>';
}
```

`.cap` 문자열은 여기서 사라진다(⑥에서 과목 줄의 칩으로 옮긴다).

### 새 카드 한 장에 드는 코드

목표대로 3~5줄이다. 축척 한 줄 + 그림 두세 줄 + 치수 한두 줄.

```js
rail: function(){ var s = P(44);
  return ground() + slab(16, GY, 284, 7) + wall(268, 52, s.up(1.9), GY) +
    bar(60, GY, 60, s.up(.9), 2.6) + bar(248, GY, 248, s.up(.9), 2.6) +
    bar(60, s.up(.9), 248, s.up(.9), 3.2, 'k-hi') + bar(60, s.up(.45), 248, s.up(.45), 2.2) +
    plate(60, s.up(.1), 188, s.m(.1)) + man(150, s.k) +
    dimV(s.up(.9), GY, 292, '90 cm 이상', 1, [248, 292]) +
    lead(210, s.up(.05), 232, 126, '발끝막이판 10 cm'); }
```

---

## ② 다시 그린 SVG 코드

전부 `SC` 객체 안의 항목이다. 값이 문자열에서 **함수**로 바뀌었다(③의 `artFor` 교체가 선행되어야 한다).
각 장면 첫 줄의 `P(k)` 가 그 판의 축척이고, 그 아래 모든 좌표가 거기서 나온다.

프리미티브 하나를 ②에서 더 쓴다.

```js
function cleats(x1, y1, x2, y2, n, h){           // 경사면 미끄럼막이 · 계단 논슬립
  var dx = x2 - x1, dy = y2 - y1, L = Math.sqrt(dx * dx + dy * dy),
      nx = r2(-dy / L * h), ny = r2(dx / L * h), d = '', i, t;
  for(i = 1; i < n; i++){ t = i / n;
    d += 'M' + r2(x1 + dx * t) + ' ' + r2(y1 + dy * t) + 'l' + nx + ' ' + ny; }
  return el('path', {d:d, class:'k-hi', 'stroke-width':2, 'stroke-linecap':'round'}); }
```

### 건설안전기술

```js
/* 낙하물 방지망 — 10 m 이내마다 · 내민 2 m 이상 · 수평면과 20~30°
   고친 것: 각도를 14.7°→25° 실각도로. 허용 20~30° 부채꼴 안에 망을 넣음.
            벽에 파단선을 넣어 10 m 간격을 한 판에 정직하게 표기.
            낙하물이 허공에서 끊기지 않고 아래 망에 실제로 떨어짐.
            2 m 를 망과 나란한 사선 치수로 붙임(가로 투영이 아니라 내민 길이). */
net: function(){
  var s = P(26), wx = 52, yA = 30, yB = 88,
      a = mesh(wx, yA, s.m(2), 25), b = mesh(wx, yB, s.m(2), 25);
  return ground() + wall(28, 24, 2, GY) + brk(26, 54, 59) + plate(150, GY, 158, 5) +
    sector(wx, yB, 40, 20, 30) + a.g + b.g + man(210, s.k) +
    el('rect', {x:71, y:40, width:8, height:8, class:'k-bad-f'}) +
    arrow(75, 50, 75, b.yAt(75) - 4, 'k-bad', 1.3) +
    dimD(wx, yB, b.x, b.y, '내민 2 m 이상', -11) +
    dimVB(yA, yB, 130, '10 m 이내마다', 0, [a.x, 130]) +
    ang(wx, yB, 22, 0, 25, '20~30°') +
    note(316, 124, '아래 보행로는 망 밖', 'k-t-dim', 'end', 9);
},

/* 추락방호망 — 작업면~설치지점 10 m 이하 · 내민 3 m 이상 · 처짐 12 % 이상
   고친 것: 처짐을 스팬의 실제 12 %(150 px 의 18 px)로 작도(전엔 17.5 %).
            수직거리 치수를 슬래브~지면(잘못)에서 작업면~망으로 옮기고 파단 표기.
            추락 파선을 없애고 실제로 떨어지는 사람을 그림. */
fall: function(){
  var s = P(13), dy = 30, ny = 68, n = sagNet(85, ny, 235, ny, 18);
  return ground() + slab(0, dy, 124, 8) + slab(196, dy, 124, 8) +
    bar(85, ny, 235, ny, .9, 'k-hi-th') + n.g +
    man(58, s.k, 'stand', dy) + manFall(160, 50, s.k) +
    dimH(85, 124, 100, '내민 3 m 이상', [ny, 100]) +
    dimV(ny, n.low, 160, '처짐 12 %', 0) +
    dimVB(dy + 8, ny, 58, '10 m 이하', 1, [85, 58]) +
    note(316, 124, '작업면~망 설치지점', 'k-t-dim', 'end', 9);
},

/* 안전난간 — 상부 90 cm 이상 · 중간대 · 발끝막이판 10 cm 이상
   고친 것: 44 px/m 하나로 통일. 상부 난간대가 근로자 키의 53 % 지점(허리)에 온다.
            10 cm(4.4 px)는 치수선을 포기하고 지시선으로. 개구부를 실제로 그림. */
rail: function(){
  var s = P(44), h = s.up(.9), mid = s.up(.45);
  return el('rect', {x:0, y:GY, width:56, height:VH - GY, class:'k-void'}) + slab(56, GY, 264, 7) +
    bar(64, GY, 64, h, 2.6) + bar(248, GY, 248, h, 2.6) +
    bar(60, h, 252, h, 3.2, 'k-hi') + bar(60, mid, 252, mid, 2.2) +
    plate(64, s.up(.1), 184, s.m(.1)) + man(160, s.k) +
    dimV(h, GY, 300, '90 cm', 1, [252, 300]) +
    lead(210, s.up(.05), 200, 126, '발끝막이판 10 cm 이상', 'k-hi', 'end') +
    note(8, 100, '개구부', 'k-t-dim') +
    note(316, 16, '120 cm 초과 시 중간대 2단', 'k-t-dim', 'end', 9);
},

/* 사다리식 통로 — 75° 이하 · 상단 60 cm 이상 돌출 · 폭 30 cm 이상
   고친 것: 58.5°→75° 실각도(수직 78 : 수평 20.9). 판 밖(y=-3)으로 잘리던 돌출부를
            판 안으로 들이고, 60 cm 를 그 부재에 나란한 사선 치수로 붙임. 발치에 각도 호. */
ladder: function(){
  var s = P(30), fx = 129.1, tx = 154.7, ty = 12.6, ly = 30;
  return ground() + wall(150, 170, ly, GY) + slab(150, ly, 170, 9) +
    ladderRun(fx, GY, tx, ty, s.m(.3), 8) + man(58, s.k) +
    ang(fx, GY, 20, 0, 75, '75° 이하') +
    dimD(150, ly, tx, ty, '60 cm', 13) +
    note(316, 124, '상단 60 cm 이상 돌출 · 폭 30 cm 이상', 'k-t-dim', 'end', 9);
},

/* 가설통로 — 30° 이하 · 15° 초과 시 미끄럼막이
   고친 것: 그린 각 16.9°와 라벨 30°의 불일치를 없애고 카드 상황인 22°를 실각도로.
            판정 경계인 15° 를 파선 기준선으로 함께 보여 "왜 미끄럼막이가 필요한가"를 만듦. */
ramp: function(){
  var s = P(26), x0 = 24, y0 = GY, x1 = 224, y1 = r2(GY - 200 * Math.tan(22 * Math.PI / 180));
  return ground() + slab(224, y1, 96, 8) +
    bar(x0, y0, x1, y1, 3.2) + cleats(x0, y0, x1, y1, 9, 6) +
    bar(x0, y0, 224, r2(GY - 200 * Math.tan(15 * Math.PI / 180)), .9, 'k-dim-d') +
    man(140, s.k, 'stand', r2(GY - 116 * Math.tan(22 * Math.PI / 180))) +
    ang(x0, y0, 52, 0, 22, '22°') +
    note(228, 58, '15°', 'k-t-dim') +
    note(316, 124, '30° 이하 · 15° 초과 시 미끄럼막이', 'k-t-dim', 'end', 9);
},

/* 작업발판 — 폭 40 cm 이상 · 재료 간 틈 3 cm 이하 · 지지물 2개 이상
   고친 것: 입면도에서는 폭을 그릴 수 없다. 평면도로 바꿔 40 cm 가 화면 세로가 되게 함.
            틈 3 cm 는 실제 비율(3 px)로 그려 "거의 보이지 않아야 정상"임을 보임.
            발 윤곽을 넣어 폭 40 cm 가 발 하나 겨우인 치수임을 눈으로 알게 함. */
plank: function(){
  var s = P(85);
  return note(160, 14, '평면 · 위에서 본 것', 'k-t-dim', 'middle', 9) +
    plate(30, 26, 260, s.m(.4)) + plate(30, 63, 260, s.m(.4)) +
    el('path', {d:'M70 20V104M250 20V104', class:'k-dim-d', 'stroke-width':1.4}) +
    el('rect', {x:150, y:30, width:9, height:22, rx:4.5, class:'k-body-f'}) +
    el('rect', {x:164, y:32, width:9, height:22, rx:4.5, class:'k-body-f'}) +
    dimV(26, 60, 16, '40 cm 이상', 0) +
    lead(200, 61.5, 236, 16, '틈 3 cm 이하') +
    note(70, 118, '지지물 2개 이상 고정', 'k-t-dim', 'middle', 9);
},

/* 강관비계 — 기둥 띠장방향 1.85 m · 띠장 2 m 이하 · 벽이음 5×5 m
   고친 것: 50 px=1.85 m 와 56 px=5 m 가 한 판에 있던 축척 충돌 제거(11.5 px/m 단일).
            격자 프리미티브 한 줄로 비계를 그리고, 세 치수가 서로 비례하게 됨. */
scaffold: function(){
  var s = P(11.5), gx = 96, gy0 = 16, gw = s.m(1.85) * 4, gh = s.m(2) * 4;
  return ground() + wall(52, 26, 2, GY) + grid(gx, gy0, gw, gh, 4, 4) +
    bar(gx, gy0, r2(gx + gw / 4), r2(gy0 + gh / 4), 1.1, 'k-dim') +
    bar(78, 39, gx, 39, 2.4, 'k-hi') + bar(78, 85, gx, 85, 2.4, 'k-hi') +
    man(139, s.k, 'stand', 85) +
    dimH(gx, r2(gx + gw / 4), 124, '기둥 1.85 m', [GY, 124]) +
    dimV(gy0, 39, 196, '띠장 2 m', 0, [r2(gx + gw), 196]) +
    dimV(39, 85, 268, '≤5 m', 0, [r2(gx + gw), 268]) +
    note(316, 124, '벽이음 수직·수평 5 m 이하', 'k-t-dim', 'end', 9);
},

/* 가설계단 — 폭 1 m 이상 · 높이 3 m 초과 시 3 m 이내마다 1.2 m 계단참
   고친 것: 세 축척(50/26.7/32 px per m) 공존을 20 px/m 로 통일.
            계단참을 단 위에 정확히 앉힘(전엔 폴리라인과 어긋나 떠 있었다).
            폭 1 m 는 입면에서 잴 수 없으므로 상세원 안 평면 조각으로 뺌. */
stairs: function(){
  var s = P(20), x0 = 140, d = '', i, px, py, ln = 236, ly = 48;
  for(i = 0; i < 16; i++){ px = r2(x0 + i * 6); py = r2(GY - i * 3.75);
    d += 'M' + px + ' ' + py + 'v-3.75h6'; }
  for(i = 0; i < 4; i++){ px = r2(260 + i * 6); py = r2(ly - i * 3.75);
    d += 'M' + px + ' ' + py + 'v-3.75h6'; }
  return ground() + el('path', {d:d, class:'k-line', 'stroke-width':2}) +
    plate(ln, ly, 24, 5) + man(200, s.k, 'stand', 70.5) +
    dimV(ly, GY, 120, '3 m 이내마다', 1, [x0, 120]) +
    dimH(ln, 260, 40, '계단참 1.2 m', [ly, 40]) +
    detail(56, 44, 26, 176, 62, 10,
      el('path', {d:'M-16-11V11M16-11V11', class:'k-line', 'stroke-width':1.6}) +
      el('path', {d:'M-16 2H16', class:'k-hi', 'stroke-width':1.2}), '폭 1 m 이상');
},

/* 굴착면 기울기 — 모래 1:1.8
   고친 것: 이 판의 가장 큰 오류. 그려진 비탈이 1:0.85 인데 라벨은 1:1.8 이었다.
            수직 64 : 수평 115.2 로 다시 깎아 실제 1:1.8 로 만들고,
            카드가 다루는 위반값 1:0.8 을 붉은 파선 유령으로 겹쳐 차이를 보게 함.
            비탈면 위에 기울기 삼각형(수직 1 / 수평 1.8)을 얹음. */
trench: function(){
  var s = P(20), tx = 96, ty = 44, bx = r2(tx + 64 * 1.8);
  return soil(['0 ' + ty, tx + ' ' + ty, bx + ' ' + GY, '320 ' + GY, '320 132', '0 132']) +
    el('path', {d:'M0 ' + ty + 'H' + tx + 'L' + bx + ' ' + GY + 'H320', class:'k-line', 'stroke-width':1.8}) +
    el('path', {d:'M' + tx + ' ' + ty + 'L147.2 ' + GY, class:'k-bad-d', 'stroke-width':1.6}) +
    slope(130, 82.9, 36, 20, '1', '1.8') + man(268, s.k) +
    el('path', {d:'M40 12v8M64 6v8M88 14v8M52 24v6', class:'k-dim', 'stroke-width':1.2}) +
    note(150, 122, '1 : 0.8 (미달)', 'k-t-bad', 'middle', 9.5) +
    note(316, 14, '모래 1:1.8 · 그 밖의 흙 1:1.2', 'k-t-dim', 'end', 9) +
    note(316, 26, '연암·풍화암 1:1.0 · 경암 1:0.5', 'k-t-dim', 'end', 9);
},

/* 동바리 — 파이프서포트 3개 이상 이음 금지 · 이음 볼트 4개 이상 · 3.5 m 초과 시 2 m마다 수평연결재
   고친 것: '2 m마다'를 기둥 사이 가로 치수로 그려 뜻이 반대였다. 수평연결재 두 줄의
            세로 간격으로 옮김. 축척을 17 px/m 로 통일. 이음부를 슬리브+볼트로 보이게 하고
            볼트 4개는 상세원으로. '#2A3purple'.replace() 잔재 제거. */
shore: function(){
  var s = P(17), top = 24, xs = [64, 134, 204, 274], d = '', i;
  for(i = 0; i < 4; i++) d += 'M' + xs[i] + ' ' + top + 'V' + GY;
  return ground() + slab(14, 14, 292, 10) +
    el('path', {d:d, class:'k-line', 'stroke-width':3}) +
    xs.map(function(x){ return el('rect', {x:x - 5, y:86, width:10, height:13, class:'k-plate'}); }).join('') +
    bar(50, 74, 288, 74, 2.2, 'k-hi') + bar(50, 40, 288, 40, 2.2, 'k-hi') +
    arrow(90, 2, 90, 12) + arrow(170, 2, 170, 12) + arrow(250, 2, 250, 12) +
    dimV(40, 74, 300, '2 m', 1, [274, 300]) +
    dimV(top, GY, 34, '3.5 m 초과', 0, [64, 34]) +
    detail(150, 48, 24, 64, 92, 9,
      el('path', {d:'M0-20V20', class:'k-line', 'stroke-width':4}) +
      el('rect', {x:-7, y:-9, width:14, height:18, class:'k-plate'}) +
      el('path', {d:'M-4-5h8M-4 1h8', class:'k-hi', 'stroke-width':1.6}), '이음 볼트 4개 이상') +
    note(316, 124, '3개 이상 이음 금지', 'k-t-dim', 'end', 9);
},

/* 말비계 — 지주부재 75° 이하 · 2 m 초과 시 발판 폭 40 cm 이상
   고친 것: 그린 각 57°→75° 실각도. '폭 40 cm'를 발판 길이(128 px)에 붙여
            320 px/m 와 30 px/m 가 100배 차이 나던 것을 사판(斜板)으로 바꿔
            폭이 실제 깊이변이 되게 함. 하단 미끄럼 방지 부재 추가. */
horse: function(){
  var s = P(26), py = s.up(2), r = r2(s.m(2) / Math.tan(75 * Math.PI / 180));
  return ground() +
    bar(r2(110 - r), GY, 110, py, 2.8) + bar(r2(110 + r), GY, 110, py, 2.8) +
    bar(r2(220 - r), GY, 220, py, 2.8) + bar(r2(220 + r), GY, 220, py, 2.8) +
    [110 - r, 110 + r, 220 - r, 220 + r].map(function(x){
      return el('rect', {x:r2(x - 4), y:104, width:8, height:4, class:'k-hi-f'}); }).join('') +
    deck(92, py - 4, 146, s.m(.4), 5) + man(170, s.k, 'stand', py - 4) +
    ang(r2(110 - r), GY, 26, 0, 75, '75° 이하') +
    dimD(238, py - 4, r2(238 + s.m(.4) * .62), r2(py - 4 - s.m(.4) * .78), '40 cm', 9) +
    dimV(py - 4, GY, 290, '2 m 초과', 1, [234, 290]) +
    note(316, 16, '하단 미끄럼 방지', 'k-t-dim', 'end', 9);
},

/* 항타기·항발기 — 버팀대 3개 이상 · 권상 와이어로프 안전계수 5 이상 · 드럼 2회 이상 남김
   고친 것: 셋째 버팀대가 기둥과 겹쳐 둘로만 보였다. 앞쪽으로 빼고,
            평면 상세원에서 120° 3방향임을 못박음. 드럼 잔여 감김도 상세원으로. */
pile: function(){
  return ground() + bar(150, GY, 150, 12, 4.5) + plate(126, 102, 48, 6) +
    bar(150, 28, 66, GY, 2.4) + bar(150, 28, 234, GY, 2.4) + bar(150, 28, 168, 118, 2.4) +
    bar(150, 16, 196, 16, 2) + bar(196, 16, 196, 86, 1.6, 'k-hi') + plate(184, 86, 24, 16) +
    detail(60, 44, 24, 150, 44, 9,
      el('circle', {cx:0, cy:0, r:13, class:'k-line', fill:'none', 'stroke-width':1.4}) +
      el('circle', {cx:0, cy:0, r:9, class:'k-hi', fill:'none', 'stroke-width':1.4}) +
      el('circle', {cx:0, cy:0, r:6, class:'k-hi', fill:'none', 'stroke-width':1.4}), '드럼 2회 이상') +
    detail(268, 42, 24, 150, 30, 9,
      el('circle', {cx:0, cy:0, r:3, class:'k-hi-f'}) +
      el('path', {d:'M0 0L0-15M0 0L13 8M0 0L-13 8', class:'k-hi', 'stroke-width':1.6}), '버팀대 3개 이상') +
    note(316, 124, '권상 와이어로프 안전계수 5 이상', 'k-t-dim', 'end', 9);
},

/* 강관틀비계 — SC 에 아예 없어 사무동 그림(SC.site)으로 떨어지던 카드. 신규 작도.
   높이 20 m 초과 또는 중량물 적재 시 주틀 간격 1.8 m 이하 */
frame: function(){
  var s = P(13), pitch = s.m(1.8);
  return ground() + wall(40, 22, 2, GY) + frames(84, 20, pitch, 76, 5) +
    plate(84, 16, r2(pitch * 4 + pitch * .72), 5) + man(214, s.k, 'stand', 96) +
    dimH(84, r2(84 + pitch), 124, '주틀 간격 1.8 m 이하', [GY, 124]) +
    dimVB(4, 96, 250, '20 m 초과', 0, [r2(84 + pitch * 4.72), 250]) +
    note(316, 16, '중량물 적재 시에도 1.8 m 이하', 'k-t-dim', 'end', 9);
},

/* 인력 운반 — 남성 체중의 40 % · 무릎을 굽혀 · 몸에 붙여서
   고친 것: 상자가 사람에게서 30 px 떨어져 공중에 떠 있었고 자세는 곧게 선 막대사람이라
            '무릎 굽혀'와 정반대였다. 웅크린 자세로 바꾸고 짐을 몸에 붙임.
            허리만 굽힌 오답 자세를 붉은 유령으로 나란히 둠. */
carry: function(){
  var s = P(44);
  return ground() + man(96, s.k, 'carry') +
    el('rect', {x:104, y:62, width:30, height:24, class:'k-plate'}) +
    el('g', {class:'k-ghost'}, man(246, s.k, 'stoop')) +
    el('rect', {x:254, y:70, width:26, height:20, class:'k-bad-d2'}) +
    el('path', {d:'M228 24l20 20M248 24l-20 20', class:'k-bad', 'stroke-width':2.2}) +
    lead(134, 74, 300, 40, '체중 40 % 이하', 'k-hi', 'end') +
    note(96, 124, '무릎 굽혀 다리 힘으로 · 몸에 붙여서', 'k-t-dim', 'middle', 9);
},
```

`man()` 에 한 줄 보탠다. 앉은 자세는 머리가 원점에서 1.7 m 가 아니라 0.85 m 위에 있다.

```js
function man(x, k, pose, gy, flip){
  var s = r2(1.7 * k / 24), dy = pose === 'sit' ? r2(11 * s) : 0,   /* ← 이 줄 */
      t = 'translate(' + r2(x) + ',' + ((gy === undefined ? GY : r2(gy)) + dy) + ') scale(' +
          (flip ? -s : s) + ',' + s + ')';
  /* 이하 동일 */ }
```

### 기계위험방지

```js
/* 롤러기 — 손 조작식 급정지 조작부 밑면에서 1.8 m 이내 · 급정지거리 원주의 1/3
   고친 것: 아래 롤러(cy 104, r 26)가 지면 아래 22 px 묻혀 있었다. 지면 위로 올림.
            근로자 20 px(=0.5 m)를 40 px/m 기준 68 px 로. 조작부 1.8 m 가 사람 머리
            바로 위에 오면서 "이건 상한값"이라는 게 눈에 보이게 됨. */
roller: function(){
  var s = P(40), tb = s.up(1.8);
  return ground() + plate(150, 20, 80, 6) +
    el('circle', {cx:190, cy:44, r:20, class:'k-solid'}) +
    el('circle', {cx:190, cy:84, r:20, class:'k-solid'}) +
    bar(160, 64, 220, 64, 2.6, 'k-bad') +
    bar(120, tb, 266, tb, 3.2, 'k-hi') + bar(128, tb, 128, GY, 2) + bar(258, tb, 258, GY, 2) +
    man(96, s.k) +
    dimV(tb, GY, 74, '1.8 m 이내', 1, [120, 74]) +
    lead(220, 64, 256, 20, '물림점', 'k-bad') +
    detail(276, 78, 26, 190, 64, 9,
      el('circle', {cx:0, cy:0, r:15, class:'k-line', fill:'none', 'stroke-width':1.4}) +
      el('path', {d:'M15 0A15 15 0 0 1 -7.5 13', class:'k-bad', 'stroke-width':3}), '원주의 1/3') +
    note(316, 16, '복부 0.8~1.1 m · 무릎 0.4~0.6 m', 'k-t-dim', 'end', 9);
},

/* 연삭기 덮개 — 탁상용 노출각도 125° 이내 · 워크레스트 간격 3 mm 이하
   고친 것: 부채꼴만 있고 각도 호·라벨이 없어 125° 를 읽을 수 없었다. ang() 로 명시.
            숫돌 아래를 파고들던 받침 블록을 정리하고, 3 mm(=1.4 px)는 8배 상세원으로. */
grinder: function(){
  return ground() + plate(112, 96, 56, 12) + bar(140, 96, 140, 58, 3) +
    el('circle', {cx:140, cy:58, r:36, class:'k-solid'}) +
    el('circle', {cx:140, cy:58, r:6, class:'k-line', fill:'none', 'stroke-width':1.4}) +
    el('path', {d:'M152.4 19.4A41 41 0 1 0 163.5 91.5', class:'k-cover', 'stroke-width':6}) +
    sector(140, 58, 36, 55, -70) +
    ang(140, 58, 26, 55, -70, '125° 이내') +
    plate(180, 66, 36, 6) +
    detail(58, 40, 26, 177, 68, 8,
      el('path', {d:'M-18-14A22 22 0 0 1-18 14', class:'k-line', 'stroke-width':3}) +
      el('rect', {x:-4, y:-4, width:22, height:8, class:'k-plate'}) +
      el('path', {d:'M-9-9v18M-4-9v18', class:'k-hi', 'stroke-width':1}), '워크레스트 3 mm 이하') +
    note(316, 118, '상부 사용 60° · 원통 180°', 'k-t-dim', 'end', 9) +
    note(316, 129, '평면·절단 150°', 'k-t-dim', 'end', 9);
},

/* 프레스 안전거리 — D(mm) ≥ 1.6 × T(ms)
   고친 것: D 를 프레임과 '허공에 뜬 근로자'(y 96, 지면 108) 사이에서 쟀다.
            D 는 방호장치↔위험한계 거리인데 방호장치가 그려져 있지 않았다.
            광전자식 센서면(붉은 파선 3줄)을 세우고 D 를 센서면↔금형 위험한계로.
            사람 전신 대신 손·팔뚝만 그린다(90 px/m 근경이라 전신은 판을 넘는다). */
press: function(){
  return ground() + slab(60, 8, 200, 14) + bar(72, 22, 72, 100, 3.4) + bar(248, 22, 248, 100, 3.4) +
    plate(96, 30, 128, 20) + plate(96, 86, 128, 12) + band(96, 50, 128, 36) +
    bar(262, 26, 262, 100, 2.2) + bar(300, 26, 300, 100, 2.2) +
    el('path', {d:'M262 44H300M262 62H300M262 80H300', class:'k-bad-d', 'stroke-width':1.4}) +
    el('path', {d:'M320 66h-52a7 7 0 0 1 0-14h34', class:'k-body', 'stroke-width':6,
      'stroke-linecap':'round', fill:'none'}) +
    dimH(224, 262, 112, 'D ≥ 1.6 × T', [100, 112]) +
    lead(224, 68, 180, 128, '위험한계', 'k-bad', 'end') +
    note(316, 16, '손 속도 1.6 m/s 기준', 'k-t-dim', 'end', 9);
},

/* 둥근톱 반발예방장치 — 분할날·톱날 원주면 간격 12 mm 이내 · 분할날 두께 톱날의 1.1배 이상
   고친 것: 12 mm 치수선이 y=36 에 있었는데 그 높이의 톱날은 x=130 — 아무것도 잡지
            않는 치수선이었다. 초승달로 그려져 날로 안 읽히던 분할날을 톱날 원주를
            따르는 두께 있는 부재로. 12 mm 는 5배 상세원으로 뺌. */
sawblade: function(){
  return ground() + plate(16, 70, 288, 7) +
    el('circle', {cx:140, cy:96, r:44, class:'k-line', fill:'none', 'stroke-width':2}) +
    el('path', {d:'M166 51A52 52 0 0 1 189 78', class:'k-hi', 'stroke-width':4,
      'stroke-linecap':'round'}) +
    el('path', {d:'M204 62h30v8h-30z', class:'k-plate'}) +
    detail(64, 38, 26, 178, 62, 9,
      el('path', {d:'M-16-16A24 24 0 0 1 4 16', class:'k-line', 'stroke-width':3}) +
      el('path', {d:'M2-18A24 24 0 0 1 20 8', class:'k-hi', 'stroke-width':3}) +
      el('path', {d:'M-6-14L6-19', class:'k-hi', 'stroke-width':1}), '간격 12 mm 이내') +
    lead(219, 62, 260, 22, '반발예방 발톱') +
    note(316, 124, '분할날 두께 = 톱날의 1.1배 이상', 'k-t-dim', 'end', 9);
},

/* 지게차 헤드가드 — 개구부 16 cm 미만 · 좌석 윗면~상부틀 0.903 m 이상
   고친 것: 좌석이 없는데 0.903 m 를 떠 있는 글자로 적었다. 좌석과 앉은 운전자를 넣어
            치수선이 실제 두 면(좌석 윗면·상부틀 밑면)에 닿게 함.
            18/24/22 px 로 제각각이던 개구부를 16 cm(4.2 px) 등간격 살대로 다시 짜고
            그중 한 칸을 5배 상세원으로. */
forklift: function(){
  var s = P(26), gy0 = 42.5, sy = 66, d = '', i;
  for(i = 0; i <= 17; i++) d += 'M' + r2(106 + i * 4.24) + ' ' + gy0 + 'v6';
  return ground() + plate(96, 72, 88, 24) + wheel(114, 100, 8) + wheel(166, 100, 8) +
    plate(120, sy, 32, 6) + bar(150, sy, 150, 52, 3) +
    bar(104, gy0, 182, gy0, 3.2, 'k-hi') + el('path', {d:d, class:'k-hi', 'stroke-width':1}) +
    bar(106, gy0, 106, 72, 2.4) + bar(180, gy0, 180, 72, 2.4) +
    bar(184, 96, 214, 96, 3.4) + bar(184, 40, 184, 96, 3.4) +
    man(134, s.k, 'sit', sy) +
    dimV(gy0 + 6, sy, 232, '0.903 m 이상', 0, [182, 232]) +
    detail(268, 92, 24, 140, 45, 7,
      el('path', {d:'M-12-14v28M12-14v28', class:'k-hi', 'stroke-width':2}) +
      el('path', {d:'M-12 0H12M-12-4v8M12-4v8', class:'k-hi', 'stroke-width':1.2}), '16 cm 미만') +
    note(316, 16, '입승식은 1.88 m 이상', 'k-t-dim', 'end', 9);
},

/* 산업용 로봇 — 울타리 1.8 m 이상 · 곤란하면 안전매트·광전자식
   고친 것: 8 px 가로 눈금이 울타리로 안 읽혔다. 세로 살대로 다시 짬.
            30 px/m 로 두면 울타리 54 px > 사람 51 px 이라 '1.8 m 이상'이 눈으로 확인된다. */
robot: function(){
  var s = P(30), fy = s.up(1.8), d = '', i;
  for(i = 0; i <= 8; i++) d += 'M' + r2(204 + i * 4) + ' ' + fy + 'V' + GY;
  return ground() + plate(94, 90, 48, 18) + bar(118, 90, 118, 50, 5) + bar(118, 50, 168, 32, 4) +
    el('circle', {cx:118, cy:50, r:5, class:'k-hi-f'}) + el('circle', {cx:168, cy:32, r:4, class:'k-hi-f'}) +
    band(140, GY - 4, 56, 4, 'k-hi-f2') +
    el('path', {d:d, class:'k-line', 'stroke-width':1}) +
    bar(204, fy, 236, fy, 2.6, 'k-hi') + bar(204, fy, 204, GY, 2.4) + bar(236, fy, 236, GY, 2.4) +
    man(280, s.k) +
    dimV(fy, GY, 252, '1.8 m', 0, [236, 252]) +
    lead(168, 104, 130, 126, '안전매트', 'k-hi', 'end') +
    note(316, 16, '곤란하면 광전자식 방호장치', 'k-t-dim', 'end', 9);
},
```

### 전기위험방지

```js
/* 전기 기계·기구 조작 — 작업공간 폭 70 cm 이상 · 조작부 조도 150 lux 이상
   고친 것: 160 px 을 70 cm(=229 px/m)로 적어 놓고 같은 판의 사람은 24 px(=0.10 m)였다.
            44 px/m 하나로 통일하니 70 cm 는 31 px, 사람은 75 px. 어깨가 양쪽에 닿는
            좁기가 그대로 보인다(팔 붙인 narrow 자세). */
panelspace: function(){
  var s = P(44), gapL = 86, gapR = gapL + s.m(.7);
  return ground() + el('rect', {x:30, y:26, width:56, height:GY - 26, class:'k-solid'}) +
    plate(40, 40, 36, 22) + bar(48, 52, 68, 52, 2, 'k-hi') +
    wall(gapR, 40, 2, GY) + man(r2((gapL + gapR) / 2), s.k, 'narrow') +
    bar(58, 2, 58, 12, 2) + sector(58, 12, 46, -55, -125, 'k-hi-f2') +
    dimH(gapL, gapR, 124, '70 cm 이상', [GY, 124]) +
    lead(58, 46, 160, 22, '조작부 150 lux 이상') +
    note(316, 124, '곤란하면 절연용 보호구 착용', 'k-t-dim', 'end', 9);
},

/* 충전전로 접근한계거리 — 15 kV 60 cm
   고친 것: 치수선이 근로자 '몸통 중심'에 닿았다. 접근한계는 충전부↔신체 최근접부이므로
            손 뻗은 자세로 바꾸고 치수선 끝을 손끝에 붙임. 사람 24 px(=0.55 m)를 51 px 로. */
approach: function(){
  var s = P(30), cx = 250, cy = 62, rr = s.m(.6), hand = 215;
  return ground() + bar(292, GY, 292, 4, 4) + bar(292, 44, 258, 44, 2.4) +
    bar(258, 44, 258, 56, 1.6) + el('circle', {cx:cx, cy:cy, r:6, class:'k-bad-f'}) +
    el('circle', {cx:cx, cy:cy, r:rr, class:'k-bad-dc'}) +
    plate(176, 72, 76, 6) + man(200, s.k, 'reach', 72) +
    dimH(hand, r2(cx - rr), 96, '60 cm', [cy, 96]) +
    note(316, 14, '0.75 kV 30 · 15 kV 60 cm', 'k-t-dim', 'end', 9) +
    note(316, 26, '37 kV 90 · 145 kV 150 cm', 'k-t-dim', 'end', 9);
},

/* 가공전선로 이격거리 — 50 kV 이하 3 m
   고친 것: '3 m' 치수선이 10 px 짜리 토막이었고 위·아래 끝 어느 쪽도 전선이나 붐 끝에
            닿지 않았다. 13 px/m 로 두고 3 m = 39 px 를 전선 처짐 곡선과 붐 끝 사이에
            실제로 걸었다. 전선 둘레 이격 포락선을 파선 원으로 추가. */
powerline: function(){
  var s = P(13), w = sagNet(50, 24, 290, 24, 14), cy = 37.4, ty = r2(cy + s.m(3));
  return ground() + bar(50, GY, 50, 12, 3) + bar(290, GY, 290, 12, 3) +
    bar(36, 20, 64, 20, 2) + bar(276, 20, 304, 20, 2) + w.g +
    el('circle', {cx:196, cy:cy, r:s.m(3), class:'k-bad-dc'}) +
    bar(110, GY, 110, 96, 4) + bar(110, 96, 196, ty, 3.4) +
    el('circle', {cx:196, cy:ty, r:4, class:'k-line', fill:'none', 'stroke-width':1.4}) +
    plate(92, 96, 40, 12) + man(150, s.k) +
    dimV(cy, ty, 214, '3 m 이상', 0, [196, 214]) +
    note(316, 124, '50 kV 초과 시 10 kV마다 10 cm 추가', 'k-t-dim', 'end', 9);
},

/* 내압방폭구조 안전간극 — 접합면 틈새는 화염일주한계 이하 (ⅡB 0.5 mm)
   고친 것: 화염 호가 x=154 에서 끊겨 틈(x=160)에 닿지 않았고, 치수선은 아무것도 없는
            y=118 에 있었다. 규정의 뜻 자체 — 화염이 틈을 지나며 꺼진다 — 를
            40배 상세원 안에서 그린다(불꽃이 접합면 사이에서 가늘어지다 사라진다). */
exgap: function(){
  return el('rect', {x:40, y:30, width:145, height:70, class:'k-solid'}) +
    el('rect', {x:190, y:30, width:60, height:70, class:'k-solid'}) +
    bar(185, 26, 185, 104, 3) + bar(190, 26, 190, 104, 3) +
    el('path', {d:'M96 64l16-12-4 12h14l-18 14 5-14z', class:'k-bad-f'}) +
    el('path', {d:'M118 64h58', class:'k-bad-d', 'stroke-width':1.4}) +
    detail(268, 50, 30, 187, 64, 9,
      el('path', {d:'M-5-26v52M5-26v52', class:'k-line', 'stroke-width':5}) +
      el('path', {d:'M-28 0h20M-8-4q9 4 12 0M4 0h2', class:'k-bad', 'stroke-width':3,
        'stroke-linecap':'round'}) +
      el('path', {d:'M-5-20h10M-5-24v8M5-24v8', class:'k-hi', 'stroke-width':1.2}), 'ⅡB 0.5 mm') +
    note(316, 118, 'ⅡA 0.9 · ⅡB 0.5 mm', 'k-t-dim', 'end', 9) +
    note(316, 129, 'ⅡC 0.5 mm 미만', 'k-t-dim', 'end', 9);
},

/* 감전방지용 누전차단기 — 물기 있는 장소 15 mA · 일반 30 mA·0.03초
   고친 것: 누설전류 파선이 x=140 허공에서 끝났다. 분전반→공구→근로자→젖은 바닥→
            접지까지 한 줄로 잇는다. 접지 기호가 없던 것도 채운다. */
elcb: function(){
  var s = P(30);
  return ground('water') + el('rect', {x:236, y:20, width:70, height:64, class:'k-solid'}) +
    plate(248, 32, 46, 16) + bar(258, 40, 284, 40, 2.4, 'k-hi') + bar(271, 48, 271, 74, 2) +
    bar(236, 74, 176, 74, 1.8) + man(150, s.k, 'reach') +
    el('rect', {x:162, y:68, width:20, height:12, class:'k-plate'}) +
    el('path', {d:'M166 80v14M150 108h16', class:'k-bad-d', 'stroke-width':1.6}) +
    earth(96, GY) + bar(96, 98, 140, 98, 1, 'k-bad-d') +
    lead(271, 40, 232, 14, '15 mA · 0.03초', 'k-hi', 'end') +
    note(316, 124, '정격 50 A 이상은 200 mA · 0.1초', 'k-t-dim', 'end', 9);
},
```

### 화학설비 · 인간공학

```js
/* 밀폐공간 적정공기 — 산소 18 % 이상 23.5 % 미만 · H₂S 10 ppm 미만 · CO 30 ppm 미만
   고친 것: 사다리가 수직구 폭 전체를 채워 근로자와 겹쳤다. 사다리를 좌측 벽으로 붙이고
            근로자는 오른쪽에. 숫자가 허공에 떠 있던 것을 측정기와 지시선으로 가스층에 건다. */
confined: function(){
  var s = P(22);
  return el('rect', {x:0, y:34, width:320, height:VH - 34, class:'k-earth'}) +
    el('path', {d:'M0 34H120M200 34H320', class:'k-line', 'stroke-width':1.6}) +
    el('rect', {x:120, y:34, width:80, height:VH - 34, class:'k-void'}) +
    plate(110, 26, 100, 9) + band(122, 88, 76, 42) +
    ladderRun(128, 126, 128, 40, 11, 7) + man(176, s.k, 'stand', 126) +
    bar(214, 26, 214, 96, 1, 'k-hi') + el('rect', {x:208, y:96, width:12, height:10, class:'k-hi-f'}) +
    lead(214, 100, 246, 62, '산소 18~23.5 %') +
    note(316, 82, 'H₂S 10 ppm 미만', 'k-t-dim', 'end', 9) +
    note(316, 94, 'CO 30 ppm 미만', 'k-t-dim', 'end', 9) +
    note(316, 124, '18 % 미만이면 즉시 대피', 'k-t-dim', 'end', 9);
},

/* 정전기 재해 방지 — 이황화탄소 등 유속 1 m/s 이하 · 접지·제전기·습도
   고친 것: 규정의 핵심인 접지가 글자로만 있고 그림에 없었다. 접지 기호와 본딩선을 넣고,
            액면 충돌을 막는 딥파이프를 그린다(유속 규정이 왜 있는지가 여기서 나온다). */
staticflow: function(){
  return ground() + vessel(176, 26, 116, 82, 8) + band(186, 62, 96, 46, 'k-pace-band') +
    pipe(12, 40, 208, 40, 8) + pipe(208, 40, 208, 98, 8) +
    arrow(60, 40, 130, 40, 'k-hi', 2) +
    bar(96, 36, 96, 96, 1.2, 'k-hi') + earth(96, GY) +
    bar(292, 96, 306, 96, 1.4, 'k-hi') + earth(306, GY) +
    lead(96, 40, 60, 20, '유속 1 m/s 이하', 'k-hi', 'end') +
    lead(208, 96, 250, 122, '액면 충돌 방지', 'k-hi', 'end') +
    note(316, 16, '도전성 위험물은 7 m/s 이하', 'k-t-dim', 'end', 9);
},

/* VDT 작업 — 눈~화면 40 cm 이상 · 화면 상단이 시선 수평선 아래 10~15° · 팔꿈치 90° 이상
   고친 것: 시선 기준 수평선이 없어 각도를 읽을 수 없었고(그린 각 6.6°), 선 자세 글리프를
            앉은 사람으로 쓰고 있었다. 110 px/m 근경으로 머리·어깨만 그리고
            수평 기준선 + 12.5° 호 + 40 cm 가로 치수를 한 점(눈)에서 낸다. */
vdt: function(){
  var ex = 82, ey = 44, sx = 126, top = r2(ey + 44 * Math.tan(12.5 * Math.PI / 180));
  return plate(40, 104, 260, 7) +
    el('circle', {cx:70, cy:36, r:16, class:'k-skin'}) +
    el('path', {d:'M70 52v26M70 60l-18 10M46 76v26M52 100h58', class:'k-body', 'stroke-width':6,
      'stroke-linecap':'round', 'stroke-linejoin':'round', fill:'none'}) +
    el('circle', {cx:ex, cy:ey, r:2.4, class:'k-hi-f'}) +
    el('path', {d:'M' + ex + ' ' + ey + 'H264', class:'k-dim-d', 'stroke-width':1.2}) +
    el('rect', {x:sx, y:top, width:80, height:r2(104 - top), class:'k-solid'}) +
    bar(ex, ey, sx, top, 1.2, 'k-hi') +
    ang(ex, ey, 40, 0, -12.5, '10~15°') +
    ang(46, 100, 16, 0, 90, '90° 이상') +
    dimH(ex, sx, 20, '40 cm 이상', [20, top]) +
    note(316, 124, '화면 상단이 시선 아래에 오게', 'k-t-dim', 'end', 9);
},
```

### 나머지 — ①의 "한 줄만 고치는 것" 패치

```js
/* gangway: 선체 바닥이 수면 위에 떠 있던 것 + 규정 본체인 안전망 누락 */
gangway: function(){
  var s = P(13), g = sagNet(64, 104, 180, 62, 12, 'k-hi');
  return ground('water') +
    el('path', {d:'M176 44h144v72H196z', class:'k-solid'}) +
    bar(56, 96, 176, 50, 3) + bar(56, 84, 176, 38, 1.6) +
    cleats(56, 96, 176, 50, 7, 5) + g.g + man(120, s.k, 'stand', 73) +
    lead(240, 44, 300, 22, '300톤급 이상', 'k-hi', 'end') +
    lead(122, 92, 60, 126, '현문사다리 아래 안전망', 'k-hi', 'end');
},

/* rotor: 좌우 베어링 사이에 축이 없었다 + 원주속도를 벡터로 */
rotor: function(){
  return ground() + plate(40, 20, 16, 88) + plate(264, 20, 16, 88) +
    bar(56, 64, 264, 64, 5) +
    el('circle', {cx:160, cy:64, r:34, class:'k-solid'}) +
    el('circle', {cx:160, cy:64, r:5, class:'k-hi-f'}) +
    arrow(160, 30, 206, 30, 'k-hi', 2) +
    lead(194, 30, 240, 16, '원주속도', 'k-hi', 'end') +
    note(316, 118, '25 m/s 초과 → 격리된 장소', 'k-t-dim', 'end', 9) +
    note(316, 129, '축 1 t 초과 & 120 m/s 이상 → 비파괴검사', 'k-t-dim', 'end', 8.5);
},

/* wirerope: 매단 하중이 지면에 놓여 있었다 + 소선 절단을 상세원으로 */
wirerope: function(){
  return ground() + slab(110, 0, 100, 10) + bar(160, 10, 160, 56, 2.6, 'k-hi') +
    el('path', {d:'M154 56h12l-6 10z', class:'k-line', fill:'none', 'stroke-width':1.6}) +
    bar(160, 66, 160, 74, 2) + plate(134, 74, 52, 22) +
    detail(258, 44, 26, 160, 40, 8,
      el('path', {d:'M-16-16L16 16M-16 0L16 16M-16 16L16-8', class:'k-line', 'stroke-width':2}) +
      el('path', {d:'M-4-6l6 4', class:'k-bad', 'stroke-width':2.4}), '소선 10 % 이상 금지') +
    note(316, 112, '탑승 10 · 화물 5', 'k-t-dim', 'end', 9) +
    note(316, 124, '훅·샤클 3 · 그 밖 4 이상', 'k-t-dim', 'end', 9);
},

/* boiler: 압력계에 눈금·설정점이 없어 '최고사용압력 이하 작동'을 읽을 수 없었다 */
boiler: function(){
  return ground() + vessel(60, 42, 150, 66, 16) + bar(135, 42, 135, 20, 3) +
    el('path', {d:'M123 20h24l-6-11h-12z', class:'k-plate'}) +
    arrow(147, 14, 162, 2, 'k-hi', 1.6) + arrow(152, 18, 170, 10, 'k-hi', 1.6) +
    el('circle', {cx:246, cy:66, r:22, class:'k-void'}) +
    el('path', {d:'M230.4 50.4A22 22 0 0 1 262 51', class:'k-line', 'stroke-width':1.4}) +
    el('path', {d:'M262 51A22 22 0 0 1 252 86', class:'k-bad', 'stroke-width':3}) +
    bar(246, 66, 258, 52, 2, 'k-hi') + el('circle', {cx:246, cy:66, r:3, class:'k-hi-f'}) +
    lead(262, 51, 300, 22, '최고사용압력', 'k-hi', 'end') +
    note(316, 118, '2개 설치 시 하나는 1.05배 이하', 'k-t-dim', 'end', 9) +
    note(316, 129, '검사 매년 1회 이상', 'k-t-dim', 'end', 9);
},

/* gasweld: 토치(화기)를 '5 m 이격' 치수선 한가운데 그려 화기가 둘이었다 */
gasweld: function(){
  return ground() + cyl(40, 40, 32, 68) + cyl(78, 40, 32, 68) + bar(56, 40, 56, 30, 2.4) +
    el('path', {d:'M56 30q0-18 60-18t60 14', class:'k-line', 'stroke-width':1.6, fill:'none'}) +
    el('path', {d:'M176 26l14 6-14 6z', class:'k-hi-f'}) +
    el('rect', {x:244, y:56, width:56, height:52, class:'k-solid'}) +
    el('path', {d:'M262 96q6-14 0-24t10-10q-4 14 6 20t-4 14z', class:'k-bad-f'}) +
    dimH(110, 244, 124, '5 m 이상', [GY, 124]) +
    lead(56, 62, 130, 62, '용기 40 ℃ 이하') +
    note(316, 16, '아세틸렌 배관에 구리 70 % 이상 합금 금지', 'k-t-dim', 'end', 8.5);
},
```

`lux`, `noise`, `weather`, `mobscaf`, `caisson`, `chemdist`, `welder`, `site`, `report` 는 축척·치수 부착에 문제가 없다. 색 상수만 클래스로 바꾸고(⑤), `welder` 는 케이블 양 끝을 손과 용접기에 붙이고, `noise` 는 근로자에 귀덮개 두 줄(`el('path',{d:'M-6-19h12',class:'k-hi','stroke-width':2})`)을, `mobscaf` 는 캐스터마다 구름방지 브레이크 표시를 더한다.

---

## ④ 모션

지금 있는 것은 카드 등장/이탈과 배경 교차 페이드 둘뿐이다. **세 가지만** 더한다. 셋 다 CSS 뿐이고, 셋 다 카드 한 장에 한 번만 돈다. 반복하는 것, 계속 도는 것, 끌리는 것은 넣지 않는다.

### 1. 치수선이 그려진다 (0.5초, 카드당 한 번)

카드가 안착한 뒤 노란 치수선이 왼쪽에서 오른쪽으로 그어지고, 수치는 그 뒤에 뜬다. 그림을 보는 순서를 "구조물 → 어디에 걸리는지 → 몇인지"로 강제하는 장치이므로 장식이 아니다.

`dimH / dimV / dimVB / dimD / ang / slope` 이 전부 `pathLength="1"` 과 `class="k-hi k-draw"` 를 달고 나오므로(③) 길이가 제각각이어도 같은 속도로 그려진다. JS 없음 — `.art` 의 `innerHTML` 이 카드마다 갈아치워지면서 애니메이션이 자동으로 다시 돈다.

```css
#card .art svg .k-draw{stroke-dasharray:1;stroke-dashoffset:1;
  animation:kdraw .5s cubic-bezier(.3,.8,.4,1) .16s forwards}
@keyframes kdraw{to{stroke-dashoffset:0}}
#card .art svg .k-t-hi{opacity:0;animation:kfade .28s ease-out .5s forwards}
@keyframes kfade{to{opacity:1}}
```

### 2. 게이지 숫자가 한 번 튄다 (0.22초)

게이지 막대는 이미 `width .45s` 로 움직인다. 여기에 **숫자만** 220 ms 동안 2 px 올라갔다 내려오고, 증감 색을 1.2초 물었다가 원래 색으로 풀린다. 막대·트랙에는 손대지 않는다.

```css
.g .lb b{display:inline-block;transition:color .9s ease}
.g .lb b.up{color:var(--ok)} .g .lb b.dn{color:var(--bad)}
.g .lb b.bump{animation:gbump .22s ease-out}
@keyframes gbump{50%{transform:translateY(-2px)}}
```

```js
function flashDelta(d){
  d.forEach(function(v, i){
    var e = $('gd' + i), n = $('gv' + i);
    n.className = ''; void n.offsetWidth;                     // 재생 강제
    if(!v){ e.className = 'dlt'; return; }
    e.textContent = (v > 0 ? '+' : '') + v;
    e.className = 'dlt on ' + (v > 0 ? 'up' : 'dn');
    n.className = 'bump ' + (v > 0 ? 'up' : 'dn');
    setTimeout(function(){ e.className = 'dlt ' + (v > 0 ? 'up' : 'dn'); n.className = ''; }, 1300);
  });
}
```

### 3. 사고 카드가 한 번 흔들린다 (0.26초, 진폭 3 px)

카드 전체가 아니라 **그림만** 흔든다. `#card` 의 `transform` 은 드래그·비행 로직이 쓰고 있어서 건드리면 충돌하고, `.art` 는 `overflow:hidden` 이라 3 px 이동이 테두리를 벌리지 않는다.

```css
#card.hit .art svg{animation:kshake .26s ease-out .18s 1}
@keyframes kshake{
  0%{transform:translateX(0)} 22%{transform:translateX(-3px)}
  52%{transform:translateX(3px)} 78%{transform:translateX(-1.5px)}
  100%{transform:translateX(0)}}
```

### 넣지 않은 것

- 배경 실루엣 패럴랙스 — 카드가 바뀔 때마다 배경이 밀리면 카드 자체가 흔들려 보인다.
- 게이지 막대의 글로우·펄스 — `.low` 상태(≤22)의 정적인 붉은 링이 이미 경고를 하고 있다. 겹치면 둘 다 안 읽힌다.
- 카드 등장 시 그림의 페이드인 — 치수선이 이미 순서를 만든다. 두 번 하면 느려 보인다.
- 판정 시트의 바운스 — 지금의 `cubic-bezier(.2,.8,.3,1)` 이면 충분하다.

### prefers-reduced-motion

기존 `*{animation-duration:.01ms!important;transition-duration:.01ms!important}` 만으로는 **모자란다.** `animation-delay` 가 살아 있어 치수선이 0.16초 동안 안 보이다가 튀어나오고, `stroke-dashoffset:1` 초기값 때문에 `.01ms` 사이에 깜빡인다. 명시적으로 끈다.

```css
@media (prefers-reduced-motion:reduce){
  *{animation-duration:.01ms!important;animation-delay:0ms!important;
    animation-iteration-count:1!important;transition-duration:.01ms!important}
  #card .art svg .k-draw{stroke-dasharray:none!important;stroke-dashoffset:0!important;animation:none!important}
  #card .art svg .k-t-hi{opacity:1!important;animation:none!important}
  #card.hit .art svg{animation:none!important}
  .g .lb b.bump{animation:none!important}
  #scene svg{transition:none!important}
}
```

`#scene` 의 교차 페이드는 JS 가 950 ms 뒤에 옛 `<svg>` 를 지운다. 트랜지션을 껐으니 그 동안 두 장이 겹쳐 보이는데, 새 것이 `opacity:.5` 로 즉시 올라오고 옛 것은 즉시 0 이 되므로 결과는 같다. 타이머는 그대로 둔다.

---

## ⑤ 밝은 모드

지금 이 페이지는 `:root{color-scheme:dark}` 로 고정이고, 형제 페이지(`index/lab/memo/palace/game`)는 `localStorage['safety_theme']` 와 `data-theme` 로 토글한다. 이 페이지만 어두운 채로 남으면 전환할 때 화면이 튄다.

### 5-1. 하드코딩된 값의 목록

SVG 안에서 색이 나오는 곳은 정확히 두 부류다.

**(가) JS 문자열 상수 5개** — `ST '#5A6B87'` / `DM '#33425C'` / `HI '#E3B54D'` / `BD '#F07056'` / `SK '#F1C9A5'`.
**(나) 함수 인자로 흘러든 리터럴 7종** — `#1E293C`(부재 채움, 18곳) · `#243044`(판재, 21곳) · `#161F2E`(흙) · `#0F1725`·`#0D1420`(빈 곳) · `#0F1B2A`·`#2C4A63`(물) · 그 밖 `rgba(227,181,77,.18)` 류의 반투명 채움 6곳.

### 5-2. 방법 — `currentColor` 가 아니라 클래스 + CSS 변수

`currentColor` 는 색이 **하나**일 때만 쓸모가 있다. 이 그림은 한 판에 최소 다섯 색(구조선·보조선·치수·위험·사람)이 동시에 있으므로 `currentColor` 하나로는 못 나눈다.
프리젠테이션 속성에 `fill="var(--x)"` 를 직접 쓰는 방법도 있으나 브라우저별 지원이 고르지 않다. **클래스를 붙이고 CSS 규칙에서 변수를 읽는 방식**이 가장 확실하고, 마크업도 짧아진다(`fill="#1E293C" stroke="#5A6B87" stroke-width="1.2"` 32자 → `class="k-solid"` 15자).

③의 프리미티브는 이미 전부 클래스만 낸다. 남은 것은 CSS 를 붙이는 일뿐이다.

```css
/* ---------- 그림 색 토큰 ---------- */
:root{
  --k-line:#5A6B87;  --k-dim:#33425C;   --k-hi:#E3B54D;   --k-bad:#F07056;
  --k-skin:#F1C9A5;  --k-body:#8FB3E6;
  --k-solid:#1E293C; --k-plate:#243044; --k-void:#0D1420;
  --k-earth:#161F2E; --k-water:#0F1B2A; --k-cover:#33425C;
  --k-t-dim:#6E7C95;
  --art-bg:linear-gradient(180deg,#0D1420 0%,#131D2C 100%);
  --art-bg-hit:linear-gradient(180deg,#201214 0%,#1A1620 100%);
  --art-wash:rgba(240,112,86,.10);
  --on-accent:#1A1200;
}
:root[data-theme="light"]{
  --k-line:#55637C;  --k-dim:#A4B0C4;   --k-hi:#8F6512;   --k-bad:#A8391F;
  --k-skin:#C08B5C;  --k-body:#2F5FA8;
  --k-solid:#DCE3ED; --k-plate:#C6D1E0; --k-void:#A9B5C6;
  --k-earth:#E2E8F1; --k-water:#D2DFEC; --k-cover:#9AA8BE;
  --k-t-dim:#4A5568;
  --art-bg:linear-gradient(180deg,#F8FAFD 0%,#EAEFF6 100%);
  --art-bg-hit:linear-gradient(180deg,#FBF0EC 0%,#F4EDF0 100%);
  --art-wash:rgba(168,57,31,.08);
  --on-accent:#FFFFFF;
}

/* ---------- 클래스 규칙 (선 계열은 fill:none 이 기본) ---------- */
#card .art svg{font-family:var(--mono);font-size:10.5px}
#card .art svg text{font-family:var(--mono)}
.k-line,.k-dim,.k-hi,.k-hi-th,.k-bad,.k-body,.k-cover,.k-bad-d,.k-bad-d2,.k-dim-d,.k-dim-s,.k-bad-dc
  {fill:none;stroke-linejoin:round}
.k-line{stroke:var(--k-line)}
.k-dim{stroke:var(--k-dim)}
.k-dim-d{stroke:var(--k-dim);stroke-dasharray:5 4}
.k-dim-s{stroke:var(--k-dim);stroke-dasharray:2 2;stroke-width:1}
.k-hi{stroke:var(--k-hi)}
.k-hi-th{stroke:var(--k-hi);opacity:.55}
.k-bad{stroke:var(--k-bad)}
.k-bad-d{stroke:var(--k-bad);stroke-dasharray:5 4}
.k-bad-d2{stroke:var(--k-bad);stroke-dasharray:3 3;fill:none;opacity:.5}
.k-bad-dc{stroke:var(--k-bad);stroke-dasharray:4 4;fill:var(--k-bad);fill-opacity:.10;stroke-width:1.2}
.k-body{stroke:var(--k-body)}
.k-cover{stroke:var(--k-cover);stroke-linecap:butt}
.k-solid{fill:var(--k-solid);stroke:var(--k-line);stroke-width:1.2}
.k-plate{fill:var(--k-plate);stroke:var(--k-line);stroke-width:1}
.k-void{fill:var(--k-void);stroke:var(--k-line);stroke-width:1.2}
.k-earth{fill:var(--k-earth);stroke:none}
.k-water{fill:var(--k-water);stroke:none}
.k-soil{fill:url(#kx);stroke:var(--k-line);stroke-width:1.4}
.k-hatch{stroke:var(--k-dim)}
.k-detail{fill:var(--k-void);stroke:var(--k-hi);stroke-width:1.2}
.k-skin{fill:var(--k-skin);stroke:none}
.k-hi-f{fill:var(--k-hi);stroke:none}
.k-hi-f2{fill:var(--k-hi);stroke:none;opacity:.14}
.k-bad-f{fill:var(--k-bad);stroke:none}
.k-bad-band{fill:var(--k-bad);opacity:.16;stroke:none}
.k-pace-band{fill:var(--pace);opacity:.16;stroke:none}
.k-body-f{fill:var(--k-body);stroke:none;opacity:.5}
.k-hitwash{fill:var(--art-wash);stroke:none}
.k-ghost path,.k-ghost circle{stroke:var(--k-bad)!important;fill:none!important;opacity:.5}
.k-t-hi{fill:var(--k-hi);stroke:none}
.k-t-dim{fill:var(--k-t-dim);stroke:none}
.k-t-bad{fill:var(--k-bad);stroke:none}
```

밝은 값을 고른 근거 세 가지.
- `--k-hi` 는 `#E3B54D` 를 밝은 바탕에 그대로 두면 대비 1.9:1 로 사라진다. 형제 페이지의 밝은 `--warn` 과 **같은 값** `#8F6512` 를 쓴다(대비 5.4:1). 색상은 그대로 노랑 계열이라 "치수는 노란 선"이라는 규칙이 깨지지 않는다.
- 채움 3종(`solid / plate / void`)은 어두운 모드에서 **바탕보다 밝고** 밝은 모드에서 **바탕보다 어둡다**. 명도 서열(`solid > plate > void`)은 뒤집는다 — `void`(구멍·굴착 내부)는 어느 쪽에서든 "가장 깊은 것"이어야 하므로 어두운 모드에서 가장 어둡고 밝은 모드에서 가장 진하다.
- `--k-dim`(보조선)은 밝은 모드에서 `#A4B0C4` 로 **연하게**, `--k-t-dim`(보조 글자)은 `#4A5568` 로 **진하게** 나눈다. 선은 배경으로 물러나야 하고 글자는 읽혀야 하므로 같은 토큰을 쓸 수 없다.

### 5-3. 페이지 전체 토큰

```css
:root{color-scheme:dark}
:root[data-theme="light"]{color-scheme:light;
  --bg:#F4F6FA; --panel:#FFFFFF; --panel2:#EAEEF5; --card:#FFFFFF;
  --line:#C6D0DE; --line-soft:#E0E6EF;
  --text:#14202E; --muted:#4A5568; --dim:#66738A;
  --safe:#1F6B45; --pace:#2F5FA8; --coin:#8F6512; --gov:#6D4A9C;
  --bad:#A8391F; --ok:#1F6B45; --warn:#8F6512;
}
:root[data-theme="light"] body{
  background-image:radial-gradient(120% 70% at 50% -10%, #FFFFFF 0%, #F4F6FA 62%)}
:root[data-theme="light"] #scene svg.on{opacity:.26}   /* 어두운 모드 .5 → 밝은 바탕에선 과하다 */
:root[data-theme="light"] #card{box-shadow:0 14px 32px rgba(20,32,46,.12)}
:root[data-theme="light"] #sheet{box-shadow:0 -12px 34px rgba(20,32,46,.14)}
:root[data-theme="light"] #over{background:rgba(244,246,250,.94)}
:root[data-theme="light"] .ch:hover{background:#DFE6F1}
#card .art{background:var(--art-bg)}
#card.hit .art{background:var(--art-bg-hit)}
#sheet .go,#over .again{color:var(--on-accent)}       /* #1A1200 하드코딩 제거 */
```

`#over .again` 과 `#sheet .go` 는 배경이 `var(--warn)` 인데 밝은 모드에서 `--warn` 이 어두운 갈색이 되므로 글자색이 `#1A1200` 인 채로 두면 안 읽힌다.

배경 실루엣 `BGS` 의 색 7종(`#7FA6E0`, `#F0A35B`, `#E3B54D`, `#6BC3C9`, `#B58FE0`, `#8C99B0`, `#F07056`)은 채도가 있어 밝은 바탕에서도 형태가 남는다. 불투명도만 `.5 → .26` 으로 내리면 된다(위 규칙).

### 5-4. 부트스트랩 · 토글

형제 페이지와 **같은 키·같은 스크립트**를 쓴다. `<head>` 안, `<style>` 앞에 둔다.

```html
<script>(function(){try{var t=localStorage.getItem('safety_theme');
  if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
```

`#top` 의 `처음부터` 버튼 왼쪽에 토글을 넣고, 형제 페이지의 스크립트를 그대로 붙인다.

```html
<button class="b bTheme" type="button" aria-pressed="true">밝은 모드</button>
```

`<meta name="theme-color">` 도 두 벌로 나눈다.

```html
<meta name="theme-color" content="#0A1018" media="(prefers-color-scheme:dark)">
<meta name="theme-color" content="#F4F6FA" media="(prefers-color-scheme:light)">
```

---

## ⑥ 카드 앞면 레이아웃

### 6-1. 지금 넘치고 있다

세로 360 × 640(안전영역 제외) 기준 실측.

| | 지금 | |
|---|---|---|
| `#top` 실제 높이 | 40.3 px | `#app{padding-top:56px}` — **15.7 px 를 헛되게 예약** |
| `#app` 안쪽 여유 | 356.8 px | 640 − 46 − 상하 32 − gap 56 − hud 29.8 − meta 17.8 − 선택 83.8(2줄) − 힌트 17.8 |
| `#card` 실제 높이 | **370.5 px** | 그림 124 + 과목 16.3 + 화자 47.5 + 본문 93 + 조문 68.8 + 여백 19 + 테두리 2 |

**13.7 px 가 넘친다.** `body{overflow:hidden}` 이라 조문 줄 아래가 잘리고, 선택 버튼 글이 두 줄이 되는 카드(`'미조치 위험까지 그대로 올린다'`, `'2개 이음으로 다시 세운다'`)에서 매번 발생한다.

원인은 셋이다. ① `#top` 예약 과다 ② `.say{min-height:6em}` 이 `em` 기준이라 글꼴 크기가 오를수록 같이 커진다 ③ `.who` 의 `margin:6px 0 12px` + 줄높이 1.55 = 47.5 px 를 한 줄짜리 이름에 쓴다.

### 6-2. 다시 잡은 실측값 (360 × 640 세로 기준)

| 요소 | 값 | 계 |
|---|---|---|
| `#top` | padding 8/8, crumb 15 px · lh 23 | 40 px |
| `#app` padding-top | 46 px | |
| `#app` padding | `10px 14px calc(12px + env(safe-area-inset-bottom))`, gap 10 | 상 10 · 하 12 · gap 40 |
| `#hud` | lb 11 px · lh 15 / gap 4 / track 6 | 25 px |
| `#meta` | 11 px · lh 15 | 15 px |
| `#choices` | padding 11/12, gap 3, kb 10·lh 13, tx 13·lh 18 (2줄 36) | 76 px |
| `#swipeHint` | 10.5 px · lh 14 | 14 px |
| **`#board` 여유** | 640 − 46 − 10 − 12 − 40 − 25 − 15 − 76 − 14 | **402 px** |

카드 안쪽.

| 요소 | 값 | 높이 |
|---|---|---|
| `.art` | height 104, margin `-16 -16 12` | 116 px |
| `.head` (과목 + 그림 칩) | 10 px · lh 14 | 14 px |
| `.who` | Gothic A1 800 · 17 px · lh 24 · margin `5 0 10` | 39 px |
| `.say` | 15 px · lh 24 · min-height 72 (3줄) · 최대 4줄 | 72~96 px |
| `.topic` | margin-top 12 · border 1 · padding-top 10 · 11.5 px · lh 17 · 2줄 | 57 px |
| `#card` padding | `16px 16px 16px` (상단은 `.art` 의 음수 마진이 상쇄) | 16 px |
| 테두리 | 1 px × 2 | 2 px |
| **합계** | | **316 ~ 340 px** |

여유 402 − 340 = **62 px**. 선택 버튼이 두 줄이 되고 본문이 네 줄이 되어도 남는다.

### 6-3. 타이포 스케일

두 단만 둔다. 세 단 이상은 어느 폭에서 무엇이 적용되는지 아무도 못 따라간다.

| 요소 | ≤ 400 px | ≥ 401 px | 색·자족 |
|---|---|---|---|
| `.subj` (과목) | 10 / 14, ls .10em | 10.5 / 15 | mono, `--dim`, 대문자 |
| `.artTag` (그림 이름) | 10 / 14 | 10.5 / 15 | mono, `--muted` |
| `.who` (화자) | **17 / 24**, 800 | **19 / 26** | display, `--text`, ls −.02em |
| `.say` (본문) | **15 / 24** | **16.5 / 27** | sans, `--text` |
| `.topic` (조문) | 11.5 / 17 | 12.5 / 19 | sans, `--muted`, 조문번호만 `--text` 600 |
| `.ch .kb` | 10 / 13 | 10 / 13 | mono, `--dim` |
| `.ch .tx` | 13 / 18 | 13.5 / 19 | sans 500 |
| `.g .lb` | 11 / 15 | 11.5 / 16 | sans, `--muted` |

본문과 화자의 비는 15 : 17 = 1 : 1.13 이다. 지금(15.5 : 19 = 1 : 1.23)보다 좁혔다. 화자 이름은 한 줄짜리 라벨이지 제목이 아니므로 본문보다 크게 벌릴 이유가 없다.

### 6-4. 세로 리듬

경쟁하던 다섯 덩어리에 **네 단계의 간격**만 준다.

```
그림  ──────────────── 12 px ──── (그림과 글의 경계, 유일한 큰 틈)
과목 · 그림 이름  ───── 5 px ───── (같은 층위)
화자  ──────────────── 10 px ──── (말하는 사람 → 말)
본문
       ──────────────── 12 px + 1 px 선 + 10 px ──── (내용 → 근거, 유일한 구분선)
조문
```

구분선은 `.topic` 위 하나뿐이다. `.art` 아래 `border-bottom` 은 남기되 `--line-soft` 로 유지하고, 그 밖에는 선을 넣지 않는다. 선이 둘 이상이면 그림·본문·조문이 서로 다른 카드처럼 보인다.

### 6-5. 마크업·CSS 패치

`.cap` 을 지우고 과목 줄로 옮긴다(④의 치수 자리를 비워 주는 일이기도 하다).

```html
<div class="art" id="cArt" aria-hidden="true"></div>
<div class="head"><span class="subj" id="cSubj"></span><span class="artTag" id="cTag"></span></div>
<div class="who"><i></i><span id="cWho"></span></div>
<div class="say" id="cSay"></div>
<div class="topic" id="cTopic"></div>
```

```js
/* next() 안, $('cSubj') 다음 줄에 */
$('cTag').textContent = pick.f ? pick.f.replace(/<[^>]+>/g, '').split(' · ')[0] : '';
```

```css
#app{padding-top:46px;padding-left:14px;padding-right:14px;padding-bottom:calc(12px + env(safe-area-inset-bottom));gap:10px}
#hud{gap:8px} .g{gap:4px} .g .lb{font-size:11px;line-height:15px} .g .track{height:6px}
#meta{font-size:11px;line-height:15px}
#swipeHint{font-size:10.5px;line-height:14px}
.ch{padding:11px 12px;gap:3px} .ch .kb{font-size:10px;line-height:13px} .ch .tx{font-size:13px;line-height:18px}

#card{padding:16px}
#card .art{height:104px;margin:-16px -16px 12px}
#card .head{display:flex;align-items:baseline;gap:8px;min-width:0}
#card .subj{font-family:var(--mono);font-size:10px;line-height:14px;letter-spacing:.10em;
  color:var(--dim);text-transform:uppercase;flex:none}
#card .artTag{font-family:var(--mono);font-size:10px;line-height:14px;color:var(--muted);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#card .artTag:not(:empty)::before{content:"· "}
#card .who{font-size:17px;line-height:24px;margin:5px 0 10px;gap:8px}
#card .say{font-size:15px;line-height:24px;min-height:72px}
#card .topic{margin-top:12px;padding-top:10px;font-size:11.5px;line-height:17px}

@media (min-width:401px){
  #card .art{height:124px}
  #card .who{font-size:19px;line-height:26px}
  #card .say{font-size:16.5px;line-height:27px;min-height:81px}
  #card .topic{font-size:12.5px;line-height:19px}
  #card .subj,#card .artTag{font-size:10.5px;line-height:15px}
  .ch .tx{font-size:13.5px;line-height:19px}
}
```

기존 `@media (max-width:420px)` 블록은 위 규칙과 어긋나므로 통째로 지운다(`#card .say{min-height:6em}` 이 넘침의 직접 원인이다).

### 6-6. 남는 문제 하나

`#card.rep`(닷새마다 오는 현상 보고)는 `.say` 안에 표 세 줄 + 위험 목록 최대 5줄이 들어가 340 px 을 넘긴다. `.rp .risk ul` 에 `max-height:96px;overflow-y:auto` 를 걸어 카드 높이를 고정한다. 잘리는 것은 4건째부터인데 이미 `r.risks.slice(0,4)` 로 잘라서 넘기고 있으므로 실제로는 스크롤이 거의 생기지 않는다.

```css
#card.rep .say{min-height:0}
#card.rep .rp .risk ul{max-height:96px;overflow-y:auto}
```
