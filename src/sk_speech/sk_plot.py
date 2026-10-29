import numpy as np
import librosa
import parselmouth as pm
from parselmouth.praat import call
from . import sk_filters as fl
from . import sk_noise as ns
from . import sk_pitch as pt
from . import sk_formants as fmt
from . import sk_vowels as vw
from . import sk_volume as vm
import matplotlib.pyplot as plt

def plot_formant_trajectory(time_stamps, formant_frequencies, index):
    plt.figure(figsize=(12, 6))
    plt.plot(time_stamps, formant_frequencies, label=f'Formant F{index} Trajectory')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'Formant F{index} Trajectory')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_pitch_trajectory(time, pitch_trajectory):
    plt.figure(figsize=(12, 6))
    plt.plot(time, pitch_trajectory, label='Pitch Trajectory')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Pitch Trajectory')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_trajectory_formants_and_pitch(y, sr, window_size=1024):
    # Получение траектории тона
    pitch_trajectory, time = pt.extract_f0_voiced(y, sr)

    # Инициализация графика
    plt.figure(figsize=(14, 8))

    # График траектории основного тона
    plt.plot(time, pitch_trajectory, label='Pitch', color='black', linewidth=2)

    # Вызов formant_trajectory для формант F1-F5 и построение графиков
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    for index in range(1, 6):  # Форманты F1-F5
        # Получение траектории форманты
        time_stamps, formant_frequencies = fmt.formant_trajectory(y, sr, index, window_size)
        plt.plot(time_stamps, formant_frequencies, label=f'F{index}', color=colors[index - 1], linestyle='--')

    # Настройки графика
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Pitch and Formant Trajectories')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_spectral_slope(times, slopes):
    plt.figure(figsize=(12, 6))
    plt.plot(times, slopes, label='Spectral Slope')
    plt.xlabel('Time (s)')
    plt.ylabel('Spectral Slope')
    plt.title('Spectral Slope of Speech Signal')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_intensity(y, sr):
    """
    Построение графиков интенсивности основного тона и интенсивностей формант.

    :param y: Нормализованный аудиосигнал.
    :param sr: Частота дискретизации.
    """
    hop_length = 512

    # Рассчитываем интенсивность основного тона
    pitch_intensity = pt.calculate_pitch_intensity(y, sr)

    total_time = np.arange(len(pitch_intensity)) * hop_length / sr

    # Создаем график
    plt.figure(figsize=(14, 8))
    plt.plot(total_time, pitch_intensity, label='Pitch Intensity', color='blue')

    # Рассчитываем и добавляем графики интенсивности формант
    colors = ['green', 'red', 'purple', 'orange', 'brown']
    for i in range(1, 6):
        formant_intensity = fmt.calculate_formant_intensity(y, sr, formant_index=i)
        if formant_intensity.size > 0:
            plt.plot(total_time, formant_intensity, label=f'Formant {i} Intensity', color=colors[i-1])

    # Оформление графика
    plt.xlabel('Time (s)')
    plt.ylabel('Intensity (dB)')
    plt.title('Pitch and Formant Intensities')
    plt.legend()
    plt.grid(True)
    plt.show()

def visualize_pitch(input_file, output_file):
    """
    Визуализирует оригинальный и изменённый основной тон.

    Args:
    input_file: str
        Путь к входному аудиофайлу.
    output_file: str
        Путь к выходному аудиофайлу.
    """
    # Загрузка аудиофайлов
    y, sr = librosa.load(input_file, sr=None)
    y_shifted, sr_shifted = librosa.load(output_file, sr=None)

    # Извлечение основного тона
    sound_original = pm.Sound(y, sr)
    pitch_original = call(sound_original, "To Pitch", 0.0, 75, 600)
    f0_original = pitch_original.selected_array['frequency']

    sound_shifted = pm.Sound(y_shifted, sr_shifted)
    pitch_shifted = call(sound_shifted, "To Pitch", 0.0, 75, 600)
    f0_shifted = pitch_shifted.selected_array['frequency']

    # Временные метки
    time_original = np.linspace(0, len(y) / sr, len(f0_original))
    time_shifted = np.linspace(0, len(y_shifted) / sr_shifted, len(f0_shifted))

    # Визуализация
    plt.figure(figsize=(15, 8))

    plt.subplot(3, 1, 1)
    plt.plot(time_original, f0_original, label="Оригинальный тон (F0)")
    plt.xlabel("Время (с)")
    plt.ylabel("Частота (Гц)")
    plt.title("Оригинальный основной тон (F0)")
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(time_shifted, f0_shifted, label="Изменённый тон (F0)", color='r')
    plt.xlabel("Время (с)")
    plt.ylabel("Частота (Гц)")
    plt.title("Изменённый основной тон (F0)")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_original, f0_original, label="Оригинальный тон (F0)")
    plt.plot(time_shifted, f0_shifted, label="Изменённый тон (F0)", color='r')
    plt.xlabel("Время (с)")
    plt.ylabel("Частота (Гц)")
    plt.title("Сравнение оригинального и изменённого основного тона (F0)")
    plt.legend()

    plt.tight_layout()
    plt.show()

