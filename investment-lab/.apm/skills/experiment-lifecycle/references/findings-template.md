# Findings — Experiment N

> **Latest valuable results only.** This file is rewritten when a result changes, not appended to —
> the running history is in [`JOURNAL_N.md`](JOURNAL_N.md).
>
> **[`RESULTS.md`](../../RESULTS.md) is compiled from this file.** When a finding here changes,
> change it here first, then update the summary.
>
> The hypothesis this tested is in [`BLUEPRINT_N.md`](BLUEPRINT_N.md).

## Status

**<One line: adopted as the benchmark / leading candidate, not graduated / rejected.>** <Then which
criteria of the gate in `Paper_Trading/BITACORA.md` it clears and which it does not.>

## The variants, priced by the engine

Every variant priced by the **KaxaNuk Backtest Engine** over one window shared by all of them
(`engine.align_to_common_start`). The control row is the benchmark's rule re-struck on this
experiment's window.

**<N> variants were ranked.** The count is published because a reader cannot discount a best-of-N
result without knowing N.

| Variant | CAGR | Vol | Sharpe | Max DD | vs control |
| --- | ---: | ---: | ---: | ---: | ---: |
| **<winner>** | | | | | |
| *<control>* | | | | | — |

<Any excluded run, by name, with its reason — a truncated engine run, a rejected book. A metric
computed over a truncated run does not belong in the same column as a complete one.>

## What this experiment established

1. **<The headline, in one sentence, with its number.>** <Then the reading — what the number means
   and what it does not.>
2. **<Each lever's result, read as a curve across its sweep, never as the single best cell.>**
3. **<Any prediction made from the analyzer before the backtest, and whether it held.>**

## Attribution

<Step 6 for this book: Brinson-Fachler allocation, selection and interaction; KN5FM factor against
idiosyncratic. What it settles — is there idiosyncratic alpha? — and what it does not. If it has not
been run on this variant, say so: criterion 2 of the gate is evaluable on this stack and unevaluated
is not the same as passed.>

## Caveats

- **<The margin against the control and whether it survives deflation.>**
- **<Which conclusions rest on one episode, one regime, one window.>**
- **What the engine does not model** that matters for this book — borrow cost, capacity.
- **Nothing here is out of sample**, and no variant has a control arm differing in exactly one
  thing, until one does.
