import datetime
from datetime import timedelta
import re
import threading
import time

import yfinance as yf
import pandas_ta as ta

import requests
from tabulate import tabulate

from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import schedule
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import crete_update_table
import getoptionchain
import storetoken
import document
import pyotp
import storecandlestickdata
import logging
import mplfinance as mpf

logging.basicConfig(
    filename='optionsorderlog.log',  # Name of the log file
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format in logs
)


api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)

timeframe_map = {
    '1m': Interval.in_1_minute,
    '5m': Interval.in_5_minute,
    '15m': Interval.in_15_minute,
    '30m': Interval.in_30_minute,
}

symbols = {
    "NIFTY": 'NIFTY',
    "BANKNIFTY": 'BANKNIFTY',
}


# def fetchdataandreturn_pivot():
#     username = 'YourTradingViewUsername'
#     password = 'YourTradingViewPassword'
#
#     tv = TvDatafeed(username, password)
#     # index
#     nifty_index_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_daily, n_bars=3)
#     data = nifty_index_data
#     # print(data['high'].values[-2], data['low'].values[-2], data['close'].values[-2])
#     high_price = data['high'].values[-2]
#     low_price = data['low'].values[-2]
#     close_price = data['close'].values[-2]
#     datafile = []
#     # print(high_price, low_price, close_price)
#     # Calculate Fibonacci Levels
#     pi = (high_price + low_price + close_price) / 3
#     R1 = pi + (0.382 * (high_price - low_price))
#     R2 = pi + (0.6182 * (high_price - low_price))
#     R3 = R2 + (R2 - R1)
#     S1 = pi - (0.382 * (high_price - low_price))
#     S2 = pi - (0.6182 * (high_price - low_price))
#     S3 = S2 - (R1 - S1)
#     fibonacci_levels = {
#         'p': round(pi, 2),
#         's1': round(S1, 2),
#         'r1': round(R1, 2),
#         's2': round(S2, 2),
#         'r2': round(R2, 2),
#         'r3': round(R3, 2),
#         's3': round(S3, 2)
#     }
#
#     global pivot_fibo_level
#     pivot_fibo_level = fibonacci_levels
#     print(pivot_fibo_level)


def fetchdataandreturn_pivot():
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)

    # Initialize an array to store the levels for each symbol
    pivot_fibo_levels_array = []

    # Loop through each symbol in the symbols dictionary
    for symbol_name, symbol_code in symbols.items():
        index_data = tv.get_hist(symbol=symbol_code, exchange='NSE', interval=Interval.in_daily, n_bars=3)
        data = index_data

        high_price = data['high'].values[-2]
        low_price = data['low'].values[-2]
        close_price = data['close'].values[-2]

        # Calculate Fibonacci Levels
        pi = (high_price + low_price + close_price) / 3
        R1 = pi + (0.382 * (high_price - low_price))
        R2 = pi + (0.6182 * (high_price - low_price))
        R3 = high_price + 2 * (pi - low_price)
        S1 = pi - (0.382 * (high_price - low_price))
        S2 = pi - (0.6182 * (high_price - low_price))
        S3 = S2 - (R1 - S1)

        fibonacci_levels = {
            'symbol': symbol_name,
            'p': round(pi, 2),
            's1': round(S1, 2),
            'r1': round(R1, 2),
            's2': round(S2, 2),
            'r2': round(R2, 2),
            'r3': round(R3, 2),
            's3': round(S3, 2)
        }

        # Append the levels to the array
        pivot_fibo_levels_array.append(fibonacci_levels)

    # Print or return the array with the Fibonacci levels for each symbol

    global pivot_fibo_level
    pivot_fibo_level = pivot_fibo_levels_array
    print(pivot_fibo_level)
    # return pivot_fibo_levels_array



