from telegram import constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import Application
from bot.config import TELEGRAM_TOKEN
from bot.config import ADMIN_CHAT
from bot.config import MN_THREAD_ID
from bot.config import MN_CHAT_ID
from bot.schedule.get_docs import get_new_docs
from bot.schedule.get_docs import download_docs
from urllib.parse import urlparse

import logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def send_updates(context: ContextTypes.DEFAULT_TYPE):
    docs = get_new_docs()

    if docs is None:
        return

    formatted_docs = []
    for doc in docs:
        logging.info(f"New document: {doc.url}")

        if doc.url.endswith(".xlsx") or doc.url.endswith(".xls"):
            file_name = urlparse(doc.url).path.split('/')[-1]
            formatted_docs.append(f"[{file_name}]({doc.url})\n")

    if not formatted_docs:
        formatted_docs.clear()
        return

    link_text = ''

    for link in formatted_docs:
        link_text += link

    new_docs = download_docs()
    blocks = []

    for institute, groups in new_docs.items():
        institute_block = f'*{institute}*\n`{", ".join(groups)}`\n\n'
        blocks.append(institute_block)

    for chat in ADMIN_CHAT:

        if chat == MN_CHAT_ID:
            mn_thread_id = MN_THREAD_ID
        else:
            mn_thread_id = None

        chunk = ""
        first = True
        for block in blocks:
            if len(chunk) + len(block) <= 4096:
                chunk += block
            else:
                if first:
                    text = f"*Обновления в расписании!*\n\n{link_text}\n{chunk}"
                    await context.bot.send_message(chat_id=chat,
                                                   message_thread_id=mn_thread_id,
                                                   text=text, parse_mode="Markdown",
                                                   disable_web_page_preview=True)
                    first = False

                else:

                    await context.bot.send_message(chat_id=chat,
                                                   message_thread_id=mn_thread_id,
                                                   text=chunk, parse_mode="Markdown",
                                                   disable_web_page_preview=True)
                chunk = block

        if chunk:
            if first:
                text = f"*Обновления в расписании!*\n\n{link_text}\n{chunk}"
                await context.bot.send_message(chat_id=chat,
                                               message_thread_id=mn_thread_id,
                                               text=text, parse_mode="Markdown",
                                               disable_web_page_preview=True)
            else:
                await context.bot.send_message(chat_id=chat,
                                               message_thread_id=mn_thread_id,
                                               text=chunk, parse_mode="Markdown",
                                               disable_web_page_preview=True)
    return


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.job_queue.run_repeating(send_updates, interval=300)
    application.run_polling()
