# Changelog for the KaxaNuk-APM/attribution-analysis subpackage

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-06
### Added
- `attribution-analysis-runs` skill: installing the licensed package without leaking its key, the
  four inputs the library reads and the exact layouts it detects, the workbook and the same
  configuration in code, the CLI and the two attribution classes, the tables that come back, and how
  step 6 is called from a KN Research Process repository. It stops where `alpha-decomposition`
  starts: this skill gets the numbers out, that one reads them.
- `references/api.md`: the verified public surface — `main()`, `Configuration`,
  `BrinstonFachlerArrowAttribution` and `FactorModelArrowAttribution` with the attributes each call
  sets, the metrics function list, the input handlers, the entities and the CLI — plus a map of the
  documentation pages this skill was written from.
- `references/configuration.md`: every parameter in `attribution_analysis_parameters.xlsx`, the
  pre-run checklist, and the same configuration built as a frozen dataclass for sweeps.
- Four traps that produce a clean-looking but wrong run, each read off the module source rather
  than the prose: the factor file name *is* the factor name and is cut at the first dot; four factor
  names are reserved and silently dropped; `attribution_plots()` is the only thing that sets
  `.brinston_fach_indexes` and it calls `plt.show()`; and every input is aligned to the intersection
  of its date range, so one short factor file shortens the whole analysis.
- Two places the library's documentation and its code disagree, named as such: `main()` writes no
  files despite the user guide's `Output/` folder, and `portfolio_input_format = excel` reaches an
  unbound `benchmark_return_handlers`.
