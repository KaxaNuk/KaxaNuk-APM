# Portfolio Construction — the public surface

Checked against **`kaxanuk.portfolio_construction` 1.28.0**, from its source and a wheel built from it,
on 2026-09-17. Almost every callable is keyword-only. Where this file and the library disagree, the
library wins; report the difference.

## Imports

| From | Names |
| --- | --- |
| `kaxanuk.portfolio_construction.entities` | `UniverseSnapshot`, `AllocatedUniverse`, `Weights`, `Signal`, `BinaryMatrix`, `TimeSignal`, `Classification`, `ThresholdSpec`, `Mandate`, `Bounds`, `ConstraintLayer`, `BenchmarkSpec`, `Scenario`, `MarketDataPanel`, `Configuration`, and every method's config |
| `kaxanuk.portfolio_construction.selection` | `LiquidityFilter`, `BinaryFilter`, `ColumnMembershipFilter`, `MembershipFilter`, `CompositeUniverseFilter`, `UniverseCreator`, `UniverseMembership`, `SelectionInterface` |
| `kaxanuk.portfolio_construction.sizing` | `build_allocator`, `describe`, `requirements_for`, `ALLOCATOR_REQUIREMENTS`, the fourteen allocators and their configs, `SizingInterface` |
| `kaxanuk.portfolio_construction.timing` | `CalendarRebalancer`, `FixedDateRebalancer`, `TimeSignalRebalancer`, `MomentumTurnoverRebalancer`; with QuantLib, `EndOfMonthRebalancer`, `LastTradingDayOfMonthRebalancer`, `WeeklyMondayRebalancer`, `QuarterlyFridayWednesdayRebalancer` |
| `kaxanuk.portfolio_construction.pipeline` | `run_pipeline`, `PipelineResult`, `PipelineTrace`, `StageRecord` |
| `kaxanuk.portfolio_construction.enums` | `MissingDataPolicy`, `RebalanceFrequency`, `ComparisonOp`, `CovarianceMethod`, `OptimizationObjective`, `WeightingMethod`, `TimingMode`, `BenchmarkKind`, `LimitBasis`, `ExposureMeasure`, `StandardField` |
| `kaxanuk.portfolio_construction.helpers` | `PanelHelper`, `RollingHelper`, `CrossSectionalHelper`, `ThresholdHelper`, `CovarianceHelper`, `PortfolioDiagnosticsHelper`, `FeasibilityHelper`, `FrontierHelper`, `ResamplingHelper`, `ScenarioHelper`, `ActiveHelper`, `DataQualityHelper` |
| `kaxanuk.portfolio_construction.input_handlers` | `CsvInput`, `ParquetInput` |
| `kaxanuk.portfolio_construction.output_handlers` | `CsvOutputHandler`, `PdfReportOutput`, `PortfolioReport` |
| by module path only | `builders.universe_builder.UniverseBuilder`, `config_handlers.excel_configurator.ExcelConfigurator`, `market_data_pipeline_services.market_data_service.MarketDataProcessingService`, `entities.portfolio.PortfolioEntity`, `output_handlers.excel_output_handler.ExcelOutputHandler` |

Every exception derives from `exceptions.PortfolioConstructionError`: `AllocationError`,
`ConfigurationError` (with `AllocatorConfigurationError`, `MandateError`, `ViewError`, `BenchmarkError`
under it), `FilterError`, `PipelineError`, `PortfolioEntityError`, `ReadingCSVError`, `MarketDataError`.
An unknown method name in `build_allocator` raises `KeyError`, listing the names.

## Sizing: the registry

`build_allocator(*, name, config=None, returns=None, prices=None, date_column="date")`. `prices` is
always refused. `config=None` works only when the method's config has no required field. A
returns-based method takes `returns`; a snapshot-only method refuses it.

