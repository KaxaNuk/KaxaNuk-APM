---
name: attribution-analysis-runs
description: >
  Load this skill whenever a run of the KaxaNuk Attribution Analysis library is being set up,
  executed, debugged or read. Use it when the user asks to install `kaxanuk-attribution_analysis`,
  initialise its project files, shape the four inputs it reads (market data, daily portfolio and
  benchmark weights, benchmark returns, per-factor returns), turn a backtested book into the daily
  weights it requires, fill in `attribution_analysis_parameters.xlsx`, call the CLI or
  `performance_attribution.main`, drive `BrinstonFachlerArrowAttribution` or
  `KNFMArrowAttribution` directly, or get the allocation / selection / interaction and
  per-factor tables back out. It covers the exact input layouts, the traps that produce a
  clean-looking but wrong run, and how step 6 is called from a KN Research Process repository. It
  does NOT cover what the numbers mean for a strategy (use `alpha-decomposition`) or running the
  backtest that produced the book (use `backtest-engine-runs`).
metadata:
  version: 0.2.2
---

# Running the KaxaNuk Attribution Analysis

Step 6 of the KaxaNuk Investment Lab: a book that beat its benchmark is taken apart into the pieces
that explain it. The library is **licensed** — not on public PyPI, and deliberately absent from the
KN Research Process template's `pyproject.toml` so its index URL and key never enter version control.
Its documentation is public, at
`https://kaxanuk-attribution-analysis.readthedocs-hosted.com/en/latest/`, and this skill is written
against the **0.2.0** build of it. Go there for anything this file does not cover; this file keeps
what the documentation does not say, and what a KaxaNuk repository adds.

**This skill gets the numbers out. It does not read them.** What allocation, selection and the
idiosyncratic residual mean for a strategy — and the counterfactual books that turn the residual
into selection, sizing and timing — is `alpha-decomposition`, in the `investment-lab` package.

## 1. Install it without leaking the key

The documentation's quick start has the command; the ready-to-run version, key included, arrives in
the licence welcome email:

```bash
pip install kaxanuk-attribution_analysis --extra-index-url https://license:{YOUR_LICENSE_KEY}@{SERVER}/simple/
kaxanuk.attribution_analysis init excel
```

Three rules, and the first is not negotiable:

- **Never print, echo or commit the key or the index URL** — not into a notebook output, a log line,
  a shell history or a dependency file. The command carries a credential: run it, do not paste it
  back. An exposed key is rotated, not edited out.
- **Never add the library to a repository's dependency file.** It is installed by hand, per machine,
  by whoever holds the licence.
- **Python 3.12 or 3.13** — the Backtest Engine's ceiling too, and part of why a KN Research Process
  repository pins `requires-python = ">=3.12,<3.14"`.

The licence key lives in `Config/.env` as **`KNAA_API_KEY_KAXANUK`** — a different variable from the
engine's `KNBE_API_KEY_KAXANUK`, and both sit in the same file; `~/.kaxanuk_license` or the exported
variable work too. **Never print the value of any of them.** The licence is checked against KaxaNuk's
server on every run, with a 24-hour local cache and a 7-day offline grace period: a run that worked
last week can fail today on a plane, and that is the licence, not the data.

**Keep it installed.** `uv sync` is *exact* by default and removes every package the lockfile does not
name, and this one is deliberately not in the lockfile. Once it is installed, after a relock use
`uv sync --inexact` with the repository's groups, run everything else through `uv run`, and check
`uv pip list | grep -i kaxanuk` before step 6. If the library has vanished, that is why, and the
install command is the fix.

## 2. Guard the import, always

A clone without a licence must still run everything else. Any module or cell that imports the
library reports what is missing and skips, rather than raising:

```python
try:
    from kaxanuk.attribution_analysis import performance_attribution
except ImportError:
    performance_attribution = None
```

Check for `None` at the call site and say plainly that step 6 was skipped for want of the licensed
library. **A pipeline that dies at an optional import is a pipeline nobody can read.**

## 3. The four inputs

The layouts are on the documentation's *Data Formats* page; `init excel` lays down `Input/Data/`,
`Input/Portfolios/`, `Input/Benchmark_Portfolios/` and `Input/Factor_Models/`. What decides whether a
run is right:

**The first header decides everything, and it is not what the documentation says.** A weight file is
read as horizontal when its first header is `Ticker` and as vertical when it is **`date_column`** —
`StandardField.DATE.value`, case-insensitive, checked on 0.2.0 by running it. Anything else raises
`MissingPortfolioError: First column must be 'Ticker' or 'date_column'` before a number is read. *Data
Formats* and `detect_portfolio_format`'s own docstring both say `Date`/`date`, and both are wrong;
`date` is rejected. The same rule governs the portfolio weights, the benchmark weights and the
benchmark returns file.

