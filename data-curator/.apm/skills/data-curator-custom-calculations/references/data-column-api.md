# DataColumn API

`DataColumn` wraps a `pyarrow.Array`. It is what every calculation parameter receives, and the preferred
return type.

```python
from kaxanuk.data_curator import DataColumn
```

## Null semantics

`DataColumn` treats any null or `NaN` as a missing value and propagates it: **any row where an operand is null
comes out null**, and a division by zero comes out null instead of `inf`. That is the main reason to stay in
`DataColumn` arithmetic rather than dropping to raw arrays — you get the correct missing-data behaviour for
free. When you do drop down to `pyarrow.compute`, `pandas` or `numpy`, you own that cleanup.

## Operators

`+`, `-`, `*`, `/`, `//`, `%`, unary `-`/`+`, and the comparisons `==`, `!=`, `<`, `<=`, `>`, `>=` all work
element-wise between two `DataColumn`s or between a `DataColumn` and a scalar (`int`, `float`, `Decimal`,
`pyarrow.Scalar`), and preserve length:

```python
return m_close_split_adjusted * fis_weighted_average_diluted_shares_outstanding   # market cap
return m_close_split_adjusted - m_open_split_adjusted                             # daily range
return c_last_twelve_months_net_income / c_market_cap                             # earnings to price
```

Decimal columns are cast to float on division, since the precision is lost anyway.

## Slicing

Slicing returns a shorter `DataColumn`, which is how lags are expressed:

```python
shifted_ratio = m_close[1:] / m_close[:-1]      # P_t / P_{t-1}, length N - 1
shifted_ratio = m_close[21:] / m_close[:-21]    # P_t / P_{t-21}, length N - 21
```

## Conversions and inspection

```python
column.to_pyarrow()             # -> pyarrow.Array, for pyarrow.compute
column.to_pandas()              # -> pandas.Series backed by Arrow, for rolling/ewm/shift
column.type                     # -> pyarrow.DataType
column.is_null()                # -> True if the whole column is null
len(column)                     # -> number of rows
DataColumn.load(data, dtype=None)       # wrap an Array, Series, ndarray or list
DataColumn.concatenate(*columns, separator='', null_replacement='')   # string-join columns element-wise
DataColumn.equal(column1, column2, approximate_floats=False, equal_nulls=False)
```

`DataColumn.load()` is the canonical way to build the return value.
`DataColumn.concatenate()` is how composite keys are built, for example joining `f_fiscal_year` and
`f_fiscal_period` into one period key.

## Pattern A — shift and pad with pyarrow

Restore the length by prepending as many `None`s as rows the shift consumed:

```python
import pyarrow
import pyarrow.compute

shifted_ratio = (
    m_close_dividend_and_split_adjusted[21:]
    / m_close_dividend_and_split_adjusted[:-21]
)
momentum = pyarrow.compute.subtract(
    shifted_ratio.to_pyarrow(),
    1
)
output = pyarrow.concat_arrays([
    pyarrow.array([None] * 21, type=momentum.type),
    momentum,
])

return DataColumn.load(output)
```

## Pattern B — pandas

`pandas` pads automatically, so lengths take care of themselves:

```python
series = m_close_dividend_and_split_adjusted.to_pandas()
result = series.rolling(21).mean()

return DataColumn.load(result)
```

## Pattern C — clean up non-finite results

Whenever a formula leaves `pyarrow`'s or `pandas`' own null handling, funnel the result through the helper:

```python
from kaxanuk.data_curator.features import helpers

rebased = m_high / m_low
result = pyarrow.compute.ln(
    rebased.to_pyarrow()
)

return helpers.replace_infinite_with_none(
    DataColumn.load(result)
)
```

## Helpers worth reusing

From `kaxanuk.data_curator.features.helpers`, all keyword-only unless noted:

| Helper | Purpose |
|---|---|
| `annualized_volatility(*, column, days)` | rolling standard deviation scaled by `sqrt(252)` |
| `exponential_moving_average(*, column, days)` | EMA with a `2 / (days + 1)` smoothing factor, reset on gaps |
| `simple_moving_average(column, days)` | rolling mean |
| `log_returns(column)` | `ln(P_t / P_{t-1})`, first row `None` |
| `relative_strength_index(*, column, days)` | RSI |
| `chaikin_money_flow(*, high, low, close, volume, days)` | CMF |
| `indexed_rolling_window_operation(*, key_column, value_column, operation_function, window_length)` | rolling window over the *unique* keys, repeating the result on duplicate keys — the way to do last-twelve-months maths on filing data infilled across days |
| `replace_infinite_with_none(column)` | turn `inf` / `-inf` into null |

`MARKET_DAYS_PER_YEAR = 252` also lives there.