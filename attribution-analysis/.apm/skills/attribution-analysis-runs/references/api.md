# Attribution Analysis — the public surface

Taken from the library's own documentation build on 2026-09-06, including the module sources that
build carries. Where a name could not be verified, this file says so rather than guessing: **an
invented signature is worse than a missing one.** The pages are listed at the end of `SKILL.md`.

Everything below lives under `kaxanuk.attribution_analysis`.

## The entry point

`performance_attribution.main`

```python
main(
    configuration: Configuration,
    *,
    launch_dashboard: bool = True,
    dashboard_port: int,
) -> None
```

Keyword-only after `configuration`; `dashboard_port` is **required and has no default**. Returns
`None` — every output is a side effect: log lines, matplotlib figures, and a Dash server when
`launch_dashboard=True` *and* the factor model is enabled.

It runs in four stages: load, align every table to the intersection of its date range, run the
enabled methodologies, then plot or serve. `validate_license()` is the first thing it does.

Raises `FileNotFoundError` for a missing configured directory or file, and `ConfigurationError` from
`Configuration.__post_init__` for an invalid field.

## Configuration

`entities.configuration.Configuration` — a frozen dataclass, so it can be built directly instead of
through a workbook.

| Group | Fields |
| --- | --- |
| Directories | `input_directory`, `weights_portfolio_directory`, `weights_benchmark_directory`, `benchmark_returns_directory`, `investable_assets_directory`, `factor_returns_by_factor_directory` |
| File names | `portfolio_file_name`, `benchmark_file_name`, `benchmark_return_file_name` |
| Column mapping | `user_column_date`, `user_column_price` |
| Formats | `market_data_input_format` (`"csv"` / `"parquet"`), `portfolio_input_format` (`"csv"` / `"excel"`) |
| Window | `start_date`, `end_date` (`datetime.date` or `"auto"`) |
| Methods | `brinson_fachler_method`, `factor_model_method` (both `bool`) |

`config_handlers.excel_configurator.ExcelConfigurator(path)` reads the workbook and exposes
`get_configuration()` and `get_dashboard_port()`. It implements
`config_handlers.configurator_interface.ConfiguratorInterface`, whose `DASHBOARD_PORT_MIN` and
`DASHBOARD_PORT_MAX` bound the port.

## `BrinstonFachlerArrowAttribution`

Module: `interfaces.brinston_fachler_arrow_method`. Implements
`interfaces.brinston_fachler_arrow_interface.BrinstonFachlerArrowInterface`.

Note the spelling: the class is `Brinston`, the method is `brinson_fachler_model`, the methodology
is Brinson-Fachler. All three are as written.

```python
BrinstonFachlerArrowAttribution(
    returns_investable_assets: pa.Table,
    complete_portfolio_weights: pa.Table,
    complete_benchmark_weights: pa.Table,
    date_column: str = "date",
)
```

Each table carries the date column plus one float64 column per asset. Weight rows should sum to 1.0
per date.

| Call | Sets | Contents |
| --- | --- | --- |
| `brinson_fachler_model(date)` | `.detail_table`, `.totals` | one date; also returns them as a tuple |
| `time_series_calculation()` | `.df`, `.output_dict` | every date present in both weight tables *and* in the returns |
| `attribution_plots()` | `.brinston_fach_indexes` | cumulative sums; **also calls `plt.show()`** |

Columns:

- `.detail_table` (per asset): `asset`, `portfolio_weights`, `benchmark_weights`, `returns_data`,
  `portfolio_returns`, `benchmark_returns`, `alpha`, `allocation`, `selection`, `interaction`.
- `.totals` and `.df`: `date`, `portfolio_returns`, `benchmark_returns`, `alpha`, `allocation`,
  `selection`, `interaction`.
- `.output_dict`: date to that date's `.detail_table`.
- `.brinston_fach_indexes`: `date` plus the cumulative sum of the six numeric columns.

