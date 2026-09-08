# Backtest Engine — the public surface

Taken from the official documentation on 2026-09-06. Where a page could not be reached, this file
says so rather than guessing: **an invented signature is worse than a missing one.** The URLs are at
the end of `SKILL.md`.

## `PyArrowBacktester`

Module: `kaxanuk.backtest_engine.backtest.pyarrow_backtester`. Base: `BaseBacktesterInterface`.

```python
PyArrowBacktester(
    *,
    configuration: Configuration,
    market_data_bundle: MarketDataBundlePyarrow,
    portfolio_dict: dict[Timestamp, dict[str, float]],
    benchmark: Table | None,
    portfolio_df: DataFrame | None = None,
    commission_model: CommissionModelInterface | None = None,
    slippage_model: SlippageModelInterface | None = None,
    benchmarks: dict[str, Table] | None = None,
)
```

Keyword-only. In practice it is built through one of the two class methods rather than directly:

```python
@classmethod
create_from_configuration(
    configuration: Configuration,
    input_handlers: list[InputHandlerInterface],
    portfolio_handlers: list[PortfolioInputHandlerInterface],
    commission_model: CommissionModelInterface | None = None,
    slippage_model: SlippageModelInterface | None = None,
) -> PyArrowBacktester
```

```python
@classmethod
create_from_pipeline_result(
    configuration: Configuration,
    pipeline_result: DataPipelineResult,
    commission_model: CommissionModelInterface | None = None,
    slippage_model: SlippageModelInterface | None = None,
) -> PyArrowBacktester
```

Run it:

| Method | Returns |
| --- | --- |
| `run()` | `BacktestResultDict` |
| `run_with_benchmark()` | `BacktestResultDict`, with the comparison arm |

Properties on the instance: `execution_broker` (`ExecutionBroker`), `portfolio_manager`
(`PortfolioStateManager`), `rebalance_dates` (`list[Timestamp]`), `reporting_engine`
(`ReportingEngine`), `tickers` (`list[str]`).

## The `metrics` module

Public, so a figure quoted in a document can be recomputed from the returned series instead of copied
out of a cell.

**Return and risk**

| Function | Returns |
| --- | --- |
| `annualize_rets(r, periods_per_year=252)` | `float` — `(1 + r).prod() ** (periods_per_year / n_periods) - 1` |
| `annualize_vol(r, periods_per_year=252)` | `float` — `r.std() * sqrt(periods_per_year)` |
| `calculate_annualized_return(initial_value, final_value, years)` | `float` — CAGR |
| `compound(r)` | `float` — `expm1(log1p(r).sum())` |
| `sharpe_ratio(r, riskfree_rate, periods_per_year=252)` | `float` |
| `sortino_ratio(r, riskfree_rate=0.0, target_return=None, periods_per_year=252)` | `float` |
| `sortino_ratio_simple(r, riskfree_rate=0.0, periods_per_year=252, use_log_returns=False)` | `float` |
| `downside_deviation(r, target_return=0.0, periods_per_year=252)` | `float` |
| `var_historic(r, level=5)` | `float` or `pd.Series` |
| `var_gaussian(r, level, modified)` | `float` — Cornish-Fisher when `modified` |
| `cvar_historic(r, level=5)` | `float` or `pd.Series` |
| `tracking_error(portfolio_returns, benchmark_returns, periods_per_year=252, annualized=True)` | `float` |
| `information_ratio(portfolio_returns, benchmark_returns, periods_per_year=252)` | `float` |
| `skewness(r)` / `kurtosis(r)` | `float` — population, kurtosis not excess |
| `drawdown(return_series)` | `pd.DataFrame` — Wealth, Previous Peak, Drawdown |

**Series and tables**

| Function | Returns |
| --- | --- |
| `index_price_construction(daily_portfolio_returns, base=1000)` | `pd.Series` |
| `wealth_index(returns, initial_capital)` | `pd.Series` |
| `analyze_annual_returns(df, portfolio_column, strategy_name, method='simple', min_observations=2)` | `pd.DataFrame` |
| `calculate_yearly_returns(series, strategy_name, method, min_observations, annualize=True, trading_days_per_year=252)` | `list[dict]` |
| `calculate_daily_returns(price_array)` | `pa.Array` |
| `calculate_pct_change(price_array)` | `pa.Array` |
| `calculate_returns_table(price_table, date_column_name)` | `pa.Table` |
| `decimal_cumprod_pyarrow(returns_array)` | `pa.Array` |
| `pct_change_pyarrow(column, output_column_name, table, periods=1)` | `pa.Table` |

**Composite and plots**

`compute_portfolio_statistics(initial_capital, initial_portfolio_value, final_portfolio_value,
returns, total_portfolio_series, years, risk_free_rate=0.0, var_level=5.0, periods_per_year=252,
benchmark_returns=None, additional_metrics=None)` returns `dict[str, float]` — performance, risk and
distribution metrics in one call.

`annual_returns_plot(...)` and `active_returns_plot(...)` return a `matplotlib.figure.Figure`.
**A KN Research Process repository commits no charts**, so these are for looking at, not for saving
into the tree.

## CLI

```
python -m kaxanuk.backtest_engine [--version] COMMAND [ARGS]...
```

| Subcommand | Arguments and options |
| --- | --- |
| `autorun` | installs missing project files on the first run, then executes the entry script |
| `init CONFIG_FORMAT` | `excel`; `--entry_script <name>` changes the generated entry script (default `__main__.py`) |
| `run [ENTRY_SCRIPT_LOCATIONS]...` | paths to entry scripts or directories |
| `update CONFIG_FORMAT` | `excel` or `entry_script` — refresh a template |

The quick start also documents `kaxanuk.backtest_engine init excel` as the first command after
installing, and `python -m kaxanuk.backtest_engine.services.cli autorun` as the run command. Treat
the module-level form above as current and the services path as the older spelling; confirm against
the installed build's `--version` before writing either into a project.

## Named in the documentation but not verified here

These appear in the API overview, but their signature pages could not be retrieved. **Read the
component pages before calling them; do not infer a signature from the name.**

- `MultiPortfolioBacktester.generate_individual_reports` — under Backtest Components, Orchestrators.
- `arrow_to_pandas_for_analysis()` — the helper that turns returned PyArrow tables into pandas.
- Cost models, execution, interfaces and enums — Backtest Components lists them as Commission,
  slippage and trading-record models; portfolio state, trade broker and reporting engine; abstract
  interfaces for backtesters and cost models; and trading enums for order side, price type and
  rebalance status.
- Portfolio Data Pipeline: portfolio configuration service, transformer, helpers and date utilities.

## Inputs, in one place

| Input | Shape |
| --- | --- |
| Portfolio, horizontal | first column `Ticker`; one column per rebalancing date |
| Portfolio, vertical | first column `date`; one column per ticker |
| Market data | `{TICKER}.csv` or `{TICKER}.parquet`; a date column plus at least three price columns, roles mapped in the configuration |
| Dates | `YYYY-MM-DD` |
| Configuration | `Config/backtest_engine_parameters.xlsx`, or a dict or YAML in code |
| Licence | `Config/.env` — `KNBE_API_KEY_KAXANUK`. The published quick start still shows an older `KNPC_API_KEY_KAXANUK`; that spelling is stale |
