# Changelog for the KaxaNuk-APM/data-curator subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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