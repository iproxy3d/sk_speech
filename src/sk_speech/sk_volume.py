import time
import math
import pickle
import json
import os
import copy
import librosa
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d
from pydub import AudioSegment
from audiostretchy.stretch import stretch_audio
from . import sk_filters as fl
from . import sk_noise as ns
from . import sk_pitch as pt
from . import sk_formants as fmt
from . import sk_vowels as vw
from . import sk_vocal_tract as vk
from . import sk_detection as dt
from ._resources import data_path

def create_empty_value(template_speech=False):
    return {
        "f0": create_empty_formant(),
        "f1": create_empty_formant(),
        "f2": create_empty_formant(),
        "f3": create_empty_formant(),
        "f4": create_empty_formant(),
        "f5": create_empty_formant(),
        "duration": 0,
        "vowels": {"vowel_boundaries": [(0, 'i'), (0, 'u'), (0, 'o'), (0, 'a'), (0, 'e')],
                   "amplitude": {'i': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                                 'u': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                                 'o': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                                 'a': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                                 'e': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                                 },
                   "energy": {'i': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                              'u': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                              'o': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                              'a': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                              'e': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                              },
                   "freq": {'i': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                            'u': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                            'o': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                            'a': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                            'e': {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0, },
                            },
                   "count": 0},
        "speed": 0,
        "cmax": 0,
        "cmin": 0,
        "amplitude_db": 0,
        "template_speech": template_speech,
        "gender": '',
    }


def create_empty_formant():
    return {
        "freq": 0,
        "bandwidth": 0,
        "energy": 0,
        "intensity": 0,
        "amplitude": 0,
        "slope": 0,
        "period": {"time": 0, "offset": 0, "amplitude": 0},
        "count": 0
    }

def load_vectors_from_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            speech = json.load(f)
    else:
        speech = {
            "params": {
                "norm": create_empty_value(True),
                "volume_up": {"emotion_up": create_empty_value(True), "emotion_down": create_empty_value(True)},
                "volume_down": {"emotion_up": create_empty_value(True), "emotion_down": create_empty_value(True)},
            },
            "vectors": {
                "volume_up": {"emotion_up": create_empty_value(True), "emotion_down": create_empty_value(True)},
                "volume_down": {"emotion_up": create_empty_value(True), "emotion_down": create_empty_value(True)},
            },
            "files": {
                "norm": None,
                "volume_up": {"emotion_up": None, "emotion_down": None},
                "volume_down": {"emotion_up": None, "emotion_down": None},
            },
        }
    return speech

def _load_bundled_vectors(file_name):
    """Load a default profile from package data, independent of cwd."""

    with data_path(file_name) as file_path:
        return load_vectors_from_json(file_path)


# Default profiles are shipped with the installed package.
default_speech_man = _load_bundled_vectors('speech_vectors_man.json')
default_speech_woman = _load_bundled_vectors('speech_vectors_woman.json')

def trim_silence(y, sr, top_db=20, apply_noise_reduction=False):
    """Удаляет тишину в начале и в конце аудиофайла и при необходимости применяет шумоподавление."""
    if apply_noise_reduction:
        y = ns.noise_reduction_spectral_subtraction_fast(y, sr)

    # Тримминг тишины
    y_trimmed = librosa.effects.trim(y, top_db=top_db)[0]

    return y_trimmed

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def trim_silence_pydub(sound):
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)
    trimmed_sound = sound[start_trim:duration - end_trim]
    return trimmed_sound

def calculate_intensity_avg(y, sr):
    # Рассчитайте интенсивность питча
    pitch_intensity = np.abs(pt.calculate_pitch_intensity(y, sr))
    count = 1
    combined_intensity = np.mean(pitch_intensity)

    # Рассчитайте интенсивность для каждой форманты
    for formant_index in range(1, 6):
        formant_intensity = np.abs(fmt.calculate_formant_intensity(y, sr, formant_index))

        if len(formant_intensity) > 0:
            combined_intensity = combined_intensity + np.mean(formant_intensity)
            count += 1

    combined_intensity /= count

    # Нормализуем для сравнения с интенсивностью питча
    # if len(pitch_intensity) > 0:
    #     combined_intensity = np.clip(combined_intensity, 0, np.max(pitch_intensity))

    return combined_intensity

def calculate_intensity_max(y, sr):
    # Рассчитайте интенсивность питча
    pitch_intensity = np.abs(pt.calculate_pitch_intensity(y, sr))
    combined_intensity = np.mean(pitch_intensity)

    # Рассчитайте интенсивность для каждой форманты
    for formant_index in range(1, 6):
        formant_intensity = np.abs(fmt.calculate_formant_intensity(y, sr, formant_index))

        if len(formant_intensity) > 0:
            combined_intensity = max(combined_intensity, np.mean(formant_intensity))

    # Нормализуем для сравнения с интенсивностью питча
    # if len(pitch_intensity) > 0:
    #     combined_intensity = np.clip(combined_intensity, 0, np.max(pitch_intensity))

    return combined_intensity

def transition(V_norm, V_loud, alpha):
    return V_norm * (1 - alpha) + V_loud * alpha

def calculate_pitch_shift_semitones(frequency_change):
    base_frequency = 440  # Средняя частота, например, нота Ля
    new_frequency = base_frequency + frequency_change
    semitones = 12 * np.log2(new_frequency / base_frequency)
    return semitones

def energy_speech(volume):
    # Нормальная энергия для формант
    E_F_norm = [1.0, 1.0, 1.0, 1.0, 1.0]

    if 0 <= volume <= 1.0:
        E_F = [1.2, 1.2, 1.2, 1.2, 1.2]
        alpha = volume
        pitch_shift_hz = 30
        energy_pitch_factor = 2.0
        formant_shifts = [10, 20, 15, 20, 20]  # Примерные значения для громкой речи
        formant_bandwidth_factors = [1.2, 1.2, 1.2, 1.2, 1.2]
    elif -1.0 <= volume < 0:
        E_F = [0.8, 0.7, 0.6, 0.7, 0.6]
        alpha = abs(volume)
        pitch_shift_hz = -30
        energy_pitch_factor = 0.5
        formant_shifts = [-10, -20, -15, -20, -20]  # Примерные значения для тихой речи
        formant_bandwidth_factors = [0.8, 0.8, 0.8, 0.8, 0.8]
    elif 1 < volume:
        E_F = [1.5, 1.2, 1.0, 1.1, 1.0]
        alpha = volume * 0.5
        pitch_shift_hz = 50
        energy_pitch_factor = 3.0
        formant_shifts = [30, 50, 40, 50, 50]  # Примерные значения для кричащей речи
        formant_bandwidth_factors = [1.5, 1.5, 1.5, 1.5, 1.5]
    elif volume < -1.0:
        E_F = [0.4, 0.3, 0.2, 0.3, 0.2]
        alpha = abs(volume) * 0.5
        pitch_shift_hz = -60
        energy_pitch_factor = 0.1
        formant_shifts = [-30, -50, -40, -50, -50]  # Примерные значения для шёпота
        formant_bandwidth_factors = [0.5, 0.5, 0.5, 0.5, 0.5]
    else:
        E_F = [0, 0, 0, 0, 0]
        alpha = 0
        pitch_shift_hz = 0
        energy_pitch_factor = 1.0
        formant_shifts = [0, 0, 0, 0, 0]
        formant_bandwidth_factors = [1.0, 1.0, 1.0, 1.0, 1.0]

    # Вычисление множителя для изменения энергий формант
    formant_energy_factors = [transition(E_F_norm[i], E_F[i], alpha) for i in range(5)]
    # Вычисление сдвига частот формант
    formant_shifts = [transition(0, formant_shifts[i], alpha) for i in range(5)]
    # Вычисление множителя для изменение ширины канала формант
    formant_bandwidth_factors = [transition(1.0, formant_bandwidth_factors[i], alpha) for i in range(5)]
    # Вычисление множителя для изменения энергий тона
    energy_pitch_factor = transition(1.0, energy_pitch_factor, alpha)
    # Вычисление сдвига частот тона
    pitch_shift_hz = transition(0.0, pitch_shift_hz, alpha)
    pitch_shift_semitones = calculate_pitch_shift_semitones(pitch_shift_hz)

    # Множители усиления энергии формант гласных для различных типов речи
    if 0 <= volume <= 1.0:
        formant_energy_vowel = {
            'a': formant_energy_factors,
            'e': formant_energy_factors,
            'i': [formant_energy_factors[0], formant_energy_factors[1] * 1.5, formant_energy_factors[2] * 1.5,
                  formant_energy_factors[3]],
            'o': formant_energy_factors,
            'u': formant_energy_factors,
        }
    elif -1.0 <= volume < 0:
        formant_energy_vowel = {
            'a': formant_energy_factors,
            'e': formant_energy_factors,
            'i': [formant_energy_factors[0], formant_energy_factors[1] * 0.8, formant_energy_factors[2] * 0.8,
                  formant_energy_factors[3]],
            'o': formant_energy_factors,
            'u': formant_energy_factors,
        }
    elif 1 < volume :
        formant_energy_vowel = {
            'a': [factor * 1.5 for factor in formant_energy_factors],
            'e': [factor * 1.5 for factor in formant_energy_factors],
            'i': [formant_energy_factors[0] * 1.8, formant_energy_factors[1] * 2.0, formant_energy_factors[2] * 2.0,
                  formant_energy_factors[3] * 1.5],
            'o': [factor * 1.5 for factor in formant_energy_factors],
            'u': [factor * 1.5 for factor in formant_energy_factors],
        }
    elif volume < -1.0:
        formant_energy_vowel = {
            'a': [factor * 0.5 for factor in formant_energy_factors],
            'e': [factor * 0.5 for factor in formant_energy_factors],
            'i': [formant_energy_factors[0] * 0.6, formant_energy_factors[1] * 0.4, formant_energy_factors[2] * 0.4,
                  formant_energy_factors[3] * 0.5],
            'o': [factor * 0.5 for factor in formant_energy_factors],
            'u': [factor * 0.5 for factor in formant_energy_factors],
        }

    return energy_pitch_factor, pitch_shift_semitones, formant_bandwidth_factors, formant_energy_factors, formant_shifts, formant_energy_vowel


