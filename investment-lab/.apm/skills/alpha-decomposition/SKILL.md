---
name: alpha-decomposition
description: >
  Load this skill when a KaxaNuk Investment Lab strategy beats its benchmark and the question
  becomes "is the signal doing anything, or is this a factor exposure wearing the signal's name?".
  Use it to read Attribution Analysis output (Brinson-Fachler, KN5FM), to decompose idiosyncratic
  return into selection, sizing and timing by building counterfactual books the Backtest Engine can
  price, to run the exclusion-filter test when the factor model is blind to an absolute rule, and
  to evidence graduation criterion 2. It does NOT run the engine or the attribution library for
  you — it says which books to price and how to read the numbers that come back.
metadata:
  version: 0.1
---

# Alpha decomposition — is the signal doing anything?

A book that beats its benchmark has not been understood. It has been observed. This skill is the
procedure that turns "the book went up" into "here is the part of the return that is the idea, and
here is the part that is beta, size, sector and luck" — the question `RESULTS.md` has to answer
before a strategy can graduate, and one this stack can actually answer because step 6 exists.

The method is Paleologo's (*Advanced Portfolio Management*, chapter 8): split total return into
factor and idiosyncratic, then split the idiosyncratic part three ways **by counterfactual books,
never by formula**. Every counterfactual below is a weight file, so the same `engine.py` that
priced the real book prices it, over the same window, at the same costs.

Work in the experiment's notebook, section 5 or a section after it. Record every number in
`FINDINGS_N.md`, then `RESULTS.md`. Publish the count of counterfactuals run.

## 1. First, the factor / idiosyncratic split — read what step 6 already reports

Run both KaxaNuk methodologies (the experiment notebook's attribution cell does this) and pull out:

| From | Numbers to record | The question each answers |
| --- | --- | --- |
| **Brinson-Fachler** | cumulative alpha; **allocation**, **selection**, **interaction** effects | is the return the sectors the book leans into, or the names it picks inside them? |
| **KN5FM** | total excess; **factor** contribution by factor — beta, size, value, momentum, residual volatility, industries — and the **idiosyncratic** residual | how much of this is a factor fund wearing the strategy's name? |

Two readings, both of which count as answers:

- **Allocation ≈ 0 with selection and interaction positive** means a large sector tilt is *not*
  where the money comes from. Say so plainly; it is the opposite of what the tilt makes a reader
  assume.
- **A roughly even factor / idiosyncratic split** is a *pass with a qualification* on criterion 2.
  There is real idiosyncratic alpha, and half the excess is exposure available more cheaply
  elsewhere. Report both halves with equal weight.

State the attribution window beside the backtest window — it is bound by factor-file coverage and
benchmark-holdings start, and is usually shorter. Record how many factor files the run used;
attribution numbers are only comparable across runs when the factor set is identical.

## 2. When the factor model is blind — the absolute-versus-relative problem

**Momentum in a factor model is relative**: a name ranked against its peers. **A trend rule is
absolute**: a name against its own history. The two produce different books from the same names,
and a factor model built on the relative kind is close to invisible to an absolute rule. So a
strategy can beat every benchmark while KN5FM assigns ~0% to the factor its thesis is named after.

**That is a finding, not a failure**, and it is the expected state for any threshold signal — a
moving-average cross, a breakout, a drawdown gate. When you see it:

1. Say so in `FINDINGS_N.md`, in those terms.
2. Do not conclude the signal is weak. Conclude the model cannot see it, and go to section 4.
3. Rename the pillar in `OBJECTIVE.md` if it is called "momentum" and is a trend rule. The
   distinction predicts which factor model will see the strategy and which will not.

## 3. Then, the idiosyncratic part three ways — counterfactual books

Before any of them: **drop economically insignificant positions** from both the real book and the
counterfactuals, or the comparison is dominated by residual slivers nobody was betting on.

Each counterfactual keeps everything about the real book except one thing. The Sharpe difference
between the real book and the counterfactual, over the same engine window, is that one thing's
contribution. All three read the objects the experiment notebook already has — `eligible_matrix`,
`selected_matrix`, `REBALANCE_DATES`, `target_weights`, `sizing_matrix` — and hand a new
`target_weights` to `engine.to_engine_frame` and `engine.run_variant`.

### 3a. Sizing skill — equalise positions within each date

Same names, same dates, every held position at equal weight. Side and gross unchanged.

```python
held = target_weights > 0
sizing_counterfactual = held.astype(float).div(held.sum(axis=1), axis=0).fillna(0.0)
```

**Sharpe(real) − Sharpe(equal-weighted) is what sizing contributed.** Positive means the big
positions were the good ones. This is the cheapest counterfactual and often already exists: an
equal-weight variant in the same experiment *is* this book.

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

## 5. The worked example — the reference implementation

Golden Flow, Experiment 1 against KN600, 2017-01-03 to 2025-08-12, 99.5% factor coverage:

- **Brinson-Fachler:** +24% cumulative alpha; allocation **≈ 0%**, selection **+5.7%**, interaction
  **+18%**. A large Technology overweight that contributed nothing on its own.
- **KN5FM:** ~+17% total excess; beta **+10.5%**, size **+9.8%**, momentum **+1.0%**,
  idiosyncratic **~+9%**. Half factor, half idiosyncratic — criterion 2 passed with a qualification.
- **Section 2 applied:** the golden cross is an absolute rule; KN5FM's momentum is relative; the
  ~1% momentum contribution is the model's blindness, not the signal's weakness.
- **Sizing (3a), already measured without anyone reading it as such:** Experiment 2's equal-weight
  variant against its ADTV-weighted control, same window — **0.8728 against 0.9024 Sharpe**, so ADTV
  sizing contributed **+0.03 Sharpe of sizing skill**. Small, positive, stated in exactly those
  terms.
- **Selection (3b), timing (3c) and the exclusion filter (4): never run.** They are the top open
  leads in that repository's `RESULTS.md`, and they need no new data.

## What this skill will not let you do

- **Call a strategy understood on the factor split alone.** The split says how much is
  idiosyncratic; the counterfactuals say what the idiosyncratic part is made of.
- **Run one random draw.** K is a trial count. Publish it, and report the percentile, not the best
  draw.
- **Tune on the counterfactuals.** They measure the rule you stated in `BLUEPRINT_N.md`. A rule
  changed to look better against its own counterfactual is a new experiment with a new blueprint.
- **Quote a number that did not come from the engine.** Every counterfactual is priced by
  `engine.run_variant` over the shared window, never approximated.
