# VIX-Mean-Reversion-Trading-Strategy

This repository implements a mean reversion trading strategy on the VIX (Volatility Index) using Z-score bands. The goal of this strategy is to take advantage of the mean-reverting behavior of the VIX by entering short positions when the VIX is significantly above its moving average and long positions when it is significantly below.

## Key Concepts

1. VIX (Volatility Index): The VIX represents market expectations of volatility. It is known to exhibit mean-reverting behavior, making it suitable for strategies that capitalize on deviations from the average.

2. Z-score: This is a statistical measure that tells us how far a data point is from the mean in terms of standard deviations. We calculate a moving Z-score to identify when the VIX is unusually high or low relative to its recent history.

3. Mean Reversion Strategy: The strategy assumes that VIX will revert to its average after deviating. Thus, we short the VIX when it exceeds a certain threshold above the average (high Z-score) and go long when it falls below a certain threshold (low Z-score).

## Strategy Workflow

### 1. Data Retrieval:

Connect to Interactive Brokers (IBKR) using the ib_insync library.
Fetch hourly VIX data for the past three years using the IBKR API.

### 2. Moving Z-score Calculation:

Calculate the moving average and standard deviation of the VIX over a specified window (200 hours).
Compute the Z-score of the VIX close price based on this moving average and standard deviation.

### 3. Trade Entry and Exit:

Entry:
Short the VIX when the Z-score rises above a specified upper threshold (e.g., 1.5).
Go long on the VIX when the Z-score falls below a specified lower threshold (e.g., -0.6).
Exit:
Exit a trade when the Z-score returns to a neutral range (close to 0).
Alternatively, exit based on take-profit or stop-loss thresholds (e.g., 50% profit or 20% loss on the position).

### 4. Trade Analysis and Export:

Log details of each trade, including entry and exit points, trade duration, profit/loss, and reason for exit.
Export the trade log to an Excel file for further analysis.

### 5. Visualization:

Generate a plot showing the VIX close price, Z-score bands, and markers for long and short entries.
