import numpy as np
from scipy.io.wavfile import write

# 1. Расчет временно изменяющихся частот гармоник вокруг центральной частоты
def calculate_harmonic_frequencies(Freq_range, Bw_range, N, t):
    Freq_start, Freq_end = Freq_range
    Bw_start, Bw_end = Bw_range

    # Плавное изменение центральной частоты и ширины канала
    Freq_t = np.linspace(Freq_start, Freq_end, len(t))
    Bw_t = np.linspace(Bw_start, Bw_end, len(t))

    frequencies = []
    for i, (Freq, Bw) in enumerate(zip(Freq_t, Bw_t)):
        half_range = Bw / 2
        step = Bw / (N - 1)
        freqs = [Freq + k * step - half_range for k in range(N)]
        frequencies.append(freqs)

    return np.array(frequencies)

# 2. Расчет временно изменяющихся амплитуд гармоник
def calculate_harmonic_amplitudes(Freq_range, f_k, Amp_range, Bw_range, t):
    Freq_start, Freq_end = Freq_range
    Amp_start, Amp_end = Amp_range
    Bw_start, Bw_end = Bw_range

    # Плавное изменение амплитуды и ширины канала
    Amp_t = np.linspace(Amp_start, Amp_end, len(t))
    Bw_t = np.linspace(Bw_start, Bw_end, len(t))

    amplitudes = []
    for i, (Freq, Bw, Amp) in enumerate(zip(np.linspace(Freq_start, Freq_end, len(t)), Bw_t, Amp_t)):
        sigma = Bw / 2  # Гауссовское затухание
        amp0 = Amp / (i+1)
        amps = [amp0 * np.exp(-0.5 * ((freq - Freq) / sigma)**2) for freq in f_k[i]]
        amplitudes.append(amps)

    return np.array(amplitudes)

# 3. Генерация временной оси
def generate_time_axis(rate, duration):
    return np.linspace(0, duration, int(rate * duration), endpoint=False)

# 4. Генерация сигналов для всех гармоник
def generate_harmonic_signal(f_k, A_k, t):
    signals = []
    for i in range(len(t)):
        harmonic_signal = [A * np.sin(2 * np.pi * f * t[i]) for f, A in zip(f_k[i], A_k[i])]
        signals.append(np.sum(harmonic_signal))
    return np.array(signals)

# 5. Сохранение итогового сигнала в WAV-файл
def save_to_wav(signal, rate, filename):
    # Масштабируем сигнал в диапазон int16
    signal = signal / np.max(np.abs(signal))  # Нормализация
    signal = (signal * 32767).astype(np.int16)
    write(filename, rate, signal)

# 6. Функция для создания сигнала с плавными изменениями параметров
def create_signal(Freq_range, Amp_range, Bw_range, duration, rate=44100, num_harmonics=5):
    # Генерация временной оси
    t = generate_time_axis(rate, duration)

    # Генерация частот и амплитуд гармоник
    f_k = calculate_harmonic_frequencies(Freq_range, Bw_range, num_harmonics, t)
    A_k = calculate_harmonic_amplitudes(Freq_range, f_k, Amp_range, Bw_range, t)

    # Генерация итогового сигнала
    signal = generate_harmonic_signal(f_k, A_k, t)

    return signal

# 7. Функция для объединения нескольких сигналов
def combine_signals(signals):
    # Приведение всех сигналов к одинаковой длине
    min_length = min(len(signal) for signal in signals)
    aligned_signals = [signal[:min_length] for signal in signals]

    # Суммирование сигналов
    combined_signal = np.sum(aligned_signals, axis=0)

    return combined_signal

# Основной блок для тестирования функций
if __name__ == "__main__":
    # Параметры для формант буквы "А"
    F1_params = ((850, 950), (1.0, 1.0), (50, 50))
    F2_params = ((1200, 1300), (0.5, 0.5), (100, 100))
    F0_params = ((200, 220), (0.2, 0.2), (50, 50))

    duration = 1.0  # Длительность, сек
    rate = 44100   # Частота дискретизации

    # Создание сигналов для каждой форманты
    F1_signal = create_signal(*F1_params, duration, rate, num_harmonics=5)
    F2_signal = create_signal(*F2_params, duration, rate, num_harmonics=5)
    F0_signal = create_signal(*F0_params, duration, rate, num_harmonics=3)

    # Объединение сигналов
    combined_signal = combine_signals([F1_signal, F2_signal, F0_signal])

    # Сохранение объединенного сигнала в файл
    save_to_wav(combined_signal, rate, "combined_vowel_A.wav")

    print("Сигнал успешно сохранен в файл 'combined_vowel_A.wav'")
