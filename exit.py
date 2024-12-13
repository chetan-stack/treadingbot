import re
import datetime
from flask import Flask, render_template
import crete_update_table
app = Flask(__name__)


# def sum_profit_or_loss(formatted_data):
#     total_profit_or_loss = 0.0
#     for item in formatted_data:
#         try:
#             profit_or_loss = item.get('profit', 'N/A')
#             if profit_or_loss != 'N/A':
#                 total_profit_or_loss += float(profit_or_loss)
#         except ValueError:
#             print(f"Error converting profit_or_loss to float for item: {item}")
#     return total_profit_or_loss

def sum_profit_or_loss(formatted_data):
    total_profit_or_loss = 0.0
    today = datetime.date.today()
    pushdata = []
    order = 0
    for item in formatted_data:
        try:
            created_date = item.get('createddate')

            # Check if created_date exists and is not None
            if created_date and created_date != 'None':
                # Parse the datetime string to a datetime object
                item_datetime = item['createddate'].split(" ")
                item_date = item_datetime[0]  # Extract just the date part

                # Compare item_date with today's date
                if item_date == str(today):
                    order += 1
                    profit_or_loss = item.get('profit', 'N/A')
                    if profit_or_loss != 'N/A':
                        pattern = r"Profit/Loss:\s*(-?\d+\.\d+)"
                        match = re.search(pattern, item['profit'])
                        profit_loss = pushdata.append(match.group(1))

                        total_profit_or_loss += float(match.group(1))
        except (ValueError, TypeError) as e:
            print(f"Error processing item {item.get('id')}: {e}")
    brokage = order * 50
    return str(total_profit_or_loss) + " - no. of order: " + str(order) + " - brokreg: " + str(brokage)

@app.route('/')
def home():
    try:
        fetchdata = crete_update_table.fetchsupportforweb()
        date = datetime.date.today()
        # print(date)
        formatted_data = []
        for item in fetchdata:
            if item['createddate']:
                datetime_obj = item['createddate'].split(" ")
            if item['createddate'] and datetime_obj[0] == str(date):
                try:

                    profit_str = item.get('profit')

                        # Define the updated regex pattern to extract data
                    # pattern = r'Time: (?P<date>.*?) - Symbol: (?P<symbol>.*?) - Exit Price: (?P<ltp>.*?) - Buy Price: (?P<buyprice>.*?) - Trailing Stoploss Price: (?P<trailing_stoploss_price>.*?) - Target Price: (?P<target_price>.*?) - Profit/Loss: (?P<profit_or_loss>.*?)$'
                    #
                    # match = re.match(pattern, profit_str)
                    # if match:
                    #     data = match.groupdict()
                    # else:
                    #     data = {
                    #         'date': 'N/A',
                    #         'symbol': 'N/A',
                    #         'lt                     p': 'N/A',
                    #         'buyprice': 'N/A',
                    #         'trailing_stoploss_price': 'N/A',
                    #         'target_price': 'N/A',
                    #         'profit_or_loss': 'N/A'
                    #     }

                    # Split the string into key-value pairs
                    pairs = re.split(r' - ', profit_str)

                    # Initialize an empty dictionary
                    result = {}

                    # Parse each pair
                    for pair in pairs:
                        key, value = pair.split(': ', 1)  # Split only on the first ': '

                        # Handle specific types
                        if "Time" in key:
                            result[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                        elif "Symbol" in key:
                            result[key] = value
                        else:
                            result[key] = float(value)

                    # Print the result as a Python dictionary
                    print(result)
                    # Extract and process the 'profit' field safely
                    parts = item['profit'].split(' - ')

                    # Check if the parts list is not empty and get the last item
                    if parts:
                        # Get the last part and clean up the value
                        last_part = parts[-1].split(' ')[-1]  # Last item in the last part

                        # Extract values from the last part if needed
                        ltp = parts[0].split(' ')[1] if len(parts[0].split(' ')) > 1 else 'N/A'
                        buyPrice = parts[1].split(' ')[1] if len(parts[1].split(' ')) > 1 else 'N/A'
                        profitValue = last_part if last_part else 'N/A'
                    else:
                        ltp = buyPrice = profitValue = 'N/A'

                    formatted_item = {
                        'id': item.get('id'),
                        'script': item.get('script'),
                        'token': item.get('token'),
                        'lotsize': item.get('lotsize'),
                        'buyPrice': item.get('ltp'),
                        'nltp':result['Exit Price'],
                        'trailing_stoploss_price': result['Trailing Stoploss Price'],
                        'target_price': result['Target Price'],
                        'max_price_achieved': result['Target Price'],
                        'profit': result['Profit/Loss'],
                        'profittext': item.get('profit'),
                        'createddate': item.get('createddate')
                    }
                    formatted_data.append(formatted_item)
                except Exception as e:
                    formatted_data.append({
                        'id': item.get('id'),
                        'script': item.get('script'),
                        'token': item.get('token'),
                        'lotsize': item.get('lotsize'),
                        'date': 'Error',
                        'symbol': 'Error',
                        'nltp':item.get('ltp'),
                        'ltp': item.get('ltp'),
                        'buyPrice': item.get('ltp'),
                        'trailing_stoploss_price': 'Error',
                        'target_price': 'Error',
                        'max_price_achieved': 'Error',
                        'profit': item.get('profit'),
                        'createddate': item.get('createddate')
                    })
                    print(f"Error processing item {item.get('id')}: {e}")

    except Exception as e:
        return f"An error occurred: {e}"
    print(formatted_data)
    allprofit = sum_profit_or_loss(formatted_data)
    return render_template('index.html', fetchdata=formatted_data,allprofit=allprofit)


if __name__ == '__main__':
    app.run(debug=True, port=4000)


                # crete_update_table.inserttokenns(petoken['symbo23l'], petoken['exch_seg'], petoken['token'], petoken['lotsize'], ltpbuy, token) if checktype == 'pe' else crete_update_table.inserttokenns(cetoken['symbol'], cetoken['exch_seg'], cetoken['token'], cetoken['lotsize'], ltpbuy, token) if checktype == 'ce' else 'no order'
                # logging.info(f"place buy order {checktype}")
                #
                # crete_update_table.inserttokenns(stickprice, petoken['exch_seg'], token, lotsize, ltp, '0')
                # logging.info(f"place sell order {stickprice}")
                #
                # bot_message = f'braekout  in {interwal} timeframe status:sell for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
                # sendAlert(bot_message)