# Анализ аудио

Низкоуровневые функции получают массив сэмплов и частоту дискретизации. Не меняйте частоту
при загрузке, если это не требуется задачей:

```python
import librosa

y, sr = librosa.load("speech.wav", sr=None, mono=True)
```

## F0 и интенсивность

```python
from sk_speech import PitchExtractor

track = PitchExtractor().from_file("speech.wav")

for time_s, f0_hz, intensity_db, voiced in zip(
    track.time_s,
    track.f0_hz,
    track.intensity_db,
    track.voiced,
):
    print(time_s, f0_hz, intensity_db, voiced)
```

F0 есть только для озвученных кадров. Интенсивность извлекается для всей записи и интерполируется
на общую временную сетку. Модуль [`sk_pitch`](api/sk_pitch.md) дополнительно извлекает ширину полосы, энергию,
амплитуду, наклон, периодичность, ритм и тембр.

## Форманты F1–F5

```python
from sk_speech import sk_formants

formants = sk_formants.get_formant_info(y, sr)
for index in range(1, 6):
    frequency = sk_formants.get_formant_frequency_by_index(
        y,
        sr,
        formant_index=index,
        formants=formants,
    )
    print(f"F{index}: {frequency:.1f} Гц")
```

Передавайте уже рассчитанный `formants` в другие функции этого модуля. Это избавляет от повторного
извлечения Praat при расчёте частот, полос, энергии и амплитуд тех же формант.

## Границы и типы гласных

```python
from sk_speech import sk_vowels

vowels = sk_vowels.detect_vowel_boundaries(y, sr, threshold=0.1)
for start, end, vowel_type in vowels:
    print(start, end, vowel_type)
```

Это эвристическое выделение. Порог зависит от микрофона, помещения и говорящего; его нужно подбирать на
размеченных примерах целевой задачи.

## Шум

```python
from sk_speech import sk_noise

report = sk_noise.analyze_noise_level(y, sr)
print(report)
```

Отчёт объединяет RMS, спектральную плоскость и спектральную плотность мощности. Пороги каждой метрики нужно
калибровать на целевых записях.

## Режим речи

```python
from sk_speech import sk_detection

print("quiet:", sk_detection.is_soft_speech(y, sr))
print("loud:", sk_detection.is_loud_speech(y, sr))
print("whisper:", sk_detection.is_whisper(y, sr))
print("scream:", sk_detection.is_scream(y, sr))
```

Эти функции реализуют акустические эвристики, а не универсальную классификацию. Их пороги нужно проверять
и настраивать под свою измерительную цепь.

## Комплексный профиль

Если нужен набор связанных признаков, используйте `sk_volume.get_speech_params()`. Если нужен один показатель,
вызывайте специализированную функцию напрямую: это снижает число повторных расчётов.

Подробные сигнатуры и форматы возврата смотрите в [оглавлении API](API.md).
