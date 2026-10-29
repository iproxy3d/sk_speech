import librosa
import numpy as np
import soundfile as sf
from sk_speech import sk_pitch as pt
from sk_speech import sk_filters as fl

input_file = 'net_norm.wav'
input_file = 'out_gammatone27.wav'
pitch_shift_hz = 10

y, sr = librosa.load(input_file, sr=None)
y, sr = pt.flatten_pitch(y, sr)
sf.write('out_gammatone27_2.wav', y, sr)

# определяем тренд pitch
slope, variance, trend = pt.calculate_pitch_slope(y, sr)
print(f"Slope: {slope}, Variance: {variance}, Trend: {trend}")

# # Определяем, pitch
# avg_f0 = pt.extract_f0(y, sr)
# print(f'pitch: {avg_f0} Hz')
#
# # Определяем, pitch, там где есть речь
# f0 = pt.extract_f0_segment(y, sr)
# avg_f0_2 = np.mean(f0)
# print(f'pitch 2: {avg_f0_2} Hz')
#
# # Определение ширины пропускания основного тона речи
# pitch_bandwidth = pt.calculate_pitch_bandwidth(y, sr)
# print(f"Ширина пропускания основного тона речи: {pitch_bandwidth:.2f} Hz")
#
# # Определение энергии тона
# avg_pitch_energy = pt.calculate_pitch_energy(y, sr)
# print(f"Средняя энергия тона речи: {avg_pitch_energy:.2f}")
#
# # Рассчитываем интенсивность pitch
# intensity = pt.calculate_pitch_intensity_avg(y, sr)
# print(f'Интенсивность тона речи: {intensity:.6f}')
# # intensity_db = pt.calculate_pitch_intensity(y, sr, only_speech=True)
#
# # Определение амплитуды тона
# avg_pitch_amplitude = pt.calculate_pitch_amplitude(y, sr)
# print(f"Средняя амплитуда основного тона речи: {avg_pitch_amplitude:.6f}")
# # avg_pitch_amplitude = pt.calculate_pitch_amplitude2(y, sr)
# # print(f"Средняя амплитуда основного тона речи: {avg_pitch_amplitude:.6f}")
#
# # Определение длительности основного тона речи
# pitch_duration = pt.calculate_pitch_duration(y, sr)
# print(f"Длительность основного тона речи: {pitch_duration:.2f} секунд")
#
# spectral_tilt = pt.calculate_spectral_tilt_pitch(y, sr)
# print("Спектральный наклон основного тона:", spectral_tilt)
#
# # Удаление тона речи для шепота
# output_file = 'out_pitch_remove_and_reduce_formants.wav'
# resynthesized_signal = pt.remove_pitch_and_reduce_formants(y, sr)
# sf.write(output_file, resynthesized_signal, sr)
#
# # Усиленного pitch
# output_file = 'out_pitch_change_energy.wav'
# factor = 2.0  # Коэффициент усиления (например, увеличиваем энергию в 2 раза)
# resynthesized_signal, sr = pt.change_pitch_energy(y, sr, factor)
# sf.write(output_file, resynthesized_signal, sr)
#
# output_file = 'out_pitch_change_shift.wav'
# pitch_shift_semitones = fl.hz_to_semitones(avg_f0+pitch_shift_hz, avg_f0)
# y_shifted, sr = pt.change_pitch_pydub(y, sr, pitch_shift_semitones)
# sf.write(output_file, y_shifted, sr)
# new_f0 = pt.extract_f0(y_shifted, sr)
# print(f"Новый основной тон (F0): {new_f0:.2f} Hz")
#
# # output_file = 'out_pitch_change_rubberband.wav'
# # y_shifted = pt.change_pitch_rubberband(y, sr, pitch_shift_hz)
# # sf.write(output_file, y_shifted, sr)
# # new_f0 = pt.extract_f0(y_shifted, sr)
# # print(f"Новый основной тон (F0): {new_f0:.2f} Hz")
#
# intensive = pt.calculate_pitch_intensity_avg2(y, sr)
# print(f"intensive: {intensive:.2f}")
#
# output_file = 'out_pitch_change_bandwidth.wav'
# pitch_factor = 1.5  # Примерный фактор изменения ширины канала pitch
# modified_signal = pt.change_pitch_bandwidth(y, sr, pitch_factor)
# sf.write(output_file, modified_signal, sr)
