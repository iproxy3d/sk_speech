# Модели данных временных рядов

[← К оглавлению API](../API.md)

Модуль: `sk_speech.pitch.models`.

Контейнеры исходных и нормализованных последовательностей.

## Класс `PitchTrack`

Покадровая последовательность времени, F0, интенсивности и признака озвученности вместе с метаданными записи.

```python
PitchTrack(time_s: np.ndarray, f0_hz: np.ndarray, intensity_db: np.ndarray, voiced: np.ndarray, sample_rate: int, frame_step_s: float, duration_s: float)
```

#### `PitchTrack.to_csv`

```python
to_csv(path: str | Path) -> Path
```

Записывает колонки `time_s`, `f0_hz`, `intensity_db` и `voiced` в CSV без зависимости от pandas.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `Path`.

## Класс `NormalizedPitchTrack`

Покадровые отклонения F0 и интенсивности относительно нейтрального профиля.

```python
NormalizedPitchTrack(time_s: np.ndarray, f0_relative: np.ndarray, f0_delta_hz: np.ndarray, intensity_delta_db: np.ndarray, voiced: np.ndarray)
```

#### `NormalizedPitchTrack.to_csv`

```python
to_csv(path: str | Path) -> Path
```

Записывает нормализованные отклонения F0 и интенсивности вместе с временем и маской озвученных кадров в CSV.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `Path`.
