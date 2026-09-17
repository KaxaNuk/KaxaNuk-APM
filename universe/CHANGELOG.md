# Changelog for the KaxaNuk-APM/universe subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-09-17
### Fixed
- `universe.ipynb` writes no `Charts/`. Template 0.7.3 removed the folder; the skill's diagram and its
  table of outputs still named it.
- The *does NOT cover* clause named `data-refinery-custom-calculations` and
  `data-analyzer-signal-screening`, which are not published: those stages wait for their libraries.
  It points at the template's `Data/refinery.py` and `Data/analyzer.ipynb` instead, and at
  `portfolio-construction-runs` for sizing.
### Changed
- The stage is placed in the order of work: after the objective, whose claims decide what the
  universe has to contain, as the template has said since 0.7.2.

## [0.1.0] - 2026-09-10
### Added
- `universe-point-in-time`: the `Universe/` stage of a KN Research Process repository — what the
  seed is and why it retains delisted names, the one required column, the two-layer security
  master and why the seed wins on identity, the recycled-identifier check, why every joined
  classification is `current_*` and never point-in-time, the data-issues register and the failure
  each check catches, and the date from which the universe is actually usable. Written from the
  template's 0.7.0 contract; worked examples come from its `example` branch only.
