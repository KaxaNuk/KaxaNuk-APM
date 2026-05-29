---
description: Initialize APM (Agent Packaging Manager) for the current repository
input:
  - agent_type: "Optional: AI agent system to use (e.g. claude, codex, cursor, copilot)"
metadata:
  version: 0.1.1
---

# Initialize APM

You are tasked with setting up [Microsoft APM](https://microsoft.github.io/apm/llms.txt) for the current repository.
The tasks that need to be completed are as follows:
- Install `apm-cli` as a dev dependency
- Run the APM initialization
- Edit the `.gitignore` file

To accomplish those tasks we go through the following steps.
If you see that any step was already been completed, just continue with the next step.


## Step 1: Install `apm-cli` as a dev dependency
Check how development dependencies are managed in the current repository.
You need to check the following:
1. Is there a `pyproject.toml` file managing the dependencies?
2. Are the dev dependencies being managed in `pyproject.toml`, `requirements-dev.txt`, or not at all?
3. Is a dependency management tool for Python being used for managing these files (e.g. pdm, uv, poetry)?

Once you have checked the above points, the way to install APM will depend on the following cases:

### Possibility 1: Both `pyproject.toml` and `requirements-dev.txt` files are missing from the repo
In this case:
1. Create a new `requirements-dev.txt` file, containing just `apm-cli`.
2. Run `pip install -r requirements-dev.txt` to install APM.

### Possibility 2: `pyproject.toml` is missing but `requirements-dev.txt` exists
In this case:
1. Add `apm-cli` to the `requirements-dev.txt` file.
2. Run `pip install -r requirements-dev.txt` to install APM.

### Possibility 3: `pyproject.toml` exists but `requirements-dev.txt` is missing
In this case:
- If you found the dependency management tool, use it to add the latest compatible version of `apm-cli`
    as a dev dependency.
- Otherwise, check [PyPI](https://pypi.org/project/apm-cli/) to find the current APM version, add it manually
    to the `dev` list in the `dependency-groups` section, and run `pip install`.

### Possibility 4: Both `pyproject.toml` and `requirements-dev.txt` files exist
In this case:
- If the `pyproject.toml` file contains a `dependency-groups` section, we'll ignore the `requirements-dev.txt` file
    and follow the instructions above for the "if `pyproject.toml` exists but `requirements-dev.txt` is missing" case.
- Otherwise, we'll ignore the `pyproject.toml` file and follow the instructions above for the "if `pyproject.toml` is
    missing but `requirements-dev.txt` exists" case.


## Step 2: Run the APM initialization
If an `apm.yml` file already exists in the repository's root directory, you can skip this step.

Determine the value of the `target` option for the user's AI agent system type as follows:
- If ${input:agent_type} is set, use that as the target value. If that fails during initialization because of an
    unknown target error, refer to [APM's cli reference](https://microsoft.github.io/apm/_llms-txt/cli-reference.txt)
    to see the valid targets.
- Otherwise if you as an agent are a valid target, use the value that refers to yourself.
- Otherwise, if a `CLAUDE.md` file or a `.claude` folder exists, use `claude`.
- Otherwise leave the `target` option empty.

To create the `apm.yml` file, you need to run `apm init -y` in the repository's root directory, appending the `--target`
option with the determined value, if a value was determined.

Example if Claude is detected:
```sh
apm init -y --target claude
```

In case of an error during initialization, you can always rerun the command appending the `--verbose` flag to see more
details.


## Step 3: Edit the `.gitignore` file
After initializing APM successfully, a new entry should have been added to the `.gitignore` file to ignore the
`apm_modules/` folder.
We need to add additional entries to guarantee that the developer's local setup is kept out of the repository.
Add to the `.gitignore` file all the entries in the following list that are missing from the file:
```gitignore
.agents/
.claude/
apm_modules/
.mcp.json
apm.lock.yaml
```


## Step 4: Inform the user of next steps
Now that APM has been successfully initialized for the current repo, give the user a summary of what you did.
Then tell the user that they need to run `apm install` for each APM dependency's URL to add them to their local AI setup.
Propose to run it yourself if they give you their APM dependency URLs.
If they do, run `apm install <dependency_url>` for each `<dependency_url>` you receive.
