# Changelog for the KaxaNuk-APM/context-system subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-05
### Added
- Initial release: `docs/context/` working memory (memory, lessons, todo, results, session-log).
- Instruction `context-system` (applies to every file): read on demand, subagent hand-off, task management,
  hard caps.
- Prompt `/compact-context`: snapshot to `docs/context/archive/` and hard-compact over-cap files.
- Hooks (Python, stdlib only): `SessionStart` bootstrap, `UserPromptSubmit` size check (`--caps` prints the
  table), `SubagentStop` capture gated on a non-empty `agent_type`, `SessionEnd` daily stub, `PreCompact`
  marker. Every hook exits 0 and is a no-op when `docs/context/` is absent.
