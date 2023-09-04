import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT = list(map(int, os.getenv("ADMIN_CHAT").split(",")))
MN_THREAD_ID = int(os.getenv("MN_THREAD_ID"))
MN_CHAT_ID = int(os.getenv("MN_CHAT_ID"))
