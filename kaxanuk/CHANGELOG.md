# Changelog for the KaxaNuk-APM/kaxanuk subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-06
### Added
- The meta-package: `common`, `data-curator`, `backtest-engine` and `investment-lab` under one
  dependency, for the in-house case where all of them are used. It carries no primitives of its own,
  so there is exactly one place a package can be added to the set.
- Anyone who licenses a single library installs that library's package instead. The split is what
  makes that possible; this package is the convenience on top of it, not a replacement for it.