**The weights are daily.** Portfolio and benchmark weights alike, no nulls. **Once a weight table
spans a year or more, the library requires 240 to 260 rows a year** in its first and last year and
raises `DataIntegrityError` otherwise, precisely to catch a rebalance-only file passed by mistake. So
the weight file a Backtest Engine priced — one column per rebalance date — **cannot be passed in**,
whatever the *Data Formats* example suggests. The attribution reads the book as it was actually held
each trading day, drift included (section 8).

**Market data — one file per security**, `{TICKER}.csv` or `{TICKER}.parquet`, with the date and price
columns named in the configuration (`user_column_date`, `user_column_price`); returns are computed
from the prices, and the Data Curator's `m_date` and `m_close_split_adjusted` drop straight in. Dates
must be `YYYY-MM-DD` or `YYYY/MM/DD`. **A blank price in any row read fails that security, and one
failed security aborts the whole load** with a single `DataLoadingError` naming them all — so trim a
file's rows before its first price and after its last.

**Benchmark returns** go through the same portfolio loader, so they take the same two shapes: one row
of dates-as-columns, or a vertical file whose first header is `date_column` and whose single other
column is the index's daily return. Checked on 0.2.0: the vertical form loads and is reported as one
ticker.

**Per-factor returns — one CSV per factor**: the first column is the date, then one column per asset
holding that factor's return *for that asset*. **The first header may be empty** — the loader takes
the first column whatever it is called, and a file whose header row starts with a bare comma loads
(checked on 0.2.0). Five things about that directory, none of which announces itself:

- **The file name is the factor name**, cut at the first dot: `f_residual.volatility.csv` silently
  becomes `f_residual`, and two names that collide overwrite each other.
- **Every entry in the directory is read as a factor file**; only `.gitkeep` is skipped. A stray
  `notes.md` or `.DS_Store` fails there, not with a message about the directory.
- **Only the portfolio's own tickers are read.** A column for a name the book never held is skipped in
  0.2.0, and a held name missing from a factor file lowers that factor's coverage instead of raising.
  The run logs `Average total factor coverage throughout the portfolio`, as a percentage, and
  `Factor '<name>': reading k/n asset columns` per file. **Read both.** Low coverage means the factor
  attribution describes part of the book.
- **An explicit `start_date` earlier than a factor file's first date raises `DateRangeError`**, while a
  late `end_date` is quietly clamped.
- **Observed in the 0.2.0 source, not promised by the documentation:** `f_market`,
  `f_total_factor_returns`, `f_total_excess_returns` and `f_idyo_returns` are dropped from the
  percentage decomposition, which uses `f_total_excess_returns` as its denominator when present. Name
  a factor one of these by accident and it vanishes without a word. The plots group on exactly
  `f_size`, `f_momentum`, `f_beta`, `f_residual volatility` (with the space), `f_value` and
  `f_<GICS sector>`; any other name still attributes and lands in neither panel.

**Also observed in the source — confirm with a small run before relying on it:** `main()` loads market
data only for the tickers in the *portfolio* weight file, so benchmark weight on a name the portfolio
file does not list has no return and drops out of the Brinson-Fachler benchmark. List every benchmark
constituent in the portfolio file, at zero weight, with its market data.

## 4. Configure it

`Config/attribution_analysis_parameters.xlsx`, one **General** sheet: the parameter name in A (**do
not touch**), your value in B, the description in C. The documentation's *Configuration Reference*
has every row; `references/configuration.md` has them with the traps below. The ones that decide the
run are the two methods (`brinson_fachler_method`, `factor_model_method`, independent), the two
columns read from your market data, the formats (lowercase), and the window (`YYYY-MM-DD` or `auto`).

Three traps:

- **`portfolio_input_format = excel` does not complete.** In 0.2.0 the benchmark-returns handler is
  still built only on the `csv` branch, so the Excel branch reaches an unbound name. Keep the weights
  as `.csv`, and report it upstream rather than working around it silently.
- **Three directories are joined onto `input_directory`** — the portfolio weights, the benchmark
  weights and the benchmark returns — while `investable_assets_directory` and
  `factor_returns_by_factor_directory` are used as given. Moving `input_directory` moves the first
  three and leaves the market data and the factors where they were.
- **`ExcelConfigurator` ends the process on a bad cell**: it logs the configuration error and calls
  `sys.exit`, so in a notebook a typo arrives as `SystemExit`, not as an exception you can read. A
  notebook or a sweep builds `Configuration` directly, which raises `ConfigurationError` at
  construction instead — and **a sweep that edits a workbook between runs is a sweep nobody will
  reproduce.**

