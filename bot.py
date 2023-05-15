import logging
import threading

from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
from pathlib import Path
from pyglet.media import Player, load

from spectr import create_spectrogram
from matching import finish, finish_debug, get_song
import os

dotenv_path = Path('.env.txt')
load_dotenv(dotenv_path=dotenv_path)

# logging so don't miss important messages
logging.basicConfig(level=logging.INFO)
bot_token = os.getenv("BOT_TOKEN")
# bot's object
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

command = ''


# handler for /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Hello! I'm music recognizing bot. Waiting for your commands...")


@dp.message_handler(commands=['run'])
async def run(message: types.Message):
    global command
    command = 'run'
    await message.answer("Send me an audiofile or voice message. I'll show you its title")


@dp.message_handler(commands=['debug'])
async def debug(message: types.Message):
    global command
    command = 'debug'
    await message.answer("Send me an audiofile or voice message. I'll show you its title "
                         "and some additional info")


player = None


def play_audio(audio_file):
    global player
    player = Player()
    source = load(audio_file)
    player.queue(source)
    player.play()


def stop_audio():
    global player
    if player is not None:
        player.pause()
        player.delete()
        player = None


@dp.callback_query_handler(lambda c: c.data == 'play')
async def play_callback_handler(callback_query: types.CallbackQuery):
    audio_file = get_song()
    threading.Thread(target=play_audio, args=(audio_file,)).start()


@dp.callback_query_handler(lambda c: c.data == 'stop')
async def stop_callback_handler(callback_query: types.CallbackQuery):
    stop_audio()


@dp.message_handler(commands=['play'])
async def play_music(message: types.Message):
    audio_file = get_song()
    await bot.send_audio(message.chat.id, audio=open(audio_file, 'rb'))


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer('All commands:\n'
                         '/start - run bot\n'
                         '/run - waiting for audio and shows its title\n'
                         '/debug - gives an additional info of your file\n'
                         '/play - sends an audio player')


user_home_dir = os.path.expanduser('~')
user = os.path.split(user_home_dir)[-1]
disk = os.path.split(user_home_dir)[0]
common_path = os.path.join(disk, user, 'Desktop')

try:
    if not os.path.isdir('Downloaded audio'):
        os.chdir(common_path)
        os.mkdir('Downloaded audio')
except:
    print()


# handler for audio messages, voice messages and photos
@dp.message_handler(content_types=['audio', 'voice'])
async def show_spectrogram(message: types.Message):
    global command
    unique_id = path_to_file = file_info = ''
    # getting a directory for saving a file
    directory = os.path.join(disk, user, 'Desktop', 'Downloaded audio')
    # checking a type of message
    if message.audio is not None:
        audio_id = message.audio.file_id
        unique_id = message.audio.file_unique_id
        file_info = await bot.get_file(audio_id)
        path_to_file = os.path.join(directory, f'{unique_id}.mp3')
    elif message.voice is not None:
        audio_id = message.voice.file_id
        unique_id = message.voice.file_unique_id
        file_info = await bot.get_file(audio_id)
        path_to_file = os.path.join(directory, f'{unique_id}.ogg')

    # downloading a file
    try:
        await bot.download_file(file_info.file_path,
                                destination=os.path.join(path_to_file))
        await message.answer("Your audio is successfully downloaded")
    except:
        await message.answer("Error downloading")

    print(command)
    if command == 'run':
        create_spectrogram(path_to_file, unique_id)

        path_to_photo = os.path.join(disk, user, 'Desktop',
                                     'Created spectrograms', f'{unique_id}.png')
        try:
            await message.answer(finish())
        except:
            await message.answer("I'm Sorry. Something went wrong...")
    elif command == 'debug':
        create_spectrogram(path_to_file, unique_id)

        path_to_photo = os.path.join(disk, user, 'Desktop',
                                     'Created spectrograms', f'{unique_id}.png')
        # showing spectrogram
        try:
            with open(path_to_photo, 'rb') as photo:
                await message.answer_photo(photo, caption='Your spectrogram')
            photo.close()
        except:
            await message.answer("Error showing")

        try:
            await message.answer(finish_debug())
        except:
            await message.answer("I'm Sorry. Something went wrong...")
    else:
        await message.answer('Try some existed commands, please')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
