import librosa
import soundfile as sf
from sk_speech import sk_filters as fl

formant_ranges = [
    (300, 900),  # F1 range
    (900, 1700),  # F2 range
    (1700, 2600),  # F3 range
    (2600, 3400),  # F4 range
    (3400, 4500)  # F5 range
]

input_file = 'net_norm.wav'

output_file = 'out_normalize_audio.wav'
y, sr = librosa.load(input_file, sr=None)
y = fl.normalize_audio(y)
sf.write(output_file, y, sr)

output_file = 'out_apply_bandpass_filter.wav'
y, sr = librosa.load(input_file, sr=None)
y = fl.apply_bandpass_filter(y, sr, formant_ranges[0][0], formant_ranges[0][1])
sf.write(output_file, y, sr)

output_file = 'out_apply_smoothing_filter.wav'
y, sr = librosa.load(input_file, sr=None)
y = fl.apply_smoothing_filter(y, sr)
sf.write(output_file, y, sr)

output_file = 'out_apply_window_function.wav'
window_length=2000
y, sr = librosa.load(input_file, sr=None)
y = fl.apply_window_function(y, window_length)
sf.write(output_file, y, sr)

output_file = 'out_apply_compression.wav'
y, sr = librosa.load(input_file, sr=None)
compression_factor = 0.5
y = fl.apply_compression(y, compression_factor)
sf.write(output_file, y, sr)

output_file = 'out_apply_distortion.wav'
y, sr = librosa.load(input_file, sr=None)
distortion_factor = 0.5
y = fl.apply_distortion(y, distortion_factor)
sf.write(output_file, y, sr)

output_file = 'out_apply_reverb.wav'
y, sr = librosa.load(input_file, sr=None)
reverb_factor = 0.5
y = fl.apply_reverb(y, sr, reverb_factor)
sf.write(output_file, y, sr)

output_file = 'out_apply_harmonic.wav'
y, sr = librosa.load(input_file, sr=None)
harmonic_factor = 2.0
y = fl.apply_harmonic(y, harmonic_factor)
sf.write(output_file, y, sr)

reference_file = 'net_norm.wav'
input_file_noisy = 'net_norm2.wav'
output_file_filtered = 'out_apply_adaptive_filter.wav'
lms_filter = fl.train_adaptive_filter(reference_file)
fl.apply_adaptive_filter(input_file_noisy, output_file_filtered, lms_filter)

