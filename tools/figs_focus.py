# -*- coding: utf-8 -*-
"""빈출 지도에 붙는 그림.

말로만 적힌 주제 가운데 **그림이라야 잡히는 것**이 있다. 「기계설비의 위험점」이
그렇다 — 여섯 가지가 「무엇과 무엇 사이인가」로 갈리는데, 그 「사이」는 글로
읽어서는 안 그려진다.

    주제 이름 → SVG 조각

`build_focus.py` 가 해설 앞에 끼워 넣는다. 여기 없는 주제는 그림 없이 간다.
지금 29개 주제, 기출의 8.5 %, 상위 50개 중 22개.

## 무엇에 그림을 그리는가

셋 중 하나면 그린다. 아니면 표가 낫다.

  · **자리** — 「기계보다 위인가 아래인가」(굴착기계), 「선반의 어디에 붙는가」
    (방호장치), 「어느 깊이의 흠인가」(비파괴검사).
  · **치수** — 숫자가 길이·각도·비인 것. 75°·40 cm·4배는 글로 읽으면 안 남는다.
  · **까닭** — 「왜 1,600 인가」(손이 1.6 m/s 로 온다), 「왜 하한이 분모인가」
    (띠의 왼쪽 끝이 값을 정한다).

정의를 늘어놓는 표(브레인스토밍 4원칙 같은 것)는 그리지 않는다. 그림이 표를
되풀이할 뿐이다.

## 그리는 규칙

  · viewBox 는 모두 `0 0 120 92`. 같은 크기라야 여섯이 나란히 섰을 때 읽힌다.
  · 기계 부품은 `--line`(테두리)과 `--panel2`(면). 데이터가 아니라 무대다.
  · **갈리는 자리만 `--bad`** 로 칠한다 — 위험점이거나, 답이 되는 치수다.
  · 회전·왕복 방향은 `--dim` 화살표. 얇게.
  · 글자는 `--muted`, 9px. 그림 안에서는 부품 이름만 적고 설명은 밖에서 한다.
  · **숫자는 지어내지 않는다.** 그림에 적는 값은 그 주제의 표에 있는 것뿐이다.

색은 전부 CSS 변수라 밝은 판에서도 따라 바뀐다. 딱 하나 예외가 「화재의 분류」다
— 거기서는 표시색(백·황·청)이 곧 답이라 실제 색을 쓴다.

## 두 가지 함정

  · **글자는 viewBox 밖으로 흐른다.** 좌표가 안에 있어도 잘린다.
    `figcheck.py` 가 폭을 어림해 잡는다.
  · **id 는 문서 전체에서 유일해야 한다.** 한 주제 이름이 과목 둘에 걸리면
    같은 그림이 두 번 찍힌다. 그래서 최종 번호는 `build_focus.uniq_ids` 가
    찍히는 자리에서 붙인다.
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
        '롤러기 · 기어</text>'
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
        '<text x="60" y="88" fill="var(--muted)" font-size="8" text-anchor="middle">'
        '벨트·풀리 · 체인·스프로킷</text>'
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
        '<text x="30" y="87" fill="var(--dim)" font-size="7.5" text-anchor="middle">'
        '15↑ → 10마다</text>'
        '<text x="84" y="87" fill="var(--dim)" font-size="7.5" text-anchor="middle">'
        '8↑ → 7마다</text>')
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


# ── 여기서부터 배치 2. 뼈대를 먼저 두고 그림을 얹는다 ────────────────
def fig1(label, alt, art, cap_, sub, rows=None, tag=None):
    """그림 하나(+숫자 몇 줄). tag 를 주면 치수선 촉을 함께 깐다."""
    body = ('<figure class="hz"><svg viewBox="0 0 120 92" role="img" aria-label="%s">'
            '%s%s</svg><figcaption><b>%s</b><span>%s</span></figcaption></figure>'
            % (alt, defs2(tag) if tag else "", art, cap_, sub))
    cls = "figset one" if rows else "figset solo"
    return ('<div class="%s" aria-label="%s">%s%s</div>'
            % (cls, label, body, numset(rows) if rows else ""))


def figs(label, cells, rows=None, tag=None):
    """그림 여럿을 나란히. cells = [(제목, 부제, alt, 그림)]

    치수선 촉은 첫 그림에만 깔고 나머지가 같은 id 를 쓴다 — 한 문서 안이니
    닿고, 그림마다 defs 를 되풀이하면 id 가 중복된다.
    """
    h = ""
    for j, (c, sub, alt, art) in enumerate(cells):
        d = ""
        if tag:
            # <svg> 를 건너뛴 url(#id) 참조는 기대지 않는다. 그림마다 제 촉을 깔고
            # id 에 번호를 붙여 문서 안에서 겹치지 않게 한다.
            d = defs2("%s%d" % (tag, j))
            art = art.replace("#dS" + tag, "#dS%s%d" % (tag, j))                      .replace("#dE" + tag, "#dE%s%d" % (tag, j))
        h += ('<figure class="hz"><svg viewBox="0 0 120 92" role="img" aria-label="%s">'
              '%s%s</svg><figcaption><b>%s</b><span>%s</span></figcaption></figure>'
              % (alt, d, art, c, sub))
    return ('<div class="figset" aria-label="%s">%s%s</div>'
            % (label, h, numset(rows) if rows else ""))


def dim(x1, y1, x2, y2, tag, color="var(--bad)", w=1.4):
    """양끝에 촉이 붙는 치수선."""
    return ('<g color="%s"><path d="M%s %s L%s %s" stroke="currentColor"'
            ' stroke-width="%s" marker-start="url(#dS%s)" marker-end="url(#dE%s)"/></g>'
            % (color, x1, y1, x2, y2, w, tag, tag))


def cap(x, y, t, fill="var(--muted)", size=9, anchor="middle"):
    return ('<text x="%s" y="%s" fill="%s" font-size="%s" text-anchor="%s">%s</text>'
            % (x, y, fill, size, anchor, t))


def box(x, y, w, h, r=1.5, fill="var(--panel2)", sw=1.4):
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"'
            ' stroke="var(--line)" stroke-width="%s"/>' % (x, y, w, h, r, fill, sw))


def ground(y=80, x1=10, x2=110):
    return ('<path d="M%s %s H%s" stroke="var(--line)" stroke-width="1.6"/>'
            % (x1, y, x2))


# ── 방망사의 인장강도 ─────────────────────────────────────────────────
# 두 가지가 값을 가른다 — 그물코 크기와 매듭 유무. 둘을 따로 보여 준다.
def net_strength():
    def mesh(step, knot):
        xs = list(range(18, 103, step))
        ys = list(range(16, 71, step))
        a = "".join('<path d="M%d 16 V70" stroke="var(--line)" stroke-width="1.2"/>' % x
                    for x in xs)
        a += "".join('<path d="M18 %d H102" stroke="var(--line)" stroke-width="1.2"/>' % y
                     for y in ys)
        if knot:
            a += "".join('<circle cx="%d" cy="%d" r="2.1" fill="var(--bad)"/>' % (x, y)
                         for x in xs for y in ys)
        a += dim(xs[0], 78, xs[1], 78, "n")
        a += cap((xs[0] + xs[1]) / 2.0, 90, "그물코", "var(--bad)", 8.5)
        return a
    return figs(
        "방망사의 인장강도",
        [("매듭 없는 방망", "10 cm · 신품 240",
          "그물코 10센티미터 매듭 없는 방망은 신품 240킬로그램", mesh(21, False)),
         ("매듭 방망", "10 cm · 신품 200",
          "그물코 10센티미터 매듭 방망은 신품 200킬로그램", mesh(21, True)),
         ("매듭 방망", "5 cm · 신품 110",
          "그물코 5센티미터 매듭 방망은 신품 110킬로그램", mesh(12, True))],
        [("10 cm 매듭 없음", "240 / 150", "신품 / 폐기 시"),
         ("10 cm 매듭", "200 / 135", ""),
         ("5 cm 매듭", "110 / 60", "그물코가 작을수록 낮다"),
         ("처짐 · 수직거리", "12 % 이상 · 10 m 이내", "내민 길이는 벽에서 3 m 이상")],
        tag="n")


# ── 선반의 방호장치 ───────────────────────────────────────────────────
# 넷이 「선반의 어디에 붙는가」로 갈린다. 같은 선반 위에 하나씩 켠다.
LATHE = (box(10, 62, 100, 12, 2)
         + box(10, 32, 26, 30, 2)
         + '<circle cx="42" cy="47" r="9" fill="var(--panel2)" stroke="var(--line)"'
           ' stroke-width="1.4"/>'
         + box(50, 43, 40, 8, 1)
         + box(92, 38, 16, 24, 2)
         + box(66, 51, 6, 11, 1))


def lathe_guards():
    return figs(
        "선반의 방호장치",
        [("쉴드", "칩 · 절삭유 튐",
          "쉴드는 칩과 절삭유가 튀는 것을 막는 투명판",
          LATHE
          + '<rect x="46" y="14" width="56" height="22" rx="2" fill="var(--bad)"'
            ' opacity=".16" stroke="var(--bad)" stroke-width="1.6"/>'
          + '<path d="M70 41 L58 32 M74 41 L88 33" stroke="var(--dim)"'
            ' stroke-width="1.2"/>'
          + cap(74, 11, "투명 가림막", "var(--bad)", 8.5)),
         ("척 커버", "회전부 접촉",
          "척 커버는 척과 공작물의 회전부에 닿는 것을 막는 덮개",
          LATHE
          + '<circle cx="42" cy="47" r="13" fill="var(--bad)" opacity=".14"/>'
          + '<path d="M29 47 A13 13 0 0 1 55 47" fill="none" stroke="var(--bad)"'
            ' stroke-width="2.4"/>'
          + cap(42, 26, "척을 덮는다", "var(--bad)", 8.5)),
         ("칩 브레이커", "길게 이어지는 칩",
          "칩 브레이커는 바이트에 홈이나 턱을 두어 칩을 짧게 끊는다",
          LATHE
          + '<circle cx="69" cy="50" r="6" fill="var(--bad)" opacity=".2"/>'
          + '<path d="M72 46 q9 -6 3 -12 q-6 -6 4 -10" fill="none" stroke="var(--bad)"'
            ' stroke-width="1.8" stroke-linecap="round"/>'
          + cap(88, 14, "칩을 끊는다", "var(--bad)", 8.5)),
         ("브레이크", "관성 회전",
          "브레이크는 스위치를 끈 뒤 남는 관성 회전을 급정지시킨다",
          LATHE
          + '<circle cx="23" cy="47" r="11" fill="var(--bad)" opacity=".18"/>'
          + '<path d="M17 41 L29 53 M29 41 L17 53" stroke="var(--bad)"'
            ' stroke-width="2.4" stroke-linecap="round"/>'
          + cap(23, 26, "급정지", "var(--bad)", 8.5))],
        [("쉴드", "칩 · 절삭유 튐", "투명판"),
         ("척 커버", "척과 공작물 회전부", "덮개"),
         ("칩 브레이커", "길게 이어지는 칩", "바이트의 홈 · 턱"),
         ("브레이크", "관성 회전", "급정지"),
         ("방진구", "가늘고 긴 공작물", "받쳐 준다")])


# ── 달비계의 안전계수 ─────────────────────────────────────────────────
# 「사람이 매달리는 줄일수록 크다」가 그림의 말이다. 양 끝값만 켠다.
def suspended_factor():
    art = (box(10, 8, 100, 8, 1)
           + '<path d="M30 16 V52" stroke="var(--bad)" stroke-width="2.6"/>'
           + '<path d="M90 16 V52" stroke="var(--bad)" stroke-width="2.6"/>'
           + cap(24, 36, "10", "var(--bad)", 11, "end")
           + cap(96, 36, "10", "var(--bad)", 11, "start")
           + box(22, 52, 76, 9, 1.5)
           + '<path d="M26 61 L38 76 M94 61 L82 76" stroke="var(--line)"'
             ' stroke-width="1.6"/>'
           + '<circle cx="60" cy="76" r="8" fill="var(--bad)" opacity=".18"/>'
           + '<path d="M38 76 H82" stroke="var(--bad)" stroke-width="2.4"/>'
           + cap(60, 90, "2.5 — 강대(강재)", "var(--bad)", 9)
           + cap(60, 30, "달기 와이어로프 · 강선", "var(--muted)", 8.5)
           + cap(60, 49, "작업발판", "var(--muted)", 8.5))
    return fig1("달비계의 안전계수",
                "달기 와이어로프는 안전계수 10, 달기 강대는 강재 2.5로 가장 작다",
                art, "매달린 줄이 가장 크다", "10 · 5 · 2.5 · 5",
                [("달기 와이어로프 · 강선", "10 이상", "가장 크다"),
                 ("달기 체인 · 달기 훅", "5 이상", ""),
                 ("달기 강대와 지점 — 강재", "2.5 이상", "가장 작다"),
                 ("달기 강대와 지점 — 목재", "5 이상", "")])


# ── 작업발판의 구조 ───────────────────────────────────────────────────
def platform_spec():
    art = (box(12, 44, 8, 34, 1) + box(101, 44, 8, 34, 1)
           + "".join(box(x, 38, 25, 10, 1) for x in (20, 48, 76))
           + '<rect x="45" y="38" width="3" height="10" fill="var(--bad)"/>'
           + '<rect x="73" y="38" width="3" height="10" fill="var(--bad)"/>'
           + dim(20, 30, 101, 30, "w")
           + cap(60, 26, "40 cm 이상", "var(--bad)", 9)
           + cap(60, 62, "지지물 2개 이상", "var(--muted)", 8.5)
           + cap(60, 90, "발판재료 간 틈 3 cm 이하", "var(--bad)", 9))
    return fig1("작업발판의 구조",
                "작업발판의 폭은 40센티미터 이상, 발판재료 간 틈은 3센티미터 이하",
                art, "폭 40 · 틈 3", "달비계만 20",
                [("작업발판의 폭", "40 cm 이상", "달비계는 20 cm 이상"),
                 ("발판재료 간 틈", "3 cm 이하", "달비계는 틈이 없도록"),
                 ("지지물 연결", "2개 이상", "뒤집힘 방지"),
                 ("추락 위험 장소", "안전난간", "")],
                tag="w")


# ── 양수기동식 방호장치의 안전거리 ────────────────────────────────────
# 「왜 1,600 인가」가 그림의 말이다 — 손이 오는 속도만큼 버튼을 물린다.
def press_distance():
    art = (box(8, 12, 42, 62, 2)
           + '<rect x="12" y="34" width="34" height="10" fill="var(--bad)"'
             ' opacity=".22"/>'
           + '<path d="M12 39 H46" stroke="var(--bad)" stroke-width="2.2"/>'
           + cap(29, 30, "위험한계", "var(--bad)", 8.5)
           + '<circle cx="88" cy="46" r="7" fill="var(--panel2)" stroke="var(--line)"'
             ' stroke-width="1.6"/>'
           + '<circle cx="106" cy="46" r="7" fill="var(--panel2)" stroke="var(--line)"'
             ' stroke-width="1.6"/>'
           + cap(97, 32, "두 손 버튼", "var(--muted)", 8.5)
           + dim(46, 66, 88, 66, "p")
           + cap(67, 62, "D", "var(--bad)", 11)
           + cap(60, 88, "손은 1.6 m/s 로 온다", "var(--muted)", 8.5))
    return fig1("양수기동식 방호장치의 안전거리",
                "안전거리는 손의 접근속도 1.6미터퍼초에 도달시간을 곱한 값",
                art, "1,600 × 시간", "답은 mm",
                [("양수기동식", "D = 1,600 T", "T 는 하사점 도달시간"),
                 ("양수조작식 · 광전자식", "D = 1,600 (T₁ + T₂)", "급정지시간"),
                 ("손쳐내기식", "D = 0.5 × 행정길이", ""),
                 ("T 를 SPM 으로", "(1/개소수 + 1/2) × 60,000 / SPM", "단위는 ms")],
                tag="p")


# ── 이동식 비계 ───────────────────────────────────────────────────────
def rolling_tower():
    art = (ground(80, 8, 112)
           + "".join('<path d="M%d 18 V74" stroke="var(--line)" stroke-width="2.2"/>' % x
                     for x in (40, 80))
           + "".join('<path d="M40 %d H80" stroke="var(--line)" stroke-width="1.4"/>' % y
                     for y in (22, 36, 50, 64))
           + box(34, 14, 52, 6, 1)
           + '<circle cx="42" cy="77" r="3" fill="var(--panel2)" stroke="var(--line)"'
             ' stroke-width="1.3"/>'
           + '<circle cx="78" cy="77" r="3" fill="var(--panel2)" stroke="var(--line)"'
             ' stroke-width="1.3"/>'
           + '<path d="M40 62 L24 78 M80 62 L96 78" stroke="var(--line)"'
             ' stroke-width="1.3"/>'
           + dim(40, 86, 80, 86, "t")
           + dim(94, 18, 94, 74, "t")
           + cap(60, 92, "밑변 최소폭", "var(--bad)", 8.5)
           + cap(112, 48, "4배", "var(--bad)", 9, "end")
           + cap(60, 10, "적재 250 kg 이하", "var(--bad)", 8.5))
    return fig1("이동식 비계",
                "이동식 비계의 최대 높이는 밑변 최소폭의 4배 이하",
                art, "높이 ≤ 밑변 × 4", "적재 250 kg",
                [("최대 높이", "밑변 최소폭의 4배", "밑변 2 m 면 8 m"),
                 ("작업발판 최대 적재하중", "250 kg", "강관비계는 400 kg"),
                 ("바퀴", "브레이크 · 쐐기 + 아웃트리거", ""),
                 ("승탑", "사람이 탄 채 이동 금지", "")],
                tag="t")


# ── 사다리식 통로의 구조 ──────────────────────────────────────────────
def ladder_spec():
    lean = (ground(78, 8, 112)
            + '<path d="M92 6 V78" stroke="var(--line)" stroke-width="2"/>'
            + '<path d="M26 74 L48 14 M40 74 L62 14" stroke="var(--line)"'
              ' stroke-width="2"/>'
            + "".join('<path d="M%.1f %.1f L%.1f %.1f" stroke="var(--line)"'
                      ' stroke-width="1.4"/>'
                      % (26 + i * 4.4, 74 - i * 12.0, 40 + i * 4.4, 74 - i * 12.0)
                      for i in range(1, 5))
            + '<path d="M40 74 A22 22 0 0 0 47 55" fill="none" stroke="var(--bad)"'
              ' stroke-width="1.6"/>'
            + cap(56, 70, "75° 이하", "var(--bad)", 9, "start")
            + '<path d="M55 14 V30" stroke="var(--bad)" stroke-width="2.6"/>'
            + cap(58, 11, "상단 60 이상", "var(--bad)", 8.5, "start")
            + cap(10, 90, "폭 30 cm 이상", "var(--muted)", 8.5, "start"))
    fixed = (ground(78, 8, 112)
             + '<path d="M76 6 V78" stroke="var(--line)" stroke-width="2"/>'
             + '<path d="M44 12 V78 M60 12 V78" stroke="var(--line)" stroke-width="2"/>'
             + "".join('<path d="M44 %d H60" stroke="var(--line)" stroke-width="1.4"/>' % y
                       for y in range(22, 79, 11))
             + dim(60, 40, 76, 40, "l")
             + cap(80, 38, "벽 사이", "var(--muted)", 8.5, "start")
             + cap(80, 49, "15 이상", "var(--bad)", 8.5, "start")
             + '<path d="M60 78 A16 16 0 0 0 60 62" fill="none" stroke="var(--bad)"'
               ' stroke-width="1.6"/>'
             + cap(10, 90, "고정식은 90° 이하", "var(--bad)", 9, "start"))
    return figs("사다리식 통로의 구조",
                [("일반 사다리식", "75° 이하",
                  "일반 사다리식 통로의 기울기는 75도 이하", lean),
                 ("고정식", "90° 이하",
                  "고정식 사다리식 통로의 기울기는 90도까지", fixed)],
                [("폭", "30 cm 이상", "작업발판 40 과 다르다"),
                 ("발판과 벽 사이", "15 cm 이상", "발이 들어갈 틈"),
                 ("상단 돌출", "60 cm 이상", "붙잡을 곳"),
                 ("기울기", "75° 이하", "고정식은 90° 이하"),
                 ("길이 10 m 이상", "5 m 이내마다 계단참", ""),
                 ("고정식 높이 7 m 이상", "등받이울 또는 추락방지 시스템", "")],
                tag="l")


# ── 롤러기 급정지장치 ─────────────────────────────────────────────────
# 조작부는 「몸의 어디로 치는가」로 높이가 갈린다. 사람 옆에 세워야 보인다.
def roller_stop():
    def h(m):
        return round(82 - m * 37.8, 1)
    art = (ground(82, 8, 112)
           + '<circle cx="28" cy="19" r="6" fill="var(--panel2)" stroke="var(--line)"'
             ' stroke-width="1.4"/>'
           + '<path d="M28 25 V56 M28 56 L20 82 M28 56 L36 82 M28 32 L16 46'
             ' M28 32 L42 44" fill="none" stroke="var(--line)" stroke-width="1.6"'
             ' stroke-linecap="round"/>'
           + box(66, 14, 32, 68, 2)
           + "".join('<path d="M62 %s H102" stroke="var(--bad)" stroke-width="2.6"/>'
                     % h(m) for m in (1.8, 0.95, 0.6))
           + cap(104, h(1.8) - 2.5, "1.8 이내", "var(--bad)", 8.5, "end")
           + cap(104, h(0.95) - 2.5, "0.8~1.1", "var(--bad)", 8.5, "end")
           + cap(104, h(0.6) - 2.5, "0.6 이내", "var(--bad)", 8.5, "end")
           + cap(10, 92, "손 · 복부 · 무릎", "var(--muted)", 8.5, "start"))
    return fig1("롤러기 급정지장치",
                "조작부 높이는 손 조작 1.8미터 이내, 복부 0.8에서 1.1미터, 무릎 0.6미터 이내",
                art, "조작부의 높이", "1.8 · 0.8~1.1 · 0.6",
                [("손 조작식", "밑면에서 1.8 m 이내", ""),
                 ("복부 조작식", "0.8 ~ 1.1 m", ""),
                 ("무릎 조작식", "0.6 m 이내", ""),
                 ("조작부 로프", "와이어 4 mm · 섬유 6 mm 이상", ""),
                 ("급정지거리", "30 m/min 미만이면 원주의 1/3", "이상이면 1/2.5")])


# ── 강관비계의 조립간격 ───────────────────────────────────────────────
def tie_spacing():
    def facade(nx, ny, lab):
        xs = [round(18 + i * (84.0 / nx), 1) for i in range(nx + 1)]
        ys = [round(16 + i * (54.0 / ny), 1) for i in range(ny + 1)]
        a = "".join('<path d="M%s 16 V70" stroke="var(--line)" stroke-width="1.3"/>' % x
                    for x in xs)
        a += "".join('<path d="M18 %s H102" stroke="var(--line)" stroke-width="1.3"/>' % y
                     for y in ys)
        a += "".join('<circle cx="%s" cy="%s" r="2.6" fill="var(--bad)"/>' % (x, y)
                     for x in xs for y in ys)
        return a + cap(60, 12, "● 벽이음", "var(--muted)", 8.5) \
                 + cap(60, 84, lab, "var(--bad)", 9)
    return figs("강관비계의 조립간격",
                [("단관비계", "5 · 5",
                  "단관비계의 벽이음은 수직 수평 모두 5미터",
                  facade(3, 3, "수직 5 m · 수평 5 m")),
                 ("틀비계", "6 · 8",
                  "강관틀비계의 벽이음은 수직 6미터 수평 8미터",
                  facade(2, 2, "수직 6 m · 수평 8 m"))],
                [("단관비계", "수직 5 m · 수평 5 m", "둘 다 5"),
                 ("틀비계 (높이 5 m 이상)", "수직 6 m · 수평 8 m", ""),
                 ("벽이음이 하는 일", "넘어짐 · 좌굴을 막는다", "비계 붕괴의 첫째 원인")])


# ── 말비계 ────────────────────────────────────────────────────────────
def horse_scaffold():
    art = (ground(78, 8, 112)
           + box(38, 16, 44, 7, 1)
           + '<path d="M46 23 L28 78 M74 23 L92 78" stroke="var(--line)"'
             ' stroke-width="2.4"/>'
           + '<path d="M34 58 H86" stroke="var(--line)" stroke-width="1.6"/>'
           + cap(60, 54, "보조부재", "var(--muted)", 8.5)
           + '<path d="M28 78 A18 18 0 0 0 34 61" fill="none" stroke="var(--bad)"'
             ' stroke-width="1.6"/>'
           + cap(42, 74, "75° 이하", "var(--bad)", 9, "start")
           + dim(38, 11, 82, 11, "m")
           + cap(60, 8, "40 cm 이상", "var(--bad)", 8.5)
           + '<rect x="23" y="78" width="10" height="3" fill="var(--bad)"/>'
           + '<rect x="87" y="78" width="10" height="3" fill="var(--bad)"/>'
           + cap(60, 90, "밑부분 미끄럼 방지", "var(--muted)", 8.5))
    return fig1("말비계",
                "말비계 지주부재와 수평면의 기울기는 75도 이하, 작업발판 폭은 40센티미터 이상",
                art, "기울기 75 · 폭 40", "가설통로는 30°",
                [("지주부재와 수평면의 기울기", "75° 이하", "사다리식 통로와 같다"),
                 ("75° 이하일 때", "보조부재", "다리가 벌어지지 않게"),
                 ("높이 2 m 초과", "작업발판 폭 40 cm 이상", ""),
                 ("밑부분", "미끄럼 방지장치", "")],
                tag="m")


# ── 계단의 강도 ───────────────────────────────────────────────────────
def stair_spec():
    steps, x, y = "", 20, 74
    for _ in range(5):
        steps += ('<path d="M%d %d H%d V%d" fill="none" stroke="var(--line)"'
                  ' stroke-width="1.8"/>' % (x, y, x + 9, y - 8))
        x, y = x + 9, y - 8
    art = (ground(74, 8, 112)
           + steps
           + box(65, 30, 24, 4, 1)
           + cap(77, 27, "계단참", "var(--bad)", 8.5)
           + '<path d="M89 34 H104 V74" fill="none" stroke="var(--line)"'
             ' stroke-width="1.8"/>'
           + dim(15, 74, 15, 34, "c")
           + cap(12, 56, "3 m", "var(--bad)", 9, "end")
           + '<path d="M20 12 H104" stroke="var(--dim)" stroke-width="1.2"'
             ' stroke-dasharray="3 3"/>'
           + cap(62, 9, "위쪽 2 m 이내 장애물 없게", "var(--muted)", 8.5)
           + cap(60, 90, "매 m² 당 500 kg · 안전율 4", "var(--bad)", 9))
    return fig1("계단의 강도",
                "계단은 매 제곱미터당 500킬로그램 이상, 높이 3미터를 넘으면 3미터 이내마다 계단참",
                art, "500 · 4 · 1 · 3", "400 은 비계 쪽",
                [("강도", "매 m² 당 500 kg 이상", "안전율 4 이상"),
                 ("폭", "1 m 이상", "급유용 · 보수용은 제외"),
                 ("계단참", "높이 3 m 초과 시 3 m 이내마다", "너비 1.2 m 이상"),
                 ("난간", "높이 1 m 이상이면 개방된 쪽", ""),
                 ("위쪽 공간", "2 m 이내 장애물 없게", "")],
                tag="c")


# ── 방호장치의 분류 ───────────────────────────────────────────────────
# 다섯이 「무엇으로 막는가」로 갈린다. 같은 무대에 손과 위험을 놓고 방법만 바꾼다.
def _hand(x, y):
    return ('<g fill="var(--panel2)" stroke="var(--line)" stroke-width="1.4">'
            '<rect x="%d" y="%d" width="16" height="11" rx="5"/>'
            '<rect x="%d" y="%d" width="9" height="7" rx="3"/></g>'
            % (x, y, x + 14, y + 2))


_MACH = (box(78, 28, 30, 34, 2)
         + '<circle cx="93" cy="45" r="9" fill="var(--bad)" opacity=".2"/>'
         + '<path d="M87 39 L99 51 M99 39 L87 51" stroke="var(--bad)"'
           ' stroke-width="2" stroke-linecap="round"/>')


def guard_types():
    return figs(
        "방호장치의 분류",
        [("격리형", "사이를 막는다",
          "격리형은 사람과 위험 사이를 막는다 — 덮개형 게이트 가드식",
          _MACH + _hand(14, 40)
          + '<rect x="58" y="16" width="7" height="60" rx="2" fill="var(--bad)"'
            ' opacity=".7"/>'
          + cap(46, 90, "덮개 · 게이트 가드", "var(--muted)", 8.5)),
         ("위치제한형", "손이 갈 수 없는 자리",
          "위치제한형은 조작부를 손이 닿지 않는 거리에 둔다 — 양수조작식",
          _MACH + _hand(10, 40)
          + dim(30, 68, 76, 68, "g")
          + cap(53, 64, "떨어뜨린다", "var(--bad)", 8.5)
          + cap(46, 90, "양수조작식", "var(--muted)", 8.5)),
         ("접근거부형", "손을 밀어낸다",
          "접근거부형은 다가온 손을 밀어내거나 당긴다 — 손쳐내기식 수인식",
          _MACH + _hand(30, 40)
          + '<path d="M70 45 H40" stroke="var(--bad)" stroke-width="2.4"'
            ' marker-end="url(#dEg)"/>'
          + '<path d="M70 26 V64" stroke="var(--bad)" stroke-width="2.4"/>'
          + cap(46, 90, "손쳐내기 · 수인식", "var(--muted)", 8.5)),
         ("접근반응형", "다가가면 멈춘다",
          "접근반응형은 사람이 다가오면 기계를 멈춘다 — 광전자식 감응식",
          _MACH + _hand(14, 40)
          + '<path d="M62 14 V78" stroke="var(--bad)" stroke-width="2"'
            ' stroke-dasharray="4 3"/>'
          + cap(62, 10, "빛의 벽", "var(--bad)", 8.5)
          + cap(46, 90, "광전자식(감응식)", "var(--muted)", 8.5)),
         ("포집형", "날아오는 것을 받는다",
          "포집형은 위험원에서 날아오는 것을 받는다 — 연삭기 덮개 반발예방장치",
          box(40, 46, 40, 22, 2)
          + '<circle cx="60" cy="46" r="14" fill="var(--panel2)" stroke="var(--line)"'
            ' stroke-width="1.4"/>'
          + '<path d="M40 46 A20 20 0 0 1 80 46" fill="none" stroke="var(--bad)"'
            ' stroke-width="2.6"/>'
          + "".join('<path d="M60 40 L%d %d" stroke="var(--bad)" stroke-width="1.4"/>'
                    % (60 + dx, 40 + dy)
                    for dx, dy in ((-16, -12), (0, -17), (16, -12)))
          + cap(60, 20, "받아 낸다", "var(--bad)", 8.5)
          + cap(60, 90, "연삭기 덮개 · 반발예방", "var(--muted)", 8.5))],
        [("격리형", "사이를 막는다", "완전차단 · 덮개 · 게이트 가드식"),
         ("위치제한형", "손이 갈 수 없는 자리에", "양수조작식"),
         ("접근거부형", "손을 밀어내거나 당긴다", "손쳐내기식 · 수인식"),
         ("접근반응형", "다가가면 멈춘다", "광전자식(감응식)"),
         ("포집형", "날아오는 것을 받는다", "위험원 쪽이다")],
        tag="g")


# ── 연삭숫돌의 파괴 원인 ──────────────────────────────────────────────
def grinder_break():
    def wheel(fr):
        return ('<circle cx="60" cy="44" r="30" fill="var(--panel2)"'
                ' stroke="var(--line)" stroke-width="1.6"/>'
                '<circle cx="60" cy="44" r="%s" fill="var(--line)" opacity=".5"/>'
                '<circle cx="60" cy="44" r="4" fill="var(--panel)"/>' % fr)
    ok = (wheel(10) + dim(60, 44, 70, 44, "r")
          + cap(60, 88, "플랜지 ≥ 숫돌 지름의 1/3", "var(--bad)", 8.5)
          + cap(60, 12, "정상", "var(--muted)", 9))
    bad = (wheel(5)
           + '<path d="M60 14 L54 44 L66 52 L60 74" fill="none" stroke="var(--bad)"'
             ' stroke-width="2.4"/>'
           + cap(60, 88, "플랜지가 작으면 깨진다", "var(--bad)", 8.5)
           + cap(60, 12, "현저히 작을 때", "var(--muted)", 9))
    side = ('<circle cx="44" cy="44" r="26" fill="var(--panel2)" stroke="var(--line)"'
            ' stroke-width="1.6"/>'
            + box(80, 38, 26, 12, 1)
            + '<path d="M70 44 H78" stroke="var(--line)" stroke-width="2"/>'
            + cap(44, 88, "정면(원주면) — 정상", "var(--muted)", 8.5)
            + '<rect x="30" y="12" width="28" height="9" fill="var(--bad)"'
              ' opacity=".22"/>'
            + '<path d="M32 21 H56" stroke="var(--bad)" stroke-width="2.4"/>'
            + cap(44, 10, "측면 — 위험", "var(--bad)", 8.5))
    return figs("연삭숫돌의 파괴 원인",
                [("플랜지", "1/3 이상", "플랜지 지름은 숫돌 지름의 3분의 1 이상이어야 한다", ok),
                 ("플랜지 부족", "파괴 원인", "플랜지가 현저히 작으면 숫돌이 깨진다", bad),
                 ("사용면", "정면이 정상", "숫돌은 정면인 원주면으로 쓰고 측면 연삭은 위험하다",
                  side)],
                [("회전속도 초과", "원심력이 강도를 넘는다", ""),
                 ("측면 사용", "정면(원주면)이 정상 사용면", ""),
                 ("큰 충격 · 균열 · 편심", "취성 재료라 충격에 약하다", "작업 전 음향검사"),
                 ("플랜지", "숫돌 지름의 1/3 이상", "모자라면 위험"),
                 ("시운전", "작업 전 1분 · 교체 후 3분 이상", "덮개는 지름 5 cm 이상 숫돌")],
                tag="r")


# ── 폭발위험장소의 구분 ───────────────────────────────────────────────
# 0 · 1 · 2 종은 「가스가 얼마나 오래 있나」다. 한 색의 진하기로 나타낸다.
def hazard_zone():
    art = ('<rect x="6" y="10" width="108" height="72" fill="var(--bad)"'
           ' opacity=".06"/>'
           + cap(101, 78, "2종", "var(--bad)", 9)
           + '<rect x="18" y="16" width="76" height="60" rx="3" fill="var(--bad)"'
             ' opacity=".13"/>'
           + box(26, 22, 60, 50, 3)
           + '<path d="M26 46 H86 V69 A3 3 0 0 1 83 72 H29 A3 3 0 0 1 26 69 Z"'
             ' fill="var(--line)" opacity=".45"/>'
           + '<rect x="26" y="23" width="60" height="23" fill="var(--bad)"'
             ' opacity=".3"/>'
           + cap(56, 38, "0종", "var(--bad)", 11)
           + cap(56, 60, "액면", "var(--muted)", 8.5)
           + box(48, 14, 16, 8, 1)
           + '<circle cx="56" cy="14" r="7" fill="var(--bad)" opacity=".22"/>'
           + cap(60, 9, "1종 — 개구부 부근", "var(--bad)", 8.5)
           + cap(60, 90, "늘 0종 · 가끔 1종 · 이상 시 2종", "var(--muted)", 8.5))
    return fig1("폭발위험장소의 구분",
                "0종은 탱크 안 액면 상부, 1종은 개구부 부근, 2종은 이상 시에만",
                art, "얼마나 오래 있나", "0 · 1 · 2 종",
                [("0종", "계속 또는 장시간", "탱크 안 액면 상부 · 개방용기 내부"),
                 ("1종", "정상 운전 중 때때로", "벤트 · 맨홀 · 충전 개구부 부근"),
                 ("2종", "이상 시에만 잠깐", "환기가 잘 되는 곳"),
                 ("0종에 쓸 수 있는 것", "본질안전 ia 만", "2종은 n(비점화)까지")])


# ── 정전기 방전의 종류 ────────────────────────────────────────────────
def discharge_types():
    def plate(y):
        return '<rect x="16" y="%d" width="88" height="6" fill="var(--line)"/>' % y
    corona = ('<path d="M60 76 V40 L60 22" stroke="var(--line)" stroke-width="3"/>'
              + "".join('<path d="M60 22 L%.0f %.0f" stroke="var(--bad)"'
                        ' stroke-width="1.4"/>'
                        % (60 + 14 * math.cos(math.radians(a)),
                           22 + 14 * math.sin(math.radians(a)))
                        for a in range(200, 341, 20))
              + cap(60, 90, "뾰족한 끝 · 「쉬」 소리", "var(--muted)", 8.5))
    streamer = ('<path d="M60 76 V26" stroke="var(--line)" stroke-width="3"/>'
                + '<path d="M60 26 L52 12 M60 26 L68 10 M60 26 L60 8"'
                  ' stroke="var(--bad)" stroke-width="2"/>'
                + '<path d="M52 12 L46 6 M68 10 L74 6" stroke="var(--bad)"'
                  ' stroke-width="1.4"/>'
                + cap(60, 90, "줄기 모양으로 자란다", "var(--muted)", 8.5))
    spark = (plate(14) + plate(66)
             + '<path d="M56 20 L66 38 L54 42 L64 66" fill="none" stroke="var(--bad)"'
               ' stroke-width="2.6" stroke-linejoin="round"/>'
             + cap(60, 90, "한 번에 뚫린다 · 폭발 위험", "var(--muted)", 8.5))
    creep = (plate(58)
             + '<path d="M60 58 V44" stroke="var(--line)" stroke-width="3"/>'
             + "".join('<path d="M60 44 %s" fill="none" stroke="var(--bad)"'
                       ' stroke-width="1.6"/>' % d
                       for d in ("q-14 4 -22 12 q-6 6 -14 8",
                                 "q14 4 22 12 q6 6 14 8",
                                 "q-6 8 -8 18", "q6 8 8 18"))
             + cap(60, 90, "부도체 표면을 따라 번진다", "var(--muted)", 8.5))
    thunder = ('<path d="M28 30 q-6 -16 12 -16 q6 -12 22 -6 q16 -8 24 6 q14 2 8 16 Z"'
               ' fill="var(--line)" opacity=".45"/>'
               + '<path d="M58 32 L66 48 L54 52 L62 72" fill="none" stroke="var(--bad)"'
                 ' stroke-width="2.4" stroke-linejoin="round"/>'
               + '<path d="M20 78 V40 M100 78 V40" stroke="var(--line)"'
                 ' stroke-width="2"/>'
               + cap(60, 90, "대전운 — 분체 사일로", "var(--muted)", 8.5))
    return figs("정전기 방전의 종류",
                [("코로나", "가장 약하다", "코로나 방전은 뾰족한 끝에서 국부적으로 일어난다",
                  corona),
                 ("스트리머", "코로나보다 세다", "스트리머 방전은 코로나가 줄기 모양으로 자란 것",
                  streamer),
                 ("불꽃", "에너지가 크다", "불꽃 방전은 공기가 뚫려 한 번에 일어난다", spark),
                 ("연면", "표면을 따라", "연면방전은 부도체 표면을 따라 나뭇가지 모양으로 번진다",
                  creep),
                 ("뇌상", "공중의 대전운", "뇌상 방전은 공중에 떠 있는 대전운에서 일어난다",
                  thunder)],
                [("코로나", "뾰족한 끝에서", "파괴력이 가장 작다"),
                 ("스트리머", "줄기 모양", "코로나보다 세다"),
                 ("불꽃", "한 번에", "폭발 위험이 크다"),
                 ("연면", "부도체 표면을 따라", "필름 · 시트 권취"),
                 ("뇌상", "공중의 대전운", "분체 저장 사일로")])


# ── 가스의 위험도 ─────────────────────────────────────────────────────
# H = (상한 − 하한) / 하한. 분모가 하한이라는 말은 띠의 **왼쪽 끝**이 값을
# 정한다는 뜻이다. 띠를 나란히 놓으면 그 말이 눈으로 보인다.
GASES = [("이황화탄소", 1.2, 44, "35.7"), ("아세틸렌", 2.5, 81, "31.4"),
         ("수소", 4, 75, "17.8"), ("프로판", 2.1, 9.5, "3.5"),
         ("메탄", 5, 15, "2.0")]


def gas_hazard():
    """띠 다섯을 나란히. 이름은 왼쪽 칸, 값은 오른쪽 칸에 세워 서로 안 겹치게 한다."""
    def px(v):
        return round(44 + v / 85.0 * 56, 1)
    art = '<path d="M44 72 H100" stroke="var(--line)" stroke-width="1.2"/>'
    for t in (0, 25, 50, 75):
        art += ('<path d="M%s 72 V75" stroke="var(--line)" stroke-width="1"/>' % px(t)
                + cap(px(t), 83, str(t), "var(--dim)", 7))
    for i, (nm, lo, hi, h) in enumerate(GASES):
        y = 12 + i * 11
        art += ('<rect x="%s" y="%s" width="%s" height="5" rx="2.5"'
                ' fill="var(--line)"/>' % (px(lo), y, round(px(hi) - px(lo), 1)))
        art += ('<rect x="%s" y="%s" width="3" height="5" rx="1.5"'
                ' fill="var(--bad)"/>' % (round(px(lo) - 1, 1), y))
        art += cap(40, y + 4.5, nm, "var(--muted)", 7.5, "end")
        art += cap(119, y + 4.5, h, "var(--bad)", 8, "end")
    art += cap(66, 91, "폭발범위 [%] — 붉은 끝이 하한", "var(--dim)", 7)
    return fig1("가스의 위험도",
                "위험도는 상한에서 하한을 빼고 하한으로 나눈 값이라 하한이 낮은 가스가 크다",
                art, "분모가 하한이다", "H = (U − L) / L",
                [("이황화탄소", "1.2 ~ 44 %", "H = 35.7 — 가장 크다"),
                 ("아세틸렌", "2.5 ~ 81 %", "H = 31.4"),
                 ("수소", "4 ~ 75 %", "H = 17.8"),
                 ("프로판", "2.1 ~ 9.5 %", "H = 3.5"),
                 ("메탄", "5 ~ 15 %", "H = 2.0 — 작다")])


# ── 비파괴검사(NDT) ───────────────────────────────────────────────────
# 「어느 깊이의 흠을 찾는가」로 갈린다. 시험편을 잘라 보면 한눈에 나뉜다.
def ndt_depth():
    art = (box(12, 32, 96, 34, 2)
           + '<path d="M40 32 L44 44 L36 44 Z" fill="var(--bad)"/>'
           + '<ellipse cx="66" cy="38" rx="6" ry="2.6" fill="var(--bad)"'
             ' opacity=".55"/>'
           + '<ellipse cx="86" cy="52" rx="8" ry="3.4" fill="var(--bad)"/>'
           + '<path d="M40 30 V18" stroke="var(--dim)" stroke-width="1"/>'
           + cap(40, 15, "표면에 열린 흠", "var(--muted)", 7.5)
           + '<path d="M66 34 V24" stroke="var(--dim)" stroke-width="1"/>'
           + cap(88, 22, "표면 바로 아래", "var(--muted)", 7.5)
           + '<path d="M86 56 V72" stroke="var(--dim)" stroke-width="1"/>'
           + cap(86, 80, "내부 결함", "var(--muted)", 7.5)
           + cap(24, 26, "PT · ET", "var(--bad)", 8.5)
           + cap(60, 90, "MT 는 강자성체만", "var(--dim)", 7.5)
           + cap(20, 78, "RT · UT", "var(--bad)", 8.5))
    return fig1("비파괴검사(NDT)",
                "표면 흠은 침투탐상과 와류탐상, 내부 결함은 방사선투과와 초음파탐상으로 찾는다",
                art, "어느 깊이를 보나", "겉 PT·ET · 속 RT·UT",
                [("RT 방사선투과", "내부 결함", ""),
                 ("UT 초음파탐상", "내부 결함 · 두께", ""),
                 ("MT 자분탐상", "표면과 바로 아래", "강자성체만"),
                 ("PT 침투탐상", "표면에 열린 결함", ""),
                 ("ET 와류탐상", "표면", "도전성 재료"),
                 ("AE 음향방출", "진행 중인 균열", ""),
                 ("파괴시험", "인장 · 압축 · 굽힘 · 충격 · 피로", "「탐상」·「투과」가 비파괴")])


# ── 흙막이 계측기기 ───────────────────────────────────────────────────
# 여섯이 「현장의 어디에 붙는가」로 갈린다. 단면 하나에 다 얹는다.
def excavation_gauges():
    art = ('<path d="M6 30 H30 V78 H90 V30 H114" fill="none" stroke="var(--line)"'
           ' stroke-width="1.8"/>'
           + '<rect x="6" y="30" width="24" height="52" fill="var(--line)"'
             ' opacity=".18"/>'
           + '<rect x="90" y="30" width="24" height="52" fill="var(--line)"'
             ' opacity=".18"/>'
           + '<path d="M30 44 H90" stroke="var(--line)" stroke-width="2.4"/>'
           + '<path d="M30 40 V48 M90 40 V48" stroke="var(--line)" stroke-width="2.4"/>'
           + box(94, 14, 18, 16, 1)
           + '<circle cx="34" cy="44" r="3" fill="var(--bad)"/>'
           + cap(38, 41, "하중계", "var(--bad)", 7.5, "start")
           + '<circle cx="30" cy="60" r="3" fill="var(--bad)"/>'
           + cap(34, 66, "변형률계", "var(--bad)", 7.5, "start")
           + '<circle cx="16" cy="44" r="3" fill="var(--bad)"/>'
           + cap(6, 40, "지하수위계", "var(--bad)", 7.5, "start")
           + '<circle cx="16" cy="64" r="3" fill="var(--bad)"/>'
           + cap(6, 76, "간극수압계", "var(--bad)", 7.5, "start")
           + '<circle cx="102" cy="52" r="3" fill="var(--bad)"/>'
           + cap(108, 58, "지중경사계", "var(--bad)", 7.5, "end")
           + '<circle cx="103" cy="14" r="3" fill="var(--bad)"/>'
           + cap(108, 11, "건물경사계", "var(--bad)", 7.5, "end")
           + cap(60, 90, "무엇을 재는가로 짝짓는다", "var(--muted)", 8))
    return fig1("흙막이 계측기기",
                "하중계는 버팀보의 축하중, 변형률계는 부재의 변형률, 경사계는 기울기를 잰다",
                art, "어디에 붙는가", "힘 · 변형 · 물 · 기울기",
                [("하중계 load cell", "축하중", "버팀보 · 어스앵커"),
                 ("변형률계 strain gauge", "부재의 변형률", "흙막이 부재 · 띠장"),
                 ("지하수위계", "지하수위", "배면 지반"),
                 ("간극수압계 piezometer", "흙 속 물의 압력", "연약지반"),
                 ("지중경사계 inclinometer", "흙의 수평변위", "흙막이 배면"),
                 ("건물경사계 tiltmeter", "인접 건물의 기울기", "주변 구조물")])


# ── 굴착기계의 종류와 용도 ────────────────────────────────────────────
# 「기계보다 위인가 아래인가」 하나로 갈린다. 지면선을 그으면 끝난다.
def excavators():
    def base(y=50):
        return (box(30, y, 34, 14, 2)
                + '<circle cx="38" cy="%d" r="4" fill="var(--panel2)"'
                  ' stroke="var(--line)" stroke-width="1.2"/>' % (y + 14)
                + '<circle cx="56" cy="%d" r="4" fill="var(--panel2)"'
                  ' stroke="var(--line)" stroke-width="1.2"/>' % (y + 14))
    gl = '<path d="M4 68 H116" stroke="var(--line)" stroke-width="1.8"/>'
    back = (gl + '<path d="M4 68 H116" stroke="var(--line)" stroke-width="1.8"/>'
            + base(44)
            + '<path d="M64 46 L92 58" stroke="var(--line)" stroke-width="2.4"/>'
            + '<path d="M92 58 L88 76 q10 6 16 -4" fill="none" stroke="var(--bad)"'
              ' stroke-width="2.4"/>'
            + '<path d="M78 84 H108" stroke="var(--bad)" stroke-width="1.2"'
              ' stroke-dasharray="3 3"/>'
            + cap(60, 92, "기계보다 낮은 곳 · 수중도", "var(--muted)", 8))
    power = (gl + base(44)
             + '<path d="M64 50 L92 30" stroke="var(--line)" stroke-width="2.4"/>'
             + '<path d="M92 30 L100 16 q10 4 4 14" fill="none" stroke="var(--bad)"'
               ' stroke-width="2.4"/>'
             + '<path d="M84 12 H112" stroke="var(--bad)" stroke-width="1.2"'
               ' stroke-dasharray="3 3"/>'
             + cap(60, 92, "기계보다 높은 곳", "var(--muted)", 8))
    drag = (gl + base(44)
            + '<path d="M64 46 L100 22" stroke="var(--line)" stroke-width="2.4"/>'
            + '<path d="M100 22 L84 74" stroke="var(--dim)" stroke-width="1.2"/>'
            + '<path d="M80 72 q8 8 16 0" fill="none" stroke="var(--bad)"'
              ' stroke-width="2.4"/>'
            + '<path d="M70 80 H110" stroke="var(--bad)" stroke-width="1.2"'
              ' stroke-dasharray="3 3"/>'
            + cap(60, 92, "낮고 넓은 곳 · 연약지반", "var(--muted)", 8))
    clam = (gl + base(30)
            + '<path d="M64 34 L94 20" stroke="var(--line)" stroke-width="2.4"/>'
            + '<path d="M94 22 V56" stroke="var(--dim)" stroke-width="1.2"/>'
            + '<path d="M86 56 q8 14 16 0" fill="none" stroke="var(--bad)"'
              ' stroke-width="2.6"/>'
            + '<path d="M84 68 V86 M104 68 V86" stroke="var(--bad)"'
              ' stroke-width="1.2" stroke-dasharray="3 3"/>'
            + cap(56, 92, "좁고 깊은 수직 굴착", "var(--muted)", 8))
    return figs("굴착기계의 종류와 용도",
                [("백호", "아래", "백호는 기계보다 낮은 곳을 판다", back),
                 ("파워 셔블", "위", "파워 셔블은 기계보다 높은 곳을 판다", power),
                 ("드래그라인", "낮고 넓게", "드래그라인은 기계보다 낮고 넓은 곳을 판다", drag),
                 ("클램셸", "좁고 깊게", "클램셸은 좁고 깊은 수직 굴착에 쓴다", clam)],
                [("백호(드래그 셔블)", "기계보다 낮은 곳", "가장 널리 쓰인다 · 수중도"),
                 ("파워 셔블", "기계보다 높은 곳", "버킷이 바깥으로 밀린다"),
                 ("드래그라인", "낮고 넓은 곳", "연약지반 · 수중"),
                 ("클램셸", "좁고 깊은 수직 굴착", "우물통 · 잠함")])


# ── 매슬로우의 욕구단계 이론 ──────────────────────────────────────────
MASLOW = ["생리적", "안전", "사회적", "존경", "자아실현"]


def maslow():
    art = ""
    for i, nm in enumerate(MASLOW):
        y0, y1 = 80 - i * 14.0, 80 - (i + 1) * 14.0
        w0, w1 = 50 * (80 - y0) / 70.0 + 6, 50 * (80 - y1) / 70.0 + 6
        hot = (i == 1)
        art += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z"'
                ' fill="%s" stroke="var(--line)" stroke-width="1.2"/>'
                % (60 - w0, y0, 60 + w0, y0, 60 + w1, y1, 60 - w1, y1,
                   "var(--bad)" if hot else "var(--panel2)"))
        art += cap(60, y0 - 4.5, "%d %s" % (i + 1, nm),
                   "var(--panel)" if hot else "var(--muted)", 8.5)
    art += cap(60, 90, "아래가 채워져야 위로 올라간다", "var(--dim)", 8)
    return fig1("매슬로우의 욕구단계 이론",
                "생리적 안전 사회적 존경 자아실현 다섯 단계로 아래가 채워져야 위로 올라간다",
                art, "생 · 안 · 사 · 존 · 자", "2단계가 안전")


# ── 화재의 분류 ───────────────────────────────────────────────────────
# 여기서는 색이 곧 답이다(표시색). 그래서 이 그림만 판의 색을 벗어난다.
FIRE = [("A급", "일반화재", "백색", "#F2F4F8", "냉각 — 물"),
        ("B급", "유류 · 가스", "황색", "#E9B949", "질식 — 포 · 분말"),
        ("C급", "전기화재", "청색", "#3C7DD9", "질식 — CO₂ · 분말"),
        ("D급", "금속화재", "무색", "", "건조사 · 팽창질석")]


def fire_class():
    cells = []
    for gr, what, cname, hexv, how in FIRE:
        disc = ('<circle cx="60" cy="40" r="26" fill="%s" stroke="var(--line)"'
                ' stroke-width="1.6"/>' % hexv if hexv else
                '<circle cx="60" cy="40" r="26" fill="none" stroke="var(--line)"'
                ' stroke-width="1.6" stroke-dasharray="5 4"/>')
        art = (disc
               + ('<text x="60" y="46" fill="#12151C" font-size="20"'
                  ' font-weight="700" text-anchor="middle">%s</text>' % gr[0]
                  if hexv else cap(60, 46, gr[0], "var(--muted)", 20))
               + cap(60, 78, what, "var(--muted)", 9)
               + cap(60, 90, how, "var(--dim)", 8))
        if gr in ("C급", "D급"):
            art += ('<circle cx="98" cy="14" r="10" fill="none" stroke="var(--bad)"'
                    ' stroke-width="2"/>'
                    '<path d="M91 21 L105 7" stroke="var(--bad)" stroke-width="2"/>'
                    + cap(98, 18, "물", "var(--bad)", 9))
        cells.append((gr, cname, "%s는 %s이고 표시색은 %s" % (gr, what, cname), art))
    return figs("화재의 분류", cells,
                [("A급 일반화재", "백색", "냉각소화 — 물"),
                 ("B급 유류 · 가스", "황색", "질식소화 — 포 · 분말 · CO₂"),
                 ("C급 전기화재", "청색", "물 금지 — 감전"),
                 ("D급 금속화재", "무색", "물 절대 금지 — 수소가 난다"),
                 ("K급 주방화재", "—", "비누화 소화약제")])


# ── 거푸집의 측압 ─────────────────────────────────────────────────────
def form_pressure():
    arrows = ""
    for i in range(6):
        y = 20 + i * 10
        ln = 4 + i * 5.2
        c = "var(--bad)" if i >= 4 else "var(--dim)"
        arrows += ('<path d="M78 %d H%.1f" stroke="%s" stroke-width="2"'
                   ' marker-end="url(#dEf2)"/>' % (y, 78 + ln, c, ))
    art = (box(20, 12, 6, 68, 1) + box(78, 12, 6, 68, 1)
           + '<rect x="26" y="12" width="52" height="68" fill="var(--line)"'
             ' opacity=".22"/>'
           + arrows
           + cap(52, 8, "굳지 않은 콘크리트", "var(--muted)", 8.5)
           + cap(104, 74, "최대", "var(--bad)", 8.5, "end")
           + cap(52, 90, "액체에 가까울수록 크다", "var(--muted)", 8.5))
    return fig1("거푸집의 측압",
                "측압은 깊이가 깊을수록 커지고 콘크리트가 액체에 가까울수록 커진다",
                art, "깊을수록 크다", "기온만 낮을수록",
                [("타설속도", "빠를수록 크다", "굳기 전에 높이 쌓인다"),
                 ("슬럼프", "클수록 크다", "묽어서 액체처럼 누른다"),
                 ("다짐", "과할수록 크다", "진동이 유동성을 키운다"),
                 ("기온 · 습도", "낮을수록 크다", "응결이 느려진다 — 유일한 「낮을수록」"),
                 ("타설 높이", "높을수록 크다", "머리압"),
                 ("철근량", "적을수록 크다", "붙잡아 주는 것이 없다"),
                 ("거푸집 표면", "매끄러울수록 크다", "마찰이 적다")],
                tag="f2")


# ── 피뢰기의 보호여유도 ───────────────────────────────────────────────
# 분모가 어느 쪽인가가 갈림길이다. 두 막대를 세우면 「차이 ÷ 아래」가 보인다.
def arrester_margin():
    art = ('<path d="M14 80 H106" stroke="var(--line)" stroke-width="1.4"/>'
           + '<rect x="26" y="18" width="26" height="62" rx="2" fill="var(--line)"'
             ' opacity=".4"/>'
           + '<rect x="70" y="46" width="26" height="34" rx="2" fill="var(--bad)"'
             ' opacity=".35"/>'
           + '<path d="M26 18 H100" stroke="var(--line)" stroke-width="1"'
             ' stroke-dasharray="3 3"/>'
           + '<path d="M70 46 H100" stroke="var(--bad)" stroke-width="1"'
             ' stroke-dasharray="3 3"/>'
           + dim(103, 18, 103, 46, "a")
           + cap(112, 34, "여유", "var(--bad)", 8.5, "end")
           + cap(39, 88, "충격절연강도 BIL", "var(--muted)", 8)
           + cap(83, 88, "제한전압", "var(--bad)", 8)
           + cap(60, 12, "여유도 = 차이 ÷ 제한전압", "var(--muted)", 8.5))
    return fig1("피뢰기의 보호여유도",
                "보호여유도는 충격절연강도에서 제한전압을 뺀 값을 제한전압으로 나눈 것",
                art, "분모는 제한전압", "20 % 이상",
                [("보호여유도", "(BIL − 제한전압) ÷ 제한전압", "× 100 [%]"),
                 ("제한전압", "BIL ÷ (1 + 여유도)", ""),
                 ("BIL 로 나누면", "20 % 가 나와 오답", "갈림길은 분모다"),
                 ("실무", "20 % 이상 확보", "")],
                tag="a")


# 주제 이름 → 그림. 없는 주제는 그림 없이 간다.
FIGS = {
    "기계설비의 위험점": hazard_points,
    "지게차의 안정도": forklift_stability,
    "가설통로의 구조": ramp_spec,
    "강관비계의 구조": scaffold_spec,
    "방망사의 인장강도": net_strength,
    "선반의 방호장치": lathe_guards,
    "달비계의 안전계수": suspended_factor,
    "작업발판의 구조": platform_spec,
    "양수기동식 방호장치의 안전거리": press_distance,
    "이동식 비계": rolling_tower,
    "사다리식 통로의 구조": ladder_spec,
    "롤러기 급정지장치": roller_stop,
    "강관비계의 조립간격": tie_spacing,
    "말비계": horse_scaffold,
    "계단의 강도": stair_spec,
    "방호장치의 분류": guard_types,
    "연삭숫돌의 파괴 원인": grinder_break,
    "폭발위험장소의 구분": hazard_zone,
    "정전기 방전의 종류": discharge_types,
    "가스의 위험도": gas_hazard,
    "비파괴검사(NDT)": ndt_depth,
    "흙막이 계측기기": excavation_gauges,
    "굴착기계의 종류와 용도": excavators,
    "매슬로우의 욕구단계 이론": maslow,
    "화재의 분류": fire_class,
    "거푸집의 측압": form_pressure,
    "피뢰기의 보호여유도": arrester_margin,
}


def fig_for(mid):
    f = FIGS.get(mid)
    return f() if f else ""
