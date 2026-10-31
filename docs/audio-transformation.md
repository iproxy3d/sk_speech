# Преобразование аудио

Функции преобразования обычно возвращают новый массив и не изменяют входной `y`. Конкретная
сигнатура и формат результата указаны в API соответствующего модуля.

```python
import librosa
import soundfile as sf

y, sr = librosa.load("speech.wav", sr=None, mono=True)
```

## Фильтры

```python
from sk_speech import sk_filters

# Подавить компоненты ниже 100 Гц.
high_passed = sk_filters.apply_high_pass_filter(y, sr, cutoff=100)

# Оставить полосу 300–3400 Гц.
band_passed = sk_filters.apply_bandpass_filter(y, sr, lowcut=300, highcut=3400)
```

Оба метода используют фильтры Баттерворта 10-го порядка в форме SOS. Подробности: [API `sk_filters`](api/sk_filters.md).

## Изменение F0 и формант

```python
from sk_speech import sk_formants, sk_pitch

result = sk_pitch.change_pitch_shift_hz(y, sr, pitch_shift_hz=20)
result = sk_formants.change_formant_frequencies(
    result,
    sr,
    frequency_factors=[1.04, 1.03, 1.02, 1.01, 1.0],
)
```

`pitch_shift_hz=20` сдвигает целевой основной тон на 20 Гц. Пять множителей `frequency_factors` соответствуют F1–F5
и меняют резонансные области спектра.

## Скорость и громкость

```python
from sk_speech import sk_pitch, sk_volume

result = sk_pitch.change_audio_speed(y, sr, begin_speed=1.0, end_speed=1.15)
result = sk_volume.change_audio_volume(result, sr, volume_factor=1.2)
```

`change_audio_speed()` плавно меняет скорость от начала к концу записи. `change_audio_volume()` масштабирует
амплитуду и нормализует результат.

## Шумоподавление

```python
from sk_speech import sk_noise

result = sk_noise.noise_reduction_spectral_subtraction(
    y,
    sr,
    noise_profile_sec=0.5,
)
```

Метод оценивает шумовой спектр на начальном участке, вычитает его в частотной области и восстанавливает
сигнал. Подход предполагает, что начальный участок репрезентативен для шума всей записи.

## Сохранение и цепочки операций

```python
result = sk_filters.apply_high_pass_filter(y, sr, cutoff=80)
result = sk_pitch.change_pitch_shift_hz(result, sr, pitch_shift_hz=15)
result = sk_volume.change_audio_volume(result, sr, volume_factor=0.9)
sf.write("result.wav", result, sr)
```

После каждого этапа проверяйте амплитуду и число сэмплов: скоростные преобразования меняют длину
сигнала, а последовательные усиления могут вызвать клиппинг.
