import os
import librosa
import numpy as np
import soundfile as sf
from sk_speech import sk_volume as vm
from sk_speech import sk_vowels as vw
from sk_speech import sk_pitch as pt
from sk_speech import sk_formants as fmt

def save_filenames_without_extension(directory, output_file):
    """
    Обходит все файлы в указанной папке, извлекает их названия и сохраняет их без расширений в файл output_file.

    :param directory: Путь к папке, содержащей файлы.
    :param output_file: Имя выходного файла для сохранения названий файлов.
    """
    datas = []

    y, sr = librosa.load(os.path.join(directory, 'neutral_1_0.wav'), sr=None)

    f0 = pt.extract_f0_segment(y, sr)
    avg_f0_norm = np.mean(f0)
    avg_pitch_bandwidth_norm = pt.calculate_pitch_bandwidth(y, sr)
    avg_pitch_energy_norm = pt.calculate_pitch_energy(y, sr)
    avg_pitch_intensity_norm = pt.calculate_pitch_intensity_avg(y, sr)
    avg_pitch_amplitude_norm = pt.calculate_pitch_amplitude(y, sr)
    avg_pitch_duration_norm = pt.calculate_pitch_duration(y, sr)

    avg_formant_frequency_norm = [0, 0, 0, 0, 0]
    avg_formant_bandwidth_norm = [0, 0, 0, 0, 0]
    avg_formant_energy_norm = [0, 0, 0, 0, 0]
    avg_formant_intensity_norm = [0, 0, 0, 0, 0]
    avg_formant_amplitude_norm = [0, 0, 0, 0, 0]
    avg_formant_duration_norm = [0, 0, 0, 0, 0]
    for formant_index in range(1, 6):
        avg_formant_frequency_norm[formant_index-1] = fmt.get_formant_frequency_by_index(y, sr, formant_index)
        avg_formant_bandwidth_norm[formant_index-1] = fmt.calculate_formant_bandwidth(y, sr, formant_index, method='avg')
        avg_formant_energy_norm[formant_index-1] = fmt.calculate_formant_energy3(y, sr, formant_index)
        avg_formant_intensity_norm[formant_index-1] = fmt.calculate_formant_intensity_avg(y, sr, formant_index)
        avg_formant_amplitude_norm[formant_index-1] = fmt.calculate_formant_amplitude_avg(y, sr, formant_index)
        avg_formant_duration_norm[formant_index-1] = fmt.calculate_formant_duration(y, sr, formant_index)

    # Обход всех файлов в указанной папке
    for root, _, files in os.walk(directory):
        for file in files:
            # Извлечение названия файла без расширения
            em_name = os.path.splitext(file)[0]
            em_name = em_name.split('_')[0]
            # print(em_name)
            y, sr = librosa.load(os.path.join(directory, file), sr=None)

            y, sr = pt.flatten_pitch(y, sr)

            s = f'em_name: {em_name}'
            # datas.append(s)

            # определяем тренд pitch
            slope, variance, trend = pt.calculate_pitch_slope(y, sr)
            s = f'Slope: {slope:.2f}| Variance: {variance:.2f}| Trend: {trend}'
            # datas.append(s)
            # print(f"em_name: {em_name}, Наклон: {slope:.2f}, Дисперсия: {variance:.2f}, Trend: {trend}")

            f0 = pt.extract_f0_segment(y, sr)
            if len(f0) > 0:
                avg_f0 = np.nanmean(f0)
            else:
                avg_f0 = 0
            avg_pitch_bandwidth = pt.calculate_pitch_bandwidth(y, sr)
            avg_pitch_energy = pt.calculate_pitch_energy(y, sr)
            avg_pitch_intensity = pt.calculate_pitch_intensity_avg(y, sr)
            avg_pitch_amplitude = pt.calculate_pitch_amplitude(y, sr)
            avg_pitch_duration = pt.calculate_pitch_duration(y, sr)

            # s = f'source pitch: {avg_f0:.2f} | pitch_bandwidth: {avg_pitch_bandwidth:.2f} | pitch_energy: {avg_pitch_energy:.2f} | pitch_intensity: {avg_pitch_intensity:.2f} | pitch_amplitude: {avg_pitch_amplitude:.2f} | pitch_duration: {avg_pitch_duration:.2f}'
            # s = f'source pitch: {avg_f0:.2f}'
            s = f'{avg_pitch_energy:.2f}'
            # datas.append(s)

            avg_f0 -= avg_f0_norm
            avg_pitch_bandwidth -= avg_pitch_bandwidth_norm
            avg_pitch_energy -= avg_pitch_energy_norm
            avg_pitch_intensity -= avg_pitch_intensity_norm
            avg_pitch_amplitude -= avg_pitch_amplitude_norm
            avg_pitch_duration -= avg_pitch_duration_norm

            # s = f'delta pitch: {avg_f0:.2f} | pitch_bandwidth: {avg_pitch_bandwidth:.2f} | pitch_energy: {avg_pitch_energy:.2f} | pitch_intensity: {avg_pitch_intensity:.2f} | pitch_amplitude: {avg_pitch_amplitude:.2f} | pitch_duration: {avg_pitch_duration:.2f}'
            # s = f'delta pitch: {avg_f0:.2f}'
            # datas.append(s)

            for formant_index in range(1, 6):
                avg_formant_frequency = fmt.get_formant_frequency_by_index(y, sr, formant_index)
                avg_formant_bandwidth = fmt.calculate_formant_bandwidth(y, sr, formant_index, method='avg')
                avg_formant_energy = fmt.calculate_formant_energy3(y, sr, formant_index)
                avg_formant_intensity = fmt.calculate_formant_intensity_avg(y, sr, formant_index)
                avg_formant_amplitude = fmt.calculate_formant_amplitude_avg(y, sr, formant_index)
                avg_formant_duration = fmt.calculate_formant_duration(y, sr, formant_index)

                # s = f'source F{formant_index}: {avg_formant_frequency:.2f} | formant_bandwidth: {avg_formant_bandwidth:.2f} | formant_energy: {avg_formant_energy:.2f} | formant_intensity: {avg_formant_intensity:.2f} | formant_amplitude: {avg_formant_amplitude:.2f} | formant_duration: {avg_formant_duration:.2f}'
                # s = f'source F{formant_index}: {avg_formant_frequency:.2f}'
                s = f'{avg_formant_frequency:.2f}'
                if formant_index==3:
                    datas.append(s)

                avg_formant_frequency -= avg_formant_frequency_norm[formant_index-1]
                avg_formant_bandwidth -= avg_formant_bandwidth_norm[formant_index-1]
                avg_formant_energy -= avg_formant_energy_norm[formant_index-1]
                avg_formant_intensity -= avg_formant_intensity_norm[formant_index-1]
                avg_formant_amplitude -= avg_formant_amplitude_norm[formant_index-1]
                avg_formant_duration -= avg_formant_duration_norm[formant_index-1]

                # s = f'delta F{formant_index}: {avg_formant_frequency:.2f} | formant_bandwidth: {avg_formant_bandwidth:.2f} | formant_energy: {avg_formant_energy:.2f} | formant_intensity: {avg_formant_intensity:.2f} | formant_amplitude: {avg_formant_amplitude:.2f} | formant_duration: {avg_formant_duration:.2f}'
                # s = f'delta F{formant_index}: {avg_formant_frequency:.2f}'
                s = f'delta F{formant_index}: {avg_formant_intensity:.2f}'
                # datas.append(s)

    # Сохранение названий файлов в выходной файл
    with open(output_file, 'w') as f:
        for data in datas:
            f.write(f"{data}\n")

# Пример использования
directory = "emotions"
output_file = "outO.txt"
directory = "emotionsJ"
output_file = "outJ.txt"
save_filenames_without_extension(directory, output_file)
