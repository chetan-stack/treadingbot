from datetime import datetime
import requests
import pandas as pd
import xlwings as xsw

def getparams(symbol,target,type):
    print('option chain check with price : ',target, 'order type : ',type)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8'
     }


    session = requests.session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    print(cookies)
    response = session.get(url,headers=headers,cookies=cookies).json()['filtered']['data']
    rawdata = pd.DataFrame(response)
    print(rawdata)
    docdata = []
    for i in response:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info = k
                info['instrumenet Type'] = j
                docdata.append(info)
    df = pd.DataFrame(docdata)
        # wb = xsw.Book("angle_excel.xlsx")
        # st = wb.sheets('nifty')
        # st.range('A1').value = df
    target = int(target)
    today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
    # print(df)
    closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
    unique_strike_prices = sorted(df['strikePrice'].unique())

    # Find the index of the closest strike price in the unique strike prices list
    closest_index = unique_strike_prices.index(closest_strike_price)

    # Find the strike prices before and after the closest one
    previous_strike_price = unique_strike_prices[closest_index - 1] if closest_index > 0 else None
    next_strike_price = unique_strike_prices[closest_index + 1] if closest_index < len(
        unique_strike_prices) - 1 else None

    print("Closest strike price:", closest_strike_price)
    print("Strike price before:", previous_strike_price)
    print("Strike price after:", next_strike_price)
    setdf = df[(df['strikePrice'] == closest_strike_price)]
    minsetdf = df[(df['strikePrice'] == previous_strike_price)]
    maxset = df[(df['strikePrice'] == next_strike_price)]
    # print(setdf,minsetdf,maxset)
    print('strick price',setdf[setdf['instrumenet Type'] == 'PE']['strikePrice'].values[-1],'---',setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1], '--', setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1], '----',
      setdf['expiryDate'].values[-1], 'PE', '----', setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
      '--', setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1], '----', setdf['expiryDate'].values[0],
      'CE')

    if type == 'ce' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    elif type == 'pe' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    else:
         return False


