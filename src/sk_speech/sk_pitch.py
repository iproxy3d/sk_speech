import numpy as np
import librosa
from scipy.fft import fft, fftfreq
from scipy.signal import medfilt
from scipy.stats import linregress
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter1d
from scipy import stats
import scipy.signal
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import parselmouth as pm
from parselmouth.praat import call
from pydub import AudioSegment
# import rubberband as rb
import soundfile as sf
# import penn
from . import sk_filters as fl
from . import sk_noise as ns


def get_pitch_with_retries(sound, time_step=0.01, pitch_from=75, pitch_to=500):
    """
    Пытается вычислить pitch объекта sound, увеличивая time_step на 10 при каждом исключении,
    пока ошибка не исчезнет или time_step не станет больше 1.

    Параметры:
        sound (parselmouth.Sound): Звуковой объект для анализа.
        time_step (float): Начальное значение для time_step (шаг по времени).
        pitch_from (float): Минимальная частота pitch.
        pitch_to (float): Максимальная частота pitch.

    Возвращает:
        parselmouth.Pitch или None: Объект Pitch при успешном анализе или None при неудаче.
    """
    while time_step <= 1:
        try:
            pitch = sound.to_pitch(time_step=time_step, pitch_floor=pitch_from, pitch_ceiling=pitch_to)
            return pitch  # Успешно получен pitch, возвращаем результат
        except pm.PraatError as e:
            # print(f"Ошибка: {e}. Увеличиваем time_step и повторяем попытку...")
            time_step *= 10  # Увеличиваем time_step в 10 раз

    # Если вышли из цикла и не смогли получить pitch
    # print("Не удалось получить pitch: достигнут максимальный time_step > 1.")
    return None

def extract_f0(y, sr, pitch_from=75, pitch_to=600):
    """
    Извлекает основной тон (f0) из аудио сигнала.

    Args:
    y: ndarray
        Аудио сигнал.
    sr: int
        Частота дискретизации.

    Returns:
    f0: float
        Основной тон (f0).
    """
    sound = pm.Sound(y, sr)
    pitch = call(sound, "To Pitch", 0.0, pitch_from, pitch_to)
    f0 = call(pitch, "Get mean", 0, 0, "Hertz")
    return f0

def extract_f0_values(y, sr, pitch_from=75, pitch_to=600):
    sound = pm.Sound(y, sr)
    pitch = call(sound, "To Pitch", 0.0, pitch_from, pitch_to)
    f0_values = pitch.selected_array['frequency']
    return f0_values

def extract_f0_segment(y, sr, pitch_from=75, pitch_to=600):
    # Создание объекта Sound из аудиосигнала
    sound = pm.Sound(y, sr)

    # Извлечение частоты основного тона
    pitch = get_pitch_with_retries(sound, time_step=0.01, pitch_from=pitch_from, pitch_to=pitch_to)
    if pitch is None:
        return None
    pitch_values = pitch.selected_array['frequency']

    pitch_values = remove_short_sequences(pitch_values)
    # Определение сегментов с основным тоном
    voiced_segments = ~np.isnan(pitch_values)
    pitch_values = pitch_values[voiced_segments]
    pitch_values = pitch_values[pitch_values > 0]

    return pitch_values

def extract_f0_min_max_avg(y, sr):
    pitch_values = extract_f0_segment(y, sr)

    if len(pitch_values) == 0 or np.all(np.isnan(pitch_values)):
        return 0, 0, 0

    return np.min(pitch_values), np.max(pitch_values), np.mean(pitch_values)

def remove_short_sequences_mask(f0, min_length=15):
    """
    Возвращает маску для значений F0, где длинные последовательности помечены как True, а короткие как False.

    :param f0: Массив значений F0 с NaN.
    :param min_length: Минимальная длина последовательности для сохранения.
    :return: Булевый массив той же длины, что и f0, с пометками True для длинных последовательностей.
    """
    mask = np.full(len(f0), False, dtype=bool)
    current_sequence = []
    old_value = np.nan
    start_index = None

    for i, value in enumerate(f0):
        if not np.isnan(value) and value > 0 and (np.isnan(old_value) or (old_value > 0 and abs(old_value - value) < 50)):
            if start_index is None:
                start_index = i  # Запоминаем индекс начала последовательности
            current_sequence.append(value)
            old_value = value
        else:
            if len(current_sequence) >= min_length and start_index is not None:
                mask[start_index:i] = True  # Помечаем всю последовательность как True
            current_sequence = []
            start_index = None
        if not np.isnan(value) and value > 0:
            old_value = value

    # Проверяем последнюю последовательность
    if len(current_sequence) >= min_length and start_index is not None:
        mask[start_index:] = True

    return mask

def filter_intensity_by_voiced_times(intensity_values, intensity_times, voiced_times):
    # Создание интерполятора для интенсивности
    interp = interp1d(intensity_times, intensity_values, kind='linear', fill_value='extrapolate')

    # Интерполяция значений интенсивности для временных меток voiced_times
    interpolated_intensity_values = interp(voiced_times)

    # Возвращаем интерполированные значения интенсивности и времена
    return interpolated_intensity_values, voiced_times

def extract_f0_voiced(y, sr, speech=True, pitch_from=75, pitch_to=600, time_step=0.01):
    # Создание объекта Sound из аудиосигнала
    sound = pm.Sound(y, sr)

    # Извлечение частоты основного тона
    pitch = get_pitch_with_retries(sound, time_step=time_step, pitch_from=pitch_from, pitch_to=pitch_to)
    if pitch is None:
        return None, None, None, None, None, None, None
    pitch_values = pitch.selected_array['frequency']
    voiced_times = pitch.xs()

    # Получение интенсивности звука
    try:
        intensity = sound.to_intensity()
        intensity_values = intensity.values.flatten()
        intensity_times = intensity.xs()
    except pm.PraatError as e:
        return None, None, None, None, None, None, None

    if speech:
        mask = remove_short_sequences_mask(pitch_values)
        pitch_values = pitch_values[mask]
        voiced_times = voiced_times[mask]

    # Определение сегментов с основным тоном
    voiced_segments = ~np.isnan(pitch_values)

    # Вычисление времени для озвученных сегментов
    voiced_times = voiced_times[voiced_segments]
    pitch_values = pitch_values[voiced_segments]

    voiced_times = voiced_times[pitch_values > 0]
    pitch_values = pitch_values[pitch_values > 0]

    intensity_values, intensity_times = filter_intensity_by_voiced_times(intensity_values, intensity_times,
                                                                         voiced_times)

    # Создание Manipulation объекта
    manipulation = call(sound, "To Manipulation", 0.001, pitch_from, pitch_to)

    # Получение PitchTier из Pitch
    pitch_tier = call(pitch, "Down to PitchTier")

    return pitch_values, voiced_times, intensity_values, intensity_times, sound, manipulation, pitch_tier


def calculate_pitch_frequency(y):
    # Извлечение основного тона (F0) с помощью метода "probabilistic YIN"
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    # Извлечение ненулевых значений основного тона (только озвученные кадры)
    f0_voiced = f0[voiced_flag]

    # Средняя частота основного тона
    avg_pitch_frequency = np.mean(f0_voiced) if len(f0_voiced) > 0 else 0

    return avg_pitch_frequency


def extract_f0_penn(y, sr):
    # Here we'll use a 10 millisecond hopsize
    hopsize = .01

    # Provide a sensible frequency range given your domain and model
    fmin = 30.
    fmax = 1000.

    # Choose a gpu index to use for inference. Set to None to use cpu.
    gpu = 0

    # If you are using a gpu, pick a batch size that doesn't cause memory errors
    # on your gpu
    batch_size = 2048

    # Select a checkpoint to use for inference. Selecting None will
    # download and use FCNF0++ pretrained on MDB-stem-synth and PTDB
    checkpoint = None

    # Centers frames at hopsize / 2, 3 * hopsize / 2, 5 * hopsize / 2, ...
    center = 'half-hop'

    # (Optional) Linearly interpolate unvoiced regions below periodicity threshold
    interp_unvoiced_at = .065

    # Infer pitch and periodicity
    pitch, periodicity = penn.from_audio(
        y,
        sr,
        hopsize=hopsize,
        fmin=fmin,
        fmax=fmax,
        checkpoint=checkpoint,
        batch_size=batch_size,
        center=center,
        interp_unvoiced_at=interp_unvoiced_at,
        gpu=gpu)

    return pitch

def remove_short_sequences(f0, min_length=15):
    """
    Убирает короткие последовательности значений F0.

    :param f0: Массив значений F0 с NaN.
    :param min_length: Минимальная длина последовательности для сохранения.
    :return: Массив значений F0 без коротких последовательностей.
    """
    valid_f0 = []
    current_sequence = []
    old_value = np.nan

    for value in f0:
        if not np.isnan(value) and value > 0 and (
                np.isnan(old_value) or (old_value > 0 and abs(old_value - value < 50))):
        # if not np.isnan(value) and value > 0:
            current_sequence.append(value)
            old_value = value
        else:
            if len(current_sequence) >= min_length:
                valid_f0.extend(current_sequence)
            current_sequence = []
        if not np.isnan(value) and value > 0:
            old_value = value

    # Проверяем последнюю последовательность
    if len(current_sequence) >= min_length:
        valid_f0.extend(current_sequence)

    return np.array(valid_f0)

def calculate_pitch_bandwidth(y, sr, pitch=None):
    if pitch:
        pitch_values = pitch["frequencies"]
    else:
        pitch_values = extract_f0_segment(y, sr)

    # Рассчитайте ширину полосы пропускания
    if len(pitch_values) > 1:
        pitch_bandwidth = np.max(pitch_values) - np.min(pitch_values)
    else:
        pitch_bandwidth = 0

    return pitch_bandwidth

