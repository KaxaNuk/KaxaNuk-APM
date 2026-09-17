---
name: universe-point-in-time
description: >
  Load this skill whenever you build, extend, run or debug the Universe stage of a KN Research
  Process repository — `Universe/Investable_Universe.csv` and `Universe/universe.ipynb`, step 2.
  Use it when the user asks what belongs in the seed, how to add or change the securities a
  strategy trades, why delisted names are kept, how to build or refresh `Security_Master.csv`, how
  to reconcile a provider against the seed, what a recycled identifier is, why classifications are
  prefixed `current_`, what belongs in `Data_Issues.csv`, or from which date a universe is usable.
  It covers the seed's contract, the two-layer master, the checks and the usable date. It does NOT
  cover downloading prices (use `data-curator-custom-calculations`), the refinery's cross-sectional
  panel or screening a feature (the template's `Data/refinery.py` and `Data/analyzer.ipynb` describe
  them), sizing a book (use `portfolio-construction-runs`), or the research process around the stage
  (use `experiment-lifecycle`).
metadata:
  version: 0.1.1
---

# The Universe — the eligible list, rebuilt for each date rather than for today

**In plain words:** which securities are investable, point-in-time. **It produces**
`Universe/Security_Master.csv` and `Universe/Data_Issues.csv`. **It prevents** survivorship bias —
testing on the winners that happened to survive.

**Eligibility is decided here and nowhere else.** Everything downstream reads the security master
and does not second-guess it.

The stage comes **after the objective**: the claims in `OBJECTIVE.md` decide what the universe has to
contain, so the seed is chosen once they exist. And it sits **between** the two Data commands, where
the order is not cosmetic either: the curator downloads from the seed, this notebook profiles what the
curator wrote, and the refinery joins the master this notebook produces.

```
Universe/Investable_Universe.csv   the seed, committed  ->  edit this to change the universe
        |
        +--> Data/curator.py       downloads one file per identifier in it
        |
        +--> universe.ipynb        Security_Master.csv, Data_Issues.csv
                    |
                    +--> Data/refinery.py    joins the master onto the panel as current_*
```

## 1. The seed is the whole decision

`Universe/Investable_Universe.csv` is the only file in the repository that decides what the
strategy is about. It is **committed** — the one data file that is — because the entire pipeline
grows from it, and because a universe nobody can reconstruct makes every number downstream
unverifiable.

- **One column is required: `main_identifier`**, the name the Data Curator asks the provider for.
  Every other column is the strategy's own. Replace the rows with equities, ETFs, FX crosses,
  crypto pairs or futures and every stage below still runs: nothing downstream names an asset class.
- **It is point-in-time, and it retains delisted, acquired and renamed names.** A universe built
  from *today's* members has silently deleted everything that failed, and the backtest then
  discovers that markets go up. If a seed shows 0% delisted, it is not a universe, it is a survivor
  list.
- **It is also the membership list.** The Curator's folder holds the cash proxy and the benchmarks
  as well, because the engine prices everything from one directory; the refinery and the panel
  loader both take membership from the seed, so those extras can never leak into a cross-section
  and there is no second list to forget to update.

**Changing the seed changes every published number.** Adding or removing a security changes the
cross-section, so every rank, every breadth reading and every book struck from them moves. Treat it
as a change-set of its own: its own branch, its own changelog entry, and the pipeline re-run before
any figure from it is quoted beside an older one.

### What else the seed is worth carrying

Nothing beyond the identifier is required, and two columns earn their place in most strategies:

- **A stable identity — an ISIN, a FIGI, an issuer key.** A point-in-time universe *contains*
  renamed securities: two identifiers sharing one identity, each carrying part of the history.
  Without a column that says which two rows are one company, the panel holds both legs and doubles
  the bet at the changeover. **The stitching downstream is only as good as this column**, and
  where the seed has none the loader keys by the identifier itself and stitches nothing — which is
  correct, because the seed has told it nothing.
- **A readable name**, so a book can be read by a person rather than decoded.

Add whatever else the strategy groups or reports by. A column the provider can fill may be left
empty in the seed and filled by section 2; a column only you know — a hand-assigned bucket, an
internal classification — belongs in the seed, because nothing else will supply it.

## 2. The security master, in two layers

The seed gives identity. Everything else comes from the provider: the official name, what kind of
instrument it is, where it trades, in what currency, and when it started.

**Cache the provider's raw payload, then shape the master from the cache.** Two layers, and the
split pays three times: re-running costs nothing, changing the column mapping never triggers a
refetch, and the untouched payload stays available for fields the notebook does not yet use.
Adding a provider is then one fetch function and one normaliser, registered in an adapter table,
and no other cell changes.