def placeorderwhenconfermation(symbol,target,type):
    print('option chain check with price : ',target, 'order type : ',type)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8'
     }


    session = requests.session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    print(cookies)
    response = session.get(url,headers=headers,cookies=cookies).json()['filtered']['data']
    rawdata = pd.DataFrame(response)
    print(rawdata)
    docdata = []
    for i in response:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info = k
                info['instrumenet Type'] = j
                docdata.append(info)
    df = pd.DataFrame(docdata)
        # wb = xsw.Book("angle_excel.xlsx")
        # st = wb.sheets('nifty')
        # st.range('A1').value = df
    target = int(target)
    today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
    # print(df)
    closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
    unique_strike_prices = sorted(df['strikePrice'].unique())

    # Find the index of the closest strike price in the unique strike prices list
    closest_index = unique_strike_prices.index(closest_strike_price)

    # Find the strike prices before and after the closest one
    previous_strike_price = unique_strike_prices[closest_index - 1] if closest_index > 0 else None
    next_strike_price = unique_strike_prices[closest_index + 1] if closest_index < len(
        unique_strike_prices) - 1 else None

    print("Closest strike price:", closest_strike_price)
    print("Strike price before:", previous_strike_price)
    print("Strike price after:", next_strike_price)
    setdf = df[(df['strikePrice'] == closest_strike_price)]
    minsetdf = df[(df['strikePrice'] == previous_strike_price)]
    maxset = df[(df['strikePrice'] == next_strike_price)]
    # print(setdf,minsetdf,maxset)
    print('strick price',setdf[setdf['instrumenet Type'] == 'PE']['strikePrice'].values[-1],'---',setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1], '--', setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1], '----',
      setdf['expiryDate'].values[-1], 'PE', '----', setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
      '--', setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1], '----', setdf['expiryDate'].values[0],
      'CE')
    print(int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) , int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]) , int(maxset[maxset['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) , int(maxset[maxset['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]))
    if int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]) and int(maxset[maxset['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(maxset[maxset['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return 'ce'
    elif int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]) and int(minsetdf[minsetdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(minsetdf[minsetdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return 'pe'
    else:
         return 'no order'


def exitorder(symbol,target,type):
    print('option chain check with price : ',target, 'order type : ',type)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8',
        'Cookie': '_ga=GA1.1.1264432697.1673939756; _ga_QJZ4447QD3=GS1.1.1717392523.55.0.1717392523.0.0.0; defaultLang=en; AKA_A2=A; _abck=6485F05FA55DEFC3F98E9E0C0673542E~0~YAAQMyEPF3FEjOuSAQAAhGQOLwyyCFxHDH/omkxt5akR5fRB7EGaAbQat+czFP81VXUtxyaqSrrQgkQLdDEwf6Gog/1tW8Yt+OacSXA0Ayx/Glb/1o2PJhMx6V+tbcqDYMFQh31nygTdpYrG3DdGB6yrJsCVQGYQMfyTVLLIQdUVPEo0v5LFdGCRciau0GxrIEPbDPyL8e/PEjwJdXpRixJFfP9wl+FtgnfstXkj6cmoXniI0uqfOtnZYeBpZN4kMjLX90pU83gkkbmP5tiCplevfN2FGDK7QXxRQe+rzOPkIT7CvgbIulQHzqf0nD7CWroefF7RWkgjZJOGT2Bbs7RXvQVxJWitM45XIZmlbqcMD85enXcLYV+po0Wx/VtYqKKrUCifTbGpjFRPL2TOBZnqKTGl3yvc62M=~-1~-1~-1; ak_bmsc=84975F772EC2509A20990977AA57269A~000000000000000000000000000000~YAAQMyEPF+1EjOuSAQAA62sOLxmJdU7I27sP/mXQx7lxrkfV7d5Dmj/VQNPwriQbs2pjdq3W+nRgo6VG2CknK/5HmtsY3PnTn7Cb9aRyMXtq2B+t1LsGZlmz2N3rkXoabwX42GdtNXm9ILcoDSh3S3ObsGeAbIxYtk5lk4MPGdTWOUTx4Tyiw+wsQ3rUIr58bZ5ukiQVRFZnx5SAXg9uyWdlUN+OnGkjBotS5z/uwzv3XCcwMNzXynKLEoR5b/BfSyv8Xj4eZ/bM2mOaO3TtMfkF6Fqvtq/ZlcZu3L6O6Pvr3frDcLe1X2oUEulCJua7vD2UIEhX9sibrMuHvwBp7rGd4dMUAas4GV4L8sJomJz5k/I4Ckim8TUKLvvGAyiFUEzuuqVGdhaOCF490G6fSQhcRZaXt2J5ZaC0uMgq7brLb4+aoB+vwUiNkBFH5dRfREiQAesxfig/81OgKQ==; nsit=OfICSOo3W8pVSBMb26LWtdkD; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTczMTY2Mjg3NCwiZXhwIjoxNzMxNjcwMDc0fQ.9VYX8S7j-1AcviXqFV6QEwiNiQAoyOoSXkrB-CMbyo8; bm_sz=F167D39231F7F04A52361AED8CD949B5~YAAQNCEPF8hVDwKTAQAAj4cmLxkbd8c7+xwtOGonh34NmmT3eEB/UUcIysDuYUIAtZnCkmg2X1j6tcqw58Kg+Cp/oUQXGGyXmvHHQ2Yn/4iCDgN8NLWLjTMmnd9GmQ/9AR36eJKrYhwcKvpYhGY9wm/1wL7LJbXhkW+4ag/5WhwlGcUWlG8Xu+yffLR99T28QvXxBoyBupQEhlS9/BllQe5Nq5bgvntYhkPRsNGheak8CWro0H5fNGAJZiluUkjnY6h79uSKiFIKDVK8dI5S8VZbzQg3LfnR8KauuPm4RMYljOihxWqaV06OlJaKJlfE8SSJCAkHuAecax7fYDme/QukaVMlI6hiJGpEzeFn6GFMeiwqAVpGa/liwqc/gnraMvbyjiWjN0d7XlCAUNUU3Aumntee5mHYNLRQyg==~3425073~3556408; _ga_87M7PJ3R97=GS1.1.1731661294.183.1.1731662876.58.0.0; _ga_WM2NSQKJEK=GS1.1.1731661294.16.1.1731662876.0.0.0; RT="z=1&dm=nseindia.com&si=60d56915-5fc7-4873-b4df-f6cc75e7afc3&ss=m3iiln8b&sl=1&se=8c&tt=1x4&bcn=%2F%2F684d0d44.akstat.io%2F&ld=rk7g"; bm_sv=E7F5A9D8DB1C45F3D460DA4778D0F57D~YAAQPSEPF4jEWQyTAQAAdpAmLxlHNkbzIKFC5wey6IFRjsM3GHgwsjd1DtlJ6l5Z7DLd6ACjPk1f0HvgGq7CPYyCnYRY3tmwzTRxBW6aU3bAE8OKAj0A1sJPY9o+8FhVSLh0csJ7P8brQdLJ+4lSBd5/6FMe+rr7EdcSyf9Wm2575zGMBfimCgx6/TdRFXmmykP8K77yFx5pta/2+3qrypbLbXQYa3ctV1h60RpwXcN/QZVD4MHZrvZhpfVxlqOjKwZZMw==~1'

    }


    session = requests.session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    print(cookies)
    response = session.get(url,headers=headers,cookies=cookies).json()['filtered']['data']
    rawdata = pd.DataFrame(response)
    print(rawdata)
    docdata = []
    for i in response:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info = k
                info['instrumenet Type'] = j
                docdata.append(info)
    df = pd.DataFrame(docdata)
        # wb = xsw.Book("angle_excel.xlsx")
        # st = wb.sheets('nifty')
        # st.range('A1').value = df
    target = int(target)
    today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
    # print(df)
    closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
    unique_strike_prices = sorted(df['strikePrice'].unique())

    # Find the index of the closest strike price in the unique strike prices list
    closest_index = unique_strike_prices.index(closest_strike_price)

    # Find the strike prices before and after the closest one
    previous_strike_price = unique_strike_prices[closest_index - 1] if closest_index > 0 else None
    next_strike_price = unique_strike_prices[closest_index + 1] if closest_index < len(
        unique_strike_prices) - 1 else None

    # print("Closest strike price:", closest_strike_price)
    # print("Strike price before:", previous_strike_price)
    # print("Strike price after:", next_strike_price)
    setdf = df[(df['strikePrice'] == closest_strike_price)]
    minsetdf = df[(df['strikePrice'] == previous_strike_price)]
    maxset = df[(df['strikePrice'] == next_strike_price)]
    # print(setdf,minsetdf,maxset)
    print('strick price',setdf[setdf['instrumenet Type'] == 'PE']['strikePrice'].values[-1],'---',setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1], '--', setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1], '----',
      setdf['expiryDate'].values[-1], 'PE', '----', setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
      '--', setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1], '----', setdf['expiryDate'].values[0],
      'CE')

    if type == 'ce' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    elif type == 'pe' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    else:
         return False



print(getparams('BANKNIFTY',50200,'ce'))