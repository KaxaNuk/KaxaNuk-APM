---
name: alpha-decomposition
description: >
  Load this skill when a KaxaNuk Investment Lab strategy beats its benchmark and the question
  becomes "is the signal doing anything, or is this a factor exposure wearing the signal's name?".
  Use it to read Attribution Analysis output in two layers and a third pass — Brinson-Fachler, the
  factor model, Brinson-Fachler again on the residual — to decompose idiosyncratic return into
  selection, sizing and timing by building counterfactual books the Backtest Engine can price, to
  run the exclusion-filter test when the factor model is blind to an absolute rule, and to evidence
  graduation criterion 2. It does NOT run the engine or the attribution library for you — it says
  which books to price and how to read the numbers that come back. Shaping the attribution library's
  inputs and calling it is `attribution-analysis-runs`; pricing a book is `backtest-engine-runs`.
metadata:
  version: 0.2.1
---

# Alpha decomposition — is the signal doing anything?

A book that beats its benchmark has not been understood. It has been observed. This skill is the
procedure that turns "the book went up" into "here is the part of the return that is the idea, and
here is the part that is beta, size, sector and luck" — the question `RESULTS.md` has to answer
before a strategy can graduate, and one this stack can actually answer because step 6 exists.

The method is Paleologo's (*Advanced Portfolio Management*, 2021, chapter 8): split total return
into factor and idiosyncratic, then split the idiosyncratic part three ways **by counterfactual
books, never by formula**. The book is a lead in the template's `Bibliotheca/BIBLIOGRAPHY.md`; write
its note before citing it in a findings file. Every counterfactual below is a weight file, so the
same `Experiments/backtest_engine.py` that priced the real book prices it, over the same window, at
the same costs.

Work in the experiment's notebook, section 5 or a section after it. Record every number in
`FINDINGS_N.md`, then `RESULTS.md`. Publish the count of counterfactuals run.

## 1. First, two layers and a third pass — read what step 6 reports

