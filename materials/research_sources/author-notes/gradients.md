# Градиенты частоты, гамматон и биоакустика

[Все авторские заметки](README.md) · [Реестр утверждений](claims.tsv)

<a name="cross-species-acoustic-gradients"></a>

## Фазовые распределения градиентов в разнородных записях

**Хронология.** Дата фрагмента не указана. Строки [4095–4100](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4095-L4100).

Автор измерял частотные пики и градиенты на реальных записях человеческой речи и вокализаций разных видов. На фазовых графиках получились визуально сходные крестообразные распределения при разных масштабах и положениях центра.

<a name="cross-species-acoustic-gradients-features"></a>

**`cross-species-acoustic-gradients-features`** · `procedure` · `experiment_documented`

В выполненном анализе автор вычислял градиент как разность частот соседних пиков, делённую на время между ними. Для частоты в герцах и интервала в секундах единица — Гц/с. Для речи в хронологии указаны F0 и форманты F1–F5. Для межвидового сравнения важно сохранять правило выделения сопоставимых спектральных пиков.

Строки [4095](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4095).

<a name="cross-species-acoustic-gradients-shape"></a>

**`cross-species-acoustic-gradients-shape`** · `observation` · `experiment_documented`

На полученных фазовых графиках автор наблюдал крестообразную форму с различиями в масштабе, положении центра и чёткости структуры. В перечне анализируемого материала фигурируют человек, птицы, пчёлы, муравьи, дельфины и сверчки. Сравнение формы было визуальным.

Строки [4096–4098](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4096-L4098).

<a name="cross-species-acoustic-gradients-entropy"></a>

**`cross-species-acoustic-gradients-entropy`** · `hypothesis` · `unverified`

Автор связывает сходство с возможным общим механизмом минимизации энтропии и предлагает аналогию с неокортексом и оптимизацией по Лагранжу. Функционал, ограничения и сравниваемые модели в этом фрагменте не заданы.

Строки [4099–4100](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L4099-L4100).

**Материалы для повторения.** Графики, перечень записей, частоты дискретизации и параметры поиска пиков позволят повторить анализ. Для проверки сходства количественно пригодятся метрика формы, сравнение исходных и нормированных координат и контрольные сигналы.

**Связанные материалы**

