# Changelog for the KaxaNuk-APM/portfolio-construction subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-17
### Added
- `portfolio-construction-runs`, written against KaxaNuk Portfolio Construction 1.28.0 now that the
  library exists: installing it by hand from a clone beside the strategy, with the extras that decide
  which methods exist; guarding the import; the three stages and the registry of fourteen sizing
  methods; the loaders' traps — exact-date snapshots, warm-up nulls that abort a whole run, date-blind
  filters, numeric columns only; the exporter, which upper-cases tickers and refuses shorts.
- `references/api.md`: the surface the skill was checked against, from the library's source and a
  wheel built from it, and where its README and its code disagree.
### Changed
- The seam stays the contract, and the library goes inside it. One weigher signature, the cut made
  once, weights summing to at most one, constraints as levers and the invariants carry over from
  `portfolio-construction-seam`. What is new is the rule the library needs: **build one allocator per
  rebalance date, on the history already cut.** A returns-based method estimates over the table it
  was built with, and `run_pipeline` builds each once for every date — the library's own changelog
  measures 24% future observations in its integration test.
- A cap's freed weight still becomes cash. The library's `Weights.cap` redistributes it instead; the
  skill names that as a different lever.
### Removed
- `portfolio-construction-seam`, replaced by the skill above.
- The worked example's figures. They came from a book the template's `example` branch no longer
  carries; `liquid-momentum` has not reached step 4, so the skill quotes no number.

## [0.1.0] - 2026-09-09
### Added
- `portfolio-construction-seam`: the `Experiments/portfolio_construction.py` contract of a KN
  Research Process repository — the weigher signature, `build_target_weights` and the one causal
  cut, weights summing to at most one, the constraints as levers a later experiment earns, the two
  timing helpers, sizing by a feature through a score handed to the seam, the invariants every rule
  must pass, and what the library swap looks like. Written from the template's 0.6.0 contract; the
  worked example is the `example` branch's benchmark book.