Three properties the fetch layer needs, for the same reason the Curator's does: **cached**,
**resumable** — only identifiers missing from the cache are ever requested — and a switch that
makes the whole section offline, so a run can report what the cache holds and touch no network.

**The adapter declares what it can supply.** The columns a provider does not carry are a permanent
gap for that provider, not a fetch failure, and saying which is which is the difference between a
known limitation and a mystery.

### The seed wins on identity

A provider value never overwrites an identity column. It is **compared**, and a disagreement is
reported:

> **A provider that now points an identifier at a different security is a recycled symbol.** The
> ticker of a company that delisted gets reissued, and joining on it across the whole history
> silently mixes two companies. The seed's identity is authoritative; the provider's is evidence
> that the identifier has been reused, and the register records it.

### Classification is what a security is **today**

The provider keeps no history. On a universe whose members get reclassified — an equity moving
between GICS sectors, a fund changing category — **every period before the move is attributed
wrongly, and nothing raises an error.**

That is why the refinery prefixes every joined column `current_`, and why anything bucketed on one
is read as indicative. **Group or report by a `current_*` column; never select on it.** If the
strategy needs true point-in-time classification, it has to arrive as a per-date column out of the
Data stage, and until it does, the gap belongs in the register and in the caveats of every findings
file.

## 3. The data-issues register

The seed says what *should* exist. This section reads what *does* — the Curator's own output — and
writes `Universe/Data_Issues.csv`, one row per issue with the identifiers attached, so the next
stage has a work list rather than a chart to interpret.

| Check | The failure it catches |
| --- | --- |
| **Missing file** | an identifier the provider does not carry, which becomes a silent hole in the panel |
| **Schema drift** | a folder holding two column sets, which makes every downstream read conditional |
| **Late start** | a series that begins after the panel does, so the cross-section is smaller before that date |
| **Early end** | a series that stops early — delisted or halted, and a held position must be exited on its last priced day |
| **Internal gaps** | sessions missing inside a name's own range. Measure against a **real trading calendar**, not a business-day range: a business-day range counts every market holiday as a gap and makes almost every name look broken. An index ETF's own dates *are* the calendar |
| **Identity conflict** | the provider's identity differs from the seed's — a recycled identifier |
| **Status disagreement** | the price history and the provider's listing status disagree: a series ending early on a name the provider calls active is a data gap, not a delisting, and the reverse is a reused symbol |
| **Unusable values** | zero or negative prices, which break every return calculation downstream |
| **No usable signal** | a history shorter than the strategy's longest warm-up, so the name can never be selected |

Give each row a severity, and **sort blocking first**. A register nobody can triage is a chart with
extra steps.

## 4. When the universe is actually usable

A file that starts in 2010 gives no signal in 2010. Every feature has a warm-up, and a five-year
one moves the honest start of a backtest by five years.

**The date that matters is the first day on which every security can be both priced and
signalled** — and, for a strategy that selects a fixed number of names, the first day the eligible
pool is at least as deep as the book. Before it the strategy is choosing from a smaller menu than
it appears to be, and a backtest that starts earlier is quietly comparing books drawn from
different universes.

Nothing else in the pipeline says so, which is why it is answered here, and why it is declared in
`BLUEPRINT_N.md` before the rule rather than discovered afterwards.

## 5. What the stage hands on

| Output | Consumed by |
| --- | --- |
| `Universe/Security_Master.csv` | `Data/refinery.py`, which joins its columns onto the panel as `current_*` |
| `Universe/Data_Issues.csv` | the caveats table of every `FINDINGS_N.md`, and the Data stage's work list |
| The usable date | `BLUEPRINT_N.md`, as the declared window |

`Security_Master.csv`, `Data_Issues.csv` and the provider cache are all **regenerable and therefore
gitignored**; `Investable_Universe.csv` is the only committed input. Composition, listing status and
listing age belong here too — a universe whose members mostly listed after the backtest starts is a
different universe from the one the row count suggests.

## What this skill will not let you do

- **Build a universe from today's index members.** It deletes every failure and the backtest
  discovers that markets go up.
- **Let a provider overwrite the seed's identity.** Compare, report the disagreement, and keep the
  seed.
- **Select on a `current_*` column**, or present a classification-bucketed number without saying it
  is a today-snapshot.
- **Drop a bad identifier silently.** It goes in the register, by name, with the check that caught it.
- **Change the seed without a change-set.** New branch, changelog entry, and the pipeline re-run
  before a figure from the new universe stands beside one from the old.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come
  from the template's `example` branch only.
