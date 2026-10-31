# Форманты F1–F5

[← К оглавлению API](../API.md)

Модуль: `sk_speech.sk_formants`.

Извлечение, измерение, динамика, паттерны, синтез и преобразование формант.

## Функции

#### `formant_range`

```python
formant_range(formant_index)
```

Возвращает допустимый частотный диапазон для заданного номера форманты.

**Параметры:**

- `formant_index` — номер форманты: 1 соответствует F1.

**Возвращает:** результат выражения `formant_ranges[formant_index][1] - formant_ranges[formant_index][0]`.

#### `get_formants_with_retries`

```python
get_formants_with_retries(sound, time_step=0.01, max_number_of_formants=5, pitch_to=5500)
```

Пытается построить объект Formant Praat, повторяя расчёт с альтернативными настройками при ошибке.

**Параметры:**

- `sound` — объект аудиосигнала Praat или Pydub согласно функции.
- `time_step` — временной шаг анализа, с.
- `max_number_of_formants` — данные или параметры формант.
- `pitch_to` — верхняя граница F0, Гц.

**Возвращает:** результат выражения `formants | None`.

#### `analyze_formants_alternative`

```python
analyze_formants_alternative(signal, sr, speech=True, time_step=0.01, method='praat')
```

Альтернативное извлечение формант для проверки влияния метода.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.
- `time_step` — временной шаг анализа, с.
- `method` — имя выбираемого алгоритма.

**Возвращает:** `tuple` со значениями: `frequencies, times, bandwidths, intensities`.

#### `extract_formants_via_lpc`

```python
extract_formants_via_lpc(signal, sr, frame_length=0.03, hop_length=0.01, lpc_order=12)
```

Извлечение динамических значений формант через LPC для всего аудиосигнала.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.
- `lpc_order` — порядок линейного предсказания.

**Возвращает:** `tuple` со значениями: `formants_over_time, times`.

#### `formant_frequencies`

```python
formant_frequencies(signal, sr, speech=True, time_step=0.01)
```

Извлекает покадровые частоты и ширины F1–F5 из объекта Formant Praat.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.
- `time_step` — временной шаг анализа, с.

**Возвращает:** `tuple` со значениями: `None, None, None, None`.

#### `formant_frequencies2`

```python
formant_frequencies2(signal, sr, speech=True, time_step=0.01)
```

Альтернативно извлекает частоты и ширины F1–F5 с фильтрацией некорректных значений.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.
- `time_step` — временной шаг анализа, с.

**Возвращает:** `tuple` со значениями: `None, None, None, None`.

#### `get_formant_info`

```python
get_formant_info(signal, sr)
```

Строит объекты Sound и Formant Praat и возвращает их вместе с исходным массивом и частотой дискретизации для повторных расчётов.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `formant_frequencies_expended`

```python
formant_frequencies_expended(signal, sr, speech=True, time_step=0.01, max_number_of_formants=5)
```

Извлекает расширенные ряды частот, ширин и временных меток F1–F5 с настраиваемым числом формант.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.
- `time_step` — временной шаг анализа, с.
- `max_number_of_formants` — данные или параметры формант.

**Возвращает:** `tuple` со значениями: `None, None, None, None`.

#### `extract_formants`

```python
extract_formants(signal, sr, speech=True, formants=None)
```

Извлекает частоты формант F1–F5 из аудиосигнала.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** результат выражения `freqs`.

#### `extract_formants_from_segment`

```python
extract_formants_from_segment(signal_segment, sr, speech=True)
```

Извлекает частоты формант из сегмента сигнала.

**Параметры:**

- `signal_segment` — Сегмент аудиосигнала..
- `sr` — Частота дискретизации..
- `speech` — режим или структура профиля речи — зависит от функции.

**Возвращает:** результат выражения `frequencies`.

#### `extract_formants_and_f0`

```python
extract_formants_and_f0(signal, sr)
```

Извлекает форманты и основной тон (F0) из аудиосигнала с помощью Parselmouth.

**Параметры:**

- `signal` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..

