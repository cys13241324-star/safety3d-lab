# -*- coding: utf-8 -*-
"""`focus.html` — 빈출 지도를 CBT 회차에서 지어낸다.

    python tools/build_focus.py

다른 페이지가 전부 암기·체험(3D 실습장 · 암기 은행 · 순찰로 · 게임)인데, 시험이
**무엇을 자주 내는지**를 쓰는 페이지가 하나도 없었다. CBT 문항에는 `subject` ·
`mid`(주제) · `fq`(출제빈도)가 이미 붙어 있으므로 순위는 지어내지 않는다.

24회차 2,880문항 → 고유 주제 1,966개. 상위 200개가 기출의 37 %, 326개가 47 %다.
그래서 이 페이지의 진도는 **외운 개수가 아니라 덮은 기출 비중**으로 잰다.

`deckcov.py` 와 같은 자료를 읽는다. 그쪽은 덱이 기출을 덮는지를 재고, 이쪽은
사람이 기출을 덮는지를 잰다.
"""
import collections
import html
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

HERE = pathlib.Path(__file__).parent.resolve()
LAB = HERE.parent
CBT = next((p for p in (LAB.parent / "sanup-safety-cbt",
                        LAB.parent.parent / "sanup-safety-cbt")
            if p.exists()), LAB.parent / "sanup-safety-cbt")
OUT = LAB / "focus.html"

CANON = {"화학설비위험방지": "화학설비위험방지기술",
         "기계위험방지": "기계위험방지기술",
         "전기위험방지": "전기위험방지기술",
         "인간공학": "인간공학 및 시스템안전공학"}
SHORT = {"안전관리론": "안전관리",
         "인간공학 및 시스템안전공학": "인간공학",
         "기계위험방지기술": "기계",
         "전기위험방지기술": "전기",
         "화학설비위험방지기술": "화학",
         "건설안전기술": "건설"}
ORDER = ["안전관리론", "인간공학 및 시스템안전공학", "기계위험방지기술",
         "전기위험방지기술", "화학설비위험방지기술", "건설안전기술"]


def block(s, name):
    m = re.search(r"(?:const|let|var)\s+" + name + r"\s*=\s*\{", s)
    if not m:
        return None
    st = m.end() - 1
    d = 0
    for j in range(st, len(s)):
        if s[j] in "[{":
            d += 1
        elif s[j] in "]}":
            d -= 1
            if d == 0:
                return s[st:j + 1]
    return None


def load():
    seen, topics = set(), {}
    nq = 0
    for f in sorted(CBT.glob("CBT_*/*_CBT.html")):
        m = re.search(r"CBT_(\d{4})_(\d)회", str(f))
        rid = m.group(0).replace("CBT_", "").replace("_", " ") if m else f.name
        if rid in seen:
            continue
        b = block(f.read_text(encoding="utf-8", errors="ignore"), "D")
        if not b:
            continue
        try:
            D = json.loads(b)
        except ValueError:
            continue
        seen.add(rid)
        nq += len(D.get("q") or [])
        for c in (D.get("cards") or {}).values():
            mid = (c.get("mid") or "").strip()
            if not mid:
                continue
            subj = CANON.get((c.get("subject") or "").strip(),
                             (c.get("subject") or "").strip())
            e = topics.setdefault((subj, mid),
                                  {"fq": 0, "r": set(), "kind": c.get("kind", ""),
                                   "ch": c.get("chapter", ""), "front": "", "back": ""})
            e["fq"] += int(c.get("fq") or 1)
            e["r"].add(rid)
            if not e["front"]:
                e["front"] = c.get("front") or ""
            if len(c.get("back") or "") > len(e["back"]):
                e["back"] = c.get("back") or ""
    return topics, sorted(seen), nq


