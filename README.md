# MusBot. Телеграм бот для распознавания музыки
## Задача
Разработать аналог приложения "Shazam" - Телеграм бота для распознавания музыки через голосовые или музыкальные файлы формата MP3.
## Анализ предметной области
Для того, чтобы представить музыку в удобном для Shazam или любого другого сервиса виде, мы выделили следующие шаги преобразования:
1.	Анализ частот. Преобразование Фурье;
2.	Создание «карты созвездий»;
3.	Устранение времени.
### Анализ частот. Преобразование Фурье
Преобразование Фурье - математический метод, позволяющий представить музыку в её первоначальном виде – до того, как все частоты смешались в один поток. 

![image](https://github.com/miroutom/MusBot/assets/78901500/77eaa2fc-dc6d-461c-bad0-95892ac39333)


Использование данного метода позволяет нам получить график, именуемый спектрограммой, показывающий зависимость частот (ось Y) от времени (ось X). Ниже представлена реализация метода Фурье с помощью библиотеки `scipy`.

![image](https://github.com/miroutom/MusBot/assets/78901500/9a675d4c-bb5a-4753-83e9-867a3ac7f747)


### Создание "карты созвездий"
Создание "карты созвездий" или "отпечатка" композиции - это процесс анализа спектрограммы и выделения на ней самых ярких областей в каждый момент времени. Использование данной карты позволяет сократить размер композиции, а также удалить все лишние звуки.


![image](https://github.com/miroutom/MusBot/assets/78901500/81934d68-afd0-425c-a8bf-1d1200152929)


### Устранение времени
На данном этапе возникла довольно серьёзная проблема - записанный пользователем фрагмент может оказаться в любом моменте песни: будь то начало, середина или конец. В итоге, алгоритм примет совершенно другую карту. Поэтому на данном шаге было принято решение найти какую-то опорную точку O и связать её с несколькими другими точками. Так, вместо конкретных частот с привязкой ко времени, мы храним информацию о том, как эти частоты связаны между собой. 

## Реализация алгоритма

### Обработка аудио. Создание спектрограммы
Для создания спектрограммы сперва нужно было выбрать необходимую библиотеку. Мы предпочли `scipy`, так как в сравнении с её не менее известным аналогом `librosa`, она гораздо быстрее.
```Python
from scipy.io import wavfile
from scipy.signal import spectrogram
```
Данная библиотека обрабатывает аудиофайлы в формате WAV. Но поскольку мы решили, что бот будет принимать форматы MP3 и OGG, необходимо было сделать предварительную обработку.
```Python
    if input_file[-3:] == 'mp3':
        sound = AudioSegment.from_mp3(input_file)
        sound.export(output_file, format='wav')
    elif input_file[-3:] == 'ogg':
        sound = AudioSegment.from_ogg(input_file)
        sound.export(output_file, format='wav')
```

После чего файл проверяется на количество каналов в нём (`scipy` обрабатывает только одноканальную музыку) и исходя из этого создаётся спектрограмма.
```Python
    try:
        f, t, Sxx = spectrogram(data[:, 0], samplerate, nperseg=FRAME_SIZE,
                                noverlap=HOP_SIZE, window='hamming')
    except:
        f, t, Sxx = spectrogram(data, samplerate, nperseg=FRAME_SIZE,
                                noverlap=HOP_SIZE, window='hamming')
```

Затем данная картинка отображается при помощи использования библиотеки `matplotlib`.

![image](https://github.com/miroutom/MusBot/assets/78901500/89943812-6d59-4afa-a537-08c473e9eb5c)


### Создание "карты созвездий"
Данный этап был значительно упрощён в виду того, что библиотеки, реализующие `fingerprinting` оказались устаревшими или изменёнными, поэтому было принятно решение создать карту созвездий с использованием `np.array` и функции `flatten`, преобразовывающей многомерный массив в одномерный.
```Python
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
```

### Нахождение наибольшего совпадения
Для нахождения наибольшего совпадения мы написали функцию косинусного расстояния между векторами, работающей по следующему принципу:
1. Уравнять размеры векторов, заполнив меньший нулями
2. Вычислить скалярное произведение и норму векторов
3. Рассчитать косинусное расстояние как скалярное произведение, поделённое на произведение норм
```Python
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
```
