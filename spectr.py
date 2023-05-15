import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np
import os
from fingerprinting import get_peaks
from pydub import AudioSegment

user_home_dir = os.path.expanduser('~')
user = os.path.split(user_home_dir)[-1]
disk = os.path.split(user_home_dir)[0]
common_path = os.path.join(disk, user, 'Desktop')

FRAME_SIZE = 2 ** 12
HOP_SIZE = int(FRAME_SIZE * 0.5)

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

    samplerate, data = wavfile.read(output_file)

    try:
        f, t, Sxx = spectrogram(data[:, 0], samplerate, nperseg=FRAME_SIZE,
                                noverlap=HOP_SIZE, window='hamming')
    except:
        f, t, Sxx = spectrogram(data, samplerate, nperseg=FRAME_SIZE,
                                noverlap=HOP_SIZE, window='hamming')

    Sxx[Sxx == 0] = np.finfo(float).eps

    max_time = int(np.max(t))
    max_freq = int(np.max(f))

    spec_peaks = get_peaks(Sxx[:max_freq, :max_time])
    plot_peaks = np.array(spec_peaks)
    plot_peaks[:, 0] = (plot_peaks[:, 0] * max_freq) / len(f)

    plt.pcolormesh(t, f, 10 * np.log10(Sxx / Sxx.max()), vmin=-120,
                 vmax=0, cmap='inferno')
    plt.colorbar()
    plt.scatter(plot_peaks[:, 1], plot_peaks[:, 0], s=10, color='white')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [s]')

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