`.df` comes back with the right schema and zero rows when no date qualifies, so an empty result is
not an exception. Check `num_rows`.

A pandas reference implementation exists as `interfaces.brinston_fachler_method.BrinstonFachlerAttribution`
(interface: `BrinstonFachlerInterface`). The PyArrow one is what `main()` runs.

## `FactorModelArrowAttribution`

Module: `interfaces.factor_model_arrow_attribution`. Implements
`interfaces.factor_model_arrow_interface.FactorModelArrowAttributionInterface`.

```python
FactorModelArrowAttribution(
    daily_portfolio_weights: pa.Table,
    by_factor_factor_returns: dict[str, pa.Table],
    asset_returns: pa.Table,
    portfolio_returns: pa.Table | None = None,
    benchmark_returns: pa.Table | None = None,
    date_column: str = "date",
)
```

`by_factor_factor_returns` maps a factor name to a table of that factor's **per-asset** returns.
`portfolio_returns` is computed from weights and asset returns when it is not supplied.

| Call | Sets / returns |
| --- | --- |
| `multifactor_attribution()` | `.portfolio_attribution_ts` — daily contribution, one column per factor |
| `time_series_calculation()` | `.simulated_rets` — the cumulative sum of the above |
| `run()` | both of the above, then `portfolio_returns` if it was not given. Raises `ValueError` if `asset_returns` is `None` |
| `calc_pct_area()` | `.pct_df_returns` — daily percentage split, plus `f_idio_returns` |
| `cummulative_pct_decomp()` | **returns** `dict[str, float]`: each factor's share of total excess return at the last date, plus `idio_returns` |
| `last_day_decomposition()`, `attribution_plots(title=None)`, `plot_stacked_weights_normalized()` | plotting and last-day views |

Reserved names, dropped from the factor set wherever a decomposition is computed: `f_market`,
`f_total_factor_returns`, `f_total_excess_returns`, `f_idyo_returns`. When
`f_total_excess_returns` is present in `.simulated_rets` it becomes the denominator of
`cummulative_pct_decomp()`; otherwise the denominator is the sum of the remaining factor columns.

`multifactor_attribution()` logs `Average total factor coverage throughout the portfolio` — the
mean, across dates, of the portfolio weight covered by at least one factor file.

`calc_pct_area()` divides by the day's portfolio return and forward-fills any non-finite result from
the previous day, starting at 0.0.

A pandas reference implementation exists as `interfaces.factor_model_attribution.FactorModelAttribution`
(interface: `FactorModelAttributionInterface`), alongside module-level helpers `resample_rate`,
`weighted_std` and `wexp`.

## Metrics — `modules.performance_functions`

Public, so a figure quoted in a document can be recomputed from the returned series rather than
copied out of a cell.

`annualize_rets`, `annualize_vol`, `compound`, `cvar_historic`, `drawdown`, `kurtosis`,
`portfolio_return_daily_ts`, `semideviation`, `sharpe_ratio`, `skewness`, `summary_stats`,
`var_gaussian`, `var_historic`.

```python
summary_stats(
    r: pd.DataFrame,
    riskfree_rate: float = 0.0,
    periods_per_year: int = 252,
) -> pd.DataFrame
```

One row, indexed `'Strategy'`, with columns `Annualized Return`, `Annualized Vol`, `Sharpe Ratio`,
`Max Drawdown`, `Skewness`, `Kurtosis`, `Cornish-Fisher VaR (5%)`, `Historic CVaR (5%)`.

## Input handlers and services

