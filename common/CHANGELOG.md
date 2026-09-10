# Changelog for the KaxaNuk-APM/common subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.3.0 (2026-09-07)

**Before reporting Python work as done, run the `bloom-code-lint` checker on the files you touched; the two Python instructions no longer restate what it enforces.**

### Added
- `bloom-code-lint` skill: a deterministic checker (`scripts/bloom_code_check.py`, stdlib only) for the
  mechanical subset of the Bloom Code style guide, 17 rules `BLOOM001`-`BLOOM017`, each reported with a
  remediation hint. It exists because prose imperatives lose effect over long sessions and a check that fails
  the run does not; the checker is clean under its own rules. Two rules are read with a threshold by default:
  BLOOM010 (one item per line) fires from three items, or from two when the line is over the length limit
  (`--max-line-length`, default 120); BLOOM012 (one call per line) allows a single nested call. `--strict`
  restores the literal reading of both.
- Unit tests under `tests/` for the checker and for `propagate_mcp_env_vars.py`; `pytest` joins the repo dev
  dependencies.

### Changed
- `python-bloom-code` instructions 2.1.0: the mechanically checkable rules moved into the checker; the file
  keeps the judgment rules, each ending with a `Verification:` line saying how to prove it held, plus the
  instruction to run the checker. Cuts the always-on cost of every `.py` turn by roughly two thirds.
- `python-pep8` instructions 2.0.0: no longer restates PEP 8; lists only the points where KaxaNuk is stricter.
- `propagate-mcp-env-vars` 0.2.1: the script is wrapped in a `main()` guard so it can be imported and tested;
  substitution is functional and file encoding is explicit UTF-8. Behavior unchanged.

### Fixed
- `bloom-code-lint`: BLOOM010 no longer flags type parameter lists inside subscripts
  (`typing.Callable[[str, int], bool]`).

## [0.2.0] - 2026-09-05
### Added
- `how-we-work` skill: the issue-before-branch rule, the `issues/<number>` convention, the
  pull-request checklist, the changelog format and Semantic Versioning as KaxaNuk applies it to
  libraries, research repositories and APM packages, plus how a release is tagged.

## [0.1.1] - 2026-07-08
### Changed
- Updated the description of the `devcontainer-aware-command-execution` skill to reflect its usage for cli scripts.


## [0.1.0] - 2026-05-29
### Added
- Initial release
