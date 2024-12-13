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


stockscanner = [
    'RELIANCE',
'TCS',
'ICICIBANK',
'HDFCBANK',
'SBIN',
]

# stockscanner = [
#
#
#         "AARTIIND",
#         "ABB",
#         "ABBOTINDIA",
#         "ABCAPITAL",
#         "ABFRL",
#         "ACC",
#         "ADANIENT",
#         "ADANIPORTS",
#         "ALKEM",
#         "AMBUJACEM",
#         "APOLLOHOSP",
#         "APOLLOTYRE",
#         "ASHOKLEY",
#         "ASIANPAINT",
#         "ASTRAL",
#         "ATUL",
#         "AUBANK",
#         "AUROPHARMA",
#         "AXISBANK",
#         "BAJAJ-AUTO",
#         "BAJAJFINSV",
#         "BAJFINANCE",
#         "BALKRISIND",
#         "BALRAMCHIN",
#         "BANDHANBNK",
#         "BANKBARODA",
#         "BATAINDIA",
#         "BEL",
#         "BERGEPAINT",
#         "BHARATFORG",
#         "BHARTIARTL",
#         "BHEL",
#         "BIOCON",
#         "BOSCHLTD",
#         "BPCL",
#         "BRITANNIA",
#         "BSOFT",
#         "CANBK",
#         "CANFINHOME",
#         "CHAMBLFERT",
#         "CHOLAFIN",
#         "CIPLA",
#         "COALINDIA",
#         "COFORGE",
#         "COLPAL",
#         "CONCOR",
#         "COROMANDEL",
#         "CROMPTON",
#         "CUB",
#         "CUMMINSIND",
#         "DABUR",
#         "DALBHARAT",
#         "DEEPAKNTR",
#         "DIVISLAB",
#         "DIXON",
#         "DLF",
#         "DRREDDY",
#         "EICHERMOT",
#         "ESCORTS",
#         "EXIDEIND",
#         "FEDERALBNK",
#         "GAIL",
#         "GLENMARK",
#         "GMRINFRA",
#         "GNFC",
#         "GODREJCP",
#         "GODREJPROP",
#         "GRANULES",
#         "GRASIM",
#         "GUJGASLTD",
#         "HAL",
#         "HAVELLS",
#         "HCLTECH",
#         "HDFCAMC",
#         "HDFCBANK",
#         "HDFCLIFE",
#         "HEROMOTOCO",
#         "HINDALCO",
#         "HINDCOPPER",
#         "HINDPETRO",
#         "HINDUNILVR",
#         "ICICIBANK",
#         "ICICIGI",
#         "ICICIPRULI",
#         "IDEA",
#         "IDFC",
#         "IDFCFIRSTB",
#         "IEX",
#         "IGL",
#         "INDHOTEL",
#         "INDIACEM",
#         "INDIAMART",
#         "INDIGO",
#         "INDUSINDBK",
#         "INDUSTOWER",
#         "INFY",
#         "IOC",
#         "IPCALAB",
#         "IRCTC",
#         "ITC",
#         "JINDALSTEL",
#         "JKCEMENT",
#         "JSWSTEEL",
#         "JUBLFOOD",
#         "KOTAKBANK",
#         "LALPATHLAB",
#         "LAURUSLABS",
#         "LICHSGFIN",
#         "LT",
#         "LTF",
#         "LTIM",
#         "LTTS",
#         "LUPIN",
#         "M&M",
#         "M&MFIN",
#         "MANAPPURAM",
#         "MARICO",
#         "MARUTI",
#         "MCDOWELL-N",
#         "MCX",
#         "METROPOLIS",
#         "MFSL",
#         "MGL",
#         "MOTHERSON",
#         "MPHASIS",
#         "MRF",
#         "MUTHOOTFIN",
#         "NATIONALUM",
#         "NAUKRI",
#         "NAVINFLUOR",
#         "NESTLEIND",
#         "NMDC",
#         "NTPC",
#         "OBEROIRLTY",
#         "OFSS",
#         "ONGC",
#         "PAGEIND",
#         "PEL",
#         "PERSISTENT",
#         "PETRONET",
#         "PFC",
#         "PIDILITIND",
#         "PIIND",
#         "PNB",
#         "POLYCAB",
#         "POWERGRID",
#         "PVRINOX",
#         "RAMCOCEM",
#         "RBLBANK",
#         "RECLTD",
#         "RELIANCE",
#         "SAIL",
#         "SBICARD",
#         "SBILIFE",
#         "SBIN",
#         "SHREECEM",
#         "SHRIRAMFIN",
#         "SIEMENS",
#         "SRF",
#         "SUNPHARMA",
#         "SUNTV",
#         "SYNGENE",
#         "TATACHEM",
#         "TATACOMM",
#         "TATACONSUM",
#         "TATAMOTORS",
#         "TATAPOWER",
#         "TATASTEEL",
#         "TCS",
#         "TECHM",
#         "TITAN",
#         "TORNTPHARM",
#         "TRENT",
#         "TVSMOTOR",
#         "UBL",
#         "ULTRACEMCO",
#         "UPL",
#         "VEDL",
#         "VOLTAS",
#         "WIPRO",
#         "ZEEL",
#         "ZYDUSLIFE"
#
#
# ]