def calculate_pitch_bandwidth_welch(y, sr, pitch=None):
    """Estimate F0-band width with a Welch spectrum.

    The method estimates the significant frequency range around average F0
    using a band-pass filter and a Welch power spectrum.
    """
    # Средняя частота основного тона
    avg_f0 = extract_f0(y, sr)

    # Применяем полосовой фильтр вокруг средней частоты основного тона
    bandwidth = 300
    if np.isnan(avg_f0) or avg_f0 <= 0:
        return 0

    b, a = scipy.signal.butter(2, [max(avg_f0 - bandwidth, 1), avg_f0 + bandwidth], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, y)

    # Рассчитываем спектр мощности отфильтрованного сигнала
    f, Pxx = scipy.signal.welch(filtered_signal, sr, nperseg=2048)

    # Определяем полосу пропускания на основе энергии спектра
    threshold = 0.5 * np.max(Pxx)  # Порог на уровне 50% от максимальной энергии
    significant_frequencies = f[Pxx > threshold]

    if len(significant_frequencies) == 0:
        return 0  # Если нет значительных частот, возвращаем 0

    # Полоса пропускания определяется как разница между максимальной и минимальной значительной частотой
    bandwidth = significant_frequencies[-1] - significant_frequencies[0]

    return bandwidth

def calculate_pitch_bandwidth2(y, sr):
    # Извлечение основного тона (F0) с помощью метода "probabilistic YIN"
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax)

    # Извлечение ненулевых значений основного тона (только озвученные кадры)
    f0_voiced = f0[voiced_flag]

    if len(f0_voiced) == 0:
        return 0  # Если нет озвученных кадров, возвращаем 0

    # Средняя частота основного тона
    avg_f0 = np.mean(f0_voiced)

    # Применяем полосовой фильтр вокруг средней частоты основного тона
    bandwidth = 300
    if np.isnan(avg_f0) or avg_f0 <= 0:
        return 0

    b, a = scipy.signal.butter(2, [max(avg_f0 - bandwidth, 1), avg_f0 + bandwidth], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, y)

    # Рассчитываем спектр мощности отфильтрованного сигнала
    f, Pxx = scipy.signal.welch(filtered_signal, sr, nperseg=2048)

    # Определяем полосу пропускания на основе энергии спектра
    threshold = 0.5 * np.max(Pxx)  # Порог на уровне 50% от максимальной энергии
    significant_frequencies = f[Pxx > threshold]

    if len(significant_frequencies) == 0:
        return 0  # Если нет значительных частот, возвращаем 0

    # Полоса пропускания определяется как разница между максимальной и минимальной значительной частотой
    bandwidth = significant_frequencies[-1] - significant_frequencies[0]

    return bandwidth

def calculate_pitch_energy(y, sr, pitch=None):
    """
    Рассчитывает среднюю энергию основного тона в аудиосигнале с использованием Parselmouth.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :return: Средняя энергия основного тона.
    """
    if pitch:
        pitch_values = pitch["frequencies"]
    else:
        # Создание объекта Sound из аудиосигнала
        sound = pm.Sound(y, sr)

        # Извлечение основного тона и интенсивности с одинаковым шагом времени
        pitch = get_pitch_with_retries(sound, time_step=0.01)
        if pitch is None:
            return None
        pitch_values = pitch.selected_array['frequency']

    bandwidth = calculate_pitch_bandwidth(y, sr, pitch) / 2
    if not (bandwidth > 0):
        return 0

    # Фильтруем ненулевые значения частоты основного тона
    pitch_energy = []
    for pitch_value in pitch_values:
        if pitch_value > 0:  # Учитываем только ненулевые значения основного тона
            # Применяем полосовой фильтр для выделения основного тона
            b, a = scipy.signal.butter(2, [max(pitch_value - bandwidth, 1), pitch_value + bandwidth], btype='band', fs=sr)
            filtered_signal = scipy.signal.lfilter(b, a, y)
            energy = np.sum(filtered_signal ** 2)  # Энергия пропорциональна квадрату амплитуды
            pitch_energy.append(energy)

    # Средняя энергия основного тона
    avg_pitch_energy = np.mean(pitch_energy) if pitch_energy else 0

    return avg_pitch_energy

def change_pitch_energy2(y, sr, factor, pitch_range=(75, 600)):
    if factor == 1.0:
        return y, sr

    # Загрузка аудиофайла
    sound = pm.Sound(y, sr)

    # Создание Manipulation объекта
    manipulation = call(sound, "To Manipulation", 0.001, pitch_range[0], pitch_range[1])

    # Получение PitchTier из Pitch
    pitch_tier = call(manipulation, "Extract pitch tier")

    # Увеличение частот в PitchTier
    call(pitch_tier, "Multiply frequencies", sound.xmin, sound.xmax, factor)

    # Замена PitchTier в Manipulation объекте
    call([pitch_tier, manipulation], "Replace pitch tier")

    # Ресинтез звука
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    # Преобразование звука в массив значений
    resynthesized_signal = resynthesized_sound.values[0]

    return resynthesized_signal, int(sound.sampling_frequency)

def change_pitch_energy3(y, sr, factor, pitch_range=(75, 600)):
    if factor == 1.0:
        return y, sr

    # Загрузка аудиофайла
    sound = pm.Sound(y, sr)

    # Получение основного тона (pitch)
    pitch = call(sound, "To Pitch", 0.0, pitch_range[0], pitch_range[1])

    # Создание Manipulation объекта
    manipulation = call(sound, "To Manipulation", 0.001, pitch_range[0], pitch_range[1])

    # Получение PitchTier из Pitch
    pitch_tier = call(pitch, "Down to PitchTier")

    # Увеличение частот в PitchTier
    start_time = call(pitch_tier, "Get start time")
    end_time = call(pitch_tier, "Get end time")
    call(pitch_tier, "Multiply frequencies", start_time, end_time, factor)

    # Коррекция частот на выход за пределы диапазона
    num_points = call(pitch_tier, "Get number of points")
    for i in range(1, num_points + 1):
        time = call(pitch_tier, "Get time from index", i)
        freq = call(pitch_tier, "Get value at time", time)

        # Если частота выходит за пределы диапазона, корректируем её
        if freq > pitch_range[1]:
            freq = pitch_range[1]
        elif freq < pitch_range[0]:
            freq = pitch_range[0]

        # Обновляем точку в PitchTier
        call(pitch_tier, "Remove point near", time)
        call(pitch_tier, "Add point", time, freq)

    # Замена PitchTier в Manipulation объекте
    call([manipulation, pitch_tier], "Replace pitch tier")

    # Ресинтез звука
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    # Преобразование звука в массив значений
    resynthesized_signal = resynthesized_sound.values[0]

    return resynthesized_signal, int(sound.sampling_frequency)

def change_pitch_energy(y, sr, factor, pitch_range=(75, 600), speech=True, pitch_from=75, pitch_to=600):
    # if factor == 1.0:
    #     return y, sr

    pitch_values = []
    if speech:
        pitch_values, _, _, _, sound, manipulation, pitch_tier = extract_f0_voiced(y, sr, speech=True,
                                                                                   pitch_from=pitch_from,
                                                                                   pitch_to=pitch_to)

    if len(pitch_values) == 0:
        pitch_values, _, _, _, sound, manipulation, pitch_tier = extract_f0_voiced(y, sr, speech=False,
                                                                                   pitch_from=pitch_from,
                                                                                   pitch_to=pitch_to)

    # # Загрузка аудиофайла
    # sound = pm.Sound(y, sr)
    #
    # # Получение основного тона (pitch)
    # pitch = call(sound, "To Pitch", 0.0, pitch_range[0], pitch_range[1])
    #
    # # Создание Manipulation объекта
    # manipulation = call(sound, "To Manipulation", 0.001, pitch_range[0], pitch_range[1])
    #
    # # Получение PitchTier из Pitch
    # pitch_tier = call(pitch, "Down to PitchTier")
    # pitch_tier = call(manipulation, "Extract pitch tier")

    # Увеличение частот в PitchTier
    start_time = call(pitch_tier, "Get start time")
    end_time = call(pitch_tier, "Get end time")
    call(pitch_tier, "Multiply frequencies", start_time, end_time, factor)

    # Извлечение частот из PitchTier для анализа
    num_points = call(pitch_tier, "Get number of points")
    # pitch_values = []
    # for i in range(1, num_points + 1):
    #     time = call(pitch_tier, "Get time from index", i)
    #     freq = call(pitch_tier, "Get value at time", time)
    #     pitch_values.append(freq)

    # Расчет средней частоты и границ
    pitch_values = np.array(pitch_values)
    pitch_mean = np.mean(pitch_values)
    freq_max = np.max(pitch_values)
    freq_min = np.min(pitch_values)

    # Определение коэффициентов для корректировки диапазона
    k_max = (freq_max - pitch_mean) / (pitch_range[1] - pitch_mean)
    k_min = (pitch_mean - freq_min) / (pitch_mean - pitch_range[0])
    k = max(k_max, k_min)

    if k > 1:
        # Корректируем ширину частотного диапазона
        for i in range(1, num_points + 1):
            time = call(pitch_tier, "Get time from index", i)
            freq = call(pitch_tier, "Get value at time", time)

            # Сжатие частотного диапазона относительно средней частоты
            new_freq = (freq - pitch_mean) / k + pitch_mean

            # Обновляем точку в PitchTier
            call(pitch_tier, "Remove point near", time)
            call(pitch_tier, "Add point", time, new_freq)

    # Замена PitchTier в Manipulation объекте
    call([manipulation, pitch_tier], "Replace pitch tier")

    # Ресинтез звука
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    # Преобразование звука в массив значений
    resynthesized_signal = resynthesized_sound.values[0]

    return resynthesized_signal, int(sound.sampling_frequency)


