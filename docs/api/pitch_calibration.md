# Калибровка F0 и интенсивности

[← К оглавлению API](../API.md)

Модуль: `sk_speech.pitch.calibration`.

Нейтральный профиль и относительные покадровые отклонения.

## Класс `PitchProfile`

Нейтральный профиль говорящего: средние и стандартные отклонения F0 и интенсивности, число озвученных кадров и шаг временной сетки.

```python
PitchProfile(mean_f0_hz: float, mean_intensity_db: float, std_f0_hz: float, std_intensity_db: float, voiced_frames: int, frame_step_s: float)
```

#### `PitchProfile.save`

```python
save(path: str | Path) -> Path
```

Сериализует нейтральный профиль в JSON, создавая родительские каталоги при необходимости.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `Path`.

#### `PitchProfile.load`

```python
load(path: str | Path) -> 'PitchProfile'
```

Читает JSON-профиль и восстанавливает объект `PitchProfile`.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `PitchProfile`.

## Функции

#### `calibrate_pitch`

```python
calibrate_pitch(track: PitchTrack) -> PitchProfile
```

Строит нейтральный профиль по озвученным кадрам эталонной записи: рассчитывает средние и стандартные отклонения F0 и интенсивности.

**Параметры:**

- `track` (`PitchTrack`) — объект `PitchTrack` с покадровыми F0 и интенсивностью.

**Возвращает:** `PitchProfile`.

#### `normalize_pitch`

```python
normalize_pitch(track: PitchTrack, profile: PitchProfile) -> NormalizedPitchTrack
```

Вычисляет для каждого кадра относительное отклонение F0 от нейтрального среднего, отклонение F0 в герцах и разность интенсивности в децибелах.

**Параметры:**

- `track` (`PitchTrack`) — объект `PitchTrack` с покадровыми F0 и интенсивностью.
- `profile` (`PitchProfile`) — объект нейтрального профиля `PitchProfile`.

**Возвращает:** `NormalizedPitchTrack`.