storedata = []


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

def storegerateddata():
    for i in stockscanner:
        try:
            stock_symbol = i + '.NS'
            print(stock_symbol)
            stock_data = yf.Ticker(stock_symbol)
            # Get the latest stock price (Last Traded Price or LTP)
            latest_price = stock_data.history(period='5 min')['Close'][0]
            df = pd.DataFrame(stock_data.history(period='1d', interval='5m'))
            df["sup"] = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)['SUPERT_10_3.0']
            df["ema"] = ta.ema(df["Close"], length=10)
            df["supertrend"] = np.where(df["Close"] > df['sup'], 'Buy Side', 'Sell Side')

            df.dropna(inplace=True)

            closevalue = df.Close.values[-1]
            Lowvalue = df.Low.values[-2]
            Highvalue = df.High.values[-2]


            if df.sup.values[-2] < df.Close.values[-2] and df.sup.values[-1] > df.Close.values[-1]:
                supertendmove = 'BUY MOVE'
            elif df.sup.values[-2] > df.Close.values[-2] and df.sup.values[-1] < df.Close.values[-1]:
                supertendmove = 'SELL MOVE'
            else:
                supertendmove = 'NO MOVE'

            fetchdataandreturn_pivot(i)

            r_level = defineresistancelevel(pivot_fibo_level, df.Close.values[-1])
            s_level = definesupportlevel(pivot_fibo_level, df.Close.values[-1])
            catchdata = getoptionchain.getparams(i,latest_price,'ce')

            # print('show',r_level,s_level)
            createformat = {
                'symbol': i,
                'price': latest_price,
                'pe_oi':catchdata['pe_oi'],
                'pe_change':catchdata['pe_change'],
                'ce_oi': catchdata['ce_oi'],
                'ce_change': catchdata['ce_change'],
                'Strick price': catchdata['strick'],
                'max oi': catchdata['max oi'],
                'max oi type': catchdata['max oi type'],
                'supertrend': supertendmove,
                'Market Move':  df["supertrend"].values[-1],
                'max oi strick': catchdata['max oi strick'],
                'registance': pivot_fibo_level[r_level],
                'support': pivot_fibo_level[s_level],
                'support_test_buy': df.Close.values[-1] > df.sup.values[-1]  and df.Low.values[-2] <= pivot_fibo_level[s_level] and df.Close.values[-1] > pivot_fibo_level[s_level],
                'registance_test_sell': df.Close.values[-1] < df.sup.values[-1] and df.High.values[-2] >= pivot_fibo_level[r_level] and df.Close.values[-1] < pivot_fibo_level[r_level],

            }
            condition1 = createformat['support_test_buy'] and catchdata['ce_change'] < catchdata['pe_change']
            condition2 = createformat['registance_test_sell'] and catchdata['ce_change'] > catchdata['pe_change']
            createformat['signal'] = 'buy' if condition1 else ('sell' if condition2 else 'no match')
            symbol_index = None
            for index, data in enumerate(storedata):
                if data['symbol'] == i:
                    # Update the existing entry in storedata
                    # data.update(createformat)
                    symbol_index = index
                    break
            if symbol_index is None:
                storedata.append(createformat)
            else:
                # Update the entry at the same index
                storedata[symbol_index] = createformat
            # storedata.append(createformat)
            df = pd.DataFrame(storedata)
            print(storedata)
            wb = xsw.Book("angeone.xlsx")
            st = wb.sheets('nifty')
            st.range('A1').value = df
            # storeexceldata()
            time.sleep(2)
        except Exception as e:
            print(e)

def storeexceldata():
    wb = xsw.Book("angeone.xlsx")
    st = wb.sheets('nifty')
    st.range('A1').value = storedata



storegerateddata()
schedule.every(2).minutes.do(storegerateddata)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e