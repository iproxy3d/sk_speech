# Калибровка и временные ряды

Калибровка заменяет универсальную «нулевую» точку на нейтральный профиль конкретного говорящего и
измерительной цепи. Профиль строится по эталонной записи нейтральной речи.

## Извлечение рядов

```python
from sk_speech import PitchConfig, PitchExtractor

extractor = PitchExtractor(
    PitchConfig(
        sample_rate=16_000,
        frame_step_s=0.01,
        pitch_floor_hz=50.0,
        pitch_ceiling_hz=800.0,
    )
)

neutral_track = extractor.from_file("neutral.wav")
current_track = extractor.from_file("current.wav")
```

Одинаковые параметры `PitchConfig` нужно использовать для эталона и текущей записи. Иначе отличия могут
быть вызваны самой конфигурацией анализа.

## Профиль нейтральной речи

```python
from sk_speech import calibrate_pitch

profile = calibrate_pitch(neutral_track)
profile.save("pitch_profile.json")

print(profile.mean_f0_hz)
print(profile.std_f0_hz)
print(profile.mean_intensity_db)
print(profile.std_intensity_db)
```

В расчёт F0 входят только озвученные кадры с конечными значениями. Интенсивность усредняется по
озвученным кадрам, если они есть; иначе используются все конечные значения.

## Нормализация текущей записи

```python
from sk_speech import PitchProfile, normalize_pitch

profile = PitchProfile.load("pitch_profile.json")
normalized = normalize_pitch(current_track, profile)

print(normalized.f0_relative)
print(normalized.f0_delta_hz)
print(normalized.intensity_delta_db)
```

- `f0_relative` — относительное отклонение: `(F0 - mean_f0_hz) / mean_f0_hz`;
- `f0_delta_hz` — разность текущего F0 и среднего F0 в герцах;
- `intensity_delta_db` — разность текущей и средней интенсивности в децибелах;
- `voiced` — маска кадров, для которых F0 можно интерпретировать.

## Экспорт в CSV

```python
neutral_track.to_csv("neutral_features.csv")
current_track.to_csv("current_features.csv")
normalized.to_csv("normalized_features.csv")
```

При объединении рядов ориентируйтесь на `time_s`, а не на номер строки. Для эталона и рабочих записей используйте
один микрофон, расстояние, усиление и конфигурацию извлечения.

См. [API калибровки](api/pitch_calibration.md) и [API извлекателя](api/pitch_extractor.md).