def change_speech_volume(y, sr, volume, is_noise = False, is_shift = False):
    # для тихой речи
    # boost_dB = [-10, -15, -10, -5, -5]  # Уменьшение амплитуды для F1, F2, F3, F4, F5
    # pitch_shift_hz = -10  # Снижение основного тона
    # formant_shifts = {
    #     'a': [-10, -10, -10, -5, -5],
    #     'e': [-10, -10, -10, -5, -5],
    #     'i': [-10, -10, -10, -5, -5],
    #     'o': [-10, -10, -10, -5, -5],
    #     'u': [-10, -10, -10, -5, -5],
    # }

    # formant_gains_dict = {
    #     'a': [-10, -15, -10, -5],
    #     'e': [-10, -15, -10, -5],
    #     'i': [-10, -15, -10, -5],
    #     'o': [-10, -15, -10, -5],
    #     'u': [-10, -15, -10, -5],
    # }
    # formant_shifts_dict = {
    #     'a': [-10, -10, -10, -5],
    #     'e': [-10, -10, -10, -5],
    #     'i': [-10, -10, -10, -5],
    #     'o': [-10, -10, -10, -5],
    #     'u': [-10, -10, -10, -5],
    # }
    energy_pitch_factor = 3
    energy_pitch_factor = 2

    formant_energy_factors = [4, 5, 6, 7, 8]
    formant_energy_factors = [2, 3, 2, 1.5, 1.2]

    # множители усиления энергии формант гласных для кричащей речи
    formant_energy_dict = {
        'a': [4, 5, 4, 3.5],  # Усиление для гласной 'a' (например, F1, F2, F3, F4)
        'e': [4, 5, 4, 3.5],  # Усиление для гласной 'e'
        'i': [4, 6, 5, 4],  # Усиление для гласной 'i' (более высокий F2 и F3)
        'o': [4, 5, 4, 3.5],  # Усиление для гласной 'o'
        'u': [4, 5, 4, 3.5],  # Усиление для гласной 'u'
    }

    # Увеличение амплитуды для каждой форманты
    # F1: 10-15 дБ
    # F2: 10-20 дБ
    # F3: 5-15 дБ
    # F4: 5-15 дБ
    # F5: 5-15 дБ
    boost_dB = [10, 10, 5, 5, 5]  # Initial amplitude factors

    formant_gains_dict = {
        'a': [10, 15, 10, 5],  # Усиление для гласной 'a' в dB (например, F0, F1, F2, F3)
        'e': [10, 15, 10, 5],  # Усиление для гласной 'e'
        'i': [10, 20, 15, 10],  # Усиление для гласной 'i' (более высокий F2 и F3)
        'o': [10, 15, 10, 5],  # Усиление для гласной 'o'
        'u': [10, 15, 10, 5],  # Усиление для гласной 'u'
    }

    # Изменение pitch на 30 Гц
    # Мужчины +25-35 Гц
    # Женщины +35-45 Гц
    # Дети +50 Гц
    pitch_shift_hz = 10  # Приращение частоты основного тона в Гц

    # Значения сдвига формант в Гц
    formant_shifts = [30, 50, 40, 50, 50]  # Значение сдвига для F1, F2, F3, F4, F5

    formant_shifts_dict = {
        'a': [70, 60, 60, 50],
        'e': [50, 50, 50, 50],
        'i': [30, 60, 40, 50],
        'o': [50, 50, 50, 50],
        'u': [50, 50, 50, 50],
    }

    formant_bandwidth_factors = {
        'F1': 1.75,  # Увеличение в среднем в 1.75 раза
        'F2': 1.55,  # Увеличение в среднем в 1.55 раза
        'F3': 1.55,  # Увеличение в среднем в 1.55 раза
        'F4': 1.35,  # Увеличение в среднем в 1.35 раза
        'F5': 1.35  # Увеличение в среднем в 1.35 раза
    }

    for vowel, value in formant_gains_dict.items():
        for r in range(4):
            value[r] = (value[r] - boost_dB[r]) * volume
    for r in range(5):
        boost_dB[r] = boost_dB[r] * volume
    for vowel, value in formant_energy_dict.items():
        for r in range(4):
            # value[r] = (value[r] - formant_energy_factors[r]) * volume
            value[r] = value[r] * volume
    # for r in range(5):
    #     formant_energy_factors[r] = (formant_energy_factors[r] - energy_pitch_factor) * volume
    # for r in range(5):
    #     formant_energy_factors[r] = formant_energy_factors[r] * volume
    for r in range(5):
        formant_energy_factors[r] = formant_energy_factors[r] - 1.0

    for vowel, value in formant_shifts_dict.items():
        for r in range(4):
            value[r] = (value[r] - formant_shifts[r]) * volume
    # for r in range(5):
    #     formant_shifts[r] = (formant_shifts[r] - pitch_shift_hz) * volume

    pitch_shift_hz = pitch_shift_hz * volume  # Целевая частота основного тона в Гц
    # energy_pitch_factor = energy_pitch_factor * volume

    # При переходе от гласной к согласной или наоборот, амплитуда будет изменяться постепенно,
    # создавая области повышенной энергии вокруг гласных.
    # frame_duration = 0.10 # seconds (100 ms) изменяемое окно вокруг гласной
    # frame_duration = 0.3 # seconds (100 ms) изменяемое окно вокруг гласной

    frame_duration = 0.3 * max(volume, 0)  # seconds (100 ms) изменяемое окно вокруг гласной

    if is_noise:
        # Apply spectral subtraction for noise reduction
        y = ns.noise_reduction_spectral_subtraction(y, sr, noise_profile_sec=0.5, num_iterations=3,
                                                    high_pass=True, low_pass=True, normalize=False, target_dBFS=-20.0)

    # Вызов функций
    if frame_duration > 0:
        threshold = 0.1
        boundaries_with_types = vw.detect_vowel_boundaries(y, sr, threshold)

        # print("Границы гласных найдены на следующих индексах с указанием типа гласной:")
        # for boundary, vowel_type in boundaries_with_types:
        #     print(f"Индекс: {boundary}, Тип гласной: {vowel_type}")

    # Максимальная амплитуда в dB
    max_amplitude_dB = -3
    max_amplitude_dB = 0

    (energy_pitch_factor, pitch_shift_semitones, formant_bandwidth_factors, formant_energy_factors, formant_shifts,
     formant_energy_vowel) = energy_speech(volume)

    # Затем изменяем ширину канала формант
    # formant_bandwidth_factors = [1.5, 1.5, 1.5, 1.5, 1.5]  # Пример коэффициентов для изменения ширины канала формант
    # formant_bandwidth_factors = [1.5, 1.5, 1.5, 1.5, 1.5]  # Пример коэффициентов для изменения ширины канала формант
    y = fmt.change_formant_bandwidth(y, sr, formant_bandwidth_factors)

    # Увеличение амплитуды для каждой форманты
    # y = fmt.boost_formants_peak(y, sr, boost_dB, max_amplitude_dB)
    # y = fmt.change_formant_energy2(y, sr, formant_energy_factors)
    # formant_energy_factors = [2, 3, 2, 1.5, 1.2]
    y = fmt.change_formant_energy4(y, sr, formant_energy_factors)

    # formant_energy_vowel = {
    #     'a': [2, 3, 2, 1.5],
    #     'e': [2, 3, 2, 1.5],
    #     'i': [2, 4, 3, 2],
    #     'o': [2, 3, 2, 1.5],
    #     'u': [2, 3, 2, 1.5]
    # }

    if is_shift:
        # сдвиг формант
        y, sr = fmt.change_formants_shifts3(y, sr, formant_shifts)

    # Увеличение амплитуды каждой гласной
    if frame_duration > 0:
        # y = vw.amplify_vowels(y, sr, boundaries_with_types, formant_gains_dict, frame_duration)
        y = vw.energy_vowels(y, sr, boundaries_with_types, formant_energy_vowel, frame_duration)

        # сдвиг формант гласных
        if frame_duration > 0:
            y = vw.apply_formant_shifts_vowels(y, sr, boundaries_with_types, formant_shifts_dict, frame_duration)
    #
    #     avg_f0 = pt.extract_f0(y, sr)
    #     pitch_shift_semitones = fl.hz_to_semitones(avg_f0+pitch_shift_hz, avg_f0)
    #     y, sr = pt.change_pitch_pydub(y, sr, pitch_shift_semitones)

    # pitch_shift_semitones = 2
    # y, sr = pt.change_pitch_pydub(y, sr, pitch_shift_semitones)

    # energy_pitch_factor = 2
    if energy_pitch_factor != 0:
        y, sr = pt.change_pitch_energy(y, sr, energy_pitch_factor)

    return y

def change_volume(y, sr, volume_from, volume_to, is_noise = False, is_shift = False):
    volume = max(abs(volume_from), abs(volume_to))
    if volume:
        y_filtered = change_speech_volume(y, sr, volume, is_noise, is_shift)

        # Mix
        if volume_from != volume_to:
            start_mix_ratio = volume_from / volume  # Mix ratio at the beginning of the file (20% original, 80% filtered)
            end_mix_ratio = volume_to / volume  # Mix ratio at the end of the file (80% original, 20% filtered)

            y_filtered = mix_audio(y, y_filtered, start_mix_ratio, end_mix_ratio)
        return y_filtered
    else:
        return y

def compute_spectral_slope(y, sr, window_size=1024, hop_size=512):
    """
    Рассчитывает спектральный наклон для аудиосигнала.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param window_size: Размер окна для анализа.
    :param hop_size: Шаг между окнами.
    :return: Массив спектральных наклонов и временных меток.
    """
    slopes = []
    times = []

    num_windows = (len(y) - window_size) // hop_size + 1

    for i in range(num_windows):
        start = i * hop_size
        end = start + window_size
        segment = y[start:end]

        if len(segment) < window_size:
            # Если сегмент меньше чем window_size, пропускаем его
            continue

        # Применение окна для уменьшения утечек спектра
        windowed_segment = segment * np.hamming(window_size)

        # Вычисление спектра
        spectrum = np.abs(np.fft.fft(windowed_segment))
        frequencies = np.fft.fftfreq(window_size, 1 / sr)

        # Пропуск частот меньше 0
        positive_freqs = frequencies[frequencies > 0]
        positive_spectrum = spectrum[frequencies > 0]

        if len(positive_freqs) == 0 or len(positive_spectrum) == 0:
            continue

        # Логарифм спектра мощности
        log_Pxx = np.log(positive_spectrum + 1e-10)  # Добавляем маленькое число для предотвращения логарифма нуля

        # Линейная регрессия для расчета спектрального наклона
        X = positive_freqs.reshape(-1, 1)  # Частоты в качестве независимой переменной
        reg = LinearRegression().fit(X, log_Pxx)
        slope = reg.coef_[0]

        slopes.append(slope)
        times.append(start / sr + window_size / (2 * sr))  # Среднее время для окна

    return times, slopes

def change_volume_linear(audio_path, output_path, start_db, end_db):
    # Загрузка аудиофайла
    audio = AudioSegment.from_file(audio_path)

    # Длительность аудиофайла в миллисекундах
    duration_ms = len(audio)

    # Разделение аудиофайла на сегменты для постепенного увеличения громкости
    num_steps = 100  # количество шагов интерполяции
    step_duration_ms = duration_ms // num_steps

    # Создание нового аудиофайла с увеличенной громкостью
    new_audio = AudioSegment.empty()

    for i in range(num_steps):
        # Расчет текущего уровня громкости
        current_db = start_db + (end_db - start_db) * (i / num_steps)
        segment_start = i * step_duration_ms
        segment_end = min((i + 1) * step_duration_ms, duration_ms)
        segment = audio[segment_start:segment_end]

        # Применение увеличения громкости к сегменту
        segment = segment + current_db

        # Добавление сегмента к новому аудиофайлу
        new_audio += segment

    # Сохранение нового аудиофайла
    new_audio.export(output_path, format="wav")

def change_audio_volume(y, sr, volume_factor):
    # Умножаем сигнал на коэффициент громкости
    modified_signal = y * volume_factor

    # Убеждаемся, что значения не выходят за пределы [-1, 1]
    modified_signal = np.clip(modified_signal, -1.0, 1.0)

    return modified_signal, sr

def mix_audio(y_orig, y_filtered, start_mix_ratio=1.0, end_mix_ratio=1.0):
    # Ensure both audio signals have the same length
    min_length = min(len(y_orig), len(y_filtered))
    y_orig = y_orig[:min_length]
    y_filtered = y_filtered[:min_length]

    # Calculate mix ratios for each sample
    num_samples = len(y_orig)
    mix_ratios = np.linspace(start_mix_ratio, end_mix_ratio, num_samples)

    # Mix the audio signals based on the mix ratios
    y_mixed = y_orig * (1 - mix_ratios) + y_filtered * mix_ratios

    # Save the mixed audio
    return y_mixed

def get_tract_length(y, sr):
    # Определение частоты форманты
    total = 0
    tract_length = {"avg": 0.0, 'f1': 0.0, 'f2': 0.0, 'f3': 0.0, 'f4': 0.0, 'f5': 0.0}
    for formant_index in range(1, 6):
        avg_formant_freq = fmt.get_formant_frequency_by_index(y, sr, formant_index)
        L = vk.get_tract_length_from_formant(avg_formant_freq, formant_index)*100
        total += L
        tract_length[f'f{formant_index}'] = L

    tract_length["avg"] = total / 5.0

    return tract_length

def get_tract_length_expended(y, sr):
    # Определение частоты форманты
    total = 0
    tract_length = {"avg": 0.0, 'f1': 0.0, 'f2': 0.0, 'f3': 0.0, 'f4': 0.0, 'f5': 0.0, 'f6': 0.0, 'f7': 0.0}
    frequencies, times, bandwidths, intensities = fmt.formant_frequencies_expended(y, sr, speech=True,
                                                                                   max_number_of_formants=7)
    for formant_index in range(6, 8):
        avg_formant_freq = np.nanmean(frequencies[formant_index-1])
        L = vk.get_tract_length_from_formant(avg_formant_freq, formant_index)*100
        total += L
        tract_length[f'f{formant_index}'] = L

    tract_length["avg"] = total / 2.0


    return tract_length


def calculate_loudness_corrections(frequencies):
    """
    Рассчитывает поправочные коэффициенты для восприятия громкости на основе частот.
    :param frequencies: массив частот (в Гц)
    :return: массив поправочных коэффициентов в дБ для каждой частоты
    """
    reference_frequencies = [50, 100, 200, 500, 1000, 2000, 3000, 4000, 5000, 5500]
    reference_corrections = [12, 6, 3, 1, 0, -3, -6, -8, -10, -12]
    
    loudness_correction_function = interp1d(reference_frequencies, reference_corrections, kind='linear', fill_value="extrapolate")
    
    return loudness_correction_function(frequencies)

