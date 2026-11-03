"""The page's headline, conclusions and sentence-by-sentence answer to the post's TL;DR.

Measured numbers come from results/summary.json. The text states how those numbers read, and the asserts in facts() stop the
build if a number no longer supports that reading.
"""
N1, E2 = "N1_nothink_T07_p08_pp15", "E2_edit_nothink_T07"


def pct(x, d=1):
    return f"{100 * x:.{d}f}"


def pct_pl(x, d=1):
    return pct(x, d).replace(".", ",")


def points(x, lang="en"):
    s = f"{100 * x:+.1f}".replace("-", "−")
    return s if lang == "en" else s.replace(".", ",")


def facts(ctx):
    math = ctx["math"]
    n1, e2 = math["conditions"][N1], math["conditions"][E2]
    edit = next(c for c in ctx["dec"]["exploratory"] if c["a"] == E2 and c["b"] == N1)["acc"]
    assert n1["samples"] == 2000 and e2["samples"] == 500, "the text gives these sample sizes"
    assert edit["ci95"][0] <= 0 <= edit["ci95"][1], "the text says the edit adds nothing measurable with thinking off"
    authors = math["authors"]
    return dict(n1=n1, e2=e2, edit=edit, base=authors["unedited"]["full"]["acc"], edited=authors["p50c"]["full"]["acc"])


def strip_items(ctx):
    f = facts(ctx)
    return [(100 * f["base"], "The post: no edit, thinking on", "Post: bez edycji, myślenie włączone"),
            (100 * f["edited"], "The post: with the edit, thinking on", "Post: z edycją, myślenie włączone"),
            (100 * f["n1"]["acc"], "Measured here: no edit, thinking off, the model&rsquo;s default", "Zmierzone tutaj: bez edycji, myślenie wyłączone, tryb domyślny modelu"),
            (100 * f["e2"]["acc"], "Measured here: with the edit, thinking off", "Zmierzone tutaj: z edycją, myślenie wyłączone")]


def findings(ctx):
    f = facts(ctx)
    n1, e2, edited = f["n1"]["acc"], f["e2"]["acc"], f["edited"]
    return [
        ("<strong>Writing small networks: holds.</strong> With no feedback, Astra&rsquo;s networks beat PPO at 100M steps in all three games.",
         "<strong>Pisanie małych sieci: stoi.</strong> Bez informacji zwrotnej sieci Astry biją PPO po 100 mln kroków we wszystkich trzech grach."),
        ("<strong>Reading weights better than humans or algorithms: not shown.</strong> The post tests neither, one line of numpy shows the same signal in its first experiment, and the only test on a large model failed.",
         "<strong>Czytanie wag lepiej niż ludzie i algorytmy: nie pokazano.</strong> Post nie testuje ani jednych, ani drugich, w pierwszym eksperymencie jedna linijka numpy pokazuje ten sam sygnał, a jedyny test na dużym modelu się nie udał."),
        (f"<strong>The Qwen fix: real, but its 6x starts from the looping mode.</strong> With no edit and thinking off, the model&rsquo;s default, it scores {pct(n1)}%. The post&rsquo;s edited score is {pct(edited)}%. With thinking off, the edit adds nothing measurable ({pct(e2)}%).",
         f"<strong>Naprawa Qwena: prawdziwa, ale jej 6x liczone jest od trybu z pętlami.</strong> Bez edycji, z wyłączonym myśleniem, czyli w trybie domyślnym, model ma {pct_pl(n1)}%. Post po edycji ma {pct_pl(edited)}%. Przy wyłączonym myśleniu edycja nie dodaje niczego mierzalnego ({pct_pl(e2)}%)."),
        ("<strong>&ldquo;Soon&rdquo;: a forecast.</strong> The largest written network has 1.5M weights, and the one edit of a real model repaired one failure in one run.",
         "<strong>&bdquo;Wkrótce&rdquo;: to prognoza.</strong> Największa napisana sieć ma 1,5 mln wag, a jedyna edycja prawdziwego modelu naprawiła jedną usterkę w jednym przebiegu."),
    ]