def build():
    topics, rounds, nq = load()
    rows = sorted(topics.items(), key=lambda kv: (-kv[1]["fq"], kv[0][0], kv[0][1]))
    tot = sum(v["fq"] for v in topics.values())
    data = []
    for i, ((subj, mid), v) in enumerate(rows):
        data.append({"i": i, "s": subj, "m": mid, "q": v["fq"],
                     "r": sorted(v["r"], reverse=True), "k": v["kind"],
                     "c": v["ch"], "f": v["front"], "b": v["back"]})
    # 과목별 가중 합 — 진도 계산에 쓴다
    per = collections.Counter()
    for d in data:
        per[d["s"]] += d["q"]
    marks = []
    acc = 0
    for n in (50, 100, 200, 326, 500, 800):
        acc = sum(d["q"] for d in data[:n])
        marks.append((n, round(acc / tot * 100, 1)))

    payload = json.dumps({"t": data, "tot": tot, "nq": nq,
                          "rounds": rounds, "per": dict(per),
                          "order": ORDER, "short": SHORT, "marks": marks},
                         ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/").replace("<!--", "<\\!--")

    lede = ("기출 %d회차 %s문항에서 주제 %s개를 뽑아 **출제빈도 순**으로 세웠습니다. "
            "외운 것을 체크하면 그것이 기출의 몇 %%를 덮는지 계산합니다. "
            "진도는 외운 개수가 아니라 <b>덮은 출제비중</b>으로 잽니다."
            % (len(rounds), format(nq, ","), format(len(data), ",")))
    lede = lede.replace("**", "")

    doc = TEMPLATE.replace("__LEDE__", lede) \
                  .replace("__NROUND__", str(len(rounds))) \
                  .replace("__NQ__", format(nq, ",")) \
                  .replace("__NTOPIC__", format(len(data), ",")) \
                  .replace("__M200__", str(marks[2][1])) \
                  .replace("__M326__", str(marks[3][1])) \
                  .replace("__DATA__", payload)
    OUT.write_text(doc, encoding="utf-8")
    print("%s — %.1f MB" % (OUT.name, OUT.stat().st_size / 1024 / 1024))
    print("  회차 %d · 문항 %d · 주제 %d · 가중합 %d" % (len(rounds), nq, len(data), tot))
    print("  파레토: " + " · ".join("상위%d→%.1f%%" % m for m in marks))


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>산업안전기사 빈출 지도</title>
<script>(function(){try{var t=localStorage.getItem('safety_theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<style>
:root{--bg:#0A1018;--panel:#0F1622;--panel2:#182234;--line:#33425C;--line-soft:#1E2938;--text:#E8EEF8;--muted:#8C99B0;--dim:#8290AC;--accent:#7FA6E0;--accent-ink:#0B111C;--ok:#5CC08A;--ok-soft:rgba(92,192,138,.16);--bad:#F07056;--warn:#E3B54D;--warn-soft:rgba(227,181,77,.10);--warn-line:rgba(227,181,77,.45);--on-accent:#1A1200;--glass:rgba(15,22,34,.9);--tint:rgba(255,255,255,.05);--sans:"IBM Plex Sans KR","Pretendard","Malgun Gothic",sans-serif;--mono:"IBM Plex Mono",Consolas,monospace;--display:"Gothic A1","IBM Plex Sans KR",sans-serif;color-scheme:dark}
:root[data-theme="light"]{color-scheme:light;--bg:#F4F6FA;--panel:#FFFFFF;--panel2:#EAEEF5;--line:#C6D0DE;--line-soft:#E0E6EF;--text:#14202E;--muted:#4A5568;--dim:#66738A;--accent:#2F5FA8;--accent-ink:#FFFFFF;--ok:#1F6B45;--ok-soft:rgba(31,107,69,.12);--bad:#A8391F;--warn:#8F6512;--warn-soft:rgba(143,101,18,.10);--warn-line:rgba(143,101,18,.35);--on-accent:#FFFFFF;--glass:rgba(255,255,255,.93);--tint:rgba(0,0,0,.04)}
*{box-sizing:border-box}
:focus-visible{outline:2px solid var(--warn);outline-offset:2px}
button,a,select,input,[role=button]{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:15px;line-height:1.55;min-height:100vh}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.wrap{max-width:940px;margin:0 auto;padding:34px 18px 90px}
.topRow{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:14px}
.back{color:var(--muted);text-decoration:none;font-size:13.5px}
.back:hover{color:var(--text)}
.b{font:inherit;font-size:13.5px;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:transparent;color:var(--text);cursor:pointer}
.b:hover{border-color:var(--muted)}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}
h1{font-family:var(--display);font-weight:700;font-size:32px;letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance}
.hazard{height:6px;max-width:300px;border-radius:3px;margin:10px 0 16px;background:var(--warn-line)}
.lede{color:var(--muted);margin:0 0 22px;max-width:64ch}
.lede b{color:var(--text);font-weight:600}

/* 진도 */
.prog{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:0 0 20px}
.prog .big{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:4px}
.prog .pc{font-family:var(--mono);font-size:38px;font-weight:600;color:var(--warn);line-height:1}
.prog .cap{color:var(--muted);font-size:13.5px}
.bar{height:12px;border-radius:6px;background:var(--panel2);border:1px solid var(--line-soft);overflow:hidden;margin:12px 0 6px;position:relative}
.bar i{display:block;height:100%;background:var(--warn);width:0;transition:width .3s}
.bar u{position:absolute;top:0;bottom:0;width:1px;background:var(--line);text-decoration:none}
.ticks{display:flex;justify-content:space-between;font-family:var(--mono);font-size:10.5px;color:var(--dim)}
.perSub{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:8px;margin-top:16px}
.ps{background:var(--panel2);border:1px solid var(--line-soft);border-radius:8px;padding:9px 11px}
.ps .n{font-size:12px;color:var(--muted);margin-bottom:5px}
.ps .v{font-family:var(--mono);font-size:15px;font-weight:600}
.ps .sb{height:4px;border-radius:2px;background:var(--line-soft);margin-top:6px;overflow:hidden}
.ps .sb i{display:block;height:100%;background:var(--accent);width:0}

/* 조작 */
.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 12px}
.tabs{display:flex;flex-wrap:wrap;gap:6px}
.tab{font:inherit;font-size:13px;padding:6px 11px;border-radius:20px;border:1px solid var(--line);background:transparent;color:var(--muted);cursor:pointer}
.tab[aria-pressed=true]{background:var(--warn-soft);border-color:var(--warn-line);color:var(--text)}
input[type=search]{font:inherit;font-size:14px;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--text);min-width:180px;flex:1 1 180px}
.cnt{font-family:var(--mono);font-size:12.5px;color:var(--dim);margin-left:auto;white-space:nowrap}

/* 목록 */
ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
li{background:var(--panel);border:1px solid var(--line-soft);border-radius:10px;overflow:hidden}
li.done{border-color:var(--ok);background:var(--ok-soft)}
.hd{display:grid;grid-template-columns:44px 52px 1fr auto;gap:10px;align-items:center;padding:10px 12px;cursor:pointer}
.rk{font-family:var(--mono);font-size:12px;color:var(--dim);text-align:right}
.fq{font-family:var(--mono);font-size:12.5px;color:var(--warn);white-space:nowrap}
.fq b{font-size:15px;font-weight:600}
.ttl{min-width:0}
.ttl .m{font-weight:500;overflow-wrap:anywhere}
.ttl .sub{font-size:11.5px;color:var(--dim);margin-top:2px}
.chip{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:4px;background:var(--panel2);border:1px solid var(--line-soft);color:var(--muted);margin-right:5px}
.chip.f{color:var(--accent);border-color:var(--accent)}
.ck{width:26px;height:26px;border-radius:6px;border:1.5px solid var(--line);background:transparent;color:transparent;cursor:pointer;font-size:15px;line-height:1;flex:none}
li.done .ck{border-color:var(--ok);color:var(--ok)}
.bd{display:none;padding:0 14px 14px 14px;border-top:1px solid var(--line-soft)}
li.open .bd{display:block}
.bd .q{font-weight:600;margin:12px 0 8px}
.bd .a{color:var(--muted);font-size:14px;line-height:1.7}
.bd .a strong{color:var(--text)}
.bd .a u{text-decoration:none;border-bottom:1px solid var(--warn-line);color:var(--text)}
.bd .a ul{list-style:disc;padding-left:20px;margin:6px 0}
.bd .rr{margin-top:10px;font-family:var(--mono);font-size:11px;color:var(--dim)}
.more{display:block;width:100%;margin:16px 0 0;padding:11px;border-radius:8px;border:1px solid var(--line);background:transparent;color:var(--text);font:inherit;cursor:pointer}
.more:hover{border-color:var(--warn)}
.empty{text-align:center;color:var(--dim);padding:40px 0}
footer{margin-top:36px;color:var(--dim);font-family:var(--mono);font-size:11.5px;line-height:1.7}
@media (max-width:560px){
  .wrap{padding:20px 12px 80px}
  h1{font-size:26px}
  .hd{grid-template-columns:38px 46px 1fr auto;gap:8px;padding:9px 10px}
  .prog{padding:16px}
  .prog .pc{font-size:32px}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="topRow">
    <a class="back" href="index.html">← 학습실</a>
    <button class="b bTheme" type="button">밝은 모드</button>
  </div>

  <p class="eyebrow">출제빈도 · 기출 __NROUND__회차</p>
  <h1>빈출 지도</h1>
  <div class="hazard"></div>
  <p class="lede">__LEDE__</p>

  <section class="prog" aria-label="진도">
    <div class="big">
      <span class="pc mono" id="pc">0.0%</span>
      <span class="cap" id="cap">아직 체크한 주제가 없습니다</span>
    </div>
    <div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" id="barw">
      <i id="bar"></i><u style="left:37%"></u><u style="left:47.3%"></u>
    </div>
    <div class="ticks"><span>0%</span><span>상위 200주제 = 37%</span><span>326주제 = 47%</span><span>100%</span></div>
    <div class="perSub" id="perSub"></div>
  </section>

  <div class="ctl">
    <div class="tabs" id="subTabs"></div>
  </div>
  <div class="ctl">
    <div class="tabs" id="kindTabs"></div>
    <input type="search" id="q" placeholder="주제 검색" aria-label="주제 검색">
    <span class="cnt" id="cnt"></span>
  </div>

  <ol id="list"></ol>
  <button class="more" id="more" type="button" hidden>더 보기</button>
  <p class="empty" id="empty" hidden>해당하는 주제가 없습니다.</p>

  <footer>
    기출 __NROUND__회차 __NQ__문항 · 고유 주제 __NTOPIC__개 · 상위 200주제가 기출의 __M200__%, 326주제가 __M326__%<br>
    순위는 CBT 문항에 붙은 출제빈도를 합산한 것입니다. 체크는 이 브라우저에만 남습니다.<br>
    © addto press. 기출 문항과 해설의 저작권은 출판사에 있습니다.
  </footer>
</div>

<script>window.__D=__DATA__;</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
<script>
(function(){
  var D = window.__D, T = D.t, KEY = 'safety_focus_v1', PAGE = 60;
  var done = {}, subj = '', kind = '', kw = '', shown = PAGE, onlyTodo = false;
  try { done = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e) { done = {}; }
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(done)); } catch(e){} }

  var list = document.getElementById('list'), moreB = document.getElementById('more'),
      empty = document.getElementById('empty'), cntEl = document.getElementById('cnt');

  /* ---------- 진도 ---------- */
  function renderProg(){
    var got = 0, per = {};
    for (var i = 0; i < T.length; i++) {
      if (done[T[i].m]) { got += T[i].q; per[T[i].s] = (per[T[i].s] || 0) + T[i].q; }
    }
    var pc = D.tot ? got / D.tot * 100 : 0, n = Object.keys(done).length;
    document.getElementById('pc').textContent = pc.toFixed(1) + '%';
    document.getElementById('cap').textContent = n
      ? n.toLocaleString() + '개 체크 — 기출 ' + D.nq.toLocaleString() + '문항 가운데 이만큼을 덮습니다'
      : '아직 체크한 주제가 없습니다';
    document.getElementById('bar').style.width = Math.min(100, pc) + '%';
    document.getElementById('barw').setAttribute('aria-valuenow', pc.toFixed(1));
    var h = '';
    D.order.forEach(function(s){
      var tot = D.per[s] || 0, g = per[s] || 0, r = tot ? g / tot * 100 : 0;
      h += '<div class="ps"><div class="n">' + (D.short[s] || s) + '</div>'
         + '<div class="v mono">' + r.toFixed(0) + '%</div>'
         + '<div class="sb"><i style="width:' + r.toFixed(1) + '%"></i></div></div>';
    });
    document.getElementById('perSub').innerHTML = h;
  }

  /* ---------- 거르기 ---------- */
  function filtered(){
    var q = kw.trim().toLowerCase();
    return T.filter(function(x){
      if (subj && x.s !== subj) return false;
      if (kind && x.k !== kind) return false;
      if (onlyTodo && done[x.m]) return false;
      if (q && (x.m + ' ' + x.c + ' ' + x.f).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
  }

  function esc(s){ return (s || '').replace(/[<>&]/g, function(c){ return {'<':'&lt;','>':'&gt;','&':'&amp;'}[c]; }); }

  function render(){
    var rows = filtered(), part = rows.slice(0, shown), h = '';
    for (var i = 0; i < part.length; i++) {
      var x = part[i], d = !!done[x.m];
      h += '<li class="' + (d ? 'done' : '') + '" data-m="' + esc(x.m) + '">'
        + '<div class="hd" role="button" tabindex="0" aria-expanded="false">'
        +   '<span class="rk mono">' + (x.i + 1) + '</span>'
        +   '<span class="fq mono"><b>' + x.q + '</b>회</span>'
        +   '<span class="ttl"><span class="m">' + esc(x.m) + '</span>'
        +     '<span class="sub"><span class="chip">' + esc(D.short[x.s] || x.s) + '</span>'
        +     '<span class="chip' + (x.k === '공식형' ? ' f' : '') + '">' + esc(x.k) + '</span>'
        +     esc(x.c) + ' · ' + x.r.length + '회차 출제</span></span>'
        +   '<button class="ck" type="button" aria-label="외웠음 표시" aria-pressed="' + d + '">✓</button>'
        + '</div>'
        + '<div class="bd"><div class="q">' + x.f + '</div><div class="a">' + x.b + '</div>'
        +   '<div class="rr">출제 회차 · ' + x.r.join(' / ') + '</div></div>'
        + '</li>';
    }
    list.innerHTML = h;
    empty.hidden = rows.length > 0;
    moreB.hidden = rows.length <= shown;
    moreB.textContent = '더 보기 (' + (rows.length - shown).toLocaleString() + '개 남음)';
    var w = 0; for (var j = 0; j < rows.length; j++) w += rows[j].q;
    cntEl.textContent = rows.length.toLocaleString() + '개 · 기출 비중 '
                      + (D.tot ? (w / D.tot * 100).toFixed(1) : 0) + '%';
  }

  /* ---------- 수식 ---------- */
  function typeset(el){
    if (!window.renderMathInElement) return;
    try {
      window.renderMathInElement(el, {
        delimiters: [{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],
        throwOnError: false
      });
    } catch(e){}
  }

  /* ---------- 조작 ---------- */
  function mkTabs(id, items, get, set){
    var box = document.getElementById(id), h = '';
    items.forEach(function(it){
      h += '<button class="tab" type="button" data-v="' + esc(it[0]) + '" aria-pressed="'
         + (get() === it[0]) + '">' + esc(it[1]) + '</button>';
    });
    box.innerHTML = h;
    box.addEventListener('click', function(e){
      var b = e.target.closest('.tab'); if (!b) return;
      set(b.dataset.v); shown = PAGE;
      box.querySelectorAll('.tab').forEach(function(t){
        t.setAttribute('aria-pressed', t.dataset.v === get());
      });
      render();
    });
  }

  var subTabs = [['', '전체']].concat(D.order.map(function(s){ return [s, D.short[s] || s]; }));
  mkTabs('subTabs', subTabs, function(){ return subj; }, function(v){ subj = v; });
  mkTabs('kindTabs', [['', '모든 유형'], ['단답형', '단답형'], ['공식형', '공식형'], ['용어형', '용어형'],
                      ['__todo', '안 외운 것만']],
         function(){ return onlyTodo ? '__todo' : kind; },
         function(v){ if (v === '__todo') { onlyTodo = !onlyTodo; } else { kind = v; onlyTodo = false; } });

  document.getElementById('q').addEventListener('input', function(e){
    kw = e.target.value; shown = PAGE; render();
  });
  moreB.addEventListener('click', function(){ shown += PAGE; render(); });

  list.addEventListener('click', function(e){
    var li = e.target.closest('li'); if (!li) return;
    if (e.target.closest('.ck')) {
      var m = li.dataset.m;
      if (done[m]) delete done[m]; else done[m] = 1;
      save(); li.classList.toggle('done');
      li.querySelector('.ck').setAttribute('aria-pressed', !!done[m]);
      renderProg();
      return;
    }
    if (e.target.closest('.hd')) {
      var wasOpen = li.classList.contains('open');
      li.classList.toggle('open');
      li.querySelector('.hd').setAttribute('aria-expanded', !wasOpen);
      if (!wasOpen) typeset(li.querySelector('.bd'));
    }
  });
  list.addEventListener('keydown', function(e){
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var hd = e.target.closest('.hd'); if (!hd) return;
    e.preventDefault(); hd.click();
  });

  /* ---------- 테마 ---------- */
  (function(){
    function cur(){ return document.documentElement.getAttribute('data-theme') || 'dark'; }
    function sync(){
      document.querySelectorAll('.bTheme').forEach(function(b){
        var d = cur() === 'dark';
        b.textContent = d ? '밝은 모드' : '어두운 모드';
        b.setAttribute('aria-pressed', d);
      });
    }
    document.querySelectorAll('.bTheme').forEach(function(b){
      b.addEventListener('click', function(){
        var t = cur() === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', t);
        try { localStorage.setItem('safety_theme', t); } catch(e){}
        sync();
      });
    });
    sync();
  }());

  renderProg(); render();
}());
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