def calculate_speech_volume(frequencies, amplitudes_db, combine_mode="amplitude"):
    """
    Рассчитывает суммарную громкость речи с учетом поправок для восприятия громкости.
    :param frequencies: массив частот (в Гц)
    :param amplitudes_db: массив относительных цифровых амплитуд в дБ
    :param combine_mode: ``amplitude`` складывает линейные амплитуды;
        ``power`` складывает мощности независимых компонент
    :return: скорректированная относительная амплитуда в дБ. Это не dB SPL
        без отдельной калибровки микрофона.
    """
    # Фильтруем валидные частоты и амплитуды (исключаем NaN)
    frequencies = np.asarray(frequencies, dtype=float)
    amplitudes_db = np.asarray(amplitudes_db, dtype=float)
    if frequencies.shape != amplitudes_db.shape:
        raise ValueError("frequencies and amplitudes_db must have the same shape")
    valid_indices = np.isfinite(frequencies) & (frequencies > 0) & np.isfinite(amplitudes_db)
    valid_frequencies = frequencies[valid_indices]
    valid_amplitudes_db = amplitudes_db[valid_indices]

    if len(valid_frequencies) == 0:
        return -float('inf')  # Нет валидных данных для расчета

    # Получаем поправочные коэффициенты для громкости
    loudness_corrections_db = calculate_loudness_corrections(valid_frequencies)
    
    # Применяем поправочные коэффициенты
    corrected_amplitudes_db = [amp_db + correction for amp_db, correction in zip(valid_amplitudes_db, loudness_corrections_db)]
    
    if combine_mode == "amplitude":
        combined = np.sum(10 ** (np.asarray(corrected_amplitudes_db) / 20))
        speech_amplitude_db = 20 * np.log10(combined) if combined > 0 else -float('inf')
    elif combine_mode == "power":
        combined = np.sum(10 ** (np.asarray(corrected_amplitudes_db) / 10))
        speech_amplitude_db = 10 * np.log10(combined) if combined > 0 else -float('inf')
    else:
        raise ValueError("combine_mode must be 'amplitude' or 'power'")
    
    return min(speech_amplitude_db, 0)


def calculate_formant_energy(amplitude_db, bandwidth):
    """
    Рассчитывает энергию форманты на основе амплитуды в дБ и ширины канала.
    :param amplitude_db: Амплитуда форманты в децибелах
    :param bandwidth: Ширина канала форманты в Гц
    :return: Энергия форманты
    """
    # Преобразование амплитуды из дБ в линейные величины
    amplitude_linear = 10 ** (amplitude_db / 20)

    # Расчет энергии форманты
    energy = amplitude_linear ** 2 * bandwidth

    return energy

def get_speech_params(y, sr, template_speech=False, options=None):
    if options is None:
        options = copy.deepcopy({
            "freq": True, "bandwidth": True, "energy": True, "intensity": True,
            "amplitude": True, "slope": True, "period": True, "formant_period": True,
            "pitch": True, "formants": True, "vowels": True, "formant_max": 5,
            "change": {
                "pitch_freq": True, "pitch_amplitude": False,
                "formant_freq": False, "formant_amplitude": True,
                "vowel_freq": False, "vowel_amplitude": False,
            },
            "duration": True, "speed": True, "gender": True, "tract": True,
            "check_speech": True,
        })
    speech = {"f0": {"freq": 0, "freq_min": 0, "freq_max": 0,
                     "bandwidth": 0, "bandwidth_min":0, "bandwidth_max": 0,
                     "energy": 0, "energy_min":0, "energy_max": 0,
                     "intensity": 0, "intensity_min":0, "intensity_max": 0,
                     "amplitude": 0, "amplitude_min":0, "amplitude_max": 0, "amplitude_from":0, "amplitude_to": 0,
                     "slope": 0, "slope_min":0, "slope_max": 0,
                     "amplitude_slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},},
              "f1": {"freq": 0, "freq_min": 0, "freq_max": 0,
                     "bandwidth": 0, "bandwidth_min":0, "bandwidth_max": 0,
                     "energy": 0, "energy_min":0, "energy_max": 0,
                     "intensity": 0, "intensity_min":0, "intensity_max": 0,
                     "amplitude": 0, "amplitude_min":0, "amplitude_max": 0, "amplitude_from":0, "amplitude_to": 0,
                     "slope": 0, "slope_min":0, "slope_max": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},},
              "f2": {"freq": 0, "freq_min": 0, "freq_max": 0,
                     "bandwidth": 0, "bandwidth_min":0, "bandwidth_max": 0,
                     "energy": 0, "energy_min":0, "energy_max": 0,
                     "intensity": 0, "intensity_min":0, "intensity_max": 0,
                     "amplitude": 0, "amplitude_min":0, "amplitude_max": 0, "amplitude_from":0, "amplitude_to": 0,
                     "slope": 0, "slope_min":0, "slope_max": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},},
              "f3": {"freq": 0, "freq_min": 0, "freq_max": 0,
                     "bandwidth": 0, "bandwidth_min":0, "bandwidth_max": 0,
                     "energy": 0, "energy_min":0, "energy_max": 0,
                     "intensity": 0, "intensity_min":0, "intensity_max": 0,
                     "amplitude": 0, "amplitude_min":0, "amplitude_max": 0, "amplitude_from":0, "amplitude_to": 0,
                     "slope": 0, "slope_min":0, "slope_max": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},},
              "f4":{"freq": 0, "freq_min": 0, "freq_max": 0,
                     "bandwidth": 0, "bandwidth_min":0, "bandwidth_max": 0,
                     "energy": 0, "energy_min":0, "energy_max": 0,
                     "intensity": 0, "intensity_min":0, "intensity_max": 0,
                     "amplitude": 0, "amplitude_min":0, "amplitude_max": 0, "amplitude_from":0, "amplitude_to": 0,
                     "slope": 0, "slope_min":0, "slope_max": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},},
              "f5": {"freq": 0, "freq_min": 0, "freq_max": 0,
                     "bandwidth": 0, "bandwidth_min":0, "bandwidth_max": 0,
                     "energy": 0, "energy_min":0, "energy_max": 0,
                     "intensity": 0, "intensity_min":0, "intensity_max": 0,
                     "amplitude": 0, "amplitude_min":0, "amplitude_max": 0, "amplitude_from":0, "amplitude_to": 0,
                     "slope": 0, "slope_min":0, "slope_max": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},},
              "duration": 0,
              "vowels": {"vowel_boundaries": [], "amplitude": [], "energy": [], "freq": [], },
              "template_speech": False,
              "speed": 0,
              "cmax": 0,
              "cmin": 0,
              "gender": '',
              "options": {},
              "info": {"pitch": None, "formants": None, "vowel_formants": None, }
              }
    speech["template_speech"] = template_speech
    speech["options"] = options
    speech["duration"] = librosa.get_duration(y=y, sr=sr)

    # Определяем, pitch, там где есть речь
    if options.get("pitch", False):

        is_speech = options.get("check_speech", True)
        pitch = pt.get_pitch_info(y, sr, speech=is_speech)
        if len(pitch["frequencies"])==0 and is_speech:
            pitch = pt.get_pitch_info(y, sr, speech=False)
        speech["info"]["pitch"] = pitch
        f0 = pitch["frequencies"]

        if options.get("duration", False):
            speech["duration"] = pt.calculate_pitch_duration(y, sr, pitch=pitch)

        if f0.size > 0 and not np.isnan(f0).all():
            f0_freq_avg = np.nanmean(f0)
            speech["f0"]["freq"] = f0_freq_avg
            if options.get("bandwidth", False):
                speech["f0"]["bandwidth"] = pt.calculate_pitch_bandwidth(y, sr, pitch=pitch)
            if options.get("energy", False):
                speech["f0"]["energy"] = pt.calculate_pitch_energy(y, sr, pitch=pitch)
            if options.get("intensity", False):
                speech["f0"]["intensity"] = pt.calculate_pitch_intensity_avg(y, sr, pitch=pitch)
            if options.get("amplitude", False):
                amp = pt.calculate_pitch_amplitude(y, sr, pitch=pitch)
                speech["f0"]["amplitude"] = amp
                speech["f0"]["amplitude_from"] = amp
                speech["f0"]["amplitude_to"] = amp
                slope, variance, trend = pt.calculate_intensity_slope(y, sr, is_smooth=True, is_peak=True, pitch=pitch)
                speech["f0"]["amplitude_slope"] = slope

            if options.get("period", False):
                pitch_period, pitch_offset, pitch_amplitude = pt.extract_pitch_rate(y, sr, pitch=pitch)
                speech["f0"]["period"]["time"] = pitch_period
                speech["f0"]["period"]["offset"] = pitch_offset
                speech["f0"]["period"]["amplitude"] = pitch_amplitude
            if options.get("slope", False):
                slope, variance, trend = pt.calculate_pitch_slope(y, sr, is_smooth=True, is_peak=True, pitch=pitch)
                speech["f0"]["slope"] = slope

            if options.get("duration", False):
                speech["f0"]["period"]["time_min"] = 0
                speech["f0"]["period"]["time_max"] = speech["duration"]

                speech["f0"]["period"]["offset_min"] = -speech["duration"]
                speech["f0"]["period"]["offset_max"] = speech["duration"]

            speech["f0"]["period"]["amplitude_min"] = 5
            speech["f0"]["period"]["amplitude_max"] = 150

            # Получение границ гласных
            if options.get("vowels", False):
                speech["vowels"]["vowel_boundaries"] = vw.detect_vowel_boundaries(y, sr, threshold=0.1)
                vowel_formants = vw.get_vowel_formant_info(y, sr, speech["vowels"]["vowel_boundaries"])
                speech["info"]["vowel_formants"] = vowel_formants

                if len(speech["vowels"]["vowel_boundaries"]) > 0:
                    if template_speech:
                        if options.get("amplitude", False):
                            speech["vowels"]["amplitude"] = vw.mean_amplitude_dB_for_vowels(y, sr,
                                                                                            speech["vowels"][
                                                                                                "vowel_boundaries"],
                                                                                            formants=vowel_formants)
                        if options.get("energy", False):
                            speech["vowels"]["energy"] = vw.mean_energy_for_vowels(y, sr,
                                                                                   speech["vowels"]["vowel_boundaries"],
                                                                                   formants=vowel_formants)
                        if options.get("freq", False):
                            speech["vowels"]["freq"] = vw.mean_formants_for_vowels(y, sr,
                                                                                   speech["vowels"]["vowel_boundaries"],
                                                                                   formants=vowel_formants)
                        speech["vowels"]["vowel_boundaries"] = vw.group_vowels(speech["vowels"]["vowel_boundaries"])
                    else:
                        if options.get("amplitude", False):
                            speech["vowels"]["amplitude"] = vw.calculate_formant_amplitude(y, sr,
                                                                                           speech["vowels"][
                                                                                               "vowel_boundaries"],
                                                                                           formants=vowel_formants)
                        if options.get("energy", False):
                            speech["vowels"]["energy"] = vw.calculate_formant_energy(y, sr,
                                                                                     speech["vowels"]["vowel_boundaries"],
                                                                                     formants=vowel_formants)
                        if options.get("freq", False):
                            speech["vowels"]["freq"] = vw.calculate_formant_freq(y, sr,
                                                                                 speech["vowels"]["vowel_boundaries"],
                                                                                 formants=vowel_formants)
                    if options.get("speed", False) and options.get("duration", False):
                        speech["speed"] = speech["duration"] / len(speech["vowels"]["vowel_boundaries"])

            if options.get("amplitude", False):
                speech["f0"]["amplitude_min"] = -70
                speech["f0"]["amplitude_max"] = 0

                d = speech["f0"]["amplitude_slope"] * speech["duration"] * 0.5
                amp1 = speech["f0"]["amplitude"] - d
                amp2 = speech["f0"]["amplitude"] + d
                speech["f0"]["amplitude_from"] = amp1
                speech["f0"]["amplitude_to"] = amp2

            if (speech["f0"]["freq"] < 170):
                speech["gender"] = 'man'

                if options.get("freq", False):
                    f0_freq_min = max(speech["f0"]["freq"] * 0.75, 50)
                    f0_freq_max = min(speech["f0"]["freq"] * 2.00, 500)

                if options.get("bandwidth", False):
                    speech["f0"]["bandwidth_min"] = max(speech["f0"]["bandwidth"] * 0.43, 20)
                    speech["f0"]["bandwidth_max"] = min(speech["f0"]["bandwidth"] * 1.20, 50)

                if options.get("energy", False):
                    speech["f0"]["energy_min"] = max(speech["f0"]["energy"] * 0.7, 0)
                    speech["f0"]["energy_max"] = min(speech["f0"]["energy"] * 1.50,
                                                     calculate_formant_energy(speech["f0"]["amplitude_max"],
                                                                              fmt.formant_range(0)))

                if options.get("intensity", False):
                    speech["f0"]["intensity_min"] = max(speech["f0"]["intensity"] * 0.5, 0)
                    speech["f0"]["intensity_max"] = min(speech["f0"]["intensity"] * 1.50, 100)

                if options.get("slope", False):
                    speech["f0"]["slope_min"] = max(speech["f0"]["slope"] * 0.50, 0)
                    speech["f0"]["slope_max"] = min(speech["f0"]["slope"] * 1.5, 100)
            else:
                speech["gender"] = 'woman'

                if options.get("freq", False):
                    f0_freq_min = max(speech["f0"]["freq"] * 0.80, 50)
                    f0_freq_max = min(speech["f0"]["freq"] * 2.50, 600)

                if options.get("bandwidth", False):
                    speech["f0"]["bandwidth_min"] = max(speech["f0"]["bandwidth"] * 0.9, 20)
                    speech["f0"]["bandwidth_max"] = min(speech["f0"]["bandwidth"] * 1.70, 90)

                if options.get("energy", False):
                    speech["f0"]["energy_min"] = max(speech["f0"]["energy"] * 0.7, 0)
                    speech["f0"]["energy_max"] = min(speech["f0"]["energy"] * 1.50, 1000)

                if options.get("intensity", False):
                    speech["f0"]["intensity_min"] = max(speech["f0"]["intensity"] * 0.5, 0)
                    speech["f0"]["intensity_max"] = min(speech["f0"]["intensity"] * 1.50, 100)

                if options.get("slope", False):
                    speech["f0"]["slope_min"] = max(speech["f0"]["slope"] * 0.50, 0)
                    speech["f0"]["slope_max"] = min(speech["f0"]["slope"] * 1.5, 100)

            if options.get("freq", False):
                speech["f0"]["freq_min"] = f0_freq_min
                speech["f0"]["freq_max"] = f0_freq_max

                speech["f0"]["freq_cmin"] = (speech["f0"]["freq"] - f0_freq_min) / speech["f0"]["freq"]
                speech["f0"]["freq_cmax"] = (f0_freq_max - speech["f0"]["freq"]) / speech["f0"]["freq"]

    speech["volume"] = 0.0
    speech["emotion"] = 0.0

    # start = time.perf_counter()
    # finish = time.perf_counter()
    # print('Время работы get_speech_params: ' + str(finish - start))
    # Определяем, форманты
    if options.get("formants", False):
        formants = fmt.get_formant_info(y, sr)
        speech["info"]["formants"] = formants

        count = options.get("formant_max", 5)
        for formant_index in range(1, count+1):
            f_name = f'f{formant_index}'
            if options.get("freq", False):
                speech[f_name]["freq"] = fmt.get_formant_frequency_by_index(y, sr, formant_index,
                                                                            formants=formants)
                freq_min = max(speech[f_name]["freq"] * 0.80, 50)
                freq_max = min(speech[f_name]["freq"] * 2.50, 600)

                speech[f_name]["freq_min"] = freq_min
                speech[f_name]["freq_max"] = freq_max

                speech[f_name]["freq_cmin"] = (speech[f_name]["freq"] - freq_min) / speech[f_name]["freq"]
                speech[f_name]["freq_cmax"] = (freq_max - speech[f_name]["freq"]) / speech[f_name]["freq"]

            if options.get("bandwidth", False):
                speech[f_name]["bandwidth"] = fmt.calculate_formant_bandwidth(y, sr, formant_index, method='avg',
                                                                              formants=formants)
                speech[f_name]["bandwidth_min"] = max(speech[f_name]["bandwidth"] * 0.8, 0)
                speech[f_name]["bandwidth_max"] = min(speech[f_name]["bandwidth"] * 1.3,
                                                      fmt.formant_range(formant_index))

            if options.get("energy", False):
                speech[f_name]["energy"] = fmt.calculate_formant_energy3(y, sr, formant_index, formants=formants)
                speech[f_name]["energy_min"] = max(speech[f_name]["energy"] * 0.7, 0)
                speech[f_name]["energy_max"] = min(speech[f_name]["energy"] * 1.50,
                                                   calculate_formant_energy(speech[f_name]["amplitude_max"],
                                                                            fmt.formant_range(formant_index)))

            if options.get("intensity", False):
                speech[f_name]["intensity"] = fmt.calculate_formant_intensity_avg(y, sr, formant_index,
                                                                                  formants=formants)
                speech[f_name]["intensity_min"] = max(speech[f_name]["intensity"] * 0.5, 0)
                speech[f_name]["intensity_max"] = min(speech[f_name]["intensity"] * 1.50, 100)

            if options.get("formant_period", False):
                formant_period, formant_offset, formant_amplitude = fmt.extract_formant_rate(y, sr, formant_index,
                                                                                             formants=formants)
                speech[f_name]["period"]["time"] = formant_period
                speech[f_name]["period"]["offset"] = formant_offset
                speech[f_name]["period"]["amplitude"] = formant_amplitude

                speech[f_name]["period"]["time_min"] = 0
                speech[f_name]["period"]["time_max"] = speech["duration"]

                speech[f_name]["period"]["offset_min"] = -speech["duration"]
                speech[f_name]["period"]["offset_max"] = speech["duration"]

                speech[f_name]["period"]["amplitude_min"] = 5
                speech[f_name]["period"]["amplitude_max"] = 150

            if options.get("slope", False):
                slope, variance, trend = fmt.calculate_formant_slope(y, sr, formant_index, is_smooth=True,
                                                                     is_peak=True, formants=formants)
                speech[f_name]["slope"] = slope
                speech[f_name]["slope_min"] = max(speech[f_name]["slope"] * 0.50, -100)
                speech[f_name]["slope_max"] = min(speech[f_name]["slope"] * 1.5, 100)

            if options.get("amplitude", False):
                speech[f_name]["amplitude"] = fmt.calculate_formant_amplitude_avg(y, sr, formant_index,
                                                                                  formants=formants)
                speech[f_name]["amplitude_min"] = -70
                speech[f_name]["amplitude_max"] = 70

                d = speech["f0"]["amplitude_slope"] * speech["duration"] * 0.5
                amp1 = speech[f_name]["amplitude"] - d
                amp2 = speech[f_name]["amplitude"] + d
                speech[f_name]["amplitude_from"] = amp1
                speech[f_name]["amplitude_to"] = amp2


    if options.get("tract", False):
        speech["tract_length"] = get_tract_length(y, sr)

    enabled_components = []
    if options.get("pitch", False):
        enabled_components.append("f0")
    if options.get("formants", False):
        enabled_components.extend(
            f"f{i}" for i in range(1, options.get("formant_max", 5) + 1)
        )
    if options.get("amplitude", False) and enabled_components:
        frequencies = [speech[key]["freq"] for key in enabled_components]
        amplitudes = [speech[key]["amplitude"] for key in enabled_components]
        amplitude_db = calculate_speech_volume(frequencies, amplitudes)
        speech["amplitude_db"] = amplitude_db if np.isfinite(amplitude_db) else 0.0
    else:
        speech["amplitude_db"] = 0.0

    return speech

