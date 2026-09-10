---
description: Python PEP 8 coding standard
applyTo: "**/*.py"
metadata:
  version: 2.0.0
---
# Python PEP 8 coding standard
Follow [PEP 8](https://peps.python.org/pep-0008/) and [PEP 257](https://peps.python.org/pep-0257/) as published.
This file does not restate them; it only lists where this project is stricter:

- Compound statements on one line are forbidden, including single-clause inline `if`, `for` and `while`.
- Every module, class, function and method has a docstring. Triple-quoted strings always use double quotes;
    a multiline docstring closes on its own line.
- Absolute imports everywhere except test fixtures. No wildcard imports unless republishing an internal
    interface as part of a public API.
- Declare the public API of a module with `__all__` (`__all__ = []` means none).
- Comments are complete English sentences and are kept current with the code.
- Respect the project's configured line length for code, docstrings and comments.
- If the project configures a linter or formatter (ruff, flake8, black), run it before reporting work done
    instead of reviewing style by hand.
