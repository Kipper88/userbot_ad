from pyrogram import Client
from pyrogram.types import InputMediaPhoto
from io import BytesIO
import json
import asyncio
import time
import logging

# Импорт конфигурации
from cfg import *

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger("MyApp")

# Подключение к Pyrogram
app = Client('session_name', 26851519, "abe97f63a8836d5c9b69df440b8fd1d2")

# Функция загрузки JSON с обработкой ошибок
async def load_json():
    try:
        with open('database/messages.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug("JSON-файл успешно загружен")
        return data
    except json.JSONDecodeError:
        logger.error("Ошибка чтения JSON, возможно, файл поврежден")
        return {"messages": []}
    except FileNotFoundError:
        logger.error("Файл messages.json не найден")
        return {"messages": []}

# Проверка времени сообщений
async def check_time():
    d = await load_json()
    d = d['messages']
    ids = []
    for i in d:
        if time.time() > i['last_time'] + i['plus']:
            ids.append({"chat_id": i['chat_id'], "file_path": i['file_path'], "message": i['message']})
    logger.info(f"Найдено {len(ids)} сообщений для отправки")
    return ids if ids else None

# Функция отправки фото
async def send_photos_with_descriptions(chat_id, file_path, message, key):
    binary_photos = []
    count = 0
    
    for i in file_path:
        try:
            with open(i, 'rb') as f:
                file = f.read()
                with BytesIO(file) as binary:
                    if count == 0:
                        binary_photos.append(InputMediaPhoto(binary, message))
                    else:
                        binary_photos.append(InputMediaPhoto(binary))
                    count += 1
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {i}: {e}")
            return
    
    it = 0
    while it < 5:
        try:
            await asyncio.wait_for(app.send_media_group(chat_id, binary_photos), timeout=30)
            logger.info(f"Фото успешно отправлены в чат {chat_id}")
            break
        except asyncio.TimeoutError:
            logger.warning("send_media_group timeout, повторная попытка...")
        except Exception as e:
            logger.error(f"Ошибка при отправке фото: {e}")
        await asyncio.sleep(10)
        it += 1

    # Обновление времени в JSON
    try:
        with open('database/messages.json', 'r', encoding='utf-8') as f:
            d = json.load(f)
        d['messages'][key]['last_time'] = time.time()
        with open('database/messages.json', 'w', encoding='utf-8') as file:
            json.dump(d, file, indent=4)
        logger.debug("JSON-файл успешно обновлен")
    except Exception as e:
        logger.error(f"Ошибка обновления JSON: {e}")

# Основная асинхронная функция
async def main():
    await app.start()
    logger.info("Бот запущен и работает")
    while True:
        try:
            logger.info("Проверка сообщений...")
            t = await check_time()
            
            if t:
                for idx, i in enumerate(t):
                    logger.info(f"Отправка сообщения в {i['chat_id']}")
                    await send_photos_with_descriptions(i['chat_id'], i['file_path'], i['message'], idx)
                    await asyncio.sleep(5)
            
            await asyncio.sleep(5)
        except Exception as err:
            logger.error(f"Ошибка в основном цикле: {err}", exc_info=True)

if __name__ == "__main__":
    app.run(main())
