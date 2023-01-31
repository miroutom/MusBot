import asyncio
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InputFile
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env.txt')
load_dotenv(dotenv_path=dotenv_path)

# логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
bot_token = os.getenv("BOT_TOKEN")
# объект бота
bot = Bot(token=bot_token)
# диспетчер
dp = Dispatcher(bot)


# хэндлер на команду /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Привет!')


@dp.message_handler(content_types=["audio", "photo"])
async def spectrogram(message: types.Message):
    audio_id = message.audio.file_id
    file_info = await bot.get_file(audio_id)
    try:
        await bot.download_file(file_info.file_path,
                                destination=f'D:\\PyCharm\\PyCharm 2022.3\\pythonProject\\{message.audio.file_unique_id}.mp3')
        await message.answer("Ваше аудио успешно скачано")
    except:
        await message.answer("Скачивание не удалось")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
