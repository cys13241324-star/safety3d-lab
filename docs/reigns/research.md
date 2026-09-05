# reigns.html 레퍼런스 조사

조사일 2026-09-05 · 대상 `C:\Users\co132\Desktop\project\산업안전기사-github\safety3d-lab\reigns.html` (1,083줄, 단일 HTML, 무의존)

## ① 요약 5줄

1. **레퍼런스보다 급한 게 먼저 나왔다.** 현재 덱은 오답이 심는 씨앗 40종 중 **30종에 대응하는 사고 카드가 없고**, `next()`의 발화 코드가 매칭 실패 시 씨앗을 제거하지 않아 죽은 씨앗이 영구히 쌓인다 → 판이 길어질수록 사고 카드가 **덜** 뜬다. 이 게임의 핵심 학습 장치인 지연 피드백이 후반으로 갈수록 꺼진다.
2. 카테고리 1의 최고 참조는 `Sisyphe42/ReignsAgent`(★298, MIT, 2026-08 활동). `packages/core`(헤드리스 결정론 런타임)와 `packages/reviewer`(몬테카를로 밸런싱)가 필요한 두 조각을 그대로 갖고 있고, MIT라 코드 차용까지 된다. `packages/interface/web/assets/swipe-input.js`도 무의존 바닐라라 바로 읽힌다.
3. `outfrost/deckswipe`는 GitHub에 **README 두 줄짜리 리다이렉트 껍데기만 남아 있다**(archived, 라이선스 없음). 코드는 Codeberg로 이전했고 Codeberg는 AI 스크레이퍼를 차단한다 — 포크 `meltar95/deckswipe`에서 원본과 **MIT LICENSE(ⓒ2018-2020 Iwo 'Outfrost' Bujkiewicz)**를 확인했다. 건질 것은 `CardDrawQueue`의 상대지연 큐 40줄.
4. 카드게임 밸런싱 "도구" 생태계는 사실상 비어 있다(네 가지 질의 결과 ★0~8의 개인 습작뿐). ReignsAgent Reviewer를 베끼는 게 정답이고, 그 경고 코드 `unsatisfied_required_tags`가 위 1번 버그를 자동으로 잡는 바로 그 검사다.
5. 지연 피드백 설계는 학술적으로 지지되지만 **전면 적용은 금물**이다. Butler 외 (2007)는 지연 우위를 보이고 Metcalfe (2017)는 그럴듯한 오답의 가치를 지지하지만, Kulik & Kulik (1988)은 실무 자료에서 즉시 피드백이 유리한 경우가 많았다고 보고한다 → 조문·수치는 즉시(지금대로), 체감만 지연시키는 하이브리드가 맞다.

---

## ①-b 현재 덱 진단 (조사 중 발견 — 레퍼런스보다 이게 급하다)

레퍼런스를 뒤지다 지금 파일에서 두 가지가 나왔다. 아래 권고 3(시뮬레이터)이 자동으로 잡아 줄 종류의 문제이고, 실제로 ReignsAgent Reviewer의 `unsatisfied_required_tags` 경고가 정확히 이 케이스다.

**(1) 씨앗 40종 중 30종은 절대 터지지 않는다.**

`DECK`의 오답 선택지가 심는 `tag`는 40종. `FALLOUT`이 받아 주는 `req`는 10종(`approach, confined, elcb, fall, net, press, scaffold, shore, trench, weather`)뿐이다. 나머지 30종은 사고 카드가 없다.

```
boiler caisson carry chemdist exgap forklift frame gangway gasweld grinder
horse ladder lux mobscaf noise panelspace pile plank powerline rail
ramp robot roller rotor sawblade stairs staticflow vdt welder wirerope
```

`next()`의 발화 코드를 보면 이게 단순한 누락에서 끝나지 않는다.

```js
var seed = ripe[Math.floor(Math.random() * ripe.length)];
pick = FALLOUT.filter(function(c){ return c.req === seed.tag; })[0];
if(pick){ st.seeds = st.seeds.filter(function(s){ return s !== seed; }); }
```

매칭되는 사고 카드가 없으면 `pick`은 `undefined`고, `if(pick)`이 거짓이라 **그 씨앗은 `st.seeds`에서 제거되지 않는다.** 죽은 씨앗이 영구히 쌓이면서 `ripe` 풀을 채우고, 그 판이 길어질수록 45% 굴림이 죽은 씨앗을 뽑을 확률이 올라간다. 즉 **후반으로 갈수록 사고 카드가 오히려 덜 뜬다.** 지연 피드백이라는 이 게임의 핵심 학습 장치가 시간이 갈수록 약해지는 구조다.

권고 2의 상대지연 큐로 바꾸면 이 클래스의 버그가 원천적으로 사라진다 — 큐에는 실재하는 카드 id만 들어가고, 저자가 `followup`을 적는 순간 대상 카드가 있는지 눈으로 보이기 때문이다.

**(2) 과목 분포가 시험 배점과 어긋난다.**

| 과목 | 카드 수 | 산업안전기사 필기 배점 |
|---|---|---|
| 건설안전기술 | 18 | 20문항 |
| 기계위험방지 | 9 | 20문항 |
| 전기위험방지 | 6 | 20문항 |
| 화학설비위험방지 | 4 | 20문항 |
| 인간공학 | 2 | 20문항 |
| 안전관리론 | 1 | 20문항 |

