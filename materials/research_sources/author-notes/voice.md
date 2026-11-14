# Акустический профиль, просодия и синтез

[Все авторские заметки](README.md) · [Реестр утверждений](claims.tsv)

<a name="voice-profile-volume"></a>

## Изменение громкости по акустическому профилю

**Хронология.** 11.08.2024. Строки [1240–1246](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1240-L1246).

В тестах преобразования реальной речи автор сравнил сдвиг частот с их масштабированием. По результатам сравнения он выбрал масштабирование с автоматическим сдвигом и регулировкой амплитуды.

<a name="voice-profile-volume-trial"></a>

**`voice-profile-volume-trial`** · `observation` · `experiment_documented`

В выполненных тестах автор сопоставил `is_freq` и `is_f0_mul` и не заметил большой разницы между сдвигом и умножением частот. В том интерфейсе `is_f0_mul` воздействовал также на форманты. Выбранная комбинация изменяет положение, ширину и энергию полосы. В хронологии дано качественное сравнение вариантов.

Строки [1240–1244](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1240-L1244). [Комментарий Telegram](../catalog/acoustics.md#src-1241) · [change_speech()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_volume.py#L1772)

<a name="voice-profile-volume-calibration"></a>

**`voice-profile-volume-calibration`** · `research_question` · `open`

Открыта автоматическая оценка исходной громкости и силы эмоционального выражения. В момент записи эти параметры задавались вручную. Ошибка исходного уровня меняла глубину преобразования.

Строки [1246](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1246). [change_speech()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_volume.py#L1772) · [Галерея преобразований](../../../materials/README.md#%D0%B3%D1%80%D0%BE%D0%BC%D0%BA%D0%BE%D1%81%D1%82%D1%8C-%D0%B8-%D0%BF%D1%80%D0%B5%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE-%D1%8D%D1%82%D0%B0%D0%BB%D0%BE%D0%BD%D1%83)

**Материалы для повторения.** Исходная, эталонная и обработанная записи вместе с настройками тестов позволят сравнить варианты на слух и по спектру. Для отдельной оценки величины эффекта пригодятся одинаковая шкала уровней и метрика.

**Связанные материалы**

- Внешний код по исходному комментарию не получен. [Комментарий Telegram](../catalog/acoustics.md#src-1241).
- В текущей версии громкость и выраженность управляются отдельно. Сигнатура относится к этой ревизии. [change_speech()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_volume.py#L1772).
- Демонстрации простой регулировки и работы с эталоном. [Галерея преобразований](../../../materials/README.md#%D0%B3%D1%80%D0%BE%D0%BC%D0%BA%D0%BE%D1%81%D1%82%D1%8C-%D0%B8-%D0%BF%D1%80%D0%B5%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE-%D1%8D%D1%82%D0%B0%D0%BB%D0%BE%D0%BD%D1%83).

<a name="formants-volume-linear"></a>

## Линейные зависимости от уровня громкости

**Хронология.** 17–18.07.2024. Строки [853–884](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L853-L884).

В экспорт включены черновые модели и перечень операций для преобразования голоса. Происхождение развёрнутых пояснений по одному TXT установить нельзя.

<a name="formants-volume-linear-linear"></a>

**`formants-volume-linear-linear`** · `heuristic` · `missing_material`

Громкость нормируют переменной $V$ от 0 для нормальной речи до 1 для самой громкой. Для формант по гласным предложены линейные зависимости. Среди других кандидатов упомянуты амплитуда, усиление эквалайзера, искажения, реверберация и гармоническое возбуждение. Коэффициенты остались на изображениях.

Строки [853–862](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L853-L862).

<a name="formants-volume-linear-energy"></a>

**`formants-volume-linear-energy`** · `heuristic` · `unverified`

Вставка записывает $E\sim A^2f^2$ и вводит условную энергию речи $E_0(1+k)\,O_2/100$, где $O_2$ задан в процентах от максимума. Единицы и смысл амплитуды $A$ в первой формуле не определены. Для цифрового аудио меру энергии нужно задать через величину сигнала, окно и калибровку.

Строки [863–877](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L863-L877).

<a name="formants-volume-linear-pipeline"></a>

**`formants-volume-linear-pipeline`** · `procedure` · `proposal`

В кратком списке операций указаны фильтрация шума, усиление областей F0 и F1–F5, сдвиг F1–F5 при необходимости и компрессия динамического диапазона.

Строки [878–884](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L878-L884).

**Для дальнейшего исследования.** Нужны 5 и 9 фото из сообщений 853 и 860, таблицы параметров по гласным, нейтральные и громкие повторы тех же фраз. Для линейной модели проверить остатки и перенос между дикторами.

**Иллюстрации из хронологии.** [853](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L853) (5 фото), [860](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L860) (9 фото).

**Связанные материалы**

- Связанная реализация изменения громкости. [change_speech_volume()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_volume.py#L275).
- Продолжение обсуждения. [Профиль и автоматическая калибровка](voice.md#voice-profile-volume).

<a name="formant-pattern-observations"></a>

## Изменение F3 в профессиональной озвучке

**Хронология.** 06.08.2024. Строки [1075–1087](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1075-L1087).

Анализ профессиональной озвучки выявил эпизоды выраженного изменения F3. Автор отметил их в таблицах по записям и сопоставил с изменениями F0 и различиями эмоциональной подачи.

<a name="formant-pattern-observations-tables"></a>

**`formant-pattern-observations-tables`** · `observation` · `experiment_documented`

В результатах анализа профессиональной озвучки автор выделил цветом случаи выраженного сдвига F3. Стрелки в таблицах показывали выраженность изменений F0 и F3. На рассмотренном материале автор также отметил различимость страха. Численные величины и количество примеров можно будет сопоставить с таблицами при их добавлении.

Строки [1075–1083](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1075-L1083).

<a name="formant-pattern-observations-f3"></a>

**`formant-pattern-observations-f3`** · `hypothesis` · `unverified`

Предложено проверить, отражает ли F3 интенсивность выражения при разных знаках эмоциональной окраски. Отдельно поставлен вопрос о сближении формант. Гипотеза допускает влияние артикуляции и гласной.

Строки [1076–1087](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1076-L1087).

**Материалы для повторения.** Таблицы из строки 1082 покажут выделенные реплики и направление изменений. Записи и параметры измерения формант позволят повторить анализ и оценить перенос между гласными и дикторами.

**Иллюстрации из хронологии.** [1082](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1082) (2 фото).

**Связанные материалы**

- Учебная точка входа по измерению F0. [Учебный материал о F0](../catalog/acoustics.md#src-0346).
- Соседние наблюдения и внешний эксперимент. [Контур F0 и эмоциональная просодия](voice.md#affective-pitch-contour).

<a name="neutral-f0-amplitude"></a>

## Оценка отклонения от нейтрального голоса

**Хронология.** 15.08.2024. Строки [1273–1274](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1273-L1274).

Проектные варианты оценки двух координат акустического профиля относительно нейтральной речи.

<a name="neutral-f0-amplitude-f0"></a>

**`neutral-f0-amplitude-f0`** · `heuristic` · `proposal`

Для оценки выраженности предложено сравнивать максимум F0 с нейтральной речью того же диктора. Среди вариантов указаны минимум, среднее, максимум либо их сочетание. В записи встречаются 170–340 Гц без достаточного пояснения, являются ли это границами F0 или примером изменения.

Строки [1273](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1273). [PitchExtractor.extract()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/pitch/extractor.py#L78)

<a name="neutral-f0-amplitude-amplitude"></a>

**`neutral-f0-amplitude-amplitude`** · `heuristic` · `proposal`

Громкость предложено оценивать через среднюю амплитуду основной гармоники или среднюю амплитуду формантных областей.

Строки [1274](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1274). [calculate_speech_volume()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_volume.py#L621)

**Для дальнейшего исследования.** Нужны нейтральные образцы того же диктора, явная шкала, маска звонких участков и раздельная проверка влияния усиления, расстояния до микрофона и клиппинга.

**Связанные материалы**

- Получение контура F0. [PitchExtractor.extract()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/pitch/extractor.py#L78).
- Смежная оценка по частотам и амплитудам. [calculate_speech_volume()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_volume.py#L621).

<a name="affective-pitch-contour"></a>

## Контур F0, волнение и воспринимаемая эмоция

**Хронология.** 06–10.08.2024. Строки [1140–1152](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1140-L1152), [1173–1191](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1173-L1191), [1215–1239](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1215-L1239).

Автор просмотрел результаты измерения F0 и заметил сильное повышение тона в части примеров страха, радости и любопытства. Затем сопоставил собственные наблюдения с экспериментом на синтезированных гласных.

<a name="affective-pitch-contour-pitch-observation"></a>

**`affective-pitch-contour-pitch-observation`** · `observation` · `experiment_documented`

При просмотре измерений F0 автор отметил сильное повышение на примерах страха, радости и любопытства. В примерах ряда других эмоций он описал более низкий тон и отдельно отметил, что волнение могло изменить направление наблюдаемого эффекта.

Строки [1141–1152](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1141-L1152).

<a name="affective-pitch-contour-pitch"></a>

**`affective-pitch-contour-pitch`** · `hypothesis` · `unverified`

На основе этих измерений автор предложил интерпретировать направление изменения F0 через волнение, спокойствие и напористость. Проверка обобщения требует сравнения внутри диктора и учёта степени возбуждения.

Строки [1140–1152](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1140-L1152).

<a name="affective-pitch-contour-stimuli"></a>

**`affective-pitch-contour-stimuli`** · `external_summary` · `source_checked`

У Xu и Chuenwattanapranithi слушатели оценивали синтезированные гласные. В одном условии движению модели гортани сопутствовал квазилинейный сдвиг F0 примерно на 5 Гц от 106 Гц. Совместное понижение чаще воспринималось как гнев, совместное повышение — как радость. Это результат по конкретным стимулам.

Строки [1173–1184](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1173-L1184). [Xu и Chuenwattanapranithi](../catalog/prosody.md#src-1173) · [Полный текст на сайте UCL](https://www.homepages.ucl.ac.uk/~uclyyix/yispapers/Xu_Chuenwattanapranithi_ICPhS2007.pdf)

<a name="affective-pitch-contour-features"></a>

**`affective-pitch-contour-features`** · `research_question` · `open`

Автор спрашивает, брать ли контур по гласным или по всем звонким участкам. Упомянут медианный фильтр как вариант сглаживания перед анализом тренда, точный источник этого варианта не указан.

Строки [1186–1191](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1186-L1191).

<a name="affective-pitch-contour-bandwidth"></a>

**`affective-pitch-contour-bandwidth`** · `hypothesis` · `unverified`

Ширина частотной полосы предложена как возможный признак различения страха и радости. В соседних сообщениях обсуждается ускорение или замедление речи и частота модуляции F0. Эти идеи можно проверять независимо.

Строки [1215–1239](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L1215-L1239).

**Материалы для повторения.** Исходные записи и контуры F0 позволят повторить сравнение по репликам. Для оценки переносимости нужны одинаковый фонетический контекст, независимые оценки эмоции и сравнение внутри диктора.

**Связанные материалы**

- Карточка исследования. [Xu и Chuenwattanapranithi](../catalog/prosody.md#src-1173).
- Описание стимула и результатов. [Полный текст на сайте UCL](https://www.homepages.ucl.ac.uk/~uclyyix/yispapers/Xu_Chuenwattanapranithi_ICPhS2007.pdf).
- Отдельная гипотеза о формантном признаке. [Сдвиги F3](voice.md#formant-pattern-observations).

<a name="two-speech-modes-synthesis"></a>

## Переключение речевого режима в синтезе

**Хронология.** Дата фрагмента не указана. Строки [3220–3252](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3220-L3252).

В черновике выделены две цели высказывания. При передаче информации просодия выделяет смысловые части, при передаче состояния ритм и темп могут варьироваться сильнее.

<a name="two-speech-modes-synthesis-modes"></a>

**`two-speech-modes-synthesis-modes`** · `hypothesis` · `unverified`

В условно «монологическом» режиме автор предполагает большую устойчивость на протяжении выдоха и иллюстрирует расстановку акцентов схемой 1–23. В условно «диалогическом» режиме предполагается более выраженная вариативность. Обсуждение лобных долей, лимбической системы и кортизола служит авторским объяснением.

Строки [3220–3242](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3220-L3242).

<a name="two-speech-modes-synthesis-switch"></a>

**`two-speech-modes-synthesis-switch`** · `heuristic` · `proposal`

Для синтеза предлагается оценить эмоцию и её силу по тексту, затем сравнить с индивидуальным порогом для этой эмоции. Для одной фразы приведены реализации с выделенным словом «фрукт» и с паузами и растяжением звуков.

Строки [3243–3252](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3243-L3252).

**Для дальнейшего исследования.** Нужны независимо размеченные формат общения, коммуникативная задача и сила выражения, а также оценки естественности, смысла и распознаваемости эмоции при разных порогах.

**Связанные материалы**

- Поисковая текстовая копия. [Авторский документ «Два типа речи»](../../../materials/research_sources/snapshots/%D0%B4%D0%B2%D0%B0%20%D1%82%D0%B8%D0%BF%D0%B0%20%D1%80%D0%B5%D1%87%D0%B8.extracted.md).
- Родственная модель речевых режимов. [Формулировка и доступное время выдоха](breathing.md#expiration-and-phrase-choice).

<a name="phoneme-formant-transitions"></a>

## Переходы F1 и F2 на примере слова «слон»

**Хронология.** 26.11.2024. Строки [3140–3216](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3140-L3216).

Дополнительный пример хронологии о применении траекторий частоты, полосы и энергии для поиска границ звуков.

<a name="phoneme-formant-transitions-example"></a>

**`phoneme-formant-transitions-example`** · `heuristic` · `unverified`

На «с» запись выделяет шумовую полосу, на «л» — более концентрированную энергию, на «о» — рост F1 и падение F2, на переходе к «н» — изменение энергии и рост F2. Для «л» приведены ориентиры F1 300–400 Гц и F2 1000–1400 Гц, для «о» — 500–600 и 800–1000 Гц соответственно. В шумовом «с» оценку спектрального максимума нужно пометить отдельно от резонанса гласного.

Строки [3140–3216](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3140-L3216).

**Для дальнейшего исследования.** Нужны WAV, разметка границ фонем, параметры LPC или спектрального трекера и повторы слова у разных дикторов. Числа в обсуждении приведены как ориентиры.

**Связанные материалы**

- Смежный способ поиска границ гласных. [detect_vowel_boundaries_gradient()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_vowels.py#L1225).
