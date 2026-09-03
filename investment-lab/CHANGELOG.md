# Changelog for the KaxaNuk-APM/investment-lab subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-03
### Added
- `alpha-decomposition` skill: reading Attribution Analysis output into a factor / idiosyncratic
  split, recognising when a factor model built on relative factors is blind to an absolute rule,
  then decomposing the idiosyncratic part into selection, sizing and timing by counterfactual books
  the Backtest Engine prices, plus the exclusion-filter test. Worked example from Golden Flow.
- `experiment-lifecycle` references `blueprint-template.md`, `journal-template.md` and
  `findings-template.md`, one per file of the four-file experiment contract.
### Changed
- `experiment-lifecycle` rewritten to the KN Research Process as shipped by the
  `KaxaNuk-Community/R_KN-Research-Process` template and its reference implementation, Golden Flow
  0.9.0: eight steps with stage-owned folders at the repository root, four control documents
  (`OBJECTIVE.md`, `RESULTS.md` compiled from `FINDINGS_N.md`, `CHANGELOG.md`, `AGENTS.md`), four
  files per experiment with stated contracts, the notebook section contract in which one cell is the
  strategy, the one-experiment-at-a-time restriction with the benchmark exception, the seven-clause
  bar and the graduation gate. A new strategy is started by copying the template repository.
- `brainstorming-template.md` is forward-looking only; the dated log moved to `journal-template.md`.
- `structure.md` describes the template repository's tree, what is committed, and the seven
  instantiation steps.
- `blueprint-notebook.ipynb` is the template's Experiment 1 notebook: 24 cells, output-free, with
  the rule cell declaring its three contract objects as an empty book and raising.
### Removed
- `hypothesis-template.md`, superseded by `blueprint-template.md`.
- The `Experiments/<Name>/Results/` layout, per-experiment `Hypothesis.md` and `Brainstorming.md`,
  and the root `FindingsConcernsDecisions.md`, which the reference implementation stopped using at
  its 0.3.0.

## [0.1.0] - 2026-07-27
### Added
- Initial release, with the `experiment-lifecycle` skill: the standard structure,
  five-stage pipeline, and documentation flow for a US equity model-portfolio
  experiment, plus copyable notebook and Bibliotheca templates.