from datetime import time
import asyncio
import logging
import sys
from os import getenv
import time
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import threadtest
# Bot token can be obtained via https://t.me/BotFather
TOKEN = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
storemessage = []


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    print('actual', message.chat.id, message.chat.first_name)

    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:

        await message.reply(message.text)
        storemessage.append(message.text)
        print(storemessage)
        threadtest.run_in_thread(storemessage)
        # Send a copy of the received message
        time.sleep(2)
        print(message.chat.id, message.chat.first_name)
        await message.send_copy(chat_id=message.chat.id)

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        # Use asyncio.run() if no event loop is running
        asyncio.run(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called" in str(e):
            # Handle the case for already running event loop
            print("Event loop already running. Running main directly.")
            main()