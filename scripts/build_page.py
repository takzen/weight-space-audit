"""Builds the bilingual results page from results/summary.json, so no measured number is typed by hand.

  python build_page.py <out.html> [<results_dir>] [--standalone] [--card=map|og --lang=en|pl]

--standalone writes a full HTML document with link-preview tags, for GitHub Pages. Without it, the file is the page body that
the Artifact host wraps. --card writes one fixed-size image page in one language, in the light theme, for render_cards.sh to
turn into a PNG. page_text.py and page_final.py hold the prose.
"""
import hashlib
import html
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import page_final  # noqa: E402
import page_text as W  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0]
RESULTS = Path(args[1]) if len(args) > 1 else ROOT / "results"
STANDALONE = "--standalone" in sys.argv
PAGES_URL = "https://takzen.github.io/weight-space-audit/"

with open(RESULTS / "summary.json", encoding="utf-8") as f:
    SUMMARY = json.load(f)
with open(ROOT / "results_exploratory" / "exp1_maps.json", encoding="utf-8") as f:
    MAPS = json.load(f)
with open(ROOT / "results_exploratory" / "minatar.json", encoding="utf-8") as f:
    MINATAR = json.load(f)
with open(ROOT / "results_exploratory" / "breakout_recheck.txt", encoding="utf-8") as f:
    RECHECK = json.loads(f.readline())
PLAN_PATH = ROOT / "PLAN.md"
PLAN_BYTES = PLAN_PATH.read_bytes() if PLAN_PATH.exists() else None
PLAN_SHA = hashlib.sha256(PLAN_BYTES).hexdigest() if PLAN_BYTES else (ROOT / "logs" / "plan_sha256.txt").read_text(encoding="utf-8").split()[0]
DEVIATIONS = (ROOT / "DEVIATIONS.md").read_text(encoding="utf-8")

MATH = SUMMARY["math500"]


def T(en, pl):
    return f'<span lang="en">{en}</span><span lang="pl">{pl}</span>'


