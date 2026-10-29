import librosa
import numpy as np
from pydub import AudioSegment
from . import sk_filters as fl

def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

def compute_rms(y, frame_length=2048, hop_length=512):
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)
    return rms.flatten()

# Вычисление спектральной разреженности
def compute_spectral_flatness(y, frame_length=2048, hop_length=512):
    flatness = librosa.feature.spectral_flatness(y=y, n_fft=frame_length, hop_length=hop_length)
    return flatness.flatten()

# Вычисляет спектральную плотность мощности (PSD) аудиосигнала.
def compute_power_spectral_density(y, sr, n_fft=2048, hop_length=512):
    y = y / np.max(np.abs(y))  # Нормализация аудиосигнала
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    psd = np.mean(np.abs(stft)**2 / n_fft, axis=1)  # Среднее значение PSD по временным кадрам
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    return freqs, psd

def analyze_noise_in_psd(y, sr, speech_band=(300, 3400), noise_threshold_db=-20):
    """
    Анализирует PSD для определения присутствия шума и его уровня.

    :param y: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param speech_band: Диапазон частот, характерный для речи (Hz).
    :param noise_threshold_db: Порог уровня шума в децибелах.
    :return: Признак наличия шума и уровень шума.
    """
    freqs, psd = compute_power_spectral_density(y, sr)

    # Определяем индексы частот, не относящихся к речевому диапазону
    noise_indices = np.where((freqs < speech_band[0]) | (freqs > speech_band[1]))[0]

    if len(noise_indices) == 0:
        raise ValueError("Не найдено частот за пределами указанного диапазона. Проверьте диапазон частот.")

    # Средний уровень PSD в шумовом диапазоне
    noise_level = np.mean(psd[noise_indices])

    # Применяем логарифмическое преобразование для получения значения в децибелах
    if noise_level <= 0:
        noise_level_db = -np.inf
    else:
        noise_level_db = 10 * np.log10(noise_level)

    # Определение наличия шума
    noise_present = noise_level_db > noise_threshold_db

    return noise_present, noise_level_db

def analyze_noise_level_sf(y, sr, n_fft=2048, hop_length=512, flatness_threshold=0.3):
    """
    Анализирует уровень шума в аудиосигнале на основе спектральной разреженности.

    :param y: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param n_fft: Длина окна для вычисления STFT.
    :param hop_length: Шаг между окнами.
    :param flatness_threshold: Порог для спектральной плоскости, выше которого считается шумом.
    :return: Уровень шума.
    """
    spectral_flatness = compute_spectral_flatness(y, n_fft, hop_length)
    avg_flatness = np.mean(spectral_flatness)

    is_noisy = avg_flatness > flatness_threshold

    return is_noisy, avg_flatness

def analyze_noise_level_rms(y, sr, frame_length=2048, hop_length=512, noise_threshold_db=-40):
    """
    Анализирует уровень шума в аудиосигнале на основе RMS значений.

    :param y: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param frame_length: Длина окна для вычисления RMS.
    :param hop_length: Шаг между окнами.
    :param noise_threshold_db: Порог для определения шума в децибелах.
    :return: Уровень шума, является ли сигнал шумным.
    """
    # Вычисляем RMS значения
    rms = compute_rms(y, frame_length, hop_length)
    
    # Преобразуем RMS значения в децибелы
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    
    # Находим средний уровень шума в местах, где уровень RMS ниже порога
    noise_rms_db = rms_db[rms_db < noise_threshold_db]
    avg_noise_level_db = np.mean(noise_rms_db) if len(noise_rms_db) > 0 else -np.inf
    
    # Определяем, является ли сигнал шумным
    is_noisy = avg_noise_level_db > noise_threshold_db
    
    return is_noisy, avg_noise_level_db

