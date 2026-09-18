# Changelog for the KaxaNuk-APM/investment-lab subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.1] - 2026-09-17
### Added
- `alpha-decomposition` checks that the benchmark is whole before any row of the first cut is read.
  The attribution library prices only the securities the book's weight file names, so an unwidened
  book is compared with the part of the index it owns: in the run that proved it, a benchmark return of
  6% of the index's, alpha five times too large, the excess under interaction. The check is one
  comparison — the first cut's `benchmark_returns` against the index's own return over the window.

## [0.7.0] - 2026-09-17
The first release after 0.4.2: 0.5.0 and 0.6.0 were never published, and this entry says what
became of them.
### Removed
- `objective-and-bibliotheca`, added in the unpublished 0.6.0. Step 1 — the objective, the reading for
  its claims, the note convention — belongs to the KaxaNuk Researcher (`KaxaNuk/KaxaNuk-Researcher`),
  whose `objective` and `read` write those files after a plan and the owner's go. Two sources of the
  same convention would drift.
- `experiment-lifecycle` no longer names `data-refinery-custom-calculations` or
  `data-analyzer-signal-screening`. Those stages wait for their libraries, and so do their skills.
### Changed
- `experiment-lifecycle` follows the template's **order of work**, 0.7.4: the objective before any
  paper, reading for each claim, the universe with delisted names, the data, the benchmark and then
  the blueprint, the broad reading, the cycle, and every finished cycle into `RESULTS.md`. It listed
  the universe before the objective, which the Researcher had to warn about.
- `experiment-lifecycle` says what `main` and `example` are now — the shape, and one strategy worked
  through it between example markers — and how to bring a file across; that four stages have
  libraries (the Data Curator, Portfolio Construction, the Backtest Engine, Attribution Analysis) and
  two do not yet; that the attribution reads the book's **daily** weights; and that graduation
  criterion 3 asks for the trial count published beside the winner, with the sign-off saying whether
  the deflated figure was computed.
- `alpha-decomposition`'s worked example is `liquid-momentum`, the strategy the template's `example`
  branch now carries: not yet priced, so the section quotes no number, and says where the
  decomposition will look — sizing skill zero by construction, an absolute signal a relative factor
  model may not see, the exclusion-filter test first, timing waiting on a rebalance rule. The example
  it described — twelve ETFs, a jump model, 95.3% invested — is no longer on that branch.
- `alpha-decomposition` reads Brinson-Fachler the way the attribution library computes it, per asset
  and per date; an allocation number speaks about groups only when the inputs were aggregated to
  groups. A counterfactual that is attributed reads its own backtest's daily weights.
- `references/structure.md` is the template's tree at 0.7.5, kept by hand: `Bibliotheca/LOG.md`,
  `Notes/` and the gitignored `Extracts/` in place of `Knowledge/`, no `Universe/Charts/`, the
  strategy's own README.
- The four experiment documents and the notebook are regenerated from `example` with the example's
  own lines stripped. `tools/sync_investment_lab_references.py` strips whole-line example markers and
  `# EXAMPLE-ONLY CELL` cells before writing; without it the references would have carried another
  strategy's content.

## [0.6.0] - 2026-09-10
### Added
- `objective-and-bibliotheca` skill: step 1 as five passes — draft the idea into three claims, turn
  each claim into the question that would settle it, find sources per question and **deliberately
  look for the ones that disagree**, verify every citation against the publisher's record before
  writing the note, then rewrite the objective from the notes so each claim points at a note that
  existed before the sentence did. Carries the note-versus-lead distinction, the note convention's
  four rules, and a stopping condition that is about argument rather than volume: six notes that
  argue with each other beat twenty that agree.
- The skill was written from doing it. `liquid-momentum` on the template's `example` branch is the
  worked example it points at, and the three design decisions that came out of that reading — the
  one-month skip, momentum living in the Refinery, the liquidity screen worded as a cost — are the
  argument for running step 1 before step 3 rather than after it.
### Changed
- `experiment-lifecycle` hands step 1 to the new skill in its *does NOT cover* clause, and says so
  by name the way every other boundary in this repository is drawn.
- `experiment-lifecycle` also names `universe-point-in-time` alongside the module skills, so every
  step of the process points at the package that covers it. Its list of the eight steps loses the
  four now owned by a sibling skill, which is what stops it being loaded for their questions.
### Fixed
- Both skills' descriptions fit the 1024-character ceiling a Claude skill description has. They
  were 1207 and 1077, so the tail — the *does NOT cover* clauses that keep ten sibling skills from
  being loaded for each other's questions — was the part at risk of being cut.

## [0.5.0] - 2026-09-09
### Changed
- `experiment-lifecycle`'s references are regenerated from the template at **0.6.0**: the four
  experiment documents, the notebook, and `references/structure.md`, which now shows `SETUP.md`,
  the committed `apm.yml`, `Bibliotheca/Knowledge/`, `LICENSE`, and the `current_*` prefix on the
  refined panel.
- `experiment-lifecycle` names the skill for each of the six stages — the three new stage packages
  included — in its module paragraph and in its description's "does not cover" list.
- `references/structure.md` says that a bare `uv sync` removes hand-installed licensed engines, and
  points at `backtest-engine-runs` for the commands that keep them.

## [0.4.2] - 2026-09-06
### Changed
- `alpha-decomposition` names `attribution-analysis-runs` as the skill that shapes the attribution
  library's inputs and calls it. This skill still reads numbers rather than producing them; now it
  says where they come from.
- Its third pass no longer hedges on whether the library can run Brinson-Fachler on residual
  returns. It cannot, so the instruction is to build the residual series from the factor model's
  output — and the two spellings of that residual, `f_idio_returns` and `idio_returns`, are named,
  because they are not interchangeable.

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