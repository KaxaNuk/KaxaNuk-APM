---
name: bloom-code-lint
description: >
  Run this skill after writing, editing or reviewing any Python file in a project that follows the KaxaNuk
  "Bloom Code" style guide, and before reporting that work as done. It runs a deterministic checker that
  reports every violation of the mechanical Bloom Code rules with a remediation hint. Do not use it for
  non-Python files, and do not use it as a substitute for the project's configured linter or formatter
  (ruff, flake8, black), which cover PEP 8.
metadata:
  version: 0.1.0
---

# Bloom Code Lint

## What it does
`scripts/bloom_code_check.py` parses each Python file with `ast` and `tokenize` and prints one line per
violation in the form `path:line: CODE message`. Exit code 0 means clean, 1 means at least one violation.
Output is ASCII only.

## Steps
1. Run the checker on the files (or directories) you touched:
   ```sh
   python <this skill's directory>/scripts/bloom_code_check.py <path> [<path> ...]
   ```
   Local application packages are detected automatically (packages and modules directly under the working
   directory or under `src/`). If a package lives elsewhere, declare it so its `from x import y` imports are
   accepted: `--local-package <name>` (repeatable). `--max-line-length N` (default 120) sets the line length
   above which two comma-separated items must split; `--strict` restores the literal reading of BLOOM010 and
   BLOOM012 (see the table).
2. Fix every reported line. The message says what to change; the rule table below says why.
3. Re-run until the checker prints `[ok]`. Only then report the Python work as done.

Do not "fix" a violation by disabling or editing the checker.

## Rules
| Code | Rule | Fix |
|---|---|---|
| BLOOM001 | Nested function definition | Move it to module level as an internal (`_`-prefixed) function |
| BLOOM002 | Import alias | Import the module itself and use its qualified name |
| BLOOM003 | `from x import y` on a non-local module | `import x`, then `x.y`; declare local packages with `--local-package` |
| BLOOM004 | `from __future__` import | Quote forward references instead |
| BLOOM005 | Bound name shorter than 3 characters (`_` allowed) | Use a meaningful name |
| BLOOM006 | Variable assigned more than once in a scope (if/elif/else branches count once) | Bind a new name per concept |
| BLOOM007 | Function returns a tuple | Split into single-value functions, or return a dataclass or dict |
| BLOOM008 | Implicit string concatenation | Use `str.join` |
| BLOOM009 | Declaration out of order | Module: public then internal. Class: abstract, `__init__`, properties (public, protected, private), methods (public, protected, private). Alphabetical within each block |
| BLOOM010 | Comma-separated items sharing a line: 3+ items, or 2 items on a line over `--max-line-length` (`--strict`: from 2 items) | One item per line, none on the opening line (calls, parameters, lists, tuples, sets, dicts, `from` imports) |
| BLOOM011 | Missing type hint on a parameter or return (`self`/`cls` exempt) | Annotate it |
| BLOOM012 | More than one nested call on a line: `f(g(h(x)))` fires, `len(x.split())` does not (`--strict`: any nested call) | Each nested call on its own line |
| BLOOM013 | `raise` with an inline message | Assign the message to a variable (for example `msg`) first |
| BLOOM014 | Tuple literal without parentheses (unpacking targets and subscripts exempt) | Parenthesize it |
| BLOOM015 | `return`/`yield`/`raise` without a blank line before it, or a block containing one without blank lines around it (a leading docstring does not count as preceding code) | Add the blank line |
| BLOOM016 | Comprehension on one line | Output expression, each `for` clause and the `if` clause on separate lines |
| BLOOM017 | Multiline docstring summary on the opening line | Start the summary on its own line |

## Not covered (judgment rules)
Grouping of constants and class attributes, abbreviations, meaningful naming, dataclass-vs-dict choice, line
breaks inside statements, and operator chains (`a and b`, `a + b`) are left to the Bloom Code instructions file.
