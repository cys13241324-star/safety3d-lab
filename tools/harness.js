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
var HANDLERS = {}, TIMERS = [];
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

function gauge(i){ return Number(ELS['gv' + i].textContent); }

// L  = always the left choice  (the regulation-compliant option in every card)
// R  = always the right choice (the shortcut)
// RND= coin flip
// BAL= comply while safety/oversight is the weakest, cut corners while schedule/budget is
function decide(pol){
  if(pol === 'L') return 'chL';
  if(pol === 'R') return 'chR';
  if(pol === 'RND') return Math.random() < 0.5 ? 'chL' : 'chR';
  var g = [gauge(0), gauge(1), gauge(2), gauge(3)];
  var lo = 0;
  for(var i = 1; i < 4; i++) if(g[i] < g[lo]) lo = i;
  return (lo === 0 || lo === 3) ? 'chL' : 'chR';
}

function runPolicy(pol, n){
  var days = [], causes = {}, won = 0, reports = 0, hits = 0;
  for(var g = 0; g < n; g++){
    press('bFresh');
    var guard = 0;
    while(!isOver() && guard++ < 500){
      if(ELS['card'].classList.contains('rep')) reports++;
      if(ELS['card'].classList.contains('hit')) hits++;
      press(decide(pol));
      press('sGo');
    }
    if(guard >= 500) return {err: 'no end'};
    var d = Number(ELS['oDays'].textContent);
    days.push(d);
    if(d > 60) won++;
    var c = ELS['oTag'].textContent;
    causes[c] = (causes[c] || 0) + 1;
  }
  days.sort(function(a,b){ return a - b; });
  var sum = 0; for(var i = 0; i < days.length; i++) sum += days[i];
  return {mean: sum / n, med: days[Math.floor(n/2)], min: days[0], max: days[days.length-1],
          won: won, rate: (won * 100 / n), causes: causes, reports: reports, hits: hits};
}

var POLS = ['L', 'BAL', 'RND', 'R'];
var NAME = {L:'always comply', BAL:'balance the weakest', RND:'coin flip', R:'always cut corners'};
WScript.Echo('');
WScript.Echo('policy               n    mean  median  min  max   reached 60d');
WScript.Echo('-------------------------------------------------------------');
var results = {};
for(var pi = 0; pi < POLS.length; pi++){
  var r = runPolicy(POLS[pi], GAMES);
  if(r.err){ WScript.Echo('FAIL: ' + POLS[pi] + ' ' + r.err); WScript.Quit(1); }
  results[POLS[pi]] = r;
  var pad = function(v, w){ v = String(v); while(v.length < w) v = ' ' + v; return v; };
  var padr = function(v, w){ v = String(v); while(v.length < w) v = v + ' '; return v; };
  WScript.Echo(padr(NAME[POLS[pi]], 20) + pad(GAMES, 4) + pad(r.mean.toFixed(1), 8) + pad(r.med, 7) +
               pad(r.min, 5) + pad(r.max, 5) + pad(r.rate.toFixed(0) + '%', 12));
}
WScript.Echo('');
for(var pi = 0; pi < POLS.length; pi++){
  var r = results[POLS[pi]];
  var parts = [];
  for(var k in r.causes) if(r.causes.hasOwnProperty(k)) parts.push(k + ' ' + r.causes[k]);
  WScript.Echo(NAME[POLS[pi]] + ' -- end causes: ' + parts.join(' / '));
}

/* ---------- resume check ---------- */
WScript.Echo('');
press('bFresh');
for (var i = 0; i < 7; i++) { press('chL'); press('sGo'); }
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
