import numpy as np
import math
import librosa
import scipy.signal
from scipy.interpolate import interp1d
from scipy.signal import resample
from scipy.signal import medfilt
from scipy.signal import butter, lfilter
from scipy.signal import get_window
import parselmouth as pm
from parselmouth.praat import call
from sklearn.linear_model import LinearRegression
import soundfile as sf
import concurrent.futures

from . import sk_filters as fl
from . import sk_formants as fmt
from . import sk_pitch as pt

def compute_vowel_type(y, sr, start, end, frame_length, hop_length):
    mfcc = librosa.feature.mfcc(y=y[start:end], sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)

    sound = pm.Sound(y[start:end], sampling_frequency=sr)
    formants = sound.to_formant_burg(time_step=0.01)

    # Используем только F1 и F2 для классификации
    f1 = np.mean([formants.get_value_at_time(1, t) for t in formants.ts() if not np.isnan(formants.get_value_at_time(1, t))])
    f2 = np.mean([formants.get_value_at_time(2, t) for t in formants.ts() if not np.isnan(formants.get_value_at_time(2, t))])

    if f1 < 450 and f2 > 1700:
        vowel_type = 'i'
    elif f1 < 450 and f2 < 1700:
        vowel_type = 'u'
    elif 450 <= f1 <= 800 and 700 <= f2 <= 1200:
        vowel_type = 'o'
    elif 450 <= f1 <= 800 and 1200 < f2 <= 1700:
        vowel_type = 'a'
    elif f1 > 800 and f2 < 1700:
        vowel_type = 'e'
    else:
        vowel_type = 'e'  # Default to 'e' for uncertain cases

    midpoint_time = (start + end) // 2 * hop_length
    return (midpoint_time, vowel_type)


def detect_vowel_boundaries_parallel(y, sr, threshold=0.1):
    y = fl.normalize_audio(y)

    frame_length = int(0.025 * sr)
    hop_length = int(0.01 * sr)

    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    vowel_segments = []
    in_vowel = False
    start_frame = 0

    for i in range(len(energy)):
        if energy[i] > threshold and zcr[i] < 0.1:
            if not in_vowel:
                start_frame = i
                in_vowel = True
        else:
            if in_vowel:
                end_frame = i
                vowel_segments.append((start_frame, end_frame))
                in_vowel = False

    if in_vowel:
        vowel_segments.append((start_frame, len(energy)))

    vowel_types = []

    # Параллельная обработка
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for start_frame, end_frame in vowel_segments:
            midpoint_frame = (start_frame + end_frame) // 2
            midpoint_time = midpoint_frame * hop_length

            start = max(0, midpoint_time - frame_length)
            end = min(len(y), midpoint_time + frame_length)

            # Отправляем задачи на исполнение
            futures.append(executor.submit(compute_vowel_type, y, sr, start, end, frame_length, hop_length))

        # Собираем результаты
        for future in concurrent.futures.as_completed(futures):
            vowel_types.append(future.result())

    return vowel_types

def detect_vowel_boundaries(y, sr, threshold=0.1):
    # Normalize audio
    y = fl.normalize_audio(y)

    frame_length = int(0.025 * sr)
    hop_length = int(0.01 * sr)

    # Compute energy and zero-crossing rate
    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    # Detect vowel segments
    vowel_segments = []
    in_vowel = False
    start_frame = 0

    for i in range(len(energy)):
        if energy[i] > threshold and zcr[i] < 0.1:
            if not in_vowel:
                start_frame = i
                in_vowel = True
        else:
            if in_vowel:
                end_frame = i
                vowel_segments.append((start_frame, end_frame))
                in_vowel = False

    # Check if the last segment ends at the end of the file
    if in_vowel:
        vowel_segments.append((start_frame, len(energy)))

    # Determine vowel types
    vowel_types = []
    for start_frame, end_frame in vowel_segments:
        # Compute the midpoint
        midpoint_frame = (start_frame + end_frame) // 2
        midpoint_time = midpoint_frame * hop_length

        start = max(0, midpoint_time - frame_length)
        end = min(len(y), midpoint_time + frame_length)
        mfcc = librosa.feature.mfcc(y=y[start:end], sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)

        # Use Parselmouth to get formant frequencies
        sound = pm.Sound(y[start:end], sampling_frequency=sr)
        formants = sound.to_formant_burg(time_step=0.01)

        # Extract average formant values
        f1 = np.mean([formants.get_value_at_time(1, t) for t in formants.ts() if not np.isnan(formants.get_value_at_time(1, t))])
        f2 = np.mean([formants.get_value_at_time(2, t) for t in formants.ts() if not np.isnan(formants.get_value_at_time(2, t))])

        # Determine vowel type based on MFCC and formant frequencies
        if f1 < 450 and f2 > 1700:
            vowel_type = 'i'
        elif f1 < 450 and f2 < 1700:
            vowel_type = 'u'
        elif 450 <= f1 <= 800 and 700 <= f2 <= 1200:
            vowel_type = 'o'
        elif 450 <= f1 <= 800 and 1200 < f2 <= 1700:
            vowel_type = 'a'
        elif f1 > 800 and f2 < 1700:
            vowel_type = 'e'
        else:
            vowel_type = 'e'  # Default to 'e' for uncertain cases

        vowel_types.append((midpoint_time, vowel_type))

    return vowel_types

def detect_vowel_boundaries2(y, sr, threshold=0.1):
    # Normalize audio
    y = fl.normalize_audio(y)

    frame_length = int(0.025 * sr)
    hop_length = int(0.01 * sr)

    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    vowel_segments = []
    in_vowel = False
    start_frame = 0

    for i in range(len(energy)):
        if energy[i] > threshold:
            if not in_vowel:
                start_frame = i
                in_vowel = True
        else:
            if in_vowel:
                end_frame = i
                vowel_segments.append((start_frame, end_frame))
                in_vowel = False

    # Check if the last segment ends at the end of the file
    if in_vowel:
        vowel_segments.append((start_frame, len(energy)))

    vowel_types = []
    for start_frame, end_frame in vowel_segments:
        # Compute the midpoint
        midpoint_frame = (start_frame + end_frame) // 2
        midpoint_time = midpoint_frame * hop_length

        start = max(0, midpoint_time - frame_length)
        end = min(len(y), midpoint_time + frame_length)
        mfcc = librosa.feature.mfcc(y=y[start:end], sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)

        # Use Parselmouth to get formant frequencies
        sound = pm.Sound(y[start:end], sampling_frequency=sr)
        formants = sound.to_formant_burg(time_step=0.01)

        # Extract average formant values
        f1 = np.mean(
            [formants.get_value_at_time(1, t) for t in formants.ts() if not np.isnan(formants.get_value_at_time(1, t))])
        f2 = np.mean(
            [formants.get_value_at_time(2, t) for t in formants.ts() if not np.isnan(formants.get_value_at_time(2, t))])

        # Determine vowel type based on MFCC and formant frequencies
        if mfcc_mean[2] > -5 and f1 < 800 and f2 > 1000 and f2 < 2000:
            vowel_type = 'e'
        elif mfcc_mean[1] > -5 and f1 > 400 and f1 < 800 and f2 > 1000 and f2 < 2000:
            vowel_type = 'a'
        elif mfcc_mean[3] > -5 and f1 < 400 and f2 > 2000:
            vowel_type = 'i'
        elif mfcc_mean[4] > -5 and f1 > 400 and f1 < 800 and f2 > 800 and f2 < 1500:
            vowel_type = 'o'
        else:
            vowel_type = 'u'

        vowel_types.append((midpoint_time, vowel_type))

    return vowel_types

def create_formant_mask_amplitude(freqs, formant_freqs, bandwidth=50):
    mask = np.zeros_like(freqs, dtype=bool)
    for f in formant_freqs:
        mask |= (freqs > f - bandwidth) & (freqs < f + bandwidth)
    return mask

