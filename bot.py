import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import TOKEN
from datetime import datetime

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

MSG = "Милая, пора пить таблеточки 💊"
reminder_times = ["8:00", "20:00"]
subscribed_users = set()
sent_today = {}

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Старт", callback_data="start_reminder")],
    [InlineKeyboardButton(text="🛑 Стоп", callback_data="stop_reminder")]
])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я буду напоминать тебе пить таблеточки в 08:00 и 20:00.\n"
        "Нажми кнопку ниже, чтобы включить или отключить напоминания:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "start_reminder")
async def handle_start_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    subscribed_users.add(user_id)
    await callback.answer("Ты подписана на напоминания 💌")
    await callback.message.edit_text("✅ Напоминания включены.\n\n(Нажми «Стоп», чтобы отключить)", reply_markup=keyboard)

@dp.callback_query(F.data == "stop_reminder")
async def handle_stop_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    subscribed_users.discard(user_id)
    await callback.answer("Ты отписалась от напоминаний ❌")
    await callback.message.edit_text("🛑 Напоминания отключены.\n\n(Нажми «Старт», чтобы включить)", reply_markup=keyboard)

async def send_reminders():
    while True:
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.date().isoformat()

        for target_time in reminder_times:
            if time_str == target_time and sent_today.get(target_time) != date_str:
                for user_id in subscribed_users:
                    try:
                        await bot.send_message(user_id, MSG)
                        logging.info(f"Отправлено {user_id} в {time_str}")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке: {e}")
                sent_today[target_time] = date_str

        await asyncio.sleep(30)

async def main():
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
