from pyrogramv2 import client
from pyrogramv2.types import InputMediaPhoto
from io import BytesIO

import json
import asyncio
import time
import logging

from cfg import *

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат сообщения
    datefmt="%Y-%m-%d %H:%M:%S",  # Формат даты
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8")  # Логирование в файл
    ]
)

# Создание логгера
logger = logging.getLogger("MyApp")

app = client.Client('session_name', 26851519, "abe97f63a8836d5c9b69df440b8fd1d2")
app.start()


async def load_json():
    with open('database/messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

async def check_time():
    d = await load_json()
    d = d['messages']
    
    ids = []
    for i in d:
        if time.time() > i['last_time'] + i['plus']: # 24h
            ids.append({"chat_id": i['chat_id'], "file_path": i['file_path'], "message": i['message']})
    if len(ids) != 0:
        return ids
        
        

async def send_photos_with_descriptions(chat_id, file_path, message, key, app):      
    binary_photos = []
    count = 0
    for i in file_path:
        with open(i, 'rb') as f:
            file = f.read()
            binary = BytesIO(file)

            if count == 0:
                binary_photos.append(InputMediaPhoto(binary, message))
                count += 1
            else: 
                binary_photos.append(InputMediaPhoto(binary))
    
    it = True
    while it:
        try:   
            await app.send_media_group(chat_id, binary_photos)
            it = False
        except Exception as e:
            time.sleep(5)
            continue
    
    with open('database/messages.json', 'r') as f:
        d = json.load(f)

    d['messages'][key]['last_time'] = time.time()
    with open('database/messages.json', 'w', encoding='utf-8') as file:
        json.dump(d, file, indent=4)
        
async def main():
    while True:
        try:
            t = await check_time()
            
            if t:
                it = 0
                for i in t:
                    await send_photos_with_descriptions(i['chat_id'], i['file_path'], i['message'], it, app)
                    it += 1
                    await asyncio.sleep(60)

            await asyncio.sleep(5)
        except Exception as err:
            logger.error(str(err), exc_info=True)
        
if __name__ == "__main__":
    app.run(main())