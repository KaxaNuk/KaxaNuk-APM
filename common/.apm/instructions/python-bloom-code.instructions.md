---
description: Python Bloom Code Style Guide
applyTo: "**/*.py"
metadata:
  version: 2.1.0
---
# Python "Bloom Code" Style Guide
Strict superset of PEP 8 whose single objective is reading speed for someone unfamiliar with the codebase.
The mechanical part is enforced by a script (see below); this file keeps only what needs judgment.

## Judgment rules
Each rule ends with how to verify it; a rule you cannot verify is a rule you did not apply.
- Organize predictably: group declarations by a shared characteristic, then alphabetically within each group.
    This applies to constants, class attributes, dict literals and import blocks, not only to functions.
    Verification: read each block top to bottom; every adjacent pair belongs to the same group and is in
    alphabetical order.
- No abbreviations, acronyms, aliases or mnemonics. A name says what the thing is.
    Verification: grep the changed files for identifiers of 5 characters or fewer and for runs of capital
    letters; every hit is a whole English word or gets renamed.
- One concept per variable: bind a new name instead of overwriting an existing one, so every intermediate
    value stays inspectable while debugging.
    Verification: the checker's BLOOM006 passes, and a name bound in several `if`/`elif`/`else` branches
    means the same concept in every branch.
- Return a single value. If a function needs several, first try splitting it into functions that return one value
    each; if that is infeasible, return a dataclass (fixed attributes) or a dict (dynamic keys), never a tuple.
    Verification: BLOOM007 passes, and no function returns a dict whose keys are known in advance (that is a
    dataclass).
- Use line breaks to separate logical concepts inside a statement and reduce visual clutter.
    Verification: no physical line carries two logical steps; BLOOM010 and BLOOM012 pass.
- Type-hinted functions do not repeat parameter or return types in the docstring.
    Verification: grep docstrings for `:type`, `:rtype`, `Args:` blocks with parenthesized types and
    `Returns:` lines that name a type; none appear inside a type-hinted function.

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
