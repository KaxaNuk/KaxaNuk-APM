---
name: experiment-lifecycle
description: >
  Load this skill whenever you start, structure, run or document a KaxaNuk Investment Lab
  strategy repository or one of its experiments. Use it when the user asks to start a new strategy
  from the KN Research Process template, scaffold an Experiments/Experiment_N/ folder, write a
  blueprint, journal, brainstorming or findings file, update RESULTS.md or the changelog, or move
  an experiment through the eight steps: Bibliotheca, Universe, Data, Portfolio, Backtest,
  Attribution, Paper trading, Production. It defines the document architecture and each file's
  contract, the notebook section contract, the restrictions, the bar a new signal must clear and
  the graduation gate. It does NOT cover authoring Data Curator `c_*` calculations (use
  `data-curator-custom-calculations`) or reading attribution output into selection, sizing and
  timing skill (use `alpha-decomposition`).
metadata:
  version: 0.2
---

# The KN Research Process — how a strategy repository is worked in

Every KaxaNuk Investment Lab strategy lives in its own repository, built from the **KN Research
Process template** (`KaxaNuk-Community/R_KN-Research-Process`) and shaped like the reference
implementation, **Golden Flow**. The point of the fixed shape is comparability and legibility: any
experiment looks like any other, every experiment is measured against the same declared benchmark,
and a CIO can read the whole state of a project from two files.

Work in English: notebook narrative, documents, function names and comments.

**To start a new strategy, copy the template repository; do not scaffold one by hand.** To work
inside one, follow this skill. `references/structure.md` has the tree and the instantiation steps.

## 1. The eight steps

Steps 1-7 are the Investment Lab and live in the repository. Step 8 does not: a strategy leaves the
Lab when it joins the KN Fund allocation.

| # | Step | The question it answers | Where it lives |
| --- | --- | --- | --- |
| 1 | **Bibliotheca** | What do we believe, and on what evidence? | `Bibliotheca/`, `OBJECTIVE.md` |
| 2 | **Universe** | Which securities are investable, point-in-time? | `Universe/` |
| 3 | **Data** | Curation, refinery, analysis — what can we measure? | `Data/` |
| 4 | **Portfolio** | How is the book constructed? | `Experiments/Experiment_N/Portfolio/` |
| 5 | **Backtest** | How would it have performed, net of costs? | `Experiments/Experiment_N/Backtest/` |
| 6 | **Attribution** | Where do the alpha and the risk actually come from? | `Experiments/Experiment_N/Attribution/` |
| 7 | **Paper trading** | Does it hold up on data the rule has never seen? | `Paper_Trading/` |
| 8 | Production | Joins the KN Fund allocation | outside the repository |

**Each step reads only from the steps above it and owns its outputs.** A notebook that recomputes a
column the refinery already produced has broken the process even if the number comes out the same.
A step is finished when its output is reproducible from the step above by re-running one command or
one notebook, never by a manual fix-up nobody wrote down.

The six Lab libraries map onto these stages one to one. Three are live — Data Curator
(`Data/curator.py`), Backtest Engine and Attribution Analysis (both through
`Experiments/engine.py`). Three are in development — Data Refinery (`Data/refinery.py`), Data
Analyzer (`Data/analyzer.ipynb`), Portfolio Construction (step 4, in the experiment notebook) — and
those are exactly the stages a repository hand-rolls today. A hand-rolled stage says so in its
docstring and names the interface the library will replace.

## 2. The control documents — what belongs where

Four files at the root carry the whole state of the project. Everything else is code, or a note
feeding one of them.

| Document | Holds | Reader | Changes when |
| --- | --- | --- | --- |
| `OBJECTIVE.md` | the main idea, the objective, and the claims inside it with their status | anyone, first | almost never — a change here means a different strategy |
| `RESULTS.md` | the executive summary of every experiment, compiled from the `FINDINGS_N.md` files and citing each; the methods record as an appendix | CIO, PM, researcher | a `FINDINGS_N.md` changes |
| `CHANGELOG.md` | every version, newest first, in the Data Curator convention `## X.Y.Z (YYYY-MM-DD)` with `### Added / Changed / Deprecated / Fixed / Removed` | whoever needs to know what moved | any change-set lands |
| `AGENTS.md` | how work is done: the process, the restrictions, the bar, the house rules | anyone doing work there | the process changes |