def calculate_pitch_intensity(y, sr, only_speech=False, shift=True, pitch=None):
    """Return Praat broadband intensity values aligned with pitch metadata.

    This function does not isolate energy of the F0 harmonic; it estimates broadband intensity
    and can optionally retain only time regions where F0 is voiced.  Values
    are relative for ordinary digital recordings, not calibrated dB SPL.
    """
    if pitch:
        pitch_values = pitch["frequencies"]
        pitch_times = pitch["voiced_times"]
        intensity_values = pitch["intensity"]
        intensity_times = pitch["intensity_times"]
    else:
        # Загрузка аудиофайла
        sound = pm.Sound(y, sr)

        # Получение основного тона (pitch)
        pitch = get_pitch_with_retries(sound)
        if pitch is None:
            return None
        pitch_values = pitch.selected_array['frequency']
        pitch_times = pitch.xs()

        # Получение интенсивности звука
        intensity = sound.to_intensity()
        intensity_values = intensity.values.flatten()
        intensity_times = intensity.xs()

    if only_speech:
        # Интерполяция значений pitch до временных меток интенсивности
        interpolated_pitch_values = np.interp(intensity_times, pitch_times, pitch_values)

        # Маска для выбора только тех интенсивностей, где есть pitch
        mask = interpolated_pitch_values > 0
        pitch_intensity_values = intensity_values[mask]

        intensity_threshold = 50
        voiced_frames = pitch_intensity_values > intensity_threshold
        intensity_values = pitch_intensity_values[voiced_frames]

    return intensity_values


def calculate_pitch_intensity2(y, sr, f0_min=80, f0_max=300, frame_length=2048, hop_length=512, only_speech=False, shift=True):
    """
    Рассчитывает интенсивность основного тона в аудиосигнале.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param f0_min: Минимальная частота основного тона (в Гц).
    :param f0_max: Максимальная частота основного тона (в Гц).
    :param frame_length: Длина фрейма для анализа.
    :param hop_length: Шаг между фреймами.
    :return: Массив интенсивностей основного тона.
    """
    # Рассчитаем основной тон
    f0, voiced_flag, _ = librosa.pyin(y, fmin=f0_min, fmax=f0_max, frame_length=frame_length, hop_length=hop_length)

    # Рассчитаем интенсивность по фреймам
    power = np.abs(librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)) ** 2
    intensity_db = 10 * np.log10(power + np.finfo(float).eps)

    if only_speech:
        # Проверка на правильный размер
        if len(voiced_flag) != len(intensity_db[0]):
            voiced_flag = voiced_flag[:len(intensity_db[0])]

        # Интенсивность основного тона для озвученных фрагментов
        voiced_intensity_db = intensity_db[0][voiced_flag]

        # Получение интенсивности для ненулевых значений основного тона
        pitch_intensity = voiced_intensity_db.copy()
        pitch_intensity[f0[voiced_flag] == 0] = 0  # Установка интенсивности в 0 для неозвученных фреймов

        if pitch_intensity.size == 0:
            return np.array([])

    else:
        voiced_intensity_db = intensity_db[0]

    # Сдвиг интенсивности, чтобы минимальное значение было равно 0
    if shift:
        voiced_intensity_db -= np.min(voiced_intensity_db)

    return voiced_intensity_db

def calculate_pitch_intensity_avg(y, sr, pitch):
    # Рассчитываем интенсивность с учетом озвученных фрагментов
    intensity_db = calculate_pitch_intensity(y, sr, only_speech=True, pitch=pitch)
    if intensity_db.size == 0:
        return False

    avg_pitch_intensity = np.mean(intensity_db) if len(intensity_db) > 0 else 0
    return avg_pitch_intensity

def calculate_intensity_scream(y, sr, frame_length=2048, hop_length=512):
    """
    Рассчитывает интенсивность речи в аудиосигнале в децибелах.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param frame_length: Размер окна для анализа.
    :param hop_length: Шаг между окнами.
    :return: Массив интенсивностей в децибелах.
    """
    # Рассчитываем RMS
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)
    # Конвертируем RMS в децибелы
    intensity_db = 20 * np.log10(rms + np.finfo(float).eps)  # dB amplitude from RMS
    return intensity_db.flatten()

def calculate_total_intensity(y, frame_length=2048, hop_length=512):
    """
    Рассчитывает общую интенсивность аудио сигнала.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param frame_length: Длина окна для анализа.
    :param hop_length: Шаг между окнами.
    :return: Общая интенсивность аудио.
    """
    power = np.abs(librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)) ** 2
    intensity_db = 10 * np.log10(power + np.finfo(float).eps)

    intensity_db -= np.min(intensity_db)

    return intensity_db[0]

def calculate_pitch_amplitude(signal, sr, pitch=None):
    if pitch:
        f0_min = np.nanmin(pitch["frequencies"])
        f0_max = np.nanmax(pitch["frequencies"])
        avg_pitch = np.nanmean(pitch["frequencies"])
    else:
        # signal = normalize_audio(signal)
        f0_min, f0_max, avg_pitch = extract_f0_min_max_avg(signal, sr)

    if avg_pitch == 0:
        return 0

    # Полосовой фильтр вокруг средней частоты pitch
    b, a = scipy.signal.butter(2, [max(f0_min, 1), f0_max], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Рассчитываем энергию отфильтрованного сигнала
    pitch_energy = np.sum(filtered_signal ** 2)

    # Средняя амплитуда pitch
    avg_pitch_amplitude = np.sqrt(pitch_energy / len(filtered_signal))

    # Преобразование средней амплитуды в dB
    avg_pitch_amplitude_db = 20 * np.log10(avg_pitch_amplitude)

    return avg_pitch_amplitude_db

def calculate_pitch_amplitude2(signal, sr):
    # signal = normalize_audio(signal)
    avg_pitch = extract_f0(signal, sr)

    if avg_pitch == 0:
        return 0

    # Полосовой фильтр вокруг средней частоты pitch
    pitch_bandwidth = calculate_pitch_bandwidth(signal, sr)
    b, a = scipy.signal.butter(2, [max(avg_pitch - pitch_bandwidth, 1), avg_pitch + pitch_bandwidth], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Рассчитываем энергию отфильтрованного сигнала
    pitch_energy = np.sum(filtered_signal ** 2)

    # Средняя амплитуда pitch
    avg_pitch_amplitude = np.sqrt(pitch_energy / len(filtered_signal))

    # Преобразование средней амплитуды в dB
    avg_pitch_amplitude_db = 20 * np.log10(avg_pitch_amplitude)

    return avg_pitch_amplitude_db


def extract_tone(y, sr, pitch, window_size_ms=10):
    """
    Извлекает основной тон из сигнала.

    :param y: Входной сигнал (массив значений)
    :param sr: Частота дискретизации (Гц)
    :param pitch: Объект Pitch, содержащий информацию о тональности
    :param window_size_ms: Размер окна для извлечения тона (мс)
    :return: Сигнал с извлечённым тоном
    """
    pitch_frequencies = pitch.selected_array['frequency']
    pitch_times = pitch.xs()

    window_size = int(sr * window_size_ms / 1000)  # Размер окна в сэмплах
    half_window = window_size // 2

    tone_signal = np.zeros_like(y)

    for time, frequency in zip(pitch_times, pitch_frequencies):
        if frequency > 0:  # Убедитесь, что частота положительна
            start_index = int(time * sr) - half_window
            end_index = start_index + window_size

            # Защита от выхода за пределы массива
            if start_index < 0 or end_index > len(y):
                continue

            # Генерация тона
            t = np.arange(start_index, end_index) / sr
            tone = np.sin(2 * np.pi * frequency * t)

            # Вставляем тон в сигнал
            tone_signal[start_index:end_index] += tone[:end_index - start_index]

    return tone_signal


def change_pitch_amplitude(y, sr, amplitude_factor):
    # Загрузка аудиосигнала в объект Sound
    sound = pm.Sound(y, sr)

    # Получение основного тона (pitch)
    pitch = call(sound, "To Pitch", 0.0, 50, 800)

    # Извлечение основного тона из исходного сигнала
    tone_signal = extract_tone(y, sr, pitch)

    # Удаление старого тона из исходного сигнала
    new_signal = y - tone_signal

    if amplitude_factor > 0:
        # Изменение амплитуды тона
        modified_tone = tone_signal * amplitude_factor

        # Добавление изменённого тона обратно в сигнал
        new_signal += modified_tone

    # Приведение нового сигнала к допустимому диапазону значений
    new_signal = np.clip(new_signal, -1.0, 1.0)

    return new_signal, int(sr)

def change_pitch_amplitude_range(y, sr, amplitude_factor_from, amplitude_factor_to):
    # Загрузка аудиосигнала в объект Sound
    sound = pm.Sound(y, sr)

    # Получение основного тона (pitch)
    pitch = call(sound, "To Pitch", 0.0, 50, 800)

    # Извлечение основного тона из исходного сигнала
    tone_signal = extract_tone(y, sr, pitch)

    # Удаление старого тона из исходного сигнала
    new_signal = y - tone_signal

    if amplitude_factor_from > 0 and amplitude_factor_to > 0:
        # Количество сэмплов в сигнале
        num_samples = len(tone_signal)

        # Линейная интерполяция множителя амплитуды от начального значения до конечного
        amplitude_factors = np.linspace(amplitude_factor_from, amplitude_factor_to, num_samples)

        # Изменение амплитуды тона по интерполированным значениям
        modified_tone = tone_signal * amplitude_factors

        # Добавление изменённого тона обратно в сигнал
        new_signal += modified_tone

    # Приведение нового сигнала к допустимому диапазону значений
    new_signal = np.clip(new_signal, -1.0, 1.0)

    return new_signal, int(sr)

def change_pitch_amplitude_with_bandwidth(y, sr, amplitude_factor, pitch=None):
    if pitch:
        pitch_values = pitch["frequencies"]
        voiced_times = pitch["voiced_times"]
    else:
        # Извлечение частоты основного тона
        pitch_values, voiced_times, _, _, _, _, _ = extract_f0_voiced(y, sr)

    # Определение границ фильтра на основе минимальных и максимальных значений pitch_values
    lowcut = np.min(pitch_values)  # Нижняя граница: минимальное значение pitch_values
    highcut = np.max(pitch_values)  # Верхняя граница: максимальное значение pitch_values

    # Создание полосового фильтра для диапазона частот pitch_values
    b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)

    # Копируем оригинальный сигнал для модификации
    new_signal = np.copy(y)

    # Преобразование времён в индексы семплов
    voiced_segments = (voiced_times * sr).astype(int)

    for i in range(1, len(voiced_segments)):
        # Преобразуем индексы времени в семплы
        start_sample = voiced_segments[i - 1]
        end_sample = min(voiced_segments[i], len(y))

        # Извлечение сегмента
        segment = y[start_sample:end_sample]

        # Применение фильтра к сегменту
        filtered_signal = scipy.signal.lfilter(b, a, segment)

        # Вычитание старого тона из исходного сигнала
        new_signal[start_sample:end_sample] -= filtered_signal

        # Изменение амплитуды тона
        modified_tone = filtered_signal * amplitude_factor

        # Добавление изменённого тона обратно в сигнал
        new_signal[start_sample:end_sample] += modified_tone

    # Приведение нового сигнала к допустимому диапазону значений [-1.0, 1.0]
    new_signal = np.clip(new_signal, -1.0, 1.0)

    return new_signal, sr

def change_pitch_amplitude_with_bandwidth_range(y, sr, amplitude_factor_from, amplitude_factor_to, pitch=None):
    if pitch:
        pitch_values = pitch["frequencies"]
        voiced_times = pitch["voiced_times"]
    else:
        # Извлечение частоты основного тона
        pitch_values, voiced_times, _, _, _, _, _ = extract_f0_voiced(y, sr)

    # Определение границ фильтра на основе минимальных и максимальных значений pitch_values
    lowcut = np.min(pitch_values)  # Нижняя граница: минимальное значение pitch_values
    highcut = np.max(pitch_values)  # Верхняя граница: максимальное значение pitch_values

    # Создание полосового фильтра для диапазона частот pitch_values
    b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)

    # Копируем оригинальный сигнал для модификации
    new_signal = np.copy(y)

    # Преобразование времён в индексы семплов
    voiced_segments = (voiced_times * sr).astype(int)

    # Линейная интерполяция значений амплитуды от amplitude_factor_from до amplitude_factor_to
    total_segments = len(voiced_segments) - 1
    amplitude_factors = np.linspace(amplitude_factor_from, amplitude_factor_to, total_segments)

    for i in range(1, len(voiced_segments)):
        # Преобразуем индексы времени в семплы
        start_sample = voiced_segments[i - 1]
        end_sample = min(voiced_segments[i], len(y))

        # Извлечение сегмента
        segment = y[start_sample:end_sample]

        # Применение фильтра к сегменту
        filtered_signal = scipy.signal.lfilter(b, a, segment)

        # Вычитание старого тона из исходного сигнала
        new_signal[start_sample:end_sample] -= filtered_signal

        # Получение текущего коэффициента амплитуды
        amplitude_factor = amplitude_factors[i - 1]

        # Изменение амплитуды тона
        modified_tone = filtered_signal * amplitude_factor

        # Добавление изменённого тона обратно в сигнал
        new_signal[start_sample:end_sample] += modified_tone

    # Приведение нового сигнала к допустимому диапазону значений [-1.0, 1.0]
    new_signal = np.clip(new_signal, -1.0, 1.0)

    return new_signal, sr