**Возвращает:** `tuple` со значениями: `formants, pitch_values`.

#### `get_formant_frequency_by_index`

```python
get_formant_frequency_by_index(signal, sr, formant_index, formants=None)
```

Возвращает среднюю частоту выбранной форманты.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** результат выражения `formant_frequency`.

#### `remove_outliers`

```python
remove_outliers(data, m=1.5)
```

Удаляет значения, отстоящие от медианы более чем на `m` медианных абсолютных отклонений.

**Параметры:**

- `data` — входные данные соответствующего метода.
- `m` — множитель медианного абсолютного отклонения для отсечения выбросов.

**Возвращает:** результат выражения `data | data[(data >= lower_bound) & (data <= upper_bound)]`.

#### `calculate_formant_bandwidth_`

```python
calculate_formant_bandwidth_(bandwidths, formant_index, method='max')
```

Агрегирует ряд ширин выбранной форманты методом `max`, `mean` или `median`.

**Параметры:**

- `bandwidths` — ширины частотных полос, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `method` — имя выбираемого алгоритма.

**Возвращает:** `float` — средняя ширина полосы выбранной форманты, Гц; `0` при отсутствии данных.

#### `calculate_formant_bandwidth`

```python
calculate_formant_bandwidth(signal, sr, formant_index, speech=True, method='max', formants=None)
```

Рассчитывает ширину полосы выбранной форманты по переданным данным.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `speech` — режим или структура профиля речи — зависит от функции.
- `method` — имя выбираемого алгоритма.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — средняя ширина полосы выбранной форманты, Гц.

#### `calculate_formant_energy`

```python
calculate_formant_energy(signal, sr, formant_index, formants=None)
```

Рассчитывает энергию выбранной форманты по переданным данным.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — суммарная энергия выбранной формантной полосы; `0` при отсутствии данных.

#### `calculate_formant_energy2`

```python
calculate_formant_energy2(signal, sr, formants=None)
```

Рассчитывает энергию выбранной форманты по переданным данным. Это вариант алгоритма №2 с отдельной реализацией.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — энергия форманты по анализируемым кадрам.

#### `calculate_formant_energy_arr`

```python
calculate_formant_energy_arr(signal, sr, formant_index, formants=None)
```

Рассчитывает энергию в частотной полосе выбранной форманты для каждого временного кадра.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `list[float]` — энергия форманты для каждого переданного участка.

#### `calculate_formant_energy3`

```python
calculate_formant_energy3(signal, sr, formant_index, formants=None)
```

Рассчитывает энергию выбранной форманты по переданным данным. Это вариант алгоритма №3 с отдельной реализацией.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — средняя энергия выбранной формантной полосы; `0` при отсутствии данных.

#### `calculate_formant_and_f0_energy`

```python
calculate_formant_and_f0_energy(signal, sr)
```

Рассчитывает энергию формант и F0 в аудиосигнале, используя Parselmouth для извлечения формантов и F0.

**Параметры:**

- `signal` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..

**Возвращает:** `tuple` — энергии формант и средняя энергия F0.

#### `change_formant_energy`

```python
change_formant_energy(y, sr, formant_index, factor)
```

Создаёт преобразованный аудиосигнал, изменяя энергию выбранной форманты.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `factor` — множитель преобразования.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `change_formant_energy2`

```python
change_formant_energy2(signal, sr, energy_factors)
```

Изменяет энергию каждой форманты F1-F5 в аудиосигнале.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `energy_factors` — Список факторов энергии для каждой форманты [E1, E2, E3, E4, E5]..

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `change_formant_energy3`

```python
change_formant_energy3(signal, sr, energy_factors)
```

Изменяет энергию каждой форманты F1-F5.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `energy_factors` — Список факторов энергии для каждой форманты [E1, E2, E3, E4, E5]..

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `change_formant_amplitude`

```python
change_formant_amplitude(signal, sr, factors, formants=None)
```

