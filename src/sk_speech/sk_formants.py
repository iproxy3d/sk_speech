import subprocess
import numpy as np
import librosa
import scipy.signal
from scipy.signal import resample
from scipy.signal import medfilt
from scipy.stats import linregress
from scipy.ndimage import uniform_filter1d
from scipy import stats
import parselmouth as pm
from parselmouth.praat import call
from sklearn.linear_model import LinearRegression
import soundfile as sf
from . import sk_filters as fl
from . import sk_pitch as pt
import matplotlib.pyplot as plt

formant_ranges = {
    0: (50, 600),
    1: (200, 1400),
    # 1: (200, 1500),
    # 1: (5, 25000),
    2: (800, 2500),
    # 2: (800, 3000),
    # 2: (800, 50000),
    3: (1500, 3500),
    4: (2500, 4500),
    5: (3500, 5500),
    6: (5500, 6500),
    7: (6500, 7500),
    8: (7500, 8500),
    9: (8500, 9500),
    # 6: (4500, 6500),
    # 7: (5500, 7500),
    # 8: (6500, 8500),
    # 9: (7500, 9500),
}

def formant_range(formant_index):
    return formant_ranges[formant_index][1] - formant_ranges[formant_index][0]

def get_formants_with_retries(sound, time_step=0.01, max_number_of_formants=5, pitch_to=5500):
    while time_step <= 1:
        try:
            formants = sound.to_formant_burg(time_step=time_step,
                                             max_number_of_formants=max_number_of_formants,
                                             maximum_formant=pitch_to)
            return formants  # Успешно получен pitch, возвращаем результат
        except pm.PraatError as e:
            # print(f"Ошибка: {e}. Увеличиваем time_step и повторяем попытку...")
            time_step *= 10  # Увеличиваем time_step в 10 раз

    # Если вышли из цикла и не смогли получить pitch
    # print("Не удалось получить pitch: достигнут максимальный time_step > 1.")
    return None

def analyze_formants_alternative(signal, sr, speech=True, time_step=0.01, method="praat"):
    """
    Альтернативное извлечение формант для проверки влияния метода.
    """
    if method == "praat":
        # Извлечение частот и ширины полос через Praat
        frequencies, times, bandwidths, intensities = formant_frequencies(signal, sr, speech=speech, time_step=time_step)
    elif method == "lpc":
        # Пример извлечения через LPC (SciPy)
        frequencies, times = extract_formants_via_lpc(signal, sr, frame_length=0.03, hop_length=time_step, lpc_order=8)
        bandwidths = np.full_like(times, np.nan)  # Без ширины канала
        intensities = np.full_like(times, np.nan)  # Без интенсивности
    else:
        raise ValueError("Метод не распознан: используйте 'praat' или 'lpc'.")
    return frequencies, times, bandwidths, intensities

def extract_formants_via_lpc(signal, sr, frame_length=0.03, hop_length=0.01, lpc_order=12):
    """
    Извлечение динамических значений формант через LPC для всего аудиосигнала.

    Args:
        signal (numpy.ndarray): Аудиосигнал.
        sr (int): Частота дискретизации.
        frame_length (float): Длина кадра в секундах.
        hop_length (float): Шаг между кадрами в секундах.
        lpc_order (int): Порядок LPC.

    Returns:
        list: Списки формант по времени (для F1, F2, F3...).
        list: Временные метки для каждого кадра.
    """
    # Преобразуем frame и hop в количество сэмплов
    frame_samples = int(frame_length * sr)
    hop_samples = int(hop_length * sr)

    # Окончание сигнала для кадрирования
    window = np.hanning(frame_samples)  # Ханнинг окно для сглаживания
    frames = librosa.util.frame(signal, frame_length=frame_samples, hop_length=hop_samples).T
    times = np.arange(len(frames)) * hop_length  # Временные метки

    # Результаты анализа формант
    formants_over_time = [[] for _ in range(5)]  # Максимум 5 формант

    for frame in frames:
        frame = frame * window  # Применяем окно к кадру
        frame = frame - np.mean(frame)  # Убираем DC-смещение

        # LPC анализ
        a = librosa.lpc(frame, order=lpc_order)
        roots = np.roots(a)
        roots = [r for r in roots if np.imag(r) >= 0]  # Положительные частоты
        angles = np.angle(roots)
        frequencies = np.abs(angles * (sr / (2 * np.pi)))  # Преобразование в Гц

        # Сортировка частот и отбор 5 наименьших (форманты)
        formants = sorted(frequencies)[:5]
        for i, freq in enumerate(formants):
            formants_over_time[i].append(freq)

        # Заполняем NaN для отсутствующих формант
        for i in range(len(formants), 5):
            formants_over_time[i].append(np.nan)

    return formants_over_time, times


def formant_frequencies(signal, sr, speech=True, time_step=0.01):
    sound = pm.Sound(signal, sampling_frequency=sr)
    formants = get_formants_with_retries(sound, time_step=time_step)
    if formants is None:
        return None, None, None, None

    frequencies = [[] for _ in range(5)]
    bandwidths = [[] for _ in range(5)]
    intensities = []
    times = formants.ts()

    min_duration = 0.064  # Минимальная продолжительность для анализа интенсивности
    sound_duration = sound.get_total_duration()

    if sound_duration >= min_duration:
        intensity = sound.to_intensity()
        intensity_threshold = 50 if speech else 0  # Порог интенсивности

        for t in times:
            intensity_value = intensity.get_value(t)
            if intensity_value > intensity_threshold:
                intensities.append(intensity_value)
                for i in range(1, 6):
                    freq = formants.get_value_at_time(i, t)
                    bandwidth = formants.get_bandwidth_at_time(i, t)

                    # Если частота в пределах допустимых значений для форманты
                    if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1]:
                        frequencies[i-1].append(freq)
                        bandwidths[i-1].append(bandwidth)
                    else:
                        frequencies[i-1].append(np.nan)
                        bandwidths[i-1].append(np.nan)
            else:
                intensities.append(np.nan)
                for i in range(1, 6):
                    frequencies[i-1].append(np.nan)
                    bandwidths[i-1].append(np.nan)
    else:
        intensities = [np.nan] * len(times)
        for t in times:
            for i in range(1, 6):
                freq = formants.get_value_at_time(i, t)
                bandwidth = formants.get_bandwidth_at_time(i, t)
                frequencies[i-1].append(freq)
                bandwidths[i-1].append(bandwidth)

    # Приведение длин всех массивов к одной длине, заполняем NaN при необходимости
    max_length = max(len(f) for f in frequencies)
    for i in range(5):
        while len(frequencies[i]) < max_length:
            frequencies[i].append(np.nan)
            bandwidths[i].append(np.nan)

    while len(intensities) < max_length:
        intensities.append(np.nan)

    return frequencies, times, bandwidths, intensities

def formant_frequencies2(signal, sr, speech=True, time_step=0.01):
    sound = pm.Sound(signal, sampling_frequency=sr)
    formants = get_formants_with_retries(sound, time_step=time_step)
    if formants is None:
        return None, None, None, None

    frequencies = [[] for _ in range(5)]
    bandwidths = [[] for _ in range(5)]
    intensities = []
    times = formants.ts()

    min_duration = 0.064  # Minimum duration required for intensity analysis
    sound_duration = sound.get_total_duration()

    oldvalue = [0, 0, 0, 0, 0]
    if sound_duration >= min_duration:
        intensity = sound.to_intensity()
        if speech:
            # Define the intensity threshold for detecting speech
            intensity_threshold = 50

            for t in times:
                intensity_value = intensity.get_value(t)
                if intensity_value > intensity_threshold:
                    intensities.append(intensity_value)
                    for i in range(1, 6):
                        freq = formants.get_value_at_time(i, t)
                        bandwidth = formants.get_bandwidth_at_time(i, t)
                        # if (not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1] and
                        #         (oldvalue[i-1] == 0 or (oldvalue[i-1] != 0 and abs(oldvalue[i-1] - freq) < 100))):
                        if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1]:
                            frequencies[i - 1].append(freq)
                            bandwidths[i - 1].append(bandwidth)
                            oldvalue[i - 1] = freq
                        else:
                            frequencies[i - 1].append(np.nan)
                            bandwidths[i - 1].append(np.nan)
                else:
                    intensities.append(np.nan)
                    for i in range(1, 6):
                        frequencies[i - 1].append(np.nan)
                        bandwidths[i - 1].append(np.nan)
        else:
            for t in times:
                intensity_value = intensity.get_value(t)
                intensities.append(intensity_value)
                for i in range(1, 6):
                    freq = formants.get_value_at_time(i, t)
                    bandwidth = formants.get_bandwidth_at_time(i, t)
                    # if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1] and (oldvalue[i-1] == 0 or (oldvalue[i-1] != 0 and abs(oldvalue[i-1] - freq) < 100)):
                    if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1]:
                        frequencies[i - 1].append(freq)
                        bandwidths[i - 1].append(bandwidth)
                    else:
                        frequencies[i - 1].append(np.nan)
                        bandwidths[i - 1].append(np.nan)
    else:
        intensities = [np.nan] * len(times)
        for t in times:
            for i in range(1, 6):
                freq = formants.get_value_at_time(i, t)
                bandwidth = formants.get_bandwidth_at_time(i, t)
                frequencies[i - 1].append(freq)
                bandwidths[i - 1].append(bandwidth)

    # Ensure all lists have the same length by padding with NaNs
    max_length = max(len(f) for f in frequencies)
    for i in range(5):
        while len(frequencies[i]) < max_length:
            frequencies[i].append(np.nan)
            bandwidths[i].append(np.nan)

    while len(intensities) < max_length:
        intensities.append(np.nan)

    return frequencies, times, bandwidths, intensities

def get_formant_info(signal, sr):
    frequencies, voiced_time, bandwidths, intensities = formant_frequencies(signal, sr, speech=True)
    return {"frequencies": frequencies, "voiced_times": voiced_time,
            "bandwidths": bandwidths, "intensities": intensities}

def formant_frequencies_expended(signal, sr, speech=True, time_step=0.01, max_number_of_formants=5):
    sound = pm.Sound(signal, sampling_frequency=sr)
    formants = get_formants_with_retries(sound, time_step=time_step, max_number_of_formants=max_number_of_formants, pitch_to=(max_number_of_formants*1000+500))
    if formants is None:
        return None, None, None, None

    frequencies = [[] for _ in range(max_number_of_formants)]
    bandwidths = [[] for _ in range(max_number_of_formants)]
    intensities = []
    times = formants.ts()

    min_duration = 0.064  # Minimum duration required for intensity analysis
    sound_duration = sound.get_total_duration()

    oldvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if sound_duration >= min_duration:
        intensity = sound.to_intensity()
        if speech:
            # Define the intensity threshold for detecting speech
            intensity_threshold = 50

            for t in times:
                intensity_value = intensity.get_value(t)
                if intensity_value > intensity_threshold:
                    intensities.append(intensity_value)
                    for i in range(1, max_number_of_formants+1):
                        freq = formants.get_value_at_time(i, t)
                        bandwidth = formants.get_bandwidth_at_time(i, t)
                        # if (not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1] and
                        #         (oldvalue[i-1] == 0 or (oldvalue[i-1] != 0 and abs(oldvalue[i-1] - freq) < 100))):
                        if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1]:
                            frequencies[i - 1].append(freq)
                            bandwidths[i - 1].append(bandwidth)
                            oldvalue[i - 1] = freq
                        else:
                            frequencies[i - 1].append(np.nan)
                            bandwidths[i - 1].append(np.nan)
                else:
                    intensities.append(np.nan)
                    for i in range(1, max_number_of_formants+1):
                        frequencies[i - 1].append(np.nan)
                        bandwidths[i - 1].append(np.nan)
        else:
            for t in times:
                intensity_value = intensity.get_value(t)
                intensities.append(intensity_value)
                for i in range(1, max_number_of_formants+1):
                    freq = formants.get_value_at_time(i, t)
                    bandwidth = formants.get_bandwidth_at_time(i, t)
                    # if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1] and (oldvalue[i-1] == 0 or (oldvalue[i-1] != 0 and abs(oldvalue[i-1] - freq) < 100)):
                    if not np.isnan(freq) and formant_ranges[i][0] <= freq <= formant_ranges[i][1]:
                        frequencies[i - 1].append(freq)
                        bandwidths[i - 1].append(bandwidth)
                    else:
                        frequencies[i - 1].append(np.nan)
                        bandwidths[i - 1].append(np.nan)
    else:
        intensities = [np.nan] * len(times)
        for t in times:
            for i in range(1, max_number_of_formants+1):
                freq = formants.get_value_at_time(i, t)
                bandwidth = formants.get_bandwidth_at_time(i, t)
                frequencies[i - 1].append(freq)
                bandwidths[i - 1].append(bandwidth)

    # Ensure all lists have the same length by padding with NaNs
    max_length = max(len(f) for f in frequencies)
    for i in range(max_number_of_formants):
        while len(frequencies[i]) < max_length:
            frequencies[i].append(np.nan)
            bandwidths[i].append(np.nan)

    while len(intensities) < max_length:
        intensities.append(np.nan)

    return frequencies, times, bandwidths, intensities

def extract_formants(signal, sr, speech=True, formants=None):
    if formants:
        frequencies = formants["frequencies"]
    else:
        frequencies, _, _, _ = formant_frequencies(signal, sr, speech)
    freqs = []
    for i in range(5):
        if all(np.isnan(freq) for freq in frequencies[i]):
            freqs.append(np.nan)
        else:
            freqs.append(np.nanmean(frequencies[i]))

    return freqs

def extract_formants_from_segment(signal_segment, sr, speech=True):
    """
    Извлекает частоты формант из сегмента сигнала.

    :param signal_segment: Сегмент аудиосигнала.
    :param sr: Частота дискретизации.
    :return: Массив частот формант.
    """
    # Пре-эмфазис для усиления высоких частот
    pre_emphasis = 0.97
    emphasized_signal = np.append(signal_segment[0], signal_segment[1:] - pre_emphasis * signal_segment[:-1])

    frequencies = extract_formants(emphasized_signal, sr, speech)
    return frequencies

def extract_formants_and_f0(signal, sr):
    """
    Извлекает форманты и основной тон (F0) из аудиосигнала с помощью Parselmouth.

    :param signal: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :return: Список частот формант и значение F0.
    """
    sound = pm.Sound(signal, sr)
    formant = sound.to_formant_burg(time_step=0.01)
    pitch = sound.to_pitch(time_step=0.01)

    formants = []
    for i in range(1, 6):  # Форманты с 1 по 5
        formant_freq = formant.get_value_at_time(i, 0.5)
        if np.any(~np.isnan(formant_freq)):
            formants.append(formant_freq)
        else:
            formants.append(0)

    # Извлечение F0
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values > 0]  # Исключаем нулевые значения

    return formants, pitch_values

