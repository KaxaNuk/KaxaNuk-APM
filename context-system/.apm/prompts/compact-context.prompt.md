---
description: Snapshot and hard-compact over-cap docs/context working-memory files into archive
input:
  - file: "Optional: a single docs/context file name to force-compact even if under cap"
metadata:
  version: 0.1.0
---

# Compact context

Compact the working-memory files in `docs/context/` that have grown past their token cap. If
${input:file} is given, compact only that file regardless of its size.

## Caps - single source of truth
The cap values live in the `UserPromptSubmit` hook of this package. Find its command in the
harness hook configuration (Claude: `.claude/settings.json`, key `UserPromptSubmit`) and run that
same command with the extra argument `--caps`. It prints one `name cap` line per file, cap in
approximate tokens (bytes / 4). The values are not restated here.

## Procedure
1. **Measure.** Get the cap table as above. List `docs/context/*.md` with their sizes; tokens = bytes / 4.
   Targets = files over cap, or only ${input:file} when given. Today's date in `YYYY-MM-DD`.
2. **Snapshot first.** For each target create `docs/context/archive/<name-without-extension>/` if
   missing and COPY the full current file to `docs/context/archive/<name-without-extension>/<date>.md`.
   Copy, never move: the active file must stay at its canonical path.
3. **Hard-compact** each target (a subagent per file is allowed so the main context stays clean, not
   required). Rules:
   - One line per entry. No prose paragraphs.
   - Dedupe aggressively: merge every entry stating the same fact, rule or decision into one line.
   - Drop stale, superseded or completed items. Done todos go to `results.md` (then age into archive),
     never back into `todo.md`.
   - `results.md` and `session-log.md`: keep recent entries detailed, collapse older ones into grouped
     monthly one-liners. Collapse runs of auto-captured `subagent` lines into one line per work block.
     Drop `(auto-stub ...)` and `context compaction` lines older than the most recent real entry.
   - PRESERVE EXACTLY: file paths, commit hashes, migration and table names, code identifiers, dates,
     command strings, error strings, magic constants, URLs.
   - Target: under the cap, ideally about 60% of it. Lose no load-bearing fact.
4. **Write back.** Write the compacted text to `docs/context/<name>.new.md`, then move it over the
   original.
5. **Report** before and after token counts (bytes / 4) per file.

Never run this inline during unrelated feature work: hard-compaction reads whole files and derails the
task. This command is the only sanctioned time to compact.
