from pyrogram import Client
from pyrogram.errors import RPCError
from pyrogram.types import InputMediaPhoto
from io import BytesIO
import json
import asyncio
import time
import logging
import random

from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler(
    "app.log",  # Имя файла
    maxBytes=5 * 1024 * 1024,  # 5 MB лимит
    backupCount=3,  # Хранить 3 старых файла (app.log.1, app.log.2, ...)
    encoding="utf-8"
)

# Импорт конфигурации
from cfg import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[log_handler, logging.StreamHandler()]
)
logger = logging.getLogger("MyApp")


# Функция выбора и проверки работоспособности прокси
async def get_working_proxy():
    random.shuffle(proxies) # Перемешиваем список прокси
    for proxy in proxies:
        logger.info(f"Пробуем прокси: {proxy}")
        app = Client('session', api_id=api_id, api_hash=api_hash, proxy=proxy)
        try:
            await app.start()
            user = await app.get_me()
            if user:
                logger.info(f"Прокси {proxy} работает, бот авторизован как {user.username}")
                return app  # Возвращаем рабочий клиент
        except Exception as e:
            logger.warning(f"Прокси {proxy} не работает: {e}")
        finally:
            if app.is_connected:
                await app.stop()

    logger.error("Нет рабочих прокси, бот не может запуститься.")
    return None


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
    messages = d['messages']
    ids = []
    
    for msg in messages:
        if time.time() > msg['last_time'] + msg['plus']:
            ids.append(msg)
    
    logger.info(f"Найдено {len(ids)} сообщений для отправки")
    return ids if ids else None


# Функция обновления времени отправки в JSON
async def update_message_time(chat_id, file_path):
    try:
        with open('database/messages.json', 'r', encoding='utf-8') as f:
            d = json.load(f)

        for msg in d['messages']:
            if msg['chat_id'] == chat_id and msg['file_path'] == file_path:
                msg['last_time'] = time.time()
                break

        with open('database/messages.json', 'w', encoding='utf-8') as file:
            json.dump(d, file, indent=4)

        logger.debug(f"Обновлено время отправки для чата {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка обновления JSON: {e}")


# Функция отправки фото
async def send_photos_with_descriptions(app, chat_id, file_path, message):
    binary_photos = []
    binary_streams = []  # Список для хранения открытых потоков
    count = 0

    for i in file_path:
        try:
            with open(i, 'rb') as f:
                file_content = f.read()
            
            binary = BytesIO(file_content)
            binary.seek(0)
            binary_streams.append(binary)  # Добавляем в список, чтобы не закрывался до конца отправки
            
            if count == 0:
                binary_photos.append(InputMediaPhoto(binary, message))
            else:
                binary_photos.append(InputMediaPhoto(binary))
            
            count += 1
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {i}: {e}", exc_info=True)
            return

    it = 0
    while it < 5:
        try:
            await asyncio.wait_for(app.send_media_group(chat_id, binary_photos), timeout=30)
            logger.info(f"Фото успешно отправлены в чат {chat_id}")

            # После успешной отправки обновляем время в JSON
            await update_message_time(chat_id, file_path)
            break
        except asyncio.TimeoutError:
            logger.warning("send_media_group timeout, повторная попытка...")
        except Exception as e:
            logger.error(f"Ошибка при отправке фото: {e}")
        await asyncio.sleep(10)
        it += 1

    # Закрытие потоков после отправки
    for binary in binary_streams:
        binary.close()


# Функция основного цикла с автоматическим переподключением
async def run_bot():
    app = None

    while True:
        try:
            if app and not app.is_connected:
                await app.stop()  # Останавливаем старый клиент перед созданием нового

            app = await get_working_proxy()
            if not app:
                logger.error("Не удалось подключиться, повторяем через 30 секунд...")
                await asyncio.sleep(30)
                continue

            await app.start()
            logger.info("Бот запущен и работает")

            while True:
                try:
                    if not app.is_connected:  # Проверяем, не отключился ли клиент
                        raise ConnectionError("Pyrogram отключился, требуется переподключение")

                    logger.info("Проверка сообщений...")
                    messages = await check_time()

                    if messages:
                        for msg in messages:
                            logger.info(f"Отправка сообщения в {msg['chat_id']}")
                            await send_photos_with_descriptions(app, msg['chat_id'], msg['file_path'], msg['message'])
                            await asyncio.sleep(5)

                    await asyncio.sleep(5)

                except (RPCError, ConnectionError) as err:
                    logger.error(f"Ошибка соединения: {err}, переподключение через 30 секунд...")
                    break  # Выход из вложенного цикла, чтобы перезапустить клиента

        except Exception as err:
            logger.error(f"Ошибка в основном цикле: {err}", exc_info=True)

        logger.info("Перезапуск бота через 30 секунд...")
        await asyncio.sleep(30)  # Ожидание перед повторной попыткой подключения


# Запуск бота
if __name__ == "__main__":
    asyncio.run(run_bot())