40장 중 18장이 건설안전기술이다. 6과목 균등 배점 시험의 학습 도구로서는 건설 편중이 심하고, 안전관리론은 카드 한 장이라 사실상 다루지 않는다. Reviewer의 `cardVisitRates`를 과목별로 집계하면 "60일 한 판에서 각 과목이 몇 번 나오는가"가 숫자로 나온다.

---

## ② 저장소 표

모든 항목은 `gh api repos/OWNER/NAME`로 실재·스타·라이선스·최근 푸시를 확인함. 확인 못 한 것은 싣지 않음.

### 카테고리 1 — Reigns류 구현

| 저장소 | ★ | 라이선스 | 최근 푸시 | 상태 | 가져올 것 |
|---|---|---|---|---|---|
| `Sisyphe42/ReignsAgent` | 298 | **MIT** | 2026-08-16 | 활성 | `packages/core/src/index.js`의 카드 스키마 + `getEligibleCards`/`requirementsMatch` 게이팅 + `chooseWeightedCard` 가중추첨 + `serializeState`/`restoreState` 스냅샷. 코드 차용 가능. |
| `outfrost/deckswipe` (GitHub) | 85 | 없음(리다이렉트 껍데기) | 2025-09-15 | **archived, 코드 없음** | GitHub 쪽은 README 2줄뿐. 실제 코드는 codeberg.org/outfrost/deckswipe. |
| `meltar95/deckswipe` (deckswipe 포크, 코드 보존) | 0 | **MIT** (LICENSE 원문 확인, ⓒ2018-2020 Iwo 'Outfrost' Bujkiewicz) | 2025-03-13 | 포크 | `CardModel/DrawQueue/CardDrawQueue.cs`의 상대지연 큐 + `Followup.cs` + `Prerequisite/CardPrerequisite.cs`(`CardStatus` 비트플래그). C#이지만 알고리즘이 40줄이라 JS 이식이 쉽다. |
| `sboigelot/TwentyCardsToTheApocalypse` | 7 | **GPL-3.0** | 2017-02-23 | 방치 | 20턴 고정 종말 시계 구조. **GPL이므로 코드 차용 금지, 아이디어 참고만.** 사실 얻을 게 별로 없다. |
| `anthkris/id-simulator` | 4 | MIT | 2018-10-08 | 방치 | "교육설계자 되기" Reigns-like. 교육 소재를 카드로 옮긴 선례로서의 가치뿐, 코드는 참고 수준 이하. |
| `oselcuk/eas-reigns` | 3 | **없음(무라이선스)** | 2019-04-18 | 방치 | 기후변화 주제 Reigns-like. **라이선스 없음 = 전체 권리 유보. 코드 열람만 가능, 복사 금지.** |

### 카테고리 2 — 밸런싱/시뮬레이션

| 저장소 | ★ | 라이선스 | 최근 푸시 | 가져올 것 |
|---|---|---|---|---|
| `Sisyphe42/ReignsAgent` `packages/reviewer` | 298 | **MIT** | 2026-08-16 | `runMonteCarloReview` — 기본 10만 사이클 × 최대 100턴, 시드 고정. 경고 코드가 이 프로젝트에 그대로 필요한 것들이다(아래 상세). |
| `boardgameio/boardgame.io` | 12,423 | MIT | 2026-08-18 | `src/plugins/random/random.alea.ts`(시드 PRNG로 리플레이 재현), `src/ai/mcts-bot.ts`·`random-bot.ts`(봇으로 밸런스 회귀 테스트). **단, 도입 시 무의존 구조가 깨짐 — 아이디어만.** |
| `inkle/ink` / `y-lohse/inkjs` | 4,927 / 647 | MIT / MIT | 2026-05-05 / 2026-09-01 | 분기 서사 + 상태 변수 언어. **inkjs를 넣으면 무의존이 깨진다(빌드+런타임 ~200KB). 채택 비추, 아이디어만.** |
| `klembot/twinejs` | 2,877 | **GPL-3.0** | 2026-08-22 | 분기 스토리 저작 UI. **GPL, 코드 차용 불가.** 카드 저작 도구가 필요해지면 개념 참고. |

### 카테고리 3 — 교육용 게임화 · 지연 피드백 · 간격 학습