## 5. Run it

The CLI, from the project root, is on the documentation's *CLI* page. Two details it is easy to
misread: `autorun` on a fresh folder **installs the project files and exits** — it runs only on the
next call — and `run` executes each entry script as its own subprocess.

In code, the documented sequence — *Running from Python* — is four calls, and the first two are not
optional in a notebook:

```python
load_config_env()
configure_logger(
    logger_name="kaxanuk.attribution_analysis",
    logger_level=logging.INFO,
    logger_format="[%(levelname)s] %(message)s",
    logger_file=None,
)
parameters_path = pathlib.Path("Config") / "attribution_analysis_parameters.xlsx"
configurator = ExcelConfigurator(parameters_path)
performance_attribution.main(
    configurator.get_configuration(),
    launch_dashboard=False,
    dashboard_port=configurator.get_dashboard_port(),
)
```

`load_config_env()` is what reads `Config/.env`, and without `configure_logger` at `INFO` the coverage
and date-range lines this skill tells you to read never print. The imports are
`services.env_loader`, `services.configuration_logger`, `config_handlers.excel_configurator` and
`performance_attribution`, under `kaxanuk.attribution_analysis`.

- **`dashboard_port` is keyword-only and has no default** — required even with the dashboard off,
  whatever the `main()` examples in the documentation show.
- **`main()` shows plots itself.** With Brinson-Fachler on it always draws its figure, and with
  `launch_dashboard=False` it draws the factor model's too — each through `plt.show()`. In a script, a
  notebook batch or CI, call `matplotlib.use("Agg")` before `main()`, or the run blocks on a window
  nobody will close.

## 6. Read what comes back

**`main()` writes no files.** It returns `None`: log lines, figures, and perhaps a dashboard. The
quick start, the Excel workflow and the CLI page all say results are written to `Output/`; nothing
is. **To get numbers back, build the two attribution objects yourself** and read their attributes:

```python
brinson = BrinstonFachlerArrowAttribution(
    returns_investable_assets=asset_returns,
    complete_portfolio_weights=portfolio_weights,
    complete_benchmark_weights=benchmark_weights,
    date_column="date",
)
brinson.time_series_calculation()          # sets .df and .output_dict
brinson.attribution_plots()                # sets .brinston_fach_indexes, and calls plt.show()
```

| Attribute | What it holds |
| --- | --- |
| `.df` | the daily totals: `date`, `portfolio_returns`, `benchmark_returns`, `alpha`, `allocation`, `selection`, `interaction`; zero rows, full schema, when no date qualifies |
| `.output_dict` | date to per-asset detail: `asset`, both weights, `returns_data`, both returns, `alpha` and the three effects |
| `.brinston_fach_indexes` | the cumulative sums — the series to quote. Set only by `attribution_plots()` |

**Read the effects the way the library defines them.** Its *Brinson-Fachler* methodology page computes
them **per asset and per date**: with `r` the asset's return, `r_b = w_b · r`, and
`alpha = w_p · r − r_b`, allocation is `(w_p − w_b) · r_b`, selection is `alpha · w_p`, and interaction
the remainder. That is not the textbook group-level split, so an *allocation* number is not a sector
bet unless the inputs were built as groups. Say which you mean when you quote one.