def analyze_noise_level(y, sr, noise_threshold_db=-40, spectral_flatness_threshold=0.5):
    # RMS Analysis
    is_noisy_rms, avg_noise_level_db = analyze_noise_level_rms(y, sr, noise_threshold_db=noise_threshold_db)

    # Spectral Flatness Analysis
    is_noisy_flatness, avg_flatness = analyze_noise_level_sf(y, sr, flatness_threshold=spectral_flatness_threshold)

    # Power Spectral Density Analysis
    is_noisy_psd, avg_psd = analyze_noise_in_psd(y, sr, noise_threshold_db=noise_threshold_db)

    # Normalizing values
    normalized_rms = normalize(avg_noise_level_db, -80, 0)  # Assuming dB scale from -80 to 0
    normalized_flatness = normalize(avg_flatness, 0, 1)  # Spectral flatness is naturally between 0 and 1
    normalized_psd = normalize(avg_psd, -80, 0)  # Assuming dB scale from -80 to 0

    # Combining values with equal weights
    combined_noise_level = (normalized_rms + normalized_flatness + normalized_psd) / 3

    return {
        'avg_noise_level_db': avg_noise_level_db,
        'is_noisy_rms': is_noisy_rms,
        'avg_flatness': avg_flatness,
        'is_noisy_flatness': is_noisy_flatness,
        'avg_psd': avg_psd,
        'is_noisy_psd': is_noisy_psd,
        'combined_noise_level': combined_noise_level
    }

def spectral_subtraction(y, sr, n_fft=2048, hop_length=512, noise_estimation_method='psd'):
    # Вычисляем STFT
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft)
    phase = np.angle(stft)

    # Оценка спектра шума
    if noise_estimation_method == 'psd':
        freqs, psd = compute_power_spectral_density(y, sr, n_fft, hop_length)
        noise_psd = np.mean(psd)  # Среднее значение PSD по всем частотам
        noise_psd = np.expand_dims(noise_psd, axis=0)  # Делается расширение размерности для вычитания
        noise_psd = np.tile(noise_psd, (magnitude.shape[1], 1)).T  # Копируем шум по временным кадрам
    elif noise_estimation_method == 'sf':
        flatness = compute_spectral_flatness(y, n_fft, hop_length)
        avg_flatness = np.mean(flatness)
        noise_psd = np.mean(magnitude ** 2, axis=1) * avg_flatness
        noise_psd = np.expand_dims(noise_psd, axis=1)  # Делается расширение размерности для вычитания
    else:
        raise ValueError("Неизвестный метод оценки шума")

    # Устранение шума
    enhanced_magnitude = magnitude - noise_psd
    enhanced_magnitude[enhanced_magnitude < 0] = 0  # Убираем отрицательные значения

    # Восстановление сигнала
    enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
    enhanced_y = librosa.istft(enhanced_stft, hop_length=hop_length)

    return enhanced_y

def spectral_subtraction2(y, sr, noise_psd, n_fft=2048, hop_length=512):
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft)
    phase = np.angle(stft)

    # Устранение шума
    noise_psd = np.expand_dims(noise_psd, axis=0)  # Изменяем размерность для вычитания
    enhanced_magnitude = magnitude - noise_psd
    enhanced_magnitude[enhanced_magnitude < 0] = 0  # Убираем отрицательные значения

    # Восстановление сигнала
    enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
    enhanced_y = librosa.istft(enhanced_stft, hop_length=hop_length)

    return enhanced_y


def estimate_noise_psd(y, sr, frame_length=2048, hop_length=512):
    psd = compute_power_spectral_density(y, sr, n_fft=frame_length, hop_length=hop_length)[1]
    spectral_flatness = compute_spectral_flatness(y, frame_length=frame_length, hop_length=hop_length)
    avg_flatness = np.mean(spectral_flatness)

    # Оценка уровня шума на основе PSD и спектральной разреженности
    avg_psd = np.mean(psd)
    noise_psd = avg_psd * avg_flatness
    return noise_psd