| 저장소/서비스 | ★ | 라이선스 | 최근 푸시 | 가져올 것 |
|---|---|---|---|---|
| `ratelworks/agent-safety-oss` | 45 | **MIT** | 2026-08-03 | **도메인이 정확히 겹치는 유일한 한국어 오픈소스.** 산안법·기준규칙·중처법·KOSHA Guide 기반 법정 안전문서 작성 도구. 게임은 아니지만 조문을 "현장 상황 → 근거 조항 → 요구 조치"로 구조화한 스키마가 카드 JSON의 출발점이 된다. MIT라 스키마 재사용 가능. |
| `OWASP/cornucopia` | 146 | **CC-BY-SA-4.0** | 2026-09-04 | 보안 표준 조항을 "카드 한 장 = 요구조항 한 개"로 옮긴 가장 성숙한 실사례. **조문 ID를 카드 메타데이터로 박고 빌드 시점에 원문을 주입하는 파이프라인**을 볼 것. ⚠ **copyleft(SA) — 카드 텍스트를 가져오면 파생물도 SA. 구조만 참고할 것.** |
| `t-mw/storylets-rs` | 8 | **MIT** | 2025-01-19 | **권고 2의 대안 설계 근거.** 각 카드가 전제조건 집합을 갖고 자격 만족 풀에서 뽑는 스토리렛 모델. "3일 뒤 폭발"이 사실상 `{seed:'net', turnsElapsed>=3}` 전제조건일 뿐이라는 것 — 별도 타이머 큐 없이 권고 1의 `requirements` 하나로 끝낼 수 있다는 논거. Rust지만 코드가 짧다. |
| `adamshostack/eop` (Elevation of Privilege) | 360 | **null** (README에 원 MS 배포 기준 CC-BY-3.0 US 명시) | 2024-06-20 | `cards.yaml` 한 파일이 덱 전체. 덱을 단일 선언형 데이터로 두고 렌더러를 분리하는 구조. ⚠ SPDX 미판정이므로 텍스트 차용 전 원 고지 확인. |
| `seo-jinseok/korean-law-mcp` | 5 | **MIT** | 2025-12-26 | 법제처 API 호출 패턴. 기준규칙 조문 원문을 카드 제작 단계에서 배치로 뽑을 때. (MEMORY의 법제처 API 메모와 함께 볼 것.) |
| `finalchild/law-mcp` | 31 | **없음(무라이선스)** | 2025-07-07 | 같은 목적, 스타는 더 많음. **라이선스 없음 = 코드 복사 금지, 엔드포인트·파라미터 조합만 참고.** |
| `alyssaxuu/carden` | 487 | **MIT** | 2022-06-17 | SRS + 게임화 조합의 MIT 선례. 4년 미갱신이지만, SRS 스케줄과 게임 진행(스트릭·성장)을 한 상태 객체에 합치는 방식 참고. |
| `open-spaced-repetition/ts-fsrs` | 774 | **MIT** | 2026-09-03 | 현재 유지되는 FSRS 표준 구현. **최신 기본 파라미터 배열과 difficulty/stability 갱신식**을 여기서. |
| `open-spaced-repetition/fsrs.js` | 181 | **MIT** | 2024-04-10 | 순수 JS 단일 구현. **바닐라 50줄 축약의 원본으로 가장 직접적.** ⚠ FSRS-4 세대라 낡음 — 공식은 `ts-fsrs`로 대조할 것. |
| `open-spaced-repetition/free-spaced-repetition-scheduler` | 712 | **MIT** | 2026-04-21 | FSRS(DSR 모델) 원본 명세. 재구현 근거. |
| `open-spaced-repetition/awesome-fsrs` | 680 | **CC0-1.0** | 2026-09-01 | 구현체·논문·벤치마크 목록. |
| **Bad News** (getbadnews.com) | — | 실서비스 | — | 브라우저 선택형 카드 게임 중 **효과가 논문으로 검증된 드문 사례.** "플레이어를 위반자 역할로 세워 규칙을 체득시키는" 프레이밍과, 사전/사후 문항으로 효과를 재는 최소 평가 설계. |
| **iCivics "Do I Have a Right?"** | — | 실서비스 | — | 사례 카드 → 조항 매칭 → 판정 결과 루프. 기준규칙 조문 매칭의 직접 참고. |

**지연 피드백 근거** (전부 Crossref DOI 검증)

- **Butler, Karpicke & Roediger (2007)**, *The effect of type and timing of feedback on learning from multiple-choice tests*, J. Exp. Psychol.: Applied 13(4), 273–281. DOI `10.1037/1076-898X.13.4.273` — **지연 피드백이 즉시 피드백보다 최종 성적 우수.** 피드백 "종류"는 차이 없음. 이 게임 설계의 핵심 근거이자, **연출보다 지연 자체가 효과의 원천**이라는 시사점.
- **Metcalfe (2017)**, *Learning from Errors*, Annual Review of Psychology 68, 465–489. DOI `10.1146/annurev-psych-010416-044022` — hypercorrection effect: **확신에 차서 틀린 오답일수록 교정 후 기억이 더 남는다.** → 오답 선택지를 "현장에서 실제로 통용되는 그럴듯한 위법 관행"으로 쓰는 것을 정당화한다. 현재 카드의 `b` 선택지("5 cm 차이는 넘긴다", "망은 쳤으니 넘어간다")가 이미 이 원칙을 잘 따르고 있다.
- **Kulik & Kulik (1988)**, *Timing of Feedback and Verbal Learning*, Review of Educational Research 58(1), 79–97. DOI `10.3102/00346543058001079` — **반증 단서.** 53개 연구 메타분석에서, 실험실형 과제는 지연이 유리했지만 **실제 교실 퀴즈·실무 자료에서는 즉시 피드백이 유리한 경우가 많았다.** → 전면 지연은 위험. 하이브리드가 맞다(아래 권고 2).
- **Roediger & Karpicke (2006)**, *Test-Enhanced Learning*, Psychological Science 17(3), 249–255. DOI `10.1111/j.1467-9280.2006.01693.x` — 인출 연습이 재독보다 낫다. **해설(`#sheet`)을 보이기 전에 반드시 좌/우를 고르게 하는 현재 UX가 옳다는 근거.** 지우지 말 것.
- **Cepeda, Pashler, Vul, Wixted & Rohrer (2006)**, *Distributed practice in verbal recall tasks*, Psychological Bulletin 132(3), 354–380. DOI `10.1037/0033-2909.132.3.354` — 317개 실험. 최적 간격은 목표 파지 기간에 비례. SRS 도입 시의 인용처.
- **Ud Din & Gibson (2019)**, *Serious games for learning prevention through design concepts*, Safety Science 115. DOI `10.1016/j.ssci.2019.02.005` — 건설 안전 도메인에서 시리어스 게임 효과를 실험으로 잰 드문 연구. 잠재(latent) 위험 인지가 주제라 이 프로젝트의 서사와 직결.
- ⚠ **Kandemir, Esposito, Gurgand & Ramus (2026)**, *A Meta-Analysis of the Impact of Feedback Timing on Learning Outcomes in Computer-Assisted Learning*, Educational Psychology Review 38(1). DOI `10.1007/s10648-026-10117-8` — 매체가 정확히 일치하는 최신 메타분석이지만 **본문을 확인하지 못했다**(Springer 인증 리다이렉트). 서지정보만 Crossref로 확인. 지연 방침의 강도를 정하기 전에 본문을 직접 볼 것.

