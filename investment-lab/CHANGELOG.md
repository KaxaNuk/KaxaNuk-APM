# Changelog for the KaxaNuk-APM/investment-lab subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-05
### Added
- `start-a-strategy` prompt: copies `main` of the public KN Research Process template
  (`KaxaNuk/KaxaNuk-Research-Process`), initialises APM, installs the three KaxaNuk packages and
  hands over with the template's five first steps. Same shape as `initialize-apm`.
- `alpha-decomposition` reads attribution in two layers and a third pass — Brinson-Fachler, the
  factor model, Brinson-Fachler again on the residual — and says what each answers.
- `tools/sync_investment_lab_references.py` at the repository root regenerates the
  `experiment-lifecycle` references from the template, so they cannot drift again.
### Changed
- `experiment-lifecycle` resynced to template 0.4.0: `main` is description-only; the four shared
  modules are `securities_panel.py`, `portfolio_construction.py`, `backtest_engine.py` and
  `attribution_analysis.py`; joined classification columns are prefixed `current_`; the bar has
  eight clauses; one-experiment-at-a-time has two standing exceptions and one a researcher may
  ask for; every blueprint prediction cites a Bibliotheca note or an analyzer section; the dev
  container and the lockfile are gone. `references/structure.md` now points at the template as the
  source of truth and names the version it copies.
- `alpha-decomposition`'s worked example is the template's `example` branch — twelve asset-class
  ETFs and a regime model, unpriced — with what it settled before any engine ran. Examples in this
  public package come from that branch only.
- Shared-module references renamed from `engine.py` / `panel.py` to `backtest_engine.py` /
  `securities_panel.py`; the Paleologo book is cited as a lead, not as a shipped note.
### Removed
- `references/blueprint-notebook.ipynb` (24 code cells), replaced by
  `references/experiment-notebook.ipynb`, the template's markdown-only Experiment 1 notebook.
- The in-house worked example that the previous `alpha-decomposition` carried.

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