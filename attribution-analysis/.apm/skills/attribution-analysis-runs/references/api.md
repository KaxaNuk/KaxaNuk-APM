# Attribution Analysis — the surface a run touches

The API reference is public: `https://kaxanuk-attribution-analysis.readthedocs-hosted.com/en/latest/api_reference/index.html`,
build **0.2.0**, read on 2026-09-17. This file keeps only what a run touches, and the places the
documentation and the code disagree. Everything lives under `kaxanuk.attribution_analysis`.

## The entry point — `performance_attribution.main`

```python
main(
    configuration: Configuration,
    *,
    launch_dashboard: bool = True,
    dashboard_port: int,
) -> None
```

`dashboard_port` is **required and has no default**. It returns `None`: log lines, matplotlib figures,
and a Dash server when `launch_dashboard=True` *and* the factor model ran. It loads the weights (with a
fail-fast check of the configured window), the market data for the portfolio's tickers, the benchmark
returns and the factor files; aligns every table to the common date range; runs the enabled methods;
then plots or serves.

It can raise, among others: `FileNotFoundError`, `ConfigurationError`, `MissingPortfolioError` and
`DateRangeError` from loading the weights, `DataLoadingError` from the market data,
`DataIntegrityError` and `NullError` from the weight entities, `DataValidationError` for an empty
table, `MissingColumnError`, `EntityTypeError` and `DateParsingError`.

## Configuration

- `entities.configuration.Configuration` — a frozen dataclass: six directories, three file names, the
  two market-data column names, the two formats, `start_date` / `end_date` (`datetime.date`,
  `datetime` or `"auto"`) and the two method flags. Validated in `__post_init__`.
- `config_handlers.excel_configurator.ExcelConfigurator(file_path, logger_format="[%(levelname)s] %(message)s")`
  — `get_configuration()`, `get_dashboard_port()`. **On a configuration error it calls `sys.exit`.**
- `services.env_loader.load_config_env()` and
  `services.configuration_logger.configure_logger(logger_name=..., logger_level=..., logger_format=..., logger_file=...)`
  — used as *Running from Python* shows; neither has an API page.

## `interfaces.brinston_fachler_arrow_method.BrinstonFachlerArrowAttribution`

```python
BrinstonFachlerArrowAttribution(
    returns_investable_assets: pa.Table,
    complete_portfolio_weights: pa.Table,
    complete_benchmark_weights: pa.Table,
    date_column: str = "date",
)
```

| Call | Sets |
| --- | --- |
| `brinson_fachler_model(date)` | `.detail_table`, `.totals`, and returns both |
| `time_series_calculation()` | `.df`, `.output_dict` — dates in both weight tables that also have returns |
| `attribution_plots()` | `.brinston_fach_indexes`, and calls `plt.show()` |

Effects per asset and date: `allocation = (w_p − w_b) · r_b` with `r_b = w_b · r`,
`selection = alpha · w_p`, `interaction = alpha − allocation − selection`.

## `interfaces.factor_model_arrow_attribution.FactorModelArrowAttribution`

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

| Call | Sets or returns |
| --- | --- |
| `multifactor_attribution()` | `.portfolio_attribution_ts`; logs the average factor coverage |
| `time_series_calculation()` | `.simulated_rets` |
| `run()` | both, and the portfolio returns if none were given; `ValueError` without `asset_returns` |
| `calc_pct_area()` | `.pct_df_returns`, with `f_idio_returns` |
| `cummulative_pct_decomp()` | returns `dict[str, float]`, with `idio_returns` |
| `attribution_plots(title=None)`, `last_day_decomposition(title)` | figures; `title` is required by the second and overridden inside it |

`modules.data_wrangling.load_by_factor_returns_arrow(path, available_factors, portfolio_weights, start_date=None, end_date=None)`
returns `dict[str, FactorReturns]` — pass `{name: factor.table}` to the class. `available_factors`
are file names with their extension. It reads the date column plus the portfolio's own tickers,
slices from the portfolio's first weighted date, raises `DateRangeError` for a `start_date` before a
file's first date and clamps a late `end_date`.

## Entities that decide whether a run loads

| Entity | Validation on construction |
| --- | --- |
| `entities.portfolio_weights_arrow.PortfolioWeights` | a `date` timestamp column, float64 assets, no nulls, and **240–260 rows a year** in the first and last year once the table spans a year |
| `entities.returns_table.ReturnsTable` | at least one row, a `date` timestamp column, float64 assets; the first row may be null |
| `entities.factor_returns.FactorReturns` | the same, with a `factor_name` |

## Metrics — `modules.performance_functions`

`annualize_rets`, `annualize_vol`, `compound`, `cvar_historic`, `drawdown`, `kurtosis`,
`portfolio_return_daily_ts`, `semideviation`, `sharpe_ratio`, `skewness`, `summary_stats`,
`var_gaussian`, `var_historic`. `summary_stats(r, riskfree_rate=0.0, periods_per_year=252)` returns one
row indexed `'Strategy'`. Periods per year are never inferred.

## The CLI and the dashboard

`kaxanuk.attribution_analysis init excel [--entry_script NAME]`, `run [PATHS...]`, `autorun`,
`update excel | entry_script`, `--version`. `dashboard.attribution_dashboard.create_dashboard_from_attribution(attribution_results, portfolio_name=None, benchmark_name=None, logo_path=None, days_of_smoothing=45, date_column="date")`
returns an `AttributionDashboard`, whose `run_server(*, debug=True, port=8050)` blocks. The dashboard is
imported lazily, only when `main()` launches it.

## Where the documentation and the code disagree, at 0.2.0

Each was checked against the module source the documentation build publishes, and each changes what
a caller should do.

1. **Results are not written to `Output/`.** The quick start, the Excel workflow and the CLI page say
   they are; `main()` returns `None` and writes nothing. Build the attribution objects and read their
   attributes.
2. **`portfolio_input_format = "excel"` does not complete.** `main()` builds the benchmark-returns
   handler only on the `csv` branch, then uses it unconditionally.
3. **The *Data Formats* weight example cannot load.** It shows three rebalance dates over four years;
   the weight entities reject anything but a daily series once it spans a year.
4. **Factor columns for names the book never held do not raise.** *Data Formats* and the loader's
   docstring say every factor column must be a portfolio ticker; the loader reads only the portfolio's
   tickers, so an extra column is skipped.
5. **The `main()` examples omit `dashboard_port`**, which the signature requires.
