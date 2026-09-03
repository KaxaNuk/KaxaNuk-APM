# Blueprint — Experiment N

> **The hypothesis, fixed once written.** Thesis, rules, success criteria and key risks, recorded
> *before* any code runs. Written by hand, or with the AI.
>
> **This file does not change when results arrive.** A hypothesis edited after its test is no longer
> a hypothesis — that is the whole reason it is kept apart from the result. What the experiment
> actually produced is in [`FINDINGS_N.md`](FINDINGS_N.md).
>
> Planning lives in [`BRAINSTORMING_N.md`](BRAINSTORMING_N.md), the running log in
> [`JOURNAL_N.md`](JOURNAL_N.md).
>
> Recorded <YYYY-MM-DD>, before the notebook's rule cell was written.

---

## Experiment N — <the idea, in five words>

### Thesis

<One paragraph. What this experiment claims, and the economic mechanism behind it — why the world
should work this way, not just what the statistics will show. For Experiment 1, the benchmark, the
claim is deliberately modest: a rule simple enough to be understood, liquid enough to be traded, and
stable enough to measure other things against. For every later experiment, the claim is an
improvement over the benchmark on a named axis.>

### Rules

- **Selection:** <the eligibility condition, naming the column — `c_<signal> == 1`>.
- **Ranking and sizing:** <the ranking column and the holding count; the weighting scheme; where
  the uninvested residual goes — `BIL`, a real priced instrument, because the engine's weight file
  has no cash row>.
- **Rebalancing:** <calendar, or event-driven on a stated trigger. State what happens between
  triggers — weights drift, nothing trades>.
- **What this experiment changes relative to the benchmark**, lever by lever, each isolated so
  attribution can tell them apart. <Experiment 1 has none.>

### Success criteria

<Stated before the result, against the benchmark, net of costs, over the same window. For example:
beat Experiment 1's Sharpe net of costs; cut maximum drawdown meaningfully; attribute the
improvement to the lever that earned it. A win that cannot be decomposed is not a finding.>

**Graduation:** <not applicable for the benchmark; for a candidate, the full gate is in
`Paper_Trading/BITACORA.md` and passing it is a decision, not a threshold>.

### Key risks

- **Survivorship and point-in-time integrity.** The universe must include delisted names;
  quantified in `Universe/universe.ipynb`.
- **<The signal's known weakness, accepted here or attacked here.>**
- **Multiple testing.** <How many variants this experiment will run. Running eleven and quoting the
  winner is exactly the situation the Deflated Sharpe Ratio exists for; the count is published
  beside the result.>
- **The signal may not be what earns the return.** If the book beats its benchmarks because it holds
  large, liquid, high-beta names rather than because of the signal, the honest product is a cheaper
  factor fund. Step 6 exists to answer this.
