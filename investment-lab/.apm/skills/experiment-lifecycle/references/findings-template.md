# Findings — Experiment N

> **Latest valuable results only.** This file is rewritten when a result changes, not appended to —
> the running history is in [`JOURNAL_N.md`](JOURNAL_N.md), and the hypothesis this tested is in
> [`BLUEPRINT_N.md`](BLUEPRINT_N.md).
>
> **[`../../RESULTS.md`](../../RESULTS.md) is compiled from this file.** When a finding here
> changes, change it here first, then update the summary.

## Status

**Not yet run.** When it has: one line saying whether the benchmark is adopted, and the reminder
that the benchmark is not a graduation candidate — its job is to be the thing others are measured
against.

## The predictions, evaluated

**Every prediction in the blueprint gets a row, including the ones that were wrong.** A falsified
prediction is worth more than a correct one: it says something about the strategy that nobody knew,
and it cost one run to find out.

| # | Prediction | Outcome | What it changed |
| --- | --- | --- | --- |
| 1 | as written in the blueprint | confirmed or falsified, with the number | what is now understood differently |

## The book, priced by the engine

Record the date of the last full re-run from a wiped working copy, the engine version, and the
window. Then the book against every benchmark it reports against: CAGR, volatility, Sharpe, Sortino,
maximum drawdown.

## What the benchmark actually is, structurally

Rebalance frequency, turnover, holdings, concentration, invested share, and any structural tilt —
each with a reading of what a bad value would have meant.

## Attribution — is this the signal, or a factor exposure wearing its name?

Brinson-Fachler: allocation, selection, interaction. The factor model: factor against idiosyncratic.
State the window, which is bound by the supplied files' coverage and is usually shorter than the
backtest.

**What it settles**, and **what it does not** — naming the counterfactual book that would settle
what is left: the same holdings with the signal off, positions equalised, a random draw at the same
sizes, entry dates shifted.

## What is open, ranked

The single highest-value run outstanding, and what it would settle.

## Caveats

| # | Caveat | Effect |
| --- | --- | --- |
| 1 | what a reader must know before quoting a number above | what it does to that number |