def get_speech_vector(params, norm_params):
    def get_max_value(value, value0, volume):
        if volume == 0 or not value or not value0:
            return 0
        return (value - value0) / abs(volume)

    vector = {"f0": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,},
                     "freq_max": 0, "freq_min": 0, },
              "f1": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,}, },
              "f2": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,}, },
              "f3": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,}, },
              "f4": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,}, },
              "f5": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0,
                     "period": {"time":0, "offset":0, "amplitude":0,}, },
              "speed": 0,
              "vowels": {"amplitude": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                         "energy": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                         "freq": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                         },
              "options": {},
              }
    vector["options"] = norm_params["options"]

    for index in range(vector["options"].get("formant_max", 5)+1):
        if not vector["options"].get("pitch", False) and (index==0):
            continue
        if not vector["options"].get("formants", False) and (index>0):
            break

        f_name = f"f{index}"
        if vector["options"].get("freq", False):
            norm_params[f_name]["freq_min"] = min(norm_params[f_name]["freq_min"], params[f_name]["freq"])
            norm_params[f_name]["freq_max"] = max(norm_params[f_name]["freq_max"], params[f_name]["freq"])

        if vector["options"].get("bandwidth", False):
            norm_params[f_name]["bandwidth_min"] = min(norm_params[f_name]["bandwidth_min"], params[f_name]["bandwidth"])
            norm_params[f_name]["bandwidth_max"] = max(norm_params[f_name]["bandwidth_max"], params[f_name]["bandwidth"])

        if vector["options"].get("energy", False):
            norm_params[f_name]["energy_min"] = min(norm_params[f_name]["energy_min"], params[f_name]["energy"])
            norm_params[f_name]["energy_max"] = max(norm_params[f_name]["energy_max"], params[f_name]["energy"])

        if vector["options"].get("intensity", False):
            norm_params[f_name]["intensity_min"] = min(norm_params[f_name]["intensity_min"], params[f_name]["intensity"])
            norm_params[f_name]["intensity_max"] = max(norm_params[f_name]["intensity_max"], params[f_name]["intensity"])

        if vector["options"].get("amplitude", False):
            norm_params[f_name]["amplitude_min"] = min(norm_params[f_name]["amplitude_min"], params[f_name]["amplitude"])
            norm_params[f_name]["amplitude_max"] = max(norm_params[f_name]["amplitude_max"], params[f_name]["amplitude"])

        if vector["options"].get("slope", False):
            norm_params[f_name]["slope_min"] = min(norm_params[f_name]["slope_min"], params[f_name]["slope"])
            norm_params[f_name]["slope_max"] = max(norm_params[f_name]["slope_max"], params[f_name]["slope"])

    emotion = 0.0
    if vector["options"].get("pitch", False) and vector["options"].get("freq", False):
        if params["f0"]["freq"] > norm_params["f0"]["freq"]:
            emotion = (params["f0"]["freq"] - norm_params["f0"]["freq"]) / (
                        norm_params["f0"]["freq_max"] - norm_params["f0"]["freq"])
        elif params["f0"]["freq"] < norm_params["f0"]["freq"]:
            emotion = (params["f0"]["freq"] - norm_params["f0"]["freq"]) / (
                        norm_params["f0"]["freq"] - norm_params["f0"]["freq_min"])

    intensity_avg = params["amplitude_db"]
    intensity_norm_avg = norm_params["amplitude_db"]
    # for formant_index in range(1, 6):
    #     f_name = f'f{formant_index}'
    #     intensity_avg += params[f_name]["intensity"]
    #     intensity_norm_avg += norm_params[f_name]["intensity"]
    # intensity_avg /= 6
    # intensity_norm_avg /= 6
    if intensity_avg > intensity_norm_avg:
        volume = (intensity_avg - intensity_norm_avg) / (100 - intensity_norm_avg)
    elif intensity_avg < intensity_norm_avg:
        volume = (intensity_avg - intensity_norm_avg) / (intensity_norm_avg - (-50.0))
    else:
        volume = 0.0

    vector["volume"] = 0.0 if volume == 0 else math.copysign(1, volume)
    vector["emotion"] = 0.0 if emotion == 0 else math.copysign(1, emotion)

    if abs(volume) < 0.001:
        volume = 0.0
    if abs(emotion) < 0.001:
        emotion = 0.0
    params["volume"] = volume
    params["emotion"] = emotion

    if vector["options"].get("speed", False):
        vector["speed"] = get_max_value(params["speed"], norm_params["speed"], emotion)

    if vector["options"].get("vowels", False) and vector["options"].get("formants", False):
        for index, (boundary, vowel_type) in enumerate(params["vowels"]["vowel_boundaries"]):
            for formant_index in range(1, vector["options"].get("formant_max", 5)+1):
                f_name = f'f{formant_index}'
                a = 0
                a0 = 0
                e = 0
                e0 = 0
                f = 0
                f0 = 0
                if params["template_speech"]:
                    if vector["options"].get("amplitude", False):
                        a = params["vowels"]["amplitude"][vowel_type][f_name]
                    if vector["options"].get("energy", False):
                        e = params["vowels"]["energy"][vowel_type][f_name]
                    if vector["options"].get("freq", False):
                        f = params["vowels"]["freq"][vowel_type][f_name]
                else:
                    if vector["options"].get("amplitude", False):
                        a = params["vowels"]["amplitude"][f_name][index]
                    if vector["options"].get("energy", False):
                        e = params["vowels"]["energy"][f_name][index]
                    if vector["options"].get("freq", False):
                        f = params["vowels"]["freq"][index][formant_index - 1]
                if norm_params["template_speech"]:
                    if vector["options"].get("amplitude", False):
                        a0 = norm_params["vowels"]["amplitude"][vowel_type][f_name]
                    if vector["options"].get("energy", False):
                        e0 = norm_params["vowels"]["energy"][vowel_type][f_name]
                    if vector["options"].get("freq", False):
                        f0 = norm_params["vowels"]["freq"][vowel_type][f_name]
                else:
                    if vector["options"].get("amplitude", False):
                        a0 = norm_params["vowels"]["amplitude"][f_name][index]
                    if vector["options"].get("energy", False):
                        e0 = norm_params["vowels"]["energy"][f_name][index]
                    if vector["options"].get("freq", False):
                        f0 = norm_params["vowels"]["freq"][index][formant_index - 1]

                if vector["options"].get("amplitude", False):
                    vector["vowels"]["amplitude"][f_name].append(get_max_value(a, a0, volume))
                if vector["options"].get("energy", False):
                    vector["vowels"]["energy"][f_name].append(get_max_value(e, e0, volume))
                if vector["options"].get("freq", False):
                    vector["vowels"]["freq"][f_name].append(get_max_value(f, f0, emotion))

    # Определяем, pitch и форманты, там где есть речь
    vector["f0"]["amplitude_slope"] = get_max_value(params["f0"]["amplitude_slope"],
                                                    norm_params["f0"]["amplitude_slope"], volume)
    for formant_index in range(vector["options"].get("formant_max", 5)+1):
        if not vector["options"].get("pitch", False) and (formant_index==0):
            continue
        if not vector["options"].get("formants", False) and (formant_index>0):
            break

        f_name = f'f{formant_index}'
        if vector["options"].get("freq", False):
            vector[f_name]["freq"] = get_max_value(params[f_name]["freq"], norm_params[f_name]["freq"], emotion)
        if vector["options"].get("bandwidth", False):
            vector[f_name]["bandwidth"] = get_max_value(params[f_name]["bandwidth"], norm_params[f_name]["bandwidth"], volume)
        if vector["options"].get("energy", False):
            vector[f_name]["energy"] = get_max_value(params[f_name]["energy"], norm_params[f_name]["energy"], volume)
        if vector["options"].get("intensity", False):
            vector[f_name]["intensity"] = get_max_value(params[f_name]["intensity"], norm_params[f_name]["intensity"], volume)
        if vector["options"].get("amplitude", False):
            vector[f_name]["amplitude"] = get_max_value(params[f_name]["amplitude"], norm_params[f_name]["amplitude"], volume)

        if vector["options"].get("slope", False):
            vector[f_name]["slope"] = get_max_value(params[f_name]["slope"], norm_params[f_name]["slope"], emotion)
        if vector["options"].get("period", False):
            vector[f_name]["period"]["time"] = get_max_value(params[f_name]["period"]["time"],
                                                             norm_params[f_name]["period"]["time"], emotion)
            vector[f_name]["period"]["offset"] = get_max_value(params[f_name]["period"]["offset"],
                                                               norm_params[f_name]["period"]["offset"], emotion)
            vector[f_name]["period"]["amplitude"] = get_max_value(params[f_name]["period"]["amplitude"],
                                                                  norm_params[f_name]["period"]["amplitude"], volume)

    return vector

