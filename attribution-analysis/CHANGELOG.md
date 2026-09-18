# Changelog for the KaxaNuk-APM/attribution-analysis subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2026-09-17
### Changed
- **Widening the book to the benchmark is a rule, proved by a run, where 0.2.0 carried it as a caution
  read from the source.** The first cut prices only the securities the book's weight file names and
  computes the benchmark's return from those prices alone; the benchmark returns file never enters it.
  A book of 8 names in a 788-name index reported a benchmark return of 6% of the index's own, alpha about
  five times too large and most of the excess under interaction. With the other 780 names added at zero
  weight — priced to earn exactly the index's return — the benchmark return reached 98.9% of the index's
  and the book's own return did not move.
- The hand-off in section 8 says so step by step: `Daily_Weights` from the engine, `date_column` first,
  the cash position kept, the engine's benchmark column dropped, every constituent added at zero weight
  with a price series of its own.

## [0.2.2] - 2026-09-17
From building both attribution objects by hand and reading their tables, which is the only way to get
numbers out of a library whose `main()` writes nothing.
### Fixed
- **The factor model class is `KNFMArrowAttribution`, not `FactorModelArrowAttribution`.** Every API
  page uses the latter and it does not exist in 0.2.0: the import raises `ImportError`, which is where
  anyone following the documentation stops. `interfaces` exports `KNFMArrowAttribution`, the pandas
  `KNFMAttribution` and the interfaces `FiveFMArrowAttributionInterface` and
  `FiveFMAttributionInterfase`; the module path keeps the `factor_model` spelling.
### Added
- Confirmed against a run: `.df` carries `date`, `portfolio_returns`, `benchmark_returns`, `alpha`,
  `allocation`, `selection` and `interaction`, one row per aligned date, and the identity
  `alpha = allocation + selection + interaction` holds; `.brinston_fach_indexes` and `.output_dict`
  populate after `attribution_plots()`; the factor model returns `.portfolio_attribution_ts` with one
  column per factor file, `.simulated_rets`, `.pct_df_returns` and a `cummulative_pct_decomp()` share
  per factor plus `idio_returns`.
- **`f_Market` is not reserved.** The decomposition excluded `f_idyo_returns`,
  `f_total_excess_returns` and `f_total_factor_returns` and kept `f_Market` as an ordinary factor: the
  reserved names match exactly, in lower case.

## [0.2.1] - 2026-09-17
Corrections from running the library, version 0.2.0, on a real benchmark and twenty real factor files.
### Fixed
- **A vertical weight file's first header is `date_column`, not `Date`/`date`.** 0.2.0 said what the
  documentation says; the code compares against `StandardField.DATE.value` and
  `CsvPortfolioInputHandler` raises `MissingPortfolioError: First column must be 'Ticker' or
  'date_column'`. A file with `date` is rejected. This governs the portfolio weights, the benchmark
  weights and the benchmark returns alike, and it is the first thing a run stops on.
### Added
- Confirmed by the same run, and added where it was silent: a factor file's **first header may be
  empty**; the benchmark returns load through the portfolio loader in the vertical form, reported as
  one ticker; a 788-ticker vertical benchmark at ~251 rows a year passes the density check; the
  alignment and coverage lines print as `Aligned all tables to common date range: ...` and
  `Average total factor coverage throughout the portfolio :  100.0000%`; both methodologies ran,
  `plt.show()` was called for each, and no file was written.

## [0.2.0] - 2026-09-17
### Changed
- `attribution-analysis-runs` is written against the library's **public documentation**, build 0.2.0,
  at `https://kaxanuk-attribution-analysis.readthedocs-hosted.com/en/latest/`. It links to the pages
  that cover a topic instead of copying them; `references/api.md` keeps only the surface a run touches
  and `references/configuration.md` the workbook with what its page leaves out.
- **The weights are daily.** Once a weight table spans a year, the library requires 240 to 260 rows a
  year and raises `DataIntegrityError` otherwise, for the portfolio and the benchmark alike. The skill
  said to pass the rebalance-date weight file the Backtest Engine priced, which fails that check; it
  now says to take the drifted daily book from the engine's results.
- The in-code run is the documented sequence: `load_config_env()` and `configure_logger` at `INFO`
  before `ExcelConfigurator` and `main()`. Without them a notebook does not read `Config/.env`, and the
  coverage and date-range lines the skill tells you to read never print.
- `main()` itself calls `plt.show()` — Brinson-Fachler's figure always, the factor model's with the
  dashboard off — so the non-interactive backend is set before `main()`, not only before a direct call.
- The Brinson-Fachler effects are read the way the methodology page defines them: per asset and per
  date, not the textbook split by group.
### Added
- Traps the documentation states or the 0.2.0 source shows: market-data dates in two formats only; one
  blank price fails a security and one failed security aborts the load; an explicit `start_date` before
  a factor file's first date raises; `ExcelConfigurator` ends the process with `sys.exit` on a bad cell;
  benchmark weight on a name the portfolio file omits drops out of Brinson-Fachler (source-derived, to
  confirm with a small run); `run_server` defaults to `debug=True`.
### Fixed
- A factor column for a name the book never held is skipped in 0.2.0, not rejected with
  `DataValidationError`.
- An empty date intersection raises; it does not quietly yield no data.
- Three directories are joined onto `input_directory` — the benchmark returns as well as the two
  weights directories.
- `autorun` on a fresh folder installs the project files and exits; it runs on the next call.
- `update` backs files up as `.1`, `.2` and upwards.
- The keep-it-installed paragraph said "engine", copied from `backtest-engine-runs`.
- `f_residual volatility` is the plot name with the space; the note sat after `f_value`.

## [0.1.1] - 2026-09-09
### Added
- `attribution-analysis-runs` carries the same keep-it-installed rule as `backtest-engine-runs`:
  a bare `uv sync` removes the licensed package; `uv sync --inexact` and `uv run` keep it.

## [0.1.0] - 2026-09-06
### Added
- `attribution-analysis-runs` skill: installing the licensed package without leaking its key, the
  four inputs the library reads and the exact layouts it detects, the workbook and the same
  configuration in code, the CLI and the two attribution classes, the tables that come back, and how
  step 6 is called from a KN Research Process repository. It stops where `alpha-decomposition`
  starts: this skill gets the numbers out, that one reads them.
- `references/api.md`: the verified public surface — `main()`, `Configuration`,
  `BrinstonFachlerArrowAttribution` and `FactorModelArrowAttribution` with the attributes each call
  sets, the metrics function list, the input handlers, the entities and the CLI — plus a map of the
  documentation pages this skill was written from.
- `references/configuration.md`: every parameter in `attribution_analysis_parameters.xlsx`, the
  pre-run checklist, and the same configuration built as a frozen dataclass for sweeps.
- Four traps that produce a clean-looking but wrong run, each read off the module source rather
  than the prose: the factor file name *is* the factor name and is cut at the first dot; four factor
  names are reserved and silently dropped; `attribution_plots()` is the only thing that sets
  `.brinston_fach_indexes` and it calls `plt.show()`; and every input is aligned to the intersection
  of its date range, so one short factor file shortens the whole analysis.
- Two places the library's documentation and its code disagree, named as such: `main()` writes no
  files despite the user guide's `Output/` folder, and `portfolio_input_format = excel` reaches an
  unbound `benchmark_return_handlers`.