Создаёт преобразованный аудиосигнал, изменяя амплитуду выбранной форманты.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factors` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `change_formant_amplitude_range`

```python
change_formant_amplitude_range(signal, sr, factors_from, factors_to, formants=None)
```

Плавно меняет амплитуду каждой из F1–F5 от начального к конечному набору множителей.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factors_from` — коэффициент или доля преобразования.
- `factors_to` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `calculate_formant_intensity`

```python
calculate_formant_intensity(signal, sr, formant_index, formants=None)
```

Рассчитывает интенсивность выбранной форманты по переданным данным.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — интенсивность выбранной формантной полосы по времени.

#### `calculate_formant_intensity_avg`

```python
calculate_formant_intensity_avg(signal, sr, formant_index, formants=None)
```

Усредняет интенсивность по временным точкам, в которых выбранная форманта имеет корректную частоту.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — средняя интенсивность выбранной форманты.

#### `calculate_formant_amplitude`

```python
calculate_formant_amplitude(signal, sr, formant_index, formants=None)
```

Рассчитывает амплитуду выбранной форманты по переданным данным.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — средняя амплитуда выбранной форманты; `0` при отсутствии данных.

#### `calculate_formant_amplitude_avg`

```python
calculate_formant_amplitude_avg(signal, sr, formant_index, formants=None)
```

Усредняет амплитуду спектра в полосе выбранной форманты по всем корректным кадрам.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — средняя амплитуда выбранной форманты в децибелах.

#### `calculate_formant_duration`

```python
calculate_formant_duration(signal, sr, formant_index, formants=None)
```

Рассчитывает длительность присутствия выбранной форманты по переданным данным.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — суммарная длительность присутствия форманты, с.

#### `calculate_formant_duration2`

```python
calculate_formant_duration2(y, sr, formant_index, formants=None)
```

Рассчитывает длительность присутствия выбранной форманты по переданным данным. Это вариант алгоритма №2 с отдельной реализацией.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — длительность присутствия форманты, с; `0` при отсутствии данных.

#### `formant_at_index`

```python
formant_at_index(y, sr, index, speech=True, window_size=1024)
```

Вырезает окно вокруг заданного индекса сэмпла и извлекает из этого окна F1–F5.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `index` — индекс анализируемого элемента.
- `speech` — режим или структура профиля речи — зависит от функции.
- `window_size` — размер окна обработки.

**Возвращает:** результат выражения `formants`.

#### `formant_trajectory`

```python
formant_trajectory(y, sr, index, window_size=1024)
```

Перемещает по сигналу перекрывающиеся окна и возвращает временную траекторию частоты выбранной форманты.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `index` — индекс анализируемого элемента.
- `window_size` — размер окна обработки.

**Возвращает:** `tuple` со значениями: `time_stamps, formant_frequencies`.

#### `change_formants_shifts`

```python
change_formants_shifts(signal, sr, formant_shifts)
```

Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_shifts` — данные или параметры формант.

**Возвращает:** `tuple` со значениями: `modified_values[0], int(snd.sampling_frequency)`.

#### `change_formants_shifts2`

```python
change_formants_shifts2(signal, sr, formant_shifts)
```

Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_shifts` — данные или параметры формант.

**Возвращает:** `tuple` со значениями: `modified_signal, sr`.

#### `change_formants_shifts31`

