from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import controller as c
def start_message():
    return "Привет! 🚭 Я помогу тебе бросить курить.\n\nТы сейчас куришь?"

def smoking_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    return markup

def ask_smoking_type():
    return 'Что именно ты куришь?'
def ask_smoking_type_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("сигареты"),
        KeyboardButton("электронки"),
        KeyboardButton("сигареты и электронки")
    )
    return markup

def ask_cigarettes_amount():
    return 'Сколько сигарет ты куришь в день?'

def ask_cigarettes_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("1–5"),
        KeyboardButton("6–10"),
        KeyboardButton("11–20"),
        KeyboardButton("Больше 20")
    )
    return markup

def ask_vape_amount():
    return 'На сколько дней тебе хватает электронной сигареты (10 000 тяг)?'

def ask_vape_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Меньше недели"),
        KeyboardButton("1–2 недели"),
        KeyboardButton("2–4 недели"),
        KeyboardButton("Больше месяца")
    )
    return markup

def ask_motivation():
    return "Почему ты хочешь бросить курить?"

def ask_goal():
    return "Отлично! Какая твоя главная цель?"

def saved_message():
    return (
        "Супер! Я сохранил твою информацию ✅\n"
        "Будем работать над этим вместе 💪\n"
        "Воспользуйся командой /profile, чтобы посмотреть профиль"
    )
def profile_message(user, history):
    if user:
        _, username, smoking_status, smoking_type, cigarettes_amount, vape_amount, motivation, goal, reminder_time, last_smoke_date, current_streak, max_streak, cigarette_price, vape_price = user
        profile_text = (
            f"📋 Твой профиль:\n\n"
            f"👤 Username: {username}\n"
            f"🌫️ Что куришь: {smoking_type}\n"
            f"🚬 Сигареты в день: {cigarettes_amount or '—'}\n"
            f"💨 Электронки: {vape_amount or '—'}\n"
            f"💡 Мотивация: {motivation}\n"
            f"⏰️ Время напоминания: {reminder_time}\n"
            f"🔥 Текущий стрик: {current_streak} дней\n"
            f"🏆 Максимальный стрик: {max_streak} дней\n"

        )
        saved_money = c.calculate_money_saved(user[0])
        profile_text += f"💵 Сэкономлено: {saved_money} руб.\n"

        if history:
            profile_text += f"\n🗓 История курения:\n"
            for record in history:
                print(history)
                date, cig, vape = record
                profile_text += f"{date}: 🚬 {cig} | 💨 {vape}\n"
        else:
            profile_text += "Нет данных о курении за дни."

    else:
        return "У тебя пока нет сохранённого профиля. Напиши /start."
    return profile_text

def help_message():
    help_text = (
        "👋 Привет! Я бот для бросания или отслеживания курения.\n\n"
        "Вот что я умею:\n"
        "▫️ /start — начать работу с ботом\n"
        "▫️ /profile — заполнить или обновить профиль (куришь ли ты, сколько и т.п.)\n"
        "▫️ /track — внести запись о курении за сегодня\n"
        "▫️ /stats — посмотреть статистику (неделя, 2 недели, месяц)\n"
        "▫️ /reminder — настроить напоминание 'курил ли ты сегодня?'\n\n"
        "💡 Даже если ты не куришь, можешь использовать меня ради интереса 🚀"
    )
    return help_text
def ask_smoked_today():
    return "Ты курил сегодня?"

def ask_smoked_today_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    return markup

def ask_today_cigarettes():
    return "Сколько сигарет ты сегодня курил? Введи число."

def ask_today_vape():
    return "Сколько затяжек электронной сигареты ты сделал сегодня? Введи число."

def praise_for_no_smoke():
    return "Отлично! Так держать! Сегодня ты не курил ✅"

def ask_reminder_time():
    return "Во сколько напоминать тебе каждый день? ⏰\nНапиши время в формате HH:MM (например 19:30)."

def invalid_reminder_time():
    return "❌ Введи корректное время в формате HH:MM (например 18:45)."

def saved_reminder_time(time_text):
    return f"✅ Отлично! Теперь напоминание будет приходить каждый день в {time_text}."

def encouragement_message_after_smoke():
    return (
        "Данные за сегодня сохранены ✅\n"
        "В следующий раз обязательно получится!.🚭"
    )

def stats_period_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton("📅 Неделя"),
        KeyboardButton("📅 2 недели"),
        KeyboardButton("📅 Месяц")
    )
    return markup
