import asyncio
from datetime import datetime
import os
from telebot.async_telebot import AsyncTeleBot
import controller as c
import database as db
import views as v
# Создаём экземпляр асинхронного бота, токен берётся из переменных окружения
bot = AsyncTeleBot(os.environ["TELEGRAM_TOKEN"])
c.init()

@bot.message_handler(commands=['start'])
async def start_handler(message):
    text, markup, _ = c.handle_start(message, bot)
    await bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['profile'])
async def profile_handler(message):
    text, _, _ = c.handle_profile(message)
    await bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['track'])
async def track_handler(message):
    text, markup, remove_markup = c.start_daily_tracking(message)
    await bot.send_message(message.chat.id, text, reply_markup=markup or remove_markup)

@bot.message_handler(commands=['reminder'])
async def reminder_handler(message):
    text, markup, remove_markup = c.handle_reminder_command(message)
    await bot.send_message(message.chat.id, text, reply_markup=markup or remove_markup)

@bot.message_handler(commands=['stats'])
async def stats_handler(message):
    text, markup, _ = c.handle_stats_command(message)
    await bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=["help"])
async def help_handler(message):
    await bot.send_message(message.chat.id, v.help_message())

@bot.message_handler(func=lambda m: True)
async def all_messages_handler(message):
    chat_id = message.chat.id

    if chat_id in c.user_states:
        state = c.user_states[chat_id]
        if state.startswith("ask_"):
            text, markup, remove_markup = c.handle_fill_profile(message)
        elif state.startswith("track_"):
            text, markup, remove_markup = c.handle_daily_tracking(message)
        elif state.startswith("reminder_"):
            text, markup, remove_markup = c.handle_reminder_time(message)
        elif state.startswith("stats_"):
            text, markup, buf = c.handle_stats_period(message)
            if buf:
                await bot.send_photo(message.chat.id, buf, caption=text)
                return
    else:
        text, markup, remove_markup = ("Я тебя не понял 🤔 Напиши /help", None, None)

    await bot.send_message(chat_id, text, reply_markup=markup or remove_markup)

async def send_reminder(user_id):
        try:
            await bot.send_message(user_id, "Не забудь внести данные о курении сегодня! 🚬📊\nКоманда: /track")
        except Exception as e:
            print(f"Ошибка при отправке напоминания {user_id}: {e}")

async def reminder_loop():
    while True:
        users = c.get_all_users()  # [user_id, ...]
        now = datetime.now()
        current_time = f"{now.hour:02}:{now.minute:02}"
        for user_id in users:
            reminder_time = db.get_user_reminder_time(user_id)
            if reminder_time == current_time:
                await send_reminder(user_id)

        await asyncio.sleep(60)  # проверка каждую минуту

async def main():
    task_bot = asyncio.create_task(bot.polling())
    task_reminder = asyncio.create_task(reminder_loop())
    await asyncio.gather(task_bot, task_reminder)

if __name__ == '__main__':
    asyncio.run(main())
