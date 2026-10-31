# API пакета `sk_speech`

Справочник разделён по модулям, чтобы каждую подсистему можно было читать отдельно. Для первого знакомства начните с [руководства по началу работы](getting-started.md), а затем выберите нужный модуль.

## Соглашения

- `y`, `signal`, `audio_data` — одномерный массив аудиосэмплов `numpy.ndarray`;
- `sr`, `fs`, `sample_rate` — частота дискретизации в герцах;
- F0 и частоты формант задаются в герцах;
- временные значения задаются в секундах, если явно не указаны сэмплы;
- функции преобразования обычно возвращают новый сигнал и не изменяют входной массив;
- варианты методов с суффиксами `2`, `3` и далее являются отдельными алгоритмами и сохраняются как самостоятельные публичные функции.

## Навигация по модулям

| Модуль | Область | Классы и методы |
|---|---|---:|
| `sk_speech.pitch.calibration` | [Калибровка F0 и интенсивности](api/pitch_calibration.md) | 4 |
| `sk_speech.pitch.extractor` | [Покадровое извлечение F0 и интенсивности](api/pitch_extractor.md) | 2 |
| `sk_speech.pitch.models` | [Модели данных временных рядов](api/pitch_models.md) | 2 |
| `sk_speech.regulators` | [Физиологические регуляторы](api/regulators.md) | 40 |
| `sk_speech.sk_detection` | [Классификация режима речи](api/sk_detection.md) | 8 |
| `sk_speech.sk_filters` | [Фильтры и ERB-преобразования](api/sk_filters.md) | 26 |
| `sk_speech.sk_formants` | [Форманты F1–F5](api/sk_formants.md) | 72 |
| `sk_speech.sk_gammatone` | [Адаптивная гамматонная обработка](api/sk_gammatone.md) | 10 |
| `sk_speech.sk_noise` | [Шум](api/sk_noise.md) | 17 |
| `sk_speech.sk_pitch` | [Основной тон и просодия](api/sk_pitch.md) | 72 |
| `sk_speech.sk_plot` | [Визуализация](api/sk_plot.md) | 16 |
| `sk_speech.sk_signal` | [Генерация сигналов](api/sk_signal.md) | 7 |
| `sk_speech.sk_vocal_cords` | [Голосовая щель и воздушный поток](api/sk_vocal_cords.md) | 16 |
| `sk_speech.sk_vocal_tract` | [Голосовой тракт](api/sk_vocal_tract.md) | 4 |
| `sk_speech.sk_volume` | [Комплексный профиль и преобразование речи](api/sk_volume.md) | 41 |
| `sk_speech.sk_vowels` | [Гласные](api/sk_vowels.md) | 34 |

## Практические руководства

- [С чего начать](getting-started.md) — установка, загрузка аудио и первый анализ;
- [Анализ аудио](audio-analysis.md) — F0, интенсивность, форманты, гласные, шум и комплексный профиль;
- [Преобразование аудио](audio-transformation.md) — изменение F0, формант, скорости, громкости и шумоподавление;
- [Калибровка и временные ряды](calibration-and-timeseries.md) — нейтральный профиль, нормализация и CSV.
