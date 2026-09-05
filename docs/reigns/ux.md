# 「안전관리자의 하루」 UX·학습설계 규격

대상: `safety3d-lab/reigns.html` (1,083행 단일 HTML, 무의존성, 오프라인 동작)
전제: 이 구조를 깨지 않는다. 아래 제안은 전부 같은 파일 안에서 끝난다. 예외는 ⑦의 마지막 항목 하나이고 비용을 따로 적었다.

읽은 근거: `reigns.html` 전체, `index.html`, `memo.html`(213~265행), `lab.html`(405~420, 1495, 1862행), `palace.html`(113~205행).

---

## ① 진단표

| # | 문제 | 위치 (reigns.html) | 왜 문제인가 (수험생 관점) | 심각도 |
|---|---|---|---|---|
| D1 | **저장이 전혀 없다.** 파일 어디에도 `localStorage` 호출이 없다(전 파일 grep 0건). 형제 5개 페이지는 전부 쓴다. 탭을 닫거나 새로고침하면 60일 중 47일차도 사라진다. | 834~843 `reset()` — 상태 `st`가 통째로 메모리 변수 | 60일 = 앉은 자리에서 40~60번 판단. 지하철에서 20일차까지 갔다가 전화 한 통 오면 처음부터. 그래서 아무도 준공까지 못 간다 → **놓친 규정 목록(종료 화면)이 이 게임의 학습 산출물인데 그 화면에 도달하지 못한다.** | 치명 |
| D2 | **틀린 규정이 안 돌아온다.** 오답 씨앗(`st.seeds`)은 `FALLOUT` 배열에 짝(`req`)이 있는 **10개 주제만** 사고 카드로 회수된다. DECK은 40장·39주제. 나머지 29주제는 틀려도 그 회차에 두 번 다시 안 나온다. 게다가 회수 확률이 `Math.random() < 0.45`. | 918~923 `next()`의 ripe/FALLOUT 분기, 750~811 `FALLOUT`(10장), 507~747 `DECK`(40장) | 「1:1.8」을 틀린 사람이 그 회차 내내 1:1.8을 한 번도 다시 못 본다. 학습 도구로서 가장 큰 구멍. "한 번 보고 지나가면 끝"인 이유가 바로 이 코드다. | 치명 |
| D3 | **`st.recent`가 죽은 코드.** 835행에서 `recent:[]`로 초기화되고 전 파일 어디서도 읽거나 쓰지 않는다. 최근 카드 반복 방지 장치가 설계만 남고 빠졌다. | 835 (초기화), 이후 참조 0건 | 후반부에 `used` 풀이 소진되면 940행의 `DECK.forEach(function(c){ c.used = false; })`로 통째 리셋 → 방금 본 카드가 바로 다시 나올 수 있다. | 중 |
| D4 | **판정 시트와 종료 화면이 화면 밖으로 밀려 있을 뿐, DOM에서 살아 있다.** `#sheet`는 `transform:translateY(102%)`, `#over`는 `opacity:0;pointer-events:none`. 둘 다 `display:none`이 아니다. → 카드를 고르기 전에도 Tab을 누르면 포커스가 보이지 않는 「다음 날」·「다시 부임한다」 버튼으로 빠진다. | 90~92 (`#sheet`), 110~112 (`#over`) | 키보드·스크린리더 사용자가 포커스를 잃고 자기 위치를 모른다. 접근성 항목 중 유일한 "동작 불능"급. | 상 |
| D5 | **스크린리더에 아무것도 전달되지 않는다.** 파일 내 `aria-live` 0건, `tabindex` 0건, `role`은 카드 그림 SVG의 `role="img"` 하나뿐(그마저 부모 `#cArt`가 `aria-hidden="true"`). 카드가 바뀌어도, 판정이 떠도, 게이지가 −14 되어도 낭독되는 것이 없다. | 190·199 (`aria-hidden`), 845~875 `renderHud`/`flashDelta`, 970~1003 `choose` | 게임 진행 자체가 불가능하다. | 상 |
| D6 | **세로 화면에서 카드가 잘린다.** `body{overflow:hidden}` + `#app{height:100%;padding-top:56px}` + `#card{position:absolute}` + `#card .say{min-height:6em}`(모바일). 375×667에서 상단바 45 + 패딩 56 + 게이지 41 + 여백 14 + 날짜 18 + 여백 14 + 선택지 62 + 여백 14 + 힌트 18 + 하단 18 ≈ 300px가 고정으로 빠지고 카드에 367px가 남는데, 카드 최소 높이는 그림 112 + 본문 154 + 과목 14 + 화자 37 + 조문 42 + 패딩 36 ≈ **395px**. 넘치는 만큼 `overflow:hidden`에 잘려 나간다. | 23~27, 32, 56~60, 141~143, 170~175, 178 | 조문 줄(`#cTopic`)이 맨 먼저 잘린다. 그게 이 게임의 학습 정보다. SE·미니 계열, 그리고 iOS Safari에서 툴바가 내려온 **모든** 기기에서 발생(`height:100%`는 large viewport로 해석된다). | 상 |
| D7 | **카드 안에서 세로 스크롤이 불가능하다.** `#card{touch-action:none}`. 5일마다 오는 현상 보고 카드는 `reportHtml()`이 표 2줄 + 미조치 위험 최대 5줄을 그려 가장 길다. 그런데 손가락으로 밀면 좌우 드래그로만 해석되어 아래를 못 본다. | 60 (`touch-action:none`), 890~906 `reportHtml`, 152~168 (`.rp` CSS, 높이 제한 없음) | 「미조치 위험 N건」이 이 게임의 유일한 누적 피드백인데 휴대폰에서 안 보인다. | 상 |
| D8 | **판정 시트에 높이 상한이 없다.** `#sheet`에 `max-height`/`overflow`가 없다(파일 내 `max-height`는 126행 `#over .viol ul` 하나뿐). 기준 문자열이 긴 카드(예: 60행 강관비계 `f`)에서 「다음 날」 버튼이 뷰포트 아래로 밀려 나간다. 가로 모드에서는 거의 항상. | 88~106 (`#sheet` 블록), 126 | 진행 불가. 되돌릴 방법도 없다(Esc 핸들러 없음). | 상 |
| D9 | **위험 상태를 색으로만 알린다.** 게이지 22 이하에서 `.g.low`가 붙어 채움색이 `--bad`, 라벨색이 `--bad`, 트랙에 붉은 링. 문자·기호·무늬 변화 없음. 게이지에 `role="progressbar"`도 없다. | 41~43, 845~861 | 적록색약(남성 약 8%)에게 "예산이 곧 바닥"이 전달되지 않는다. | 중 |
| D10 | **작은 글씨의 명도비 미달.** `--dim:#6E7C95`가 `--card:#141E2E` 위에서 약 4.0:1. 이 값을 쓰는 곳이 `.subj`(10.5px), `.art .cap`(10px), `.g .lb b`(12px), `#sheet .std .k`(10.5px), `#meta`(11.5px). **같은 사이트 `index.html`은 이미 `--dim:#8290AC`(약 5.6:1)를 쓴다** — reigns만 옛 값이 남았다. | 16 (reigns 팔레트) vs `index.html` 6행 팔레트 | 게이지 숫자와 과목 라벨이 안 읽힌다. 한 글자 고치면 끝나는 문제. | 중 |
| D11 | **사이트 공통 테마를 무시한다.** 형제 5개 페이지는 전부 `<head>`에서 `safety_theme`를 읽어 `data-theme`를 심고 `.bTheme` 버튼을 둔다(`index.html` 8행·126행). reigns는 `color-scheme:dark` 고정이고 관련 코드 0건. `⋯` 더보기 메뉴도 없어 형제 페이지 이동 동선이 상단바 링크 1개(`3D 실습장`)뿐이다. | 12~22 (`:root`), 180~196 (`#top`) | 밝은 모드로 맞춰 둔 사람이 이 페이지만 눈이 부시다. 사이트 안에서 이 페이지만 이질적. | 중 |
| D12 | **온보딩이 한 줄 텍스트뿐.** `#swipeHint`의 "카드를 좌우로 밀거나 방향키로 결정합니다" 한 문장. 게이지 4개가 뭘 뜻하는지, 0이 되면 어떻게 되는지, 60일이 목표인지 아무 데도 없다. `palace.html`은 `#intro` 다이얼로그로 하는데(175~181행) reigns에는 없다. | 210 (`#swipeHint`), 186~211 | 첫 카드에서 게이지가 −12 되면 왜 깎였는지 모른 채 계속 밀게 된다. 학습이 아니라 도박이 된다. | 상 |
| D13 | **오답 기록이 회차와 함께 증발한다.** `st.viol`은 종료 화면에서 조문 기준으로 중복 제거되어 한 번 렌더된 뒤, `oAgain` → `reset()`이 `st`를 통째로 새로 만들며 사라진다. 회차 사이에 누적되는 것이 하나도 없다. | 1015~1040 `finish()`, 1041 (`oAgain` → `reset`), 834~843 | "내가 자꾸 틀리는 규정"을 알 방법이 없다. 시험 대비의 핵심 정보를 매 회차 버린다. | 치명 |
| D14 | **형제 페이지로 건너뛸 데가 없다.** DECK 카드 키 39개 중 **21개가 `lab.html`의 topic id와 문자열까지 정확히 일치**한다(`net fall rail ladder ramp plank scaffold stairs trench powerline roller grinder press approach chemdist shore lux wirerope gasweld elcb vdt`). `memo.html` 묶음 데이터에는 `topic3d` 필드가 이미 붙어 있다. 배선만 없다. | `lab.html` 410~416·1862, `memo.html` BANK의 `topic3d` 필드 | 시트에서 "1:1.8이 뭐지"까지 온 사람이 그 자리에서 3D 실습장·암기 노트로 못 간다. 사이트 전체를 하나의 학습 루프로 묶을 마지막 한 칸이 비어 있다. | 상 |

