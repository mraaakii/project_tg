import database as db
import views as v
from telebot.types import ReplyKeyboardRemove
from datetime import datetime
from graf import build_smoking_stats

#Константы состояний пользователя
ASK_SMOKING = "ask_smoking"
ASK_SMOKING_TYPE = "ask_smoking_type"
ASK_CIGARETTES_AMOUNT = "ask_cigarettes_amount"
ASK_VAPE_AMOUNT = "ask_vape_amount"
ASK_MOTIVATION = "ask_motivation"
ASK_CIGARETTE_PRICE = "ask_cigarette_price"
ASK_VAPE_PRICE = "ask_vape_price"
user_states = {}

TRACK_SMOKED_TODAY = "track_smoked_today"
TRACK_TODAY_CIGARETTES = "track_today_cigarettes"
TRACK_TODAY_VAPE = "track_today_vape"

REMINDER_SET = "reminder_SET"

STATS_PERIOD = "stats_period"

def init(): #Инициализация базы данных при запуске бота
    db.init_db()

def handle_start(message, bot): #начинаем опрос профиля
    user_states[message.chat.id] = ASK_SMOKING
    return v.start_message(), v.smoking_keyboard(), None

def handle_profile(message): #Отображение профиля пользователя + история трекинга
    user = db.get_user(message.chat.id)
    history = db.get_daily_tracking(message.chat.id)
    return v.profile_message(user, history), None, None

def handle_fill_profile(message): # Пошаговое заполнение профиля пользователя.
    state = user_states.get(message.chat.id)
    #курит ли
    if state == ASK_SMOKING:
        if message.text.lower() == "да":
            db.save_user(message.chat.id, message.from_user.username, smoking_status=True)
            user_states[message.chat.id] = ASK_SMOKING_TYPE
            return v.ask_smoking_type(), v.ask_smoking_type_keyboard(), None
        elif message.text.lower() == "нет":
            db.save_user(message.chat_id, smoking_status=False)
            user_states.pop(message.chat.id, None)
            return "Отлично 🚀 Рад, что тебе не нужно бороться с этой привычкой!", None, None
        else:
            return "Пожалуйста, выбери 'Да' или 'Нет'.", None, None
    #что курит
    elif state == ASK_SMOKING_TYPE:
        if message.text.lower() in ["сигареты", "электронки", "сигареты и электронки"]:
            db.update_user_field(message.chat.id, "smoking_type", message.text)
            if message.text == "сигареты":
                user_states[message.chat.id] = ASK_CIGARETTES_AMOUNT
                return v.ask_cigarettes_amount(), v.ask_cigarettes_keyboard(), None
            elif message.text == "электронки":
                user_states[message.chat.id] = ASK_VAPE_AMOUNT
                return v.ask_vape_amount(), v.ask_vape_keyboard(), None
            else: #оба варианта
                user_states[message.chat.id] = ASK_CIGARETTES_AMOUNT
                return v.ask_cigarettes_amount(), v.ask_cigarettes_keyboard(), None
        else:
                return "Пожалуйста, выбери один из вариантов.", None, None
    #кол-во сигарет в день
    elif state == ASK_CIGARETTES_AMOUNT:
        db.update_user_field(message.chat.id, "cigarettes_amount", message.text)
        user_states[message.chat.id] = ASK_CIGARETTE_PRICE
        return "Сколько стоит пачка сигарет, которые ты обычно покупаешь? (в рублях)", ReplyKeyboardRemove(), None
    #цена пачки
    elif state == ASK_CIGARETTE_PRICE:
        try:
            price = float(message.text)
            db.update_user_field(message.chat.id, "cigarette_price", price)
        except ValueError:
            return "Введи число, например 200.", None, None

        user = db.get_user(message.chat.id)
        smoking_type = user[3] or ""

        if "электронки" in smoking_type.lower():
            user_states[message.chat.id] = ASK_VAPE_AMOUNT
            return v.ask_vape_amount(), v.ask_vape_keyboard(), None
        else:
            user_states[message.chat.id] = ASK_MOTIVATION
            return v.ask_motivation(), ReplyKeyboardRemove(), None
    #на сколько хватает электронной сигаретыс
    elif state == ASK_VAPE_AMOUNT:
        db.update_user_field(message.chat.id, "vape_amount", message.text)
        user_states[message.chat.id] = ASK_VAPE_PRICE
        return "Сколько стоит электронная сигарета (в рублях)?", ReplyKeyboardRemove(), None
    #цена электронной сигареты
    elif state == ASK_VAPE_PRICE:
        try:
            price = float(message.text)
            db.update_user_field(message.chat.id, "vape_price", price)
        except ValueError:
            return "Введи число, например 1200.", None, None
        user_states[message.chat.id] = ASK_MOTIVATION
        return v.ask_motivation(), ReplyKeyboardRemove(), None
    #мотивация
    elif state == ASK_MOTIVATION:
        db.update_user_field(message.chat.id, "motivation", message.text)
        user_states.pop(message.chat.id, None)
        return v.saved_message(), None, None

    else:
        return "Напиши /start, чтобы пройти опрос заново.", None, None

