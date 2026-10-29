import numpy as np
import librosa
from scipy.stats import linregress
import parselmouth as pm
from . import sk_noise as ns
from . import sk_pitch as pt
from . import sk_formants as fmt

def is_soft_speech(y, sr, intensity_min_db=20, intensity_max_db=45, f0_min=50, f0_max=300, formant_thresholds=(300, 3000)):
    """
    Определяет, является ли аудиосигнал тихой речью, используя интенсивность, основной тон (F0) и форманты.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param intensity_min_db: Минимальный порог интенсивности в децибелах для определения тихой речи.
    :param intensity_max_db: Максимальный порог интенсивности в децибелах для определения тихой речи.
    :param f0_min: Минимальная частота тона (Hz).
    :param f0_max: Максимальная частота тона (Hz).
    :param formant_thresholds: Ожидаемые диапазоны частот для первых двух формант (F1, F2).
    :return: True если сигнал является тихой речью, иначе False.
    """
    y = ns.noise_reduction_spectral_subtraction(y, sr, normalize=True)

    # Рассчитываем частоту тона в заданном диапазоне F0
    f0, time = pt.extract_f0_voiced(y, sr)

    # Если F0 отсутствует или все значения NaN, это не тихая речь
    if f0 is None or np.all(np.isnan(f0)):
        return False

    # Убираем короткие последовательности значений F0
    valid_f0 = pt.remove_short_sequences(f0, min_length=15)
    if len(valid_f0) == 0:
        return False

    f0_mean = np.mean(valid_f0)
    f0_mean_max = np.max(valid_f0)
    if f0_mean < f0_min or f0_mean > f0_max or f0_mean_max > f0_max:
        return False

    # Рассчитываем интенсивность с учетом озвученных фрагментов
    intensity_db = pt.calculate_pitch_intensity(y, sr, only_speech=True)
    if intensity_db.size == 0:
        return False

    avg_intensity = np.mean(intensity_db)

    # Проверяем, что средняя интенсивность находится в диапазоне для тихой речи
    if not (intensity_min_db <= avg_intensity <= intensity_max_db):
        return False

    # Проверка формант
    formants = fmt.extract_formants_from_segment_fast(y, sr)
    if formants:
        significant_formants = [f for f in formants[:2] if formant_thresholds[0] < f < formant_thresholds[1]]
        if len(significant_formants) < 2:
            return False

    return True

def is_loud_speech(y, sr, intensity_threshold_db=55, spectral_flatness_threshold=0.2, f0_min=80, f0_max=300, formant_thresholds=(300, 3000)):
    """
    Определяет, является ли аудиосигнал громкой речью, используя интенсивность, спектральную плоскость, основной тон (F0) и форманты.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param intensity_threshold_db: Порог интенсивности в децибелах для определения громкой речи.
    :param spectral_flatness_threshold: Порог для спектральной плоскости.
    :param f0_min: Минимальная частота тона (Hz).
    :param f0_max: Максимальная частота тона (Hz).
    :param formant_thresholds: Ожидаемые диапазоны частот для первых двух формант (F1, F2).
    :return: True если сигнал является громкой речью, иначе False.
    """
    y = ns.noise_reduction_spectral_subtraction(y, sr, normalize=True)

    # Рассчитываем интенсивность с учетом озвученных фрагментов
    intensity_db = pt.calculate_pitch_intensity(y, sr, only_speech=True)
    if intensity_db.size == 0:
        return False

    avg_intensity = np.mean(intensity_db)

    # Проверяем, что средняя интенсивность выше порога
    if avg_intensity < intensity_threshold_db:
        return False

    # Рассчитываем спектральную плоскость
    spectral_flatness = librosa.feature.spectral_flatness(y=y)
    avg_spectral_flatness = np.mean(spectral_flatness)
    if avg_spectral_flatness > spectral_flatness_threshold:
        return False

    # Рассчитываем частоту тона в заданном диапазоне F0
    # f0, voiced_flag, _ = librosa.pyin(y, fmin=f0_min, fmax=f0_max)
    f0, time = pt.extract_f0_voiced(y, sr)

    # Если F0 отсутствует или все значения NaN, это не громкая речь
    if f0 is None or np.all(np.isnan(f0)):
        return False

    # Убираем короткие последовательности значений F0
    valid_f0 = pt.remove_short_sequences(f0, min_length=15)
    if len(valid_f0) == 0:
        return False

    f0_mean = np.max(valid_f0)
    if f0_mean < f0_min or f0_mean > f0_max:
        return False

    # Проверка формант
    formants = fmt.extract_formants_from_segment_fast(y, sr)
    if formants:
        significant_formants = [f for f in formants[:2] if formant_thresholds[0] < f < formant_thresholds[1]]
        if len(significant_formants) < 2:
            return False

    return True

