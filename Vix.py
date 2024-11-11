import nest_asyncio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ib_insync import *

# to allow async functions in Jupyter Notebook
nest_asyncio.apply()

# Parameters
initial_capital = 10000
moving_window = 200  # Moving average window for Z-score in hours
max_position_pct = 0.3
z_score_entry_threshold = 1.5  # entry threshold for wider bands
z_score_exit_threshold = 0.6   # exit threshold for wider bands
take_profit_pct = 0.5  # 50% take-profit threshold
stop_loss_pct = 0.2  # 20% stop-loss threshold

# Connect to IBKR API
ib = IB()
try:
    ib.connect('333.0.0.1', 7496, clientId=##)  
    
    # Verify connection
    if ib.isConnected():
        print("Connected to IBKR API")

        # Define VIX contract
        contract = Index('VIX', 'CBOE')  

        # Request hourly data for the last 3 years
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='3 Y',
            barSizeSetting='1 hour',
            whatToShow='TRADES',
            useRTH=True  # Use regular trading hours only
        )

        # Convert data to DataFrame
        df = util.df(bars)
        df.set_index('date', inplace=True)  
        print("Hourly Close Data Head:")
        print(df.head())  

        # Calculate hourly returns
        vix_data = df[['close']].copy()
        vix_data['returns'] = vix_data['close'].pct_change().dropna()

        # Calculate the moving Z-score of VIX price
        vix_data['moving_avg'] = vix_data['close'].rolling(moving_window).mean()
        vix_data['moving_std'] = vix_data['close'].rolling(moving_window).std()
        vix_data['moving_z_score'] = (vix_data['close'] - vix_data['moving_avg']) / vix_data['moving_std']
        vix_data.dropna(inplace=True)

        # Function to run a backtest on the strategy
        def run_backtest():
            capital = initial_capital
            positions = 0
            entry_date = None
            entry_capital = 0
            entry_price = 0
            capital_history = []
            trade_log = []
            entry_points = []
            exit_points = []

            for i in range(len(vix_data)):
                date = vix_data.index[i]
                z_val = vix_data['moving_z_score'].iloc[i]
                close_price = vix_data['close'].iloc[i]
                max_capital_for_trade = max_position_pct * capital

                if z_val > z_score_entry_threshold and positions == 0:
                    # Enter a short position
                    position_change = -max_capital_for_trade / close_price
                    entry_capital = max_capital_for_trade
                    entry_date = date
                    entry_price = close_price
                    capital += -position_change * vix_data['returns'].iloc[i] * close_price
                    positions = position_change
                    entry_points.append((date, entry_price))
                    trade_log.append({
                        'Entry Date': entry_date,
                        'Trade Type': 'Sell',
                        'Position Size': abs(position_change),
                        'Entry Price': entry_price,
                        'Moving Z-score': z_val  # Add Moving Z-score to the log
                    })

                elif z_val < -z_score_entry_threshold and positions == 0:
                    # Enter a long position
                    position_change = max_capital_for_trade / close_price
                    entry_capital = max_capital_for_trade
                    entry_date = date
                    entry_price = close_price
                    capital += position_change * vix_data['returns'].iloc[i] * close_price
                    positions = position_change
                    entry_points.append((date, entry_price))
                    trade_log.append({
                        'Entry Date': entry_date,
                        'Trade Type': 'Buy',
                        'Position Size': abs(position_change),
                        'Entry Price': entry_price,
                        'Moving Z-score': z_val  # Add Moving Z-score to the log
                    })

                elif abs(z_val) <= z_score_exit_threshold and positions != 0:
                    # Exit based on Z-score returning to neutral range
                    exit_price = close_price
                    profit = positions * (exit_price - entry_price)
                    capital += profit
                    exit_points.append((date, exit_price))
                    trade_log[-1].update({
                        'Exit Date': date,
                        'Exit Price': exit_price,
                        'Profit': profit,
                        'Closing Reason': 'Z-score Exit',
                        'Moving Z-score': z_val  # Update Moving Z-score on exit
                    })
                    positions = 0

                # Stop Loss and Take Profit
                if positions != 0:
                    current_price = close_price
                    trade_profit = positions * (current_price - entry_price)
                    profit_pct = trade_profit / entry_capital

                    # Check for take profit or stop loss
                    if profit_pct >= take_profit_pct:
                        capital += trade_profit
                        exit_points.append((date, current_price))
                        trade_log[-1].update({
                            'Exit Date': date,
                            'Exit Price': current_price,
                            'Profit': trade_profit,
                            'Closing Reason': 'Take Profit',
                            'Moving Z-score': z_val  # Update Moving Z-score on exit
                        })
                        positions = 0
                    elif profit_pct <= -stop_loss_pct:
                        capital += trade_profit
                        exit_points.append((date, current_price))
                        trade_log[-1].update({
                            'Exit Date': date,
                            'Exit Price': current_price,
                            'Profit': trade_profit,
                            'Closing Reason': 'Stop Loss',
                            'Moving Z-score': z_val  # Update Moving Z-score on exit
                        })
                        positions = 0

                capital_history.append(capital)

            # Create a DataFrame from trade_log
            trade_df = pd.DataFrame(trade_log)

            results = {
                'total_return': (capital - initial_capital) / initial_capital * 100,
                'trade_log': trade_df,
                'entry_points': entry_points,
                'exit_points': exit_points
            }

            return results

        # Function to analyze trades and save to Excel
        def analyze_trades(results, strategy_name="Strategy"):
            # Extract the trade log from the results
            trade_log = results['trade_log']

            # Calculate additional stats for each trade
            trade_log['Trade Length (hours)'] = (pd.to_datetime(trade_log['Exit Date']).dt.tz_localize(None) - 
                                                 pd.to_datetime(trade_log['Entry Date']).dt.tz_localize(None)).dt.total_seconds() / 3600
            trade_log['Profit (%)'] = (trade_log['Profit'] / (trade_log['Entry Price'] * trade_log['Position Size'])) * 100

            # Convert datetime columns to timezone-unaware to avoid Excel export issues
            trade_log['Entry Date'] = pd.to_datetime(trade_log['Entry Date']).dt.tz_localize(None)
            trade_log['Exit Date'] = pd.to_datetime(trade_log['Exit Date']).dt.tz_localize(None)

            # Select and rename columns for better readability
            trade_log = trade_log[['Entry Date', 'Exit Date', 'Trade Type', 'Position Size', 
                                   'Entry Price', 'Exit Price', 'Profit', 'Profit (%)', 
                                   'Trade Length (hours)', 'Closing Reason']]
            
            # Export to Excel
            output_filename = f"{strategy_name}_Trade_Stats2.xlsx"
            trade_log.to_excel(output_filename, index=False)
            print(f"Trade statistics have been saved to {output_filename}")

        # Run the strategy and save its trade log to Excel
        strategy_results = run_backtest()
        analyze_trades(strategy_results, strategy_name="Zscore_Only_Strategy")

    else:
        print("Failed to connect to IBKR API.")

finally:
    # Ensure the connection is closed at the end
    ib.disconnect()
    print("Disconnected from IBKR API.")
