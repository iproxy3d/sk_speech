# Дыхание, паузы и планирование фразы

[Все авторские заметки](README.md) · [Реестр утверждений](claims.tsv)

<a name="breath-pause-estimate"></a>

## Оценка дыхательной паузы по соседним фразам

**Хронология.** 01.06.2024. Строки [9–40](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L9-L40).

Черновая эвристика для планирования времени вдоха по предыдущей и следующей фразам. Автор соотносит длительность речи с числом фонем, а ресурс для паузы выражает в условных словах.

<a name="breath-pause-estimate-rule"></a>

**`breath-pause-estimate-rule`** · `heuristic` · `proposal`

Для предыдущей фразы берут число условных слов $N$, для следующей — $M$. Токен длиной до трёх букв считают за полслова, более длинный — за одно. При выходе за предел семь условных слов фразу предлагают делить, сохраняя короткие грамматические элементы при соседнем слове. Формула в записи: $P=(7-M)\cdot0.24-(7-N)\cdot0.18$ с. Отдельно предложен множитель эмоции на границе предложений.

Строки [10–29](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L10-L29). [Respiratory.pause() и speech()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/regulators.py#L747)

<a name="breath-pause-estimate-example"></a>

**`breath-pause-estimate-example`** · `calculation` · `arithmetic_checked`

На одном фрагменте из временных меток получена пауза $18.270-17.800=0.470$ с. При $N=4$, $M=3$ формула даёт $0.420$ с, расхождение $0.050$ с. Вариант с одинаковым коэффициентом $2.4/11\approx0.218$ даёт $0.218$ с. В соседнем примере $7\cdot0.24=1.68$ с, хотя в записи округлённо указано 1,8 с.

Строки [29–40](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L29-L40).

**Для проверки.** Нужны исходный файл с отметками вдоха, согласованное соответствие фонем и условных слов, проверка на нескольких дикторах и правило на случай отрицательного $P$. Коэффициенты имеют смысл секунд на условное слово в первой формуле. Вариант с 0,218 переносит число из секунд на фонему.

**Связанные материалы**

- Смежная модель фаз дыхания. В этой ревизии pause() задаёт паузу по газовым параметрам, а тело speech() содержит только return. [Respiratory.pause() и speech()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/regulators.py#L747).
- Другая постановка с оценкой по аудио. [Кластеризация наблюдаемых пауз](breathing.md#pause-clustering).

<a name="stress-breathing-pause"></a>

## Паузы при физической и психосоциальной нагрузке

**Хронология.** Дата фрагмента не указана. Строки [76–94](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L76-L94).

В записи сопоставлены обсуждение акустических признаков стресса из публикации и авторское объяснение того, как прогноз вдоха мог бы влиять на размещение пауз.

<a name="stress-breathing-pause-paper"></a>

**`stress-breathing-pause-paper`** · `external_summary` · `source_checked`

Kappen и соавторы сравнили сети акустических признаков до и после лабораторной психосоциальной нагрузки. Структуры сетей были сходны, HNR занимало центральное положение, изменение jitter положительно связывалось с изменением самооценки негативного аффекта. Сдвиги F1/F2 и неудачное размещение пауз при физической нагрузке обсуждаются в обзоре литературы внутри статьи.

Строки [76–89](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L76-L89). [Kappen и соавторы](../catalog/prosody.md#src-0076)

<a name="stress-breathing-pause-forecast"></a>

**`stress-breathing-pause-forecast`** · `hypothesis` · `unverified`

Автор предполагает, что при подготовке фразы мозг грубо оценивает потребность во вдохе по словам. При стрессе приоритет быстрого сообщения может укорачивать паузы, а ошибка прогноза приводит к вдоху внутри синтаксической группы.

Строки [91–94](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L91-L94).

**Для проверки.** Нужны синхронная запись дыхания и речи, разметка синтаксических границ и сравнение задач с разной нагрузкой. Условия физической и психосоциальной нагрузки следует учитывать отдельно.

**Связанные материалы**

- Первоисточник пересказа. [Kappen и соавторы](../catalog/prosody.md#src-0076).
- Предшествующая эвристика. [Формула оценки паузы](breathing.md#breath-pause-estimate).

<a name="prosody-physiology-mapping"></a>

## Связь просодии с ЧСС и ЧДД

**Хронология.** 11.06.2024. Строки [172–217](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L172-L217).

Автор ищет наблюдаемые акустические признаки, которые можно было бы сопоставить с дыханием и кровообращением.

<a name="prosody-physiology-mapping-mapping"></a>

**`prosody-physiology-mapping-mapping`** · `hypothesis` · `unverified`

Первоначальная схема связывает тон с эмоцией, громкость с пульсом, скорость речи с частотой дыхания. В заметке от 6 августа появляется иной вариант связи ЧСС с тоном. Оба сохраняются как рабочие предположения.

Строки [172–178](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L172-L178).

<a name="prosody-physiology-mapping-ratio"></a>

**`prosody-physiology-mapping-ratio`** · `external_summary` · `partially_checked`

В записи индекс Хильдебрандта задан как $Q=\mathrm{ЧСС}/\mathrm{ЧДД}$ при измерении обеих частот за минуту. Выписаны диапазоны 2,9–4,8 и 2,8–4,9 из разных фрагментов. Ссылка на работу о ступенчатой физической нагрузке позволяет установить контекст, происхождение и применимость приведённых диапазонов к речи остаются открытыми.

Строки [204–212](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L204-L212). [Индекс Хильдебрандта у спортсменов](../catalog/breath.md#src-0216) · [Запись из «Успехов современной биологии»](../catalog/breath.md#src-0206)

**Для проверки.** Нужны синхронные аудио, кардиограмма или пульс и датчик дыхания, а также контроль темпа и усилия. Фото из сообщения на строке 214 нужно сопоставить с приложенной ссылкой.

**Метки вложений без файлов.** [214](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L214) (1 фото).

**Связанные материалы**

- Источник по физической нагрузке. [Индекс Хильдебрандта у спортсменов](../catalog/breath.md#src-0216).
- Карточка фиксирует ограничение доступа. [Запись из «Успехов современной биологии»](../catalog/breath.md#src-0206).
- Продолжение гипотезы. [Периоды ЧСС и ЧДД](breathing.md#f0-heart-breath-periods).

<a name="equivalent-alveolus"></a>

## Модель суммарной альвеолы

**Хронология.** 12.06.2024. Строки [226–245](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L226-L245).

Автор предлагает описать изменение объёма эквивалентной сферой и через радиус перейти от целевого объёма к оценке длительности вдоха.

<a name="equivalent-alveolus-model"></a>

**`equivalent-alveolus-model`** · `heuristic` · `missing_material`

Последовательность черновика: $V(r)$, затем зависимость $R(t)$, затем $R(V)$ для обратного расчёта времени. Записаны максимальный радиус 9,5 с неуказанной в тексте единицей и 7 с на надувание до предела по аналогии с шариком. Формулы из трёх изображений в TXT отсутствуют.

Строки [226–236](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L226-L236). [Течение газа](../catalog/breath.md#src-0243) · [Газовые законы](../catalog/breath.md#src-0244) · [Respiratory.calculate_V_t()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/regulators.py#L372)

<a name="equivalent-alveolus-examples"></a>

**`equivalent-alveolus-examples`** · `calculation` · `arithmetic_checked`

При условных 16 циклах в минуту получено $60/16=3.75$ с на цикл. Сохранены варианты 2 и 1,5 с, 1,8 и 1,34 с для вдоха и выдоха. Отдельно указана оценка 2 с для 500 см³. В записи не задан способ отнести остаток до 3,75 с к паузе или к иному режиму.

Строки [237–242](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L237-L242).

**Для проверки.** Нужны изображения с формулами, единица радиуса, зависимость потока или радиуса от времени и исходные измерения. Оценка для 500 см³ приведена как запись автора.

**Метки вложений без файлов.** [226](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L226) (1 фото), [229](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L229) (1 фото), [234](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L234) (1 фото).

**Связанные материалы**

- Смежная учебная справка. [Течение газа](../catalog/breath.md#src-0243).
- Смежная учебная справка. [Газовые законы](../catalog/breath.md#src-0244).
- В реализации объём вычисляется по радиусу сферы. Формулы с фото требуют собственной сверки. [Respiratory.calculate_V_t()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/regulators.py#L372).

<a name="oxygen-breath-trigger"></a>

## Условие дополнительного вдоха

**Хронология.** 09.07.2024. Строки [819–823](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L819-L823).

Черновой вариант учёта дополнительной паузы в синтезе речи при недостаточном ресурсе для произнесения фразы.

<a name="oxygen-breath-trigger-rule"></a>

**`oxygen-breath-trigger-rule`** · `heuristic` · `proposal`

Порог сравнивается с текущим условным количеством $O_2$. Он зависит от минимума для $N$ фонем и множителя стресса. При недостатке ресурса добавляют вдох, а его время включают в общую длительность и соответствующий участок тишины. Автор предлагает задавать требование фразы независимо от объёма лёгких.

Строки [819–823](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L819-L823).

**Для проверки.** В TXT отсутствуют единицы $O_2$, способ калибровки на фонему, шкала множителя и поведение на границе порога. Для инженерной проверки достаточно начать с явной единицы прокси ресурса и записи вдохов.

**Связанные материалы**

- Более ранний вариант оценки. [Эвристика по длинам фраз](breathing.md#breath-pause-estimate).

<a name="f0-heart-breath-periods"></a>

## Периоды модуляции F0, дыхания и пульса

**Хронология.** 26.11.2024. Строки [3113–3136](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3113-L3136).

Сопоставление характерных временных масштабов для моделирования движения контура F0. В записи рядом приведены определения темпа и ритма.

<a name="f0-heart-breath-periods-numbers"></a>

**`f0-heart-breath-periods-numbers`** · `calculation` · `arithmetic_checked`

Для иллюстративных 15 дыхательных циклов в минуту получается 4 с на цикл, для 70 ударов в минуту — около 0,857 с на удар. Эти числа вычислены как $60/r$. Измеренного периода F0 в этом сравнении нет.

Строки [3113–3117](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3113-L3117).

<a name="f0-heart-breath-periods-modulation"></a>

**`f0-heart-breath-periods-modulation`** · `hypothesis` · `unverified`

Предполагается, что при стрессе ЧСС может модулировать амплитуду либо период движения контура F0. В заметке период около 0,5 с приводится как пример возможной связи с тревожностью. Запись об экспериментах с естественностью синтеза и упомянутая работа 2009 года требуют точной идентификации.

Строки [3118–3124](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3118-L3124). [extract_pitch_rate()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_pitch.py#L2100) · [change_pitch_intonation_ex()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_pitch.py#L1682)

<a name="f0-heart-breath-periods-pigeon"></a>

**`f0-heart-breath-periods-pigeon`** · `observation` · `reported`

Для одной описанной проверки на материале голубя приведены интервалы 0,35 и 0,17 с и расчёт $60/150=0.4$ с по ориентиру ЧСС 140–160 уд/мин. Интервалы различаются. Источник аудио, привязка временных меток и синхронный пульс птицы не указаны.

Строки [3125–3130](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3125-L3130).

**Для проверки.** Измерять несущую F0, частоту движения её контура, кратковременный jitter и темп артикуляции как разные признаки. Для проверки нужны синхронные ряды, контрольные временные сдвиги и оценка связи внутри диктора.

**Связанные материалы**

- Инженерный анализ периода контура. [extract_pitch_rate()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_pitch.py#L2100).
- Период и амплитуда задаются при преобразовании. [change_pitch_intonation_ex()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/src/sk_speech/sk_pitch.py#L1682).

<a name="pause-clustering"></a>

## Кластеризация коротких и длинных пауз

**Хронология.** 09.01.2025. Строки [3397–3423](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3397-L3423).

Автор описывает анализ записей без транскрипции. При предобработке удаляется шум, аудио нормализуется, интервалы тишины определяются по уровню сигнала.

<a name="pause-clustering-procedure"></a>

**`pause-clustering-procedure`** · `procedure` · `code_partial`

В диалоге предложен k-means по длительности с $k=3$ и переходом на $k=2$ при нехватке данных. Значения больше 3000 мс для кластеризации заменяются максимальным значением ниже 3000 мс. После сортировки кластеров короткие паузы получают метку A, остальные — B. Подсчитывается число A между B. Паузы B могут обозначать дыхание, ожидание или границу мысли.

Строки [3397–3412](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3397-L3412). [find_word_boundaries()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/examples/test_pause.py#L412) · [Подсчёт внутренних пауз](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/examples/test_pause.py#L490)

<a name="pause-clustering-comparison"></a>

**`pause-clustering-comparison`** · `observation` · `reported`

Автор сообщает, что автоматический выбор числа кластеров и проверка границ слов через ASR дали худшие результаты. Приведён пример длительностей 23, 90, 200, 500 и 1000 мс. Размер выборки, версии ASR и метрика сравнения в этом фрагменте отсутствуют.

Строки [3415–3423](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3415-L3423).

**Для проверки.** Нужны WAV и разметка дыхательных событий и слов, правило перехода с трёх кластеров на два, версия кода и результаты сравнения. Число внутренних пауз и число слов имеют разные определения. Для непрерывной последовательности из $n$ слов с паузой на каждой внутренней границе ожидается $n-1$ пауз.

**Связанные материалы**

- Порог по уровню и короткие паузы между длинными есть. Ограничение длительности закомментировано, повторный запуск с k=2 в этой функции отсутствует. [find_word_boundaries()](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/examples/test_pause.py#L412).
- Возвращается количество коротких пауз. [Подсчёт внутренних пауз](https://github.com/iproxy3d/sk_speech/blob/15e96a4582fc922f77aef75c9f74247e9dba7b1a/examples/test_pause.py#L490).

<a name="expiration-and-phrase-choice"></a>

## Длительность выдоха и выбор формулировки

**Хронология.** 09.01.2025. Строки [3387–3396](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3387-L3396), [3424–3468](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3424-L3468).

Рабочая гипотеза о приспособлении длительности и лексики фразы к выдоху. В обсуждении сопоставлены информационная речь, эмоциональная речь и пение.

<a name="expiration-and-phrase-choice-wording"></a>

**`expiration-and-phrase-choice-wording`** · `hypothesis` · `unverified`

На условном примере 2,0 и 1,8 с одно сообщение о Маше и грибах предлагается произнести с иным порядком слов и близкими по смыслу глаголами. Автор допускает подбор слов, предлогов и пауз под доступное время. Пример иллюстрирует идею.

Строки [3387–3393](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3387-L3393).

<a name="expiration-and-phrase-choice-counts"></a>

**`expiration-and-phrase-choice-counts`** · `observation` · `reported`

Автор сообщает ориентир 3–4 слова на выдох и более редкие длинные цепочки. В обсуждении встречаются 7–10 и более 10 слов как ориентиры возможного снижения связности, с оговорками о возрасте, навыке, пении и заученных фразах. Экспорт не содержит проверяемого размера выборки, разметки выдохов и критерия связности.

Строки [3459–3467](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3459-L3467).

<a name="expiration-and-phrase-choice-temperature"></a>

**`expiration-and-phrase-choice-temperature`** · `analogy` · `unverified`

Сопоставление с температурой LLM относится к распределению вариантов формулировки. Автор прямо оговаривает различия механизма выбора и влияние ошибок планирования. В строках 3394–3396 находится вставка, похожая на ответ собеседника или LLM, с замечанием о том, что параметр температуры сам по себе не задаёт длительность синтеза.

Строки [3424–3457](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3424-L3457).

<a name="expiration-and-phrase-choice-memory"></a>

**`expiration-and-phrase-choice-memory`** · `external_summary` · `source_checked`

Коуэн обсуждает ёмкость кратковременного хранения в чанках, Миллер — ограничения обработки информации и группировку в чанки. Числа из этих работ сами по себе не устанавливают число слов за выдох, порог связности или сравнимую единицу в вокализациях животных.

Строки [3461–3468](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3461-L3468). [Коуэн, 2001](https://pubmed.ncbi.nlm.nih.gov/11515286/) · [Миллер, 1956](https://doi.org/10.1037/h0043158)

**Для проверки.** Нужны повторные записи одинаковых сообщений при разных измеренных длительностях выдоха, слепая оценка связности и контроль говорящего, задачи и темпа. Сначала проверить, в какой степени кластер B отражает реальный вдох.

**Связанные материалы**

- Предшествующий анализ. [Метод подсчёта пауз](breathing.md#pause-clustering).
- Публикация о кратковременной памяти. [Коуэн, 2001](https://pubmed.ncbi.nlm.nih.gov/11515286/).
- Публикация о ёмкости обработки информации. [Миллер, 1956](https://doi.org/10.1037/h0043158).

<a name="pause-hierarchy-graph"></a>

## Дерево пауз и ритмических границ

**Хронология.** Дата фрагмента не указана. Строки [3779–3782](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3779-L3782), [3685–3711](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3685-L3711), [3743–3776](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3743-L3776).

Гипотеза о представлении речевых границ деревом и использовании его при прогнозе следующего фрагмента.

<a name="pause-hierarchy-graph-tree"></a>

**`pause-hierarchy-graph-tree`** · `hypothesis` · `unverified`

Автор предлагает моделировать ритмические отношения пауз древовидным графом. Узлы можно трактовать как вложенные интервалы, если разметка языка и речи покажет воспроизводимую иерархию.

Строки [3779–3780](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3779-L3780).

<a name="pause-hierarchy-graph-evidence"></a>

**`pause-hierarchy-graph-evidence`** · `external_summary` · `source_checked`

Соседняя ссылка ведёт к Meliza и Margoliash. Они исследовали избирательность и терпимость к вариациям песенных мотивов в слуховой области скворцов. Это сравнительный контекст для слуховых объектов.

Строки [3782](https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt#L3782). [Исследование слуховых объектов у птиц](../catalog/hearing.md#src-2275)

**Для проверки.** Для оценки дерева нужны записи с границами слов и фраз, критерий уровней и сравнение с плоским порогом длительности. Обзор о корковых осцилляциях обсуждает временную организацию слуховой обработки, а эксперимент со смешанной речью — избирательное внимание.

**Связанные материалы**

- Источник из строки 3782. [Исследование слуховых объектов у птиц](../catalog/hearing.md#src-2275).
- Фон для временных масштабов. [Обзор о корковых осцилляциях](../catalog/hearing.md#src-3692).
- Контекст слухового внимания. [Mesgarani и Chang](../catalog/hearing.md#src-3759).
