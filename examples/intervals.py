import os
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment

from sk_speech import sk_formants as fmt
from sk_speech import sk_pitch as pt
from sk_speech import sk_volume as vm
from sk_speech import sk_vowels as vw

def analyze_text_in_intervals(audio_file, text, common_intervals):
    """
    Анализирует текст в интервалах времени для аудиофайла.

    Параметры:
        audio_file (str): Путь к аудиофайлу.
        text (str): Текст аудиофайла.
        common_intervals (list): Список интервалов в формате [(start, end), ...].

    Возвращает:
        dict: Словарь с результатами анализа:
              - буквы, попавшие в `common_intervals`;
              - процент времени букв в интервалах.
    """
    # 1. Загрузка аудиофайла и определение его длины
    audio = AudioSegment.from_file(audio_file)
    audio = vm.trim_silence_pydub(audio)
    audio_length_ms = len(audio)  # Длина аудио в миллисекундах
    # audio_length_ms = 854.5
    print("Длина аудио в миллисекундах:", audio_length_ms)

    # 2. Длина текста
    text_length = len(text)

    # 3. Длина интервала для одной буквы
    letter_duration = audio_length_ms / text_length  # Длительность одной буквы в мс
    print("Длина интервала для одной буквы:", letter_duration)


    # 4. Интервалы времени для каждой буквы
    letter_intervals = [(i * letter_duration, (i + 1) * letter_duration) for i in range(text_length)]

    # 5. Определение букв, попавших в common_intervals
    common_letters = []  # Список букв, попавших в common_intervals
    common_time = []  # Общее время букв в common_intervals

    for i, (start, end) in enumerate(letter_intervals):
        for interval_start, interval_end in common_intervals:
            # Проверяем пересечение интервала буквы с common_intervals
            overlap_start = max(start, interval_start)
            overlap_end = min(end, interval_end)
            if overlap_start < overlap_end:  # Есть пересечение
                common_letters.append(text[i])
                v = (overlap_end - overlap_start) * 100 / (end - start)
                common_time.append(v)

    # Результаты
    return {
        "letters_in_common_intervals": common_letters,
        "percentage_in_common_intervals": common_time,
    }

def find_frequency_peaks(freq_files, bw_files, time_files):
    """
    Находит пики частот, их ширину канала и длительности для каждого файла.

    Параметры:
        freq_files (list): Список массивов частот, один массив на файл.
        bw_files (list): Список массивов ширины канала, один массив на файл.
        time_files (list): Список массивов времени, один массив на файл.

    Возвращает:
        list: Список списков кортежей (peak_freq, peak_bw, duration) для каждого файла.
    """
    all_peaks = []

    for freq, bw, times in zip(freq_files, bw_files, time_files):
        if len(freq) != len(times) or len(freq) != len(bw):
            raise ValueError("Длины массивов freq, bw и times должны совпадать.")

        peaks = []
        n = len(freq)

        if n < 2:
            continue

        # Добавляем первый элемент как пик
        peaks.append((freq[0], bw[0], times[1] - times[0] if n > 1 else 0))

        # Находим внутренние пики
        for i in range(1, n - 1):
            if (freq[i] > freq[i - 1] and freq[i] > freq[i + 1]) or (freq[i] < freq[i - 1] and freq[i] < freq[i + 1]):
                duration = times[i + 1] - times[i]
                peaks.append((freq[i], bw[i], duration))

        # Добавляем последний элемент как пик
        peaks.append((freq[-1], bw[-1], 0))

        all_peaks.append(peaks)

    return all_peaks


