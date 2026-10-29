import numpy as np
import librosa
import scipy.io.wavfile as wav
import soundfile as sf
from . import sk_filters as fl
from . import sk_pitch as pt
from . import sk_formants as fmt

# Параметры фильтров и аудиофайла
FRAMERATE = 16000  # Частота дискретизации
NCHANNELS = 20  # Количество фильтров
LOW_CUTOFF = 50  # Частота отсечки
HIGH_CUTOFF = 5500

# Загрузка WAV файла
def load_audio(filename):
    y, sr = librosa.load(filename, sr=None)
    return y, sr

def adjust_center_frequencies_limited(center_freqs, pitch_freq, formants, max_shift_ratio=0.1, max_shift_limit=100):
    """
    Настраивает центральные частоты фильтров с учетом ограничения на смещение,
    с нелинейным уменьшением допустимого сдвига для высоких частот.

    :param center_freqs: Массив центральных частот.
    :param pitch_freq: Частота pitch.
    :param formants: Список частот формант F1-F5.
    :param max_shift_ratio: Максимальный процент смещения от текущей частоты.
    :param max_shift_limit: Максимальный предел смещения в герцах.
    :return: Модифицированные центральные частоты.
    """
    adjusted_center_freqs = np.copy(center_freqs)

    if pitch_freq > 0:
        freq = formants + [pitch_freq]
    else:
        freq = formants

    for formant in freq:
        closest_idx = np.argmin(np.abs(adjusted_center_freqs - formant))
        closest_freq = adjusted_center_freqs[closest_idx]

        # Вычисляем допустимое смещение как минимум между процентом от текущей частоты и фиксированным лимитом
        max_shift = min(max_shift_ratio * closest_freq, max_shift_limit)
        
        # Новая частота ограничена в пределах [closest_freq - max_shift, closest_freq + max_shift]
        new_freq = np.clip(formant, closest_freq - max_shift, closest_freq + max_shift)

        # Обновляем центральную частоту
        adjusted_center_freqs[closest_idx] = new_freq

    return adjusted_center_freqs

def get_adaptive_weights(freq):
    if freq < 500:
        # Для низких частот
        return 0.6, 0.2, 0.15, 0.05
    elif 500 <= freq <= 2000:
        # Для средних частот
        return 0.5, 0.3, 0.15, 0.05
    else:
        # Для высоких частот
        return 0.4, 0.3, 0.2, 0.1


def filter_center_frequencies(center_frequencies, pitch_freq, formants, pitch_threshold=200, formant_thresholds=None):
    if formant_thresholds is None:
        # Устанавливаем пороговые значения отклонений для каждой форманты, если они не заданы
        formant_thresholds = [300, 400, 100, 100, 500]  # Например, для F1-F5 соответственно

    filtered_frequencies = []

    for freq in center_frequencies:
        # Проверяем отклонение от pitch_freq
        if pitch_freq > 0:
            pitch_distance = np.abs(freq - pitch_freq)
            if pitch_distance <= pitch_threshold:
                filtered_frequencies.append(freq)
                continue  # Если частота удовлетворяет критерию pitch, добавляем и идём дальше

        # Проверяем отклонения от формант
        for i, formant_freq in enumerate(formants):
            if i < len(formant_thresholds):  # Проверяем, что для форманты задан порог
                formant_distance = np.abs(freq - formant_freq)
                if formant_distance <= formant_thresholds[i]:
                    filtered_frequencies.append(freq)
                    break  # Если частота удовлетворяет критерию форманты, добавляем и выходим из цикла

    return np.array(filtered_frequencies)

# Применение фильтров к аудиосигналу
def apply_erb_filterbank(audio_data, sampling_rate, n_filters=20, lowcut=100, highcut=5500, speech=True):
    # Определение центра частот для фильтров
    CENTER_FREQUENCIES = fl.centre_freqs(sampling_rate, n_filters, cutoff=lowcut)
    formants = []

    if speech:
        pitch_values, _, _, _, _, _, _ = pt.extract_f0_voiced(audio_data, sampling_rate, True)
        if np.any(~np.isnan(pitch_values)):
            pitch_freq = np.nanmean(pitch_values)
        else:
            pitch_freq = 0

        formants_values, _, _, _ = fmt.formant_frequencies(audio_data, sampling_rate, True)
        for freq in formants_values:
            if np.any(~np.isnan(freq)):
                formant_freq = np.nanmean(freq)
                formants.append(formant_freq)

        if pitch_freq > 0 or len(formants) > 0:
            # Ограничиваем смещение до 10% от частоты, но не более 100 Гц
            CENTER_FREQUENCIES = adjust_center_frequencies_limited(CENTER_FREQUENCIES, pitch_freq, formants,
                                                                   max_shift_ratio=0.1, max_shift_limit=100)

            # CENTER_FREQUENCIES = filter_center_frequencies(CENTER_FREQUENCIES, pitch_freq, formants)

    # Применение highcut фильтрации
    if highcut > 0:
        CENTER_FREQUENCIES = CENTER_FREQUENCIES[CENTER_FREQUENCIES <= highcut]

    # Проверка на случай, если все фильтры исключены
    if len(CENTER_FREQUENCIES) == 0:
        raise ValueError("All filter frequencies are above highcut value. No filters to apply.")

    # Создание фильтров
    FILTERBANK_COEFFICIENTS = fl.make_erb_filters(sampling_rate, CENTER_FREQUENCIES)

    # Рассчет thresholds для каждой центральной частоты с учетом всех формант
    thresholds = []

    for freq in CENTER_FREQUENCIES:
        total_threshold = 0
        total_weight = 0

        # Получение адаптивных весов для текущей частоты
        energy_weight, intensity_weight, amplitude_weight, spectral_tilt_weight = get_adaptive_weights(freq)

        for formant_index, formant_freq in enumerate(formants):
            delta = abs(freq - formant_freq)

            energy = fmt.calculate_formant_energy3(audio_data, sampling_rate, formant_index + 1)
            intensity = fmt.calculate_formant_intensity_avg(audio_data, sampling_rate, formant_index + 1)
            amplitude = fmt.calculate_formant_amplitude_avg(audio_data, sampling_rate, formant_index + 1) + 100
            spectral_tilt, _, _ = fmt.calculate_formant_slope(audio_data, sampling_rate, formant_index + 1,
                                                              is_smooth=True, is_peak=False,)

            normalized_energy = energy / max(1e-10, np.nanmax(energy))
            normalized_intensity = intensity / max(1e-10, np.nanmax(intensity))
            normalized_amplitude = amplitude / max(1e-10, np.nanmax(amplitude))
            normalized_spectral_tilt = spectral_tilt / max(1e-10, np.nanmax(spectral_tilt))

            formant_threshold = (energy_weight * normalized_energy +
                                 intensity_weight * normalized_intensity +
                                 amplitude_weight * normalized_amplitude +
                                 spectral_tilt_weight * normalized_spectral_tilt) / (1 + delta)

            total_threshold += formant_threshold
            total_weight += 1 / (1 + delta)

        if total_weight > 0:
            avg_threshold = total_threshold / total_weight
        else:
            avg_threshold = 0
        avg_threshold *= 0.01

        thresholds.append(avg_threshold)

    # Применение фильтров
    filtered_matrix = fl.erb_filterbank(audio_data, FILTERBANK_COEFFICIENTS)

    return filtered_matrix, thresholds