def change_pitch_amplitude_with_bandwidth2(y, sr, amplitude_factor):
    # Определение основного тона с помощью librosa.pyin
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=800, sr=sr)

    # Определение границ фильтра на основе минимальных и максимальных значений f0
    voiced_frequencies = f0[voiced_flag]  # Только частоты, где есть голос
    lowcut = np.min(voiced_frequencies)  # Нижняя граница: половина минимального f0
    highcut = np.max(voiced_frequencies)  # Верхняя граница: удвоенное максимальное f0

    # Создание полосового фильтра для диапазона частот f0
    b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)

    # Копируем оригинальный сигнал для модификации
    new_signal = np.copy(y)

    # Поиск сегментов, где звук озвучен (voiced)
    segments = []
    segment_start = None

    for i, voiced in enumerate(voiced_flag):
        if voiced and segment_start is None:
            segment_start = i  # Начало сегмента
        elif not voiced and segment_start is not None:
            # Конец сегмента
            segments.append((segment_start, i))
            segment_start = None

    if segment_start is not None:  # Закрыть последний сегмент, если он остался открытым
        segments.append((segment_start, len(voiced_flag)))

    # Обработка каждого сегмента
    for start, end in segments:
        # Преобразование индексов фреймов в индексы семплов
        start_sample = start * 512
        end_sample = min(end * 512, len(y))

        # Извлечение сегмента
        segment = y[start_sample:end_sample]

        # Применение фильтра к сегменту
        filtered_signal = scipy.signal.lfilter(b, a, segment)

        # Вычитание старого тона из исходного сигнала
        new_signal[start_sample:end_sample] -= filtered_signal

        # Изменение амплитуды тона
        modified_tone = filtered_signal * amplitude_factor

        # Добавление изменённого тона обратно в сигнал
        new_signal[start_sample:end_sample] += modified_tone

    # Приведение нового сигнала к допустимому диапазону значений [-1.0, 1.0]
    new_signal = np.clip(new_signal, -1.0, 1.0)

    return new_signal, sr

def change_pitch_amplitude_with_voice(y, sr, amplitude_factor):
    # Определение основного тона с помощью librosa.pyin
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=800, sr=sr)

    # Копируем оригинальный сигнал для модификации
    new_signal = np.copy(y)

    # Поиск сегментов, где звук озвучен (voiced)
    segments = []
    segment_start = None

    for i, voiced in enumerate(voiced_flag):
        if voiced and segment_start is None:
            segment_start = i  # Начало сегмента
        elif not voiced and segment_start is not None:
            # Конец сегмента
            segments.append((segment_start, i))
            segment_start = None

    if segment_start is not None:  # Закрыть последний сегмент, если он остался открытым
        segments.append((segment_start, len(voiced_flag)))

    # Обработка каждого сегмента
    for start, end in segments:
        # Преобразование индексов фреймов в индексы семплов
        start_sample = start * 512
        end_sample = min(end * 512, len(y))

        # Добавление изменённого тона обратно в сигнал
        new_signal[start_sample:end_sample] *= amplitude_factor

    # Приведение нового сигнала к допустимому диапазону значений [-1.0, 1.0]
    new_signal = np.clip(new_signal, -1.0, 1.0)

    return new_signal, sr

def get_pitch_info(y, sr, speech=True):
    # freq, voiced_time,  = extract_f0_segment(y, sr)
    freq, voiced_time, intensity_values, intensity_times, sound, manipulation, pitch_tier = extract_f0_voiced(y, sr, speech=speech)

    return {"frequencies": freq, "voiced_times": voiced_time,
            "intensity": intensity_values, "intensity_times": intensity_times,
            "sound": sound, "manipulation": manipulation, "pitch_tier": pitch_tier}

def calculate_pitch_duration(y, sr, pitch=None):
    """
    Рассчитывает длительность речи с основным тоном (F0) в аудиосигнале с использованием Parselmouth.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :return: Длительность речи с основным тоном в секундах.
    """
    if pitch:
        voiced_time_segments = pitch["voiced_times"]
    else:
        _, voiced_time_segments, _, _, _, _, _ = extract_f0_voiced(y, sr)

    if len(voiced_time_segments) == 0:
        return 0  # Если нет озвученных сегментов, возвращаем 0

    # Длительность основного тона (время от первого до последнего озвученного сегмента)
    duration = voiced_time_segments[-1] - voiced_time_segments[0]

    return duration

def get_pitch_trajectory(y, sr):
    # Извлечение частоты основного тона (F0) с помощью метода "probabilistic YIN"
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    # Проверка на наличие пропущенных значений (nan)
    valid_indices = ~np.isnan(f0)
    hop_length = 512  # значение по умолчанию, используемое в librosa.pyin
    time = np.arange(len(f0)) * hop_length / sr
    time = time[valid_indices]
    pitch_trajectory = f0[valid_indices]

    return time, pitch_trajectory

# Функция remove_pitch_and_reduce_formants уменьшает или убирает основную частоту (F0) и снижает амплитуды формант.
def remove_pitch_and_reduce_formants(y, sr):
    # Удаление тона (F0)
    # Использование librosa.effects.pitch_shift с большим отрицательным значением полутона для удаления тона.
    y_no_pitch = librosa.effects.pitch_shift(y, sr=sr, n_steps=-12)

    # Уменьшение амплитуды формант
    # Применение librosa.effects.percussive для уменьшения амплитуды формант.
    y_no_pitch = librosa.effects.percussive(y_no_pitch, margin=5.0)

    return y_no_pitch