```python
change_formants_shifts31(signal, sr, formant_shifts, formants=None)
```

Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_shifts` — данные или параметры формант.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `modified_signal, sr`.

#### `change_formants_shifts3`

```python
change_formants_shifts3(signal, sr, formant_shifts, max_shift=500, segment_duration=0.01, formants=None)
```

Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты. Сглаживает эффект при больших значениях formant_shifts.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `formant_shifts` — Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5]..
- `max_shift` — Максимальное значение смещения частоты форманты (в герцах)..
- `segment_duration` — Длительность сегмента в секундах, используемого для обработки..
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `modified_signal, sr`.

#### `change_formants_shifts4`

```python
change_formants_shifts4(signal, sr, shift_factors, max_shift=500, formants=None)
```

Изменяет частоту формант в аудиосигнале на фиксированное значение для каждой форманты.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `shift_factors` — Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5]..
- `max_shift` — Максимальное значение смещения частоты форманты (в герцах)..
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `calculate_segment_duration`

```python
calculate_segment_duration(formant_shifts, base_duration=0.0025, S=350, beta=0.1)
```

Подбирает длительность сегмента для сдвига формант в зависимости от максимального требуемого сдвига.

**Параметры:**

- `formant_shifts` — данные или параметры формант.
- `base_duration` — коэффициент или доля преобразования.
- `S` — площадь, масштаб или параметр чувствительности согласно модели.
- `beta` — коэффициент формы, чувствительности или затухания согласно методу.

**Возвращает:** `float` — ограниченная заданным диапазоном длительность сегмента, с.

#### `change_formants_shifts5`

```python
change_formants_shifts5(signal, sr, formant_shifts, max_shift=500, segment_duration=0.01)
```

Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты. Сглаживает эффект при больших значениях formant_shifts. Новые частоты формант остаются в пределах своего диапазона.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `formant_shifts` — Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5]..
- `max_shift` — Максимальное значение смещения частоты форманты (в герцах)..
- `segment_duration` — Длительность сегмента в секундах, используемого для обработки..

**Возвращает:** `tuple` со значениями: `modified_signal, sr`.

#### `change_formants_shifts6`

```python
change_formants_shifts6(signal, sr, formant_shifts, max_shift=500, formants=None)
```

Изменяет частоты формант в аудиофайле на фиксированное значение для каждой форманты. Сглаживает эффект при больших значениях formant_shifts. Новые частоты формант остаются в пределах своего диапазона с возможным сжатием.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `formant_shifts` — Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5]..
- `max_shift` — Максимальное значение смещения частоты форманты (в герцах)..
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `modified_signal, sr`.

#### `boost_formants_filter`

```python
boost_formants_filter(y, sr, boost_dB, max_amplitude_dB)
```

Строит маску полос F1–F5, усиливает их в STFT на `boost_dB`, ограничивает амплитуду и выполняет обратное STFT.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `boost_dB` — усиление формантных полос, дБ.
- `max_amplitude_dB` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `y + y_boosted`.

#### `boost_formants_peak`

```python
boost_formants_peak(signal, sr, gain_dB, max_amplitude_dB)
```

Находит пики вокруг F1–F5 в STFT, усиливает их на `gain_dB` с ограничением уровня и восстанавливает сигнал.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `gain_dB` — усиление спектральных пиков, дБ.
- `max_amplitude_dB` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `y_boosted`.

#### `change_formants_amplitude`

```python
change_formants_amplitude(y, sr, boost_dB, max_amplitude_dB=0)
```

Изменяет амплитуду формант в аудиофайле.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `boost_dB` — усиление формантных полос, дБ.
- `max_amplitude_dB` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `y_boosted`.

#### `change_formants_amplitude2`

```python
change_formants_amplitude2(signal, sr, amplitude_factors, max_amplitude_dB=0)
```

Изменяет амплитуду каждой форманты F1-F5.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `amplitude_factors` — Список факторов амплитуды для каждой форманты [A1, A2, A3, A4, A5]..
- `max_amplitude_dB` — амплитуда или коэффициент амплитуды.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `compute_spectral_slope_for_formant`

```python
compute_spectral_slope_for_formant(y, sr, formant_index, window_size=1024, hop_size=512)
```

Рассчитывает линейный наклон логарифма амплитудного спектра в полосе вокруг выбранной форманты по кадрам.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `window_size` — размер окна обработки.
- `hop_size` — шаг между кадрами, сэмплы.

**Возвращает:** `tuple[numpy.ndarray, numpy.ndarray]` — временные координаты и спектральный наклон формантной области.

#### `compute_spectral_slope_for_formant2`

```python
compute_spectral_slope_for_formant2(signal, sr, formant_index, formants=None)
```

Оценивает спектральный наклон вокруг траектории выбранной форманты с использованием заранее извлечённых формант.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `float` — спектральный наклон формантной области; `0` при отсутствии данных.

#### `change_formant_bandwidth2`

```python
change_formant_bandwidth2(signal, sr, bandwidth_factors, formants=None)
```

Создаёт преобразованный аудиосигнал, изменяя ширину полосы выбранной форманты. Это вариант алгоритма №2 с отдельной реализацией.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `bandwidth_factors` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `change_formant_bandwidth`

```python
change_formant_bandwidth(signal, sr, bandwidth_factors, formants=None)
```

Изменяет ширину канала формант F1-F5 в аудиосигнале вокруг средней частоты форманты.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `bandwidth_factors` — Список факторов ширины канала для каждой форманты [B1, B2, B3, B4, B5]..
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `change_formant_frequencies`

```python
change_formant_frequencies(signal, sr, frequency_factors)
```

Изменяет частоту каждой форманты F1-F5 в заданное количество раз.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `frequency_factors` — Список факторов частоты для каждой форманты [F1, F2, F3, F4, F5]..

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `extract_formant_rate`

```python
extract_formant_rate(y, sr, formant_index=1, medfilt_size=5, formants=None)
```

Извлекает период, фазу и амплитуду колебаний частоты форманты из аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `medfilt_size` — нечётный размер окна медианного фильтра.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `None, None, None`.

#### `calculate_formant_slope`

```python
calculate_formant_slope(y, sr, formant_index=1, is_smooth=True, is_peak=True, formants=None)
```

Рассчитывает наклон и направление изменения частоты форманты по переданным данным.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `is_smooth` — сгладить ряд перед расчётом.
- `is_peak` — рассчитывать наклон по обнаруженным пикам.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple[float, float, str]` — наклон частоты форманты, дисперсия остатков и словесное направление тренда.

