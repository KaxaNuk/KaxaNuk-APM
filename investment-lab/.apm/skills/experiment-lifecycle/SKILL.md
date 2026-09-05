---
name: experiment-lifecycle
description: >
  Load this skill whenever you start, structure, run or document a KaxaNuk Investment Lab
  strategy repository or one of its experiments. Use it when the user asks to start a new strategy
  from the KN Research Process template, scaffold an Experiments/Experiment_N/ folder, write a
  blueprint, journal, brainstorming or findings file, update RESULTS.md or the changelog, or move
  an experiment through the eight steps: Bibliotheca, Universe, Data, Portfolio, Backtest,
  Attribution, Paper trading, Production. It defines the document architecture and each file's
  contract, the notebook section contract, where each kind of logic goes, the restrictions, the bar
  a new signal must clear and the graduation gate. It does NOT cover authoring Data Curator `c_*`
  calculations (use `data-curator-custom-calculations`), reading attribution output into selection,
  sizing and timing skill (use `alpha-decomposition`), or the branch-and-changelog procedure of a
  code repository (use `how-we-work` from the `common` package).
metadata:
  version: 0.3
---

# The KN Research Process — how a strategy repository is worked in

Every KaxaNuk Investment Lab strategy lives in its own repository, copied from the **KN Research
Process template**, public at `KaxaNuk/KaxaNuk-Research-Process`. The template's `main` holds no
code: every file is a short description of what is expected in it — what the stage produces, what
it prevents, where its logic belongs. The fixed shape buys comparability and legibility: any
experiment looks like any other, every experiment is measured against the same declared benchmark,
and a CIO reads the whole state of a project from two files, `OBJECTIVE.md` and `RESULTS.md`.

Work in English: notebook narrative, documents, function names and comments.

**To start a new strategy, copy the template; never scaffold one by hand.** Run the
`start-a-strategy` prompt in this package, or use *Use this template* on GitHub. To work inside one,
follow this skill. `references/structure.md` has the tree, what is committed, and the steps to fill
it in. **Do not name Obsidian, a deck, or any KaxaNuk in-house strategy in a repository document.**

## 1. The eight steps

Steps 1 to 7 are the Investment Lab and live in the repository. Step 8 does not: a strategy leaves
the Lab when it joins the KN Fund allocation. Each stage owns its outputs and reads only from the
stage above it.

| # | Step | In plain words | It produces | It prevents | Where |
| --- | --- | --- | --- | --- | --- |
| 1 | **Bibliotheca** | a literature review with a thesis at the end of it | a referenced hypothesis, dated | backtesting a hunch you cannot defend | `Bibliotheca/`, `OBJECTIVE.md` |
| 2 | **Universe** | the eligible list, rebuilt for each date rather than for today | a point-in-time membership table | survivorship bias | `Universe/` |
| 3 | **Data** | curation, then refinery, then analysis | a reproducible dataset, and evidence a feature carries signal | beautiful results from broken inputs | `Data/` |
| 4 | **Portfolio** | how much of what, and how often you change your mind | weights with position and turnover limits | a good signal in a book nobody could hold | `Experiments/Experiment_N/` |
| 5 | **Backtest** | the simulation, run by the Backtest Engine | a cost-aware track record | paper returns real trading would erase | `Experiments/Experiment_N/Backtest/` |
| 6 | **Attribution** | which part of the return did you actually earn? | factor and idiosyncratic breakdown | selling factor beta as alpha | `Experiments/Experiment_N/Attribution/` |
| 7 | **Paper trading** | a dress rehearsal on data nobody has seen | out-of-sample evidence | plumbing problems on day one of funding | `Paper_Trading/` |
| 8 | Production | real capital, real monitoring, a drawdown policy | a funded strategy with an owner | research that stays research | outside the repository |

**A stage that recomputes something an earlier stage produced has broken the process**, even when
the number matches: the next experiment computes it slightly differently and the two stop being
comparable. A step is finished when its output is reproducible from the step above by re-running
one command or one notebook.