Savvy investors follow a process, a thesis and data, and attribution gives all three about a book.
Run both methodologies (the experiment notebook's attribution cell does this) and record:

| Layer | From | Numbers to record | The question it answers |
| --- | --- | --- | --- |
| **First cut** | Brinson-Fachler | cumulative alpha; **allocation**, **selection**, **interaction** | is the return the groups the book leans into, or the names it picks inside them? The exact lever that moved |
| **Second layer** | the factor model | total excess; **factor** contribution by factor — beta, size, value, momentum, residual volatility, liquidity, industries — and the **idiosyncratic** residual | which systematic premia paid, on purpose or by accident? How much of this is a factor fund wearing the strategy's name? |
| **Third pass** | Brinson-Fachler on the residual | allocation and selection of the return left after factor exposure is stripped | does the selection story survive — and would the Sharpe survive once that factor turns? |

The third pass is what the first cut alone cannot give: a book that looks like skilful stock-picking
in Brinson-Fachler can be a persistent low-beta or momentum tilt that happened to pay over the
sample. The attribution library does not run Brinson-Fachler on residual returns directly, so build
the residual series from the factor model's output — `calc_pct_area()` names it `f_idio_returns`,
`cummulative_pct_decomp()` names it `idio_returns` — and run the first cut on it in the notebook,
saying in `FINDINGS_N.md` that it was done that way. Getting those tables out at all is
`attribution-analysis-runs`.

Two readings, both of which count as answers:

- **Allocation ≈ 0 with selection and interaction positive** means a large group tilt is *not*
  where the money comes from. Say so plainly; it is the opposite of what the tilt makes a reader
  assume.
- **A roughly even factor / idiosyncratic split** is a *pass with a qualification* on criterion 2.
  There is real idiosyncratic alpha, and half the excess is exposure available more cheaply
  elsewhere. Report both halves with equal weight.

State the attribution window beside the backtest window — it is bound by factor-file coverage and
benchmark-holdings start, and is usually shorter. Record how many factor files the run used;
attribution numbers are only comparable across runs when the factor set is identical.

## 2. When the factor model is blind — the absolute-versus-relative problem

**Momentum in a factor model is relative**: a name ranked against its peers. **A trend or regime
rule is absolute**: a name against its own history. The two produce different books from the same
names, and a factor model built on the relative kind is close to invisible to an absolute rule. So a
strategy can beat every benchmark while the model assigns roughly nothing to the factor its thesis
is named after.

**That is a finding, not a failure**, and it is the expected state for any threshold signal — a
moving-average cross, a breakout, a regime label, a drawdown gate. When you see it:

1. Say so in `FINDINGS_N.md`, in those terms.
2. Do not conclude the signal is weak. Conclude the model cannot see it, and go to section 4.
3. Rename the pillar in `OBJECTIVE.md` if it is called "momentum" and is a trend rule. The
   distinction predicts which factor model will see the strategy and which will not.

## 3. Then, the idiosyncratic part three ways — counterfactual books

Before any of them: **drop economically insignificant positions** from both the real book and the
counterfactuals, or the comparison is dominated by residual slivers nobody was betting on.

Each counterfactual keeps everything about the real book except one thing. The Sharpe difference
between the real book and the counterfactual, over the same engine window, is that one thing's
contribution. All three read the objects the experiment notebook already has — `selected_matrix`,
`REBALANCE_DATES`, `target_weights`, and the eligibility matrix the rule built them from — and hand a
new `target_weights` to `backtest_engine.to_engine_frame` and `backtest_engine.run_variant`.

### 3a. Sizing skill — equalise positions within each date

Same names, same dates, every held position at equal weight. Side and gross unchanged.

```python
held = target_weights > 0
sizing_counterfactual = held.astype(float).div(held.sum(axis=1), axis=0).fillna(0.0)
```

**Sharpe(real) − Sharpe(equal-weighted) is what sizing contributed.** Positive means the big
positions were the good ones. This is the cheapest counterfactual and often already exists: an
equal-weight variant in the same experiment *is* this book — and for a benchmark that is already
equal weight, sizing skill is zero by construction and should be reported as such.

### 3b. Selection skill — a random draw from the eligible pool at the same sizes

Same dates, same number of names, same weight vector — but the names are drawn at random from
what was eligible that day. Repeat K times; K is a trial count and is published.

```python
rng = numpy.random.default_rng(seed)
draws = []
for _ in range(K):
    rows = []
    for date in REBALANCE_DATES:
        real = target_weights.loc[date]
        weights = numpy.sort(real[real > 0].to_numpy())[::-1]          # the real size distribution
        pool = eligible_matrix.loc[date]
        picked = rng.choice(pool.index[pool], size=len(weights), replace=False)
        rows.append(pandas.Series(weights, index=picked, name=date))
    draws.append(pandas.DataFrame(rows).reindex(columns=target_weights.columns).fillna(0.0))
```

Price every draw. **The real book's percentile among the K random books is the selection skill**;
the mean random Sharpe is what the eligibility rule plus the sizing scheme earn *without* picking.
Report the percentile and K, as a permutation test reports a p-value.

### 3c. Timing skill — the same names with entry dates shifted

Same selections, same weights, every re-strike moved by a fixed lag (5, 21 days) or to a random
date inside a window around the real one. If moving the entries costs nothing, the rule has no
timing skill — it is a selection rule that happens to fire on some day.

```python
shifted_dates = REBALANCE_DATES + pandas.tseries.offsets.BDay(lag)
timing_counterfactual = target_weights.set_axis(shifted_dates)
```

Clip to trading days that exist in the panel and drop any shifted date past the sample's end.

### Reading the three together

| Counterfactual | Sharpe gap to the real book | Reading |
| --- | --- | --- |
| equal-weighted | small positive | sizing helps a little — say "a little", in Sharpe |
| random draw (mean) | large positive | the names matter; the rule is selecting, not just filtering |
| random draw (mean) | ≈ 0 | the eligibility filter plus sizing is the whole strategy |
| shifted entries | ≈ 0 | no timing skill; do not claim any |

Sizing plus selection plus timing does not have to sum to the idiosyncratic return — the
counterfactuals overlap. They are three questions, not a partition.

## 4. The exclusion-filter test — the counterfactual for an absolute rule

The direct test of whether a threshold signal earns its keep, and the fallback when section 2
applies: **the same book with the signal switched off.**

```python
eligible_without_signal = tradable_matrix & ~last_tradable_day          # signal removed
# then re-run the experiment's own selection and weighting on this eligibility matrix
```

Same ranking column, same holding count, same weighting, same trigger — only the eligibility
condition changes. Price both. **Sharpe(with signal) − Sharpe(without) is what the signal
contributes as a filter**, which a factor model cannot measure.

**What a null result means.** If the two books are close, the signal is not adding beyond the
sizing rule's own selection, and the honest description of the strategy is "top-N by the sizing
column". That is worth knowing and belongs in `OBJECTIVE.md` as a falsified claim.

## 5. The worked example — the template's `example` branch

The KN Research Process template carries one strategy worked end to end on its `example` branch:
twelve asset-class ETFs, a statistical jump model fitted per asset in the Refinery, and the
benchmark rule — hold every asset in its good regime, equally weighted, cash for the rest. The
licensed engines were absent from that clone, so **it was never priced and has no attribution**.
It still settled three things before any engine ran, and each is a lesson for this skill:

- **The signal separates risk, not return.** In the good regime forward volatility is lower on
  11 of 12 assets (−5.6 points a year) while forward return is higher on only 5 of 12. So the
  decomposition to expect, once priced, is a Sharpe gain through the denominator — and section 3b's
  random draws should be read on volatility as well as Sharpe.
- **Look-ahead was worth 44 annualised points.** The same fitted model read with hindsight
  (smoothed labels) showed a good-minus-bad forward return of +38.9%; read causally, −5.1%. The
  two agree on 81% of days and differ exactly at the turning points. Before decomposing any fitted
  signal, run this audit; it is one line of code and routinely the largest number in the file.
- **A blueprint prediction was falsified by the book's shape alone.** The blueprint predicted the
  book would average roughly half in cash; it averaged 95.3% invested, because equal weight over a
  shrinking eligible set concentrates rather than de-risks. The two levers the blueprint declined —
  a weight cap and a minimum holding count — turned out to be the entire defensive mechanism.

**What to run first when it is priced:** the exclusion-filter test (section 4), because the
strategy *is* the filter — same twelve assets, always eligible, equal weight. Sizing skill (3a) is
zero by construction. Timing (3c) matters, because the rule re-strikes about 40 times a year with
one-way turnover near 810% — the number most likely to decide whether the idea survives costs.

## What this skill will not let you do

- **Call a strategy understood on the factor split alone.** The split says how much is
  idiosyncratic; the counterfactuals say what the idiosyncratic part is made of.
- **Run one random draw.** K is a trial count. Publish it, and report the percentile, not the best
  draw.
- **Tune on the counterfactuals.** They measure the rule you stated in `BLUEPRINT_N.md`. A rule
  changed to look better against its own counterfactual is a new experiment with a new blueprint.
- **Quote a number that did not come from the engine.** Every counterfactual is priced by
  `backtest_engine.run_variant` over the shared window, never approximated.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come
  from the template's `example` branch only.
