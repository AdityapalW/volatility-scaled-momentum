import numpy as np
import pandas as pd
import pytest

from src.data_loader import completed_monthly_prices, download_snapshot, quality_report


def test_month_end_missing_price_not_filled_and_partial_month_excluded():
    prices = pd.DataFrame({"A": [100, np.nan, 120, 130]},
                          index=pd.to_datetime(["2026-08-28", "2026-08-31", "2026-09-30", "2026-10-20"]))
    monthly = completed_monthly_prices(prices, "2026-10-21")
    assert len(monthly) == 2
    assert np.isnan(monthly.loc["2026-08-31", "A"])
    assert monthly.loc["2026-09-30", "A"] == 120


def test_quality_reports_duplicates_gaps_and_bad_prices():
    prices = pd.DataFrame({"A": [100, np.nan, -2, np.inf]},
                          index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-02", "2020-01-03"]))
    report = quality_report(prices)
    assert report["duplicate_dates"] == 1
    assert report["invalid_nonpositive_or_infinite"] == 2
    assert report["tickers"]["A"]["missing"] == 1


def test_mock_download_preserves_snapshot_and_refuses_overwrite(tmp_path, monkeypatch):
    import yfinance
    dates = pd.to_datetime(["2026-09-29", "2026-09-30"])
    raw = pd.DataFrame([[100.0, 0], [101.0, 0]], index=dates,
                       columns=pd.MultiIndex.from_tuples([("Adj Close", "A"), ("Stock Splits", "A")]))
    monkeypatch.setattr(yfinance, "download", lambda *args, **kwargs: raw)
    universe = tmp_path / "universe.csv"
    universe.write_text("ticker\nA\n")
    config = {"data": {"universe_file": str(universe), "start": "2026-01-01", "end_exclusive": "2026-10-01"}}
    snapshot = tmp_path / "snapshot"
    assert download_snapshot(config, snapshot).iloc[-1, 0] == 101
    assert (snapshot / "manifest.json").exists()
    assert (snapshot / "yahoo_daily.csv").exists()
    with pytest.raises(FileExistsError):
        download_snapshot(config, snapshot)
