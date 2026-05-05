from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response_text = requests.post("http://localhost:8000/send?thread_id=2&platform=telegram", json={"content": user_message, "platform": "telegram"}).json().get("response_content", "No response from agent")

    await update.message.reply_html(response_text)

if __name__ == '__main__':

    application = ApplicationBuilder().token('8756865294:AAFz_yP7744NY5rWme6O39s-RNXuY4jqaQY').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), message_handler
    ))


    application.run_polling()