import random

import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
from sk_speech import sk_volume as vm

def generate_base_signal(A, F, BW, duration, sample_rate):
    """
    Generate the base sine wave signal.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    base_signal = A * np.sin(2 * np.pi * F * t * 0.1)
    return base_signal


def fractal_detailing_recursive(F, A, BW, duration, sample_rate, level, scale, noise_factor,
                                a1, b1, a2, b2, a3, b3, a4, b4, a5, b5):
    """
    Рекурсивная функция для создания фрактального сигнала с тиражированием частей на каждом уровне.
    """
    # Если достигли базового уровня, генерируем сигнал для данной частоты F
    if level == 0:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        amp = A * np.sin(2 * np.pi * t * scale / duration)
        freq = F + BW * np.sin(2 * np.pi * t * scale / duration)
        base_signal = amp * np.sin(2 * np.pi * freq * t * scale)
        # base_signal = A * np.sin(2 * np.pi * F * t)
        # base_signal = (
        #                (A*a1) * np.sin(2 * np.pi * (F*b1*scale) * t + 0.5) +
        #                (A*a2) * np.sin(2 * np.pi * (F*b2*scale) * t + 0.1) +
        #                (A*a3) * np.sin(2 * np.pi * (F*b3*scale) * t + 3) +
        #                (A*a4) * np.sin(2 * np.pi * (F*b4*scale) * t + 0.7) +
        #                (A*a5) * np.sin(2 * np.pi * (F*b5*scale) * t + 0.18) +
        #                (A*a1) * np.sin(1 * np.pi * (F*b1*scale) * t + 0.5) +
        #                (A*a2) * np.sin(1.4 * np.pi * (F*b2*scale) * t + 0.1) +
        #                (A*a3) * np.sin(1.7 * np.pi * (F*b3*scale) * t + 3) +
        #                (A*a4) * np.sin(-0.3 * np.pi * (F*b4*scale) * t + 0.7) +
        #                (A*a5) * np.sin(-4.2 * np.pi * (F*b5*scale) * t + 0.18) +
        #                (A*a1) * np.cos(7.3 * np.pi * (F*b1*scale) * t + 0.5) +
        #                (A*a2) * np.cos(-2.6 * np.pi * (F*b2*scale) * t + 0.1) +
        #                (A*a3) * np.cos(-6.2 * np.pi * (F*b3*scale) * t + 3) +
        #                (A*a4) * np.cos(2.6 * np.pi * (F*b4*scale) * t + 0.7) +
        #                (A*a5) * np.cos(-2.3 * np.pi * (F*b5*scale) * t + 0.18) +
        #                (A*a1) * np.cos(3.2 * np.pi * (F*b1*scale) * t + 0.5) +
        #                (A*a2) * np.cos(3.2 * np.pi * (F*b2*scale) * t + 0.1) +
        #                (A*a3) * np.cos(1.7 * np.pi * (F*b3*scale) * t + 3) +
        #                (A*a4) * np.cos(0.3 * np.pi * (F*b4*scale) * t + 0.7) +
        #                (A*a5) * np.cos(2.2 * np.pi * (F*b5*scale) * t + 0.18)
        #                )
        return base_signal

    # Задаем параметры текущего уровня
    current_amplitude = A / (2 ** level) * (1 + noise_factor * level * np.random.randn())
    current_bandwidth = BW / (2 ** level)

    # Определяем два смещенных значения частоты для подуровней
    shift_noise1 = noise_factor * level * np.random.randn()
    shift_noise2 = noise_factor * level * np.random.randn()
    shift = current_bandwidth / 2
    freq1 = F + shift * (1 + shift_noise1)
    freq2 = F - shift * (1 + shift_noise2)

    # Длительность для каждого подуровня
    split_duration = duration / 2

    # Генерируем сигналы для подуровней и вызываем рекурсию для детализации
    part_signal1 = fractal_detailing_recursive(freq1, current_amplitude, BW, split_duration, sample_rate, level - 1,
                                               scale*2, noise_factor, a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
    part_signal2 = fractal_detailing_recursive(freq2, current_amplitude, BW, split_duration, sample_rate, level - 1,
                                               scale*2, noise_factor, a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)

    # Тиражируем подуровни, чтобы заполнить длительность исходного уровня
    extended_part_signal1 = np.tile(part_signal1, int(np.ceil(duration / split_duration)))[:int(sample_rate * duration)]
    extended_part_signal2 = np.tile(part_signal2, int(np.ceil(duration / split_duration)))[:int(sample_rate * duration)]

    # Суммируем два подуровня для текущей частоты
    detailed_signal = extended_part_signal1 + extended_part_signal2

    return detailed_signal

def fractal_detailing3(base_signal, A, F, BW, duration, sample_rate, level, noise_factor=0.001):
    """
    Рекурсивная функция для создания фрактальной детализации сигнала.
    На каждом уровне сигнал делится на части, каждая из которых детализируется.
    """
    if level == 0:
        return base_signal  # Базовый случай: возвращаем исходный сигнал на самом низком уровне

    # Задаем параметры текущего уровня
    current_amplitude = A / (2 ** level) * (1 + noise_factor * level * np.random.randn())
    current_bandwidth = BW / (2 ** level) * (1 + noise_factor * level * np.random.randn())
    num_splits = 2 ** level
    split_duration = duration / num_splits
    t = np.linspace(0, split_duration, int(sample_rate * split_duration), endpoint=False)

    # Сигнал уровня, который будет складываться из детализированных подфракталов
    level_signal = np.zeros_like(base_signal)

    # Генерация и смешивание сигналов для каждой части
    for i in range(num_splits):
        # Добавляем слабый шум к частотному сдвигу
        shift_noise = noise_factor * level * np.random.randn()  # Шум для сдвига частоты
        shift = ((-1) ** i * current_bandwidth / 2) * (1 + shift_noise)
        freq = F + shift

        # Генерация сигнала с добавлением шума
        part_signal_noise = noise_factor * level * np.random.randn(len(t))  # Шум для сигнала
        v = 2 * np.pi * freq * t * 0.1
        part_signal = current_amplitude * np.sin(v) + part_signal_noise

        # Расширяем часть сигнала, чтобы соответствовать длине исходного сигнала
        extended_part_signal = np.tile(part_signal, int(np.ceil(len(base_signal) / len(part_signal))))[:len(base_signal)]

        # Рекурсивный вызов для каждой части с уменьшением уровня
        detailed_part_signal = fractal_detailing(extended_part_signal, A, F, BW, duration, sample_rate, level - 1)

        # Смешиваем подфрактал в текущий сигнал уровня
        level_signal += detailed_part_signal

    # Объединяем сигнал уровня с исходным сигналом
    detailed_signal = base_signal + level_signal

    return detailed_signal

def fractal_detailing2(base_signal, A, F, BW, duration, sample_rate, levels):
    """
    Apply fractal detailing to the base signal by progressively splitting and mixing.
    """
    detailed_signal = np.copy(base_signal)  # Start with the base signal

    for level in range(1, levels + 1):
        # Define parameters for the current level
        current_amplitude = A / (2 ** level)
        current_bandwidth = BW / (2 ** level)
        num_splits = 2 ** level
        split_duration = duration / num_splits
        t = np.linspace(0, split_duration, int(sample_rate * split_duration), endpoint=False)

        # Generate and mix signals for each split part
        level_signal = np.zeros_like(base_signal)
        for i in range(num_splits):
            # Generate sub-signal with slight frequency shift
            shift = (-1) ** i * current_bandwidth / 2
            freq = F + shift
            part_signal = current_amplitude * np.sin(2 * np.pi * freq * t)

            # Extend the part signal to match the duration of the original signal
            extended_part_signal = np.tile(part_signal, int(np.ceil(len(base_signal) / len(part_signal))))[
                                   :len(base_signal)]

            # Mix into the level signal
            level_signal += extended_part_signal

        # Combine the level signal into the detailed signal
        detailed_signal += level_signal

    return detailed_signal


# Parameters for the base signal
A = 0.1       # Initial amplitude
F = 150       # Base frequency in Hz (e.g., A4 pitch)
BW = 100       # Base bandwidth (spread around frequency in Hz)
duration = 5.0  # Duration in seconds
sample_rate = 44100  # Sample rate for audio
N = 10         # Number of fractal levels for detailing
noise_factor = 0.01  # Коэффициент шума

a1 = random.uniform(0.5, 2.0)
b1 = random.uniform(0.5, 2.0)
a2 = random.uniform(0.5, 2.0)
b2 = random.uniform(0.5, 2.0)
a3 = random.uniform(0.5, 2.0)
b3 = random.uniform(0.5, 2.0)
a4 = random.uniform(0.5, 2.0)
b4 = random.uniform(0.5, 2.0)
a5 = random.uniform(0.5, 2.0)
b5 = random.uniform(0.5, 2.0)

# # Generate the base signal
# base_signal = generate_base_signal(A, F, BW, duration, sample_rate)
# # Apply fractal detailing
# signal_pitch = fractal_detailing(base_signal, A, F, BW, duration, sample_rate, N, noise_factor)

signal_pitch = fractal_detailing_recursive(F, A, BW, duration, sample_rate, N, 1.0, noise_factor,
                                           a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
# To save the output:
signal_pitch = np.int16(signal_pitch / np.max(np.abs(signal_pitch)) * 32767)
write("fractal_pitch.wav", sample_rate, signal_pitch)

# Plot for visualization
plt.figure(figsize=(10, 4))
plt.plot(signal_pitch)  # Plot a small sample of the signal for clarity
plt.title("Sample of Fractal Detailed Signal")
plt.xlabel("Sample")
plt.ylabel("Amplitude")
plt.show()


# formant 1
a1 = random.uniform(0.5, 2.0)
b1 = random.uniform(0.5, 2.0)
a2 = random.uniform(0.5, 2.0)
b2 = random.uniform(0.5, 2.0)
a3 = random.uniform(0.5, 2.0)
b3 = random.uniform(0.5, 2.0)
a4 = random.uniform(0.5, 2.0)
b4 = random.uniform(0.5, 2.0)
a5 = random.uniform(0.5, 2.0)
b5 = random.uniform(0.5, 2.0)

A = 0.5       # Initial amplitude
F = 1500       # Base frequency in Hz (e.g., A4 pitch)
BW = 50       # Base bandwidth (spread around frequency in Hz)
# base_signal = generate_base_signal(A, F, BW, duration, sample_rate)
# signal_formant1 = fractal_detailing(base_signal, A, F, BW, duration, sample_rate, N, noise_factor)
signal_formant1 = fractal_detailing_recursive(F, A, BW, duration, sample_rate, N, 1.0, noise_factor,
                                             a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
signal_formant1 = np.int16(signal_formant1 / np.max(np.abs(signal_formant1)) * 32767)
write("fractal_formant1.wav", sample_rate, signal_formant1)

# formant 2
a1 = random.uniform(0.5, 2.0)
b1 = random.uniform(0.5, 2.0)
a2 = random.uniform(0.5, 2.0)
b2 = random.uniform(0.5, 2.0)
a3 = random.uniform(0.5, 2.0)
b3 = random.uniform(0.5, 2.0)
a4 = random.uniform(0.5, 2.0)
b4 = random.uniform(0.5, 2.0)
a5 = random.uniform(0.5, 2.0)
b5 = random.uniform(0.5, 2.0)

A = 0.5       # Initial amplitude
F = 2000       # Base frequency in Hz (e.g., A4 pitch)
BW = 100       # Base bandwidth (spread around frequency in Hz)
# base_signal = generate_base_signal(A, F, BW, duration, sample_rate)
# signal_formant2 = fractal_detailing(base_signal, A, F, BW, duration, sample_rate, N, noise_factor)
signal_formant2 = fractal_detailing_recursive(F, A, BW, duration, sample_rate, N, 1.0, noise_factor,
                                              a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
signal_formant2 = np.int16(signal_formant2 / np.max(np.abs(signal_formant2)) * 32767)
write("fractal_formant2.wav", sample_rate, signal_formant2)

# formant 3
a1 = random.uniform(0.5, 2.0)
b1 = random.uniform(0.5, 2.0)
a2 = random.uniform(0.5, 2.0)
b2 = random.uniform(0.5, 2.0)
a3 = random.uniform(0.5, 2.0)
b3 = random.uniform(0.5, 2.0)
a4 = random.uniform(0.5, 2.0)
b4 = random.uniform(0.5, 2.0)
a5 = random.uniform(0.5, 2.0)
b5 = random.uniform(0.5, 2.0)

A = 0.5       # Initial amplitude
F = 2500       # Base frequency in Hz (e.g., A4 pitch)
BW = 150       # Base bandwidth (spread around frequency in Hz)
# base_signal = generate_base_signal(A, F, BW, duration, sample_rate)
# signal_formant3 = fractal_detailing(base_signal, A, F, BW, duration, sample_rate, N, noise_factor)
signal_formant3 = fractal_detailing_recursive(F, A, BW, duration, sample_rate, N, 1.0, noise_factor,
                                              a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
signal_formant3 = np.int16(signal_formant3 / np.max(np.abs(signal_formant3)) * 32767)
write("fractal_formant3.wav", sample_rate, signal_formant3)

# formant 4
a1 = random.uniform(0.5, 2.0)
b1 = random.uniform(0.5, 2.0)
a2 = random.uniform(0.5, 2.0)
b2 = random.uniform(0.5, 2.0)
a3 = random.uniform(0.5, 2.0)
b3 = random.uniform(0.5, 2.0)
a4 = random.uniform(0.5, 2.0)
b4 = random.uniform(0.5, 2.0)
a5 = random.uniform(0.5, 2.0)
b5 = random.uniform(0.5, 2.0)

A = 0.5       # Initial amplitude
F = 3500       # Base frequency in Hz (e.g., A4 pitch)
BW = 200       # Base bandwidth (spread around frequency in Hz)
# base_signal = generate_base_signal(A, F, BW, duration, sample_rate)
# signal_formant4 = fractal_detailing(base_signal, A, F, BW, duration, sample_rate, N, noise_factor)
signal_formant4 = fractal_detailing_recursive(F, A, BW, duration, sample_rate, N, 1.0, noise_factor,
                                              a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
signal_formant4 = np.int16(signal_formant4 / np.max(np.abs(signal_formant4)) * 32767)
write("fractal_formant4.wav", sample_rate, signal_formant4)

# formant 4
a1 = random.uniform(0.5, 2.0)
b1 = random.uniform(0.5, 2.0)
a2 = random.uniform(0.5, 2.0)
b2 = random.uniform(0.5, 2.0)
a3 = random.uniform(0.5, 2.0)
b3 = random.uniform(0.5, 2.0)
a4 = random.uniform(0.5, 2.0)
b4 = random.uniform(0.5, 2.0)
a5 = random.uniform(0.5, 2.0)
b5 = random.uniform(0.5, 2.0)

A = 0.5       # Initial amplitude
F = 4500       # Base frequency in Hz (e.g., A4 pitch)
BW = 250       # Base bandwidth (spread around frequency in Hz)
# base_signal = generate_base_signal(A, F, BW, duration, sample_rate)
# signal_formant5 = fractal_detailing(base_signal, A, F, BW, duration, sample_rate, N, noise_factor)
signal_formant5 = fractal_detailing_recursive(F, A, BW, duration, sample_rate, N, 1.0, noise_factor,
                                              a1, b1, a2, b2, a3, b3, a4, b4, a5, b5)
signal_formant5 = np.int16(signal_formant5 / np.max(np.abs(signal_formant5)) * 32767)
write("fractal_formant5.wav", sample_rate, signal_formant5)

audio_signals = [signal_pitch, signal_formant1, signal_formant2, signal_formant3, signal_formant4, signal_formant5]
final_mixed_audio = vm.mix_audio_signals(audio_signals)
final_mixed_audio = np.int16(final_mixed_audio / np.max(np.abs(final_mixed_audio)) * 32767)
write('final_audio.wav', sample_rate, final_mixed_audio)

