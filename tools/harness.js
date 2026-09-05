// Test harness: runs the reigns game script under JScript with a DOM stub.
// Source is ASCII only -- WSH reads .js as ANSI. Korean comes from the game at runtime.

/* ---------- ES5 polyfills (JScript 5.8 lacks these) ---------- */
if (!Array.prototype.forEach) Array.prototype.forEach = function (f, t) {
  for (var i = 0; i < this.length; i++) f.call(t, this[i], i, this);
};
if (!Array.prototype.map) Array.prototype.map = function (f, t) {
  var r = []; for (var i = 0; i < this.length; i++) r.push(f.call(t, this[i], i, this)); return r;
};
if (!Array.prototype.filter) Array.prototype.filter = function (f, t) {
  var r = []; for (var i = 0; i < this.length; i++) if (f.call(t, this[i], i, this)) r.push(this[i]); return r;
};
if (!Array.prototype.indexOf) Array.prototype.indexOf = function (v) {
  for (var i = 0; i < this.length; i++) if (this[i] === v) return i; return -1;
};
if (!Array.prototype.findIndex) Array.prototype.findIndex = function (f) {
  for (var i = 0; i < this.length; i++) if (f(this[i], i, this)) return i; return -1;
};
if (!Object.keys) Object.keys = function (o) { var r = []; for (var k in o) if (o.hasOwnProperty(k)) r.push(k); return r; };
if (typeof JSON === 'undefined') {
  JSON = {
    stringify: function (o) {
      var t = typeof o;
      if (o === null || t === 'undefined') return 'null';
      if (t === 'number' || t === 'boolean') return String(o);
      if (t === 'string') return '"' + o.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n') + '"';
      if (o instanceof Array) { var a = []; for (var i = 0; i < o.length; i++) a.push(JSON.stringify(o[i])); return '[' + a.join(',') + ']'; }
      var p = []; for (var k in o) if (o.hasOwnProperty(k) && typeof o[k] !== 'function') p.push(JSON.stringify(String(k)) + ':' + JSON.stringify(o[k]));
      return '{' + p.join(',') + '}';
    },
    parse: function (s) { return eval('(' + s + ')'); }
  };
}

/* ---------- DOM stub ---------- */
var HANDLERS = {}, TIMERS = [], FOCUS = null;
function classList(el) {
  return {
    add: function (c) { if ((' ' + el.className + ' ').indexOf(' ' + c + ' ') < 0) el.className = (el.className + ' ' + c).replace(/^\s+/, ''); },
    remove: function (c) { el.className = (' ' + el.className + ' ').replace(' ' + c + ' ', ' ').replace(/^\s+|\s+$/g, ''); },
    contains: function (c) { return (' ' + el.className + ' ').indexOf(' ' + c + ' ') >= 0; },
    toggle: function (c, f) { if (f) this.add(c); else this.remove(c); }
  };
}
function mkEl(id) {
  var el = {
    id: id, className: '', textContent: '', innerHTML: '', hidden: false,
    style: {}, dataset: {}, firstChild: null, parentNode: null, children: [],
    appendChild: function (c) { this.children.push(c); c.parentNode = this; this.firstChild = this.children[0]; return c; },
    removeChild: function (c) { for (var i = 0; i < this.children.length; i++) if (this.children[i] === c) { this.children.splice(i, 1); break; } this.firstChild = this.children[0] || null; },
    setPointerCapture: function () {},
    setAttribute: function (k, v) { this['attr_' + k] = v; },
    getAttribute: function (k) { return this.hasOwnProperty('attr_' + k) ? this['attr_' + k] : null; },
    focus: function () { FOCUS = this.id; },
    removeAttribute: function (k) { delete this['attr_' + k]; },
    addEventListener: function (ev, fn) { HANDLERS[id + ':' + ev] = fn; },
    querySelectorAll: function () { return []; }
  };
  el.classList = classList(el);
  // innerHTML?? ?? ??? ??? ????, ?? ??? ?? ??? ?? ??
  // (renderHud ? gf#.parentNode.parentNode ?? ??? ??? ?? ?)
  el.parentNode = GHOST;
  return el;
}
var GHOST = { className: '', style: {}, children: [], appendChild: function(){}, removeChild: function(){} };
GHOST.classList = classList(GHOST);
GHOST.parentNode = GHOST;

