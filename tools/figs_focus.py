# -*- coding: utf-8 -*-
"""빈출 지도에 붙는 그림.

말로만 적힌 주제 가운데 **그림이라야 잡히는 것**이 있다. 「기계설비의 위험점」이
그렇다 — 여섯 가지가 「무엇과 무엇 사이인가」로 갈리는데, 그 「사이」는 글로
읽어서는 안 그려진다.

    주제 이름 → SVG 조각

`build_focus.py` 가 해설 앞에 끼워 넣는다. 여기 없는 주제는 그림 없이 간다.

## 그리는 규칙

  · viewBox 는 모두 `0 0 120 92`. 같은 크기라야 여섯이 나란히 섰을 때 읽힌다.
  · 기계 부품은 `--line`(테두리)과 `--panel2`(면). 데이터가 아니라 무대다.
  · **위험점만 `--bad`** 로 칠한다. 한 그림에 빨강은 한 군데뿐이다.
  · 회전·왕복 방향은 `--dim` 화살표. 얇게.
  · 글자는 `--muted`, 9px. 그림 안에서는 부품 이름만 적고 설명은 밖에서 한다.

색은 전부 CSS 변수라 밝은 판에서도 따라 바뀐다.
"""
import math

# 화살표 촉. id 는 문서 전체에서 유일해야 하므로 그림마다 번호를 붙인다.
def defs(n):
    return ('<defs><marker id="fa%d" viewBox="0 0 8 8" refX="6" refY="4"'
            ' markerWidth="5" markerHeight="5" orient="auto">'
            '<path d="M0 0.5 L7 4 L0 7.5 Z" fill="var(--dim)"/></marker></defs>' % n)