| Purpose | Class or function |
| --- | --- |
| Market data | `input_handlers.csv_input.CsvInput`, `input_handlers.parquet_input.ParquetInput` |
| Portfolio weights | `input_handlers.csv_portfolio_input_handler.CsvPortfolioInputHandler`, `input_handlers.excel_portfolio_input_handler.ExcelPortfolioInputHandler` |
| Weights and returns | `input_handlers.portfolio_weights_input_handler.WeightsInputHandler`, `input_handlers.portfolio_returns_input_handler.PortfolioReturnsInputHandler` |
| Loading | `market_data_pipeline.market_data_service.MarketDataService`, `portfolio_data_pipeline.portfolio_service.PortfolioService` |
| Factor files | `modules.data_wrangling.load_by_factor_returns_arrow` (and `..._csv`) |
| Shaping | `modules.table_conversion_arrow` — `pyarrow_prices_to_attribution_format`, `portfolio_table_to_arrow`, `returns_table_to_arrow`, `compute_returns_from_prices_arrow` |
| Portfolio shape | `portfolio_data_pipeline.portfolio_transformer` — `detect_portfolio_format`, `transpose_vertical_to_horizontal`, `entity_to_weights_dict` |
| Dates | `portfolio_data_pipeline.date_utils` — `parse_config_date`, `parse_date_with_formats` |
| Environment and logging | `services.env_loader.load_config_env`, `services.configuration_logger.configure_logger` |
| Licence | `services.license_validator.validate_license` |

`load_by_factor_returns_arrow(path, available_factors, portfolio_weights, start_date=None, end_date=None)`
derives each factor's name from its file name with `file_name.split(".")[0]`, skips only
`.gitkeep`, reads only the date column plus the portfolio's own tickers, and parses dates as
`%Y-%m-%d` falling back to `%d/%m/%Y`. It raises `DateRangeError`, `DataValidationError`,
`MissingColumnError` or `EntityTypeError`.

## Entities

`entities.configuration.Configuration`, `entities.factor_returns.FactorReturns` (`.table`,
`.factor_name`, `.validate_asset_coverage()`), `entities.market_data.MarketData`,
`entities.market_data_daily_row.MarketDataDailyRow`, `entities.portfolio.PortfolioEntity`
(`.from_dict`, `.get_tickers`, `.get_date_columns`, `.get_weights_for_date_column`),
`entities.portfolio_daily_weights.PortfolioDailyWeights`,
`entities.portfolio_returns.PortfolioReturns`, `entities.portfolio_weights_arrow.PortfolioWeights`
(`.table`, `.asset_names`), `entities.returns_table.ReturnsTable` (`.table`),
`entities.strategy_weights.DailyWeights`, `entities.ticker.Ticker`.

## The CLI

`kaxanuk.attribution_analysis`, from the project root.

| Command | Arguments | What it does |
| --- | --- | --- |
| `init CONFIG_FORMAT` | `excel`; `--entry_script <name>.py` | creates `Config/`, `Input/**`, `Output/` and the entry script. Fails if `Config/` exists |
| `run [PATHS...]` | zero or more entry scripts or directories | runs `__main__.py` in the working directory when given nothing |
| `autorun` | — | installs the files if missing, otherwise runs |
| `update CONFIG_FORMAT` | `excel` or `entry_script` | regenerates from the template, backing the old file up as `*.1.xlsx` / `*.1.py` |
| `--version`, `--help` | — | — |

## Dashboard

`dashboard.attribution_dashboard.AttributionDashboard` and
`create_dashboard_from_attribution(attribution_results, portfolio_name, benchmark_name, days_of_smoothing)`.
Imported lazily inside `main()`, so it is not pulled in by importing the package.
`dashboard.run_server(port=...)` blocks. The supporting modules are `dashboard.callbacks`,
`dashboard.components`, `dashboard.layouts` and `dashboard.styles`.

## Two disagreements between the documentation and the code

Both were read off the module sources in the same build, and both change what a caller should do.

1. **The user guide says results are written to `Output/`.** `main()` is documented as returning
   `None` with "all outputs are side-effects: log messages, plots, and/or a running Dash server",
   and nothing in the pipeline writes a result file. Build the attribution objects and read their
   attributes.
2. **`portfolio_input_format = "excel"` does not complete.** `main()` builds
   `benchmark_return_handlers` only on the `csv` branch of that switch, then uses it unconditionally.
   The `excel` branch reaches an unbound name.
