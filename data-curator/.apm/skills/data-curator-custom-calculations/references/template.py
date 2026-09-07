"""
<Module title> — <one-line description>.

Custom Data Curator calculations. Every function whose name starts with ``c_`` becomes an output column with
that same name, and each of its parameters is injected with the data of the column named after it.

Place this module where the project's caller of ``main()`` loads it from: the library-standard location is
``Config/custom_calculations.py``, but projects with their own multi-module layout have their own rules, and a
notebook can skip files entirely by attaching these functions to an in-memory module (see
``programmatic-run.md``). Either way, remember to also select the column: the ``Output_Columns`` sheet of
``Config/data_curator_parameters.xlsx`` in the standard setup, or the ``columns`` tuple of the
``Configuration`` when calling ``main()`` directly.

Delete the examples below once the real calculations are written.
"""

import pyarrow
import pyarrow.compute

from kaxanuk.data_curator import DataColumn
from kaxanuk.data_curator.exceptions import CalculationError
from kaxanuk.data_curator.features import helpers


def c_example_momentum_21d_dividend_and_split_adjusted(
    m_close_dividend_and_split_adjusted
):
    r"""
    Calculate the 21-day momentum of the dividend-and-split-adjusted close prices.

    Parameters
    ----------
    m_close_dividend_and_split_adjusted : DataColumn
        The dividend-and-split-adjusted close prices.

    Returns
    -------
    DataColumn
        The 21-day momentum. The first 21 rows are null, as there is no price 21 rows earlier.

    Notes
    -----
    .. math::

        \mathrm{Momentum}_t = \frac{P_t}{P_{t-21}} - 1
    """
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

    return helpers.replace_infinite_with_none(
        DataColumn.load(output)
    )


def c_example_annualized_volatility_21d(
    c_log_returns_dividend_and_split_adjusted
):
    r"""
    Calculate the 21-day annualized volatility, composing an existing calculated column and a helper.

    Parameters
    ----------
    c_log_returns_dividend_and_split_adjusted : DataColumn
        The log returns of the dividend-and-split-adjusted close prices, calculated by the built-in function
        of the same name.

    Returns
    -------
    DataColumn
        The annualized volatility. The first 20 rows are null, as the rolling window is not yet full.

    Notes
    -----
    .. math::

        \mathrm{Annualized\ Volatility} = \sigma \times \sqrt{252}
    """
    return helpers.annualized_volatility(
        column=c_log_returns_dividend_and_split_adjusted,
        days=21
    )


def c_example_sales_to_price(
    c_market_cap,
    fis_revenues,
    configuration
):
    r"""
    Calculate the sales to price ratio, showing a fundamentals-dependent, period-aware calculation.

    Depends on fundamental data, so the run needs a fundamental data provider, and the values depend on the
    configured period. Fundamental values are infilled forward from each filing, so consecutive rows repeat.

    Parameters
    ----------
    c_market_cap : DataColumn
        The market capitalization, calculated by the built-in function of the same name.
    fis_revenues : DataColumn
        The revenues reported in the income statement.
    configuration : kaxanuk.data_curator.entities.Configuration
        The run configuration, used here to reject an unsupported period.

    Returns
    -------
    DataColumn
        The revenues over the market capitalization. Null wherever either input is null, and wherever the
        market capitalization is zero.

    Notes
    -----
    .. math::

        \mathrm{Sales\ to\ Price}_t = \frac{\mathrm{Revenues}_t}{\mathrm{Market\ Cap}_t}
    """
    if configuration.period not in ('annual', 'quarterly'):
        msg = f"c_example_sales_to_price failed, unexpected period type: {configuration.period}"

        raise CalculationError(msg)

    # DataColumn division already yields null on zero denominators and on null operands
    return fis_revenues / c_market_cap


def _example_private_helper(*, column, days):
    """
    Shape a private helper like this: no ``c_`` prefix, so it never becomes a column.

    Parameters
    ----------
    column : DataColumn
        The column to operate on.
    days : int
        The window length.

    Returns
    -------
    DataColumn
    """
    return DataColumn.load(
        column.to_pandas().rolling(days).sum()
    )