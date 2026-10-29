import time
import librosa
import numpy as np
import soundfile as sf
from sk_speech import sk_volume as vm
from sk_speech import sk_vowels as vw
from sk_speech import sk_formants as fmt
from sk_speech import sk_pitch as pt
from sk_speech import sk_plot as pl
from pydub import AudioSegment
import matplotlib.pyplot as plt

# vm.process_audio('test_em6.wav', 'breaks')
# vm.process_audio('jocker.wav', 'breaks')

# folder_path = 'pattern'
# vm.process_wav_files_in_folder(folder_path, 'pattern/norm.wav')

# options=None
options = {"freq": True, "amplitude": True, "period": True, "slope": False,
           "change": {"pitch_freq": True, "pitch_amplitude": False,
                      "formant_freq": False, "formant_amplitude": True,
                      "vowel_freq": False, "vowel_amplitude": False, },
           "pitch": True, "formants": True, "vowels": False, "formant_max": 5}

start = time.perf_counter()
speech = vm.init_speech('test_em_sber_norm.wav', options=options)
finish = time.perf_counter()
print('Время работы init_speech: ' + str(finish - start))

input_file = 'test_em_sber5.wav'
start = time.perf_counter()
cur_speech = vm.speech_params(input_file, speech)
finish = time.perf_counter()
print('Время работы vm.speech_params: ' + str(finish - start))

start = time.perf_counter()
y_new, sr_new = vm.change_speech(speech, cur_speech, volume=1.0, emotion=0.5)
sf.write('out_change_speech_up_up.wav', y_new, sr_new)
finish = time.perf_counter()
print('Время работы vm.change_speech: ' + str(finish - start))

start = time.perf_counter()
y_new, sr_new = vm.change_speech(speech, cur_speech, volume=1.0, emotion=-0.5)
sf.write('out_change_speech_up_down.wav', y_new, sr_new)
finish = time.perf_counter()
print('Время работы vm.change_speech: ' + str(finish - start))

start = time.perf_counter()
y_new, sr_new = vm.change_speech(speech, cur_speech, volume=-1.5, emotion=0.5)
sf.write('out_change_speech_down_up.wav', y_new, sr_new)
finish = time.perf_counter()
print('Время работы vm.change_speech: ' + str(finish - start))

start = time.perf_counter()
y_new, sr_new = vm.change_speech(speech, cur_speech, volume=-1.5, emotion=-0.7)
sf.write('out_change_speech_down_down.wav', y_new, sr_new)
finish = time.perf_counter()
print('Время работы change_speech: ' + str(finish - start))

volume_from = 1.0
volume_to = 1.0
# volume_from = 2.0
# volume_to = 2.0
# volume_from = 0.3
# volume_to = 0.3

input_file = 'net_norm.wav'
input_file = 'input_n0_0.wav'
y, sr = librosa.load(input_file, sr=None)

# # Рассчитываем интенсивность pitch
# intensity = vm.calculate_intensity_avg(y, sr)
# print(f'Интенсивность речи: {intensity:.6f}')
#
# # Рассчитываем интенсивность pitch
# intensity = vm.calculate_intensity_max(y, sr)
# print(f'Интенсивность речи по максимуму: {intensity:.6f}')

# Load original and filtered audio files
# output_file = 'out_speech_mix_audio.wav'
# filtered_file = 'net_norm2.wav'
# y_filtered, sr_filtered = librosa.load(filtered_file, sr=None)
# volume = max(volume_from, volume_to)
# if volume != 0:
#     start_mix_ratio = volume_from / volume  # Mix ratio at the beginning of the file (20% original, 80% filtered)
#     end_mix_ratio = volume_to / volume  # Mix ratio at the end of the file (80% original, 20% filtered)
# else:
#     start_mix_ratio = 0
#     end_mix_ratio = 0

# y_mix = vm.mix_audio(y, y_filtered, start_mix_ratio, end_mix_ratio)
# sf.write(output_file, y_mix, sr)

# output_file = 'out_speech_change_volume.wav'
# y_filtered = vm.change_speech_volume(y, sr, volume, is_noise=False, is_shift=True)
# sf.write(output_file, y_filtered, sr)

# output_file = 'out_speech_change_volume2.wav'
# y_filtered = vm.change_volume(y, sr, volume_from, volume_to, False, False)
# sf.write(output_file, y_filtered, sr)