---

## ② 학습 루프 설계와 저장 스키마

### 2-1. 키 이름과 스키마

형제 페이지가 이미 쓰는 키: `safety_theme`, `memo_srs_v1`, `memo_done_v1`, `memo_exam_v1`, `memo_palace_last`, `game_best_v1`, `game_mode`, `game_sound`, `palace_lite`, `safety3d_tut_v1`.
**아래 4개는 전부 미사용 접두사 `reigns_`를 쓴다. 충돌 없음.**

```js
/* reigns_run_v1 — 진행 중인 회차 하나. finish() 하면 지운다. */
{
  v: 1,
  ts: 1757030000000,          // 마지막 저장 시각. 이어하기 안내에 "3일 전"으로 표시
  g: [62, 58, 60, 60],        // 게이지 4개
  day: 23,
  cur: 'trench',              // 지금 화면에 떠 있는 카드 키. null이면 카드 뽑기부터
  used: { net:1, fall:1 },    // DECK 소진 상태 (기존 c.used 플래그를 상태로 옮긴 것)
  seeds: [ {tag:'shore', day:19} ],
  recheck: [ {k:'rail', due:26, n:1} ],   // ★ 신설: 재점검 큐 (2-2)
  viol: [ {k:'rail', law:'…제13조', f:'안전난간 · …', w:'개구부 담당', day:12} ],
  okCount: 14, pOk: 2, pNo: 1, snap: [70,52,55,63],
  reports: 4, lastReport: 20,
  onboard: 1                  // 0 = 아직 브리핑 카드를 안 봄
}

/* reigns_srs_v1 — 주제(카드 키)별 간격 반복 기록.
   memo.html:227 grade() 의 {n, ok, iv, due, last} 모양을 그대로 따른다.
   식별자 공간이 다르므로(memo 는 '6-17', reigns 는 'net') memo_srs_v1 에 절대 쓰지 않는다. */
{
  "net":    { n:3, ok:2, iv:2, due:1757200000000, last:1757030000000, miss:1 },
  "trench": { n:1, ok:0, iv:0, due:1757030600000, last:1757030000000, miss:1 },
  "__days": { "2026-09-05": 41 }       // memo.html 과 같은 "하루 판단 수" 카운터
}

/* reigns_miss_v1 — 「내가 놓친 규정」 누적 노트. 회차를 넘어 살아남는다. */
{
  "rail": {
    law: '산업안전보건기준에 관한 규칙 제13조',
    f:   '안전난간 · 상부 난간대 90 cm 이상 · 120 cm 초과 시 중간대 2단 · 발끝막이판 10 cm 이상',
    w:   '개구부 담당',
    s:   '건설안전기술',
    n:   3,            // 누적 오답 수
    fix: 1,            // 그 뒤 재점검에서 바로잡은 수
    last: 1757030000000,
    runs: [12, 47]     // 어느 회차 몇 일차에 틀렸는지
  }
}

/* reigns_stats_v1 — 회차 기록. 이어하기 화면과 종료 화면에서 쓴다. */
{ runs: 5, bestDay: 47, cleared: 1, lastEnd: 'safety', totalOk: 132, totalNo: 61 }
```

읽기/쓰기 헬퍼는 memo.html 관례를 그대로 옮긴다(전부 `try/catch`, 실패 시 기본값 반환).

```js
function LS(k, d){ try{ var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; }catch(e){ return d; } }
function SV(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
```

저장 시점: `choose()` 끝, `sGo` 클릭 후 `st.day++` 뒤, `finish()` 직전. 즉 **한 번의 판단마다 두 번**. 60일치 상태가 2 KB 미만이라 부담 없다.

- **난이도 중 / 우선순위 P0.** `reset()`을 `newRun()`과 `resume()`으로 쪼개고, `next()`(908~968행)의 필터가 `c.used` 대신 `st.used[c.k]`를 보게 바꾼다. 실제로 손대는 곳은 3군데다.

### 2-2. 틀린 규정이 다시 돌아오는 구조 (핵심)

현재 회수 경로는 `seeds → FALLOUT`(사고 카드) 하나뿐이고 10주제·45%다(D2). 이걸 **2층**으로 만든다.

**1층 — 재점검 큐 `st.recheck`.** 주제 불문 전부 커버.

```js
// choose() 안
if(!ch.ok && c.k){
  st.recheck.push({ k:c.k, due: st.day + 3 + Math.floor(Math.random()*3), n:1 });
  gradeK(c.k, false);      // reigns_srs_v1 갱신
  noteMiss(c);             // reigns_miss_v1 갱신
} else if(ch.ok && c.k){
  gradeK(c.k, true);
}
```

