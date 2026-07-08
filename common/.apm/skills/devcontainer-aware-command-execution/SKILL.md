---
name: devcontainer-aware-command-execution
description: >
  Load this skill whenever you might need to execute any shell commands, including running any cli scripts.
  It explains the required way to run commands in the current environment.
  Any commands you or any subagent may run on the command line will fail unless these instructions are followed.
  Applies to both coding and research tasks.
metadata:
  version: 0.2.1
---

# Dev Container Aware Command Execution

## Execution Environment
Before starting any task, determine the execution environment by following these steps:
1. Read `.devcontainer/devcontainer.json` and note the service name.
2. Run `docker ps` to check if the service is active (it may be prefixed with `devcontainer-`).
3. If active: all shell commands for the remainder of the task must be run inside the container via `docker exec`.
4. If not active: run commands directly on the host. If a command fails because the local environment doesn't match
   the expected one and `docker` is available, suggest starting the devcontainer.

This check must be completed before any shell command execution, including commands run by subagents.
If you remember that you were using the devcontainer environment but suddenly the container is not running anymore,
notify the user so they decide whether to start it again or give you new instructions.
When spawning a subagent that may run shell commands, perform the check beforehand and pass the execution context
to the subagent prompt.
This is especially important during research tasks, as they will fail otherwise!

Actions that count as shell command execution:
- Running commands via the Bash tool
- Spawning subagents that explore installed packages, run tests, execute scripts, or interact with the runtime

Actions that do NOT require this check:
- Reading or editing files on the host filesystem
- Searching for files or content within the project directory using Glob or Grep
