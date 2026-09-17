# Changelog for the KaxaNuk-APM/data-curator subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-09-17
### Removed
- `FEEDBACK-programmatic-and-notebook-flow.md`, the feedback the 0.2.0 skill was rewritten from. All
  four of its gaps — calculations defined in memory, the column selection without Excel, the whole
  configuration in code, validation without a file — are covered by `programmatic-run.md`, and the
  note was never part of the installed skill.

## [0.2.0] - 2026-07-25
### Added
- `programmatic-run.md` reference to the `data-curator-custom-calculations` skill, covering running `main()`
  without configuration files, in-memory calculation modules for notebooks, and the output handlers.
### Changed
- The `data-curator-custom-calculations` skill now detects the loading and selection surface instead of
  assuming files on disk and an Excel configuration, and states the attribute-name discovery contract.
### Fixed
- The `data-curator-custom-calculations` skill no longer claims `m_date` is output automatically, and now
  notes that dividend and split columns also require a fundamental data provider.


## [0.1.0] - 2026-07-25
### Added
- Initial release, with the `data-curator-custom-calculations` skill.