```js
// next() 안. 보고 카드 분기 다음, FALLOUT 분기 앞
var due = st.recheck.filter(function(r){ return st.day >= r.due; });
if(!pick && due.length){
  var r = due[0];
  pick = DECK.filter(function(c){ return c.k === r.k; })[0];
  if(pick){
    pick.recheck = r;
    st.recheck = st.recheck.filter(function(x){ return x !== r; });
  }
}
```

재점검으로 온 카드는 같은 카드지만 **머리에 한 줄이 붙는다.**

```html
<div class="rechk" id="cRechk" hidden>
  지난 <b id="cRechkDay">12</b>일차에 넘긴 자리입니다. 그때 기준은 무엇이었습니까?
</div>
```
```css
#card .rechk{margin:-6px 18px 10px;padding:7px 10px;border-radius:7px;font-size:12.5px;
  background:rgba(227,181,77,.10);border:1px solid rgba(227,181,77,.45);color:var(--warn)}
#card .rechk b{font-family:var(--mono);font-weight:500}
```
`#cSubj`도 `'재점검 · ' + pick.s`로 바꾼다.

재점검에서 **또 틀리면** `r.n++`, `due = st.day + 2`로 간격을 **좁힌다**. 맞히면 큐에서 빠지고 `srs.iv`가 늘어 다음 회차에 늦게 돌아온다.

**2층 — 카드 뽑기 가중치.** 지금은 균등 무작위(944~947행). 가중 추첨으로 바꾼다.

```js
function weight(c){
  var r = srs[c.k] || {n:0, ok:0, iv:0, due:0}, now = Date.now(), w = 1;
  if(st.seeds.some(function(s){ return s.tag === c.k; })) w += 3.0;   // 현장에 남은 위험
  if(r.n && !r.iv)                                        w += 2.2;   // 최근에 틀림
  if(r.due && r.due <= now)                               w += 1.4;   // 복습 시점 도래
  if(r.ok >= 2 && r.iv >= 4)                              w -= 0.7;   // 이미 굳음
  if(st.recentK.indexOf(c.k) >= 0)                        w  = 0.05;  // 최근 6장 회피
  return Math.max(0.05, w);
}
function pickWeighted(pool){
  var tot = 0, i, ws = pool.map(function(c){ var w = weight(c); tot += w; return w; });
  var t = Math.random() * tot;
  for(i = 0; i < pool.length; i++){ t -= ws[i]; if(t <= 0) return pool[i]; }
  return pool[pool.length - 1];
}
```
`st.recentK`는 835행에 이미 있으나 죽어 있는 `recent:[]`(D3)를 되살린 것이다. `choose()`에서 `st.recentK.unshift(c.k); st.recentK.length = Math.min(st.recentK.length, 6);`로 채운다.

- **난이도 중 / 우선순위 P1.** `next()` 안 40행이면 끝난다. 무의존성·오프라인 유지.

### 2-3. 「내가 놓친 규정」 누적 노트

상단바 `⋯` 메뉴와 종료 화면 양쪽에서 열리는 서랍. `palace.html`의 `#toc` 서랍과 같은 자리·같은 동작(`aria-expanded`/`aria-controls`).

```html
<aside id="note" hidden aria-labelledby="noteTitle">
  <div class="nhead">
    <h2 id="noteTitle">놓친 규정 <span class="pg" id="noteN">0</span></h2>
    <button class="b sm" id="bNoteClose" type="button" aria-label="노트 닫기">✕</button>
  </div>
  <ul id="noteBody"></ul>
  <p class="nfoot"><button class="b sm" id="bNoteClear" type="button">기록 비우기</button></p>
</aside>
```
```html
<!-- noteBody 항목 하나 -->
<li data-k="rail">
  <div class="nl">산업안전보건기준에 관한 규칙 제13조</div>
  <div class="nf">안전난간 · 상부 난간대 <em>90 cm</em> 이상 · 120 cm 초과 시 중간대 2단 · 발끝막이판 <em>10 cm</em> 이상</div>
  <div class="nm"><b>3</b>번 넘김 · <b>1</b>번 바로잡음</div>
  <div class="nb">
    <a class="b sm" href="lab.html?v=09041852#topic=rail" target="_blank" rel="noopener">3D 실습장에서 재보기 →</a>
    <a class="b sm" href="memo.html?v=09041852#g=6-02" target="_blank" rel="noopener">암기 은행 →</a>
    <button class="b sm" type="button" data-again="rail">내일 다시 만나기</button>
  </div>
</li>
```
```css
#note{position:fixed;right:0;top:var(--topH);bottom:0;z-index:35;width:min(400px,92vw);
  background:var(--panel);border-left:1px solid var(--line);overflow-y:auto;
  padding:14px 16px calc(16px + env(safe-area-inset-bottom,0px));
  transform:translateX(100%);transition:transform .28s cubic-bezier(.2,.8,.3,1)}
#note.on{transform:none}
#note .nhead{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px}
#note h2{font-family:var(--display);font-weight:800;font-size:17px;margin:0}
#note .pg{font-family:var(--mono);font-size:13px;color:var(--bad)}
#note ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:12px}
#note li{border-left:2px solid var(--bad);padding:2px 0 2px 12px}
#note .nl{font-family:var(--mono);font-size:11.5px;color:var(--muted);line-height:1.5}
#note .nf{font-size:13.5px;line-height:1.55;margin-top:4px}
#note .nf em{font-style:normal;color:var(--warn);font-family:var(--mono);font-weight:500}
#note .nm{font-size:12px;color:var(--dim);margin-top:5px}
#note .nm b{color:var(--text);font-family:var(--mono);font-weight:500}
#note .nb{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
```
`내일 다시 만나기` 버튼은 `st.recheck.push({k:k, due:st.day + 1, n:1})` 한 줄이다. 노트가 게임에 직접 개입하는 유일한 지점이고, 이게 노트를 "죽은 목록"이 아니라 학습 도구로 만든다.

### 2-4. 형제 페이지 딥링크 배선표

`lab.html`은 `#topic=xxx`를 이미 파싱한다(`lab.html:1862`, `location.hash.match(/topic=([a-z]+)/)`). `memo.html`은 `#g=<id>`를 이미 파싱한다(`memo.html:254`). reigns에 상수 두 개만 넣으면 배선이 끝난다.

