import os
import pandas as pd
from sk_speech import sk_volume as vm

def analyze_audio_files(directory):
    # Списки для хранения данных
    data_file_1 = []

    # Инициализация нейтральной речи
    options = {"freq": True, "amplitude": True, "period": True, "slope": True,
               "pitch": True, "formants": True, "vowels": False, "formant_max": 5}
    speech = vm.init_speech(os.path.join(directory, "neutral_1_0.wav"), options=options)  # Укажите файл с нейтральной речью

    # Обход всех файлов в указанной папке и подпапках
    for subdir, _, files in os.walk(directory):
        for file in files:
            # Проверка, является ли файл WAV и соответствует ли формату имени
            if file.endswith(".wav") and "_" in file:
                emotion = file.split("_")[0]  # Извлечение названия эмоции
                file_path = os.path.join(subdir, file)

                # Получение параметров речи
                cur_speech = vm.speech_params(file_path, speech)

                # Извлечение значений из параметров речи
                f0_period = cur_speech['params']['f0']['period']
                time = f0_period['time']
                offset = f0_period['offset']
                amplitude = f0_period['amplitude']

                f0_period_n = speech['params']['norm']['f0']['period']
                half_time = cur_speech['params']["duration"] / 2

                # Приведение к нулю в случае None
                if f0_period_n['time'] == 0:
                    time_normalized = 0
                else:
                    time_normalized = time / f0_period_n['time'] if time is not None and f0_period_n['time'] is not None else 0
                if f0_period_n['offset'] == 0:
                    offset_normalized = 0
                else:
                    offset_normalized = offset / f0_period_n['offset'] if offset is not None and f0_period_n['offset'] is not None else 0
                if f0_period_n['amplitude'] == 0:
                    amplitude_normalized = 0
                else:
                    amplitude_normalized = amplitude / f0_period_n['amplitude'] if amplitude is not None and f0_period_n['amplitude'] is not None else 0

                type_data = 'монотонность'
                if amplitude and amplitude > 10:
                    if time_normalized < 1.0:
                        type_data = 'нервозность'
                    elif time_normalized > 1.0:
                        type_data = 'мелодичность'
                    else:
                        type_data = 'тревожность'
                    # if time < half_time:
                    #     type_data = 'нервозность'
                    # elif time > half_time:
                    #     type_data = 'мелодичность'
                    # else:
                    #     type_data = 'тревожность'

                # Сохранение в первый файл
                data_file_1.append([emotion, time, offset, amplitude,
                                    time_normalized, offset_normalized, amplitude_normalized, type_data
                                    ])

    # Создание DataFrame для сохранения в CSV
    df_file_1 = pd.DataFrame(data_file_1, columns=['Emotion', 'Time', 'Offset', 'Amplitude','Time_in_norm', 'Offset_in_norm', 'Amplitude_in_norm', 'TypeData'])

    # Сохранение в файлы
    df_file_1.to_csv('file_J.csv', index=False)

# Укажите директорию с аудиофайлами
directory_path = 'emotionsJ'
analyze_audio_files(directory_path)
