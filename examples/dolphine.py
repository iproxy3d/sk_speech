import os
import numpy as np
from scipy.io.wavfile import write
import librosa
from sk_speech import sk_formants as fmt
from sk_speech import sk_pitch as pt
from sk_speech import sk_volume as vm
from sk_speech import sk_filters as fl

def process_audio_files(input_file, output_folder, speed_factor, pitch_shift_hz,
                        shift_factors,  min_speech_duration=0.4, max_speech_pause=0.5, min_pause_duration=0.3):
    """
    Обрабатывает аудиофайл: разбивает на участки с речью, изменяет скорость,
    сдвигает форманты и склеивает в один файл с паузами между участками.

    Разделит аудиофайл на участки с речью.
    Изменит скорость каждого участка.
    Применит сдвиги формант.
    Склеит все обработанные участки с паузами между ними.

    :param input_file: Путь к входному аудиофайлу.
    :param output_folder: Папка для сохранения промежуточных файлов.
    :param speed_factor: Коэффициент изменения скорости.
    :param shift_factors: Список сдвигов частот для каждой форманты.
    :param min_speech_duration: Минимальная длительность участка с речью (в секундах).
    :param max_speech_pause: Максимальная длительность паузы между участками (в секундах).
    """
    # Создаем выходную папку, если она не существует
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Загружаем сегмент
    y_changed, sr = librosa.load(input_file)

    # Сдвигаем форманты
    formant_shifts = [-200, 350, 700, 1050, 1400]
    y_changed, sr = fmt.change_formants_shifts6(y_changed, sr, formant_shifts)
    output_file = os.path.join(output_folder, 'final_audio_formants.wav')
    write(output_file, sr, y_changed)

    avg_f0 = pt.extract_f0(y_changed, sr, pitch_from=600, pitch_to=2000)
    pitch_shift_semitones = fl.hz_to_semitones(avg_f0 -600, avg_f0)
    y_changed, sr = pt.change_pitch_pydub(y_changed, sr, pitch_shift_semitones)
    output_file = os.path.join(output_folder, 'final_audio_pitch_hz.wav')
    write(output_file, sr, y_changed)

    # Изменяем скорость аудио
    speed_factor = 0.45
    y_changed = pt.change_audio_speed(y_changed, sr, begin_speed=speed_factor, end_speed=speed_factor)
    output_file = os.path.join(output_folder, 'final_audio_speed.wav')
    write(output_file, sr, y_changed)

    y_changed, sr = pt.change_pitch_energy(y_changed, sr, 0.5, pitch_range=(70, 600), speech=True)
    # y_changed, sr = pt.change_pitch_energy(y_changed, sr, 0.5, pitch_range=(75, 600), speech=False, pitch_from=600, pitch_to=2000)
    output_file = os.path.join(output_folder, 'final_audio_pitch.wav')
    write(output_file, sr, y_changed)

    # Разбиваем аудио на участки с речью
    segments = vm.process_audio(input_file, output_folder, min_speech_duration=min_speech_duration,
                                max_speech_pause=max_speech_pause, min_pause_duration=min_pause_duration)

    # Итоговый сигнал для склеивания
    final_audio = []
    sr = None  # Частота дискретизации

    for segment_file in segments:
        # Загружаем сегмент
        y, sr = librosa.load(segment_file, sr=None)

        avg_f0 = pt.extract_f0(y_speed_changed, sr)
        pitch_shift_semitones = fl.hz_to_semitones(avg_f0 + pitch_shift_hz, avg_f0)
        y_pitch_shifted, sr = pt.change_pitch_pydub(y, sr, pitch_shift_semitones)

        # Добавляем обработанный сигнал в итоговый массив
        final_audio.append(y_pitch_shifted)

        # Добавляем паузу, равную 1/3 длительности файла
        pause_duration = len(y_pitch_shifted) / sr / 3
        pause = np.zeros(int(sr * pause_duration))  # Создаем паузу
        final_audio.append(pause)

    # Склеиваем все обработанные сегменты
    final_audio = np.concatenate(final_audio)

    # Сохраняем итоговый аудиофайл
    output_file = os.path.join(output_folder, 'final_audio.wav')
    write(output_file, sr, final_audio.astype(np.int16))

# Пример использования
input_audio_file = 'Животные/dolphin.wav'  # Укажите путь к вашему аудиофайлу
output_directory = 'Животные/dolphin_out'    # Укажите папку для выходных файлов
speed_change_factor = 0.5                        # Изменение скорости (например, 1.5)
pitch_shift_hz = -600
formant_shifts = [100, 200, 300, 400, 500]  # Сдвиги формант

# process_audio_files(input_audio_file, output_directory, speed_change_factor, pitch_shift_hz, formant_shifts)

y, sr = librosa.load(input_audio_file)
freq, voiced_time, intensity_values, intensity_times, _, _, _ = pt.extract_f0_voiced(y, sr, speech=False,
                                                                                     time_step=0.001,
                                                                                     pitch_from=100, pitch_to=1500)
period, offset, amplitude = pt.extract_pitch_rate(y, sr)
signal_pitch = vm.generate_signal(freq, None, intensity_values, voiced_time, delta_time=0.001, sr=sr)
# output_file = os.path.join(output_directory, 'final_audio_pitch.wav')
# write(output_file, sr, (signal_pitch * 32767).astype(np.int16))

frequencies, times, bandwidths, intensities = fmt.formant_frequencies(y, sr, time_step=0.001, speech=False)
signal_formant1 = vm.generate_signal(frequencies[0], bandwidths[0], intensities, times, energy_correction=600, delta_time=0.001, sr=sr)
# output_file = os.path.join(output_directory, 'final_audio_formant1.wav')
# write(output_file, sr, (signal_formant1 * 32767).astype(np.int16))

signal_formant2 = vm.generate_signal(frequencies[1], bandwidths[1], intensities, times, energy_correction=600, delta_time=0.001, sr=sr)
signal_formant3 = vm.generate_signal(frequencies[2], bandwidths[2], intensities, times, energy_correction=600, delta_time=0.001, sr=sr)
signal_formant4 = vm.generate_signal(frequencies[3], bandwidths[3], intensities, times, energy_correction=600, delta_time=0.001, sr=sr)
signal_formant5 = vm.generate_signal(frequencies[4], bandwidths[4], intensities, times, energy_correction=600, delta_time=0.001, sr=sr)

audio_signals = [signal_pitch, signal_formant1, signal_formant2, signal_formant3, signal_formant4, signal_formant5]
final_mixed_audio = vm.mix_audio_signals(audio_signals)
output_file = os.path.join(output_directory, 'final_audio.wav')
write(output_file, sr, (final_mixed_audio * 32767).astype(np.int16))
