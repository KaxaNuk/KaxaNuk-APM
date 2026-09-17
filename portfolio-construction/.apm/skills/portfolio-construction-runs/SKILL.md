---
name: portfolio-construction-runs
description: >
  Load this skill whenever a book is sized in a KN Research Process repository — step 4, the rule
  cell and `Experiments/portfolio_construction.py` — or the KaxaNuk Portfolio Construction library is
  installed, configured, called or debugged. Use it when the user asks to pick or compare a sizing
  method (equal weight, inverse volatility, risk parity, HRP, mean-variance, the KN Index), call
  `build_allocator` or `run_pipeline`, build point-in-time eligibility, lag a signal, choose
  rebalance dates, add a weight cap or a minimum holding count, express cash as a position, or write
  the weight file the Backtest Engine reads. It covers installing the library, the per-date weigher
  and its one causal cut, the traps that make a plausible book wrong, and the invariants every rule
  must pass. It does NOT cover pricing the book (use `backtest-engine-runs`), reading what sizing
  earned (use `alpha-decomposition`), or the documents around the experiment (use
  `experiment-lifecycle`).
metadata:
  version: 0.2.0
---

# Portfolio construction — the library inside one signature, and one cut

**In plain words:** how much of what, and how often you change your mind. **It produces** the
`REBALANCE_DATES x securities` target weights a rule hands to the diagnostics and the weight file.
**It prevents** a good signal in a portfolio nobody could hold — and a weighting difference that
reads as a signal difference because each notebook invented its own sizing.

Written against **KaxaNuk Portfolio Construction 1.28.0**. The library keeps three questions apart —
*who plays* (selection), *how much* (sizing), *when* (timing) — and deliberately leaves a fourth to
its caller: *what was known on the day*. That fourth question is most of this skill.

## 1. Install it, and keep it installed

The library is **proprietary**: not on public PyPI, its repository `KaxaNuk/Portfolio-Construction`
private, and no licence key or environment variable of its own. Whoever has access installs it by
hand, per machine, from a clone kept **beside** the strategy — never inside it:

```bash
uv pip install -e "<path to the Portfolio-Construction clone>[solver,clustering]"
```

- **Distribution and import `kaxanuk.portfolio_construction`; Python 3.12 or 3.13** — the Backtest
  Engine's ceiling too, so a KN Research Process repository needs nothing new.
- **The extras decide which methods exist.** `solver` (cvxpy) for constrained mean-variance, CVaR and
  CDaR; `clustering` (scipy) for HRP, HERC and NCO; `plots` (matplotlib) for figures and the PDF
  report; `calendars` (QuantLib, whatever the README says) for the exchange-calendar rebalancers. A
  missing extra fails differently per method: HRP and the solver methods when they are built, HERC and
  NCO only when they allocate, the calendar rebalancers with a bare `ModuleNotFoundError`.
- **`init excel` needs the editable install.** From a wheel it creates `Config/`, `Input/` and
  `Output/`, then fails to find its templates, and the leftover `Config/` blocks the retry. A research
  notebook does not need those files at all: configure in code.
- **Never add it to a strategy's `pyproject.toml`.** A clone without access must still resolve. And
  as with the licensed engines, `uv sync` is exact and removes a hand-installed package: after a
  relock use `uv sync --inexact`, and run everything else through `uv run`.

## 2. Guard the import — step 4 still runs without it

```python
try:
    from kaxanuk.portfolio_construction.sizing import build_allocator
except ImportError:
    build_allocator = None
```

A clone without the library still builds a book: equal weight needs nothing but the eligible set.
**A method that needs the library, asked for without it, is reported and skipped — never quietly
replaced by equal weight**, because a book sized another way is another experiment.

## 3. The three stages, and the registry

| Stage | Question | The pieces |
| --- | --- | --- |
| Selection | who plays | a `Signal` per date — True, False or null per security — and a `BinaryMatrix` across dates; `LiquidityFilter`, `BinaryFilter`, `ColumnMembershipFilter`, `CompositeUniverseFilter`, `UniverseCreator` |
| Sizing | how much | fourteen methods behind one factory, `build_allocator(*, name, config=None, returns=None)` |
| Timing | when | `CalendarRebalancer`, `FixedDateRebalancer`, `TimeSignalRebalancer`, and the QuantLib calendars |

**Null is not zero.** Selection is tri-state, and missing data becomes True or False only through
`MissingDataPolicy` — `EXCLUDE` by default, which for a returns history means listwise deletion: a
date with a gap in any eligible security is dropped for all of them. **The library dies loud**: one
pinned solver, `optimal_inaccurate` is an error, an infeasible mandate names the constraint that
cannot be met. Read an error before working around it.

