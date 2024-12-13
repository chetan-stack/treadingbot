from telegram import Application, CommandHandler, MessageHandler, Update
from telegram.ext import ContextTypes, filters

# Function to send a message to a specific client
async def send_message_to_client(client_id: int, message: str, app: Application) -> None:
    """
    Send a message to a specific client using their chat ID.

    :param client_id: The chat ID of the client.
    :param message: The message to send.
    :param app: The bot application instance.
    """
    try:
        # Use the bot instance to send a message
        await app.bot.send_message(chat_id=client_id, text=message)
        print(f"Message sent to client {client_id}: {message}")
    except Exception as e:
        print(f"Failed to send message to client {client_id}: {e}")

# Example handlers for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Use /sendimg to test the bot.")

async def hanndle_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Placeholder for sending an image
    await update.message.reply_text("Image sending functionality here.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Received your message: {update.message.text}")

# Main function
def main():
    # Initialize the Application
    print('Starting bot...')
    bot_token = "YOUR_BOT_TOKEN"  # Replace with your bot token
    app = Application.builder().token(bot_token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sendimg", hanndle_response))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Send a test message to a specific client (replace with an actual chat ID)
    test_client_id = 123456789  # Replace with the recipient's chat ID
    test_message = "Hello from the bot!"
    app.job_queue.run_once(lambda _: send_message_to_client(test_client_id, test_message, app), when=0)

    # Start the bot using polling
    print('Polling...')
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()