# ── 기계설비의 위험점 여섯 ────────────────────────────────────────────
# 각 그림은 「무엇과 무엇 사이」를 눈으로 보여 준다. 빨간 자리가 위험점이다.
HAZARD = {
    "협착점": (
        "왕복 + 고정",
        # 프레스 슬라이드가 내려와 고정 베드와 만난다
        '<rect x="26" y="12" width="68" height="26" rx="2" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.5"/>'
        '<rect x="26" y="60" width="68" height="20" rx="2" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.5"/>'
        '<path d="M60 42 V56" stroke="var(--dim)" stroke-width="1.5"'
        ' marker-end="url(#fa)"/>'
        '<rect x="26" y="45" width="68" height="10" fill="var(--bad)" opacity=".22"/>'
        '<path d="M26 50 H94" stroke="var(--bad)" stroke-width="2"/>'
        '<text x="60" y="8" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '슬라이드(왕복)</text>'
        '<text x="60" y="90" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '베드(고정)</text>'
    ),
    "끼임점": (
        "회전 + 고정",
        # 도는 숫돌과 고정된 작업대 사이
        '<circle cx="44" cy="46" r="26" fill="var(--panel2)" stroke="var(--line)"'
        ' stroke-width="1.5"/>'
        '<path d="M44 26 A20 20 0 0 1 61 40" fill="none" stroke="var(--dim)"'
        ' stroke-width="1.5" marker-end="url(#fa)"/>'
        '<rect x="78" y="40" width="30" height="30" rx="2" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.5"/>'
        '<rect x="70" y="40" width="9" height="14" fill="var(--bad)" opacity=".22"/>'
        '<path d="M74 38 V56" stroke="var(--bad)" stroke-width="2"/>'
        '<text x="44" y="86" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '숫돌(회전)</text>'
        '<text x="93" y="86" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '작업대</text>'
    ),
    "절단점": (
        "회전체 단독",
        # 짝이 없다 — 날 자체가 위험하다
        '<circle cx="60" cy="44" r="27" fill="var(--panel2)" stroke="var(--line)"'
        ' stroke-width="1.5"/>'
        '<circle cx="60" cy="44" r="5" fill="var(--line)"/>'
        + "".join(
            '<path d="M%.1f %.1f L%.1f %.1f" stroke="var(--bad)" stroke-width="2"'
            ' stroke-linecap="round"/>'
            % (60 + 27 * math.cos(math.radians(a)), 44 + 27 * math.sin(math.radians(a)),
               60 + 33 * math.cos(math.radians(a)), 44 + 33 * math.sin(math.radians(a)))
            for a in range(0, 360, 30))
        + '<path d="M60 11 A33 33 0 0 1 88 27" fill="none" stroke="var(--dim)"'
        ' stroke-width="1.5" marker-end="url(#fa)"/>'
        '<text x="60" y="88" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '커터·톱날 — 짝이 없다</text>'
    ),
    "물림점": (
        "회전 + 회전",
        # 두 롤러가 서로 반대로 돌며 맞물린다
        '<circle cx="38" cy="42" r="24" fill="var(--panel2)" stroke="var(--line)"'
        ' stroke-width="1.5"/>'
        '<circle cx="86" cy="42" r="24" fill="var(--panel2)" stroke="var(--line)"'
        ' stroke-width="1.5"/>'
        '<path d="M38 24 A18 18 0 0 1 53 35" fill="none" stroke="var(--dim)"'
        ' stroke-width="1.5" marker-end="url(#fa)"/>'
        '<path d="M86 24 A18 18 0 0 0 71 35" fill="none" stroke="var(--dim)"'
        ' stroke-width="1.5" marker-end="url(#fa)"/>'
        '<ellipse cx="62" cy="42" rx="7" ry="12" fill="var(--bad)" opacity=".22"/>'
        '<path d="M62 28 V56" stroke="var(--bad)" stroke-width="2"/>'
        '<text x="62" y="86" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '롤러기·기어 — 맞물리는 자리</text>'
    ),
    "접선물림점": (
        "회전체의 접선",
        # 풀리에 벨트가 접선으로 들어간다
        '<circle cx="40" cy="46" r="24" fill="var(--panel2)" stroke="var(--line)"'
        ' stroke-width="1.5"/>'
        '<circle cx="40" cy="46" r="4" fill="var(--line)"/>'
        '<path d="M40 22 H112" stroke="var(--line)" stroke-width="3" fill="none"/>'
        '<path d="M40 70 H112" stroke="var(--line)" stroke-width="3" fill="none"/>'
        '<path d="M40 26 A20 20 0 0 1 56 36" fill="none" stroke="var(--dim)"'
        ' stroke-width="1.5" marker-end="url(#fa)"/>'
        '<circle cx="62" cy="22" r="9" fill="var(--bad)" opacity=".22"/>'
        '<path d="M53 22 H71" stroke="var(--bad)" stroke-width="2"/>'
        '<text x="60" y="88" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '벨트와 풀리 · 체인과 스프로킷</text>'
    ),
    "회전말림점": (
        "돌출된 회전부",
        # 축이 돌면서 소매·장갑을 감아 들인다
        '<rect x="18" y="34" width="84" height="20" rx="10" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.5"/>'
        '<rect x="62" y="28" width="12" height="32" rx="2" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.5"/>'
        '<path d="M30 30 A14 14 0 0 1 46 30" fill="none" stroke="var(--dim)"'
        ' stroke-width="1.5" marker-end="url(#fa)"/>'
        '<path d="M68 60 q8 10 -4 16 q-12 6 -4 14" fill="none" stroke="var(--bad)"'
        ' stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="68" cy="44" r="10" fill="var(--bad)" opacity=".22"/>'
        '<text x="60" y="88" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '축 · 커플링 — 감겨 들어간다</text>'
    ),
}


def hazard_points():
    """「기계설비의 위험점」 한 장. 여섯을 나란히 놓는다."""
    cells = []
    for i, (name, (rel, art)) in enumerate(HAZARD.items()):
        cells.append(
            '<figure class="hz"><svg viewBox="0 0 120 92" role="img" aria-label="%s — %s">'
            '%s%s</svg><figcaption><b>%s</b><span>%s</span></figcaption></figure>'
            % (name, rel, defs(i), art.replace("url(#fa)", "url(#fa%d)" % i), name, rel))
    return ('<div class="figset" aria-label="기계설비의 위험점 여섯 가지">'
            + "".join(cells) + "</div>")


