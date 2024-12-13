from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import requests

import technically_filtered_stock

# Assuming `technically_filtered_stock` and `generate_content` are already defined in your project

def chooseoption(data):
    symbol = technically_filtered_stock.condition
    listdata = technically_filtered_stock.get_data(symbol[data])
    content = generate_content(listdata, data)
    return content


def telegrameBot(message):
    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"  # Your bot token
    bot_chatid = "2027669179"  # Your chat ID

    # Encode the message to handle special characters in HTML
    bot_message = f"{message}"  # Example: Make the message bold using HTML tags

    # Build the Telegram API URL
    send_message = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Create the payload for the POST request
    payload = {
        "chat_id": bot_chatid,
        "text": bot_message,
        "parse_mode": "HTML"  # Use HTML parse mode
    }

    try:
        # Make the POST request
        response = requests.post(send_message, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Return the response as JSON
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {"ok": False, "error": str(e)}

def generate_content(listdata,head):
    if len(listdata) > 0:
        content = ""
        serachhead = ' '.join(head.split('-')).title()
        content += f"""<b>{serachhead} - Use Symbol Code for Getting Chart Anlysis,Fundamental and News:</b>
"""
        for i, stock in enumerate(listdata):
            symbolup = "↑" if int(stock['per_chg']) > 0 else "↓" if stock['per_chg'] < 0 else "→"
            if i >= 15:  # Limit to 15 items
                break

            content += f"""
<b>Symbol:</b> {stock['name']} - {stock['nsecode']}
<b>Close Price:</b> {stock['close']}
<b>Percentage Change:</b> {stock['per_chg']}% {symbolup}
<b>Volume:</b> {stock['volume']}
<b>View News:</b> `/view{stock['nsecode']}news`
<b>View Fundamental:</b> `/view{stock['nsecode']}info`
"""
        return content  # Add an extra newline at the end
    return 'No Data Found'


def run_in_thread(data_list):
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(chooseoption, data): data for data in data_list}
        for future in futures:
            data = futures[future]
            try:
                telegrameBot(future.result())
                print('future.result()',future.result())
                results[data] = future.result()
            except Exception as e:
                results[data] = f"Error: {str(e)}"
    return results

def run_in_thread(data_list):
    with ThreadPoolExecutor() as executor:
        try:
            futures = executor.submit(chooseoption, data_list)
            telegrameBot(futures.result())
        except Exception as e:
             print(f"Error: {str(e)}")



if __name__ == "__main__":
    # Example usage
    data_list = ['15minute-stock-breakouts', 'intradaystock']  # Replace with your actual keys
    results = run_in_thread(data_list)

    # for key, result in results.items():
    #     print(f"Results for {key}:")
    #     if isinstance(result, str) and result.startswith("Error"):
    #         print(result)
    #     else:
    #         print(result)  # Replace with actual handling of the result