def get_formant_frequency_by_index(signal, sr, formant_index, formants=None):
    # Проверка допустимости индекса форманты
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    # Выделяем форманты
    formants = extract_formants(signal, sr, formants=formants)

    # Получаем частоту для указанной форманты
    formant_frequency = formants[formant_index - 1]

    return formant_frequency

def remove_outliers(data, m=1.5):
    data = np.array(data)
    if len(data) == 0 or np.all(np.isnan(data)):
        return data
    lower_quartile = np.nanpercentile(data, 25)
    upper_quartile = np.nanpercentile(data, 75)
    iqr_value = upper_quartile - lower_quartile
    lower_bound = lower_quartile - (m * iqr_value)
    upper_bound = upper_quartile + (m * iqr_value)
    return data[(data >= lower_bound) & (data <= upper_bound)]

def calculate_formant_bandwidth_(bandwidths, formant_index, method='max'):
    # Проверка допустимости индекса форманты
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    if len(bandwidths[formant_index-1]) == 0 or np.all(np.isnan(bandwidths[formant_index-1])):
        return 0

    # Удаляем выбросы из значений ширины полосы
    cleaned_bandwidths = remove_outliers(bandwidths[formant_index-1])

    # Применяем полосовой фильтр для указанной форманты
    if len(cleaned_bandwidths) == 0 or np.all(np.isnan(cleaned_bandwidths)):
        return 0
    elif method == 'max':
        formant_bandwidth = np.nanmax(cleaned_bandwidths)
    else:
        formant_bandwidth = np.nanmean(cleaned_bandwidths)

    return formant_bandwidth

def calculate_formant_bandwidth(signal, sr, formant_index, speech=True, method='max', formants = None):
    # Проверка допустимости индекса форманты
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    # Рассчитаем форманты и их ширину полосы пропускания
    if formants:
        bandwidths = formants["bandwidths"]
    else:
        _, _, bandwidths, _ = formant_frequencies(signal, sr, speech)

    formant_bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index, method=method)

    return formant_bandwidth

def calculate_formant_energy(signal, sr, formant_index, formants = None):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Formant index must be between 1 and 5")

    if formants:
        frequencies = formants["frequencies"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, _, bandwidths, _ = formant_frequencies(signal, sr)

    index = formant_index - 1
    formant_frequency = np.nanmean(frequencies[index])
    bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
    if bandwidth == 0:
        return 0
    b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1), min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    frame_length = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=filtered_signal, frame_length=frame_length, hop_length=hop_length)
    amplitude = rms ** 0.5
    energy = amplitude ** 2 * bandwidth

    return np.sum(energy)

def calculate_formant_energy2(signal, sr, formants = None):
    formant_energies = []

    # Выделяем форманты
    if formants:
        frequencies = formants["frequencies"]
    else:
        frequencies = extract_formants(signal, sr)

    # Применяем полосовые фильтры для каждой форманты
    for formant_index, formant in enumerate(frequencies, start=1):
        bandwidth = calculate_formant_bandwidth(signal, sr, formant_index, formants=formants) / 2
        if bandwidth > 0 and formant > 0 and formant + bandwidth < sr / 2:
            b, a = scipy.signal.butter(2, [max(formant - bandwidth, 1), min(formant + bandwidth, sr/2 -1)], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)
            energy = np.sum(filtered_signal ** 2)  # Энергия форманты
            formant_energies.append(energy)
        else:
            formant_energies.append(0)  # Если форманта вне допустимого диапазона, энергия равна 0

    return formant_energies

def calculate_formant_energy_arr(signal, sr, formant_index, formants=None):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    index = formant_index - 1
    if len(frequencies[index]) == 0 or np.all(np.isnan(frequencies[index])):
        return []

    # Создание полосового фильтра для форманты
    formant_frequency = np.nanmean(frequencies[index])
    if np.isnan(formant_frequency) or formant_frequency <= 0:
        return []

    bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
    b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1),
                                   min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Рассчитываем амплитуду отфильтрованного сигнала
    frame_length = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=filtered_signal, frame_length=frame_length, hop_length=hop_length)
    amplitude = rms[0] ** 0.5

    # Перевод времени в индексы амплитуды
    frame_times = np.arange(len(amplitude)) * (hop_length / sr)
    energy = []

    for t, bw in zip(times, bandwidths[index]):
        if not np.isnan(bw):
            closest_frame_idx = np.argmin(np.abs(frame_times - t))
            energy.append(((amplitude[closest_frame_idx] ** 2) * bw, t))

    return energy

def calculate_formant_energy3(signal, sr, formant_index, formants = None):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    index = formant_index - 1
    if len(frequencies[index]) == 0 or np.all(np.isnan(frequencies[index])):
        return 0

    # Создание полосового фильтра для форманты
    formant_frequency = np.nanmean(frequencies[index])
    if np.isnan(formant_frequency) or formant_frequency <= 0:
        return 0

    bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
    b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1),
                                   min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Рассчитываем амплитуду отфильтрованного сигнала
    frame_length = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=filtered_signal, frame_length=frame_length, hop_length=hop_length)
    amplitude = rms[0] ** 0.5

    # Перевод времени в индексы амплитуды
    frame_times = np.arange(len(amplitude)) * (hop_length / sr)
    energy = []

    for t, bw in zip(times, bandwidths[index]):
        if not np.isnan(bw):
            closest_frame_idx = np.argmin(np.abs(frame_times - t))
            energy.append((amplitude[closest_frame_idx] ** 2) * bw)

    return np.nanmean(energy)


def calculate_formant_and_f0_energy(signal, sr):
    """
    Рассчитывает энергию формант и F0 в аудиосигнале, используя Parselmouth для извлечения формантов и F0.

    :param signal: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :return: Список энергий формант и средняя энергия F0.
    """
    formant_energies = []
    f0_energy = []

    # Извлечение формантов и F0 с использованием Parselmouth
    formants, pitch_values = extract_formants_and_f0(signal, sr)

    # Применяем полосовые фильтры для каждой форманты
    for formant_index, formant in enumerate(formants, start=1):
        bandwidth = calculate_formant_bandwidth(signal, sr, formant_index) / 2
        if bandwidth > 0 and formant > 0 and formant + bandwidth < sr / 2:
            b, a = scipy.signal.butter(2, [max(formant - bandwidth, 1), min(formant + bandwidth, sr/2 -1)], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)
            energy = np.sum(filtered_signal ** 2)  # Энергия форманты
            formant_energies.append(energy)
        else:
            formant_energies.append(0)  # Если форманта вне допустимого диапазона, энергия равна 0

    # Применяем полосовой фильтр для каждой частоты основного тона (F0)
    bandwidth = pt.calculate_pitch_bandwidth(signal, sr) / 2
    for f0 in pitch_values:
        if bandwidth > 0 and f0 > 0 and f0 + bandwidth < sr / 2:
            b, a = scipy.signal.butter(2, [max(f0 - bandwidth, 1), min(f0 + bandwidth, sr/2 -1)], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)
            energy = np.sum(filtered_signal ** 2)  # Энергия основного тона
            f0_energy.append(energy)

    # Средняя энергия основного тона
    avg_f0_energy = np.mean(f0_energy) if f0_energy else 0

    return formant_energies, avg_f0_energy

def change_formant_energy(y, sr, formant_index, factor):
    bandwidth = calculate_formant_bandwidth(y, sr, formant_index) / 2
    if bandwidth == 0:
        return y

    sound = pm.Sound(y, sr)
    signal = sound.values[0]

    intensity = sound.to_intensity()
    intensity_values = intensity.values.flatten()

    intensity_threshold = 50
    voiced_frames = intensity_values > intensity_threshold

    time_step = intensity.time_step
    voiced_times = [i * time_step for i, voiced in enumerate(voiced_frames) if voiced]

    if not voiced_times:
        raise ValueError("Не удалось найти озвученные фрагменты в аудиофайле.")

    formant = sound.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=5500)
    formant_frequencies = []
    low, high = formant_ranges[formant_index]
    oldvalue = 0
    for time in voiced_times:
        frequency = formant.get_value_at_time(formant_index, time)
        if not np.isnan(frequency) and low <= frequency <= high and (oldvalue == 0 or (oldvalue != 0 and abs(oldvalue - frequency) < 100)):
            formant_frequencies.append(frequency)
            oldvalue = frequency

    if not formant_frequencies:
        raise ValueError(f"Не удалось найти действительные частоты для форманты с индексом {formant_index}.")

    formant_freq = np.mean(formant_frequencies)

    lowcut = formant_freq - bandwidth
    highcut = formant_freq + bandwidth

    if lowcut < 0:
        lowcut = 0
    if highcut > sr / 2:
        highcut = sr / 2

    b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Вычитание исходного сигнала форманты
    combined_signal = signal - filtered_signal

    # Усиление энергии форманты
    amplified_signal = filtered_signal * factor

    # Объединение усиленного сигнала с оригинальным сигналом
    combined_signal += amplified_signal

    return combined_signal

def change_formant_energy2(signal, sr, energy_factors):
    """
    Изменяет энергию каждой форманты F1-F5 в аудиосигнале.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param energy_factors: Список факторов энергии для каждой форманты [E1, E2, E3, E4, E5].
    :return: Изменённый аудиосигнал.
    """
    # Получение частот формант, временных шагов, ширины полос и интенсивности
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Создаем массив для хранения измененного сигнала
    modified_signal = np.copy(signal)

    for t_idx, t in enumerate(times):
        for i in range(5):  # F1-F5
            if energy_factors[i] == 0:
                continue
            freq = frequencies[i][t_idx]
            bandwidth = bandwidths[i][t_idx] / 2
            
            if not np.isnan(freq) and freq > 0:
                # Применяем полосовой фильтр для текущей форманты
                b, a = scipy.signal.butter(2, [max(freq - bandwidth, 1), min(freq + bandwidth, sr/2 -1)], btype='band', fs=sr)
                filtered_signal = scipy.signal.lfilter(b, a, signal)

                # Изменяем энергию отфильтрованного сигнала
                filtered_signal *= energy_factors[i]

                # Синтезируем модифицированный сигнал
                segment_start = int(t * sr) - len(filtered_signal) // 2
                segment_end = segment_start + len(filtered_signal)

                if segment_start < 0:
                    segment_start = 0
                    segment_end = len(filtered_signal)
                if segment_end > len(signal):
                    segment_end = len(signal)
                    segment_start = segment_end - len(filtered_signal)

                modified_signal[segment_start:segment_end] += filtered_signal[:segment_end - segment_start]

    # Нормализация, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal

def change_formant_energy3(signal, sr, energy_factors):
    """
    Изменяет энергию каждой форманты F1-F5.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param energy_factors: Список факторов энергии для каждой форманты [E1, E2, E3, E4, E5].
    """
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        formant_index = i + 1
        formant_frequency = np.nanmean(frequencies[i])
        if np.isnan(formant_frequency) or formant_frequency <= 0:
            continue

        bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
        b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1), min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
        filtered_signal = scipy.signal.lfilter(b, a, signal)

        # Рассчитываем амплитуду отфильтрованного сигнала
        frame_length = 2048
        hop_length = 512
        rms = librosa.feature.rms(y=filtered_signal, frame_length=frame_length, hop_length=hop_length)
        amplitude = rms ** 0.5

        # Рассчитать энергию как произведение амплитуды в квадрате и ширины полосы
        frame_times = np.arange(len(amplitude[0])) * hop_length / sr
        energy = []
        for t, bw in zip(times, bandwidths[i]):
            if not np.isnan(bw):
                closest_frame_idx = np.argmin(np.abs(frame_times - t))
                energy.append((amplitude[closest_frame_idx] ** 2) * bw * energy_factors[i])

        # Вычитаем исходный фильтрованный сигнал
        modified_signal -= filtered_signal

        # Усиление энергии форманты
        modified_signal += filtered_signal * np.mean(energy) / np.mean(amplitude ** 2)

    # Нормализация, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal

def change_formant_amplitude(signal, sr, factors, formants=None):
    if formants:
        frequencies = formants["frequencies"]
    else:
        frequencies, _, _, _ = formant_frequencies(signal, sr)
    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        if factors[i] != 0 and not np.all(np.isnan(frequencies[i])):
            lowcut = np.nanmin(frequencies[i])
            highcut = np.nanmax(frequencies[i])

            if lowcut >= highcut:
                continue
            if lowcut == highcut:
                lowcut -= 10
                highcut += 10
            if highcut > sr / 2:
                highcut = sr / 2

            b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Сначала убираем старую форманту
            modified_signal -= filtered_signal

            # Затем усиливаем сигнал форманты и добавляем его обратно
            amplified_signal = filtered_signal * factors[i]
            modified_signal += amplified_signal

    modified_signal = np.clip(modified_signal, -1, 1)
    return modified_signal


def change_formant_amplitude_range(signal, sr, factors_from, factors_to, formants=None):
    if formants:
        frequencies = formants["frequencies"]
    else:
        frequencies, _, _, _ = formant_frequencies(signal, sr)

    modified_signal = np.copy(signal)

    # Длина сигнала
    num_samples = len(signal)

    for i in range(5):  # F1-F5
        if factors_from[i] != 0 or factors_to[i] != 0:  # Проверяем, есть ли изменения для данной форманты
            if not np.all(np.isnan(frequencies[i])):
                lowcut = np.nanmin(frequencies[i])
                highcut = np.nanmax(frequencies[i])

                if lowcut >= highcut:
                    continue
                if lowcut == highcut:
                    lowcut -= 10
                    highcut += 10
                if highcut > sr / 2:
                    highcut = sr / 2

                # Создание полосового фильтра для диапазона частот форманты
                b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)

                # Фильтрация сигнала для данной форманты
                filtered_signal = scipy.signal.lfilter(b, a, signal)

                # Создание линейной интерполяции для множителей от factors_from до factors_to
                interpolation_factors = np.linspace(factors_from[i], factors_to[i], num_samples)

                # Удаление старой форманты из исходного сигнала
                modified_signal -= filtered_signal

                # Усиление сигнала форманты с изменяющимся коэффициентом и добавление обратно
                modified_signal += filtered_signal * interpolation_factors

    # Приведение модифицированного сигнала к допустимому диапазону значений [-1, 1]
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal

