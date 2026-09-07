# Skill feedback — support the programmatic / notebook flow

Feedback for `data-curator-custom-calculations` (v0.1), from using it to build a
self-contained, single-notebook experiment that drives the Data Curator
**programmatically** (no `Config/*.xlsx`, no `src/` modules).

Verified against `kaxanuk-data-curator` 0.49.1.

## Context: a third project architecture the skill doesn't cover

The skill currently assumes custom calculations live in **files on disk** and are
selected through an **Excel config surface**. Its "Locate the calculations layout"
step lists two shapes — the standard `Config/custom_calculations.py`, and multi-file
`src/` packages scanned by an entry script — both of which read the config from
`Config/data_curator_parameters.xlsx`.

A growing third shape is the **experiment-in-a-notebook**: one `.ipynb` that inlines
the config as plain Python, defines the `c_*` functions in a cell, and calls
`kaxanuk.data_curator.main()` directly. There is no entry script and no workbook.
Once a strategy is finalized, the calcs migrate into `src/` and the Excel flow.

The skill should treat "how this project loads calcs and selects columns" as a
**dimension to detect**, not a fixed Excel assumption.

## Gap 1 — custom functions need not live in a file

The skill implies a `c_*` function must be written into a module file that the loader
imports. It doesn't state the actual discovery contract, which is looser and more
useful to know: `ColumnBuilder` resolves a column to a function purely by
**attribute name** on each object in `custom_calculation_modules` —
`hasattr(module, name)` / `getattr(module, name)`, first module wins. It does **not**
filter by `func.__module__`.

Consequence worth documenting: functions defined in a notebook cell (whose
`__module__` is `__main__`) can be attached to an in-memory module and passed
straight to `main()`:

```python
import types

def _module_from_functions(module_name, functions):
    module = types.ModuleType(module_name)
    for function in functions:
        setattr(module, function.__name__, function)
    return module

custom_calculation_modules = [
    _module_from_functions("my_calcs", [c_sma_50d, c_sma_200d, c_sma_50d_200d_signal]),
]
```

No file, no import machinery, no `__module__` gymnastics. (Any object works —
even a `SimpleNamespace` — but a `ModuleType` matches the `list[ModuleType]` hint.)

## Gap 2 — "Wire the column into the output" is Excel-only

Step 5 tells the agent to add the column name to the `Output_Columns` sheet, or to
follow a project's "own configuration surface" without saying what that looks like.
For the programmatic flow it's concrete and should be spelled out: the selected
columns are the `columns` tuple of the `Configuration` entity passed to `main()`.

```python
from kaxanuk.data_curator.entities import Configuration

configuration = Configuration(
    start_date=..., end_date=..., period="quarterly",
    identifiers=(...),
    columns=(*base_columns, "c_sma_50d_200d_signal", ...),  # <- selection lives here
)
```

Same rule as Excel (intermediate columns resolve as dependencies and need not be
listed), just a different surface.

## Gap 3 — the whole config can be built without Excel

Step 1 says "Read the project's entry script (usually `__main__.py`)". A notebook
experiment has neither `__main__.py` nor a workbook. Worth stating that the entire
configuration surface is optional: `Configuration(start_date, end_date, period,
identifiers, columns)` can be constructed directly, providers instantiated as
`FinancialModelingPrep(api_key=...)`, and `main()` called with
`output_handlers=[CsvOutput(...), ParquetOutput(...)]`. `main()` calls
`provider.initialize()` internally, so callers only instantiate. `ExcelConfigurator`
is one way to produce a `Configuration`, not the only way.

## Gap 4 — validation step assumes a file

Step 6's checklist includes `python -m py_compile <file>` and "a location the
project's loader actually picks up (mind loaders that skip files starting with `_`)".
Neither applies to inline notebook cells. Add a notebook branch: the function
compiles by running the cell, discovery is by attribute name (Gap 1), and the check
becomes "the function's name is in `Configuration.columns` (or a dependency of one)".

## Suggested shape

Add an early **"Detect the loading + selection surface"** decision with three
branches — (a) Excel + standard/`src` modules *(current)*, (b) programmatic
`main()` with file modules, (c) programmatic `main()` with in-memory modules
(notebook). Keep the naming/`DataColumn`/composition guidance shared across all
three; only steps 1, 5 and 6 differ per surface. A short `references/programmatic-run.md`
with a minimal end-to-end `main()` call (Configuration + provider + handlers +
in-memory module) would cover (b) and (c) without bloating `SKILL.md`.

## What already worked well

- The naming, input-column, `DataColumn` API and composition references transferred
  verbatim to the notebook flow — none of that is surface-specific, which is the
  right factoring.
- "Reuse before writing" and the null/length contract caught real issues.
- The `configuration` special-parameter note (period-aware maths) is exactly what a
  programmatic caller needs, since they set `period` themselves.