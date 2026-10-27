"""Signal construction only; these weights are not a backtest."""

import math

import numpy as np
import pandas as pd


def momentum_12_1(monthly_prices: pd.DataFrame) -> pd.DataFrame:
    """At month-end t, use P[t-1] / P[t-12] - 1 (11 monthly returns).

    Require every price in the lookback, including the formation month.
    Missing calendar months must remain missing rather than compressing time.
    """
    if not isinstance(monthly_prices.index, pd.DatetimeIndex):
        raise ValueError("Prices require a DatetimeIndex")
    if monthly_prices.index.has_duplicates or not monthly_prices.index.is_monotonic_increasing:
        raise ValueError("Dates must be unique and sorted")
    if monthly_prices.empty:
        raise ValueError("Prices cannot be empty")
    periods = monthly_prices.index.to_period("M")
    if periods.has_duplicates:
        raise ValueError("Expected at most one price per calendar month")
    prices = monthly_prices.copy()
    prices.index = periods
    prices = prices.reindex(pd.period_range(periods.min(), periods.max(), freq="M"))
    prices = prices.where(np.isfinite(prices) & (prices > 0))
    valid = prices.rolling(13, min_periods=13).count().eq(13)
    signal = (prices.shift(1) / prices.shift(12) - 1).where(valid)
    signal.index = signal.index.to_timestamp("M")
    signal.index.name = "date"
    return signal


def decile_weights(scores: pd.Series, fraction: float = 0.1,
                   long_exposure: float = 0.5, short_exposure: float = 0.5) -> pd.Series:
    """Deterministic tails: floor(N * fraction), ties broken by ticker.

    Require enough eligible securities for at least one security in each tail.
    """
    if not 0 < fraction <= 0.5:
        raise ValueError("fraction must lie in (0, 0.5]")
    if not all(np.isfinite(x) and x > 0 for x in (long_exposure, short_exposure)):
        raise ValueError("Exposures must be finite and positive")
    if scores.index.has_duplicates:
        raise ValueError("Ticker labels must be unique")
    eligible = scores.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    ordered = eligible.sort_values(kind="stable")
    count = math.floor(len(ordered) * fraction)
    if count == 0:
        raise ValueError("Too few eligible securities for the requested tails")
    weights = pd.Series(0.0, index=scores.index, name="weight")
    weights.loc[ordered.index[:count]] = -short_exposure / count
    weights.loc[ordered.index[-count:]] = long_exposure / count
    return weights
