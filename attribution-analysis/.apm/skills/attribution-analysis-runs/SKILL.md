---
name: attribution-analysis-runs
description: >
  Load this skill whenever a run of the KaxaNuk Attribution Analysis library is being set up,
  executed, debugged or read. Use it when the user asks to install `kaxanuk-attribution-analysis`,
  initialise its project files, shape the four inputs it reads (market data, portfolio weights,
  benchmark weights and returns, per-factor returns), fill in
  `attribution_analysis_parameters.xlsx`, call the CLI or `performance_attribution.main`, drive
  `BrinstonFachlerArrowAttribution` or `FactorModelArrowAttribution` directly, or get the
  allocation / selection / interaction and per-factor tables back out. It covers the exact input
  layouts, the reserved factor names, the traps that produce a clean-looking but wrong run, and how
  step 6 is called from a KN Research Process repository. It does NOT cover what the numbers mean
  for a strategy (use `alpha-decomposition`) or running the backtest that produced the weights (use
  `backtest-engine-runs`).
metadata:
  version: 0.1
---

# Running the KaxaNuk Attribution Analysis

Step 6 of the KaxaNuk Investment Lab: a book that beat its benchmark is taken apart into the pieces
that explain it. The library is **licensed** and closed-source — it is not on public PyPI, and it is
deliberately absent from the KN Research Process template's `pyproject.toml` so its index URL and
key never enter version control.

**This skill gets the numbers out. It does not read them.** What allocation, selection and the
idiosyncratic residual mean for a strategy — and the counterfactual books that turn the residual
into selection, sizing and timing — is `alpha-decomposition`, in the `investment-lab` package.

## 1. Install it without leaking the key

Install from the index URL in the licence welcome email:

```bash
pip install kaxanuk-attribution_analysis --extra-index-url https://license:{YOUR_LICENSE_KEY}@{SERVER}/simple/
```

Then lay down the project files, once:

```bash
kaxanuk.attribution_analysis init excel
```

Three rules, and the first is not negotiable:

- **Never print, echo or commit the key or the index URL** — not into a notebook output, a log line,
  a shell history or a dependency file. The command above carries a credential: run it, do not paste
  it back. An exposed key is rotated, not edited out.
- **Never add the library to a repository's dependency file.** It is installed by hand, per machine,
  by whoever holds the licence.
- **Python 3.12 or 3.13**, per the documentation. The same ceiling as the Backtest Engine, and part
  of why a KN Research Process repository pins `requires-python = ">=3.12,<3.14"`.

The licence key lives in `Config/.env` as **`KNAA_API_KEY_KAXANUK`** — a different variable from the
engine's `KNBE_API_KEY_KAXANUK`, and both can sit in the same file. A `~/.kaxanuk_license` file or
the exported environment variable work too. **Never print the value of any of them.**

`validate_license()` runs on **every** call to `main()`, against the licence server, with a 24-hour
local cache and a 7-day offline grace period. A run that worked last week can fail today on a plane;
that is the licence, not the data.

## 2. Guard the import, always

A clone without a licence must still run everything else. Any module or cell that imports the
library reports what is missing and skips, rather than raising:

```python
try:
    from kaxanuk.attribution_analysis.performance_attribution import main as attribution_main
except ImportError:
    attribution_main = None
```

Check for `None` at the call site and say plainly that step 6 was skipped for want of the licensed
library. **A pipeline that dies at an optional import is a pipeline nobody can read.**

## 3. The four inputs

`init excel` lays down the tree the configuration expects:

```text
Input/
├── Data/                      one file per ticker
├── Portfolios/                the book's weights
├── Benchmark_Portfolios/      the benchmark's weights, and its returns
└── Factor_Models/             one file per factor
```