#### `calculate_intensity_slope`

```python
calculate_intensity_slope(y, sr, is_smooth=True, is_peak=True, formants=None)
```

Рассчитывает наклон и направление изменения интенсивности по переданным данным.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `is_smooth` — сгладить ряд перед расчётом.
- `is_peak` — рассчитывать наклон по обнаруженным пикам.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple[float, float, str]` — наклон интенсивности, дисперсия остатков и словесное направление тренда.

#### `flatten_formants`

```python
flatten_formants(signal, sr, mean_formant_signals=[0.1, 0.1, 0.1, 0.1, 0.1])
```

Выравнивает форманты F1-F5 на уровне их средней частоты в аудиосигнале, сохраняя исходный сигнал и изменяя частоты формант.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `mean_formant_signals` — данные или параметры формант.

**Возвращает:** `numpy.ndarray` — рассчитанный сигнал или числовая последовательность.

#### `slope_formants`

```python
slope_formants(signal, sr, slope_factors=[0.5, 0.5, 0.5, 0.5, 0.5], mixing_percent=[0.1, 0.1, 0.1, 0.1, 0.1], filtered_percent=[1.0, 1.0, 1.0, 1.0, 1.0], method='center', replace=True)
```

Выделяет полосы F1–F5, синтезирует для них частоты с заданными наклонами и смешивает их с исходным сигналом по отдельным коэффициентам.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `slope_factors` — коэффициент или доля преобразования.
- `mixing_percent` — коэффициент или доля преобразования.
- `filtered_percent` — коэффициент или доля преобразования.
- `method` — имя выбираемого алгоритма.
- `replace` — заменять исходную формантную полосу, а не только добавлять новую.

**Возвращает:** `numpy.ndarray` — рассчитанный сигнал или числовая последовательность.

#### `change_formant_energy_and_shift`

```python
change_formant_energy_and_shift(signal, sr, energy_factors, frequency_shifts, formants=None)
```

Усиливает энергию формант и сдвигает их частоты одновременно.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `energy_factors` — Список коэффициентов усиления для каждой форманты [E1, E2, E3, E4, E5]..
- `frequency_shifts` — Список сдвигов частот для каждой форманты [S1, S2, S3, S4, S5]..
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.

#### `find_max_formant_energy_time`

```python
find_max_formant_energy_time(formant_energy)
```

Находит индекс или временную точку максимальной энергии форманты.

**Параметры:**

- `formant_energy` — энергия или коэффициент энергии.

**Возвращает:** `float` — время максимальной энергии выбранной форманты, с.

#### `segment_and_smooth`

```python
segment_and_smooth(data, num_segments)
```

Разбивает данные на секции и сглаживает их до прямой.

**Параметры:**

- `data` — входные данные соответствующего метода.
- `num_segments` — число сегментов для агрегирования временной динамики.

**Возвращает:** результат выражения `smoothed_segments`.

#### `analyze_formant_patterns`

```python
analyze_formant_patterns(frequencies, bandwidths, formant_ranges, num_segments=3, eps_freq=0.1, eps_width=10)
```

Анализирует последовательности изменений частот и ширины канала, разбитых на секции для каждой форманты.

**Параметры:**

- `frequencies` — частоты или последовательности частот.
- `bandwidths` — ширины частотных полос, Гц.
- `formant_ranges` — данные или параметры формант.
- `num_segments` — число сегментов для агрегирования временной динамики.
- `eps_freq` — частота или последовательность частот, Гц.
- `eps_width` — допуск различия ширин полос, Гц.

**Возвращает:** результат выражения `formant_patterns`.

#### `analyze_formant_patterns2`

```python
analyze_formant_patterns2(frequencies, bandwidths, formant_ranges, num_segments=3, eps_freq=5, eps_width=5, dist=1000, eps_dist=10)
```

Анализирует последовательности изменений частот и ширины канала, разбитых на секции для каждой форманты.

**Параметры:**

- `frequencies` — частоты или последовательности частот.
- `bandwidths` — ширины частотных полос, Гц.
- `formant_ranges` — данные или параметры формант.
- `num_segments` — число сегментов для агрегирования временной динамики.
- `eps_freq` — частота или последовательность частот, Гц.
- `eps_width` — допуск различия ширин полос, Гц.
- `dist` — расстояние между формантами или их паттернами.
- `eps_dist` — допуск различия расстояний между формантами.

**Возвращает:** `tuple` со значениями: `formant_patterns, dist_patterns`.

#### `analyze_formant_patterns3`

```python
analyze_formant_patterns3(frequencies, bandwidths, times, formant_ranges, delta_time=1.0, eps_freq=5, eps_width=5, dist=1000, eps_dist=10)
```

Анализирует последовательности изменений частот, ширины канала и расстояния между соседними формантами, разбитых на секции с учетом временных интервалов.

**Параметры:**

- `frequencies` — частоты или последовательности частот.
- `bandwidths` — ширины частотных полос, Гц.
- `times` — временные координаты, с.
- `formant_ranges` — данные или параметры формант.
- `delta_time` — шаг времени, с.
- `eps_freq` — частота или последовательность частот, Гц.
- `eps_width` — допуск различия ширин полос, Гц.
- `dist` — расстояние между формантами или их паттернами.
- `eps_dist` — допуск различия расстояний между формантами.

**Возвращает:** `tuple` со значениями: `formant_patterns, time_segments`.

#### `analyze_formant_patterns4`

```python
analyze_formant_patterns4(frequencies, bandwidths, times, formant_ranges, delta_time=1.0, eps_freq=5, eps_width=5, dist=1000, eps_dist=10)
```

Анализирует последовательности изменений частот, ширины канала и расстояния между соседними формантами, разбитых на секции с учетом временных интервалов.

**Параметры:**

- `frequencies` — частоты или последовательности частот.
- `bandwidths` — ширины частотных полос, Гц.
- `times` — временные координаты, с.
- `formant_ranges` — данные или параметры формант.
- `delta_time` — шаг времени, с.
- `eps_freq` — частота или последовательность частот, Гц.
- `eps_width` — допуск различия ширин полос, Гц.
- `dist` — расстояние между формантами или их паттернами.
- `eps_dist` — допуск различия расстояний между формантами.

**Возвращает:** `tuple` со значениями: `formant_patterns, time_segments`.

#### `simplify_formant_patterns`

```python
simplify_formant_patterns(formant_patterns, time_segments)
```

Упрощает паттерны формантов, объединяя последовательные одинаковые паттерны и соответствующие временные сегменты.

**Параметры:**

- `formant_patterns` — данные или параметры формант.
- `time_segments` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** результат выражения `simplified_patterns`.

#### `simplify_formant_patterns2`

```python
simplify_formant_patterns2(formant_patterns, time_segments)
```

Упрощает паттерны формантов, объединяя последовательные одинаковые паттерны только в случае совпадения для всех формант и соответствующие временные сегменты.

**Параметры:**

- `formant_patterns` — данные или параметры формант.
- `time_segments` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** результат выражения `simplified_patterns`.

#### `print_simplified_patterns`

```python
print_simplified_patterns(simplified_patterns)
```

Выводит упрощенные паттерны формантов в заданном формате.

**Параметры:**

- `simplified_patterns` — упрощённые паттерны динамики формант.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `classify_phonemes`

```python
classify_phonemes(simplified_patterns, phonems)
```

Классифицирует фонемы на основе упрощенных паттернов формантов.

**Параметры:**

- `simplified_patterns` — упрощённые паттерны динамики формант.
- `phonems` — входные данные соответствующего метода.

**Возвращает:** `str` — метка или текстовый результат классификации.

#### `compare_patterns`

```python
compare_patterns(current, phonema)
```

Сравнивает входные структуры.

**Параметры:**

- `current` — входные данные соответствующего метода.
- `phonema` — входные данные соответствующего метода.

**Возвращает:** результат выражения `pr > 0.8 and pr < 1.2`.

#### `plot_formant_distance_dynamics`

```python
plot_formant_distance_dynamics(formant_patterns, time_segments)
```

Строит график изменения расстояний между соседними формантами на основе результатов анализа.

**Параметры:**

- `formant_patterns` — данные или параметры формант.
- `time_segments` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `calculate_formant_dynamics`

```python
calculate_formant_dynamics(formant_freqs, times, formant_bandwidths, formant_ranges, delta_time=0.05)
```

Рассчитывает динамику отклонения частоты и средней ширины канала для каждой форманты по сегментам времени.

**Параметры:**

- `formant_freqs` — частота или последовательность частот, Гц.
- `times` — временные координаты, с.
- `formant_bandwidths` — ширина полосы или набор ширин, Гц.
- `formant_ranges` — данные или параметры формант.
- `delta_time` — шаг времени, с.

**Возвращает:** `tuple` — динамика формант по сегментам и границы временных сегментов.

#### `plot_formant_dynamics`

```python
plot_formant_dynamics(formant_dynamics, time_segments)
```

Визуализирует динамику отклонения частоты и ширины канала для первых трех формант по времени.

**Параметры:**

- `formant_dynamics` — данные или параметры формант.
- `time_segments` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `generate_varying_bandwidth_signal`

```python
generate_varying_bandwidth_signal(delta_time, start_freq, end_freq, start_bw, end_bw, sample_rate=44100)
```

Генерирует аудиосигнал с периодической функцией, которая изменяется по частоте и ширине канала.

**Параметры:**

- `delta_time` — шаг времени, с.
- `start_freq` — частота или последовательность частот, Гц.
- `end_freq` — частота или последовательность частот, Гц.
- `start_bw` — ширина полосы в начале синтезируемого сигнала, Гц.
- `end_bw` — ширина полосы в конце синтезируемого сигнала, Гц.
- `sample_rate` — частота дискретизации, Гц.

**Возвращает:** `numpy.ndarray` — рассчитанный сигнал или числовая последовательность.

#### `generate_formant_dynamics_sound`

```python
generate_formant_dynamics_sound(formant_dynamics, delta_time, sample_rate=44100)
```

Генерирует аудиосигнал на основе динамики отклонения частот и ширины каналов для каждой форманты.

**Параметры:**

- `formant_dynamics` — данные или параметры формант.
- `delta_time` — шаг времени, с.
- `sample_rate` — частота дискретизации, Гц.

**Возвращает:** результат выражения `final_audio`.