def create_formant_mask_energy(freqs, formant_freqs, bandwidth=50):
    # Создание маски для частот формантов
    mask = np.zeros_like(freqs, dtype=bool)
    for freq in formant_freqs:
        low = max(0, freq - bandwidth)
        high = min(np.nanmax(freqs), freq + bandwidth)
        mask |= (freqs >= low) & (freqs <= high)
    return mask

def amplify_vowels(y, sr, vowel_boundaries, formant_gains_dict, frame_duration=0.05):
    frame_length = int(frame_duration * sr)
    hop_length = int(0.01 * sr)
    y_amplified = np.copy(y)

    for boundary, vowel_type in vowel_boundaries:
        start = max(0, boundary - frame_length // 2)
        end = min(len(y), boundary + frame_length // 2)
        segment = y[start:end]
        # freqs = fmt.formant_frequencies(segment, sr)
        freqs, _, _, _ = fmt.formant_frequencies(segment, sr)
        formant_gains = formant_gains_dict.get(vowel_type, [0, 0, 0, 0, 0])

        # print(f"Processing vowel type: {vowel_type}, Gains: {formant_gains}")

        # Apply formant amplification
        fft_segment = scipy.fftpack.fft(segment)
        freqs_segment = scipy.fftpack.fftfreq(len(segment), d=1 / sr)

        shifted_fft_segment = np.copy(fft_segment)
        for i, freqs_at_time in enumerate(freqs):
            for j, freq in enumerate(freqs_at_time):
                if not np.isnan(freq) and j < len(formant_gains):
                    gain = 10 ** (formant_gains[j] / 20)
                    # print(f"Applying gain: {gain} to frequency: {freq}")

                    nyquist = 0.5 * sr
                    normal_freq = freq / nyquist
                    width = 0.1
                    low = max(0.01, normal_freq - width / 2)
                    high = min(1.0, normal_freq + width / 2)
                    b, a = scipy.signal.butter(N=4, Wn=[low, high], btype='band')
                    filtered_segment = scipy.signal.filtfilt(b, a, segment)
                    filtered_segment_fft = scipy.fftpack.fft(filtered_segment)

                    mask = create_formant_mask_amplitude(freqs_segment, [freq], bandwidth=50)
                    shifted_fft_segment[mask] = filtered_segment_fft[mask] * gain

        segment_filtered = scipy.fftpack.ifft(shifted_fft_segment).real
        y_amplified[start:end] = segment_filtered

    y_amplified = np.clip(y_amplified, -1.0, 1.0)
    return y_amplified

def determine_vowel_type(frame_start, vowel_boundaries, sr, frame_duration=0.05):
    frame_length = int(frame_duration * sr)
    for boundary, vowel_type in vowel_boundaries:
        if boundary - frame_length <= frame_start <= boundary + frame_length:
            return vowel_type
    return 'unknown'

def apply_formant_shifts_vowels(y, sr, vowel_boundaries, formant_shifts_dict, frame_duration=0.05):
    y_shifted = np.copy(y)

    frame_length = int(frame_duration * sr)
    hop_length = int(frame_duration * sr / 2)  # Оптимизируйте шаг для наложения

    for start in range(0, len(y) - frame_length, hop_length):
        end = start + frame_length
        if end > len(y):
            end = len(y)
        segment = y[start:end]

        vowel_type = determine_vowel_type(start, vowel_boundaries, sr, frame_duration)
        formant_shifts = formant_shifts_dict.get(vowel_type, [0, 0, 0, 0, 0])

        if np.any(formant_shifts):
            fft_segment = scipy.fftpack.fft(segment)
            freqs = scipy.fftpack.fftfreq(len(segment), d=1/sr)

            # Создание маски для частот формантов
            mask = np.zeros_like(freqs, dtype=bool)
            for shift in formant_shifts:
                formant_freq = shift
                mask |= (freqs > formant_freq - 50) & (freqs < formant_freq + 50)

            shifted_fft_segment = np.copy(fft_segment)
            for shift in formant_shifts:
                formant_freq = shift
                mask_freqs = (freqs > formant_freq - 50) & (freqs < formant_freq + 50)
                if np.any(mask_freqs):
                    shifted_fft_segment[mask_freqs] = np.interp(
                        freqs[mask_freqs] + shift,
                        freqs[mask_freqs],
                        fft_segment[mask_freqs],
                        left=0,
                        right=0
                    )

            segment_shifted = scipy.fftpack.ifft(shifted_fft_segment).real
            y_shifted[start:end] = segment_shifted

    y_shifted = np.clip(y_shifted, -1.0, 1.0)
    return y_shifted

def energy_vowels(y, sr, vowel_boundaries, formant_gains_dict, frame_duration=0.05):
    frame_length = int(frame_duration * sr)
    if frame_length == 0:
        return y

    hop_length = int(0.01 * sr)
    y_energy_amplified = np.copy(y)

    for boundary, vowel_type in vowel_boundaries:
        start = max(0, boundary - frame_length // 2)
        end = min(len(y), boundary + frame_length // 2)
        if start == end:
            continue
        segment = y[start:end]
        freqs, times, bandwidths, intensities = fmt.formant_frequencies(segment, sr)
        formant_gains = formant_gains_dict.get(vowel_type, [0, 0, 0, 0])

        fft_segment = scipy.fftpack.fft(segment)
        freqs_segment = scipy.fftpack.fftfreq(len(segment), d=1 / sr)

        shifted_fft_segment = np.copy(fft_segment)
        for i, freqs_at_time in enumerate(freqs):
            for j, freq in enumerate(freqs_at_time):
                if not np.isnan(freq) and j < len(formant_gains) and formant_gains[j] != 0:
                    gain = 10 ** (formant_gains[j] / 10)  # Power gain
                    nyquist = 0.5 * sr
                    normal_freq = freq / nyquist
                    width = 0.1
                    low = max(0.01, normal_freq - width / 2)
                    high = min(1.0, normal_freq + width / 2)
                    b, a = scipy.signal.butter(N=4, Wn=[low, high], btype='band')
                    filtered_segment = scipy.signal.filtfilt(b, a, segment)
                    filtered_segment_fft = scipy.fftpack.fft(filtered_segment)

                    mask = create_formant_mask_energy(freqs_segment, [freq], bandwidth=50)
                    shifted_fft_segment[mask] = filtered_segment_fft[mask] * gain

        segment_filtered = scipy.fftpack.ifft(shifted_fft_segment).real
        y_energy_amplified[start:end] = segment_filtered

    # Нормализация сигнала для предотвращения клиппинга
    y_energy_amplified = np.clip(y_energy_amplified, -1.0, 1.0)
    return y_energy_amplified

def shift_formants_vowels(input_file, output_file, vowel_boundaries, formant_shifts_dict, frame_duration=0.05):
    y, sr = librosa.load(input_file, sr=None)
    y_shifted = apply_formant_shifts_vowels(y, sr, vowel_boundaries, formant_shifts_dict, frame_duration)
    sf.write(output_file, y_shifted, sr)


def calculate_formant_amplitude(y, sr, vowel_boundaries, formants=None):
    formant_amplitudes = {f'f{i + 1}': [] for i in range(5)}  # Для F1-F5

    for index, (start, vowel_type) in enumerate(vowel_boundaries):
        # Определяем сегмент звука вокруг границы
        start = max(0, start - int(0.025 * sr))
        end = min(len(y), start + int(0.025 * sr))
        segment = y[start:end]

        # Получаем частоты формантов для сегмента
        if formants:
            frequencies = formants[index]["frequencies"]
        else:
            frequencies, _, _, _ = fmt.formant_frequencies(segment, sr)

        for i, freqs_at_time in enumerate(frequencies):
            for freq in freqs_at_time:
                if not np.isnan(freq):
                    # Создаем фильтр для частотной области вокруг форманты
                    nyquist = 0.5 * sr
                    normal_freq = freq / nyquist
                    width = 0.1
                    low = max(0.01, normal_freq - width / 2)
                    high = min(1.0, normal_freq + width / 2)

                    b, a = scipy.signal.butter(N=4, Wn=[low, high], btype='band')
                    filtered_segment = scipy.signal.filtfilt(b, a, segment)

                    # Преобразование отфильтрованного сегмента в частотную область
                    fft_filtered_segment = scipy.fftpack.fft(filtered_segment)
                    freqs_filtered_segment = scipy.fftpack.fftfreq(len(filtered_segment), d=1 / sr)

                    # Создаем маску для частот формантов
                    mask = create_formant_mask_amplitude(freqs_filtered_segment, [freq], bandwidth=50)

                    if np.any(mask):
                        # Рассчитываем амплитуду в децибелах
                        amplitude = 20 * np.log10(np.abs(fft_filtered_segment[mask]).mean())
                        formant_amplitudes[f'f{i + 1}'].append(amplitude)
                else:
                    formant_amplitudes[f'f{i + 1}'].append(freq)

    return formant_amplitudes

def calculate_formant_freq(y, sr, vowel_boundaries, formants):
    mean_formants = []

    for index, (boundary, vowel_type) in enumerate(vowel_boundaries):
        start = max(0, boundary - sr // 2)
        end = min(len(y), boundary + sr // 2)
        segment = y[start:end]

        # Получаем частоты формантов для сегмента
        if formants:
            frequencies = formants[index]["frequencies"]
        else:
            frequencies, _, _, _ = fmt.formant_frequencies(segment, sr)

        # Рассчитываем средние значения для каждой форманты F1-F5
        formant_means = []
        for i in range(5):
            if np.all(np.isnan(frequencies[i])):
                formant_means.append(None)  # Если не удается рассчитать значение для форманты
            else:
                formant_means.append(np.nanmean(frequencies[i]))

        mean_formants.append(formant_means)

    return mean_formants


def calculate_formant_energy(y, sr, vowel_boundaries, formants=None):
    formant_energies = {f'f{i + 1}': [] for i in range(5)}  # Для F1-F5

    for index, (start, vowel_type) in enumerate(vowel_boundaries):
        # Определяем сегмент звука вокруг границы
        start = max(0, start - int(0.025 * sr))
        end = min(len(y), start + int(0.025 * sr))
        segment = y[start:end]

        # Получаем частоты формантов для сегмента
        if formants:
            frequencies = formants[index]["frequencies"]
        else:
            frequencies, _, _, _ = fmt.formant_frequencies(segment, sr)

        for i, freqs_at_time in enumerate(frequencies):
            for j, freq in enumerate(freqs_at_time):
                if not np.isnan(freq):  # Только для F1-F5
                    # Создаем фильтр для частотной области вокруг форманты
                    nyquist = 0.5 * sr
                    normal_freq = freq / nyquist
                    width = 0.1  # Ширина канала фильтра
                    low = max(0.01, normal_freq - width / 2)
                    high = min(1.0, normal_freq + width / 2)

                    b, a = scipy.signal.butter(N=4, Wn=[low, high], btype='band')
                    filtered_segment = scipy.signal.filtfilt(b, a, segment)

                    # Преобразование отфильтрованного сегмента в частотную область
                    fft_filtered_segment = scipy.fftpack.fft(filtered_segment)
                    freqs_filtered_segment = scipy.fftpack.fftfreq(len(filtered_segment), d=1 / sr)

                    # Создаем маску для частот формантов
                    mask = create_formant_mask_energy(freqs_filtered_segment, [freq], bandwidth=50)

                    if np.any(mask):
                        # Рассчитываем энергию
                        energy = np.mean(np.abs(fft_filtered_segment[mask]) ** 2)
                        formant_energies[f'f{i + 1}'].append(energy)
                else:
                    formant_energies[f'f{i + 1}'].append(freq)

    return formant_energies


def mean_amplitude_dB_for_vowels(y, sr, vowel_boundaries, formants=None):
    # Группировка гласных
    vowel_types = group_vowels(vowel_boundaries)
    formant_amplitudes_by_vowel = {vowel: {f'f{i + 1}': [] for i in range(5)} for vowel in vowel_types}

    # Рассчитываем амплитуды для формант
    formant_amplitudes = calculate_formant_amplitude(y, sr, vowel_boundaries, formants=formants)

    # Заполняем словарь амплитуд по гласным
    for index, (start, vowel_type) in enumerate(vowel_boundaries):
        for i in range(5):
            formant_key = f'f{i + 1}'
            amplitude = formant_amplitudes[formant_key][index]
            formant_amplitudes_by_vowel[vowel_type][formant_key].append(amplitude)

    # Рассчитываем средние значения амплитуд по гласным
    mean_amplitudes_by_vowel = {}
    for vowel, amplitudes in formant_amplitudes_by_vowel.items():
        mean_amplitudes_by_vowel[vowel] = {}
        for formant_key, values in amplitudes.items():
            if values and not np.all(np.isnan(values)):
                mean_amplitudes_by_vowel[vowel][formant_key] = np.nanmean(values)
            else:
                mean_amplitudes_by_vowel[vowel][formant_key] = None

    # Определение отсутствующих гласных
    missing_vowels = find_missing_vowels(vowel_boundaries)

    # Заполнение отсутствующих гласных значениями от наиболее похожих
    for missing_vowel in missing_vowels:
        closest_vowel = find_closest_vowel(mean_amplitudes_by_vowel.keys(), mean_amplitudes_by_vowel)
        if closest_vowel:
            mean_amplitudes_by_vowel[missing_vowel] = mean_amplitudes_by_vowel[closest_vowel].copy()
        else:
            mean_amplitudes_by_vowel[missing_vowel] = {'f1': 0, 'f2': 0, 'f3': 0, 'f4': 0, 'f5': 0}

    return mean_amplitudes_by_vowel

import numpy as np

def mean_energy_for_vowels(y, sr, vowel_boundaries, formants=None):
    vowel_types = group_vowels(vowel_boundaries)
    formant_energies_by_vowel = {vowel: {f'f{i + 1}': [] for i in range(5)} for vowel in vowel_types}

    # Получаем энергии формантов для всех границ
    formant_energies = calculate_formant_energy(y, sr, vowel_boundaries, formants=formants)

    # Заполняем formant_energies_by_vowel значениями
    for index, (start, vowel_type) in enumerate(vowel_boundaries):
        for i in range(5):
            formant_key = f'f{i + 1}'
            energy = formant_energies[formant_key][index]
            formant_energies_by_vowel[vowel_type][formant_key].append(energy)

    # Рассчитываем средние значения для каждой группы гласных
    mean_energies_by_vowel = {}
    for vowel, energies in formant_energies_by_vowel.items():
        mean_energies_by_vowel[vowel] = {}
        for formant_key, values in energies.items():
            if values:
                mean_energies_by_vowel[vowel][formant_key] = np.mean(values)
            else:
                mean_energies_by_vowel[vowel][formant_key] = None

    return mean_energies_by_vowel


def mean_formants_for_vowels(y, sr, vowel_boundaries, formants=None):
    vowel_types = group_vowels(vowel_boundaries)
    formant_means_by_vowel = {vowel: {f'f{i + 1}': [] for i in range(5)} for vowel in vowel_types}

    # Получаем средние значения формантов
    mean_formants = calculate_formant_freq(y, sr, vowel_boundaries, formants=formants)

    # Заполняем словарь formant_means_by_vowel значениями
    for (start, vowel_type), vowel_formants in zip(vowel_boundaries, mean_formants):
        for i, freq in enumerate(vowel_formants):
            formant_key = f'f{i + 1}'
            formant_means_by_vowel[vowel_type][formant_key].append(freq)

    # Рассчитываем средние значения для каждой группы гласных
    mean_formants_by_vowel = {
        vowel: {
            formant_key: np.nanmean([f for f in frequencies if f is not None]) if frequencies and any(
                f is not None for f in frequencies) else np.nan
            for formant_key, frequencies in vowel_formants.items()
        }
        for vowel, vowel_formants in formant_means_by_vowel.items()
    }

    return mean_formants_by_vowel

def group_vowels(vowel_boundaries):
    # Извлекаем только типы гласных
    vowel_types = [vowel_type for _, vowel_type in vowel_boundaries]

    # Получаем уникальные типы
    unique_vowel_types = list(set(vowel_types))

    unique_vowel_types.sort()

    return unique_vowel_types

def find_missing_vowels(vowel_boundaries):
    # Определяем все возможные гласные
    all_vowels = {'i', 'u', 'o', 'a', 'e'}

    # Получаем уникальные гласные, присутствующие в данных
    grouped_vowels = set(group_vowels(vowel_boundaries))

    # Определяем отсутствующие гласные
    missing_vowels = all_vowels - grouped_vowels

    return missing_vowels

def find_closest_vowel(existing_vowels, mean_amplitudes_by_vowel):
    closest_vowel = None

    for vowel in existing_vowels:
        if vowel in mean_amplitudes_by_vowel:
            f1_amplitude = mean_amplitudes_by_vowel[vowel].get('f1', np.nan)
            f2_amplitude = mean_amplitudes_by_vowel[vowel].get('f2', np.nan)

            if not np.isnan(f1_amplitude) and not np.isnan(f2_amplitude):
                closest_vowel = vowel
                break

    return closest_vowel

def create_formant_mask_low_high(freqs, low, high):
    mask = np.zeros_like(freqs, dtype=bool)
    mask |= (freqs >= low) & (freqs <= high)
    return mask

def amplitude_vowels_mul(y, sr, vowels, frame_duration=0.05, formants=None):
    frame_length = int(frame_duration * sr)
    if frame_length == 0:
        return y

    y_energy_amplified = np.copy(y)

    for index, (boundary, vowel_type) in enumerate(vowels["vowel_boundaries"]):
        start = max(0, boundary - frame_length // 2)
        end = min(len(y), boundary + frame_length // 2)
        if start == end:
            continue
        segment = y[start:end]
        if formants:
            freqs = formants[index]["frequencies"]
        else:
            freqs, _, _, _ = fmt.formant_frequencies(segment, sr)

        fft_segment = scipy.fftpack.fft(segment)
        freqs_segment = scipy.fftpack.fftfreq(len(segment), d=1 / sr)

        shifted_fft_segment = np.copy(fft_segment)
        for i, freqs_at_time in enumerate(freqs):
            if len(freqs_at_time) == 0 or np.all(np.isnan(freqs_at_time)):
                continue
            f_name = f'f{i+1}'
            if not f_name in vowels["amplitude"][f_name]:
                continue
            formant_gain = vowels["amplitude"][f_name][index]
            freq = np.nanmean(freqs_at_time)
            if not np.isnan(formant_gain) and formant_gain > 0 and not np.isnan(freq) and freq > 0:
                low = np.nanmin(freqs_at_time)-10
                high = np.nanmax(freqs_at_time)+10
                b, a = scipy.signal.butter(N=4, Wn=[low, high], btype='band', fs=sr)

                filtered_segment = scipy.signal.filtfilt(b, a, segment)
                filtered_segment_fft = scipy.fftpack.fft(filtered_segment)

                mask = create_formant_mask_low_high(freqs_segment, low, high)
                shifted_fft_segment[mask] = filtered_segment_fft[mask] * formant_gain

        segment_filtered = scipy.fftpack.ifft(shifted_fft_segment).real
        y_energy_amplified[start:end] = segment_filtered

    # Нормализация сигнала для предотвращения клиппинга
    y_energy_amplified = np.clip(y_energy_amplified, -1.0, 1.0)
    return y_energy_amplified

def get_vowel_formant_info(y, sr, vowel_boundaries):
    formants = []
    for index, (start, vowel_type) in enumerate(vowel_boundaries):
        # Определяем сегмент звука вокруг границы
        start = max(0, start - int(0.025 * sr))
        end = min(len(y), start + int(0.025 * sr))
        segment = y[start:end]

        # Получаем частоты формантов для сегмента
        frequencies, voiced_time, bandwidths, intensities = fmt.formant_frequencies(segment, sr)
        formants.append({"frequencies": frequencies, "voiced_times": voiced_time,
                         "bandwidths": bandwidths, "intensities": intensities})

    return formants

def smooth_stretch_vowel(y, sr, stretch_factor):
    """
    Нелинейное растяжение участка с гласной с плавным переходом на границах.

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        stretch_factor: float
            Фактор растяжения (например, 5.0 для увеличения длины в 5 раз).

    Возвращает:
        np.ndarray: Аудиосигнал с растянутым и сглаженным участком.
    """
    # Используем librosa для растяжения
    stretched_vowel = librosa.effects.time_stretch(y, rate=1 / stretch_factor)
    stretched_len = len(stretched_vowel)

    # Создаем весовую функцию с плавным затуханием к границам
    weights = np.hanning(stretched_len)

    # Применяем веса к растянутому сигналу
    smoothed_vowel = stretched_vowel * weights

    return smoothed_vowel


def stretch_vowels_preserve_pitch(y, sr, vowel_boundaries, delta_seconds, speed_factor):
    """
    Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными,
    при этом сохраняется тональность (pitch).

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        vowel_boundaries: list of tuples
            Список пар (индекс_центра_гласной, гласная).
        delta_seconds: float
            Длительность окрестности гласной (в секундах).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).

    Возвращает:
        np.ndarray: Измененный аудиосигнал.
    """
    # Рассчитываем количество фреймов для delta
    delta_frames = int(delta_seconds * sr)

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for vowel_frame, vowel in vowel_boundaries:
        # Диапазон окрестности гласной
        start = max(0, vowel_frame - delta_frames)
        end = min(len(y), vowel_frame + delta_frames)

        # Часть до текущей гласной (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем гласную (растягиваем/сжимаем с сохранением тональности)
        vowel_audio = y[start:end]
        stretched_vowel = librosa.effects.time_stretch(vowel_audio, rate=1 / speed_factor)
        # stretched_vowel = smooth_stretch_vowel(vowel_audio, sr, speed_factor)
        output_audio.append(stretched_vowel)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)


def stretch_vowels_preserve_pitch2(y, sr, vowel_boundaries, delta_seconds, speed_factor):
    """
    Ускоряет/замедляет аудио за счет повторения фрагментов с гласными,
    при этом сохраняется тональность (pitch).

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        vowel_boundaries: list of tuples
            Список пар (индекс_центра_гласной, гласная).
        delta_seconds: float
            Длительность окрестности гласной (в секундах).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).

    Возвращает:
        np.ndarray: Изменённый аудиосигнал.
    """
    # Рассчитываем количество фреймов для delta
    delta_frames = int(delta_seconds * sr)

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for vowel_frame, vowel in vowel_boundaries:
        # Диапазон окрестности гласной
        start = max(0, vowel_frame - delta_frames)
        end = min(len(y), vowel_frame + delta_frames)

        # Часть до текущей гласной (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем гласную
        vowel_audio = y[start:end]
        original_length = len(vowel_audio)
        target_length = int(original_length * speed_factor)

        # Если целевая длина больше исходной, повторяем фрагменты
        if target_length > original_length:
            repeats = target_length // original_length
            remainder = target_length % original_length
            stretched_vowel = np.concatenate(
                [vowel_audio] * repeats + [vowel_audio[:remainder]]
            )
        else:
            # Если целевая длина меньше исходной, обрезаем
            stretched_vowel = vowel_audio[:target_length]

        output_audio.append(stretched_vowel)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)


def stretch_vowels_preserve_pitch3(y, sr, vowel_boundaries, delta_seconds, speed_factor):
    """
    Ускоряет/замедляет аудио за счет чередования прямого и обратного повторения фрагментов с гласными,
    при этом сохраняется тональность (pitch).

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        vowel_boundaries: list of tuples
            Список пар (индекс_центра_гласной, гласная).
        delta_seconds: float
            Длительность окрестности гласной (в секундах).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).

    Возвращает:
        np.ndarray: Изменённый аудиосигнал.
    """
    # Рассчитываем количество фреймов для delta
    delta_frames = int(delta_seconds * sr)

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for vowel_frame, vowel in vowel_boundaries:
        # Диапазон окрестности гласной
        start = max(0, vowel_frame - delta_frames)
        end = min(len(y), vowel_frame + delta_frames)

        # Часть до текущей гласной (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем гласную
        vowel_audio = y[start:end]
        original_length = len(vowel_audio)
        target_length = int(original_length * speed_factor)

        # Создаём инвертированный фрагмент
        reversed_audio = vowel_audio[::-1]

        # Чередуем A (исходный) и B (инвертированный) до нужной длины
        stretched_vowel = []
        while len(stretched_vowel) < target_length:
            if len(stretched_vowel) + original_length <= target_length:
                stretched_vowel.extend(vowel_audio)
            else:
                stretched_vowel.extend(vowel_audio[:target_length - len(stretched_vowel)])

            if len(stretched_vowel) + original_length <= target_length:
                stretched_vowel.extend(reversed_audio)
            else:
                stretched_vowel.extend(reversed_audio[:target_length - len(stretched_vowel)])

        # Преобразуем в массив и добавляем к результату
        stretched_vowel = np.array(stretched_vowel[:target_length])
        output_audio.append(stretched_vowel)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)

def stretch_vowels_preserve_pitch4(y, sr, vowel_boundaries, delta_seconds, speed_factor, filter_size=200):
    """
    Ускоряет/замедляет аудио за счёт чередования прямого и обратного повторения фрагментов с гласными,
    применяя медианный фильтр для устранения резких колебаний.

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        vowel_boundaries: list of tuples
            Список пар (индекс_центра_гласной, гласная).
        delta_seconds: float
            Длительность окрестности гласной (в секундах).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).
        filter_size: int
            Размер окна медианного фильтра (должен быть нечётным).

    Возвращает:
        np.ndarray: Изменённый аудиосигнал.
    """
    # Проверяем и исправляем размер фильтра
    if filter_size % 2 == 0:
        filter_size += 1  # Преобразуем в нечётное

    # Рассчитываем количество фреймов для delta
    delta_frames = int(delta_seconds * sr)

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for vowel_frame, vowel in vowel_boundaries:
        # Диапазон окрестности гласной
        start = max(0, vowel_frame - delta_frames)
        end = min(len(y), vowel_frame + delta_frames)

        # Часть до текущей гласной (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем гласную
        vowel_audio = y[start:end]
        original_length = len(vowel_audio)
        target_length = int(original_length * speed_factor)

        # Создаём инвертированный фрагмент
        reversed_audio = vowel_audio[::-1]

        # Чередуем A (исходный) и B (инвертированный) до нужной длины
        stretched_vowel = []
        while len(stretched_vowel) < target_length:
            if len(stretched_vowel) + original_length <= target_length:
                stretched_vowel.extend(vowel_audio)
            else:
                stretched_vowel.extend(vowel_audio[:target_length - len(stretched_vowel)])

            if len(stretched_vowel) + original_length <= target_length:
                stretched_vowel.extend(reversed_audio)
            else:
                stretched_vowel.extend(reversed_audio[:target_length - len(stretched_vowel)])

        # Преобразуем в массив и обрезаем до целевой длины
        stretched_vowel = np.array(stretched_vowel[:target_length])

        # Применяем медианный фильтр
        stretched_vowel_filtered = medfilt(stretched_vowel, kernel_size=filter_size)

        # Добавляем сглаженный фрагмент к результату
        output_audio.append(stretched_vowel_filtered)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)


def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

def stretch_vowels_preserve_pitch5(y, sr, vowel_boundaries, delta_seconds, speed_factor, cutoff_freq=5000):
    """
    Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными,
    с применением сглаживания переходов и фильтрации для уменьшения эха.

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        vowel_boundaries: list of tuples
            Список пар (индекс_центра_гласной, гласная).
        delta_seconds: float
            Длительность окрестности гласной (в секундах).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).
        cutoff_freq: float
            Частота среза для низкочастотного фильтра.

    Возвращает:
        np.ndarray: Измененный аудиосигнал.
    """
    # Рассчитываем количество фреймов для delta
    delta_frames = int(delta_seconds * sr)

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for vowel_frame, vowel in vowel_boundaries:
        # Диапазон окрестности гласной
        start = max(0, vowel_frame - delta_frames)
        end = min(len(y), vowel_frame + delta_frames)

        # Часть до текущей гласной (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем гласную
        vowel_audio = y[start:end]
        stretched_vowel = librosa.effects.time_stretch(vowel_audio, rate=1 / speed_factor)

        # Применяем низкочастотный фильтр
        stretched_vowel = butter_lowpass_filter(stretched_vowel, cutoff=cutoff_freq, fs=sr)

        # Сглаживаем переходы через fade-in/fade-out
        fade_length = int(0.1 * sr)  # Длительность затухания в 0.1 секунды
        fade_in = np.linspace(0, 1, fade_length)
        fade_out = np.linspace(1, 0, fade_length)

        if len(stretched_vowel) > 2 * fade_length:
            stretched_vowel[:fade_length] *= fade_in
            stretched_vowel[-fade_length:] *= fade_out

        output_audio.append(stretched_vowel)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)


def wsola(audio, sr, speed_factor, frame_size=2048, hop_size=512):
    """
    Реализует WSOLA для изменения скорости аудиосигнала с сохранением высоты тона.
    """
    # Новый шаг окна при изменении скорости
    new_hop_size = max(1, int(hop_size / speed_factor))

    # Генерация окна (например, Ханнинг)
    window = get_window("hann", frame_size)

    # Рассчитываем длину выходного сигнала
    output_length = int(len(audio) * speed_factor)
    output_audio = np.zeros(output_length, dtype=np.float32)

    # Инициализация индексов для чтения и записи
    read_index = 0
    write_index = 0

    # Цикл по фреймам
    while read_index + frame_size <= len(audio):
        # Извлечение фрейма и наложение окна
        frame = audio[read_index:read_index + frame_size] * window

        # Запись фрейма в выходной массив
        if write_index + frame_size <= output_length:
            output_audio[write_index:write_index + frame_size] += frame
        else:
            # Если выходной массив уже полностью заполнен, записываем только часть фрейма
            output_audio[write_index:output_length] += frame[:output_length - write_index]

        # Обновление индексов
        read_index += hop_size
        write_index += new_hop_size

        # Проверка на окончание записи
        if write_index >= output_length:
            break

    return output_audio

def stretch_vowels_preserve_pitch6(y, sr, vowel_boundaries, delta_seconds, speed_factor):
    """
    Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными,
    при этом сохраняется тональность (pitch).

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        vowel_boundaries: list of tuples
            Список пар (индекс_центра_гласной, гласная).
        delta_seconds: float
            Длительность окрестности гласной (в секундах).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).

    Возвращает:
        np.ndarray: Измененный аудиосигнал.
    """
    # Рассчитываем количество фреймов для delta
    delta_frames = int(delta_seconds * sr)

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for vowel_frame, vowel in vowel_boundaries:
        # Диапазон окрестности гласной
        start = max(0, vowel_frame - delta_frames)
        end = min(len(y), vowel_frame + delta_frames)

        # Часть до текущей гласной (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем гласную (растягиваем/сжимаем с сохранением тональности)
        vowel_audio = y[start:end]
        # stretched_vowel = librosa.effects.time_stretch(vowel_audio, rate=1 / speed_factor)
        stretched_vowel = wsola(vowel_audio, sr, speed_factor=speed_factor)
        output_audio.append(stretched_vowel)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)

def stretch_vowels_preserve_pitch7(y, sr, intervals, speed_factor, cutoff_freq=5000):
    """
    Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными,
    с применением сглаживания переходов и фильтрации для уменьшения эха.

    Параметры:
        y: np.ndarray
            Аудиосигнал.
        sr: int
            Частота дискретизации.
        intervals: list of tuples
            Список пар (начало_интервала_в_мс, конец_интервала_в_мс).
        speed_factor: float
            Фактор изменения скорости (например, 2.0 для замедления в 2 раза).
        cutoff_freq: float
            Частота среза для низкочастотного фильтра.

    Возвращает:
        np.ndarray: Измененный аудиосигнал.
    """
    # Преобразуем интервалы из миллисекунд в индексы
    intervals_in_frames = [
        (int(start_ms / 1000 * sr), int(end_ms / 1000 * sr)) for start_ms, end_ms in intervals
    ]

    # Новый массив для результата
    output_audio = []
    current_index = 0

    for start, end in intervals_in_frames:
        # Убедимся, что индексы в пределах длины сигнала
        start = max(0, start)
        end = min(len(y), end)

        # Часть до текущего интервала (остается неизменной)
        if current_index < start:
            output_audio.append(y[current_index:start])

        # Обрабатываем интервал
        vowel_audio = y[start:end]
        stretched_vowel = librosa.effects.time_stretch(vowel_audio, rate=1 / speed_factor)

        # Применяем низкочастотный фильтр
        stretched_vowel = butter_lowpass_filter(stretched_vowel, cutoff=cutoff_freq, fs=sr)

        output_audio.append(stretched_vowel)

        # Обновляем текущий индекс
        current_index = end

    # Добавляем оставшуюся часть сигнала
    if current_index < len(y):
        output_audio.append(y[current_index:])

    # Объединяем все части в один сигнал
    return np.concatenate(output_audio)

def detect_vowel_boundaries_gradient(input_audio_file):

    def hz_to_mel(frequency_hz):
        """Преобразует частоту из Гц в MEL."""
        return 2595 * np.log10(1 + frequency_hz / 5000)

    def angle_bac(x, y):
        # Рассчитываем тангенс угла BAC
        tan_angle = y / x

        # Используем арктангенс для получения угла в радианах
        rad_angle = math.atan(tan_angle)

        # Переводим угол из радианов в градусы
        deg_angle = math.degrees(rad_angle)

        return deg_angle

    def filter_pitch(t_pitch, freq, bandwidth, times, eps=0.0001):
        # Создаем пустые списки для хранения отфильтрованных значений
        filtered_freq = []
        filtered_bandwidth = []
        filtered_times = []

        for time in t_pitch:
            # Находим индекс элемента в times1, который соответствует времени в t_pitch с учетом погрешности
            index = np.argmin(np.abs(times - time))

            if np.abs(time - times[index]) < eps:
                filtered_freq.append(freq[index])
                filtered_bandwidth.append(bandwidth[index])
                filtered_times.append(times[index])

        # Преобразуем результаты обратно в массивы NumPy
        filtered_freq = np.array(filtered_freq)
        filtered_bandwidth = np.array(filtered_bandwidth)
        filtered_times = np.array(filtered_times)

        return filtered_freq, filtered_bandwidth, filtered_times

    def extract_speech(input_audio_file):
        y, sr = librosa.load(input_audio_file)
        # y = vm.trim_silence(y, sr)
        y, sr = pt.flatten_pitch(y, sr)
        if y is None:
            return None, None, None, None

        f_pitch, t_pitch, intensity_values, intensity_times, _, _, _ = pt.extract_f0_voiced(y, sr, speech=True, time_step=0.001)
        if f_pitch is None:
            return False

        f_pitch = np.array(f_pitch)
        t_pitch = np.array(t_pitch)

        f, t, bandwidths, _ = fmt.formant_frequencies(y, sr, speech=False, time_step=0.001)
        try:
            if f is None:
                return None, None, None, None
            freq1 = np.array(f[0])
            freq2 = np.array(f[1])
            if bandwidths is None:
                return None, None, None, None
            bandwidth1 = np.array(bandwidths[0])
            bandwidth2 = np.array(bandwidths[1])
            times = np.array(t)
        except ValueError:
            return False

        mask = freq1 > 0
        freq1 = freq1[mask]
        bandwidth1 = bandwidth1[mask]
        times1 = times[mask]

        mask = freq2 > 0
        freq2 = freq2[mask]
        bandwidth2 = bandwidth2[mask]
        times2 = times[mask]

        freq1, bandwidth1, times1 = filter_pitch(t_pitch, freq1, bandwidth1, times1)
        freq2, bandwidth2, times2 = filter_pitch(t_pitch, freq2, bandwidth2, times2)

        # freq1 = hz_to_mel(freq1)
        # freq2 = hz_to_mel(freq2) / 4.3

        # bandwidth1 = hz_to_mel(bandwidth1)
        # bandwidth2 = hz_to_mel(bandwidth2) / 1.5

        return freq1, bandwidth1, times1, freq2, bandwidth2, times2

    def find_frequency_peaks(freq_files, bw_files, time_files):
        """
        Находит пики частот, их ширину канала и длительности для каждого файла.

        Параметры:
            freq_files (list): Список массивов частот, один массив на файл.
            bw_files (list): Список массивов ширины канала, один массив на файл.
            time_files (list): Список массивов времени, один массив на файл.

        Возвращает:
            list: Список списков кортежей (peak_freq, peak_bw, duration) для каждого файла.
        """
        all_peaks = []

        for freq, bw, times in zip(freq_files, bw_files, time_files):
            if len(freq) != len(times) or len(freq) != len(bw):
                raise ValueError("Длины массивов freq, bw и times должны совпадать.")

            peaks = []
            n = len(freq)
            sum_angle = 0
            count_angle = 0

            if n < 2:
                continue

            # Добавляем первый элемент как пик
            peaks.append((round(freq[0]), bw[0], times[0] if n > 1 else 0))

            # import matplotlib.pyplot as plt
            # data = freq[100:200]
            # # Создаем список индексов для оси X
            # x = range(len(data))
            # # Строим график
            # plt.plot(x, data)
            # # Добавляем заголовок и подписи осей
            # plt.title('График частот')
            # plt.xlabel('Индекс')
            # plt.ylabel('Частота')
            # # Показываем график
            # plt.show()

            # Находим внутренние пики
            for i in range(1, n - 1):
                freq_prior = round(freq[i - 1])
                freq_cur = round(freq[i])
                freq_next = round(freq[i + 1])

                time_diff = (times[i] - times[i - 1]) * 10
                freq_diff = freq_cur - freq_prior
                angle = angle_bac(time_diff, freq_diff)

                if count_angle == 0:
                    old_angle = angle
                else:
                    old_angle = sum_angle / count_angle
                angle_diff = abs(angle - old_angle)
                sum_angle += angle
                count_angle += 1

                if times[i] > 700:
                    times[i] = times[i] * 1

                if (freq_prior < freq_cur > freq_next) or (freq_prior > freq_cur < freq_next) or (angle_diff > 20):
                # if (freq_prior < freq_cur > freq_next) or (freq_prior > freq_cur < freq_next) or (angle_diff > 6):
                    peaks.append((freq_cur, bw[i], times[i]))
                    sum_angle = 0
                    count_angle = 0

            # Добавляем последний элемент как пик
            peaks.append((round(freq[-1]), bw[-1], times[-1]))

            all_peaks.append(peaks)

        return all_peaks

    def calculate_peak_slopes(freq_files, bw_files, time_files):
        all_peak_frequencies = []
        all_peaks_diff = []
        all_slopes = []
        all_peak_bw = []
        all_bw_diff = []
        all_bw_slopes = []
        all_durations = []
        all_times = []

        # Для каждого файла
        for freq, bw, times in zip(freq_files, bw_files, time_files):
            if (len(freq) == 0) or (len(bw) == 0) or (len(times) == 0):
                continue

            # Находим пики
            peaks = find_frequency_peaks([freq], [bw], [times])[0]

            # Извлекаем частоты, ширину канала и времена пиков
            peak_frequencies = [peak[0] for peak in peaks]
            peak_bw = [peak[1] for peak in peaks]
            peak_times = [peak[2] for peak in peaks]

            # Рассчитываем углы наклона между пиками
            peaks_diff = []
            bw_diff = []
            bw_slopes = []
            slopes = []
            durations = []
            for i in range(1, len(peak_frequencies)):
                freq_diff = peak_frequencies[i] - peak_frequencies[i - 1]
                bw_difference = peak_bw[i] - peak_bw[i - 1]
                duraction = peak_times[i] - peak_times[i - 1]
                time_diff = duraction * 10

                if peak_times[i] > 700:
                    peak_times[i] = peak_times[i] * 1

                if time_diff != 0:
                    # slope = freq_diff / time_diff
                    angle = angle_bac(time_diff, freq_diff)
                    slopes.append(angle)

                    # slope = bw_difference / time_diff
                    angle = angle_bac(time_diff, bw_difference)
                    bw_slopes.append(angle)
                else:
                    slopes.append(0)
                    bw_slopes.append(0)

                peaks_diff.append(freq_diff)
                bw_diff.append(bw_difference)
                durations.append(duraction)

            # Добавляем результаты для текущего файла
            all_peak_frequencies.append(peak_frequencies)
            all_peak_bw.append(peak_bw)
            all_peaks_diff.append(peaks_diff)
            all_slopes.append(slopes)
            all_bw_diff.append(bw_diff)
            all_bw_slopes.append(bw_slopes)
            all_durations.append(durations)
            all_times.append(peak_times)

        return all_peak_frequencies, all_peaks_diff, all_slopes, all_peak_bw, all_bw_diff, all_bw_slopes, all_durations, all_times

    def filter_short_durations(
            peak_freqs, peak_diff, slopes, peak_bw, bw_diff, bw_slopes,
            durations, times, eps=10
    ):
        """
        Фильтрует пики, ширину канала и длительности, удаляя участки с длительностью меньше заданного порога.

        Параметры:
            peak_freqs (list): Список частот пиков для каждого файла.
            peak_diff (list): Список разниц частот между пиками для каждого файла.
            slopes (list): Список углов наклона частот между пиками для каждого файла.
            durations (list): Список длительностей между пиками для каждого файла.
            times (list): Список времен начала каждого пика для каждого файла.
            peak_bw (list): Список ширины канала пиков для каждого файла.
            bw_diff (list): Список разниц ширины канала между пиками для каждого файла.
            bw_slopes (list): Список углов наклона ширины канала между пиками для каждого файла.
            eps (float): Порог длительности. Участки с длительностью меньше этого значения объединяются с предыдущими.

        Возвращает:
            tuple:
                - new_peak_freqs: Список фильтрованных частот пиков.
                - new_peak_diff: Список фильтрованных разниц частот между пиками.
                - new_slopes: Список фильтрованных углов наклона частот.
                - new_durations: Список фильтрованных длительностей.
                - new_times: Список фильтрованных времен начала пиков.
                - new_peak_bw: Список фильтрованных ширин каналов.
                - new_bw_diff: Список фильтрованных разниц ширин каналов.
                - new_bw_slopes: Список фильтрованных углов наклона ширины каналов.
        """
        new_peak_freqs = []
        new_peak_diff = []
        new_slopes = []
        new_durations = []
        new_times = []
        new_peak_bw = []
        new_bw_diff = []
        new_bw_slopes = []

        for file_peaks, file_peak_diff, file_slopes, file_bw, file_bw_diff, file_bw_slopes, file_durations, file_times in zip(
                peak_freqs, peak_diff, slopes, peak_bw, bw_diff, bw_slopes, durations, times
        ):
            filtered_peak_freqs = []
            filtered_peak_diff = []
            filtered_slopes = []
            filtered_durations = []
            filtered_times = []
            filtered_peak_bw = []
            filtered_bw_diff = []
            filtered_bw_slopes = []

            for i in range(len(file_peaks)):
                # if i == 77:
                #     i += 0
                if i == 0:
                    # Добавляем первый пик
                    filtered_peak_freqs.append(file_peaks[i])
                    filtered_peak_bw.append(file_bw[i])
                    filtered_times.append(file_times[i])
                elif i - 1 < len(file_durations):  # Проверяем корректность индекса
                    if file_durations[i - 1] < eps:
                        if filtered_durations:
                            # Если длительность меньше порога, добавляем её к предыдущему участку
                            filtered_durations[-1] += file_durations[i - 1]
                    else:
                        # Добавляем текущий пик, его длительность, ширину канала и время
                        filtered_peak_freqs.append(file_peaks[i])
                        filtered_peak_bw.append(file_bw[i])
                        filtered_durations.append(file_durations[i - 1])
                        filtered_times.append(file_times[i])

            # Углы наклона и разницы ширины канала вычисляются только между оставшимися пиками
            for j in range(1, len(filtered_peak_freqs)):
                freq_diff = filtered_peak_freqs[j] - filtered_peak_freqs[j - 1]
                bw_difference = filtered_peak_bw[j] - filtered_peak_bw[j - 1]
                duration = filtered_durations[j - 1]

                # Для частот
                filtered_peak_diff.append(freq_diff if duration != 0 else 0)
                # filtered_slopes.append(freq_diff / duration if duration != 0 else 0)
                filtered_slopes.append(angle_bac(duration, freq_diff) if duration != 0 else 0)

                # Для ширины канала
                filtered_bw_diff.append(bw_difference)
                # filtered_bw_slopes.append(bw_difference / duration if duration != 0 else 0)
                filtered_bw_slopes.append(angle_bac(duration, bw_difference) if duration != 0 else 0)

            # Добавляем результаты для текущего файла
            new_peak_freqs.append(filtered_peak_freqs)
            new_peak_diff.append(filtered_peak_diff)
            new_slopes.append(filtered_slopes)
            new_peak_bw.append(filtered_peak_bw)
            new_bw_diff.append(filtered_bw_diff)
            new_bw_slopes.append(filtered_bw_slopes)
            new_durations.append(filtered_durations)
            new_times.append(filtered_times)

        return new_peak_freqs, new_peak_diff, new_slopes, new_peak_bw, new_bw_diff, new_bw_slopes, new_durations, new_times

    def find_common_intervals(segment_peak1, segment_gradients1, peak_bw1, segment_bw1, segment_durations1, segment_times1,
                              segment_peak2, segment_gradients2, peak_bw2, segment_bw2, segment_durations2, segment_times2,
                              eps=1e-6):
        """
        Находит общие интервалы, где градиенты обеих последовательностей находятся в пределах [-5, 5].

        Аргументы:
            segment_gradients1, segment_gradients2: Списки градиентов для F1 и F2.
            segment_durations1, segment_durations2: Списки длительностей для F1 и F2.
            segment_times1, segment_times2: Списки времени начала каждого элемента для F1 и F2.
            eps: Погрешность для синхронизации времени.

        Возвращает:
            Список общих интервалов в формате [(start_time, end_time), ...].
        """
        # Начальные значения
        te = 0
        index1, index2 = 0, 0  # Индексы для массивов F1 и F2
        is_interval = False  # Флаг для отслеживания активного интервала
        intervals = []  # Список интервалов (tb, te)
        freq_1 = 0
        freq_2 = 0

        while index1 < len(segment_gradients1) and index2 < len(segment_gradients2):
            if index1 == 13:
                index1 = index1 + 0
            # Рассчитываем начальное и конечное время текущего элемента
            time_start1 = segment_times1[index1]
            time_end1 = time_start1 + segment_durations1[index1]
            time_start2 = segment_times2[index2]
            time_end2 = time_start2 + segment_durations2[index2]

            # Текущие элементы для F1 и F2
            item1_grad = segment_gradients1[index1]
            item2_grad = segment_gradients2[index2]
            # item1_bw = segment_bw1[index1]
            # item2_bw = segment_bw2[index2]
            item1_bw = peak_bw1[index1]
            item2_bw = peak_bw2[index2]
            item1_bw = hz_to_mel(item1_bw)
            item2_bw = hz_to_mel(item2_bw)

            freq_cur1 = segment_peak1[index1]
            if index1 == len(segment_gradients1):
                freq_next1 = freq_cur1 + math.cos(item1_grad) * segment_durations1[index1]
            else:
                freq_next1 = segment_peak1[index1+1]
            freq_cur1 = hz_to_mel(freq_cur1)
            freq_next1 = hz_to_mel(freq_next1)
            level_cur1 = int(freq_cur1 / 25)
            level_next1 = int(freq_next1 / 25)
            if index1 == 0:
                freq_1 = freq_cur1
            level_diff1 = abs(freq_1 - freq_cur1)

            freq_cur2 = segment_peak2[index2]
            if index2 == len(segment_gradients2):
                freq_next2 = freq_cur2 + math.cos(item2_grad) * segment_durations1[index2]
            else:
                freq_next2 = segment_peak2[index2+1]
            freq_cur2 = hz_to_mel(freq_cur2) / 4.3
            freq_next2 = hz_to_mel(freq_next2) / 4.3
            level_cur2 = int(freq_cur2 / 25)
            level_next2 = int(freq_next2 / 25)
            if index2 == 0:
                freq_2 = freq_cur2
            level_diff2 = abs(freq_2 - freq_cur2)

            # Общее начальное и конечное время пересечения
            tb = max(time_start1, time_start2)  # начало интервала пересечения
            te = min(time_end1, time_end2)  # конец интервала пересечения

            # Если оба градиента в пределах [-5; 5] и есть пересечение
            # if (abs(item1_grad) <= 0.6 and abs(item2_grad) <= 0.6 and
            #         abs(item1_bw) <= 2 and abs(item2_bw) <= 2 and tb < te):
            if (level_diff1 <= 10 and level_diff2 <= 10 and tb < te) and (item1_bw < 50) and (item2_bw < 50):
                if not is_interval:
                    # Начало нового интервала
                    is_interval = True
                    interval_start = tb  # запоминаем начало нового интервала
                    freq_1 = freq_cur1
                    freq_2 = freq_cur2
            else:
                if is_interval:
                    # Конец текущего интервала
                    is_interval = False
                    if abs(interval_start - tb) > 0:
                        intervals.append((interval_start, tb))  # добавляем интервал в список
                freq_1 = freq_cur1
                freq_2 = freq_cur2

            # Рассчитываем новое время t1 и t2
            nt1 = time_end1
            nt2 = time_end2

            # Обновляем индексы и времена
            if abs(nt1 - nt2) < eps:
                index1 += 1
                index2 += 1
            elif nt1 < nt2:
                index1 += 1
            else:
                index2 += 1

        # Завершаем последний интервал, если он активен
        if is_interval:
            intervals.append((interval_start, te))

        return intervals

    def merge_close_intervals(intervals, eps=1e-6):
        """
        Объединяет соседние интервалы, если разница между их границами меньше заданного порога.

        Параметры:
            intervals (list): Список интервалов в формате [(start_time, end_time), ...].
            eps (float): Пороговое значение разницы между границами интервалов для их объединения.

        Возвращает:
            list: Список объединенных интервалов.
        """
        if not intervals:
            return []

        # Отсортировать интервалы по началу
        intervals.sort(key=lambda x: x[0])

        merged_intervals = [intervals[0]]  # Инициализируем результат первым интервалом

        for current_start, current_end in intervals[1:]:
            last_start, last_end = merged_intervals[-1]

            # Проверяем разницу между концом предыдущего и началом текущего интервала
            if abs(current_start - last_end) < eps:
                # Объединяем интервалы
                merged_intervals[-1] = (last_start, max(last_end, current_end))
            else:
                # Добавляем новый интервал
                merged_intervals.append((current_start, current_end))

        return merged_intervals

    # window_size = 10  # 20 мс мин для тона
    window_size = 5  # 20 мс мин для тона
    freq1, bw1, times1, freq2, bw2, times2 = extract_speech(input_audio_file)

    converted_file_freqs = []
    converted_file_bw = []
    converted_file_times = []
    converted_segment_times = np.array(times1) * 1000
    converted_file_times.append(converted_segment_times.tolist())
    converted_file_freqs.append(freq1)
    converted_file_bw.append(bw1)

    times = converted_file_times
    freq = converted_file_freqs
    bw = converted_file_bw

    peak_freq, peak_diff, peak_slopes, peak_bw, bw_diff, bw_slopes, peak_durations, peak_times = calculate_peak_slopes(
        freq, bw, times)
    new_peak_freq = peak_freq
    new_peak_times = peak_times

    peak_freq, peak_diff, peak_slopes, peak_bw, bw_diff, bw_slopes, peak_durations, peak_times = filter_short_durations(
        peak_freq,
        peak_diff,
        peak_slopes,
        peak_bw,
        bw_diff,
        bw_slopes,
        peak_durations,
        peak_times,
        eps=window_size)

    # import matplotlib.pyplot as plt
    # # Построение графика
    # plt.plot(times[0], freq[0], label='Форманта 1 (Гц)')
    # plt.plot(new_peak_times[0], new_peak_freq[0], label='Определение пиков')
    # plt.plot(peak_times[0], peak_freq[0], label='Сглаживание')
    # # Настройка осей и заголовка
    # plt.xlabel('Время (Times)')
    # plt.ylabel('Частота (Freq)')
    # plt.title('Три прямые на одном графике')
    # plt.legend()
    # # Показ графика
    # plt.show()

    if not peak_slopes:
        return []

    segment_peak1 = np.concatenate(peak_freq)
    segment_gradients1 = np.concatenate(peak_slopes)
    segment_peak_bw1 = np.concatenate(peak_bw)
    segment_bw1 = np.concatenate(bw_slopes)
    segment_durations1 = np.concatenate(peak_durations)
    segment_times1 = np.concatenate(peak_times)

    converted_file_freqs = []
    converted_file_bw = []
    converted_file_times = []
    converted_segment_times = np.array(times2) * 1000
    converted_file_times.append(converted_segment_times.tolist())
    converted_file_freqs.append(freq2)
    converted_file_bw.append(bw2)

    times = converted_file_times
    freq = converted_file_freqs
    bw = converted_file_bw

    peak_freq, peak_diff, peak_slopes, peak_bw, bw_diff, bw_slopes, peak_durations, peak_times = calculate_peak_slopes(
        freq, bw, times)
    # new_peak_freq = peak_freq
    # new_peak_times = peak_times
    peak_freq, peak_diff, peak_slopes, peak_bw, bw_diff, bw_slopes, peak_durations, peak_times = filter_short_durations(
        peak_freq,
        peak_diff,
        peak_slopes,
        peak_bw,
        bw_diff,
        bw_slopes,
        peak_durations,
        peak_times,
        eps=window_size)

    # import matplotlib.pyplot as plt
    # # Построение графика
    # plt.plot(times[0], freq[0], label='Форманта 1 (Гц)')
    # plt.plot(new_peak_times[0], new_peak_freq[0], label='Определение пиков')
    # plt.plot(peak_times[0], peak_freq[0], label='Сглаживание')
    # # Настройка осей и заголовка
    # plt.xlabel('Время (Times)')
    # plt.ylabel('Частота (Freq)')
    # plt.title('Три прямые на одном графике')
    # plt.legend()
    # # Показ графика
    # plt.show()

    if not peak_slopes:
        return []

    segment_peak2 = np.concatenate(peak_freq)
    segment_gradients2 = np.concatenate(peak_slopes)
    segment_peak_bw2 = np.concatenate(peak_bw)
    segment_bw2 = np.concatenate(bw_slopes)
    segment_durations2 = np.concatenate(peak_durations)
    segment_times2 = np.concatenate(peak_times)

    common_intervals = find_common_intervals(segment_peak1, segment_gradients1, segment_peak_bw1, segment_bw1, segment_durations1, segment_times1,
                                             segment_peak2, segment_gradients2, segment_peak_bw2, segment_bw2, segment_durations2, segment_times2)
    common_intervals = merge_close_intervals(common_intervals, eps=30)

    return common_intervals