**Market data — one file per security**, `{TICKER}.csv` or `{TICKER}.parquet`. Each needs a date
column and a price column; both names are declared in the configuration (`user_column_date`,
`user_column_price`) rather than inferred, so a provider's naming does not have to be bent. Returns
are computed internally from the price series, and every other column is ignored. The Data Curator's
defaults — `m_date` and `m_close_split_adjusted` — drop straight in.

**Portfolio and benchmark weights.** Two layouts, detected automatically, the same pair the Backtest
Engine reads:

| Layout | First column | The rest |
| --- | --- | --- |
| Horizontal | `Ticker` | one column per rebalancing date |
| Vertical | a date header | one column per ticker |

Weights are decimals, and **no nulls** — a blank cell is not a zero here, it is a failed load. `.csv`
and `.xlsx` are both read.

**Benchmark returns** use the *weight-file* shape, not a two-column series: one row, one column per
date, read through the same portfolio loader. It exists to bound the common date range.

**Per-factor returns — one file per factor**, first column the date, then one column per asset
holding that factor's return *for that asset*. Not a factor return series: an asset-by-factor panel,
one file per factor.

```text
date,AAPL,MSFT,GOOGL
2020-01-02,0.010,-0.004,0.006
```

Four things about this directory decide whether a run is right, and none of them announce themselves:

- **The file name is the factor name**, cut at the first dot: `f_momentum.csv` becomes `f_momentum`.
  So `f_residual.volatility.csv` silently becomes `f_residual`, and two files that collide overwrite
  each other in the dict.
- **Every entry in the directory is read as a factor file.** Only `.gitkeep` is skipped. A stray
  `notes.md`, a `.DS_Store` or a subdirectory is opened as CSV and fails there, not with a message
  about the directory.
- **`f_market`, `f_total_factor_returns`, `f_total_excess_returns` and `f_idyo_returns` are
  reserved.** The percentage decomposition drops them from the factor set and treats
  `f_total_excess_returns`, if present, as the denominator. Name a factor one of these by accident
  and it vanishes from the attribution without a word.
- **Factor columns must be a subset of the portfolio's tickers.** A column for a name the book never
  held raises `DataValidationError`; a held name missing from a factor file does not — it is dropped
  from that factor's coverage instead. The run logs `Average total factor coverage`; **read that
  line.** Coverage well under 1.0 means the factor attribution is describing part of the book.

The style and industry names the plots group on are exact — `f_size`, `f_momentum`, `f_beta`,
`f_residual volatility`, `f_value` (with the space), and `f_<GICS sector>` such as
`f_Information Technology`. Anything else still attributes; it just lands in neither panel.

## 4. Configure it

`Config/attribution_analysis_parameters.xlsx`, one **General** sheet, three columns: the parameter
name in A (**do not touch**), your value in B, the description in C. The full table is in
`references/configuration.md`. The ones that decide the run:

| Parameter | What it decides |
| --- | --- |
| `brinson_fachler_method` / `factor_model_method` | which methodologies run — `yes`/`no`, independent |
| `user_column_date` / `user_column_price` | which columns of *your* market-data files are read |
| `market_data_input_format` | `csv` or `parquet`, lowercase |
| `portfolio_input_format` | `csv` or `excel`, lowercase — **see the trap below** |
| `start_date` / `end_date` | `YYYY-MM-DD`, or `auto` to take them from the data |
| `parameters_format_version` | system use; if the package asks, run `update excel` |

Two traps in this workbook:

- **`portfolio_input_format = excel` is not a working path in the documented pipeline.** The
  benchmark-returns handler is only constructed on the `csv` branch, so the Excel branch reaches an
  unbound name. Keep the weights as `.csv` and read workbooks elsewhere until this is fixed
  upstream — and report it as a library bug rather than working around it silently.
- **`investable_assets_directory` and `factor_returns_by_factor_directory` are used as given**,
  while the two weights directories are joined onto `input_directory`. The shipped template writes
  the first two as `Input/Data` and `Input/Factor_Models` for exactly that reason. Changing
  `input_directory` does not move them.

## 5. Run it