def calculate_formant_intensity(signal, sr, formant_index, formants = None):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Formant index must be between 1 and 5")

    if formants:
        frequencies = formants["frequencies"]
        formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, _, bandwidths, _ = formant_frequencies(signal, sr)

    index = formant_index - 1
    if len(frequencies[index]) == 0 or np.all(np.isnan(frequencies[index])):
        return []

    # Создание полосового фильтра для форманты
    formant_frequency = np.nanmean(frequencies[index])
    if np.isnan(formant_frequency) or formant_frequency <= 0:
        return []

    formant_energies = []
    # Создание полосового фильтра для форманты
    bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
    b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1),
                                   min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Рассчитываем мощность отфильтрованного сигнала
    frame_length = 2048
    hop_length = 512
    filtered_power = np.abs(librosa.feature.rms(y=filtered_signal, frame_length=frame_length,
                                                hop_length=hop_length)) ** 2
    filtered_intensity_db = 10 * np.log10(filtered_power + np.finfo(float).eps)

    return filtered_intensity_db

def calculate_formant_intensity_avg(signal, sr, formant_index, formants=None):
    intensity = calculate_formant_intensity(signal, sr, formant_index, formants=formants)
    intensity_avg = np.mean(intensity) if len(intensity) > 0 else 0
    return abs(intensity_avg)

def calculate_formant_amplitude(signal, sr, formant_index, formants=None):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    if formants:
        frequencies = formants["frequencies"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, _, bandwidths, _ = formant_frequencies(signal, sr)

    index = formant_index - 1
    if len(frequencies[index]) == 0 or np.all(np.isnan(frequencies[index])):
        return 0

    # Создание полосового фильтра для форманты
    formant_frequency = np.nanmean(frequencies[index])
    if np.isnan(formant_frequency) or formant_frequency <= 0:
        return 0

    bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
    b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1),
                                   min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Рассчитываем амплитуду отфильтрованного сигнала
    frame_length = 2048
    hop_length = 512
    if len(filtered_signal) > 0 or np.isnan(filtered_signal):
        amplitude = np.abs(librosa.feature.rms(y=filtered_signal, frame_length=frame_length, hop_length=hop_length))
    else:
        amplitude = 0

    return amplitude

def calculate_formant_amplitude_avg(signal, sr, formant_index, formants=None):
    # Вычисляем амплитуду как среднее значение абсолютных значений отфильтрованного сигнала
    filtered_signal = calculate_formant_amplitude(signal, sr, formant_index, formants=formants)
    amplitude = np.mean(np.abs(filtered_signal))

    # Преобразование средней амплитуды в dB
    if amplitude > 0.00001:
        avg_amplitude_db = 20 * np.log10(amplitude)
    else:
        avg_amplitude_db =0.0

    return avg_amplitude_db

def calculate_formant_duration(signal, sr, formant_index, formants=None):
    # Проверка допустимости индекса форманты
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    # Извлечение формантов
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Получаем частоты и ширину полос для указанной форманты
    formant_freqs = frequencies[formant_index - 1]
    formant_bandwidths = bandwidths[formant_index - 1]
    
    # Проверка наличия данных
    if len(formant_freqs) == 0 or np.all(np.isnan(formant_freqs)):
        return 0

    # Создание маски для активных временных меток
    active_times = []
    for t_idx, t in enumerate(times):
        freq = formant_freqs[t_idx]
        bandwidth = formant_bandwidths[t_idx] / 2

        if not np.isnan(freq) and freq > 0:
            # Создание полосового фильтра для выделения указанной форманты
            b, a = scipy.signal.butter(2, [max(freq - bandwidth, 1), min(freq + bandwidth, sr/2 -1)],
                                       btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Определение порога для значительной активности форманты
            threshold = np.max(np.abs(filtered_signal)) * 0.1  # Порог в 10% от максимальной амплитуды фильтрованного сигнала
            if np.max(np.abs(filtered_signal)) > threshold:
                active_times.append(t)

    # Если нет активных временных меток, возвращаем 0
    if len(active_times) == 0:
        return 0

    # Длительность форманты (время от первого до последнего активного сегмента)
    duration = active_times[-1] - active_times[0]

    return duration

def calculate_formant_duration2(y, sr, formant_index, formants=None):
    # Проверка допустимости индекса форманты
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    # Извлечение формант
    if formants:
        frequencies = formants["frequencies"]
    else:
        formants = extract_formants(y, sr)
        # Получаем частоту для указанной форманты
        frequencies = formants[formant_index - 1]

    # Применяем полосовой фильтр для выделения указанной форманты
    bandwidth = calculate_formant_bandwidth(y, sr, formant_index, formants=formants) / 2

    if np.isnan(frequencies) or frequencies <= 0:
        return 0

    b, a = scipy.signal.butter(2, [max(frequencies - bandwidth, 1), min(frequencies + bandwidth, sr/2 -1)],
                               btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, y)

    # Определение порога для значительной активности форманты
    threshold = np.max(np.abs(filtered_signal)) * 0.1  # Порог в 10% от максимальной амплитуды
    active_frames = np.abs(filtered_signal) > threshold

    # Временные метки для активных кадров
    time = np.arange(len(y)) / sr
    active_time_segments = time[active_frames]

    if len(active_time_segments) == 0:
        return 0  # Если нет активных сегментов, возвращаем 0

    # Длительность форманты (время от первого до последнего активного сегмента)
    duration = active_time_segments[-1] - active_time_segments[0]

    return duration

def formant_at_index(y, sr, index, speech=True, window_size=1024):
    # Определение временного сегмента вокруг указанного индекса
    half_window = window_size // 2
    start_index = max(0, index - half_window)
    end_index = min(len(y), index + half_window)

    # Извлечение сегмента сигнала
    segment = y[start_index:end_index]

    # Извлечение формант из сегмента
    formants = extract_formants_from_segment(segment, sr, speech)

    return formants

def formant_trajectory(y, sr, index, window_size=1024):
    if index < 1 or index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    half_window = window_size // 2
    num_windows = (len(y) - window_size) // half_window
    formant_frequencies = []
    time_stamps = []

    for i in range(num_windows):
        start_index = i * half_window
        end_index = start_index + window_size
        segment = y[start_index:end_index]

        # Извлечение формант из сегмента
        formants = extract_formants_from_segment(segment, sr)

        # Проверка на наличие необходимой форманты
        if len(formants) >= index:
            formant_frequency = formants[index - 1]
            formant_frequencies.append(formant_frequency)
            time_stamps.append((start_index + end_index) / (2 * sr))  # Среднее время сегмента

    return time_stamps, formant_frequencies

def change_formants_shifts(signal, sr, formant_shifts):
    """
    Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.
    """
    # Загрузка аудиофайла
    snd = pm.Sound(signal, sr)

    # Получение объекта формант
    formant = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5)

    # Получение временных шагов
    time_steps = formant.ts()

    # Определение функции для получения новой частоты форманты
    def get_new_formant_freq(original_freq, formant_num):
        if original_freq <= 0:
            return original_freq
        return original_freq + formant_shifts[formant_num]

    # Создание нового объекта звука для изменённого звука
    modified_values = np.copy(snd.values)

    # Итерация по каждому временно́му шагу и изменение частот формант
    for t_idx, t in enumerate(time_steps):
        for i in range(1, 6):  # Форманты F1 до F5
            original_freq = formant.get_value_at_time(i, t)
            if original_freq > 0:  # Убедиться, что частота форманты действительна
                new_freq = get_new_formant_freq(original_freq, i - 1)

                # Расчёт коэффициента ресэмплинга
                resample_ratio = new_freq / original_freq

                # Регулировка значений звука вокруг частоты форманты
                segment_start = max(0, int(t * snd.sampling_frequency) - int(snd.sampling_frequency / 50))
                segment_end = min(len(snd.values[0]), int(t * snd.sampling_frequency) + int(snd.sampling_frequency / 50))

                segment = snd.values[:, segment_start:segment_end]

                # Ресэмплинг сегмента для изменения частоты форманты
                resampled_segment = resample(segment, int(len(segment[0]) * resample_ratio), axis=1)

                # Регулировка длины для соответствия оригинальному сегменту
                if len(resampled_segment[0]) > (segment_end - segment_start):
                    resampled_segment = resampled_segment[:, :segment_end - segment_start]
                elif len(resampled_segment[0]) < (segment_end - segment_start):
                    pad_width = (segment_end - segment_start) - len(resampled_segment[0])
                    resampled_segment = np.pad(resampled_segment, ((0, 0), (0, pad_width)), mode='constant')

                # Добавление ресэмплированного сегмента к изменённым значениям
                modified_values[:, segment_start:segment_end] = resampled_segment

    # Нормализация изменённых значений, чтобы предотвратить клиппинг
    modified_values = np.clip(modified_values, -1, 1)

    # Сохранение изменённого звука
    return modified_values[0], int(snd.sampling_frequency)

def change_formants_shifts2(signal, sr, formant_shifts):
    """
    Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.
    """
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Определение функции для получения новой частоты форманты
    def get_new_formant_freq(original_freq, formant_num):
        if original_freq <= 0:
            return original_freq
        return original_freq + formant_shifts[formant_num]

    # Создание нового объекта звука для изменённого звука
    modified_signal = np.copy(signal)

    # Итерация по каждому временно́му шагу и изменение частот формант
    for t_idx, t in enumerate(times):
        for i in range(5):  # Форманты F1 до F5
            original_freq = frequencies[i][t_idx]
            if original_freq > 0:  # Убедиться, что частота форманты действительна
                new_freq = get_new_formant_freq(original_freq, i)

                # Расчёт коэффициента ресэмплинга
                resample_ratio = new_freq / original_freq

                # Регулировка значений звука вокруг частоты форманты
                segment_start = max(0, int(t * sr) - int(sr / 50))
                segment_end = min(len(signal), int(t * sr) + int(sr / 50))

                segment = signal[segment_start:segment_end]

                # Ресэмплинг сегмента для изменения частоты форманты
                resampled_segment = resample(segment, int(len(segment) * resample_ratio))

                # Регулировка длины для соответствия оригинальному сегменту
                if len(resampled_segment) > (segment_end - segment_start):
                    resampled_segment = resampled_segment[:segment_end - segment_start]
                elif len(resampled_segment) < (segment_end - segment_start):
                    pad_width = (segment_end - segment_start) - len(resampled_segment)
                    resampled_segment = np.pad(resampled_segment, (0, pad_width), mode='constant')

                # Добавление ресэмплированного сегмента к изменённым значениям
                modified_signal[segment_start:segment_end] = resampled_segment

    # Нормализация изменённых значений, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal, sr

def change_formants_shifts31(signal, sr, formant_shifts, formants=None):
    """
    Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.
    """
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
    else:
        frequencies, times, _, _ = formant_frequencies(signal, sr)

    # Определение функции для получения новой частоты форманты
    def get_new_formant_freq(original_freq, formant_num):
        if original_freq <= 0:
            return original_freq
        return original_freq + formant_shifts[formant_num]

    # Создание нового объекта звука для изменённого звука
    modified_signal = np.copy(signal)

    # Итерация по каждому временно́му шагу и изменение частот формант
    for t_idx, t in enumerate(times):
        for i in range(5):  # Форманты F1 до F5
            original_freq = frequencies[i][t_idx]
            if original_freq > 0:  # Убедиться, что частота форманты действительна
                new_freq = get_new_formant_freq(original_freq, i)

                # Расчёт коэффициента ресэмплинга
                resample_ratio = new_freq / original_freq

                # Регулировка значений звука вокруг частоты форманты
                segment_start = max(0, int(t * sr) - int(sr / 50))
                segment_end = min(len(signal), int(t * sr) + int(sr / 50))

                segment = signal[segment_start:segment_end]

                # Ресэмплинг сегмента для изменения частоты форманты
                resampled_segment = resample(segment, int(len(segment) * resample_ratio))

                # Регулировка длины для соответствия оригинальному сегменту
                if len(resampled_segment) > (segment_end - segment_start):
                    resampled_segment = resampled_segment[:segment_end - segment_start]
                elif len(resampled_segment) < (segment_end - segment_start):
                    pad_width = (segment_end - segment_start) - len(resampled_segment)
                    resampled_segment = np.pad(resampled_segment, (0, pad_width), mode='constant')

                # Добавление ресэмплированного сегмента к изменённым значениям
                modified_signal[segment_start:segment_end] = resampled_segment

    # Нормализация изменённых значений, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal, sr


