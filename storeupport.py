import datetime
import re
import time
import yfinance as yf
import pandas_ta as ta

import requests
from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import schedule
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import crete_update_table
import getoptionchain
import storetoken
import document
import pyotp

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


def fetchdataandreturn_pivot():
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)
    # index
    nifty_index_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_daily, n_bars=3)
    data = nifty_index_data
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
        'p': round(pi, 2),
        's1': round(S1, 2),
        'r1': round(R1, 2),
        's2': round(S2, 2),
        'r2': round(R2, 2),
        'r3': round(R3, 2),
        's3': round(S3, 2)
    }

    global pivot_fibo_level
    pivot_fibo_level = fibonacci_levels
    print(pivot_fibo_level)


def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=100)

        # print(df)
        if df is not None:
            df.ema = ta.ema(df.close, length=9)
            print('ema', df.ema.values[-1])
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
    data = fibo_level
    filter_value = close

    matching_keys = [key for key, value in data.items() if value >= filter_value]
    max_key = min(matching_keys, key=lambda k: data[k], default='p')
    return max_key


def definesupportlevel(fibo_level, close):
    data = fibo_level
    filter_value = close

    matching_keys = [key for key, value in data.items() if value <= filter_value]
    max_key = max(matching_keys, key=lambda k: data[k], default='p')
    return max_key


def stetergytosendalert(script, interwal, data, level, closehigh, closelow):
    df = data
    # print('interval', closehigh,closelow)
    # r_level = defineresistancelevel(pivot_fibo_level, df.close.values[-1])
    # s_level = definesupportlevel(pivot_fibo_level, df.close.values[-1])

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
    if len(data) > 0:
        for a in level:
            ema_greater_than_allsell = (df.ema.values[-1] > df.open.values[-1] and
                                        df.ema.values[-1] > df.close.values[-1] and
                                        df.ema.values[-1] > df.high.values[-1] and
                                        df.ema.values[-1] > df.low.values[-1])
            ema_greater_than_allbuy = (df.ema.values[-1] < df.open.values[-1] and
                                       df.ema.values[-1] < df.close.values[-1] and
                                       df.ema.values[-1] < df.high.values[-1] and
                                       df.ema.values[-1] < df.low.values[-1])
            cetrue = (closehigh < df.close.values[-1]) if closehigh != '' else True
            petrue = (closelow > df.close.values[-1]) if closelow != '' else True
            print('pe true,', petrue, 'ce true,',cetrue)
            # print(a,'print a data',previtemclose)
            if a > df.low.values[-2] and a < df.close.values[-1] and df.Candle_Color.values[
                -1] == 1 and ema_greater_than_allbuy and cetrue:
                if getoptionchain.getparams(symbol, df.close.values[-1], 'ce'):
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
                        crete_update_table.inserttokenns(stickprice, cetoken['exch_seg'], token, lotsize, ltp, '0')
                        bot_message = f'braekout  in {interwal} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
                        sendAlert(bot_message)
            elif a < df.high.values[-2] and a > df.close.values[-1] and df.Candle_Color.values[
                -1] == 0 and ema_greater_than_allsell and petrue:
                if getoptionchain.getparams(symbol, df.close.values[-1], 'pe'):
                    # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                    stickprice = petoken['symbol']
                    lotsize = petoken['lotsize']
                    token = petoken['token']
                    ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
                    fetchdata = crete_update_table.fetchtokennbook()
                    filteristoken = [item for item in fetchdata if
                                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                    if len(filteristoken) == 0:
                        crete_update_table.inserttokenns(stickprice, petoken['exch_seg'], token, lotsize, ltp, '0')
                        bot_message = f'braekout  in {interwal} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
                        sendAlert(bot_message)

            # elif df.low.values[-2] < pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level] and \
            #         df.close.values[-1] > df.ema.values[-1] and cetrue:
            #     if getoptionchain.getparams(symbol, df.close.values[-1], 'ce'):
            #         # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
            #         stickprice = cetoken['symbol']
            #         lotsize = cetoken['lotsize']
            #         token = cetoken['token']
            #         # print('token details :',cetoken['symbol'],stickprice,lotsize)
            #         ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
            #         fetchdata = crete_update_table.fetchtokennbook()
            #         filteristoken = [item for item in fetchdata if
            #                          re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
            #         if len(filteristoken) == 0:
            #             crete_update_table.inserttokenns(stickprice, cetoken['exch_seg'], token, lotsize, ltp, '0')
            #             bot_message = f'braekout  in {s_level} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
            #             sendAlert(bot_message)
            # elif df.high.values[-2] > pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level] and \
            #         df.close.values[-1] < df.ema.values[-1] and petrue:
            #     if getoptionchain.getparams(symbol, df.close.values[-1], 'pe'):
            #         # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
            #         stickprice = petoken['symbol']
            #         lotsize = petoken['lotsize']
            #         token = petoken['token']
            #         ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
            #         fetchdata = crete_update_table.fetchtokennbook()
            #         filteristoken = [item for item in fetchdata if
            #                          re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
            #         if len(filteristoken) == 0:
            #             crete_update_table.inserttokenns(stickprice, petoken['exch_seg'], token, lotsize, ltp, '0')
            #             bot_message = f'braekout  in {r_level} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
            #             sendAlert(bot_message)
        else:
            print('no support zone')

def aggregate_data(df, time_frame):
    resampled_df = df.resample(time_frame).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    })
    return resampled_df

def storesupportlevel():
    print('start stetergy')
    closehigh = ''
    closelow = ''
    for script, token in symbols.items():
        result1, level1, data = fetch_and_process_data(script, Interval.in_1_minute, '100', 20, 20)
        time.sleep(2)
        for interval, key in timeframe_map.items():
            result, level, df = fetch_and_process_data(script, key, '100', 20, 20)

            if result1:
                print('level', level)

                df_5min = aggregate_data(data, '5T').tail(10)
                closehigh = df_5min.high.values[-2]
                closelow = df_5min.low.values[-2]
                # merged_array = level + pivot_fibo_level  # Merging the two arrays
                stetergytosendalert(script, interval, data, level, closehigh, closelow)
                # fetchdta = crete_update_table.fetchsupport()
                # string_result = ' '.join(map(str, level.to_list()))
                # print(len(fetchdta))
                # if len(fetchdta) > 0:
                #     stetergytosendalert(script,interval,df,level)
                #     getid = checktable(interval,script)
                #     if getid is not None:
                #             crete_update_table.updatesupport(getid,string_result)
                #     else:
                #             crete_update_table.createupport(interval,string_result,script)
                #
                # else:
                #     crete_update_table.createupport(interval,string_result,script)

                # print('store data',fetchdta)


# fetch_and_process_data('NIFTY', Interval.in_1_minute, '100', '20', '20')
# fetchdataandreturn_pivot()
storesupportlevel()
schedule.every(1).minutes.do(storesupportlevel)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e