def change_pitch_shift_hz(y, sr, pitch_shift_hz):
    # Извлечение текущего F0
    current_f0 = extract_f0(y, sr)

    if current_f0 is None or current_f0 <= 0:
        raise ValueError("Не удалось извлечь текущий F0 или он некорректен.")

    # Расчет целевого F0
    target_f0 = current_f0 + pitch_shift_hz

    if target_f0 <= 0:
        raise ValueError("Целевой F0 должен быть положительным.")

    # Расчет количества полутонов для сдвига
    n_steps = fl.hz_to_semitones(target_f0, current_f0)

    # Сдвиг тона
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)

    return y_shifted

def change_pitch_fixed_hz(y, sr, pitch_shift_hz):
    # Определение текущего pitch (в герцах) для всего аудиофайла
    pitches, _ = librosa.piptrack(y=y, sr=sr)
    pitches = pitches[pitches > 0]

    # Если pitch не обнаружен, использовать 440 Гц как стандарт
    if len(pitches) == 0:
        current_pitch = 440.0
    else:
        current_pitch = np.median(pitches)

    # Перевод изменения pitch из герц в полутоновые шаги
    pitch_shift_semitones = fl.hz_to_semitones(current_pitch + pitch_shift_hz, current_pitch)

    # Применение изменения pitch с использованием метода Phase Vocoder
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift_semitones)
    return y_shifted


def change_pitch_fixed_hz_segmented(y, sr, pitch_shift_hz, segment_duration=2.0):
    # Длительность сегмента в сэмплах
    segment_samples = int(segment_duration * sr)

    # Обработка сегментов
    segments = [y[i:i+segment_samples] for i in range(0, len(y), segment_samples)]

    # Обработка каждого сегмента
    shifted_segments = []
    for segment in segments:
        # Определение текущего pitch (в герцах) для сегмента
        pitches, _ = librosa.piptrack(y=segment, sr=sr)
        pitches = pitches[pitches > 0]

        if len(pitches) == 0:
            current_pitch = 440.0
        else:
            current_pitch = np.median(pitches)

        # Перевод изменения pitch из герц в полутоновые шаги
        # pitch_shift_semitones = hz_to_semitones(current_pitch + pitch_shift_hz) - hz_to_semitones(current_pitch)
        pitch_shift_semitones = fl.hz_to_semitones(current_pitch + pitch_shift_hz, current_pitch)

        # Применение изменения pitch
        shifted_segment = librosa.effects.pitch_shift(segment, sr=sr, n_steps=pitch_shift_semitones)
        shifted_segments.append(shifted_segment)

    # Объединение сегментов
    y_shifted = np.concatenate(shifted_segments)

    return y_shifted

def change_pitch_fixed_hz_with_filter(y, sr, pitch_shift_hz):
    # Определение текущего pitch (в герцах) для всего аудиофайла
    pitches, _ = librosa.piptrack(y=y, sr=sr)
    pitches = pitches[pitches > 0]

    if len(pitches) == 0:
        current_pitch = 440.0
    else:
        current_pitch = np.median(pitches)

    # Перевод изменения pitch из герц в полутоновые шаги
    # pitch_shift_semitones = hz_to_semitones(current_pitch + pitch_shift_hz) - hz_to_semitones(current_pitch)
    pitch_shift_semitones = fl.hz_to_semitones(current_pitch + pitch_shift_hz, current_pitch)

    # Применение изменения pitch
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift_semitones)

    # Применение сглаживающего фильтра
    y_filtered = fl.apply_smoothing_filter(y_shifted, sr)

    return y_filtered

def change_pitch_pydub2(y, sr, pitch_shift_semitones):
    # Конвертация массива y в int16
    y_int16 = (y * 32767).astype(np.int16)

    # Создание объекта AudioSegment из массива y_int16 и частоты дискретизации sr
    sound = AudioSegment(
        y_int16.tobytes(),
        frame_rate=sr,
        sample_width=y_int16.dtype.itemsize,
        channels=1
    )

    # Применение изменения pitch
    shifted_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * (2 ** (pitch_shift_semitones / 12.0)))
    })

    shifted_sound = shifted_sound.set_frame_rate(sound.frame_rate)

    # Конвертация объекта AudioSegment обратно в массив numpy
    y_shifted = np.array(shifted_sound.get_array_of_samples(), dtype=np.float32) / 32767.0

    # Возвращение измененного массива y_shifted и частоты дискретизации sr
    return y_shifted, sr

def change_pitch_pydub(y, sr, pitch_shift_semitones):
    # Конвертация массива y в int16
    y_int16 = (y * 32767).astype(np.int16)

    # Создание объекта AudioSegment из массива y_int16 и частоты дискретизации sr
    sound = AudioSegment(
        y_int16.tobytes(),
        frame_rate=sr,
        sample_width=y_int16.dtype.itemsize,
        channels=1
    )

    # Изменение частоты дискретизации для изменения pitch
    new_frame_rate = int(sound.frame_rate * (2 ** (pitch_shift_semitones / 12.0)))
    shifted_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": new_frame_rate})

    # Восстановление частоты дискретизации до исходной
    shifted_sound = shifted_sound.set_frame_rate(sr)

    # Конвертация объекта AudioSegment обратно в массив numpy
    y_shifted = np.array(shifted_sound.get_array_of_samples(), dtype=np.float32) / 32767.0

    # Обрезка или дополнение массива до исходной длины
    if len(y_shifted) > len(y):
        y_shifted = y_shifted[:len(y)]
    else:
        y_shifted = np.pad(y_shifted, (0, len(y) - len(y_shifted)), 'constant')

    # Возвращение измененного массива y_shifted и частоты дискретизации sr
    return y_shifted, sr

def change_pitch_rubberband(y, sr, pitch_shift_hz):
    # Применение изменения pitch с помощью RubberBand
    y_shifted = rb.pitch_shift(y, sr, pitch_shift_hz)

    return y_shifted

'''
Спектральный наклон (spectral tilt) — это параметр, описывающий уменьшение энергии в спектре звука с 
увеличением частоты. В контексте основного тона (pitch) это может помочь понять, как распределяется 
энергия по гармоникам основного тона.
'''
def calculate_spectral_tilt_pitch(y, sr):
    """
    Рассчитывает спектральный наклон основного тона в аудиосигнале.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :return: Спектральный наклон основного тона.
    """
    # Извлечение основного тона (F0) с помощью Parselmouth
    f0_values = extract_f0_values(y, sr)
    f0_voiced = f0_values[~np.isnan(f0_values) & (f0_values > 0)]

    if len(f0_voiced) == 0:
        return 0  # Если нет озвученных кадров, возвращаем 0

    # Средняя частота основного тона
    avg_f0 = np.mean(f0_voiced)
    if np.isnan(avg_f0):
        return 0

    # Применяем полосовой фильтр вокруг средней частоты основного тона
    bandwidth = calculate_pitch_bandwidth(y, sr)
    b, a = scipy.signal.butter(2, [max(avg_f0 - bandwidth, 1), avg_f0 + bandwidth], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, y)

    # Рассчитываем спектр мощности отфильтрованного сигнала
    f, Pxx = scipy.signal.welch(filtered_signal, sr, nperseg=2048)

    # Исключаем нулевые и отрицательные частоты и их мощности
    mask = f > 0
    f = f[mask]
    Pxx = Pxx[mask]

    # Применяем логарифм к частотам и мощностям
    log_f = np.log(f).reshape(-1, 1)
    log_Pxx = np.log(Pxx)

    # Применяем линейную регрессию для нахождения наклона спектра
    reg = LinearRegression().fit(log_f, log_Pxx)
    spectral_tilt = reg.coef_[0]

    return spectral_tilt

def calculate_spectral_tilt_pitch2(y, sr):
    """
    Рассчитывает спектральный наклон основного тона в аудиосигнале.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :return: Спектральный наклон основного тона.
    """
    # Извлечение основного тона (F0) с помощью метода "probabilistic YIN"
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    # Извлечение ненулевых значений основного тона (только озвученные кадры)
    f0_voiced = f0[voiced_flag]

    if len(f0_voiced) == 0:
        return 0  # Если нет озвученных кадров, возвращаем 0

    # Средняя частота основного тона
    avg_f0 = np.mean(f0_voiced)
    if np.isnan(avg_f0):
        return 0

    # Применяем полосовой фильтр вокруг средней частоты основного тона
    bandwidth = calculate_pitch_bandwidth(y, sr)
    b, a = scipy.signal.butter(2, [max(avg_f0 - bandwidth, 1), avg_f0 + bandwidth], btype='band', fs=sr)
    filtered_signal = scipy.signal.lfilter(b, a, y)

    # Рассчитываем спектр мощности отфильтрованного сигнала
    f, Pxx = scipy.signal.welch(filtered_signal, sr, nperseg=2048)

    # Исключаем нулевые и отрицательные частоты и их мощности
    mask = f > 0
    f = f[mask]
    Pxx = Pxx[mask]

    # Применяем логарифм к частотам и мощностям
    log_f = np.log(f).reshape(-1, 1)
    log_Pxx = np.log(Pxx)

    # Применяем линейную регрессию для нахождения наклона спектра
    reg = LinearRegression().fit(log_f, log_Pxx)
    spectral_tilt = reg.coef_[0]

    return spectral_tilt


