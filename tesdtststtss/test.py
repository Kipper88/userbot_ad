# import asyncio
# import json
# from pyrogramv2 import Client

# # Конфигурация для Pyrogram
# API_ID = 23808169  # Замените на ваш api_id
# API_HASH = "b0e2ecd46aff626b28178cf3e230d85b"  # Замените на ваш api_hash
# SESSION_NAME = "session_name"  # Название сессии

# # Путь к файлу JSON
# JSON_FILE = "messages.json"

# async def join_groups(app, json_file):
#     try:
#         # Чтение JSON-файла
#         with open(json_file, "r", encoding="utf-8") as file:
#             data = json.load(file)

#         # Обрабатываем список групп
#         messages = data.get("messages", [])
#         for message in messages:
#             chat_url = message.get("chat_url").split('/')[-1]
#             if chat_url:
#                 x = 0
#                 while x < 2:
#                     try:
#                         print(f"Попытка присоединиться к {chat_url}...")
#                         await app.join_chat(chat_url)
#                         print(f"Успешно присоединились к {chat_url}")
#                         break
#                     except Exception as e:
#                         print(f"Ошибка при присоединении к {chat_url}: {e}")
#                         await asyncio.sleep(30)
#                         x+=1
                
                    
#             else:
#                 print("URL чата отсутствует в одном из объектов.")
#     except Exception as e:
#         print(f"Ошибка при чтении файла JSON: {e}")

# async def main():
#     async with Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH) as app:
#         await join_groups(app, JSON_FILE)

# if __name__ == "__main__":
#     asyncio.run(main())

import requests

# Настройки прокси
proxies = {
    "http": "http://8.211.42.167:1234"
}

# Выполнение GET-запроса через прокси
try:
    response = requests.get("https://api.ipify.org?format=json", proxies=proxies)
    print(f"Ответ: {response.json()}")  # Должен вернуть IP, используемый для запроса
except requests.exceptions.RequestException as e:
    print(f"Ошибка запроса: {e}")


