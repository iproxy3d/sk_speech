import librosa
import soundfile as sf
from sk_speech import sk_vowels as vw
from sk_speech import sk_plot as pl

threshold = 0.1

formant_energy_dict = {
    'a': [5, 10, 5, 3],  # Усиление для гласной 'a' в dB (например, F1, F2, F3, F4)
    'e': [5, 10, 5, 3],  # Усиление для гласной 'e'
    'i': [5, 15, 10, 5],  # Усиление для гласной 'i' (более высокий F2 и F3)
    'o': [5, 10, 5, 3],  # Усиление для гласной 'o'
    'u': [5, 10, 5, 3],  # Усиление для гласной 'u'
}

formant_energy_dict = {
    'a': [5, 15, 10, 5],  # Усиление для гласной 'a' в dB (например, F1, F2, F3, F4)
    'e': [5, 15, 10, 5],  # Усиление для гласной 'e'
    'i': [5, 15, 10, 5],  # Усиление для гласной 'i' (более высокий F2 и F3)
    'o': [5, 15, 10, 5],  # Усиление для гласной 'o'
    'u': [5, 15, 10, 5],  # Усиление для гласной 'u'
}
formant_gains_dict = {
    'a': [10, 15, 10, 5],  # Усиление для гласной 'a' в dB (например, F0, F1, F2, F3)
    'e': [10, 15, 10, 5],  # Усиление для гласной 'e'
    'i': [10, 20, 15, 10],  # Усиление для гласной 'i' (более высокий F2 и F3)
    'o': [10, 15, 10, 5],  # Усиление для гласной 'o'
    'u': [10, 15, 10, 5],  # Усиление для гласной 'u'
}

formant_shifts_dict = {
    'a': [70, 60, 60, 50],
    'e': [50, 50, 50, 50],
    'i': [30, 60, 40, 50],
    'o': [50, 50, 50, 50],
    'u': [50, 50, 50, 50],
}

# При переходе от гласной к согласной или наоборот, амплитуда будет изменяться постепенно,
# создавая области повышенной энергии вокруг гласных.
frame_duration = 0.3 # seconds (100 ms) изменяемое окно вокруг гласной

input_file = 'net_norm.wav'
y, sr = librosa.load(input_file, sr=None)

# Получение границ гласных
boundaries_with_types = vw.detect_vowel_boundaries(y, sr)

# Увеличение амплитуды каждой гласной
output_file = 'out_vowels_amplify.wav'
y_amplified = vw.amplify_vowels(y, sr, boundaries_with_types, formant_gains_dict, frame_duration)
sf.write(output_file, y_amplified, sr)

# сдвиг формант гласных
output_file = 'out_vowels_apply_formant_shifts.wav'
y_shifted = vw.apply_formant_shifts_vowels(y, sr, boundaries_with_types, formant_shifts_dict, frame_duration)
sf.write(output_file, y_shifted, sr)

# vw.shift_formants_vowels(input_file, output_file, boundaries_with_types, formant_shifts_dict, frame_duration)

# Увеличение энергии гласных в формантах
output_file = 'out_vowels_energy.wav'
y_energy_amplified =vw.energy_vowels(y, sr, boundaries_with_types, formant_energy_dict, frame_duration)
sf.write(output_file, y_energy_amplified, sr)

pl.visualize_vowel_boundaries(input_file, boundaries_with_types, threshold)
pl.visualize_spectrograms(input_file, output_file)
pl.visualize_amplified_vowels(input_file, output_file, boundaries_with_types)
pl.visualize_energy_vowels(input_file, output_file, boundaries_with_types)
