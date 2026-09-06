---
description: docs/context working memory - read on demand, keep it small
applyTo: "**"
metadata:
  version: 0.1.0
---
# Context files - read ON DEMAND, never bulk-read
`docs/context/` is the project's working memory: `memory.md` (architecture decisions), `lessons.md`
(past mistakes turned into rules), `todo.md` (open work), `results.md` (build log), `session-log.md`
(session history). Reference material, not a boot sequence: bulk-reading them every task wastes
thousands of tokens.

- Trivial or single-file task: skip them entirely.
- Non-trivial task: grep the relevant file for the module, symbol or feature you touch and read only
    the matching lines. Full-read a file only when its whole content is on-topic.
- Before a fix: grep `lessons.md` for the area; you may have hit it before.
- When starting work: find the item in `todo.md` and move its status `pending` -> `in_progress` -> `done`.

## Subagents do not inherit the conversation
Paste the relevant `memory.md` / `lessons.md` lines into a subagent's prompt; it cannot know decisions
it never saw. A hook appends each real subagent's final line to `results.md`; distill anything
load-bearing into `memory.md` yourself.

## Task management
1. Plan: write the phases to `todo.md`, one line per item.
2. Finished item: 1-4 lines in `results.md`.
3. Correction from the user: one line in `lessons.md`. Friction only; update an existing line instead of
    adding a near-duplicate; delete a lesson that turns out wrong.
4. Settled architecture decision: one line in `memory.md` as `# decision: sentence`.
5. End of a work block: one line in `session-log.md` as `- [YYYY-MM-DD]: information`. A hook writes a
    bare stub when you do not; your line carries the substance.
6. HARD CAPS. Each file has a token cap that lives in ONE place: the `UserPromptSubmit` hook
    (`context_size_check.py --caps` prints the table). Never restate the values. When a turn shows
    `[context-size] OVER CAP`, run `/compact-context`. Day to day: one line per entry, no prose, dedupe
    before appending; `todo.md` holds only `pending` / `in_progress` (done items move to `results.md`).
