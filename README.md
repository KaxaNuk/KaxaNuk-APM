# KaxaNuk-APM
Microsoft APM-compatible AI scaffolding packages for use in KaxaNuk systems.

To use it you must first install APM, and then add as an APM dependency the package or its individual contents.

---

## Catalog
Each subfolder with an `apm.yml` is a package. What each one ships:

### `common` (dev conventions for every KaxaNuk Python repo)
| Primitive | Type | Fires on | Purpose |
|---|---|---|---|
| `filesystem-boundaries` | instruction | every file | Only read well-defined locations outside the project |
| `python-bloom-code` | instruction | `**/*.py` | Bloom Code judgment rules + order to run the checker |
| `python-pep8` | instruction | `**/*.py` | Points where this project is stricter than PEP 8 |
| `python-test-writing` | instruction | `**/tests/**/*.py` | Unit test folder and file structure |
| `initialize-apm` | prompt | `/initialize-apm` | Install and initialize APM in a repo |
| `apm-usage` | skill | any APM task | Pointer to the APM docs |
| `bloom-code-lint` | skill | after writing Python | Deterministic checker for the mechanical Bloom rules |
| `devcontainer-aware-command-execution` | skill | before any shell command | Run inside the devcontainer when it is up |
| `propagate-mcp-env-vars` | skill | MCP 401/403 with `${VAR}` URLs | Resolve `.env` references into `.mcp.json` |

### `context-system` (working memory in `docs/context/`)
| Primitive | Type | Fires on | Purpose |
|---|---|---|---|
| `context-system` | instruction | every file | Read `docs/context/` on demand; task management; hard caps |
| `compact-context` | prompt | `/compact-context` | Snapshot and hard-compact over-cap files |
| `bootstrap_context` | hook | `SessionStart` | Create missing `docs/context/` stubs |
| `context_size_check` | hook | `UserPromptSubmit` | Warn when a file is over cap (`--caps` prints the table) |
| `subagent_capture` | hook | `SubagentStop` | Append a real subagent's final line to `results.md` |
| `session_end_log` | hook | `SessionEnd` | Daily stub in `session-log.md` when the model wrote none |
| `precompact_log` | hook | `PreCompact` | Compaction marker in `session-log.md` |

---

## Installing APM
You can use the either the automated or manual way to install APM.

### Automated Installation
Give this prompt to your AI assistant:
```text
Please run the command that you can find in https://github.com/KaxaNuk/KaxaNuk-APM/common/.apm/prompts/initialize-apm.prompt.md
```

### Manual Installation
In case you want to execute the steps manually:
1. Install APM in your dev environment. Preferably add `apm-cli` to your pyproject dev dependencies.
2. `apm init` the repo if it doesn't have an `apm.yml` file at the root.
3. Install the parts you want from APM.
4. Recommended: Add the following lines to your `.gitignore` file to keep your local AI setup from polluting the repo:
    ```
    # AI - managed by APM
    .agents/
    .claude/
    apm_modules/
    .mcp.json
    apm.lock.yaml
    ```

---

## Adding the APM Dependencies

Before installing dependencies, it's recommended to configure your target agent system with `apm config set target <env>`.
For example if using Claude:
```bash
apm config set target claude
```

You can check the available targets at <https://github.com/microsoft/apm/blob/main/docs/src/content/docs/concepts/primitives-and-targets.md#target-catalogue>

### Add a specific package
Each subfolder in this repo containing an `apm.yml` file is its own APM package.
For example, to add the `common` package to your project:
```bash
apm install KaxaNuk/KaxaNuk-APM/common
```
Or the working-memory package:
```bash
apm install KaxaNuk/KaxaNuk-APM/context-system
```

### Pick and mix
If you just want specific AI primitives without installing the rest, just add the relevant folder (for skills) or `.md` file (for instructions, prompts, etc.):
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
Every change to the AI primitives in this repo increments the packages' versions. APM pins dependencies to the versions it downloaded during install.

To update all the APM dependencies to the latest versions, run:
```bash
apm install --update
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

Run the unit tests of the skill scripts:
```bash
pytest
```

Check the repo's own Python against the Bloom Code style guide:
```bash
python common/.apm/skills/bloom-code-lint/scripts/bloom_code_check.py common tests --local-package bloom_code_check --local-package propagate_mcp_env_vars
```