```js
// lab.html 의 T 테이블에 실재하는 21개. 나머지 키는 3D 버튼을 숨긴다.
var LAB3D = {net:1,fall:1,rail:1,ladder:1,ramp:1,plank:1,scaffold:1,stairs:1,trench:1,
  powerline:1,roller:1,grinder:1,press:1,approach:1,chemdist:1,shore:1,lux:1,
  wirerope:1,gasweld:1,elcb:1,vdt:1};

// memo.html BANK 의 topic3d 필드를 역인덱싱해 손으로 고른 대표 묶음 id
var MEMO = {
  net:'6-17', fall:'6-10', rail:'6-02', ladder:'6-06', ramp:'6-13', plank:'6-03',
  scaffold:'6-03', stairs:'6-13', trench:'6-04', shore:'6-14', horse:'6-03',
  mobscaf:'6-03', frame:'6-03', pile:'6-08', caisson:'6-18', gangway:'6-12',
  carry:'6-12', weather:'6-11', lux:'6-31', vdt:'2-08', noise:'2-20',
  roller:'3-02', grinder:'3-06', press:'3-02', sawblade:'3-17', forklift:'3-13',
  robot:'3-15', boiler:'3-04', rotor:'3-10', wirerope:'3-07', elcb:'4-06',
  welder:'4-01', approach:'4-13', powerline:'4-09', panelspace:'4-17',
  exgap:'4-05', confined:'5-27', chemdist:'5-20', gasweld:'3-21', staticflow:'4-03'
};
var VQ = '?v=09041852';   // 사이트 공통 캐시 무효화 쿼리
function labURL(k){  return LAB3D[k] ? 'lab.html'  + VQ + '#topic=' + k        : ''; }
function memoURL(k){ return MEMO[k]  ? 'memo.html' + VQ + '#g='     + MEMO[k]  : ''; }
```

이 두 링크는 **노트뿐 아니라 판정 시트 안에도** 놓는다. 틀린 직후가 가장 궁금한 순간이다.

```html
<!-- #sheet 안, .law 아래 -->
<div class="jump" id="sJump">
  <a class="b sm" id="sLab"  target="_blank" rel="noopener">3D로 확인 →</a>
  <a class="b sm" id="sMemo" target="_blank" rel="noopener">암기 은행 →</a>
</div>
```
```css
#sheet .jump{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
#sheet .jump .b{font:inherit;font-size:12.5px;padding:7px 11px;border-radius:7px;
  border:1px solid var(--line);background:var(--panel2);color:var(--text);text-decoration:none}
#sheet .jump .b:hover{border-color:var(--warn)}
#sheet .jump .b[hidden]{display:none}
```
`target="_blank"`인 이유는 회차 진행을 끊지 않기 위해서다. 2-1의 저장이 들어가면 같은 탭 이동도 안전해지지만, 새 탭이 흐름을 덜 깬다.

- **난이도 하 / 우선순위 P1.** 상수 두 개 + `choose()` 안 3줄.

---

## ③ 온보딩

### 원칙

Reigns는 별도 튜토리얼 화면이 없다. **첫 카드가 튜토리얼이다** — 조언자가 "폐하, 좌우로 미십시오"라고 말하고, 기울일 때 뜨는 라벨이 결과를 미리 보여 준다. reigns.html은 그 라벨 장치(`.pick.l`/`.pick.r`, 71~76행)를 **이미 갖고 있는데** 가르치는 데 쓰지 않고 있다.

그래서 `#intro` 다이얼로그를 **처음 온 사람에게는 띄우지 않는다.** 다이얼로그는 이어하기 전용으로 돌린다.

### 3-1. 0일차 브리핑 카드 (`reigns_run_v1.onboard === 0`일 때만)

DECK 앞에 붙는 특수 카드 하나. 게이지 변동은 `[0,0,0,0]`이라 어느 쪽으로 밀어도 손해가 없다.

```js
var BRIEF = {
  k:'brief', s:'부임', w:'현장소장', law:'', brief:1, art:'report',
  t:'오늘부터 이 현장 안전관리자입니다. 준공까지 60일. 하루에 한 건씩 결정이 올라옵니다.',
  f:'',
  a:{l:'왼쪽으로 밀어 봅니다',   d:[0,0,0,0], ok:1,
     o:'그렇게 결정합니다. 위 네 칸이 그 결과로 움직입니다. 하나라도 0이 되면 그날로 끝입니다.'},
  b:{l:'오른쪽으로 밀어 봅니다', d:[0,0,0,0], ok:1,
     o:'그렇게 결정합니다. 위 네 칸이 그 결과로 움직입니다. 하나라도 0이 되면 그날로 끝입니다.'}
};
```

브리핑 카드에서만 세 가지가 더 붙는다.

**(a) 게이지를 가리키는 콜아웃.** 카드 그림 자리(`#cArt`)에 현장 그림 대신 게이지 설명 SVG를 그린다. 320×132 판 위에 막대 네 개와 위쪽 화살표, 각각에 「다치면 준다 / 늦으면 준다 / 쓰면 준다 / 어기면 준다」 한 줄씩. 기존 헬퍼 `TX()`·`L()`·`R()`(261~272행)로 그대로 그릴 수 있다. **새 그림 라이브러리가 필요 없다.**

**(b) 손가락 고스트.** 첫 3초 동안 카드 위를 좌우로 한 번 왕복하는 반투명 원.

```css
#card .ghost{position:absolute;left:50%;top:54%;width:34px;height:34px;margin:-17px;
  border-radius:50%;border:2px solid var(--warn);background:rgba(227,181,77,.14);
  pointer-events:none;animation:gh 2.4s ease-in-out 2}
@keyframes gh{
  0%,100%{transform:translateX(0);opacity:0}
  20%{opacity:1}
  50%{transform:translateX(-64px);opacity:1}
  80%{transform:translateX(48px);opacity:.6}
}
@media (prefers-reduced-motion:reduce){
  #card .ghost{animation:none;opacity:1;width:auto;height:auto;margin:0;left:0;right:0;
    border:0;background:none;text-align:center;color:var(--warn);font-size:13px}
  #card .ghost::after{content:"← 밀거나 방향키 →"}
}
```
움직임을 줄인 환경에서는 애니메이션 대신 **글자**로 같은 말을 한다. 정보를 잃지 않는다.

**(c) 첫 판정 시트에만 붙는 한 줄.**

```html
<p class="firsthint" id="sFirst" hidden>
  아래 <b>규정 기준</b> 칸의 노란 숫자가 시험에 나오는 부분입니다. 이 칸만 눈에 담고 넘기세요.
</p>
```

**3장이면 규칙 전달이 끝난다.** 브리핑(밀기 + 게이지) → 첫 실제 카드(기준 칸) → 둘째 카드부터 정상. 3초 안에 읽히는 정보는 브리핑 카드 본문 한 문장이다: "준공까지 60일. 하루에 한 건씩."

### 3-2. `#swipeHint`의 수명

지금 210행의 힌트는 60일 내내 자리를 18px 잡고 앉아 있다(D6의 원인 중 하나). **판단 3회 후 숨긴다.**
```js
if(st.day > 3) $('swipeHint').hidden = true;
```
대신 선택 버튼의 `.kb`(`← 왼쪽` / `오른쪽 →`)가 계속 남아 조작을 알린다.

### 3-3. `#intro`는 이어하기 전용 (`palace.html` 175~181행 패턴)

`reigns_run_v1`이 있을 때만, 첫 카드 대신 먼저 뜬다.

