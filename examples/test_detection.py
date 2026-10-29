import librosa
from sk_speech import sk_detection as dt

file_path = 'net_norm.wav'
file_path = 'net_norm2.wav'
file_path = 'net_loud1.wav'
file_path = 'net_loud2.wav'
file_path = 'net_scream1.wav'
file_path = 'net_whisper.wav'
# file_path = 'net_whisper3.wav'
# file_path = 'net_whisper4.wav'

y, sr = librosa.load(file_path, sr=None)

# Определяем, является ли сигнал громкой речью
is_loud_speech_signal = dt.is_loud_speech(y, sr)
print(f'Сигнал является громкой речью: {is_loud_speech_signal}')

# Определяем, является ли сигнал тихой речью
is_soft_speech_signal = dt.is_soft_speech(y, sr)
print(f'Сигнал является тихой речью: {is_soft_speech_signal}')

# Определяем, является ли сигнал шёпотом
is_whisper_signal = dt.is_whisper(y, sr)
print(f'Сигнал является шёпотом: {is_whisper_signal}')

# Определяем, является ли сигнал криком
is_scream_signal = dt.is_scream(y, sr)
print(f'Сигнал является криком: {is_scream_signal}')


slope, intercept, times, rms, residuals, variance = dt.compute_volume_trend(y, sr)

print(f"Slope (K): {slope}")
print(f"Intercept (M): {intercept}")
print(f"Variance of residuals: {variance}")

import matplotlib.pyplot as plt
# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(times, rms, label='RMS')
plt.plot(times, intercept + slope * times, label='Linear Fit', color='red')
plt.xlabel('Time (s)')
plt.ylabel('RMS')
plt.legend()
plt.title('Volume Trend')
plt.show()

silence_percent = dt.silence_percentage(y, sr)
print(f"Silence percentage: {silence_percent:.2f}%")


analysis_results = dt.analyze_speech(y, sr)
print("Formant clarity scores (lower is better):", analysis_results["formant_clarity"])
print(f"Silence percentage: {analysis_results['silence_percentage']:.2f}%")
freqs, psd = analysis_results['psd']

# Plot PSD
plt.figure(figsize=(10, 6))
plt.semilogy(freqs, psd)
plt.title('Power Spectral Density')
plt.xlabel('Frequency (Hz)')
plt.ylabel('PSD (dB/Hz)')
plt.grid(True)
plt.show()


clarity_scores = dt.formant_clarity(y, sr)
print("Formant clarity scores (lower is better):", clarity_scores)
