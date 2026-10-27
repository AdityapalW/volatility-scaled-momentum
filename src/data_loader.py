"""Immutable Yahoo snapshots and explicit data-quality diagnostics."""

import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def quality_report(prices: pd.DataFrame) -> dict:
    """Report gaps and suspicious moves without silently filling or removing them."""
    returns = prices.pct_change(fill_method=None)
    return {
        "rows": len(prices),
        "duplicate_dates": int(prices.index.duplicated().sum()),
        "dates_sorted": bool(prices.index.is_monotonic_increasing),
        "invalid_nonpositive_or_infinite": int(((prices <= 0) | np.isinf(prices)).sum().sum()),
        "large_adjusted_moves_over_50pct": int((returns.abs() > 0.5).sum().sum()),
        "tickers": {
            str(ticker): {
                "observations": int(series.notna().sum()),
                "missing": int(series.isna().sum()),
                "first_valid": str(series.first_valid_index()),
                "last_valid": str(series.last_valid_index()),
                "internal_missing": int(series.loc[series.first_valid_index():series.last_valid_index()].isna().sum())
                if series.notna().any() else 0,
            }
            for ticker, series in prices.items()
        },
    }


def completed_monthly_prices(prices: pd.DataFrame, end_exclusive: str) -> pd.DataFrame:
    """Use the actual final observed trading date each month, without filling gaps.

    Exclude the cutoff's current month, including when a download ends mid-month.
    A ticker missing on a month's final market date remains missing.
    """
    cutoff = pd.Timestamp(end_exclusive)
    daily = prices.loc[prices.index < cutoff]
    last_complete = (cutoff.to_period("M") - 1).to_timestamp("M")
    final_rows = daily.groupby(daily.index.to_period("M"), sort=True).tail(1).copy()
    final_rows.index = final_rows.index.to_period("M").to_timestamp("M")
    final_rows.index.name = "date"
    return final_rows.loc[:last_complete]


def download_snapshot(config: dict, snapshot: Path) -> pd.DataFrame:
    """Download once to a new directory; never overwrite a previous snapshot."""
    import yfinance as yf

    data = config["data"]
    universe = pd.read_csv(data["universe_file"], dtype=str)
    tickers = universe["ticker"].str.strip().str.upper().str.replace(".", "-", regex=False)
    if tickers.isna().any() or tickers.eq("").any() or tickers.duplicated().any():
        raise ValueError("Universe must contain unique, nonempty Yahoo ticker symbols")
    if tickers.empty:
        raise ValueError("Universe cannot be empty")
    if pd.Timestamp(data["start"]) >= pd.Timestamp(data["end_exclusive"]):
        raise ValueError("Data start must precede end_exclusive")
    yf.set_tz_cache_location(str(Path(".cache/yfinance").resolve()))
    snapshot.mkdir(parents=True, exist_ok=False)
    raw = yf.download(tickers.tolist(), start=data["start"], end=data["end_exclusive"],
                      auto_adjust=False, actions=True, progress=False,
                      keepna=True, threads=False, group_by="column", multi_level_index=True)
    if raw is None or raw.empty or "Adj Close" not in raw.columns.get_level_values(0):
        raise ValueError("No adjusted prices returned; remove the empty snapshot directory and retry")
    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    prices = raw["Adj Close"].reindex(columns=tickers.tolist()).copy()
    prices.index.name = "date"
    prices.columns.name = "ticker"
    report = quality_report(prices)
    raw.to_csv(snapshot / "yahoo_daily.csv", index_label="date")
    prices.to_csv(snapshot / "adjusted_close.csv")
    pd.DataFrame({"ticker": tickers}).to_csv(snapshot / "universe.csv", index=False)
    (snapshot / "quality.json").write_text(json.dumps(report, indent=2) + "\n")
    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance via yfinance; adjusted close, dividends and splits retained",
        "config": config,
        "versions": {name: importlib.metadata.version(name)
                     for name in ("numpy", "pandas", "yfinance", "PyYAML")},
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(snapshot.iterdir()) if p.is_file()},
    }
    (snapshot / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if report["duplicate_dates"] or not report["dates_sorted"] or report["invalid_nonpositive_or_infinite"]:
        raise ValueError(f"Invalid price structure; inspect {snapshot / 'quality.json'}")
    missing = [t for t in tickers if prices[t].notna().sum() == 0]
    if missing:
        raise ValueError(f"No data for {missing}; snapshot retained for inspection")
    return prices