```html
<div id="intro" hidden><div class="box" role="dialog" aria-modal="true" aria-labelledby="introTitle">
  <p class="eyebrow">산업안전기사 · 안전관리자의 하루</p>
  <h1 id="introTitle">23일차에서 멈춰 있습니다</h1>
  <p class="how">근로자 안전 <em>41</em> · 공정률 <em>63</em> · 예산 <em>52</em> · 감독기관 <em>58</em>.
     현장에 남은 미조치 위험 <em>2건</em>. 놓친 규정 노트에 <em>7건</em>이 쌓였습니다.</p>
  <div class="row">
    <button class="b primary" id="introResume" type="button">23일차부터 이어서</button>
    <button class="b" id="introNew"  type="button">새 현장에 부임</button>
    <button class="b" id="introNote" type="button">놓친 규정 노트 보기</button>
  </div>
</div></div>
```
CSS는 `palace.html` 113~119행(`#intro`, `#intro .box`, `.eyebrow`, `h1`, `.how`, `.row`)을 그대로 가져오면 된다. 변수명(`--panel`, `--line`, `--warn`, `--scrim`)이 이미 같다. `--scrim`만 reigns 팔레트에 없으니 `--scrim:rgba(6,10,17,.78)` 한 줄을 16행 부근에 추가한다.

- **난이도 중 / 우선순위 P1.** 브리핑 카드 자체만 떼면 난이도 하(DECK에 객체 하나 + `next()`에 분기 한 줄).

---

## ④ 모바일 레이아웃

기준 기기: **375×667**(SE·미니, 하한), **390×844**(14/15, 안전영역 하단 34px), **412×915**(안드로이드 다수).

### 4-1. 높이 예산을 다시 짠다

문제의 뿌리는 **카드 높이가 내용에 따라 늘어나는데(`min-height`) 담을 통은 고정**이라는 점이다. 반대로 만든다. **통이 카드 높이를 정하고, 본문이 그 안에서 스크롤한다.**

```css
html,body{height:100dvh}
@supports not (height:100dvh){ html,body{height:100%} }

:root{ --topH:44px; }
@media (min-width:521px){ :root{ --topH:52px; } }

#top{padding:6px 12px;min-height:var(--topH)}
#top .b{min-height:36px;padding:7px 11px}          /* 44px 표적에 근접 */

#app{
  height:100dvh;
  padding: calc(var(--topH) + 8px) 14px calc(8px + env(safe-area-inset-bottom,0px));
  gap:10px;
}

#hud{gap:8px}
.g .lb{font-size:11px}
.g .track{height:6px}

#board{flex:1;min-height:0}

/* 카드: 높이를 통이 정한다 */
#card{
  position:absolute;
  width:100%; max-width:400px;
  height:100%;                 /* = #board 높이 */
  max-height:460px;
  display:flex; flex-direction:column;
  padding:0 0 16px;            /* 그림이 위쪽 라운드까지 꽉 차게 */
  touch-action:pan-y;          /* ★ D7 */
  overscroll-behavior:contain;
}
#card .art{height:clamp(80px,13dvh,132px);margin:0 0 12px;border-radius:15px 15px 0 0;flex:none}
#card .subj{flex:none;padding:0 18px}
#card .who {flex:none;padding:0 18px;margin:4px 0 10px}
#card .say{
  flex:1; min-height:0; padding:0 18px;
  overflow-y:auto; -webkit-overflow-scrolling:touch;
  font-size:clamp(14.5px,4.1vw,16.5px); line-height:1.62;
}
#card .topic{flex:none;margin:12px 18px 0;padding-top:11px}

#choices{gap:8px}
.ch{padding:11px 12px;min-height:52px}
.ch .tx{font-size:13px}
```

67행의 `min-height:5.2em`과 172행의 `min-height:6em`은 **삭제한다.** 그 값들의 원래 목적은 카드 높이 튐 방지인데, 카드 높이가 고정되면서 목적이 이미 달성된다.

375×667에서 남는 board 높이:
`667 − 44(top) − 8 − 34(hud) − 10 − 16(meta) − 10 − 58(choices) − 10 − 8(하단) = 469px`
→ 카드 `max-height:460px`에 딱 걸리고, 본문이 길면 `.say`가 스크롤한다. **잘리는 곳이 없다.**

390×844(안전영역 34):
`844 − 44 − 8 − 34 − 10 − 16 − 10 − 58 − 10 − 8 − 34 = 612` → 카드 460 + 위아래 여백 76씩. 여유.

`100dvh`가 D6의 근본 해법인 이유: iOS Safari에서 `height:100%`는 툴바가 있어도 **large viewport**로 계산되어 툴바 뒤로 내용을 밀어 넣는다. `dvh`는 현재 보이는 높이를 따라간다.

### 4-2. 한 손 조작

- 선택 버튼 두 개는 화면 하단에서 `58 + 8 + safe-area` 위치 = 엄지 도달권(하단 0~180px) 한가운데다. **위치 자체는 지금도 맞다.** 문제는 `#swipeHint`가 그 아래 18px를 점유해 버튼이 26px 떠 있는 것. §3-2대로 힌트를 3판 뒤 숨기면 버튼이 하단으로 내려앉는다.
- 판정 시트의 「다음 날」(`#sheet .go`)은 이미 폭 100%. 유지하고 `padding-bottom`에 안전영역만 더한다.
- 상단바 `처음부터` 버튼은 오조작 위험이 큰데 상단 오른쪽에 있다 — 엄지 사각지대라 오히려 다행이다. 다만 2-1의 저장이 들어가면 이 버튼이 **파괴적 동작**이 되므로 `⋯` 메뉴 안으로 옮기고 확인 한 단계를 둔다.

### 4-3. 스와이프와 페이지 스크롤 충돌

현재 `touch-action:none`(60행)이라 카드 위에서 세로 스크롤이 아예 안 된다. `body{overflow:hidden}`이므로 **페이지 스크롤과의 충돌은 원래 없다.** 충돌은 §4-1에서 `.say`에 스크롤을 주는 순간 새로 생긴다. 축 잠금으로 해결한다.

```js
var dragging = false, x0 = 0, y0 = 0, dx = 0, axis = 0;   // axis 0=미정 1=가로 2=세로

cardEl.addEventListener('pointerdown', function(e){
  if(st.dead || !$('sheet').hidden) return;
  dragging = true; x0 = e.clientX; y0 = e.clientY; dx = 0; axis = 0;
  cardEl.className = 'drag' + curExtra;
});
cardEl.addEventListener('pointermove', function(e){
  if(!dragging) return;
  var ax = e.clientX - x0, ay = e.clientY - y0;
  if(!axis){
    if(Math.abs(ax) < 8 && Math.abs(ay) < 8) return;        // 8px 데드존
    axis = Math.abs(ax) > Math.abs(ay) * 1.2 ? 1 : 2;       // 가로가 1.2배 이상일 때만 카드 넘기기
    if(axis === 1){ cardEl.setPointerCapture(e.pointerId); }
    else { dragging = false; cardEl.className = 'settle' + curExtra; return; }  // 세로는 .say 스크롤에 넘긴다
  }
  dx = ax;
  cardEl.style.transform = 'translateX(' + dx + 'px) rotate(' + (dx * 0.05) + 'deg)';
  $('pickL').style.opacity = dx < -30 ? Math.min(1, (-dx - 30) / 50) : 0;
  $('pickR').style.opacity = dx >  30 ? Math.min(1, ( dx - 30) / 50) : 0;
});
```
`1.2` 배수는 한 손 엄지 스와이프가 호를 그려 세로 성분이 섞이는 것을 감안한 값이다. 확정 임계 `92px`(1061행)는 375px 폭에서 화면의 약 25%로 적절하니 그대로 둔다.

