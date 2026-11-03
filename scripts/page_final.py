"""Headline, verdicts and the sentence-by-sentence check of the post's TL;DR.

Sentences that depend on a measurement are chosen here from the data, so the text can't drift from the numbers. Conditions that
haven't run yet leave their sentences out. Passing --final to build_page.py refuses to build while a decision rule still has no data.
"""
N1, N2, E2 = "N1_nothink_T07_p08_pp15", "N2_nothink_T10_p10_pp20", "E2_edit_nothink_T07"
C0, E0, C1, E1 = "C0_think_T06_pp15", "E0_edit_T06_pp15", "C1_think_T10_pp15", "E1_edit_T10_pp15"


def T(en, pl):
    return f'<span lang="en">{en}</span><span lang="pl">{pl}</span>'


def P(en, pl, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<p lang="en"{c}>{en}</p><p lang="pl"{c}>{pl}</p>'


def pct(x, d=1):
    return f"{100 * x:.{d}f}"


def pct_pl(x, d=1):
    return pct(x, d).replace(".", ",")


def points(x, lang="en"):
    s = f"{100 * x:+.1f}".replace("-", "−")
    return s if lang == "en" else s.replace(".", ",")


def diff_en(q):
    return f'{points(q["diff"])} points (95% interval {points(q["ci95"][0])} to {points(q["ci95"][1])})'


def diff_pl(q):
    return f'{points(q["diff"], "pl")} pkt (przedział 95% {points(q["ci95"][0], "pl")} do {points(q["ci95"][1], "pl")})'


def explored(ctx, a, b):
    return next((c for c in ctx["dec"].get("exploratory", []) if c["a"] == a and c["b"] == b), None)


def strip_items(ctx):
    math = ctx["math"]
    items = [(7.9, "MATH-500 in the post, unedited, thinking on", "MATH-500 w poście, bez edycji, myślenie włączone"),
             (48.1, "MATH-500 in the post, edited, thinking on", "MATH-500 w poście, z edycją, myślenie włączone")]
    a = math.get("authors", {})
    if a.get("unedited") and a.get("p50c"):
        items = [(100 * a["unedited"]["full"]["acc"], items[0][1], items[0][2]), (100 * a["p50c"]["full"]["acc"], items[1][1], items[1][2])]
    c = math["conditions"].get(N1)
    if c and c["samples"] >= 2000:
        items.append((100 * c["acc"], "MATH-500 here, unedited, thinking off, the card's default mode", "MATH-500 tutaj, bez edycji, myślenie wyłączone, tryb domyślny z karty"))
    c = math["conditions"].get(E2)
    if c:
        items.append((100 * c["acc"], "MATH-500 here, edited, thinking off (exploratory)", "MATH-500 tutaj, z edycją, myślenie wyłączone (eksploracyjnie)"))
    return items


def same_score_title(ctx):
    """The chart's headline, chosen from the interval of unedited-with-thinking-off minus the post's edited score."""
    q = explored(ctx, N1, "authors:p50c")
    c = ctx["math"]["conditions"].get(N1)
    if not q or not c or c["samples"] < 2000:
        return ("MATH-500, the same 100 problems (measurement still running)", "MATH-500, te same 100 zadań (pomiar jeszcze trwa)")
    if q["acc"]["ci95"][0] > 0:
        return ("With thinking off, the unedited model scores higher than the edit", "Z wyłączonym myśleniem model bez edycji wypada lepiej niż z edycją")
    if q["acc"]["ci95"][1] < 0:
        return ("The edit scores higher than the unedited model with thinking off", "Edycja wypada lepiej niż model bez edycji z wyłączonym myśleniem")
    return ("With thinking off, the unedited model matches the edit's score", "Z wyłączonym myśleniem model bez edycji dorównuje wynikowi edycji")


def findings(ctx):
    """The page's three conclusions, shown first. The Qwen line follows the measurements."""
    n1 = ctx["math"]["conditions"].get(N1)
    both = ctx["dec"].get("calibration", {}).get("both_pass")
    a = ctx["math"].get("authors", {}).get("p50c")
    edited = a["full"]["acc"] if a else 0.481
    if both is False:
        head_en, head_pl = "The Qwen fix: didn&rsquo;t fully reproduce here.", "Naprawa Qwena: tu nie odtworzyła się w pełni."
    else:
        head_en, head_pl = "The Qwen fix: real, but its 6x starts from the looping mode.", "Naprawa Qwena: prawdziwa, ale jej 6x liczone jest od trybu z pętlami."
    tail_en, tail_pl = "", ""
    if n1 and n1["samples"] >= 2000:
        tail_en = f" With no edit and thinking off, the model&rsquo;s default, it scores {pct(n1['acc'])}%. The post&rsquo;s edited score is {pct(edited)}%."
        tail_pl = f" Bez edycji, z wyłączonym myśleniem, czyli w trybie domyślnym, model ma {pct_pl(n1['acc'])}%. Post po edycji ma {pct_pl(edited)}%."
    e2, e2c = explored(ctx, E2, N1), ctx["math"]["conditions"].get(E2)
    if e2 and e2c:
        lo, hi = e2["acc"]["ci95"]
        if lo <= 0 <= hi:
            tail_en += f" With thinking off, the edit adds nothing measurable ({pct(e2c['acc'])}%)."
            tail_pl += f" Przy wyłączonym myśleniu edycja nie dodaje niczego mierzalnego ({pct_pl(e2c['acc'])}%)."
        elif hi < 0:
            tail_en += f" With thinking off, the edit lowers the score ({pct(e2c['acc'])}%)."
            tail_pl += f" Przy wyłączonym myśleniu edycja obniża wynik ({pct_pl(e2c['acc'])}%)."
        else:
            tail_en += f" With thinking off, the edit raises the score ({pct(e2c['acc'])}%)."
            tail_pl += f" Przy wyłączonym myśleniu edycja podnosi wynik ({pct_pl(e2c['acc'])}%)."
    return [
        ("<strong>Writing weights: holds.</strong> With no feedback, Astra&rsquo;s networks beat PPO at 100M steps in all three games.",
         "<strong>Pisanie wag: stoi.</strong> Bez informacji zwrotnej sieci Astry biją PPO po 100 mln kroków we wszystkich trzech grach."),
        ("<strong>Reading weights better than humans or algorithms: not shown.</strong> The post tests neither, one line of numpy shows the same signal in Exp 1, and the only test on a large model failed.",
         "<strong>Czytanie wag lepiej niż ludzie i algorytmy: nie pokazano.</strong> Post nie testuje ani jednych, ani drugich, w eksp. 1 jedna linijka numpy pokazuje ten sam sygnał, a jedyny test na dużym modelu się nie udał."),
        (f"<strong>{head_en}</strong>{tail_en}", f"<strong>{head_pl}</strong>{tail_pl}"),
    ]


def sentence5(ctx):
    """What the measurements say about 'With the same sampling settings...'. Returns (kind, verdict_en, verdict_pl, why_en, why_pl)."""
    math, dec = ctx["math"], ctx["dec"]
    intro_en = ("The 7.9% describes a model that rarely finishes: 93% of its answers hit the 32,768-token cap. The gain comes from answers that used to be cut off, as the post says too.")
    intro_pl = ("Te 7,9% opisuje model, który rzadko kończy: 93% odpowiedzi dochodzi do limitu 32 768 tokenów. Zysk pochodzi z odpowiedzi, które wcześniej były ucinane, co mówi też post.")
    en, pl = [], []

    cal = dec.get("calibration", {})
    both = cal.get("both_pass")
    if both is True:
        en.append("Re-measured here on the same 100 problems, both the unedited and the edited score agree with the authors, so the published numbers stand.")
        pl.append("Zmierzone tu ponownie na tych samych 100 zadaniach, oba wyniki, bez edycji i z edycją, zgadzają się z autorami, więc opublikowane liczby stoją.")
    elif both is False:
        en.append("Re-measured here on the same 100 problems, at least one score doesn't agree with the authors under the rule fixed in advance. The rows below say which.")
        pl.append("Zmierzone tu ponownie na tych samych 100 zadaniach, co najmniej jeden wynik nie zgadza się z autorami według reguły ustalonej z góry. Wiersze niżej mówią który.")

    n1 = math["conditions"].get(N1)
    q = explored(ctx, N1, "authors:p50c")
    if n1 and n1["samples"] >= 2000:
        ci = n1["acc_ci95"]
        en.append(f"With no edit and thinking off, the card's default mode, the same model scores {pct(n1['acc'])}% on all 500 problems (95% interval {pct(ci[0])}&ndash;{pct(ci[1])}), with {pct(n1['cut_share'])}% of answers cut at 8,192 tokens.")
        pl.append(f"Bez edycji, z wyłączonym myśleniem, czyli w domyślnym trybie z karty, ten sam model ma {pct_pl(n1['acc'])}% na wszystkich 500 zadaniach (przedział 95% {pct_pl(ci[0])}&ndash;{pct_pl(ci[1])}), a {pct_pl(n1['cut_share'])}% odpowiedzi jest uciętych na 8192 tokenach.")
        if q:
            en.append(f"Compared per problem with the post's edited score, that is {diff_en(q['acc'])}.")
            pl.append(f"W porównaniu po zadaniach z wynikiem posta po edycji to {diff_pl(q['acc'])}.")

    e2 = explored(ctx, E2, N1)
    e2_fin = explored(ctx, f"{E2}:finished", f"{N1}:finished")
    if e2:
        lo, hi = e2["acc"]["ci95"]
        en_e2 = f"With thinking off, the edit itself changes the score by {diff_en(e2['acc'])} and the share of cut answers by {diff_en(e2['cut'])}, on {e2['acc']['problems']} problems (exploratory)."
        pl_e2 = f"Z wyłączonym myśleniem sama edycja zmienia wynik o {diff_pl(e2['acc'])}, a odsetek uciętych odpowiedzi o {diff_pl(e2['cut'])}, na {e2['acc']['problems']} zadaniach (eksploracyjnie)."
        if lo <= 0 <= hi:
            en_e2 += " So in this mode it adds nothing measurable."
            pl_e2 += " W tym trybie nie dodaje więc niczego mierzalnego."
        elif hi < 0:
            en_e2 += " So in this mode it costs accuracy."
            pl_e2 += " W tym trybie obniża więc trafność."
        elif e2_fin and e2_fin["acc"]["ci95"][0] > 0:
            en_e2 += f" Among finished answers alone the score changes by {diff_en(e2_fin['acc'])}, so here the edit does more than let answers finish, which counts for it."
            pl_e2 += f" Na samych ukończonych odpowiedziach wynik zmienia się o {diff_pl(e2_fin['acc'])}, więc tutaj edycja robi coś więcej, niż pozwala odpowiedziom się skończyć, co przemawia na jej korzyść."
        elif e2_fin and e2["cut"]["ci95"][1] < 0:
            en_e2 += f" Among finished answers alone the score changes by {diff_en(e2_fin['acc'])}, so the gain comes from more answers finishing, the same defect as with thinking on."
            pl_e2 += f" Na samych ukończonych odpowiedziach wynik zmienia się o {diff_pl(e2_fin['acc'])}, więc zysk bierze się z tego, że więcej odpowiedzi się kończy, czyli z tej samej usterki co przy włączonym myśleniu."
        else:
            en_e2 += " These numbers don't show where the gain comes from."
            pl_e2 += " Te liczby nie pokazują, skąd bierze się zysk."
        en.append(en_e2)
        pl.append(pl_e2)

    q1, q3 = dec.get("q1"), dec.get("q3")
    if q1:
        ok = q1["verdict"] == "supported"
        en.append(f"The post's T 0.6 is the card's setting for vision benchmarks, and its text benchmarks used T 1.0. The planned test of T 1.0, unedited, thinking on: {diff_en(q1['gain'])}, with the cut share down by {points(q1['cut_drop']['diff'])}. "
                  + ("By the rule fixed in advance, the baseline depends strongly on temperature." if ok else "By the rule fixed in advance, that does not show the baseline depends strongly on temperature."))
        pl.append(f"T 0,6 z posta to ustawienie z karty dla benchmarków wizyjnych, a jej benchmarki tekstowe używały T 1,0. Zaplanowany test T 1,0, bez edycji, z włączonym myśleniem: {diff_pl(q1['gain'])}, a odsetek uciętych spada o {points(q1['cut_drop']['diff'], 'pl')}. "
                  + ("Według reguły ustalonej z góry baza silnie zależy od temperatury." if ok else "Według reguły ustalonej z góry to nie pokazuje, że baza silnie zależy od temperatury."))
    if q3:
        en.append(f"At that setting the edit adds {diff_en(q3['gain'])}.")
        pl.append(f"Przy tym ustawieniu edycja dodaje {diff_pl(q3['gain'])}.")

    fin = explored(ctx, f"{E0}:finished", N1)
    credit_en, credit_pl = "", ""
    if fin:
        credit_en = (f"When the edited model finishes with thinking on, it is right {pct(fin['a_mean'])}% of the time, against {pct(fin['b_mean'])}% for "
                     f"thinking off on those same {fin['acc']['problems']} problems ({diff_en(fin['acc'])}, exploratory). Answers that finish are the easier ones to finish, so this describes them and proves no cause.")
        credit_pl = (f"Gdy model z edycją kończy odpowiedź z włączonym myśleniem, ma rację w {pct_pl(fin['a_mean'])}% przypadków, a myślenie wyłączone na tych samych {fin['acc']['problems']} zadaniach w {pct_pl(fin['b_mean'])}% "
                     f"({diff_pl(fin['acc'])}, eksploracyjnie). Odpowiedzi, które się kończą, to te łatwiejsze do ukończenia, więc to opis, a nie dowód przyczyny.")
    ife_en = "IFEval wasn't re-measured here. The post's base of 21.0 is under half the card's 44.0 with thinking on and 52.1 with thinking off, so against the card the 3x shrinks to about 1.4x and 1.2x, with protocols that differ."
    ife_pl = "IFEval nie był tu mierzony. Baza posta, 21,0, to mniej niż połowa liczb z karty: 44,0 z myśleniem i 52,1 bez niego, więc względem karty 3x kurczy się do około 1,4x i 1,2x, przy różnych protokołach."

    if both is False:
        verdict = ("part", "Didn't fully reproduce here", "Tu nie odtworzyło się w pełni")
    elif both is True and n1 and n1["samples"] >= 2000:
        verdict = ("part", "The numbers hold. The baseline is the looping mode", "Liczby stoją. Punktem odniesienia jest tryb z pętlami")
    elif n1 and n1["samples"] >= 2000:
        verdict = ("wait", "The baseline is the looping mode. Measurement still running", "Punktem odniesienia jest tryb z pętlami. Pomiar jeszcze trwa")
    else:
        verdict = ("wait", "Measurement still running", "Pomiar jeszcze trwa")
    return (*verdict, [x for x in (intro_en, " ".join(en), credit_en, ife_en) if x], [x for x in (intro_pl, " ".join(pl), credit_pl, ife_pl) if x])


def claims(ctx):
    m, r = ctx["minatar"], ctx["recheck"]
    bo_lo, bo_hi = sorted((m["breakout"]["network"]["mean"], r["mean"]))
    as_n, se_n = m["asterix"]["network"]["mean"], m["seaquest"]["network"]["mean"]
    as_en, se_en = f"{as_n:.1f}", f"{se_n:.1f}"
    as_pl, se_pl = as_en.replace(".", ","), se_en.replace(".", ",")
    kind5, v5_en, v5_pl, why5_en, why5_pl = sentence5(ctx)
    return [
        dict(q_en="We find that frontier LLMs are surprisingly good at natively reading and writing neural network weights, well past what we&rsquo;d expect from humans or conventional algorithms.",
             q_pl="Odkryliśmy, że czołowe LLM-y są zaskakująco dobre w natywnym czytaniu i pisaniu wag sieci neuronowych, znacznie lepsze, niż oczekiwalibyśmy od ludzi lub konwencjonalnych algorytmów.",
             kind="no", v_en="Not shown", v_pl="Nie pokazano",
             why_en='The post tests no humans and runs no conventional baseline for reading. Its one baseline is PPO, for writing (<a href="#exp5">Exp 5</a>, <a href="#exp6">6</a>). The post asks &ldquo;where would you even start?&rdquo; For the networks in <a href="#exp1">Exp 1</a>: with the size of the first-layer weights. One line of numpy draws the map at the top of this page. A person or a script gets that signal too. Whether people would then name the games wasn&rsquo;t tested.',
             why_pl='Post nie testuje ludzi i nie uruchamia żadnego konwencjonalnego punktu odniesienia dla czytania. Jego jedynym punktem odniesienia jest PPO, przy pisaniu (<a href="#exp5">eksp. 5</a>, <a href="#exp6">6</a>). Post pyta: &bdquo;where would you even start?&rdquo; Przy sieciach z <a href="#exp1">eksp. 1</a>: od rozmiaru wag pierwszej warstwy. Jedna linijka numpy rysuje mapę z góry tej strony. Człowiek albo skrypt też dostaje ten sygnał. Nie sprawdzano, czy ludzie nazwaliby potem te gry.'),
        dict(q_en="Just by looking at the raw weights, GPT-6 Astra can tell what a network was trained to do.",
             q_pl="Patrząc tylko na surowe wagi, GPT-6 Astra potrafi określić, do czego sieć wytrenowano.",
             kind="part", v_en="True for small networks", v_pl="Prawda dla małych sieci",
             why_en='Right on 4 of 4 game policies (<a href="#exp1">Exp 1</a>) and 3 of 3 diffusion models (<a href="#exp2">Exp 2</a>), from pasted text with no tools, with the signal in one layer both times. <a href="#exp3">Exp 3</a> is the stronger case: with the outer layers removed it names three languages and finds every copying head, using Python and a published recipe. That makes ten small networks. The only test of a behaviour in a large model is <a href="#exp7">Exp 7</a>, where Astra could not tell the sycophantic Gemma from the honest one using weights alone, as the post reports.',
             why_pl='Trafnie dla 4 z 4 polityk w grach (<a href="#exp1">eksp. 1</a>) i 3 z 3 modeli dyfuzyjnych (<a href="#exp2">eksp. 2</a>), z wklejonego tekstu, bez narzędzi, a sygnał leży za każdym razem w jednej warstwie. Mocniejszy jest <a href="#exp3">eksp. 3</a>: bez skrajnych warstw nazywa trzy języki i znajduje wszystkie głowy kopiujące, z Pythonem i opublikowanym przepisem. Razem to dziesięć małych sieci. Jedyny test zachowania w dużym modelu to <a href="#exp7">eksp. 7</a>, gdzie Astra nie odróżniła z samych wag lizusowskiej Gemmy od uczciwej, co post przyznaje.'),
        dict(q_en="And without any environment feedback, it has no trouble writing, from scratch, small game-playing networks that outplay networks trained with PPO for 100 million steps.",
             q_pl="A bez żadnej informacji zwrotnej ze środowiska bez trudu pisze od zera małe sieci do gier, które ogrywają sieci trenowane algorytmem PPO przez 100 milionów kroków.",
             kind="yes", v_en="Holds", v_pl="Stoi",
             why_en=f'The logs confirm it, with no tool calls and all three games above PPO at 100M steps (<a href="#exp5">Exp 5</a>). Re-scored here, the networks reach {bo_lo:.0f}&ndash;{bo_hi:.0f} on Breakout (published 517), {as_en} on Asterix and {se_en} on Seaquest (published 53.2 and 53.1). A check meant to deflate the result failed: short rule-based programs written once by Claude lost all three games. PPO at 100M is a low bar, and at 500M its best seed still beats Astra on Asterix and Seaquest. This is the post&rsquo;s strongest result.',
             why_pl=f'Logi to potwierdzają: zero wywołań narzędzi i wszystkie trzy gry powyżej PPO po 100 mln kroków (<a href="#exp5">eksp. 5</a>). Policzone tu ponownie sieci osiągają {bo_lo:.0f}&ndash;{bo_hi:.0f} w Breakoucie (opublikowane 517), {as_pl} w Asterixie i {se_pl} w Seaquest (opublikowane 53,2 i 53,1). Kontrola mająca osłabić wynik nie wyszła: krótkie programy regułowe napisane raz przez Claude&rsquo;a przegrały we wszystkich trzech grach. PPO po 100 mln to niska poprzeczka, a po 500 mln jego najlepsze ziarno nadal bije Astrę w Asterixie i Seaquest. To najmocniejszy wynik posta.'),
        dict(q_en="Likewise, asked to make Qwen3.5-0.8B better at math without gradients, Astra identifies an issue in its weights causing reasoning loops that Qwen&rsquo;s own model card warns about, and fixes this by natively editing 0.016% of the weights.",
             q_pl="Podobnie, poproszona o poprawę Qwen3.5-0.8B w matematyce bez gradientów, Astra wykrywa w jego wagach problem powodujący pętle rozumowania, przed którymi ostrzega karta modelu, i naprawia go, natywnie edytując 0,016% wag.",
             kind="part", v_en="The fix is real. The wording oversells it", v_pl="Naprawa jest prawdziwa. Opis ją zawyża",
             why_en='The fix works, on problems Astra held out, with a random-direction control (<a href="#exp8">Exp 8</a>). Three parts of the sentence say more than the logs do. &ldquo;Identifies&rdquo;: the prompt already points there (&ldquo;if the model often fails because it repeats itself and never finishes&rdquo;), while the authors&rsquo; thread calls it &ldquo;We simply asked&rdquo;. &ldquo;Natively&rdquo;: this took 20 hours, 80 Python runs, 50 forward passes and about 6,000 generated answers, so it is interpretability work on activations, and the edit has the form of known direction removal, <code>W &minus; c&middot;u(uᵀW)</code>. &ldquo;0.016%&rdquo;: that counts the weights touched, while the authors&rsquo; manifest gives a relative change of 10.6% and 8.1% in the two matrices. It is also one run: of 7 completed Qwen runs, six gained at most 6.2 points.',
             why_pl='Naprawa działa, na zadaniach odłożonych przez samą Astrę, z kontrolą w postaci losowego kierunku (<a href="#exp8">eksp. 8</a>). Trzy części tego zdania mówią więcej niż logi. &bdquo;Identifies&rdquo;: prompt sam tam prowadzi (&bdquo;if the model often fails because it repeats itself and never finishes&rdquo;), a wątek autorów nazywa to &bdquo;We simply asked&rdquo;. &bdquo;Natively&rdquo;: to 20 godzin, 80 uruchomień Pythona, 50 przebiegów w przód i około 6000 wygenerowanych odpowiedzi, czyli praca interpretacyjna na aktywacjach, a edycja ma postać znanego usuwania kierunku, <code>W &minus; c&middot;u(uᵀW)</code>. &bdquo;0.016%&rdquo;: to liczba dotkniętych wag, a manifest autorów podaje zmianę względną 10,6% i 8,1% w obu macierzach. To też jeden przebieg: z 7 ukończonych przebiegów na Qwen sześć zyskało najwyżej 6,2 pkt.'),
        dict(q_en="With the same sampling settings, this weight correction raises MATH-500 from 7.9% to 48.1% and generalizes out of the box to instruction following, raising IFEval by 3x.",
             q_pl="Przy tych samych ustawieniach próbkowania ta korekta wag podnosi MATH-500 z 7,9% do 48,1% i od razu uogólnia się na wykonywanie instrukcji, podnosząc IFEval trzykrotnie.",
             kind=kind5, v_en=v5_en, v_pl=v5_pl, why_en=why5_en, why_pl=why5_pl),
        dict(q_en="All of this is possible without allowing Astra to write training loops. It uses its reasoning to figure out what each part of a neural network computes, or should compute, and changes the weights accordingly.",
             q_pl="Wszystko to jest możliwe bez pozwalania Astrze na pisanie pętli treningowych. Używa rozumowania, by ustalić, co każda część sieci oblicza lub powinna obliczać, i odpowiednio zmienia wagi.",
             kind="part", v_en="True for training loops, thin for the rest", v_pl="Prawda co do pętli treningowych, reszta słabo podparta",
             why_en='The prompts forbid training and the logs show none. &ldquo;Its reasoning&rdquo; means one reply with no tools in Exp 1, 2, 4 and 5, which is impressive. In Exp 6 and 8 it also means Python, measured activations and many forward passes. &ldquo;What each part of a neural network computes&rdquo; has less behind it: 56 of 144 head labels in <a href="#exp3">Exp 3</a> are &ldquo;unclear&rdquo;, and in the one causal check in the logs (<a href="#exp7">Exp 7</a>, pair 1), the components Astra named closed less of the margin than random ones (0.04 against 0.19).',
             why_pl='Prompty zabraniają treningu i logi go nie pokazują. &bdquo;Rozumowanie&rdquo; to w eksp. 1, 2, 4 i 5 jedna odpowiedź bez narzędzi, co robi wrażenie. W eksp. 6 i 8 to także Python, zmierzone aktywacje i wiele przebiegów w przód. Za &bdquo;co każda część oblicza&rdquo; stoi mniej: 56 ze 144 etykiet głów w <a href="#exp3">eksp. 3</a> to &bdquo;unclear&rdquo;, a w jedynej kontroli przyczynowej w logach (<a href="#exp7">eksp. 7</a>, para 1) składniki wskazane przez Astrę zamknęły mniej marginesu niż losowe (0,04 wobec 0,19).'),
        dict(q_en="Throughout the history of deep learning, we encoded our simplistic inductive biases into tiny symbolic optimizers like Adam or Muon. This is changing: our neural network weights will soon be natively optimized by LLMs that deliberately reason about their weights.",
             q_pl="Przez całą historię głębokiego uczenia kodowaliśmy nasze uproszczone założenia indukcyjne w maleńkich symbolicznych optymalizatorach, takich jak Adam czy Muon. To się zmienia: wagi naszych sieci wkrótce będą natywnie optymalizowane przez LLM-y, które świadomie rozumują o swoich wagach.",
             kind="fore", v_en="A forecast these results can't carry", v_pl="Prognoza, której te wyniki nie uniosą",
             why_en='The evidence so far: the largest written network has 1.5M weights and plays Go against weak opponents, and the one edit of a real model repaired one failure in one run. On Gemma 3 270M, which rarely loops, the same task stayed near the base (2.8% against 2.6&ndash;3.8% under strict grading). The post sets the limit itself: &ldquo;Editing weights could remove an obstacle that hid an ability, but it could not add an ability the model lacked.&rdquo;',
             why_pl='Dowody na dziś: największa napisana sieć ma 1,5 mln wag i gra w go ze słabymi przeciwnikami, a jedyna edycja prawdziwego modelu naprawiła jedną usterkę w jednym przebiegu. Na Gemmie 3 270M, która rzadko się zapętla, to samo zadanie zostało blisko bazy (2,8% wobec 2,6&ndash;3,8% przy ścisłym ocenianiu). Post sam wyznacza granicę: &bdquo;Editing weights could remove an obstacle that hid an ability, but it could not add an ability the model lacked.&rdquo;'),
    ]


def narrative(ctx):
    if ctx["final"]:
        dec = ctx["dec"]
        missing = [k for k, v in (("calibration", dec.get("calibration", {}).get("both_pass")), ("q1", dec.get("q1")), ("q3", dec.get("q3"))) if v is None]
        assert not missing, f"--final needs the decision rules applied, still missing: {missing}"
    title_en, title_pl = same_score_title(ctx)
    return dict(
        h1_en="Astra can write weights. Beating humans and algorithms at reading them isn&rsquo;t shown",
        h1_pl="Astra potrafi pisać wagi. Przewagi nad ludźmi i algorytmami w ich czytaniu nikt nie pokazał",
        lead_en="A sentence-by-sentence check of the TL;DR of &ldquo;Sparks of Weight-Space Programming&rdquo; (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, November 2, 2026). All eight experiments were read in the authors' logs, and the Qwen result was re-measured on a home RTX 4060 under rules fixed in advance.",
        lead_pl="Sprawdzenie zdanie po zdaniu TL;DR posta &bdquo;Sparks of Weight-Space Programming&rdquo; (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, 2 listopada 2026). Wszystkie osiem eksperymentów przeczytano w logach autorów, a wynik na Qwen zmierzono ponownie na domowej karcie RTX 4060, według reguł ustalonych z góry.",
        strip=strip_items(ctx),
        strip_note_en="All on the full 500 problems. The cap is 32,768 tokens with thinking on and 8,192 with thinking off.",
        strip_note_pl="Wszystko na pełnych 500 zadaniach. Limit to 32 768 tokenów z myśleniem i 8192 bez niego.",
        card_title_en=title_en, card_title_pl=title_pl,
        card_foot_en="Qwen3.5-0.8B on a home RTX 4060, under rules fixed in advance. Thinking-off rows with the edit are exploratory.",
        card_foot_pl="Qwen3.5-0.8B na domowej karcie RTX 4060, według reguł ustalonych z góry. Wiersze z edycją bez myślenia są eksploracyjne.",
        share_title="Weight-space sparks, checked sentence by sentence",
        share_desc="Astra can write weights. Beating humans and algorithms at reading them isn't shown. All eight experiments read from the authors' logs, and the Qwen result re-measured on a home RTX 4060.",
        claims=claims(ctx),
    )