**Ask the registry before choosing a method.** `describe("hrp")` prints what a method needs and what
it honours; `requirements_for("hrp")` returns the same as data.

| What the method needs | Methods |
| --- | --- |
| nothing but the eligible set | `equal_weight` |
| a column in the snapshot | `feature_weighting` (one numeric feature), `kn_index` (market cap and two traded-value windows) |
| a returns history | `inverse_volatility`, `risk_parity`, `max_diversification`, `mean_variance`, `black_litterman` (plus market cap); `hrp`, `herc`, `nco` with `clustering`; `constrained_mean_variance`, `cvar`, `cdar` with `solver` |

Every method's configuration, required fields, bounds and short-selling policy are in
`references/api.md`.

## 4. The contract: one signature, one cut

In a KN Research Process repository the library is called from **inside** the step-4 shared module,
`Experiments/portfolio_construction.py`, never around it. A **weigher** is any function of this shape:

```python
weigher(
    eligible_securities: pandas.Index,      # what may be held on this rebalance date
    returns_history: pandas.DataFrame,      # daily returns, ending STRICTLY BEFORE that date
    settings: ConstructionSettings,
) -> pandas.Series                          # weights, non-negative, summing to at most 1.0
```

Equal weight, inverse volatility, HRP or any other method in the registry is the same shape, so
swapping one for another is one line in the rule cell and nothing else in the notebook moves — which
is what makes two experiments comparable rather than merely adjacent.

**The cut is the module's, made once.** `build_target_weights` hands each weigher the rows dated
strictly before the rebalance date; `.loc[:date]` would include the date itself. A weigher never sees
a date, so it has no future to reach for.

**Never let the library make that cut, because it does not.** A returns-based method estimates over
whatever table it was built with, and `run_pipeline` builds each method once for every date, so over
a multi-date run the early books are sized on returns that had not happened yet. The library's own
changelog records it — *Known and open after 1.28.0*, 24% future observations in its integration
test — and says to slice the history yourself. So **build one allocator per rebalance date, on the
history already cut**, inside the weigher:

```python
eligible_history = returns_history[eligible_securities]
dated_history = eligible_history.rename_axis("date")
history_table = pyarrow.Table.from_pandas(
    dated_history.reset_index(),
    preserve_index=False,
)
allocator = build_allocator(
    name="inverse_volatility",
    config=InverseVolatilityConfig(),
    returns=history_table,
)
eligible_table = pyarrow.table(
    {
        "ticker": list(eligible_securities),
    }
)
snapshot = UniverseSnapshot(table=eligible_table)
allocated = allocator.allocate(snapshot=snapshot)
weights = Weights.from_allocated(allocated=allocated)
weight_by_security = pandas.Series(
    weights.as_mapping()
)
```

- **The history is wide** — a `date` column, then one numeric column per security; a timestamp or a
  `date32` date both read — and must carry **every** eligible security, or the method raises
  `AllocationError`. It needs at least two complete dates.
- **The factory checks the pairing.** A snapshot-only method refuses a `returns` argument and a
  returns-based one refuses to be built without it, so pass the history only when
  `requirements_for(name).history_input` says so. Snapshot methods read their columns from the
  snapshot table: put the feature there, as it stood before the date.
- **Weights sum to at most one, not to exactly one.** A method's book sums to its target exposure,
  1.0; the module scales it down when a lever asks for cash, and the residual becomes a real, priced
  cash position when the weight file is written. Nothing eligible is an empty book — 100% cash, kept as
  an all-zero row, because "went to cash" is an instruction the engine has to receive.

## 5. Eligibility and timing, point in time

The library lags nothing, and **a snapshot reads its values on the date it is built for.** So the
order is the module's, and it is fixed:

- **Lag the eligibility** so the set used on rebalance date *t* is the one observed at *t-1*, filled
  with False so the warm-up holds nothing rather than everything. A security has to have been
  authorised yesterday and be sellable today, and those are two different days on purpose.
- **Rebalance on change** when the rule is event-driven: the days the lagged set changed. A
  `BinaryMatrix` of the lagged signal counts entries and exits per date with `turnover()`. A calendar
  rule takes `CalendarRebalancer(trading_dates=..., frequency=RebalanceFrequency.MONTH_END)` on the
  panel's own dates — and yields a date for an incomplete last period too, so check the last one.