The CLI, from the project root:

| Command | What it does |
| --- | --- |
| `kaxanuk.attribution_analysis autorun` | installs missing project files on the first run, then executes the entry script |
| `kaxanuk.attribution_analysis init excel` | lays down `Config/`, `Input/`, `Output/` and `__main__.py` |
| `kaxanuk.attribution_analysis run [PATHS]` | executes the given entry scripts or directories |
| `kaxanuk.attribution_analysis update excel` | refreshes the workbook after an upgrade (also `update entry_script`) |

Or in code, which is what a notebook or a sweep should use:

```python
configurator = ExcelConfigurator(pathlib.Path("Config") / "attribution_analysis_parameters.xlsx")

main(
    configurator.get_configuration(),
    launch_dashboard=False,
    dashboard_port=configurator.get_dashboard_port(),
)
```

`dashboard_port` is keyword-only and **has no default** — it is required even when the dashboard is
off. `Configuration` is a frozen dataclass and can be built directly, without a workbook, which is
the form a parameter sweep should take: **a sweep that edits a workbook between runs is a sweep
nobody will reproduce.**

## 6. Read what comes back

**`main()` writes no files.** It logs, it plots, and it may serve a dashboard; the `Output/` folder
`init` creates stays empty. The user guide's "results are written to the Output folder" does not
match the pipeline — **to get numbers back, build the two attribution objects yourself** and read
their attributes:

```python
brinson = BrinstonFachlerArrowAttribution(
    returns_investable_assets=asset_returns,
    complete_portfolio_weights=portfolio_weights,
    complete_benchmark_weights=benchmark_weights,
    date_column="date",
)
brinson.time_series_calculation()          # sets .df and .output_dict
brinson.attribution_plots()                # sets .brinston_fach_indexes
```

| Attribute | What it holds |
| --- | --- |
| `.df` | the daily totals: `date`, `portfolio_returns`, `benchmark_returns`, `alpha`, `allocation`, `selection`, `interaction` |
| `.output_dict` | date to per-asset detail table — the same columns plus `asset`, both weights and `returns_data` |
| `.brinston_fach_indexes` | the cumulative sums of all six — the series to quote |

```python
factor_model = FactorModelArrowAttribution(
    daily_portfolio_weights=portfolio_weights,
    by_factor_factor_returns=factor_tables,
    asset_returns=asset_returns,
    benchmark_returns=benchmark_returns,
    date_column="date",
)
factor_model.run()                         # sets .portfolio_attribution_ts and .simulated_rets
factor_model.calc_pct_area()               # sets .pct_df_returns
decomposition = factor_model.cummulative_pct_decomp()
```

`.portfolio_attribution_ts` is the daily contribution per factor, `.simulated_rets` its cumulative
sum, `.pct_df_returns` the daily percentage split, and `cummulative_pct_decomp()` returns the
one-number-per-factor share of total excess return at the last date. Everything is a `pa.Table`;
`.to_pandas()` at the analysis boundary.

Note the spelling. The classes are **`Brinston`**`FachlerArrowAttribution` and
`.brinston_fach_indexes`, while the method is `brinson_fachler_model` and the methodology is
Brinson-Fachler. Both spellings are load-bearing and neither is a typo you may fix.

Four things to know before quoting any of it:

- **The idiosyncratic residual has three spellings.** `f_idio_returns` is the column
  `calc_pct_area()` creates; `idio_returns` is the key `cummulative_pct_decomp()` returns;
  `f_idyo_returns` is a *reserved input* name that both drop. They are not interchangeable — say
  which one a quoted number came from.
- **`attribution_plots()` calls `plt.show()`, and it is the only thing that sets
  `.brinston_fach_indexes`.** In a script, a notebook batch or CI, set a non-interactive backend
  (`matplotlib.use("Agg")`) before calling it, or the run blocks on a window nobody will close.