The six Lab modules map one to one onto the stages: Data Curator (`Data/curator.py`), Data Refinery
(`Data/refinery.py`), Data Analyzer (`Data/analyzer.ipynb`), Portfolio Construction
(`Experiments/portfolio_construction.py`), Backtest Engine (`Experiments/backtest_engine.py`),
Attribution Analysis (`Experiments/attribution_analysis.py`). Three are live libraries — Curator,
Backtest Engine, Attribution Analysis — and three are hand-rolled until the library lands; a
hand-rolled stage says so in its docstring and names the interface the library will replace.

## 2. The control documents

Four files at the root carry the whole state. Everything else is code, or a note feeding one of them.

| Document | Holds | Changes when |
| --- | --- | --- |
| `OBJECTIVE.md` | the main idea, the objective, the claims inside it with their status | almost never — a change here means a different strategy |
| `RESULTS.md` | the executive summary of every experiment, **compiled from the `FINDINGS_N.md` files and citing each** | a `FINDINGS_N.md` changes |
| `CHANGELOG.md` | every version, newest first: `## X.Y.Z (YYYY-MM-DD)` with `### Added / Changed / Removed` | any change-set lands |
| `AGENTS.md` | how work is done: workflow, who writes each document, restrictions, the bar, the five ways a backtest lies | the process changes |

`CLAUDE.md` is one line, `@AGENTS.md`. `README.md` says what the repository is and where each kind
of logic goes. `Paper_Trading/BITACORA.md` is the graduation gate — a contract, deliberately not
named `JOURNAL`, because a journal here is an append-only dated log.

**When a number changes, change it in `FINDINGS_N.md` first, then `RESULTS.md`.** One exception:
findings from step 3 go straight into `RESULTS.md`, because notebook outputs are stripped before
committing and a measurement living only in a cell output does not survive the commit.

## 3. The four files in every experiment

Each `Experiments/Experiment_N/` is one idea: four markdown files, a notebook, and three gitignored
output folders (`Portfolio/`, `Backtest/`, `Attribution/`, each kept by a `.gitkeep`).

| File | Holds | Who writes it | Changes when | Template |
| --- | --- | --- | --- | --- |
| `BLUEPRINT_N.md` | **the hypothesis** — thesis, rules, predictions, success criteria, risks | a person, or with the AI | **never, once written** | `references/blueprint-template.md` |
| `BRAINSTORMING_N.md` | **planning** — ideas, what to try, what was dropped | a person, or with the AI | thinking happens, before the work | `references/brainstorming-template.md` |
| `JOURNAL_N.md` | **the running log**, dated, oldest first | the AI, as work proceeds | append only; a correction is a new entry | `references/journal-template.md` |
| `FINDINGS_N.md` | **the latest results worth keeping** | the AI, from the journal | rewritten when a result changes; feeds `RESULTS.md` | `references/findings-template.md` |

`BLUEPRINT` is fixed so a result cannot reshape the question it was meant to answer. `JOURNAL` is
append-only so the path is recoverable. `FINDINGS` is rewritten so there is one current answer.
`BRAINSTORMING` looks forward so planning is never mistaken for history. **Every prediction in a
blueprint cites where it comes from** — a note in `Bibliotheca/` or a section of the analyzer — and
a prediction with no source is a lead to read first, not a prediction.

Repository-level history — choosing the benchmark, the data step, the architecture — belongs in
`JOURNAL_1.md`, Experiment 1 being the declared benchmark. Later journals point there.

## 4. The notebook — one section contract, one cell that is the strategy

`experiment_N.ipynb` follows the same sections every time. `references/experiment-notebook.ipynb` is
the template's Experiment 1 notebook — markdown only, one cell per section saying what that section
computes — and is the file to copy.

