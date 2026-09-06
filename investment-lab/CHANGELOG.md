# Changelog for the KaxaNuk-APM/investment-lab subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-09-06
### Fixed
- `references/structure.md` shows the template's real Python range, `>=3.12,<3.14`, not `>=3.14`.
  The ceiling is the Backtest Engine's, which is documented for 3.12 or 3.13.

## [0.4.0] - 2026-09-06
### Removed
- The `start-a-strategy` prompt. It moved to the KN Research Process template as `SETUP.md`, on the
  rule that **the instruction to install a thing belongs with that thing**. A bootstrap held in an
  APM package could only be reached by pasting a raw GitHub URL at an assistant — you had to install
  APM to find out how to install anything — and that is the step that broke outside Claude. The
  template now owns creating the repository, the one folder it lives in, and the commands, and it
  asks whether to install these packages rather than assuming.
### Changed
- The package is now scoped to **working inside a strategy repository that already exists**:
  `experiment-lifecycle` and `alpha-decomposition`. `apm.yml`'s description says so.
- `experiment-lifecycle` and its `references/structure.md` point at the template's `SETUP.md` for
  scaffolding instead of at the removed prompt.

## [0.3.1] - 2026-09-05
### Changed
- `start-a-strategy` sets the strategy up **in** the folder it is pointed at, instead of creating a
  folder inside it. `destination` is now the root itself; both copy forms clone into `.`, so the
  process folders and the AI setup — `.claude/`, `apm_modules/`, `apm.yml`, `.venv/` — end up side
  by side in one place, and the user opens that place. A non-empty destination still gets a
  `${strategy_name}` folder, and the prompt says so rather than doing it silently.
- The prompt refuses to continue when the destination already holds `apm.yml`, `apm_modules/`,
  `.claude/` or `requirements-dev.txt` without a template beside them. That is the wrapper folder
  the old flow produced: two `apm.yml` files and two `.claude/` directories, of which an agent
  opened at the outer level reads the empty one and never sees the research tree.
- The environment step is `uv sync`, not `uv sync --group dev` — `dev` is a default group — and the
  prompt now says why it comes before `apm init`: `apm-cli` arrives with it.
- Step order renumbered to six, with the root decided in its own step before anything is copied, and
  the target layout drawn at the top of the prompt so every later step can point at it.

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