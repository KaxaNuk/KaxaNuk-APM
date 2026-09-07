# Changelog for the KaxaNuk-APM/context-system subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-09-07)

**Install with `apm install KaxaNuk/KaxaNuk-APM/context-system` in a project that wants durable working memory; the first session creates `docs/context/` and the hooks keep it bounded from then on.**

### Added
- `docs/context/` working memory: `memory.md`, `lessons.md`, `todo.md`, `results.md`, `session-log.md`.
- Instruction `context-system` (applies to every file): read the context files on demand with grep, never in
  bulk; hand the relevant lines to subagents; task management; hard caps that live only in the hook.
- Prompt `/compact-context`: snapshot to `docs/context/archive/` and hard-compact the files over cap.
- Hooks (Python, stdlib only, always exit 0, no-op when `docs/context/` is absent): `SessionStart` bootstrap
  of the missing stubs, `UserPromptSubmit` size check (`--caps` prints the table), `SubagentStop` capture
  gated on a non-empty `agent_type` so ambient turns never leak the user's prompt into `results.md`,
  `SessionEnd` daily stub, `PreCompact` marker.

### Verified
- `apm install` (apm-cli 0.29.0) into a Claude-target project on 2026-09-05: hooks merged into
  `.claude/settings.json` with commands anchored on `${CLAUDE_PROJECT_DIR}/.claude/hooks/context-system/...`,
  script bundle deployed with its sibling module, instruction deployed as `.claude/rules/context-system.md`,
  prompt deployed as `.claude/commands/compact-context.md`. All five hooks ran with synthetic payloads: bootstrap
  created five stubs then stayed silent, size check silent under cap and loud over cap, subagent capture wrote
  zero lines for an ambient payload and one line (accents intact) for a real one, session end wrote one stub
  per day, precompact wrote its marker, invalid stdin exited 0.