def limits(ctx):
    f = facts(ctx)
    n1, e2, base, edited = f["n1"]["acc"], f["e2"]["acc"], f["base"], f["edited"]
    return [
        ("<strong>Astra wasn&rsquo;t re-run.</strong> Everything about it comes from the authors&rsquo; logs, so nothing here says how often it would find the fix again.",
         "<strong>Astry nie uruchamiano ponownie.</strong> Wszystko o niej pochodzi z logów autorów, więc nic tu nie mówi, jak często znalazłaby tę naprawę ponownie."),
        (f"<strong>The post&rsquo;s {pct(base)}% and {pct(edited)}% weren&rsquo;t re-run.</strong> They come from the authors&rsquo; files. A longer test, with that re-run and other temperatures, was stopped early because it needed about ten more hours, so this page says nothing about temperature.",
         f"<strong>Wyników posta {pct_pl(base)}% i {pct_pl(edited)}% nie powtórzono.</strong> Pochodzą z plików autorów. Dłuższy test, z tą powtórką i innymi temperaturami, przerwano, bo wymagał jeszcze około dziesięciu godzin, więc ta strona nic nie mówi o wpływie temperatury."),
        (f"<strong>{pct(n1)}% and {pct(edited)}% aren&rsquo;t a strict comparison.</strong> They come from different machines and different modes, with token caps of 8,192 and 32,768. They show the same range, not a tie.",
         f"<strong>{pct_pl(n1)}% i {pct_pl(edited)}% to nie jest ścisłe porównanie.</strong> Pochodzą z różnych maszyn i różnych trybów, z limitami 8192 i 32 768 tokenów. Pokazują ten sam zakres, a nie remis."),
        (f"<strong>The {pct(e2)}% comes from one sample per problem, and the {pct(n1)}% from four.</strong> The {pct(e2)}% run was added after the original plan.",
         f"<strong>{pct_pl(e2)}% to jedna próbka na zadanie, a {pct_pl(n1)}% to cztery.</strong> Przebieg z {pct_pl(e2)}% doszedł już po pierwotnym planie."),
        ("<strong>Thinking off isn&rsquo;t better everywhere.</strong> The model card scores thinking on higher on some benchmarks, such as MMLU-Pro.",
         "<strong>Wyłączone myślenie nie jest lepsze wszędzie.</strong> Karta modelu daje włączonemu myśleniu wyższe wyniki na niektórych benchmarkach, np. MMLU-Pro."),
    ]


