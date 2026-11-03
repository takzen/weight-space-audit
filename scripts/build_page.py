"""Builds the bilingual results page from results/summary.json, so no measured number is typed by hand.

  python build_page.py <out.html> [<results_dir>] [--final] [--standalone] [--card=chart|map --lang=en|pl]

Without --final, measured conclusions are limited to what the decision rules say so far. --standalone writes a full HTML
document with link-preview tags, for GitHub Pages. Without it, the file is the page body that the Artifact host wraps.
--card writes one fixed-size image page in one language, in the light theme, for render_cards.sh to turn into a PNG.
page_text.py holds the prose.
"""
import hashlib
import html
import json
import math
import os
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
FINAL = "--final" in sys.argv
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
QUEUE_LOG = (ROOT / "logs" / "queue.log").read_bytes().replace(b"\x00", b"").decode("utf-8", "replace")

MATH = SUMMARY.get("math500", {"conditions": {}, "authors": {}, "decisions": {}})
GSM = SUMMARY.get("gsm8k", {"conditions": {}, "authors": {}, "decisions": {}})
CONDS = MATH["conditions"]
DEC = MATH.get("decisions", {})
AUTHORS = MATH.get("authors", {})


def T(en, pl):
    return f'<span lang="en">{en}</span><span lang="pl">{pl}</span>'