**`RESULTS.md` is compiled from `FINDINGS_N.md`, never the other way round.** When a number changes,
change it in the findings file first, then the summary.

`Paper_Trading/BITACORA.md` is the graduation gate — a contract, deliberately not named `JOURNAL`,
because under this architecture a journal is an append-only dated log.

## 3. The four files in every experiment

Each `Experiments/Experiment_N/` is one idea, self-contained: four markdown files, a notebook, and
three gitignored output folders (`Portfolio/`, `Backtest/`, `Attribution/`).

| File | What it holds | Who writes it | When it changes | Template |
| --- | --- | --- | --- | --- |
| `BLUEPRINT_N.md` | **the hypothesis** — thesis, rules, success criteria, key risks | by hand, or with the AI | **never, once written** | `references/blueprint-template.md` |
| `BRAINSTORMING_N.md` | **planning** — ideas, what to try next, what was considered and dropped | by hand, or with the AI | whenever thinking happens, before the work | `references/brainstorming-template.md` |
| `JOURNAL_N.md` | **the running log** — every iteration, dated, oldest first | the AI, as work proceeds | append only; a correction is a new entry | `references/journal-template.md` |
| `FINDINGS_N.md` | **the latest results worth keeping** | the AI, from the journal | rewritten when a result changes; feeds `RESULTS.md` | `references/findings-template.md` |

The split matters. `BLUEPRINT` is fixed so a result cannot quietly reshape the question it was meant
to answer. `JOURNAL` is append-only so the path is recoverable. `FINDINGS` is rewritten so there is
exactly one current answer. `BRAINSTORMING` looks forward so planning is not mistaken for history.

Repository-level history — choosing the benchmark, the data step, the architecture — belongs in
`JOURNAL_1.md`, Experiment 1 being the declared benchmark. Later journals point there rather than
copying it.

## 4. The notebook — one section contract, one cell that is the strategy

`experiment_N.ipynb` follows the same sections every time. `references/blueprint-notebook.ipynb` is
the template's Experiment 1 notebook and is the file to copy.

| Section | Contains |
| --- | --- |
| Position in the pipeline · What this notebook does not do | what the experiment claims, and the standing warnings |
| 0 · Setup | imports, paths, and **the strategy's columns** — `SIGNAL_COLUMN`, `SIZING_COLUMN` — the only strategy names outside the rule |
| 1 · The panel | load and stitch by ISIN — inline in the benchmark, through `Experiments/panel.py` everywhere else |
| 2 · The rule | selection, sizing, timing; must produce `selected_matrix`, `REBALANCE_DATES`, `target_weights`. 2.1 asserts the invariants every rule must pass |
| 3 · Construction | the book and its diagnostics: trigger frequency, turnover, concentration, sector drift; then the deliverables |
| 4 · Backtest | one engine pass through `engine.run_variant`; guarded import, reports-and-skips without a licence |
| 5 · Attribution | Brinson-Fachler and KN5FM, guarded the same way |
| 6 · Verdict | what it concluded, in words |
| Handoff · Open items | what the next stage consumes; what this one left open |

**Everything after section 2 is strategy-agnostic given those three objects.** In the template the
rule cell declares them as an empty book and raises, so the notebook lints as a whole and never
produces a number for a strategy nobody stated.

**Experiment 1 writes its panel loading inline** — it is the benchmark, and a baseline that cannot be
read top to bottom without chasing an import is a worse baseline. Every later experiment imports
`panel.py`, declares its own columns in section 0, and passes them through
`panel.load_company_panel(..., columns=...)`. **No strategy column is ever named in `panel.py` or
`engine.py`**: a signal that leaks into shared code becomes every later experiment's default
without anyone deciding it.