# output_file = 'out_speech_change_volume_linear.wav'
# start_db = 0  # Начальное увеличение громкости
# end_db = 20  # Конечное увеличение громкости
# vm.change_volume_linear(input_file, output_file, start_db, end_db)

# Вычисление спектрального наклона
# times, slopes = vm.compute_spectral_slope(y, sr)
# print("Спектральный наклон:", np.mean(slopes))

output_file = 'out_speech_change_volume.wav'
# pl.visualize_vowel_boundaries(input_file, boundaries_with_types)
# pl.visualize_spectrograms(input_file, output_file)
# pl.visualize_amplified_vowels(input_file, output_file, boundaries_with_types)
# pl.visualize_energy_vowels(input_file, output_file, boundaries_with_types)

# # Путь к файлам
# file_names = [f"f{i}.wav" for i in range(1, 21)]
# # Создаем пустой аудиофайл
# combined = AudioSegment.empty()
# # Склеиваем файлы
# for file_name in file_names:
#     input_file = 'da.wav'
#     input_file = 'auto.wav'
#     # input_file = 'new_message.wav'
#     audio = AudioSegment.from_wav(input_file)
#     combined += audio
# # Сохраняем объединенный файл
# combined.export("out_1.wav", format="wav")
#
# # Создаем пустой аудиофайл
# combined = AudioSegment.empty()
# # Склеиваем файлы
# input_file = 'net.wav'
# input_file = 'da.wav'
# input_file = 'auto.wav'
# # input_file = 'new_message.wav'
# output_file = "out_2.wav"
# y, sr = librosa.load(input_file, sr=None)
# volume = -2.0
# volume = 0.0
# # volume = 2.0
# for file_name in file_names:
#     print(volume)
#     y_filtered = vm.change_speech_volume(y, sr, volume, is_noise=False, is_shift=True)
#     sf.write(file_name, y_filtered, sr)
#
#     audio = AudioSegment.from_wav(file_name)
#     combined += audio
#     volume += 0.1
# # Сохраняем объединенный файл
# combined.export(output_file, format="wav")
#
# input_file = "out_1.wav"
# output_file = "out_2.wav"

# input_file = "out_da1.wav"
# y, sr = librosa.load(input_file, sr=None)
# frequency_factors = [1.0, 1.0, 1.0, 1.0, 1.0]  # Коэффициенты масштабирования для каждой форманты
# y_filtered = fmt.change_formant_frequencies(y, sr, frequency_factors)
# sf.write('out_formants_change_frequencies.wav', y_filtered, sr)

# input_file = "out_da1.wav"
# y, sr = librosa.load(input_file, sr=None)
# bandwidth_factors = [1.0, 1.0, 1.0, 1.0, 1.0]  # Коэффициенты масштабирования для каждой форманты
# bandwidth_factors = [5.0, 5.0, 5.0, 5.0, 5.0]  # Коэффициенты масштабирования для каждой форманты
# y_filtered = fmt.change_formant_bandwidth(y, sr, bandwidth_factors)
# sf.write('out_formants_change_bandwidth4.wav', y_filtered, sr)

# y, sr = librosa.load(input_file, sr=None)
# boundaries_with_types = vw.detect_vowel_boundaries(y, sr)
# pl.visualize_vowel_boundaries(input_file, boundaries_with_types)
# pl.visualize_spectrograms(input_file, output_file)
# pl.visualize_amplified_vowels(input_file, output_file, boundaries_with_types)
# pl.visualize_energy_vowels(input_file, output_file, boundaries_with_types)

input_file = 'net.wav'
input_file = 'test_em_norm.wav'
input_file = 'test_em_sber_norm.wav'
y, sr = librosa.load(input_file, sr=None)
# y, sr = pt.flatten_pitch(y, sr)
tract_length_orig = vm.get_tract_length(y, sr)
print("Длина голосового тракта спокойной речи:", tract_length_orig)
tract_length_orig = vm.get_tract_length_expended(y, sr)
print("Длина голосового тракта 6-7 форманты:", tract_length_orig)

y_new = fmt.flatten_formants(y, sr)
sf.write('out_flatten_formants.wav', y_new, sr)