def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=100)
        df['Supertrend'] = ta.supertrend(df['high'], df['low'], df['close'], length=10,
                          multiplier=2)['SUPERT_10_2.0']

        # Check if the last three Supertrend values are the same
        if df['Supertrend'].values[-3] == df['Supertrend'].values[-2] == \
                df['Supertrend'].values[-1]:
            trend_status = '0'  # All values are the same
        else:
            trend_status = '1'  # Values are different

        # Add the result as a new column (optional)
        df.loc[df.index[-1], 'Trend_Status'] = trend_status
        # print(df)
        if df is not None:
            # df.ema = ta.ema(df.close, length=9)
            # print('ema', df.ema.values[-1])
            resistancelevel = []
            supportlevel = []
            itemclose = df.close.values[-1]

            supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
            resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close

            level = pd.concat([supports, resistances])
            level = level[abs(level.diff()) > level_diff_threshold]

            for a in level:
                if a > itemclose:
                    resistancelevel.append(a)
                else:
                    supportlevel.append(a)

            # Handle empty lists
            if resistancelevel:
                registance_item = max(resistancelevel, key=lambda x: x if x > itemclose else float('-inf'))
            else:
                registance_item = None

            if supportlevel:
                support_item = max(supportlevel, key=lambda x: x if x < itemclose else float('-inf'))
            else:
                support_item = None
            return True, level, df
            # return df, level, registance_item, support_item,itemclose
        else:
            return False, 'no', df
    except Exception as e:
        print('error', e)


# def storesupportlevel():
#     for script,token in symbols.items():
#         for interval,key in timeframe_map.items():
#
#             fetch_and_process_data(script, key, '100', '20', '20')
storedata = []


# def checktable(timeframe,symbol):
#     fetchdta = crete_update_table.fetchsupport()
#     for person in fetchdta:
#         if person["timeframe"] == timeframe and person["symbol"] == symbol:
#             return person["id"]
#     return None


def sendAlert(bot_message):
    get_message = format(bot_message)
    print(get_message)

    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"
    send_message = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatid + \
                   "&parse_mode=MarkdownV2&text=" + bot_message

    # response = requests.get(send_message)
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                             data={'chat_id': bot_chatid, 'text': bot_message})

    print(response)
    return response.json()


def defineresistancelevel(fibo_level, close):
    # Filter out any string values from the fibo_level dictionary
    filtered_data = {key: value for key, value in fibo_level.items() if isinstance(value, (int, float))}

    # Find keys where the value is greater than or equal to the close value
    matching_keys = [key for key, value in filtered_data.items() if value >= close]

    # Get the key corresponding to the smallest value among the matching keys
    max_key = min(matching_keys, key=lambda k: filtered_data[k], default='p')

    return max_key

def definesupportlevel(fibo_level, close):
    # Filter out any string values from the fibo_level dictionary
    filtered_data = {key: value for key, value in fibo_level.items() if isinstance(value, (int, float))}

    # Find keys where the value is less than or equal to the close value
    matching_keys = [key for key, value in filtered_data.items() if value <= close]

    # Get the key corresponding to the largest value among the matching keys
    max_key = max(matching_keys, key=lambda k: filtered_data[k], default='p')

    return max_key

def find_pe_or_ce(text):
    results = ''
    if 'PE' in text:
        results = 'pe'
    if 'CE' in text:
        results = 'ce'
    return results

def placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose):
    lotsize = int(lotsize)
    print(lotsize)
    logging.info(f"enter in sell {symbol},{stickprice},{token},{lotsize},{ltp},{interwal},{itemclose} ")
    checktype = find_pe_or_ce(stickprice)
    logging.info(f"order type {checktype} ")
    strickprice = itemclose + 1000 if checktype == 'ce' else itemclose - 1000 if checktype == 'pe' else 0
    logging.info(f"strick ptice type {strickprice}")
    cetoken, petoken = storetoken.placeorderdetails('NFO', 'OPTIDX', symbol, strickprice)
    fetchdata = crete_update_table.fetchtokennbook()
    filteristoken = [item for item in fetchdata if re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] < 0]
    logging.info(f"alredy order place or not {filteristoken}")
    if len(filteristoken) == 0:
                logging.info(f"enter bracket order")
                forltp = cetoken if checktype == 'ce' else petoken if checktype == 'pe' else 0
                ltpbuy = obj.ltpData(forltp['exch_seg'], forltp['symbol'], forltp['token'])['data']['ltp']
                logging.info(f"lpt for headage buy order: {ltpbuy}")
                lotsize -= (int(lotsize) + int(lotsize))
                print(lotsize)
                # lotsize = -25
                logging.info(f"sell place order lotsize : {lotsize}")
                # crete_update_table.inserttokenns(petoken['symbo23l'], petoken['exch_seg'], petoken['token'], petoken['lotsize'], ltpbuy, token) if checktype == 'pe' else crete_update_table.inserttokenns(cetoken['symbol'], cetoken['exch_seg'], cetoken['token'], cetoken['lotsize'], ltpbuy, token) if checktype == 'ce' else 'no order'
                # logging.info(f"place buy order {checktype}")
                #
                # crete_update_table.inserttokenns(stickprice, petoken['exch_seg'], token, lotsize, ltp, '0')
                # logging.info(f"place sell order {stickprice}")
                #
                # bot_message = f'braekout  in {interwal} timeframe status:sell for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
                # sendAlert(bot_message)
def stoplossarea(df,ltp,ordertype):
    target = ltp * 1.10
    stoploss = df.low.values[-2] if storedata == 1 else df.high.close[-2]
    change = df.high.values[-2] - df.low.values[-2]

# def getPremiumData(exchange, maintoken,stickprice):
#     logging.info(f"enter in premium data stuctutre{maintoken} exchange {exchange}")
#     current_date_time = datetime.datetime.now()
#     form_date = current_date_time - timedelta(days=3)
#     api_key = document.api_key
#     user_id = document.user_id
#     password = document.password
#     totp = pyotp.TOTP(document.totp).now()
#
#     obj = SmartConnect(api_key=api_key)
#     token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
#     jwtToken = token['data']["jwtToken"]
#     refreshToken = token['data']['refreshToken']
#     feedToken = token['data']['feedToken']
#     print(feedToken)
#     try:
#
#         historicParam = {
#             "exchange": exchange,
#             "symboltoken": maintoken,
#             "interval": "ONE_MINUTE",
#             "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
#             "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
#         }
#         hist_data = obj.getCandleData(historicParam)["data"]
#         df = pd.DataFrame(hist_data,columns=['date', 'open', 'high', 'low', 'close', 'volume'])
#         logging.info(f'get premuim data succesfully')
#         df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
#         df["ema"] = ta.ema(df["close"], length=9)
#         df.dropna(inplace=True)
#         resistancelevel = []
#         supportlevel = []
#         itemclose = df.close.values[-1]
#         logging.info(f"premium data created")
#         supports = df[df.low == df.low.rolling(10, center=True).min()].close
#         resistances = df[df.high == df.high.rolling(10, center=True).max()].close
#
#         level = pd.concat([supports, resistances])
#         level = level[abs(level.diff()) > 10]
#         title = f"{stickprice} + 1m"
#         logging.info('all level created with timeframe 1m')
#         mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart2.png')
#         sendImgAlert("Here is an image:", "static/chart2.png")
#         logging.info(f"create chart successfully for premium.")
#         return level,df
#     except Exception as e:
#         bot_message = f"Historic API failed: {e}"
#         sendAlert(bot_message)

