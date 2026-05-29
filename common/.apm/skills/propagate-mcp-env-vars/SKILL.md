---
name: propagate-mcp-env-vars
description: >
  Invoke this skill when an MCP tool returns an authentication error (401/403) and its
  server URL in apm.yml contains environment variable references (e.g. ${MY_API_KEY}).
metadata:
  version: 0.2
---

# Propagate MCP Environment Variables

## When to Use
Use this skill when you encounter authentication errors on MCP tools and their server
definition in `apm.yml` contains `${VAR}` references in the `url` field. The error is
caused by agents like Claude Code not resolving environment variables in HTTP MCP server URLs.

## Steps
1. Check the `.mcp.json` file exists in the root of the repo. If not, tell the user to add their MCP server URL 
  by running `apm install --mcp %YOUR_MCP_SERVER_URL%` where `%YOUR_MCP_SERVER_URL%` is the URL of the MCP server.
2. Check that the `.mcp.json` file is registered in the `.gitignore` file. If not, tell the user
  that it needs to be added to the files ignored by git to prevent secret exfiltration before
  running the script. Offer to add it to the `.gitignore` file for the user.
3. After confirming `.mcp.json` is registered in the `.gitignore` file, run `scripts/propagate_mcp_env_vars.py`
  without any arguments.
  The script reads the `.env` files listed in the `ENV_FILES` constant at the top of the script (paths relative
  to the project root), then substitutes all `${VAR}` references in `.mcp.json` with their resolved values.
4. **Tell the user they must restart their agent session** for the updated `.mcp.json` to take effect.
  The MCP server connection is established at startup and will not pick up changes made during an active session.