### 4-4. 판정 시트 (D8)

```css
#sheet{
  max-height:min(72dvh,560px);
  overflow-y:auto; overscroll-behavior:contain;
  padding:16px 18px calc(18px + env(safe-area-inset-bottom,0px));
}
#sheet .go{position:sticky;bottom:0;margin-top:14px}
```
`position:sticky`가 "「다음 날」이 화면 밖으로 밀려남"을 근본에서 막는다. 시트 안에서 아무리 스크롤해도 버튼은 항상 손 닿는 자리에 있다.

### 4-5. 가로 모드 (짧은 높이)

```css
@media (orientation:landscape) and (max-height:520px){
  #app{max-width:820px;display:grid;align-content:start;
       grid-template-columns:1fr 1fr;
       grid-template-areas:"hud hud" "meta meta" "board ch"}
  #hud{grid-area:hud} #meta{grid-area:meta}
  #board{grid-area:board} #choices{grid-area:ch;align-self:center;grid-template-columns:1fr;gap:10px}
  #card{max-height:none;height:100%}
  #card .art{display:none}
  #swipeHint{display:none}
}
```
그림을 버리는 이유: 가로 500px 높이에서 그림·본문·조문·선택지를 전부 넣으면 어느 것도 안 읽힌다. **읽어야 하는 것은 조문이다.**

- **난이도 하 / 우선순위 P0.** CSS 교체 + 드래그 함수 15행. `#card`를 `display:flex`로 바꾸면서 내부 요소로 `padding:0 18px`를 옮기는 게 유일하게 손이 가는 부분이다.

---

## ⑤ 접근성 체크리스트와 수정 마크업

| 항목 | 지금 상태 | 조치 | 난이도 |
|---|---|---|---|
| 키보드 전용 조작 | ←/→/Enter/Space 동작함(1070~1077행). 단 헤더 버튼에 포커스가 있어도 ←/→가 카드를 넘김 | 가드 추가 (5-5) | 하 |
| 포커스 순서 | **깨짐.** 숨겨지지 않은 `#sheet`·`#over` 버튼이 항상 Tab 순서에 있음(D4) | `hidden` 속성 병행 (5-1) | 하 |
| 라이브 리전 | **없음** (`aria-live` 0건) | `#cLive`·`#sLive` 신설 (5-2) | 하 |
| `prefers-reduced-motion` | 전역 규칙 있음(29행) — **통과**. 단 `#scene` 제거 타이머가 950ms 고정(494행)이라 옛 장면이 겹쳐 보임 | 타이머 분기 (5-7) | 하 |
| 색만으로 상태 구분 | **위반 2건**: `.g.low`(D9), `#sheet .verdict`(97~99행) | 문자·기호·무늬 병기 (5-3, 5-4) | 하 |
| 명도비 | `--dim` 약 4.0:1 (D10) | `#8290AC`로 교체 (5-6) | 하 |
| 터치 표적 44px | `.ch` 약 62px — 통과. `#top .b` 약 30px — 미달 | `min-height:36px` (§4-1) | 하 |
| 대체 텍스트 | 카드 그림이 `aria-hidden="true"`(199행) — 장식이므로 **올바름** | 유지 | — |
| 확대 400% | `body{overflow:hidden}` + 고정 높이라 잘림 | §4-1의 `.say` 스크롤로 완화 | — |

### 5-1. 포커스 함정 제거 (D4)

```html
<div id="sheet" hidden role="dialog" aria-modal="true" aria-labelledby="sOut">
  <span class="verdict" id="sV"></span>
  <p class="out" id="sOut"></p>
  <p class="firsthint" id="sFirst" hidden>…</p>
  <button class="peek" id="sPeek" type="button">기준 확인 <kbd>Space</kbd></button>
  <div class="std"><span class="k">규정 기준</span><span class="v" id="sStd"></span></div>
  <div class="law" id="sLaw"></div>
  <div class="jump" id="sJump">…</div>
  <button class="go" id="sGo" type="button">다음 날</button>
</div>
```
```js
var lastFocus = null, RM = matchMedia('(prefers-reduced-motion:reduce)');

function openSheet(){
  lastFocus = document.activeElement;
  var s = $('sheet');
  s.hidden = false;
  requestAnimationFrame(function(){ s.classList.add('on'); $('sPeek').focus(); });
}
function closeSheet(){
  var s = $('sheet');
  s.classList.remove('on');
  setTimeout(function(){ s.hidden = true; }, RM.matches ? 0 : 320);
  if(lastFocus && lastFocus.isConnected) lastFocus.focus(); else $('chL').focus();
}
```
`#over`도 같은 방식으로 `hidden` + `role="dialog" aria-modal="true"`. 열 때 `oTitle`에 `tabindex="-1"`을 주고 포커스를 옮긴다.

27행의 `[hidden]{display:none!important}`가 이미 있으므로 `transform` 트랜지션과 공존한다. **`hidden=false` → rAF → `.on` 순서가 중요하다.** 같은 프레임에서 둘 다 하면 트랜지션이 안 뜬다.

### 5-2. 라이브 리전 (D5)

```html
<!-- #app 안, #board 앞 -->
<div id="cLive" class="sr" aria-live="polite"    aria-atomic="true"></div>
<div id="sLive" class="sr" aria-live="assertive" aria-atomic="true"></div>
```
```css
.sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;
  clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap;border:0}
```
```js
// next() 끝
$('cLive').textContent = st.day + '일차. ' + pick.s + '. ' + pick.w + '. ' +
  (pick.report ? '현상 보고입니다.' : pick.t) +
  ' 왼쪽 방향키: ' + pick.a.l + '. 오른쪽 방향키: ' + pick.b.l + '.';

// reveal() 안 (2단 시트가 열릴 때) — 게이지 변화까지 같이 읽는다
var names = ['근로자 안전','공정률','예산','감독기관'];
var chg = ch.d.map(function(v, i){ return v ? names[i] + ' ' + (v > 0 ? '+' : '') + v : ''; })
              .filter(Boolean).join(', ');
$('sLive').textContent = $('sV').textContent + '. ' + ch.o + ' ' + chg +
  (c.f ? ' 규정 기준: ' + c.f.replace(/<\/?em>/g, '') : '');
```
`assertive`를 쓰는 이유: 판정은 사용자의 직접 조작에 대한 즉각 응답이고, 직후 포커스가 `#sGo`로 옮겨 가기 때문이다.

### 5-3. 게이지 (D9 + 스크린리더)

