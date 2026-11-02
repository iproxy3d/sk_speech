# С чего начать

![Какие характеристики можно извлекать из речевого сигнала](<../images/Акустический анализ речи_ множество измерений.png>)

*Концептуальная карта основных групп признаков. Графики и числа на
инфографике иллюстративны; точные результаты определяются входной записью и
параметрами анализа.*

## Требования

- Python 3.10 или новее;
- поддерживаются Windows и Linux;
- для анализа достаточно WAV-файла и базовой установки пакета.

## Установка из PyPI

Рекомендуется использовать отдельное виртуальное окружение.

```bash
python -m venv .venv
```

Активируйте его:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
source .venv/bin/activate
```

Установите опубликованный пакет:

```bash
python -m pip install --upgrade pip
python -m pip install sk-speech
```

Имя дистрибутива в PyPI содержит дефис — `sk-speech`, а имя импорта в
Python содержит подчёркивание — `sk_speech`.

Проверьте установку:

```bash
python -c "import sk_speech; print(sk_speech.__version__)"
```

Для дополнительных сценариев доступны extras:

```bash
# Зависимости расширенных примеров
python -m pip install "sk-speech[examples]"

# Нейросетевая оценка F0 методом PENN
python -m pip install "sk-speech[penn]"

# Сдвиг высоты тона через pyrubberband
python -m pip install "sk-speech[rubberband]"
```

Для изменения исходного кода, запуска тестов и примеров из репозитория:

```bash
git clone https://github.com/iproxy3d/sk_speech.git
cd sk_speech
python -m pip install -e ".[dev,examples]"
```

## Загрузка аудио

Большинство низкоуровневых функций принимает монофонический `numpy.ndarray` и частоту
дискретизации:

```python
import librosa

y, sr = librosa.load("speech.wav", sr=None, mono=True)
print(y.shape)
print(sr)
```

`sr=None` сохраняет исходную частоту дискретизации. Это важно для частотных расчётов.

## Первый анализ: F0 и интенсивность

```python
from sk_speech import PitchConfig, PitchExtractor

config = PitchConfig(
    sample_rate=16_000,
    frame_step_s=0.01,
    pitch_floor_hz=50.0,
    pitch_ceiling_hz=800.0,
)
track = PitchExtractor(config).from_file("speech.wav")

print(track.time_s)
print(track.f0_hz)
print(track.intensity_db)
print(track.voiced)
track.to_csv("pitch_features.csv")
```

- `time_s` — общая временная сетка;
- `f0_hz` — F0 в герцах, `NaN` для неозвученных кадров;
- `intensity_db` — широкополосная интенсивность Praat на той же сетке;
- `voiced` — логическая маска озвученных кадров.

Для обычной цифровой записи `intensity_db` — относительный уровень. Физический dB SPL требует
калибровки микрофона и всей измерительной цепи.

## Комплексный профиль

```python
import librosa
from sk_speech import sk_volume

y, sr = librosa.load("speech.wav", sr=None, mono=True)
profile = sk_volume.get_speech_params(y, sr)

print(profile["f0"])
print(profile["f1"])
print(profile["duration"])
print(profile["vowels"])
```

`get_speech_params()` объединяет расчёт F0, F1–F5, длительности, скорости, гласных и других
признаков. Расчёт затратнее извлечения одного признака. Для потоковой обработки включайте через
`options` только нужные признаки. См. [API `sk_volume`](api/sk_volume.md).

## Куда дальше

- [Анализ аудио](audio-analysis.md);
- [Преобразование аудио](audio-transformation.md);
- [Калибровка и временные ряды](calibration-and-timeseries.md);
- [Дыхание и голосообразование](physiological-modeling.md);
- [Оглавление API](API.md).
