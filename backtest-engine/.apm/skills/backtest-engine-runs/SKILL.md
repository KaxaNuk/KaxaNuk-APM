---
name: backtest-engine-runs
description: >
  Load this skill whenever a run of the KaxaNuk Backtest Engine is being set up, executed, debugged
  or read. Use it when the user asks to install `kaxanuk-backtest-engine`, initialise its project
  files, shape a portfolio weight file or market-data files for it, fill in
  `backtest_engine_parameters.xlsx`, call `PyArrowBacktester` or the `kaxanuk.backtest_engine` CLI,
  attach a commission or slippage model, add a benchmark, or read the returned tables and the Excel
  report (CAGR, Sharpe, Sortino, VaR, CVaR, drawdown, annual returns, weights). It covers the two
  inputs the engine reads and the exact layouts it detects, the licence and its environment
  variable, and how the engine is called from inside a KN Research Process repository. It does NOT
  cover the research process, the experiment documents or the notebook contract (use
  `experiment-lifecycle` from the `investment-lab` package), reading attribution output into
  selection, sizing and timing (use `alpha-decomposition`), or authoring Data Curator `c_*` columns
  (use `data-curator-custom-calculations`).
metadata:
  version: 0.1
---

# Running the KaxaNuk Backtest Engine

Step 5 of the KaxaNuk Investment Lab: the rules are run over history, with costs and no look-ahead,
and a track record comes back. The engine is **licensed** and closed-source — it is not on public
PyPI, and it is deliberately absent from the KN Research Process template's `pyproject.toml` so its
index URL and key never enter version control.

**Every performance figure in a KaxaNuk strategy comes from this engine.** There is deliberately no
second, lighter simulator: one that disagreed would only let a reader pick the number they preferred.

## 1. Install it without leaking the key

Install from the index URL in the licence welcome email:

```bash
pip install kaxanuk-backtest-engine --extra-index-url https://license:{YOUR_LICENSE_KEY}@{SERVER}/simple/
```

Then lay down the project files, once:

```bash
python -m kaxanuk.backtest_engine init excel
```

Three rules, and the first is not negotiable:

- **Never print, echo or commit the key or the index URL** — not into a notebook output, a log line,
  a shell history or a dependency file. The command above carries a credential: run it, do not paste
  it back. An exposed key is rotated, not edited out.
- **Never add the engine to a repository's dependency file.** It is installed by hand, per machine,
  by whoever holds the licence.
- **Check the supported Python before assuming it installs into an existing environment.** The
  documentation states Python 3.12 or 3.13. A project pinned above that range needs a separate
  interpreter for the engine — report the mismatch rather than quietly pinning around it.

The licence key lives in `Config/.env`. The engine's quick start names it `KNPC_API_KEY_KAXANUK`; a
repository created from the KN Research Process template ships a `Config/.env.template` naming
`KNBE_API_KEY_KAXANUK`. **Confirm which one this build reads, against the licence email, before
filling anything in** — and report the answer without printing the value of either.

## 2. Guard the import, always

A clone without a licence must still run everything else. Any module or cell that imports the engine
reports what is missing and skips, rather than raising:

```python
try:
    from kaxanuk.backtest_engine.backtest.pyarrow_backtester import PyArrowBacktester
except ImportError:
    PyArrowBacktester = None
```

Check for `None` at the call site and say plainly that step 5 was skipped for want of the licensed
engine. **A pipeline that dies at an optional import is a pipeline nobody can read.**

## 3. The two inputs

**The portfolio file — what to hold, and when.** Two layouts, detected automatically:

| Layout | First column | The rest |
| --- | --- | --- |
| Horizontal | `Ticker` | one column per rebalancing date |
| Vertical | `date` | one column per ticker |

**The market-data files — one per security**, named `{TICKER}.csv` or `{TICKER}.parquet`. Each needs
a date column and at least three price columns. Which column plays which role is declared in the
configuration rather than inferred from its name, so a provider's naming does not have to be bent to
suit the engine.

Two consequences, and both are ways a backtest lies:

- **Commission is charged on the unadjusted price**, so the file the engine costs against has to
  carry the price actually paid, not a back-adjusted series.
- **A security missing from the market data on a rebalance date cannot be filled.** Reconcile the
  portfolio file's tickers against the market-data directory *before* running, and report the
  difference by name. A run that quietly holds fewer names than the weights say still summarises
  cleanly, and that is the failure nobody catches.