var ELS = {};
var document = {
  getElementById: function (id) { if (!ELS[id]) ELS[id] = mkEl(id); return ELS[id]; },
  createElement: function () { var e = mkEl('_tmp'); e.firstChild = mkEl('_svg'); return e; },
  addEventListener: function (ev, fn) { HANDLERS['doc:' + ev] = fn; },
  documentElement: { getAttribute: function () { return null; }, setAttribute: function () {} },
  body: mkEl('body')
};
var localStorage = (function () {
  var m = {};
  return {
    getItem: function (k) { return m.hasOwnProperty(k) ? m[k] : null; },
    setItem: function (k, v) { m[k] = String(v); },
    removeItem: function (k) { delete m[k]; }
  };
})();
function setTimeout(fn) { TIMERS.push(fn); return TIMERS.length; }
function clearTimeout() {}
function requestAnimationFrame(fn) { fn(); return 1; }
function addEventListener(ev, fn) { HANDLERS['win:' + ev] = fn; }
var innerWidth = 900, devicePixelRatio = 1;
function drain() { var g = 0; while (TIMERS.length && g++ < 500) { var f = TIMERS.shift(); f(); } }

/* ---------- load the game script ---------- */
function readUtf8(path) {
  var s = new ActiveXObject('ADODB.Stream');
  s.Type = 2; s.Charset = 'utf-8'; s.Open(); s.LoadFromFile(path);
  var t = s.ReadText(); s.Close(); return t;
}
var SRC = readUtf8(WScript.Arguments(0));
var m = SRC.match(/<script>\r?\n([\s\S]*)\r?\n<\/script>/);
if (!m) { WScript.Echo('FAIL: no <script> block found'); WScript.Quit(1); }

try { eval(m[1]); }
catch (e) { WScript.Echo('FAIL init: ' + e.message); WScript.Quit(1); }
drain();
WScript.Echo('init OK  day1 card: ' + ELS['cWho'].textContent + ' / ' + ELS['cSubj'].textContent);
WScript.Echo('art svg bytes: ' + ELS['cArt'].innerHTML.length + '  backdrop layers: ' + ELS['scene'].children.length);

/* ---------- play many games with random choices ---------- */
function press(k) { var h = HANDLERS[k + ':click']; if (h) h({}); drain(); }
function isOver() { return ELS['over'].classList.contains('on'); }

var GAMES = Number(WScript.Arguments(1) || 60);

function gauge(i){ return Number(String(ELS['gv' + i].textContent).replace(/[^0-9]/g, '')); }

// L  = always the left button.  NOT "always comply": since cards flip which side
//      the compliant option sits on, this is now a side-mashing strategy and should lose.
// R  = always the right button.  Same caveat.
// ORAnn = knows the rule nn% of the time (reads card.dataset.ok). This is the comply model.
// RND= coin flip
// BAL= comply while safety/oversight is the weakest, cut corners while schedule/budget is
function decide(pol){
  if(pol.substr(0,3) === 'ORA'){
    var acc = pol.length > 3 ? Number(pol.substr(3)) / 100 : 1;
    var d = ELS['card'].dataset.ok, right = (d === 'r') ? 'chR' : 'chL';
    if(Math.random() < acc) return right;
    return right === 'chR' ? 'chL' : 'chR';
  }
  // TRI = knows the rules AND triages: the fund cannot cover every card, so spend it
  //       on what actually kills and let the cheap, low-severity ones slide.
  //       This is the strategy the game is meant to reward.
  if(pol.substr(0,3) === 'TRI'){
    var acc2 = pol.length > 3 ? Number(pol.substr(3)) / 100 : 1;
    var el = ELS['card'];
    var sev = Number(el.dataset.sev || 0);
    var cost = Number(el.dataset.cost || 0);
    var fund = Number(el.dataset.fund || 0);
    // Pay while the fund holds. When it does not: a diversion is illegal and costs
    // oversight every time, so only commit one for a rule that actually kills.
    // Cheaper, low-severity rules get skipped instead -- a small risk beats a crime.
    var comply = (cost <= fund) || sev >= 14;
    var side = (el.dataset.ok === 'r') ? 'chR' : 'chL';
    if(!comply) side = (side === 'chR') ? 'chL' : 'chR';
    if(Math.random() < acc2) return side;
    return side === 'chR' ? 'chL' : 'chR';
  }
  if(pol === 'L') return 'chL';
  if(pol === 'R') return 'chR';
  if(pol === 'RND') return Math.random() < 0.5 ? 'chL' : 'chR';
  var g = [gauge(0), gauge(1), gauge(2), gauge(3)];
  var lo = 0;
  for(var i = 1; i < 4; i++) if(g[i] < g[lo]) lo = i;
  return (lo === 0 || lo === 3) ? 'chL' : 'chR';
}

