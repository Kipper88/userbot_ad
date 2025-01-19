from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InputMediaPhoto, BufferedInputFile, ContentType
from filter import isAdmin

import re
import os
import subprocess
import sys
import shutil

import asyncio
import json
from cfg import API_KEY

bot = Bot(API_KEY)
dp = Dispatcher()

dp.message.middleware.register(isAdmin())

process = None

async def load_json():
    with open('database/messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

async def process_photo(file, path):
    with open(path, 'wb') as f:
        f.write(file)
    


@dp.message(CommandStart())
async def start(message):
    await message.reply("Список команд:\n\n \
1. /show - показать список добавленных чатов на рассылку\n \
2. /showone [номер чата в списке] - показать чат из списка\n \
2. /change (номер чата int) - изменить параметры рассылки (поменять сообщение, поменять какие-либо параметры) (/add выполняет почти те же функции)\n \
3. /add - добавить чат. Форма:\n \
    chat_id: id чата (узнавать через AyuGram)\n \
    plus: период отправки сообщений\n \
    last_time: время старта в int - указывать не текущее время, а будущее (4 метод)\n \
    chat_url: ссылка на чат\n \
    message: сообщение\n \
4. /time - узнать текущее время\n \
5. /start_bot - включить юзербота для рассылки\n \
6. /stop_bot - выключить юзербота для рассылки\n \
                            ")
    
@dp.message(Command('time'))
async def get_time(message):
    await message.reply("https://www.unixtimestamp.com/ru/")
    
@dp.message(Command("show"))
async def show(message):
    data = await load_json()
    text = ''
    count = 0
    for i in data['messages']:
        text += f"{count+1}. {i['chat_url']}\n"
        
        count += 1
        
        
    text = 'Не найдено ни одного чата' if text == '' else text
    await message.reply(text)
    
@dp.message(Command('showone'))
async def showone(message):
    try:
        data = await load_json()
        key = int(message.text.split(' ')[1])
        text = ''
        i = data['messages'][key-1]
        
        text += f"id: {i['chat_id']}\n"
        text += f"last_time: {i['last_time']}\n"
        text += f"plus: {i['plus']}\n\n"
        text += i['message'].encode('utf-8').decode('utf-8')
        
        binary_ph = []
        count = 0
        for i in i['file_path']:
            with open(i, 'rb') as f:
                f = f.read()
                inp = BufferedInputFile(f, 'img.jpeg')
                if count == 0:
                    binary_ph.append(InputMediaPhoto(media=inp, caption=text))
                else:
                    binary_ph.append(InputMediaPhoto(media=inp))
                
                count += 1
                            
        await message.answer_media_group(binary_ph)    
    except:
        await message.answer('Произошла непредвиденная ошибка. Возможно, вы неверно ввели номер чата. Попробуйте:\n\n/showone number')
    
    
@dp.message(Command('add'))
async def add(message):
    data = await load_json()
    
    text = message.text if message.text else message.caption if message.caption else "No"
            
            
            
    
    pattern = r"""
        chat_id:\s*(?P<chat_id>-?\d+)\s*            # chat_id: целое число (может быть отрицательным)
        plus:\s*(?P<plus>\d+)\s*                    # plus: целое число
        last_time:\s*(?P<last_time>\d+)\s*          # last_time: целое число
        chat_url:\s*(?P<chat_url>https?://[^\s]+)\s* # chat_url: строка (URL)
        message:\s*(?P<message>.*)                  # message: любое сообщение (включая переносы строк)
    """
    
    match = re.search(pattern, text, re.VERBOSE | re.DOTALL)
    
    if match:
        id = int(match.group('chat_id'))
        # Создаем папку для сохранения изображений
        dir_path = f'src\\{id}'
        os.makedirs(dir_path, exist_ok=True)  # Создаем папку, если она не существует
        
        photos = message.photo

        if photos:
            photo = photos[-1]
            file_unique_id = photo.file_unique_id
                
                # Загрузка фотографии
            file_path = os.path.join(dir_path, f"{file_unique_id}.jpg")  # Сохраняем с уникальным именем

                # Загружаем фото
            file = await bot.download(photo.file_id)
            file = file.getvalue()
            await process_photo(file, file_path)
            
        extracted_data = {
            "chat_url": str(match.group('chat_url')),
            "chat_id": int(match.group('chat_id')),
            "file_path": [file_path],
            "plus": int(match.group('plus')),
            "last_time": int(match.group('last_time')),
            "message": match.group('message').strip()
        }
        
        d = data
        
        with open('database/messages.json', 'w') as f:
            d['messages'].append(extracted_data)  
                    
            json.dump(d, f, indent=4)
        
        await message.reply("Успешно добавлен чат. Посмотреть его можно с помощью команды /show")
    else:
        await message.reply('Неверно введена форма. Попробуйте снова')
        
@dp.message(Command('addphoto'), F.content_type == ContentType.PHOTO)
async def addphoto(message):
    pattern = r"id:\s*(?P<id>\d+)"
    
    match = re.search(pattern, message.caption)
    
    if match:
        id = int(match.group('id')) - 1
        
        data_js = await load_json()
        
        chat_id = data_js['messages'][id]['chat_id']
        dir_path = f'src\\{chat_id}'
        
        photos = message.photo
        if photos:
            photo = photos[-1]
            file_unique_id = photo.file_unique_id
                
                # Загрузка фотографии
            file_path = os.path.join(dir_path, f"{file_unique_id}.jpg")  # Сохраняем с уникальным именем

                # Загружаем фото
            file = await bot.download(photo.file_id)
            file = file.getvalue()
            await process_photo(file, file_path)

            data_js['messages'][id]['file_path'].append(file_path)
            with open('database/messages.json', 'w') as f:
                json.dump(data_js, f, indent=4)
                        
            
            await message.reply('Успешно добавлено')
    else:
        await message.reply('Не было введено поле id, либо оно отсутствует/неверно введено')
        
@dp.message(Command('edit'))
async def edit(message):
    pattern = r"""
        id:\s*(?P<id>-?\d+)\s*                    # id: целое число (может быть отрицательным)
        key:\s*(?P<key>.+?)\s*                    # key: строка (одна или более любых символов)
        value:\s*(?P<value>.+?)\s*                # value: текст или цифры (одна или более любых символов)
    """
    
    match = re.search(pattern, message.text, re.VERBOSE)
    
    d = await load_json()
    
    key = match.group("key")
    id = match.group("id")
    value = match.group('value')
    
    d['messages'][id][key] = value
    
    with open('database/messages.json', 'w') as f:
        json.dump(d, f, indent=4)
        
    await message.reply('Внесения успешно внесены')
    
@dp.message(Command('delete'))
async def delete(message):    
    pattern = r"id:\s*(?P<id>\d+)"
    
    match = re.search(pattern, message.text)
    
    if match:
        id = int(match.group('id')) - 1
        
        data_js = await load_json()
        
        chat_id = data_js['messages'][id]['chat_id']
        dir_path = f'src\\{chat_id}'
        
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        del data_js['messages'][id]
        with open('database/messages.json', 'w') as f:
            json.dump(data_js, f, indent=4)
        await message.reply('Успешно удалено')
    else:
        await message.reply('Не было введено поле id, либо оно отсутствует/неверно введено')
        
    
    

@dp.message(Command('start_bot'))
async def start_bot(message):
    global process
    if not process:
        process = subprocess.Popen([sys.executable, 'userbot.py'])
        await message.reply("Бот успешно запущен")
    else:
        await message.reply("Бот уже запущен")
    

@dp.message(Command('stop_bot'))
async def stop_bot(message):
    global process
    if process:
        process.kill()
        process = None
        await message.reply("Бот успешно выключен")
    else:
        await message.reply("Бот не был запущен")
        
        


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())