def extract_pitch_intensity(signal, sr):
    """
    Extracts the pitch and its corresponding intensity from an audio signal.

    Parameters:
    - signal: The audio signal (1D numpy array).
    - sr: The sample rate of the audio signal.

    Returns:
    - pitch_frequencies: Array of pitch frequencies.
    - pitch_intensities: Array of intensities corresponding to the pitch frequencies.
    - times: Array of time stamps for each pitch measurement.
    """
    snd = pm.Sound(signal, sr)

    # Extract pitch using Parselmouth
    pitch = snd.to_pitch()

    # Get pitch frequencies and time stamps
    pitch_frequencies = pitch.selected_array['frequency']
    pitch_frequencies = pitch_frequencies[pitch_frequencies > 0]
    times = pitch.xs()

    # Calculate the bandwidth as the difference between max and min pitch frequencies
    max_pitch = np.nanmax(pitch_frequencies)
    min_pitch = np.nanmin(pitch_frequencies)

    # Define the bandpass filter around the average pitch frequency
    b, a = scipy.signal.butter(2, [min_pitch, max_pitch], btype='band', fs=sr)

    # Apply the filter to the signal
    filtered_signal = scipy.signal.lfilter(b, a, signal)

    # Create an array to store pitch intensities
    pitch_intensities = []

    frame_length = 2048

    # Get the intensity for each time stamp
    for t in times:
        # Find the closest sample index for the current time
        sample_idx = int(t * sr)

        # Extract the frame around the sample index
        start_idx = max(0, sample_idx - frame_length // 2)
        end_idx = min(len(signal), sample_idx + frame_length // 2)
        frame = filtered_signal[start_idx:end_idx]

        # Calculate the RMS (root mean square) of the filtered frame
        rms = np.sqrt(np.mean(frame ** 2))

        # Convert RMS to intensity in dB
        intensity_db = 20 * np.log10(rms + np.finfo(float).eps)

        # Append the intensity to the list
        pitch_intensities.append(intensity_db)

    return np.array(pitch_frequencies), np.array(pitch_intensities), np.array(times)


def calculate_pitch_intensity_avg2(signal, sr):
    pitch_frequencies, pitch_intensities, times = extract_pitch_intensity(signal, sr)

    return np.nanmean(pitch_intensities)


def change_pitch_bandwidth(signal, sr, pitch_factor):
    """
    Изменяет ширину канала pitch в аудиосигнале.

    :param signal: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param pitch_factor: Фактор изменения ширины канала pitch.
    :return: Изменённый аудиосигнал.
    """
    # Загрузка аудиофайла
    sound = pm.Sound(signal, sr)

    # Получение основного тона (pitch)
    pitch = get_pitch_with_retries(sound)
    if pitch is None:
        return None

    # Получение временной информации о рамках
    times = pitch.ts()

    # Копия оригинального сигнала для модификации
    modified_signal = np.copy(signal)

    for i, time in enumerate(times):
        # Получение текущей частоты pitch
        current_pitch = pitch.get_value_at_time(time)
        if np.isnan(current_pitch) or current_pitch <= 0:
            continue

        # Изменение ширины канала pitch
        new_bandwidth = current_pitch * pitch_factor

        # Применяем полосовой фильтр с новой шириной полосы
        lowcut = max(current_pitch - new_bandwidth / 2, 1)
        highcut = min(current_pitch + new_bandwidth / 2, sr / 2)

        b, a = scipy.signal.butter(2, [lowcut, highcut], btype='band', fs=sr)
        filtered_signal = scipy.signal.lfilter(b, a, signal)

        # Вычисление сегмента, соответствующего текущему времени
        segment_start = int(time * sr) - len(filtered_signal) // 2
        segment_end = segment_start + len(filtered_signal)

        # Корректировка границ сегмента, если они выходят за пределы сигнала
        if segment_start < 0:
            segment_start = 0
            segment_end = len(filtered_signal)
        if segment_end > len(signal):
            segment_end = len(signal)
            segment_start = segment_end - len(filtered_signal)

        # Вычитание исходного сигнала в текущем сегменте
        modified_signal[segment_start:segment_end] -= signal[segment_start:segment_end]

        # Добавление масштабированного сигнала
        modified_signal[segment_start:segment_end] += filtered_signal[:segment_end - segment_start]

    # Нормализация, чтобы предотвратить клиппинг
    modified_signal = np.clip(modified_signal, -1, 1)

    return modified_signal


def smooth_values(values, window_size=5):
    """Сглаживание значений с помощью скользящего среднего."""
    return np.convolve(values, np.ones(window_size)/window_size, mode='valid')

def detect_peaks(pitch, prominence=1.0):
    """Простое определение пиков."""
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(pitch, prominence=prominence)
    return peaks

def calculate_pitch_slope(y, sr, is_smooth=True, is_peak=True, pitch=None):
    if pitch:
        freq = pitch["frequencies"]
        times = pitch["voiced_times"]
    else:
        # Извлечение частоты основного тона
        freq, times, _, _, _, _, _ = extract_f0_voiced(y, sr)

    if len(times) == 0:
        return 0, 0, ''  # Если нет озвученных сегментов, возвращаем 0

    # Сглаживание частот
    if is_smooth:
        freq = smooth_values(freq)
        # Обновляем времена после сглаживания
        times = times[:len(freq)]

    # Оставляем только пики частот
    if is_peak:
        peaks = detect_peaks(freq)
        freq = freq[peaks]
        times = times[peaks]

    # Проводим линейную регрессию
    if len(times) < 2:  # Нужно хотя бы две точки для регрессии
        return 0, 0, ''

    slope, intercept, r_value, p_value, std_err = linregress(times, freq)

    # Вычисляем предсказанные значения по линейной регрессии
    predicted_freq = intercept + slope * times

    # Вычисляем остатки (разницу между реальными и предсказанными значениями)
    residuals = freq - predicted_freq

    # Вычисляем дисперсию остатков
    variance = np.var(residuals)

    # Определяем направление тренда
    if slope > 0 and variance < 0.01:
        trend = "Рост"
    elif slope < 0 and variance < 0.01:
        trend = "Падение"
    else:
        trend = "Стабильный"

    return slope, variance, trend

def calculate_intensity_slope(y, sr, is_smooth=True, is_peak=True, pitch=None):
    # Извлекаем данные о частоте и интенсивности
    if pitch:
        intensity_values = pitch["intensity"]
        intensity_times = pitch["intensity_times"]
    else:
        # Извлечение частоты основного тона и интенсивности
        _, _, intensity_values, intensity_times, _, _, _ = extract_f0_voiced(y, sr)

    if len(intensity_times) == 0:
        return 0, 0, ''  # Если нет данных по интенсивности, возвращаем 0

    # Сглаживание интенсивности
    if is_smooth:
        intensity_values = smooth_values(intensity_values)  # Функция для сглаживания интенсивности
        # Обновляем времена после сглаживания
        intensity_times = intensity_times[:len(intensity_values)]

    # Оставляем только пики интенсивности
    if is_peak:
        peaks = detect_peaks(intensity_values)
        intensity_values = intensity_values[peaks]
        intensity_times = intensity_times[peaks]

    # Проводим линейную регрессию
    if len(intensity_times) < 2:  # Нужно хотя бы две точки для регрессии
        return 0, 0, ''

    slope, intercept, r_value, p_value, std_err = linregress(intensity_times, intensity_values)

    # Вычисляем предсказанные значения по линейной регрессии
    predicted_intensity = intercept + slope * intensity_times

    # Вычисляем остатки (разницу между реальными и предсказанными значениями)
    residuals = intensity_values - predicted_intensity

    # Вычисляем дисперсию остатков
    variance = np.var(residuals)

    # Определяем направление тренда
    if slope > 0 and variance < 0.01:
        trend = "Рост"
    elif slope < 0 and variance < 0.01:
        trend = "Падение"
    else:
        trend = "Стабильный"

    return slope, variance, trend

def modify_pitch_slope(y, sr, slope_change=1.0):
    # Загрузка аудио
    sound = pm.Sound(y, sr)

    # Извлечение частоты основного тона (pitch)
    pitch_trajectory, voiced_time_segments, _, _, _, _, _ = extract_f0_voiced(y, sr)

    # Применение изменения наклона
    time = np.arange(len(pitch_trajectory))
    pitch_slope = slope_change * (time / len(pitch_trajectory))
    new_pitch_values = pitch_trajectory * (1 + pitch_slope)

    # Получение основного тона (pitch)
    pitch = call(sound, "To Pitch", 0.0, 75, 600)
    pitch_tier = call(pitch, "Down to PitchTier")

    # Удаление существующих точек PitchTier
    start_time = call(pitch_tier, "Get start time")
    end_time = call(pitch_tier, "Get end time")
    call(pitch_tier, "Remove points between", start_time, end_time)

    # Добавление новых точек с измененным наклоном pitch
    for t, freq in zip(voiced_time_segments, new_pitch_values):
        call(pitch_tier, "Add point", t, freq)

    # Создание Manipulation объекта
    manipulation = call(sound, "To Manipulation", 0.001, 75, 600)

    # Замена PitchTier в Manipulation объекте
    call([manipulation, pitch_tier], "Replace pitch tier")

    # Ресинтез звука с измененным pitch
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    return resynthesized_sound.values[0], int(sound.sampling_frequency)

def slope_pitch(y, sr, start_delta=0.0, end_delta=0.0, pitch=None):
    # Извлечение частоты основного тона (pitch)
    if pitch:
        sound = pitch["sound"]
        manipulation = pitch["manipulation"]
        pitch_tier = pitch["pitch_tier"]

        pitch_values = pitch["frequencies"]
        times = pitch["voiced_times"]
        start_time = np.nanmin(times)
        end_time = np.nanmax(times)
    else:
        # Загрузка аудио
        sound = pm.Sound(y, sr)

        try:
            pitch_info = call(sound, "To Pitch", 0.0, 75, 600)
        except pm.PraatError as e:
            return None, None

        pitch_values = pitch_info.selected_array['frequency']

        # Получение PitchTier из Pitch
        pitch_tier = call(pitch_info, "Down to PitchTier")
        start_time = call(pitch_info, "Get start time")
        end_time = call(pitch_info, "Get end time")

        # Создание Manipulation объекта
        manipulation = call(sound, "To Manipulation", 0.001, 75, 600)

    # Рассчитываем среднее значение для озвученных сегментов (исключая нулевые значения)
    mean_pitch = np.mean(pitch_values[pitch_values > 0])

    try:
        # Устанавливаем константное значение pitch на протяжении всего аудио
        call(pitch_tier, "Remove points between", start_time, end_time)
        call(pitch_tier, "Add point", start_time, mean_pitch + start_delta)
        call(pitch_tier, "Add point", end_time, mean_pitch + end_delta)
    except pm.PraatError as e:
        return None, None

    # Замена PitchTier в Manipulation объекте
    call([manipulation, pitch_tier], "Replace pitch tier")

    # Ресинтез звука с выровненным pitch
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    return resynthesized_sound.values[0], int(sound.sampling_frequency)

def flatten_pitch(y, sr, pitch=None):
    return slope_pitch(y, sr, start_delta=0.0, end_delta=0.0, pitch=pitch)

def change_audio_speed(y, sr, begin_speed=1.0, end_speed=1.0):
    # Инвертируем коэффициенты скоростей для удобства
    begin_speed = 1 / begin_speed
    end_speed = 1 / end_speed

    # Расчет целевой длины сигнала
    avg_speed = (begin_speed + end_speed) / 2
    target_length = int(len(y) * avg_speed)

    # Создаем массив коэффициентов изменения скорости, изменяющийся линейно от начала до конца
    speed_factors = np.linspace(begin_speed, end_speed, target_length)

    # Создаем массив кумулятивного времени для нового сигнала
    new_time_steps = np.cumsum(1 / speed_factors) / sr

    # Создаем массив времени для исходного сигнала
    original_time_steps = np.arange(len(y)) / sr

    # Интерполяция аудиосигнала на новые временные позиции
    new_y = np.interp(new_time_steps, original_time_steps, y)

    return new_y

def change_pitch_intonation_ex(y, sr, begin_period, end_period, begin_amplitude, end_amplitude, offset=0,
                               slope_change=0.0, pitch=None):
    if pitch:
        sound = pitch["sound"]
        manipulation = pitch["manipulation"]
        pitch_tier = pitch["pitch_tier"]

        pitch_values = pitch["frequencies"]
        times = pitch["voiced_times"]

        start_time = np.nanmin(times)
        end_time = np.nanmax(times)
    else:
        # Загрузка аудио
        sound = pm.Sound(y, sr)

        # Извлечение основного тона (pitch)
        pitch_info = call(sound, "To Pitch", 0.0, 75, 600)
        pitch_values = pitch_info.selected_array['frequency']

        # Получение PitchTier из Pitch
        pitch_tier = call(pitch_info, "Down to PitchTier")

        times = pitch_info.xs()
        start_time = call(pitch_tier, "Get start time")
        end_time = call(pitch_tier, "Get end time")

        # Создание Manipulation объекта
        manipulation = call(sound, "To Manipulation", 0.001, 75, 600)


    # Создание новой интонации с использованием синусоидального изменения
    new_pitch_values = pitch_values.copy()
    duration = times[-1] - times[0]  # Длительность аудио
    for i, t in enumerate(times):
        k = (t - times[0]) / duration
        # Линейное изменение периода и амплитуды
        period = begin_period + (end_period - begin_period) * k
        amplitude = begin_amplitude + (end_amplitude - begin_amplitude) * k

        # Изменение частоты с учетом плавного изменения периода и амплитуды
        new_pitch_values[i] += amplitude * np.sin(2 * np.pi * (t - offset) / period)
        pitch_slope = slope_change * k
        new_pitch_values[i] = new_pitch_values[i] * (1 + pitch_slope)
        new_pitch_values[i] = max(75, new_pitch_values[i])  # Убедимся, что частота не ниже 75 Гц

    # Очистка старых точек
    call(pitch_tier, "Remove points between", start_time, end_time)

    # Добавление новых значений pitch
    for t, freq in zip(times, new_pitch_values):
        call(pitch_tier, "Add point", t, freq)

    # Замена PitchTier в Manipulation объекте
    call([manipulation, pitch_tier], "Replace pitch tier")

    # Ресинтез звука с новой интонацией
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    return resynthesized_sound.values[0], int(sound.sampling_frequency)


def change_pitch_intonation(y, sr, period, offset, amplitude):
    return change_pitch_intonation_ex(y, sr, begin_period=period, end_period=period, begin_amplitude=amplitude,
                                      end_amplitude=amplitude, offset=offset)


def change_audio_speed_period(y, sr, period, offset, amplitude, mean_speed=1.0):
    # Создаем массив временных шагов
    time_steps = np.arange(len(y)) / sr

    # Вычисляем изменение скорости по синусоидальной функции
    speed_factors = mean_speed + amplitude * np.sin(2 * np.pi * (time_steps - offset) / period)

    # Новый массив с измененным временем
    new_time_steps = np.cumsum(1 / speed_factors) / sr

    # Интерполяция аудиосигнала для изменения времени
    new_y = np.interp(new_time_steps, time_steps, y)

    return new_y


def change_audio_speed_acceleration(y, sr, initial_speed=1.0, acceleration=0.0):
    # Создаем массив временных шагов
    time_steps = np.arange(len(y)) / sr

    # Вычисляем скорость в каждый момент времени на основе начальной скорости и ускорения
    speed_factors = initial_speed + acceleration * time_steps

    # Новый массив с измененным временем
    new_time_steps = np.cumsum(1 / speed_factors) / sr

    # Интерполяция аудиосигнала для изменения времени
    new_y = np.interp(new_time_steps, time_steps, y)

    return new_y


def change_audio_speed_periodic(y, sr, period, offset, amplitude, mean_speed=1.0):
    # Создаем массив временных шагов
    time_steps = np.arange(len(y)) / sr

    # Рассчитываем синусоиду с заданным периодом и смещением
    speed_modulation = amplitude * np.abs(np.sin(2 * np.pi * (time_steps - offset) / period))

    # Итоговая скорость в каждый момент времени
    speed_factors = mean_speed + speed_modulation

    # Новый массив с измененным временем
    new_time_steps = np.cumsum(1 / speed_factors) / sr

    # Интерполяция аудиосигнала для изменения времени
    new_y = np.interp(new_time_steps, time_steps, y)

    return new_y


def change_modulate_speed_per_fragment(y, sr, fragment_duration, base_speed=1.0, amplitude=0.5):
    num_samples_per_fragment = int(fragment_duration * sr)
    num_fragments = len(y) // num_samples_per_fragment

    modulated_signal = []

    for i in range(num_fragments):
        fragment = y[i * num_samples_per_fragment: (i + 1) * num_samples_per_fragment]

        # Создаем массив скоростей, от базовой скорости до базовая + амплитуда
        time_steps = np.arange(len(fragment)) / sr
        speed_factors = base_speed + amplitude * np.sin(np.pi * time_steps / time_steps[-1])

        # Новый массив с измененным временем для каждого фрагмента
        new_time_steps = np.cumsum(1 / speed_factors) / sr

        # Интерполяция аудиосигнала для изменения времени
        modulated_fragment = np.interp(new_time_steps, time_steps, fragment)

        modulated_signal.extend(modulated_fragment)

    return np.array(modulated_signal)


def extract_timbre(y, sr, n_formants=3):
    # Преобразование звука в спектрограмму
    S = np.abs(librosa.stft(y))

    # Спектральный конверт
    spectral_envelope = librosa.feature.melspectrogram(S=S, sr=sr)

    # Вычисление формант (примерный расчет)
    formants = []
    for i in range(n_formants):
        formant = np.mean(spectral_envelope[i])
        formants.append(formant)

    return spectral_envelope, formants


def extract_rhythm(y, sr):
    # Извлечение темпограммы
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)

    # Вычисление среднего темпа
    # tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    tempo = librosa.feature.rhythm.tempo(onset_envelope=onset_env, sr=sr)

    return tempogram, tempo


def extract_timbre_from_pitch(y, sr):
    # Расчет высоты тона
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    # Получаем средние значения высоты тона
    avg_pitches = np.mean(pitches, axis=1)

    # Расчет спектрального центра
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

    # Вычисление среднего значения спектрального центра
    avg_spectral_centroid = np.mean(spectral_centroid)

    return avg_pitches, avg_spectral_centroid


def extract_rhythm_from_pitch(y, sr):
    # Извлечение начальных событий для анализа ритма
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # Определение высоты тона
    pitches, _ = librosa.piptrack(y=y, sr=sr)
    pitch_changes = np.mean(pitches, axis=1)

    # Вычисление темпограммы на основе начальных событий
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)

    # Вычисление среднего значения темпограммы
    avg_tempogram = np.mean(tempogram)

    return pitch_changes, avg_tempogram


