# Шум

[← К оглавлению API](../API.md)

Модуль: `sk_speech.sk_noise`.

Оценка шума, спектральная плоскость, PSD и несколько вариантов шумоподавления.

## Функции

#### `normalize`

```python
normalize(value, min_val, max_val)
```

Линейно переводит значение из диапазона `[min_val, max_val]` в диапазон `[0, 1]`.

**Параметры:**

- `value` — входные данные соответствующего метода.
- `min_val` — нижняя граница исходного диапазона.
- `max_val` — верхняя граница исходного диапазона.

**Возвращает:** `float` — значение, линейно приведённое к диапазону от 0 до 1.

#### `compute_rms`

```python
compute_rms(y, frame_length=2048, hop_length=512)
```

Рассчитывает покадровое среднеквадратичное значение амплитуды сигнала.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** `numpy.ndarray` — покадровые среднеквадратичные амплитуды.

#### `compute_spectral_flatness`

```python
compute_spectral_flatness(y, frame_length=2048, hop_length=512)
```

Рассчитывает покадровую спектральную плоскость: отношение геометрического среднего спектра к арифметическому.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `frame_length` — длина кадра в сэмплах или секундах согласно функции.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** `numpy.ndarray` — покадровые значения спектральной плоскости.

#### `compute_power_spectral_density`

```python
compute_power_spectral_density(y, sr, n_fft=2048, hop_length=512)
```

Оценивает спектральную плотность мощности и возвращает соответствующие частотные координаты.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `n_fft` — размер окна быстрого преобразования Фурье, сэмплы.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** `tuple[numpy.ndarray, numpy.ndarray]` — частотная сетка и оценка спектральной плотности мощности.

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

Объединяет RMS, спектральную плоскость и PSD в один словарь показателей шума и пороговых решений.

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

Оценивает шумовой спектр выбранным методом и вычитает его из спектра сигнала перед обратным STFT.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `n_fft` — размер окна быстрого преобразования Фурье, сэмплы.
- `hop_length` — шаг между кадрами, сэмплы.
- `noise_estimation_method` — способ оценки шумового спектра.

**Возвращает:** результат выражения `enhanced_y`.

#### `spectral_subtraction2`

```python
spectral_subtraction2(y, sr, noise_psd, n_fft=2048, hop_length=512)
```

Выполняет спектральное вычитание с заранее переданным шумовым PSD.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_psd` — заранее оценённая спектральная плотность мощности шума.
- `n_fft` — размер окна быстрого преобразования Фурье, сэмплы.
- `hop_length` — шаг между кадрами, сэмплы.

**Возвращает:** результат выражения `enhanced_y`.

#### `estimate_noise_psd`

```python
estimate_noise_psd(y, sr, frame_length=2048, hop_length=512)
```

Оценивает шумовой PSD по кадрам с наименьшей энергией.

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

Анализирует уровень и признаки наличия шума и возвращает рассчитанные показатели. Это вариант алгоритма №2 с отдельной реализацией.

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

Выполняет ускоренное итеративное спектральное вычитание, оценивая шум по начальному участку записи.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_profile_sec` — длительность начального участка для оценки шума, с.
- `num_iterations` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `None | y_denoised`.

#### `noise_reduction_spectral_subtraction`

```python
noise_reduction_spectral_subtraction(y, sr, noise_profile_sec=0.5, num_iterations=2, high_pass=False, low_pass=False, normalize=False, target_dBFS=-20.0)
```

Выполняет настраиваемое итеративное спектральное вычитание с дополнительными ФВЧ, ФНЧ и нормализацией.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `noise_profile_sec` — длительность начального участка для оценки шума, с.
- `num_iterations` — коэффициент или доля преобразования.
- `high_pass` — включить фильтр верхних частот.
- `low_pass` — включить фильтр нижних частот.
- `normalize` — включить нормализацию результата.
- `target_dBFS` — целевой средний цифровой уровень, dBFS.

**Возвращает:** результат выражения `y_denoised`.

#### `apply_noise_reduction`

```python
apply_noise_reduction(y, noise_reduction_factor=0.3)
```

Реализует простой шумовой затвор: обнуляет сэмплы, амплитуда которых ниже доли от максимума.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `noise_reduction_factor` — коэффициент или доля преобразования.

**Возвращает:** результат выражения `y_reduced_noise`.

#### `add_noise`

```python
add_noise(y, noise_amplitude=0.005)
```

Добавляет к сигналу белый гауссов шум заданной амплитуды.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `noise_amplitude` — амплитуда или коэффициент амплитуды.

**Возвращает:** результат выражения `y_noisy`.

#### `remove_noise`

```python
remove_noise(y, sr, method='lowpass', **kwargs)
```

Нормализует сигнал и применяет выбранный фильтр: ФНЧ, ФВЧ, медианный или скользящее среднее.

**Параметры:**

- `y` — одномерный аудиосигнал `numpy.ndarray`.
- `sr` — частота дискретизации, Гц.
- `method` — имя выбираемого алгоритма.
- `kwargs` — дополнительные именованные параметры выбранного алгоритма.

**Возвращает:** `numpy.ndarray` — новый аудиосигнал после описанного преобразования.