slopes = [0.1, 0.1, 0.1, 0.1, 0.1]
mixing_percent=[0.05, 0.05, 0.05, 0.05, 0.05]
filtered_percent = [0.1, 0.1, 0.1, 0.1, 0.1]
y_new = fmt.slope_formants(y, sr, slopes, mixing_percent, method='', replace=True)
sf.write('out_slope_formants.wav', y_new, sr)

norm_params = vm.get_speech_params(y, sr)

speech = vm.init_speech(input_file)
print("Инициализация речи", speech)

input_file = 'net_loud1.wav'
input_file = 'input_n0_0.wav'
input_file = 'test_em3.wav'
input_file = 'test_em2.wav'
input_file = 'test_em.wav'
input_file = 'test_em4.wav'
# input_file = 'test_em5.wav'
# input_file = 'test_em_sber.wav'
# input_file = 'test_em_sber2.wav'
# input_file = 'test_em_sber3.wav'
# input_file = 'test_em_sber4.wav'
input_file = 'test_em_sber5.wav'
y, sr = librosa.load(input_file, sr=None)

params = vm.get_speech_params(y, sr)
print("Параметры речи:", params)

vectors = vm.get_speech_vector(params, norm_params)
print("Вектор речи:", vectors)

y_new, sr_new = pt.modify_pitch_slope(y, sr, slope_change=2.0)
sf.write('out_pitch_slope_up.wav', y_new, sr_new)
y_new, sr_new = pt.modify_pitch_slope(y, sr, slope_change=-0.7)
sf.write('out_pitch_slope_down.wav', y_new, sr_new)
y_new, sr_new = pt.flatten_pitch(y, sr)
sf.write('out_flatten_pitch.wav', y_new, sr_new)
y_new, sr_new = pt.slope_pitch(y, sr, -100, -30)
sf.write('out_slope_pitch_minis_up.wav', y_new, sr_new)
y_new, sr_new = pt.slope_pitch(y, sr, -30, -100)
sf.write('out_slope_pitch_minis_down.wav', y_new, sr_new)
y_new = pt.change_audio_speed(y, sr, begin_speed=0.7, end_speed=1.3)
sf.write('out_audio_speed_up.wav', y_new, sr_new)
y_new = pt.change_audio_speed(y, sr, begin_speed=1.3, end_speed=0.7)
sf.write('out_audio_speed_down.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation(y, sr, period=1.5, offset=0.5, amplitude=50)
sf.write('out_pitch_intonation_1_5__0_5__50.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation(y, sr, period=0.2, offset=0.0, amplitude=70)
sf.write('out_pitch_intonation_0_2__0_0__70.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation(y, sr, period=3.0, offset=0.0, amplitude=70)
sf.write('out_pitch_intonation_3_0__0_0__70.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation_ex(y, sr, begin_period=0.2, end_period=0.2, offset=0.0, begin_amplitude=70, end_amplitude=0)
sf.write('out_pitch_intonation_0_2__0_0__70_0.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation_ex(y, sr, begin_period=3.0, end_period=3.0, offset=0.0, begin_amplitude=70, end_amplitude=0)
sf.write('out_pitch_intonation_3_0__0_0__70_0.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation_ex(y, sr, begin_period=0.2, end_period=0.2, offset=0.0, begin_amplitude=0, end_amplitude=70)
sf.write('out_pitch_intonation_0_2__0_0__0_70.wav', y_new, sr_new)
y_new, sr_new = pt.change_pitch_intonation_ex(y, sr, begin_period=3.0, end_period=3.0, offset=0.0, begin_amplitude=0, end_amplitude=70)
sf.write('out_pitch_intonation_3_0__0_0__0_70.wav', y_new, sr_new)

# combined = AudioSegment.empty()
# amplitude = 0.0
# for index in range(10):
#     y_new, sr_new = pt.flatten_pitch(y, sr)
#     y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=1.5, offset=0.5, amplitude=amplitude)
#     sf.write('out.wav', y_new, sr_new)
#     audio = AudioSegment.from_wav('out.wav')
#     combined += audio
#     amplitude += 20
# combined.export('out_period_amplitude.wav', format="wav")
#
# combined = AudioSegment.empty()
# offset = 0.0
# for index in range(10):
#     y_new, sr_new = pt.flatten_pitch(y, sr)
#     y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=2.0, offset=offset, amplitude=50)
#     sf.write('out.wav', y_new, sr_new)
#     audio = AudioSegment.from_wav('out.wav')
#     combined += audio
#     offset += 0.1
# combined.export('out_period_offset.wav', format="wav")
#
# combined = AudioSegment.empty()
# period = 0.05
# for index in range(40):
#     y_new, sr_new = pt.flatten_pitch(y, sr)
#     y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=period, offset=0.5, amplitude=50)
#     sf.write('out.wav', y_new, sr_new)
#     audio = AudioSegment.from_wav('out.wav')
#     combined += audio
#     period += 0.05
# combined.export('out_period_period.wav', format="wav")
#
#
# combined = AudioSegment.empty()
# speed = 0
# for index in range(10):
#     y_new, sr_new = pt.flatten_pitch(y, sr)
#     y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=2.5, offset=0.5, amplitude=70)
#     y_new = pt.change_audio_speed(y_new, sr_new, begin_speed=1.0-speed, end_speed=1.0+speed)
#     sf.write('out.wav', y_new, sr_new)
#     audio = AudioSegment.from_wav('out.wav')
#     combined += audio
#     speed += 0.025
# combined.export('out_period_speed_up.wav', format="wav")
#
# combined = AudioSegment.empty()
# speed = 0
# for index in range(10):
#     y_new, sr_new = pt.flatten_pitch(y, sr)
#     y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=0.5, offset=0.5, amplitude=70)
#     y_new = pt.change_audio_speed(y_new, sr_new, begin_speed=1.0+speed, end_speed=1.0-speed)
#     sf.write('out.wav', y_new, sr_new)
#     audio = AudioSegment.from_wav('out.wav')
#     combined += audio
#     speed += 0.025
# combined.export('out_period_speed_down.wav', format="wav")

combined = AudioSegment.empty()
slope_change = 0.1
amplitude = -50
for index in range(10):
    y_new, sr_new = pt.slope_pitch(y, sr, start_delta=-50.0, end_delta=-50.0)
    y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=1.5, offset=0.5, amplitude=amplitude)
    y_new, sr_new = pt.modify_pitch_slope(y_new, sr_new, slope_change=slope_change)
    y_new = pt.change_audio_speed(y_new, sr_new, begin_speed=0.9, end_speed=1.1)
    sf.write('out.wav', y_new, sr_new)
    audio = AudioSegment.from_wav('out.wav')
    combined += audio
    slope_change += 0.2
    amplitude = amplitude + 10
combined.export('out_period_speed_pitch_slope_up.wav', format="wav")

combined = AudioSegment.empty()
slope_change = 2.5
amplitude = 50
for index in range(10):
    y_new, sr_new = pt.slope_pitch(y, sr, start_delta=-50.0, end_delta=-50.0)
    y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=1.5, offset=0.5, amplitude=amplitude)
    y_new, sr_new = pt.modify_pitch_slope(y_new, sr_new, slope_change=slope_change)
    y_new = pt.change_audio_speed(y_new, sr_new, begin_speed=0.9, end_speed=1.1)
    sf.write('out.wav', y_new, sr_new)
    audio = AudioSegment.from_wav('out.wav')
    combined += audio
    slope_change -= 0.2
amplitude = amplitude - 10
combined.export('out_period_speed_pitch_slope_down.wav', format="wav")

combined = AudioSegment.empty()
slope_change = 0.1
amplitude = 0
for index in range(10):
    y_new, sr_new = pt.slope_pitch(y, sr, start_delta=-50.0, end_delta=-50.0)
    # y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=0.3, offset=0.5, amplitude=amplitude)
    y_new, sr_new = pt.change_pitch_intonation_ex(y_new, sr_new, begin_period=0.3, end_period=3.0, begin_amplitude=0, end_amplitude=amplitude, offset=0.5)
    y_new, sr_new = pt.modify_pitch_slope(y_new, sr_new, slope_change=slope_change)
    y_new = pt.change_audio_speed(y_new, sr_new, begin_speed=0.9, end_speed=1.1)
    sf.write('out.wav', y_new, sr_new)
    audio = AudioSegment.from_wav('out.wav')
    combined += audio
    slope_change += 0.2
    amplitude = amplitude + 10
combined.export('out_period_small_slope_pitch_up.wav', format="wav")

combined = AudioSegment.empty()
slope_change = 2.5
amplitude = 0
for index in range(10):
    y_new, sr_new = pt.slope_pitch(y, sr, start_delta=-50.0, end_delta=-50.0)
    # y_new, sr_new = pt.change_pitch_intonation(y_new, sr_new, period=3.0, offset=0.5, amplitude=amplitude)
    y_new, sr_new = pt.change_pitch_intonation_ex(y_new, sr_new, begin_period=3.0, end_period=0.3, begin_amplitude=0, end_amplitude=amplitude, offset=0.5)
    y_new, sr_new = pt.modify_pitch_slope(y_new, sr_new, slope_change=slope_change)
    y_new = pt.change_audio_speed(y_new, sr_new, begin_speed=0.9, end_speed=1.1)
    sf.write('out.wav', y_new, sr_new)
    audio = AudioSegment.from_wav('out.wav')
    combined += audio
    slope_change -= 0.2
    amplitude = amplitude + 5
combined.export('out_period_large_slope_pitch_down.wav', format="wav")

# volume = 1.5
# emotion = 1.0
# new_params = vm.get_speech_new(norm_params, params, vectors, volume, emotion)
# print("Новые параметры речи:", new_params)
#
# muls = vm.get_speech_mul(new_params, params)
# print("Множители параметров речи:", muls)

# Создаем пустой аудиофайл
combined = AudioSegment.empty()
# Склеиваем файлы
volume = 0.0
emotion = 0.0
for index in range(10):
    new_params = vm.get_speech_new(norm_params, params, vectors, volume*(2**0.5), emotion)
    print("Новые параметры речи:", new_params)
    muls = vm.get_speech_mul(new_params, params)
    print("Множители параметров речи:", muls)
    y_new, sr_new = vm.get_change_speech(y, sr, muls, new_params, params)

    print(volume)
    sf.write('out.wav', y_new, sr_new)
    audio = AudioSegment.from_wav('out.wav')
    combined += audio
    volume += 0.5
    emotion += 0.1
output_file = 'out_get_change_speech.wav'
# output_file = 'out_get_change_speech2.wav'
combined.export(output_file, format="wav")

# y_new, sr_new = vm.get_change_speech(y, sr, muls, new_params, params)
# sf.write('out_get_change_speech1.wav', y_new, sr_new)

y_new, sr_new = pt.flatten_pitch(y, sr)
y_new = pt.change_audio_speed_period(y_new, sr_new, period=1.5, offset=0, amplitude=0.2, mean_speed=1.0)
sf.write('out_change_audio_speed_period.wav', y_new, sr_new)

y_new, sr_new = pt.flatten_pitch(y, sr)
y_new = pt.change_audio_speed_periodic(y_new, sr_new, period=1.5, offset=0, amplitude=0.2, mean_speed=1.0)
sf.write('out_change_audio_speed_periodic.wav', y_new, sr_new)

y_new, sr_new = pt.flatten_pitch(y, sr)
y_new = pt.change_audio_speed_acceleration(y_new, sr_new, initial_speed=1.0, acceleration=0.2)
sf.write('out_change_audio_speed_acceleration.wav', y_new, sr_new)

y_new, sr_new = pt.flatten_pitch(y, sr)
y_new = pt.change_modulate_speed_per_fragment(y, sr, fragment_duration=0.5, base_speed=1.0, amplitude=0.2)
sf.write('out_change_modulate_speed_per_fragment.wav', y_new, sr_new)


spectral_envelope, formants = pt.extract_timbre(y, sr)

# # Визуализация спектрального конверта
# plt.figure(figsize=(10, 4))
# librosa.display.specshow(librosa.power_to_db(spectral_envelope, ref=np.max), sr=sr, x_axis='time', y_axis='mel')
# plt.colorbar(format='%+2.0f dB')
# plt.title('Spectral Envelope (Timbre)')
# plt.tight_layout()
# plt.show()

print("Formants:", formants, "spectral_envelope:", np.mean(spectral_envelope))

tempogram, tempo = pt.extract_rhythm(y, sr)

# Визуализация темпограммы
# plt.figure(figsize=(10, 4))
# librosa.display.specshow(tempogram, sr=sr, x_axis='time', y_axis='tempo')
# plt.title('Tempogram (Rhythm)')
# plt.tight_layout()
# plt.show()

print("Average Tempo (BPM):", tempo)

avg_pitches, avg_spectral_centroid = pt.extract_timbre_from_pitch(y, sr)
print("avg_pitches:", avg_pitches, "avg_spectral_centroid:", avg_spectral_centroid)

pitch_changes, avg_tempogram = pt.extract_rhythm_from_pitch(y, sr)
print("pitch_changes:", pitch_changes, "avg_tempogram:", avg_tempogram)

input_file = 'test_em_sber3.wav'
y, sr = librosa.load(input_file, sr=None)

y, sr = pt.flatten_pitch(y, sr)

pitch_period, pitch_offset, pitch_amplitude = pt.extract_pitch_rate(y, sr)
print(f"  Pitch period: {pitch_period}")
print(f"  Pitch offset: {pitch_offset}")
print(f"  Pitch amplitude: {pitch_amplitude}")

segments = pt.find_speech_segments(y, sr)
combined = AudioSegment.empty()
old_end_time = 0
for i, (start_time, end_time, segment_y, segment_sr) in enumerate(segments):
    # segment_y, segment_sr = pt.change_pitch_intonation(segment_y, segment_sr, period=0.2, offset=0.0, amplitude=50)
    if i == 0:
        segment_y, segment_sr = pt.change_pitch_intonation_ex(segment_y, segment_sr,
                                                              begin_period=0.2, end_period=0.2,
                                                              begin_amplitude=0, end_amplitude=70,
                                                              offset=0.0, slope_change=1.0)
    else:
        segment_y, segment_sr = pt.change_pitch_intonation_ex(segment_y, segment_sr,
                                                              begin_period=0.3, end_period=0.1,
                                                              begin_amplitude=0, end_amplitude=70,
                                                              offset=0.0, slope_change=2.5)

    print(f"Segment {i + 1}:")
    print(f"  Start time: {start_time:.2f} s")
    print(f"  End time: {end_time:.2f} s")
    print(f"  Duration: {end_time - start_time:.2f} s")
    print(f"  Sample rate: {segment_sr}")
    pitch_period, pitch_offset, pitch_amplitude = pt.extract_pitch_rate(segment_y, segment_sr)
    print(f"  Pitch period: {pitch_period}")
    print(f"  Pitch offset: {pitch_offset}")
    print(f"  Pitch amplitude: {pitch_amplitude}")
    sf.write('out.wav', segment_y, segment_sr)
    silent = int(start_time*1000) - old_end_time
    combined = combined + AudioSegment.silent(duration=silent,frame_rate=sr)
    combined += AudioSegment.from_wav('out.wav')
    old_end_time = end_time
combined = combined + AudioSegment.silent(duration=1000,frame_rate=sr)
combined.export('out.wav', format="wav")

y, sr = librosa.load('out.wav', sr=None)
y = pt.change_audio_speed(y, sr, begin_speed=0.95, end_speed=0.85)
sf.write('out.wav', y, sr)

folder_path = 'emotionsJ'
vm.process_wav_files_in_folder(folder_path, 'emotionsJ/neutral_1_0.wav')

folder_path = 'emotions'
vm.process_wav_files_in_folder(folder_path, 'emotions/neutral_1_0.wav')

# folder_path = 'josh/Amused'
# vm.process_wav_files_in_folder(folder_path, 'josh/Neutral/neutral_57-84_0064.wav')

# folder_path = 'josh/Sleepy'
# vm.process_wav_files_in_folder(folder_path, 'josh/Neutral/neutral_1-28_0001.wav')

folder_path = 'pattern'
vm.process_wav_files_in_folder(folder_path, 'pattern/norm.wav')

folder_path = 'pattern/down_down'
vm.process_wav_files_in_folder(folder_path, 'pattern/norm.wav')

folder_path = 'pattern/down_up'
vm.process_wav_files_in_folder(folder_path, 'pattern/norm.wav')

folder_path = 'pattern/up_down'
vm.process_wav_files_in_folder(folder_path, 'pattern/norm.wav')

folder_path = 'pattern/up_up'
vm.process_wav_files_in_folder(folder_path, 'pattern/norm.wav')

