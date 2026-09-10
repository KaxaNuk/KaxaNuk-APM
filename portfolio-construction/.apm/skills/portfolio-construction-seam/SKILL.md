---
name: portfolio-construction-seam
description: >
  Load this skill whenever a KN Research Process experiment turns an eligible set into weights —
  the rule cell's sizing and timing, `Experiments/portfolio_construction.py`, step 4. Use it when
  the user asks to size a book, add or compare a weighting scheme, add a weight cap or a minimum
  holding count, lag a signal, rebalance only on change, size by a feature such as liquidity or a
  fitted score, check a rule's invariants, express cash as a position, or swap the hand-rolled seam
  for the KaxaNuk Portfolio Construction library. It covers the one weigher signature, the causal
  cut made once, weights summing to at most one, constraints as levers, the timing helpers and the
  invariants. It does NOT cover pricing the book (use `backtest-engine-runs`), reading what sizing
  earned (use `alpha-decomposition`), or the documents around the experiment (use
  `experiment-lifecycle`).
metadata:
  version: 0.1.0
---

# Portfolio construction — one signature, one cut, levers switched off

**In plain words:** how much of what, and how often you change your mind. **It produces** the
`REBALANCE_DATES x securities` target weights the rule cell hands to the diagnostics and the weight
file. **It prevents** a good signal in a portfolio nobody could hold — and a weighting difference
that reads as a signal difference because each notebook invented its own sizing.

`Experiments/portfolio_construction.py` is the second of the four shared modules, and the seam the
KaxaNuk Portfolio Construction library replaces. It is hand-rolled today, and the point of the
design is that replacing it is a one-line change in a rule cell rather than a rewrite: everything
is reached through a single function signature.

## 1. The contract

A **weigher** is any function with this shape:

```python
weigher(
    eligible_securities: pandas.Index,      # what may be held on this rebalance date
    returns_history: pandas.DataFrame,      # daily returns, ending STRICTLY BEFORE that date
    settings: ConstructionSettings,
) -> pandas.Series                          # weights, non-negative, summing to at most 1.0
```

Equal weight, inverse volatility, a minimum-variance optimiser, hierarchical risk parity, or a call
into the library are all the same shape, and `build_target_weights` neither knows nor cares which it
was handed. Swapping one for another is one line in the rule cell, and nothing else in the notebook
moves — which is what makes two experiments comparable rather than merely adjacent.

**A weigher never sees a date.** It is given a history that has already been cut off before the day
it is weighting, so look-ahead cannot be introduced by accident inside one: there is no future to
reach for. The cut is made in one place, `build_target_weights`, and it is one expression — the rows
dated strictly before the rebalance date — so it can be checked by reading. `.loc[:date]` would
include the rebalance date itself; that is the bug the seam exists to make impossible.

**Weights sum to at most one, not to exactly one.** A defensive strategy is sometimes not fully
invested, and a book that must sum to 1.0 cannot express one. The residual becomes cash when the
weight file is written — parked in a real, priced, transaction-costed instrument, because the
engine's weight file has no cash row of its own. Nothing eligible means an empty book, which means
100% cash: that is a position, and a deliberate one, and a date on which nothing was eligible is
kept as an all-zero row rather than dropped, because "went to cash" is an instruction the engine
has to receive.

## 2. Building the book

```python
target_weights = build_target_weights(
    buyable,             # dates x securities boolean: lagged signal AND tradable today
    REBALANCE_DATES,     # the days the book is re-struck
    returns,             # dates x securities daily returns, unlagged; the seam cuts them
    weigher,             # any function with the shape above
    settings,            # ConstructionSettings
)
```

`buyable` arrives already lagged and already intersected with what can actually be traded that
day. The two timing helpers exist so those two steps cannot be forgotten, and they are applied **in
that order**:

- `lag_eligibility(eligible, lag_days)` — the eligible set as it was known `lag_days` trading days
  earlier, filled with False so the warm-up holds nothing rather than everything. A security has to
  have been *authorised* yesterday and be *sellable* today, and those are two different days on
  purpose.
