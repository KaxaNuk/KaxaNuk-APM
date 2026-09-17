# KaxaNuk-APM

Microsoft APM-compatible AI scaffolding packages for use in KaxaNuk systems: how we code, how we
work, and how each module of the KaxaNuk Investment Lab is used — written for the agent that pairs
with you.

To use it you must first install APM, and then add as an APM dependency the package or its
individual contents.

---

## Installing APM

You can use either the automated or the manual way to install APM.

### Automated installation

Give this prompt to your AI assistant:

```text
Please follow https://github.com/KaxaNuk/KaxaNuk-APM/blob/main/common/.apm/prompts/initialize-apm.prompt.md
```

### Manual installation

1. Install APM in your dev environment. Preferably add `apm-cli` to your pyproject dev dependencies.
2. `apm init` the repo if it doesn't have an `apm.yml` file at the root.
3. Install the parts you want from APM.
4. Recommended: add the following lines to your `.gitignore` file to keep your local AI setup from
   polluting the repo:
    ```
    # AI - managed by APM
    .agents/
    .claude/
    apm_modules/
    .mcp.json
    apm.lock.yaml
    ```

---

## Starting an investment strategy

Strategies are built from the public **KN Research Process template**,
[`KaxaNuk/KaxaNuk-Research-Process`](https://github.com/KaxaNuk/KaxaNuk-Research-Process). **The
template owns its own setup** — how to create the repository, the one folder it has to live in, and
the commands — in its `SETUP.md`. Give this to your AI assistant, and it asks you for the strategy's
name and does the rest:

```text
Please help install https://github.com/KaxaNuk/KaxaNuk-Research-Process
```

A repository created from the template already carries an `apm.yml` naming the `kaxanuk` package
below — every package here under one name — so installing the skills there is
`uv run apm install --target claude` (or `--target codex`) from its root, with nothing to type.
When the request already asked for the skills, the agent installs them; when it only asked for the
repository, it asks first — nothing in that pipeline imports a skill, so *no* is a real answer.

The template's `README.md` then says what to fill in, in order. A **researcher** — a companion you
name and teach, which reads a strategy's `Bibliotheca/` and drafts the hypothesis in each blueprint
— is a separate project at `KaxaNuk/KaxaNuk-Researcher`.

---

## Adding the APM dependencies

Before installing dependencies, configure your target agent system with `apm config set target <env>`.
For example if using Claude:

```bash
apm config set target claude
```

You can check the available targets at
<https://github.com/microsoft/apm/blob/main/docs/src/content/docs/concepts/primitives-and-targets.md#target-catalogue>

### Add a specific package

Each subfolder in this repo containing an `apm.yml` file is its own APM package. **They are split
by audience, not by convenience:** somebody who licenses only one library installs that library's
package and nothing else, so a library skill never drags a research process in behind it. How to
*call* a library lives in that library's package; judgment about a strategy lives in
`investment-lab`.

| Package | Contents |
|---|---|
| `common` | Primitives for any KaxaNuk system: APM usage, dev-container-aware command execution, MCP env var propagation, Python style and filesystem instructions, and **`how-we-work`** — issues before branches, the pull-request checklist, the changelog format and Semantic Versioning as KaxaNuk applies it. |
| `universe` | Primitives for the Universe stage, step 2: the point-in-time seed and why it retains delisted names, the one required column, the two-layer security master and the recycled-identifier check, why every joined classification is `current_*`, the data-issues register, and the date from which a universe is actually usable. |
| `data-curator` | Primitives for projects built on the KaxaNuk Data Curator, starting with authoring custom `c_*` calculations. |
| `portfolio-construction` | Primitives for projects built on the KaxaNuk Portfolio Construction library: installing it, the registry of sizing methods, one allocator per rebalance date on a history cut before it, the loaders' traps, the weight file the Backtest Engine reads, and the invariants every rule must pass. |
| `backtest-engine` | Primitives for projects built on the KaxaNuk Backtest Engine: installing the licensed package without leaking its key, the two inputs it reads and the layouts it detects, the CLI and `PyArrowBacktester`, and reading the metrics back. |
| `attribution-analysis` | Primitives for projects built on the KaxaNuk Attribution Analysis library, written against its [public documentation](https://kaxanuk-attribution-analysis.readthedocs-hosted.com/en/latest/): the four inputs and the daily weights it requires, the workbook and the same configuration in code, `BrinstonFachlerArrowAttribution` and `FactorModelArrowAttribution`, and the attributes to read the tables back from. Getting the numbers out; what they mean is `alpha-decomposition`. |
| `investment-lab` | Primitives for working inside a strategy repository built from the KN Research Process template: `experiment-lifecycle` (the order of work, the eight steps, the document architecture, the notebook contract, the restrictions and the gate) and `alpha-decomposition` (reading attribution in two layers and a third pass, then selection, sizing and timing by counterfactual books). Getting the repository in the first place is the template's own `SETUP.md`. |
| `kaxanuk` | All of the above under one name. The in-house case, where every Investment Lab library is used; install a single package instead if you use one library. |

For example, to add the `common` package to your project:

```bash
apm install KaxaNuk/KaxaNuk-APM/common
```

### Pick and mix

If you just want specific AI primitives without installing the rest, add the relevant folder (for
skills) or `.md` file (for instructions, prompts, etc.):

```bash
# Skills require the folder:
apm install KaxaNuk/KaxaNuk-APM/common/.apm/skills/devcontainer-aware-command-execution
# Self-contained primitives just need the .md file:
apm install KaxaNuk/KaxaNuk-APM/common/.apm/instructions/filesystem-boundaries.instructions.md
```

### Add an MCP server

Run the following command, replacing `%YOUR_MCP_SERVER_URL%` with the URL of the MCP server:

```bash
apm install --mcp %YOUR_MCP_SERVER_URL%
```

---

## Updating

Every change to the AI primitives in this repo increments the packages' versions. APM pins
dependencies to the versions it downloaded during install.

To update all the APM dependencies to the latest versions, run:

```bash
apm install --update
```

---

## Where this is going

**One skill per step of the KN Research Process, and one per Lab module.** Today
`investment-lab` carries the process and the attribution reading; `data-curator`,
`portfolio-construction`, `backtest-engine` and `attribution-analysis` carry the four libraries that
exist; and `universe` covers step 2. The **Data Refinery** and the **Data Analyzer** get their packages
when their libraries land — until then a strategy repository hand-rolls those stages from the
descriptions on the template's `example` branch. **Step 1 is not a package here**: the objective, the
reading for its claims and the notes are the work of
[`KaxaNuk/KaxaNuk-Researcher`](https://github.com/KaxaNuk/KaxaNuk-Researcher). Planned:
`paper-trading` (the gate, re-fit nothing). Each skill names which library call is the deterministic
tool — **the agent never computes the number itself.**

**Distribution.** The packages stay installable with `apm install` from any harness. A Claude
plugin marketplace built with `apm pack` is planned, so people add one marketplace and receive
updates.

---

## Contributing

Pull requests are the way this improves — send one when a skill misled you, and say what it should
have said. Three rules keep the packages safe to publish:

1. **Worked examples come from the template's `example` branch only.** Never from a KaxaNuk in-house
   strategy, a client, or a live book — no signal, no universe, no result of theirs.
2. **Skills document the interface, never the implementation.** Entities, calls, file layouts, and
   what a module must never be asked to do; not how a licensed library computes, and not proprietary
   methodology such as how a factor model's factors are built.
3. **Scan the history for secrets before a release.** Nothing from a `.env` file, no token in a
   notebook output or a log line.

The four experiment documents and the notebook in
`investment-lab/.apm/skills/experiment-lifecycle/references/` are copies of Experiment 1's files on the
template's `example` branch, with that strategy's own lines stripped. Regenerate them rather than
editing them; `structure.md` beside them is kept by hand.

```bash
python tools/sync_investment_lab_references.py
```

---

## Development of this repo

Install the Python dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Install the APM dev dependencies:

```bash
apm install --dev
```