### 카테고리 4 — 스와이프 인터랙션 · 접근성

| 저장소 | ★ | 라이선스 | 최근 푸시 | 가져올 것 |
|---|---|---|---|---|
| `davidjerleke/embla-carousel` | 8,407 | **MIT** | 2026-09-03 | `src/components/DragTracker.ts` 60줄. 170ms 롤링 윈도우로 "오래 끌다 멈춘 뒤 뗀 것"을 flick에서 제외하고, `force = diffDrag/diffTime`, `isFlick = diffTime && !expired && |force| > 0.1`로 판정. `forceBoost = {mouse:300, touch:400}`으로 입력장치별 계수 분리. |
| `sciactive/tinygesture` | 228 | **Apache-2.0** | 2026-04-04 | 단일 파일. `threshold`(거리)와 `disregardVelocityThreshold`(이 거리 넘으면 속도 무시)를 분리. 대각선 정리는 `Math.tan((45±limit)*π/180)` 각도 게이트. |
| `john-doherty/swiped-events` | 594 | **MIT** | 2024-04-27 | 1KB 무의존. 제스처를 `CustomEvent('swiped-left', {bubbles:true})`로 발행해 로직과 완전 분리. 500ms 타임아웃 = "느리게 끈 건 스와이프 아님". |
| `gajus/swing` | 2,632 | **NOASSERTION**(LICENSE 원문 BSD-3-Clause 형태) | 2023-09-22 | `throwOutConfidence = max(min(|dx|/w,1), min(|dy|/h,1))` — 0~1 confidence 한 변수로 판정과 시각 피드백을 동기화. **차용 전 LICENSE 원문 재확인 필요.** |
| `atlassian/pragmatic-drag-and-drop` | 12,749 | **NOASSERTION**(LICENSE = Apache-2.0, ⓒ2024 Atlassian) | 2026-09-04 | `packages/live-region/src/index.tsx` 60줄 순수 DOM. `role="status"`를 쓰는 근거를 주석에 명시(`role="alert"`는 포커스 이동 시 누락됨), announce를 `setTimeout`으로 지연시켜 포커스 이동에 메시지가 잘리는 걸 방지. 접근성 가이드 mdx도 볼 것. |
| `clauderic/dnd-kit` | 17,600 | **MIT** | 2026-07-13 | `packages/dom/src/core/plugins/accessibility/`. `defaultAttributes = {role:'button', roleDescription:'draggable', tabIndex:0}`, `LiveRegion.ts`는 `role="status"+aria-live="polite"+aria-atomic="true"`에 `clip`과 `clip-path:inset(100%)` 병행. 알림 500ms 디바운스. |
| `nolimits4web/swiper` | 41,902 | **MIT** | 2026-09-02 | `src/modules/a11y/a11y.ts` — 무의존 vanilla. live region 생성 + `notify()` 문구 파라미터화 + `aria-roledescription`/`aria-disabled`/`onEnterOrSpaceKey`. 20~30줄로 축약 가능. |
| `atlassian/react-beautiful-dnd` | 33,937 | **NOASSERTION**(LICENSE = Apache-2.0) | 2025-08-18 | **archived.** 코드는 React라 못 쓰지만 `docs/guides/browser-focus.md`가 "DOM에서 제거된 요소가 포커스를 갖고 있으면 포커스가 `<body>`로 날아간다"를 다룬다 — 카드 스택에서 맨 위 카드를 지울 때의 정확한 문제. **문서 참고 전용.** |

**표준 문서** (URL 응답 확인함)

- **WCAG 2.2 SC 2.5.7 Dragging Movements (AA)** — https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html — 드래그로 되는 모든 기능은 드래그 없는 단일 포인터로도 되어야 하고, 그 대안이 swipe/flick 같은 path-based gesture여서는 안 된다. **즉 좌/우 선택 버튼이 AA 준수의 필수 요건**이다(현재 `#chL`/`#chR`이 이미 있음 — 유지할 것).
- **WCAG 2.2 SC 2.3.3 Animation from Interactions (AAA)** — https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html — 충분 기법으로 `prefers-reduced-motion` 명시.
- **W3C Pointer Events Level 3** — https://www.w3.org/TR/pointerevents3/ — §5 `setPointerCapture`(이미 사용 중), §4.2.7 `pointercancel`(이미 처리 중), §8 `touch-action`은 CSS로 명시 선언 필요(이미 `touch-action:none`), §10 `getCoalescedEvents()`로 속도 계산 정밀도 향상.
- **WAI-ARIA APG** — https://www.w3.org/WAI/ARIA/apg/patterns/ — APG에는 **drag-and-drop 전용 패턴이 없다.** 그래서 위 라이브러리들의 관행이 사실상의 기준 역할을 한다. Carousel 패턴(https://www.w3.org/WAI/ARIA/apg/patterns/carousel/)은 `aria-roledescription` 사용법 참고.