def get_speech_new(norm_params, params, vectors, volume, emotion):
    def get_new_value(vector, value0, volume):
        if not value0:
            return 0
        if vector == 0 or volume == 0 or not vector:
            return value0
        return vector * volume + value0

    speech = {"f0": {"freq":0, "bandwidth":0, "energy":0, "intensity":0, "amplitude":0, "slope": 0, "period": {}, },
              "f1": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0, "period": {}, },
              "f2": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0, "period": {}, },
              "f3": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0, "period": {}, },
              "f4": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0, "period": {}, },
              "f5": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "slope": 0, "period": {}, },
              "speed": 0,
              "vowels": {"vowel_boundaries": [],
                         "amplitude": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                         "energy": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                         "freq": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                         },
              "options": {},
              }
    speech["volume"] = volume
    speech["emotion"] = emotion
    speech["options"] = vectors["options"]

    if vectors["volume"] < 0:
        if volume < 0:
            volume = abs(volume)
        else:
            volume = -volume

    if vectors["emotion"] < 0:
        if emotion < 0:
            emotion = abs(emotion)
        else:
            emotion = -emotion

    if speech["options"].get("speed", False):
        delta_speed = math.log(1 + 0.5 * abs(vectors["speed"] * emotion))
        if vectors["speed"] > 0:
            speech["speed"] = delta_speed + norm_params["speed"]
        else:
            speech["speed"] = -delta_speed + norm_params["speed"]

    # Определяем, тон и форманты
    for formant_index in range(speech["options"].get("formant_max", 5)+1):
        if not speech["options"].get("pitch", False) and (formant_index==0):
            continue
        if not speech["options"].get("formants", False) and (formant_index>0):
            break

        f_name = f'f{formant_index}'
        if speech["options"].get("freq", False):
            if vectors["volume"] < 0:
                speech[f_name]["freq"] = get_new_value(vectors[f_name]["freq"], norm_params[f_name]["freq"],
                                                       emotion * 0.5)
                speech[f_name]["freq"] = np.clip(speech[f_name]["freq"], fmt.formant_ranges[formant_index][0],
                                                 fmt.formant_ranges[formant_index][1] * 0.5)
            else:
                speech[f_name]["freq"] = get_new_value(vectors[f_name]["freq"], norm_params[f_name]["freq"], emotion)
                speech[f_name]["freq"] = np.clip(speech[f_name]["freq"], fmt.formant_ranges[formant_index][0],
                                                 fmt.formant_ranges[formant_index][1])

        if speech["options"].get("bandwidth", False):
            speech[f_name]["bandwidth"] = get_new_value(vectors[f_name]["bandwidth"], norm_params[f_name]["bandwidth"],
                                                        volume)
            speech[f_name]["bandwidth"] = max(speech[f_name]["bandwidth"], norm_params[f_name]["bandwidth_min"])
            speech[f_name]["bandwidth"] = min(speech[f_name]["bandwidth"], norm_params[f_name]["bandwidth_max"])

        if speech["options"].get("energy", False):
            speech[f_name]["energy"] = get_new_value(vectors[f_name]["energy"], norm_params[f_name]["energy"], volume)
            speech[f_name]["energy"] = max(speech[f_name]["energy"], norm_params[f_name]["energy_min"])
            speech[f_name]["energy"] = min(speech[f_name]["energy"], norm_params[f_name]["energy_max"])

        if speech["options"].get("intensity", False):
            speech[f_name]["intensity"] = get_new_value(vectors[f_name]["intensity"], norm_params[f_name]["intensity"],
                                                        volume)
            speech[f_name]["intensity"] = max(speech[f_name]["intensity"], norm_params[f_name]["intensity_min"])
            speech[f_name]["intensity"] = min(speech[f_name]["intensity"], norm_params[f_name]["intensity_max"])

        if speech["options"].get("slope", False):
            speech[f_name]["slope"] = get_new_value(vectors[f_name]["slope"], norm_params[f_name]["slope"], emotion)
            speech[f_name]["slope"] = max(speech[f_name]["slope"], norm_params[f_name]["slope_min"])
            speech[f_name]["slope"] = min(speech[f_name]["slope"], norm_params[f_name]["slope_max"])

        if speech["options"].get("amplitude", False):
            speech[f_name]["amplitude"] = get_new_value(vectors[f_name]["amplitude"], norm_params[f_name]["amplitude"],
                                                        volume)
            # speech[f_name]["amplitude"] = max(speech[f_name]["amplitude"], norm_params[f_name]["amplitude_min"])
            # speech[f_name]["amplitude"] = min(speech[f_name]["amplitude"], norm_params[f_name]["amplitude_max"])

            d = vectors["f0"]["amplitude_slope"] * volume * params["duration"] * 0.5
            amp1 = speech[f_name]["amplitude"] - d
            amp2 = speech[f_name]["amplitude"] + d
            speech[f_name]["amplitude_from"] = amp1
            speech[f_name]["amplitude_to"] = amp2


        if speech["options"].get("period", False):
            speech[f_name]["period"]["time"] = get_new_value(vectors[f_name]["period"]["time"],
                                                             norm_params[f_name]["period"]["time"], emotion)
            speech[f_name]["period"]["offset"] = get_new_value(vectors[f_name]["period"]["offset"],
                                                               norm_params[f_name]["period"]["offset"], emotion)
            speech[f_name]["period"]["amplitude"] = get_new_value(vectors[f_name]["period"]["amplitude"],
                                                                  norm_params[f_name]["period"]["amplitude"], volume)

    if speech["options"].get("vowels", False):
        for index, (boundary, vowel_type) in enumerate(params["vowels"]["vowel_boundaries"]):
            speech["vowels"]["vowel_boundaries"].append((boundary, vowel_type))
            if speech["options"].get("formants", False):
                for formant_index in range(1, speech["options"].get("formant_max", 5)+1):
                    f_name = f'f{formant_index}'

                    a0 = 0
                    e0 = 0
                    f0 = 0
                    if norm_params["template_speech"]:
                        if speech["options"].get("amplitude", False):
                            a0 = norm_params["vowels"]["amplitude"][vowel_type][f_name]
                        if speech["options"].get("energy", False):
                            e0 = norm_params["vowels"]["energy"][vowel_type][f_name]
                        if speech["options"].get("freq", False):
                            f0 = norm_params["vowels"]["freq"][vowel_type][f_name]
                    else:
                        if speech["options"].get("amplitude", False):
                            a0 = norm_params["vowels"]["amplitude"][f_name][index]
                        if speech["options"].get("energy", False):
                            e0 = norm_params["vowels"]["energy"][f_name][index]
                        if speech["options"].get("freq", False):
                            f0 = norm_params["vowels"]["freq"][index][formant_index - 1]

                    if speech["options"].get("amplitude", False):
                        v = vectors["vowels"]["amplitude"][f_name][index]
                        a = get_new_value(v, a0, volume)
                        if vectors["volume"] < 0:
                            v = speech[f_name]["amplitude"]
                            a = max(min(a, v * 1.1), v * 0.9)
                        speech["vowels"]["amplitude"][f_name].append(a)

                    if speech["options"].get("energy", False):
                        v = vectors["vowels"]["energy"][f_name][index]
                        e = get_new_value(v, e0, volume)
                        if vectors["volume"] < 0:
                            v = speech[f_name]["energy"]
                            e = max(min(e, v * 1.1), v * 0.9)
                        e = max(e, norm_params[f_name]["energy_min"])
                        e = min(e, norm_params[f_name]["energy_max"])
                        speech["vowels"]["energy"][f_name].append(e)

                    if speech["options"].get("freq", False):
                        v = vectors["vowels"]["freq"][f_name][index]
                        f = get_new_value(v, f0, emotion)
                        if vectors["emotion"] < 0:
                            v = speech[f_name]["freq"]
                            f = max(min(f, v * 1.1), v * 0.9)
                        f = np.clip(f, fmt.formant_ranges[formant_index][0], fmt.formant_ranges[formant_index][1])
                        speech["vowels"]["freq"][f_name].append(f)

    return speech

