# Audyt programowania wag

Niezależne sprawdzenie, zdanie po zdaniu, posta [„Sparks of Weight-Space Programming”](https://rikiyat.github.io/blog/weight-space-programming/) (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, 2 listopada 2026).

**Strona z wynikami: https://takzen.github.io/weight-space-audit/#pl** (po polsku i angielsku)

In English: [README.md](README.md)

> Pomiary jeszcze trwają. Strona i ten plik są aktualizowane, gdy się kończą.

## Co wyszło

- **Pisanie wag: stoi.** Bez informacji zwrotnej sieci Astry biją PPO po 100 mln kroków we wszystkich trzech grach.
- **Czytanie wag lepiej niż ludzie i algorytmy: nie pokazano.** Post nie testuje ani jednych, ani drugich, w eksp. 1 jedna linijka numpy pokazuje ten sam sygnał, a jedyny test na dużym modelu się nie udał.
- **Naprawa Qwena: prawdziwa, ale jej 6x liczone jest od trybu z pętlami.** Z włączonym myśleniem 93% odpowiedzi modelu bez edycji dochodzi do limitu tokenów, stąd wynik 7,9%. Edycja obniża to do 33%, a wynik rośnie do 48,1%. Bez edycji, z wyłączonym myśleniem, czyli w trybie domyślnym, model ma 46,0% (przedział 95%: 42,5–49,5).
- **Przy wyłączonym myśleniu edycja na razie nie dodaje niczego mierzalnego:** 43,0% wobec 46,0%, po jednej próbce na zadanie. Kolejne próbki są w kolejce.

Wyniki 7,9% i 48,1% to liczby autorów i są tu właśnie mierzone ponownie.

## Co tu jest

| Ścieżka | Zawartość |
|---|---|
| `docs/` | Strona z wynikami, serwowana przez GitHub Pages |
| `results/` | Wyniki w `summary.json` i `summary.md` oraz surowe odpowiedzi jako `.jsonl.gz` |
| `results_exploratory/` | Mapy wag z eksp. 1 i kontrola MinAtar |
| `scripts/` | Generowanie, ocenianie, analiza i budowanie strony |
| `scripts/audit/` | Sprawdzenia logów autorów |
| `DEVIATIONS.md` | Każda zmiana względem planu |

## Jak to zmierzono

- **Model:** `Qwen/Qwen3.5-0.8B` w rewizji `2fc06364`, a w wierszach z edycją opublikowany przez autorów diff `p50c`.
- **Sprzęt i oprogramowanie:** jedna karta RTX 4060 (8 GB), vLLM 0.33.0.
- **Ocenianie:** grader autorów, który odtworzył ich oceny na 400 z 400 opublikowanych próbek.
- **Statystyka:** 95% bootstrap po zadaniach, a różnice sparowane na wspólnych zadaniach.

Reguły decyzyjne ustalono przed pierwszą mierzoną odpowiedzią, a strona pokazuje je przy każdym wyniku. Astry nie uruchamiano ponownie.

## Podziękowania i zastrzeżenie

Autorzy opublikowali logi i porażki, dzięki czemu to sprawdzenie było w ogóle możliwe.

Analiza, kod i strona: Claude Opus 5.5 (Anthropic). Anthropic konkuruje z OpenAI, którego model testuje post. Praca nie jest związana z autorami, OpenAI, Qwen ani MIT.

## Licencja

Kod na licencji MIT, a tekst i wyniki na CC BY 4.0. Szczegóły są w [LICENSE](LICENSE).
