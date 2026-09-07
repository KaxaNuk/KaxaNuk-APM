# Custom calculation conventions

The contract every `c_*` function must satisfy, and how to name it.

## 1. Function equals column

- A function `def c_foo(...)` defines an output column named `c_foo`. The column name **is** the function name.
- Only functions whose name starts with `c_` become columns. Anything else in the module is a private helper
  and is never exposed, so factor shared logic into normal functions freely.
- Resolution is by **attribute name**: for each object in the `custom_calculation_modules` list passed to
  `main()`, in order, the builder tests `hasattr(module, column_name)` and takes `getattr(module, column_name)`,
  with the built-in `kaxanuk.data_curator.features.calculations` searched last. The first match wins, so a
  custom function shadows a built-in of the same name — do that only deliberately.
- Nothing checks where the function was defined; `func.__module__` is never inspected. Living in a file is a
  project convention, not a library requirement, which is why functions defined in a notebook cell can be
  attached to an in-memory module and used directly. See `programmatic-run.md`.

## 2. Parameters are injected by column name

Each parameter name must be the name of a column the curator can resolve, and it is filled with that column's
data as a `DataColumn`. See `input-columns.md` for the tags and how to list the valid names.

- Type hints are optional. `def c_x(m_close)` and `def c_x(m_close: DataColumn)` both work; the parameter
  **name** is what matters, so never rename a parameter for readability.
- Dependencies resolve recursively: a `c_*` parameter is computed first, whether it is a built-in or another
  custom function. Cycles raise `ColumnBuilderCircularDependenciesError`.
- The parameter named exactly `configuration` is special: it receives the `Configuration` entity instead of a
  column, giving access to `configuration.period`, `.start_date`, `.end_date`, `.identifiers` and `.columns`.
  Use it when the maths depends on annual vs quarterly reporting.

## 3. Return value

- Return an iterable of the **same length as the inputs**, compatible with `pyarrow.array()`: a `DataColumn`
  (preferred), a `pyarrow.Array`, a `pandas.Series` or a 1-D `numpy.ndarray`. The result is wrapped into a
  `DataColumn` automatically, so it can feed other calculations.
- Any operation that drops rows (a shift, a diff, a ratio against a lagged slice) must pad the missing leading
  positions with `None` to restore the length. See the shift-and-pad pattern in `data-column-api.md`.
- Undefined results must be `None`, never `inf` or `NaN`. `DataColumn` arithmetic already returns null for
  divisions by zero and for any row where an operand is null; when computing through `pyarrow.compute`,
  `numpy` or `pandas` directly, clean up with `helpers.replace_infinite_with_none()`.
- A rolling window of `n` rows leaves the first `n - 1` rows null. Say so in the docstring.

## 4. Naming

Names must be a single `snake_case` identifier, prefixed with `c_`, descriptive enough to be unambiguous in an
alphabetically sorted list. The rules, in the order they are applied:

1. **Most relevant term first**, so sorted lists surface the concept: `c_exponential_moving_average_21d_close`,
   not `c_close_21d_exponential_moving_average`.
2. **Spell out elementary concepts** even when an acronym exists: `c_simple_moving_average_5d`, not `c_sma_5d`.
3. **Use standard acronyms for complex indicators** that are universally known that way: `c_rsi_14d`,
   `c_macd_26d_12d`.
4. **Encode the time parameter** as `<number><letter>` with `d` days, `w` weeks, `m` months, `y` years, placed
   after the descriptive phrase. Prefer days when feasible: `c_returns_20d` over `c_returns_4w`.
5. **State the price type** (`open`, `high`, `low`, `close`) when it distinguishes the feature, except for
   returns and for indicators that are almost always computed on the close (RSI, MACD), where `close` is
   implied and omitted.
6. **Append the adjustment** when the feature depends on adjusted prices: `_split_adjusted` or
   `_dividend_and_split_adjusted`, at the very end.

Examples from the built-in catalogue:
`c_log_returns_dividend_and_split_adjusted`, `c_simple_moving_average_21d_close_split_adjusted`,
`c_annualized_volatility_63d_log_returns_dividend_and_split_adjusted`, `c_market_cap`, `c_book_to_price`,
`c_last_twelve_months_revenue_per_share`.

## 5. Documentation

Match the built-ins: a numpy-style docstring with a one-line summary, a `Parameters` section typing every
parameter as `DataColumn`, a `Returns` section, and a `Notes` section holding the formula. Use a raw string
(`r"""`) when the notes contain LaTeX or backslashes.

## 6. Fundamentals and the period

- Any dependency on `f_*`, `fbs_*`, `fcf_*`, `fis_*`, `d_*` or `s_*` means the run needs a fundamental data
  provider, which is where dividends and splits are fetched from as well. Without one, those blocks are empty
  and every column derived from them is null.
- Fundamental values are reported per filing and infilled forward onto the daily date index, so consecutive
  rows repeat the same value and the rows before the first filing are null. Design for that.
- The configured `period` (`annual` or `quarterly`) changes the values. When a formula only makes sense for one
  of them, branch on `configuration.period` and raise `CalculationError` for the unexpected case, as
  `c_last_twelve_months_net_income` does.

## 7. Composition

Prefer composing over recomputing: take `c_log_returns_dividend_and_split_adjusted` as a parameter rather than
recomputing log returns, and reuse `kaxanuk.data_curator.features.helpers` for the heavy lifting
(`annualized_volatility`, `exponential_moving_average`, `simple_moving_average`, `log_returns`,
`relative_strength_index`, `chaikin_money_flow`, `indexed_rolling_window_operation`,
`replace_infinite_with_none`). Chaining is explicitly encouraged and costs nothing: each intermediate column is
computed once and shared.