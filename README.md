# Volatility-Scaled Momentum

Does sizing positions by recent volatility reduce momentum crashes? This project compares a fixed-exposure equity momentum portfolio with a volatility-managed version, including trading costs.

The data pipeline and momentum signals are working. The backtest is next; there are no performance results yet.

## What works so far

- Download daily Yahoo Finance prices, dividends, and stock splits.
- Save each download with its ticker list, settings, package versions, and file checksums.
- Check missing prices, duplicate dates, coverage, and unusually large daily moves.
- Calculate monthly 12-1 momentum scores and equal-weighted long/short target weights.
- Run eight offline tests covering signal timing, missing data, portfolio weights, and saved downloads.

## Run locally

Requires Python 3.11 or newer. Run these commands from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.cli --snapshot data/raw/example-01
```

The download command uses the ten tickers in `data/universe.example.csv`. It writes the original data and a `quality.json` report under `data/raw/example-01/`, then saves monthly prices, momentum scores, and the latest rankings under `data/processed/example-01/`.

Each run needs a new snapshot name to avoid overwriting data. If a download fails, its directory may remain for inspection. Downloads require internet access; tests use synthetic and mocked data.

## Strategy design

| Setting | Proposed value |
| --- | --- |
| Universe | Current S&P 500 constituents; full list still to be added |
| Momentum signal | 12-1 month adjusted-price return |
| Holdings | Equal-weighted top and bottom deciles |
| Base exposure | $0.50 long and $0.50 short per $1 of equity |
| Rebalancing | Monthly; execution timing still to be settled |
| Volatility estimate | Previous 126 daily baseline strategy returns |
| Target volatility | 12% annualized |
| Exposure multiplier | Target volatility / estimated volatility, bounded to 0.5–2.0 |
| Trading costs | 10 bps per dollar traded |
| Development period | 2005–2015 |
| Evaluation period | 2016 through the completed-data cutoff |

At month-end t, the signal is `P[t-1] / P[t-12] - 1`. This covers eleven monthly returns and skips the latest month. For September 2026, the endpoints are September 2025 and August 2026. The implementation requires thirteen consecutive valid monthly prices through the formation month. Each decile contains `floor(eligible stocks × 0.1)` names, with ties resolved by ticker.

The example configuration downloads data before October 21, 2026 and excludes October from monthly signals. The initial ten-stock run produced 5,758 daily rows and September 30 rankings. This checked the pipeline, not strategy performance.

## Data limitations

The ten-stock example is only for checking the code. Research runs need a saved constituent list with its source and membership date recorded in `config.yaml`. Using today's S&P 500 members throughout history introduces survivorship bias.

Missing prices are left missing. The quality report flags moves above 50% in adjusted daily returns, but split/dividend reconciliation and exchange-calendar checks still need review. Yahoo can revise historical data, so retain the original snapshots when comparing runs.

Raw data, generated outputs, caches, and the virtual environment are excluded from Git. Saved manifests record installed package versions; `requirements.txt` gives compatible version ranges.

## Next steps

The next stage is a baseline backtest with explicit execution timing, historical holdings, weight drift, and transaction costs. After that come volatility scaling, risk and return metrics, crash-period analysis, and factor regressions.

The [research protocol](docs/research_protocol.md) lists the assumptions still to resolve. The [project plan](docs/project_plan.md) tracks tasks, and the [decision log](docs/decision_log.md) records changes.

## Files

```text
config.yaml          Download settings and proposed strategy parameters
src/data_loader.py   Downloads, data checks, and monthly prices
src/momentum.py      Momentum scores and long/short weights
src/cli.py           Command-line entry point
tests/               Offline tests
data/raw/            Saved downloads (ignored)
data/processed/      Prices and rankings (ignored)
results/             Backtest outputs, once implemented (ignored)
docs/                Protocol, plan, decisions, and findings
```

## References

- Barroso & Santa-Clara (2015), *Momentum has its moments*, Journal of Financial Economics.
- Daniel & Moskowitz (2016), *Momentum crashes*, Journal of Financial Economics.
- [yfinance download documentation](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html).
