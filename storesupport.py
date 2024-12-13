import time
import schedule
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import crete_update_table

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

def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=100)
        #print(df)
        if df is not None:
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
            return True, level
            # return df, level, registance_item, support_item,itemclose
        else:
            return False , 'no'
    except Exception as e:
        print('error',e)



# def storesupportlevel():
#     for script,token in symbols.items():
#         for interval,key in timeframe_map.items():
#
#             fetch_and_process_data(script, key, '100', '20', '20')
storedata = []
def storesupportlevel():
    while True:
        success = True
        for script, token in symbols.items():
            for interval, key in timeframe_map.items():
                result,level = fetch_and_process_data(script, key, '100', 20, 20)
                if result:
                    fetchdta = crete_update_table.fetchsupport()
                    for item in fetchdta:
                        if item['timeframe'] == interval and item['symbol'] == script:
                            crete_update_table.deletesupport(item['id'])
                            time.sleep(2)
                            crete_update_table.createupport(result,level,script)
                        else:
                            crete_update_table.createupport(result,level,script)
                    print(fetchdta)
                if not result:
                    success = False
                    break  # Exit the inner loop if fetch_and_process_data fails
            time.sleep(2)
            if not success:
                break  # Exit the outer loop if fetch_and_process_data fails
        if success:
            break  # Exit the while loop if all combinations are processed successfully

# fetch_and_process_data('NIFTY', Interval.in_1_minute, '100', '20', '20')
storesupportlevel()
schedule.every(1).minutes.do(storesupportlevel)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e
