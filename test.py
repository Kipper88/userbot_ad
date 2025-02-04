import sqlite3
import json

# Загружаем JSON из файла (или вставьте строку напрямую)
with open("database/messages.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Подключаемся к базе данных (или создаем, если её нет)
conn = sqlite3.connect("messages.db")
cursor = conn.cursor()

# Создаем таблицу, если её нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_url TEXT,
        chat_id INTEGER,
        file_path TEXT,
        plus INTEGER,
        last_time REAL,
        message TEXT
    )
''')

# Вставляем данные
for msg in data["messages"]:
    file_paths = json.dumps(msg["file_path"])  # Преобразуем список в строку JSON
    cursor.execute('''
        INSERT INTO messages (chat_url, chat_id, file_path, plus, last_time, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (msg["chat_url"], msg["chat_id"], file_paths, msg["plus"], msg["last_time"], msg["message"]))

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Данные успешно добавлены в базу данных.")