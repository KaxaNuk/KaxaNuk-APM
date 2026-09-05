# Changelog for the KaxaNuk-APM/common subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-05
### Added
- `bloom-code-lint` skill: deterministic checker (`scripts/bloom_code_check.py`) for the mechanical subset of the
  Bloom Code style guide, 17 rules (BLOOM001-BLOOM017) with remediation messages, plus unit tests under `tests/`.

### Changed
- `python-bloom-code` instructions 2.0.0: the mechanically checkable rules moved to the `bloom-code-lint` checker;
  the file keeps only the judgment rules and the instruction to run the checker. Cuts the always-on token cost
  for every `.py` file.
- `python-pep8` instructions 2.0.0: no longer restates PEP 8; lists only the project-specific stricter points.
- `propagate-mcp-env-vars` 0.2.1: script wrapped in a `main()` guard (importable and unit-tested), functional
  substitution, explicit UTF-8, Bloom Code compliant. Behavior unchanged.
- Repo dev dependencies now include `pytest`.


## [0.1.1] - 2026-07-08
### Changed
- Updated the description of the `devcontainer-aware-command-execution` skill to reflect its usage for cli scripts.


## [0.1.0] - 2026-05-29
### Added
- Initial release
