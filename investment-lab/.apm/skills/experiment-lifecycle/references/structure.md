# Repository structure

The canonical tree of a KaxaNuk Investment Lab strategy repository, as the **KN Research Process
template** holds it — public at `KaxaNuk/KaxaNuk-Research-Process`. `main` ships the shape only: the
six folders and the documents at the root, with what goes in each folder written down in its README.
Every file inside the folders is on the `example` branch, where one strategy, `liquid-momentum`, is
worked through them. **The template is the source of truth for this tree; this file is a copy of what
it looked like at the version named below**, kept by hand. When they disagree, the template wins.

Template version: **0.7.5**. On `example` every file is a description of what is expected in it — the
`.py` files are docstrings, the notebooks are markdown cells — with the strategy's own lines beside
them between example markers.

```
<Strategy_Name>/
├── SETUP.md                     # how to get the repository and set it up - an agent can follow it
├── OBJECTIVE.md                 # the idea and its claims, written before any paper is read
├── RESULTS.md                   # executive summary compiled from FINDINGS_N.md, citing each
├── CHANGELOG.md                 # every version, newest first; what a version number means here
├── AGENTS.md                    # how work is done: first run, workflow, restrictions, the bar, the five lies
├── CLAUDE.md                    # one line: @AGENTS.md
├── README.md                    # the strategy's own: the idea, where it stands, a link to the template
├── LICENSE                      # MIT
├── apm.yml                      # committed: the KaxaNuk skills this repository wants, one line
├── pyproject.toml               # Python >=3.12,<3.14, uv-managed; the KaxaNuk libraries installed by hand are absent
├── Config/
│   └── .env.template            # a data-provider key and the two engine licences; copy to .env
├── Bibliotheca/                 # step 1
│   ├── BIBLIOGRAPHY.md          #   the index of sources and the leads, in Parts 0-5
│   ├── LOG.md                   #   what was read here, and when
│   ├── Papers/Author_Year_Title.md      # one note per paper, beside its PDF; frontmatter source, citation, local_copy, read
│   ├── Books/Author_Year_Title/INDEX.md # one folder per book: its chapters, one note per chapter chosen
│   ├── Notes/                   #   clippings and transcripts
│   └── Extracts/                #   the text a researcher's script pulls out of the PDFs, gitignored
├── Universe/                    # step 2
│   ├── Investable_Universe.csv  #   THE SEED, committed: main_identifier is the only required column
│   └── universe.ipynb           #   -> Security_Master.csv, Data_Issues.csv, Provider_Cache/ (gitignored)
├── Data/                        # step 3
│   ├── curator.py               #   Data Curator driver
│   ├── Curator/
│   │   ├── custom_calculations.py   # c_* columns: one security's own history
│   │   ├── Time_Series/         #   downloaded, gitignored — universe, cash proxy, benchmarks
│   │   ├── Benchmarks/          #   dropped in by hand: index holdings and returns
│   │   └── Factors/             #   dropped in by hand: factor-model returns
│   ├── refinery.py              #   the seam the Data Refinery library replaces
│   ├── Refinery/
│   │   ├── custom_calculations.py   # r_* columns: cross-sectional, fitted, or with a setting to sweep
│   │   └── Time_Series/         #   derived, gitignored — the panel every experiment reads, + current_*
│   ├── analyzer.ipynb           #   where a feature earns a backtest or is dropped
│   └── Analyzer/                #   charts and the signal table, gitignored
├── Experiments/                 # steps 4-6
│   ├── securities_panel.py      #   the one panel loader; names no strategy column
│   ├── portfolio_construction.py    # eligible set -> weights, one signature; the library called inside it
│   ├── backtest_engine.py       #   the one path from a weight file to a number
│   ├── attribution_analysis.py  #   the hand-supplied inputs and the book's daily weights; what is missing, first
│   └── Experiment_N/
│       ├── BLUEPRINT_N.md  BRAINSTORMING_N.md  JOURNAL_N.md  FINDINGS_N.md
│       ├── experiment_N.ipynb
│       ├── Portfolio/           #   step 4 output, gitignored
│       ├── Backtest/            #   step 5 output, gitignored
│       └── Attribution/         #   step 6 output, gitignored
└── Paper_Trading/               # step 7
    ├── BITACORA.md              #   the graduation gate — a contract, not a log
    ├── daily_update.py          #   the scheduler over graduated books; contract as docstring
    └── Paper_Trading_N/paper_trading_N.py   # one frozen rule per graduated experiment
```

## What is committed, and what is not

**Only source is committed:** code, notebooks with outputs stripped, documents and the notes, the
folder skeleton kept by `.gitkeep`, `LICENSE`, `apm.yml`, and one seed file —
`Universe/Investable_Universe.csv`. A strategy repository also commits `uv.lock`, which pins what its
results came from; the template ships without one. Everything under `Data/` except code, every
`Portfolio/`, `Backtest/` and `Attribution/`, the PDFs and `Bibliotheca/Extracts/`, every chart,
workbook and parquet is regenerated by running a stage or supplied by hand, and is gitignored by
extension and by path. `Config/.env` is gitignored **because it is secret**; the template is
committed. Everything APM installs — `.claude/`, `.agents/`, `.codex/`, `.cursor/`, `apm_modules/`,
`apm.lock.yaml`, `.mcp.json` — is gitignored too, and installed per machine from the committed
`apm.yml`.

Strip notebook outputs before committing:

```bash
uv run jupyter nbconvert --clear-output --inplace Universe/universe.ipynb Data/analyzer.ipynb Experiments/*/experiment_*.ipynb
```

## Starting a strategy from the template

Follow the template's own `SETUP.md`. It puts everything into **one folder**, the strategy root,
with `.claude/`, `apm_modules/`, `apm.yml` and `.venv/` beside the process folders rather than in a
directory above them; `uv sync` fetches Python itself; and it asks whether to install the KaxaNuk
agent skills rather than assuming. **Once a KaxaNuk library is installed by hand, a bare `uv sync`
removes it** — `backtest-engine-runs` says which commands keep it. Then follow the order of work in
`SKILL.md`, section 6: the objective first, the reading for its claims, the universe, the data, the
benchmark and `BLUEPRINT_1.md`, and only then the rule.

## Adding Experiment N to an existing strategy

From the repository root:

```bash
N=2
base="Experiments/Experiment_$N"
for d in Portfolio Backtest Attribution; do
  mkdir -p "$base/$d" && : > "$base/$d/.gitkeep"
done
```

Then copy the four templates from this skill's `references/` into `$base/`, renaming `N`, and copy
`experiment-notebook.ipynb` to `$base/experiment_$N.ipynb`. In the notebook: declare the
experiment's columns in section 0, import the panel loader from `Experiments/securities_panel.py` in
section 1, write the rule in section 2 and hand its sizing to `portfolio_construction.py`.
**`BLUEPRINT_N.md` is written before the rule**, and does not change afterwards.
