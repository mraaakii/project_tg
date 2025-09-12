import sqlite3

DB_NAME = "users.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

print("Users:")
for row in cursor.execute("SELECT * FROM users"):
    print(row)

print("\nDaily tracking:")
for row in cursor.execute("SELECT * FROM daily_tracking"):
    print(row)

conn.close()