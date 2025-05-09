import os

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
REMINDER_TIMES = ["20:00"]
MESSAGE_TEXT = "Милая, пора пить таблеточки 💊"
