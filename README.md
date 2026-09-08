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
| `data-curator` | Primitives for projects built on the KaxaNuk Data Curator, starting with authoring custom `c_*` calculations. |
| `backtest-engine` | Primitives for projects built on the KaxaNuk Backtest Engine: installing the licensed package without leaking its key, the two inputs it reads and the layouts it detects, the CLI and `PyArrowBacktester`, and reading the metrics back. |
| `attribution-analysis` | Primitives for projects built on the KaxaNuk Attribution Analysis library: the four inputs it reads and the exact layouts, the reserved factor names, the workbook and the same configuration in code, `BrinstonFachlerArrowAttribution` and `FactorModelArrowAttribution`, and the attributes to read the tables back from. Getting the numbers out; what they mean is `alpha-decomposition`. |
| `investment-lab` | Primitives for working inside a strategy repository built from the KN Research Process template: `experiment-lifecycle` (the eight steps, the document architecture, the notebook contract, the restrictions and the gate) and `alpha-decomposition` (reading attribution in two layers and a third pass, then selection, sizing and timing by counterfactual books). Getting the repository in the first place is the template's own `SETUP.md`. |
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

**One skill per step of the KN Research Process, and one per Lab module as each lands.** Today
`investment-lab` carries the process and the attribution reading, `data-curator` carries the
Curator's calculations, and `backtest-engine` and `attribution-analysis` carry steps 5 and 6 — the
two licensed libraries every performance figure comes from. Planned, in roughly this order:
`bibliotheca` (writing a source note in the convention, what a lead is, what may be cited),
`universe` (the point-in-time seed, data issues, usable dates), `refinery` (`r_*` columns,
causality, the rank identity), `analyzer` (the information coefficient table, the two questions any
signal owes), `portfolio-construction` (the one signature, constraints as levers), `paper-trading`
(the gate, re-fit nothing). Each skill names which library call is the deterministic tool — **the
agent never computes the number itself.**

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

The references in `investment-lab/.apm/skills/experiment-lifecycle/references/` are copies of the
template's files. Regenerate them rather than editing them:

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
