# Градиенты частоты, гамматон и биоакустика

[Все авторские заметки](README.md) · [Реестр утверждений](claims.tsv)

<a name="cross-species-acoustic-gradients"></a>

## Фазовые распределения градиентов в разнородных записях

**Хронология.** Дата фрагмента не указана. Строки [4095–4100](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4095-L4100).

Автор описывает форму двумерного распределения частотных пиков и динамики между ними в записях человека, животных и насекомых.

<a name="cross-species-acoustic-gradients-features"></a>

**`cross-species-acoustic-gradients-features`** · `procedure` · `reported`

Градиент в записи — разность частотных пиков, делённая на интервал времени. Для частоты в герцах и времени в секундах единица — Гц/с. Автор указывает дорожки F0–F5. В применении к речи F0 обозначает основную частоту, F1–F5 обозначают форманты. Для других таксонов нужно явно указать соответствующие типы спектральных пиков.

Строки [4095](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4095).

<a name="cross-species-acoustic-gradients-shape"></a>

**`cross-species-acoustic-gradients-shape`** · `observation` · `reported`

Распределения описаны как визуально сходные, крестообразные, различающиеся масштабом, положением центра и выраженностью формы. В перечне примеров человек, птицы, пчёлы, муравьи, дельфины и сверчки. Указания на точные записи, размеры выборок и численную меру сходства в этом фрагменте отсутствуют.

Строки [4096–4098](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4096-L4098).

<a name="cross-species-acoustic-gradients-entropy"></a>

**`cross-species-acoustic-gradients-entropy`** · `hypothesis` · `unverified`

Автор связывает сходство с возможным общим механизмом минимизации энтропии и предлагает аналогию с неокортексом и оптимизацией по Лагранжу. Функционал, ограничения и сравниваемые модели в этом фрагменте не заданы.

Строки [4099–4100](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4099-L4100).

**Для проверки.** Нужны список и версии записей, частоты дискретизации, интервалы анализа, правило поиска и сопоставления пиков, сами графики и метрика сходства. Для проверки артефакта трекера пригодны синтетические сигналы и перемешанные траектории. Сопоставить исходные и нормированные координаты.

**Связанные материалы**