def find_speech_segments(y, sr, min_energy_threshold=0.01, min_pause_duration=0.5, frame_length=2048, hop_length=512, min_false_duration=0.1):
    y_noise = ns.noise_reduction_spectral_subtraction_fast(y, sr)

    # Вычисление энергии сигнала
    energy = np.sqrt(librosa.feature.rms(y=y_noise, frame_length=frame_length, hop_length=hop_length)[0])

    # Определение порога для энергии сигнала
    energy_threshold = min_energy_threshold

    # Создание маски для участков речи
    speech_mask = energy > energy_threshold

    # Длительность одного фрейма в секундах
    frame_duration = hop_length / sr

    # Минимальная длина последовательности False в кадрах
    min_false_frames = int(min_false_duration / frame_duration)

    # Фильтрация одиночных False внутри последовательностей True
    speech_mask_filtered = np.copy(speech_mask)
    false_count = 0

    for i in range(1, len(speech_mask) - 1):
        if not speech_mask[i]:
            false_count += 1
        else:
            if 0 < false_count < min_false_frames:
                speech_mask_filtered[i - false_count:i] = True
            false_count = 0

    # Если последняя последовательность False меньше порога
    if 0 < false_count < min_false_frames:
        speech_mask_filtered[-false_count:] = True

    # Нахождение изменений в маске для определения пауз и участков речи
    changes = np.diff(speech_mask_filtered.astype(int))

    # Нахождение начальных и конечных точек участков речи
    start_points = np.where(changes == 1)[0] + 1
    end_points = np.where(changes == -1)[0]

    if len(start_points) == 0:
        return []

    if len(end_points) == 0 or end_points[0] < start_points[0]:
        # end_points = np.concatenate(([0], end_points))
        start_points = np.concatenate(([0], start_points))

    # Добавление конечной точки в конец сигнала, если это необходимо
    if len(end_points) < len(start_points):
        end_points = np.concatenate((end_points, [len(energy) - 1]))

    segments = []

    for start, end in zip(start_points, end_points):
        # Переход из индексов в секунды
        start_time = start * hop_length / sr
        end_time = end * hop_length / sr

        # Фильтрация по минимальной длительности паузы
        if end_time - start_time > min_pause_duration:
            # Найти индекс начала и конца в исходном сигнале
            start_sample = int(start * hop_length)
            end_sample = int(end * hop_length)

            # Извлечение сегмента из исходного сигнала
            segment_y = y[start_sample:end_sample]
            segment_sr = sr
            segments.append((start_time, end_time, segment_y, segment_sr))

    # if len(segments) == 0:
    #     segments.append((0, len(y) / sr, y, sr))

    return segments