#ежедневный трекинг
def start_daily_tracking(message):
    user = db.get_user(message.chat.id)
    if not user:
        return "Сначала пройди опрос с /start", None, None

    user_states[message.chat.id] = TRACK_SMOKED_TODAY
    return v.ask_smoked_today(), v.ask_smoked_today_keyboard(), None

#обработка
def handle_daily_tracking(message):

    state = user_states.get(message.chat.id)
    today = datetime.today().strftime("%d-%m-%Y")
    user = db.get_user(message.chat.id)
    smoking_type = user[3].lower()
    current_streak = user[10] or 0
    max_streak = user[11] or 0
    last_smoke_date = user[9]
#курил ли сегодня
    if state == TRACK_SMOKED_TODAY:
        if message.text.lower() == "да":
            #сброс стрика
            db.update_user_field(message.chat.id, "current_streak", 0)
            db.update_user_field(message.chat.id, "last_smoke_date", today)
            if "сигареты" in smoking_type:
                user_states[message.chat.id] = TRACK_TODAY_CIGARETTES
                return v.ask_today_cigarettes(), ReplyKeyboardRemove(), None
            elif "электронки" in smoking_type:
                user_states[message.chat.id] = TRACK_TODAY_VAPE
                return v.ask_today_vape(), ReplyKeyboardRemove(), None
            elif "сигареты и электронки" in smoking_type:
                user_states[message.chat.id] = TRACK_TODAY_CIGARETTES
                return v.ask_today_cigarettes(), ReplyKeyboardRemove(), None
            return None

        elif message.text.lower() == "нет":
            # не курил > обновляем стрик
            if last_smoke_date:
                last_smoke = datetime.strptime(last_smoke_date, "%d-%m-%Y")
                if (datetime.today() - last_smoke).days > 1:
                    current_streak = 1
                else:
                    current_streak += 1
            else:
                current_streak = 1
            max_streak = max(max_streak, current_streak)
            #сохраняем стрик и запись в бд
            db.update_user_field(message.chat.id, "current_streak", current_streak)
            db.update_user_field(message.chat.id, "max_streak", max_streak)
            db.save_daily_tracking(message.chat.id, today, cigarettes=0, vape_puffs=0)
            user_states.pop(message.chat.id, None)
            return v.praise_for_no_smoke()+f"\n🔥 Твой текущий стрик: {current_streak} дней\n🏆 Максимальный стрик: {max_streak} дней", ReplyKeyboardRemove(), None
        else:
            return "Пожалуйста, выбери кнопку 'Да' или 'Нет'.", v.ask_smoked_today_keyboard(), None
    # кол-во сигарет за сегодня
    elif state == TRACK_TODAY_CIGARETTES:
        try:
            cigarettes = int(message.text)
            if cigarettes < 0:
                raise ValueError
        except ValueError:
            return "Введи корректное число сигарет, например 5.", None, None

        if "электронки" in smoking_type:
            user_states[message.chat.id] = TRACK_TODAY_VAPE
            user_states["cigarettes_temp"] = cigarettes
            return v.ask_today_vape(), None, None
        else:
            db.save_daily_tracking(message.chat.id, today, cigarettes=cigarettes)
            user_states.pop(message.chat.id, None)
            return v.encouragement_message_after_smoke(), None, None
    # кол-во тяжек за сегодня
    elif state == TRACK_TODAY_VAPE:
        try:
            vape_puffs = int(message.text)
            if vape_puffs < 0:
                raise ValueError
        except ValueError:
            return "Введи корректное число затяжек, например 50.", None, None

        if "cigarettes_temp" in user_states:
            cigarettes = user_states.pop("cigarettes_temp")
        else:
            cigarettes = 0

        db.save_daily_tracking(message.chat.id, today, cigarettes=cigarettes, vape_puffs=vape_puffs)
        user_states.pop(message.chat.id, None)
        return v.encouragement_message_after_smoke(), None, None

    else:
        return "Напиши /track, чтобы ввести данные за сегодня.", None, None

