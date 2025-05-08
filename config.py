import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if TOKEN is None:
    print("Ошибка: Токен не найден в .env файле!")
else:
    print("Токен успешно загружен!")

