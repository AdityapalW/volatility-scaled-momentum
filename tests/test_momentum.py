import numpy as np
import pandas as pd
import pytest

from src.momentum import decile_weights, momentum_12_1


def test_signal_skips_latest_month_and_requires_warmup():
    dates = pd.date_range("2020-01-31", periods=15, freq="ME")
    prices = pd.DataFrame({"A": 100 * 1.1 ** np.arange(15)}, index=dates)
    scores = momentum_12_1(prices)
    assert scores.iloc[:12].isna().all().all()
    assert scores.iloc[12, 0] == pytest.approx(1.1 ** 11 - 1)
    prices.iloc[12, 0] *= 10
    assert momentum_12_1(prices).iloc[12, 0] == pytest.approx(scores.iloc[12, 0])


def test_future_prices_do_not_change_past_signals():
    dates = pd.date_range("2020-01-31", periods=25, freq="ME")
    prices = pd.DataFrame({"A": np.arange(25) + 100.0}, index=dates)
    expected = momentum_12_1(prices).iloc[:15]
    prices.iloc[15:] *= 100
    pd.testing.assert_frame_equal(momentum_12_1(prices).iloc[:15], expected)


def test_missing_calendar_month_cannot_be_skipped():
    dates = pd.date_range("2020-01-31", periods=14, freq="ME")
    prices = pd.DataFrame({"A": 100.0}, index=dates).drop(dates[6])
    assert momentum_12_1(prices).iloc[-1].isna().all()


def test_tail_weights_gross_net_and_deterministic_ties():
    scores = pd.Series(np.arange(20.0), index=[f"S{i:02}" for i in range(20)])
    scores.loc["S19"] = scores.loc["S18"]
    weights = decile_weights(scores)
    assert weights.sum() == pytest.approx(0)
    assert weights.abs().sum() == pytest.approx(1)
    assert weights.loc["S00"] == -0.25
    assert weights.loc["S19"] == 0.25
    pd.testing.assert_series_equal(decile_weights(scores.iloc[::-1]).sort_index(), weights.sort_index())


def test_insufficient_universe_rejected():
    with pytest.raises(ValueError, match="Too few"):
        decile_weights(pd.Series([1.0, np.nan], index=["A", "B"]))