- Смежный алгоритм для анализа гласных вычисляет углы после масштабирования времени. В диалоге градиент задан как отношение разности частот ко времени. [calculate_peak_slopes()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_vowels.py#L1390).
- Кандидат для независимой проверки. [Корпус афалин](../catalog/bio.md#src-3380).
- Связанное представление сегментов. [DBSCAN градиентов](gradients.md#dbscan-frequency-gradients).

<a name="dbscan-frequency-gradients"></a>

## DBSCAN по частотному градиенту и длительности

**Хронология.** 05.11.2024. Строки [2955–2976](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2955-L2976).

Текст описывает два графика, использованные для чтения результатов кластеризации сегментов.

<a name="dbscan-frequency-gradients-plots"></a>

**`dbscan-frequency-gradients-plots`** · `procedure` · `reported`

Слева точка имеет координаты «градиент частоты, длительность сегмента», цвет и подпись относятся к метке DBSCAN. Справа для каждого кластера построена гистограмма частотных градиентов. Высота столбца соответствует числу попаданий. При восстановлении графика шумовые точки DBSCAN следует показывать отдельной меткой.

Строки [2955–2976](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2955-L2976).

**Для проверки.** Нужны оба графика, аудио, таблица границ сегментов, преобразование шкал двух осей, расстояние, `eps`, `min_samples` и доля выбросов. В TXT нет параметров DBSCAN и числа кластеров этого опыта.

**Связанные материалы**

- Смежная сегментация по частотной динамике. [detect_vowel_boundaries_gradient()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_vowels.py#L1225).
- Градиенты в другой постановке. [Фазовые распределения](gradients.md#cross-species-acoustic-gradients).

<a name="gammatone-cluster-comparison"></a>

## Центры кластеров и гамматонные полосы

**Хронология.** 15.11.2024. Строки [2990–3056](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2990-L3056).

Числовые записи о соответствии центров частотных кластеров и гамматонного банка. Рядом обсуждается мелодия Баха, название записи и правило подсчёта корреляции в этом диапазоне не заданы.

<a name="gammatone-cluster-comparison-peaks"></a>

**`gammatone-cluster-comparison-peaks`** · `observation` · `reported`

Центры приведены в диапазоне около 191–874 Гц, в том числе 191 Гц (2237 случаев), 329 Гц (3136) и 558 Гц (3622). Частоты выше 740 Гц описаны как редкие. В записи указаны 7 совпавших нот и корреляция около 0,87. Критерий совпадения не указан.

Строки [2991–3014](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2991-L3014).

<a name="gammatone-cluster-comparison-configurations"></a>

**`gammatone-cluster-comparison-configurations`** · `observation` · `missing_material`

Дополнительно указаны 0,9042594882724244, 0,963260308274949 для 7 кластеров и 0,9624367423710899 для 5. Для отдельной серии с нерасшифрованным параметром от 70 до 260 записаны 0,95722, 0,95989, 0,96147, 0,96293, 0,98828, 0,98913, 0,98990, 0,99060, 0,99123 и 0,99181 соответственно при значениях 70, 100, 120, 140, 160, 180, 200, 220, 240, 260. Приведены округления до пяти знаков.

Строки [3018–3056](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3018-L3056).

<a name="gammatone-cluster-comparison-interpretation"></a>

**`gammatone-cluster-comparison-interpretation`** · `hypothesis` · `unverified`

Автор обсуждает, может ли соответствие отражать слуховую значимость центров. Для проверки нужна нулевая модель. Высокую корреляцию могут дать даже различные монотонно отсортированные частотные ряды.

Строки [2991–3028](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2991-L3028). [Документация гамматонограмм](../catalog/hearing.md#src-1351) · [apply_erb_filterbank()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_gammatone.py#L92)

**Для проверки.** Нужны фотографии из строк 3029, 3033, 3045, входная запись, список центров, правило попарного соответствия, вид корреляции, смысл параметра 70–260 и параметры банка. Сравнить совпадения с линейной и логарифмической сетками на заданном диапазоне.

**Метки вложений без файлов.** [3029](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3029) (1 фото), [3033](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3033) (1 фото), [3045](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3045) (1 фото).

**Связанные материалы**

- Базовый метод. [Документация гамматонограмм](../catalog/hearing.md#src-1351).
- Смежный банк с настраиваемыми границами и числом полос. [apply_erb_filterbank()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_gammatone.py#L92).

<a name="animal-sound-distributions"></a>

## Распределения природных звуков и вокализаций

**Хронология.** 26.12.2024 для гипотезы о границах, дата сравнения не указана. Строки [3336–3339](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3336-L3339), [3344](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3344).

Хронология содержит краткое сравнение распределений природных звуков и вокализаций, затем предложение о признаках границы сигнала без тишины.

<a name="animal-sound-distributions-comparison"></a>

**`animal-sound-distributions-comparison`** · `observation` · `reported`

В записанном резюме природные звуки описаны как более близкие к нормальному распределению. Летучие мыши и муравьи отмечены как промежуточные, синицы и крокодилы — как наиболее отклоняющиеся. Расширение частотного диапазона связывается с усилением различий. Признак, критерий нормальности и исходная таблица не приведены.

Строки [3336–3339](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3336-L3339).

<a name="animal-sound-distributions-boundary"></a>

**`animal-sound-distributions-boundary`** · `hypothesis` · `unverified`

Для вокализаций морских животных автор предлагает искать функциональные границы по изменению тона, тембра и интенсивности даже без участков тишины. Сравнение с тональными языками используется как эвристическая аналогия.

Строки [3344](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3344).

**Для проверки.** Нужны записи с раздельной разметкой типов сигналов, одинаковая физическая полоса или контроль её влияния, критерий расстояния между распределениями и правила разметки границ.

**Связанные материалы**

- Возможная контрольная выборка звуков среды. [ESC-50](../catalog/bio.md#src-3373).
- Корпус рукокрылых для независимого сравнения. [ChiroVox](../catalog/bio.md#src-3497).
- Корпус для проверки границ отдельных типов сигналов. [Размеченные записи афалин](../catalog/bio.md#src-3380).

<a name="dolphin-pitch-tracking"></a>

## Проверка трекера частоты на записи дельфина

**Хронология.** 19.10.2024. Строки [2799–2817](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2799-L2817).

Дополнительный фрагмент о применении речевого трекера к подводной записи. Сообщению автора предшествуют описания сторонних иллюстраций и ссылка на аудио.

<a name="dolphin-pitch-tracking-trial"></a>

**`dolphin-pitch-tracking-trial`** · `observation` · `missing_material`

Автор сообщает, что Praat не определил ожидаемый тон в своей проверке, и указывает замедление аудио в два раза. Численный результат после замедления в TXT отсутствует, сообщение обрывается.

Строки [2810–2817](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2810-L2817).

<a name="dolphin-pitch-tracking-analogy"></a>

**`dolphin-pitch-tracking-analogy`** · `analogy` · `unverified`

Сравнение механизмов звукоизвлечения с артикуляцией человека служит мотивацией поиска отслеживаемой частотной дорожки. Для свиста, щелчка и шумового фрагмента нужны отдельные правила измерения.

Строки [2812–2815](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2812-L2815).

**Для проверки.** Нужны три фото из строк 2802, 2807 и 2810, аудиофайл, разрядность, исходная частота дискретизации, способ замедления, границы поиска Praat и разметка типа сигналов.

**Метки вложений без файлов.** [2802](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2802) (1 фото), [2807](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2807) (1 фото), [2810](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2810) (1 фото).

**Связанные материалы**

- Ссылка из того же блока. Использование именно этой записи в расчёте не установлено. [Подводная запись SoundCloud](../catalog/bio.md#src-2800).
- Происхождение иллюстрации. [Сторонняя спектрограмма имитации тона](../catalog/bio.md#src-2806).
- Проверка трекера на независимом корпусе. [Размеченные записи афалин](../catalog/bio.md#src-3380).