| Name | Config — required fields in bold | History | Snapshot columns | Extra | Bounds | Shorts |
| --- | --- | --- | --- | --- | --- | --- |
| `equal_weight` | `EqualWeightConfig()` | — | — | — | none | never |
| `feature_weighting` | `FeatureWeightingAllocatorConfig(`**`feature_column`**`, `**`method`**`)` — `WeightingMethod.EQUAL`, `PROPORTIONAL`, `INVERSE` | — | the feature | — | none | flag |
| `kn_index` | `KNIndexAllocatorConfig(`**`zeta, min_weight, col_market_cap, col_adtv_63d, col_adtv_252d`**`)` | — | the three columns | — | none | never |
| `inverse_volatility` | `InverseVolatilityConfig()` | returns | — | — | none | never |
| `risk_parity` | `RiskParityConfig(budgets=None)` | returns | — | — | none | never |
| `max_diversification` | `MaxDiversificationConfig()` | returns | — | — | clip | flag |
| `mean_variance` | `MeanVarianceConfig(`**`objective`**`)` — `MIN_VARIANCE` or `MAX_SHARPE` | returns | expected return, for `MAX_SHARPE` | — | clip | flag |
| `black_litterman` | `BlackLittermanConfig(`**`market_cap_column`**`, views=())` | returns | market cap | — | clip | flag |
| `hrp` | `HRPConfig(linkage="single")` | returns | — | `clustering` | none | never |
| `herc` | `HERCConfig()` | returns | — | `clustering` | none | never |
| `nco` | `NCOConfig()` | returns | — | `clustering` | clip | flag |
| `constrained_mean_variance` | `ConstrainedMeanVarianceConfig(`**`objective`**`, mandate=None)` | returns | expected return, except `MIN_VARIANCE` | `solver` | hard | mandate |
| `cvar` | `CVaRConfig(alpha=0.95, mandate=None)` | returns | — | `solver` | hard | mandate |
| `cdar` | `CDaRConfig(alpha=0.95, mandate=None)` | returns | — | `solver` | hard | mandate |

*Bounds*: **hard**, the mandate is a constraint of the solve; **clip**, negatives clipped and the book
renormalised; **none**, group limits only afterwards, with `Weights.cap_groups`. The returns-based
configs share `covariance_method` (`SAMPLE`, `LEDOIT_WOLF`, `OAS`, `EWMA`, `SEMICOVARIANCE`),
`periods_per_year=252`, `ewma_decay=0.94`, `shrinkage=0.0` and `missing=MissingDataPolicy.EXCLUDE`.
**Since 1.28.0 every limit is annual** against `periods_per_year`: monthly returns need `12`.

- `SizingInterface.allocate(*, snapshot) -> AllocatedUniverse`, and
  `get_sizing_weights(*, universe) -> pa.Table`, which returns the table with the weight column added.
- **A returns-based method never slices its history by date** (see the skill, section 4).
- `KNIndexAllocator`: `kn_weight = zeta * traded-value weight + (1 - zeta) * market-cap weight`. With
  `max_constituents` set, `min_weight` is not applied; `min_constituents` is validated and never
  enforced.

## Entities

| Entity | Construct | What construction proves |
| --- | --- | --- |
| `UniverseSnapshot` | `UniverseSnapshot(*, table, as_of=None)` | a `ticker` column, at least one row, no null or duplicate tickers |
| `AllocatedUniverse` | returned by `allocate` | the weight column present, no nulls, no negatives unless `allow_shorts`, the sum equal to `target_exposure` (1.0) within 1e-6 |
| `Weights` | `from_allocated(*, allocated)`, `from_scores(*, scores, tickers)`, `equal(*, tickers)`, `from_table(*, table, weight_column)` | the same invariants. `as_mapping()`, `cap(*, maximum)` — **redistributes the excess** — `cap_gross`, `cap_groups(*, classification, dimension, limits)`, `exclude(*, tickers)`, `blend(other, *, alpha)`, `tilt(*, factors)` |
| `Signal` | `Signal.from_mask(*, mask, tickers, name)` | a boolean per ticker, null allowed; `&`, `\|`, `~` are Kleene; `passing_mask(*, missing)` |
| `BinaryMatrix` | `from_signals(*, signals)`, `from_panel_threshold(*, panel, threshold)`, `from_hysteresis(*, entry_matrix, exit_matrix)` | `date` first, one boolean column per ticker, dates ascending and unique. `active_on(*, target_date, missing)`, `turnover()`, `hold_through(*, dates)`, `coverage()`, `to_pandas(*, missing=None)` |
| `Classification` | `Classification(*, assignments)`, `from_snapshot_column(...)` | a dated label queried without `as_of` raises |
| `Mandate` | `Mandate(classification, layers=(), bounds={}, default_bounds=Bounds(0.0, 1.0))` | `violations(*, weights)`; `FeasibilityHelper.analyze(*, mandate, tickers)` names an impossible constraint before a solve |

## Selection and timing

- `LiquidityFilter(thresholds=(ThresholdSpec(column, op, value), ...))` — a threshold filter under
  any name; `ComparisonOp` has `GE`, `LE`, `GT`, `LT`, `EQ` and no not-equal.
- `BinaryFilter(*, column, include_value=1.0)`; `CompositeUniverseFilter(*, filters)`.
- `UniverseCreator(*, classification, dimension, rules_by_group, base_filters=())` is not a pipeline
  stage: `build_membership(*, snapshots) -> UniverseMembership`, whose `matrix` is a `BinaryMatrix`.
