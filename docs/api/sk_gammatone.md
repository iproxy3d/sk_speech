# Адаптивная гамматонная обработка

[← К оглавлению API](../API.md)

Модуль: `sk_speech.sk_gammatone`.

ERB-фильтрация с настройкой центральных частот по F0 и формантам.

## Функции

#### `load_audio`

```python
load_audio(filename)
```

Читает аудиофайл через Librosa без принудительного изменения частоты дискретизации.

**Параметры:**

- `filename` — имя или путь к файлу.

**Возвращает:** `tuple` со значениями: `y, sr`.

#### `adjust_center_frequencies_limited`

```python
adjust_center_frequencies_limited(center_freqs, pitch_freq, formants, max_shift_ratio=0.1, max_shift_limit=100)
```

Настраивает центральные частоты фильтров с учетом ограничения на смещение, с нелинейным уменьшением допустимого сдвига для высоких частот.

**Параметры:**

- `center_freqs` — Массив центральных частот..
- `pitch_freq` — Частота pitch..
- `formants` — Список частот формант F1-F5..
- `max_shift_ratio` — Максимальный процент смещения от текущей частоты..
- `max_shift_limit` — Максимальный предел смещения в герцах..

**Возвращает:** результат выражения `adjusted_center_freqs`.

#### `get_adaptive_weights`

```python
get_adaptive_weights(freq)
```

Выбирает набор весов F0 и формант в зависимости от анализируемой центральной частоты.

**Параметры:**

- `freq` — частота или последовательность частот, Гц.

**Возвращает:** `tuple` со значениями: `0.6, 0.2, 0.15, 0.05`.

#### `filter_center_frequencies`

```python
filter_center_frequencies(center_frequencies, pitch_freq, formants, pitch_threshold=200, formant_thresholds=None)
```

Оставляет центральные частоты банка, согласованные с F0 и формантами в пределах заданных порогов.

**Параметры:**

- `center_frequencies` — частота или последовательность частот, Гц.
- `pitch_freq` — частота или последовательность частот, Гц.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.
- `pitch_threshold` — порог принятия решения.
- `formant_thresholds` — порог принятия решения.

**Возвращает:** `numpy.ndarray` — рассчитанный сигнал или числовая последовательность.

#### `apply_erb_filterbank`

```python
apply_erb_filterbank(audio_data, sampling_rate, n_filters=20, lowcut=100, highcut=5500, speech=True)
```

Строит ERB-банк, адаптирует его центральные частоты к речи и возвращает матрицу каналов и пороги их объединения.

**Параметры:**

- `audio_data` — массив аудиосэмплов.
- `sampling_rate` — частота дискретизации, Гц.
- `n_filters` — число каналов фильтров.
- `lowcut` — нижняя частота полосы пропускания, Гц.
- `highcut` — верхняя частота полосы пропускания, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.

**Возвращает:** `tuple` со значениями: `filtered_matrix, thresholds`.

#### `combine_filtered_signals`

```python
combine_filtered_signals(filtered_matrix, thresholds)
```

Объединяет выходы каналов гамматонного банка с учётом их порогов и нормализует итоговый сигнал.

**Параметры:**

- `filtered_matrix` — матрица выходов фильтрбанка «канал × сэмпл».
- `thresholds` — порог принятия решения.

**Возвращает:** `numpy.ndarray` — рассчитанный сигнал или числовая последовательность.

#### `split_audio_into_chunks`

```python
split_audio_into_chunks(audio_data, sr, chunk_length=None)
```

Разбивает аудиосигнал на фрагменты фиксированной длины.

**Параметры:**

- `audio_data` — Массив с аудиоданными..
- `sr` — Частота дискретизации..
- `chunk_length` — Длина каждого фрагмента в секундах..

**Возвращает:** результат выражения `chunks`.

#### `process_chunks`

```python
process_chunks(chunks, sr, NCHANNELS, LOW_CUTOFF, HIGH_CUTOFF, speech=True)
```

Применяет фильтры и объединяет фильтрованные сигналы для каждого фрагмента.

**Параметры:**

- `chunks` — Список аудиофрагментов..
- `sr` — Частота дискретизации..
- `NCHANNELS` — Количество каналов фильтров..
- `LOW_CUTOFF` — Нижняя граница фильтра..
- `HIGH_CUTOFF` — Верхняя граница фильтра..
- `speech` — режим или структура профиля речи — зависит от функции.

**Возвращает:** результат выражения `processed_chunks`.

#### `combine_chunks`

```python
combine_chunks(processed_chunks)
```

Склеивает обработанные фрагменты в один аудиосигнал.

**Параметры:**

- `processed_chunks` — Список обработанных фрагментов..

**Возвращает:** `numpy.ndarray` — рассчитанный сигнал или числовая последовательность.

#### `process_file`

```python
process_file(input_file, output_file, chunk_length=0.3, speech=True, n_channels=NCHANNELS, low_cutoff=LOW_CUTOFF, high_cutoff=HIGH_CUTOFF)
```

Выполняет полный цикл обработки входных данных.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.
- `chunk_length` — длина блока потоковой обработки.
- `speech` — режим или структура профиля речи — зависит от функции.
- `n_channels` — число каналов фильтров.
- `low_cutoff` — нижняя частота фильтрбанка, Гц.
- `high_cutoff` — верхняя частота фильтрбанка, Гц.

**Возвращает:** `tuple` со значениями: `output_audio, sampling_rate`.
