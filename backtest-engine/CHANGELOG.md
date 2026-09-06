# Changelog for the KaxaNuk-APM/backtest-engine subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
