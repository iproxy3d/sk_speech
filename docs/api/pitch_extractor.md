# Покадровое извлечение F0 и интенсивности

[← К оглавлению API](../API.md)

Модуль: `sk_speech.pitch.extractor`.

Высокоуровневое извлечение синхронизированных временных рядов через Praat.

## Класс `PitchConfig`

Параметры покадрового извлечения F0 и широкополосной интенсивности средствами Praat.

```python
PitchConfig(sample_rate: int | None = 16000, frame_step_s: float = 0.01, pitch_floor_hz: float = 50.0, pitch_ceiling_hz: float = 800.0, minimum_voiced_frames: int = 1)
```

## Класс `PitchExtractor`

Извлекает из файла или массива аудиосэмплов синхронизированные последовательности F0, интенсивности и маску озвученных кадров.

```python
PitchExtractor(config: PitchConfig | None=None)
```

#### `PitchExtractor.from_file`

```python
from_file(path: str | Path) -> PitchTrack
```

Читает аудиофайл через `soundfile` и передаёт полученный сигнал в покадровый извлекатель.

**Параметры:**

- `path` (`str | Path`) — путь к файлу.

**Возвращает:** `PitchTrack`.

#### `PitchExtractor.extract`

```python
extract(signal: np.ndarray, sample_rate: int) -> PitchTrack
```

Преобразует сигнал в моно, при необходимости меняет частоту дискретизации, извлекает F0 и интенсивность Praat и выравнивает их на общей временной сетке.

**Параметры:**

- `signal` (`np.ndarray`) — одномерный аудиосигнал `numpy.ndarray`.
- `sample_rate` (`int`) — частота дискретизации, Гц.

**Возвращает:** `PitchTrack`.
