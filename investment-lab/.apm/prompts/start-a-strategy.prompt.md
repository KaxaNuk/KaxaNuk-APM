---
description: Start a new investment strategy repository from the KN Research Process template, with the KaxaNuk APM packages installed
input:
  - strategy_name: "The name of the strategy, used as the repository name (letters, digits, hyphens, underscores)"
  - destination: "Optional: the folder to set the strategy up IN. Default: the current directory"
metadata:
  version: 0.2
---

# Start a strategy

You are setting up a **space to build an investment strategy**: a copy of the KN Research Process
template — the KaxaNuk Investment Lab's eight steps as a folder structure, every file saying what is
expected in it — with the KaxaNuk APM packages installed so you know how each step and each Lab
module works. The template is public at `https://github.com/KaxaNuk/KaxaNuk-Research-Process`,
`main` only, MIT.

**One folder is the whole project.** The process folders and the local AI setup sit side by side in
it:

```
<the root>/
    .claude/                installed by apm install    \
    apm_modules/            installed by apm install     |  ignored: the setup is per machine
    apm.yml                 written by apm init          |
    .venv/                  written by uv sync          /
    Bibliotheca/            \
    Universe/                |  the process, from the template
    Data/                    |
    Experiments/             |
    Paper_Trading/           |
    Config/                 /
    OBJECTIVE.md  RESULTS.md  AGENTS.md  CHANGELOG.md  README.md
```

There is **no wrapper folder around it and no strategy folder nested inside it**. Everything from
step 3 onwards runs in that one root, and the user opens that one root when you hand over.

Work through the steps in order. If a step has already been done, say so and continue with the next.
Never print a credential. Never invent a URL or a command flag: the ones below are the ones to use.

## Step 1: Check the tools

Confirm `git`, `uv` and `apm` are on the path (`git --version`, `uv --version`, `apm --version`).
For anything missing, tell the user how to install it and stop:

- `git` — <https://git-scm.com>, or GitHub Desktop, which installs it.
- `uv` — <https://docs.astral.sh/uv/>.
- `apm` — `pip install apm-cli` (it is also the `dev` dependency group of the template, so `uv sync`
  installs it once the copy exists).

## Step 2: Decide the root, and say which folder it is

The root is `${input:destination}` when a destination was given, and the current directory
otherwise. **Look at that folder before copying anything**, and take exactly one of these branches:

- **It does not exist** — create it. It is the root.
- **It is empty**, ignoring `.DS_Store` and `desktop.ini` — it is the root. This is the normal case,
  and the reason the destination is the folder to set up *in* rather than a place to create one.
- **It already holds the template** — `OBJECTIVE.md` and `Experiments/` are there. The strategy
  exists; say so, and continue from whichever of steps 4 and 5 has not been done.
- **It holds `apm.yml`, `apm_modules/`, `.claude/` or `requirements-dev.txt`, and no template** —
  **stop.** That is a folder somebody prepared by hand or with `initialize-apm`, and copying the
  template into it produces two competing setups: an outer `apm.yml` and `.claude/` that no
  research tree belongs to, plus the inner pair that comes with the template. An agent opened at the
  outer level reads the empty one and never sees the process. Tell the user to delete those entries
  — `apm.yml`, `apm.lock.yaml`, `apm_modules/`, `.claude/`, `.agents/`, `.mcp.json`,
  `requirements-dev.txt` — or to point at an empty folder, then re-run.
- **It holds anything else** — do not clone into it. Create `${input:strategy_name}` inside it, use
  that as the root, and say plainly that you did, because the folder you were pointed at was not
  empty.

State the absolute path of the root before the next step, and run every remaining step **in it**.

## Step 3: Copy the template into the root

Prefer the GitHub CLI when it is installed and authenticated, because it records the template
relationship on GitHub. From inside the root:

```sh
gh repo create ${input:strategy_name} --template KaxaNuk/KaxaNuk-Research-Process --private
```

```sh
gh repo clone ${input:strategy_name} .
```

GitHub copies a template asynchronously, so a clone that lands empty is a race and not a failure:
wait a few seconds and run the clone again.

Otherwise copy `main` and start a fresh history, so the strategy's first commit is its own:

```sh
git clone --depth 1 --branch main https://github.com/KaxaNuk/KaxaNuk-Research-Process .
```

```sh
rm -rf .git && git init && git add -A && git commit -m "Start from the KN Research Process template"
```

Both forms clone into `.` — the root itself — which is why step 2 requires it to be empty. Only
`main` is copied either way. The template's `example` branch, one strategy worked end to end, is
kept by KaxaNuk beside `main` and is not part of a new strategy.

## Step 4: Install the Python environment

In the root:

```sh
uv sync
```

```sh
cp Config/.env.template Config/.env
```

`uv sync` installs the `dev` group, which is where `apm-cli` comes from, so this step comes before
step 5. Tell the user to put a data-provider key in `Config/.env` themselves, and that the two
KaxaNuk engine licences are optional: steps 1 to 4 of the process run without them, steps 5 and 6
report what is missing and skip. Do not open, read back or echo `Config/.env`.

## Step 5: Initialise APM and install the KaxaNuk packages

In the root — **the same folder as steps 3 and 4, never a level above it**:

```sh
apm config set target claude
```

```sh
apm init -y --target claude
```

```sh
apm install KaxaNuk/KaxaNuk-APM/common KaxaNuk/KaxaNuk-APM/data-curator KaxaNuk/KaxaNuk-APM/investment-lab
```

Use the target the user works with if it is not Claude; the list is in the APM CLI reference. The
template's `.gitignore` already keeps `.claude/`, `.agents/`, `apm_modules/`, `apm.yml`,
`apm.lock.yaml` and `.mcp.json` out of the repository, so the AI setup stays per machine.

## Step 6: Hand over

Give the absolute path of the root and say that it is the whole project: **open that folder**, not a
parent of it. Confirm the four ignored entries — `.claude/`, `apm_modules/`, `apm.yml`, `.venv/` —
are beside the process folders and not above them.

Then say, in this order, what the user does next — it is the *Starting your own strategy* section of
the template's `README.md`:

1. Put the securities in `Universe/Investable_Universe.csv`; `main_identifier` is the only required
   column.
2. Write `OBJECTIVE.md` — the idea and its claims — before anything is measured.
3. Write the `c_*` and `r_*` columns and the two drivers.
4. Run curator, `universe.ipynb`, refinery, `analyzer.ipynb`, in that order.
5. Write `BLUEPRINT_1.md` before the rule.

If a KaxaNuk researcher exists on this machine — a folder created from `KaxaNuk/KaxaNuk-Researcher`
— say to open both folders together: the researcher reads the strategy's `Bibliotheca/` and drafts
the objective and the blueprint from it. Skills installed in step 5 are discoverable in a **new**
session; say so.