def get_speech_mul(new_params, params):
    def  get_mul(value, new_value):
        if value == 0 or not value or not new_value:
            return 0
        return new_value / value

    def  get_mul2(value, new_value, mul0):
        if value == 0 or not value or not new_value:
            return 0
        return new_value / (value * mul0)

    muls = {"f0": {"freq":0, "bandwidth":0, "energy":0, "intensity":0, "amplitude":0, "period": {}, },
            "f1": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "period": {}, },
            "f2": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "period": {}, },
            "f3": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "period": {}, },
            "f4": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "period": {}, },
            "f5": {"freq": 0, "bandwidth": 0, "energy": 0, "intensity": 0, "amplitude": 0, "period": {}, },
            "speed": 0,
            "vowels": {"vowel_boundaries": [],
                       "amplitude": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                       "energy": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                       "freq": {"f1": [], "f2": [], "f3": [], "f4": [], "f5": [], },
                       },
            "options": {},
            }

    muls["options"] = new_params["options"]

    if muls["options"].get("speed", False):
        muls["speed"] = get_mul(params["speed"], new_params["speed"])

    # Определяем, pitch и форманты, там где есть речь
    for formant_index in range(muls["options"].get("formant_max", 5)+1):
        if not muls["options"].get("pitch", False) and (formant_index==0):
            continue
        if not muls["options"].get("formants", False) and (formant_index>0):
            break

        f_name = f'f{formant_index}'
        if muls["options"].get("freq", False):
            muls[f_name]["freq"] = get_mul(params[f_name]["freq"], new_params[f_name]["freq"])
        if muls["options"].get("bandwidth", False):
            muls[f_name]["bandwidth"] = get_mul(params[f_name]["bandwidth"], new_params[f_name]["bandwidth"])
        if muls["options"].get("energy", False):
            muls[f_name]["energy"] = get_mul(params[f_name]["energy"], new_params[f_name]["energy"])
        if muls["options"].get("intensity", False):
            muls[f_name]["intensity"] = get_mul(params[f_name]["intensity"], new_params[f_name]["intensity"])
        if muls["options"].get("amplitude", False):
            amp_new = new_params[f_name]["amplitude"] + 70
            amp_old = params[f_name]["amplitude"] + 70
            muls[f_name]["amplitude"] = get_mul(amp_old, amp_new)

            amp_new = new_params[f_name]["amplitude_from"] + 70
            amp_old = params[f_name]["amplitude_from"] + 70
            muls[f_name]["amplitude_from"] = get_mul(amp_old, amp_new)

            amp_new = new_params[f_name]["amplitude_to"] + 70
            amp_old = params[f_name]["amplitude_to"] + 70
            muls[f_name]["amplitude_to"] = get_mul(amp_old, amp_new)

        if muls["options"].get("period", False):
            muls[f_name]["period"]["time"] = get_mul(params[f_name]["period"]["time"],
                                                     new_params[f_name]["period"]["time"])
            muls[f_name]["period"]["offset"] = get_mul(params[f_name]["period"]["offset"],
                                                       new_params[f_name]["period"]["offset"])
            muls[f_name]["period"]["amplitude"] = get_mul(params[f_name]["period"]["amplitude"],
                                                          new_params[f_name]["period"]["amplitude"])

    if muls["options"].get("vowels", False):
        for index, (boundary, vowel_type) in enumerate(new_params["vowels"]["vowel_boundaries"]):
            muls["vowels"]["vowel_boundaries"].append((boundary, vowel_type))
            if muls["options"].get("formants", False):
                for formant_index in range(1, muls["options"].get("formant_max", 5)+1):
                    f_name = f'f{formant_index}'

                    if muls["options"].get("amplitude", False):
                        amp_new = new_params["vowels"]["amplitude"][f_name][index] + 70
                        amp_old = params["vowels"]["amplitude"][f_name][index] + 70
                        m = muls[f_name]["amplitude"]
                        m = get_mul2(amp_old, amp_new, m)
                        muls["vowels"]["amplitude"][f_name].append(m)

                    if muls["options"].get("energy", False):
                        m = muls[f_name]["energy"]
                        if m != 1.0:
                            m = get_mul2(params["vowels"]["energy"][f_name][index],
                                         new_params["vowels"]["energy"][f_name][index], m)
                        muls["vowels"]["energy"][f_name].append(m)

                    if muls["options"].get("freq", False):
                        m = muls[f_name]["freq"]
                        if m != 1.0:
                            m = get_mul2(params["vowels"]["freq"][index][formant_index - 1],
                                         new_params["vowels"]["freq"][f_name][index], m)
                        muls["vowels"]["freq"][f_name].append(m)

    return muls

def get_change_speech(y, sr, muls, new_params, params):

    pitch = params["info"]["pitch"]
    formants = params["info"]["formants"]
    vowel_formants = params["info"]["vowel_formants"]

    if muls["options"].get("pitch", False):
        # if is_freq:
        #     pitch_shift_hz = new_params["f0"]["freq"] - params["f0"]["freq"]
        #     avg_f0 = params["f0"]["freq"]
        #     pitch_shift_semitones = fl.hz_to_semitones(avg_f0 + pitch_shift_hz, avg_f0)
        #     y, sr = pt.change_pitch_pydub(y, sr, pitch_shift_semitones)

        if muls["options"]["change"].get("pitch_freq", False):
            y, sr = pt.change_pitch_energy(y, sr, muls["f0"]["freq"], pitch_range=(75, 600))
            # y, sr = pt.change_pitch_energy2(y, sr, muls["f0"]["freq"])

        if muls["options"]["change"].get("pitch_amplitude", False):
            m = max(muls["f0"]["amplitude"], 0.0)
            m_from = max(muls["f0"]["amplitude_from"], 0.0)
            m_to = max(muls["f0"]["amplitude_to"], 0.0)

            if m < 1.0:
                # y, sr = pt.change_pitch_amplitude_with_bandwidth(y, sr, m, pitch=pitch)
                y, sr = pt.change_pitch_amplitude_with_bandwidth_range(y, sr, m_from, m_to, pitch=pitch)
            else:
                # y, sr = pt.change_pitch_amplitude(y, sr, m)
                pt.change_pitch_amplitude_range(y, sr, m_from, m_to)

    formant_shifts = [0, 0, 0, 0, 0]
    boost_dB = [0, 0, 0, 0, 0]
    formant_amplitude_factors = [0, 0, 0, 0, 0]
    formant_amplitude_from = [0, 0, 0, 0, 0]
    formant_amplitude_to = [0, 0, 0, 0, 0]
    formant_energy_factors = [0, 0, 0, 0, 0]
    formant_bandwidth_factors = [0, 0, 0, 0, 0]
    if muls["options"].get("formants", False):
        for formant_index in range(1, muls["options"].get("formant_max", 5)+1):
            f_name = f'f{formant_index}'
            formant_shifts[formant_index - 1] = new_params[f_name]["freq"] - params[f_name]["freq"]
            formant_amplitude_factors[formant_index - 1] = max(muls[f_name]["amplitude"], 0.0)
            formant_amplitude_from[formant_index - 1] = max(muls[f_name]["amplitude_from"], 0.0)
            formant_amplitude_to[formant_index - 1] = max(muls[f_name]["amplitude_to"], 0.0)
            boost_dB[formant_index - 1] = max(muls[f_name]["intensity"], 0.0)
            formant_energy_factors[formant_index - 1] = max(muls[f_name]["energy"], 0.0)
            formant_bandwidth_factors[formant_index - 1] = max(muls[f_name]["bandwidth"], 0.001)

        if muls["options"]["change"].get("formant_freq", False):
            y, sr = fmt.change_formants_shifts6(y, sr, formant_shifts, max_shift=500, formants=formants)

        if muls["options"]["change"].get("formant_amplitude", False):
            # y = fmt.change_formant_amplitude(y, sr, formant_amplitude_factors, formants=formants)
            y = fmt.change_formant_amplitude_range(y, sr, formant_amplitude_from, formant_amplitude_to, formants=formants)

    # Увеличение амплитуды каждой гласной
    if muls["options"].get("vowels", False):
        frame_duration = 0.3 * max(abs(new_params["volume"]), 0)  # seconds (100 ms) изменяемое окно вокруг гласной
        if frame_duration > 0:
            if muls["options"]["change"].get("vowel_amplitude", False):
                y = vw.amplitude_vowels_mul(y, sr, muls["vowels"], frame_duration, formants=vowel_formants)

            # сдвиг формант гласных
            if muls["options"]["change"].get("vowel_freq", False):
                y = vw.shifts_vowels_mul(y, sr, muls["vowels"], frame_duration)

    return y, sr


def process_wav_files_in_folder(folder_path, file_norm_speach):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder {folder_path} does not exist.")

    # output_file = os.path.join(folder_path, 'vectors.txt')
    output_file = os.path.join(folder_path, 'vectors.json')

    if not os.path.exists(file_norm_speach):
        raise FileNotFoundError(f"File {file_norm_speach} does not exist.")

    y_norm, sr_norm = librosa.load(file_norm_speach, sr=None)
    norm_params = get_speech_params(y_norm, sr_norm, template_speech=True)

    list_params = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.wav') and filename.lower() != file_norm_speach.lower():
            input_file = os.path.join(folder_path, filename)
            print(f"Processing file: {input_file}")

            y, sr = librosa.load(input_file, sr=None)
            params = get_speech_params(y, sr)
            print("Параметры речи:", params)

            vectors = get_speech_vector(params, norm_params)
            print("Вектор речи:", vectors)

            volume = math.copysign(1, params["volume"])
            emotion = math.copysign(1, params["emotion"])
            new_params = get_speech_new(norm_params, params, vectors, volume, emotion)
            print("Новые параметры речи:", new_params)

            list_params.append(new_params)

    total_params = {
        "volume_up": {"emotion_up": create_empty_value(True), "emotion_down": create_empty_value(True)},
        "volume_down": {"emotion_up": create_empty_value(True), "emotion_down": create_empty_value(True)}
    }

    for param in list_params:
        volume = "volume_up" if param["volume"] > 0 else "volume_down" if param["volume"] < 0 else ""
        emotion = "emotion_up" if param["emotion"] > 0 else "emotion_down" if param["emotion"] < 0 else ""

        if volume and emotion:
            total_param = total_params[volume][emotion]
            update_vowels(total_param["vowels"], param["vowels"])
            for formant_index in range(0, 6):
                f_name = f'f{formant_index}'
                update_param(total_param[f_name], param[f_name])

    average_params(total_params)
    average_vowels(total_params)

    speech = {
        "params": {
            "norm": norm_params,
            "volume_up": {"emotion_up": total_params["volume_up"]["emotion_up"], "emotion_down": total_params["volume_up"]["emotion_down"]},
            "volume_down": {"emotion_up": total_params["volume_down"]["emotion_up"], "emotion_down": total_params["volume_down"]["emotion_down"]},
        },
        "vectors": {
            "volume_up": {"emotion_up": get_speech_vector(total_params["volume_up"]["emotion_up"], norm_params),
                          "emotion_down": get_speech_vector(total_params["volume_up"]["emotion_down"], norm_params)},
            "volume_down": {"emotion_up": get_speech_vector(total_params["volume_down"]["emotion_up"], norm_params),
                            "emotion_down": get_speech_vector(total_params["volume_down"]["emotion_down"], norm_params)},
        },
    }

    def check_value_up(key1, key2, value):
        key1[value] = abs(key1[value])
        key2[value] = abs(key2[value])

    def check_value_down(key1, key2, value):
        key1[value] = -abs(key1[value])
        key2[value] = -abs(key2[value])

    keys = [f"f{i}" for i in range(6)]  # Создаём список ключей "f0" до "f5"
    for key in keys:
        key_1 = speech["vectors"]["volume_up"]["emotion_up"][key]
        key_2 = speech["vectors"]["volume_up"]["emotion_down"][key]
        key_3 = speech["vectors"]["volume_down"]["emotion_up"][key]
        key_4 = speech["vectors"]["volume_down"]["emotion_down"][key]

        check_value_up(key_1, key_2, "amplitude")
        check_value_down(key_3, key_4, "amplitude")

        check_value_up(key_1, key_2, "energy")
        check_value_down(key_3, key_4, "energy")

        check_value_up(key_1, key_2, "intensity")
        check_value_down(key_3, key_4, "intensity")

    # Конвертация params в сериализуемый формат
    serializable_data = convert_params_to_serializable(speech)
    # Сохранение в файл JSON
    with open(output_file, 'w') as f:
        json.dump(serializable_data, f, indent=4)

def convert_params_to_serializable(params):
    """Рекурсивно конвертирует объекты numpy и другие нестандартные типы данных в стандартные типы данных Python."""
    if isinstance(params, dict):
        return {key: convert_params_to_serializable(value) for key, value in params.items()}
    elif isinstance(params, list):
        return [convert_params_to_serializable(item) for item in params]
    elif isinstance(params, np.ndarray):
        return params.tolist()
    elif isinstance(params, (np.integer, int)):
        return int(params)
    elif isinstance(params, (np.floating, float)):
        return float(params)
    elif isinstance(params, np.bool_):
        return bool(params)
    elif isinstance(params, np.datetime64):
        return str(params)
    else:
        return params

def update_param(total_param, param):
    total_param["freq"] += param["freq"]
    total_param["bandwidth"] += param["bandwidth"]
    total_param["energy"] += param["energy"]
    total_param["intensity"] += param["intensity"]
    total_param["amplitude"] += param["amplitude"]
    total_param["period"]["time"] += param["period"]["time"]
    total_param["period"]["offset"] += param["period"]["offset"]
    total_param["period"]["amplitude"] += param["period"]["amplitude"]
    total_param["count"] += 1

