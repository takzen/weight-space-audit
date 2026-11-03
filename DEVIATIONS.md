# Changes from the plan

The plan stays as frozen (sha256 `24800e252cd45303cdb3473de1236783de46640bae726bd52d5fac6174f87dfd`), and its full text is on the
results page. Everything that differs from it is listed here, in the order it happened. The decision rules have not changed.

## Before the restart, on 2026-11-02

1. **Process cleanup in `run_cond.py`, after the queue had started.** vLLM's engine outlives its parent, so a run now stops
   leftover engines at start and its own engine at exit. Generation code is unchanged.
2. **Rule code added to `analyze.py`, after the queue had started.** It applies the plan's rules to the saved answers.
3. **One partial look at N1 math500**, at 218 answers (119 correct, 53 cut at 8,192 tokens), to check that the runner and the
   grader worked. The count is biased because short answers finish first. It changed nothing.
4. **Exploratory additions after the freeze:** the Experiment 1 weight maps and the MinAtar control. Both are labelled exploratory.

## The restart

5. **The run stopped overnight and resumed on 2026-11-03.** It stopped with 831 of 2,000 N1 math500 answers saved, all valid.
   The answers in flight were generated again on resume, so the finished condition has no gap.

## Changes made on restart, on 2026-11-03 around 05:00

Decided before any of C0, E0, C1, E1, C3, C2 or N2 had produced an answer. The only measured results known at that point were
the partial look above.

6. **Deadline moved from 07:30 to 18:00 on 2026-11-03.** With 07:30, only N1 and part of C0 would have run, so none of the
   decision rules could have been applied.
7. **Running order changed** so that the conditions the decision rules need come first:
   - Plan: N1 math500, N1 gsm8k, C0, E0, C1, C3, E1, N2 math500, N2 gsm8k, C2.
   - Now: N1 math500, C0, E0, C1, E1, N1 gsm8k, C3, N2 math500, N2 gsm8k, C2.
8. **`run_queue_v2.sh` waits for free GPU memory before each attempt.** `run_queue.sh` is the original version. Settings, seeds
   and generation are unchanged.
9. **One exploratory condition added, around 05:05 on 2026-11-03: the edited model with thinking off** (`E2_edit_nothink_T07`, the
   settings of N1, MATH-500 first with 1 sample, later with 4, and GSM8K last if time allows). The plan left this out because the
   post's protocol is thinking on. It answers a question the other conditions can't: does the edit add anything when the model
   doesn't loop? It was added before N1 had finished and before any edited answer with thinking off existed. It sits behind
   `run_queue_v3.sh`, which replaced v2 after a few minutes, and only its first 500 answers run ahead of the plan's conditions,
   about 20 minutes. It decides no rule, and the page labels it exploratory.
10. **Exploratory comparisons added to `analyze.py`:** E2 minus N1, and N1 and E2 against the authors' per-problem results on all
    500 problems. They use the authors' published scores directly, so they lean on the calibration of C0 and E0. Also added:
    finished answers from E0 and E1 against N1 on the same problems. Finishing relates to being right within a problem, so this
    describes finished answers and shows no cause. None of these comparisons decides a rule.
11. **What E2 can show, restated at about 05:50 on 2026-11-03, before E2 had finished and before any of its answers were read.**
    Item 9 called thinking off the mode where the model doesn't loop. N1 then showed 31.4% of answers cut at 8,192 tokens, so this
    mode often fails to finish too, and fewer cuts there would be the same defect. A comparison of finished answers, E2 against N1,
    was added to `analyze.py`. The page reports accuracy, cut share and finished answers for E2, and it says the edit does more than
    let answers finish only if accuracy rises and the interval for finished answers sits above zero. This decides no rule.
