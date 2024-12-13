from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

import extractfundamental
import googlefeeds
import sendindtructionfortelegrame
import re
# Bot credentials
bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
bot_chatid = "2027669179"

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
    await update.message.reply_text(
        "Hello! I am your bot. You can view automatically generated support and resistance levels, as well as the best levels for buying and selling. To get a sample, send a request in the format: symbol-interval (e.g., nifty-1m).")


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
        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
        data = response.json()

        # Search for the item with a matching name, case-insensitive
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
    print(f"Received message: {user_message}")
    # Echo the message back
    await update.message.reply_text(f"Searching For... {user_message}")
    # Send an image back as a response
    split = user_message.split('-')
    formatcheck = check_format(user_message)
    # symbolfilter = filter_first_symbol(split[0])
    symbolfilter = {}
    news = False
    if split[0].lower() == 'news':
        await update.message.reply_text(f"Searching for news")
        textchange = f"{split[1]} stock"
        news_data = googlefeeds.scrape_google_news(textchange)
        formatted_news = ""
        for news in news_data:
            formatted_news += f"Headline: {news['headline']}\nURL: {'check'}\nDate: {news['source']}\n\n"

        await update.message.reply_text(f"{formatted_news}")

    if split[0].lower() == 'bitcoin':
        symbolfilter['name'] = 'BTCUSD'
        symbolfilter['exch_seg'] = 'CRYPTO'

    elif split[0].lower() == 'ethereum':
        symbolfilter['name'] = 'ETHUSD'
        symbolfilter['exch_seg'] = 'CRYPTO'
    else:
        symbolfilter = get_item_by_name(split[0])


    print("Matching item:", symbolfilter['name'])

    if symbolfilter['exch_seg'] == 'MCX':
         symbolfilter['name'] = f"{symbolfilter['name']}"
    if formatcheck == True and symbolfilter != None:
        if split[1] != None:
            try:
                # Print the status of the symbolfilter
                print('changestatus', symbolfilter['name'])
                # Call the function and retrieve levels
                registancelevel, supportlevel, level = sendindtructionfortelegrame.index(
                    symbolfilter['name'], symbolfilter['exch_seg'], split[1]
                )
                foundmental = extractfundamental.main(symbolfilter['name'])
                # Specify the image path and send the chart
                image_path = "path/to/your/image.jpg"  # Update to the correct image path
                await update.message.reply_photo(photo=open('static/chart.png', 'rb'))

                # Send a message with resistance, support, and entry levels
                await update.message.reply_text(
                    f"Most Significant Resistance Level: {registancelevel}\n"
                    f"Most Significant Support Level: {supportlevel}\n"
                    f"Levels for planning Entry: {level}\n"
                )
                await update.message.reply_text(f"fundamental: {foundmental}")
            except FileNotFoundError as e:
                print(f"File error: {e}")
                await update.message.reply_text("Error: The chart image could not be found.")
            except KeyError as e:
                print(f"Key error: {e}")
                await update.message.reply_text("Error: check symbol name and format : .")
            except Exception as e:
                print(f"Unexpected error: {e}")
                await update.message.reply_text("An unexpected error occurred. Please try again.")
        else:
            foundmental = extractfundamental.main(symbolfilter['name'])
            await update.message.reply_text(f"fundamental: {foundmental}")

    elif news == True:
        await update.message.reply_text(f"Searching for news")
        news_data = googlefeeds.search_text(split[0])
        formatted_news = ""
        for news in news_data:
            formatted_news += f"Headline: {news['headline']}\nURL: {news['url']}\nSource: {news['source']}\n\n"

        await update.message.reply_text(f"{formatted_news}")
    else:
        await update.message.reply_text(f"{formatted_news}")
        await update.message.reply_text(f"Error: use format - symbol-1m use any timeframe 5m,10m,15m,30m,45m,1h,2h..,1d,1w,1m")


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



def main():
    # Initialize the Application
    print('startingbot....')
    app = Application.builder().token(bot_token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sendimg", hanndle_response))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot using polling
    print('polling....')
    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