def update_vowels(total_param, param):
    for index, (boundary, vowel_type) in enumerate(param["vowel_boundaries"]):
        for formant_index in range(1,6):
            f_name = f'f{formant_index}'
            total_param["amplitude"][vowel_type][f_name] += param["amplitude"][f_name][index]
            total_param["energy"][vowel_type][f_name] += param["energy"][f_name][index]
            total_param["freq"][vowel_type][f_name] += param["freq"][f_name][index]

            for index_t, (count, vowel_type_t) in enumerate(total_param["vowel_boundaries"]):
                if vowel_type_t == vowel_type:
                    total_param["vowel_boundaries"][index_t] = (count+1, vowel_type)
                    break


def average_params(params):
    for volume_type in params:
        for emotion_type in params[volume_type]:
            param = params[volume_type][emotion_type]
            for formant_index in range(0, 6):
                f_name = f'f{formant_index}'
                if param[f_name]["count"] > 0:
                    param[f_name]["freq"] /= param[f_name]["count"]
                    param[f_name]["bandwidth"] /= param[f_name]["count"]
                    param[f_name]["energy"] /= param[f_name]["count"]
                    param[f_name]["intensity"] /= param[f_name]["count"]
                    param[f_name]["amplitude"] /= param[f_name]["count"]
                    param[f_name]["period"]["time"] /= param[f_name]["count"]
                    param[f_name]["period"]["offset"] /= param[f_name]["count"]
                    param[f_name]["period"]["amplitude"] /= param[f_name]["count"]

            keys = [f"f{i}" for i in range(6)]  # Создаём список ключей "f0" до "f5"
            frequencies = [param[key]["freq"] for key in keys]
            amplitudes = [param[key]["amplitude"] for key in keys]
            param["amplitude_db"] = calculate_speech_volume(frequencies, amplitudes)

def average_vowels(params):
    for volume_type in params:
        for emotion_type in params[volume_type]:
            param = params[volume_type][emotion_type]["vowels"]
            for index, (count, vowel_type) in enumerate(param["vowel_boundaries"]):
                if count > 0:
                    for formant_index in range(1, 6):
                        f_name = f'f{formant_index}'
                        param["amplitude"][vowel_type][f_name] /= count
                        param["energy"][vowel_type][f_name] /= count
                        param["freq"][vowel_type][f_name] /= count


def init_speech(file_speech_norm,
                file_speech_volume_up_emotion_up=None,
                file_speech_volume_up_emotion_down=None,
                file_speech_volume_down_emotion_up=None,
                file_speech_volume_down_emotion_down=None,
                gender=None,
                options=None,
                ):
    if not options:
        options = {"freq": True, "bandwidth": True, "energy": True, "intensity": True,
                   "amplitude": True, "slope": True, "period": True,
                   "pitch": True, "formants": True, "vowels": True,
                   "duration": True, "speed": True, "gender": True, "tract": True, "check_speech": True,
                   "change": {"pitch_freq": True, "pitch_amplitude": False,
                              "formant_freq": False, "formant_amplitude": True,
                              "vowel_freq": False, "vowel_amplitude": False, },
                   }

    y, sr = librosa.load(file_speech_norm, sr=None)
    norm_params = get_speech_params(y, sr, template_speech=True, options=options)

    if gender == 'man':
        default_speech = default_speech_man
    elif gender == 'woman':
        default_speech = default_speech_woman
    else:
        if (norm_params["f0"]["freq"] < 170):
            default_speech = default_speech_man
        else:
            default_speech = default_speech_woman

    if file_speech_volume_up_emotion_up:
        y, sr = librosa.load(file_speech_volume_up_emotion_up, sr=None)
        volume_up_emotion_up_params = get_speech_params(y, sr, True, options=options)
        volume_up_emotion_up_vectors = get_speech_vector(volume_up_emotion_up_params, norm_params)
    else:
        volume_up_emotion_up_params = default_speech["params"]["volume_up"]["emotion_up"]
        volume_up_emotion_up_vectors = default_speech["vectors"]["volume_up"]["emotion_up"]

    if file_speech_volume_up_emotion_down:
        y, sr = librosa.load(file_speech_volume_up_emotion_down, sr=None)
        volume_up_emotion_down_params = get_speech_params(y, sr, True, options=options)
        volume_up_emotion_down_vectors = get_speech_vector(volume_up_emotion_down_params, norm_params)
    else:
        volume_up_emotion_down_params = default_speech["params"]["volume_up"]["emotion_down"]
        volume_up_emotion_down_vectors = default_speech["vectors"]["volume_up"]["emotion_down"]

    if file_speech_volume_down_emotion_up:
        y, sr = librosa.load(file_speech_volume_down_emotion_up, sr=None)
        volume_down_emotion_up_params = get_speech_params(y, sr, True, options=options)
        volume_down_emotion_up_vectors = get_speech_vector(volume_down_emotion_up_params, norm_params)
    else:
        volume_down_emotion_up_params = default_speech["params"]["volume_down"]["emotion_up"]
        volume_down_emotion_up_vectors = default_speech["vectors"]["volume_down"]["emotion_up"]

    if file_speech_volume_down_emotion_down:
        y, sr = librosa.load(file_speech_volume_down_emotion_down, sr=None)
        volume_down_emotion_down_params = get_speech_params(y, sr, True, options=options)
        volume_down_emotion_down_vectors = get_speech_vector(volume_down_emotion_down_params, norm_params)
    else:
        volume_down_emotion_down_params = default_speech["params"]["volume_down"]["emotion_down"]
        volume_down_emotion_down_vectors = default_speech["vectors"]["volume_down"]["emotion_down"]

    volume_up_emotion_up_params["options"] = norm_params["options"]
    volume_up_emotion_down_params["options"] = norm_params["options"]
    volume_down_emotion_up_params["options"] = norm_params["options"]
    volume_down_emotion_down_params["options"] = norm_params["options"]

    volume_up_emotion_up_vectors["options"] = norm_params["options"]
    volume_up_emotion_down_vectors["options"] = norm_params["options"]
    volume_down_emotion_up_vectors["options"] = norm_params["options"]
    volume_down_emotion_down_vectors["options"] = norm_params["options"]

    speech = {
        "params": {
            "norm": norm_params,
            "volume_up": {"emotion_up": volume_up_emotion_up_params,
                          "emotion_down": volume_up_emotion_down_params},
            "volume_down": {"emotion_up": volume_down_emotion_up_params,
                            "emotion_down": volume_down_emotion_down_params},
        },
        "vectors": {
            "volume_up": {"emotion_up": volume_up_emotion_up_vectors,
                          "emotion_down": volume_up_emotion_down_vectors},
            "volume_down": {"emotion_up": volume_down_emotion_up_vectors,
                            "emotion_down": volume_down_emotion_down_vectors},
        },
        "files": {
            "norm": file_speech_norm,
            "volume_up": {"emotion_up": file_speech_volume_up_emotion_up,
                          "emotion_down": file_speech_volume_up_emotion_down},
            "volume_down": {"emotion_up": file_speech_volume_down_emotion_up,
                            "emotion_down": file_speech_volume_down_emotion_down},
        },
    }

    return speech

def change_speech(speech, cur_speech, volume, emotion):
    y, sr = librosa.load(cur_speech["params"]["file"], sr=None)

    vec_volume = math.copysign(1, volume)
    vec_emotion = math.copysign(1, emotion)
    params_norm = speech["params"]["norm"]
    vectors = cur_speech["vectors"]

    if vectors["volume"] != vec_volume or vectors["emotion"] != vec_emotion:
        pitch_period, pitch_offset, pitch_amplitude = pt.extract_pitch_rate(y, sr,
                                                                            pitch=cur_speech["params"]["info"]["pitch"])
        if pitch_period:
            v0 = min(max(0.5 * (1 + cur_speech["params"]["volume"]), 0.01), 1.0)
            v = min(max(0.5 * (1 + volume), 0.01), 1.0)
            pitch_amplitude = pitch_amplitude * v / v0
            pitch_amplitude = min(max(pitch_amplitude, 5), 50)
            # y, sr = pt.flatten_pitch(y, sr, pitch=cur_speech["params"]["info"]["pitch"])
            y, sr = pt.change_pitch_intonation_ex(y, sr, begin_period=pitch_period, end_period=pitch_period,
                                                  begin_amplitude=pitch_amplitude, end_amplitude=pitch_amplitude,
                                                  offset=pitch_offset, pitch=cur_speech["params"]["info"]["pitch"])

        type_volume = "volume_up" if volume >= 0 else "volume_down"
        type_emotion = "emotion_up" if emotion >= 0 else "emotion_down"

        vectors = speech["vectors"][type_volume][type_emotion]
        vectors["f0"]["amplitude_slope"] = cur_speech["vectors"]["f0"]["amplitude_slope"]
        if cur_speech["vectors"]["emotion"] == vec_emotion:
            for formant_index in range(1, vectors["options"].get("formant_max", 5)+1):
                f_name = f'f{formant_index}'
                vectors[f_name]["freq"] = cur_speech["vectors"][f_name]["freq"]
                vectors[f_name]["slope"] = cur_speech["vectors"][f_name]["slope"]
                vectors[f_name]["period"]["time"] = cur_speech["vectors"][f_name]["period"]["time"]
                vectors[f_name]["period"]["offset"] = cur_speech["vectors"][f_name]["period"]["offset"]
            vectors["vowels"]["freq"] = cur_speech["vectors"]["vowels"]["freq"]
        elif cur_speech["vectors"]["volume"] == vec_volume:
            for formant_index in range(1, vectors["options"].get("formant_max", 5)+1):
                f_name = f'f{formant_index}'
                vectors[f_name]["bandwidth"] = cur_speech["vectors"][f_name]["bandwidth"]
                vectors[f_name]["energy"] = cur_speech["vectors"][f_name]["energy"]
                vectors[f_name]["intensity"] = cur_speech["vectors"][f_name]["intensity"]
                vectors[f_name]["amplitude"] = cur_speech["vectors"][f_name]["amplitude"]
                vectors[f_name]["period"]["amplitude"] = cur_speech["vectors"][f_name]["period"]["amplitude"]
            vectors["vowels"]["amplitude"] = cur_speech["vectors"]["vowels"]["amplitude"]
            vectors["vowels"]["energy"] = cur_speech["vectors"]["vowels"]["energy"]

        # params = get_speech_params(y, sr, options=speech["params"]["norm"]["options"])
        params = cur_speech["params"]
        params["f0"]["period"]["amplitude"] = pitch_amplitude
    else:
        params = cur_speech["params"]
        pitch_amplitude = params["f0"]["period"]["amplitude"]
        if pitch_amplitude and pitch_amplitude > 0:
            v0 = min(max(0.5 * (1 + params["volume"]), 0.01), 1.0)
            v = min(max(0.5 * (1 + volume), 0.01), 1.0)
            pitch_amplitude_n = pitch_amplitude * v / v0
            pitch_amplitude_n = min(max(pitch_amplitude_n, 5), 50)
            m = pitch_amplitude_n / pitch_amplitude
            y, sr = pt.scale_pitch_width(y, sr, factor=m)

    new_params = get_speech_new(params_norm, params, vectors, volume, emotion)
    muls = get_speech_mul(new_params, params)
    y_new, sr_new = get_change_speech(y, sr, muls, new_params, params)

    return y_new, sr_new


def speech_params(input_file, speech):
    y, sr = librosa.load(input_file, sr=None)

    start = time.perf_counter()
    params = get_speech_params(y, sr, options=speech["params"]["norm"]["options"])
    finish = time.perf_counter()
    print('Время работы get_speech_params: ' + str(finish - start))

    vectors = get_speech_vector(params, speech["params"]["norm"])

    params["file"] = input_file
    type_volume = "volume_up" if vectors["volume"] >= 0 else "volume_down"
    type_emotion = "emotion_up" if vectors["emotion"] >= 0 else "emotion_down"
    vectors_0 = speech["vectors"][type_volume][type_emotion]

    for formant_index in range(6):
        f_name = f'f{formant_index}'
        if abs(vectors[f_name]["bandwidth"]) < 1.0 or abs(params["volume"]) < 0.1:
            vectors[f_name]["bandwidth"] = vectors_0[f_name]["bandwidth"]
        if abs(vectors[f_name]["energy"]) < 0.1 or abs(params["volume"]) < 0.1:
            vectors[f_name]["energy"] = vectors_0[f_name]["energy"]
        if abs(vectors[f_name]["intensity"]) < 1.0 or abs(params["volume"]) < 0.1:
            vectors[f_name]["intensity"] = vectors_0[f_name]["intensity"]
        if abs(vectors[f_name]["amplitude"]) < 1.0 or abs(params["volume"]) < 0.1:
            vectors[f_name]["amplitude"] = vectors_0[f_name]["amplitude"]
        if abs(vectors[f_name]["period"]["amplitude"]) < 1.0 or abs(params["volume"]) < 0.1:
            vectors[f_name]["period"]["amplitude"] = vectors_0[f_name]["period"]["amplitude"]

        if abs(params["emotion"]) < 0.1:
            vectors[f_name]["freq"] = vectors_0[f_name]["freq"]
            vectors[f_name]["period"]["time"] = vectors_0[f_name]["period"]["time"]
            vectors[f_name]["period"]["offset"] = vectors_0[f_name]["period"]["offset"]

    return {"params": params, "vectors": vectors, }