- **The percentage decomposition divides by the day's total return.** On days near zero the ratio
  explodes; the library forward-fills the non-finite result from the previous day. Read
  `.pct_df_returns` as a shape, and quote `cummulative_pct_decomp()` for a number.
- **Everything is aligned to the intersection of every input's date range** before anything is
  computed. One short factor file silently shortens the whole analysis. Log the common range the run
  reports and state it beside the backtest window — they are usually not the same.

`summary_stats(returns)` from `modules.performance_functions` gives the single-row frame the
dashboard shows: annualised return and vol, Sharpe, max drawdown, skew, kurtosis, Cornish-Fisher VaR
and historic CVaR. The whole module is public, so a figure in a document can be recomputed from the
series rather than copied out of a cell — the function list is in `references/api.md`.

## 7. The dashboard

With `factor_model_method` enabled and `launch_dashboard=True`, a Dash app is served on
`dashboard_port` (1–9999, typically 8050). Two conditions worth knowing:

- **The dashboard needs the factor model.** With only Brinson-Fachler enabled, `launch_dashboard`
  does nothing at all — static matplotlib plots are what you get.
- `dashboard.run_server(...)` **blocks**. Never launch it from an automated run, a scheduled job or
  a notebook you expect to finish; pass `launch_dashboard=False` and read the tables.

Dash is imported lazily inside `main()`, so importing the package does not pull it in.

## 8. Inside a KN Research Process repository

Step 6 reads what step 5 produced. The weight file the Backtest Engine priced is the same book the
attribution decomposes, so the two must be shaped from one source, over one window:

- `Experiments/Experiment_N/Portfolio/portfolio_weights.csv` — the book, in the shape section 3
  describes. Write it once; do not re-derive it for the attribution.
- The benchmark's weights and its return series belong to the experiment, not to the library's
  defaults. A benchmark chosen after seeing the result is not a benchmark.
- `Experiments/Experiment_N/Attribution/` — where output lands, and **nothing in it is committed**:
  no workbooks, no charts, no dashboards. The numbers reach `FINDINGS_N.md`, and `RESULTS.md` is
  compiled from those.
- Record the factor set — **how many files, and their names.** Attribution numbers are only
  comparable across runs when the factor set is identical, and the file names *are* the factor set.

Then hand off. `alpha-decomposition` takes it from the tables: two layers and a third pass, and the
counterfactual books that say what the residual is made of.

## What this skill will not let you do

- **Quote a number this library did not produce.** The agent never computes an attribution figure
  itself; it shapes inputs, calls the library and reads tables back.
- **Report a factor split without its coverage.** The `Average total factor coverage` line and the
  count of factor files travel with every attribution number.
- **Treat an empty `Output/` as a failed run.** It is the documented behaviour of the pipeline; read
  the attributes instead.
- **Silently accept a shortened window.** The common date range is an output, and it is stated.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come
  from the template's `example` branch only.

## Where the documentation is

This skill was written from the library's own documentation build, and every claim about behaviour
that contradicts a prose page was read off the module source that build carries. Go to it for
anything this file does not answer, and prefer it whenever the two disagree — except where this file
says the documentation and the code disagree, and names which is which.

| Page | Path in the docs build |
| --- | --- |
| Quick start | `user_guide/quick_start.html` |
| Data formats | `user_guide/end_user_manual/data_formats.html` |
| Configuration reference | `user_guide/end_user_manual/configuration.html` |
| Excel workflow | `user_guide/end_user_manual/excel_workflow.html` |
| Running from Python | `user_guide/end_user_manual/running_from_python.html` |
| Brinson-Fachler methodology | `methodology/brinson_fachler.html` |
| Factor model methodology | `methodology/factor_model.html` |
| Performance attribution — `main()` | `api_reference/performance_attribution.html` |
| Attribution methodologies | `api_reference/attribution_methodologies.html` |
| Metrics | `api_reference/metrics.html` |
| CLI | `api_reference/cli.html` |