| Section | Contains |
| --- | --- |
| Header · Position in the pipeline · What this notebook does not do | the claim, the standing warnings, the four shared modules |
| 0 · Setup | paths, and **the strategy's columns** — signal, mark price, fill price, commission price — the only strategy names in the notebook outside the rule |
| 1 · The panel | refined files to `dates x securities` matrices, renamed securities stitched into one position by ISIN |
| 2 · The rule | selection, sizing, timing; must produce `selected_matrix`, `REBALANCE_DATES`, `target_weights` with rows summing to **at most** 1.0; 2.1 asserts the invariants |
| 3 · Construction | the book's shape — invested share, trigger frequency, turnover, concentration, group drift; 3.1 writes the deliverables, `portfolio_weights.csv` with cash as a real priced position |
| 4 · Backtest | the KaxaNuk Backtest Engine, the only backtest anywhere; guarded import, reports and skips without a licence |
| 5 · Attribution | Brinson-Fachler, the factor model, and Brinson-Fachler again on the residual; guarded the same way |
| 6 · Verdict | what it concluded, in words |
| Handoff · Open items | what the next stage consumes; what this one left open |

**Two look-aheads are stated plainly and nowhere else:** the signal used on rebalance date *t* is the
one observed at *t-1* (the lag), and a delisting exit needs one day of hindsight, because a position
is sold on the last day it still has a fill price.

**Four modules beside the notebook are shared by every experiment**, one per Lab library:
`securities_panel.py` (the one panel loader), `portfolio_construction.py` (eligible set to weights,
one signature every scheme shares, constraints switched off by default as levers a later experiment
earns), `backtest_engine.py` (the one path from a weight file to a number), `attribution_analysis.py`
(shaping the hand-supplied inputs, saying what is missing first). **A strategy column is named in
exactly two kinds of place — a notebook's setup cell and the rule — never in a shared module**, so a
signal cannot become every later experiment's default without anyone deciding it. Experiment 1
writes its panel loading inline because a baseline that cannot be read top to bottom is a worse
baseline; later experiments import the loader.

## 5. Where each kind of logic goes

**The prefix tells you which stage owns a column, and therefore which file to open.**

| Prefix | Built by | Scope |
| --- | --- | --- |
| `m_*` | the provider, via the Curator | raw market data — never edited |
| `c_*` | `Data/Curator/custom_calculations.py` | **one security's own history** |
| `r_*` | `Data/Refinery/custom_calculations.py` | **securities against each other, per date**, or anything fitted |
| `current_*` | `Data/refinery.py`, joined from the security master | today's classification — **not point-in-time**; group or report by it, never select on it |

A `c_*` column that needs other securities is misplaced. Widening the Curator's schema refetches
every identifier, so nothing tunable lives there: **a fitted column lives in the Refinery even when
it is per-security, because a sweep must never cost a download.** Its inputs — arithmetic with
nothing to tune — stay in the Curator.

## 6. Scaffolding

**A new strategy.** Run the `start-a-strategy` prompt (copies the template, initialises APM,
installs the KaxaNuk packages), then in this order — each step the smallest change that makes the
next one possible:

1. Put the securities in `Universe/Investable_Universe.csv`; `main_identifier` is the only required
   column, every other column is the strategy's own.
2. State the idea in `OBJECTIVE.md`, before anything is measured.
3. Write the `c_*` and `r_*` columns into the two `custom_calculations.py`, and the Curator and
   Refinery drivers that call the libraries (use `data-curator-custom-calculations`).
4. Run steps 2 and 3 in order: curator, `universe.ipynb`, refinery, `analyzer.ipynb`. The universe
   notebook sits between the two Data commands — it profiles what the curator downloaded and writes
   the security master the refinery joins.
5. Write `BLUEPRINT_1.md` before the rule. Then the rule, section 2 of the notebook.

**A new experiment `N` inside an existing strategy:**

1. Create `Experiments/Experiment_N/` with `Portfolio/`, `Backtest/`, `Attribution/`, each holding a
   `.gitkeep`. The template's `.gitignore` already covers them.
2. Copy the four templates from `references/`, replacing `N`. **Write `BLUEPRINT_N.md` before any
   code**, stating the economic mechanism and citing every prediction's source. The blueprint
   template is the benchmark's; delete the sentences that only apply to Experiment 1.
