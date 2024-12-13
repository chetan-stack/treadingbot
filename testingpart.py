from tvDatafeed import TvDatafeed, Interval
import pandas as pd

# Credentials for TradingView
username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)

# Fetch historical data for Nifty index
nifty_index_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_1_minute, n_bars=100000)

df = pd.DataFrame(nifty_index_data,columns=['date', 'open', 'high', 'low', 'close','volume'])

df['date'] = pd.to_datetime(df['date'])


df['time_diff'] = df['date'].diff()

print(df.head())


                # logging.info(f"sell place order lotsize : {lotsize}")
                # crete_update_table.inserttokenns(petoken['symbo23l'], petoken['exch_seg'], petoken['token'], petoken['lotsize'], ltpbuy, token) if checktype == 'pe' else crete_update_table.inserttokenns(cetoken['symbol'], cetoken['exch_seg'], cetoken['token'], cetoken['lotsize'], ltpbuy, token) if checktype == 'ce' else 'no order'
                # logging.info(f"place buy order {checktype}")
                #
                # crete_update_table.inserttokenns(stickprice, petoken['exch_seg'], token, lotsize, ltp, '0')
                # logging.info(f"place sell order {stickprice}")
                #
                # bot_message = f'braekout  in {interwal} timeframe status:sell for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
                # sendAlert(bot_message)