def getPremiumData(exchange, maintoken,stickprice):
    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=3)
    print(current_date_time,form_date)
    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()

    obj = SmartConnect(api_key=api_key)
    token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
    jwtToken = token['data']["jwtToken"]
    refreshToken = token['data']['refreshToken']
    feedToken = token['data']['feedToken']
    print(feedToken)
    try:

        historicParam = {
            "exchange": exchange,
            "symboltoken": maintoken,
            "interval": "ONE_MINUTE",
            "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
            "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
        }
        hist_data = obj.getCandleData(historicParam)["data"]
        storedata = hist_data[:100]
        df = pd.DataFrame(storedata,columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
        df["ema"] = ta.ema(df["close"], length=9)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        resistancelevel = []
        supportlevel = []
        itemclose = df.close.values[-1]
        supports = df[df.low == df.low.rolling(10, center=True).min()].close
        resistances = df[df.high == df.high.rolling(10, center=True).max()].close

        level = pd.concat([supports, resistances])
        level = level[abs(level.diff()) > 10]

        title = f"{stickprice} - 1m"
        logging.info('all level created with timeframe 1m')
        try:
            ltp= 200.00
            resistance = min([x for x in level if x > ltp], key=lambda x: abs(x - ltp), default=None)
            support = min([x for x in level if x < ltp], key=lambda x: abs(x - ltp), default=None)
            target = resistance if (resistance is not None and resistance < (ltp * 1.10)) else (ltp * 1.10)
            stoploss = support if (support is not None and support > (ltp * 0.95)) else (ltp * 0.95)
            # condition = df.close.values[-1] > df.ema.values[-1]
            print(target,stoploss,support,resistance)
            mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart.png')
            sendImgAlert("Here is an image:", "static/chart.png")
        except Exception as e:
            print(e)
            sendAlert(f"{e}")
        print('done')
        logging.info(f"create chart successfully for premium.")

        return level,df

    except Exception as e:
        bot_message = f"Historic API failed: {e}"
        # sendAlert(bot_message)


def placebuyorder(symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,level,df):
    bot_message = f'enter in place order {stickprice} {exc} {token}'
    sendAlert(bot_message)
    logging.info(f"enter in place buy order order : {stickprice},{exc},{token},{lotsize},{ltp},{interval},{itemclose} ")
    checkprice = 10 if symbol == 'NIFTY' else 20 if symbol == 'BANKNIFTY' else 20
    targetchange = (ltp * 1.10) - ltp
    delta = 0
    #ordertype = 1 if 'CE' in stickprice else 0
    level,premiumdf = getPremiumData(exc,token,stickprice)
    try:
        resistance = min([x for x in level if x > ltp], key=lambda x: abs(x - ltp), default=None)
        support = min([x for x in level if x < ltp], key=lambda x: abs(x - ltp), default=None)
        target = resistance if (resistance is not None and resistance < (ltp * 1.10)) else (ltp * 1.10)
        stoploss = support if (support is not None and support > (ltp * 0.95)) else (ltp * 0.95)

        condition = premiumdf.close.values[-1] > premiumdf.ema.values[-1]
        if condition:
        # if True:
            stickprice = f"{stickprice} - {target} - {stoploss}"
            # crete_update_table.insert_place_order(symbol,exc,token,delta,itemclose,ltp,target,stoploss,lotsize,'0')
            crete_update_table.inserttokenns(stickprice, exc, token, lotsize, ltp, '0')
            bot_message = f'braekout  in {interval} level: {level} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
            sendAlert(bot_message)
            logging.info(f"buy order place successfully for symbol {stickprice}" )

        else:
            data = {
                'targetchange': targetchange,
                'totaltarget': targetchange * lotsize,
                'buyprice': ltp,
                'symbol': symbol,
                'stickprice': stickprice
            }
            logging.info(f"not placing order for symbol {data}" )
            bot_message = f'This order in not fit for good profit target is {data} '
            sendAlert(bot_message)
    except Exception as e:
        bot_message = f"Historic API failed: {e}"
        sendAlert(bot_message)


def sendImgAlert(bot_message, image_path=None):
    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"

    if image_path:
        # Send image
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        with open(image_path, 'rb') as photo:
            response = requests.post(url, data={'chat_id': bot_chatid}, files={'photo': photo})
    else:
        # Send text message
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        response = requests.post(url, data={'chat_id': bot_chatid, 'text': bot_message, 'parse_mode': 'MarkdownV2'})

    print(response)
    return response.json()

def stetergytosendalert(script, interwal, data, level, closehigh, closelow,tdf):
    df = data
    sup = df['Trend_Status'].values[-1]

    itemclose = data.close.values[-1]
    symbol = script
    # getdata = crete_update_table.fetchsupport()
    cetoken, petoken = storetoken.placeorderdetails('NFO', 'OPTIDX', symbol, df.close.values[-1])
    df['Candle_Color'] = 1  # Initialize with a value indicating green candles
    df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
    print(cetoken['symbol'], petoken['symbol'])
    logging.info(f"sup is 0 then side ways market - sup value: {sup}")
    if len(data) > 0 and sup == '1':

        # Start a new thread for plotting
        data = storecandlestickdata.createchart(script,interwal,df,level)


        print(data)
        cetrue = (closehigh < df.close.values[-1]) if closehigh != '' else True
        petrue = (closelow > df.close.values[-1]) if closelow != '' else True
        logging.info(f"symbol {script} - interval {interwal} - pe {petrue} - ce {cetrue} - timeframe {tdf}")
        for a in level:
            # print(a,'print a data',previtemclose)
            if a > df.low.values[-2] and a < df.close.values[-1] and df.Candle_Color.values[-1] == 1 and cetrue:
                logging.info(f"first level check for call : a > df.low.values[-2] and a < df.close.values[-1] and df.Candle_Color.values[ -1] == 1 and cetrue{cetrue} ")
                if getoptionchain.getparams(symbol, df.close.values[-1], 'ce'):
                    logging.info(f"option chain : True ")
                    # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                    stickprice = cetoken['symbol']
                    lotsize = cetoken['lotsize']
                    token = cetoken['token']
                    # print('token details :',cetoken['symbol'],stickprice,lotsize)
                    ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
                    fetchdata = crete_update_table.fetchtokennbook()
                    filteristoken = [item for item in fetchdata if
                                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                    if len(filteristoken) == 0:
                        logging.info(f"place order : True ")
                        placebuyorder(symbol,stickprice, cetoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,a,df)
                        title = f"{symbol} - {interwal}"
                        mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart.png')
                        sendImgAlert("Here is an image:", "static/chart.png")
                    placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)

            elif a < df.high.values[-2] and a > df.close.values[-1] and df.Candle_Color.values[-1] == 0 and petrue:
                logging.info(f"second level check for put : a < df.high.values[-2] and a > df.close.values[-1] and df.Candle_Color.values[-1] == 0 and petrue{petrue}")

                if getoptionchain.getparams(symbol, df.close.values[-1], 'pe'):
                    logging.info(f"level 2 : option chain : True ")
                    # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                    stickprice = petoken['symbol']
                    lotsize = petoken['lotsize']
                    token = petoken['token']
                    ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
                    fetchdata = crete_update_table.fetchtokennbook()
                    filteristoken = [item for item in fetchdata if
                                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                    if len(filteristoken) == 0:
                        logging.info(f"level 2 : place order : True ")
                        placebuyorder(symbol,stickprice, petoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,a,df)
                        title = f"{symbol} - {interwal}"
                        mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart.png')
                        sendImgAlert("Here is an image:", "static/chart.png")
                    placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)


        else:
            print('no support zone')
            logging.info(f"no biying level for {script} for interval {interwal}")
    else:
        print(f'data length : {len(data)} or may be side ways market sup value : {sup}')


def pivotpointstatergy(script, interwal, data, level, closehigh, closelow,tdf):
    logging.info(f"interval {interwal} enter in pivot level")
    df = data
    deflevel = [item for item in pivot_fibo_level if item['symbol'] == script]
    sup = df['Trend_Status'].values[-1]
    print('pivot levels',deflevel[0])
    pivotlevel = deflevel[0]
    r_level = defineresistancelevel(pivotlevel, df.close.values[-1])
    s_level = definesupportlevel(pivotlevel, df.close.values[-1])
    print(r_level,s_level,pivotlevel[r_level],pivotlevel[s_level])
    itemlow = data.low.values[-1]
    itemhigh = data.high.values[-1]

    preitemlow = data.low.values[-2]
    preitemhigh = data.high.values[-2]

    itemclose = data.close.values[-1]
    symbol = script
    # getdata = crete_update_table.fetchsupport()
    cetoken, petoken = storetoken.placeorderdetails('NFO', 'OPTIDX', symbol, df.close.values[-1])
    df['Candle_Color'] = 1  # Initialize with a value indicating green candles
    df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
    print(cetoken['symbol'], petoken['symbol'])
    logging.info(f"sup is 0 then side ways market - sup value: {sup}")
    if len(data) > 0 and sup == '1':
        cetrue = (closehigh < df.close.values[-1]) if closehigh != '' else True
        petrue = (closelow > df.close.values[-1]) if closelow != '' else True
        logging.info(f"symbol {script} - interval {interwal} - pe {petrue} - ce {cetrue} - timeframe {tdf}")

        if df.low.values[-2] < pivotlevel[s_level] and df.close.values[-1] > pivotlevel[s_level] and df.Candle_Color.values[-1] == 1 and cetrue:
            logging.info(f"third level for pivot point : df.low.values[-2] < pivotlevel[s_level] and df.close.values[-1] > pivotlevel[s_level] and cetrue{cetrue}")
            if getoptionchain.getparams(symbol, df.close.values[-1], 'ce'):
                logging.info(f"level 3 : option chain : True ")
                # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                stickprice = cetoken['symbol']
                lotsize = cetoken['lotsize']
                token = cetoken['token']
                # print('token details :',cetoken['symbol'],stickprice,lotsize)
                ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
                fetchdata = crete_update_table.fetchtokennbook()
                filteristoken = [item for item in fetchdata if
                                 re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                if len(filteristoken) == 0:
                    logging.info(f"level 3 : place order : True ")
                    placebuyorder(symbol,stickprice, cetoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,s_level,df)

                placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)

        elif df.high.values[-2] > pivotlevel[r_level] and df.close.values[-1] < pivotlevel[r_level] and df.Candle_Color.values[-1] == 0 and petrue:
            logging.info(f"fourth level for pivot point : df.high.values[-2] > pivotlevel[r_level] and df.close.values[-1] < pivotlevel[r_level] and petrue {petrue}")
            if getoptionchain.getparams(symbol, df.close.values[-1], 'pe'):
                logging.info(f"level 4 : option chain : True ")
                # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                stickprice = petoken['symbol']
                lotsize = petoken['lotsize']
                token = petoken['token']
                ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
                fetchdata = crete_update_table.fetchtokennbook()
                filteristoken = [item for item in fetchdata if
                                 re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                if len(filteristoken) == 0:
                    logging.info(f"level 4 : place order : True ")
                    placebuyorder(symbol,stickprice, petoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,s_level,df)

                placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)


    else:
        print('no support zone')
        logging.info(f"no biying level for {script} for interval {interwal}")



def aggregate_data(df, time_frame):
    resampled_df = df.resample(time_frame).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    })
    return resampled_df

