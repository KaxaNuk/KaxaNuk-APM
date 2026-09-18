# Changelog for the KaxaNuk-APM/backtest-engine subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2026-09-17
Written from a run of engine **0.66.0** on synthetic data, not from the documentation.
### Added
- **What a truncated run looks like, and the check that catches it.** A book whose weights sum to
  exactly 1.0 with `cash_reserve_percentage = 0` cannot pay commission at a rebalance: the engine
  prints one `Cash error` line, stops valuing there, and still returns `success=True`, `error=None`,
  a full statistics block and an Excel report. In the reproduction it valued 522 of 1305 days and
  annualised over the stub, so its CAGR read 23.6% against the complete run's 14.2%. `data["end_date"]`
  and `data["years"]` describe the window **valued**, not the one configured, and comparing the two is
  the check. The skill said to check the last valued date; it now says how, and what causes it.
- **`Daily_Weights`** named as what step 6 reads: the drifted book, one row per valued day, columns
  being the holdings plus the benchmark and `CASH_RESERVE`. The attribution library rejects a file
  carrying only the rebalance dates, so this is the series to write out beside the other results.
- **`references/api.md` gains the `main()` entry point** — its keyword-only signature, `load_config_env`
  for reading the licence out of `Config/.env`, and every key of `BacktestResult.data`, verified on
  0.66.0.
- Two guards worth knowing before a first run: `commission_cents` is rejected outside `[0.00, 0.10]`,
  and every rebalancing date is checked for prices on the positions it touches.

## [0.1.3] - 2026-09-09
### Added
- `backtest-engine-runs` says how to keep the licensed package installed: `uv sync` is exact by
  default and removes a package the lockfile does not name, so once the engine is installed the
  rule is `uv sync --inexact` after a relock and `uv run` for everything else. Probed in a strategy
  repository on 2026-09-09; without it the engine silently vanishes and every notebook reports
  "not installed".

## [0.1.2] - 2026-09-06
### Fixed
- The `backtest-engine-runs` description fits the 1024-character ceiling a Claude skill's
  description has. It was 1060, so the tail — the "does NOT cover" clauses that keep the engine
  skill from being loaded for a research-process question — was the part at risk of being cut.
### Changed
- The description points at `attribution-analysis-runs` for running the attribution library, now
  that the package exists.

## [0.1.1] - 2026-09-06
### Fixed
- The licence key is `KNBE_API_KEY_KAXANUK`, the name KaxaNuk actually uses and the one the KN
  Research Process template ships in `Config/.env.template`. The engine's published quick start
  shows an older `KNPC_API_KEY_KAXANUK`; the skill now says which is current instead of asking the
  reader to work it out.
- The Python paragraph says what the 3.12-or-3.13 ceiling means downstream: it is why a research
  repository pins `>=3.12,<3.14` and installs 3.13, since the Data Curator allows up to 3.14 and the
  engine does not.

## [0.1.0] - 2026-09-06
### Added
- `backtest-engine-runs` skill: installing the licensed package without leaking its key, the two
  inputs the engine reads and the exact layouts it detects, configuration by workbook or in code,
  the CLI and the `PyArrowBacktester` entry points, the metrics that come back, and how the whole
  thing is called from a KN Research Process repository through `Experiments/backtest_engine.py`.
- `references/api.md`: the verified public surface — `PyArrowBacktester`, its two constructors and
  two run methods, the metrics module function list, and the CLI subcommands — plus a map of the
  official documentation with the pages this skill was written from, so a reader can go to the
  source rather than trust a summary.
