import librosa
import soundfile as sf
from sk_speech import sk_noise as ns

input_file = 'net_norm.wav'
y, sr = librosa.load(input_file, sr=None)

# freqs, psd = ns.compute_power_spectral_density(y, sr)
# ns.plot_psd(freqs, psd)

noise_present, noise_level = ns.analyze_noise_in_psd(y, sr)
print(f'PSD Уровень шума: {noise_level}, Содержит ли шум: {noise_present}')

# Анализируем уровень шума
noise_present, avg_flatness = ns.analyze_noise_level_sf(y, sr)
print(f'SF Уровень шума: {avg_flatness}, Содержит ли шум: {noise_present}')

# Строим график спектральной плоскости
# plot_spectral_flatness(y, sr)

# Анализируем уровень шума
noise_present, avg_noise_level_db = ns.analyze_noise_level_rms(y, sr)
print(f'RMS Средний уровень шума: {avg_noise_level_db} dB, Содержит ли шум: {noise_present}')

# Анализируем уровень шума
noise_analysis = ns.analyze_noise_level(y, sr)
print(f'Средний уровень шума: {noise_analysis["avg_noise_level_db"]} dB, Содержит ли шум (RMS): {noise_analysis["is_noisy_rms"]}')
print(f'Средняя спектральная разреженность: {noise_analysis["avg_flatness"]}, Содержит ли шум (Flatness): {noise_analysis["is_noisy_flatness"]}')
print(f'Средняя спектральная плотность мощности: {noise_analysis["avg_psd"]}, Содержит ли шум (PSD): {noise_analysis["is_noisy_psd"]}')
print(f'Объединенный уровень шума: {noise_analysis["combined_noise_level"]}')

output_file = 'out_cleaned_audio.wav'
# Удаление шума из аудиосигнала
cleaned_y = ns.spectral_subtraction(y, sr, noise_estimation_method='sf')
# Сохранение очищенного сигнала
sf.write(output_file, cleaned_y, sr)

output_file = 'out_cleaned_audio2.wav'
# Оценка уровня шума
is_noisy_rms, avg_noise_level_db, is_noisy_flatness, avg_flatness = ns.analyze_noise_level2(y, sr)
# Оценка спектра шума
noise_psd = ns.estimate_noise_psd(y, sr)*2
# Удаление шума
cleaned_y = ns.spectral_subtraction2(y, sr, noise_psd=noise_psd)
# Сохранение очищенного сигнала
sf.write(output_file, cleaned_y, sr)


output_file = 'out_apply_noise_reduction.wav'
y, sr = librosa.load(input_file, sr=None)
whisper_factor = 0.3
y = ns.apply_noise_reduction(y, whisper_factor)
sf.write(output_file, y, sr)

output_file = 'out_noise_reduction_spectral_subtraction_fast.wav'
y, sr = librosa.load(input_file, sr=None)
y = ns.noise_reduction_spectral_subtraction_fast(y, sr)
sf.write(output_file, y, sr)

output_file = 'out_noise_reduction_spectral_subtraction_fast.wav'
y, sr = librosa.load(input_file, sr=None)
y = ns.noise_reduction_spectral_subtraction_fast(y, sr)
sf.write(output_file, y, sr)

output_file = 'out_noise_reduction_spectral_subtraction.wav'
y, sr = librosa.load(input_file, sr=None)
y = ns.noise_reduction_spectral_subtraction(y, sr, high_pass=True, low_pass=True, normalize=True)
sf.write(output_file, y, sr)

output_file = 'out_add_noise.wav'
y, sr = librosa.load(input_file, sr=None)
y = ns.add_noise(y)
sf.write(output_file, y, sr)

output_file = 'out_remove_noise_lowpass.wav'
y_filtered = ns.remove_noise(y, sr, method='lowpass')
sf.write(output_file, y_filtered, sr)

output_file = 'out_remove_noise_highpass.wav'
y_filtered = ns.remove_noise(y, sr, method='highpass')
sf.write(output_file, y_filtered, sr)

output_file = 'out_remove_noise_median.wav'
y_filtered = ns.remove_noise(y, sr, method='median')
sf.write(output_file, y_filtered, sr)

output_file = 'out_remove_noise_moving_average.wav'
y_filtered = ns.remove_noise(y, sr, method='moving_average')
sf.write(output_file, y_filtered, sr)