- `CalendarRebalancer(*, trading_dates, frequency)` with `RebalanceFrequency.WEEK_START`, `WEEK_END`,
  `MONTH_START`, `MONTH_END`, `QUARTER_START`, `QUARTER_END`, `YEAR_START`, `YEAR_END`;
  `get_timing_dates()`.
- `FixedDateRebalancer(*, dates)` returns the dates as given: no sorting, no trading-day check.
- `TimeSignalRebalancer(*, signal, mode)` — `TimingMode.ON_CHANGE` or `WHILE_TRUE`. With `EXCLUDE`, a
  null inside a True run makes two spurious change points.

## Pipeline

`run_pipeline(*, stages, snapshots) -> PipelineResult`. `stages` is a sequence of `(name, stage)`,
selection or sizing; `snapshots` maps each date to a table. The missing-data policy is fixed at
`EXCLUDE`. **One failing date aborts every date and returns nothing.** `PipelineResult.weights` maps
each date to the last stage's table; `trace.summary()` gives rows in and out per stage, and
`trace.dump(*, directory)` writes each stage's table as Parquet.

## Loading data

```python
configuration = Configuration(
    start_date=datetime.date(2018, 1, 1),
    end_date=datetime.date(2025, 12, 31),
    date_column_name="m_date",
    input_market_data_directory="Data/Curator/Time_Series",
    output_directory="Experiments/Experiment_1/Portfolio",
    market_data_input_format="csv",
    identifiers=("AAPL", "MSFT"),
    input_data_column_names=("m_close", "c_market_cap"),
    field_mapping={StandardField.DATE: "m_date"},
)
service = MarketDataProcessingService(
    configuration=configuration,
    input_handlers=[CsvInput(input_dir="Data/Curator/Time_Series")],
)
market_data = service.load_and_process_market_data(tickers=set(configuration.identifiers))
```

- Both directories must already exist, relative to the working directory.
- `market_data` maps each column to a wide panel: `date`, then one column per identifier, null where an
  identifier has no row. Column order follows the set, so it is not stable between runs.
- Only numeric columns load, as decimals. `PanelHelper.simple_returns(*, table)` turns a price panel
  into returns.
- `UniverseBuilder().build_snapshots(*, market_data_dict, tickers, required_fields, rebalance_dates)`
  gives one table per date, reading values **on** that date, and all-null for a date the panel lacks.

## Writing the weight file

`PortfolioEntity.from_dict(weights_dict)` takes ISO date strings as keys — a `date` key raises —
upper-cases tickers, fills tickers absent on a date with 0.0, refuses negatives, and accepts a column
summing below 1. `CsvOutputHandler(*, output_dir, filename="portfolio_weights.csv").write(portfolio=...,
config=None)` writes `Ticker` then one column per date: the horizontal layout the Backtest Engine
detects.

## CLI

| Command | Behaviour |
| --- | --- |
| `kaxanuk.portfolio_construction init excel` | lays down `Config/portfolio_construction_parameters.xlsx`, `Input/`, `Output/` and `kn_us_equity_benchmark_portfolio.py`. **Editable installs only** |
| `kaxanuk.portfolio_construction run [PATH ...]` | runs each entry script in a subprocess |
| `kaxanuk.portfolio_construction autorun` | `init` if the entry script is missing, `run` otherwise |
| `kaxanuk.portfolio_construction update excel` | backs up and replaces the workbook |

The workbook — sheets `General`, `Identifiers`, `Column_Mapping`, `Universe_Filters`, `KN_Index` —
describes one flow, a threshold filter then the KN Index; the rebalance dates live in the entry
script. `ExcelConfigurator` calls `sys.exit(1)` on a configuration error, so in a notebook it raises
`SystemExit`. The shipped workbook carries absolute paths from a developer's machine in `General`, and
its format list offers `excel`, which no input handler reads, while leaving out `parquet`, which one
does.

## Where the README and the code disagree, at 1.28.0

- The `calendars` extra installs QuantLib, not `exchange-calendars`.
- Market data is CSV or Parquet, one file per identifier; there is no Excel input.
- The example scripts live in `examples/`.
- The API is described as stable since 1.0.0, but 1.28.0, a minor release, changed `HRPAllocator` and
  renamed `FrontierBand` fields.
- *The library never guesses around look-ahead* — true of what it does, but a returns-based method
  inside `run_pipeline` reads future rows, as the changelog's *Known and open* section says.
