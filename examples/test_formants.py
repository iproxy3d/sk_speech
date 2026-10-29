import librosa
import soundfile as sf
from sk_speech import sk_formants as fmt

# Укажите индекс и размер окна
index = 20000  # Пример индекса
window_size = 1024  # Размер окна для анализа
hop_size = 512  # Шаг окна

input_file = 'net_norm.wav'
y, sr = librosa.load(input_file, sr=None)

# formant_freqs, times, formant_bandwidths, intensities = fmt.formant_frequencies(y, sr)
# # for formant_index in range(5):
# #     print(f"F{formant_index}: {formant_freqs[formant_index]:.2f} Hz")
#
# formant_freqs = fmt.extract_formants(y, sr)
# print("Частота форманты (F1-F5):")
# for formant_index in range(5):
#     print(f"F{formant_index+1}: {formant_freqs[formant_index]:.2f} Hz")
#
# # Определение частоты форманты
# print("Частота форманты (F1-F5):")
# for formant_index in range(1, 6):
#     formant_frequency = fmt.get_formant_frequency_by_index(y, sr, formant_index)
#     print(f"F{formant_index}: {formant_frequency:.2f} Hz")
#
# # Определение форманты в точке с данными y[index]
# formant_freqs = fmt.formant_at_index(y, sr, index, window_size=window_size)
# print(f"Частота форманты (F1-F5) в позиции {index}:")
# for formant_index in range(5):
#     print(f"F{formant_index+1}: {formant_freqs[formant_index]:.2f} Hz")
#
# # Определение полосы пропускания форманты
# print("Полоса пропускания форманты (F1-F5):")
# for formant_index in range(1, 6):
#     # method='avg', method='max'
#     formant_bandwidth = fmt.calculate_formant_bandwidth(y, sr, formant_index, method='max')
#     print(f"F{formant_index}: {formant_bandwidth:.2f} Hz")
#
# Определение длительности форманты
print("Длительность форманты (F1-F5):")
for formant_index in range(1, 6):
    formant_duration = fmt.calculate_formant_duration(y, sr, formant_index)
    print(f"F{formant_index}: {formant_duration:.2f} секунд")
    formant_duration = fmt.calculate_formant_duration2(y, sr, formant_index)
    print(f"F{formant_index}: {formant_duration:.2f} секунд")

# Определение амплитуды форманты
print("Средняя амплитуда форманты (F1-F5):")
for formant_index in range(1, 6):
    formant_amplitude = fmt.calculate_formant_amplitude_avg(y, sr, formant_index)
    print(f"F{formant_index}: {formant_amplitude:.6f}")

# Определение энергии формант F1-F5 для всего сигнала
print("Средняя энергия формант (F1-F5):")
for formant_index in range(1, 6):
    energy = fmt.calculate_formant_energy(y, sr, formant_index)
    print(f"F{formant_index} Энергия: {energy:.2f}")
    energy = fmt.calculate_formant_energy3(y, sr, formant_index)
    print(f"F{formant_index} Энергия: {energy:.2f}")

formant_energies = fmt.calculate_formant_energy2(y, sr)
print("Средняя энергия формант (F1-F5):")
for i, energy in enumerate(formant_energies, start=1):
    print(f"F{i} Энергия2: {energy:.2f}")

# Определение энергии формант F1-F5 для всего сигнала
formant_energies, f0_energy = fmt.calculate_formant_and_f0_energy(y, sr)
print(f"Средняя энергия тона речи: {f0_energy:.2f}")
print("Средняя энергия формант (F1-F5):")
for i, energy in enumerate(formant_energies, start=1):
    print(f"F{i} Энергия: {energy:.2f}")

print("Средняя интенсивность форманты (F1-F5):")
for formant_index in range(1, 6):
    intensity = fmt.calculate_formant_intensity_avg(y, sr, formant_index)
    print(f"F{formant_index} Интенсивность: {intensity:.2f}")

# Определение спектрального наклона для первой форманты (F1)
print("Спектральный наклон форманты (F1-F5):")
for formant_index in range(1, 6):
    times, slopes = fmt.compute_spectral_slope_for_formant(y, sr, formant_index, window_size, hop_size)
    print(f"F{formant_index}: {times} {slopes}")
    slopes = fmt.compute_spectral_slope_for_formant2(y, sr, formant_index)
    print(f"F{formant_index}: {slopes}")

# Определение траектории первой форманты (F1)
index = 1  # Индекс форманты (например, F1)
time_stamps, formant_frequencies = fmt.formant_trajectory(y, sr, index, window_size)

output_path = 'out_formants_change_energy.wav'
formant_index = 1  # Увеличиваем энергию первой форманты (F1)
factor = 5.0  # Коэффициент усиления (например, увеличиваем энергию в 2 раза)
resynthesized_signal = fmt.change_formant_energy(y, sr, formant_index, factor)
sf.write(output_path, resynthesized_signal, sr)

output_path = 'out_formants_change_energy2.wav'
energy_factors = [2, 3, 4, 5, 6]
y_boosted = fmt.change_formant_energy2(y, sr, energy_factors)
sf.write(output_path, y_boosted, sr)

# Значения сдвига формант в Гц
output_path = 'out_formants_change_shifts.wav'
formant_shifts = [30, 50, 40, 50, 50]  # Значение сдвига для F1, F2, F3, F4, F5
y_shift, sr_shift = fmt.change_formants_shifts(y, sr, formant_shifts)
sf.write(output_path, y_shift, sr_shift)

output_path = 'out_formants_change_shifts2.wav'
formant_shifts = [30, 50, 40, 50, 50]  # Значение сдвига для F1, F2, F3, F4, F5
y_shift, sr_shift = fmt.change_formants_shifts2(y, sr, formant_shifts)
sf.write(output_path, y_shift, sr_shift)

output_path = 'out_formants_change_shifts3.wav'
formant_shifts = [30, 50, 40, 50, 50]  # Значение сдвига для F1, F2, F3, F4, F5
y_shift, sr_shift = fmt.change_formants_shifts3(y, sr, formant_shifts)
sf.write(output_path, y_shift, sr_shift)

# Увеличение амплитуды для каждой форманты
# F1: 10-15 дБ
# F2: 10-20 дБ
# F3: 5-15 дБ
# F4: 5-15 дБ
# F5: 5-15 дБ
boost_dB = [10, 10, 5, 5, 5]  # Initial amplitude factors
max_amplitude_dB = 0 # Максимальная амплитуда в dB
output_path = 'out_formants_change_amplitude.wav'
y_boosted = fmt.change_formants_amplitude(y, sr, boost_dB, max_amplitude_dB)
sf.write(output_path, y_boosted, sr)

output_path = 'out_formants_change_amplitude2.wav'
y_boosted = fmt.change_formants_amplitude2(y, sr, boost_dB, max_amplitude_dB)
sf.write(output_path, y_boosted, sr)

output_path = 'out_formants_change_bandwidth.wav'
bandwidth_factors = [1.5, 1.2, 1.3, 1.4, 1.1]  # Примерные факторы ширины канала для F1-F5
modified_signal = fmt.change_formant_bandwidth(y, sr, bandwidth_factors)
sf.write(output_path, y_boosted, sr)