def P(en, pl, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<p lang="en"{c}>{en}</p><p lang="pl"{c}>{pl}</p>'


def num(x, d=1):
    """A number in both languages (Polish uses a decimal comma)."""
    s = f"{x:.{d}f}"
    return T(s, s.replace(".", ","))


def e(x, d=1):
    return f"{x:.{d}f}"


def p(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def pc(x):
    return 100 * x


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


def cond_view(key):
    c = CONDS.get(key)
    if not c:
        return None
    sub = c.get("on_subset") or {"acc": c["acc"], "acc_ci95": c["acc_ci95"], "problems": c["problems"]}
    cut = c.get("cut_on_subset")
    return {"acc": pc(sub["acc"]), "lo": pc(sub["acc_ci95"][0]), "hi": pc(sub["acc_ci95"][1]), "problems": sub["problems"],
            "cut": pc(cut if cut is not None else c["cut_share"]), "samples": c["samples"], "tokens": c["mean_tokens"],
            "finished_acc": c.get("acc_given_finished"), "no_answer": c.get("finished_no_answer"),
            "median_tokens": c["median_tokens"], "loop": c.get("cut_loop_share"), "closed": c.get("closed_think_share")}


ROWS = [
    ("group", "Thinking on, up to 32,768 tokens", "Myślenie włączone, do 32 768 tokenów"),
    ("C0_think_T06_pp15", "unedited", "Unedited", "Bez edycji", "T 0.6, presence 1.5", "T 0,6, presence 1,5", "the post's setting",
     "ustawienie z posta", "unedited"),
    ("E0_edit_T06_pp15", "edited", "Edited", "Z edycją", "T 0.6, presence 1.5", "T 0,6, presence 1,5", "the post's setting",
     "ustawienie z posta", "p50c"),
    ("C1_think_T10_pp15", "unedited", "Unedited", "Bez edycji", "T 1.0, presence 1.5", "T 1,0, presence 1,5",
     "the card's setting for thinking on text", "ustawienie z karty dla myślenia na tekście", None),
    ("E1_edit_T10_pp15", "edited", "Edited", "Z edycją", "T 1.0, presence 1.5", "T 1,0, presence 1,5",
     "the card's setting for thinking on text", "ustawienie z karty dla myślenia na tekście", None),
    ("C3_think_T10_pp20", "unedited", "Unedited", "Bez edycji", "T 1.0, presence 2.0", "T 1,0, presence 2,0",
     "top of the card's presence range", "górna granica zakresu presence z karty", None),
    ("C2_think_T06_pp00", "unedited", "Unedited", "Bez edycji", "T 0.6, presence 0", "T 0,6, presence 0",
     "the card's setting for precise coding", "ustawienie z karty do precyzyjnego kodowania", None),
    ("group", "Thinking off, up to 8,192 tokens", "Myślenie wyłączone, do 8192 tokenów"),
    ("N1_nothink_T07_p08_pp15", "unedited", "Unedited", "Bez edycji", "T 0.7, top_p 0.8, presence 1.5", "T 0,7, top_p 0,8, presence 1,5",
     "the card's benchmark setting", "ustawienie benchmarkowe z karty", None),
    ("E2_edit_nothink_T07", "edited", "Edited", "Z edycją", "T 0.7, top_p 0.8, presence 1.5", "T 0,7, top_p 0,8, presence 1,5",
     "exploratory, added after the plan", "eksploracyjny, dodany po planie", None),
    ("N2_nothink_T10_p10_pp20", "unedited", "Unedited", "Bez edycji", "T 1.0, top_p 1.0, presence 2.0", "T 1,0, top_p 1,0, presence 2,0",
     "the card's setting for text", "ustawienie z karty dla tekstu", None),
]


def chart():
    out = []
    axis = "".join(f'<b style="left:{v}%">{v}</b>' for v in (0, 20, 40, 60, 80, 100))
    axis_cut = "".join(f'<b style="left:{v}%">{v}</b>' for v in (0, 50, 100))
    out.append(f'<div class="ch-head"><div></div><div class="ch-title">{T("Accuracy, % correct", "Trafność, % poprawnych")}'
               f'<div class="axis">{axis}</div></div><div></div>'
               f'<div class="ch-title">{T("Cut at the token cap, %", "Ucięte na limicie tokenów, %")}'
               f'<div class="axis">{axis_cut}</div></div><div></div></div>'
               f'<p class="ch-phone">{T("Line: accuracy, % correct. Bar: % cut at the token cap. Both scales run from 0 to 100.", "Linia: trafność, % poprawnych. Pasek: % uciętych na limicie tokenów. Obie skale biegną od 0 do 100.")}</p>')
    for r in ROWS:
        if r[0] == "group":
            out.append(f'<div class="ch-group">{T(r[1], r[2])}</div>')
            continue
        key, series, name_en, name_pl, set_en, set_pl, sub_en, sub_pl, ref = r
        v = cond_view(key)
        label = (f'<div class="ch-label"><span class="ch-name"><i class="swatch {series}"></i>{T(name_en, name_pl)}</span> '
                 f'<code>{T(set_en, set_pl)}</code><small>{T(sub_en, sub_pl)}</small></div>')
        if not v:
            out.append(f'<div class="ch-row pending">{label}<div class="ch-pending">{T("not measured yet", "jeszcze nie zmierzone")}</div></div>')
            continue
        marks = (f'<span class="ci {series}" style="left:{v["lo"]:.2f}%;width:{max(v["hi"] - v["lo"], 0.15):.2f}%"></span>'
                 f'<span class="dot {series}" style="left:{v["acc"]:.2f}%"></span>')
        tip_ref_en = tip_ref_pl = ""
        if ref and AUTHORS.get(ref, {}).get("subset"):
            a = pc(AUTHORS[ref]["subset"]["acc"])
            marks += f'<span class="ring" style="left:{a:.2f}%"></span>'
            tip_ref_en = f"; authors on these problems {e(a)}%"
            tip_ref_pl = f"; autorzy na tych zadaniach {p(a)}%"
        short = f' <span class="flag">n={v["problems"]}</span>' if v["problems"] < 100 else ""
        tip_en = (f'{e(v["acc"])}% correct (95% interval {e(v["lo"])}–{e(v["hi"])}){tip_ref_en}; {e(v["cut"])}% cut at the cap; '
                  f'mean {v["tokens"]:,.0f} tokens; {v["problems"]} problems')
        tokens_pl = f'{v["tokens"]:,.0f}'.replace(",", " ")
        tip_pl = (f'{p(v["acc"])}% poprawnych (przedział 95% {p(v["lo"])}–{p(v["hi"])}){tip_ref_pl}; {p(v["cut"])}% uciętych na limicie; '
                  f'średnio {tokens_pl} tokenów; zadań: {v["problems"]}')
        out.append(
            f'<div class="ch-row" tabindex="0" data-tip-en="{html.escape(tip_en)}" data-tip-pl="{html.escape(tip_pl)}">{label}'
            f'<div class="track">{marks}</div>'
            f'<div class="ch-val"><strong>{num(v["acc"])}</strong><small>{T(e(v["lo"]) + "–" + e(v["hi"]), p(v["lo"]) + "–" + p(v["hi"]))}</small>{short}</div>'
            f'<div class="track bars"><span class="bar {series}" style="width:{v["cut"]:.2f}%"></span></div>'
            f'<div class="ch-val"><strong>{num(v["cut"], 0)}</strong></div></div>')
    return "".join(out)


def legend():
    return (f'<div class="legend"><span><i class="swatch unedited"></i>{T("Unedited model", "Model bez edycji")}</span>'
            f'<span><i class="swatch edited"></i>{T("Edited model (authors&#39; p50c diff)", "Model z edycją (diff p50c autorów)")}</span>'
            f'<span><i class="ringkey"></i>{T("Authors&#39; score on the same problems", "Wynik autorów na tych samych zadaniach")}</span>'
            f'<span><i class="cikey"></i>{T("95% interval over problems", "Przedział 95% po zadaniach")}</span></div>')


def fmt_full(section, key, full_size):
    c = section["conditions"].get(key)
    if not c:
        return T("not measured yet", "jeszcze nie zmierzone")
    a, lo, hi, cut = pc(c["acc"]), pc(c["acc_ci95"][0]), pc(c["acc_ci95"][1]), pc(c["cut_share"])
    size = f'<br><small>{T(str(c["samples"]) + " answers", "odpowiedzi: " + str(c["samples"]))}</small>' if c["samples"] != full_size else ""
    return (f'<strong>{num(a)}</strong> <small>{T(e(lo) + "–" + e(hi), p(lo) + "–" + p(hi))}</small><br>'
            f'<small>{T(e(cut, 0) + "% cut", p(cut, 0) + "% uciętych")}</small>{size}')


def full_table():
    def author_cell(section, run):
        a = section.get("authors", {}).get(run)
        if not a:
            published = {"unedited": 13.84, "p50c": 67.10}
            return f'<strong>{num(published[run])}</strong>' if section is GSM else "–"
        cut = a.get("cut_share")
        extra = f'<br><small>{T(e(pc(cut), 0) + "% cut", p(pc(cut), 0) + "% uciętych")}</small>' if cut is not None else ""
        return f'<strong>{num(pc(a["full"]["acc"]))}</strong>{extra}'

    rows = [
        (T("Post: unedited, thinking on, T 0.6", "Post: bez edycji, myślenie włączone, T 0,6"), author_cell(MATH, "unedited"), author_cell(GSM, "unedited")),
        (T("Post: edited, thinking on, T 0.6", "Post: z edycją, myślenie włączone, T 0,6"), author_cell(MATH, "p50c"), author_cell(GSM, "p50c")),
        (T("This test: unedited, thinking off, T 0.7", "Ten test: bez edycji, myślenie wyłączone, T 0,7"),
         fmt_full(MATH, "N1_nothink_T07_p08_pp15", 2000), fmt_full(GSM, "N1_nothink_T07_p08_pp15", 2638)),
        (T("This test: edited, thinking off, T 0.7 (exploratory)", "Ten test: z edycją, myślenie wyłączone, T 0,7 (eksploracyjny)"),
         fmt_full(MATH, "E2_edit_nothink_T07", 2000), fmt_full(GSM, "E2_edit_nothink_T07", 2638)),
        (T("This test: unedited, thinking off, T 1.0", "Ten test: bez edycji, myślenie wyłączone, T 1,0"),
         fmt_full(MATH, "N2_nothink_T10_p10_pp20", 2000), fmt_full(GSM, "N2_nothink_T10_p10_pp20", 2638)),
    ]
    body = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return (f'<div class="scroll"><table class="data"><thead><tr><th scope="col">{T("Setting", "Ustawienie")}</th>'
            f'<th scope="col">MATH-500 <small>{T("500 problems, 4 samples", "500 zadań, 4 próbki")}</small></th>'
            f'<th scope="col">GSM8K <small>{T("1,319 problems, 2 samples", "1319 zadań, 2 próbki")}</small></th></tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def signed(x, d=1, lang="en"):
    s = f"{100 * x:+.{d}f}"
    s = s.replace("-", "−")
    return s if lang == "en" else s.replace(".", ",")


def diff_text(q):
    """A paired difference in points with its interval, in both languages."""
    if not q or q["diff"] is None:
        return T("not measured yet", "jeszcze nie zmierzone")
    return T(f'{signed(q["diff"])} points (95% interval {signed(q["ci95"][0])} to {signed(q["ci95"][1])})',
             f'{signed(q["diff"], lang="pl")} pkt (przedział 95% {signed(q["ci95"][0], lang="pl")} do {signed(q["ci95"][1], lang="pl")})')


def status(ok):
    if ok is None:
        return f'<span class="chip">{T("Waiting", "Czekamy")}</span>'
    if ok:
        return f'<span class="chip good"><b aria-hidden="true">✓</b>{T("Passes", "Zaliczona")}</span>'
    return f'<span class="chip bad"><b aria-hidden="true">✕</b>{T("Fails", "Niezaliczona")}</span>'


def decisions():
    cal = DEC.get("calibration", {})
    cal_rows = []
    for key, name_en, name_pl in (("C0_think_T06_pp15", "Unedited", "Bez edycji"), ("E0_edit_T06_pp15", "Edited", "Z edycją")):
        c = cal.get(key)
        if not c:
            cal_rows.append(f'<li>{T(name_en, name_pl)}: {T("not measured yet", "jeszcze nie zmierzone")}</li>')
            continue
        cal_rows.append(
            f'<li><strong>{T(name_en, name_pl)}.</strong> {T("Accuracy minus the authors&#39;", "Trafność minus wynik autorów")}: {diff_text(c["acc_minus_authors"])}. '
            f'{T("Cut share", "Odsetek uciętych")} {num(pc(c["cut_share"]), 0)}% {T("against the published", "wobec opublikowanych")} {num(pc(c["published_cut"]), 0)}%. {status(c["passes"])}</li>')
    q1, q3 = DEC.get("q1"), DEC.get("q3")
    q1_verdict = (f'<span class="chip strong">{T("Supported", "Potwierdzona") if q1["verdict"] == "supported" else T("Rejected", "Odrzucona")}</span>'
                  if q1 else "")
    q1_body = (f'{T("Accuracy gain", "Zysk trafności")}: {diff_text(q1["gain"])}. {T("Drop in cut share", "Spadek odsetka uciętych")}: {diff_text(q1["cut_drop"])}.'
               if q1 else T("Not measured yet.", "Jeszcze nie zmierzone."))
    q3_body = (f'{T("Accuracy", "Trafność")}: {diff_text(q3["gain"])}. {T("Cut share", "Odsetek uciętych")}: {diff_text(q3["cut_change"])}.'
               if q3 else T("Not measured yet.", "Jeszcze nie zmierzone."))
    n1m, n1g = MATH["conditions"].get("N1_nothink_T07_p08_pp15"), GSM["conditions"].get("N1_nothink_T07_p08_pp15")
    n2m, n2g = MATH["conditions"].get("N2_nothink_T10_p10_pp20"), GSM["conditions"].get("N2_nothink_T10_p10_pp20")
    q2_parts = []
    if n1m:
        q2_parts.append(f'{T("Card&#39;s benchmark setting", "Ustawienie benchmarkowe z karty")}: MATH-500 {num(pc(n1m["acc"]))}%'
                        + (f', GSM8K {num(pc(n1g["acc"]))}%' if n1g else ""))
    if n2m:
        q2_parts.append(f'{T("card&#39;s setting for text", "ustawienie z karty dla tekstu")}: MATH-500 {num(pc(n2m["acc"]))}%'
                        + (f', GSM8K {num(pc(n2g["acc"]))}%' if n2g else ""))
    q2_body = ("; ".join(q2_parts) + ".") if q2_parts else T("Not measured yet.", "Jeszcze nie zmierzone.")
    items = [
        (T("Cal", "Kal"), T("Do these runs match the authors&#39;?", "Czy te przebiegi zgadzają się z autorami?"),
         T("The accuracy difference on the same problems must have an interval that includes zero, and the cut share must be within 10 points of the published 93% and 33%. If either fails, the thinking-on rows count as not comparable with the post.",
           "Przedział różnicy trafności na tych samych zadaniach musi obejmować zero, a odsetek uciętych musi się mieścić w 10 punktach od opublikowanych 93% i 33%. Jeśli coś nie przejdzie, wiersze z włączonym myśleniem uznaję za nieporównywalne z postem."),
         f'<ul class="plain">{"".join(cal_rows)}</ul>', ""),
        ("Q1", T("Does the unedited model stop looping at the card&#39;s temperature?", "Czy model bez edycji przestaje się zapętlać przy temperaturze z karty?"),
         T("&ldquo;The post&#39;s baseline depends strongly on temperature&rdquo; counts as supported only with a gain of at least 15 points, an interval above zero, and a cut share down by at least 20 points.",
           "Hipoteza &bdquo;baza posta silnie zależy od temperatury&rdquo; przechodzi tylko przy zysku co najmniej 15 punktów, przedziale powyżej zera i odsetku uciętych niższym o co najmniej 20 punktów."),
         q1_body, q1_verdict),
        ("Q2", T("What does the unedited model score with thinking off, its default mode?", "Ile zdobywa model bez edycji z wyłączonym myśleniem, czyli w trybie domyślnym?"),
         T("Descriptive only. The post&#39;s protocol is thinking on, so these numbers give context and do not compete with the edit.",
           "Tylko opis. Protokół posta to włączone myślenie, więc te liczby dają kontekst i nie konkurują z edycją."),
         q2_body, ""),
        ("Q3", T("How much does the edit add at the card&#39;s setting?", "Ile dodaje edycja przy ustawieniu z karty?"),
         T("Edited minus unedited at T 1.0, reported with its interval whatever its size.", "Z edycją minus bez edycji przy T 1,0, podane z przedziałem bez względu na wielkość."),
         q3_body, ""),
    ]
    return "".join(
        f'<article class="dec"><div class="dec-id">{i}</div><div class="dec-body"><h3>{q}</h3>'
        f'<p class="rule"><span class="tag">{T("Rule fixed in advance", "Reguła ustalona z góry")}</span> {rule}</p>'
        f'<div class="res"><span class="tag">{T("Measured", "Zmierzone")}</span> {res} {chip}</div></div></article>'
        for i, q, rule, res, chip in items)


EXPLORATORY_LABELS = {
    ("E2_edit_nothink_T07", "N1_nothink_T07_p08_pp15"): ("Thinking off: edited minus unedited", "Myślenie wyłączone: z edycją minus bez edycji"),
    ("N1_nothink_T07_p08_pp15", "authors:p50c"): ("Unedited, thinking off, minus the post's edited score, thinking on",
                                                  "Bez edycji, myślenie wyłączone, minus wynik posta z edycją, myślenie włączone"),
    ("N1_nothink_T07_p08_pp15", "authors:unedited"): ("Unedited, thinking off, minus the post's unedited score, thinking on",
                                                      "Bez edycji, myślenie wyłączone, minus wynik posta bez edycji, myślenie włączone"),
    ("E2_edit_nothink_T07", "authors:p50c"): ("Edited, thinking off, minus the post's edited score, thinking on",
                                              "Z edycją, myślenie wyłączone, minus wynik posta z edycją, myślenie włączone"),
    ("E2_edit_nothink_T07:finished", "N1_nothink_T07_p08_pp15:finished"): ("Thinking off, finished answers only: edited minus unedited",
                                                                           "Myślenie wyłączone, tylko ukończone odpowiedzi: z edycją minus bez edycji"),
    ("E0_edit_T06_pp15:finished", "N1_nothink_T07_p08_pp15"): ("Edited at T 0.6, finished answers only, minus unedited with thinking off",
                                                               "Z edycją przy T 0,6, tylko ukończone odpowiedzi, minus bez edycji z wyłączonym myśleniem"),
    ("E1_edit_T10_pp15:finished", "N1_nothink_T07_p08_pp15"): ("Edited at T 1.0, finished answers only, minus unedited with thinking off",
                                                               "Z edycją przy T 1,0, tylko ukończone odpowiedzi, minus bez edycji z wyłączonym myśleniem"),
}


def exploratory(section, title_en, title_pl):
    rows = []
    for c in section.get("decisions", {}).get("exploratory", []):
        en, pl = EXPLORATORY_LABELS[(c["a"], c["b"])]
        rows.append(f'<tr><th scope="row">{T(en, pl)}</th><td>{diff_text(c["acc"])}</td><td>{diff_text(c["cut"]) if c.get("cut") else "&ndash;"}</td><td>{c["acc"]["problems"]}</td></tr>')
    if not rows:
        return ""
    return (f'<h3 class="sub">{T(title_en, title_pl)}</h3>'
            f'<div class="scroll"><table class="data"><thead><tr><th scope="col">{T("Comparison, same problems", "Porównanie, te same zadania")}</th>'
            f'<th scope="col">{T("Accuracy", "Trafność")}</th><th scope="col">{T("Cut share", "Odsetek uciętych")}</th><th scope="col">{T("Problems", "Zadania")}</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


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


VERDICT_ICONS = {"yes": "✓", "part": "◐", "no": "✕", "fore": "?", "wait": "…"}


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


def progress_note():
    done = QUEUE_LOG.count("COND_DONE")
    total = 13
    shortened = [ln.split()[1:3] for ln in QUEUE_LOG.splitlines() if ln.startswith("COND_SHORTENED_BY_DEADLINE")]
    if FINAL:
        if not shortened:
            return ""
        names = ", ".join(f"{a} {b}" for a, b in shortened)
        return P(f"Cut short by the deadline, as the plan allows: <code>{names}</code>. Answers still running at the deadline were lost, and those tend to be the long ones, so a shortened row understates its cut share.",
                 f"Skrócone przez termin, co plan dopuszcza: <code>{names}</code>. Odpowiedzi trwające w chwili terminu przepadły, a są to zwykle te długie, więc skrócony wiersz zaniża odsetek uciętych.", "note")
    pending_en, pending_pl = "", ""
    if "both_pass" not in DEC.get("calibration", {}):
        pending_en = " The post's 7.9% and 48.1% haven't been re-measured here yet."
        pending_pl = " Wyników posta 7,9% i 48,1% jeszcze tu nie powtórzono."
    return P(f"Interim version: {done} of {total} measurements are done.{pending_en}", f"Wersja robocza: gotowe {done} z {total} pomiarów.{pending_pl}", "note")


CTX = dict(math=MATH, gsm=GSM, dec=DEC, authors=AUTHORS, final=FINAL, minatar=MINATAR, recheck=RECHECK)
hero_map = board("pacman", "agent", "Pac-Man, agent channel", "Pac-Man, kanał agenta", "hero-map")
pac = MAPS["pacman"]
map_values = "".join("<tr>" + "".join(f"<td>{v:.1f}</td>" for v in row) + "</tr>" for row in pac["channels"]["agent"])
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
    {progress_note()}
    {P(W.DISCLOSE_EN, W.DISCLOSE_PL, "note")}
  </div>
  <div class="hero-fig">
    {hero_map}
    <p class="fig-code"><code>np.linalg.norm(W1, axis=1).reshape(10, 10, 5)[:, :, 0]</code></p>
    {P("One line of numpy, no LLM and no forward pass: the size of the first-layer weights per input cell draws the maze. A cell the agent never visits gets no gradient and keeps its small starting weights.",
       "Jedna linijka numpy, bez LLM i bez przebiegu w przód: rozmiar wag pierwszej warstwy na komórkę wejścia rysuje labirynt. Komórka, w której agent nigdy nie bywa, nie dostaje gradientu i zachowuje małe wagi startowe.", "fig-note")}
    <div class="scale" aria-hidden="true"><span>{T("≈ 0.4", "≈ 0,4")}</span><div class="scale-bar">{scale}</div><span>{num(pac["max"])}</span></div>
    <details class="values"><summary>{T("Values of this map", "Wartości tej mapy")}</summary><div class="scroll"><table class="grid-values"><tbody>{map_values}</tbody></table></div></details>
  </div>
</header>
<main>
<section id="claims"><h2>{T("Their claim, sentence by sentence", "Ich teza, zdanie po zdaniu")}</h2>
  {P(W.CLAIMS_INTRO_EN, W.CLAIMS_INTRO_PL)}
  <div class="claims">{claim_rows()}</div>
</section>
<section id="measured"><h2>{T("The measurement", "Pomiar")}</h2>
  {P(W.INTRO_EN, W.INTRO_PL)}
  <figure class="fig chart">
    <figcaption>{T("MATH-500: the same 100 problems in every row", "MATH-500: te same 100 zadań w każdym wierszu")}</figcaption>
    {legend()}
    <div class="ch">{chart()}</div>
    {P(W.CHART_NOTE_EN, W.CHART_NOTE_PL, "fig-note")}
  </figure>
  <h3 class="sub">{T("Rules and results", "Reguły i wyniki")}</h3>
  <div class="decs">{decisions()}</div>
  <h3 class="sub">{T("Thinking off, on the full benchmarks", "Myślenie wyłączone, na pełnych benchmarkach")}</h3>
  {full_table()}
  {P(W.FULL_NOTE_EN, W.FULL_NOTE_PL, "fig-note")}
  {exploratory(MATH, "Exploratory comparisons on MATH-500", "Porównania eksploracyjne na MATH-500")}
  {exploratory(GSM, "Exploratory comparisons on GSM8K", "Porównania eksploracyjne na GSM8K")}
  {P(W.EXPLORATORY_NOTE_EN, W.EXPLORATORY_NOTE_PL, "fig-note") if MATH.get("decisions", {}).get("exploratory") else ""}
  <h3 class="sub">{T("The authors ran into this first", "Autorzy trafili na to pierwsi")}</h3>
  {W.AUTHORS_CODE}
  <h3 class="sub">{T("The model card&#39;s own numbers", "Liczby z karty modelu")}</h3>
  {P(W.CARD_INTRO_EN, W.CARD_INTRO_PL)}
  {card_table()}
  {P(W.CARD_NOTE_EN, W.CARD_NOTE_PL, "fig-note")}
</section>
<section id="audit"><h2>{T("What the logs show, experiment by experiment", "Co pokazują logi, eksperyment po eksperymencie")}</h2>
  {P(W.AUDIT_INTRO_EN, W.AUDIT_INTRO_PL)}
  {audit()}
</section>
<section id="overall"><h2>{T("One name, three skills", "Jedna nazwa, trzy umiejętności")}</h2>{W.OVERALL}</section>
<section id="credit"><h2>{T("What deserves credit", "Co trzeba docenić")}</h2>{W.CREDIT}</section>
<section id="open"><h2>{T("What would settle the open questions", "Co rozstrzygnęłoby otwarte pytania")}</h2>{W.OPEN}</section>
<section id="limits"><h2>{T("Limits of this check", "Ograniczenia tego sprawdzenia")}</h2>{W.LIMITS}</section>
<section id="method"><h2>{T("Method", "Metoda")}</h2>{W.method(PLAN_SHA)}
  {plan_block}
  <details class="values plan"><summary>{T("Every change from the plan (in English)", "Każda zmiana względem planu (po angielsku)")}</summary>
  <pre>{html.escape(DEVIATIONS)}</pre></details>
</section>
</main>
<footer class="foot">{W.FOOT}</footer>
</div>
<div id="tip" role="status" hidden></div>
<script>{W.JS}</script>
"""


def card(kind, lang):
    """A fixed-size page for one image, with the same chart and maps as the main page."""
    if kind == "og":
        inner = (f'<h1>{T(n["h1_en"], n["h1_pl"])}</h1><div class="strip">{strip}</div>'
                 f'<p class="card-foot">{T("An independent check of &ldquo;Sparks of Weight-Space Programming&rdquo;", "Niezależne sprawdzenie &bdquo;Sparks of Weight-Space Programming&rdquo;")}</p>')
    elif kind == "chart":
        inner = (f'<h1>{T(n["card_title_en"], n["card_title_pl"])}</h1>{legend()}<div class="ch">{chart()}</div>'
                 f'<p class="card-foot">{T(n["card_foot_en"], n["card_foot_pl"])}</p>')
    else:
        inner = (f'<h1>{T("One line of numpy draws the game from the weights", "Jedna linijka numpy rysuje grę z samych wag")}</h1>'
                 f'<div class="card-maps">{board("pacman", "agent", "Pac-Man, agent channel: the maze", "Pac-Man, kanał agenta: labirynt", "card-big")}'
                 f'<div class="card-small">'
                 + board("breakout", "agent", "Breakout, agent: the paddle row", "Breakout, agent: rząd paletki")
                 + board("breakout", "reward", "Breakout, reward: the bricks", "Breakout, nagrody: cegły")
                 + board("pong", "agent", "Pong, agent: the paddle column", "Pong, agent: kolumna paletki")
                 + board("freeway", "moving", "Freeway, moving: the lanes", "Freeway, ruch: pasy")
                 + f'</div></div><p class="card-code"><code>np.linalg.norm(W1, axis=1).reshape(10, 10, 5)</code></p>'
                 f'<p class="card-foot">{T("Size of the first-layer weights per input cell of four PPO policies, with no LLM and no forward pass. Cells the agent never uses keep their small starting weights.", "Rozmiar wag pierwszej warstwy na komórkę wejścia czterech polityk PPO, bez LLM i bez przebiegu w przód. Komórki, których agent nie używa, zachowują małe wagi startowe.")}</p>')
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
print("written", OUT, len(PAGE), "bytes; final" if FINAL else "bytes; interim")
