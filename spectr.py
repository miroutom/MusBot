from pydub import AudioSegment
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np


def create_spectrogram(path_to_file: str, unique_id: str):
    input_file = f'{path_to_file}'
    output_file = f'{path_to_file}.wav'

    if input_file[-3:] == 'mp3':
        sound = AudioSegment.from_mp3(input_file)
        sound.export(output_file, format='wav')
    elif input_file[-3:] == 'ogg':
        sound = AudioSegment.from_ogg(input_file)
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