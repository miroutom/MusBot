import numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram
import os
import spectr


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
    # flatten spectrogram to generate fingerprint
    fingerprint = log_spectrogram.flatten()
    return fingerprint


# function to calculate cosine distance between two fingerprints
def cosine_distance(x, y):
    # pad the smaller fingerprint with zeros to match the size of the larger fingerprint
    if len(x) < len(y):
        x = np.pad(x, (0, len(y) - len(x)), mode='constant')
    elif len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)), mode='constant')
    # calculate cosine distance
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))


# function to find the closest match for an audio file in a given set of fingerprints
def find_closest_match(audio_file, fingerprint_maps):
    # generate fingerprint for query audio file
    query_fp = finger_print(audio_file)
    # initialize maximum distance and closest match
    max_distance = 0
    closest_match = ''
    # iterate through fingerprint maps and find closest match
    for key in fingerprint_maps:
        # calculate cosine distance between query fingerprint and current fingerprint
        distance = cosine_distance(query_fp, fingerprint_maps[key])
        # update maximum distance and closest match if a closer match is found
        if distance > max_distance:
            max_distance = distance
            closest_match = key
    # return closest match and its distance from query audio file
    return closest_match, max_distance


# prompt user to enter directory path containing audio files
# path = input("Enter the directory path where your music files are located: ")
# # validate directory path
# while True:
#     try:
#         if not os.path.exists(path):
#             raise FileNotFoundError
#         break
#     except FileNotFoundError:
#         print("Invalid directory path!")
#         path = input("Enter the directory path where your music files are located: ")

path = "D:\\PyCharm\\PyCharm Community Edition 2023.1\\pythonProject\\music"

# generate fingerprints for all audio files in directory
fingerprint_maps = {}
for file_name in os.listdir(path):
    if file_name.endswith('.wav'):
        audio_file_path = os.path.join(path, file_name)
        try:
            fp = finger_print(audio_file_path)
            fingerprint_maps[file_name] = fp
        except Exception as e:
            print(f"Error processing file {audio_file_path}: {e}")


# prompt user to enter path of audio file to match
# audio = input("Enter the path of the audio file you want to match: ")
# # validate audio file path
# while True:
#     try:
#         if not os.path.exists(audio):
#             raise FileNotFoundError
#         break
#     except FileNotFoundError:
#         print("Invalid audio file path!")
#         audio = input("Enter the path of the audio file you want to match: ")

def finish():
    audio = os.path.join(spectr.output_file)
    # find closest match for query audio file
    closest_match, max_distance = find_closest_match(audio, fingerprint_maps)

    # print closest match and its distance from query audio file
    return f"Closest match found: {closest_match} with distance {max_distance}"
