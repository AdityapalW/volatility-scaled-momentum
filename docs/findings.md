# Findings

No backtest results yet. The current code downloads prices, checks data quality, and produces momentum rankings and target weights.

The ten-stock example ran successfully. Eight offline tests cover signal timing, missing data, exposure, and snapshot preservation. These checks establish that the implemented functions behave as expected; they do not test the investment hypothesis.

## Planned results

- Baseline, volatility-scaled, and constant-exposure comparisons over matching dates.
- Development and evaluation performance, before and after specified costs.
- Returns, volatility, Sharpe, drawdown, turnover, and crash-window losses.
- Factor regressions and uncertainty estimates.
- Data sources, code revision, and assumptions needed to reproduce the results.
- Limitations from survivorship bias, missing data, execution, borrow fees, and financing.

The final write-up will assess whether the evidence supports the original hypothesis.