def process_audio(file_input, folder, min_speech_duration=3.0,
                  max_speech_pause=1.0, only_pitch=True, remove_other_pitch=False,
                  speech_params_required=True, min_total_speech_duration=3.0,
                  min_pause_duration=1.0):
    # Читаем аудиофайл
    y, sr = librosa.load(file_input, sr=None)

    # Найти сегменты с речью
    if only_pitch:
        segments = trim_segments_to_pitch(y, sr, min_energy_threshold=0.01, min_pause_duration=min_pause_duration,
                                          frame_length=2048, remove_other_pitch=remove_other_pitch,
                                          hop_length=512, min_false_duration=0.1, pitch_margin=0.1)
    else:
        segments = pt.find_speech_segments(y, sr, min_energy_threshold=0.01, min_pause_duration=min_pause_duration)

    # Создаем папку, если она не существует
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Инициализация переменных для объединения сегментов
    total_duration = 0
    total_audio = AudioSegment.empty()
    segment_index = 1
    old_end_time = 0
    speech_present = False

    # Перебираем найденные сегменты речи
    for i, (start_time, end_time, segment_y, segment_sr) in enumerate(segments):
        # print(f"Segment {i + 1}:")
        # print(f"  Start time: {start_time:.2f} s")
        # print(f"  End time: {end_time:.2f} s")
        # print(f"  Duration: {end_time - start_time:.2f} s")
        # print(f"  Sample rate: {segment_sr}")
        segment_y = trim_silence(segment_y, segment_sr, top_db=20, apply_noise_reduction=False)

        if speech_params_required:
            params = get_speech_params(segment_y, segment_sr)
            speech_duration = params["duration"]
            # is_scream_signal = dt.is_scream(y, sr)
            # is_whisper_signal = dt.is_whisper(y, sr)
            # is_soft_speech_signal = dt.is_soft_speech(y, sr)
            if (speech_duration < 0.1) or len(params["vowels"]) == 0:
                old_end_time = end_time
                continue
        else:
            speech_duration = pt.calculate_pitch_duration(segment_y, sr)
            if speech_duration < 0.1:
                old_end_time = end_time
                continue

        # Создаем AudioSegment для текущего сегмента
        y_int16 = np.int16(segment_y * 32767)
        segment_audio = AudioSegment(
            y_int16.tobytes(),
            frame_rate=segment_sr,
            sample_width=y_int16.dtype.itemsize,
            channels=1
        )

        # Добавляем текущий сегмент к общему
        # total_duration += (end_time - start_time)
        total_duration += speech_duration

        total_duration2 = total_duration
        if i < len(segments) - 1:
            next_start_time = segments[i+1][0]
            next_pause = next_start_time - end_time
            total_duration2 = total_duration2 + next_pause
        else:
            next_pause = 0

        # Если общая длительность >= 3 секунд или это последний сегмент
        if total_duration2 >= min_speech_duration or i == len(segments) - 1:
            new_audio = False
            if (not min_total_speech_duration or total_duration >= min_total_speech_duration) and speech_present:
                total_audio += segment_audio
                total_audio = trim_silence_pydub(total_audio)

                # Сохраняем аудиоблок в файл
                output_file = os.path.join(folder,
                                           f"{os.path.splitext(os.path.basename(file_input))[0]}_{segment_index}.wav")
                total_audio.export(output_file, format="wav")

                print(f"Saved segment {segment_index} to {output_file}")
                new_audio = True

            if next_pause > max_speech_pause or new_audio:
                # Сбрасываем для следующего блока
                total_audio = AudioSegment.empty()
                total_duration = 0
                segment_index += 1
                speech_present = False
            else:
                silence_duration = start_time - old_end_time
                total_duration += silence_duration
                total_audio += AudioSegment.silent(duration=silence_duration * 1000, frame_rate=segment_sr)
                total_audio += segment_audio
                speech_present = True
        else:
            silence_duration = start_time - old_end_time
            if silence_duration > max_speech_pause:
                # Сбрасываем для следующего блока
                total_audio = AudioSegment.empty()
                total_duration = 0
                segment_index += 1
                speech_present = False
            else:
                total_duration += silence_duration
                total_audio += AudioSegment.silent(duration=silence_duration * 1000, frame_rate=segment_sr)
                total_audio += segment_audio
                speech_present = True

        # Обновляем время окончания
        old_end_time = end_time

def trim_segments_to_pitch(y, sr, min_energy_threshold=0.01, min_pause_duration=0.5, remove_other_pitch=False,
                           frame_length=2048, hop_length=512,
                           min_false_duration=0.3, pitch_margin=1.0):
    # 1. Найти сегменты с речью
    speech_segments = pt.find_speech_segments(y, sr, min_energy_threshold, min_pause_duration, frame_length, hop_length,
                                              min_false_duration)

    # 2. Массив для хранения обрезанных сегментов
    trimmed_segments = []

    for (start_time, end_time, segment_y, segment_sr) in speech_segments:
        # 3. Найти pitch для текущего сегмента
        pitch_values, voiced_times, _, _, _, _, _ = pt.extract_f0_voiced(segment_y, segment_sr)

        pitch_avg = np.nanmean(pitch_values)
        if remove_other_pitch:
            # Создание маски для фильтрации по диапазону (±50 Hz от среднего значения pitch)
            pitch_mask = (pitch_values > pitch_avg - 100) & (pitch_values < pitch_avg + 100)

            # Применение фильтрации к pitch_values и voiced_times
            pitch_values = pitch_values[pitch_mask]
            voiced_times = voiced_times[pitch_mask]

        if len(voiced_times) == 0:
            continue
        formant_energy = fmt.calculate_formant_energy_arr(segment_y, sr, 1)
        max_energy_time = fmt.find_max_formant_energy_time(formant_energy)

        # Найти ближайшее значение времени к max_energy_time
        closest_idx = np.argmin(np.abs(voiced_times - max_energy_time))

        # Проверить, попадает ли ближайшее время в допустимый диапазон
        if np.abs(voiced_times[closest_idx] - max_energy_time) <= 0.1:  # допустимая погрешность в 0.01 сек
            # Возвращаем pitch по найденному индексу
            pitch_main = pitch_values[closest_idx]
        else:
            pitch_main = pitch_avg

        # Пропуск сегмента, если в нём нет озвученных частей
        if len(voiced_times) > 0 and pitch_avg > 0:
            if remove_other_pitch:
                pitch_mask = (pitch_values > pitch_main - 100) & (pitch_values < pitch_main + 100)
                # Применение фильтрации к pitch_values и voiced_times
                voiced_times = voiced_times[pitch_mask]

            # 4. Определение границ участка с pitch
            pitch_start_time = voiced_times[0]
            pitch_end_time = voiced_times[-1]

            # 5. Добавление запаса (например, 0.1 сек)
            trimmed_start_time = max(0, pitch_start_time - pitch_margin)
            trimmed_end_time = min(end_time - start_time, pitch_end_time + pitch_margin)

            # 6. Конвертируем время в индексы для обрезки сигнала
            trimmed_start_sample = int(trimmed_start_time * segment_sr)
            trimmed_end_sample = int(trimmed_end_time * segment_sr)

            # Создание копии аудиосегмента для обработки
            voiced_mask = np.zeros_like(segment_y, dtype=bool)

            # Применение запасов в 0.1 секунды перед началом и после конца участков с pitch
            buffer_duration = 0.1
            for t in voiced_times:
                start_idx = max(0, int((t - buffer_duration) * sr))
                end_idx = min(len(segment_y), int((t + buffer_duration) * sr))

                # voiced_y = segment_y[start_idx:end_idx]
                # vowels = vw.detect_vowel_boundaries(voiced_y, sr, threshold=0.1)
                # if len(vowels) > 0:
                #     voiced_mask[start_idx:end_idx] = True
                # else:
                #     voiced_mask[start_idx:end_idx] = False
                voiced_mask[start_idx:end_idx] = True

            # Оставление озвученных участков и заполнение остальных тишиной
            segment_y[~voiced_mask] = 0.0

            # 7. Обрезаем аудиосигнал по новым границам
            trimmed_segment_y = segment_y[trimmed_start_sample:trimmed_end_sample]

            # 8. Сохраняем обрезанный сегмент
            trimmed_segments.append(
                (start_time + trimmed_start_time, start_time + trimmed_end_time, trimmed_segment_y, segment_sr))

    return trimmed_segments

def set_speed(input_file, output_file, speed):
    stretch_audio(input_file, output_file, ratio=speed)


def generate_signal(frequencies, bandwidths, intensities, times, delta_time, energy_correction=0, sr=44100):
    """
    Генерирует аудиосигнал на основе массивов частот, ширины канала и интенсивности.

    Parameters:
    - frequencies: Массив частот для каждого сегмента.
    - bandwidths: Массив ширины канала для каждого сегмента.
    - intensities: Массив интенсивности для каждого сегмента.
    - times: Массив временных меток для каждого значения частоты.
    - En: Коэффициент энергии.
    - sr: Частота дискретизации.

    Returns:
    - audio_signal: Сгенерированный аудиосигнал.
    """
    audio_signal = []

    if times[0] > 0:
        initial_silence_duration = times[0]
        initial_silence = np.zeros(int(sr * initial_silence_duration))
        audio_signal = np.concatenate((audio_signal, initial_silence))

    for i in range(1, len(times)):
        # Определяем параметры текущего сегмента
        freq = frequencies[i]
        intensity = intensities[i]
        duration = times[i] - times[i - 1]

        # Генерация сигнала для текущего сегмента
        if abs(duration - delta_time) <= 0.001 and not np.isnan(freq):
            # Расчёт энергии и амплитуды
            if energy_correction == 0:
                amplitude = intensity * 0.5
            else:
                bw = bandwidths[i]
                energy = intensity * energy_correction
                amplitude = np.sqrt(energy / bw)  # Амплитуда для синусоиды

            # Если длительность в пределах delta_time, генерируем звуковой сигнал
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            segment = amplitude * np.sin(2 * np.pi * freq * t)
            audio_signal = np.concatenate((audio_signal, segment))
        else:
            # Если длительность превышает delta_time, добавляем тишину
            silence_duration = duration - delta_time
            silence = np.zeros(int(silence_duration * sr))
            audio_signal = np.concatenate((audio_signal, silence))

    # Преобразуем итоговый сигнал в массив numpy
    audio_signal = np.array(audio_signal)

    # # Нормализуем для сохранения в аудиофайл
    # if np.max(np.abs(audio_signal)) > 0:
    #     audio_signal /= np.max(np.abs(audio_signal))

    return audio_signal


def mix_audio_signals(audio_signals):
    """
    Смешивает несколько аудиосигналов разной длины, добавляя тишину там, где сигнал отсутствует,
    и возвращает один аудиосигнал с длиной, равной максимальной длине среди всех сигналов.

    Parameters:
    - audio_signals (list of np.array): Список numpy массивов, представляющих аудиосигналы.

    Returns:
    - np.array: Смешанный аудиосигнал.
    """
    # Определяем максимальную длину среди всех сигналов
    max_length = max(len(signal) for signal in audio_signals)

    # Дополняем каждый сигнал тишиной до максимальной длины
    padded_signals = [
        np.pad(signal, (0, max_length - len(signal)), 'constant') for signal in audio_signals
    ]

    # Суммируем все сигналы для создания итогового смешанного сигнала
    mixed_signal = np.sum(padded_signals, axis=0)
    # mixed_signal = np.int16(mixed_signal / np.max(np.abs(mixed_signal)) * 32767)

    # Нормализуем итоговый сигнал, чтобы избежать переполнения
    # if np.max(np.abs(mixed_signal)) > 0:
    #     mixed_signal /= np.max(np.abs(mixed_signal))

    return mixed_signal
