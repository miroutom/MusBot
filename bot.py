import gc
import logging
from aiogram import Bot, Dispatcher, types, executor
import os
from dotenv import load_dotenv
from pathlib import Path
from aiogram.types import InputFile
from pydub import AudioSegment
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np

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


def create_spectrogram(path_to_file: str, unique_id: str):
    input_file = f'{path_to_file}'
    output_file = f'{path_to_file}.wav'

    sound = AudioSegment.from_mp3(input_file)
    sound.export(output_file, format='wav')

    output_file_mono = f'{output_file}_mono.wav'

    stereo_audio = AudioSegment.from_file(output_file, format='wav')
    mono_audios = stereo_audio.split_to_mono()
    mono_left = mono_audios[0].export(output_file_mono, format='wav')

    samplerate, data = wavfile.read(output_file_mono)
    f, t, Sxx = spectrogram(data, samplerate)

    plt.pcolormesh(1000 * t, f / 1000, 10 * np.log10(Sxx / Sxx.max()), vmin=-120, vmax=0, cmap='inferno')
    plt.ylabel('Frequency [kHz]')
    plt.xlabel('Time [ms]')
    plt.colorbar()
    img = f'{unique_id}.png'
    plt.savefig(img)
    plt.clf()


@dp.message_handler(content_types=['audio', 'photo'])
async def show_spectrogram(message: types.Message):
    unique_id = ''
    audio_id = message.audio.file_id
    unique_id = message.audio.file_unique_id
    file_info = await bot.get_file(audio_id)
    path_to_file = f'D:\\PyCharm\\PyCharm 2022.3\\pythonProject\\{message.audio.file_unique_id}.mp3'

    try:
        await bot.download_file(file_info.file_path,
                                destination=f'D:\\PyCharm\\PyCharm 2022.3\\pythonProject\\{message.audio.file_unique_id}.mp3')
        await message.answer("Your audio is successfully downloaded")
    except:
        await message.answer("Error downloading")

    create_spectrogram(path_to_file, unique_id)
    
    try:
        with open(f"{unique_id}.png", 'rb') as photo:
            await message.answer_photo(photo, caption='Your spectrogram')
        photo.close()
        del photo
    except:
        await message.answer("Error showing")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
