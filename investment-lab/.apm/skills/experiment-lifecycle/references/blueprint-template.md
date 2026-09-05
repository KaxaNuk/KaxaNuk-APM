# Blueprint — Experiment N

> **The hypothesis, fixed once written.** Thesis, rules, predictions, success criteria and key
> risks, recorded *before* any code runs.
>
> **This file does not change when results arrive.** A hypothesis edited after its test is no longer
> a hypothesis — that is the whole reason it is kept apart from the result. What the experiment
> actually produced is in [`FINDINGS_N.md`](FINDINGS_N.md); planning lives in
> [`BRAINSTORMING_N.md`](BRAINSTORMING_N.md), the running log in [`JOURNAL_N.md`](JOURNAL_N.md).
>
> Record the date it was written, and delete this blockquote.

---

## Experiment N — <the idea, in five words>

### Thesis

One paragraph: what book this rule produces, and why it is a fair yardstick — sensible, liquid,
low-complexity — for judging whether any later idea adds value. **Be modest on purpose.** The
benchmark does not assert its signal is the best of its kind, only that it is simple enough to be
understood, liquid enough to be traded, and stable enough to measure other things against.

### Rules

- **Selection:** the eligibility condition, naming the column it reads.
- **Sizing:** the weighting scheme. Say which constraints are switched off, and that each one is a
  lever a later experiment has to earn.
- **Cash:** where the uninvested residual goes — a real, priced instrument, because the engine's
  weight file has no cash row.
- **Timing:** calendar, or event-driven on a stated trigger. Say what happens between triggers.
- **Lag:** how many days between the signal and the fill, and what the engine adds on top.
- **Screens deliberately absent**, and why each is redundant under the rules above.

### What this experiment should show

**Predictions, fixed before the run.** Each should come from `Data/analyzer.ipynb`, which measures
the signal but builds no book. Getting these right is worth more than a good Sharpe; getting them
wrong is worth more than a bad one.

| # | Prediction | Where it comes from | What would falsify it |
| --- | --- | --- | --- |
| 1 | what the book should do | a `Bibliotheca/` note, or the analyzer section and its number | the observation that would refute it |

Note anything you are watching but cannot predict, because nothing licenses a prediction about it.
Costs usually belong here.

### Success criteria

As the benchmark, Experiment 1 does not need to win. It needs to be a **fair, stable yardstick**:

1. Reproducible from a clean clone, through the pipeline, with no manual step.
2. A tradeable trigger frequency — not a rule that fires every day.
3. Net-of-cost results reported against every benchmark it declares.
4. Every prediction above evaluated explicitly in `FINDINGS_N.md`, **including the ones that turn
   out wrong.**

**Graduation: not applicable.** The benchmark's job is to be the thing others are measured against,
so it stays in the Lab even if it scores well.

### Key risks

- **Survivorship and point-in-time integrity.** The universe must include delisted names; step 2
  quantifies how many.
- **The signal's known weakness** — slow exits, whipsaw, regime dependence — accepted here on
  simplicity grounds and attacked in a later experiment.
- **Concentration.** How the weighting concentrates, and which diagnostics measure it.
- **The signal may not be what earns the return.** If the book beats its benchmarks because of a
  factor exposure rather than the signal, the honest product is a cheaper factor fund. That is what
  step 6 exists to answer.

### Open questions this experiment deliberately does not answer

Each is a later experiment, and each has to beat this one.