### 카테고리 5 — 단일 HTML 배포

| 저장소 | ★ | 라이선스 | 최근 푸시 | 가져올 것 |
|---|---|---|---|---|
| `Sisyphe42/ReignsAgent` `packages/interface/src/player-build.js` | 298 | MIT | 2026-08-16 | `stitchPlayerRuntime(template, coreSource)` — 템플릿의 `/* CORE_IMPORT_MARKER */`를 찾아 코어 소스의 `export ` 키워드만 정규식으로 벗겨 인라인. 결과물이 `standalone-player.html`(73KB) 단일 파일. |
| `StarKnightt/operation-ironhold` | 89 | MIT | 2026-07-26 | 단일 290KB HTML FPS. 실제로 존재하고 최근 유지보수되는 몇 안 되는 사례. 자산 인라인/에셋 없는 절차생성 패턴. |
| `drakeaxelrod/single-html-file-apps` | 10 | MIT | 2025-07-10 | 단일 HTML 앱 모음. 규모가 작아 참고 강도는 낮다. |

`js13kGames` 조직(github.com/js13kGames)은 실재하지만 **개별 출품작 저장소가 대부분 ★0~2이고 라이선스가 제각각(GPL-3.0/무라이선스/MIT 혼재)이다.** 13KB 제약 하의 기법 자체는 참고할 만하나, 특정 저장소를 코드 소스로 삼지 말 것.

---

## ③ 채택 권고 3가지

### 권고 1 — 카드 스키마에 `requirements` 게이팅을 넣는다 (출처: ReignsAgent core, MIT)

**현재 문제.** `next()`는 `DECK.filter(c => !c.used)`에서 균등 랜덤으로 뽑는다. 카드가 나올 조건이 `used` 하나뿐이라, "안전난간 카드를 이미 무시한 사람에게만 뜨는 후속 카드", "예산이 20 밑일 때만 뜨는 본사 압박 카드" 같은 걸 표현할 수 없다. 지금 `FALLOUT`이 이걸 흉내내려고 `req`라는 별도 배열과 `st.seeds` 특수 경로를 쓰는데, 이게 사고 카드에만 통하는 일회용 배관이다.

**가져올 것.** ReignsAgent `packages/core/src/index.js`의 요구조건 5키를 카드 공통 필드로 승격한다.

```
requirements: { allTags, anyTags, noneTags, variables, factions }
```
`factions`는 게이지별 `{min, max, equals}`. 판정은 `getEligibleCards(cards, state)` 한 줄로 끝나고, `FALLOUT`/`FLAVOR`/`DECK`이 하나의 덱으로 합쳐진다. 지금의 `tag`/`req`/`used`가 전부 `noneTags`/`allTags`/`dismissedCards`로 흡수된다.

**같이 가져올 것 두 개.**
- `chooseWeightedCard` — 카드마다 `weight`, 상태에 `cardWeights` 오프셋. 사고 카드의 확률을 `Math.random() < 0.45` 하드코딩 대신 가중치로 표현할 수 있다.
- `evaluateGameOver`가 **`value <= 0 || value >= 100` 양쪽 모두**를 사망으로 본다는 점. 현재 reigns.html은 `Math.min(100, ...)`로 클램프만 하고 `findIndex(v => v <= 0)`로만 죽는다. 그래서 지금은 공정률·예산을 100에 붙여 두는 게 순이득이고, "안전만 챙기면 된다"는 잘못된 학습이 생긴다. 상한 사망을 넣으면 감독기관 100 = 현장 전면 감사, 공정률 100 = 무리한 돌관 같은 서사도 붙일 수 있다.

**비용.** 없음. 순수 JS 로직, 의존성 0. 카드 40장의 데이터 마이그레이션(1회)이 전부다.

### 권고 2 — 씨앗 발화를 상대지연 큐로 결정론화한다 (출처: deckswipe `CardDrawQueue`, MIT)

**현재 문제.**
```js
var ripe = st.seeds.filter(s => st.day - s.day >= 3);
if(!pick && ripe.length && Math.random() < 0.45){ ... }
```
"3일 지나면 45% 확률로 터진다"는 건 (a) 언제 터질지 저자가 모르고, (b) 운 나쁘면 60일 내내 안 터져서 지연 피드백이라는 학습 장치 자체가 발동하지 않으며, (c) 시뮬레이션으로 검증할 수 없다.

**가져올 것.** deckswipe의 `CardDrawQueue`는 큐 각 항목이 **직전 항목으로부터의 상대 지연**을 들고 있고, `Next()`는 맨 앞 항목의 `Delay`를 1 깎아 0이 되면 반환한다. `Insert()`가 누적 지연을 따라가며 삽입 위치를 정하고 앞뒤 항목의 delay를 보정한다. 40줄짜리 알고리즘이고 JS 이식이 그대로 된다.

이 프로젝트로 옮기면: `b:{... tag:'net'}` 대신 `b:{... followup:{card:'net_accident', delay:3}}`. 선택 즉시 큐에 꽂히고, 정확히 3일 뒤 사고 카드가 뜬다. **위반 → 사고**의 인과가 학습자에게 셀 수 있는 간격으로 보이고, 시뮬레이터가 "위반 N건 중 사고로 회수된 비율"을 정확히 잴 수 있다.