def plot_vowel_boundaries(y, sr, vowel_boundaries, threshold):
    # Определение минимальной длины для синхронизации графиков
    min_length = len(y)
    time = np.arange(min_length) / sr
    y = y[:min_length]

    # Визуализация
    plt.figure(figsize=(12, 6))
    plt.plot(time, y, label='Signal')
    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    for boundary, vowel in vowel_boundaries:
        plt.axvline(x=boundary / sr, color='g', linestyle='--', label=vowel)
    plt.title('Signal and Detected Vowel Boundaries')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

def visualize_vowel_boundaries(input_file, vowel_boundaries, threshold=0.1):
    y, sr = librosa.load(input_file, sr=None)
    y = y / np.max(np.abs(y))
    plot_vowel_boundaries(y, sr, vowel_boundaries, threshold)

def visualize_amplified_vowels(original_file, amplified_file, vowel_boundaries):
    # Загрузка файлов
    y_orig, sr_orig = librosa.load(original_file, sr=None)
    y_amplified, sr_amplified = librosa.load(amplified_file, sr=None)

    # Определение минимальной длины для синхронизации графиков
    min_length = min(len(y_orig), len(y_amplified))
    time = np.arange(min_length) / sr_orig
    y_orig = y_orig[:min_length]
    y_amplified = y_amplified[:min_length]

    # Визуализация
    plt.figure(figsize=(18, 12))

    # График оригинального сигнала
    plt.subplot(3, 1, 1)
    plt.plot(time, y_orig, label='Original Signal')
    plt.title('Original Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()

    # Добавление вертикальных линий для границ гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='r', linestyle='--', linewidth=1, alpha=0.7)

    # График увеличенного сигнала
    plt.subplot(3, 1, 2)
    plt.plot(time, y_amplified, label='Amplified Vowels', color='orange', alpha=0.6)
    plt.title('Amplified Vowels Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()

    # Добавление вертикальных линий для границ гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='r', linestyle='--', linewidth=1, alpha=0.7)

    # Сравнительный график
    plt.subplot(3, 1, 3)
    plt.plot(time, y_orig, label='Original Signal', alpha=0.6)
    plt.plot(time, y_amplified, label='Amplified Vowels', color='orange', alpha=0.3)
    plt.title('Comparison of Original and Amplified Signals')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()

    # Добавление вертикальных линий для границ гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='r', linestyle='--', linewidth=1, alpha=0.7)

    plt.tight_layout()
    plt.show()

def compute_energy(signal, frame_length, hop_length):
    energy = np.array([
        np.sum(np.abs(signal[i:i+frame_length])**2)
        for i in range(0, len(signal) - frame_length + 1, hop_length)
    ])
    return energy

def visualize_energy_vowels(original_file, amplified_file, vowel_boundaries):
    # Загрузка файлов
    y_orig, sr_orig = librosa.load(original_file, sr=None)
    y_amplified, sr_amplified = librosa.load(amplified_file, sr=None)

    # Определение минимальной длины для синхронизации графиков
    min_length = min(len(y_orig), len(y_amplified))
    y_orig = y_orig[:min_length]
    y_amplified = y_amplified[:min_length]

    # Параметры окон для вычисления энергии
    frame_length = int(0.025 * sr_orig)  # 25 ms окна
    hop_length = int(0.01 * sr_orig)     # 10 ms шаг

    # Вычисление энергии
    energy_orig = compute_energy(y_orig, frame_length, hop_length)
    energy_amplified = compute_energy(y_amplified, frame_length, hop_length)

    # Временная шкала для энергии
    time_energy = np.arange(len(energy_orig)) * hop_length / sr_orig

    # Визуализация
    plt.figure(figsize=(18, 12))

    # График энергии оригинального сигнала
    plt.subplot(3, 1, 1)
    plt.plot(time_energy, energy_orig, label='Original Signal Energy')
    plt.title('Original Signal Energy')
    plt.xlabel('Time (s)')
    plt.ylabel('Energy')
    plt.legend()

    # Добавление вертикальных линий для границ гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='r', linestyle='--', linewidth=1, alpha=0.7)

    # График энергии сигнала с увеличенной энергией формант
    plt.subplot(3, 1, 2)
    plt.plot(time_energy, energy_amplified, label='Energy-Amplified Vowels', color='orange', alpha=0.6)
    plt.title('Energy-Amplified Vowels Signal Energy')
    plt.xlabel('Time (s)')
    plt.ylabel('Energy')
    plt.legend()

    # Добавление вертикальных линий для границ гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='r', linestyle='--', linewidth=1, alpha=0.7)

    # Сравнительный график энергии
    plt.subplot(3, 1, 3)
    plt.plot(time_energy, energy_orig, label='Original Signal Energy', alpha=0.6)
    plt.plot(time_energy, energy_amplified, label='Energy-Amplified Vowels', color='orange', alpha=0.3)
    plt.title('Comparison of Original and Energy-Amplified Signals Energy')
    plt.xlabel('Time (s)')
    plt.ylabel('Energy')
    plt.legend()

    # Добавление вертикальных линий для границ гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='r', linestyle='--', linewidth=1, alpha=0.7)

    plt.tight_layout()
    plt.show()

def visualize_shifted_formants(original_file, shifted_file,
                               show_formant_1=True, show_formant_2=True, show_formant_3=True, show_formant_4=True):
    # Загрузка аудио файлов
    y_orig, sr_orig = librosa.load(original_file, sr=None)
    y_shifted, sr_shifted = librosa.load(shifted_file, sr=None)

    # Извлечение частот формант из оригинального и сдвинутого файлов
    times_orig, formants_orig = fmt.extract_formant_frequencies(y_orig, sr_orig)
    times_shifted, formants_shifted = fmt.extract_formant_frequencies(y_shifted, sr_shifted)

    # Получение границ гласных
    vowel_boundaries = vw.detect_vowel_boundaries(y_orig, sr_orig)

    plt.figure(figsize=(14, 10))

    # Визуализация частот формант для оригинального аудио
    if show_formant_1:
        plt.plot(times_orig, formants_orig[1], label='Formant 1 (Original)', linestyle='-', marker='o')
    if show_formant_2:
        plt.plot(times_orig, formants_orig[2], label='Formant 2 (Original)', linestyle='-', marker='o')
    if show_formant_3:
        plt.plot(times_orig, formants_orig[3], label='Formant 3 (Original)', linestyle='-', marker='o')
    if show_formant_4:
        plt.plot(times_orig, formants_orig[4], label='Formant 4 (Original)', linestyle='-', marker='o')

    # Визуализация частот формант для сдвинутого аудио
    if show_formant_1:
        plt.plot(times_shifted, formants_shifted[1], label='Formant 1 (Shifted)', linestyle='--', marker='x')
    if show_formant_2:
        plt.plot(times_shifted, formants_shifted[2], label='Formant 2 (Shifted)', linestyle='--', marker='x')
    if show_formant_3:
        plt.plot(times_shifted, formants_shifted[3], label='Formant 3 (Shifted)', linestyle='--', marker='x')
    if show_formant_4:
        plt.plot(times_shifted, formants_shifted[4], label='Formant 4 (Shifted)', linestyle='--', marker='x')

    # Добавление вертикальных линий для гласных
    for boundary, _ in vowel_boundaries:
        plt.axvline(x=boundary / sr_orig, color='gray', linestyle='--', linewidth=1, alpha=0.6)

    plt.title('Formant Frequencies in Original and Shifted Audio')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def visualize_spectrograms(input_file, output_file):
    """
    Визуализирует спектрограммы аудиофайлов до и после фильтрации шума.

    Args:
    input_file: str
        Путь к входному аудиофайлу (до фильтрации шума).
    output_file: str
        Путь к выходному аудиофайлу (после фильтрации шума).
    """
    # Загрузка аудиофайлов
    y_before, sr_before = librosa.load(input_file, sr=None)
    y_after, sr_after = librosa.load(output_file, sr=None)

    # Вычисление STFT
    S_before = np.abs(librosa.stft(y_before))
    S_after = np.abs(librosa.stft(y_after))

    # Визуализация
    plt.figure(figsize=(15, 8))

    # Спектрограмма до фильтрации шума
    plt.subplot(2, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(S_before, ref=np.max), sr=sr_before, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Спектрограмма до фильтрации шума')

    # Спектрограмма после фильтрации шума
    plt.subplot(2, 1, 2)
    librosa.display.specshow(librosa.amplitude_to_db(S_after, ref=np.max), sr=sr_after, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Спектрограмма после фильтрации шума')

    plt.tight_layout()
    plt.show()

def visualize_remove_noise(input_file, output_file):
    """
    Визуализирует частотные спектры аудиофайлов до и после фильтрации шума.

    Args:
    input_file: str
        Путь к входному аудиофайлу (до фильтрации шума).
    output_file: str
        Путь к выходному аудиофайлу (после фильтрации шума).
    """
    # Загрузка аудиофайлов
    y_before, sr_before = librosa.load(input_file, sr=None)
    y_after, sr_after = librosa.load(output_file, sr=None)

    # Вычисление STFT
    stft_before = librosa.stft(y_before)
    stft_after = librosa.stft(y_after)

    # Получение амплитудных спектров
    magnitude_before, _ = librosa.magphase(stft_before)
    magnitude_after, _ = librosa.magphase(stft_after)

    # Среднее значение амплитуд по времени
    mean_magnitude_before = np.mean(magnitude_before, axis=1)
    mean_magnitude_after = np.mean(magnitude_after, axis=1)

    # Частоты
    frequencies_before = librosa.fft_frequencies(sr=sr_before)
    frequencies_after = librosa.fft_frequencies(sr=sr_after)

    # Визуализация
    plt.figure(figsize=(15, 8))

    # График частотного спектра до фильтрации шума
    plt.subplot(3, 1, 1)
    plt.plot(frequencies_before, 20 * np.log10(mean_magnitude_before + 1e-6), label="До фильтрации шума")
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда (дБ)")
    plt.title("Частотный спектр до фильтрации шума")
    plt.legend()

    # График частотного спектра после фильтрации шума
    plt.subplot(3, 1, 2)
    plt.plot(frequencies_after, 20 * np.log10(mean_magnitude_after + 1e-6), label="После фильтрации шума", color='r')
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда (дБ)")
    plt.title("Частотный спектр после фильтрации шума")
    plt.legend()

    # Совместный график
    plt.subplot(3, 1, 3)
    plt.plot(frequencies_before, 20 * np.log10(mean_magnitude_before + 1e-6), label="До фильтрации шума")
    plt.plot(frequencies_after, 20 * np.log10(mean_magnitude_after + 1e-6), label="После фильтрации шума", color='r')
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда (дБ)")
    plt.title("Сравнение частотных спектров до и после фильтрации шума")
    plt.legend()

    plt.tight_layout()
    plt.show()

def plot_psd(freqs, psd, title='Power Spectral Density'):
    """
    Отображает спектральную плотность мощности (PSD).

    :param freqs: Частоты.
    :param psd: Значения PSD.
    :param title: Заголовок графика.
    """
    plt.figure(figsize=(10, 6))
    plt.semilogy(freqs, psd)
    plt.title(title)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('PSD (dB/Hz)')
    plt.grid(True)
    plt.show()

def plot_spectral_flatness(y, sr, n_fft=2048, hop_length=512):
    """
    Строит график спектральной плоскости.

    :param y: Аудиосигнал.
    :param sr: Частота дискретизации.
    :param n_fft: Длина окна для вычисления STFT.
    :param hop_length: Шаг между окнами.
    """
    spectral_flatness = ns.compute_spectral_flatness(y, frame_length = n_fft, hop_length = hop_length)

    plt.figure(figsize=(10, 6))
    plt.plot(spectral_flatness.T, alpha=0.8)
    plt.title('Spectral Flatness')
    plt.xlabel('Time Frames')
    plt.ylabel('Flatness')
    plt.grid(True)
    plt.show()