In a KN Research Process repository the eligible set comes from the refined panel — the rule builds
it from the `r_*` columns — and the library sizes it. If you do use its loaders and `run_pipeline`,
three traps are silent until they are not:

- **Snapshots match dates exactly.** A rebalance date the panel does not hold gives all-null features,
  every filter goes null and the run aborts. Take dates from the panel's own `date` column;
  `FixedDateRebalancer` checks nothing.
- **Warm-up nulls abort the whole run.** A 252-day column is null for a year, `EXCLUDE` removes every
  security, and one failing date stops every date with nothing written. Start after the warm-up.
- **Filters inside the pipeline are date-blind.** A selection stage receives a bare table, so a
  `MembershipFilter` on a dated `Classification` raises, or applies one date to all. Point-in-time
  membership comes from a per-date flag column (`BinaryFilter`) or
  `UniverseCreator.build_membership`, read per date with
  `BinaryMatrix.active_on(target_date=..., missing=MissingDataPolicy.EXCLUDE)`.

The loaders — `CsvInput` and `ParquetInput`, over the Curator's one-file-per-identifier folders — read
**numeric columns only**; a text column or a Parquet `NaN` fails with nothing more than *No input
handler succeeded*.

## 6. Constraints are levers, switched off

`ConstructionSettings` carries what every weigher respects, kept apart from the weigher so two methods
can be compared without also changing the constraints:

| Setting | Default | What switching it on means |
| --- | --- | --- |
| `maximum_weight` | 1.0 | a cap. **What it frees becomes cash.** The library's `Weights.cap` redistributes the excess to keep the book fully invested — a different lever; use it only when the blueprint names that one |
| `minimum_holdings` | 1 | below it the book is cash. The honest response to too few things to hold is to hold less |
| `risk_lookback_days` | 63 | the history handed to a weigher that estimates risk |

The defaults switch every constraint **off**, because a constraint is a lever a later experiment has
to earn against the simpler baseline. The library's richer machinery — a `Mandate` with group limits,
a tracking-error budget, Black-Litterman views — is a lever of the same kind: one at a time, each
beating the book without it. `liquid-momentum`, on the template's `example` branch, sizes by equal
weight: the method every other one in the registry has to beat.

## 7. The weight file

In a KN Research Process repository `Experiments/backtest_engine.py` writes
`Portfolio/portfolio_weights.csv`: wide, `Ticker` first, one ISO date per column, every column
summing to exactly 1.0 with the residual in the cash proxy. Outside one, the library's exporter writes
the same layout — `PortfolioEntity.from_dict(weights_dict={"2025-01-02": {...}})`, then
`CsvOutputHandler(output_dir=..., filename="portfolio_weights.csv").write(portfolio=..., config=None)`
— with two things to know: it **upper-cases tickers**, which must still match the market-data file
names, and it **refuses negative weights**, so a long/short book cannot go through it.

The attribution library does not read this file: it needs the book's **daily** weights, as the engine
marked them. That hand-off is `attribution-analysis-runs`.

## 8. The invariants every rule must pass

Cheap to check in section 2.1 of the notebook, expensive to discover inside a P&L. Whatever the
method:

- no book is more than fully invested, and none is negatively invested;
- no negative weights, if the strategy is long-only; gross and net within the limits the engine will
  be given, if it is not;
- **every security paid for today had its signal on the prior close** — check the signal itself, not
  the composed eligibility, because the signal is what had to exist in advance;
- every security bought is tradable on the day it is bought, so a fill price exists;
- nothing is still held on a day after it stopped being tradable.

Run them over **every** book an experiment builds, not only the benchmark's. A variant that holds a
name the benchmark could not is a bug wearing a Sharpe.

## What this skill will not let you do

- **Give a weigher a date**, or a history that reaches the rebalance date.
- **Build one returns-based allocator for many dates**, or run one through `run_pipeline` over a
  multi-date window.
- **Redistribute what a cap frees** unless the blueprint names that lever.
- **Choose a sizing method on the Sharpe it produces** over the window it will be judged on. Choose it
  on a property of the book — concentration, turnover, capacity — and publish the comparison.
- **Swap in equal weight because the library is missing.** Report the skip.
- **Quote a number the engine did not produce.** This module builds weights; `backtest-engine-runs`
  prices them.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come from
  the template's `example` branch only.

## Where the documentation is

The library has no public documentation site yet. Its repository carries it: `README.md` for the
principles and each method's card, `CHANGELOG.md` — read *Known and open* before trusting a feature —
and `examples/`. `references/api.md` is the surface this skill was checked against, with the places
where the README and the code disagree.