def calculate_amplitude_from_period(filtered_pitches, filtered_times, period):
    if period is None or len(filtered_pitches) == 0:
        return None

    # Преобразуем filtered_pitches в одномерный массив
    filtered_pitches = filtered_pitches.flatten()

    # Инициализируем список для хранения амплитуд за каждый период
    amplitudes = []

    start_time = filtered_times[0]
    current_period = []

    for i in range(len(filtered_pitches)):
        # Определяем временные рамки для текущего периода
        if filtered_times[i] < start_time + period:
            current_period.append(filtered_pitches[i])
        else:
            # Рассчитываем амплитуду для текущего периода
            if len(current_period) > 1:
                min_pitch = np.min(current_period)
                max_pitch = np.max(current_period)
                amplitude = max_pitch - min_pitch
                amplitudes.append(amplitude)

            # Переходим к следующему периоду
            start_time = filtered_times[i]
            current_period = [filtered_pitches[i]]

    # Если осталась незавершенная часть периода
    if len(current_period) > 1:
        min_pitch = np.min(current_period)
        max_pitch = np.max(current_period)
        amplitude = (max_pitch - min_pitch)
        amplitudes.append(amplitude)

    if len(amplitudes) == 0:
        return None

    # Возвращаем среднюю амплитуду
    avg_amplitude = np.mean(amplitudes) * 0.5

    return avg_amplitude

def calculate_period(filtered_pitches, filtered_times):
    filtered_pitches = uniform_filter1d(filtered_pitches, size=5)

    if len(filtered_pitches) < 2 or len(filtered_times) < 2:
        return None

    # Находим изменения направления
    direction_changes = []

    prev_diff = filtered_pitches[1] - filtered_pitches[0]
    prev_time_diff = filtered_times[1] - filtered_times[0]
    prev_sign = np.sign(prev_diff)
    is_start = True
    for i in range(1, len(filtered_pitches) - 1):
        next_diff = filtered_pitches[i + 1] - filtered_pitches[i]
        next_time_diff = filtered_times[i + 1] - filtered_times[i]

        # Если направление меняется (знак разности меняется) и интервалы ненулевые
        next_sign = np.sign(next_diff)
        if next_sign == 0:
            next_sign = prev_sign
        if (prev_sign != next_sign or is_start) and abs(prev_diff) > 0 and abs(next_diff) > 0 and prev_time_diff > 0 and next_time_diff > 0:
            direction_changes.append(i)
            is_start = False
        if next_diff != 0:
            prev_sign = next_sign
            prev_diff = next_diff
            prev_time_diff = next_time_diff

    # Если изменений направления недостаточно для оценки периода
    if len(direction_changes) < 2:
        return None

    # Рассчитываем интервалы времени между изменениями направления
    periods = np.diff([filtered_times[i] for i in direction_changes])

    # Исключаем нулевые интервалы, если они есть
    periods = periods[periods > 0]

    # Если все интервалы оказались нулевыми, возвращаем None
    if len(periods) == 0:
        return None

    # Средний период
    avg_period = np.mean(periods)
    periods = periods[abs(periods-avg_period) < avg_period*0.7]
    if len(periods) == 0:
        return None
    max_period = np.max(periods) * 2

    return max_period


def calculate_period_shift(filtered_pitches, filtered_times, period):
    if period is None or len(filtered_pitches) == 0:
        return None

    # Преобразуем filtered_pitches в одномерный массив
    filtered_pitches = filtered_pitches.flatten()

    shifts = []

    # Начальная точка отсчета
    start_time = filtered_times[0]
    start_index = 0

    for i in range(1, len(filtered_pitches)):
        # Если мы достигли конца периода
        if filtered_times[i] >= start_time + period:
            # В текущем периоде ищем первую точку смены направления
            for j in range(start_index + 1, i):
                if np.sign(filtered_pitches[j] - filtered_pitches[j-1]) != np.sign(filtered_pitches[j+1] - filtered_pitches[j]):
                    shift_time = filtered_times[j] - start_time
                    shifts.append(shift_time)
                    break

            # Обновляем начальную точку для следующего периода
            start_time = filtered_times[i]
            start_index = i

    if len(shifts) == 0:
        # В текущем периоде ищем первую точку смены направления
        for j in range(1, len(filtered_pitches) - 1):
            if np.sign(filtered_pitches[j] - filtered_pitches[j - 1]) != np.sign(
                    filtered_pitches[j + 1] - filtered_pitches[j]):
                shift_time = filtered_times[j] - start_time
                return shift_time

        return None

    # Среднее смещение времени
    avg_shift = np.mean(shifts)

    return avg_shift

def extract_pitch_rate(y, sr, medfilt_size=5, pitch=None):
    # Извлечение F0 и временных меток
    if pitch:
        filtered_pitches = pitch["frequencies"]
        filtered_times = pitch["voiced_times"]
    else:
        filtered_pitches, filtered_times, _, _, _, _, _ = extract_f0_voiced(y, sr)

    if len(filtered_pitches) == 0:
        return None, None, None  # Если нет данных о высоте тона, возвращаем None

    # Применение медианного фильтра
    filtered_pitches = medfilt(filtered_pitches.flatten(), medfilt_size).reshape(-1, 1)

    if len(filtered_pitches) == 0:
        return None, None, None  # Если нет отфильтрованных частот, возвращаем None

    # Интервалы между временными метками, где зафиксированы действительные высоты тона
    pitch_intervals = np.diff(filtered_times)

    if len(pitch_intervals) == 0:
        return None, None, None  # Если нет интервалов, возвращаем None

    # Расчет периода, амплитуды
    period = calculate_period(filtered_pitches, filtered_times)
    amplitude = calculate_amplitude_from_period(filtered_pitches, filtered_times, period)
    offset = calculate_period_shift(filtered_pitches, filtered_times, period)

    return period, offset, amplitude


def scale_pitch_width(y, sr, factor=1.0):
    # Загрузка аудио
    sound = pm.Sound(y, sr)

    # Извлечение частоты основного тона (pitch)
    pitch = call(sound, "To Pitch", 0.0, 75, 600)
    pitch_values = pitch.selected_array['frequency']

    # Рассчитываем среднее значение для озвученных сегментов (исключая нулевые значения)
    mean_pitch = np.mean(pitch_values[pitch_values > 0])

    # Создание Manipulation объекта
    manipulation = call(sound, "To Manipulation", 0.001, 75, 600)

    # Получение PitchTier из Pitch
    pitch_tier = call(pitch, "Down to PitchTier")
    start_time = call(pitch_tier, "Get start time")
    end_time = call(pitch_tier, "Get end time")

    # Преобразование частот в PitchTier
    for t in np.arange(start_time, end_time, 0.01):
        current_pitch = call(pitch, "Get value at time", t, "Hertz", "linear")

        if current_pitch > 0:  # Только если значение тона больше нуля
            # Изменение ширины частоты относительно mean_pitch
            new_pitch = (current_pitch - mean_pitch) * factor + mean_pitch
            call(pitch_tier, "Remove point near", t)
            call(pitch_tier, "Add point", t, new_pitch)

    # Замена PitchTier в Manipulation объекте
    call([manipulation, pitch_tier], "Replace pitch tier")

    # Ресинтез звука с измененной шириной pitch
    resynthesized_sound = call(manipulation, "Get resynthesis (overlap-add)")

    return resynthesized_sound.values[0], int(sound.sampling_frequency)