3. Copy `references/experiment-notebook.ipynb` to `experiment_N.ipynb`; declare the experiment's
   columns in section 0; import the panel loader in section 1; write the rule in section 2.
4. Add a row to `RESULTS.md` when `FINDINGS_N.md` first reports, citing it. A new experiment is a
   MINOR bump in `CHANGELOG.md`, and the entry is part of the change-set.

## 7. Restrictions

**One experiment at a time.** When working on `Experiment_N`, do not open another experiment's files
to decide what this one should do. Two standing exceptions, and one that has to be asked for:

- **Experiment 1 is the declared benchmark** — a real strategy with a real return, not a null. Its
  rules freeze once `FINDINGS_1.md` reports; improvements go into a new experiment.
- **`RESULTS.md` is the shared record.** Comparing *final* results is the point of having several
  experiments. Borrowing another experiment's *choices* before your own are made is what is
  forbidden.
- **A researcher may lift this, explicitly.** When one experiment needs to read another, the request
  and the reason go in that experiment's `JOURNAL_N.md` first. A look-across that is written down is
  a decision; one that is not is contamination.

**The bar any new signal must clear:**

1. State the economic reason before running — in `BLUEPRINT_N.md`.
2. Read sweeps as curves, not cells.
3. Count the trials and publish the count beside the winner.
4. Accept results net, or not at all — every figure from the Backtest Engine, never from a second,
   lighter simulator.
5. Attribute before believing. This stack can, so "we could not tell" is not an available answer.
6. Never choose a parameter on the metric it will be judged by; choose it on a property of the
   signal — persistence, coverage, turnover — and publish the sweep.
7. Prefer the feature anyone can explain in a sentence; add complexity one lever at a time.
8. Report the rejected result as loudly as the promising one.

**Other standing rules:** never change a committed result to agree with a new run — find out why it
moved first; exclude a bad run by name with its reason, never silently; commit no binaries and no
notebook outputs; put no logic in a file that cannot be traced to a stage; do not touch Production;
never print a value from `Config/.env`; never use the section symbol — write "section"; mark
example content with `# --- example: begin ---` in Python, the same words in an HTML comment in
Markdown, and `# EXAMPLE-ONLY CELL` on a whole notebook cell.

## 8. Research integrity and the graduation gate

`AGENTS.md` in every repository carries **the five ways a backtest lies** — survivorship, look-ahead,
multiple testing, unmodelled costs and capacity, dirty data — with what the repository does about
each and what it admits it does not. **If the signal is fitted, measure what look-ahead costs:** read
the same model causally and smoothed and report the gap. It is the cheapest audit in the process
and routinely the largest number in it.

**Graduation** to `Paper_Trading/` requires all five criteria in `Paper_Trading/BITACORA.md`: beats
the benchmarks and its own control on engine Sharpe; attribution shows idiosyncratic alpha in both
layers (load `alpha-decomposition`); conclusions survive perturbation and the trial count is
deflated; costs and capacity modelled and stated; explicit sign-off. An experiment is promoted, not
copied — `Paper_Trading_N/` mirrors `Experiment_N`, and a paper-trading script re-fits nothing.

## 9. Versioning

The version tracks **the results and the pipeline that produces them**, not an API. MAJOR when
published results are invalidated; MINOR for new capability; PATCH when no result changes. A result
that changes is MAJOR even if the diff was one line; re-running on refreshed data is not a bump.
While on `0.x`, a result-invalidating change bumps MINOR. `1.0.0` is reserved for the first strategy
that reaches paper trading with its results reproduced from a clean clone.

## References

- `references/structure.md` — the template's tree, what is committed, and the steps to fill it in.
- `references/blueprint-template.md`, `brainstorming-template.md`, `journal-template.md`,
  `findings-template.md` — the four files of an experiment, as the template ships them.
- `references/experiment-notebook.ipynb` — the template's Experiment 1 notebook, markdown only.

These references are copies of the template's files. Regenerate them from the public template with
`python tools/sync_investment_lab_references.py` at the repository root before a release.
