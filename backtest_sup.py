import time
import schedule
import xlwings as xsw
import getoptionchain
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from tvDatafeed import TvDatafeed,Interval

# Replace 'TCS.NS' with the ticker symbol of the Indian stock you're interested in

# Fetch live stock data






def defineresistancelevel(fibo_level,close):
  data = fibo_level
  filter_value = close

  matching_keys = [key for key, value in data.items() if value >= filter_value]
  max_key = min(matching_keys, key=lambda k: data[k], default='p')
  return max_key

def definesupportlevel(fibo_level,close):
  data = fibo_level
  filter_value = close

  matching_keys = [key for key, value in data.items() if value <= filter_value]
  max_key = max(matching_keys, key=lambda k: data[k], default='p')
  return max_key


def fetchdataandreturn_pivot(symbol):
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)
    # index
    nifty_index_data = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_daily, n_bars=3)
    data = nifty_index_data
    if data is not None:
        # print(data['high'].values[-2], data['low'].values[-2], data['close'].values[-2])
        high_price = data['high'].values[-2]
        low_price = data['low'].values[-2]
        close_price = data['close'].values[-2]
        datafile = []
        # print(high_price, low_price, close_price)
        # Calculate Fibonacci Levels
        pi = (high_price + low_price + close_price) / 3
        R1 = pi + (0.382 * (high_price - low_price))
        R2 = pi + (0.6182 * (high_price - low_price))
        R3 = R2 + (R2 - R1)
        S1 = pi - (0.382 * (high_price - low_price))
        S2 = pi - (0.6182 * (high_price - low_price))
        S3 = S2 - (R1 - S1)
        fibonacci_levels = {
            'p': round(pi,2),
            's1': round(S1,2),
            'r1': round(R1,2),
            's2': round(S2,2),
            'r2': round(R2,2),
            'r3': round(R3,2),
            's3': round(S3,2)
        }
        global pivot_fibo_level
        pivot_fibo_level = fibonacci_levels

storedata = []
def orderbook(data):

    data['orderplace'] = 'no order'
    for i in range(1, len(data)):
        r_level = defineresistancelevel(pivot_fibo_level, data.Close.values[i - 1])
        s_level = definesupportlevel(pivot_fibo_level, data.Close.values[i - 2])
        if data['Close'].values[i - 2] < data['sup'].values[i - 2] and data['Close'].values[i - 1] > data['sup'].values[i - 1]:
            data['orderplace'].values[i] = 'buy'
        elif data['Close'].values[i - 2] > data['sup'].values[i - 2] and data['Close'].values[i - 1] < data['sup'].values[i - 1]:
            data['orderplace'].values[i] = 'sell'
        elif data['Close'].values[i - 1] > data['sup'].values[i - 1]  and data['Low'].values[i - 1] <= pivot_fibo_level[s_level] and data['Close'].values[i - 1] > pivot_fibo_level[s_level]:
            data['orderplace'].values[i] = 'buy'
        elif data['Close'].values[i - 1] < data['sup'].values[i - 1]  and data['High'].values[i - 1] >= pivot_fibo_level[r_level] and data['Close'].values[i - 1] < pivot_fibo_level[r_level]:
            data['orderplace'].values[i] = 'sell'

    return data

def placeorder(data):
    ordervalue = []
    for i in range(1, len(data)):
        if data['orderplace'].values[i] == 'buy':
            ordervalue.append({'buyorder':data['Close'].values[i]})
        if data['orderplace'].values[i] == 'sell':
            ordervalue.append({'sellorder':data['Close'].values[i]})
    return ordervalue


def calculate_order_count_and_last_profit(orders):
    buy_count = 0
    sell_count = 0
    last_buy_price = None
    last_sell_price = None
    last_profit = 0

    for order in orders:
        if 'buyorder' in order:
            buy_count += 1
            last_buy_price = order['buyorder']
        elif 'sellorder' in order:
            sell_count += 1
            last_sell_price = order['sellorder']

        if last_buy_price is not None and last_sell_price is not None:
            print(last_sell_price - last_buy_price)
            last_profit += last_sell_price - last_buy_price

    return buy_count, sell_count, last_profit

def storegerateddata():
        try:
            stock_symbol = '^NSEI'
            start_date = '2024-05-22'  # Start date
            end_date = '2024-05-23'
            print(stock_symbol)
            stock_data = yf.Ticker(stock_symbol)
            # Get the latest stock price (Last Traded Price or LTP)
            latest_price = stock_data.history(period='1 min')['Close'][0]
            # df = pd.DataFrame(stock_data.history(period='1d', interval='5m'))
            df = yf.download(stock_symbol, start=start_date, end=end_date, interval='5m')

            # print(df)
            df["sup"] = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=2)['SUPERT_10_2.0']
            # df["ema"] = ta.ema(df["Close"], length=10)
            supertrend = []

            df.dropna(inplace=True)

            # print(df)
            # print(orderbook(df))
            fetchdataandreturn_pivot('NIFTY')

            print(placeorder(orderbook(df)))
            ordertype = placeorder(orderbook(df))
            buy_count, sell_count, last_profit = calculate_order_count_and_last_profit(ordertype)

            print("Buy count:", buy_count)
            print("Sell count:", sell_count)
            print("Last profit:", last_profit)

        except Exception as e:
            print(e)

# def storeexceldata():
#     wb = xsw.Book("angeone.xlsx")
#     st = wb.sheets('nifty')
#     st.range('A1').value = storedata



storegerateddata()
schedule.every(2).minutes.do(storegerateddata)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e