def claims(ctx):
    f = facts(ctx)
    n1, e2, edit = f["n1"], f["e2"], f["edit"]
    lo, hi = n1["acc_ci95"]
    m, r = ctx["minatar"], ctx["recheck"]
    bo_lo, bo_hi = sorted((m["breakout"]["network"]["mean"], r["mean"]))
    as_n, se_n = m["asterix"]["network"]["mean"], m["seaquest"]["network"]["mean"]
    as_en, se_en = f"{as_n:.1f}", f"{se_n:.1f}"
    as_pl, se_pl = as_en.replace(".", ","), se_en.replace(".", ",")
    return [
        dict(q_en="We find that frontier LLMs are surprisingly good at natively reading and writing neural network weights, well past what we&rsquo;d expect from humans or conventional algorithms.",
             q_pl="Odkryliśmy, że czołowe LLM-y są zaskakująco dobre w natywnym czytaniu i pisaniu wag sieci neuronowych, znacznie lepsze, niż oczekiwalibyśmy od ludzi lub konwencjonalnych algorytmów.",
             kind="no", v_en="Not shown", v_pl="Nie pokazano",
             why_en="The post tests no humans, and for reading it compares with no algorithm. Its only comparison is PPO, for writing. In its first experiment, one line of numpy draws the game from the weights, as in the map on this page. Whether a person could then name the game wasn&rsquo;t tested.",
             why_pl="Post nie testuje ludzi, a przy czytaniu nie porównuje z żadnym algorytmem. Jego jedyne porównanie to PPO, przy pisaniu. W pierwszym eksperymencie jedna linijka numpy rysuje grę z samych wag, jak na mapie na tej stronie. Nie sprawdzano, czy człowiek nazwałby potem grę."),
        dict(q_en="Just by looking at the raw weights, GPT-6 Astra can tell what a network was trained to do.",
             q_pl="Patrząc tylko na surowe wagi, GPT-6 Astra potrafi określić, do czego sieć wytrenowano.",
             kind="part", v_en="True for small networks", v_pl="Prawda dla małych sieci",
             why_en="It gets 4 of 4 game networks and 3 of 3 diffusion models right, and the signal sits in one layer each time. It also names three languages and finds every copying head in small transformers, with Python and a published recipe. The only test of reading a behaviour from weights in a large model failed: Astra couldn&rsquo;t tell the sycophantic Gemma from the honest one, as the post reports.",
             why_pl="Trafnie rozpoznaje 4 z 4 sieci do gier i 3 z 3 modeli dyfuzyjnych, a sygnał leży za każdym razem w jednej warstwie. W małych transformerach nazywa też trzy języki i znajduje wszystkie głowy kopiujące, z Pythonem i opublikowanym przepisem. Jedyny test odczytania zachowania z samych wag w dużym modelu się nie udał: Astra nie odróżniła lizusowskiej Gemmy od uczciwej, co post przyznaje."),
        dict(q_en="And without any environment feedback, it has no trouble writing, from scratch, small game-playing networks that outplay networks trained with PPO for 100 million steps.",
             q_pl="A bez żadnej informacji zwrotnej ze środowiska bez trudu pisze od zera małe sieci do gier, które ogrywają sieci trenowane algorytmem PPO przez 100 milionów kroków.",
             kind="yes", v_en="Holds", v_pl="Stoi",
             why_en=f"The logs confirm it: no tool calls, and all three games above PPO at 100M steps. Re-scored here, the networks reach {bo_lo:.0f}&ndash;{bo_hi:.0f} on Breakout (published 517), {as_en} on Asterix and {se_en} on Seaquest (published 53.2 and 53.1). Short rule-based programs written once by Claude, as a check meant to deflate the result, lost all three games. This is the post&rsquo;s strongest result. PPO at 100M is a low bar, though: at 500M its best seed still beats Astra on Asterix and Seaquest.",
             why_pl=f"Logi to potwierdzają: zero wywołań narzędzi i wszystkie trzy gry powyżej PPO po 100 mln kroków. Policzone tu ponownie sieci osiągają {bo_lo:.0f}&ndash;{bo_hi:.0f} w Breakoucie (opublikowane 517), {as_pl} w Asterixie i {se_pl} w Seaquest (opublikowane 53,2 i 53,1). Krótkie programy regułowe napisane raz przez Claude&rsquo;a, jako kontrola mająca osłabić wynik, przegrały we wszystkich trzech grach. To najmocniejszy wynik posta. PPO po 100 mln to jednak niska poprzeczka: po 500 mln jego najlepsze ziarno nadal bije Astrę w Asterixie i Seaquest."),
        dict(q_en="Likewise, asked to make Qwen3.5-0.8B better at math without gradients, Astra identifies an issue in its weights causing reasoning loops that Qwen&rsquo;s own model card warns about, and fixes this by natively editing 0.016% of the weights.",
             q_pl="Podobnie, poproszona o poprawę Qwen3.5-0.8B w matematyce bez gradientów, Astra wykrywa w jego wagach problem powodujący pętle rozumowania, przed którymi ostrzega karta modelu, i naprawia go, natywnie edytując 0,016% wag.",
             kind="part", v_en="The fix is real. The wording oversells it", v_pl="Naprawa jest prawdziwa. Opis ją zawyża",
             why_en="The fix works on problems Astra held out, and an edit in a random direction gains almost nothing. But the prompt itself points at the loops (&ldquo;if the model often fails because it repeats itself and never finishes&rdquo;), while the authors&rsquo; thread says &ldquo;We simply asked&rdquo;. &ldquo;Natively&rdquo; took 20 hours, 80 Python runs and about 6,000 generated answers. &ldquo;0.016%&rdquo; counts the weights touched, while the two edited matrices change by 10.6% and 8.1%. It is also one run: of 7 completed Qwen runs, the other six gained at most 6.2 points.",
             why_pl="Naprawa działa na zadaniach odłożonych przez samą Astrę, a edycja w losowym kierunku nie daje prawie nic. Ale prompt sam naprowadza na pętle (&bdquo;if the model often fails because it repeats itself and never finishes&rdquo;), a wątek autorów mówi &bdquo;We simply asked&rdquo;. &bdquo;Natively&rdquo; to 20 godzin, 80 uruchomień Pythona i około 6000 wygenerowanych odpowiedzi. &bdquo;0.016%&rdquo; to liczba dotkniętych wag, a dwie edytowane macierze zmieniają się o 10,6% i 8,1%. To też jeden przebieg: z 7 ukończonych przebiegów na Qwenie pozostałe sześć zyskało najwyżej 6,2 pkt."),
        dict(q_en="With the same sampling settings, this weight correction raises MATH-500 from 7.9% to 48.1% and generalizes out of the box to instruction following, raising IFEval by 3x.",
             q_pl="Przy tych samych ustawieniach próbkowania ta korekta wag podnosi MATH-500 z 7,9% do 48,1% i od razu uogólnia się na wykonywanie instrukcji, podnosząc IFEval trzykrotnie.",
             kind="part", v_en="The jump starts from the looping mode", v_pl="Skok liczony jest od trybu z pętlami",
             why_en=["The 7.9% describes a model that rarely finishes: with thinking on, 93% of its answers hit the token cap. The edit brings that down to 33%, and the gain comes from those answers, as the post says too. These are the authors&rsquo; numbers, not re-run here.",
                     f"With no edit and thinking off, the model&rsquo;s default mode, the same model scores {pct(n1['acc'])}% on all 500 problems (95% interval {pct(lo)}&ndash;{pct(hi)}), although {pct(n1['cut_share'], 0)}% of its answers are cut there too. In that mode the edit adds nothing measurable: {pct(e2['acc'])}%, a change of {points(edit['diff'])} points (95% interval {points(edit['ci95'][0])} to {points(edit['ci95'][1])}).",
                     "IFEval wasn&rsquo;t measured here. The post&rsquo;s base of 21.0 is under half the model card&rsquo;s 44.0 with thinking on and 52.1 with thinking off, so against the card the 3x shrinks to about 1.4x and 1.2x, with protocols that differ."],
             why_pl=["Te 7,9% opisuje model, który rzadko kończy: z włączonym myśleniem 93% odpowiedzi dochodzi do limitu tokenów. Edycja obniża to do 33%, a zysk pochodzi właśnie z tych odpowiedzi, co mówi też post. To liczby autorów, tu ich nie powtórzono.",
                     f"Bez edycji, z wyłączonym myśleniem, czyli w trybie domyślnym, ten sam model ma {pct_pl(n1['acc'])}% na wszystkich 500 zadaniach (przedział 95% {pct_pl(lo)}&ndash;{pct_pl(hi)}), choć i tu {pct_pl(n1['cut_share'], 0)}% odpowiedzi jest uciętych. W tym trybie edycja nie dodaje niczego mierzalnego: {pct_pl(e2['acc'])}%, czyli zmiana o {points(edit['diff'], 'pl')} pkt (przedział 95% {points(edit['ci95'][0], 'pl')} do {points(edit['ci95'][1], 'pl')}).",
                     "IFEval nie był tu mierzony. Baza posta, 21,0, to mniej niż połowa liczb z karty modelu: 44,0 z myśleniem i 52,1 bez niego, więc względem karty 3x kurczy się do około 1,4x i 1,2x, przy różnych protokołach."]),
        dict(q_en="All of this is possible without allowing Astra to write training loops. It uses its reasoning to figure out what each part of a neural network computes, or should compute, and changes the weights accordingly.",
             q_pl="Wszystko to jest możliwe bez pozwalania Astrze na pisanie pętli treningowych. Używa rozumowania, by ustalić, co każda część sieci oblicza lub powinna obliczać, i odpowiednio zmienia wagi.",
             kind="part", v_en="True for training loops, thin for the rest", v_pl="Prawda co do pętli treningowych, reszta słabo podparta",
             why_en="The prompts forbid training and the logs show none. In four experiments &ldquo;its reasoning&rdquo; is one reply with no tools, which is impressive. For Go and Qwen it also means Python, measured activations and many runs of the model. &ldquo;What each part of a neural network computes&rdquo; has less behind it: 56 of 144 head labels in the third experiment are &ldquo;unclear&rdquo;, and in the one causal check in the logs, the parts Astra named moved the result less than random ones (0.04 against 0.19).",
             why_pl="Prompty zabraniają treningu i logi go nie pokazują. W czterech eksperymentach &bdquo;rozumowanie&rdquo; to jedna odpowiedź bez narzędzi, co robi wrażenie. Przy go i Qwenie to także Python, zmierzone aktywacje i wiele przebiegów modelu. Za &bdquo;co każda część oblicza&rdquo; stoi mniej: 56 ze 144 etykiet głów w trzecim eksperymencie to &bdquo;unclear&rdquo;, a w jedynej kontroli przyczynowej w logach składniki wskazane przez Astrę zmieniły wynik mniej niż losowe (0,04 wobec 0,19)."),
        dict(q_en="Throughout the history of deep learning, we encoded our simplistic inductive biases into tiny symbolic optimizers like Adam or Muon. This is changing: our neural network weights will soon be natively optimized by LLMs that deliberately reason about their weights.",
             q_pl="Przez całą historię głębokiego uczenia kodowaliśmy nasze uproszczone założenia indukcyjne w maleńkich symbolicznych optymalizatorach, takich jak Adam czy Muon. To się zmienia: wagi naszych sieci wkrótce będą natywnie optymalizowane przez LLM-y, które świadomie rozumują o swoich wagach.",
             kind="fore", v_en="A forecast these results can't carry", v_pl="Prognoza, której te wyniki nie uniosą",
             why_en="The largest written network has 1.5M weights and plays Go against weak opponents, and the one edit of a real model repaired one failure in one run. On Gemma 3 270M, which rarely loops, the same task stayed near the base (2.8% against 2.6&ndash;3.8%, under strict grading). The post sets the limit itself: &ldquo;Editing weights could remove an obstacle that hid an ability, but it could not add an ability the model lacked.&rdquo;",
             why_pl="Największa napisana sieć ma 1,5 mln wag i gra w go ze słabymi przeciwnikami, a jedyna edycja prawdziwego modelu naprawiła jedną usterkę w jednym przebiegu. Na Gemmie 3 270M, która rzadko się zapętla, to samo zadanie zostało blisko bazy (2,8% wobec 2,6&ndash;3,8%, przy ścisłym ocenianiu). Post sam wyznacza granicę: &bdquo;Editing weights could remove an obstacle that hid an ability, but it could not add an ability the model lacked.&rdquo;"),
    ]


def narrative(ctx):
    return dict(
        h1_en="An interesting demo, but much less than the authors claim",
        h1_pl="Ciekawy pokaz, ale dużo mniej, niż piszą autorzy",
        lead_en="A sentence-by-sentence check of the TL;DR of &ldquo;Sparks of Weight-Space Programming&rdquo; (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, November 2, 2026), based on the authors' public logs and two runs of Qwen.",
        lead_pl="Sprawdzenie zdanie po zdaniu TL;DR posta &bdquo;Sparks of Weight-Space Programming&rdquo; (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, 2 listopada 2026), na podstawie publicznych logów autorów i dwóch przebiegów na Qwenie.",
        strip=strip_items(ctx),
        strip_note_en="MATH-500, all 500 problems. The 7.9% and 48.1% are the authors' numbers, not re-run here.",
        strip_note_pl="MATH-500, wszystkie 500 zadań. 7,9% i 48,1% to liczby autorów, tu ich nie powtórzono.",
        share_title="An interesting demo, but much less than the authors claim",
        share_desc="A sentence-by-sentence check of the TL;DR of Sparks of Weight-Space Programming, based on the authors' public logs and two runs of Qwen.",
        claims=claims(ctx),
    )