#спрашиваем время напоминания
def handle_reminder_command(message):
    user_states[message.chat.id] = REMINDER_SET
    return v.ask_reminder_time(), None, None

#Обработка введённого времени напоминания. Формат: ЧЧ:ММ
def handle_reminder_time(message):
    try:
        time_text = message.text.strip()
        hour, minute = map(int, time_text.split(":"))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except ValueError:
        return v.invalid_reminder_time(), None, None

    db.update_user_field(message.chat.id, "reminder_time", time_text)
    user_states.pop(message.chat.id, None)
    return v.saved_reminder_time(time_text), None, None

#возвращает список всех user_id
def get_all_users():
    users = db.get_all_users()
    return [user[0] for user in users]


def calculate_money_saved(user_id):
    """
  Подсчёт сэкономленных денег по сравнению с привычным уровнем курения.
    - Для сигарет берём цену пачки / 20 (1 сигарета).
    - Для вейпа берём цену / 10000 (условно на 10к тяг).
    - Берём историю курения из БД.
    - Считаем, сколько потратил бы пользователь по привычке,
      и сколько реально потратил → разница = сэкономил.
      """
    user = db.get_user(user_id)
    if not user:
        return 0

    cigarettes_amount = user[4] # среднее кол-во сигарет в профиле
    cigarette_price = user[12] if len(user) > 12 else 0
    vape_amount = user[5]
    vape_price = user[13] if len(user) > 13 else 0

    # цена за 1 сигарету
    price_per_cig = cigarette_price / 20 if cigarette_price else 0
    # цена за 1 затяжку (если устройство на 10 000 тяг)
    price_per_puff = vape_price / 10000 if vape_price else 0

    records = db.get_daily_tracking(user_id)
    spent = 0
    would_spend = 0

    try:
        # сигареты (берём верхнюю границу диапазона)
        if cigarettes_amount:
            avg_cigs = int(cigarettes_amount.split("–")[1]) if "–" in cigarettes_amount else int(cigarettes_amount)
        else:
            avg_cigs = 0
    except:
        avg_cigs = 0

    # вейп — переведём "1–2 недели" в примерное число тяг в день
    vape_daily = 0
    if vape_amount == "Меньше недели":
        vape_daily = 2000
    elif vape_amount == "1–2 недели":
        vape_daily = 1000
    elif vape_amount == "2–4 недели":
        vape_daily = 500
    elif vape_amount == "Больше месяца":
        vape_daily = 300

    for _, cig, vape in records:
        spent += cig * price_per_cig + vape * price_per_puff
        would_spend += avg_cigs * price_per_cig + vape_daily * price_per_puff

    return round(would_spend - spent, 2)
#выбор периода для статистики
def handle_stats_command(message):
    user_states[message.chat.id] = "stats_period"
    return "Выбери период для статистики:", v.stats_period_keyboard(), None
#обработка выбранного периода
def handle_stats_period(message):
    period = message.text
    history = db.get_daily_tracking(message.chat.id)

    if not history:
        return None, "Нет данных для отображения статистики.", None

    if period == "📅 Неделя":
        data = history[-7:]
        caption = "📊 Твоя статистика за последнюю неделю"
    elif period == "📅 2 недели":
        data = history[-14:]
        caption = "📊 Твоя статистика за последние 2 недели"
    elif period == "📅 Месяц":
        data = history[-30:]
        caption = "📊 Твоя статистика за последний месяц"
    else:
        return None, "Выбери период с кнопок.", None

    buf = build_smoking_stats(data)
    return caption, None, buf






