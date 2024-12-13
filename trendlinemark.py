import pandas as pd
import numpy as np
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval


def analyze_nifty_data(username, password, symbol='NIFTY', exchange='NSE', interval=Interval.in_5_minute, n_bars=100):
    # Connect to TradingView
    tv = TvDatafeed(username, password)

    # Fetch historical data
    df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
    itemclose = df.close.values[-1]

    # Calculate support and resistance levels
    supports = df[df.low == df.low.rolling(20, center=True).min()].low
    resistances = df[df.high == df.high.rolling(20, center=True).min()].high

    level = pd.concat([supports, resistances])
    level = level[abs(level.diff()) > 20]

    resistancelevel = []
    supportlevel = []
    for a in level:
        if a > itemclose:
            resistancelevel.append(a)
        else:
            supportlevel.append(a)

    if resistancelevel:
        resistance_item = max(resistancelevel, key=lambda x: x if x > itemclose else float('-inf'))
    else:
        resistance_item = None

    if supportlevel:
        support_item = max(supportlevel, key=lambda x: x if x < itemclose else float('-inf'))
    else:
        support_item = None

    print("Resistance Levels:", sorted(resistancelevel, reverse=True))
    print("Support Levels:", sorted(supportlevel, reverse=True))
    print("Nearest Resistance:", resistance_item)
    print("Nearest Support:", support_item)

    # Calculate trend lines
    def calculate_trend_lines(df):
        trend_points_up = df[df.low == df.low.rolling(10, center=True).min()].dropna()
        x_up = (trend_points_up.index - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
        y_up = trend_points_up.low.values

        trend_points_down = df[df.high == df.high.rolling(10, center=True).max()].dropna()
        x_down = (trend_points_down.index - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
        y_down = trend_points_down.high.values

        coefficients_up = np.polyfit(x_up, y_up, 1)
        coefficients_down = np.polyfit(x_down, y_down, 1)

        uptrend_line = np.poly1d(coefficients_up)
        downtrend_line = np.poly1d(coefficients_down)

        return uptrend_line, downtrend_line

    uptrend_line, downtrend_line = calculate_trend_lines(df)

    # Create trend line data
    x_vals = np.linspace((df.index[0] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'),
                         (df.index[-1] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'), 100)
    uptrend_vals = uptrend_line(x_vals)
    downtrend_vals = downtrend_line(x_vals)

    trend_up = pd.Series(uptrend_vals, index=pd.to_datetime(x_vals, unit='s'))
    trend_down = pd.Series(downtrend_vals, index=pd.to_datetime(x_vals, unit='s'))

    # Plot with trend lines
    add_plot = [
        mpf.make_addplot(trend_up, color='blue'),
        mpf.make_addplot(trend_down, color='red')
    ]

    mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', addplot=add_plot)

    print("Uptrend Line:", uptrend_line)
    print("Downtrend Line:", downtrend_line)


# Usage
analyze_nifty_data('YourTradingViewUsername', 'YourTradingViewPassword')
