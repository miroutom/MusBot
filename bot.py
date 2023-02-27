import logging
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
from pathlib import Path
from spectr import create_spectrogram
import os

dotenv_path = Path('.env.txt')
load_dotenv(dotenv_path=dotenv_path)

# logging so don't miss important messages
logging.basicConfig(level=logging.INFO)
bot_token = os.getenv("BOT_TOKEN")
# bot's object
bot = Bot(token=bot_token)
dp = Dispatcher(bot)


# handler for /start
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer('Hello!')


user_home_dir = os.path.expanduser('~')
user = os.path.split(user_home_dir)[-1]
disk = os.path.split(user_home_dir)[0]
common_path = os.path.join(disk, user, 'Desktop')

try:
    if not os.path.isdir('Downloaded audio'):
        os.chdir(common_path)
        os.mkdir('Downloaded audio"')
except:
    print()


# handler for audio messages, voice messages and photos
@dp.message_handler(content_types=['audio', 'voice', 'photo'])
async def show_spectrogram(message: types.Message):
    unique_id = path_to_file = format_file = file_info = ''
    # getting a directory for saving a file
    directory = os.path.join(disk, user, 'Desktop', 'Downloaded audio')
    # checking a type of message
    if message.audio is not None:
        audio_id = message.audio.file_id
        unique_id = message.audio.file_unique_id
        file_info = await bot.get_file(audio_id)
        path_to_file = os.path.join(directory, f'{unique_id}.mp3')
        format_file = 'mp3'
    elif message.voice is not None:
        audio_id = message.voice.file_id
        unique_id = message.voice.file_unique_id
        file_info = await bot.get_file(audio_id)
        path_to_file = os.path.join(directory, f'{unique_id}.ogg')
        format_file = 'ogg'

    # downloading a file
    try:
        await bot.download_file(file_info.file_path,
                                destination=os.path.join(path_to_file))
        await message.answer("Your audio is successfully downloaded")
    except:
        await message.answer("Error downloading")

    create_spectrogram(path_to_file, unique_id)

    path_to_photo = os.path.join(disk, user, 'Desktop', 'Created spectrograms', f'{unique_id}.png')
    # showing spectrogram
    print(path_to_photo)
    try:
        with open(path_to_photo, 'rb') as photo:
            await message.answer_photo(photo, caption='Your spectrogram')
        photo.close()
    except:
        await message.answer("Error showing")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
