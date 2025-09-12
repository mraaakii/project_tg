import sqlite3

DB_NAME = "users.db"

# Создание подключения к бд с отключённой проверкой потоков
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)
#создание таблицы users
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        smoking_status TEXT,
        smoking_type TEXT,
        cigarettes_amount TEXT,
        vape_amount TEXT,
        motivation TEXT,
        goal TEXT 
    )
    """)
    conn.commit()
    conn.close()

#Создаёт таблицу daily_tracking (учёт курения по дням)
def migrate_daily_tracking():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        cigarettes INTEGER DEFAULT 0,
        vape_puffs INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    conn.commit()
    conn.close()
    print("✅ Таблица daily_tracking создана или уже существует")

def save_user(user_id, username, smoking_status=None, smoking_type=None, cigarettes_amount=None, vape_amount=None, motivation=None, goal=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, username, smoking_status, smoking_type, cigarettes_amount, vape_amount, motivation, goal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, smoking_status, smoking_type, cigarettes_amount, vape_amount,  motivation, goal))
    conn.commit()
    conn.close()

#Обновляет одно поле в таблице users
def update_user_field(user_id, field, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit()
    conn.close()

#Возвращает данные пользователя по user_id
def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_daily_tracking(user_id, date, cigarettes=0, vape_puffs=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Проверяем, есть ли уже запись на эту дату для этого юзера
    cursor.execute("""
        SELECT id FROM daily_tracking WHERE user_id = ? AND date = ?
    """, (user_id, date))
    record = cursor.fetchone()

    if record:
        # Обновляем запись
        cursor.execute("""
            UPDATE daily_tracking
            SET cigarettes = ?, vape_puffs = ?
            WHERE user_id = ? AND date = ?
        """, (cigarettes, vape_puffs, user_id, date))
    else:
        # Создаём новую запись
        cursor.execute("""
            INSERT INTO daily_tracking (user_id, date, cigarettes, vape_puffs)
            VALUES (?, ?, ?, ?)
        """, (user_id, date, cigarettes, vape_puffs))

    conn.commit()
    conn.close()
    print(f"✅ Данные сохранены: user_id={user_id}, date={date}, cig={cigarettes}, vape={vape_puffs}")

#Возвращает список всех записей (дата, сигареты, вейп) для конкретного пользователя
def get_daily_tracking(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, cigarettes, vape_puffs 
        FROM daily_tracking
        WHERE user_id = ? ORDER BY date ASC
    """, (user_id,))

    records = cursor.fetchall()
    conn.close()
    return records
    ''' if record:
        cigarettes, vape_puffs = record
        return {
            "cigarettes": cigarettes,
            "vape_puffs": vape_puffs
        }
    else:
        return None'''

#Возвращает список всех user_id
def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

#Возвращает время напоминания для пользователя
def get_user_reminder_time(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reminder_time FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else "21:00"

#Добавляет в таблицу users колонку reminder_time
def add_reminder_field():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        ALTER TABLE users ADD COLUMN reminder_time TEXT DEFAULT '21:00'
    """)
    conn.commit()
    conn.close()
    print("✅ Поле reminder_time добавлено")

    """
    Добавляет поля для отслеживания стриков (серий без курения).
    last_smoke_date → дата последнего курения
    current_streak → текущий стрик
    max_streak → максимальный стрик
    """
def add_streak_columns():
    conn = get_connection()
    cursor = conn.cursor()
    # Проверка, есть ли колонки, чтобы не падало на ALTER TABLE
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_smoke_date TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN max_streak INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def add_price_fields():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN cigarette_price REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN vape_price REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_daily_tracking()
    #add_reminder_field()
    #add_streak_columns()
    #add_price_fields()