- `rebalance_dates_on_change(buyable)` — the days the eligible set changed, which for an
  event-driven rule are the days it trades. The first day anything is eligible counts. Between
  changes the book drifts and nothing is done: a signal that has not moved is not a reason to pay
  commission, and a calendar rebalance on an unchanged set is pure cost.

## 3. Constraints are levers, switched off

`ConstructionSettings` carries what every weigher respects, kept apart from the weigher itself so
two schemes can be compared without also changing the constraints — the only way to tell which of
the two changes mattered:

| Setting | Default | What switching it on means |
| --- | --- | --- |
| `maximum_weight` | 1.0 | a cap. What the cap frees up becomes cash, never redistributed: redistributing keeps the book fully invested at the cost of quietly breaking the cap on the securities already at it |
| `minimum_holdings` | 1 | below it the book is cash. The honest response to "too few things to hold" is to hold less |
| `risk_lookback_days` | 63 | the history handed to any weigher that estimates risk |

The defaults switch every constraint **off**, because a constraint is a lever, and a repository adds
levers one at a time so each has to earn its place against the simpler baseline. The template's
benchmark declines all three — and on its example branch that was the finding: the blueprint
predicted the book would average roughly half in cash, and it averaged 95.3% invested, because
equal weight over a shrinking eligible set concentrates rather than de-risks. The two levers the
blueprint declined turned out to be the entire defensive mechanism, which is a result about the
levers, not a reason to have switched them on quietly.

## 4. Sizing by a feature

A strategy that sizes by a *feature* — liquidity, a fitted score, anything that is a column of the
panel rather than a statistic of the returns — hands the **unlagged** feature matrix to the seam
and lets the seam make the cut, exactly as it does for the returns history: the row strictly before
the rebalance date, never the rebalance date itself. The weigher then sees one number per eligible
security, as it stood before today, and normalises over the usable ones. Never `.shift(1)` a feature
in the notebook and pass the result to a weigher that trusts it: the cut then lives in two places,
and the second one drifts.

Whatever the score is stays in the rule cell, where a reader can see it — the square root of a
liquidity measure and the reciprocal of a volatility column are two scores fed to one function, not
two weighers.

## 5. The invariants every rule must pass

Cheap to check in section 2.1 of the notebook, expensive to discover inside a P&L. Whatever the
strategy:

- no book is more than fully invested, and none is negatively invested;
- no negative weights, if the strategy is long-only; gross and net within the limits the engine will
  be given, if it is not;
- **every security paid for today had its signal on at the prior close** — check the signal itself,
  not the composed eligibility, because the signal is the thing that had to exist in advance;
- every security bought is tradable on the day it is bought, so a fill price exists;
- nothing is still held on a day after it stopped being tradable.

Run them over **every** book an experiment builds, not only the benchmark's. A variant that holds a
name the benchmark could not is a bug wearing a Sharpe.

## 6. The swap

When the KaxaNuk Portfolio Construction library lands, the rule cell changes one line — the weigher
it hands to `build_target_weights` — and nothing else. Anything the library needs that the contract
does not express is a question for its issue tracker, not a reason to teach a notebook about the
library. Until then, `portfolio_construction.py` says in its docstring that it is hand-rolled and
names the interface the library replaces.

## What this skill will not let you do

- **Give a weigher a date**, or a history that reaches the rebalance date. The cut is the seam's.
- **Redistribute what a cap frees up.** It becomes cash.
- **Choose a sizing scheme on the Sharpe it produces**, over the window it will be judged on. Choose
  it on a property of the book — concentration, turnover, capacity — and publish the comparison.
- **Size a book in a notebook by hand** because the seam lacks something. Extend the seam, and every
  experiment gets it.
- **Quote a number the engine did not produce.** The seam builds weights; `backtest-engine-runs`
  prices them.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come
  from the template's `example` branch only.
