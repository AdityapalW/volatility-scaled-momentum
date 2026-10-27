# Research protocol

Draft for the October 20–November 20, 2026 project. The settings below still need agreement from both collaborators before the backtest comparison begins.

## Question

Does volatility-based position sizing improve equity momentum's net Sharpe ratio and reduce crash losses compared with fixed exposure?

The primary comparison is net Sharpe in the evaluation period. We will also report drawdown, realized volatility, annualized return, turnover, and losses during selected crash windows. A constant-exposure portfolio calibrated on development-period risk will help distinguish volatility timing from simply taking less risk.

## Portfolio construction

The proposed settings are in `config.yaml`. The research universe will be a saved list of current S&P 500 constituents, with its source and membership date recorded. This choice introduces survivorship bias; the results will describe that universe rather than an unbiased historical index. The bundled ten-stock list is for development only.

At formation month t, rank stocks by `P[t-1] / P[t-12] - 1` using adjusted closes. Require complete monthly history through formation. Hold the top and bottom deciles at $0.50 long and $0.50 short per $1 of equity. Each side contains `floor(N/10)` names, equally weighted, with ticker order breaking ties. At rebalance, gross exposure is 1.0 and net exposure is zero; both can drift afterward.

## Volatility scaling

Estimate annualized volatility from the previous 126 daily baseline strategy returns using `daily standard deviation × sqrt(252)`. Divide the 12% target by this estimate and bound the multiplier to [0.5, 2.0].

Historical strategy returns must use the portfolios held on each historical date. Applying today's winners and losers to earlier prices would introduce look-ahead bias. Scaling starts only after a full estimation window is available, and both strategies will be compared over the same dates.

## Sample split

Use 2005–2015 for development, with earlier prices for warm-up. Evaluate from 2016 through the saved data cutoff. Because these are familiar historical periods, this is a retrospective holdout rather than a prospective test. Any changes prompted by evaluation results will be recorded as exploratory.

## Open decisions

- **Execution:** decide when month-end signals can first be traded and which returns belong to each holding period. Adjusted closing prices alone do not implement next-open execution.
- **Scaling:** confirm monthly updates, standard-deviation convention, and handling of zero or very low volatility.
- **Missing data:** choose a market calendar, minimum universe size, and treatment of missing prices, delistings, and trading suspensions for held stocks.
- **Turnover and costs:** measure dollars traded against drifted holdings, including initial entry, exits, and exposure changes; apply 10 bps per dollar traded.
- **Capital accounting:** settle borrow fees, short proceeds, collateral, cash yield, financing, and leverage treatment.
- **Metrics:** define return annualization, the risk-free series for Sharpe, regression factors and frequency, and uncertainty estimates.
- **Comparisons:** select exact 2009 and 2020 crash windows, risk calibration, and robustness variants before inspecting comparative results.
- **Data review:** save the full universe and review price gaps, coverage, and corporate actions.

## Validation

1. Check a signal by hand using its dates, endpoint prices, selected stocks, and weights.
2. Reconcile a rebalance and a holding day, including execution, drift, costs, and portfolio equity.
3. Confirm that changing future data cannot change earlier signals or positions.
4. Reconcile daily and monthly returns on small examples with known answers.
5. Inspect the 2009 and 2020 histories for implementation errors without tuning to those episodes.
6. Reproduce the analysis from saved inputs and record the code revision and package versions.

Once the open decisions are settled, record approval and the configuration checksum in the decision log.
