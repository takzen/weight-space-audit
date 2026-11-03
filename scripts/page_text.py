"""Prose, styles and script of the results page. The measured numbers come from build_page.py; numbers in the audit come from the authors' logs."""


def T(en, pl):
    return f'<span lang="en">{en}</span><span lang="pl">{pl}</span>'


def P(en, pl, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<p lang="en"{c}>{en}</p><p lang="pl"{c}>{pl}</p>'


def UL(items, cls="bul"):
    return (f'<ul lang="en" class="{cls}">' + "".join(f"<li>{a}</li>" for a, _ in items) + "</ul>"
            f'<ul lang="pl" class="{cls}">' + "".join(f"<li>{b}</li>" for _, b in items) + "</ul>")


CSS = r"""
/* Layout: a results sheet. One reading column, figures run wider, and the weight map in the hero is the single loud element. */
:root {
  --paper: #eef1f4; --sheet: #fbfcfd; --ink: #12171d; --ink-2: #414c58; --ink-3: #5c6773;
  --rule: #d6dce3; --rule-2: #b4bec9; --accent: #1c5cab;
  --edited: #2a78d6; --unedited: #eb6834; --ring: #12171d;
  --good: #006300; --bad: #b42c2c; --warn: #7d5200;
  --h0: #e3e8ee; --h1: #cde2fb; --h2: #9ec5f4; --h3: #6da7ec; --h4: #3987e5; --h5: #256abf; --h6: #184f95; --h7: #0d366b;
  --display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #0d1115; --sheet: #151a20; --ink: #e9eef3; --ink-2: #b7c1cc; --ink-3: #94a0ac;
  --rule: #27303a; --rule-2: #3f4b58; --accent: #86b6ef;
  --edited: #3987e5; --unedited: #d95926; --ring: #e9eef3;
  --good: #4cc44c; --bad: #ee7b7b; --warn: #e0a84a;
  --h0: #1c232b; --h1: #184f95; --h2: #1c5cab; --h3: #256abf; --h4: #2a78d6; --h5: #5598e7; --h6: #86b6ef; --h7: #cde2fb;
  color-scheme: dark;
} }
:root[data-theme="dark"] {
  --paper: #0d1115; --sheet: #151a20; --ink: #e9eef3; --ink-2: #b7c1cc; --ink-3: #94a0ac;
  --rule: #27303a; --rule-2: #3f4b58; --accent: #86b6ef;
  --edited: #3987e5; --unedited: #d95926; --ring: #e9eef3;
  --good: #4cc44c; --bad: #ee7b7b; --warn: #e0a84a;
  --h0: #1c232b; --h1: #184f95; --h2: #1c5cab; --h3: #256abf; --h4: #2a78d6; --h5: #5598e7; --h6: #86b6ef; --h7: #cde2fb;
  color-scheme: dark;
}
:root:not([data-lang="pl"]) body [lang="pl"] { display: none !important; }
:root[data-lang="pl"] body [lang="en"] { display: none !important; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 400 1.0625rem/1.6 var(--body); }
.wrap { max-width: 74rem; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 1rem 3rem; }
a { color: var(--accent); text-underline-offset: 2px; }
code, pre { font-family: var(--mono); font-size: .86em; }
small { font-size: .82em; color: var(--ink-3); }
h1, h2, h3, h4 { margin: 0; text-wrap: balance; }
h1 { font: 650 clamp(2.1rem, 4.6vw, 3.45rem)/1.04 var(--display); letter-spacing: -.015em; }
h2 { font: 650 clamp(1.5rem, 2.6vw, 1.95rem)/1.15 var(--display); letter-spacing: -.01em; }
h3 { font: 600 1.125rem/1.3 var(--body); }
h3.sub { font: 650 1.25rem/1.25 var(--display); margin-top: .75rem; }
h4 { font: 500 .75rem/1.2 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--ink-3); margin-bottom: .35rem; }
p { margin: 0; }
button:focus-visible, a:focus-visible, summary:focus-visible, [tabindex]:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.top { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; font: 400 .8rem/1.3 var(--mono); color: var(--ink-3); padding-bottom: 1rem; }
.langs { display: inline-flex; border: 1px solid var(--rule-2); border-radius: 3px; overflow: hidden; }
.langs button { all: unset; cursor: pointer; padding: .3rem .75rem; font: 500 .8rem/1.3 var(--mono); color: var(--ink-2); min-height: 24px; }
.langs button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.langs button:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }

.hero { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 21.5rem); gap: clamp(1.5rem, 4vw, 3.5rem); align-items: start; padding-block: 1rem 2.5rem; border-bottom: 1px solid var(--rule-2); }
.hero-text { display: grid; gap: 1.1rem; min-width: 0; }
.lead { font-size: 1.1875rem; line-height: 1.5; color: var(--ink-2); max-width: 44rem; }
.strip { display: flex; flex-wrap: wrap; gap: 1rem 2.25rem; padding-top: .35rem; }
.stat { display: grid; gap: .15rem; min-width: 9.5rem; flex: 1 1 9.5rem; max-width: 15rem; }
.stat-v { font: 650 clamp(2.4rem, 4.4vw, 3.1rem)/1 var(--display); letter-spacing: -.02em; }
.stat-l { font-size: .875rem; line-height: 1.35; color: var(--ink-2); }
.note { font-size: .9375rem; color: var(--ink-2); max-width: 44rem; }
.hero-fig { display: grid; gap: .6rem; min-width: 0; }
.fig-code code { font-size: .75rem; overflow-wrap: anywhere; }
.fig-note { font-size: .875rem; line-height: 1.45; color: var(--ink-2); max-width: 46rem; }

.board { margin: 0; display: grid; gap: .4rem; min-width: 0; }
.board figcaption { font: 400 .75rem/1.35 var(--mono); color: var(--ink-3); }
.grid10 { display: grid; grid-template-columns: repeat(10, minmax(0, 1fr)); gap: 2px; width: 100%; aspect-ratio: 1; max-width: 100%; }
.grid10 i { display: block; }
.h0 { background: var(--h0); } .h1 { background: var(--h1); } .h2 { background: var(--h2); } .h3 { background: var(--h3); }
.h4 { background: var(--h4); } .h5 { background: var(--h5); } .h6 { background: var(--h6); } .h7 { background: var(--h7); }
.boards { display: grid; grid-template-columns: repeat(auto-fit, minmax(8.5rem, 10.5rem)); gap: 1rem 1.25rem; }
.scale { display: flex; align-items: center; gap: .5rem; font: 400 .72rem/1 var(--mono); color: var(--ink-3); }
.scale-bar { display: grid; grid-template-columns: repeat(8, 1fr); gap: 2px; flex: 1; height: 10px; }
.scale-bar i { display: block; }
.values summary { cursor: pointer; font: 400 .78rem/1.4 var(--mono); color: var(--ink-3); }
.grid-values { border-collapse: collapse; font: 400 .7rem/1.5 var(--mono); font-variant-numeric: tabular-nums; margin-top: .4rem; }
.grid-values td { padding: 0 .35rem; text-align: right; color: var(--ink-2); }

main { display: grid; gap: 0; }
section { display: grid; gap: 1rem; padding-block: 2.25rem; border-bottom: 1px solid var(--rule-2); min-width: 0; }
section > p, section > ul, section > ol { max-width: 46rem; }
.bul { margin: 0; padding-left: 1.15rem; display: grid; gap: .55rem; }
.findings { max-width: 44rem; font-size: 1.0625rem; line-height: 1.5; }
.plain { margin: .3rem 0 0; padding: 0; list-style: none; display: grid; gap: .45rem; }
.find { display: grid; gap: .3rem; max-width: 46rem; }
.finds { display: grid; gap: 1.1rem; }

.fig { margin: .25rem 0; background: var(--sheet); border: 1px solid var(--rule); border-radius: 3px; padding: clamp(.9rem, 2vw, 1.4rem); display: grid; gap: .8rem; min-width: 0; }
.fig > figcaption { font: 650 1.125rem/1.25 var(--display); }
.legend { display: flex; flex-wrap: wrap; gap: .35rem 1.1rem; font-size: .8125rem; color: var(--ink-2); }
.legend span[lang], .legend > span { display: inline-flex; align-items: center; gap: .4rem; }
.swatch { display: inline-block; width: 10px; height: 10px; border-radius: 50%; flex: none; margin-right: .4rem; }
.legend .swatch { margin-right: 0; }
.swatch.edited, .dot.edited, .bar.edited, .ci.edited { background: var(--edited); }
.swatch.unedited, .dot.unedited, .bar.unedited, .ci.unedited { background: var(--unedited); }
.ringkey { width: 12px; height: 12px; border: 2px solid var(--ring); border-radius: 50%; display: inline-block; }
.cikey { width: 18px; height: 2px; background: var(--ink-2); display: inline-block; }
.ch { --cols: minmax(11rem, 1.5fr) minmax(0, 2.2fr) 4.6rem minmax(0, 1.1fr) 2.6rem; display: grid; }
.ch-head, .ch-row { display: grid; grid-template-columns: var(--cols); gap: .9rem; align-items: center; }
.ch-head { align-items: end; padding-bottom: .25rem; }
.ch-phone { display: none; font-size: .8125rem; color: var(--ink-2); }
.ch-title { font: 500 .75rem/1.3 var(--mono); color: var(--ink-3); display: grid; gap: .35rem; }
.axis { position: relative; height: 1rem; font: 400 .72rem/1 var(--mono); color: var(--ink-3); font-variant-numeric: tabular-nums; }
.axis b { position: absolute; top: 0; font-weight: 400; transform: translateX(-50%); }
.axis b:first-child { transform: none; } .axis b:last-child { transform: translateX(-100%); }
.ch-group { font: 500 .75rem/1.3 var(--mono); letter-spacing: .03em; color: var(--ink-2); padding: .85rem 0 .3rem; border-top: 1px solid var(--rule-2); margin-top: .25rem; }
.ch-row { padding: .42rem 0; border-top: 1px solid var(--rule); }
.ch-group + .ch-row { border-top: 0; }
.ch-row[tabindex] { cursor: default; }
.ch-row[tabindex]:hover { background: color-mix(in srgb, var(--rule) 35%, transparent); }
.ch-row.pending { grid-template-columns: minmax(11rem, 1.5fr) minmax(0, 4fr); }
.ch-pending { font: 400 .8rem/1.3 var(--mono); color: var(--ink-3); }
.ch-label { display: grid; gap: .05rem; font-size: .875rem; line-height: 1.3; min-width: 0; }
.ch-name { font-weight: 600; }
.ch-label code { font-size: .75rem; color: var(--ink-2); }
.ch-label small { font-size: .75rem; }
.track { position: relative; height: 26px; min-width: 0;
  background-image: linear-gradient(to right, var(--rule) 1px, transparent 1px); background-size: 20% 100%; border-right: 1px solid var(--rule); }
.dot, .ring, .ci, .bar { position: absolute; top: 50%; }
.ci { height: 2px; margin-top: -1px; border-radius: 1px; }
.dot { width: 11px; height: 11px; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 0 2px var(--sheet); }
.ring { width: 15px; height: 15px; border-radius: 50%; border: 2px solid var(--ring); transform: translate(-50%, -50%); }
.track.bars { background-size: 50% 100%; }
.bar { left: 0; height: 12px; margin-top: -6px; border-radius: 0 4px 4px 0; min-width: 1px; }
.ch-val { display: grid; gap: 0; font-variant-numeric: tabular-nums; text-align: right; line-height: 1.2; font-size: .9375rem; }
.ch-val strong { font-weight: 600; }
.ch-val small { font-size: .72rem; white-space: nowrap; }
.flag { font: 500 .7rem/1 var(--mono); color: var(--bad); }

.decs { display: grid; gap: 0; }
.dec { display: grid; grid-template-columns: 3.25rem minmax(0, 1fr); gap: .75rem; padding-block: 1rem; border-top: 1px solid var(--rule); }
.dec-id { font: 650 1.45rem/1.15 var(--display); color: var(--ink-3); }
.dec-body { display: grid; gap: .45rem; max-width: 50rem; min-width: 0; }
.rule { font-size: .9375rem; color: var(--ink-2); }
.tag { font: 500 .7rem/1.2 var(--mono); letter-spacing: .05em; text-transform: uppercase; color: var(--ink-3); margin-right: .35rem; }
.res { font-size: 1rem; }
.chip { display: inline-flex; align-items: center; gap: .3rem; font: 500 .75rem/1.25 var(--mono); padding: .14rem .45rem; border: 1px solid var(--rule-2); border-radius: 3px; color: var(--ink-2); vertical-align: 1px; }
.chip.strong { color: var(--ink); border-color: var(--ink); font-weight: 500; }
.chip.good { color: var(--good); border-color: var(--good); }
.chip.bad { color: var(--bad); border-color: var(--bad); }
.chip b { font-weight: 700; }
.chip.v-yes { color: var(--good); border-color: var(--good); }
.chip.v-part { color: var(--warn); border-color: var(--warn); }
.chip.v-no { color: var(--bad); border-color: var(--bad); }

.claims { display: grid; }
.claim { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.65fr); gap: .75rem 2.5rem; padding-block: 1.35rem; border-top: 1px solid var(--rule); min-width: 0; }
.claim-q { display: grid; grid-template-columns: 1.5rem minmax(0, 1fr); gap: .35rem; align-items: start; }
.claim-n { font: 650 1.25rem/1.25 var(--display); color: var(--ink-3); }
.claim-q blockquote { border-left: 0; padding: 0; color: var(--ink); font-size: 1rem; line-height: 1.5; grid-column: 2; grid-row: 1; }
.claim-a { display: grid; gap: .5rem; font-size: .96875rem; min-width: 0; }
.claim-a .chip { font-size: .8125rem; font-weight: 500; }

.scroll { overflow-x: auto; max-width: 100%; }
table.data { border-collapse: collapse; width: 100%; min-width: 30rem; font-size: .9375rem; background: var(--sheet); }
table.data th, table.data td { padding: .55rem .7rem; border-bottom: 1px solid var(--rule); text-align: left; vertical-align: top; }
table.data thead th { font-weight: 600; font-size: .8125rem; line-height: 1.3; border-bottom: 1px solid var(--rule-2); }
table.data thead small { display: block; font-weight: 400; }
table.data tbody th { font-weight: 500; }
table.data td { font-variant-numeric: tabular-nums; }
table.num td { text-align: right; } table.num thead th:not(:first-child) { text-align: right; }

blockquote { margin: 0; padding: .1rem 0 .1rem 1rem; border-left: 2px solid var(--rule-2); font-size: .96875rem; color: var(--ink-2); max-width: 46rem; }
blockquote code { font-size: .84em; }
.quotes { display: grid; gap: .8rem; }

.exp { display: grid; gap: .8rem; padding-block: 1.5rem; border-top: 1px solid var(--rule); min-width: 0; }
.exp header { display: flex; flex-wrap: wrap; align-items: baseline; gap: .3rem .75rem; }
.exp-id { font: 500 .78rem/1.3 var(--mono); color: var(--ink-3); }
.exp h3 { font: 650 1.2rem/1.25 var(--display); }
.exp-cols { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.75fr); gap: 1.25rem 2.25rem; font-size: .96875rem; }
.exp-cols p + p { margin-top: .5rem; }
.reading { max-width: 50rem; font-size: 1rem; }
.reading p { font-weight: 500; }

.skills { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1.25rem 2rem; }
.skill h3 { font: 650 1.1rem/1.25 var(--display); margin-bottom: .35rem; }
.skill .which { font: 400 .75rem/1.3 var(--mono); color: var(--ink-3); margin-bottom: .35rem; }
.skill p { font-size: .96875rem; }
.plan pre { white-space: pre-wrap; overflow-wrap: anywhere; background: var(--sheet); border: 1px solid var(--rule); padding: .9rem; font-size: .78rem; line-height: 1.5; border-radius: 3px; margin: .6rem 0 0; }
.hash { overflow-wrap: anywhere; }
.foot { padding-top: 1.5rem; font-size: .875rem; color: var(--ink-2); display: grid; gap: .4rem; }
#tip { position: fixed; z-index: 20; max-width: min(24rem, calc(100vw - 32px)); background: var(--ink); color: var(--paper); font: 400 .8125rem/1.4 var(--body); padding: .45rem .6rem; border-radius: 3px; pointer-events: none; }

@media (max-width: 58rem) {
  .claim { grid-template-columns: minmax(0, 1fr); }
  .hero { grid-template-columns: minmax(0, 1fr); }
  .hero-fig { max-width: 26rem; }
  .exp-cols { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 46rem) {
  .ch { --cols: minmax(0, 1fr) 4.4rem; }
  .ch-head { display: none; }
  .ch-phone { display: block; }
  .ch-row { gap: .25rem .75rem; padding: .7rem 0; }
  .ch-row.pending { grid-template-columns: minmax(0, 1fr); }
  .ch-label { grid-column: 1 / -1; }
  .ch-val small { font-size: .7rem; }
  .dec { grid-template-columns: minmax(0, 1fr); gap: .25rem; }
}
@media (prefers-reduced-motion: no-preference) { .langs button { transition: background-color .12s; } }
"""

CARD_CSS = r"""
html, body { width: 1200px; height: 800px; overflow: hidden; margin: 0; background: var(--sheet); }
.card { box-sizing: border-box; width: 1200px; height: 800px; padding: 34px 44px 24px; display: flex; flex-direction: column; gap: 12px; }
.card h1 { font: 650 37px/1.1 var(--display); letter-spacing: -.012em; }
.card .legend { font-size: 14px; }
.card .ch { --cols: 345px minmax(0, 1fr) 66px 190px 38px; flex: 1; align-content: start; }
.card .ch-row.pending { grid-template-columns: 345px minmax(0, 1fr); }
.card .ch-row { padding: 3px 0; gap: 12px; }
.card .ch-group { padding: 8px 0 2px; font-size: 13px; }
.card .ch-label { font-size: 14px; grid-template-columns: auto 1fr; column-gap: .55rem; align-items: baseline; }
.card .ch-label small { grid-column: 1 / -1; font-size: 12px; }
.card .ch-label code { font-size: 12.5px; }
.card .ch-pending { font-size: 12.5px; }
.card .track { height: 24px; }
.card .ch-val { font-size: 16px; }
.card .ch-val small { font-size: 11.5px; }
.card .ch-phone { display: none; }
.card-foot { font-size: 14.5px; line-height: 1.35; color: var(--ink-2); margin-top: auto; }
.card-maps { display: grid; grid-template-columns: 500px 1fr; gap: 40px; align-items: start; }
.card-big .grid10 { width: 500px; }
.card-small { display: grid; grid-template-columns: repeat(2, 240px); gap: 16px 36px; }
.card-small .grid10 { width: 200px; }
.card .board figcaption { font-size: 13px; }
.card-code code { font-size: 17px; }
.card.card-og { height: 630px; padding: 54px 56px 44px; justify-content: space-between; gap: 30px; }
.card.card-og h1 { margin: 0; font-size: 60px; line-height: 1.07; }
.card.card-og .strip { margin: 0; gap: 22px; grid-template-columns: repeat(auto-fit, minmax(0, 1fr)); grid-auto-flow: column; }
.card.card-og .stat-v { font-size: 62px; }
.card.card-og .stat-l { font-size: 19px; line-height: 1.3; }
.card.card-og .card-foot { margin: 0; font-size: 20px; }
"""

JS = r"""
(function () {
  var root = document.documentElement, tip = document.getElementById('tip');
  var buttons = { en: document.getElementById('b-en'), pl: document.getElementById('b-pl') };
  function setLang(l) {
    root.setAttribute('data-lang', l);
    root.setAttribute('lang', l);
    buttons.en.setAttribute('aria-pressed', l === 'en' ? 'true' : 'false');
    buttons.pl.setAttribute('aria-pressed', l === 'pl' ? 'true' : 'false');
  }
  function saved() { try { return localStorage.getItem('lang'); } catch (e) { return null; } }
  function initial() {
    var h = location.hash.replace('#', '');
    if (h === 'en' || h === 'pl') return h;
    var s = saved();
    if (s === 'en' || s === 'pl') return s;
    return 'en';
  }
  setLang(initial());
  ['en', 'pl'].forEach(function (l) {
    buttons[l].addEventListener('click', function () {
      setLang(l);
      try { localStorage.setItem('lang', l); } catch (e) {}
      location.hash = l;
    });
  });
  window.addEventListener('hashchange', function () {
    var h = location.hash.replace('#', '');
    if (h === 'en' || h === 'pl') setLang(h);
  });
  function text(el) {
    var l = root.getAttribute('data-lang');
    if (el.dataset.v) {
      var i = Array.prototype.indexOf.call(el.parentNode.children, el);
      var r = Math.floor(i / 10), c = i % 10;
      return (l === 'pl' ? 'rząd ' + r + ', kolumna ' + c + ': ' + el.dataset.v.replace('.', ',') : 'row ' + r + ', column ' + c + ': ' + el.dataset.v);
    }
    return l === 'pl' ? el.dataset.tipPl : el.dataset.tipEn;
  }
  function place(x, y) {
    var w = tip.offsetWidth, h = tip.offsetHeight, vw = window.innerWidth, vh = window.innerHeight;
    tip.style.left = Math.max(8, Math.min(x + 12, vw - w - 8)) + 'px';
    tip.style.top = Math.max(8, (y + h + 24 > vh ? y - h - 12 : y + 16)) + 'px';
  }
  function source(t) { return t && t.closest ? t.closest('[data-tip-en],[data-v]') : null; }
  document.addEventListener('pointermove', function (ev) {
    var s = source(ev.target);
    if (!s) { tip.hidden = true; return; }
    tip.textContent = text(s);
    tip.hidden = false;
    place(ev.clientX, ev.clientY);
  });
  document.addEventListener('focusin', function (ev) {
    var s = source(ev.target);
    if (!s) return;
    tip.textContent = text(s);
    tip.hidden = false;
    var b = s.getBoundingClientRect();
    place(b.left + 8, b.bottom - 8);
  });
  document.addEventListener('focusout', function () { tip.hidden = true; });
})();
"""

CLAIMS_INTRO_EN = "The claims in the post's TL;DR, in order. Each verdict links to the evidence further down."
CLAIMS_INTRO_PL = "Tezy z TL;DR posta, po kolei, w tłumaczeniu z angielskiego. Każda ocena prowadzi do dowodów niżej."
INTRO_EN = ("The post's biggest number: editing 0.016% of Qwen3.5-0.8B's weights lifts MATH-500 from 7.9% to 48.1%, with thinking on, "
            "temperature 0.6 and presence penalty 1.5. In that setting 93% of the unedited model's answers run into the 32,768-token cap. "
            "The model card warns about these thinking loops. It also recommends temperature 1.0 for thinking on text, and says this model "
            "runs with thinking off by default. The post reports no control for either, so this test adds them.")
INTRO_PL = ("Największa liczba w poście: edycja 0,016% wag Qwen3.5-0.8B podnosi MATH-500 z 7,9% do 48,1%, przy włączonym myśleniu, "
            "temperaturze 0,6 i presence penalty 1,5. W tym ustawieniu 93% odpowiedzi modelu bez edycji dochodzi do limitu 32 768 tokenów. "
            "Karta modelu ostrzega przed tymi pętlami. Zaleca też temperaturę 1,0 dla myślenia na tekście i mówi, że ten model domyślnie działa "
            "z wyłączonym myśleniem. Post nie podaje kontroli dla żadnej z tych rzeczy, więc ten test je dodaje.")
CHART_NOTE_EN = ("The 100 problems were drawn once, with a fixed seed, before any run. The draw is harder than average: the authors' unedited score is 3.0% here and 7.9% on all 500. "
                 "So compare rows with each other here, and use the table below for the full benchmarks.")
CHART_NOTE_PL = ("Te 100 zadań wylosowano raz, ze stałym ziarnem, przed wszystkimi przebiegami. Próba jest trudniejsza od średniej: wynik autorów bez edycji to tu 3,0%, a na wszystkich 500 zadaniach 7,9%. "
                 "Porównuj więc tutaj wiersze między sobą, a pełne benchmarki są w tabeli niżej.")
FULL_NOTE_EN = ("Same prompt and grader as the post. The grader reproduced the authors' grades on 400 of 400 published samples. "
                "Intervals are 95% bootstrap over problems. The token cap differs: 8,192 with thinking off, 32,768 with thinking on.")
FULL_NOTE_PL = ("Ten sam prompt i grader co w poście. Grader odtworzył oceny autorów na 400 z 400 opublikowanych próbek. "
                "Przedziały to 95% bootstrap po zadaniach. Limit tokenów jest inny: 8192 bez myślenia, 32 768 z myśleniem.")

AUTHORS_CODE = (
    P("The comments below are in the code the authors released, in <code>exp8_math/code/profiles.py</code>. The post and the experiment's README don't mention these runs. The top-level README says &ldquo;Trial runs of earlier prompt versions are left out&rdquo;, so their scores can't be checked.",
      "Poniższe komentarze są w kodzie, który autorzy sami opublikowali, w <code>exp8_math/code/profiles.py</code>. Post i README eksperymentu nie wspominają o tych przebiegach. Główne README mówi, że przebiegi próbne wcześniejszych wersji promptu pominięto (&bdquo;Trial runs of earlier prompt versions are left out&rdquo;), więc ich wyników nie da się sprawdzić.")
    + '<div class="quotes">'
    + '<blockquote><code># thinking OFF (2026-10-23): with thinking on, the 0.8B looped ("Wait, let\'s check ...") and 92 % of MATH-500 answers hit 32,768 tokens (MATH-500 9.3 %); the model card: "Qwen3.5-0.8B operates in non-thinking mode by default"</code></blockquote>'
    + '<blockquote><code># prompt v3 (2026-10-23, after the v2 runs measured noise: the unedited model read 55.5 % and 50.8 % in two 128-answer passes)</code></blockquote>'
    + '<blockquote><code># prompt v5, thinking off: answers are short and v3/v4 gains sat below the noise</code></blockquote>'
    + "</div>"
    + P("So by then the authors knew that the model loops with thinking on and that its default is thinking off. 55.5% and 50.8% are very likely that default mode, since thinking on reads about 10% on practice problems in the same logs; that part is an inference. The third comment suggests that edits with thinking off gave no gain above noise. The post gives no score for this mode.",
        "Autorzy wiedzieli więc wtedy, że z włączonym myśleniem model się zapętla i że jego domyślny tryb to myślenie wyłączone. 55,5% i 50,8% to najpewniej właśnie ten tryb, bo włączone myślenie daje w tych samych logach około 10% na zadaniach ćwiczebnych; to wniosek z liczb. Trzeci komentarz sugeruje, że edycje przy wyłączonym myśleniu nie dawały zysku ponad szum. Post nie podaje wyniku dla tego trybu.")
)

EXPLORATORY_NOTE_EN = "These comparisons were added after the plan and decide no rule. Those against the post's scores mix runs from two machines, so they rely on the calibration above."
EXPLORATORY_NOTE_PL = "Te porównania doszły po planie i niczego nie rozstrzygają. Te względem wyników posta łączą przebiegi z dwóch maszyn, więc opierają się na kalibracji opisanej wyżej."

CARD_INTRO_EN = "The card reports no MATH-500 or GSM8K for this model. It does report three benchmarks the post also uses, and the picture is mixed."
CARD_INTRO_PL = "Karta nie podaje dla tego modelu MATH-500 ani GSM8K. Podaje za to trzy benchmarki użyte też w poście, a obraz jest niejednoznaczny."
CARD_ROWS = [("IFEval", 52.1, 44.0, 21.0, 62.3), ("MMLU-Pro", 29.7, 42.3, 40.3, 45.5), ("GPQA", None, 11.9, 22.7, 36.6)]
CARD_NOTE_EN = ("The post's IFEval base is half the card's thinking-on number, so its &ldquo;3x&rdquo; shrinks to about 1.4x against the card's figure. On MMLU-Pro the post's base is close to the card, and on GPQA it is higher. "
                "The edited model beats the card's thinking-off numbers on IFEval and MMLU-Pro, which counts for the edit. Protocols differ (the card's table used T 1.0, line 285, and the post's T 0.6 is the card's setting for vision benchmarks, line 577), so treat this as context.")
CARD_NOTE_PL = ("Baza IFEval w poście to połowa liczby z karty dla włączonego myślenia, więc &bdquo;3x&rdquo; kurczy się do około 1,4x względem karty. Na MMLU-Pro baza posta jest blisko karty, a na GPQA jest wyższa. "
                "Model z edycją przebija liczby z karty dla wyłączonego myślenia na IFEval i MMLU-Pro, co przemawia za edycją. Protokoły się różnią (tabela karty używa T 1,0, wiersz 285, a T 0,6 z posta to ustawienie z karty dla benchmarków wizyjnych, wiersz 577), więc to tylko kontekst.")

DISCLOSE_EN = "Analysis, code and this page: Claude Opus 5.5 (Anthropic). Anthropic competes with OpenAI, whose model the post tests."
DISCLOSE_PL = "Analiza, kod i ta strona: Claude Opus 5.5 (Anthropic). Anthropic konkuruje z OpenAI, którego model testuje post."

AUDIT_INTRO_EN = "The numbers below come from the authors' public logs, unless the text says otherwise. Astra wasn't re-run."
AUDIT_INTRO_PL = "Liczby poniżej pochodzą z publicznych logów autorów, chyba że tekst mówi inaczej. Astry nie uruchamiano ponownie."


def audit(minatar, recheck):
    m = minatar
    bo_n, as_n, se_n = m["breakout"]["network"]["mean"], m["asterix"]["network"]["mean"], m["seaquest"]["network"]["mean"]
    bo_r, as_r, se_r = m["breakout"]["rule"]["mean"], m["asterix"]["rule"]["mean"], m["seaquest"]["rule"]["mean"]
    bo_2 = recheck["mean"]
    f = lambda x: f"{x:.1f}"  # noqa: E731
    g = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
    return [
        dict(id="exp1", n=1, title_en="Which game was this network trained on?", title_pl="Na jakiej grze trenowano tę sieć?",
             chip_en="Correct, and a simple baseline sees the same signal", chip_pl="Trafne, a prosty baseline widzi ten sam sygnał",
             post_en="Astra names the game of four PPO networks from 17,253 weights pasted as text, with no tools.",
             post_pl="Astra nazywa grę czterech sieci PPO na podstawie 17 253 wag wklejonych jako tekst, bez narzędzi.",
             logs_en="4 of 4 correct, with confidence 96&ndash;99%. One line of numpy shows the same signal, as in the maps here and at the top of the page: unused input cells keep weights of median size about 0.4, against a maximum of 14&ndash;20. Astra's Breakout answer reads it the same way, with strong weights on row 8 and &ldquo;small initialization-scale values&rdquo; elsewhere.",
             logs_pl="4 z 4 trafnie, przy pewności 96&ndash;99%. Jedna linijka numpy pokazuje ten sam sygnał, jak na mapach tutaj i na górze strony: nieużywane komórki wejścia mają wagi o medianie około 0,4, a maksimum to 14&ndash;20. Odpowiedź Astry dla Breakouta czyta to tak samo: silne wagi w rzędzie 8, a gdzie indziej &bdquo;small initialization-scale values&rdquo;.",
             maps=True,
             read_en="Doing this from pasted text with no tools is a real feat for a language model. The claim &ldquo;well past what we'd expect from humans or conventional algorithms&rdquo; doesn't hold for this experiment, because the maps give a person or a short script the same signal. Whether people could name all four games from them wasn't tested.",
             read_pl="Zrobienie tego z wklejonego tekstu, bez narzędzi, to prawdziwy wyczyn jak na model językowy. Teza &bdquo;well past what we'd expect from humans or conventional algorithms&rdquo; w tym eksperymencie nie trzyma się, bo mapy dają człowiekowi albo krótkiemu skryptowi ten sam sygnał. Nie sprawdzano, czy ludzie nazwaliby z nich wszystkie cztery gry."),
        dict(id="exp2", n=2, title_en="What will this diffusion model generate?", title_pl="Co wygeneruje ten model dyfuzyjny?",
             chip_en="3 of 3, with three models", chip_pl="3 z 3, na trzech modelach",
             post_en="From the weights alone, Astra tells that three diffusion models generate circles, squares and triangles. It draws outlines although the models generate filled shapes, which the post reads as a sign that it reads geometry.",
             post_pl="Z samych wag Astra rozpoznaje, że trzy modele dyfuzyjne generują koła, kwadraty i trójkąty. Rysuje kontury, choć modele generują pełne kształty, co post traktuje jako znak, że czyta geometrię.",
             logs_en="3 of 3, with confidence 77&ndash;88%. Plotting the strongest units of the output layer as 12&times;12 images shows pieces of the shape's edge, so this signal also sits in plain view in one layer.",
             logs_pl="3 z 3, przy pewności 77&ndash;88%. Wykreślenie najsilniejszych jednostek warstwy wyjściowej jako obrazków 12&times;12 pokazuje fragmenty krawędzi kształtu, więc i ten sygnał leży na wierzchu w jednej warstwie.",
             read_en="A fair demonstration. Three models with one attempt each can't carry a general claim.",
             read_pl="Uczciwa demonstracja. Trzy modele po jednej próbie nie uniosą ogólnej tezy."),
        dict(id="exp3", n=3, title_en="What did a language model learn, from its middle layers alone?", title_pl="Czego nauczył się model językowy, sądząc tylko po środkowych warstwach?",
             chip_en="The strongest reading result", chip_pl="Najmocniejszy wynik czytania",
             post_en="With input and output layers removed and no forward pass allowed, Astra names the language of three small transformers in both attempts and finds every copying head.",
             post_pl="Bez warstw wejściowej i wyjściowej i bez przebiegu w przód Astra w obu próbach nazywa język trzech małych transformerów i znajduje wszystkie głowy kopiujące.",
             logs_en="10 of 10 copying-head answers are right, with no false positives. The ground truth separates cleanly: copying heads score 0.22&ndash;0.55, all others at most 0.02. The method is the weight-multiplication recipe from Elhage et al., as the post says, and the prompt defines the label (&ldquo;'copy' (induction: attends to the character right after an earlier occurrence&hellip;)&rdquo;). The language question is a forced choice among three named texts, answered with confidence 48&ndash;62%, on one network per language, so luck would get all three right in one pass about 4% of the time. Other head labels are weaker: 56 of 144 are &ldquo;unclear&rdquo;, and the two attempts agree on 19, 7 and 22 of 24 heads.",
             logs_pl="10 z 10 odpowiedzi o głowach kopiujących jest poprawnych, bez fałszywych trafień. Prawda rozdziela się czysto: głowy kopiujące mają 0,22&ndash;0,55, a pozostałe najwyżej 0,02. Metoda to przepis z mnożeniem wag z pracy Elhage i in., co post przyznaje, a prompt definiuje etykietę (&bdquo;'copy' (induction: attends to the character right after an earlier occurrence&hellip;)&rdquo;). Pytanie o język to wymuszony wybór spośród trzech nazwanych tekstów, z pewnością 48&ndash;62%, na jednej sieci na język, więc szczęście dałoby trzy trafienia w jednym podejściu w około 4% przypadków. Pozostałe etykiety głów są słabsze: 56 ze 144 to &bdquo;unclear&rdquo;, a obie próby zgadzają się dla 19, 7 i 22 z 24 głów.",
             read_en="Real evidence of reading structure from mid-network weights, with Python and a published recipe. It deserves a repeat on more networks per language.",
             read_pl="Prawdziwy dowód na czytanie struktury z wag środka sieci, z Pythonem i opublikowanym przepisem. Warto to powtórzyć na większej liczbie sieci na język."),
        dict(id="exp4", n=4, title_en="Fix a failing car policy by editing weights", title_pl="Napraw zepsutą politykę auta, edytując wagi",
             chip_en="Works, as a hand-written override", chip_pl="Działa, jako ręcznie wpisane sterowanie",
             post_en="In one reply with no tools, Astra edits 3.5% of the weights and the car succeeds in all 1,024 episodes, up from 0%.",
             post_pl="W jednej odpowiedzi, bez narzędzi, Astra edytuje 3,5% wag i auto wygrywa we wszystkich 1024 epizodach, a wcześniej w 0%.",
             logs_en="51 statements change 6,073 of 171,664 weights. The authors' result file gives <code>rel_change</code> 25.66, and the answer writes values like 80 and &minus;876. All 1,024 episodes return exactly 1.373849868774414 and last 73 steps, so this is one trajectory repeated. The added path holds control until the green wheel passes x = 0.95, which this audit places at about step 67&ndash;68 of 73, roughly 93% of the episode.",
             logs_pl="51 instrukcji zmienia 6073 ze 171 664 wag. Plik wynikowy autorów podaje <code>rel_change</code> 25,66, a odpowiedź wpisuje wartości takie jak 80 i &minus;876. Wszystkie 1024 epizody zwracają dokładnie 1,373849868774414 i trwają 73 kroki, więc to jedna powtórzona trajektoria. Dodana ścieżka trzyma sterowanie, aż zielone koło minie x = 0,95, co ten audyt umieszcza około kroku 67&ndash;68 z 73, czyli mniej więcej przez 93% epizodu.",
             read_en="A correct one-shot physics plan compiled into the network, which is impressive, and the post describes the path honestly. Still, &ldquo;3.5% of the weights&rdquo; undersells how much behaviour was replaced: the trained policy barely drives in the winning run.",
             read_pl="Poprawny za pierwszym razem plan fizyczny wkompilowany w sieć robi wrażenie, a post uczciwie opisuje tę ścieżkę. Mimo to &bdquo;3,5% wag&rdquo; zaniża skalę zmiany zachowania: wytrenowana polityka prawie nie prowadzi w wygranym przejeździe."),
        dict(id="exp5", n=5, title_en="Write game networks from scratch", title_pl="Napisz od zera sieci grające w gry",
             chip_en="Holds, and it beat Claude's attempt", chip_pl="Wynik stoi, a próba Claude'a przegrała",
             post_en="Given the rules and source code, with no feedback, Astra writes whole networks in one reply and beats PPO at 100M steps in all three games. The authors' thread adds that its Breakout network &ldquo;scored 20× higher than PPO trained for 500M steps&rdquo;.",
             post_pl="Mając zasady i kod źródłowy, bez informacji zwrotnej, Astra pisze całe sieci w jednej odpowiedzi i bije PPO po 100 mln kroków we wszystkich trzech grach. Wątek autorów dodaje, że sieć do Breakouta &bdquo;scored 20× higher than PPO trained for 500M steps&rdquo;.",
             logs_en=f"The table matches the authors' evaluation file, and the tool audit shows no tool calls. Only 815, 803 and 637 of 20,486 weights are nonzero: these are designed programs compiled into a network, with saturated gates such as &plusmn;1000 in Breakout. The PPO baselines are weak: after 100M steps they end Breakout in under 180 steps on average. The thread's 20× is Breakout only (517.4 against 25.3). At 500M steps Astra beats PPO's median seed in all three games, while PPO's best seed still scores higher on Asterix and Seaquest. <strong>Exploratory control, added after the plan:</strong> Claude wrote short rule-based programs once, from the same source files, with no game runs before scoring and no tuning afterwards. They lost to Astra in all three games. Astra's networks re-scored with the same code give {f(as_n)} and {f(se_n)} on Asterix and Seaquest, matching the published means. Breakout came out at {f(bo_n)} and then {f(bo_2)} on new seeds, about 4% under the published 517.4, and the cause is unknown.",
             logs_pl=f"Tabela zgadza się z plikiem ewaluacji autorów, a audyt narzędzi nie pokazuje żadnych wywołań. Niezerowych jest tylko 815, 803 i 637 z 20 486 wag: to zaprojektowane programy wkompilowane w sieć, z nasyconymi bramkami, np. &plusmn;1000 w Breakoucie. Punkty odniesienia PPO są słabe: po 100 mln kroków kończą Breakouta średnio przed 180. krokiem. Te 20× z wątku dotyczy tylko Breakouta (517,4 wobec 25,3). Po 500 mln kroków Astra bije medianowe ziarno PPO we wszystkich trzech grach, a najlepsze ziarno PPO nadal zdobywa więcej w Asterixie i Seaquest. <strong>Kontrola eksploracyjna, dodana po planie:</strong> krótkie programy regułowe napisane przez Claude'a raz, z tych samych plików źródłowych, bez uruchamiania gry przed pomiarem i bez późniejszego dostrajania. Przegrały z Astrą we wszystkich trzech grach. Sieci Astry policzone tym samym kodem dają {g(as_n)} i {g(se_n)} w Asterixie i Seaquest, zgodnie z opublikowanymi średnimi. Breakout wyszedł {g(bo_n)}, a potem {g(bo_2)} na nowych ziarnach, około 4% poniżej opublikowanych 517,4, a przyczyny nie ustalono.",
             table="minatar",
             read_en="The strongest writing result, and it passed a check meant to deflate it. This is programming with weights as the target language, which is what the post's title says. Reading existing weights plays no part here.",
             read_pl="Najmocniejszy wynik pisania, który przeszedł kontrolę mającą go osłabić. To programowanie, w którym językiem docelowym są wagi, czyli dokładnie to, co mówi tytuł posta. Czytanie istniejących wag nie gra tu żadnej roli."),
        dict(id="exp6", n=6, title_en="Write a Go network", title_pl="Napisz sieć grającą w go",
             chip_en="Holds, absolute strength unknown", chip_pl="Wynik stoi, bezwzględna siła nieznana",
             post_en="On a 1.5M-weight network, budget 0 wins more than half its games against two small PPO networks. With 50 forward passes it beats a same-size PPO network.",
             post_pl="W sieci z 1,5 mln wag budżet 0 wygrywa ponad połowę partii z dwiema małymi sieciami PPO. Z 50 przebiegami w przód bije sieć PPO tej samej wielkości.",
             logs_en="Budget 0: 54.1% and 54.9%. Budget 50: 84.0% and 80.8%. Against same-size PPO seeds: 42.6, 26.3 and 36.3% at budget 0, and 74.2, 70.0 and 78.5% at budget 50. One run per budget. There's no visible overfit to the practice opponent. Wins come with margins of about +51 on an 81-point board and about 63 stones captured per game, so these opponents are weak, and the logs have no outside yardstick such as GNU Go.",
             logs_pl="Budżet 0: 54,1% i 54,9%. Budżet 50: 84,0% i 80,8%. Przeciw ziarnom PPO tej samej wielkości: 42,6, 26,3 i 36,3% przy budżecie 0 oraz 74,2, 70,0 i 78,5% przy budżecie 50. Jeden przebieg na budżet. Nie widać przeuczenia do przeciwnika treningowego. Wygrane mają przewagę około +51 na planszy z 81 punktami i około 63 zbite kamienie na partię, więc ci przeciwnicy są słabi, a w logach nie ma zewnętrznej miary, np. GNU Go.",
             read_en="A hand-built Go heuristic that improves with feedback is a solid result. How strong it is in absolute terms stays open.",
             read_pl="Ręcznie zbudowana heurystyka do go, która poprawia się dzięki informacji zwrotnej, to solidny wynik. Jej bezwzględna siła pozostaje otwarta."),
        dict(id="exp7", n=7, title_en="Which language model is sycophantic?", title_pl="Który model językowy jest lizusem?",
             chip_en="Failed from weights, as the post says", chip_pl="Z samych wag się nie udało, co post przyznaje",
             post_en="From weights alone, Astra could not tell which Gemma copy is the sycophant, in four attempts. With a tool that shows attention patterns, it picks right in all three pairs.",
             post_pl="Z samych wag Astra nie potrafiła wskazać lizusa wśród kopii Gemmy w czterech próbach. Z narzędziem pokazującym wzorce uwagi trafia we wszystkich trzech parach.",
             logs_en="Attempts 1&ndash;3 answer P = 0.5 on every pair, and attempt 4 was stopped undecided. With the attention tool the confidence is 90%, 97% and 55%, and on pair 3 Astra calls its own answer &ldquo;a weak, subjective judgment&rdquo;. A causal check the post doesn't show, run for the tool round on pair 1 only: patching the components Astra named closes 0.04 of the margin, the largest weight changes 0.08, and random components 0.19 on average.",
             logs_pl="Próby 1&ndash;3 dają P = 0,5 dla każdej pary, a próbę 4 przerwano bez rozstrzygnięcia. Z narzędziem uwagi pewność to 90%, 97% i 55%, a przy parze 3 Astra sama nazywa swoją odpowiedź &bdquo;a weak, subjective judgment&rdquo;. Kontrola przyczynowa, której post nie pokazuje, dla rundy z narzędziem zrobiona tylko na parze 1: podmiana składników wskazanych przez Astrę zamyka 0,04 marginesu, największe zmiany wag 0,08, a losowe składniki średnio 0,19.",
             read_en="This is the only test of reading a behaviour from weights alone in a large model, and it failed. The attention tool is a forward pass with a restricted readout: useful interpretability, and no longer weight reading. The post's outlook (&ldquo;Auditing without evaluation&rdquo;, backdoors found from the weights) gets no support from this experiment so far.",
             read_pl="To jedyny test odczytania zachowania z samych wag w dużym modelu i nie wyszedł. Narzędzie uwagi to przebieg w przód z ograniczonym odczytem: przydatna interpretowalność, ale już nie czytanie wag. Wizja z końca posta (&bdquo;Auditing without evaluation&rdquo;, tylne furtki znajdowane z wag) nie ma w tym eksperymencie na razie oparcia."),
        dict(id="exp8", n=8, title_en="Make a language model better at math", title_pl="Popraw model językowy w matematyce",
             chip_en="Real effect, one run, in the looping mode", chip_pl="Prawdziwy efekt, jeden przebieg, w trybie z pętlami",
             post_en="With 50 forward passes, Astra traces looping to one direction written by the MLPs of layers 15 and 19 and subtracts it from 64 output columns in each. MATH-500 goes 7.9 to 48.1, GSM8K 13.8 to 67.1, IFEval 21.0 to 62.3.",
             post_pl="Z 50 przebiegami w przód Astra wiąże pętle z jednym kierunkiem zapisywanym przez MLP warstw 15 i 19 i odejmuje go z 64 kolumn wyjściowych w każdej. MATH-500 rośnie z 7,9 do 48,1, GSM8K z 13,8 do 67,1, IFEval z 21,0 do 62,3.",
             logs_en="<strong>The edit:</strong> <code>W = W0 - 6*outer(u, mask64*(u@W0))</code>, a relative change of 10.6% and 8.1%, with the direction taken from matched repetitive and productive activation contexts. <strong>The prompt:</strong> the authors' thread says &ldquo;We simply asked Astra to make Qwen3.5-0.8B better at math&rdquo; and &ldquo;Astra saw Qwen get stuck in reasoning loops&rdquo;. The prompt, public in the post's trace viewer, already points there: &ldquo;if the model often fails because it repeats itself and never finishes, finding and fixing what drives that repetition counts&rdquo;, and &ldquo;(often while repeating itself in its thinking)&rdquo;. The prompts of the 10-, 25- and 50-pass runs differ only in the budget, so the jump at 50 passes isn't a prompt effect. <strong>The effort:</strong> 34 generation and 16 teacher-forced passes, about 6,000 answers, 158 turns, 80 Python runs, 20.3 hours. <strong>Astra's own held-out test:</strong> 1,152 practice problems go from 10.6% to 60.4% (+49.8 &plusmn; 1.5), 579 rescued against 5 lost, and a random-direction control gives +1.56 &plusmn; 3.52. Answers that already finished stay at 93.9%, and answers that were cut go from 1.4% to 56.7%. <strong>The runs:</strong> of 7 completed Qwen runs, six add at most 6.2 points on MATH-500. The single 50-pass run adds 40.2.",
             logs_pl="<strong>Edycja:</strong> <code>W = W0 - 6*outer(u, mask64*(u@W0))</code>, zmiana względna 10,6% i 8,1%, a kierunek pochodzi z dopasowanych kontekstów aktywacji: powtarzających się i produktywnych. <strong>Prompt:</strong> wątek autorów mówi &bdquo;We simply asked Astra to make Qwen3.5-0.8B better at math&rdquo; i &bdquo;Astra saw Qwen get stuck in reasoning loops&rdquo;. Prompt, jawny w przeglądarce śladów posta, sam tam prowadzi: &bdquo;if the model often fails because it repeats itself and never finishes, finding and fixing what drives that repetition counts&rdquo;, a także &bdquo;(often while repeating itself in its thinking)&rdquo;. Prompty przebiegów z 10, 25 i 50 przejściami różnią się tylko budżetem, więc skok przy 50 przejściach nie wynika z promptu. <strong>Nakład:</strong> 34 przebiegi z generowaniem i 16 z wymuszonym tekstem, około 6000 odpowiedzi, 158 tur, 80 uruchomień Pythona, 20,3 godziny. <strong>Własny test Astry na odłożonych danych:</strong> 1152 zadania ćwiczebne idą z 10,6% do 60,4% (+49,8 &plusmn; 1,5), 579 uratowanych wobec 5 straconych, a kontrola z losowym kierunkiem daje +1,56 &plusmn; 3,52. Odpowiedzi, które już się kończyły, zostają na 93,9%, a ucinane idą z 1,4% do 56,7%. <strong>Przebiegi:</strong> z 7 ukończonych przebiegów na Qwen sześć dodaje najwyżej 6,2 pkt na MATH-500. Jedyny przebieg z 50 przejściami dodaje 40,2.",
             read_en="The effect is real, held out, and has good internal controls. The whole gain comes from answers that used to be cut off, which the post says too: &ldquo;Fixing loops, however, is not the same as making a model better at math.&rdquo; It rests on one run, and nobody has checked whether Astra would find it again.",
             read_pl="Efekt jest prawdziwy, sprawdzony na odłożonych danych i ma dobre kontrole wewnętrzne. Cały zysk pochodzi z odpowiedzi, które wcześniej były ucinane, co mówi też sam post: &bdquo;Fixing loops, however, is not the same as making a model better at math.&rdquo; Opiera się na jednym przebiegu i nikt nie sprawdził, czy Astra znalazłaby to ponownie."),
    ]


OVERALL = (
    P("The post files everything under one name, weight-space programming. The logs show three different things, all impressive for a general-purpose LLM.",
      "Post zbiera wszystko pod jedną nazwą: programowanie w przestrzeni wag. Logi pokazują trzy różne rzeczy, wszystkie robiące wrażenie jak na ogólny LLM.")
    + '<div class="skills">'
    + f'<div class="skill"><h3>{T("Reading plain signals", "Czytanie jawnych sygnałów")}</h3><p class="which">{T("Exp 1, 2, partly 3", "Eksp. 1, 2, częściowo 3")}</p>'
    + P("The signal sits in one layer or follows a published recipe. A short script can expose much of it.", "Sygnał siedzi w jednej warstwie albo wynika z opublikowanego przepisu. Krótki skrypt potrafi wydobyć dużą jego część.") + "</div>"
    + f'<div class="skill"><h3>{T("Compiling designed programs into weights", "Kompilowanie zaprojektowanych programów do wag")}</h3><p class="which">{T("Exp 4, 5, 6", "Eksp. 4, 5, 6")}</p>'
    + P("The model reasons about the task, then writes the program as a network. It doesn't need to read trained weights to do this.", "Model rozumuje o zadaniu, a potem zapisuje program jako sieć. Nie musi do tego czytać wytrenowanych wag.") + "</div>"
    + f'<div class="skill"><h3>{T("Autonomous interpretability with activations", "Samodzielna interpretowalność na aktywacjach")}</h3><p class="which">{T("Exp 8, Exp 7 with the tool", "Eksp. 8, eksp. 7 z narzędziem")}</p>'
    + P("Many forward passes, activation measurements, and an edit in the style of known direction-removal methods. The novelty is the autonomy.", "Wiele przebiegów w przód, pomiary aktywacji i edycja w stylu znanych metod usuwania kierunku. Nowością jest samodzielność.") + "</div>"
    + "</div>"
    + P("Reading a behaviour from the weights alone in a large model is the capability the outlook needs for auditing, and it has one test so far, Exp 7, which failed.",
        "Odczytanie zachowania z samych wag w dużym modelu to umiejętność, której wizja audytu potrzebuje najbardziej. Jak dotąd ma jeden test, eksperyment 7, i ten test nie wyszedł.")
)

CREDIT = UL([
    ("<strong>The logs are public and complete enough to audit.</strong> This page exists because of them. They include the failures, the causal check that doesn't flatter Astra, and code comments that show the path to the result.",
     "<strong>Logi są publiczne i na tyle pełne, że da się je audytować.</strong> Ta strona powstała dzięki nim. Zawierają porażki, kontrolę przyczynową, która nie schlebia Astrze, i komentarze w kodzie pokazujące drogę do wyniku."),
    ("<strong>The post states its own limits.</strong> It reports the failure of Exp 7, the failure on Gemma, and says outright that fixing loops isn't the same as making a model better at math.",
     "<strong>Post sam podaje swoje granice.</strong> Opisuje porażkę eksperymentu 7, porażkę na Gemmie i wprost mówi, że naprawa pętli to nie to samo, co poprawa w matematyce."),
    ("<strong>Exp 3 and Exp 5 are hard to wave away.</strong> Copying heads found from weights with no false positives, and zero-feedback networks that beat a one-shot attempt written to deflate them.",
     "<strong>Eksperymentów 3 i 5 nie da się łatwo zbyć.</strong> Głowy kopiujące znalezione z wag bez fałszywych trafień i sieci bez informacji zwrotnej, które pobiły jednorazową próbę napisaną po to, by je osłabić."),
    ("<strong>Exp 8 is real engineering.</strong> An LLM with no gradients found one fix, kept a random control and a held-out set, and the fix works on benchmarks it never saw.",
     "<strong>Eksperyment 8 to prawdziwa inżynieria.</strong> LLM bez gradientów znalazł jedną naprawę, zachował kontrolę losową i zbiór odłożony, a naprawa działa na benchmarkach, których nigdy nie widział."),
])

OPEN = UL([
    ("Publish the scores of the thinking-off edit runs that the code comments mention.", "Opublikować wyniki przebiegów edycji z wyłączonym myśleniem, o których mówią komentarze w kodzie."),
    ("Repeat the 50-pass run several times. One run can't show how often Astra finds this fix.", "Powtórzyć przebieg z 50 przejściami kilka razy. Jeden przebieg nie pokaże, jak często Astra znajduje tę naprawę."),
    ("Measure the edit at T 1.0 on all 500 problems with 4 samples, and on IFEval. This test used 100 problems with one sample.", "Zmierzyć edycję przy T 1,0 na wszystkich 500 zadaniach z 4 próbkami i na IFEval. Ten test użył 100 zadań po jednej próbce."),
    ("Score the Go networks against an outside engine such as GNU Go.", "Ocenić sieci do go względem zewnętrznego silnika, np. GNU Go."),
    ("Run a weights-only behaviour test with more pairs and a planted trait people care about, such as a backdoor.", "Zrobić test odczytu zachowania z samych wag na większej liczbie par i z zaszytą cechą, na której komuś zależy, np. tylną furtką."),
])

LIMITS = UL([
    ("<strong>Small sample.</strong> Thinking-on rows use 100 problems with one sample each, so intervals are wide, around &plusmn;10 points, and the calibration rule can only catch large differences from the authors' runs.",
     "<strong>Mała próba.</strong> Wiersze z włączonym myśleniem to 100 zadań po jednej próbce, więc przedziały są szerokie, około &plusmn;10 punktów, a reguła kalibracji wychwyci tylko duże różnice względem przebiegów autorów."),
    ("<strong>The plan isn't externally timestamped.</strong> Its hash is recorded locally, so the order of events is a claim you have to trust. It was also written after reading the post and logs.",
     "<strong>Plan nie ma zewnętrznego znacznika czasu.</strong> Jego hash jest zapisany lokalnie, więc kolejność zdarzeń trzeba przyjąć na wiarę. Powstał też po przeczytaniu posta i logów."),
    ("<strong>Thinking off is a different mode.</strong> It isn't the setting the post evaluates, and its token cap is a quarter of the thinking-on cap. The model card also scores thinking-on higher on some benchmarks, such as MMLU-Pro.",
     "<strong>Wyłączone myślenie to inny tryb.</strong> Post ocenia inne ustawienie, a limit tokenów jest tu cztery razy niższy niż z włączonym myśleniem. Karta modelu daje też włączonemu myśleniu wyższe wyniki na niektórych benchmarkach, np. MMLU-Pro."),
    ("<strong>Only the published weights were tested.</strong> Astra wasn't re-run, so nothing here says how repeatable its process is.",
     "<strong>Testowano tylko opublikowane wagi.</strong> Astry nie uruchamiano ponownie, więc nic tu nie mówi o powtarzalności jej procesu."),
    ("<strong>Claude isn't a neutral party.</strong> Claude Opus 5.5 did this analysis and wrote this page. Anthropic, which makes Claude, competes with OpenAI, whose model the post tests.",
     "<strong>Claude nie jest stroną neutralną.</strong> Tę analizę i stronę przygotował Claude Opus 5.5. Anthropic, twórca Claude'a, konkuruje z OpenAI, którego model testuje post."),
])


def method(sha):
    return (
        UL([
            ("<strong>Models.</strong> <code>Qwen/Qwen3.5-0.8B</code> at revision <code>2fc06364</code>, text-only export with the authors' config. The edited model is the authors' published <code>p50c</code> diff. Tensors match the sha256 values in their manifest.",
             "<strong>Modele.</strong> <code>Qwen/Qwen3.5-0.8B</code> w rewizji <code>2fc06364</code>, eksport tekstowy z konfiguracją autorów. Model z edycją to opublikowany przez autorów diff <code>p50c</code>. Tensory zgadzają się z sumami sha256 z ich manifestu."),
            ("<strong>Generation.</strong> vLLM 0.33.0, bfloat16, RTX 4060 8 GB, at most 10 concurrent answers with thinking on and 32 with thinking off, per-sample seeds as in the authors' <code>evaluate.py</code>, no early stopping of loops.",
             "<strong>Generowanie.</strong> vLLM 0.33.0, bfloat16, RTX 4060 8 GB, najwyżej 10 równoczesnych odpowiedzi z myśleniem i 32 bez niego, ziarna na próbkę jak w <code>evaluate.py</code> autorów, bez wczesnego przerywania pętli."),
            ("<strong>Grading.</strong> The authors' <code>mathqa.py</code>, which reproduced their grades on 400 of 400 published samples.",
             "<strong>Ocenianie.</strong> <code>mathqa.py</code> autorów, który odtworzył ich oceny na 400 z 400 opublikowanych próbek."),
            ("<strong>Statistics.</strong> 95% percentile bootstrap over problems, 10,000 resamples. Paired differences use the problems both conditions share.",
             "<strong>Statystyka.</strong> 95% percentylowy bootstrap po zadaniach, 10 000 losowań. Różnice sparowane liczone są na zadaniach wspólnych dla obu warunków."),
            (f"<strong>Plan.</strong> Frozen before the first measured answer, at 23:15:40 local time on November 2, 2026. sha256 <code class=\"hash\">{sha}</code>. All conditions are reported.",
             f"<strong>Plan.</strong> Zamrożony przed pierwszą mierzoną odpowiedzią, 2 listopada 2026 o 23:15:40 czasu lokalnego. sha256 <code class=\"hash\">{sha}</code>. Podane są wszystkie warunki."),
            ("<strong>Changes from the plan.</strong> Listed in full below it. The main ones: a later deadline and a new running order, both set before any thinking-on condition had run, so that the decision rules could be applied. The Exp 1 maps, the MinAtar control and the edited model with thinking off were added after the plan and are exploratory.",
             "<strong>Zmiany względem planu.</strong> Pełna lista jest pod nim. Najważniejsze: późniejszy termin i nowa kolejność, ustalone przed startem warunków z włączonym myśleniem, aby dało się zastosować reguły decyzyjne. Mapy z eksperymentu 1, kontrola MinAtar i model z edycją przy wyłączonym myśleniu doszły po planie i są eksploracyjne."),
        ])
    )


FOOT = (
    P('Sources: <a href="https://rikiyat.github.io/blog/weight-space-programming/">the post</a> (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, November 2, 2026), '
      '<a href="https://x.com/rikiyatakehi/status/2117313742891327994">the authors\' thread on X</a>, '
      '<a href="https://www.alphaxiv.org/abs/2611.weight-space-programming">its alphaXiv page</a>, '
      '<a href="https://github.com/RikiyaT/lm_understand-logs">the authors\' logs</a>, '
      '<a href="https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/main/README.md">the Qwen3.5-0.8B model card</a>.',
      'Źródła: <a href="https://rikiyat.github.io/blog/weight-space-programming/">post</a> (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, 2 listopada 2026), '
      '<a href="https://x.com/rikiyatakehi/status/2117313742891327994">wątek autorów na X</a>, '
      '<a href="https://www.alphaxiv.org/abs/2611.weight-space-programming">strona na alphaXiv</a>, '
      '<a href="https://github.com/RikiyaT/lm_understand-logs">logi autorów</a>, '
      '<a href="https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/main/README.md">karta modelu Qwen3.5-0.8B</a>.')
    + P("Independent work, not affiliated with the authors, OpenAI, Qwen or MIT. Analysis, code and page: Claude Opus 5.5.",
        "Praca niezależna, niezwiązana z autorami, OpenAI, Qwen ani MIT. Analiza, kod i strona: Claude Opus 5.5.")
)


