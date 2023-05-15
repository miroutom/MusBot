import numpy as np
import os
import spectr
from fingerprinting import finger_print
from pydub import AudioSegment
from mutagen.mp3 import MP3


def cosine_distance(x, y):
    # pad the smaller fingerprint with zeros to match the size of the larger fingerprint
    if len(x) < len(y):
        x = np.pad(x, (0, len(y) - len(x)), mode='constant')
    elif len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)), mode='constant')
    # calculate cosine distance
    dot_product = np.dot(x, y)
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)
    return dot_product / (norm_x * norm_y)


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


path = "D:\\PyCharm\\PyCharm Community Edition 2023.1\\pythonProject\\music"

# generate fingerprints for all audio files in directory
fingerprint_maps = {}
for file_name in os.listdir(path):
    file_path = os.path.join(path, file_name)
    if file_path.endswith(".mp3"):
        # convert mp3 file to wav format
        output_file = os.path.join(path, f"{os.path.splitext(file_name)[0]}.wav")
        sound = AudioSegment.from_mp3(file_path)
        sound.export(output_file, format='wav')
        try:
            fp = finger_print(output_file)
            fingerprint_maps[file_name] = fp
        except Exception as e:
            print(f"Error processing file {output_file}: {e}")
        finally:
            # delete the wav file
            os.remove(output_file)


def get_duration(audio_file):
    audio_ = MP3(audio_file)
    duration_ = audio_.info.length
    minutes = int(duration_ // 60)
    seconds = int(duration_ % 60)
    duration_format = f"{minutes:02d}:{seconds:02d}"
    return duration_format


def finish():
    audio = os.path.join(spectr.output_file)
    # find closest match for query audio file
    closest_match_, max_distance_ = find_closest_match(audio, fingerprint_maps)
    path_to_file = os.path.join(path, closest_match_)
    duration = get_duration(path_to_file)
    # print closest match
    return f"Song: {closest_match_[:-4]}\nDuration: {duration}"


def finish_debug():
    audio = os.path.join(spectr.output_file)
    # find closest match for query audio file
    closest_match_, max_distance_ = find_closest_match(audio, fingerprint_maps)
    path_to_file = os.path.join(path, closest_match_)
    duration = get_duration(path_to_file)
    # print closest match
    return f"Song: {closest_match_[:-4]}\nDuration: {duration}\nDistance: {max_distance_}"


def get_song():
    audio = os.path.join(spectr.output_file)
    # find closest match for query audio file
    closest_match_, max_distance_ = find_closest_match(audio, fingerprint_maps)
    path_to_file = os.path.join(path, closest_match_)
    return path_to_file