def combine_filtered_signals(filtered_matrix, thresholds):
    # Ensure the length of thresholds matches the number of filters
    if len(thresholds) != filtered_matrix.shape[0]:
        raise ValueError("The length of the thresholds array must match the number of filters in the filtered matrix.")
    
    # Compute the maximum amplitude of the signal from each filter
    max_amplitudes = np.max(np.abs(filtered_matrix), axis=1)

    # Create a mask to exclude filters with max amplitude below their respective threshold
    # mask = max_amplitudes >= thresholds
    mask = max_amplitudes >= 0.01

    # Apply the mask to the filtered matrix
    filtered_matrix_masked = filtered_matrix[mask]

    # Combine the signals from the remaining filters
    combined_signal = np.sum(filtered_matrix_masked, axis=0)

    return combined_signal


def split_audio_into_chunks(audio_data, sr, chunk_length=None):
    """
    Разбивает аудиосигнал на фрагменты фиксированной длины.

    :param audio_data: Массив с аудиоданными.
    :param chunk_length: Длина каждого фрагмента в секундах.
    :param sr: Частота дискретизации.
    :return: Список фрагментов.
    """
    if chunk_length:
        chunk_samples = int(chunk_length * sr)  # Количество сэмплов в одном фрагменте
        num_chunks = len(audio_data) // chunk_samples
        chunks = [audio_data[i * chunk_samples:(i + 1) * chunk_samples] for i in range(num_chunks)]

        # Если остались данные в конце, добавляем их как последний фрагмент
        if len(audio_data) % chunk_samples != 0:
            chunks.append(audio_data[num_chunks * chunk_samples:])
    else:
        chunks = [audio_data]

    return chunks


def process_chunks(chunks, sr, NCHANNELS, LOW_CUTOFF, HIGH_CUTOFF, speech=True):
    """
    Применяет фильтры и объединяет фильтрованные сигналы для каждого фрагмента.

    :param chunks: Список аудиофрагментов.
    :param sr: Частота дискретизации.
    :param NCHANNELS: Количество каналов фильтров.
    :param LOW_CUTOFF: Нижняя граница фильтра.
    :param HIGH_CUTOFF: Верхняя граница фильтра.
    :param threshold: Порог для объединения фильтрованных сигналов.
    :return: Список обработанных фрагментов.
    """
    processed_chunks = []
    for chunk in chunks:
        filtered_matrix, thresholds = apply_erb_filterbank(chunk, sr, NCHANNELS, lowcut=LOW_CUTOFF, highcut=HIGH_CUTOFF,
                                                           speech=speech)
        # print("Форма фильтрованной матрицы:", filtered_matrix.shape)
        filtered_chunk = combine_filtered_signals(filtered_matrix, thresholds=thresholds)

        processed_chunks.append(filtered_chunk)

    return processed_chunks


def combine_chunks(processed_chunks):
    """
    Склеивает обработанные фрагменты в один аудиосигнал.

    :param processed_chunks: Список обработанных фрагментов.
    :return: Объединенный аудиосигнал.
    """
    return np.concatenate(processed_chunks)

def process_file(input_file, output_file, chunk_length=0.3, speech=True,
                 n_channels=NCHANNELS, low_cutoff=LOW_CUTOFF, high_cutoff=HIGH_CUTOFF):
    """Apply the adaptive gammatone pipeline to one audio file."""

    audio_data, sampling_rate = load_audio(input_file)
    chunks = split_audio_into_chunks(audio_data, chunk_length=chunk_length, sr=sampling_rate)
    processed_chunks = process_chunks(
        chunks, sampling_rate, n_channels, low_cutoff, high_cutoff, speech=speech
    )
    output_audio = fl.normalize_audio(combine_chunks(processed_chunks))
    sf.write(output_file, output_audio, sampling_rate)
    return output_audio, sampling_rate


if __name__ == '__main__':
    process_file('many_voice27.wav', 'out_gammatone27.wav')
