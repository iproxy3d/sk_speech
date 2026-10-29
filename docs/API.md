# API пакета `sk_speech`

Эта справка описывает публичные классы, функции и методы пакета по их фактическим сигнатурам в исходном коде.

## Соглашения

- `y`, `signal`, `audio_data` — одномерный массив аудиосэмплов `numpy.ndarray`;
- `sr`, `fs`, `sample_rate` — частота дискретизации в герцах;
- F0 и частоты формант задаются в герцах;
- временные значения задаются в секундах, если явно не указаны сэмплы;
- функции преобразования обычно возвращают новый сигнал и не изменяют входной массив;
- варианты методов с суффиксами `2`, `3` и далее являются отдельными алгоритмами и сохраняются как самостоятельные публичные функции.

## Навигация по модулям

| Модуль | Область |
|---|---|
| `sk_speech.pitch.calibration` | [Калибровка F0 и интенсивности](#калибровка-f0-и-интенсивности) |
| `sk_speech.pitch.extractor` | [Покадровое извлечение F0 и интенсивности](#покадровое-извлечение-f0-и-интенсивности) |
| `sk_speech.pitch.models` | [Модели данных временных рядов](#модели-данных-временных-рядов) |
| `sk_speech.regulators` | [Физиологические регуляторы](#физиологические-регуляторы) |
| `sk_speech.sk_detection` | [Классификация режима речи](#классификация-режима-речи) |
| `sk_speech.sk_filters` | [Фильтры и ERB-преобразования](#фильтры-и-erb-преобразования) |
| `sk_speech.sk_formants` | [Форманты F1–F5](#форманты-f1f5) |
| `sk_speech.sk_gammatone` | [Адаптивная гамматонная обработка](#адаптивная-гамматонная-обработка) |
| `sk_speech.sk_noise` | [Шум](#шум) |
| `sk_speech.sk_pitch` | [Основной тон и просодия](#основной-тон-и-просодия) |
| `sk_speech.sk_plot` | [Визуализация](#визуализация) |
| `sk_speech.sk_signal` | [Генерация сигналов](#генерация-сигналов) |
| `sk_speech.sk_vocal_cords` | [Голосовая щель и воздушный поток](#голосовая-щель-и-воздушный-поток) |
| `sk_speech.sk_vocal_tract` | [Голосовой тракт](#голосовой-тракт) |
| `sk_speech.sk_volume` | [Комплексный профиль и преобразование речи](#комплексный-профиль-и-преобразование-речи) |
| `sk_speech.sk_vowels` | [Гласные](#гласные) |

## Калибровка F0 и интенсивности

Модуль: `sk_speech.pitch.calibration`.

Нейтральный профиль и относительные покадровые отклонения.

### Класс `PitchProfile`

Контейнер данных или модель состояния.

```python
PitchProfile(mean_f0_hz: float, mean_intensity_db: float, std_f0_hz: float, std_intensity_db: float, voiced_frames: int, frame_step_s: float)
```

#### `PitchProfile.save`

```python
save(path: str | Path) -> Path
```

Сохраняет объект в файл и возвращает путь к созданному файлу.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `Path`.

#### `PitchProfile.load`

```python
load(path: str | Path) -> 'PitchProfile'
```

Загружает объект из файла.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `PitchProfile`.

### Функции

#### `calibrate_pitch`

```python
calibrate_pitch(track: PitchTrack) -> PitchProfile
```

Build a neutral profile from voiced frames of a reference recording.

**Параметры:**

- `track` (`PitchTrack`) — объект `PitchTrack` с покадровыми F0 и интенсивностью.

**Возвращает:** `PitchProfile`.

#### `normalize_pitch`

```python
normalize_pitch(track: PitchTrack, profile: PitchProfile) -> NormalizedPitchTrack
```

Express F0 and intensity as deviations from the neutral profile.

**Параметры:**

- `track` (`PitchTrack`) — объект `PitchTrack` с покадровыми F0 и интенсивностью.
- `profile` (`PitchProfile`) — объект нейтрального профиля `PitchProfile`.

**Возвращает:** `NormalizedPitchTrack`.

## Покадровое извлечение F0 и интенсивности

Модуль: `sk_speech.pitch.extractor`.

Высокоуровневое извлечение синхронизированных временных рядов через Praat.

### Класс `PitchConfig`

Configuration of the Praat-backed feature extractor.

```python
PitchConfig(sample_rate: int | None = 16000, frame_step_s: float = 0.01, pitch_floor_hz: float = 50.0, pitch_ceiling_hz: float = 800.0, minimum_voiced_frames: int = 1)
```

### Класс `PitchExtractor`

Extract F0 and intensity from files or in-memory audio.

```python
PitchExtractor(config: PitchConfig | None=None)
```

#### `PitchExtractor.from_file`

```python
from_file(path: str | Path) -> PitchTrack
```

Читает аудиофайл и извлекает из него признаки.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `PitchTrack`.

#### `PitchExtractor.extract`

```python
extract(signal: np.ndarray, sample_rate: int) -> PitchTrack
```

Извлекает признаки из массива аудиосэмплов.

**Параметры:**

- `signal` (`np.ndarray`) — одномерный аудиосигнал `numpy.ndarray`.
- `sample_rate` (`int`) — частота дискретизации, Гц.

**Возвращает:** `PitchTrack`.

## Модели данных временных рядов

Модуль: `sk_speech.pitch.models`.

Контейнеры исходных и нормализованных последовательностей.

### Класс `PitchTrack`

Frame-aligned F0 and relative broadband intensity.

```python
PitchTrack(time_s: np.ndarray, f0_hz: np.ndarray, intensity_db: np.ndarray, voiced: np.ndarray, sample_rate: int, frame_step_s: float, duration_s: float)
```

#### `PitchTrack.to_csv`

```python
to_csv(path: str | Path) -> Path
```

Write the aligned sequence without requiring pandas.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `Path`.

### Класс `NormalizedPitchTrack`

Pitch sequence expressed relative to a neutral calibration profile.

```python
NormalizedPitchTrack(time_s: np.ndarray, f0_relative: np.ndarray, f0_delta_hz: np.ndarray, intensity_delta_db: np.ndarray, voiced: np.ndarray)
```

#### `NormalizedPitchTrack.to_csv`

```python
to_csv(path: str | Path) -> Path
```

Сохраняет временную последовательность в CSV.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `Path`.

## Физиологические регуляторы

Модуль: `sk_speech.regulators`.

Экспериментальные модели гормонов, сердца, дыхания, давления и метаболизма.

### Класс `Message`

Контейнер данных или модель состояния.

```python
Message(sender, content)
```

### Класс `Hormone`

Контейнер данных или модель состояния.

```python
Hormone(name, initial_level)
```

#### `Hormone.decay`

```python
decay(delta_time)
```

Обновление уровня гормона с учетом времени полураспада.

**Параметры:**

- `delta_time` — Время, прошедшее с последнего обновления (в секундах)..

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Hormone.increase`

```python
increase(amount)
```

Увеличение уровня гормона.

**Параметры:**

- `amount` — Количество, на которое нужно увеличить уровень гормона..

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Hormone.draw`

```python
draw(x, y, background_color, screen)
```

Рисует представление гормона.

**Параметры:**

- `x` — входной параметр `x`.
- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `background_color` — входной параметр `background_color`.
- `screen` — входной параметр `screen`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

### Класс `Heart`

Контейнер данных или модель состояния.

```python
Heart(cur_rate, norm_rate, max_rate, min_rate, regulator, ad_norm)
```

#### `Heart.calculate_baroreflex_effect`

```python
calculate_baroreflex_effect(new_pressure)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `new_pressure` — входной параметр `new_pressure`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Heart.calculate_dV`

```python
calculate_dV(dT, SBP, DBP)
```

dQ — объемный поток, D - диаметр сосуда капиляров у альвеол, 0.0001 м R — радиус сосуда, R = D / 2 L — длина сосуда, 2000-3000 км n — вязкость крови, 4-5 мПа*с dP — разница давлений по длине сосуда, SBP - Систолическое давление DBP - Диастолическое давление dV - объем крови перекачиваемый через сосуды в легких, за время dT dT - время одного сердечного сокращения

**Параметры:**

- `dT` — входной параметр `dT`.
- `SBP` — входной параметр `SBP`.
- `DBP` — входной параметр `DBP`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Heart.calculate_recovery_heart_rate`

```python
calculate_recovery_heart_rate(delta_time, delta_hr)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `delta_time` — шаг времени, с.
- `delta_hr` — входной параметр `delta_hr`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Heart.calc_heart_rate`

```python
calc_heart_rate(hormones, arterial_pressure)
```

Выполняет операцию `calc_heart_rate` над переданными данными.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.

**Возвращает:** результат выражения `hr_new`.

#### `Heart.update`

```python
update(hormones, arterial_pressure, respiratory, delta_time)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `respiratory` — входной параметр `respiratory`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `Heart.draw`

```python
draw(x, y, background_color, screen)
```

Рисует сердце.

**Параметры:**

- `x` — входной параметр `x`.
- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `background_color` — входной параметр `background_color`.
- `screen` — входной параметр `screen`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

### Класс `Respiratory`

Контейнер данных или модель состояния.

```python
Respiratory(oxygen, carbon_dioxide, lung_volumes, regulator)
```

#### `Respiratory.calculate_radius`

```python
calculate_radius(Gaz, d0, R0, dDiff)
```

Рассчитывает радиус альвеолы R(t) на основе уровня газа, начальной толщины стенки, начального радиуса, модуля Юнга, коэффициента диффузии и плотности.

**Параметры:**

- `Gaz` — входной параметр `Gaz`.
- `d0` — входной параметр `d0`.
- `R0` — входной параметр `R0`.
- `dDiff` — входной параметр `dDiff`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_V_t`

```python
calculate_V_t(R_t)
```

Рассчитывает объем легких V(t), исходя из радиуса R(t).

**Параметры:**

- `R_t` — входной параметр `R_t`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_inhale_speed`

```python
calculate_inhale_speed(R, d)
```

Рассчитывает скорость вдоха

**Параметры:**

- `R` — входной параметр `R`.
- `d` — входной параметр `d`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_time_inhalation`

```python
calculate_time_inhalation(U, Gaz)
```

Рассчитывает время вдоха t_inhal.

**Параметры:**

- `U` — входной параметр `U`.
- `Gaz` — входной параметр `Gaz`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_pressure`

```python
calculate_pressure(oxygen_replaced_volume, carbon_dioxide_replaced_volume)
```

Альвеолярным давлением называют давление газа внутри альвеол лёгких. Оно определяет обмен газов между воздухом в лёгочных альвеолах и кровью в капиллярах, окружающих эти альвеолы. В нормальных условиях при вдохе альвеолярное давление ниже атмосферного, а при выдохе – выше. Это обеспечивает движение воздуха внутрь и наружу лёгких.

**Параметры:**

- `oxygen_replaced_volume` — Объем O2, который заменяется CO2 в м³..
- `carbon_dioxide_replaced_volume` — входной параметр `carbon_dioxide_replaced_volume`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_pleural_pressure`

```python
calculate_pleural_pressure(P_alv, oxygen_replaced_volume, carbon_dioxide_replaced_volume)
```

Плевральным давлением называется давление в плевральной полости, которая находится между двумя плеврами: висцеральной (прилегающей к легким) и париетальной (прилежащей к стенке грудной клетки). В норме оно всегда отрицательное относительно атмосферного давления. Отрицательное значение этого давления помогает удерживать легкие в растянутом состоянии и способствует их расширению  при вдохе.

**Параметры:**

- `P_alv` — входной параметр `P_alv`.
- `oxygen_replaced_volume` — входной параметр `oxygen_replaced_volume`.
- `carbon_dioxide_replaced_volume` — входной параметр `carbon_dioxide_replaced_volume`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_transpulmonary_pressure`

```python
calculate_transpulmonary_pressure(oxygen_replaced_volume, carbon_dioxide_replaced_volume)
```

Транспульмональным давлением, также называемым трансреспираторным давлением, является разница между альвеолярным и плевральным давлениями. Это давление отражает силу, необходимую для расширения лёгких против эластической тяги тканей лёгких и стенок грудной клетки.

**Параметры:**

- `oxygen_replaced_volume` — входной параметр `oxygen_replaced_volume`.
- `carbon_dioxide_replaced_volume` — входной параметр `carbon_dioxide_replaced_volume`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_diameter_with_hormones`

```python
calculate_diameter_with_hormones(base_diameter, hormones)
```

Рассчитывает диаметр дыхательных путей с учетом воздействия гормонов.

**Параметры:**

- `base_diameter` — базовый диаметр дыхательных путей в нормальном состоянии (без учета гормонов)..
- `hormones` — словарь с уровнями гормонов: {"adrenaline": 0-1, "acetylcholine": 0-1, "cortisol": 0-1}..

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.calculate_gas_diffusion`

```python
calculate_gas_diffusion(Diff, S, T, P1, P2)
```

Рассчитывает скорость диффузии газа между альвеолами и кровью.

**Параметры:**

- `Diff` — входной параметр `Diff`.
- `S` — входной параметр `S`.
- `T` — входной параметр `T`.
- `P1` — входной параметр `P1`.
- `P2` — входной параметр `P2`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `Respiratory.update_blood`

```python
update_blood(blood_volume, arterial_pressure)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `blood_volume` — входной параметр `blood_volume`.
- `arterial_pressure` — входной параметр `arterial_pressure`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `Respiratory.diffusion`

```python
diffusion(arterial_pressure)
```

Выполняет операцию `diffusion` над переданными данными.

**Параметры:**

- `arterial_pressure` — входной параметр `arterial_pressure`.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Respiratory.replace_partial_pressure`

```python
replace_partial_pressure(arterial_pressure, pressure_oxygen, pressure_carbon_dioxide)
```

Выполняет операцию `replace_partial_pressure` над переданными данными.

**Параметры:**

- `arterial_pressure` — входной параметр `arterial_pressure`.
- `pressure_oxygen` — входной параметр `pressure_oxygen`.
- `pressure_carbon_dioxide` — входной параметр `pressure_carbon_dioxide`.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Respiratory.inhale`

```python
inhale(hormones, arterial_pressure, delta_time)
```

Выполняет операцию `inhale` над переданными данными.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Respiratory.exhale`

```python
exhale(hormones, arterial_pressure, delta_time)
```

Выполняет операцию `exhale` над переданными данными.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Respiratory.pause`

```python
pause(hormones, arterial_pressure, delta_time)
```

При избытке CO₂ — пауза между вдохом и выдохом сокращается или исчезает, увеличивается частота дыхания. При недостатке O₂ — увеличивается объём вдоха и продолжительность самого вдоха, иногда увеличивая паузу, но эффект менее выражен, чем от CO₂. В условиях спокойного дыхания (называемого «нормальным» или эвпноэ) пауза может составлять от 0,5 до 2 секунд.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Respiratory.speech`

```python
speech(hormones, arterial_pressure, delta_time)
```

Выполняет операцию `speech` над переданными данными.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Respiratory.update`

```python
update(hormones, arterial_pressure, delta_time)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `Respiratory.update_breath_history`

```python
update_breath_history(time, duration, volume, breath_type)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `time` — временной параметр, с, если функция не указывает другую единицу.
- `duration` — длительность, с.
- `volume` — уровень или коэффициент громкости.
- `breath_type` — входной параметр `breath_type`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `Respiratory.draw`

```python
draw(x, y, background_color)
```

Рисует текущее состояние модели.

**Параметры:**

- `x` — входной параметр `x`.
- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `background_color` — входной параметр `background_color`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

### Класс `ArterialPressure`

Контейнер данных или модель состояния.

```python
ArterialPressure(systolic_cur, systolic_norm, systolic_max, systolic_min, diastolic_cur, diastolic_norm, diastolic_max, diastolic_min, respiratory, regulator)
```

#### `ArterialPressure.calc_arterial_pressure`

```python
calc_arterial_pressure(adrenalin, norepinephrine, delta_time)
```

Выполняет операцию `calc_arterial_pressure` над переданными данными.

**Параметры:**

- `adrenalin` — входной параметр `adrenalin`.
- `norepinephrine` — входной параметр `norepinephrine`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `ArterialPressure.hormone_metabolism`

```python
hormone_metabolism(t, hormone, k, ad_k, hr_k)
```

Выполняет операцию `hormone_metabolism` над переданными данными.

**Параметры:**

- `t` — входной параметр `t`.
- `hormone` — входной параметр `hormone`.
- `k` — входной параметр `k`.
- `ad_k` — входной параметр `ad_k`.
- `hr_k` — входной параметр `hr_k`.

**Возвращает:** результат выражения `max(hormone * ad_k * math.exp(-k * t * hr_k), 0)`.

#### `ArterialPressure.update`

```python
update(hormones, delta_time)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `ArterialPressure.draw`

```python
draw(x, y, background_color, screen)
```

Рисует параметры давления и визуализацию кровообращения.

**Параметры:**

- `x` — входной параметр `x`.
- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `background_color` — входной параметр `background_color`.
- `screen` — входной параметр `screen`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

### Класс `Metabolism`

Контейнер данных или модель состояния.

```python
Metabolism(glucose, energy, regulator)
```

#### `Metabolism.update`

```python
update(hormones, arterial_pressure, respiratory, delta_time)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `hormones` — входной параметр `hormones`.
- `arterial_pressure` — входной параметр `arterial_pressure`.
- `respiratory` — входной параметр `respiratory`.
- `delta_time` — шаг времени, с.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `Metabolism.calculate_energy`

```python
calculate_energy(arterial_pressure, respiratory)
```

Расчёт энергии, необходимой для поддержания основного метаболизма, с учётом уровня глюкозы, кислорода и гормонов. Basal Metabolic Rate (BMR) это минимальное количество энергии, необходимое для обеспечения нормальной жизнедеятельности организма в стандартных условиях. https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%BE%D0%B1%D0%BC%D0%B5%D0%BD

**Параметры:**

- `arterial_pressure` — входной параметр `arterial_pressure`.
- `respiratory` — входной параметр `respiratory`.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `Metabolism.draw`

```python
draw(x, y, background_color)
```

Рисует текущее состояние модели.

**Параметры:**

- `x` — входной параметр `x`.
- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `background_color` — входной параметр `background_color`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

### Класс `CentralRegulator`

Контейнер данных или модель состояния.

```python
CentralRegulator(delta_time)
```

#### `CentralRegulator.receive_message`

```python
receive_message(message)
```

Выполняет операцию `receive_message` над переданными данными.

**Параметры:**

- `message` — входной параметр `message`.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `CentralRegulator.send_message`

```python
send_message(recipient, content)
```

Выполняет операцию `send_message` над переданными данными.

**Параметры:**

- `recipient` — входной параметр `recipient`.
- `content` — входной параметр `content`.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `CentralRegulator.monitor_state`

```python
monitor_state()
```

Выполняет операцию `monitor_state` над переданными данными.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `CentralRegulator.create_canvas`

```python
create_canvas()
```

Инициализирует канву через pygame.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `CentralRegulator.draw`

```python
draw()
```

Передаёт канву подклассам для отрисовки.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

## Классификация режима речи

Модуль: `sk_speech.sk_detection`.

Эвристические детекторы тихой и громкой речи, шёпота, крика, пауз и ясности формант.

### Функции

#### `is_soft_speech`

```python
is_soft_speech(y, sr, intensity_min_db=20, intensity_max_db=45, f0_min=50, f0_max=300, formant_thresholds=(300, 3000))
```

Определяет, является ли аудиосигнал тихой речью, используя интенсивность, основной тон (F0) и форманты.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `intensity_min_db` — Минимальный порог интенсивности в децибелах для определения тихой речи..
- `intensity_max_db` — Максимальный порог интенсивности в децибелах для определения тихой речи..
- `f0_min` — Минимальная частота тона (Hz)..
- `f0_max` — Максимальная частота тона (Hz)..
- `formant_thresholds` — Ожидаемые диапазоны частот для первых двух формант (F1, F2)..

**Возвращает:** `bool` — результат проверки.

#### `is_loud_speech`

```python
is_loud_speech(y, sr, intensity_threshold_db=55, spectral_flatness_threshold=0.2, f0_min=80, f0_max=300, formant_thresholds=(300, 3000))
```

Определяет, является ли аудиосигнал громкой речью, используя интенсивность, спектральную плоскость, основной тон (F0) и форманты.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `intensity_threshold_db` — Порог интенсивности в децибелах для определения громкой речи..
- `spectral_flatness_threshold` — Порог для спектральной плоскости..
- `f0_min` — Минимальная частота тона (Hz)..
- `f0_max` — Максимальная частота тона (Hz)..
- `formant_thresholds` — Ожидаемые диапазоны частот для первых двух формант (F1, F2)..

**Возвращает:** `bool` — результат проверки.

#### `is_whisper`

```python
is_whisper(y, sr, f0_min=50, f0_avg=100, spectral_flatness_threshold=0.4, formant_threshold=500)
```

Определяет, является ли аудиосигнал шёпотом, используя отсутствие основного тона (F0), высокую спектральную плоскость и отсутствие значимых формантов.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `f0_min` — Минимальная частота тона (Hz) для определения наличия F0..
- `f0_avg` — данные или параметры основного тона F0.
- `spectral_flatness_threshold` — Порог для спектральной плоскости, выше которого считается шёпотом..
- `formant_threshold` — Порог для частот формант, ниже которого считается шёпотом..

**Возвращает:** `bool` — результат проверки.

#### `is_scream`

```python
is_scream(y, sr, intensity_threshold_db=80, min_f0=100, max_f0=600, pitch_threshold=400)
```

Определяет, является ли аудиосигнал криком, используя интенсивность, частоту основного тона (F0) и спектральные характеристики.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `intensity_threshold_db` — Порог интенсивности в децибелах для определения крика..
- `min_f0` — данные или параметры основного тона F0.
- `max_f0` — данные или параметры основного тона F0.
- `pitch_threshold` — порог принятия решения.

**Возвращает:** `bool` — результат проверки.

#### `compute_volume_trend`

```python
compute_volume_trend(y, sr, frame_length=2048, hop_length=512)
```

Вычисляет указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** `tuple` со значениями: `slope, intercept, times, rms, residuals, variance`.

#### `silence_percentage`

```python
silence_percentage(y, sr, threshold_db=-30)
```

Выполняет операцию `silence_percentage` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `threshold_db` — порог уровня в децибелах.

**Возвращает:** результат выражения `silence_percentage`.

#### `analyze_speech`

```python
analyze_speech(y, sr, clarity_formants=[1, 2, 3, 4, 5], silence_threshold_db=-30)
```

Анализирует сигнал и возвращает связанные показатели.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `clarity_formants` — данные или параметры формант.
- `silence_threshold_db` — порог принятия решения.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `formant_clarity`

```python
formant_clarity(y, sr)
```

Выполняет операцию `formant_clarity` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** результат выражения `clarity_scores`.

## Фильтры и ERB-преобразования

Модуль: `sk_speech.sk_filters`.

Временные и частотные фильтры, эффекты, LMS и коэффициенты гамматонного банка.

### Класс `LMSFilter`

Контейнер данных или модель состояния.

```python
LMSFilter(order, step_size)
```

#### `LMSFilter.update`

```python
update(input_signal, desired_signal)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `input_signal` — входные данные или путь к ним.
- `desired_signal` — входной параметр `desired_signal`.

**Возвращает:** `tuple` со значениями: `output, self.error`.

### Функции

#### `hz_to_semitones`

```python
hz_to_semitones(hz, reference_hz=440.0)
```

Convert Hz to semitones relative to a reference frequency (default is A4 = 440 Hz).

**Параметры:**

- `hz` — входной параметр `hz`.
- `reference_hz` — входной параметр `reference_hz`.

**Возвращает:** результат выражения `12 * np.log2(hz / reference_hz)`.

#### `semitones_to_hz`

```python
semitones_to_hz(semitones, reference_hz=440.0)
```

Convert semitones to Hz relative to a reference frequency (default is A4 = 440 Hz).

**Параметры:**

- `semitones` — входной параметр `semitones`.
- `reference_hz` — входной параметр `reference_hz`.

**Возвращает:** результат выражения `reference_hz * 2 ** (semitones / 12)`.

#### `normalize_audio`

```python
normalize_audio(y)
```

Нормализует входное значение или сигнал.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_high_pass_filter`

```python
apply_high_pass_filter(y, sr, cutoff=100)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `cutoff` — входной параметр `cutoff`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_low_pass_filter`

```python
apply_low_pass_filter(y, sr, cutoff=8000)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `cutoff` — входной параметр `cutoff`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_median_filter`

```python
apply_median_filter(y, window_size)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `window_size` — размер окна обработки.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_moving_average`

```python
apply_moving_average(y, window_size)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `window_size` — размер окна обработки.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_bandpass_filter`

```python
apply_bandpass_filter(y, sr, lowcut, highcut)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `lowcut` — входной параметр `lowcut`.
- `highcut` — входной параметр `highcut`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_smoothing_filter`

```python
apply_smoothing_filter(y, sr)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_window_function`

```python
apply_window_function(segment, window_length=2205)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `segment` — входной параметр `segment`.
- `window_length` — длина оконной функции.

**Возвращает:** результат выражения `segment * window`.

#### `apply_compression`

```python
apply_compression(y, compression_factor=2)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `compression_factor` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_compressed`.

#### `apply_distortion`

```python
apply_distortion(y, distortion_factor=0.5)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `distortion_factor` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_distorted`.

#### `apply_reverb`

```python
apply_reverb(y, sr, reverb_factor=0.5, delay_ms=50, attenuation=0.5)
```

Применяет реверберационный эффект к аудиосигналу.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `reverb_factor` — коэффициент или доля преобразования.
- `delay_ms` — входной параметр `delay_ms`.
- `attenuation` — входной параметр `attenuation`.

**Возвращает:** результат выражения `reverb`.

#### `apply_harmonic`

```python
apply_harmonic(y, harmonic_factor=1.0)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `harmonic_factor` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_harmonic_adjusted`.

#### `match_target_amplitude`

```python
match_target_amplitude(sound, target_dBFS)
```

Выполняет операцию `match_target_amplitude` над переданными данными.

**Параметры:**

- `sound` — объект аудиосигнала Praat или Pydub согласно функции.
- `target_dBFS` — входной параметр `target_dBFS`.

**Возвращает:** результат выражения `sound.apply_gain(change_in_dBFS)`.

#### `train_adaptive_filter`

```python
train_adaptive_filter(reference_file, order=50, step_size=0.01)
```

Обучает адаптивный компонент на эталонных данных.

**Параметры:**

- `reference_file` — путь к файлу или каталогу.
- `order` — входной параметр `order`.
- `step_size` — входной параметр `step_size`.

**Возвращает:** результат выражения `lms_filter`.

#### `apply_adaptive_filter`

```python
apply_adaptive_filter(input_file, output_file, lms_filter, order=50)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.
- `lms_filter` — входной параметр `lms_filter`.
- `order` — входной параметр `order`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `erb_point`

```python
erb_point(low_freq, high_freq, fraction)
```

Calculates a single point on an ERB scale between ``low_freq`` and ``high_freq``, determined by ``fraction``. When ``fraction`` is ``1``, ``low_freq`` will be returned. When ``fraction`` is ``0``, ``high_freq`` will be returned.

**Параметры:**

- `low_freq` — частота или последовательность частот, Гц.
- `high_freq` — частота или последовательность частот, Гц.
- `fraction` — входной параметр `fraction`.

**Возвращает:** результат выражения `erb_point`.

#### `erb_space`

```python
erb_space(low_freq=DEFAULT_LOW_FREQ, high_freq=DEFAULT_HIGH_FREQ, num=DEFAULT_FILTER_NUM)
```

This function computes an array of ``num`` frequencies uniformly spaced between ``high_freq`` and ``low_freq`` on an ERB scale.

**Параметры:**

- `low_freq` — частота или последовательность частот, Гц.
- `high_freq` — частота или последовательность частот, Гц.
- `num` — входной параметр `num`.

**Возвращает:** результат выражения `erb_point(low_freq, high_freq, np.arange(1, num + 1) / num)`.

#### `centre_freqs`

```python
centre_freqs(fs, num_freqs, cutoff=DEFAULT_LOW_FREQ)
```

Calculates an array of centre frequencies (for :func:`make_erb_filters`) from a sampling frequency, lower cutoff frequency and the desired number of filters.

**Параметры:**

- `fs` — sampling rate.
- `num_freqs` — number of centre frequencies to calculate.
- `cutoff` — lower cutoff frequency.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `MEL_centre_freqs`

```python
MEL_centre_freqs(n_gammatone, fmin=0, fmax=8000)
```

Выполняет операцию `MEL_centre_freqs` над переданными данными.

**Параметры:**

- `n_gammatone` — входной параметр `n_gammatone`.
- `fmin` — входной параметр `fmin`.
- `fmax` — входной параметр `fmax`.

**Возвращает:** `tuple` со значениями: `center_freqs, bandwidths`.

#### `centre_bandwidths`

```python
centre_bandwidths(centre_freqs, width=1.0)
```

Выполняет операцию `centre_bandwidths` над переданными данными.

**Параметры:**

- `centre_freqs` — частота или последовательность частот, Гц.
- `width` — входной параметр `width`.

**Возвращает:** результат выражения `erb`.

#### `make_erb_filters`

```python
make_erb_filters(fs, centre_freqs, width=1.0)
```

This function computes the filter coefficients for a bank of Gammatone filters. These filters were defined by Patterson and Holdworth for simulating the cochlea.

**Параметры:**

- `fs` — частота дискретизации, Гц.
- `centre_freqs` — частота или последовательность частот, Гц.
- `width` — входной параметр `width`.

**Возвращает:** результат выражения `fcoefs`.

#### `make_erb_filters_ex`

```python
make_erb_filters_ex(fs, centre_freqs, bandwidths=None, width=1.0)
```

Computes filter coefficients for a bank of Gammatone filters.

**Параметры:**

- `fs` — частота дискретизации, Гц.
- `centre_freqs` — частота или последовательность частот, Гц.
- `bandwidths` — ширины частотных полос, Гц.
- `width` — входной параметр `width`.

**Возвращает:** результат выражения `fcoefs`.

#### `erb_filterbank`

```python
erb_filterbank(wave, coefs)
```

:param wave: input data (one dimensional sequence)

**Параметры:**

- `wave` — input data (one dimensional sequence).
- `coefs` — gammatone filter coefficients.

**Возвращает:** результат выражения `output`.

## Форманты F1–F5

Модуль: `sk_speech.sk_formants`.

Извлечение, измерение, динамика, паттерны, синтез и преобразование формант.

### Функции

#### `formant_range`

```python
formant_range(formant_index)
```

Выполняет операцию `formant_range` над переданными данными.

**Параметры:**

- `formant_index` — номер форманты: 1 соответствует F1.

**Возвращает:** результат выражения `formant_ranges[formant_index][1] - formant_ranges[formant_index][0]`.

#### `get_formants_with_retries`

```python
get_formants_with_retries(sound, time_step=0.01, max_number_of_formants=5, pitch_to=5500)
```

Получает рассчитанное представление или характеристику.

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
- `method` — входной параметр `method`.

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
- `lpc_order` — входной параметр `lpc_order`.

**Возвращает:** `tuple` со значениями: `formants_over_time, times`.

#### `formant_frequencies`

```python
formant_frequencies(signal, sr, speech=True, time_step=0.01)
```

Выполняет операцию `formant_frequencies` над переданными данными.

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

Выполняет операцию `formant_frequencies2` над переданными данными.

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

Получает рассчитанное представление или характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `formant_frequencies_expended`

```python
formant_frequencies_expended(signal, sr, speech=True, time_step=0.01, max_number_of_formants=5)
```

Выполняет операцию `formant_frequencies_expended` над переданными данными.

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

Извлекает признак или временную последовательность из сигнала.

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

Получает рассчитанное представление или характеристику.

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

Удаляет или подавляет указанную составляющую.

**Параметры:**

- `data` — входные данные соответствующего метода.
- `m` — входной параметр `m`.

**Возвращает:** результат выражения `data | data[(data >= lower_bound) & (data <= upper_bound)]`.

#### `calculate_formant_bandwidth_`

```python
calculate_formant_bandwidth_(bandwidths, formant_index, method='max')
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `bandwidths` — ширины частотных полос, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `method` — входной параметр `method`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_bandwidth`

```python
calculate_formant_bandwidth(signal, sr, formant_index, speech=True, method='max', formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `speech` — режим или структура профиля речи — зависит от функции.
- `method` — входной параметр `method`.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_energy`

```python
calculate_formant_energy(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_energy2`

```python
calculate_formant_energy2(signal, sr, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_energy_arr`

```python
calculate_formant_energy_arr(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_energy3`

```python
calculate_formant_energy3(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_and_f0_energy`

```python
calculate_formant_and_f0_energy(signal, sr)
```

Рассчитывает энергию формант и F0 в аудиосигнале, используя Parselmouth для извлечения формантов и F0.

**Параметры:**

- `signal` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..

**Возвращает:** `tuple` со значениями: `formant_energies, avg_f0_energy`.

#### `change_formant_energy`

```python
change_formant_energy(y, sr, formant_index, factor)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `factor` — множитель преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_formant_energy2`

```python
change_formant_energy2(signal, sr, energy_factors)
```

Изменяет энергию каждой форманты F1-F5 в аудиосигнале.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `energy_factors` — Список факторов энергии для каждой форманты [E1, E2, E3, E4, E5]..

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_formant_energy3`

```python
change_formant_energy3(signal, sr, energy_factors)
```

Изменяет энергию каждой форманты F1-F5.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `energy_factors` — Список факторов энергии для каждой форманты [E1, E2, E3, E4, E5]..

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_formant_amplitude`

```python
change_formant_amplitude(signal, sr, factors, formants=None)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factors` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_formant_amplitude_range`

```python
change_formant_amplitude_range(signal, sr, factors_from, factors_to, formants=None)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factors_from` — коэффициент или доля преобразования.
- `factors_to` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `calculate_formant_intensity`

```python
calculate_formant_intensity(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_intensity_avg`

```python
calculate_formant_intensity_avg(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_amplitude`

```python
calculate_formant_amplitude(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_amplitude_avg`

```python
calculate_formant_amplitude_avg(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_duration`

```python
calculate_formant_duration(signal, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_duration2`

```python
calculate_formant_duration2(y, sr, formant_index, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `formant_at_index`

```python
formant_at_index(y, sr, index, speech=True, window_size=1024)
```

Выполняет операцию `formant_at_index` над переданными данными.

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

Выполняет операцию `formant_trajectory` над переданными данными.

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

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `calculate_segment_duration`

```python
calculate_segment_duration(formant_shifts, base_duration=0.0025, S=350, beta=0.1)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `formant_shifts` — данные или параметры формант.
- `base_duration` — коэффициент или доля преобразования.
- `S` — входной параметр `S`.
- `beta` — входной параметр `beta`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

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

Усиливает выбранные частотные составляющие.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `boost_dB` — входной параметр `boost_dB`.
- `max_amplitude_dB` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `y + y_boosted`.

#### `boost_formants_peak`

```python
boost_formants_peak(signal, sr, gain_dB, max_amplitude_dB)
```

Усиливает выбранные частотные составляющие.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `gain_dB` — входной параметр `gain_dB`.
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
- `boost_dB` — входной параметр `boost_dB`.
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

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `compute_spectral_slope_for_formant`

```python
compute_spectral_slope_for_formant(y, sr, formant_index, window_size=1024, hop_size=512)
```

Вычисляет указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `window_size` — размер окна обработки.
- `hop_size` — входной параметр `hop_size`.

**Возвращает:** `tuple` со значениями: `times, slopes`.

#### `compute_spectral_slope_for_formant2`

```python
compute_spectral_slope_for_formant2(signal, sr, formant_index, formants=None)
```

Вычисляет указанную характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `change_formant_bandwidth2`

```python
change_formant_bandwidth2(signal, sr, bandwidth_factors, formants=None)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `bandwidth_factors` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

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

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_formant_frequencies`

```python
change_formant_frequencies(signal, sr, frequency_factors)
```

Изменяет частоту каждой форманты F1-F5 в заданное количество раз.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `frequency_factors` — Список факторов частоты для каждой форманты [F1, F2, F3, F4, F5]..

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `extract_formant_rate`

```python
extract_formant_rate(y, sr, formant_index=1, medfilt_size=5, formants=None)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `medfilt_size` — входной параметр `medfilt_size`.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `None, None, None`.

#### `calculate_formant_slope`

```python
calculate_formant_slope(y, sr, formant_index=1, is_smooth=True, is_peak=True, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `formant_index` — номер форманты: 1 соответствует F1.
- `is_smooth` — входной параметр `is_smooth`.
- `is_peak` — входной параметр `is_peak`.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `0, 0, 'Нет данных'`.

#### `calculate_intensity_slope`

```python
calculate_intensity_slope(y, sr, is_smooth=True, is_peak=True, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `is_smooth` — входной параметр `is_smooth`.
- `is_peak` — входной параметр `is_peak`.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `0, 0, 'Нет данных'`.

#### `flatten_formants`

```python
flatten_formants(signal, sr, mean_formant_signals=[0.1, 0.1, 0.1, 0.1, 0.1])
```

Выравнивает форманты F1-F5 на уровне их средней частоты в аудиосигнале, сохраняя исходный сигнал и изменяя частоты формант.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `mean_formant_signals` — данные или параметры формант.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `slope_formants`

```python
slope_formants(signal, sr, slope_factors=[0.5, 0.5, 0.5, 0.5, 0.5], mixing_percent=[0.1, 0.1, 0.1, 0.1, 0.1], filtered_percent=[1.0, 1.0, 1.0, 1.0, 1.0], method='center', replace=True)
```

Выполняет операцию `slope_formants` над переданными данными.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `slope_factors` — коэффициент или доля преобразования.
- `mixing_percent` — коэффициент или доля преобразования.
- `filtered_percent` — коэффициент или доля преобразования.
- `method` — входной параметр `method`.
- `replace` — входной параметр `replace`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

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

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `find_max_formant_energy_time`

```python
find_max_formant_energy_time(formant_energy)
```

Находит указанные элементы или интервалы.

**Параметры:**

- `formant_energy` — энергия или коэффициент энергии.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `segment_and_smooth`

```python
segment_and_smooth(data, num_segments)
```

Разбивает данные на секции и сглаживает их до прямой.

**Параметры:**

- `data` — входные данные соответствующего метода.
- `num_segments` — входной параметр `num_segments`.

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
- `num_segments` — входной параметр `num_segments`.
- `eps_freq` — частота или последовательность частот, Гц.
- `eps_width` — входной параметр `eps_width`.

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
- `num_segments` — входной параметр `num_segments`.
- `eps_freq` — частота или последовательность частот, Гц.
- `eps_width` — входной параметр `eps_width`.
- `dist` — входной параметр `dist`.
- `eps_dist` — входной параметр `eps_dist`.

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
- `eps_width` — входной параметр `eps_width`.
- `dist` — входной параметр `dist`.
- `eps_dist` — входной параметр `eps_dist`.

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
- `eps_width` — входной параметр `eps_width`.
- `dist` — входной параметр `dist`.
- `eps_dist` — входной параметр `eps_dist`.

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

- `simplified_patterns` — входной параметр `simplified_patterns`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `classify_phonemes`

```python
classify_phonemes(simplified_patterns, phonems)
```

Классифицирует фонемы на основе упрощенных паттернов формантов.

**Параметры:**

- `simplified_patterns` — входной параметр `simplified_patterns`.
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

**Возвращает:** `tuple` со значениями: `formant_dynamics, time_segments`.

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
- `start_bw` — входной параметр `start_bw`.
- `end_bw` — входной параметр `end_bw`.
- `sample_rate` — частота дискретизации, Гц.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

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

## Адаптивная гамматонная обработка

Модуль: `sk_speech.sk_gammatone`.

ERB-фильтрация с настройкой центральных частот по F0 и формантам.

### Функции

#### `load_audio`

```python
load_audio(filename)
```

Загружает данные из файла.

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

Получает рассчитанное представление или характеристику.

**Параметры:**

- `freq` — частота или последовательность частот, Гц.

**Возвращает:** `tuple` со значениями: `0.6, 0.2, 0.15, 0.05`.

#### `filter_center_frequencies`

```python
filter_center_frequencies(center_frequencies, pitch_freq, formants, pitch_threshold=200, formant_thresholds=None)
```

Фильтрует входные данные по заданным условиям.

**Параметры:**

- `center_frequencies` — частота или последовательность частот, Гц.
- `pitch_freq` — частота или последовательность частот, Гц.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.
- `pitch_threshold` — порог принятия решения.
- `formant_thresholds` — порог принятия решения.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `apply_erb_filterbank`

```python
apply_erb_filterbank(audio_data, sampling_rate, n_filters=20, lowcut=100, highcut=5500, speech=True)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `audio_data` — массив аудиосэмплов.
- `sampling_rate` — входной параметр `sampling_rate`.
- `n_filters` — входной параметр `n_filters`.
- `lowcut` — входной параметр `lowcut`.
- `highcut` — входной параметр `highcut`.
- `speech` — режим или структура профиля речи — зависит от функции.

**Возвращает:** `tuple` со значениями: `filtered_matrix, thresholds`.

#### `combine_filtered_signals`

```python
combine_filtered_signals(filtered_matrix, thresholds)
```

Объединяет несколько сигналов или представлений.

**Параметры:**

- `filtered_matrix` — входной параметр `filtered_matrix`.
- `thresholds` — порог принятия решения.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

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

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `process_file`

```python
process_file(input_file, output_file, chunk_length=0.3, speech=True, n_channels=NCHANNELS, low_cutoff=LOW_CUTOFF, high_cutoff=HIGH_CUTOFF)
```

Apply the adaptive gammatone pipeline to one audio file.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.
- `chunk_length` — входной параметр `chunk_length`.
- `speech` — режим или структура профиля речи — зависит от функции.
- `n_channels` — входной параметр `n_channels`.
- `low_cutoff` — входной параметр `low_cutoff`.
- `high_cutoff` — входной параметр `high_cutoff`.

**Возвращает:** `tuple` со значениями: `output_audio, sampling_rate`.

## Шум

Модуль: `sk_speech.sk_noise`.

Оценка шума, спектральная плоскость, PSD и несколько вариантов шумоподавления.

### Функции

#### `normalize`

```python
normalize(value, min_val, max_val)
```

Нормализует входное значение или сигнал.

**Параметры:**

- `value` — входные данные соответствующего метода.
- `min_val` — входной параметр `min_val`.
- `max_val` — входной параметр `max_val`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `compute_rms`

```python
compute_rms(y, frame_length=2048, hop_length=512)
```

Вычисляет указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `compute_spectral_flatness`

```python
compute_spectral_flatness(y, frame_length=2048, hop_length=512)
```

Вычисляет указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `compute_power_spectral_density`

```python
compute_power_spectral_density(y, sr, n_fft=2048, hop_length=512)
```

Вычисляет указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `n_fft` — входной параметр `n_fft`.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** `tuple` со значениями: `freqs, psd`.

#### `analyze_noise_in_psd`

```python
analyze_noise_in_psd(y, sr, speech_band=(300, 3400), noise_threshold_db=-20)
```

Анализирует PSD для определения присутствия шума и его уровня.

**Параметры:**

- `y` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `speech_band` — Диапазон частот, характерный для речи (Hz)..
- `noise_threshold_db` — Порог уровня шума в децибелах..

**Возвращает:** `tuple` со значениями: `noise_present, noise_level_db`.

#### `analyze_noise_level_sf`

```python
analyze_noise_level_sf(y, sr, n_fft=2048, hop_length=512, flatness_threshold=0.3)
```

Анализирует уровень шума в аудиосигнале на основе спектральной разреженности.

**Параметры:**

- `y` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `n_fft` — Длина окна для вычисления STFT..
- `hop_length` — Шаг между окнами..
- `flatness_threshold` — Порог для спектральной плоскости, выше которого считается шумом..

**Возвращает:** `tuple` со значениями: `is_noisy, avg_flatness`.

#### `analyze_noise_level_rms`

```python
analyze_noise_level_rms(y, sr, frame_length=2048, hop_length=512, noise_threshold_db=-40)
```

Анализирует уровень шума в аудиосигнале на основе RMS значений.

**Параметры:**

- `y` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `frame_length` — Длина окна для вычисления RMS..
- `hop_length` — Шаг между окнами..
- `noise_threshold_db` — Порог для определения шума в децибелах..

**Возвращает:** `tuple` со значениями: `is_noisy, avg_noise_level_db`.

#### `analyze_noise_level`

```python
analyze_noise_level(y, sr, noise_threshold_db=-40, spectral_flatness_threshold=0.5)
```

Анализирует сигнал и возвращает связанные показатели.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_threshold_db` — порог принятия решения.
- `spectral_flatness_threshold` — порог принятия решения.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `spectral_subtraction`

```python
spectral_subtraction(y, sr, n_fft=2048, hop_length=512, noise_estimation_method='psd')
```

Выполняет операцию `spectral_subtraction` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `n_fft` — входной параметр `n_fft`.
- `hop_length` — шаг между кадрами, сэмплы.
- `noise_estimation_method` — входной параметр `noise_estimation_method`.

**Возвращает:** результат выражения `enhanced_y`.

#### `spectral_subtraction2`

```python
spectral_subtraction2(y, sr, noise_psd, n_fft=2048, hop_length=512)
```

Выполняет операцию `spectral_subtraction2` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_psd` — входной параметр `noise_psd`.
- `n_fft` — входной параметр `n_fft`.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** результат выражения `enhanced_y`.

#### `estimate_noise_psd`

```python
estimate_noise_psd(y, sr, frame_length=2048, hop_length=512)
```

Выполняет операцию `estimate_noise_psd` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** результат выражения `noise_psd`.

#### `analyze_noise_level2`

```python
analyze_noise_level2(y, sr, frame_length=2048, hop_length=512, noise_threshold_db=-40, flatness_threshold=0.3)
```

Анализирует сигнал и возвращает связанные показатели.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.
- `noise_threshold_db` — порог принятия решения.
- `flatness_threshold` — порог принятия решения.

**Возвращает:** `tuple` со значениями: `is_noisy_rms, avg_noise_level_db, is_noisy_flatness, avg_flatness`.

#### `noise_reduction_spectral_subtraction_fast`

```python
noise_reduction_spectral_subtraction_fast(y, sr, noise_profile_sec=0.5, num_iterations=2)
```

Выполняет операцию `noise_reduction_spectral_subtraction_fast` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_profile_sec` — входной параметр `noise_profile_sec`.
- `num_iterations` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `None | y_denoised`.

#### `noise_reduction_spectral_subtraction`

```python
noise_reduction_spectral_subtraction(y, sr, noise_profile_sec=0.5, num_iterations=2, high_pass=False, low_pass=False, normalize=False, target_dBFS=-20.0)
```

Выполняет операцию `noise_reduction_spectral_subtraction` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_profile_sec` — входной параметр `noise_profile_sec`.
- `num_iterations` — коэффициент или доля преобразования.
- `high_pass` — входной параметр `high_pass`.
- `low_pass` — входной параметр `low_pass`.
- `normalize` — входной параметр `normalize`.
- `target_dBFS` — входной параметр `target_dBFS`.

**Возвращает:** результат выражения `y_denoised`.

#### `apply_noise_reduction`

```python
apply_noise_reduction(y, noise_reduction_factor=0.3)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `noise_reduction_factor` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_reduced_noise`.

#### `add_noise`

```python
add_noise(y, noise_amplitude=0.005)
```

Выполняет операцию `add_noise` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `noise_amplitude` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `y_noisy`.

#### `remove_noise`

```python
remove_noise(y, sr, method='lowpass', **kwargs)
```

Удаляет или подавляет указанную составляющую.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `method` — входной параметр `method`.
- `kwargs` — входной параметр `kwargs`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

## Основной тон и просодия

Модуль: `sk_speech.sk_pitch`.

Расширенное извлечение и преобразование F0, интенсивности, наклона, периода, ритма и тембра.

### Функции

#### `get_pitch_with_retries`

```python
get_pitch_with_retries(sound, time_step=0.01, pitch_from=75, pitch_to=500)
```

Пытается вычислить pitch объекта sound, увеличивая time_step на 10 при каждом исключении, пока ошибка не исчезнет или time_step не станет больше 1.

**Параметры:**

- `sound` — объект аудиосигнала Praat или Pydub согласно функции.
- `time_step` — временной шаг анализа, с.
- `pitch_from` — нижняя граница F0, Гц.
- `pitch_to` — верхняя граница F0, Гц.

**Возвращает:** результат выражения `pitch | None`.

#### `extract_f0`

```python
extract_f0(y, sr, pitch_from=75, pitch_to=600)
```

Извлекает основной тон (f0) из аудио сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_from` — нижняя граница F0, Гц.
- `pitch_to` — верхняя граница F0, Гц.

**Возвращает:** результат выражения `f0`.

#### `extract_f0_values`

```python
extract_f0_values(y, sr, pitch_from=75, pitch_to=600)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_from` — нижняя граница F0, Гц.
- `pitch_to` — верхняя граница F0, Гц.

**Возвращает:** результат выражения `f0_values`.

#### `extract_f0_segment`

```python
extract_f0_segment(y, sr, pitch_from=75, pitch_to=600)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_from` — нижняя граница F0, Гц.
- `pitch_to` — верхняя граница F0, Гц.

**Возвращает:** результат выражения `None | pitch_values`.

#### `extract_f0_min_max_avg`

```python
extract_f0_min_max_avg(y, sr)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `tuple` со значениями: `0, 0, 0`.

#### `remove_short_sequences_mask`

```python
remove_short_sequences_mask(f0, min_length=15)
```

Возвращает маску для значений F0, где длинные последовательности помечены как True, а короткие как False.

**Параметры:**

- `f0` — Массив значений F0 с NaN..
- `min_length` — Минимальная длина последовательности для сохранения..

**Возвращает:** результат выражения `mask`.

#### `filter_intensity_by_voiced_times`

```python
filter_intensity_by_voiced_times(intensity_values, intensity_times, voiced_times)
```

Фильтрует входные данные по заданным условиям.

**Параметры:**

- `intensity_values` — интенсивность или её параметры.
- `intensity_times` — интенсивность или её параметры.
- `voiced_times` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** `tuple` со значениями: `interpolated_intensity_values, voiced_times`.

#### `extract_f0_voiced`

```python
extract_f0_voiced(y, sr, speech=True, pitch_from=75, pitch_to=600, time_step=0.01)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.
- `pitch_from` — нижняя граница F0, Гц.
- `pitch_to` — верхняя граница F0, Гц.
- `time_step` — временной шаг анализа, с.

**Возвращает:** `tuple` со значениями: `None, None, None, None, None, None, None`.

#### `calculate_pitch_frequency`

```python
calculate_pitch_frequency(y)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `extract_f0_penn`

```python
extract_f0_penn(y, sr)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** результат выражения `pitch`.

#### `remove_short_sequences`

```python
remove_short_sequences(f0, min_length=15)
```

Убирает короткие последовательности значений F0.

**Параметры:**

- `f0` — Массив значений F0 с NaN..
- `min_length` — Минимальная длина последовательности для сохранения..

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `calculate_pitch_bandwidth`

```python
calculate_pitch_bandwidth(y, sr, pitch=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_bandwidth_welch`

```python
calculate_pitch_bandwidth_welch(y, sr, pitch=None)
```

Estimate F0-band width with a Welch spectrum.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_bandwidth2`

```python
calculate_pitch_bandwidth2(y, sr)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_energy`

```python
calculate_pitch_energy(y, sr, pitch=None)
```

Рассчитывает среднюю энергию основного тона в аудиосигнале с использованием Parselmouth.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `change_pitch_energy2`

```python
change_pitch_energy2(y, sr, factor, pitch_range=(75, 600))
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factor` — множитель преобразования.
- `pitch_range` — данные или параметры основного тона F0.

**Возвращает:** `tuple` со значениями: `y, sr`.

#### `change_pitch_energy3`

```python
change_pitch_energy3(y, sr, factor, pitch_range=(75, 600))
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factor` — множитель преобразования.
- `pitch_range` — данные или параметры основного тона F0.

**Возвращает:** `tuple` со значениями: `y, sr`.

#### `change_pitch_energy`

```python
change_pitch_energy(y, sr, factor, pitch_range=(75, 600), speech=True, pitch_from=75, pitch_to=600)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factor` — множитель преобразования.
- `pitch_range` — данные или параметры основного тона F0.
- `speech` — режим или структура профиля речи — зависит от функции.
- `pitch_from` — нижняя граница F0, Гц.
- `pitch_to` — верхняя граница F0, Гц.

**Возвращает:** `tuple` со значениями: `resynthesized_signal, int(sound.sampling_frequency)`.

#### `calculate_pitch_intensity`

```python
calculate_pitch_intensity(y, sr, only_speech=False, shift=True, pitch=None)
```

Return Praat broadband intensity values aligned with pitch metadata.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `only_speech` — входной параметр `only_speech`.
- `shift` — входной параметр `shift`.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_intensity2`

```python
calculate_pitch_intensity2(y, sr, f0_min=80, f0_max=300, frame_length=2048, hop_length=512, only_speech=False, shift=True)
```

Рассчитывает интенсивность основного тона в аудиосигнале.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `f0_min` — Минимальная частота основного тона (в Гц)..
- `f0_max` — Максимальная частота основного тона (в Гц)..
- `frame_length` — Длина фрейма для анализа..
- `hop_length` — Шаг между фреймами..
- `only_speech` — входной параметр `only_speech`.
- `shift` — входной параметр `shift`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `calculate_pitch_intensity_avg`

```python
calculate_pitch_intensity_avg(y, sr, pitch)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_intensity_scream`

```python
calculate_intensity_scream(y, sr, frame_length=2048, hop_length=512)
```

Рассчитывает интенсивность речи в аудиосигнале в децибелах.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `frame_length` — Размер окна для анализа..
- `hop_length` — Шаг между окнами..

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_total_intensity`

```python
calculate_total_intensity(y, frame_length=2048, hop_length=512)
```

Рассчитывает общую интенсивность аудио сигнала.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `frame_length` — Длина окна для анализа..
- `hop_length` — Шаг между окнами..

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_amplitude`

```python
calculate_pitch_amplitude(signal, sr, pitch=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_amplitude2`

```python
calculate_pitch_amplitude2(signal, sr)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `extract_tone`

```python
extract_tone(y, sr, pitch, window_size_ms=10)
```

Извлекает основной тон из сигнала.

**Параметры:**

- `y` — Входной сигнал (массив значений).
- `sr` — Частота дискретизации (Гц).
- `pitch` — Объект Pitch, содержащий информацию о тональности.
- `window_size_ms` — Размер окна для извлечения тона (мс).

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_pitch_amplitude`

```python
change_pitch_amplitude(y, sr, amplitude_factor)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `amplitude_factor` — коэффициент или доля преобразования.

**Возвращает:** `tuple` со значениями: `new_signal, int(sr)`.

#### `change_pitch_amplitude_range`

```python
change_pitch_amplitude_range(y, sr, amplitude_factor_from, amplitude_factor_to)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `amplitude_factor_from` — коэффициент или доля преобразования.
- `amplitude_factor_to` — коэффициент или доля преобразования.

**Возвращает:** `tuple` со значениями: `new_signal, int(sr)`.

#### `change_pitch_amplitude_with_bandwidth`

```python
change_pitch_amplitude_with_bandwidth(y, sr, amplitude_factor, pitch=None)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `amplitude_factor` — коэффициент или доля преобразования.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `new_signal, sr`.

#### `change_pitch_amplitude_with_bandwidth_range`

```python
change_pitch_amplitude_with_bandwidth_range(y, sr, amplitude_factor_from, amplitude_factor_to, pitch=None)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `amplitude_factor_from` — коэффициент или доля преобразования.
- `amplitude_factor_to` — коэффициент или доля преобразования.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `new_signal, sr`.

#### `change_pitch_amplitude_with_bandwidth2`

```python
change_pitch_amplitude_with_bandwidth2(y, sr, amplitude_factor)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `amplitude_factor` — коэффициент или доля преобразования.

**Возвращает:** `tuple` со значениями: `new_signal, sr`.

#### `change_pitch_amplitude_with_voice`

```python
change_pitch_amplitude_with_voice(y, sr, amplitude_factor)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `amplitude_factor` — коэффициент или доля преобразования.

**Возвращает:** `tuple` со значениями: `new_signal, sr`.

#### `get_pitch_info`

```python
get_pitch_info(y, sr, speech=True)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `speech` — режим или структура профиля речи — зависит от функции.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `calculate_pitch_duration`

```python
calculate_pitch_duration(y, sr, pitch=None)
```

Рассчитывает длительность речи с основным тоном (F0) в аудиосигнале с использованием Parselmouth.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_pitch_trajectory`

```python
get_pitch_trajectory(y, sr)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `tuple` со значениями: `time, pitch_trajectory`.

#### `remove_pitch_and_reduce_formants`

```python
remove_pitch_and_reduce_formants(y, sr)
```

Удаляет или подавляет указанную составляющую.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** результат выражения `y_no_pitch`.

#### `change_pitch_shift_hz`

```python
change_pitch_shift_hz(y, sr, pitch_shift_hz)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_hz` — данные или параметры основного тона F0.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_pitch_fixed_hz`

```python
change_pitch_fixed_hz(y, sr, pitch_shift_hz)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_hz` — данные или параметры основного тона F0.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_pitch_fixed_hz_segmented`

```python
change_pitch_fixed_hz_segmented(y, sr, pitch_shift_hz, segment_duration=2.0)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_hz` — данные или параметры основного тона F0.
- `segment_duration` — коэффициент или доля преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_pitch_fixed_hz_with_filter`

```python
change_pitch_fixed_hz_with_filter(y, sr, pitch_shift_hz)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_hz` — данные или параметры основного тона F0.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_pitch_pydub2`

```python
change_pitch_pydub2(y, sr, pitch_shift_semitones)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_semitones` — данные или параметры основного тона F0.

**Возвращает:** `tuple` со значениями: `y_shifted, sr`.

#### `change_pitch_pydub`

```python
change_pitch_pydub(y, sr, pitch_shift_semitones)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_semitones` — данные или параметры основного тона F0.

**Возвращает:** `tuple` со значениями: `y_shifted, sr`.

#### `change_pitch_rubberband`

```python
change_pitch_rubberband(y, sr, pitch_shift_hz)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch_shift_hz` — данные или параметры основного тона F0.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `calculate_spectral_tilt_pitch`

```python
calculate_spectral_tilt_pitch(y, sr)
```

Рассчитывает спектральный наклон основного тона в аудиосигнале.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_spectral_tilt_pitch2`

```python
calculate_spectral_tilt_pitch2(y, sr)
```

Рассчитывает спектральный наклон основного тона в аудиосигнале.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `extract_pitch_intensity`

```python
extract_pitch_intensity(signal, sr)
```

Extracts the pitch and its corresponding intensity from an audio signal.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `tuple` со значениями: `np.array(pitch_frequencies), np.array(pitch_intensities), np.array(times)`.

#### `calculate_pitch_intensity_avg2`

```python
calculate_pitch_intensity_avg2(signal, sr)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `change_pitch_bandwidth`

```python
change_pitch_bandwidth(signal, sr, pitch_factor)
```

Изменяет ширину канала pitch в аудиосигнале.

**Параметры:**

- `signal` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `pitch_factor` — Фактор изменения ширины канала pitch..

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `smooth_values`

```python
smooth_values(values, window_size=5)
```

Сглаживание значений с помощью скользящего среднего.

**Параметры:**

- `values` — входные данные соответствующего метода.
- `window_size` — размер окна обработки.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `detect_peaks`

```python
detect_peaks(pitch, prominence=1.0)
```

Простое определение пиков.

**Параметры:**

- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.
- `prominence` — входной параметр `prominence`.

**Возвращает:** результат выражения `peaks`.

#### `calculate_pitch_slope`

```python
calculate_pitch_slope(y, sr, is_smooth=True, is_peak=True, pitch=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `is_smooth` — входной параметр `is_smooth`.
- `is_peak` — входной параметр `is_peak`.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `0, 0, ''`.

#### `calculate_intensity_slope`

```python
calculate_intensity_slope(y, sr, is_smooth=True, is_peak=True, pitch=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `is_smooth` — входной параметр `is_smooth`.
- `is_peak` — входной параметр `is_peak`.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `0, 0, ''`.

#### `modify_pitch_slope`

```python
modify_pitch_slope(y, sr, slope_change=1.0)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `slope_change` — входной параметр `slope_change`.

**Возвращает:** `tuple` со значениями: `resynthesized_sound.values[0], int(sound.sampling_frequency)`.

#### `slope_pitch`

```python
slope_pitch(y, sr, start_delta=0.0, end_delta=0.0, pitch=None)
```

Выполняет операцию `slope_pitch` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `start_delta` — входной параметр `start_delta`.
- `end_delta` — входной параметр `end_delta`.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `None, None`.

#### `flatten_pitch`

```python
flatten_pitch(y, sr, pitch=None)
```

Выполняет операцию `flatten_pitch` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** результат выражения `slope_pitch(y, sr, start_delta=0.0, end_delta=0.0, pitch=pitch)`.

#### `change_audio_speed`

```python
change_audio_speed(y, sr, begin_speed=1.0, end_speed=1.0)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `begin_speed` — входной параметр `begin_speed`.
- `end_speed` — входной параметр `end_speed`.

**Возвращает:** результат выражения `new_y`.

#### `change_pitch_intonation_ex`

```python
change_pitch_intonation_ex(y, sr, begin_period, end_period, begin_amplitude, end_amplitude, offset=0, slope_change=0.0, pitch=None)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `begin_period` — временной параметр, с, если функция не указывает другую единицу.
- `end_period` — временной параметр, с, если функция не указывает другую единицу.
- `begin_amplitude` — амплитуда или коэффициент амплитуды.
- `end_amplitude` — амплитуда или коэффициент амплитуды.
- `offset` — входной параметр `offset`.
- `slope_change` — входной параметр `slope_change`.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `resynthesized_sound.values[0], int(sound.sampling_frequency)`.

#### `change_pitch_intonation`

```python
change_pitch_intonation(y, sr, period, offset, amplitude)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `period` — временной параметр, с, если функция не указывает другую единицу.
- `offset` — входной параметр `offset`.
- `amplitude` — амплитуда или коэффициент амплитуды.

**Возвращает:** рассчитанные данные; конкретная структура определяется указанной сигнатурой и назначением метода.

#### `change_audio_speed_period`

```python
change_audio_speed_period(y, sr, period, offset, amplitude, mean_speed=1.0)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `period` — временной параметр, с, если функция не указывает другую единицу.
- `offset` — входной параметр `offset`.
- `amplitude` — амплитуда или коэффициент амплитуды.
- `mean_speed` — входной параметр `mean_speed`.

**Возвращает:** результат выражения `new_y`.

#### `change_audio_speed_acceleration`

```python
change_audio_speed_acceleration(y, sr, initial_speed=1.0, acceleration=0.0)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `initial_speed` — входной параметр `initial_speed`.
- `acceleration` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `new_y`.

#### `change_audio_speed_periodic`

```python
change_audio_speed_periodic(y, sr, period, offset, amplitude, mean_speed=1.0)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `period` — временной параметр, с, если функция не указывает другую единицу.
- `offset` — входной параметр `offset`.
- `amplitude` — амплитуда или коэффициент амплитуды.
- `mean_speed` — входной параметр `mean_speed`.

**Возвращает:** результат выражения `new_y`.

#### `change_modulate_speed_per_fragment`

```python
change_modulate_speed_per_fragment(y, sr, fragment_duration, base_speed=1.0, amplitude=0.5)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `fragment_duration` — коэффициент или доля преобразования.
- `base_speed` — входной параметр `base_speed`.
- `amplitude` — амплитуда или коэффициент амплитуды.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `extract_timbre`

```python
extract_timbre(y, sr, n_formants=3)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `n_formants` — данные или параметры формант.

**Возвращает:** `tuple` со значениями: `spectral_envelope, formants`.

#### `extract_rhythm`

```python
extract_rhythm(y, sr)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `tuple` со значениями: `tempogram, tempo`.

#### `extract_timbre_from_pitch`

```python
extract_timbre_from_pitch(y, sr)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `tuple` со значениями: `avg_pitches, avg_spectral_centroid`.

#### `extract_rhythm_from_pitch`

```python
extract_rhythm_from_pitch(y, sr)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `tuple` со значениями: `pitch_changes, avg_tempogram`.

#### `find_speech_segments`

```python
find_speech_segments(y, sr, min_energy_threshold=0.01, min_pause_duration=0.5, frame_length=2048, hop_length=512, min_false_duration=0.1)
```

Находит указанные элементы или интервалы.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `min_energy_threshold` — порог принятия решения.
- `min_pause_duration` — коэффициент или доля преобразования.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.
- `min_false_duration` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `[] | segments`.

#### `calculate_amplitude_from_period`

```python
calculate_amplitude_from_period(filtered_pitches, filtered_times, period)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `filtered_pitches` — данные или параметры основного тона F0.
- `filtered_times` — временной параметр, с, если функция не указывает другую единицу.
- `period` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_period`

```python
calculate_period(filtered_pitches, filtered_times)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `filtered_pitches` — данные или параметры основного тона F0.
- `filtered_times` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_period_shift`

```python
calculate_period_shift(filtered_pitches, filtered_times, period)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `filtered_pitches` — данные или параметры основного тона F0.
- `filtered_times` — временной параметр, с, если функция не указывает другую единицу.
- `period` — временной параметр, с, если функция не указывает другую единицу.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `extract_pitch_rate`

```python
extract_pitch_rate(y, sr, medfilt_size=5, pitch=None)
```

Извлекает признак или временную последовательность из сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `medfilt_size` — входной параметр `medfilt_size`.
- `pitch` — заранее рассчитанные данные F0; `None` запускает расчёт.

**Возвращает:** `tuple` со значениями: `None, None, None`.

#### `scale_pitch_width`

```python
scale_pitch_width(y, sr, factor=1.0)
```

Масштабирует указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `factor` — множитель преобразования.

**Возвращает:** `tuple` со значениями: `resynthesized_sound.values[0], int(sound.sampling_frequency)`.

## Визуализация

Модуль: `sk_speech.sk_plot`.

Графики траекторий, спектров, спектрограмм, гласных и результатов преобразования.

### Функции

#### `plot_formant_trajectory`

```python
plot_formant_trajectory(time_stamps, formant_frequencies, index)
```

Строит график указанной характеристики.

**Параметры:**

- `time_stamps` — временной параметр, с, если функция не указывает другую единицу.
- `formant_frequencies` — частота или последовательность частот, Гц.
- `index` — индекс анализируемого элемента.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_pitch_trajectory`

```python
plot_pitch_trajectory(time, pitch_trajectory)
```

Строит график указанной характеристики.

**Параметры:**

- `time` — временной параметр, с, если функция не указывает другую единицу.
- `pitch_trajectory` — данные или параметры основного тона F0.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_trajectory_formants_and_pitch`

```python
plot_trajectory_formants_and_pitch(y, sr, window_size=1024)
```

Строит график указанной характеристики.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `window_size` — размер окна обработки.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_spectral_slope`

```python
plot_spectral_slope(times, slopes)
```

Строит график указанной характеристики.

**Параметры:**

- `times` — временные координаты, с.
- `slopes` — входной параметр `slopes`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_intensity`

```python
plot_intensity(y, sr)
```

Построение графиков интенсивности основного тона и интенсивностей формант.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `visualize_pitch`

```python
visualize_pitch(input_file, output_file)
```

Визуализирует оригинальный и изменённый основной тон.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_vowel_boundaries`

```python
plot_vowel_boundaries(y, sr, vowel_boundaries, threshold)
```

Строит график указанной характеристики.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `threshold` — порог принятия решения.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `visualize_vowel_boundaries`

```python
visualize_vowel_boundaries(input_file, vowel_boundaries, threshold=0.1)
```

Визуализирует указанную характеристику или сравнение.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `threshold` — порог принятия решения.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `visualize_amplified_vowels`

```python
visualize_amplified_vowels(original_file, amplified_file, vowel_boundaries)
```

Визуализирует указанную характеристику или сравнение.

**Параметры:**

- `original_file` — путь к файлу или каталогу.
- `amplified_file` — путь к файлу или каталогу.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `compute_energy`

```python
compute_energy(signal, frame_length, hop_length)
```

Вычисляет указанную характеристику.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `visualize_energy_vowels`

```python
visualize_energy_vowels(original_file, amplified_file, vowel_boundaries)
```

Визуализирует указанную характеристику или сравнение.

**Параметры:**

- `original_file` — путь к файлу или каталогу.
- `amplified_file` — путь к файлу или каталогу.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `visualize_shifted_formants`

```python
visualize_shifted_formants(original_file, shifted_file, show_formant_1=True, show_formant_2=True, show_formant_3=True, show_formant_4=True)
```

Визуализирует указанную характеристику или сравнение.

**Параметры:**

- `original_file` — путь к файлу или каталогу.
- `shifted_file` — путь к файлу или каталогу.
- `show_formant_1` — данные или параметры формант.
- `show_formant_2` — данные или параметры формант.
- `show_formant_3` — данные или параметры формант.
- `show_formant_4` — данные или параметры формант.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `visualize_spectrograms`

```python
visualize_spectrograms(input_file, output_file)
```

Визуализирует спектрограммы аудиофайлов до и после фильтрации шума.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `visualize_remove_noise`

```python
visualize_remove_noise(input_file, output_file)
```

Визуализирует частотные спектры аудиофайлов до и после фильтрации шума.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_psd`

```python
plot_psd(freqs, psd, title='Power Spectral Density')
```

Отображает спектральную плотность мощности (PSD).

**Параметры:**

- `freqs` — Частоты..
- `psd` — Значения PSD..
- `title` — Заголовок графика..

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `plot_spectral_flatness`

```python
plot_spectral_flatness(y, sr, n_fft=2048, hop_length=512)
```

Строит график спектральной плоскости.

**Параметры:**

- `y` — Аудиосигнал..
- `sr` — Частота дискретизации..
- `n_fft` — Длина окна для вычисления STFT..
- `hop_length` — Шаг между окнами..

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

## Генерация сигналов

Модуль: `sk_speech.sk_signal`.

Гармонические компоненты, временные оси, сборка и сохранение синтетического сигнала.

### Функции

#### `calculate_harmonic_frequencies`

```python
calculate_harmonic_frequencies(Freq_range, Bw_range, N, t)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `Freq_range` — входной параметр `Freq_range`.
- `Bw_range` — входной параметр `Bw_range`.
- `N` — входной параметр `N`.
- `t` — входной параметр `t`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `calculate_harmonic_amplitudes`

```python
calculate_harmonic_amplitudes(Freq_range, f_k, Amp_range, Bw_range, t)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `Freq_range` — входной параметр `Freq_range`.
- `f_k` — входной параметр `f_k`.
- `Amp_range` — входной параметр `Amp_range`.
- `Bw_range` — входной параметр `Bw_range`.
- `t` — входной параметр `t`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `generate_time_axis`

```python
generate_time_axis(rate, duration)
```

Генерирует сигнал или последовательность параметров.

**Параметры:**

- `rate` — частота дискретизации, Гц.
- `duration` — длительность, с.

**Возвращает:** результат выражения `np.linspace(0, duration, int(rate * duration), endpoint=False)`.

#### `generate_harmonic_signal`

```python
generate_harmonic_signal(f_k, A_k, t)
```

Генерирует сигнал или последовательность параметров.

**Параметры:**

- `f_k` — входной параметр `f_k`.
- `A_k` — входной параметр `A_k`.
- `t` — входной параметр `t`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `save_to_wav`

```python
save_to_wav(signal, rate, filename)
```

Сохраняет результат в файл.

**Параметры:**

- `signal` — одномерный аудиосигнал `numpy.ndarray`.
- `rate` — частота дискретизации, Гц.
- `filename` — имя или путь к файлу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `create_signal`

```python
create_signal(Freq_range, Amp_range, Bw_range, duration, rate=44100, num_harmonics=5)
```

Создаёт структуру данных, маску или сигнал.

**Параметры:**

- `Freq_range` — входной параметр `Freq_range`.
- `Amp_range` — входной параметр `Amp_range`.
- `Bw_range` — входной параметр `Bw_range`.
- `duration` — длительность, с.
- `rate` — частота дискретизации, Гц.
- `num_harmonics` — входной параметр `num_harmonics`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `combine_signals`

```python
combine_signals(signals)
```

Объединяет несколько сигналов или представлений.

**Параметры:**

- `signals` — входной параметр `signals`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

## Голосовая щель и воздушный поток

Модуль: `sk_speech.sk_vocal_cords`.

Физические оценки площади голосовой щели, сопротивления, потока, давления и SPL.

### Функции

#### `calculate_base_S0`

```python
calculate_base_S0(Base0, height, height_gender)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `Base0` — входной параметр `Base0`.
- `height` — рост, используемый физической моделью.
- `height_gender` — входной параметр `height_gender`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_min_S_fast`

```python
calculate_min_S_fast(Base_min, height, height_gender, factor_fast)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `Base_min` — входной параметр `Base_min`.
- `height` — рост, используемый физической моделью.
- `height_gender` — входной параметр `height_gender`.
- `factor_fast` — коэффициент или доля преобразования.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_min_S_slow`

```python
calculate_min_S_slow(Base_min, height, height_gender, factor_slow)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `Base_min` — входной параметр `Base_min`.
- `height` — рост, используемый физической моделью.
- `height_gender` — входной параметр `height_gender`.
- `factor_slow` — коэффициент или доля преобразования.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_S`

```python
get_S(gender=None, height=None)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `gender` — пол или голосовая категория, используемая моделью.
- `height` — рост, используемый физической моделью.

**Возвращает:** `tuple` со значениями: `S0, S_min_fast, S_min_slow`.

#### `fS_t1`

```python
fS_t1(t, T0, alpha)
```

Выполняет операцию `fS_t1` над переданными данными.

**Параметры:**

- `t` — входной параметр `t`.
- `T0` — входной параметр `T0`.
- `alpha` — входной параметр `alpha`.

**Возвращает:** результат выражения `np.sin(1.5 * np.pi * t / T0) ** alpha`.

#### `fS_t2`

```python
fS_t2(t, T0, beta)
```

Выполняет операцию `fS_t2` над переданными данными.

**Параметры:**

- `t` — входной параметр `t`.
- `T0` — входной параметр `T0`.
- `beta` — входной параметр `beta`.

**Возвращает:** результат выражения `np.cos(0.5 * np.pi * (3.0 * t - T0) / T0) ** beta`.

#### `calculate_dynamic_area`

```python
calculate_dynamic_area(S_max, T0, alpha, beta)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `S_max` — входной параметр `S_max`.
- `T0` — входной параметр `T0`.
- `alpha` — входной параметр `alpha`.
- `beta` — входной параметр `beta`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_S`

```python
calculate_S(T0, S0, Stress_fast, Stress_slow, alpha, beta, w, S_min_fast, S_min_slow)
```

Рассчитывает площадь голосовой щели с учетом быстрого и медленного стресса, с корректировками для более мягкого изменения.

**Параметры:**

- `T0` — входной параметр `T0`.
- `S0` — Базовая площадь голосовой щели при спокойной речи (м²).
- `Stress_fast` — Значение стресса для быстрой реакции (от 0 до 1).
- `Stress_slow` — Значение стресса для медленной реакции (от 0 до 1).
- `alpha` — Коэффициент для экспоненциальной функции для медленного стресса.
- `beta` — Пороговое значение стресса для медленного стресса.
- `w` — Весовой коэффициент для перехода между быстрым и медленным стрессом.
- `S_min_fast` — Минимальная площадь голосовой щели при быстром стрессе (м²).
- `S_min_slow` — Минимальная площадь голосовой щели при медленном стрессе (м²).

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_diameter`

```python
calculate_diameter(height, sex)
```

Рассчитывает диаметр дыхательных путей на основе роста и пола.

**Параметры:**

- `height` — Рост человека (см).
- `sex` — Пол человека ('male' или 'female').

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_length`

```python
calculate_length(height)
```

Рассчитывает длину дыхательных путей на основе роста.

**Параметры:**

- `height` — Рост человека (см).

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `hagen_poiseuille_resistance`

```python
hagen_poiseuille_resistance(length, radius, viscosity=1.8e-05)
```

Рассчитывает сопротивление по формуле Хагена-Пуазейля для ламинарного потока.

**Параметры:**

- `length` — Длина трубы (м).
- `radius` — Радиус трубы (м).
- `viscosity` — Вязкость воздуха (Па·с).

**Возвращает:** результат выражения `resistance`.

#### `darcy_weisbach_resistance`

```python
darcy_weisbach_resistance(friction_factor, length, diameter)
```

Рассчитывает сопротивление по формуле Дарси-Уэйсбаха для турбулентного потока.

**Параметры:**

- `friction_factor` — Коэффициент трения.
- `length` — Длина трубы (м).
- `diameter` — Диаметр трубы (м).

**Возвращает:** результат выражения `resistance`.

#### `reynolds_number`

```python
reynolds_number(flow_rate, diameter, viscosity=1.81e-05, rho=1.225)
```

Рассчитывает число Рейнольдса для оценки типа потока.

**Параметры:**

- `flow_rate` — Скорость потока (м³/с).
- `diameter` — Диаметр трубы (м).
- `viscosity` — Вязкость воздуха (Па·с) ~ 1.81e-5.
- `rho` — входной параметр `rho`.

**Возвращает:** результат выражения `re_number`.

#### `calculate_flow`

```python
calculate_flow(V, T, S)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `V` — входной параметр `V`.
- `T` — входной параметр `T`.
- `S` — входной параметр `S`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_subglottic_pressure`

```python
calculate_subglottic_pressure(flow_rate, rho=1.225)
```

Рассчитывает субглотическое давление на основе скорости воздушного потока.

**Параметры:**

- `flow_rate` — Скорость воздушного потока (м/с).
- `rho` — Плотность воздуха (кг/м³).

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_spl`

```python
calculate_spl(height, sex, F0, volume_air, time_speech, Stress_fast, Stress_slow)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `height` — рост, используемый физической моделью.
- `sex` — входной параметр `sex`.
- `F0` — входной параметр `F0`.
- `volume_air` — входной параметр `volume_air`.
- `time_speech` — временной параметр, с, если функция не указывает другую единицу.
- `Stress_fast` — входной параметр `Stress_fast`.
- `Stress_slow` — входной параметр `Stress_slow`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

## Голосовой тракт

Модуль: `sk_speech.sk_vocal_tract`.

Связь длины голосового тракта и резонансных частот формант.

### Функции

#### `get_tract_length`

```python
get_tract_length(gender, age, height)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `gender` — пол или голосовая категория, используемая моделью.
- `age` — входной параметр `age`.
- `height` — рост, используемый физической моделью.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_frequency_formant`

```python
get_frequency_formant(tract_length, index)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `tract_length` — входной параметр `tract_length`.
- `index` — индекс анализируемого элемента.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_tract_length_from_formant`

```python
get_tract_length_from_formant(frequencyHz, index)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `frequencyHz` — частота или последовательность частот, Гц.
- `index` — индекс анализируемого элемента.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_tract_length_from_formants`

```python
get_tract_length_from_formants(frequencyHz1, frequencyHz2, frequencyHz3, frequencyHz4, frequencyHz5)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `frequencyHz1` — частота или последовательность частот, Гц.
- `frequencyHz2` — частота или последовательность частот, Гц.
- `frequencyHz3` — частота или последовательность частот, Гц.
- `frequencyHz4` — частота или последовательность частот, Гц.
- `frequencyHz5` — частота или последовательность частот, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

## Комплексный профиль и преобразование речи

Модуль: `sk_speech.sk_volume`.

Объединение акустических признаков, профили, векторы, пакетная обработка и комплексное изменение речи.

### Функции

#### `create_empty_value`

```python
create_empty_value(template_speech=False)
```

Создаёт структуру данных, маску или сигнал.

**Параметры:**

- `template_speech` — входной параметр `template_speech`.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `create_empty_formant`

```python
create_empty_formant()
```

Создаёт структуру данных, маску или сигнал.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `load_vectors_from_json`

```python
load_vectors_from_json(file_path)
```

Загружает данные из файла.

**Параметры:**

- `file_path` — путь к файлу.

**Возвращает:** результат выражения `speech`.

#### `trim_silence`

```python
trim_silence(y, sr, top_db=20, apply_noise_reduction=False)
```

Удаляет тишину в начале и в конце аудиофайла и при необходимости применяет шумоподавление.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `top_db` — входной параметр `top_db`.
- `apply_noise_reduction` — входной параметр `apply_noise_reduction`.

**Возвращает:** результат выражения `y_trimmed`.

#### `detect_leading_silence`

```python
detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10)
```

Обнаруживает указанные события или интервалы.

**Параметры:**

- `sound` — объект аудиосигнала Praat или Pydub согласно функции.
- `silence_threshold` — порог принятия решения.
- `chunk_size` — входной параметр `chunk_size`.

**Возвращает:** результат выражения `trim_ms`.

#### `trim_silence_pydub`

```python
trim_silence_pydub(sound)
```

Обрезает сигнал по заданному условию.

**Параметры:**

- `sound` — объект аудиосигнала Praat или Pydub согласно функции.

**Возвращает:** результат выражения `trimmed_sound`.

#### `calculate_intensity_avg`

```python
calculate_intensity_avg(y, sr)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_intensity_max`

```python
calculate_intensity_max(y, sr)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `transition`

```python
transition(V_norm, V_loud, alpha)
```

Выполняет операцию `transition` над переданными данными.

**Параметры:**

- `V_norm` — входной параметр `V_norm`.
- `V_loud` — входной параметр `V_loud`.
- `alpha` — входной параметр `alpha`.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_pitch_shift_semitones`

```python
calculate_pitch_shift_semitones(frequency_change)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `frequency_change` — частота или последовательность частот, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `energy_speech`

```python
energy_speech(volume)
```

Выполняет операцию `energy_speech` над переданными данными.

**Параметры:**

- `volume` — уровень или коэффициент громкости.

**Возвращает:** `tuple` со значениями: `energy_pitch_factor, pitch_shift_semitones, formant_bandwidth_factors, formant_energy_factors, formant_shifts, formant_energy_vowel`.

#### `change_speech_volume`

```python
change_speech_volume(y, sr, volume, is_noise=False, is_shift=False)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `volume` — уровень или коэффициент громкости.
- `is_noise` — входной параметр `is_noise`.
- `is_shift` — входной параметр `is_shift`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `change_volume`

```python
change_volume(y, sr, volume_from, volume_to, is_noise=False, is_shift=False)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `volume_from` — входной параметр `volume_from`.
- `volume_to` — входной параметр `volume_to`.
- `is_noise` — входной параметр `is_noise`.
- `is_shift` — входной параметр `is_shift`.

**Возвращает:** результат выражения `y_filtered | y`.

#### `compute_spectral_slope`

```python
compute_spectral_slope(y, sr, window_size=1024, hop_size=512)
```

Рассчитывает спектральный наклон для аудиосигнала.

**Параметры:**

- `y` — Нормализованный аудиосигнал..
- `sr` — Частота дискретизации..
- `window_size` — Размер окна для анализа..
- `hop_size` — Шаг между окнами..

**Возвращает:** `tuple` со значениями: `times, slopes`.

#### `change_volume_linear`

```python
change_volume_linear(audio_path, output_path, start_db, end_db)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `audio_path` — путь к файлу или каталогу.
- `output_path` — путь или контейнер для выходных данных.
- `start_db` — входной параметр `start_db`.
- `end_db` — входной параметр `end_db`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `change_audio_volume`

```python
change_audio_volume(y, sr, volume_factor)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `volume_factor` — коэффициент или доля преобразования.

**Возвращает:** `tuple` со значениями: `modified_signal, sr`.

#### `mix_audio`

```python
mix_audio(y_orig, y_filtered, start_mix_ratio=1.0, end_mix_ratio=1.0)
```

Смешивает несколько сигналов или представлений.

**Параметры:**

- `y_orig` — входной параметр `y_orig`.
- `y_filtered` — входной параметр `y_filtered`.
- `start_mix_ratio` — коэффициент или доля преобразования.
- `end_mix_ratio` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_mixed`.

#### `get_tract_length`

```python
get_tract_length(y, sr)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_tract_length_expended`

```python
get_tract_length_expended(y, sr)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_loudness_corrections`

```python
calculate_loudness_corrections(frequencies)
```

Рассчитывает поправочные коэффициенты для восприятия громкости на основе частот.

**Параметры:**

- `frequencies` — массив частот (в Гц).

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_speech_volume`

```python
calculate_speech_volume(frequencies, amplitudes_db, combine_mode='amplitude')
```

Рассчитывает суммарную громкость речи с учетом поправок для восприятия громкости.

**Параметры:**

- `frequencies` — массив частот (в Гц).
- `amplitudes_db` — массив относительных цифровых амплитуд в дБ.
- `combine_mode` — ``amplitude`` складывает линейные амплитуды;.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_energy`

```python
calculate_formant_energy(amplitude_db, bandwidth)
```

Рассчитывает энергию форманты на основе амплитуды в дБ и ширины канала.

**Параметры:**

- `amplitude_db` — Амплитуда форманты в децибелах.
- `bandwidth` — Ширина канала форманты в Гц.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `get_speech_params`

```python
get_speech_params(y, sr, template_speech=False, options=None)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `template_speech` — входной параметр `template_speech`.
- `options` — словарь включаемых признаков и параметров расчёта.

**Возвращает:** результат выражения `speech`.

#### `get_speech_vector`

```python
get_speech_vector(params, norm_params)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `params` — входные данные соответствующего метода.
- `norm_params` — параметры нейтрального эталона.

**Возвращает:** результат выражения `vector`.

#### `get_speech_new`

```python
get_speech_new(norm_params, params, vectors, volume, emotion)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `norm_params` — параметры нейтрального эталона.
- `params` — входные данные соответствующего метода.
- `vectors` — набор эталонных векторов признаков.
- `volume` — уровень или коэффициент громкости.
- `emotion` — управляющая координата, используемая комплексным преобразованием.

**Возвращает:** результат выражения `speech`.

#### `get_speech_mul`

```python
get_speech_mul(new_params, params)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `new_params` — входной параметр `new_params`.
- `params` — входные данные соответствующего метода.

**Возвращает:** результат выражения `muls`.

#### `get_change_speech`

```python
get_change_speech(y, sr, muls, new_params, params)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `muls` — входной параметр `muls`.
- `new_params` — входной параметр `new_params`.
- `params` — входные данные соответствующего метода.

**Возвращает:** `tuple` со значениями: `y, sr`.

#### `process_wav_files_in_folder`

```python
process_wav_files_in_folder(folder_path, file_norm_speach)
```

Выполняет полный цикл обработки входных данных.

**Параметры:**

- `folder_path` — путь к каталогу с аудиофайлами.
- `file_norm_speach` — путь к файлу или каталогу.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `convert_params_to_serializable`

```python
convert_params_to_serializable(params)
```

Рекурсивно конвертирует объекты numpy и другие нестандартные типы данных в стандартные типы данных Python.

**Параметры:**

- `params` — входные данные соответствующего метода.

**Возвращает:** рассчитанные данные; конкретная структура определяется указанной сигнатурой и назначением метода.

#### `update_param`

```python
update_param(total_param, param)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `total_param` — входной параметр `total_param`.
- `param` — входной параметр `param`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `update_vowels`

```python
update_vowels(total_param, param)
```

Обновляет внутреннее состояние модели.

**Параметры:**

- `total_param` — входной параметр `total_param`.
- `param` — входной параметр `param`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `average_params`

```python
average_params(params)
```

Выполняет операцию `average_params` над переданными данными.

**Параметры:**

- `params` — входные данные соответствующего метода.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `average_vowels`

```python
average_vowels(params)
```

Выполняет операцию `average_vowels` над переданными данными.

**Параметры:**

- `params` — входные данные соответствующего метода.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `init_speech`

```python
init_speech(file_speech_norm, file_speech_volume_up_emotion_up=None, file_speech_volume_up_emotion_down=None, file_speech_volume_down_emotion_up=None, file_speech_volume_down_emotion_down=None, gender=None, options=None)
```

Выполняет операцию `init_speech` над переданными данными.

**Параметры:**

- `file_speech_norm` — путь к файлу или каталогу.
- `file_speech_volume_up_emotion_up` — путь к файлу или каталогу.
- `file_speech_volume_up_emotion_down` — путь к файлу или каталогу.
- `file_speech_volume_down_emotion_up` — путь к файлу или каталогу.
- `file_speech_volume_down_emotion_down` — путь к файлу или каталогу.
- `gender` — пол или голосовая категория, используемая моделью.
- `options` — словарь включаемых признаков и параметров расчёта.

**Возвращает:** результат выражения `speech`.

#### `change_speech`

```python
change_speech(speech, cur_speech, volume, emotion)
```

Изменяет указанное свойство аудиосигнала.

**Параметры:**

- `speech` — режим или структура профиля речи — зависит от функции.
- `cur_speech` — входной параметр `cur_speech`.
- `volume` — уровень или коэффициент громкости.
- `emotion` — управляющая координата, используемая комплексным преобразованием.

**Возвращает:** `tuple` со значениями: `y_new, sr_new`.

#### `speech_params`

```python
speech_params(input_file, speech)
```

Выполняет операцию `speech_params` над переданными данными.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `speech` — режим или структура профиля речи — зависит от функции.

**Возвращает:** `dict` со структурированными результатами расчёта.

#### `process_audio`

```python
process_audio(file_input, folder, min_speech_duration=3.0, max_speech_pause=1.0, only_pitch=True, remove_other_pitch=False, speech_params_required=True, min_total_speech_duration=3.0, min_pause_duration=1.0)
```

Выполняет полный цикл обработки входных данных.

**Параметры:**

- `file_input` — путь к файлу или каталогу.
- `folder` — входной параметр `folder`.
- `min_speech_duration` — коэффициент или доля преобразования.
- `max_speech_pause` — входной параметр `max_speech_pause`.
- `only_pitch` — данные или параметры основного тона F0.
- `remove_other_pitch` — данные или параметры основного тона F0.
- `speech_params_required` — входной параметр `speech_params_required`.
- `min_total_speech_duration` — коэффициент или доля преобразования.
- `min_pause_duration` — коэффициент или доля преобразования.

**Возвращает:** `None`; функция изменяет состояние объекта или выполняет побочный эффект.

#### `trim_segments_to_pitch`

```python
trim_segments_to_pitch(y, sr, min_energy_threshold=0.01, min_pause_duration=0.5, remove_other_pitch=False, frame_length=2048, hop_length=512, min_false_duration=0.3, pitch_margin=1.0)
```

Обрезает сигнал по заданному условию.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `min_energy_threshold` — порог принятия решения.
- `min_pause_duration` — коэффициент или доля преобразования.
- `remove_other_pitch` — данные или параметры основного тона F0.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.
- `min_false_duration` — коэффициент или доля преобразования.
- `pitch_margin` — данные или параметры основного тона F0.

**Возвращает:** результат выражения `trimmed_segments`.

#### `set_speed`

```python
set_speed(input_file, output_file, speed)
```

Выполняет операцию `set_speed` над переданными данными.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.
- `speed` — входной параметр `speed`.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `generate_signal`

```python
generate_signal(frequencies, bandwidths, intensities, times, delta_time, energy_correction=0, sr=44100)
```

Генерирует аудиосигнал на основе массивов частот, ширины канала и интенсивности.

**Параметры:**

- `frequencies` — частоты или последовательности частот.
- `bandwidths` — ширины частотных полос, Гц.
- `intensities` — значения интенсивности.
- `times` — временные координаты, с.
- `delta_time` — шаг времени, с.
- `energy_correction` — энергия или коэффициент энергии.
- `sr` — частота дискретизации, Гц.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `mix_audio_signals`

```python
mix_audio_signals(audio_signals)
```

Смешивает несколько аудиосигналов разной длины, добавляя тишину там, где сигнал отсутствует, и возвращает один аудиосигнал с длиной, равной максимальной длине среди всех сигналов.

**Параметры:**

- `audio_signals` — входной параметр `audio_signals`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

## Гласные

Модуль: `sk_speech.sk_vowels`.

Поиск границ и типов гласных, их статистика, формантные преобразования и изменение длительности.

### Функции

#### `compute_vowel_type`

```python
compute_vowel_type(y, sr, start, end, frame_length, hop_length)
```

Вычисляет указанную характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `start` — входной параметр `start`.
- `end` — входной параметр `end`.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** `tuple` со значениями: `midpoint_time, vowel_type`.

#### `detect_vowel_boundaries_parallel`

```python
detect_vowel_boundaries_parallel(y, sr, threshold=0.1)
```

Обнаруживает указанные события или интервалы.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `threshold` — порог принятия решения.

**Возвращает:** результат выражения `vowel_types`.

#### `detect_vowel_boundaries`

```python
detect_vowel_boundaries(y, sr, threshold=0.1)
```

Обнаруживает указанные события или интервалы.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `threshold` — порог принятия решения.

**Возвращает:** результат выражения `vowel_types`.

#### `detect_vowel_boundaries2`

```python
detect_vowel_boundaries2(y, sr, threshold=0.1)
```

Обнаруживает указанные события или интервалы.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `threshold` — порог принятия решения.

**Возвращает:** результат выражения `vowel_types`.

#### `create_formant_mask_amplitude`

```python
create_formant_mask_amplitude(freqs, formant_freqs, bandwidth=50)
```

Создаёт структуру данных, маску или сигнал.

**Параметры:**

- `freqs` — частота или последовательность частот, Гц.
- `formant_freqs` — частота или последовательность частот, Гц.
- `bandwidth` — ширина полосы или набор ширин, Гц.

**Возвращает:** результат выражения `mask`.

#### `create_formant_mask_energy`

```python
create_formant_mask_energy(freqs, formant_freqs, bandwidth=50)
```

Создаёт структуру данных, маску или сигнал.

**Параметры:**

- `freqs` — частота или последовательность частот, Гц.
- `formant_freqs` — частота или последовательность частот, Гц.
- `bandwidth` — ширина полосы или набор ширин, Гц.

**Возвращает:** результат выражения `mask`.

#### `amplify_vowels`

```python
amplify_vowels(y, sr, vowel_boundaries, formant_gains_dict, frame_duration=0.05)
```

Усиливает выбранные составляющие сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formant_gains_dict` — данные или параметры формант.
- `frame_duration` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_amplified`.

#### `determine_vowel_type`

```python
determine_vowel_type(frame_start, vowel_boundaries, sr, frame_duration=0.05)
```

Выполняет операцию `determine_vowel_type` над переданными данными.

**Параметры:**

- `frame_start` — входной параметр `frame_start`.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `sr` — частота дискретизации, Гц.
- `frame_duration` — коэффициент или доля преобразования.

**Возвращает:** `str` — метка или текстовый результат классификации.

#### `apply_formant_shifts_vowels`

```python
apply_formant_shifts_vowels(y, sr, vowel_boundaries, formant_shifts_dict, frame_duration=0.05)
```

Применяет указанное преобразование или фильтр.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formant_shifts_dict` — данные или параметры формант.
- `frame_duration` — коэффициент или доля преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `energy_vowels`

```python
energy_vowels(y, sr, vowel_boundaries, formant_gains_dict, frame_duration=0.05)
```

Выполняет операцию `energy_vowels` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formant_gains_dict` — данные или параметры формант.
- `frame_duration` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y | y_energy_amplified`.

#### `shift_formants_vowels`

```python
shift_formants_vowels(input_file, output_file, vowel_boundaries, formant_shifts_dict, frame_duration=0.05)
```

Выполняет операцию `shift_formants_vowels` над переданными данными.

**Параметры:**

- `input_file` — путь к входному аудиофайлу.
- `output_file` — путь к выходному аудиофайлу.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formant_shifts_dict` — данные или параметры формант.
- `frame_duration` — коэффициент или доля преобразования.

**Возвращает:** `None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии.

#### `calculate_formant_amplitude`

```python
calculate_formant_amplitude(y, sr, vowel_boundaries, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_freq`

```python
calculate_formant_freq(y, sr, vowel_boundaries, formants)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `calculate_formant_energy`

```python
calculate_formant_energy(y, sr, vowel_boundaries, formants=None)
```

Рассчитывает указанную акустическую или физическую характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** числовое значение, массив либо структура, указанная в описании метода.

#### `mean_amplitude_dB_for_vowels`

```python
mean_amplitude_dB_for_vowels(y, sr, vowel_boundaries, formants=None)
```

Выполняет операцию `mean_amplitude_dB_for_vowels` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** результат выражения `mean_amplitudes_by_vowel`.

#### `mean_energy_for_vowels`

```python
mean_energy_for_vowels(y, sr, vowel_boundaries, formants=None)
```

Выполняет операцию `mean_energy_for_vowels` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** результат выражения `mean_energies_by_vowel`.

#### `mean_formants_for_vowels`

```python
mean_formants_for_vowels(y, sr, vowel_boundaries, formants=None)
```

Выполняет операцию `mean_formants_for_vowels` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** результат выражения `mean_formants_by_vowel`.

#### `group_vowels`

```python
group_vowels(vowel_boundaries)
```

Выполняет операцию `group_vowels` над переданными данными.

**Параметры:**

- `vowel_boundaries` — интервалы и метки обнаруженных гласных.

**Возвращает:** результат выражения `unique_vowel_types`.

#### `find_missing_vowels`

```python
find_missing_vowels(vowel_boundaries)
```

Находит указанные элементы или интервалы.

**Параметры:**

- `vowel_boundaries` — интервалы и метки обнаруженных гласных.

**Возвращает:** результат выражения `missing_vowels`.

#### `find_closest_vowel`

```python
find_closest_vowel(existing_vowels, mean_amplitudes_by_vowel)
```

Находит указанные элементы или интервалы.

**Параметры:**

- `existing_vowels` — входной параметр `existing_vowels`.
- `mean_amplitudes_by_vowel` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `closest_vowel`.

#### `create_formant_mask_low_high`

```python
create_formant_mask_low_high(freqs, low, high)
```

Создаёт структуру данных, маску или сигнал.

**Параметры:**

- `freqs` — частота или последовательность частот, Гц.
- `low` — входной параметр `low`.
- `high` — входной параметр `high`.

**Возвращает:** результат выражения `mask`.

#### `amplitude_vowels_mul`

```python
amplitude_vowels_mul(y, sr, vowels, frame_duration=0.05, formants=None)
```

Выполняет операцию `amplitude_vowels_mul` над переданными данными.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowels` — входной параметр `vowels`.
- `frame_duration` — коэффициент или доля преобразования.
- `formants` — заранее рассчитанные данные формант; `None` запускает расчёт.

**Возвращает:** результат выражения `y | y_energy_amplified`.

#### `get_vowel_formant_info`

```python
get_vowel_formant_info(y, sr, vowel_boundaries)
```

Получает рассчитанное представление или характеристику.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.

**Возвращает:** результат выражения `formants`.

#### `smooth_stretch_vowel`

```python
smooth_stretch_vowel(y, sr, stretch_factor)
```

Нелинейное растяжение участка с гласной с плавным переходом на границах.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `stretch_factor` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `smoothed_vowel`.

#### `stretch_vowels_preserve_pitch`

```python
stretch_vowels_preserve_pitch(y, sr, vowel_boundaries, delta_seconds, speed_factor)
```

Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными, при этом сохраняется тональность (pitch).

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `delta_seconds` — входной параметр `delta_seconds`.
- `speed_factor` — коэффициент или доля преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `stretch_vowels_preserve_pitch2`

```python
stretch_vowels_preserve_pitch2(y, sr, vowel_boundaries, delta_seconds, speed_factor)
```

Ускоряет/замедляет аудио за счет повторения фрагментов с гласными, при этом сохраняется тональность (pitch).

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `delta_seconds` — входной параметр `delta_seconds`.
- `speed_factor` — коэффициент или доля преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `stretch_vowels_preserve_pitch3`

```python
stretch_vowels_preserve_pitch3(y, sr, vowel_boundaries, delta_seconds, speed_factor)
```

Ускоряет/замедляет аудио за счет чередования прямого и обратного повторения фрагментов с гласными, при этом сохраняется тональность (pitch).

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `delta_seconds` — входной параметр `delta_seconds`.
- `speed_factor` — коэффициент или доля преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `stretch_vowels_preserve_pitch4`

```python
stretch_vowels_preserve_pitch4(y, sr, vowel_boundaries, delta_seconds, speed_factor, filter_size=200)
```

Ускоряет/замедляет аудио за счёт чередования прямого и обратного повторения фрагментов с гласными, применяя медианный фильтр для устранения резких колебаний.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `delta_seconds` — входной параметр `delta_seconds`.
- `speed_factor` — коэффициент или доля преобразования.
- `filter_size` — входной параметр `filter_size`.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `butter_lowpass_filter`

```python
butter_lowpass_filter(data, cutoff, fs, order=4)
```

Выполняет операцию `butter_lowpass_filter` над переданными данными.

**Параметры:**

- `data` — входные данные соответствующего метода.
- `cutoff` — входной параметр `cutoff`.
- `fs` — частота дискретизации, Гц.
- `order` — входной параметр `order`.

**Возвращает:** результат выражения `lfilter(b, a, data)`.

#### `stretch_vowels_preserve_pitch5`

```python
stretch_vowels_preserve_pitch5(y, sr, vowel_boundaries, delta_seconds, speed_factor, cutoff_freq=5000)
```

Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными, с применением сглаживания переходов и фильтрации для уменьшения эха.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `delta_seconds` — входной параметр `delta_seconds`.
- `speed_factor` — коэффициент или доля преобразования.
- `cutoff_freq` — частота или последовательность частот, Гц.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `wsola`

```python
wsola(audio, sr, speed_factor, frame_size=2048, hop_size=512)
```

Реализует WSOLA для изменения скорости аудиосигнала с сохранением высоты тона.

**Параметры:**

- `audio` — аудиосигнал.
- `sr` — частота дискретизации, Гц.
- `speed_factor` — коэффициент или доля преобразования.
- `frame_size` — входной параметр `frame_size`.
- `hop_size` — входной параметр `hop_size`.

**Возвращает:** результат выражения `output_audio`.

#### `stretch_vowels_preserve_pitch6`

```python
stretch_vowels_preserve_pitch6(y, sr, vowel_boundaries, delta_seconds, speed_factor)
```

Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными, при этом сохраняется тональность (pitch).

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `vowel_boundaries` — интервалы и метки обнаруженных гласных.
- `delta_seconds` — входной параметр `delta_seconds`.
- `speed_factor` — коэффициент или доля преобразования.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `stretch_vowels_preserve_pitch7`

```python
stretch_vowels_preserve_pitch7(y, sr, intervals, speed_factor, cutoff_freq=5000)
```

Ускоряет/замедляет аудио за счет изменения длительности фреймов с гласными, с применением сглаживания переходов и фильтрации для уменьшения эха.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `intervals` — входной параметр `intervals`.
- `speed_factor` — коэффициент или доля преобразования.
- `cutoff_freq` — частота или последовательность частот, Гц.

**Возвращает:** `numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд.

#### `detect_vowel_boundaries_gradient`

```python
detect_vowel_boundaries_gradient(input_audio_file)
```

Обнаруживает указанные события или интервалы.

**Параметры:**

- `input_audio_file` — входные данные или путь к ним.

**Возвращает:** результат выражения `[] | common_intervals`.