def calculate_peak_slopes(freq_files, bw_files, time_files):
    """
    Рассчитывает углы наклона пиков частот, ширины каналов и длительности между пиками для каждого файла.

    Параметры:
        freq_files (list): Список массивов частот, один массив на файл.
        bw_files (list): Список массивов ширины канала, один массив на файл.
        time_files (list): Список массивов времени, один массив на файл.

    Возвращает:
        tuple:
            - list: Список списков частот пиков для каждого файла.
            - list: Список списков ширины каналов пиков для каждого файла.
            - list: Список списков углов наклона частот между пиками для каждого файла.
            - list: Список списков разницы ширины каналов между пиками для каждого файла.
            - list: Список списков углов наклона ширины каналов между пиками для каждого файла.
            - list: Список списков длительностей между пиками для каждого файла.
            - list: Список списков времени начала каждого пика для каждого файла.
    """
    all_peak_frequencies = []
    all_peaks_diff = []
    all_slopes = []
    all_peak_bw = []
    all_bw_diff = []
    all_bw_slopes = []
    all_durations = []
    all_times = []

    # Для каждого файла
    for freq, bw, times in zip(freq_files, bw_files, time_files):
        if (len(freq) == 0) or (len(bw) == 0) or (len(times) == 0):
            continue

        # Находим пики
        peaks = find_frequency_peaks([freq], [bw], [times])[0]

        # Извлекаем частоты, ширину канала и времена пиков
        peak_frequencies = [peak[0] for peak in peaks]
        peak_bw = [peak[1] for peak in peaks]
        peak_times = [times[i] for i in range(len(freq)) if freq[i] in peak_frequencies]

        # Рассчитываем углы наклона между пиками
        peaks_diff = []
        bw_diff = []
        bw_slopes = []
        slopes = []
        durations = []
        for i in range(1, len(peak_frequencies)):
            freq_diff = peak_frequencies[i] - peak_frequencies[i - 1]
            bw_difference = peak_bw[i] - peak_bw[i - 1]
            time_diff = peak_times[i] - peak_times[i - 1]

            if time_diff != 0:
                slopes.append(freq_diff / time_diff)
                bw_slopes.append(bw_difference / time_diff)
            else:
                slopes.append(0)
                bw_slopes.append(0)

            peaks_diff.append(freq_diff)
            bw_diff.append(bw_difference)
            durations.append(time_diff)

        # Добавляем результаты для текущего файла
        all_peak_frequencies.append(peak_frequencies)
        all_peak_bw.append(peak_bw)
        all_peaks_diff.append(peaks_diff)
        all_slopes.append(slopes)
        all_bw_diff.append(bw_diff)
        all_bw_slopes.append(bw_slopes)
        all_durations.append(durations)
        all_times.append(peak_times)

    return all_peak_frequencies, all_peaks_diff, all_slopes, all_peak_bw, all_bw_diff, all_bw_slopes, all_durations, all_times


def filter_short_durations(
    peak_freqs, peak_diff, slopes, peak_bw, bw_diff, bw_slopes,
    durations, times, eps=10
):
    """
    Фильтрует пики, ширину канала и длительности, удаляя участки с длительностью меньше заданного порога.

    Параметры:
        peak_freqs (list): Список частот пиков для каждого файла.
        peak_diff (list): Список разниц частот между пиками для каждого файла.
        slopes (list): Список углов наклона частот между пиками для каждого файла.
        durations (list): Список длительностей между пиками для каждого файла.
        times (list): Список времен начала каждого пика для каждого файла.
        peak_bw (list): Список ширины канала пиков для каждого файла.
        bw_diff (list): Список разниц ширины канала между пиками для каждого файла.
        bw_slopes (list): Список углов наклона ширины канала между пиками для каждого файла.
        eps (float): Порог длительности. Участки с длительностью меньше этого значения объединяются с предыдущими.

    Возвращает:
        tuple:
            - new_peak_freqs: Список фильтрованных частот пиков.
            - new_peak_diff: Список фильтрованных разниц частот между пиками.
            - new_slopes: Список фильтрованных углов наклона частот.
            - new_durations: Список фильтрованных длительностей.
            - new_times: Список фильтрованных времен начала пиков.
            - new_peak_bw: Список фильтрованных ширин каналов.
            - new_bw_diff: Список фильтрованных разниц ширин каналов.
            - new_bw_slopes: Список фильтрованных углов наклона ширины каналов.
    """
    new_peak_freqs = []
    new_peak_diff = []
    new_slopes = []
    new_durations = []
    new_times = []
    new_peak_bw = []
    new_bw_diff = []
    new_bw_slopes = []

    for file_peaks, file_peak_diff, file_slopes, file_bw, file_bw_diff, file_bw_slopes, file_durations, file_times in zip(
        peak_freqs, peak_diff, slopes, peak_bw, bw_diff, bw_slopes, durations, times
    ):
        filtered_peak_freqs = []
        filtered_peak_diff = []
        filtered_slopes = []
        filtered_durations = []
        filtered_times = []
        filtered_peak_bw = []
        filtered_bw_diff = []
        filtered_bw_slopes = []

        for i in range(len(file_peaks)):
            if i == 0:
                # Добавляем первый пик
                filtered_peak_freqs.append(file_peaks[i])
                filtered_peak_bw.append(file_bw[i])
                filtered_times.append(file_times[i])
            elif i - 1 < len(file_durations):  # Проверяем корректность индекса
                if file_durations[i - 1] < eps:
                    if filtered_durations:
                        # Если длительность меньше порога, добавляем её к предыдущему участку
                        filtered_durations[-1] += file_durations[i - 1]
                else:
                    # Добавляем текущий пик, его длительность, ширину канала и время
                    filtered_peak_freqs.append(file_peaks[i])
                    filtered_peak_bw.append(file_bw[i])
                    filtered_durations.append(file_durations[i - 1])
                    filtered_times.append(file_times[i])

        # Углы наклона и разницы ширины канала вычисляются только между оставшимися пиками
        for j in range(1, len(filtered_peak_freqs)):
            freq_diff = filtered_peak_freqs[j] - filtered_peak_freqs[j - 1]
            bw_difference = filtered_peak_bw[j] - filtered_peak_bw[j - 1]
            duration = filtered_durations[j - 1]

            # Для частот
            filtered_peak_diff.append(freq_diff if duration != 0 else 0)
            filtered_slopes.append(freq_diff / duration if duration != 0 else 0)

            # Для ширины канала
            filtered_bw_diff.append(bw_difference)
            filtered_bw_slopes.append(bw_difference / duration if duration != 0 else 0)

        # Добавляем результаты для текущего файла
        new_peak_freqs.append(filtered_peak_freqs)
        new_peak_diff.append(filtered_peak_diff)
        new_slopes.append(filtered_slopes)
        new_peak_bw.append(filtered_peak_bw)
        new_bw_diff.append(filtered_bw_diff)
        new_bw_slopes.append(filtered_bw_slopes)
        new_durations.append(filtered_durations)
        new_times.append(filtered_times)

    return new_peak_freqs, new_peak_diff, new_slopes, new_peak_bw, new_bw_diff, new_bw_slopes, new_durations, new_times


