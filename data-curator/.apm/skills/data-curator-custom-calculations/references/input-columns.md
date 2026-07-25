# Input columns

Every parameter of a `c_*` function must name a column the curator can resolve. The prefix before the first
underscore selects the data block; the rest of the name is the field within it.

| Prefix | Data block | Resolved from |
|---|---|---|
| `m_`   | Market data | fields of the `MarketDataDailyRow` entity |
| `f_`   | Filing / fiscal info | fields of the `FundamentalDataRow` entity |
| `fbs_` | Balance sheet | fields of `FundamentalDataRowBalanceSheet` |
| `fcf_` | Cash flow | fields of `FundamentalDataRowCashFlow` |
| `fis_` | Income statement | fields of `FundamentalDataRowIncomeStatement` |
| `d_`   | Dividends | date field + factor field combinations |
| `s_`   | Splits | date field + factor field combinations |
| `c_`   | Calculations | built-in and custom `c_*` functions, resolved recursively |

Plus one non-column parameter: **`configuration`**, which receives the `Configuration` entity.

## Enumerate the valid names, do not guess them

The catalogue is whatever the installed version of the package declares, so read it from the package rather
than from memory. Locate the installed package with the project's tooling (for example
`python -c "import kaxanuk.data_curator, pathlib; print(pathlib.Path(kaxanuk.data_curator.__file__).parent)"`)
and read the entity modules, or list the fields directly:

```python
import dataclasses

from kaxanuk.data_curator.entities import (
    FundamentalDataRow,
    FundamentalDataRowBalanceSheet,
    FundamentalDataRowCashFlow,
    FundamentalDataRowIncomeStatement,
    MarketDataDailyRow,
)

for (prefix, entity) in (
    ('m', MarketDataDailyRow),
    ('f', FundamentalDataRow),
    ('fbs', FundamentalDataRowBalanceSheet),
    ('fcf', FundamentalDataRowCashFlow),
    ('fis', FundamentalDataRowIncomeStatement),
):
    for field in dataclasses.fields(entity):
        print(f'{prefix}_{field.name}')
```

The available `c_*` columns are the `def c_*` functions in
`kaxanuk/data_curator/features/calculations.py` plus the project's own custom modules.

## Market data columns

`MarketDataDailyRow` holds `date`, and then `open`, `high`, `low`, `close`, `volume`, `vwap`, each of them in
three variants: unadjusted, `_split_adjusted` and `_dividend_and_split_adjusted`. So `m_close`,
`m_close_split_adjusted` and `m_close_dividend_and_split_adjusted` are three different columns.

Which one to use is a modelling decision, not a detail:

- `_dividend_and_split_adjusted` for returns and anything that must be comparable through time.
- `_split_adjusted` for price levels and for anything multiplied by a share count, such as market cap.
- unadjusted for the price actually traded on the day.

`m_date` is a `date` column, not a number, and it is **not** added to the output automatically: it appears only
if it was selected, like any other column.

## Dividend and split columns

These blocks report discrete events, so their columns are built by combining every date field with every
factor field, as `<date_field>_<factor_field>`, and the factor lands on the row of that date:

- `d_` from dates `declaration_date`, `ex_dividend_date`, `record_date`, `payment_date` and factors
  `dividend`, `dividend_split_adjusted` — for example `d_ex_dividend_date_dividend`.
- `s_` from date `split_date` and factors `numerator`, `denominator` — that is `s_split_date_numerator` and
  `s_split_date_denominator`.

Rows without an event are null, so these columns are sparse by nature. Both blocks are fetched from the
**fundamental** data provider, so a run without one leaves them entirely null.

## Fundamental columns

Fundamental rows are reported per filing and infilled forward onto the daily index: every day after a filing
repeats that filing's values until the next one, and the days before the first filing are null. Values also
depend on the configured `period` (`annual` or `quarterly`).

`f_*` carries the filing metadata that makes period-aware maths possible, notably `f_fiscal_year` and
`f_fiscal_period`, which are the keys used for rolling operations across filings.

## Failure modes

- A parameter naming a field that does not exist in its entity raises
  `ColumnBuilderUnavailableEntityFieldError` at run time, naming the column.
- A `c_*` parameter with no matching function raises `ColumnBuilderCustomFunctionNotFoundError`.
- A prefix outside the table above raises `ColumnBuilderUnavailableEntityFieldError` as an unknown prefix, and
  an output column that does not match `^(c|d|f|fbs|fcf|fis|m|s)_[A-Za-z0-9_]+$` is rejected earlier, when the
  `Configuration` is built.