def defs2(tag):
    """치수선용 — 양쪽에 촉이 붙는다. 색은 선에서 물려받는다(currentColor).

    id 는 문서 전체에서 유일해야 하므로 그림마다 다른 꼬리를 받는다.
    """
    return ('<defs>'
            '<marker id="dE%s" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="5"'
            ' markerHeight="5" orient="auto"><path d="M0 0.5 L7 4 L0 7.5 Z"'
            ' fill="currentColor"/></marker>'
            '<marker id="dS%s" viewBox="0 0 8 8" refX="2" refY="4" markerWidth="5"'
            ' markerHeight="5" orient="auto"><path d="M8 0.5 L1 4 L8 7.5 Z"'
            ' fill="currentColor"/></marker></defs>') % (tag, tag)


def numset(rows):
    """숫자 몇 개를 나란히. 표를 다시 그리는 게 아니라 눈에 박히게 하는 것이다."""
    return '<div class="numset">' + "".join(
        '<div class="nb"><b>%s</b><i>%s</i>%s</div>'
        % (a, b, ('<em>%s</em>' % c) if c else "") for a, b, c in rows) + '</div>'


# ── 지게차의 안정도 ───────────────────────────────────────────────────
# 안정도 = 수직높이 ÷ 수평거리 × 100. 「비」라는 말보다 빗변 하나가 빠르다.
def forklift_stability():
    art = (
        '<path d="M14 74 H106" stroke="var(--line)" stroke-width="1.5"/>'
        '<path d="M18 74 L100 74 L100 42 Z" fill="var(--panel2)" opacity=".55"/>'
        '<path d="M18 74 L100 42" fill="none" stroke="var(--line)" stroke-width="1.8"/>'
        '<rect x="55" y="45" width="19" height="10" rx="1.5" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.3" transform="rotate(-21 64 50)"/>'
        '<path d="M73 50 V37" stroke="var(--line)" stroke-width="1.6"'
        ' transform="rotate(-21 64 50)"/>'
        '<g color="var(--bad)"><path d="M100 42 V74" stroke="currentColor"'
        ' stroke-width="1.6" marker-start="url(#dSf)" marker-end="url(#dEf)"/></g>'
        '<g color="var(--dim)"><path d="M18 81 H100" stroke="currentColor"'
        ' stroke-width="1.2" marker-start="url(#dSf)" marker-end="url(#dEf)"/></g>'
        '<text x="103" y="60" fill="var(--bad)" font-size="9">수직</text>'
        '<text x="59" y="90" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '수평거리</text>'
        '<text x="60" y="14" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '안정도 = 수직 ÷ 수평 × 100</text>')
    rows = [("하역 — 전후", "4 % 이내", "5 t 이상은 3.5 %"),
            ("하역 — 좌우", "6 % 이내", ""),
            ("주행 — 전후", "18 % 이내", ""),
            ("주행 — 좌우", "(15 + 1.1V) %", "V 는 km/h")]
    return ('<div class="figset one" aria-label="지게차의 안정도">'
            '<figure class="hz"><svg viewBox="0 0 120 92" role="img"'
            ' aria-label="안정도는 수직높이를 수평거리로 나눈 비다">' + defs2('f') + art
            + '</svg><figcaption><b>안정도의 뜻</b><span>수직 ÷ 수평 × 100</span>'
            '</figcaption></figure>' + numset(rows) + '</div>')


# ── 가설통로의 구조 ───────────────────────────────────────────────────
# 숫자 넷이 두 짝이다 — 30/15(경사), 15→10 과 8→7(계단참).
def ramp_spec():
    slope = (
        '<path d="M14 76 H106" stroke="var(--line)" stroke-width="1.5"/>'
        '<path d="M16 76 L100 76 L100 34 Z" fill="var(--panel2)" opacity=".5"/>'
        '<path d="M16 76 L100 34" fill="none" stroke="var(--line)" stroke-width="2.5"/>'
        '<path d="M42 76 A26 26 0 0 0 39 63" fill="none" stroke="var(--bad)"'
        ' stroke-width="1.6"/>'
        '<text x="46" y="71" fill="var(--bad)" font-size="9">30° 이하</text>'
        '<text x="60" y="15" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '15° 넘으면 미끄럼 방지</text>')
    land = (
        '<rect x="22" y="16" width="15" height="58" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.4"/>'
        '<rect x="76" y="16" width="15" height="58" fill="var(--panel2)"'
        ' stroke="var(--line)" stroke-width="1.4"/>'
        '<path d="M18 45 H41" stroke="var(--bad)" stroke-width="2.4"/>'
        '<path d="M72 35 H95" stroke="var(--bad)" stroke-width="2.4"/>'
        '<path d="M72 57 H95" stroke="var(--bad)" stroke-width="2.4"/>'
        '<text x="29" y="12" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '수직갱</text>'
        '<text x="83" y="12" fill="var(--muted)" font-size="9" text-anchor="middle">'
        '비계다리</text>'
        '<text x="29" y="87" fill="var(--dim)" font-size="8" text-anchor="middle">'
        '15 m↑ → 10 m마다</text>'
        '<text x="83" y="87" fill="var(--dim)" font-size="8" text-anchor="middle">'
        '8 m↑ → 7 m마다</text>')
    return ('<div class="figset" aria-label="가설통로의 구조">'
            '<figure class="hz"><svg viewBox="0 0 120 92" role="img"'
            ' aria-label="가설통로 경사는 30도 이하, 15도를 넘으면 미끄럼 방지">'
            + slope + '</svg><figcaption><b>경사</b>'
            '<span>30° 한도 · 15° 미끄럼</span></figcaption></figure>'
            '<figure class="hz"><svg viewBox="0 0 120 92" role="img"'
            ' aria-label="계단참은 수직갱 15미터 이상이면 10미터마다, 비계다리 8미터 이상이면 7미터마다">'
            + land + '</svg><figcaption><b>계단참</b>'
            '<span>15→10 · 8→7</span></figcaption></figure></div>')


# ── 강관비계의 구조 ───────────────────────────────────────────────────
def scaffold_spec():
    art = ('<path d="M20 78 H108" stroke="var(--line)" stroke-width="1.5"/>'
           + "".join('<path d="M%d 22 V78" stroke="var(--line)" stroke-width="2.2"/>' % x
                     for x in (30, 64, 98))
           + "".join('<path d="M30 %d H98" stroke="var(--line)" stroke-width="1.4"/>' % y
                     for y in (28, 44, 60, 76))
           + '<g color="var(--bad)"><path d="M30 17 H64" stroke="currentColor"'
             ' stroke-width="1.5" marker-start="url(#dSs)" marker-end="url(#dEs)"/>'
             '<path d="M108 44 V60" stroke="currentColor" stroke-width="1.5"'
             ' marker-start="url(#dSs)" marker-end="url(#dEs)"/></g>'
           + '<text x="47" y="13" fill="var(--bad)" font-size="9" text-anchor="middle">'
             '1.85 m</text>'
           + '<text x="112" y="55" fill="var(--bad)" font-size="9">2.0</text>'
           + '<text x="60" y="90" fill="var(--muted)" font-size="9" text-anchor="middle">'
             '장선 방향은 1.5 m 이하</text>')
    rows = [("띠장 방향 기둥", "1.85 m 이하", ""),
            ("장선 방향 기둥", "1.5 m 이하", ""),
            ("띠장 간격", "2.0 m 이하", ""),
            ("31 m 아래 기둥", "강관 2개로 묶음", "하중이 쌓인다"),
            ("기둥 간 적재하중", "400 kg 이하", "")]
    return ('<div class="figset one" aria-label="강관비계의 구조">'
            '<figure class="hz"><svg viewBox="0 0 120 92" role="img"'
            ' aria-label="강관비계 기둥 간격은 띠장 방향 1.85미터, 띠장 간격은 2.0미터">'
            + defs2('s') + art + '</svg><figcaption><b>강관비계</b>'
            '<span>1.85 · 1.5 · 2.0</span></figcaption></figure>'
            + numset(rows) + '</div>')


# 주제 이름 → 그림. 없는 주제는 그림 없이 간다.
FIGS = {
    "기계설비의 위험점": hazard_points,
    "지게차의 안정도": forklift_stability,
    "가설통로의 구조": ramp_spec,
    "강관비계의 구조": scaffold_spec,
}


def fig_for(mid):
    f = FIGS.get(mid)
    return f() if f else ""