```js
// renderHud(init) 의 innerHTML
'<div class="g" data-k="' + i + '" id="gg' + i + '" role="progressbar" ' +
     'aria-valuemin="0" aria-valuemax="100">' +
  '<div class="lb"><span>' + g.n + '</span><b id="gv' + i + '">0</b></div>' +
  '<div class="track"><div class="fill" id="gf' + i + '"></div><span class="dlt" id="gd' + i + '"></span></div>' +
'</div>'
```
```js
// 갱신부
var n = Math.round(v), lowv = v <= 22;
$('gv' + i).textContent = n;
$('gg' + i).setAttribute('aria-valuenow', n);
$('gg' + i).setAttribute('aria-valuetext', G[i].n + ' ' + n + (lowv ? ', 위험' : ''));
$('gg' + i).classList.toggle('low', lowv);
```
```css
.g.low .lb span::before{content:"⚠ ";font-size:11px}          /* 색 말고 기호로도 */
.g.low .track{background:repeating-linear-gradient(45deg,
  var(--line-soft) 0 4px, rgba(240,112,86,.35) 4px 8px)}       /* 색 말고 무늬로도 */
```
`$('gf'+i).parentNode.parentNode.classList.toggle('low', …)`(858행)의 DOM 타고 올라가기도 `gg`+i 직접 참조로 정리된다.

### 5-4. 판정 라벨 (색만으로 구분 금지)

```css
#sheet .verdict.ok::before{content:"✓ ";font-weight:800}
#sheet .verdict.no::before{content:"✕ ";font-weight:800}
```
`sV.textContent`가 그대로 낭독되므로 `::before`는 시각 전용으로 두는 것이 맞다(스크린리더 중복 방지).

### 5-5. 키보드 가드와 Esc 정책

```js
addEventListener('keydown', function(e){
  if(st.dead && !$('over').hidden) return;
  if(e.altKey || e.ctrlKey || e.metaKey) return;
  if(e.target.closest && e.target.closest('#top,#note,#intro')) return;   // ★ 헤더·서랍에서는 카드 조작 금지
  var open = !$('sheet').hidden;
  if(e.key === 'Escape'){
    if(!$('note').hidden){ closeNote(); e.preventDefault(); }
    return;                                     // 시트는 Esc 로 닫지 않는다 (아래 설명)
  }
  if(!open && e.key === 'ArrowLeft')      { e.preventDefault(); choose(-1); }
  else if(!open && e.key === 'ArrowRight'){ e.preventDefault(); choose(1); }
  else if(open && (e.key === 'Enter' || e.key === ' ')){
    e.preventDefault();
    if($('sheet').classList.contains('s1')) reveal(); else $('sGo').click();
  }
  else if(!open && e.key.toLowerCase() === 'n'){ e.preventDefault(); toggleNote(); }  // palace 의 T 관례를 따름
});
```

**Esc로 시트를 닫지 않는 이유가 중요하다.** 지금 `sGo`는 닫기가 아니라 **「다음 날」**이다(1005~1013행에서 `st.day++`). Esc = 취소라는 사용자 관례와 정반대의 결과(하루가 지나감)를 낸다. 시트는 Enter/Space/클릭으로만 넘긴다.

### 5-6. 명도비 한 글자 (D10)

```css
/* reigns.html 16행 */
--dim:#8290AC;   /* was #6E7C95 — index.html 팔레트와 일치시킨다 */
```

### 5-7. 움직임 축소 시 장면 교체 (494행)

```js
setTimeout(function(){ if(old.parentNode) old.parentNode.removeChild(old); }, RM.matches ? 0 : 950);
```

- **난이도 하 / 우선순위 P0** (5-1 · 5-2 · 5-4 · 5-6) · **P1** (5-3 · 5-5 · 5-7).

---

## ⑥ 피드백 타이밍 — 판단과 절충안

### 판단: **즉시 피드백을 유지한다. 다만 한 화면 안에서 두 단으로 쪼갠다.**

근거 셋.

**1. 과제의 성격.** 이 게임이 가르치는 것은 「90 cm」「1:1.8」「1.85 m」「25 V」 같은 **수치 사실의 재인**이다. 사실 재인 과제에서 지연 피드백의 이점(전이·파지)은 학습자가 그 지연 동안 스스로 인출을 시도할 때만 나온다. 이 게임의 "며칠 뒤"는 인출 시도가 아니라 그냥 다른 카드 3장이다. 지연시키면 인출이 아니라 망각만 얻는다.

**2. 오개념 고착 위험.** 카드 선택지는 둘 다 그럴듯하게 쓰여 있다(예: `rail` 카드의 "5 cm 차이는 넘긴다"). 틀린 쪽을 골랐는데 정정이 며칠 뒤에 오면, 그 사이 같은 오판을 다른 카드에서 반복한다.

**3. 지연 피드백은 이미 코드에 있다.** `st.seeds` → `FALLOUT` 사고 카드(908~925행)가 정확히 그 역할이다. 즉 현재 구조는 **즉시 판정 + 지연 결과의 이중 구조**이고, 설계 판단은 이미 옳게 내려져 있다. 진짜 문제는 지연 층이 39주제 중 10주제·확률 45%만 커버한다는 것(D2)이지 타이밍이 아니다. **고칠 것은 즉시/지연의 선택이 아니라 지연 층의 커버리지다** — ②-2의 재점검 큐가 그 답이다.

### 절충안: 판정 시트를 2단으로

**1단(선택 즉시).** 결과 서술 `ch.o`만 보인다. 정오 라벨·수치 기준·조문은 아직 없다. 아래에 버튼 하나: **「기준 확인」**.

**2단(버튼을 누르거나 1.2초 뒤 자동).** `기준 충족`/`기준 미달` 라벨 + `규정 기준` + 조문 + 3D·암기 은행 링크 + 「다음 날」.

```css
#sheet.s1 .verdict,
#sheet.s1 .std,
#sheet.s1 .law,
#sheet.s1 .jump,
#sheet.s1 .go{display:none}
#sheet.s2 .peek{display:none}
#sheet .peek{margin-top:14px;width:100%;border:1px dashed var(--line);background:transparent;
  color:var(--muted);border-radius:9px;padding:12px;font-size:14px;cursor:pointer}
#sheet .peek:hover{border-color:var(--warn);color:var(--text)}
#sheet .peek kbd{font-family:var(--mono);font-size:11.5px;border:1px solid var(--line);
  border-radius:4px;padding:0 5px;margin-left:6px}
```
```js
var peekTimer = 0;
function openSheet(){
  lastFocus = document.activeElement;
  var s = $('sheet');
  s.hidden = false; s.classList.remove('s2'); s.classList.add('s1');
  requestAnimationFrame(function(){ s.classList.add('on'); $('sPeek').focus(); });
  peekTimer = setTimeout(reveal, 1200);
}
function reveal(){
  clearTimeout(peekTimer);
  var s = $('sheet');
  if(s.classList.contains('s2')) return;
  s.classList.remove('s1'); s.classList.add('s2');
  $('sGo').focus();
  $('sLive').textContent = /* 5-2 의 문자열 */;
}
$('sPeek').addEventListener('click', reveal);
```

**이 1.2초가 왜 의미가 있나.** 결과 서술(`ch.o`)은 이미 답을 암시한다 — "망은 있으나 12 m 아래입니다". 그걸 읽는 동안 학습자는 "그럼 기준이 몇 m였지"를 스스로 떠올린다. 정답을 보기 직전의 **생성 시도**다. 이 창을 안 만들면 시선이 곧장 노란 숫자로 가서 인출 없이 읽기만 한다. 창은 짧아야 한다(길면 성가심). **1.2초 + 언제든 건너뛰기 가능**이 절충점이다.