def analyze_noise_level2(y, sr, frame_length=2048, hop_length=512, noise_threshold_db=-40, flatness_threshold=0.3):
    # Анализ спектральной разреженности
    spectral_flatness = compute_spectral_flatness(y, frame_length, hop_length)
    avg_flatness = np.mean(spectral_flatness)
    is_noisy_flatness = avg_flatness > flatness_threshold

    # Анализ RMS
    rms = compute_rms(y, frame_length, hop_length)
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    noise_rms_db = rms_db[rms_db < noise_threshold_db]
    avg_noise_level_db = np.mean(noise_rms_db) if len(noise_rms_db) > 0 else -np.inf
    is_noisy_rms = avg_noise_level_db > noise_threshold_db

    return is_noisy_rms, avg_noise_level_db, is_noisy_flatness, avg_flatness

def noise_reduction_spectral_subtraction_fast(y, sr, noise_profile_sec=0.5, num_iterations=2):
    # Compute STFT of the input signal
    try:
        stft = librosa.stft(y)
    except:
        return None
    magnitude, phase = librosa.magphase(stft)

    # Estimate the noise profile from the first `noise_profile_sec` seconds
    num_noise_samples = int(noise_profile_sec * sr)
    noise_profile = np.mean(magnitude[:, :num_noise_samples], axis=1)

    # Apply spectral subtraction iteratively
    for _ in range(num_iterations):
        magnitude = np.maximum(magnitude - noise_profile[:, np.newaxis], 0)

    # Reconstruct the denoised signal using the phase
    stft_denoised = magnitude * phase
    y_denoised = librosa.istft(stft_denoised)

    # Save the denoised audio
    return y_denoised

def noise_reduction_spectral_subtraction(y, sr, noise_profile_sec=0.5, num_iterations=2,
                                         high_pass=False, low_pass=False, normalize=False, target_dBFS=-20.0):
    y_denoised = noise_reduction_spectral_subtraction_fast(y, sr, noise_profile_sec, num_iterations)

    # Apply high-pass and low-pass filters if enabled
    if high_pass:
        y_denoised = fl.apply_high_pass_filter(y_denoised, sr, cutoff=100)
    if low_pass:
        y_denoised = fl.apply_low_pass_filter(y_denoised, sr, cutoff=8000)

    # Normalize the amplitude if enabled
    if normalize:
        y_denoised = fl.normalize_audio(y_denoised)

    # Normalize using pydub for additional control if enabled
    # if normalize:
    #     audio = AudioSegment.from_wav(output_file)
    #     normalized_audio = fl.match_target_amplitude(audio, target_dBFS)
    #     normalized_audio.export(output_file, format="wav")

    # Save the denoised audio
    return y_denoised


# Function to apply noise reduction
def apply_noise_reduction(y, noise_reduction_factor=0.3):
    noise_gate_threshold = noise_reduction_factor * np.max(np.abs(y))
    y_reduced_noise = np.where(np.abs(y) < noise_gate_threshold, 0, y)
    return y_reduced_noise

# Добавляет шум с низкой амплитудой.
def add_noise(y, noise_amplitude=0.005):
    noise = np.random.randn(len(y)) * noise_amplitude
    y_noisy = y + noise
    return y_noisy

def remove_noise(y, sr, method='lowpass', **kwargs):
    # Нормализация амплитуды
    y = fl.normalize_audio(y)

    # Применение выбранного метода фильтрации
    if method == 'lowpass':
        cutoff_freq = kwargs.get('cutoff_freq', 1500)  # Частота среза для фильтра нижних частот
        y_filtered = fl.apply_low_pass_filter(y, sr, cutoff_freq)
    elif method == 'highpass':
        cutoff_freq = kwargs.get('cutoff_freq', 250)   # Частота среза для фильтра верхних частот
        y_filtered = fl.apply_high_pass_filter(y, sr, cutoff_freq)
    elif method == 'median':
        window_size = kwargs.get('window_size', 25)     # Размер окна для медианного фильтра
        y_filtered = fl.apply_median_filter(y, window_size)
    elif method == 'moving_average':
        window_size = kwargs.get('window_size', 41)    # Размер окна для скользящего среднего
        y_filtered = fl.apply_moving_average(y, window_size)
    else:
        raise ValueError(f"Unknown method: {method}")

    return y_filtered
