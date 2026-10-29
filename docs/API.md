# API пакета `sk_speech`

## Временные ряды F0 и интенсивности

Публичные классы и функции импортируются непосредственно из `sk_speech`.

### `PitchConfig`

Параметры извлечения:

- `sample_rate` — рабочая частота дискретизации; `None` сохраняет исходную;
- `frame_step_s` — шаг временной сетки;
- `pitch_floor_hz`, `pitch_ceiling_hz` — допустимый диапазон F0;
- `minimum_voiced_frames` — минимальная длина непрерывного участка F0.

### `PitchExtractor`

- `from_file(path)` — чтение аудиофайла и извлечение признаков;
- `extract(signal, sample_rate)` — обработка массива аудиосэмплов.

Возвращает `PitchTrack`:

- `time_s` — время каждого кадра;
- `f0_hz` — F0 в герцах, `NaN` на неозвученных кадрах;
- `intensity_db` — широкополосная интенсивность на той же временной сетке;
- `voiced` — булева маска озвученных кадров;
- `sample_rate`, `frame_step_s`, `duration_s` — параметры последовательности;
- `to_csv(path)` — сохранение последовательности.

### Калибровка

- `calibrate_pitch(track)` строит `PitchProfile` нейтральной речи;
- `PitchProfile.save(path)` и `PitchProfile.load(path)` сохраняют профиль;
- `normalize_pitch(track, profile)` возвращает `NormalizedPitchTrack`.

## `sk_speech.sk_pitch`

Анализ и преобразование основного тона.

Основные группы функций:

- извлечение F0: `extract_f0`, `extract_f0_segment`, `extract_f0_voiced`,
  `get_pitch_info`;
- статистика: `extract_f0_min_max_avg`, `calculate_pitch_frequency`,
  `calculate_pitch_duration`;
- полоса и энергия: `calculate_pitch_bandwidth`,
  `calculate_pitch_bandwidth2`, `calculate_pitch_bandwidth_welch`,
  `calculate_pitch_energy`;
- интенсивность и амплитуда: `calculate_pitch_intensity`,
  `calculate_pitch_intensity2`, `calculate_pitch_amplitude`;
- динамика: `calculate_pitch_slope`, `calculate_intensity_slope`,
  `calculate_period`, `calculate_period_shift`, `extract_pitch_rate`;
- преобразования: `change_pitch_shift_hz`, `change_pitch_fixed_hz`,
  `change_pitch_intonation`, `flatten_pitch`, `slope_pitch`,
  `change_audio_speed`;
- признаки: `extract_timbre`, `extract_rhythm`,
  `extract_timbre_from_pitch`, `extract_rhythm_from_pitch`.

## `sk_speech.sk_formants`

Анализ и преобразование резонансных частот голосового тракта.

- извлечение: `formant_frequencies`, `extract_formants`,
  `extract_formants_via_lpc`, `get_formant_info`;
- отдельная форманта: `get_formant_frequency_by_index`,
  `calculate_formant_bandwidth`, `calculate_formant_energy3`,
  `calculate_formant_intensity_avg`, `calculate_formant_amplitude_avg`;
- траектории: `formant_trajectory`, `calculate_formant_slope`,
  `extract_formant_rate`, `calculate_formant_dynamics`;
- преобразования: `change_formant_frequencies`,
  `change_formant_amplitude`, `change_formant_bandwidth`,
  `change_formants_shifts`, `flatten_formants`, `slope_formants`;
- анализ паттернов: `analyze_formant_patterns`, `compare_patterns`,
  `classify_phonemes`.

Индекс форманты начинается с `1`: F1 — индекс `1`, F5 — индекс `5`.

## `sk_speech.sk_volume`

Комплексный профиль речи и управление голосом.

- `get_speech_params` — расчёт выбранных параметров по массиву аудио;
- `init_speech` — создание профиля по нейтральной записи;
- `speech_params` — сравнение записи с профилем;
- `get_speech_vector` — относительный вектор параметров;
- `calculate_speech_volume` — частотно скорректированная сумма компонент;
- `change_speech`, `get_change_speech` — применение преобразований;
- `change_volume`, `change_audio_volume`, `mix_audio` — работа с уровнем;
- `trim_silence`, `trim_silence_pydub` — удаление краевой тишины.

Параметр `combine_mode` в `calculate_speech_volume`:

- `"amplitude"` — сложение линейных амплитуд;
- `"power"` — сложение мощностей независимых компонент.

## `sk_speech.sk_vowels`

- `detect_vowel_boundaries` и варианты — поиск границ гласных;
- `determine_vowel_type`, `compute_vowel_type` — оценка типа гласной;
- `group_vowels`, `find_missing_vowels`, `find_closest_vowel` — работа с
  последовательностями гласных;
- `calculate_formant_amplitude`, `calculate_formant_energy`,
  `calculate_formant_freq` — признаки по гласным;
- `amplify_vowels`, `shift_formants_vowels`,
  `stretch_vowels_preserve_pitch` — преобразования.

## `sk_speech.sk_detection`

- `is_soft_speech` — тихая речь;
- `is_loud_speech` — громкая речь;
- `is_whisper` — шёпот;
- `is_scream` — крик;
- `analyze_speech` — объединённый анализ;
- `silence_percentage` — доля тишины;
- `formant_clarity` — выраженность формант.

## `sk_speech.sk_noise`

- RMS, spectral flatness и PSD;
- оценка уровня и наличия шума;
- спектральное вычитание;
- быстрое подавление шума;
- добавление и удаление шума.

## `sk_speech.sk_filters`

- high-pass, low-pass и band-pass фильтры;
- медианное и скользящее сглаживание;
- компрессия, distortion, reverb и гармоники;
- адаптивный LMS-фильтр;
- ERB-шкала и ERB-фильтробанк.

## `sk_speech.sk_gammatone`

- `apply_erb_filterbank` — адаптивный ERB-фильтробанк;
- `combine_filtered_signals` — сборка выбранных каналов;
- `process_chunks` — обработка последовательности фрагментов;
- `process_file` — готовая обработка аудиофайла.

## Остальные модули

- `sk_plot` — графики F0, формант, интенсивности, спектрограмм и PSD;
- `sk_signal` — генерация гармонических сигналов;
- `sk_vocal_tract` — длина голосового тракта и частоты формант;
- `sk_vocal_cords` — площадь голосовой щели, поток, давление и SPL;
- `regulators` — модели сердца, дыхания, давления, метаболизма и центрального
  регулятора.

