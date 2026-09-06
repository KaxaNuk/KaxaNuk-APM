# Changelog for the KaxaNuk-APM/backtest-engine subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