def change_formants_shifts3(signal, sr, formant_shifts, max_shift=500, segment_duration=0.01, formants=None):
    """
    Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.
    Сглаживает эффект при больших значениях formant_shifts.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param formant_shifts: Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5].
    :param max_shift: Максимальное значение смещения частоты форманты (в герцах).
    :param segment_duration: Длительность сегмента в секундах, используемого для обработки.
    :return: Изменённый аудиосигнал и частота дискретизации.
    """
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Определение функции для получения новой частоты форманты с учетом ограничений
    def get_new_formant_freq(original_freq, formant_num):
        if original_freq <= 0:
            return original_freq
        shift = np.clip(formant_shifts[formant_num], -max_shift, max_shift)  # Ограничение смещения
        return original_freq + shift

    # Создание нового объекта звука для изменённого звука
    modified_signal = np.copy(signal)

    # Итерация по каждому временно́му шагу и изменение частот формант
    segment_length = int(segment_duration * sr)  # Длительность сегмента в выборках
    for t_idx, t in enumerate(times):
        for i in range(5):  # Форманты F1 до F5
            original_freq = frequencies[i][t_idx]
            if original_freq > 0:  # Убедиться, что частота форманты действительна
                new_freq = get_new_formant_freq(original_freq, i)

                # Расчёт коэффициента ресэмплинга
                resample_ratio = new_freq / original_freq

                # Регулировка значений звука вокруг частоты форманты
                segment_start = max(0, int(t * sr) - segment_length // 2)  # Использование segment_length
                segment_end = min(len(signal), int(t * sr) + segment_length // 2)

                segment = signal[segment_start:segment_end]

                # Ресэмплинг сегмента для изменения частоты форманты
                num_samples = int(len(segment) * resample_ratio)
                if num_samples > 0:
                    resampled_segment = resample(segment, num_samples)

                    # Регулировка длины для соответствия оригинальному сегменту
                    if len(resampled_segment) > (segment_end - segment_start):
                        resampled_segment = resampled_segment[:segment_end - segment_start]
                    elif len(resampled_segment) < (segment_end - segment_start):
                        pad_width = (segment_end - segment_start) - len(resampled_segment)
                        resampled_segment = np.pad(resampled_segment, (0, pad_width), mode='constant')

                    # Добавление ресэмплированного сегмента к изменённым значениям
                    modified_signal[segment_start:segment_end] = resampled_segment

    # Нормализация изменённых значений, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    # Применение сглаживающего фильтра для уменьшения искажений
    b, a = scipy.signal.butter(3, 0.05, btype='low')
    modified_signal = scipy.signal.filtfilt(b, a, modified_signal)

    return modified_signal, sr


def change_formants_shifts4(signal, sr, shift_factors, max_shift=500, formants=None):
    """
    Изменяет частоту формант в аудиосигнале на фиксированное значение для каждой форманты.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param shift_factors: Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5].
    :param max_shift: Максимальное значение смещения частоты форманты (в герцах).
    :return: Изменённый аудиосигнал.
    """
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
    else:
        frequencies, times, _, _ = formant_frequencies(signal, sr)
    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        if shift_factors[i] != 0 and not np.all(np.isnan(frequencies[i])):
            lowcut = np.nanmin(frequencies[i])
            highcut = np.nanmax(frequencies[i])

            if lowcut >= highcut:
                continue
            if lowcut == highcut:
                lowcut -= 10
                highcut += 10
            if highcut > sr / 2:
                highcut = sr / 2

            b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Сначала убираем старую форманту
            modified_signal -= filtered_signal

            # Затем сдвигаем частоту форманты
            for t_idx, t in enumerate(times):
                original_freq = frequencies[i][t_idx]
                if original_freq > 0:  # Убедиться, что частота форманты действительна
                    shift = np.clip(shift_factors[i], -max_shift, max_shift)  # Ограничение смещения
                    new_freq = original_freq + shift

                    # Расчёт коэффициента ресэмплинга
                    resample_ratio = new_freq / original_freq

                    # Ресэмплинг сегмента для изменения частоты форманты
                    num_samples = int(len(filtered_signal) * resample_ratio)
                    if num_samples > 0:
                        resampled_signal = scipy.signal.resample(filtered_signal, num_samples)

                        # Регулировка длины для соответствия оригинальному сегменту
                        if len(resampled_signal) > len(filtered_signal):
                            resampled_signal = resampled_signal[:len(filtered_signal)]
                        elif len(resampled_signal) < len(filtered_signal):
                            pad_width = len(filtered_signal) - len(resampled_signal)
                            resampled_signal = np.pad(resampled_signal, (0, pad_width), mode='constant')

                        # Добавление сдвинутого сигнала форманты к изменённому сигналу
                        modified_signal += resampled_signal

    modified_signal = np.clip(modified_signal, -1, 1)
    return modified_signal


def calculate_segment_duration(formant_shifts, base_duration=0.0025, S=350, beta=0.1):
    max_shift = np.max(np.abs(formant_shifts))

    if max_shift <= 350:
        # Линейная компонента для границ
        linear_component = base_duration * (100 / max_shift)

        # Усиленный прогиб в середине диапазона
        x = np.clip(max_shift - 100, 0, 250)  # Прогиб начинает действовать с 100 Гц и далее
        nonlinear_component = base_duration * (1 - (x / S) ** beta)

        # Комбинированное значение
        value = linear_component * (1 - (x / S) ** beta) + nonlinear_component
    else:
        # Линейное поведение за пределами диапазона
        value = base_duration * (1 + (max_shift - 300) / S)

    return min(max(value, 0.0007), 0.0025)

def change_formants_shifts5(signal, sr, formant_shifts, max_shift=500, segment_duration=0.01):
    """
    Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.
    Сглаживает эффект при больших значениях formant_shifts.
    Новые частоты формант остаются в пределах своего диапазона.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param formant_shifts: Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5].
    :param max_shift: Максимальное значение смещения частоты форманты (в герцах).
    :param segment_duration: Длительность сегмента в секундах, используемого для обработки.
    :return: Изменённый аудиосигнал и частота дискретизации.
    """
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Определение функции для получения новой частоты форманты с учетом ограничений
    def get_new_formant_freq(original_freq, formant_num):
        if original_freq <= 0:
            return original_freq
        shift = np.clip(formant_shifts[formant_num], -max_shift, max_shift)  # Ограничение смещения
        new_freq = original_freq + shift

        # Ограничение новой частоты в пределах диапазона
        min_freq, max_freq = formant_ranges[formant_num + 1]  # +1 для соответствия индексу форманты
        return np.clip(new_freq, min_freq, max_freq)

    # Создание нового объекта звука для изменённого звука
    modified_signal = np.copy(signal)

    # Итерация по каждому временно́му шагу и изменение частот формант
    segment_duration = calculate_segment_duration(formant_shifts)
    segment_length = int(segment_duration * sr)  # Длительность сегмента в выборках

    for t_idx, t in enumerate(times):
        for i in range(5):  # Форманты F1 до F5
            original_freq = frequencies[i][t_idx]
            if original_freq > 0:  # Убедиться, что частота форманты действительна
                new_freq = get_new_formant_freq(original_freq, i)

                # Расчёт коэффициента ресэмплинга
                resample_ratio = new_freq / original_freq

                # Регулировка значений звука вокруг частоты форманты
                segment_start = max(0, int(t * sr) - segment_length // 2)  # Использование segment_length
                segment_end = min(len(signal), int(t * sr) + segment_length // 2)

                segment = signal[segment_start:segment_end]

                # Ресэмплинг сегмента для изменения частоты форманты
                num_samples = int(len(segment) * resample_ratio)
                if num_samples > 0:
                    resampled_segment = resample(segment, num_samples)

                    # Регулировка длины для соответствия оригинальному сегменту
                    if len(resampled_segment) > (segment_end - segment_start):
                        resampled_segment = resampled_segment[:segment_end - segment_start]
                    elif len(resampled_segment) < (segment_end - segment_start):
                        pad_width = (segment_end - segment_start) - len(resampled_segment)
                        resampled_segment = np.pad(resampled_segment, (0, pad_width), mode='constant')

                    # Добавление ресэмплированного сегмента к изменённым значениям
                    modified_signal[segment_start:segment_end] = resampled_segment

    # Нормализация изменённых значений, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    # Применение сглаживающего фильтра для уменьшения искажений
    b, a = scipy.signal.butter(3, 0.05, btype='low')
    modified_signal = scipy.signal.filtfilt(b, a, modified_signal)

    return modified_signal, sr


def change_formants_shifts6(signal, sr, formant_shifts, max_shift=500, formants=None):
    """
    Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.
    Сглаживает эффект при больших значениях formant_shifts.
    Новые частоты формант остаются в пределах своего диапазона с возможным сжатием.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param formant_shifts: Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5].
    :param max_shift: Максимальное значение смещения частоты форманты (в герцах).
    :param segment_duration: Длительность сегмента в секундах, используемого для обработки.
    :return: Изменённый аудиосигнал и частота дискретизации.
    """
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
    else:
        frequencies, times, _, _ = formant_frequencies(signal, sr)

    # Предварительные вычисления для каждой форманты
    freq_main_list = []
    k_list = []
    for i in range(5):  # Форманты F1 до F5
        min_freq, max_freq = formant_ranges[i + 1]  # +1 для соответствия индексу форманты

        # Вычисление средних и крайних частот с учетом сдвига
        freq_main = np.mean(frequencies[i]) + formant_shifts[i]
        freq_max = np.max(frequencies[i]) + formant_shifts[i]
        freq_min = np.min(frequencies[i]) + formant_shifts[i]

        # Вычисление коэффициентов для сжатия диапазона
        k_max = (freq_max - freq_main) / (max_freq - freq_main)
        k_min = (freq_main - freq_min) / (freq_main - min_freq)
        k = max(k_max, k_min)

        freq_main_list.append(freq_main)
        k_list.append(k)

    def get_new_formant_freq(original_freq, formant_num):
        if original_freq <= 0:
            return original_freq
        shift = np.clip(formant_shifts[formant_num], -max_shift, max_shift)
        new_freq = original_freq + shift

        # Используем заранее вычисленные значения
        freq_main = freq_main_list[formant_num]
        k = k_list[formant_num]

        if k > 1:
            # Сжатие диапазона частот форманты
            scaling_factor = 1 / k
            new_freq = freq_main + scaling_factor * (new_freq - freq_main)

        min_freq, max_freq = formant_ranges[formant_num + 1]
        return np.clip(new_freq, min_freq, max_freq)

    modified_signal = np.copy(signal)
    segment_duration = calculate_segment_duration(formant_shifts)
    segment_length = int(segment_duration * sr)

    for t_idx, t in enumerate(times):
        for i in range(5):  # Форманты F1 до F5
            original_freq = frequencies[i][t_idx]
            if original_freq > 0:
                new_freq = get_new_formant_freq(original_freq, i)

                resample_ratio = new_freq / original_freq
                segment_start = max(0, int(t * sr) - segment_length // 2)
                segment_end = min(len(signal), int(t * sr) + segment_length // 2)

                segment = signal[segment_start:segment_end]

                num_samples = int(len(segment) * resample_ratio)
                if num_samples > 0:
                    resampled_segment = resample(segment, num_samples)

                    if len(resampled_segment) > (segment_end - segment_start):
                        resampled_segment = resampled_segment[:segment_end - segment_start]
                    elif len(resampled_segment) < (segment_end - segment_start):
                        pad_width = (segment_end - segment_start) - len(resampled_segment)
                        resampled_segment = np.pad(resampled_segment, (0, pad_width), mode='constant')

                    modified_signal[segment_start:segment_end] = resampled_segment

    modified_signal = np.clip(modified_signal, -1, 1)

    b, a = scipy.signal.butter(3, 0.05, btype='low')
    modified_signal = scipy.signal.filtfilt(b, a, modified_signal)

    return modified_signal, sr

"""
Фильтрация с помощью полосовых фильтров:
Для каждой форманты используется полосовой фильтр, заданный диапазонами частот.
Каждая форманта усиливается на фиксированное значение в dB, и результат фильтрации суммируется с исходным сигналом.
Итоговый сигнал ограничивается максимальной амплитудой
+ Ясное определение диапазонов частот для каждой форманты.
- Может возникнуть перекрытие полос пропускания фильтров, что приведет к искажениям.
- Фиксированные диапазоны формант могут не соответствовать реальным значениям в каждом сигнале.
"""
def boost_formants_filter(y, sr, boost_dB, max_amplitude_dB):
    y_boosted = np.zeros_like(y)
    max_amplitude = 10 ** (max_amplitude_dB / 20)  # Преобразование dB в линейное значение
    boost_factors = [10 ** (dB / 20) for dB in boost_dB]  # Преобразование dB в линейное значение

    # Извлечение формант
    formants = extract_formants(y, sr)

    # Применяем полосовые фильтры для каждой форманты
    for formant_index, formant in enumerate(formants, start=1):
        boost_factor = boost_factors[formant_index-1]
        bandwidth = calculate_formant_bandwidth(y, sr, formant_index) / 2
        if formant > 0 and formant + bandwidth < sr / 2:
            # Убираем старый сигнал форманты
            y_boosted -= filtered_signal

            y_filtered = fl.apply_bandpass_filter(y, sr, max(formant - bandwidth, 1), formant + bandwidth)
            y_boosted += y_filtered * boost_factor

    y_boosted = np.clip(y_boosted, -max_amplitude, max_amplitude)
    return y + y_boosted

"""
Фильтрация с помощью пиковых фильтров:
Для каждой форманты создается пиковый фильтр с заданной центральной частотой.
Каждая форманта усиливается на заданное значение в dB с использованием пикового фильтра.
Усиленный сигнал добавляется к исходному.
+ Пиковые фильтры более точно настраиваются на центральные частоты формант.
+ Меньшая вероятность перекрытия частотных диапазонов.
- Требуется точное знание центральных частот формант для каждого сигнала.
- Может быть более чувствительна к ошибкам в определении частот формант.
"""
def boost_formants_peak(signal, sr, gain_dB, max_amplitude_dB):
    max_amplitude = 10 ** (max_amplitude_dB / 20)  # Преобразование dB в линейное значение
    gains = [10 ** (g / 20) for g in gain_dB]

    y_boosted = np.copy(signal)
    formants = extract_formants(signal, sr)

    for formant_index, formant in enumerate(formants, start=1):
        gain = gains[formant_index - 1]
        bandwidth = calculate_formant_bandwidth(signal, sr, formant_index) / 2
        if bandwidth > 0 and formant > 0 and formant + bandwidth < sr / 2:
            b, a = scipy.signal.butter(2, [max(formant - bandwidth, 1), min(formant + bandwidth, sr/2 -1)], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Убираем старый сигнал форманты
            y_boosted -= filtered_signal

            # Затем усиливаем сигнал форманты и добавляем его обратно
            amplified_signal = gain * filtered_signal
            y_boosted += amplified_signal

    y_boosted = np.clip(y_boosted, -max_amplitude, max_amplitude)
    return y_boosted

def change_formants_amplitude(y, sr, boost_dB, max_amplitude_dB=0):
    """
    Изменяет амплитуду формант в аудиофайле.
    """
    # Увеличение амплитуды формант
    y_boosted = boost_formants_peak(y, sr, boost_dB, max_amplitude_dB)

    return y_boosted

def change_formants_amplitude2(signal, sr, amplitude_factors, max_amplitude_dB=0):
    """
    Изменяет амплитуду каждой форманты F1-F5.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param amplitude_factors: Список факторов амплитуды для каждой форманты [A1, A2, A3, A4, A5].
    """
    max_amplitude = 10 ** (max_amplitude_dB / 20)  # Преобразование dB в линейное значение
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)
    
    modified_signal = np.copy(signal)

    for t_idx, t in enumerate(times):
        for i in range(5):  # Форманты F1 до F5
            original_freq = frequencies[i][t_idx]
            if original_freq > 0:
                bandwidth = bandwidths[i][t_idx] / 2
                b, a = scipy.signal.butter(2, [max(original_freq - bandwidth, 1), min(original_freq + bandwidth, sr/2 -1)], btype='band', fs=sr)
                filtered_signal = scipy.signal.lfilter(b, a, signal)

                # Убираем старый сигнал форманты
                modified_signal -= filtered_signal

                # Изменение амплитуды
                modified_filtered_signal = filtered_signal * amplitude_factors[i]
                
                # Добавление изменённого фильтрованного сигнала к изменённому сигналу
                modified_signal += modified_filtered_signal

    # Нормализация изменённых значений, чтобы предотвратить клиппинг
    max_val = np.max(np.abs(modified_signal))
    if max_val > 0:
        modified_signal = modified_signal / max_val

    modified_signal = np.clip(modified_signal, -max_amplitude, max_amplitude)
    return modified_signal

def compute_spectral_slope_for_formant(y, sr, formant_index, window_size=1024, hop_size=512):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Индекс форманты должен быть между 1 и 5 включительно.")

    num_windows = (len(y) - window_size) // hop_size + 1
    slopes = []
    times = []

    for i in range(num_windows):
        start = i * hop_size
        end = start + window_size
        segment = y[start:end]

        if len(segment) == 0:
            break

        # Извлечение формант из сегмента
        formants = extract_formants_from_segment(segment, sr)

        if len(formants) < formant_index:
            continue

        # Частоты формант и их диапазон
        formant_freq = formants[formant_index - 1]
        freq_range = (formant_freq * 0.5, formant_freq * 1.5)

        # Применение окна для уменьшения утечек спектра
        window = scipy.signal.get_window('hamming', window_size)
        windowed_segment = segment * window

        # Вычисление спектра
        spectrum = np.abs(np.fft.fft(windowed_segment))
        frequencies = np.fft.fftfreq(window_size, 1 / sr)

        # Пропуск частот вне интересующего диапазона
        mask = (frequencies > freq_range[0]) & (frequencies < freq_range[1])
        positive_freqs = frequencies[mask]
        positive_spectrum = spectrum[mask]

        if len(positive_freqs) == 0 or len(positive_spectrum) == 0:
            continue

        # Линейная регрессия для расчета спектрального наклона
        X = positive_freqs.reshape(-1, 1)  # Частоты в качестве независимой переменной
        y = np.log(positive_spectrum)  # Логарифм спектра в качестве зависимой переменной

        reg = LinearRegression().fit(X, y)
        slope = reg.coef_[0]

        slopes.append(slope)
        times.append(start / sr + window_size / (2 * sr))  # Среднее время для окна

    return times, slopes

def compute_spectral_slope_for_formant2(signal, sr, formant_index, formants=None):
    if formant_index < 1 or formant_index > 5:
        raise ValueError("Formant index must be between 1 and 5")

    if formants:
        frequencies = formants["frequencies"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, _, bandwidths, _ = formant_frequencies(signal, sr)
    index = formant_index - 1

    formant_frequency = np.nanmean(frequencies[index])
    if np.isnan(formant_frequency) or formant_frequency <= 0:
        return 0

    bandwidth = calculate_formant_bandwidth_(bandwidths, formant_index) / 2
    b, a = scipy.signal.butter(2, [max(formant_frequency - bandwidth, 1),
                                   min(formant_frequency + bandwidth, sr/2 -1)], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Compute the FFT of the filtered signal
    fft_spectrum = np.fft.fft(filtered_signal)
    fft_frequencies = np.fft.fftfreq(len(filtered_signal), 1 / sr)

    # Get the positive frequencies
    positive_frequencies = fft_frequencies[:len(fft_frequencies) // 2]
    positive_spectrum = np.abs(fft_spectrum[:len(fft_spectrum) // 2])

    # Remove zero frequencies for log transform
    positive_frequencies = positive_frequencies[positive_frequencies > 0]
    positive_spectrum = positive_spectrum[:len(positive_frequencies)]

    # Log transform the spectrum
    log_frequencies = np.log(positive_frequencies)
    log_spectrum = np.log(positive_spectrum)

    # Perform linear regression to get the spectral slope
    slope, intercept = np.polyfit(log_frequencies, log_spectrum, 1)

    return slope


def change_formant_bandwidth2(signal, sr, bandwidth_factors, formants=None):
    # Получение частот формант, временных шагов, ширины полос и интенсивности
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Создаем массив для хранения измененного сигнала
    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        center_freqs = frequencies[i]
        orig_bandwidths = bandwidths[i]

        for t_idx, t in enumerate(times):
            if np.isnan(center_freqs[t_idx]) or center_freqs[t_idx] <= 0:
                continue

            # Изменение ширины полосы
            new_bandwidth = orig_bandwidths[t_idx] * bandwidth_factors[i]

            # Применяем полосовой фильтр с новой шириной полосы
            lowcut = max(center_freqs[t_idx] - new_bandwidth / 2, 1)
            highcut = min(center_freqs[t_idx] + new_bandwidth / 2, sr / 2)

            b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Определение сегмента для замены
            segment_start = int(t * sr) - len(filtered_signal) // 2
            segment_end = segment_start + len(filtered_signal)

            if segment_start < 0:
                segment_start = 0
                segment_end = len(filtered_signal)
            if segment_end > len(signal):
                segment_end = len(signal)
                segment_start = segment_end - len(filtered_signal)

            # Вычитание исходного сигнала форманты
            modified_signal[segment_start:segment_end] -= filtered_signal[:segment_end - segment_start]

            # Добавление модифицированного сигнала
            modified_signal[segment_start:segment_end] += filtered_signal[:segment_end - segment_start]

    # Нормализация, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal


def change_formant_bandwidth(signal, sr, bandwidth_factors, formants=None):
    """
    Изменяет ширину канала формант F1-F5 в аудиосигнале вокруг средней частоты форманты.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param bandwidth_factors: Список факторов ширины канала для каждой форманты [B1, B2, B3, B4, B5].
    :return: Изменённый аудиосигнал.
    """
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
        bandwidths = formants["bandwidths"]
    else:
        frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)
    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        center_freqs = frequencies[i]
        orig_bandwidths = bandwidths[i]

        if np.all(np.isnan(center_freqs)):
            continue

        f_avg = np.nanmean(center_freqs)
        bandwidth = np.nanmean(orig_bandwidths)
        new_bandwidth = bandwidth * bandwidth_factors[i]

        for t_idx, t in enumerate(times):
            if np.isnan(center_freqs[t_idx]) or center_freqs[t_idx] <= 0:
                continue

            lowcut = max(f_avg - new_bandwidth / 2, 1)
            highcut = min(f_avg + new_bandwidth / 2, sr / 2)

            b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)

            segment_start = int(t * sr) - sr // 100
            segment_end = segment_start + sr // 100

            if segment_start < 0:
                segment_start = 0
            if segment_end > len(signal):
                segment_end = len(signal)

            segment = signal[segment_start:segment_end]
            filtered_segment = scipy.signal.lfilter(b, a, segment)

            # Вычитаем исходный сигнал форманты
            modified_signal[segment_start:segment_start + len(filtered_segment)] -= filtered_segment

            # Усиливаем или ослабляем сигнал форманты
            filtered_segment *= bandwidth_factors[i]

            # Добавляем его обратно
            modified_signal[segment_start:segment_start + len(filtered_segment)] += filtered_segment

    modified_signal = np.clip(modified_signal, -1, 1)
    return modified_signal


def change_formant_frequencies(signal, sr, frequency_factors):
    """
    Изменяет частоту каждой форманты F1-F5 в заданное количество раз.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param frequency_factors: Список факторов частоты для каждой форманты [F1, F2, F3, F4, F5].
    """
    # Получение частот формант, временных шагов, ширины полос и интенсивности
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    # Создаем массив для хранения измененного сигнала
    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        if not np.all(np.isnan(frequencies[i])):
            lowcut = np.nanmin(frequencies[i])
            highcut = np.nanmax(frequencies[i])

            if lowcut >= highcut:
                continue
            if lowcut == highcut:
                lowcut = lowcut - 10
                highcut = highcut + 10
            if highcut > sr / 2:
                highcut = sr / 2

            b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Масштабирование частоты форманты
            num_samples = int(len(filtered_signal) * frequency_factors[i])
            resampled_signal = scipy.signal.resample(filtered_signal, num_samples)

            # Регулировка длины для соответствия оригинальному сегменту
            segment_length = len(signal)
            if len(resampled_signal) > segment_length:
                resampled_signal = resampled_signal[:segment_length]
            elif len(resampled_signal) < segment_length:
                pad_width = segment_length - len(resampled_signal)
                resampled_signal = np.pad(resampled_signal, (0, pad_width), mode='constant')

            # Вычитание исходного сигнала форманты
            modified_signal -= filtered_signal

            # Добавление масштабированного сигнала
            modified_signal += resampled_signal

    # Нормализация, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal


def extract_formant_rate(y, sr, formant_index=1, medfilt_size=5, formants=None):
    # Извлечение формант и временных меток с помощью formant_frequencies
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
    else:
        frequencies, times, _, _ = formant_frequencies(y, sr)

    if len(frequencies[formant_index - 1]) == 0:
        return None, None, None  # Если нет данных о форманте, возвращаем None

    # Извлечение данных для конкретной форманты
    freq = np.array(frequencies[formant_index - 1])
    freq = freq[freq > 100]

    # Применение медианного фильтра
    filtered_frequencies = medfilt(freq.flatten(), medfilt_size)

    if len(filtered_frequencies) == 0:
        return None, None, None  # Если нет отфильтрованных частот, возвращаем None

    # Интервалы между временными метками, где зафиксированы действительные частоты формант
    formant_intervals = np.diff(times)

    if len(formant_intervals) == 0:
        return None, None, None  # Если нет интервалов, возвращаем None

    # Расчет периода, амплитуды и смещения
    period = pt.calculate_period(filtered_frequencies, times)
    amplitude = pt.calculate_amplitude_from_period(filtered_frequencies, times, period)
    offset = pt.calculate_period_shift(filtered_frequencies, times, period)

    return period, offset, amplitude


def calculate_formant_slope(y, sr, formant_index=1, is_smooth=True, is_peak=True, formants=None):
    # Извлечение частот формант и временных меток
    if formants:
        frequencies = formants["frequencies"]
        times = formants["voiced_times"]
    else:
        frequencies, times, _, _ = formant_frequencies(y, sr)

    if len(times) == 0:
        return 0, 0, "Нет данных"  # Если нет данных, возвращаем 0

    # Извлечение данных для конкретной форманты
    freq = np.array(frequencies[formant_index - 1])
    freq = freq[freq > 100]

    if len(freq) == 0:
        return 0, 0, "Нет данных"  # Если нет данных, возвращаем 0

    # Сглаживание частот
    if is_smooth:
        freq = pt.smooth_values(freq)
        times = times[:len(freq)]  # Обновляем времена после сглаживания

    # Оставляем только пики частот
    if is_peak:
        peaks = pt.detect_peaks(freq)
        freq = freq[peaks]
        times = times[peaks]

    # Линейная регрессия
    if len(times) < 2:  # Нужно хотя бы две точки для регрессии
        return 0, 0, "Недостаточно данных"

    slope, intercept, r_value, p_value, std_err = linregress(times, freq)

    # Вычисляем предсказанные значения по линейной регрессии
    predicted_freq = intercept + slope * times

    # Вычисляем остатки (разницу между реальными и предсказанными значениями)
    residuals = freq - predicted_freq

    # Вычисляем дисперсию остатков
    variance = np.var(residuals)

    # Определяем направление тренда
    # if slope > 0 and variance < 0.01:
    #     trend = "Рост"
    # elif slope < 0 and variance < 0.01:
    #     trend = "Падение"
    # else:
    #     trend = "Стабильный"
    if slope > 0:
        trend = "Рост"
    elif slope < 0:
        trend = "Падение"
    else:
        trend = "Стабильный"

    return slope, variance, trend


def calculate_intensity_slope(y, sr, is_smooth=True, is_peak=True, formants=None):
    # Извлечение интенсивности и временных меток
    if formants:
        intensities = formants["intensities"]
        intensity_times = formants["intensity_times"]
    else:
        _, _, intensities, intensity_times = formant_frequencies(y, sr)

    if len(intensity_times) == 0 or len(intensities) == 0:
        return 0, 0, "Нет данных"  # Если нет данных, возвращаем 0

    # Преобразуем интенсивности в массив для удобства обработки
    intensity_values = np.array(intensities)

    # Фильтрация интенсивностей (если требуется)
    intensity_values = intensity_values[intensity_values > 0]  # Убираем нулевые значения, если такие есть

    if len(intensity_values) == 0:
        return 0, 0, "Нет данных"  # Если нет данных после фильтрации, возвращаем 0

    # Сглаживание интенсивностей
    if is_smooth:
        intensity_values = pt.smooth_values(intensity_values)  # Используем подходящий метод для сглаживания
        intensity_times = intensity_times[:len(intensity_values)]  # Обновляем временные метки после сглаживания

    # Оставляем только пики интенсивностей
    if is_peak:
        peaks = pt.detect_peaks(intensity_values)
        intensity_values = intensity_values[peaks]
        intensity_times = intensity_times[peaks]

    # Линейная регрессия для интенсивностей
    if len(intensity_times) < 2:  # Нужно хотя бы две точки для регрессии
        return 0, 0, "Недостаточно данных"

    slope, intercept, r_value, p_value, std_err = linregress(intensity_times, intensity_values)

    # Вычисляем предсказанные значения по линейной регрессии
    predicted_intensity = intercept + slope * intensity_times

    # Вычисляем остатки (разницу между реальными и предсказанными значениями)
    residuals = intensity_values - predicted_intensity

    # Вычисляем дисперсию остатков
    variance = np.var(residuals)

    # Определяем направление тренда для интенсивности
    if slope > 0:
        trend = "Рост"
    elif slope < 0:
        trend = "Падение"
    else:
        trend = "Стабильный"

    return slope, variance, trend

def flatten_formants(signal, sr, mean_formant_signals=[0.1, 0.1, 0.1, 0.1, 0.1, ]):
    """
    Выравнивает форманты F1-F5 на уровне их средней частоты в аудиосигнале,
    сохраняя исходный сигнал и изменяя частоты формант.
    """
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        formant_frequencies_i = frequencies[i]

        if not np.all(np.isnan(formant_frequencies_i)):
            mean_frequency = np.nanmean(formant_frequencies_i)
            if np.isnan(mean_frequency):
                continue

            lowcut = np.nanmin(formant_frequencies_i)
            highcut = np.nanmax(formant_frequencies_i)

            if lowcut >= highcut:
                continue
            if lowcut < 0:
                lowcut = 0
            if highcut > sr / 2:
                highcut = sr / 2

            # Фильтруем сигнал, чтобы выделить сигнал форманты
            b, a = scipy.signal.butter(4, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Создаем синусоидальный сигнал на основе средней частоты форманты
            t = np.arange(len(signal)) / sr
            mean_formant_signal = mean_formant_signals[i] * np.sin(2 * np.pi * mean_frequency * t)

            # Вычитаем старую форманту и добавляем новую с фиксированной частотой
            modified_signal -= filtered_signal
            modified_signal += mean_formant_signal

    # Нормализация сигнала для предотвращения клиппинга
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal

def slope_formants(signal, sr, slope_factors=[0.5, 0.5, 0.5, 0.5, 0.5], mixing_percent=[0.1, 0.1, 0.1, 0.1, 0.1],
                   filtered_percent=[1.0, 1.0, 1.0, 1.0, 1.0], method='center', replace=True):
    frequencies, times, bandwidths, _ = formant_frequencies(signal, sr)

    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        # if slope_factors[i] == 0 or (not replace and mixing_percent[i] == 0):
        #     continue
        formant_frequencies_i = frequencies[i]

        if not np.all(np.isnan(formant_frequencies_i)):
            mean_frequency = np.nanmean(formant_frequencies_i)
            if np.isnan(mean_frequency):
                continue

            lowcut = np.nanmin(formant_frequencies_i)
            highcut = np.nanmax(formant_frequencies_i)

            if lowcut >= highcut:
                continue
            if lowcut < 0:
                lowcut = 0
            if highcut > sr / 2:
                highcut = sr / 2

            # Фильтруем сигнал, чтобы выделить сигнал форманты
            b, a = scipy.signal.butter(4, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Создаем измененный сигнал на основе наклона форманты
            t = np.arange(len(signal)) / sr
            slope = slope_factors[i]
            if method == 'center':
                new_frequency = mean_frequency * (1 + slope * (t - t.mean()))
            else:
                new_frequency = mean_frequency * (1 + slope * t)

            # Генерируем сигнал с наклоном
            sloped_formant_signal = np.sin(2 * np.pi * new_frequency * t)

            # Нормализуем наклоненный сигнал, чтобы сохранить исходную амплитуду
            sloped_formant_signal *= np.max(np.abs(filtered_signal)) / np.max(np.abs(sloped_formant_signal))

            if replace:
                # Заменяем старую форманту новой с измененным наклоном
                modified_signal -= filtered_signal * filtered_percent[i]

            # Применяем коэффициент влияния для текущей форманты
            sloped_formant_signal *= mixing_percent[i]

            # Добавляем новый сигнал с наклоном
            modified_signal += sloped_formant_signal

    # Нормализация сигнала для предотвращения клиппинга
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal


def change_formant_energy_and_shift(signal, sr, energy_factors, frequency_shifts, formants=None):
    """
    Усиливает энергию формант и сдвигает их частоты одновременно.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param energy_factors: Список коэффициентов усиления для каждой форманты [E1, E2, E3, E4, E5].
    :param frequency_shifts: Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5].
    :return: Изменённый аудиосигнал.
    """
    if formants:
        frequencies = formants["frequencies"]
    else:
        frequencies, _, _, _ = formant_frequencies(signal, sr)
    modified_signal = np.copy(signal)

    for i in range(5):  # F1-F5
        if (energy_factors[i] != 0 or frequency_shifts[i] != 0) and not np.all(np.isnan(frequencies[i])):
            lowcut = np.nanmin(frequencies[i])
            highcut = np.nanmax(frequencies[i])

            if lowcut >= highcut:
                continue
            if lowcut == highcut:
                lowcut -= 10
                highcut += 10
            if highcut > sr / 2:
                highcut = sr / 2

            # Применение полосового фильтра для выделения текущей форманты
            b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, signal)

            # Сначала убираем старую форманту
            modified_signal -= filtered_signal

            # Изменение частоты форманты
            shift_amount = frequency_shifts[i]
            if shift_amount != 0:
                resample_ratios = (frequencies[i] + shift_amount) / frequencies[i]

                # Игнорирование NaN и деление на ноль
                valid_ratios = resample_ratios[~np.isnan(resample_ratios) & (resample_ratios != 0)]
                if len(valid_ratios) == 0:
                    continue

                resample_ratio = np.mean(valid_ratios)

                # Применение ресэмплинга к выделенному сигналу
                num_samples = int(len(filtered_signal) * resample_ratio)
                resampled_signal = resample(filtered_signal, num_samples)

                # Регулировка длины для соответствия оригинальному сегменту
                if len(resampled_signal) > len(filtered_signal):
                    resampled_signal = resampled_signal[:len(filtered_signal)]
                elif len(resampled_signal) < len(filtered_signal):
                    pad_width = len(filtered_signal) - len(resampled_signal)
                    resampled_signal = np.pad(resampled_signal, (0, pad_width), mode='constant')

                filtered_signal = resampled_signal

            # Усиление сигнала форманты и добавление его обратно
            amplified_signal = filtered_signal * energy_factors[i]
            modified_signal += amplified_signal

    # Нормализация сигнала для предотвращения клиппинга
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal


def find_max_formant_energy_time(formant_energy):
    if len(formant_energy) == 0:
        return 0

    formant_energy_array = np.array(formant_energy)

    # Извлечение энергии и времени
    energies = formant_energy_array[:, 0]
    times = formant_energy_array[:, 1]

    # Нахождение индекса максимальной энергии
    max_energy_idx = np.argmax(energies)

    # Возврат времени, соответствующего максимальной энергии
    max_energy_time = times[max_energy_idx]

    return max_energy_time

def segment_and_smooth(data, num_segments):
    """
    Разбивает данные на секции и сглаживает их до прямой.

    Parameters:
    - data: Входные данные для сегментации (частоты или ширина канала).
    - num_segments: Количество сегментов.

    Returns:
    - Список сглаженных сегментов.
    """
    segment_length = len(data) // num_segments
    smoothed_segments = []

    for i in range(num_segments):
        start_idx = i * segment_length
        if i == num_segments - 1:  # Последний сегмент до конца данных
            end_idx = len(data)
        else:
            end_idx = (i + 1) * segment_length

        segment = data[start_idx:end_idx]

        # Линейная аппроксимация сегмента (сглаживание)
        x = np.arange(len(segment))
        slope, intercept, _, _, _ = stats.linregress(x, segment)
        smoothed_segment = slope * x + intercept
        smoothed_segments.append(smoothed_segment)

    return smoothed_segments


def analyze_formant_patterns(frequencies, bandwidths, formant_ranges, num_segments=3, eps_freq=0.1, eps_width=10):
    """
    Анализирует последовательности изменений частот и ширины канала, разбитых на секции для каждой форманты.

    Parameters:
    - frequencies: Список списков частот формант (каждый список для одной форманты).
    - bandwidths: Список списков ширины канала формант (каждый список для одной форманты).
    - formant_ranges: Словарь диапазонов частот для каждой форманты {форманта: (мин_частота, макс_частота)}.
    - num_segments: Количество секций, на которые будут разбиты данные.
    - eps_freq: Минимальная величина изменения частоты, чтобы считать это изменением.
    - eps_width: Минимальная величина изменения ширины канала, чтобы считать это изменением.

    Returns:
    - Список последовательностей паттернов для каждой форманты [(pattern_seq_freq, pattern_seq_width), ...].
    """

    formant_patterns = []

    for formant_idx, (formant_freq, formant_bw) in enumerate(zip(frequencies, bandwidths)):
        # Убираем значения NaN
        formant_freq = np.array(formant_freq)
        formant_bw = np.array(formant_bw)

        valid_indices = ~np.isnan(formant_freq) & ~np.isnan(formant_bw)
        valid_freq = formant_freq[valid_indices]
        valid_bw = formant_bw[valid_indices]

        # Проверяем, что все значения - NaN
        if len(valid_freq) == 0 or len(valid_bw) == 0:
            formant_patterns.append((np.nan, np.nan))
            continue

        # Разбиваем на секции и сглаживаем каждую секцию
        smoothed_freq_segments = segment_and_smooth(valid_freq, num_segments)
        smoothed_bw_segments = segment_and_smooth(valid_bw, num_segments)

        # Диапазон частот для данной форманты
        # Сдвигаем индекс formant_ranges на 1, так как F1 начинается с индекса 1
        min_freq, max_freq = formant_ranges[formant_idx + 1]

        # Анализ изменений для каждой секции частот
        freq_patterns = []
        for segment in smoothed_freq_segments:
            # Проверяем, что частоты внутри допустимого диапазона
            if np.any(segment < min_freq) or np.any(segment > max_freq):
                freq_patterns.append(np.nan)
            else:
                if len(segment) > 1:
                    slope = np.diff(segment).mean()  # Усредненное изменение в сегменте
                    if np.abs(slope) < eps_freq:
                        freq_patterns.append(0)  # Стабильность
                    elif slope > eps_freq:
                        freq_patterns.append(1)  # Рост
                    else:
                        freq_patterns.append(-1)  # Падение
                else:
                    freq_patterns.append(np.nan)

        # Анализ изменений ширины канала для каждой секции
        bw_patterns = []
        for segment in smoothed_bw_segments:
            if len(segment) > 1:
                slope = np.diff(segment).mean()  # Усредненное изменение в сегменте
                if np.abs(slope) < eps_width:
                    bw_patterns.append(0)  # Стабильность
                elif slope > eps_width:
                    bw_patterns.append(1)  # Увеличение ширины канала
                else:
                    bw_patterns.append(-1)  # Уменьшение ширины канала
            else:
                bw_patterns.append(np.nan)

        # Добавляем результаты анализа для данной форманты
        formant_patterns.append((freq_patterns, bw_patterns))

    return formant_patterns


def analyze_formant_patterns2(frequencies, bandwidths, formant_ranges,
                              num_segments=3, eps_freq=5,
                              eps_width=5, dist=1000, eps_dist=10):
    """
    Анализирует последовательности изменений частот и ширины канала, разбитых на секции для каждой форманты.

    Parameters:
    - frequencies: Список списков частот формант (каждый список для одной форманты).
    - bandwidths: Список списков ширины канала формант (каждый список для одной форманты).
    - formant_ranges: Словарь диапазонов частот для каждой форманты {форманта: (мин_частота, макс_частота)}.
    - num_segments: Количество секций, на которые будут разбиты данные.
    - eps_freq: Порог для изменения частоты, чтобы считать это изменением.
    - eps_width: Порог для изменения ширины канала.
    - dist: Ожидаемое расстояние между формантами.
    - eps_dist: Диапазон для определения ширины форманты.

    Returns:
    - Список последовательностей паттернов для каждой форманты [(pattern_seq_freq, pattern_seq_width, pattern_dist), ...].
    """

    def segment_and_smooth(data, num_segments):
        """
        Разбивает данные на секции и сглаживает их до прямой.

        Parameters:
        - data: Входные данные для сегментации (частоты или ширина канала).
        - num_segments: Количество сегментов.

        Returns:
        - Список сглаженных сегментов.
        """
        segment_length = len(data) // num_segments
        smoothed_segments = []

        for i in range(num_segments):
            start_idx = i * segment_length
            if i == num_segments - 1:  # Последний сегмент до конца данных
                end_idx = len(data)
            else:
                end_idx = (i + 1) * segment_length

            segment = data[start_idx:end_idx]

            # Линейная аппроксимация сегмента (сглаживание)
            x = np.arange(len(segment))
            slope, intercept, _, _, _ = stats.linregress(x, segment)
            smoothed_segment = slope * x + intercept
            smoothed_segments.append(smoothed_segment)

        return smoothed_segments

    # Шаг 1: Разбить все форманты на секции
    all_smoothed_freq_segments = []
    all_smoothed_bw_segments = []

    for formant_freq, formant_bw in zip(frequencies, bandwidths):
        formant_freq = np.array(formant_freq)
        formant_bw = np.array(formant_bw)

        # Убираем значения NaN
        valid_indices = ~np.isnan(formant_freq) & ~np.isnan(formant_bw)
        valid_freq = formant_freq[valid_indices]
        valid_bw = formant_bw[valid_indices]

        # Если нет валидных данных, добавляем NaN
        if len(valid_freq) == 0 or len(valid_bw) == 0:
            all_smoothed_freq_segments.append([np.nan] * num_segments)
            all_smoothed_bw_segments.append([np.nan] * num_segments)
        else:
            # Разбиваем и сглаживаем сегменты для каждой форманты
            smoothed_freq_segments = segment_and_smooth(valid_freq, num_segments)
            smoothed_bw_segments = segment_and_smooth(valid_bw, num_segments)

            all_smoothed_freq_segments.append(smoothed_freq_segments)
            all_smoothed_bw_segments.append(smoothed_bw_segments)

    # Шаг 2: Анализировать сегменты каждой форманты
    formant_patterns = []

    for formant_idx in range(len(frequencies)):
        # Получаем сглаженные сегменты для текущей форманты
        smoothed_freq_segments = all_smoothed_freq_segments[formant_idx]
        smoothed_bw_segments = all_smoothed_bw_segments[formant_idx]

        # Диапазон частот для данной форманты
        min_freq, max_freq = formant_ranges[formant_idx + 1]  # Начинаем с индекса 1

        # Анализ изменений частот
        freq_patterns = []
        for segment in smoothed_freq_segments:
            # Проверяем, что частоты внутри допустимого диапазона
            if np.any(segment < min_freq) or np.any(segment > max_freq):
                freq_patterns.append(np.nan)
            else:
                avg_diff = np.mean(np.diff(segment))  # Усредненное изменение
                if np.abs(avg_diff) < eps_freq:
                    freq_patterns.append(0)  # Стабильность
                elif avg_diff > eps_freq:
                    freq_patterns.append(1)  # Рост
                else:
                    freq_patterns.append(-1)  # Падение

        # Анализ изменений ширины канала
        bw_patterns = []
        for segment in smoothed_bw_segments:
            avg_diff = np.mean(np.diff(segment))  # Усредненное изменение
            if np.abs(avg_diff) < eps_width:
                bw_patterns.append(0)  # Стабильность
            elif avg_diff > eps_width:
                bw_patterns.append(1)  # Увеличение ширины канала
            else:
                bw_patterns.append(-1)  # Уменьшение ширины канала

        formant_patterns.append((freq_patterns, bw_patterns))

    # Шаг 3: Анализировать расстояния между соседними формантами
    dist_patterns = []
    for i in range(num_segments):  # Анализируем каждый сегмент по порядку
        segment_dist_patterns = []
        for formant_idx in range(len(frequencies) - 1):  # Сравниваем соседние форманты
            # Среднее значение сегментов для каждой форманты
            avg1 = np.mean(all_smoothed_freq_segments[formant_idx][i])  # Форманта F1
            avg2 = np.mean(all_smoothed_freq_segments[formant_idx + 1][i])  # Форманта F2

            delta = abs(avg2 - avg1)

            if delta - dist > eps_dist:
                segment_dist_patterns.append(1)  # Ширина больше нормальной
            elif delta - dist < -eps_dist:
                segment_dist_patterns.append(-1)  # Ширина меньше нормальной
            else:
                segment_dist_patterns.append(0)  # Нормальная ширина

        dist_patterns.append(segment_dist_patterns)

    return formant_patterns, dist_patterns


def analyze_formant_patterns3(frequencies, bandwidths, times, formant_ranges,
                              delta_time=1.0,
                              eps_freq=5, eps_width=5,
                              dist=1000, eps_dist=10):
    """
    Анализирует последовательности изменений частот, ширины канала и расстояния между соседними формантами,
    разбитых на секции с учетом временных интервалов.

    Parameters:
    - frequencies: Список списков частот формант (каждый список для одной форманты).
    - bandwidths: Список списков ширины канала формант (каждый список для одной форманты).
    - times: Время в секундах для каждой точки в frequencies и bandwidths.
    - formant_ranges: Словарь диапазонов частот для каждой форманты {форманта: (мин_частота, макс_частота)}.
    - delta_time: Шаг времени для сегментации (например, 1 секунда).
    - eps_freq: Порог для изменения частоты, чтобы считать это изменением.
    - eps_width: Порог для изменения ширины канала.
    - dist: Ожидаемое расстояние между формантами.
    - eps_dist: Диапазон для определения ширины форманты.

    Returns:
    - formant_patterns: Список, содержащий паттерны частоты, ширины канала и расстояний для каждой форманты,
                        а также список временных отрезков для каждого сегмента.
    """

    def segment_and_smooth(data):
        """
        Сегментирует данные по времени и сглаживает их до прямой.

        Parameters:
        - data: Входные данные для сегментации (частоты или ширина канала).

        Returns:
        - Сглаженные значения для этого временного сегмента.
        """
        if len(data) == 0:
            return np.nan

        # Линейная аппроксимация сегмента (сглаживание)
        x = np.arange(len(data))
        slope, intercept, _, _, _ = stats.linregress(x, data)
        smoothed_segment = slope * x + intercept
        return smoothed_segment

    # Шаг 1: Определим общий временной интервал [0, T]
    T = times[-1]  # Длительность всего аудио

    # Список для хранения всех сегментов частот и ширины канала для каждой форманты
    all_smoothed_freq_segments = [[] for _ in range(len(frequencies))]
    all_smoothed_bw_segments = [[] for _ in range(len(frequencies))]

    # Список для хранения временных отрезков сегментов
    time_segments = []

    # Шаг 2: Проходим по интервалу [0, T] с шагом delta_time
    current_time = 0
    while current_time < T:
        next_time = current_time + delta_time
        time_segments.append((current_time, next_time))  # Запоминаем текущий временной отрезок

        for formant_idx in range(len(frequencies)):
            formant_freq = np.array(frequencies[formant_idx])
            formant_bw = np.array(bandwidths[formant_idx])

            # Ищем индексы значений, которые попадают в текущий временной сегмент
            valid_indices = (times >= current_time) & (times < next_time)

            valid_freq_segment = formant_freq[valid_indices]
            valid_bw_segment = formant_bw[valid_indices]

            # Сглаживаем сегмент, если есть валидные данные
            if len(valid_freq_segment) > 0:
                smoothed_freq_segment = segment_and_smooth(valid_freq_segment)
                all_smoothed_freq_segments[formant_idx].append(smoothed_freq_segment)
            else:
                all_smoothed_freq_segments[formant_idx].append(np.nan)

            if len(valid_bw_segment) > 0:
                smoothed_bw_segment = segment_and_smooth(valid_bw_segment)
                all_smoothed_bw_segments[formant_idx].append(smoothed_bw_segment)
            else:
                all_smoothed_bw_segments[formant_idx].append(np.nan)

        # Переходим к следующему сегменту времени
        current_time = next_time

    # Шаг 3: Анализировать расстояния между соседними формантами перед анализом частот
    dist_patterns = [[] for _ in range(len(frequencies) - 1)]

    for time_segment_idx in range(len(all_smoothed_freq_segments[0])):  # Для каждого временного сегмента

        for formant_idx in range(len(frequencies) - 1):  # Сравниваем соседние форманты
            avg1 = np.mean(all_smoothed_freq_segments[formant_idx][time_segment_idx])
            avg2 = np.mean(all_smoothed_freq_segments[formant_idx + 1][time_segment_idx])

            delta = abs(avg2 - avg1)

            if delta - dist > eps_dist:
                dist_patterns[formant_idx].append(1)  # Ширина больше нормы
            elif delta - dist < -eps_dist:
                dist_patterns[formant_idx].append(-1)  # Ширина меньше нормы
            else:
                dist_patterns[formant_idx].append(0)  # Ширина в норме

    # Шаг 4: Анализировать сегменты каждой форманты, диапазоны частот и добавлять паттерн расстояний
    formant_patterns = []

    for formant_idx in range(len(frequencies)):
        smoothed_freq_segments = all_smoothed_freq_segments[formant_idx]
        smoothed_bw_segments = all_smoothed_bw_segments[formant_idx]

        min_freq, max_freq = formant_ranges[formant_idx + 1]  # Диапазон частот для данной форманты

        # Анализ изменений частот
        freq_patterns = []
        for segment in smoothed_freq_segments:
            if isinstance(segment, float) and np.isnan(segment):
                freq_patterns.append(np.nan)
            else:
                avg_diff = np.mean(np.diff(segment))
                avg_freq = np.mean(segment)

                if avg_freq < min_freq or avg_freq > max_freq:
                    freq_patterns.append(np.nan)  # Частота выходит за пределы диапазона
                elif np.abs(avg_diff) < eps_freq:
                    freq_patterns.append(0)  # Стабильность
                elif avg_diff > eps_freq:
                    freq_patterns.append(1)  # Рост
                else:
                    freq_patterns.append(-1)  # Падение

        # Анализ изменений ширины канала
        bw_patterns = []
        for segment in smoothed_bw_segments:
            if isinstance(segment, float) and np.isnan(segment):
                bw_patterns.append(np.nan)
            else:
                avg_diff = np.mean(np.diff(segment))
                if np.abs(avg_diff) < eps_width:
                    bw_patterns.append(0)  # Стабильность
                elif avg_diff > eps_width:
                    bw_patterns.append(1)  # Увеличение
                else:
                    bw_patterns.append(-1)  # Уменьшение

        # Добавляем паттерны для текущей форманты
        formant_patterns.append(
            (freq_patterns, bw_patterns, dist_patterns[formant_idx] if formant_idx < len(dist_patterns) else []))

    # Возвращаем паттерны и временные сегменты
    return formant_patterns, time_segments

def analyze_formant_patterns4(frequencies, bandwidths, times, formant_ranges,
                              delta_time=1.0,
                              eps_freq=5, eps_width=5,
                              dist=1000, eps_dist=10):
    """
    Анализирует последовательности изменений частот, ширины канала и расстояния между соседними формантами,
    разбитых на секции с учетом временных интервалов.

    Parameters:
    - frequencies: Список списков частот формант (каждый список для одной форманты).
    - bandwidths: Список списков ширины канала формант (каждый список для одной форманты).
    - times: Время в секундах для каждой точки в frequencies и bandwidths.
    - formant_ranges: Словарь диапазонов частот для каждой форманты {форманта: (мин_частота, макс_частота)}.
    - delta_time: Шаг времени для сегментации (например, 1 секунда).
    - eps_freq: Порог для изменения частоты, чтобы считать это изменением.
    - eps_width: Порог для изменения ширины канала.
    - dist: Ожидаемое расстояние между формантами.
    - eps_dist: Диапазон для определения ширины форманты.

    Returns:
    - formant_patterns: Список, содержащий паттерны частоты, ширины канала и расстояний для каждой форманты,
                        а также список временных отрезков для каждого сегмента.
    """

    def segment_and_smooth(data):
        """
        Сегментирует данные по времени и сглаживает их до прямой.

        Parameters:
        - data: Входные данные для сегментации (частоты или ширина канала).

        Returns:
        - Сглаженные значения для этого временного сегмента.
        """
        if len(data) == 0:
            return np.nan

        # Линейная аппроксимация сегмента (сглаживание)
        x = np.arange(len(data))
        slope, intercept, _, _, _ = stats.linregress(x, data)
        smoothed_segment = slope * x + intercept
        return smoothed_segment

    T = times[-1]  # Длительность всего аудио

    all_smoothed_freq_segments = [[] for _ in range(len(frequencies))]
    all_smoothed_bw_segments = [[] for _ in range(len(frequencies))]
    time_segments = []

    current_time = 0
    while current_time < T:
        next_time = current_time + delta_time
        time_segments.append((current_time, next_time))

        for formant_idx in range(len(frequencies)):
            formant_freq = np.array(frequencies[formant_idx])
            formant_bw = np.array(bandwidths[formant_idx])

            valid_indices = (times >= current_time) & (times < next_time) & ~np.isnan(formant_freq) & ~np.isnan(formant_bw)
            valid_freq_segment = formant_freq[valid_indices]
            valid_bw_segment = formant_bw[valid_indices]

            if len(valid_freq_segment) > 0:
                smoothed_freq_segment = segment_and_smooth(valid_freq_segment)
                all_smoothed_freq_segments[formant_idx].append(smoothed_freq_segment)
            else:
                all_smoothed_freq_segments[formant_idx].append(np.nan)

            if len(valid_bw_segment) > 0:
                smoothed_bw_segment = segment_and_smooth(valid_bw_segment)
                all_smoothed_bw_segments[formant_idx].append(smoothed_bw_segment)
            else:
                all_smoothed_bw_segments[formant_idx].append(np.nan)

        current_time = next_time

    dist_patterns = [[] for _ in range(len(frequencies) - 1)]

    for time_segment_idx in range(len(all_smoothed_freq_segments[0])):
        for formant_idx in range(len(frequencies) - 1):
            avg1 = np.mean(all_smoothed_freq_segments[formant_idx][time_segment_idx])
            avg2 = np.mean(all_smoothed_freq_segments[formant_idx + 1][time_segment_idx])

            delta = abs(avg2 - avg1)
            dist_patterns[formant_idx].append(delta)

    formant_patterns = []

    for formant_idx in range(len(frequencies)):
        smoothed_freq_segments = all_smoothed_freq_segments[formant_idx]
        smoothed_bw_segments = all_smoothed_bw_segments[formant_idx]
        min_freq, max_freq = formant_ranges[formant_idx + 1]

        freq_patterns = []
        for segment in smoothed_freq_segments:
            if isinstance(segment, float) and np.isnan(segment):
                freq_patterns.append(np.nan)
            else:
                avg_diff = np.mean(np.diff(segment))
                avg_freq = np.mean(segment)

                if avg_freq < min_freq or avg_freq > max_freq:
                    freq_patterns.append(np.nan)
                else:
                    freq_patterns.append(avg_diff)

        bw_patterns = []
        for segment in smoothed_bw_segments:
            if isinstance(segment, float) and np.isnan(segment):
                bw_patterns.append(np.nan)
            else:
                avg_diff = np.mean(np.diff(segment))
                bw_patterns.append(avg_diff)

        formant_patterns.append(
            (freq_patterns, bw_patterns, dist_patterns[formant_idx] if formant_idx < len(dist_patterns) else []))

    return formant_patterns, time_segments

def simplify_formant_patterns(formant_patterns, time_segments):
    """
    Упрощает паттерны формантов, объединяя последовательные одинаковые паттерны
    и соответствующие временные сегменты.

    Parameters:
    - formant_patterns: Список паттернов для каждой форманты (частота, ширина канала, расстояние).
    - time_segments: Список временных отрезков, соответствующих паттернам.

    Returns:
    - simplified_patterns: Упрощенные паттерны с объединением временных отрезков для каждой форманты.
    """
    simplified_patterns = []

    # Проходим по каждой форманте
    for formant_index in range(3):
        freq_pattern = formant_patterns[formant_index][0]
        bandwidth_pattern = formant_patterns[formant_index][1]
        dist_pattern = formant_patterns[formant_index][2]

        current_freq = None
        current_bw = None
        current_dist = None
        current_time_segment = None

        # Список для упрощенных паттернов текущей форманты
        simplified_current_patterns = []

        for i in range(len(freq_pattern)):
            freq = freq_pattern[i]
            bw = bandwidth_pattern[i]
            dist = dist_pattern[i]
            time_seg = time_segments[i]

            # Если паттерны изменяются, сохраняем их и соответствующий временной отрезок
            if (freq != current_freq) or (bw != current_bw) or (dist != current_dist):
                if current_freq is not None:  # Если это не первый элемент
                    # Добавляем упрощенный паттерн для текущей форманты
                    simplified_current_patterns.append((
                        current_freq,
                        current_bw,
                        current_dist,
                        current_time_segment
                    ))

                # Обновляем текущие значения
                current_freq = freq
                current_bw = bw
                current_dist = dist
                current_time_segment = time_seg  # Сохраняем временной отрезок
            else:
                # Объединяем временные отрезки
                current_time_segment = (current_time_segment[0], time_seg[1])

        # Добавляем последний паттерн
        if current_freq is not None:
            simplified_current_patterns.append((
                current_freq,
                current_bw,
                current_dist,
                current_time_segment
            ))

        # Добавляем упрощенные паттерны текущей форманты в общий список
        simplified_patterns.append(simplified_current_patterns)

    return simplified_patterns


def simplify_formant_patterns2(formant_patterns, time_segments):
    """
    Упрощает паттерны формантов, объединяя последовательные одинаковые паттерны
    только в случае совпадения для всех формант и соответствующие временные сегменты.

    Parameters:
    - formant_patterns: Список паттернов для каждой форманты (частота, ширина канала, дистанция).
    - time_segments: Список временных отрезков, соответствующих паттернам.

    Returns:
    - simplified_patterns: Упрощенные паттерны с объединением временных отрезков для каждой форманты.
    """
    simplified_patterns = []

    # Обходим каждый паттерн (индекс i)
    for i in range(len(formant_patterns[0][0])):  # Предполагается, что у всех формант одинаковое количество паттернов
        current_freqs = []
        current_bws = []
        current_dists = []

        # Вложенный цикл по формантам
        for formant_index in range(3):
            current_freqs.append(formant_patterns[formant_index][0][i])
            current_bws.append(formant_patterns[formant_index][1][i])
            current_dists.append(formant_patterns[formant_index][2][i])

        current_time_segment = time_segments[i]

        # Проверяем, совпадают ли паттерны у всех формант
        if i == 0 or not (
                current_freqs == previous_freqs and current_bws == previous_bws and current_dists == previous_dists):
            # Добавляем новый паттерн, если это не первый элемент или если паттерны отличаются
            if i > 0:  # Если это не первый паттерн, добавляем предыдущий паттерн
                simplified_patterns.append((previous_freqs, previous_bws, previous_dists, previous_time_segment))

            # Обновляем предыдущие значения
            previous_freqs = current_freqs
            previous_bws = current_bws
            previous_dists = current_dists
            previous_time_segment = current_time_segment
        else:
            # Объединяем временные отрезки
            previous_time_segment = (previous_time_segment[0], current_time_segment[1])

    # Добавляем последний паттерн
    if 'previous_freqs' in locals():  # Если у нас есть предыдущие значения
        simplified_patterns.append((previous_freqs, previous_bws, previous_dists, previous_time_segment))

    return simplified_patterns


def print_simplified_patterns(simplified_patterns):
    """
    Выводит упрощенные паттерны формантов в заданном формате.

    Parameters:
    - simplified_patterns: Упрощенные паттерны формантов.
    """
    for formant_index, patterns in enumerate(simplified_patterns):
        freqs = []
        bws = []
        dists = []
        times = []

        for pattern in patterns:
            freqs.append(pattern[0])
            bws.append(pattern[1])
            dists.append(pattern[2])
            times.append(pattern[3])

        print(f"F{formant_index + 1}: частота ({', '.join(map(str, freqs))}), "
              f"ширина канала ({', '.join(map(str, bws))}), "
              f"дистанция ({', '.join(map(str, dists))}), "
              f"время ({', '.join(map(str, times))})")

def classify_phonemes(simplified_patterns, phonems):
    """
    Классифицирует фонемы на основе упрощенных паттернов формантов.

    Parameters:
    - simplified_patterns: Упрощенные паттерны формантов.
    - phonems: Массив фонем, каждая из которых представляет собой
      кортеж (название фонемы, массив паттернов формант).

    Returns:
    - s: Строка, содержащая классифицированные фонемы или пробелы.
    """
    s = ''

    # Обходим каждый набор упрощенных паттернов
    for patterns in simplified_patterns:
        # Извлекаем рисунок для каждой форманты
        F1 = patterns[0]  # (частота, ширина канала, дистанция)
        F2 = patterns[1]
        F3 = patterns[2]

        # Расчет значений y1, y2, y3
        y1 = 100 * F1[2] + 10 * F2[2] + F3[2]  # дистанция
        y2 = 100 * F1[0] + 10 * F2[0] + F3[0]  # частота
        y3 = 100 * F1[1] + 10 * F2[1] + F3[1]  # ширина канала

        # Общий расчет v
        v_simplified_patterns = 100 * y1 + 10 * y2 + y3

        # Инициализируем переменную для максимального v среди фонем
        max_v_phonem = 0
        matched_phonem = None

        # Обходим каждую фонему в phonems
        for phonem_name, phonem_patterns in phonems:
            F1_phonem = phonem_patterns[0]
            F2_phonem = phonem_patterns[1]
            F3_phonem = phonem_patterns[2]

            # Расчет y1, y2, y3 для фонемы
            y1_phonem = 100 * F1_phonem[2] + 10 * F2_phonem[2] + F3_phonem[2]
            y2_phonem = 100 * F1_phonem[0] + 10 * F2_phonem[0] + F3_phonem[0]
            y3_phonem = 100 * F1_phonem[1] + 10 * F2_phonem[1] + F3_phonem[1]

            # Общий расчет v для фонемы
            v_phonem = 100 * y1_phonem + 10 * y2_phonem + y3_phonem

            # Обновляем максимальное значение v фонемы
            if v_phonem > max_v_phonem:
                max_v_phonem = v_phonem
                matched_phonem = phonem_name

        # Находим процент схожести
        if max_v_phonem > 0:  # Избегаем деления на ноль
            pr = v_simplified_patterns / max_v_phonem
        else:
            pr = 0

        # Добавляем соответствующую фонему или пробел
        if pr >= 0.8:
            s += matched_phonem
        else:
            s += ' '

    return s.strip()  # Возвращаем строку без лишних пробелов


def compare_patterns(current, phonema):

    y1 = current[0][0] * 100 + current[1][0] * 10 + current[2][0]
    y2 = current[0][1] * 100 + current[1][1] * 10 + current[2][1]
    y3 = current[0][2] * 100 + current[1][2] * 10 + current[2][2]
    v1 = y3*100 + y1*10 + y2

    y1 = phonema[1][0][0] * 100 + phonema[1][1][0] * 10 + phonema[1][2][0]
    y2 = phonema[1][0][1] * 100 + phonema[1][1][1] * 10 + phonema[1][2][1]
    y3 = phonema[1][0][2] * 100 + phonema[1][1][2] * 10 + phonema[1][2][2]
    v2 = y3*100 + y1*10 + y2

    if v2 == 0:
        pr = abs(v1 - v2)
    else:
        pr = v1 / v2

    return (pr > 0.80) and (pr < 1.2)


def plot_formant_distance_dynamics(formant_patterns, time_segments):
    """
    Строит график изменения расстояний между соседними формантами на основе результатов анализа.

    Parameters:
    - formant_patterns: Список, содержащий паттерны частоты, ширины канала и расстояний для каждой форманты.
    - time_segments: Список временных отрезков для каждого сегмента.
    """

    # Определяем количество формант
    num_formants = len(formant_patterns)

    # Получаем количество временных сегментов
    num_segments = len(time_segments)

    # Список для хранения значений расстояний между формантами для каждого временного сегмента
    distances = [[] for _ in range(num_formants - 1)]

    # Проходим по сегментам и извлекаем значения расстояний между формантами
    for seg_index in range(num_segments):
        for i in range(num_formants - 1):
            # Добавляем расстояние между формантами (если оно не является NaN)
            distance_value = formant_patterns[i][2][seg_index]
            if not isinstance(distance_value, float) or not np.isnan(distance_value):
                distances[i].append(distance_value)
            else:
                distances[i].append(np.nan)  # Заполняем NaN для пропущенных значений

    # Создаем график
    plt.figure(figsize=(12, 6))

    # Устанавливаем цвета для линий
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan']

    # Построение графика для каждой пары соседних формант
    for i in range(num_formants - 1):
        # Извлекаем временные метки
        time_values = [segment[0] for segment in time_segments]  # Начало каждого сегмента
        plt.plot(time_values, distances[i], color=colors[i % len(colors)], label=f'Formant {i+1} - Formant {i+2}')

    # Настройка графика
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance between Formants')
    plt.title('Dynamics of Distance between Formants over Time')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()


import numpy as np


def calculate_formant_dynamics(formant_freqs, times, formant_bandwidths, formant_ranges, delta_time=0.05):
    """
    Рассчитывает динамику отклонения частоты и средней ширины канала для каждой форманты по сегментам времени.

    Parameters:
    - formant_freqs: Список списков частот формант.
    - times: Время в секундах для каждой точки в formant_freqs и formant_bandwidths.
    - formant_bandwidths: Список списков ширины канала для каждой форманты.
    - formant_ranges: Словарь диапазонов частот для каждой форманты {форманта: (мин_частота, макс_частота)}.
    - delta_time: Длительность временного сегмента для анализа.

    Returns:
    - formant_dynamics: Список списков, где каждый вложенный список содержит пары (delta_freq, bw_avg)
                        для каждого временного сегмента и каждой форманты.
    - time_segments: Список временных сегментов, соответствующих каждому промежутку времени.
    """

    # Длительность сигнала
    T = times[-1]

    # Списки для хранения результатов
    formant_dynamics = [[] for _ in range(len(formant_freqs))]
    time_segments = []

    # Разбиваем на временные сегменты
    current_time = 0
    while current_time < T:
        next_time = current_time + delta_time
        time_segments.append((current_time, next_time))

        # Проходим по каждой форманте и вычисляем средние значения
        for formant_idx, (freq_series, bw_series) in enumerate(zip(formant_freqs, formant_bandwidths)):
            # Извлекаем значения для текущего временного сегмента и отбрасываем NaN
            valid_indices = (
                    (times >= current_time) &
                    (times < next_time) &
                    ~np.isnan(freq_series) &
                    ~np.isnan(bw_series)
            )
            valid_freqs = np.array(freq_series)[valid_indices]
            valid_bandwidths = np.array(bw_series)[valid_indices]

            # Вычисляем среднюю частоту и ширину канала, если сегмент не пуст
            if len(valid_freqs) > 0 and len(valid_bandwidths) > 0:
                freq_avg = np.mean(valid_freqs)
                bw_avg = np.mean(valid_bandwidths)

                # Средняя частота диапазона форманты
                min_freq, max_freq = formant_ranges[formant_idx + 1]
                freq_center = (min_freq + max_freq) / 2

                # Отклонение частоты от центральной частоты диапазона
                delta_freq = freq_avg - freq_center

                # Сохраняем пару (delta_freq, bw_avg) для текущего сегмента
                formant_dynamics[formant_idx].append((delta_freq, bw_avg))
            else:
                # Заполняем NaN, если нет данных для сегмента
                formant_dynamics[formant_idx].append((np.nan, np.nan))

        current_time = next_time

    return formant_dynamics, time_segments


def plot_formant_dynamics(formant_dynamics, time_segments):
    """
    Визуализирует динамику отклонения частоты и ширины канала для первых трех формант по времени.

    Parameters:
    - formant_dynamics: Список списков пар (delta_freq, bw_avg) для каждой форманты.
    - time_segments: Список временных сегментов, соответствующих каждому промежутку времени.
    """

    # Подготовка данных для оси X - временные метки сегментов
    time_values = [seg[0] for seg in time_segments]

    # Настройка цветов для первых трех формант
    colors = ['b', 'g', 'r']
    labels = ['Formant 1', 'Formant 2', 'Formant 3']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Построение графиков для отклонения частоты
    for i in range(3):
        delta_freq_values = [delta_freq for delta_freq, _ in formant_dynamics[i]]
        ax1.plot(time_values, delta_freq_values, color=colors[i], label=labels[i])

    ax1.set_ylabel('Delta Frequency (Hz)')
    ax1.set_title('Dynamics of Formant Frequency and Bandwidth Over Time')
    ax1.legend()
    ax1.grid(True)

    # Построение графиков для ширины канала
    for i in range(3):
        bw_avg_values = [bw_avg for _, bw_avg in formant_dynamics[i]]
        ax2.plot(time_values, bw_avg_values, color=colors[i], label=labels[i])

    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Bandwidth (Hz)')
    ax2.grid(True)

    plt.show()


def generate_varying_bandwidth_signal(delta_time, start_freq, end_freq, start_bw, end_bw, sample_rate=44100):
    """
    Генерирует аудиосигнал с периодической функцией, которая изменяется по частоте и ширине канала.

    Parameters:
    - delta_time: float, длительность временного отрезка в секундах.
    - start_freq: float, начальная частота (Гц).
    - end_freq: float, конечная частота (Гц).
    - start_bw: float, начальная ширина канала.
    - end_bw: float, конечная ширина канала.
    - sample_rate: int, частота дискретизации для аудиосигнала, по умолчанию 44100 Гц.

    Returns:
    - audio_signal: numpy array, массив аудиосигнала.
    """
    # Создаем временную ось
    t = np.linspace(0, delta_time, int(sample_rate * delta_time), endpoint=False)

    # Линейно изменяющаяся частота от начальной до конечной на временном интервале
    freq_t = np.linspace(start_freq, end_freq, len(t))

    # Линейно изменяющаяся ширина канала (амплитуда) от начальной до конечной на временном интервале
    bw_t = np.linspace(start_bw, end_bw, len(t))

    # Генерация периодического сигнала с изменяющейся частотой и амплитудой
    phase = 2 * np.pi * np.cumsum(freq_t) / sample_rate
    audio_signal = bw_t * np.sin(phase)

    # Нормализация для допустимых значений аудио
    audio_signal = (audio_signal / np.max(np.abs(audio_signal)) * 32767).astype(np.int16)

    return audio_signal


import numpy as np


def generate_formant_dynamics_sound(formant_dynamics, delta_time, sample_rate=44100):
    """
    Генерирует аудиосигнал на основе динамики отклонения частот и ширины каналов для каждой форманты.

    Parameters:
    - formant_dynamics: Список списков, содержащих пары (delta_freq, bw_avg) для каждой форманты и временного сегмента.
    - delta_time: Длительность каждого временного сегмента в секундах.
    - sample_rate: Частота дискретизации для создаваемого аудиосигнала.

    Returns:
    - final_audio: Итоговый аудиосигнал, объединенный для всех формант.
    """
    num_segments = len(formant_dynamics[0])
    final_audio = np.zeros(int(delta_time * sample_rate * num_segments), dtype=np.float32)

    # Проход по каждому временному сегменту
    for seg_index in range(num_segments - 1):
        segment_audio = np.zeros(int(delta_time * sample_rate), dtype=np.float32)

        # Проход по каждой форманте
        for formant_idx, formant_values in enumerate(formant_dynamics):
            # Извлечение текущих и следующих значений
            current_freq, current_bw = formant_values[seg_index]
            next_freq, next_bw = formant_values[seg_index + 1]

            # Пропускаем, если в данных NaN
            if np.isnan(current_freq) or np.isnan(current_bw) or np.isnan(next_freq) or np.isnan(next_bw):
                continue

            # Генерация сигнала для текущей форманты
            formant_audio = generate_varying_bandwidth_signal(
                delta_time,
                start_freq=current_freq, end_freq=next_freq,
                start_bw=current_bw, end_bw=next_bw,
                sample_rate=sample_rate
            )

            segment_audio += formant_audio.astype(np.float32)

        # Нормализация и добавление к итоговому звуку
        segment_audio = (segment_audio / np.max(np.abs(segment_audio)) * 0.8).astype(
            np.float32)  # Нормализация для избежания клиппинга
        start_sample = seg_index * int(delta_time * sample_rate)
        end_sample = start_sample + len(segment_audio)
        final_audio[start_sample:end_sample] += segment_audio

    # Нормализуем общий звук
    # final_audio = (final_audio / np.max(np.abs(final_audio)) * 32767).astype(np.int16)
    final_audio = final_audio / np.nanmax(np.abs(final_audio)) * 32767
    final_audio = final_audio.astype(np.int16)

    return final_audio