같이 볼 것: `CardStatus` 비트플래그(`None / CardShown / RightActionTaken / LeftActionTaken`). 카드별 "본 적 있다 / 왼쪽 골랐다 / 오른쪽 골랐다"를 3비트로 들고 있으면, 오답 복습 스케줄링과 종료 화면의 "놓친 규정" 목록이 지금의 `st.viol` push보다 정확해진다.

**대안 설계 하나 — 큐를 안 만드는 방법.** `t-mw/storylets-rs`(★8, MIT)는 이걸 별도 큐 없이 푼다. 카드가 전제조건 집합을 갖고, 매 턴 자격 만족 풀에서 뽑는다. 이 프로젝트로 옮기면 사고 카드는 그냥 `requirements: {allTags:['net'], minElapsed:3}`인 일반 카드가 되고, **권고 1의 게이팅 하나로 흡수된다.** 새 자료구조가 아예 필요 없다.

두 방식의 차이는 정확도다. 큐는 "정확히 3일 뒤", 전제조건은 "3일 뒤부터 언젠가". 학습 측면에서는 **큐 쪽이 낫다** — 학습자가 위반과 사고 사이의 간격을 셀 수 있어야 인과가 보이기 때문이다. 다만 코드 추가를 최소화하려면 전제조건 방식으로 시작해서, 사고 카드에 아주 높은 `weight`를 주어 사실상 즉시 뽑히게 하는 절충도 가능하다.

**교육적 근거.** Butler·Karpicke·Roediger (2007, DOI `10.1037/1076-898X.13.4.273`)에서 지연 피드백이 즉시 피드백보다 최종 성적이 좋았고, 피드백의 **종류**는 차이가 없었다. 즉 사고 카드를 화려하게 연출하는 것보다 **지연 자체를 확실히 발동시키는 것**이 효과의 원천이다. 지금처럼 45% 굴림 + 죽은 씨앗 30종이면 이 장치가 절반도 작동하지 않는다.

**단, 전면 지연은 하지 말 것.** Kulik & Kulik (1988, DOI `10.3102/00346543058001079`) 메타분석은 실험실 과제에서는 지연이 유리했지만 **실제 교실 퀴즈·실무 자료에서는 즉시 피드백이 유리한 경우가 많았다**고 보고한다. 하이브리드가 맞다 — **조문 원문과 수치 기준(`#sStd`/`#sLaw`)은 선택 직후 즉시 노출하고(현재 그렇게 되어 있다, 유지), "왜 그게 위험했나"의 체감만 사고 카드로 지연**시킨다.

**비용.** 없음. 순수 로직.

### 권고 3 — 별도 Node 시뮬레이터로 40장 덱을 검증한다 (출처: ReignsAgent reviewer, MIT)

**현재 문제.** 40장 규정 카드 × 각 2선택 + 10장 사고 + 4장 현장 + 5일 보고가 4게이지를 어떻게 흔드는지, 저자가 확인할 방법이 손으로 플레이하는 것뿐이다. "안전만 챙기면 예산이 며칠에 바닥나는가", "40장 중 실제로 60일 안에 뜨는 건 몇 장인가"를 아무도 모른다.

**가져올 것.** `packages/reviewer/src/index.js`의 리포트 구조를 그대로 베낀다. 실제 경고 코드(소스에서 확인):

| 경고 코드 | 이 프로젝트에서의 의미 |
|---|---|
| `never_visited_cards` | 60일 안에 한 번도 안 뜨는 규정 카드. 40장 넣어 놓고 25장만 보이면 교재로서 실패다. |
| `low_card_cycle_coverage` | 등장률이 임계(기본 5%) 미만인 카드. |
| `unreachable_cards` | 요구조건이 어떤 선택으로도 충족될 수 없는 카드 = 데드 카드. 권고 1 도입 후 필수 검사. |
| `stalled_cycles` | 뽑을 수 있는 카드가 0이 되어 멈춘 판. |
| `high_game_over_rate` | 무작위 플레이 기준 게임오버율(기본 임계 0.8). |
| `dominant_game_over_faction` | 특정 게이지가 사망 원인의 45%를 넘음. **"항상 예산으로만 죽는다"면 나머지 세 게이지는 장식이다.** |
| `unsatisfied_required_tags/variables/factions` | 아무도 만들어 주지 않는 태그를 요구하는 카드. |

`summary`에는 `averageTurns`, `turnPercentiles{p10,p50,p90}`, `gameOverByFaction`, `factionAverages`가 들어간다. 시드는 `config.seed + cycle`로 사이클마다 결정, PRNG는 mulberry32 8줄(`createSeededRng`).

**구현 형태 — 무의존을 안 깨는 방법.** ReignsAgent의 `stitchPlayerRuntime` 패턴을 뒤집어 쓴다.

1. `reigns.html` 안에 `/* DECK_START */ ... /* DECK_END */`, `/* CORE_START */ ... /* CORE_END */` 마커를 넣는다.
2. 저장소에 `tools/sim.mjs`(Node 전용, 배포물 아님)를 두고, 마커 사이를 잘라 `new Function`으로 평가한 뒤 몬테카를로를 돌린다.
3. **배포되는 `reigns.html`은 한 글자도 안 변한다.** 빌드 스텝도 없다 — `node tools/sim.mjs`를 저자가 손으로 돌린다.