function runPolicy(pol, n){
  var days = [], causes = {}, won = 0, reports = 0, hits = 0, sheets = 0, need = 0, ill = 0;
  var lastSubj = '', run = 0, maxRun = 0, seen = {}, dupes = 0;
  for(var g = 0; g < n; g++){
    press('bFresh');
    var guard = 0;
    while(!isOver() && guard++ < 500){
      if(ELS['card'].classList.contains('rep')) reports++;
      if(ELS['card'].classList.contains('hit')) hits++;
      var sj = ELS['cSubj'].textContent;
      if(sj === lastSubj){ run++; if(run > maxRun) maxRun = run; } else { lastSubj = sj; run = 1; }
      var wh = ELS['cWho'].textContent + '|' + sj;
      if(seen[wh]) dupes++; seen[wh] = 1;
      var el0 = ELS['card'];
      var n0 = Number(el0.dataset.need || 0);
      press(decide(pol));
      if(document.getElementById('sheet').classList.contains('on')) sheets++;
      var el1 = ELS['card'];
      if(Number(el1.dataset.need || 0) >= n0) { need += Number(el1.dataset.need || 0) - n0; }
      press('sGo');
    }
    if(guard >= 500) return {err: 'no end'};
    // dataset.ill only refreshes on show(); read the run total once, after the game ends
    ill += Number(ELS['card'].dataset.ill || 0);
    var d = Number(ELS['oDays'].textContent);
    days.push(d);
    if(d > 60) won++;
    var c = ELS['oTag'].textContent;
    causes[c] = (causes[c] || 0) + 1;
  }
  days.sort(function(a,b){ return a - b; });
  var sum = 0; for(var i = 0; i < days.length; i++) sum += days[i];
  return {mean: sum / n, med: days[Math.floor(n/2)], min: days[0], max: days[days.length-1],
          won: won, rate: (won * 100 / n), causes: causes, reports: reports, hits: hits,
          maxRun: maxRun, sheets: sheets / n, need: need / n, ill: ill / n, cards: (sum / n)};
}

var POLS = (WScript.Arguments.length > 2 && WScript.Arguments(2) === 'sides')
  ? ['L', 'R', 'RND'] : ['TRI', 'TRI85', 'TRI70', 'ORA', 'ORA85', 'ORA70', 'BAL', 'RND'];
var NAME = {L:'always left (side-mash)', ORA:'comply always 100%', ORA85:'comply always 85%',
            ORA70:'comply always 70%', ORA55:'comply always 55%',
            TRI:'triage 100%', TRI85:'triage 85%', TRI70:'triage 70%',
            BAL:'balance the weakest', RND:'coin flip', R:'always right (side-mash)'};
