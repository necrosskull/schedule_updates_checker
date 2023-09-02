from telegram import constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import Application
from bot.config import TELEGRAM_TOKEN
from bot.config import ADMIN_CHAT
from bot.schedule.get_docs import get_new_docs
from urllib.parse import urlparse


async def send_updates(context: ContextTypes.DEFAULT_TYPE):
    new_docs = get_new_docs()

    if new_docs is None:
        return

    formatted_docs = []
    for doc in new_docs:
        file_name = urlparse(doc.url).path.split('/')[-1]
        formatted_docs.append(f"[{file_name}]({doc.url})\n")

    chunk = ""
    first = True
    for doc in formatted_docs:
        if len(chunk) + len(doc) <= 4096:
            chunk += doc
        else:
            if first:
                text = f"*Обновления в следующих документах:*\n\n{chunk}"
                await context.bot.send_message(chat_id=ADMIN_CHAT,
                                               text=text, parse_mode="Markdown",
                                               disable_web_page_preview=True)
                first = False

            else:

                await context.bot.send_message(chat_id=ADMIN_CHAT,
                                               text=chunk, parse_mode="Markdown",
                                               disable_web_page_preview=True)
            chunk = doc

    if chunk:
        if first:
            text = f"*Обновления в следующих документах:*\n\n{chunk}"
            await context.bot.send_message(chat_id=ADMIN_CHAT,
                                           text=text, parse_mode="Markdown",
                                           disable_web_page_preview=True)
        else:
            await context.bot.send_message(chat_id=ADMIN_CHAT,
                                           text=chunk, parse_mode="Markdown",
                                           disable_web_page_preview=True)


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.job_queue.run_repeating(send_updates, interval=60, first=0)
    application.run_polling()


if __name__ == '__main__':
    main()