**비용.** GitHub Pages 배포물에는 영향 0. 저장소에 Node 스크립트 1개가 추가되고, `reigns.html`에 주석 마커 4줄이 들어간다. `Math.random()` 직접 호출을 주입 가능한 `rng` 함수로 바꾸는 리팩터가 필요하다(호출부 4곳: 사고 발화, 씨앗 선택, FLAVOR 추첨, DECK 추첨) — 이건 권고 2를 하면 2곳으로 준다.

### 권고에 딸린 저비용 수선 (구조 변경 없음)

조사 중 현재 파일에서 확인된 접근성 공백. 셋 다 수십 줄이면 끝나고 무의존을 안 깬다.

| 항목 | 현재 상태 | 고칠 것 |
|---|---|---|
| `aria-live` | **0곳.** 카드가 바뀌어도, 게이지가 움직여도, `#sheet`가 열려도 스크린리더에 아무 말이 안 간다. | Swiper `a11y.ts`(MIT) 또는 pragmatic-dnd `live-region`(Apache-2.0) 방식으로 `role="status" aria-live="polite" aria-atomic="true"` 영역 하나. `choose()` 끝에 "기준 미달. 안전 -13, 공정 +7. 12일차."를 `setTimeout(..., 0)`으로 지연 announce. |
| 카드 시맨틱 | `#card`에 `role`도 `tabindex`도 없다. 키보드 사용자는 카드에 포커스를 못 준다. 화살표키는 `window` 전역 리스너라 다른 요소에 포커스가 있어도 발동한다. | dnd-kit 기본값대로 `role="group"` + `aria-roledescription="결정 카드"` + `tabindex="0"`. 화살표 리스너를 카드/`#board` 스코프로 좁힌다. |
| 포커스 이동 | `#sheet`가 열려도 포커스가 안 옮겨간다. `#sGo`를 누르려면 Tab을 여러 번 밟아야 하고, `next()`가 카드 DOM을 갈아엎을 때 포커스 위치가 정의되지 않는다. | react-beautiful-dnd `docs/guides/browser-focus.md`의 규칙 — DOM에서 요소를 지우기 **전에** 포커스를 다음 대상으로 옮긴다. `#sheet` 열릴 때 `#sGo.focus()`, 닫힐 때 카드로 복귀. |

`prefers-reduced-motion`은 30번째 줄에 이미 전역 처리되어 있다(WCAG 2.3.3 충족). `setPointerCapture`/`pointercancel`도 이미 옳게 쓰고 있다. 좌/우 버튼(`#chL`/`#chR`)이 있어 WCAG 2.5.7도 이미 충족 — **이건 지우지 말 것.**

덧붙여, `reigns.html`에는 `localStorage` 호출이 **0곳**이다. 판을 닫으면 60일치 기록이 전부 사라지고, "놓친 규정" 목록도 그 판 안에서만 산다. 형제 페이지 `memo.html`은 `safety_theme` 키 하나만 쓰므로 `safety_*` 네임스페이스 관행만 이미 서 있는 셈이다.

제스처 판정만 한 군데 손볼 값이 있다. 현재는 `Math.abs(dx) > 92` 거리 단일 조건이라, 짧고 빠른 플릭은 무시되고 느린 긴 드래그는 무조건 확정된다. embla `DragTracker`의 이중 조건(거리 OR 속도)으로 바꾸면 모바일에서 체감이 크게 달라진다. 20줄이면 된다.

### 다음 단계 후보 — 권고 아님 (간격 반복)

권고 3까지 끝난 뒤에 검토할 것. 지금 넣으면 범위가 커진다.

카드가 판마다 초기화되므로 "틀린 규정을 다시 만나는" 일이 판 안에서만 일어난다. Cepeda 외 (2006, DOI `10.1037/0033-2909.132.3.354`)의 결론(최적 간격은 목표 파지 기간에 비례)을 쓰려면 판을 넘어가는 저장이 필요하다. 재료는 다 있다 — `open-spaced-repetition/fsrs.js`(★181, MIT, 순수 JS 단일 구현)에서 코드 골격을, `ts-fsrs`(★774, MIT, 2026-09 활동)에서 최신 파라미터와 갱신식을 가져와 50줄로 축약하면 된다. 둘 다 MIT라 라이선스 리스크는 0이고, 무의존도 안 깨진다.

다만 이걸 하려면 `localStorage`에 카드별 안정도/난이도를 쌓아야 하고, 그 순간 "가볍게 한 판" 성격이 "진도 관리 도구"로 바뀐다. 형제 페이지 `memo.html`(암기 은행)이 이미 그 역할에 더 가까우므로, **SRS는 reigns.html이 아니라 memo.html 쪽에 붙이는 게 맞을 수 있다.** 판단 보류.

---

## ④ 하지 말 것

