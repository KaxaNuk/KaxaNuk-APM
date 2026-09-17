# Changelog for the KaxaNuk-APM/kaxanuk subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-09-17
The first release after 0.2.0: 0.3.0 and 0.4.0 were never published.
### Added
- `universe` and `portfolio-construction` join the published set. `portfolio-construction` now
  documents the KaxaNuk Portfolio Construction library rather than a hand-rolled seam. Seven packages
  resolve from `kaxanuk`, in pipeline order.
### Removed
- `data-refinery` and `data-analyzer`, added in the unpublished 0.3.0. Their skills documented stages
  a strategy repository hand-rolls; they come back with the libraries that replace them.

## [0.4.0] - 2026-09-10
### Added
- `universe` joins the set, before `data-curator`: the dependency list stays in pipeline order, and
  step 2 now has a package of its own. Nine packages resolve transitively from `kaxanuk`.

## [0.3.0] - 2026-09-09
### Added
- Three packages under the one name: `data-refinery`, `data-analyzer` and `portfolio-construction`
  — the three stages a strategy repository hand-rolls until the library lands, each documenting the
  seam the library will swap into. Eight packages resolve transitively from `kaxanuk` now.

## [0.2.0] - 2026-09-06
### Added
- `attribution-analysis` joins the set, between `backtest-engine` and `investment-lab`: the
  dependency list is in pipeline order, so the packages read as the steps they serve.

## [0.1.0] - 2026-09-06
### Added
- The meta-package: `common`, `data-curator`, `backtest-engine` and `investment-lab` under one
  dependency, for the in-house case where all of them are used. It carries no primitives of its own,
  so there is exactly one place a package can be added to the set.
- Anyone who licenses a single library installs that library's package instead. The split is what
  makes that possible; this package is the convenience on top of it, not a replacement for it.
