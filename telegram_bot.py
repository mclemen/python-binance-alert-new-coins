import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from binance import main

telegram_bot_token = "your_telegram_token_here"

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    chat_id = update.effective_chat.id
    message = ""

    data = main()
    message = f'New coins detected: {new_coins}'
    context.bot.send_message(chat_id = chat_id, text = message)

def shutdown():
    updater.stop()
    updater.is_idle = False


dispatcher.add_handler(CommandHandler("start", start))
updater.start_polling()