| 검토한 것 | 안 되는 이유 |
|---|---|
| **ReignsAgent 전체 스택 도입** | Node 22+, Vite/React, Electron, 워크스페이스 서버까지 딸린 모노레포다. 단일 HTML·무빌드·오프라인 원칙과 정면충돌한다. **`packages/core`와 `packages/reviewer` 두 파일의 로직만 발췌**하는 게 맞다. MIT라 발췌는 자유(고지 유지). |
| **inkjs / Yarn Spinner로 서사 엔진 교체** | 둘 다 MIT라 라이선스는 문제없지만, inkjs는 런타임 수백 KB + `.ink` 컴파일 스텝이 붙는다. 무의존·무빌드가 깨지고, 얻는 건 지금 40장 카드에 필요 없는 표현력이다. |
| **boardgame.io 채택** | ★12k MIT의 좋은 라이브러리지만 React/서버 전제의 턴제 프레임워크다. 여기서 필요한 건 `alea` 시드 PRNG 8줄과 "봇으로 밸런스 검증" 발상뿐이고, 그건 mulberry32로 이미 해결된다. |
| **`klembot/twinejs`(GPL-3.0) 코드 차용** | GPL-3.0. 코드를 가져오면 reigns.html 전체가 GPL 전염된다. **아이디어 참고만 가능.** |
| **`sboigelot/TwentyCardsToTheApocalypse`(GPL-3.0) 코드 차용** | 같은 이유로 코드 차용 금지. 게다가 2017년 이후 방치, C#/Unity. |
| **`oselcuk/eas-reigns` 코드 차용** | **LICENSE 파일 없음 = 저작권 전면 유보.** GitHub 공개는 열람 허가일 뿐 복제 허가가 아니다. |
| **`outfrost/deckswipe`를 GitHub에서 클론** | GitHub 저장소는 2025-09에 README만 남긴 리다이렉트 껍데기가 됐다. 소스는 Codeberg에 있고 Codeberg는 AI 스크레이퍼에 의도적으로 쓰레기 응답을 준다. **포크 `meltar95/deckswipe`에서 원본과 MIT LICENSE를 확인했으니, 알고리즘 참조는 거기서 하되 출처는 원저자(Iwo 'Outfrost' Bujkiewicz)로 표기할 것.** 또한 Unity/C#이라 코드 자체는 못 쓰고 알고리즘만 이식 대상이다. |
| **"카드게임 밸런싱 도구" 기성품 도입** | `gh search repos`로 네 가지 질의를 돌린 결과 ★0~8의 개인 습작뿐이었다. 이 분야에 쓸 만한 범용 오픈소스는 사실상 없다. ReignsAgent Reviewer를 베끼는 게 정답이다. |
| **js13kGames 출품작 코드 차용** | 조직은 실재하나 개별 저장소가 GPL-3.0·무라이선스·MIT로 뒤섞여 있고 대부분 ★0~2다. 13KB 제약 하의 압축 기법을 개념적으로 볼 수는 있어도, 특정 저장소를 코드 출처로 삼지 말 것. |
| **`hundredrabbits/Left`** | 무빌드·무의존 철학은 훌륭하지만 라이선스가 GitHub API 기준 `NOASSERTION`(표준 SPDX 미판정)이다. 차용 전 LICENSE 원문 확인이 필요하므로 권고 목록에서 제외. |
| **`elzahaby/swipeableCards`(★12, GPL-3.0)** | 단일 HTML 파일에 복붙하면 전염성 라이선스가 파일 전체에 걸린다. 회피. |
| **`Popmotion/popmotion`(★20,163), `valnub/tindercardsjs`(★14)** | 둘 다 `license: null` — **라이선스 없음.** 코드 차용 불가로 간주. |
| **`hammerjs/hammer.js`(★24,343, MIT)** | 라이선스는 문제없지만 사실상 유지보수 정체 상태이고, 필요한 건 제스처 판정 20줄이다. 라이브러리 통째 도입은 무의존 원칙만 깎아먹는다. |
| **`apeatling/javascript-swipe-cards`(★34, MIT)** | 2019년 이후 방치, Hammer.js 1.1.3 의존. 덱 스택 transform/scale 연출만 눈으로 참고. |
| **`OWASP/cornucopia`(CC-BY-SA-4.0) 카드 텍스트 차용** | ShareAlike copyleft. 카드 문구를 가져오면 파생물도 SA로 배포해야 한다. **덱 빌드 구조만 참고, 텍스트는 자체 작성.** |
| **`ankitects/anki`(★30,322) 코드 차용** | GitHub SPDX `NOASSERTION`, 실질 AGPL 계열. **코드는 건드리지 말 것.** 카드 상태 머신(new/learning/review/relearning) 개념만 참고. |
| **`hwgilbert16/scholarsome`(★788, AGPL-3.0), `h16nning/skola`(★52, AGPL-3.0)** | AGPL. 단일 HTML 배포물에 넣으면 전체가 AGPL. 회피. |
| **`open-spaced-repetition/srs-benchmark`(★260)** | **라이선스 없음.** 벤치마크 결과 수치만 읽는 용도. |
| **`finalchild/law-mcp`(★31)** | **라이선스 없음.** 법제처 API 엔드포인트·파라미터 조합만 눈으로 참고. 코드는 `seo-jinseok/korean-law-mcp`(MIT)를 볼 것. |
| **`adamshostack/eop`(★360) 카드 텍스트 차용** | GitHub SPDX `null`, README에 원 MS 배포 기준 CC-BY-3.0 US. 구조는 참고하되 텍스트 차용 전 원 고지 확인 필요. |
| **`atlassian/pragmatic-drag-and-drop` / `gajus/swing` 코드 복붙** | 둘 다 GitHub API가 SPDX를 `NOASSERTION`으로 반환한다(각각 LICENSE 원문은 Apache-2.0, BSD-3-Clause 형태로 확인됨). 알고리즘 이식은 문제없을 가능성이 높지만, **복사 전에 해당 파일 헤더의 저작권 고지를 직접 확인하고 유지할 것.** |
