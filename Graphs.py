import matplotlib.pyplot as plt

#  vix_data contains the VIX close prices and the Z-score information
#  strategy_results contains the trade entries and exits

def plot_zscore_bands_and_positions(vix_data, strategy_results):
    # Plot the VIX close price
    plt.figure(figsize=(14, 8))
    plt.plot(vix_data.index, vix_data['close'], label="VIX Close Price", color="blue", linewidth=1)

    # Plot the moving Z-score bands
    z_score_upper_band = vix_data['moving_avg'] + z_score_entry_threshold * vix_data['moving_std']
    z_score_lower_band = vix_data['moving_avg'] - z_score_entry_threshold * vix_data['moving_std']
    plt.plot(vix_data.index, z_score_upper_band, linestyle="--", color="purple", label="Upper Z-score Entry Band")
    plt.plot(vix_data.index, z_score_lower_band, linestyle="--", color="purple", label="Lower Z-score Entry Band")

    # Plot the moving average
    plt.plot(vix_data.index, vix_data['moving_avg'], color="green", linestyle="-", label="Moving Average")

    # Plot entry and exit points from the trade log
    entry_points = strategy_results['entry_points']
    exit_points = strategy_results['exit_points']

    # Plot long (buy) entries
    for entry in entry_points:
        plt.scatter(entry[0], entry[1], color="green", marker="^", s=100, label="Long Entry" if entry_points.index(entry) == 0 else "")
    
    # Plot short (sell) entries
    for exit in exit_points:
        plt.scatter(exit[0], exit[1], color="red", marker="v", s=100, label="Short Entry" if exit_points.index(exit) == 0 else "")

    # Plotting
    plt.title("VIX Close Price with Z-score Bands and Trade Positions")
    plt.xlabel("Date")
    plt.ylabel("VIX Value")
    plt.legend()
    plt.grid(True)
    plt.show()

plot_zscore_bands_and_positions(vix_data, strategy_results)