```python
factor_returns = load_by_factor_returns_arrow(
    path=factor_directory,
    available_factors=factor_file_names,
    portfolio_weights=portfolio_weights_entity,
)
factor_tables = {
    factor_name: factor.table
    for factor_name, factor in factor_returns.items()
}
factor_model = KNFMArrowAttribution(
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

`load_by_factor_returns_arrow` returns `FactorReturns` entities; the class wants their tables.
`.portfolio_attribution_ts` is the daily contribution per factor, `.simulated_rets` its cumulative sum,
`.pct_df_returns` the daily percentage split, and `cummulative_pct_decomp()` a dict: each factor's
share of total excess return at the last date. Tables are `pa.Table`; `.to_pandas()` at the analysis
boundary.

Note the spelling. The classes are **`Brinston`**`FachlerArrowAttribution` and
`.brinston_fach_indexes`, the method is `brinson_fachler_model`, and the constructor's parameter is
`returns_investable_assets` while its interface spells it `returns_investible_assets`. All of it is as
written; none of it is a typo you may fix.

Four things to know before quoting any of it:

- **The idiosyncratic residual has three spellings.** `f_idio_returns` is the column `calc_pct_area()`
  creates; `idio_returns` is the key `cummulative_pct_decomp()` returns; `f_idyo_returns` is a reserved
  input name both drop. Say which one a quoted number came from.
- **The percentage decomposition divides by the day's total return.** On days near zero the ratio
  explodes, and the library forward-fills the non-finite result. Read `.pct_df_returns` as a shape and
  quote `cummulative_pct_decomp()` for a number.
- **Everything is aligned to the intersection of every input's date range**, and the run logs it as
  `Aligned all tables to common date range`. One short factor file shortens the whole analysis; state
  the common range beside the backtest window. An intersection with no dates raises rather than
  returning an empty result.
- `summary_stats(returns)`, in `modules.performance_functions`, gives the one-row frame the dashboard
  shows; the whole module is public, so a figure in a document can be recomputed from the series. Its
  functions do not infer periods per year — pass them.

## 7. The dashboard

With `factor_model_method` on and `launch_dashboard=True`, a Dash app is served on `dashboard_port`
(1–9999, typically 8050). **It needs the factor model**: with only Brinson-Fachler, static matplotlib
plots are what you get. `run_server` **blocks**, and runs with `debug=True` by default. Never launch it
from an automated run, a scheduled job or a notebook you expect to finish: pass
`launch_dashboard=False` and read the tables.

## 8. Inside a KN Research Process repository

Step 6 reads what step 5 produced, and `Experiments/attribution_analysis.py` shapes it:

- **The book's daily weights, not `Portfolio/portfolio_weights.csv`.** That file is the book on its
  rebalance dates, which the library rejects. Take the weights the engine actually held each trading
  day — the drifted book in its results, which the attribution library's own field definitions name
  `Daily_Weights` — reshape them to one row per trading day and one column per identifier, the cash
  proxy included, 0.0 where nothing was held, and write them beside the backtest's outputs.
- **The benchmark's daily weights and its daily returns** belong to the experiment, not to the
  library's defaults, with the same density rule. A benchmark chosen after seeing the result is not a
  benchmark.
- `Experiments/Experiment_N/Attribution/` is where output lands, and **nothing in it is committed**: no
  workbooks, no charts, no dashboards. The numbers reach `FINDINGS_N.md`, and `RESULTS.md` is compiled
  from those.
- **Record the factor set** — how many files, and their names — and the coverage line. Attribution
  numbers are only comparable across runs when the factor set is identical, and the file names *are*
  the factor set.

Then hand off. `alpha-decomposition` takes it from the tables: two layers and a third pass, and the
counterfactual books that say what the residual is made of.

## What this skill will not let you do

- **Pass a rebalance-only weight file** and work around the error it raises. The library is right;
  derive the daily book.
- **Quote a number this library did not produce.** The agent never computes an attribution figure
  itself; it shapes inputs, calls the library and reads tables back.
- **Report a factor split without its coverage.** The coverage line and the count of factor files
  travel with every attribution number.
- **Treat an empty `Output/` as a failed run.** It is what `main()` does; read the attributes instead.
- **Silently accept a shortened window.** The common date range is an output, and it is stated.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come from
  the template's `example` branch only.

## Where the documentation is

Base: `https://kaxanuk-attribution-analysis.readthedocs-hosted.com/en/latest/`, build **0.2.0**. Prefer
it whenever it and this file disagree — except where `references/api.md` names a place the
documentation and the code disagree, and says which is which.

| Page | Path under the base |
| --- | --- |
| Quick start — install, licence key, project tree | `user_guide/quick_start.html` |
| Data formats — the four inputs, the pre-run checklist | `user_guide/end_user_manual/data_formats.html` |
| Configuration reference — every workbook row | `user_guide/end_user_manual/configuration.html` |
| Excel workflow | `user_guide/end_user_manual/excel_workflow.html` |
| Running from Python | `user_guide/end_user_manual/running_from_python.html` |
| Brinson-Fachler methodology — the per-asset formulas | `methodology/brinson_fachler.html` |
| Factor model methodology | `methodology/factor_model.html` |
| `main()` and `Configuration` in code | `api_reference/performance_attribution.html` |
| `BrinstonFachlerArrowAttribution` | `api_reference/attribution_methodologies/brinson_fachler.html` |
| `FactorModelArrowAttribution`, the factor loader | `api_reference/attribution_methodologies/factor_model.html` |
| Weight entities — the daily-density rule | `api_reference/portfolio_data_pipeline/entities.html` |
| `ExcelConfigurator`, `Configuration` | `api_reference/portfolio_data_pipeline/configuration.html` |
| Metrics | `api_reference/metrics.html` |
| CLI | `api_reference/cli.html` |
| Dashboard | `api_reference/dashboard/core.html` |
| Release notes | `release_notes/v0/index.html` |
