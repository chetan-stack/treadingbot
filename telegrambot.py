from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, \
    CallbackContext
import requests
import threading
import extractfundamental
import googlefeeds
import sendindtructionfortelegrame
import re
import technically_filtered_stock
import json
from datetime import datetime
import telegramdb
from telegram.ext.filters import Regex  # Import Regex filter


# Bot credentials
bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
bot_chatid = "2027669179"
today_date = str(datetime.now().strftime('%Y-%m-%d'))

button_value = {
    "15 Minute Stock breakouts": "15minute-stock-breakouts",
    "Intraday Stock For BUY": "intradaystock",
    "Intraday Stock For SELL": "intradaystocksell",
    "Penny Stocks": "pennystocks",
    "Weekly value Investing king research": "weekly-value-investing-king-research",
    "Penny Stocks Strong Fundamentals": "penny-stocks-strong-fundamentals",
    "Fundamentally Strong Stocks": "fundamentally-strong-stocks",
    "Support and Resistance Levels": "support-and-resistance-levels",
    "Swing Trading Stock": "swing-trading-stock",
    "FII Invested Stocks": "fii-invested-stocks",
    "FII & DII BUYING": "fii-dii-buying"
}



def getjson():
    # Path to the JSON file
    file_path = "OpenAPIScripMaster.json"

    # Open and load the JSON file
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    # Print the JSON data
    return json_data

async def send_img_alert(bot_message, image_path=None):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    if image_path:
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        with open(image_path, 'rb') as photo:
            response = requests.post(url, data={'chat_id': bot_chatid}, files={'photo': photo})
    else:
        response = requests.post(url, data={'chat_id': bot_chatid, 'text': bot_message, 'parse_mode': 'MarkdownV2'})

    print(response.json())
    return response.json()

# Function to handle start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("15 Minute Stock breakouts", callback_data="15minute-stock-breakouts")],
        [InlineKeyboardButton("Intraday Stock For BUY", callback_data="intradaystock")],
        [InlineKeyboardButton("Intraday Stock For SELL", callback_data="intradaystocksell")],
        [InlineKeyboardButton("Penny Stocks", callback_data="pennystocks")],
        [InlineKeyboardButton("Weekly value Investing king research", callback_data="weekly-value-investing-king-research")],
        [InlineKeyboardButton("Penny Stocks Strong Fundamentals", callback_data="penny-stocks-strong-fundamentals")],
        [InlineKeyboardButton("Fundamentally Strong Stocks", callback_data="fundamentally-strong-stocks")],
        [InlineKeyboardButton("Support and Resistance Levels", callback_data="support-and-resistance-levels")],
        [InlineKeyboardButton("Swing Trading Stock", callback_data="swing-trading-stock")],
        [InlineKeyboardButton("FII Invested Stocks", callback_data="fii-invested-stocks")],
        [InlineKeyboardButton("FII & DII BUYING", callback_data="fii-dii-buying")],

    ]
    keyboardbutton = [
        ["15 Minute Stock breakouts"],
        ["Intraday Stock For BUY", "Intraday Stock For SELL"],
        ["Penny Stocks", "Weekly value Investing king research"],
        ["Penny Stocks Strong Fundamentals"],
        ["Fundamentally Strong Stocks"],
        ["Support and Resistance Levels"],
        ["Swing Trading Stock"],
        ["FII Invested Stocks", "FII & DII BUYING"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboardbutton, resize_keyboard=True, one_time_keyboard=True)

    # reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Choose an option from the menu below:\n\n"
        "1. **Individual Stock Fundamentals**: Use the stock symbol (e.g., `tcs`).\n"
        "2. **AI Analysis with Timeframes**: Append the timeframe to the stock symbol (e.g., `tcs-1m` for 1-minute data).\n"
        "3. **Market News and Updates**: Get the latest *30-line shot news* or market-related updates by using keywords like `news`, `info`, or `stock` in your search. Example: `today intraday stocks` or `stock in news`.\n\n"
        "To access the **Advanced Filter Options**, simply type `/menu` or `/start`.\n\n"
        "Have suggestions or want to connect? Type `/suggestion` followed by your query, and we'll get back to you as soon as possible.\n\n"
        "You can check any type of stock market information. Let me know how I can assist!",
        reply_markup=reply_markup
    )