WScript.Echo('');
WScript.Echo('policy                    n    mean  median  min  max  reached 60d  sheets  need(M)  divert');
WScript.Echo('------------------------------------------------------------------------------------------------');
var results = {};
for(var pi = 0; pi < POLS.length; pi++){
  var r = runPolicy(POLS[pi], GAMES);
  if(r.err){ WScript.Echo('FAIL: ' + POLS[pi] + ' ' + r.err); WScript.Quit(1); }
  results[POLS[pi]] = r;
  var pad = function(v, w){ v = String(v); while(v.length < w) v = ' ' + v; return v; };
  var padr = function(v, w){ v = String(v); while(v.length < w) v = v + ' '; return v; };
  WScript.Echo(padr(NAME[POLS[pi]], 25) + pad(GAMES, 4) + pad(r.mean.toFixed(1), 8) + pad(r.med, 7) +
               pad(r.min, 5) + pad(r.max, 5) + pad(r.rate.toFixed(0) + '%', 12) +
               pad(r.sheets.toFixed(1), 8) + pad(r.need.toFixed(0), 9) + pad(r.ill.toFixed(1), 8));
}
WScript.Echo('');
for(var pi = 0; pi < POLS.length; pi++){
  var r = results[POLS[pi]];
  var parts = [];
  for(var k in r.causes) if(r.causes.hasOwnProperty(k)) parts.push(k + ' ' + r.causes[k]);
  WScript.Echo(NAME[POLS[pi]] + ' -- end causes: ' + parts.join(' / ') + '   | longest same-subject run: ' + r.maxRun);
}

/* ---------- traced single game (diagnostic) ---------- */
if (WScript.Arguments.length > 2 && WScript.Arguments(2) === 'trace') {
  press('bFresh');
  var g = 0;
  while (!isOver() && g++ < 200) {
    var e = ELS['card'];
    WScript.Echo('day ' + ELS['mDay'].textContent +
      '  g[' + gauge(0) + ',' + gauge(1) + ',' + gauge(2) + ',' + gauge(3) + ']' +
      '  fund ' + e.dataset.fund + '  need ' + e.dataset.need + '  ill ' + e.dataset.ill +
      '  cost ' + e.dataset.cost + '  subj ' + ELS['cSubj'].textContent);
    press(decide('ORA'));
    press('sGo');
  }
  WScript.Echo('END ' + ELS['oTag'].textContent + ' :: ' + ELS['oDesc'].textContent);
  WScript.Quit(0);
}

/* ---------- resume check ---------- */
WScript.Echo('');
press('bFresh');
// Comply for 7 days rather than mashing the left button: side-mashing is a losing
// strategy, so the run could end before day 8 and leave nothing to resume from --
// the check would then fail for a reason that has nothing to do with saving.
for (var i = 0; i < 7 && !isOver(); i++) { press(decide('ORA')); press('sGo'); }
if (isOver()) { WScript.Echo('FAIL: run ended before day 8, cannot test resume'); WScript.Quit(1); }
var shownDay = ELS['mDay'].textContent, shownWho = ELS['cWho'].textContent;
var saved = localStorage.getItem('reigns_run_v1');
if (!saved) { WScript.Echo('FAIL: nothing saved mid-run'); WScript.Quit(1); }
var r = JSON.parse(saved);
WScript.Echo('saved blob: ' + saved.length + ' bytes');
WScript.Echo('  day ' + r.day + '  gauges [' + r.g.join(', ') + ']  used cards ' + r.deck.length + '  current speaker ' + (r.cur ? r.cur.w : 'NONE'));
WScript.Echo('  screen shows: ' + shownDay + ' / ' + shownWho);
var dayNum = Number(shownDay.replace(/[^0-9]/g, ''));
WScript.Echo('  day matches screen: ' + (r.day === dayNum ? 'YES' : 'NO (' + r.day + ' vs ' + dayNum + ')'));
WScript.Echo('  speaker matches screen: ' + (r.cur && r.cur.w === shownWho ? 'YES' : 'NO'));

var miss = localStorage.getItem('reigns_miss_v1');
WScript.Echo('cumulative missed articles: ' + (miss ? Object.keys(JSON.parse(miss)).length : 0));
WScript.Echo('');
WScript.Echo('=== PASS ===');