## 4. Configure it

`Config/backtest_engine_parameters.xlsx` holds the simulation parameters and the column-role
mapping. The same configuration can be supplied programmatically as a dict or YAML, which is what a
sweep should use — **a sweep that edits a workbook between runs is a sweep nobody will reproduce.**

## 5. Run it

The CLI, from the project root:

| Command | What it does |
| --- | --- |
| `python -m kaxanuk.backtest_engine autorun` | installs missing project files on the first run, then executes the entry script |
| `python -m kaxanuk.backtest_engine init excel` | lays down the configuration format and an entry script |
| `python -m kaxanuk.backtest_engine run [PATHS]` | executes the given entry scripts or directories |
| `python -m kaxanuk.backtest_engine update excel` | refreshes a template after an engine upgrade (also `update entry_script`) |

Or in code — `PyArrowBacktester`, built one of two ways and run one of two ways:

```python
backtester = PyArrowBacktester.create_from_configuration(
    configuration=configuration,
    input_handlers=[csv_input],
    portfolio_handlers=[csv_portfolio_input_handler],
    commission_model=commission_model,
)
results = backtester.run_with_benchmark()
```

`create_from_pipeline_result` is the same construction when the data pipeline has already run;
`run()` is `run_with_benchmark()` without the comparison arm. Full signatures, the properties an
instance exposes, and where each came from are in `references/api.md`.

**Attach the real cost model.** On a high-turnover book the difference between a flat cost
assumption and real per-share commission can be a third of the edge, so results are accepted **net,
or not at all**. `commission_model` and `slippage_model` are constructor arguments precisely so this
is a decision somebody makes rather than a default nobody read.

## 6. Read what comes back

`run()` returns a `BacktestResultDict`; tables arrive as PyArrow and convert to pandas for analysis.
The Excel report carries CAGR, Sharpe, Sortino, alpha, VaR, CVaR, maximum drawdown, annual returns,
drawdown analysis and portfolio weights.

The `metrics` module is public, so a figure quoted in a document can be recomputed from the returned
series rather than copied out of a cell: `sharpe_ratio`, `sortino_ratio`, `annualize_rets`,
`annualize_vol`, `var_historic`, `var_gaussian`, `cvar_historic`, `drawdown`, `tracking_error`,
`information_ratio` and `compute_portfolio_statistics` among them — all listed in
`references/api.md`.

**Read the run before believing it.** A truncated run — one that stopped valuing the book partway —
still produces a clean-looking summary over the stub. Check the last valued date against the window
that was asked for, and when they differ the variant is excluded **by name, with its reason**, never
quietly dropped.

## 7. Inside a KN Research Process repository

The engine is not called from a notebook directly. `Experiments/backtest_engine.py` is the seam, and
it owns four things: writing the weight file the engine reads, running the engine, reading the
results back, and aligning variants onto one window so they can be compared. Everything specific to
a strategy stays in that strategy's notebook.

- `Experiments/Experiment_N/Portfolio/portfolio_weights.csv` — the book, in the shape section 3
  describes.
- `Experiments/Experiment_N/Backtest/` — where results land, and **nothing in it is committed**: no
  workbooks, no charts. The numbers reach `FINDINGS_N.md`, and `RESULTS.md` is compiled from those.
- Weights sum to **at most** one. A strategy that can go to cash cannot satisfy the stricter form,
  and the engine parks the residual in a real, priced instrument.

## Where the documentation is

This skill was written from these pages. Go to them for anything it does not answer, and prefer them
whenever the two disagree.

| Page | URL |
| --- | --- |
| Quick start | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/user_guide/quick_start.html` |
| End user manual | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/user_guide/end_user_manual/index.html` |
| Base backtest | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/base_backtest_rebalance_pyarrow.html` |
| Backtest components — cost models, execution, interfaces, enums, orchestrators | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/backtest_components.html` |
| Metrics | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/metrics.html` |
| Portfolio data pipeline | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/portfolio_data_pipeline.html` |
| Market data pipeline | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/market_data_pipeline_orchestrator.html` |
| Data pipeline executor | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/data_pipeline_executor.html` |
| CLI | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/api_reference/cli.html` |
| Methodology | `https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/methodology/index.html` |