async def button_click2(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()  # Acknowledge the button click to avoid timeouts
    print('enter button')
    print(update.callback_query.message.chat)
    telegramdb.insert_user_data(query.message.chat.first_name, query.message.chat.username, query.message.chat.id, '0', 1)
    checkisvalid = telegramdb.fetch_user_by_username(query.message.chat.id)
    print(checkisvalid)
    requestcount = 10
    if today_date != checkisvalid[8]:
        telegramdb.updateuser(checkisvalid[0], 0)
        checkisvalid = telegramdb.fetch_user_by_username(update.message.chat.id)
    if (len(checkisvalid) > 0 and int(checkisvalid[5]) < requestcount) or today_date != checkisvalid[8]:
        # await query.edit_message_text(f"({checkisvalid[5]}/{requestcount}) Searching For... {query.message.text}")
        if query.data:
            # Edit the original message
            context = chooseoption(query.data)
            await query.edit_message_text(text=context,parse_mode="HTML")

        else:
            # Send a new message
            await query.edit_message_text(text="Something went worg try again latter")
        telegramdb.updateuser(checkisvalid[0], (int(checkisvalid[5]) + 1))

    else:
        await query.message.reply_text(f"Limit Exceeded for Username: {query.message.chat.first_name}")


def generate_content(listdata,head):
    print(listdata)
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
<b>View technical:</b> `/view{stock['nsecode']}chart`
"""
        return content  # Add an extra newline at the end
    return 'No Data Found'

def chooseoption(data):
    symbol = technically_filtered_stock.condition
    listdata = technically_filtered_stock.get_data(symbol[data])
    content = generate_content(listdata,data)
    return content

def check_format(text):
    # Define the pattern for "symbol-<number>m" format
    pattern = r"^[a-zA-Z0-9]+-\d+[hmdMw]$"

    # Check if the text matches the pattern
    if re.match(pattern, text):
        return True
        # Place function call here
        # your_function()
    else:
        return False

import requests

def get_item_by_name(target_name):
    try:

        getfirstsymbol = sendindtructionfortelegrame.symbols
        filtered_data = [key for key, value in getfirstsymbol.items() if target_name.lower() in value.lower() or target_name.lower() in key.lower()]
        print(filtered_data)

        if len(filtered_data) > 0:
            print('check status',filtered_data[0])
            data = {
                'name':filtered_data[0],
                'exch_seg':'NSE'
            }
            return data
        else:
            print('check symbol with else')
            # url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
            # response = requests.get(url)
            # response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
            # data = response.json()
            data = getjson()
            for item in data:
                if item.get('name') and item['name'].lower() == target_name.lower():
                      print('1')
                      return item
                # elif item.get('name') and target_name.lower() in item['name'].lower():
                #      print('2')
                #      return item['name']

            return None  # Return None if no match is found

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except ValueError as e:
        print(f"Error processing JSON: {e}")
        return None

# Usage example
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
# target_name = "hindustanunileverables"
target_name = "gold"
result = get_item_by_name(target_name)
print("Matching item:", result)

# Function to handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print('ussername',update.message.chat.username)
    telegramdb.insert_user_data(update.message.chat.first_name,update.message.chat.username,update.message.chat.id ,'0',1)
    checkisvalid = telegramdb.fetch_user_by_username(update.message.chat.id)
    print(checkisvalid)
    requestcount = 10
    if today_date != checkisvalid[8]:
        telegramdb.updateuser(checkisvalid[0], 0)
        checkisvalid = telegramdb.fetch_user_by_username(update.message.chat.id)

    print(today_date,checkisvalid[8],today_date != checkisvalid[8])
    if len(checkisvalid) > 0 and int(checkisvalid[5]) < requestcount:
        # print(f"Received message: {user_message}")
        # Echo the message back
        await update.message.reply_text(f"({checkisvalid[5]}/{requestcount}) Searching For... {user_message}")
        # Send an image back as a response
        split = user_message.split('-')
        formatcheck = check_format(user_message)
        # symbolfilter = filter_first_symbol(split[0])
        symbolfilter = {}
        # news = False
        # Input text
        news = user_message
        # news += f"{user_message} + stocks"
        # Keywords to check
        keyboardbutton = [
            "15 Minute Stock breakouts",
            "Intraday Stock For BUY",
            "Intraday Stock For SELL",
            "Penny Stocks",
            "Weekly value Investing king research",
            "Penny Stocks Strong Fundamentals",
            "Fundamentally Strong Stocks",
            "Support and Resistance Levels",
            "Swing Trading Stock",
            "FII Invested Stocks",
            "FII & DII BUYING"
        ]

        keywords = ["news", "info", "details","about","how",'why',"when",'stock',"was",'intraday']
        if any(keyword.lower() in user_message.lower() for keyword in keyboardbutton):
            context = chooseoption(button_value[user_message])
            await update.message.reply_text(text=context, parse_mode="HTML")
            return
        if any(keyword in news.lower() for keyword in keywords):
            await update.message.reply_text(f"Searching for news")
            # textchange = f"{split[1]} stock"
            news += f"{user_message} + stocks"
            news_data = googlefeeds.scrape_google_news(news)
            formatted_news = ""
            formatted_news_html = ""
            for news in news_data:
                formatted_news += f"Headline: {news['headline']}\nURL: <a href=\"{news['url']}\">Click Here</a>\nDate: {news['source']}\n\n"
            # await update.message.reply_text(f"{formattedl_news}")
            await update.message.reply_text(
                formatted_news,
                parse_mode="HTML"  # Ensures the message is interpreted as HTML
            )
            return

        if split[0].lower() == 'bitcoin':
            symbolfilter['name'] = 'BTCUSD'
            symbolfilter['exch_seg'] = 'CRYPTO'

        elif split[0].lower() == 'ethereum':
            symbolfilter['name'] = 'ETHUSD'
            symbolfilter['exch_seg'] = 'CRYPTO'

        elif split[0].lower() == 'sensex':
            symbolfilter['name'] = 'SENSEX'
            symbolfilter['exch_seg'] = 'BSE'

        else:
            symbolfilter = get_item_by_name(split[0])

        print(symbolfilter)
        # print("Matching item:", symbolfilter['name'])

        # if symbolfilter['exch_seg'] == 'MCX':
        #      symbolfilter['name'] = f"{symbolfilter['name']}"
        if formatcheck == True and symbolfilter != None:

            try:
                # Print the status of the symbolfilter
                print('changestatus', symbolfilter['name'])
                # Call the function and retrieve levels
                registancelevel, supportlevel, level = sendindtructionfortelegrame.index(
                    symbolfilter['name'], symbolfilter['exch_seg'], split[1].lower()
                )
                # Specify the image path and send the chart
                await update.message.reply_photo(photo=open('static/chart.png', 'rb'))

                # Send a message with resistance, support, and entry levels
                await update.message.reply_text(
                    f"Most Significant Resistance Level: {registancelevel}\n"
                    f"Most Significant Support Level: {supportlevel}\n"
                    f"Levels for planning Entry: {level}\n"
                )
            except FileNotFoundError as e:
                print(f"File error: {e}")
                await update.message.reply_text("Error: The chart image could not be found.")
            except KeyError as e:
                print(f"Key error: {e}")
                await update.message.reply_text("Error: check symbol name and format : .")
            except Exception as e:
                print(f"Unexpected error: {e}")
                await update.message.reply_text(f"No levels for {split[1].lower()}. Try Another Timframe")

        else:
            print(symbolfilter)

            if split[0].lower() == 'news':
                print('none')
            else:
                if symbolfilter == None:
                    await update.message.reply_text(f"Error: check symbol name and format : .")
                else:
                    foundmental = extractfundamental.main(symbolfilter['name'])
                    await update.message.reply_text(f"Fundamental Analysis: {foundmental}")
                await update.message.reply_text("Instruction :\n\n"
        "1. **Individual Stock Fundamentals**: Use the stock symbol (e.g., `tcs`).\n"
        "2. **AI Analysis with Timeframes**: Append the timeframe to the stock symbol (e.g., `tcs-1m` for 1-minute data).\n"
        "3. **Market News and Updates**: Get the latest *30-line shot news* or market-related updates by using keywords like `news`, `info`, or `stock` in your search. Example: `today intraday stocks` or `stock in news`.\n\n"
        "To access the **Advanced Filter Options**, simply type `/menu` or `/start`.\n\n"
        "Have suggestions or want to connect? Type `/suggestion` followed by your query, and we'll get back to you as soon as possible.\n\n"
        "You can check any type of stock market information. Let me know how I can assist!",)


    else:
        await update.message.reply_text(f"Limit Exceeded for Username: {update.message.chat.first_name}")

    telegramdb.updateuser(checkisvalid[0], (int(checkisvalid[5]) + 1))


# Function to send an image on /sendimg command
async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_message = "Here is an image for you."
    image_path = 'path_to_your_image.png'  # Update this with your image path
    response = send_img_alert(bot_message, image_path)
    await update.message.reply_text("Image sent!")

def hanndle_response(text: str):
    process: str = text.lower()
    if 'hello' in process:
        return 'hii'
    return 'i dont understand'

async def suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        # Combine arguments into a single suggestion string
        user_suggestion = ' '.join(context.args)
        user_name = update.effective_user.full_name
        # suggestions.append(f"{user_name}: {user_suggestion}")
        telegramdb.insert_user_suggestion(update.message.chat.first_name, update.message.chat.username,
                                    update.message.chat.id,user_suggestion)
        await update.message.reply_text(
            "Thank you for your suggestion! We appreciate your feedback and will review it shortly."
        )
    else:
        await update.message.reply_text(
            "Please provide your suggestion after the `/suggestion` command.\n"
            "Example: `/suggestion Add new stock analysis features`"
        )

async def dynamic_view_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text  # Get the full command
    dynamic_part = message_text.replace('/view', '', 1)  # Extract the dynamic part

    # Example: Check if it ends with 'news'
    if dynamic_part.endswith('news'):
        stock_name = dynamic_part.replace('news', '')  # Remove 'news' suffix
        await update.message.reply_text(f"You requested news for: {stock_name}")
        news = f"{stock_name} stock news"
        news_data = googlefeeds.scrape_google_news(news)
        formatted_news = ""
        formatted_news_html = ""
        for news in news_data:
            formatted_news += f"Headline: {news['headline']}\nURL: <a href=\"{news['url']}\">Click Here</a>\nDate: {news['source']}\n\n"
        # await update.message.reply_text(f"{formattedl_news}")
        await update.message.reply_text(
            formatted_news,
            parse_mode="HTML"  # Ensures the message is interpreted as HTML
        )

    if dynamic_part.endswith('info'):
        stock_name = dynamic_part.replace('info', '')  # Remove 'news' suffix
        await update.message.reply_text(f"You requested info for: {stock_name}")
        foundmental = extractfundamental.main(stock_name)
        await update.message.reply_text(f"Fundamental Analysis: {foundmental}")

    if dynamic_part.endswith('holding'):
        stock_name = dynamic_part.replace('holding', '')  # Remove 'news' suffix
        await update.message.reply_text(f"You requested info for: {stock_name}")
        foundmental = extractfundamental.fetchhollding(stock_name)
        await update.message.reply_text(f"<pre>{foundmental}</pre>", parse_mode="HTML")

    if dynamic_part.endswith('chart'):
        print('enter')
        stock_name = dynamic_part.replace('chart', '')  # Remove 'news' suffix
        await update.message.reply_text(f"You requested chart for: {stock_name}")

        keyboardbutton = [
            [f"{stock_name}-1m",f"{stock_name}-5m"],
            [f"{stock_name}-15m", f"{stock_name}-30m"],
            [f"{stock_name}-45m", f"{stock_name}-1h"],
            [f"{stock_name}-3h", f"{stock_name}-4h"],
            [f"{stock_name}-1d", f"{stock_name}-1w",f"{stock_name}-1M"],

        ]
        reply_markup = ReplyKeyboardMarkup(keyboardbutton, resize_keyboard=True, one_time_keyboard=True)

        # reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Choose an option from the menu below to View Chart Cnalysis:\n\n",
            reply_markup=reply_markup
        )


def main():
    # Initialize the Application
    print('startingbot....')
    app = Application.builder().token(bot_token).build()

    # app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CallbackQueryHandler(button_click2))

    app.add_handler(MessageHandler(Regex(r'^/view\w+(news|info|chart|holding)$'), dynamic_view_handler))
    app.add_handler(CommandHandler("suggestion", suggestion))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("sendimg", hanndle_response))


    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot using polling
    print('polling....')
    app.run_polling(poll_interval=3)

import asyncio

# Run main in a separate thread
if __name__ == "__main__":
    asyncio.run(main())
    # handle_message('tcs-15m')
    # bot_thread = threading.Thread(target=main, daemon=True)
    # bot_thread.start()
    #
    # # Keep the main thread alive or run other tasks
    # try:
    #     while True:
    #         pass  # Replace with your main thread logic, if needed
    # except KeyboardInterrupt:
    #     print("Stopping bot...")
