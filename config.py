import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BACKUP_FOLDER = "backups"
MAX_SIZE = 45 * 1024 * 1024  #chunking