def is_whisper(y, sr, f0_min=50, f0_avg = 100, spectral_flatness_threshold=0.4, formant_threshold=500):
    """
    Определяет, является ли аудиосигнал шёпотом, используя отсутствие основного тона (F0),
    высокую спектральную плоскость и отсутствие значимых формантов.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param f0_min: Минимальная частота тона (Hz) для определения наличия F0.
    :param f0_max: Максимальная частота тона (Hz) для определения наличия F0.
    :param spectral_flatness_threshold: Порог для спектральной плоскости, выше которого считается шёпотом.
    :param formant_threshold: Порог для частот формант, ниже которого считается шёпотом.
    :return: True если сигнал является шёпотом, иначе False.
    """
    y = ns.noise_reduction_spectral_subtraction_fast(y, sr)

    # Рассчитываем частоту тона в заданном диапазоне F0
    f0, time = pt.extract_f0_voiced(y, sr)

    # Если F0 отсутствует или все значения NaN, это может указывать на шёпот
    if f0 is None or np.all(np.isnan(f0)):
        return True

    # Убираем короткие последовательности значений F0
    valid_f0 = pt.remove_short_sequences(f0, min_length=5)

    # Если после удаления коротких последовательностей нет валидных значений F0, это шёпот
    if len(valid_f0) == 0:
        return True

    f0_mean = np.mean(valid_f0)
    if f0_mean < f0_min:
        return True
    if f0_mean > f0_avg:
        return False

    # Рассчитываем спектральную плоскость
    spectral_flatness = librosa.feature.spectral_flatness(y=y)
    avg_spectral_flatness = np.mean(spectral_flatness)
    if avg_spectral_flatness > spectral_flatness_threshold:
        return True

    # Проверка формант
    formants = fmt.extract_formants_from_segment_fast(y, sr)
    if formants:
        significant_formants = [f for f in formants[:2] if f >= formant_threshold]  # Смотрим только на первые два форманта
        if len(significant_formants) == 0:
            return True

    return False

def is_scream(y, sr, intensity_threshold_db=80, min_f0=100, max_f0=600, pitch_threshold=400):
    """
    Определяет, является ли аудиосигнал криком, используя интенсивность, частоту основного тона (F0) и спектральные характеристики.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    :param intensity_threshold_db: Порог интенсивности в децибелах для определения крика.
    :param f0_min: Минимальная частота тона (Hz) для крика.
    :param f0_max: Максимальная частота тона (Hz) для крика.
    :param spectral_flatness_threshold: Порог спектральной плоскости, выше которого может быть крик.
    :return: True если сигнал является криком, иначе False.
    """
    y = ns.noise_reduction_spectral_subtraction(y, sr)

    # Рассчитываем частоту тона
    f0, time = pt.extract_f0_voiced(y, sr)
    if len(f0) == 0:
        return False

    valid_f0 = pt.remove_short_sequences(f0, min_length=5)
    if len(valid_f0) == 0:
        return False

    max_pitch = np.max(valid_f0)
    pitch = np.mean(valid_f0)
    if max_pitch >= pitch_threshold and pitch > 100:
        return True

    return False


def compute_volume_trend(y, sr, frame_length=2048, hop_length=512):
    rms = ns.compute_rms(y, frame_length, hop_length)

    # Получаем время для каждого значения RMS
    times = np.arange(len(rms)) * (hop_length / sr)

    # Проводим линейную регрессию
    slope, intercept, r_value, p_value, std_err = linregress(times, rms)

    # Вычисляем предсказанные значения по линейной регрессии
    predicted_rms = intercept + slope * times

    # Вычисляем остатки (разницу между реальными и предсказанными значениями)
    residuals = rms - predicted_rms

    # Вычисляем дисперсию остатков
    variance = np.var(residuals)

    return slope, intercept, times, rms, residuals, variance


def silence_percentage(y, sr, threshold_db=-30):
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)

    silence_frames = np.sum(rms_db < threshold_db)
    total_frames = len(rms_db[0])

    silence_percentage = (silence_frames / total_frames) * 100
    return silence_percentage

def analyze_speech(y, sr, clarity_formants=[1, 2, 3, 4, 5], silence_threshold_db=-30):
    # Load the audio file
    snd = pm.Sound(y, sr)

    # Formant clarity
    formant = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5)
    clarity_scores = []

    for i in clarity_formants:  # Formants F1 to F5
        bandwidths = []
        for t in formant.ts():
            try:
                bw = formant.get_bandwidth_at_time(i, t)
                if bw > 0:
                    bandwidths.append(bw)
            except:
                continue
        if bandwidths:
            clarity_scores.append(np.nanmean(bandwidths))
        else:
            clarity_scores.append(np.nan)

    # Silence percentage
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    silence_frames = np.sum(rms_db < silence_threshold_db)
    total_frames = len(rms_db[0])
    silence_percent = (silence_frames / total_frames) * 100

    # Power Spectral Density
    freqs, psd = ns.compute_power_spectral_density(y, sr)

    return {
        "formant_clarity": clarity_scores,
        "silence_percentage": silence_percent,
        "psd": (freqs, psd)
    }


def formant_clarity(y, sr):
    snd = pm.Sound(y, sr)
    formant = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5)

    clarity_scores = []
    for i in range(1, 6):  # Formants F1 to F5
        bandwidths = []
        for t in formant.ts():
            try:
                bw = formant.get_bandwidth_at_time(i, t)
                if bw > 0:
                    bandwidths.append(bw)
            except:
                continue
        if bandwidths:
            clarity_scores.append(np.nanmean(bandwidths))
        else:
            clarity_scores.append(np.nan)

    return clarity_scores
