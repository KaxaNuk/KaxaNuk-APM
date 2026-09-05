---
description: Start a new investment strategy repository from the KN Research Process template, with the KaxaNuk APM packages installed
input:
  - strategy_name: "The name of the strategy, used as the folder name (letters, digits, hyphens, underscores)"
  - destination: "Optional: the parent folder to create it in. Default: the current directory"
metadata:
  version: 0.1
---

# Start a strategy

You are setting up a **space to build an investment strategy**: a copy of the KN Research Process
template — the KaxaNuk Investment Lab's eight steps as a folder structure, every file saying what is
expected in it — with the KaxaNuk APM packages installed so you know how each step and each Lab
module works. The template is public at `https://github.com/KaxaNuk/KaxaNuk-Research-Process`,
`main` only, MIT.

Work through the steps in order. If a step has already been done, say so and continue with the next.
Never print a credential. Never invent a URL or a command flag: the ones below are the ones to use.

## Step 1: Check the tools

Confirm `git`, `uv` and `apm` are on the path (`git --version`, `uv --version`, `apm --version`).
For anything missing, tell the user how to install it and stop:

- `git` — <https://git-scm.com>, or GitHub Desktop, which installs it.
- `uv` — <https://docs.astral.sh/uv/>.
- `apm` — `pip install apm-cli` (it is also the `dev` dependency group of the template, so `uv sync
  --group dev` installs it once the copy exists).

## Step 2: Copy the template

The strategy folder is `${input:destination}/${input:strategy_name}`, or `./${input:strategy_name}`
when no destination was given. Refuse to continue if that folder already exists.

Prefer the GitHub CLI when it is installed and authenticated, because it records the template
relationship on GitHub:

```sh
gh repo create ${input:strategy_name} --template KaxaNuk/KaxaNuk-Research-Process --private --clone
```

Otherwise copy `main` and start a fresh history, so the strategy's first commit is its own:

```sh
git clone --depth 1 --branch main https://github.com/KaxaNuk/KaxaNuk-Research-Process ${input:strategy_name}
cd ${input:strategy_name}
rm -rf .git
git init
git add -A
git commit -m "Start from the KN Research Process template"
```

Only `main` is copied either way. The template's `example` branch — one strategy worked end to end —
is kept by KaxaNuk beside `main` and is not part of a new strategy.

## Step 3: Install the Python environment

Inside the strategy folder:

```sh
uv sync --group dev
cp Config/.env.template Config/.env
```

Tell the user to put a data-provider key in `Config/.env` themselves, and that the two KaxaNuk
engine licences are optional: steps 1 to 4 run without them, steps 5 and 6 report what is missing
and skip. Do not open, read back or echo `Config/.env`.

## Step 4: Initialise APM and install the KaxaNuk packages

```sh
apm config set target claude
apm init -y --target claude
apm install KaxaNuk/KaxaNuk-APM/common KaxaNuk/KaxaNuk-APM/data-curator KaxaNuk/KaxaNuk-APM/investment-lab
```

Use the target the user works with if it is not Claude; the list is in the APM CLI reference. The
template's `.gitignore` already keeps `.claude/`, `.agents/`, `apm_modules/`, `apm.yml`,
`apm.lock.yaml` and `.mcp.json` out of the repository, so the AI setup stays per machine.

## Step 5: Hand over

Summarise what was created and where. Then say, in this order, what the user does next — it is the
*Starting your own strategy* section of the template's `README.md`:

1. Put the securities in `Universe/Investable_Universe.csv`; `main_identifier` is the only required
   column.
2. Write `OBJECTIVE.md` — the idea and its claims — before anything is measured.
3. Write the `c_*` and `r_*` columns and the two drivers.
4. Run curator, `universe.ipynb`, refinery, `analyzer.ipynb`, in that order.
5. Write `BLUEPRINT_1.md` before the rule.

If a KaxaNuk researcher exists on this machine — a folder created from `KaxaNuk/KaxaNuk-Researcher`
— say to open both folders together: the researcher reads the strategy's `Bibliotheca/` and drafts
the objective and the blueprint from it. Skills installed in this step are discoverable in a **new**
session; say so.