- Смежный алгоритм для анализа гласных вычисляет углы после масштабирования времени. В диалоге градиент задан как отношение разности частот ко времени. [calculate_peak_slopes()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_vowels.py#L1390).
- Кандидат для независимой проверки. [Корпус афалин](../catalog/bio.md#src-3380).
- Связанное представление сегментов. [DBSCAN градиентов](gradients.md#dbscan-frequency-gradients).

<a name="dbscan-frequency-gradients"></a>

## DBSCAN по частотному градиенту и длительности

**Хронология.** 05.11.2024. Строки [2955–2976](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2955-L2976).

Автор применил DBSCAN к сегментам аудио по двум признакам, частотному градиенту и длительности. Полученные группы рассмотрел на диаграмме рассеяния и гистограммах.

<a name="dbscan-frequency-gradients-plots"></a>

**`dbscan-frequency-gradients-plots`** · `procedure` · `experiment_documented`

На первом графике автор отобразил полученные метки DBSCAN в координатах «градиент частоты, длительность сегмента». На втором построил гистограмму градиентов по каждому кластеру. Высота столбца показывает число наблюдений в соответствующем диапазоне.

Строки [2955–2976](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2955-L2976).

**Материалы для повторения.** Для повторения понадобятся графики, аудио, таблица сегментов, масштабирование осей, `eps` и `min_samples`. При добавлении графиков полезно сохранить маркировку выбросов.

**Связанные материалы**

- Смежная сегментация по частотной динамике. [detect_vowel_boundaries_gradient()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_vowels.py#L1225).
- Градиенты в другой постановке. [Фазовые распределения](gradients.md#cross-species-acoustic-gradients).

<a name="gammatone-cluster-comparison"></a>

## Центры кластеров и гамматонные полосы

**Хронология.** 15.11.2024. Строки [2990–3056](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2990-L3056).

Автор сравнил частотные центры кластеров, полученных на музыкальной записи, с центрами гамматонного банка. В хронологии зафиксированы частоты, число наблюдений и корреляции для нескольких настроек.

<a name="gammatone-cluster-comparison-peaks"></a>

**`gammatone-cluster-comparison-peaks`** · `observation` · `experiment_documented`

По анализу музыкальной записи центры лежали примерно между 191 и 874 Гц. Для 191 Гц зафиксировано 2237 случаев, для 329 Гц — 3136, для 558 Гц — 3622. Частоты выше 740 Гц встречались редко. В исходном сравнении записаны семь нот, совпавших с центрами банка и корреляция около 0,87. Критерий совпадения в этом фрагменте не раскрыт.

Строки [2991–3014](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2991-L3014).

<a name="gammatone-cluster-comparison-configurations"></a>

**`gammatone-cluster-comparison-configurations`** · `observation` · `experiment_documented`

При других настройках автор получил 0,9042594882724244, 0,963260308274949 для 7 кластеров и 0,9624367423710899 для 5. Для отдельной серии с нерасшифрованным параметром от 70 до 260 записаны 0,95722, 0,95989, 0,96147, 0,96293, 0,98828, 0,98913, 0,98990, 0,99060, 0,99123 и 0,99181 соответственно при значениях 70, 100, 120, 140, 160, 180, 200, 220, 240, 260. Приведены округления до пяти знаков.

Строки [3018–3056](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3018-L3056).

<a name="gammatone-cluster-comparison-interpretation"></a>

**`gammatone-cluster-comparison-interpretation`** · `hypothesis` · `unverified`

Автор обсуждает, может ли соответствие отражать слуховую значимость центров. Для проверки нужна нулевая модель. Высокую корреляцию могут дать даже различные монотонно отсортированные частотные ряды.

Строки [2991–3028](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2991-L3028). [Документация гамматонограмм](../catalog/hearing.md#src-1351) · [apply_erb_filterbank()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_gammatone.py#L92)

**Материалы для повторения.** Графики из строк 3029, 3033 и 3045, входная запись, пары сравниваемых центров, параметры банка и расшифровка ряда 70–260 позволят повторить вычисления. Для проверки интерпретации можно сравнить результат с корреляцией на линейной и логарифмической сетках.

**Иллюстрации из хронологии.** [3029](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3029) (1 фото), [3033](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3033) (1 фото), [3045](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3045) (1 фото).

**Связанные материалы**

- Базовый метод. [Документация гамматонограмм](../catalog/hearing.md#src-1351).
- Смежный банк с настраиваемыми границами и числом полос. [apply_erb_filterbank()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_gammatone.py#L92).

<a name="animal-sound-distributions"></a>

## Распределения природных звуков и вокализаций

**Хронология.** 26.12.2024 для гипотезы о границах, дата сравнения не указана. Строки [3336–3339](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3336-L3339), [3344](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3344).

По анализу записей автор сравнил распределения для природных звуков и вокализаций нескольких групп животных.

<a name="animal-sound-distributions-comparison"></a>

**`animal-sound-distributions-comparison`** · `observation` · `experiment_documented`

В авторском сравнении проанализированные записи природных звуков оказались ближе к нормальному распределению. Летучие мыши и муравьи заняли промежуточное положение, синицы и крокодилы дали наибольшие отклонения. При расширении частотного диапазона различия усилились. Итог относится к рассмотренным записям.

Строки [3336–3339](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3336-L3339).

<a name="animal-sound-distributions-boundary"></a>

**`animal-sound-distributions-boundary`** · `hypothesis` · `unverified`

Для вокализаций морских животных автор предлагает искать функциональные границы по изменению тона, тембра и интенсивности даже без участков тишины. Сравнение с тональными языками используется как эвристическая аналогия.

Строки [3344](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3344).

**Материалы для повторения.** Для повторения сравнения можно приложить список записей, анализируемый признак, настройки частотной полосы, графики и выбранную меру отклонения от нормального распределения.

**Связанные материалы**

- Возможная контрольная выборка звуков среды. [ESC-50](../catalog/bio.md#src-3373).
- Корпус рукокрылых для независимого сравнения. [ChiroVox](../catalog/bio.md#src-3497).
- Корпус для проверки границ отдельных типов сигналов. [Размеченные записи афалин](../catalog/bio.md#src-3380).

<a name="dolphin-pitch-tracking"></a>

## Проверка трекера частоты на записи дельфина

**Хронология.** 19.10.2024. Строки [2799–2817](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2799-L2817).

В опыте с реальной подводной записью Praat не выделил ожидаемый тон. Автор попробовал замедлить запись вдвое и отметил этот шаг в хронологии.

<a name="dolphin-pitch-tracking-trial"></a>

**`dolphin-pitch-tracking-trial`** · `observation` · `experiment_documented`

При обработке записи дельфина Praat не определил ожидаемую частотную дорожку. Автор затем замедлил аудио в два раза. Текст сообщения обрывается после описания замедления, поэтому доступный результат относится к исходному запуску трекера.

Строки [2810–2817](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2810-L2817).

<a name="dolphin-pitch-tracking-analogy"></a>

**`dolphin-pitch-tracking-analogy`** · `analogy` · `unverified`

Сравнение механизмов звукоизвлечения с артикуляцией человека служит мотивацией поиска отслеживаемой частотной дорожки. Для свиста, щелчка и шумового фрагмента нужны отдельные правила измерения.

Строки [2812–2815](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2812-L2815).

**Материалы для повторения.** Изображения из строк 2802, 2807 и 2810, аудиофайл, способ замедления и границы поиска Praat позволят повторить опыт. При сравнении дорожек важно указать тип вокализации и исходную частоту дискретизации.

**Иллюстрации из хронологии.** [2802](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2802) (1 фото), [2807](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2807) (1 фото), [2810](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L2810) (1 фото).

**Связанные материалы**

- Ссылка из того же блока. Использование именно этой записи в расчёте не установлено. [Подводная запись SoundCloud](../catalog/bio.md#src-2800).
- Происхождение иллюстрации. [Сторонняя спектрограмма имитации тона](../catalog/bio.md#src-2806).
- Проверка трекера на независимом корпусе. [Размеченные записи афалин](../catalog/bio.md#src-3380).
