from pydub import AudioSegment
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np
from matching import finish
import os

user_home_dir = os.path.expanduser('~')
user = os.path.split(user_home_dir)[-1]
disk = os.path.split(user_home_dir)[0]
common_path = os.path.join(disk, user, 'Desktop')

FRAME_SIZE = 2048
HOP_SIZE = 512

input_file = ''
output_file = ''


def create_spectrogram(path_to_file: str, unique_id: str):
    global input_file, output_file
    input_file = f'{path_to_file}'
    output_file = f'{path_to_file}.wav'

    if input_file[-3:] == 'mp3':
        sound = AudioSegment.from_mp3(input_file)
        sound.export(output_file, format='wav')
    elif input_file[-3:] == 'ogg':
        sound = AudioSegment.from_ogg(input_file)
        sound.export(output_file, format='wav')

    # output_file_mono = f'{output_file}_mono.wav'

    # stereo_audio = AudioSegment.from_file(output_file, format='wav')
    # mono_audios = stereo_audio.split_to_mono()
    # mono_left = mono_audios[0].export(output_file_mono, format='wav')

    samplerate, data = wavfile.read(output_file)
    try:
        f, t, Sxx = spectrogram(data[:, 0], samplerate, nperseg=FRAME_SIZE, \
                            noverlap=HOP_SIZE, window='hamming')
    except:
        f, t, Sxx = spectrogram(data, samplerate, nperseg=FRAME_SIZE, \
                                noverlap=HOP_SIZE, window='hamming')
    Sxx[Sxx == 0] = np.finfo(float).eps

    plt.pcolormesh(t, f / 1000, 10 * np.log10(Sxx / Sxx.max()), vmin=-120, \
                   vmax=0, cmap='inferno')
    plt.ylabel('Frequency [kHz]')
    plt.xlabel('Time [s]')
    plt.colorbar()
    img = f'{unique_id}.png'
    try:
        if not os.path.isdir('Created spectrograms'):
            os.chdir(common_path)
            os.mkdir('Created spectrograms')
    except:
        print()
    path = os.path.join(disk, user, 'Desktop', 'Created spectrograms', img)
    plt.savefig(path)
    plt.clf()