def extract_speech(input_audio_file):
    y, sr = librosa.load(input_audio_file)
    # y = vm.trim_silence(y, sr)
    y, sr = pt.flatten_pitch(y, sr)
    if y is None:
        return None, None, None, None

    # f, t, intensity_values, intensity_times, _, _, _ = pt.extract_f0_voiced(y, sr, speech=True, time_step=0.001)
    # if f is None:
    #     return False

    f, t, bandwidths, _ = fmt.formant_frequencies(y, sr, speech=True, time_step=0.001)
    try:
        if f is None:
            return None, None, None, None
        freq1 = np.array(f[0])
        freq2 = np.array(f[1])
        if bandwidths is None:
            return None, None, None, None
        bandwidth1 = np.array(bandwidths[0])
        bandwidth2 = np.array(bandwidths[1])
        times = np.array(t)
    except ValueError:
        return False

    mask = freq1 > 0
    freq1 = freq1[mask]
    bandwidth1 = bandwidth1[mask]
    times1 = times[mask]

    mask = freq2 > 0
    freq2 = freq2[mask]
    bandwidth2 = bandwidth2[mask]
    times2 = times[mask]


    return freq1, bandwidth1, times1, freq2, bandwidth2, times2

def find_common_intervals(segment_gradients1, segment_bw1, segment_durations1, segment_times1,
                          segment_gradients2, segment_bw2, segment_durations2, segment_times2,
                          eps=1e-6):
    """
    Находит общие интервалы, где градиенты обеих последовательностей находятся в пределах [-5, 5].

    Аргументы:
        segment_gradients1, segment_gradients2: Списки градиентов для F1 и F2.
        segment_durations1, segment_durations2: Списки длительностей для F1 и F2.
        segment_times1, segment_times2: Списки времени начала каждого элемента для F1 и F2.
        eps: Погрешность для синхронизации времени.

    Возвращает:
        Список общих интервалов в формате [(start_time, end_time), ...].
    """
    # Начальные значения
    te = 0
    index1, index2 = 0, 0  # Индексы для массивов F1 и F2
    is_interval = False  # Флаг для отслеживания активного интервала
    intervals = []  # Список интервалов (tb, te)

    while index1 < len(segment_gradients1) and index2 < len(segment_gradients2):
        # Текущие элементы для F1 и F2
        item1_grad = segment_gradients1[index1]
        item2_grad = segment_gradients2[index2]
        item1_bw = segment_bw1[index1]
        item2_bw = segment_bw2[index2]

        # Рассчитываем начальное и конечное время текущего элемента
        time_start1 = segment_times1[index1]
        time_end1 = time_start1 + segment_durations1[index1]
        time_start2 = segment_times2[index2]
        time_end2 = time_start2 + segment_durations2[index2]

        # Общее начальное и конечное время пересечения
        tb = max(time_start1, time_start2)  # начало интервала пересечения
        te = min(time_end1, time_end2)  # конец интервала пересечения

        # Если оба градиента в пределах [-5; 5] и есть пересечение
        if (abs(item1_grad) <= 5 and abs(item2_grad) <= 5 and
            abs(item1_bw) <= 10 and abs(item2_bw) <= 10 and tb < te):
            if not is_interval:
                # Начало нового интервала
                is_interval = True
                interval_start = tb  # запоминаем начало нового интервала
        else:
            if is_interval:
                # Конец текущего интервала
                is_interval = False
                intervals.append((interval_start, tb))  # добавляем интервал в список

        # Рассчитываем новое время t1 и t2
        nt1 = time_end1
        nt2 = time_end2

        # Обновляем индексы и времена
        if abs(nt1 - nt2) < eps:
            index1 += 1
            index2 += 1
        elif nt1 < nt2:
            index1 += 1
        else:
            index2 += 1

    # Завершаем последний интервал, если он активен
    if is_interval:
        intervals.append((interval_start, te))

    return intervals