## 5. Scaffolding

**A new strategy:** copy `KaxaNuk-Community/R_KN-Research-Process`, then follow the seven steps in
its `README.md` — name it, state the idea in `OBJECTIVE.md`, write `BLUEPRINT_1.md` before the rule,
compute the signal as a `c_*` column, point the three notebooks at it, write the rule cell, fill
`Config/.env`. `references/structure.md` repeats the steps and the tree.

**A new experiment `N` inside an existing strategy:**

1. Create `Experiments/Experiment_N/` with `Portfolio/`, `Backtest/`, `Attribution/`, each holding a
   `.gitkeep`. Confirm `.gitignore` covers `Experiments/*/{Portfolio,Backtest,Attribution}/*` with
   the `.gitkeep` negations.
2. Copy the four templates from `references/`, replacing `N`. **Write `BLUEPRINT_N.md` before any
   code**, and state the economic mechanism, not just the rule.
3. Copy `references/blueprint-notebook.ipynb` to `experiment_N.ipynb`. Replace the inline loading in
   section 1 with `panel.load_company_panel`, declare the experiment's columns in section 0, write
   the rule in section 2.
4. Add a row to the comparable-run table in `RESULTS.md` when `FINDINGS_N.md` first reports, citing
   it. Bump the version in `CHANGELOG.md`: a new experiment is MINOR.

## 6. Restrictions

**One experiment at a time.** When working on `Experiment_N`, do not open another experiment's files
to decide what this one should do. Two standing exceptions, and only two:

- **Experiment 1 is the declared benchmark** — a real strategy with a real return, not a null.
  Beating it is a higher bar than beating a no-model control. Its rules are frozen once
  `FINDINGS_1.md` reports; improvements go into a new experiment.
- **`RESULTS.md` is the shared record.** Comparing *final* results is the point of having several
  experiments. Borrowing another experiment's *choices* before your own are made is what is
  forbidden.

**The bar any new signal must clear**, every clause earned on the reference implementation:

1. State the economic reason before running — in `BLUEPRINT_N.md`.
2. Read sweeps as curves, not cells.
3. Count the trials and publish the count beside the winner.
4. Accept results net, or not at all — every figure from the Backtest Engine through `engine.py`,
   never from a second, lighter simulator.
5. Attribute before believing. This stack can, so "we could not tell" is not an available answer.
6. Prefer the feature anyone can explain in a sentence; add complexity one lever at a time.
7. Report the rejected result as loudly as the promising one.

**Other standing rules:** never change a committed result to agree with a new run — find out why it
moved first; exclude a bad run by name with its reason, never silently; commit no binaries and no
notebook outputs; put no logic in a file that cannot be traced to a stage; never use the `§`
symbol — write "section".

## 7. Research integrity and the graduation gate

`AGENTS.md` in every repository carries **the five ways a backtest lies** — survivorship, look-ahead,
multiple testing, unmodelled costs and capacity, dirty data — with what the repository does about
each and what it admits it does not. The literature behind them ships with the template as the seven
Part 5 notes in `Bibliotheca/`.

**Graduation** to `Paper_Trading/` requires all five criteria in `Paper_Trading/BITACORA.md`: beats
the benchmarks and its own control on engine Sharpe; attribution shows selection or idiosyncratic
alpha (evaluable on this stack — load `alpha-decomposition`); conclusions survive perturbation and
the trial count is deflated; costs and capacity modelled and stated; explicit sign-off. An
experiment is promoted, not copied — `Paper_Trading_N/` mirrors `Experiment_N`, and a paper-trading
script re-fits nothing.

## 8. Versioning

The version tracks **the results and the pipeline that produces them**, not an API. MAJOR when
published results are invalidated; MINOR for new capability; PATCH when no result changes. A result
that changes is MAJOR even if the diff was one line; re-running on refreshed data is not a bump.
While on `0.x`, a result-invalidating change bumps MINOR. `1.0.0` is reserved for the first strategy
that reaches paper trading with its results reproduced from a clean clone.
