"""Run with python -m src.cli from the repository root."""

import argparse
from pathlib import Path

import yaml

from src.data_loader import completed_monthly_prices, download_snapshot
from src.momentum import decile_weights, momentum_12_1


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a snapshot and produce momentum rankings")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--snapshot", type=Path, required=True,
                        help="New directory under data/raw; existing paths are never overwritten")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    output = Path("data/processed") / args.snapshot.name
    if output.exists():
        raise FileExistsError(f"Processed output already exists: {output}; choose a new snapshot name")
    prices = download_snapshot(config, args.snapshot)
    monthly = completed_monthly_prices(prices, config["data"]["end_exclusive"])
    scores = momentum_12_1(monthly)
    strategy = config["strategy"]
    if scores.empty:
        raise ValueError("No completed months returned")
    latest = scores.iloc[-1]
    weights = decile_weights(latest, strategy["decile_fraction"],
                             strategy["long_exposure"], strategy["short_exposure"])
    output.mkdir(parents=True, exist_ok=False)
    monthly.to_csv(output / "monthly_adjusted_close.csv")
    scores.to_csv(output / "momentum_scores.csv")
    latest.rename("momentum_12_1").to_frame().join(weights).sort_values(
        "momentum_12_1", ascending=False).to_csv(output / "latest_rankings.csv", index_label="ticker")
    print(f"Snapshot: {args.snapshot}; rankings as of {scores.index[-1].date()}: {output}")
    print("Inspect quality.json before research use. These outputs are signals, not performance results.")


if __name__ == "__main__":
    main()
