# Running the curator programmatically

`Config/data_curator_parameters.xlsx` and `Config/custom_calculations.py` are one way to feed
`kaxanuk.data_curator.main()`, not a requirement. Every argument can be built in plain Python, which is what a
self-contained experiment notebook does: inline configuration, calculations defined in a cell, no entry script
and no workbook. Once a strategy is finalized it usually migrates to files and the Excel surface, so the
calculations themselves must be written to survive that move unchanged — which they do, since nothing in the
naming, `DataColumn` or composition rules depends on the surface.

## The whole call

```python
import datetime

import kaxanuk.data_curator
from kaxanuk.data_curator.data_providers import FinancialModelingPrep
from kaxanuk.data_curator.entities import Configuration
from kaxanuk.data_curator.output_handlers import InMemoryOutput

data_provider = FinancialModelingPrep(api_key=api_key)
output_handler = InMemoryOutput()

configuration = Configuration(
    start_date=datetime.date(2020, 1, 1),
    end_date=datetime.date(2024, 12, 31),
    period='quarterly',
    identifiers=('AAPL', 'MSFT'),
    columns=(
        'm_date',
        'm_close_dividend_and_split_adjusted',
        'c_simple_moving_average_50d_close_dividend_and_split_adjusted',
        'c_example_golden_cross_signal',
    ),
)

kaxanuk.data_curator.main(
    configuration=configuration,
    market_data_provider=data_provider,
    fundamental_data_provider=data_provider,
    output_handlers=[output_handler],
    custom_calculation_modules=custom_calculation_modules,
)

dataframe = output_handler.export_dataframe()
```

Notes that matter:

- `main()` is keyword-only, and it calls `initialize()` on the providers itself. Callers only instantiate them.
- One provider instance can serve both roles. `fundamental_data_provider` may be `None`, in which case the
  fundamental, dividend and split blocks come out empty and every `f_*`, `fbs_*`, `fcf_*`, `fis_*`, `d_*` and
  `s_*` column is null — including any `c_*` that depends on them. Dividends and splits are fetched from the
  **fundamental** provider, not the market one.
- `Configuration` is a frozen dataclass that validates its own fields, so a bad `period` or a column name that
  does not match `^(c|d|f|fbs|fcf|fis|m|s)_[A-Za-z0-9_]+$` fails immediately, before any network call. Vary one
  field of an existing configuration with `dataclasses.replace()`.
- `identifiers` and `columns` are tuples, and every identifier is processed with the same column selection.

## Selecting the columns

`columns` **is** the selection surface, exactly equivalent to the `Output_Columns` sheet: the output table
contains those columns, in that order, and nothing else. Intermediate `c_*` columns are resolved as
dependencies and do not need to be listed.

`m_date` is not added automatically. Include it whenever the output needs a date, and always when using
`InMemoryOutput.export_dataframe()`, which indexes the frame by `('main_identifier', 'm_date')` and raises
`OutputHandlerError` if the column is missing.

## Output handlers

Pass as many as needed; each receives the same `pyarrow.Table` per identifier.

| Handler | Constructor | Result |
|---|---|---|
| `InMemoryOutput` | `InMemoryOutput()` | keeps a `{identifier: pyarrow.Table}` dict in `.data`, and `.export_dataframe()` returns all identifiers as one `pandas.DataFrame` indexed by `('main_identifier', 'm_date')` |
| `CsvOutput` | `CsvOutput(output_base_dir='Output')` | one CSV per identifier |
| `ParquetOutput` | `ParquetOutput(output_base_dir='Output')` | one Parquet file per identifier |

`InMemoryOutput` is the natural choice in a notebook: no files, and the frame is ready to plot or backtest.

## In-memory calculation modules

`custom_calculation_modules` is a list of module objects, but the resolution is just
`hasattr(module, column_name)` / `getattr(module, column_name)` over that list in order, with the first match
winning and the built-in `calculations` module appended last. Nothing checks `func.__module__`, so functions
defined in a notebook cell — whose `__module__` is `__main__` — work as-is once attached to a module object:

```python
import types


def module_from_functions(module_name, functions):
    """
    Build an in-memory calculation module from already-defined functions.

    Parameters
    ----------
    module_name : str
        A name for the module. Only used for repr and debugging.
    functions : collections.abc.Iterable
        The calculation functions to expose, each named `c_*`.

    Returns
    -------
    types.ModuleType
    """
    module = types.ModuleType(module_name)
    for function in functions:
        setattr(module, function.__name__, function)

    return module


custom_calculation_modules = [
    module_from_functions(
        'experiment_calculations',
        [
            c_simple_moving_average_50d_close_dividend_and_split_adjusted,
            c_example_golden_cross_signal,
        ]
    ),
]
```

Any object with the right attributes works, including a `types.SimpleNamespace` or the notebook's own
`__main__` module, but a `ModuleType` matches the `list[types.ModuleType]` signature and keeps the exposed set
explicit — which is the point: only the functions you list can shadow a built-in.

Re-running the cell rebuilds the module from the current function objects, so edits take effect on the next
`main()` call with no import-cache problem. That is the one real advantage of this surface over files, where a
changed module stays cached until the process restarts.