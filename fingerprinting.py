from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure,
                                      binary_erosion)
from scipy.ndimage.filters import maximum_filter


# function to generate a fingerprint of an audio file
def finger_print(audio_file):
    # read audio file
    samplerate, data = wavfile.read(audio_file)
    # generate spectrogram
    try:
        f, t, Sxx = spectrogram(data[:, 0], samplerate)
    except:
        f, t, Sxx = spectrogram(data, samplerate)
    # replace zeros with epsilon to handle divide by zero errors
    Sxx[Sxx == 0] = np.finfo(float).eps
    # take logarithm of spectrogram
    log_spectrogram = np.log(Sxx)
    fingerprint = log_spectrogram.flatten()
    return fingerprint


def get_peaks(spectrogram, no_of_iteration=10, min_amplitude=10):
    structure = generate_binary_structure(2, 2)
    neighborhood = iterate_structure(structure, no_of_iteration)

    local_max = maximum_filter(spectrogram, footprint=neighborhood) == spectrogram
    background = (spectrogram == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # applying XOR between matrices to get boolean mask of spectrogram
    detected_peaks = local_max ^ eroded_background

    # getting peaks, their freqs and times
    peaks = spectrogram[detected_peaks].flatten()
    peak_freqs, peak_times = np.where(detected_peaks)

    peak_idx = np.where(peaks > min_amplitude)

    freqs = peak_freqs[peak_idx]
    times = peak_times[peak_idx]

    return list(zip(freqs, times))