# def storesupportlevel():
#     print('start stetergy')
#     closehigh = ''
#     closelow = ''
#     for script, token in symbols.items():
#         result1, level1, data = fetch_and_process_data(script, Interval.in_1_minute, '100', 20, 20)
#         print('success',result1)
#         # time.sleep(2)
#         for interval, key in timeframe_map.items():
#             result, level, df = fetch_and_process_data(script, key, '100', 20, 20)
#
#             if result1:
#                 print('level', level)
#
#                 df_5min = aggregate_data(data, '5T').tail(10)
#                 closehigh = df_5min.high.values[-2]
#                 closelow = df_5min.low.values[-2]
#                 change = closehigh - closelow
#                 if change > 20 and script == 'NIFTY' or change > 40 and script == 'BANKNIFTY':
#                     # merged_array = level + pivot_fibo_level  # Merging the two arrays
#                     stetergytosendalert(script, interval, data, level, closehigh, closelow)
#                 else:
#                     df_15min = aggregate_data(data, '15T').tail(10)
#                     closehigh = df_15min.high.values[-2]
#                     closelow = df_15min.low.values[-2]
#                     change = closehigh - closelow
#                     if change > 20 and script == 'NIFTY' or change > 40 and script == 'BANKNIFTY':
#                             stetergytosendalert(script, interval, data, level, closehigh, closelow)
#
#                     else:
#                         print('Side Ways Market')
#
#                 # fetchdta = crete_update_table.fetchsupport()
#                 # string_result = ' '.join(map(str, level.to_list()))
#                 # print(len(fetchdta))
#                 # if len(fetchdta) > 0:
#                 #     stetergytosendalert(script,interval,df,level)
#                 #     getid = checktable(interval,script)
#                 #     if getid is not None:
#                 #             crete_update_table.updatesupport(getid,string_result)
#                 #     else:
#                 #             crete_update_table.createupport(interval,string_result,script)
#                 #
#                 # else:
#                 #     crete_update_table.createupport(interval,string_result,script)
#
#                 # print('store data',fetchdta)
def storesupportlevel():
    try:
        print('start strategy')
        closehigh = ''
        closelow = ''
        for script, token in symbols.items():
            try:
                result1, level1, data = fetch_and_process_data(script, Interval.in_1_minute, '100', 20, 20)

                for interval, key in timeframe_map.items():
                    try:
                        result, level, df = fetch_and_process_data(script, key, '100', 20, 20)

                        if result1:
                            print('level', level)
                            df_5min = aggregate_data(data, '5T').tail(10)
                            closehigh = df_5min.high.values[-2]
                            closelow = df_5min.low.values[-2]
                            change = closehigh - closelow
                            if (change >= 20 and script == 'NIFTY') or (change >= 40 and script == 'BANKNIFTY'):
                                # merged_array = level + pivot_fibo_level  # Merging the two arrays
                                stetergytosendalert(script, interval, data, level, closehigh, closelow,'df_5min')
                                if interval == '5m':
                                    pivotpointstatergy(script, interval, data, level, closehigh, closelow,'df_5min')
                            else:
                                df_15min = aggregate_data(data, '15T').tail(10)
                                closehigh = df_15min.high.values[-2]
                                closelow = df_15min.low.values[-2]
                                change = closehigh - closelow
                                if (change > 20 and script == 'NIFTY') or (change > 40 and script == 'BANKNIFTY'):
                                    stetergytosendalert(script, interval, data, level, closehigh, closelow,'df_15min')
                                    if interval == '5m':
                                        pivotpointstatergy(script, interval, data, level, closehigh, closelow,'df_15min')
                                else:
                                    print('Side Ways Market')

                    except Exception as e:
                        print(f"Error processing data for script {script} and interval {interval}: {e}")
                        storesupportlevel()
            except Exception as e:
                print(f"Error fetching data for script {script}: {e}")
                storesupportlevel()

    except Exception as e:
        print(f"General error in storesupportlevel: {e}")
        storesupportlevel()

# Ensure that all required functions and variables are defined:
# symbols, fetch_and_process_data, Interval, timeframe_map, aggregate_data, stetergytosendalert
# Also ensure that you have proper error handling for other functions if they might raise exceptions.


# fetch_and_process_data('NIFTY', Interval.in_1_minute, '100', '20', '20')

fetchdataandreturn_pivot()
# storesupportlevel()
getPremiumData('NFO','43900','nifty')
schedule.every(1).minutes.do(storesupportlevel)
# placeoptionsellorder('BANKNIFTY','BANKNIFTY04SEP2451400CE',49076,'25',223,'1m',51410)



while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e