def P(en, pl, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<p lang="en"{c}>{en}</p><p lang="pl"{c}>{pl}</p>'


def num(x, d=1):
    """A number in both languages (Polish uses a decimal comma)."""
    s = f"{x:.{d}f}"
    return T(s, s.replace(".", ","))


def bin_of(v, median, top):
    """Log scale from the typical size of an unused cell to the largest cell; 8 classes."""
    if v <= median * 1.2:
        return 0
    t = math.log(v / (median * 1.2)) / math.log(top / (median * 1.2))
    return min(7, 1 + int(t * 7))


def board(game, channel, label_en, label_pl, cls=""):
    m = MAPS[game]
    grid = m["channels"][channel]
    cells = "".join(f'<i class="h{bin_of(v, m["median"], m["max"])}" data-v="{v:.2f}"></i>' for row in grid for v in row)
    return (f'<figure class="board {cls}"><div class="grid10" role="img" aria-label="{html.escape(label_en)}">{cells}</div>'
            f'<figcaption>{T(label_en, label_pl)}</figcaption></figure>')


def card_table():
    rows = W.CARD_ROWS
    body = "".join(f'<tr><th scope="row">{r[0]}</th>' + "".join(f"<td>{num(v) if v is not None else '–'}</td>" for v in r[1:]) + "</tr>" for r in rows)
    return (f'<div class="scroll"><table class="data num"><thead><tr><th scope="col">{T("Benchmark", "Benchmark")}</th>'
            f'<th scope="col">{T("Card, thinking off", "Karta, myślenie wyłączone")}</th>'
            f'<th scope="col">{T("Card, thinking on, T 1.0", "Karta, myślenie włączone, T 1,0")}</th>'
            f'<th scope="col">{T("Post, unedited, T 0.6", "Post, bez edycji, T 0,6")}</th>'
            f'<th scope="col">{T("Post, edited, T 0.6", "Post, z edycją, T 0,6")}</th></tr></thead><tbody>{body}</tbody></table></div>')


def minatar_table():
    published = {"breakout": (15.8, 25.3, 517.4), "asterix": (25.8, 55.2, 53.2), "seaquest": (5.6, 88.9, 53.1)}
    names = {"breakout": "Breakout", "asterix": "Asterix", "seaquest": "Seaquest"}
    rows = []
    for g, name in names.items():
        a, b, c = published[g]
        net = MINATAR[g]["network"]
        rule = MINATAR[g]["rule"]
        rows.append(f'<tr><th scope="row">{name}</th><td>{num(a)}</td><td>{num(b)}</td><td>{num(c)}</td>'
                    f'<td>{num(net["mean"])}</td><td>{num(rule["mean"])}</td></tr>')
    return (f'<div class="scroll"><table class="data num"><thead><tr><th scope="col">{T("Game", "Gra")}</th>'
            f'<th scope="col">PPO 100M <small>{T("best seed", "najlepsze ziarno")}</small></th>'
            f'<th scope="col">PPO 500M <small>{T("best seed", "najlepsze ziarno")}</small></th>'
            f'<th scope="col">Astra <small>{T("published", "opublikowane")}</small></th>'
            f'<th scope="col">Astra <small>{T("re-scored here", "policzone tutaj")}</small></th>'
            f'<th scope="col">{T("Claude&#39;s rule", "Reguła Claude&#39;a")} <small>{T("one attempt, this test", "jedna próba, ten test")}</small></th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


VERDICT_ICONS = {"yes": "✓", "part": "◐", "no": "✕", "fore": "?"}


def claim_rows():
    out = []
    for i, c in enumerate(n["claims"], 1):
        out.append(
            f'<article class="claim"><div class="claim-q"><span class="claim-n">{i}</span>'
            f'<blockquote lang="en">&ldquo;{c["q_en"]}&rdquo;</blockquote><blockquote lang="pl">{c["q_pl"]}</blockquote></div>'
            f'<div class="claim-a"><p class="verdict"><span class="chip v-{c["kind"]}"><b aria-hidden="true">{VERDICT_ICONS[c["kind"]]}</b>{T(c["v_en"], c["v_pl"])}</span></p>'
            + "".join(P(a, b) for a, b in zip(*[[x] if isinstance(x, str) else x for x in (c["why_en"], c["why_pl"])])) + '</div></article>')
    return "".join(out)


def audit():
    out = []
    for r in W.audit(MINATAR, RECHECK):
        extra = ""
        if r.get("maps"):
            extra += ('<div class="boards">'
                      + board("breakout", "agent", "Breakout, agent channel: the paddle row", "Breakout, kanał agenta: rząd paletki")
                      + board("breakout", "reward", "Breakout, reward channel: the brick rows", "Breakout, kanał nagród: rzędy cegieł")
                      + board("pong", "agent", "Pong, agent channel: the paddle column", "Pong, kanał agenta: kolumna paletki")
                      + board("freeway", "moving", "Freeway, moving objects: the lanes", "Freeway, obiekty ruchome: pasy ruchu")
                      + "</div>")
        if r.get("table") == "minatar":
            extra += minatar_table()
        out.append(
            f'<article class="exp" id="{r["id"]}"><header><span class="exp-id">{T("Exp", "Eksp.")} {r["n"]}</span>'
            f'<h3>{T(r["title_en"], r["title_pl"])}</h3><span class="chip">{T(r["chip_en"], r["chip_pl"])}</span></header>'
            f'<div class="exp-cols"><div><h4>{T("The post", "Post")}</h4>{P(r["post_en"], r["post_pl"])}</div>'
            f'<div><h4>{T("The logs", "Logi")}</h4>{P(r["logs_en"], r["logs_pl"])}</div></div>{extra}'
            f'<div class="reading"><h4>{T("Reading", "Ocena")}</h4>{P(r["read_en"], r["read_pl"])}</div></article>')
    return "".join(out)


CTX = dict(math=MATH, dec=MATH["decisions"], minatar=MINATAR, recheck=RECHECK)
hero_map = board("pacman", "agent", "Pac-Man, agent channel", "Pac-Man, kanał agenta", "hero-map")
pac = MAPS["pacman"]
scale = "".join(f'<i class="h{i}"></i>' for i in range(8))
n = page_final.narrative(CTX)
strip = "".join(
    f'<div class="stat"><div class="stat-v">{num(v)}%</div><div class="stat-l">{T(a, b)}</div></div>' for v, a, b in n["strip"])

plan_block = (f'<details class="values plan"><summary>{T("The plan as frozen before the run (in English)", "Plan zamrożony przed przebiegiem (po angielsku)")}</summary>'
              f'<pre>{html.escape(PLAN_BYTES.decode("utf-8"))}</pre></details>') if PLAN_BYTES else ""

PAGE = f"""<title>Weight-Space Sparks Audit</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,650;12..96,750&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>{W.CSS}</style>
<div class="wrap">
<nav class="top" aria-label="{html.escape('Language')}">
  <span class="top-l">{T("Independent check of a public post", "Niezależne sprawdzenie publicznego posta")} · {T("November 3, 2026", "3 listopada 2026")}</span>
  <span class="langs" role="group"><button type="button" id="b-en" data-l="en">EN</button><button type="button" id="b-pl" data-l="pl">PL</button></span>
</nav>
<header class="hero">
  <div class="hero-text">
    <h1>{T(n["h1_en"], n["h1_pl"])}</h1>
    {P(n["lead_en"], n["lead_pl"], "lead")}
    {W.UL(page_final.findings(CTX), "bul findings")}
    <div class="strip">{strip}</div>
    {P(n["strip_note_en"], n["strip_note_pl"], "note")}
    {P(W.DISCLOSE_EN, W.DISCLOSE_PL, "note")}
  </div>
  <div class="hero-fig">
    {hero_map}
    <p class="fig-code"><code>np.linalg.norm(W1, axis=1).reshape(10, 10, 5)[:, :, 0]</code></p>
    {P("One line of numpy, with no LLM and without running the network: the size of the first-layer weights per input cell draws the maze. A cell the agent never visits keeps its small starting weights.",
       "Jedna linijka numpy, bez LLM i bez uruchamiania sieci: rozmiar wag pierwszej warstwy na komórkę wejścia rysuje labirynt. Komórka, w której agent nigdy nie bywa, zachowuje małe wagi startowe.", "fig-note")}
    <div class="scale" aria-hidden="true"><span>{T("≈ 0.4", "≈ 0,4")}</span><div class="scale-bar">{scale}</div><span>{num(pac["max"])}</span></div>
  </div>
</header>
<main>
<section id="claims"><h2>{T("Their claim, sentence by sentence", "Ich teza, zdanie po zdaniu")}</h2>
  {P(W.CLAIMS_INTRO_EN, W.CLAIMS_INTRO_PL)}
  <div class="claims">{claim_rows()}</div>
</section>
<section id="authors"><h2>{T("The authors ran into this first", "Autorzy trafili na to pierwsi")}</h2>{W.AUTHORS_CODE}</section>
<section id="credit"><h2>{T("What deserves credit", "Co trzeba docenić")}</h2>{W.CREDIT}</section>
<section id="limits"><h2>{T("What this check didn&rsquo;t do", "Czego to sprawdzenie nie zrobiło")}</h2>{W.UL(page_final.limits(CTX))}</section>
<section id="details"><h2>{T("Details", "Szczegóły")}</h2>
  <details class="more"><summary>{T("What the logs show, experiment by experiment", "Co pokazują logi, eksperyment po eksperymencie")}</summary><div class="more-body">
    {P(W.AUDIT_INTRO_EN, W.AUDIT_INTRO_PL)}
    {audit()}
    <h3 class="sub">{T("One name, three skills", "Jedna nazwa, trzy umiejętności")}</h3>
    {W.OVERALL}
  </div></details>
  <details class="more"><summary>{T("The model card&#39;s own numbers", "Liczby z karty modelu")}</summary><div class="more-body">
    {P(W.CARD_INTRO_EN, W.CARD_INTRO_PL)}
    {card_table()}
    {P(W.CARD_NOTE_EN, W.CARD_NOTE_PL, "fig-note")}
  </div></details>
  <details class="more"><summary>{T("Method and changes from the plan", "Metoda i zmiany względem planu")}</summary><div class="more-body">
    {W.method(PLAN_SHA)}
    {plan_block}
    <details class="values plan"><summary>{T("Every change from the plan (in English)", "Każda zmiana względem planu (po angielsku)")}</summary>
    <pre>{html.escape(DEVIATIONS)}</pre></details>
  </div></details>
</section>
</main>
<footer class="foot">{W.FOOT}</footer>
</div>
<div id="tip" role="status" hidden></div>
<script>{W.JS}</script>
"""


def card(kind, lang):
    """A fixed-size page for one image, with the same numbers and maps as the main page."""
    if kind == "og":
        inner = (f'<h1>{T(n["h1_en"], n["h1_pl"])}</h1><div class="strip">{strip}</div>'
                 f'<p class="card-foot">{T("An independent check of &ldquo;Sparks of Weight-Space Programming&rdquo;", "Niezależne sprawdzenie &bdquo;Sparks of Weight-Space Programming&rdquo;")}</p>')
    else:
        inner = (f'<h1>{T("One line of numpy draws the game from the weights", "Jedna linijka numpy rysuje grę z samych wag")}</h1>'
                 f'<div class="card-maps">{board("pacman", "agent", "Pac-Man, agent channel: the maze", "Pac-Man, kanał agenta: labirynt", "card-big")}'
                 f'<div class="card-small">'
                 + board("breakout", "agent", "Breakout, agent: the paddle row", "Breakout, agent: rząd paletki")
                 + board("breakout", "reward", "Breakout, reward: the bricks", "Breakout, nagrody: cegły")
                 + board("pong", "agent", "Pong, agent: the paddle column", "Pong, agent: kolumna paletki")
                 + board("freeway", "moving", "Freeway, moving: the lanes", "Freeway, ruch: pasy")
                 + f'</div></div><p class="card-code"><code>np.linalg.norm(W1, axis=1).reshape(10, 10, 5)</code></p>'
                 f'<p class="card-foot">{T("Size of the first-layer weights per input cell of four PPO policies, with no LLM and without running the networks. Cells the agent never uses keep their small starting weights.", "Rozmiar wag pierwszej warstwy na komórkę wejścia czterech polityk PPO, bez LLM i bez uruchamiania sieci. Komórki, których agent nie używa, zachowują małe wagi startowe.")}</p>')
    return (f'<!doctype html>\n<html lang="{lang}" data-lang="{lang}" data-theme="light"><head><meta charset="utf-8">'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,650;12..96,750&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">'
            f'<style>{W.CSS}{W.CARD_CSS}</style></head><body><div class="card card-{kind}">{inner}</div></body></html>\n')


CARD = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--card=")), None)
if CARD:
    PAGE = card(CARD, next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--lang=")), "en"))
elif STANDALONE:
    head, body = PAGE.split('<div class="wrap">', 1)
    head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    meta = "".join(f'<meta property="og:{k}" content="{html.escape(v)}">\n' for k, v in (
        ("type", "article"), ("title", n["share_title"]), ("description", n["share_desc"]), ("url", PAGES_URL), ("image", PAGES_URL + "og.png")))
    PAGE = (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n{head}'
            f'<meta name="description" content="{html.escape(n["share_desc"])}">\n{meta}'
            f'<meta name="twitter:card" content="summary_large_image">\n</head>\n<body>\n<div class="wrap">{body}</body>\n</html>\n')
with open(OUT, "w", encoding="utf-8") as f:
    f.write(PAGE)
print("written", OUT, len(PAGE), "bytes")
