import logging
from aiogram import Bot, Dispatcher, types, executor
import os
from dotenv import load_dotenv
from pathlib import Path
from spectr import create_spectrogram


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
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer('Hello!')


@dp.message_handler(content_types=['audio', 'voice', 'photo'])
async def show_spectrogram(message: types.Message):
    unique_id = path_to_file = format_file = file_info = ''
    if message.audio is not None:
        audio_id = message.audio.file_id
        unique_id = message.audio.file_unique_id
        file_info = await bot.get_file(audio_id)
        path_to_file = f'D:\\PyCharm\\PyCharm 2022.3\\pythonProject\\{unique_id}.mp3'
        format_file = 'mp3'
    elif message.voice is not None:
        audio_id = message.voice.file_id
        unique_id = message.voice.file_unique_id
        file_info = await bot.get_file(audio_id)
        path_to_file = f'D:\\PyCharm\\PyCharm 2022.3\\pythonProject\\{unique_id}.ogg'
        format_file = 'ogg'

    try:
        await bot.download_file(file_info.file_path,
                                destination=f'D:\\PyCharm\\PyCharm 2022.3\\pythonProject\\{unique_id}.{format_file}')
        await message.answer("Your audio is successfully downloaded")
    except:
        await message.answer("Error downloading")

    create_spectrogram(path_to_file, unique_id)

    try:
        with open(f"{unique_id}.png", 'rb') as photo:
            await message.answer_photo(photo, caption='Your spectrogram')
        photo.close()
    except:
        await message.answer("Error showing")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)