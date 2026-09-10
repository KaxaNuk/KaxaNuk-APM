# Changelog for the KaxaNuk-APM/data-refinery subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-09
### Added
- `data-refinery-custom-calculations`: authoring the `r_*` columns of a KN Research Process
  repository — the two kinds of column that belong there, the function contract the driver
  resolves by parameter name, the `current_*` join and its warning, causality per date and per
  window, the rank identity `(n + 1) / 2n`, membership from the seed, stale-file deletion, and
  what the seam has to keep stable so the Data Refinery library is a one-file swap. Written from
  the template's 0.6.0 contract; the worked example is the `example` branch's jump model.
