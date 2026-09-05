---
description: Python Bloom Code Style Guide
applyTo: "**/*.py"
metadata:
  version: 2.0.0
---
# Python "Bloom Code" Style Guide
Strict superset of PEP 8 whose single objective is reading speed for someone unfamiliar with the codebase.
The mechanical part is enforced by a script (see below); this file keeps only what needs judgment.

## Judgment rules
- Organize predictably: group declarations by a shared characteristic, then alphabetically within each group.
    This applies to constants, class attributes, dict literals and import blocks, not only to functions.
- No abbreviations, acronyms, aliases or mnemonics. A name says what the thing is.
- One concept per variable: bind a new name instead of overwriting an existing one, so every intermediate
    value stays inspectable while debugging.
- Return a single value. If a function needs several, first try splitting it into functions that return one value
    each; if that is infeasible, return a dataclass (fixed attributes) or a dict (dynamic keys), never a tuple.
- Use line breaks to separate logical concepts inside a statement and reduce visual clutter.
- Type-hinted functions do not repeat parameter or return types in the docstring.

## Mechanical rules
Before reporting Python work as done, run the Bloom Code checker on every file you touched and fix each reported
line. The checker ships in the `bloom-code-lint` skill (`scripts/bloom_code_check.py`); if that skill is not
installed, apply the list below by hand.

It enforces: no nested functions; no import aliases; `from x import y` only for local packages (everything else is
`import module` + qualified names); no `from __future__`; names of at least 3 characters; no variable reassignment;
no tuple returns; no implicit string concatenation (use `join`); declaration order (module: public then internal;
class: abstract, `__init__`, properties public/protected/private, methods public/protected/private; alphabetical
within each block); one item per line in any construct with 2+ comma-separated items; one call per line; type
hints on every parameter and return; exception message in an intermediate variable before `raise`; parenthesized
tuples; a blank line before `return`/`yield`/`raise` and around blocks that contain one; comprehensions split
across lines; multiline docstring summary starting on its own line.