def merge_close_intervals(intervals, eps=1e-6):
    """
    Объединяет соседние интервалы, если разница между их границами меньше заданного порога.

    Параметры:
        intervals (list): Список интервалов в формате [(start_time, end_time), ...].
        eps (float): Пороговое значение разницы между границами интервалов для их объединения.

    Возвращает:
        list: Список объединенных интервалов.
    """
    if not intervals:
        return []

    # Отсортировать интервалы по началу
    intervals.sort(key=lambda x: x[0])

    merged_intervals = [intervals[0]]  # Инициализируем результат первым интервалом

    for current_start, current_end in intervals[1:]:
        last_start, last_end = merged_intervals[-1]

        # Проверяем разницу между концом предыдущего и началом текущего интервала
        if abs(current_start - last_end) < eps:
            # Объединяем интервалы
            merged_intervals[-1] = (last_start, max(last_end, current_end))
        else:
            # Добавляем новый интервал
            merged_intervals.append((current_start, current_end))

    return merged_intervals

window_size = 10  # 20 мс мин для тона
input_audio_file = 'C:/projects/pack/слон/2_volume_down.wav'
# input_audio_file = 'C:/projects/pack/zv/1/Молоко.wav'
freq1, bw1, times1, freq2, bw2, times2 = extract_speech(input_audio_file)

converted_file_freqs = []
converted_file_bw = []
converted_file_times = []
converted_segment_times = np.array(times1) * 1000
converted_file_times.append(converted_segment_times.tolist())
converted_file_freqs.append(freq1)
converted_file_bw.append(bw1)

print("макс время", max(converted_segment_times))
times = converted_file_times
freq = converted_file_freqs
bw = converted_file_bw

peak_freq, peak_diff, freq_slopes, peak_bw, bw_diff, bw_slopes, segment_durations, peak_times = calculate_peak_slopes(freq, bw, times)
peak_freqs, peak_diff, peak_slopes, peak_bw, bw_diff, bw_slopes, segment_durations, peak_times = filter_short_durations(peak_freq,
                                                                                peak_diff,
                                                                                freq_slopes,
                                                                                peak_bw,
                                                                                bw_diff,
                                                                                bw_slopes,
                                                                                segment_durations,
                                                                                peak_times,
                                                                                eps=window_size)

segment_gradients1 = np.concatenate(peak_slopes)
segment_bw1 = np.concatenate(bw_slopes)
segment_durations1 = np.concatenate(segment_durations)
segment_times1 = np.concatenate(peak_times)


converted_file_freqs = []
converted_file_bw = []
converted_file_times = []
converted_segment_times = np.array(times2) * 1000
converted_file_times.append(converted_segment_times.tolist())
converted_file_freqs.append(freq2)
converted_file_bw.append(bw2)

times = converted_file_times
freq = converted_file_freqs
bw = converted_file_bw

peak_freq, peak_diff, freq_slopes, peak_bw, bw_diff, bw_slopes, segment_durations, peak_times = calculate_peak_slopes(freq, bw, times)
peak_freqs, peak_diff, peak_slopes, peak_bw, bw_diff, bw_slopes, segment_durations, peak_times = filter_short_durations(peak_freq,
                                                                                peak_diff,
                                                                                freq_slopes,
                                                                                peak_bw,
                                                                                bw_diff,
                                                                                bw_slopes,
                                                                                segment_durations,
                                                                                peak_times,
                                                                                eps=window_size)

segment_gradients2 = np.concatenate(peak_slopes)
segment_bw2 = np.concatenate(bw_slopes)
segment_durations2 = np.concatenate(segment_durations)
segment_times2 = np.concatenate(peak_times)


common_intervals = find_common_intervals(segment_gradients1, segment_bw1, segment_durations1, segment_times1,
                                         segment_gradients2, segment_bw2, segment_durations2, segment_times2)
merged_intervals = merge_close_intervals(common_intervals, eps=100)
print("Общие интервалы:", merged_intervals)

text = "слон"
# text = "молоко"

result = analyze_text_in_intervals(input_audio_file, text, merged_intervals)
print("Буквы в общих интервалах:", result["letters_in_common_intervals"])
print("Процент времени букв в общих интервалах:", result["percentage_in_common_intervals"])

y, sr = librosa.load(input_audio_file)
# y = vm.trim_silence(y, sr)
speed_factor = 10.0
y = vw.stretch_vowels_preserve_pitch7(y, sr, merged_intervals, speed_factor=speed_factor)
sf.write("resize_audio.wav", y, sr)
