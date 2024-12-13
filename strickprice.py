from datetime import datetime

import requests
import pandas as pd


def initialisedTockenMap():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    global token_df
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': float})
    print('check', token_df)
    # placeorderdetails()


def placeorderdetails():
    tokeninfo = getTokenInfo('NSE', 'OPTIDX', 'NIFTY', '', '').iloc[0]['token']
    print(tokeninfo, "---token")
    global LTP
    LTP = obj.ltpData('NSE', 'NIFTY', tokeninfo)['data']['ltp']
    RTM = int(round(LTP / 100) * 100)  # to get check acurate price
    print(LTP, RTM)
    ## now check price and place order details
    # print(getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'CE').iloc[0])

    ce_symbol_data = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'CE').iloc[0]
    pe_symbol_data = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'PE').iloc[0]

    ce_symbol['token'] = ce_symbol_data['token']
    ce_symbol['symbol'] = ce_symbol_data['symbol']
    ce_symbol['lotsize'] = ce_symbol_data['lotsize']

    pe_symbol['token'] = pe_symbol_data['token']
    pe_symbol['symbol'] = pe_symbol_data['symbol']
    pe_symbol['lotsize'] = pe_symbol_data['lotsize']

def getTokenInfo(exch_seg, instrumenttype, symbol, strike_price, pe_ce, expiry_day=None):
    df = token_df
    strike_price = strike_price * 100
    if exch_seg == 'NSE':
        # print('nse')
        eq_df = df[(df['exch_seg'] == 'NSE')]
        # print(eq_df[(eq_df['name'] == 'NIFTY')],'---####---')
        return eq_df[(eq_df['name'] == 'NIFTY')]
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        print('nfo')
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (
        (df['strike'] == strike_price)) & (df['symbol'].str.endswith(pe_ce)) & (
                              df['expiry'] >= str(datetime.date.today()))].sort_values(by=['expiry'])


initialisedTockenMap()