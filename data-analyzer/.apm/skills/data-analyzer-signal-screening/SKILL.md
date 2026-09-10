---
name: data-analyzer-signal-screening
description: >
  Load this skill whenever you write, extend, run or read `Data/analyzer.ipynb` in a KN Research
  Process repository — step 3, block 3, where a feature earns a backtest or is dropped. Use it when
  the user asks whether a feature carries signal, for an information coefficient or information
  ratio, a rank-persistence or decay table, a coverage check, a diversification reading, a rank
  identity check, what a signal separates, what look-ahead costs a fitted signal, or what to write
  into a blueprint's predictions before an experiment runs. It covers the notebook's section
  contract, the per-date IC computation, why the IC table screens and does not prove, and where its
  findings go. It does NOT cover building the columns it reads (use
  `data-refinery-custom-calculations` and `data-curator-custom-calculations`), building a book, or
  reading attribution (use `alpha-decomposition`).
metadata:
  version: 0.1.0
---

# The Data Analyzer — where a feature earns a backtest

**In plain words:** build features and test whether they carry signal, before you model anything.
**It produces** the charts and the information-coefficient table in `Data/Analyzer/`. **It
prevents** a book built on a feature that never predicted anything.

The other two blocks of step 3 *produce* data; this notebook is where it is *understood*. It runs
after `Data/refinery.py` and before any experiment, because the predictions an experiment's
blueprint makes are supposed to come from here. `Universe/universe.ipynb` profiles the *catalogue*
— what exists, what is missing, from when the universe is usable; this notebook looks at the
**content**.

**A feature that fails here does not get a book built on it.** One that passes has earned a
backtest, not a belief.

## 1. The section contract

| Section | What it establishes |
| --- | --- |
| 0 · Setup | the refined panel, and **the columns this notebook reads, named once** — the eligibility column, the features it eats, the cross-sectional candidates to screen. Everything below re-runs unchanged when they change |
| 1 · What each stage contributed | the refined file is the Curator file plus columns, same rows; then **coverage per column**. A column at 60% coverage is not quietly averaged over the 60%: say so, and decide whether the gap is a warm-up, a late listing or a broken input |
| 2 · What diversification is actually available | buy-and-hold return, volatility and worst day per security; the correlation matrix, its mean off-diagonal and the extreme pairs. **If everything is one trade, choosing between them is theatre** |
| 3 · Are the cross-sectional columns what they claim to be? | every rank is a per-date percentile: check the mean against `(n + 1) / 2n` for that day's *n* ranked names, as an identity — 0.542 on twelve names, 0.5006 on eight hundred. Testing against 0.5 fails on a narrow universe and passes on a wide one |
| 4 · Information coefficient | for each feature and horizon, the per-date rank correlation with forward return, averaged; over the whole panel **and over the eligible pool the strategy actually selects from** |
| 5 · The two questions any signal owes | does the signal separate forward return *and* forward volatility by its state; and, if it is fitted, what look-ahead is worth |
| 6 · Handoff | what `Experiments/` reads, and what the blueprint may now predict |

Chart helpers, persistence and decay tables, a regime reading such as breadth, and a
classification view marked *current snapshot only* belong beside these when the strategy needs
them. What may not happen here is building a book, or choosing a parameter on the metric it will
later be judged by.

## 2. The information coefficient, computed the causal way

For each feature and horizon *h*:

1. Forward return from *t* to *t + h*, computed **within each identifier** — grouped, so one
   security's last rows never reach into the next one's first. The shift is negative: row *t*
   carries the return earned *after* *t*, which is exactly what a signal observed at *t* is asked to
   predict.
2. Re-rank the feature and the forward return **inside each date**, and correlate there. This is a
   Spearman correlation computed one cross-section at a time, never pooled across dates — pooling
   lets the sample's own time trend masquerade as predictive power.
3. **IC** is the mean of the daily correlations. The sign matters as much as the size: a negative IC
   means the feature works *inverted*. **IR** is IC divided by the standard deviation of the daily
   correlations — the consistency of the edge, which is what survives into a portfolio.
4. Do it twice: over the whole panel, and over the **eligible pool** the strategy selects from. The
   second is the one that matters — a feature can behave differently inside an already-filtered
   group, and it is the group the book is drawn from.

Write the table to `Data/Analyzer/` beside the charts, one row per feature, scope and horizon,
with IC, IC standard deviation, IR and the number of dates.

> **The IC table is a screening tool, not evidence.** An information ratio scales with the square
> root of the number of independent bets, so on a narrow universe read these as directional. In
> equities an IC of 0.02 to 0.05 in absolute value is a normal, usable signal; anything above 0.10
> deserves suspicion of look-ahead before celebration. IC is measured on ranks, not on a traded,
> costed portfolio: a feature with a good IC can still lose money after costs if it decays fast.

**Persistence is the turnover floor.** The autocorrelation of a feature's *rank* at lag *k* says
how much of today's selection still holds *k* days later. A feature whose rank autocorrelation
collapses within a month cannot drive selection in a book that rebalances on composition changes —
it would trigger constantly and pay costs for noise. A fast-decaying feature is not useless; it is
an *exit* signal rather than an entry one. Read decay beside the IC before committing a feature to
an experiment: persistence and predictive power both have to hold.

## 3. The two questions

**Does the signal separate anything?** Split forward return *and* forward volatility — realised
over the next window, a backward window shifted forward by its own length — by the signal's state
on the observation date. A signal can be worth trading on the second alone: the template's example
branch found its jump model separated risk, not return — forward volatility lower in the good
regime on 11 of 12 assets, forward return higher on only 5 of 12 — so the decomposition to expect
from the engine was a Sharpe gain through the denominator, and the blueprint said so before the run.

**If the signal is fitted, what is look-ahead worth?** Read the same model causally and smoothed
and report the gap. It is the cheapest audit in the process and routinely the largest number in it:
the two series agree on most days and differ exactly at the turning points, which is where the
money is. On the example branch the gap was worth 44 annualised points. If the signal is not fitted
— two moving averages compared on the day, say — write that the audit has nothing to compare,
rather than leaving the section out.

## 4. Where the findings go

**Findings from this stage go straight into `RESULTS.md`**, under *Before any experiment*, citing
the section each number came from. Notebook outputs are stripped before committing, so a
measurement living only in a cell output does not survive the commit — this is the one exception to
the rule that `RESULTS.md` is compiled from the findings files.

**Write down what you expect before you run the experiment.** The predictions this notebook
licenses go in `BLUEPRINT_N.md` *before* the backtest, each with the section it came from and the
observation that would falsify it. A prediction made from the data and then confirmed by the engine
is the strongest methodological result an experiment can report; a number found first and explained
afterwards is a story. `FINDINGS_N.md` then evaluates every prediction, including the wrong ones.

## What this skill will not let you do

- **Build a book here.** Weights, triggers and backtests are steps 4 and 5; this stage measures.
- **Choose a parameter on the metric it will be judged by.** Choose it on a property of the signal —
  persistence, coverage, turnover — and publish the sweep.
- **Report an IC without its scope, its horizon and its count of dates**, or without the coverage of
  the column it was computed on.
- **Pool a correlation across dates**, or compute a forward return without grouping by identifier.
- **Quote a number that lives only in a cell output.** It goes to `RESULTS.md` in the same
  change-set.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come
  from the template's `example` branch only.