`prefers-reduced-motion`과 무관하게 이 지연은 유지한다 — 애니메이션이 아니라 학습 장치다. 다만 «항상 즉시 펼치기» 토글을 `⋯` 메뉴에 두고 `reigns_stats_v1`에 저장하면 반복 회차 사용자의 마찰이 사라진다.

### 한 단계 더 (선택): 틀린 카드에만 숫자 가리기

`ok:0`으로 온 2단에서는 `sStd`의 수치를 `▢`로 덮고 탭하면 열리게 한다. `memo.html`의 `숫자 가리기(H)` 관례와 같은 상호작용이라 사이트 안에서 낯설지 않다.

```js
function maskNums(html){
  return html.replace(/<em>([^<]+)<\/em>/g,
    '<button type="button" class="mk" aria-label="가려진 값 보기">▢</button><em hidden>$1</em>');
}
// .mk 클릭 → 버튼 제거 + 다음 형제 em 의 hidden 해제
```
```css
#sheet .std .mk{font:inherit;font-family:var(--mono);border:1px solid var(--warn);
  background:rgba(227,181,77,.10);color:var(--warn);border-radius:4px;padding:0 8px;cursor:pointer}
```
맞힌 카드에는 적용하지 않는다. 이미 아는 것을 다시 가리는 건 마찰만 늘린다.

- **2단 시트: 난이도 하 / 우선순위 P1.** CSS 클래스 토글 하나 + 함수 두 개.
- **숫자 가리기: 난이도 중 / 우선순위 P2.**

---

## ⑦ 우선순위 순 실행 목록

### P0 — 이게 없으면 학습 도구가 아니다

| # | 항목 | 난이도 | 손대는 곳 |
|---|---|---|---|
| 1 | `reigns_run_v1` 저장·이어하기. `reset()`을 `newRun()`/`resume()`으로 분리, `c.used` → `st.used` | 중 | 834~843, 908~968, 1005~1013, 1041 |
| 2 | 모바일 높이 붕괴 수정: `100dvh` · 카드 고정 높이 + `.say` 스크롤 · `min-height` 삭제 · 안전영역 | 하 | 23~27, 32, 56~72, 141~150, 170~178 |
| 3 | 시트 `max-height` + `.go` 스티키 | 하 | 88~106 |
| 4 | 포커스 함정 제거: `#sheet`/`#over`에 `hidden` + `role="dialog"` + 포커스 이동·복귀 | 하 | 213~231, 1003~1013, 1015~1040 |
| 5 | `aria-live` 두 리전 + `.sr` 클래스 | 하 | 신설 2행 + `next()`/`choose()` 각 3행 |
| 6 | 판정 라벨 `✓`/`✕`, 게이지 `⚠`·무늬, `--dim:#8290AC` | 하 | 16, 41~43, 97~99 |
| 7 | `touch-action:pan-y` + 드래그 축 잠금 | 하 | 60, 1043~1066 |
| 8 | `reigns_miss_v1` 기록 시작 (UI는 P1이지만 기록은 먼저 켠다 — 데이터는 소급이 안 된다) | 하 | `choose()` 3행 |

### P1 — 학습 루프의 본체

| # | 항목 | 난이도 | 손대는 곳 |
|---|---|---|---|
| 9 | 재점검 큐 `st.recheck` + 재점검 배지 | 중 | 908~968, 970~1003, 카드 마크업 1행 |
| 10 | `reigns_srs_v1` + 가중 추첨 + `st.recentK` 되살리기(D3) | 중 | 908~968 |
| 11 | 「놓친 규정」 노트 서랍 + `⋯` 메뉴 진입 + `N` 단축키 | 중 | 신설 약 60행 |
| 12 | `lab.html#topic=` / `memo.html#g=` 딥링크(`LAB3D`·`MEMO` 상수) — 시트와 노트 양쪽 | 하 | 신설 상수 2개 + `choose()` 3행 |
| 13 | 0일차 브리핑 카드 + 손가락 고스트 + 첫 시트 한 줄 + `#swipeHint` 3판 뒤 숨김 | 중 | DECK 앞 객체 1개 + `next()` 분기 |
| 14 | 2단 판정 시트 (기준 확인 → 1.2초) | 하 | 88~106, 970~1013 |
| 15 | `#intro` 이어하기 다이얼로그 (`palace.html` 113~119행 CSS 재사용, `--scrim` 변수 추가) | 중 | 신설 약 30행 |
| 16 | `role="progressbar"` + 키보드 가드 + Esc 정책 + reduced-motion 타이머 | 하 | 845~861, 1070~1077, 494 |
| 17 | `처음부터`를 `⋯` 메뉴로 옮기고 확인 한 단계 | 하 | 184, 1078 |

### P2 — 사이트와 결을 맞춘다

| # | 항목 | 난이도 | 비고 |
|---|---|---|---|
| 18 | `safety_theme` 대응: `<head>` 부트 스크립트 + `[data-theme=light]` 팔레트 + `.bTheme` (D11) | 중 | `index.html` 8행·126행을 그대로 복사. 라이트 팔레트 변수 14개를 새로 정해야 해서 「중」 |
| 19 | `⋯` 더보기 메뉴로 형제 5개 페이지 링크 통일 (`palace.html` 190~200행 패턴) | 하 | 지금은 `3D 실습장` 하나뿐 |
| 20 | `reigns_stats_v1` — 최고 도달 일수·준공 횟수를 종료 화면과 `#intro`에 표시 | 하 | |
| 21 | 틀린 카드 2단에서 숫자 가리기(`▢`) | 중 | memo 의 `H` 관례와 동일 |
| 22 | 가로 모드 그리드 레이아웃 | 하 | §4-5 |
| 23 | `FALLOUT` 확충 — 지금 10장. 최소 20장(주제의 절반)으로 | 중 | 콘텐츠 작업. 재점검 큐(#9)가 들어가면 급하지 않다 |

### 구조를 깨는 비용이 있는 유일한 항목

**#12의 절반.** `lab.html#topic=` 쪽은 비용 0이다 — `lab.html:1862`가 이미 해시를 읽고, 키 21개가 문자열까지 일치한다.
`memo.html#g=` 쪽은 reigns 안의 `MEMO` 상수(40줄)가 **memo.html BANK의 묶음 id에 손으로 묶인 값**이라, memo의 묶음이 재편성되면 링크가 깨진다. 두 선택지가 있다.

- **(A) 지금대로 상수 표를 reigns에 둔다.** 비용: memo 재편성 때 표를 다시 만들어야 한다. 무의존성·단일 HTML·페이지별 독립 배포가 전부 유지된다. **권장.**
- **(B) `memo.html`에 `#t=<topic3d>` 해시를 추가한다.** `memo.html:254`를 한 줄 고쳐 `topic3d`로도 묶음을 찾게 만든다. 그러면 reigns는 `memo.html#t=net`만 쓰면 되고 상수 표가 사라진다. 비용: **파일 두 개를 동시에 배포해야 한다.** 지금까지 각 페이지가 서로 독립적으로 배포 가능했던 성질이 깨진다. 묶음 재편성이 잦다면 이쪽이 싸다.

그 밖의 모든 항목은 `reigns.html` 한 파일 안에서 끝나고, 외부 요청·라이브러리·빌드 도구를 추가하지 않으며, 오프라인 동작을 유지한다.
