# Changelog for the KaxaNuk-APM/attribution-analysis subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
