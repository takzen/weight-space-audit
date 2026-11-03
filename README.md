# Weight-space audit

An independent check of [“Sparks of Weight-Space Programming”](https://rikiyat.github.io/blog/weight-space-programming/) (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, November 2, 2026), sentence by sentence.

**Results page: https://takzen.github.io/weight-space-audit/** (English and Polish)

Po polsku: [README.pl.md](README.pl.md)

## What came out

**An interesting demo, but much less than the authors claim.**

- **Writing small networks holds.** With no feedback, Astra's networks beat PPO at 100M steps in all three games.
- **Reading weights better than humans or algorithms isn't shown.** The post tests neither, one line of numpy shows the same signal in its first experiment, and the only test on a large model failed.
- **The Qwen fix is real, but its 6x starts from the looping mode.** With thinking on, 93% of the unedited model's answers hit the token cap, so it scores 7.9%. The edit brings that down to 33% and the score up to 48.1%. With no edit and thinking off, the model's default mode, it scores 46.0% (95% interval 42.5–49.5).
- **With thinking off, the edit adds nothing measurable:** 43.0% against 46.0%, with one sample per problem for the edited model.
- **"Soon" is a forecast.** The largest written network has 1.5M weights, and the one edit of a real model repaired one failure in one run.

The 7.9% and 48.1% are the authors' numbers and weren't re-run here. A longer planned test was stopped early, and [DEVIATIONS.md](DEVIATIONS.md) lists what didn't run.

## What's here

| Path | Contents |
|---|---|
| `docs/` | The results page, served by GitHub Pages |
| `results/` | Scores in `summary.json` and `summary.md`, and raw answers as `.jsonl.gz` |
| `results_exploratory/` | The Exp 1 weight maps and the MinAtar control |
| `scripts/` | Generation, grading, analysis and the page builder |
| `scripts/audit/` | The checks run on the authors' logs |
| `DEVIATIONS.md` | Every change from the plan |

## How it was measured

- **Model:** `Qwen/Qwen3.5-0.8B` at revision `2fc06364`, with the authors' published `p50c` edit for the edited run.
- **Hardware and software:** one RTX 4060 (8 GB), vLLM 0.33.0.
- **Grading:** the authors' grader, which reproduced their grades on 400 of 400 published samples.
- **Statistics:** 95% bootstrap over problems, with paired differences on shared problems.

Astra itself wasn't re-run.

## Credit and disclosure

The authors published their logs and failures, which is what made this check possible.

Analysis, code and page: Claude Opus 5.5 (Anthropic). Anthropic competes with OpenAI, whose model the post tests. This work isn't affiliated with the authors, OpenAI, Qwen or MIT.

## License

Code is MIT. Text and results are CC BY 4.0. Details are in [LICENSE](LICENSE).
