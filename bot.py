import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import TOKEN
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

MSG = "Милая, пора пить таблеточки 💊"
REMINDER_TIMES = ["08:00", "18:00"]
TIMEZONE = pytz.timezone('Europe/Moscow')
subscribed_users = set()
sent_today = {}
user_states = {}

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Старт", callback_data="start_reminder")],
    [InlineKeyboardButton(text="🛑 Стоп", callback_data="stop_reminder")]
])

choice_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="took_pill_yes")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="took_pill_no")]
])


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я буду напоминать тебе пить таблеточки в 08:00 и 18:00.\n"
        "Нажми кнопку ниже, чтобы включить или отключить напоминания:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "start_reminder")
async def handle_start_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    subscribed_users.add(user_id)
    await callback.answer("Ты подписана на напоминания 💌")
    await callback.message.edit_text("✅ Напоминания включены.\n\n(Нажми «Стоп», чтобы отключить)",
                                     reply_markup=keyboard)


@dp.callback_query(F.data == "stop_reminder")
async def handle_stop_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    subscribed_users.discard(user_id)
    await callback.answer("Ты отписалась от напоминаний ❌")
    await callback.message.edit_text("🛑 Напоминания отключены.\n\n(Нажми «Старт», чтобы включить)",
                                     reply_markup=keyboard)


@dp.callback_query(F.data.in_({"took_pill_yes", "took_pill_no"}))
async def handle_pill_response(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    now = datetime.now(TIMEZONE)
    hour = now.hour

    user_state = user_states.setdefault(user_id, {'morning': None, 'evening': None})

    period = "morning" if hour < 12 else "evening"
    answer_text = "Молодец! ❤️ До завтра!" if data == "took_pill_yes" else "Поняла, напомню ещё раз позже!"

    user_state[period] = "yes" if data == "took_pill_yes" else "no"
    await callback.answer("Ответ получен.")
    await callback.message.edit_text(f"{answer_text}")


async def send_reminders():
    last_checked = datetime.now(TIMEZONE)

    while True:
        now = datetime.now(TIMEZONE)
        date_str = now.date().isoformat()

        for target_time in REMINDER_TIMES:
            target_hour, target_minute = map(int, target_time.split(":"))
            target_dt = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

            if last_checked < target_dt <= now:
                key = (target_time, date_str)

                if not sent_today.get(key):
                    for user_id in list(subscribed_users):
                        try:
                            user_state = user_states.setdefault(user_id, {'morning': None, 'evening': None})

                            if target_time == "08:00":
                                await bot.send_message(user_id, MSG + "\n\nТы выпила таблетки?",
                                                       reply_markup=choice_keyboard)
                                user_state['morning'] = None

                            elif target_time == "18:00" and user_state.get('morning') != 'yes':
                                await bot.send_message(user_id, "Напоминаю ещё раз 💊\nТы выпила таблетки?",
                                                       reply_markup=choice_keyboard)
                                user_state['evening'] = None

                            logging.info(f"Напоминание отправлено {user_id} в {target_time}")
                        except Exception as e:
                            logging.error(f"Ошибка при отправке: {e}")
                            subscribed_users.discard(user_id)

                    sent_today[key] = True

        last_checked = now
        await asyncio.sleep(20)


async def main():
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
