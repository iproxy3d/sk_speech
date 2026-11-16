
# Маршруты по задачам: исследование → код → источники → проверки

Постоянная точка входа из [каталога архива](README.md), [документации](../../docs/README.md) и [галереи материалов](../README.md). Все пути здесь относительны каталогу `materials/research_sources/`. Связь с источником означает **исследовательский контекст или технический аналог**, а **не доказательство**, что конкретная внешняя работа была использована при написании кода. В исходной хронологии есть отдельно отмеченные реальные тесты и гипотезы; повторная репликация не подразумевается.

<a id="route-r01"></a>
## R01 — Извлечь F0, интенсивность и форманты F1–F5

**Куда идти:** [анализ аудио](../../docs/audio-analysis.md) → [PitchExtractor](../../docs/api/pitch_extractor.md), [PitchTrack](../../docs/api/pitch_models.md) → [sk_pitch](../../docs/api/sk_pitch.md), [sk_formants](../../docs/api/sk_formants.md) → [каталог измерений](catalog/acoustics.md) и [заметка о F1/F2](author-notes/voice.md#phoneme-formant-transitions).

**Подтверждённые символы Python:** `PitchExtractor.from_file()`, `PitchExtractor.extract()` в [src/sk_speech/pitch/extractor.py](../../src/sk_speech/pitch/extractor.py); `sk_formants.get_formant_info()`, `sk_formants.get_formant_frequency_by_index()` в [src/sk_speech/sk_formants.py](../../src/sk_speech/sk_formants.py); также `sk_pitch.extract_f0()` в [src/sk_speech/sk_pitch.py](../../src/sk_speech/sk_pitch.py). Используйте единое `sample_rate` и контролируйте озвученные кадры. **F0 ≠ F1–F5**: основная частота голосового тона — не форманта резонатора.

**Внешние источники для сравнения методов (не подтверждённое происхождение реализации):** [Praat vs YAAPT/YIN, src-0360](catalog/acoustics.md#src-0360), [введение в F0, src-0346](catalog/acoustics.md#src-0346), [Praat форманты Python, src-0725](catalog/acoustics.md#src-0725), [formant grid, src-0839](catalog/acoustics.md#src-0839).

**Степень проверки:** функция и документация есть в ветке; научные результаты разных методов требуют сопоставления на одинаковых записях. [Связанный анализ голосовых режимов](author-documents/two-types-of-speech/review.md).

<a id="route-r02"></a>
## R02 — Построить нейтральный профиль и оценить отклонения

**Куда идти:** [практическая калибровка](../../docs/calibration-and-timeseries.md) → [PitchProfile / calibrate_pitch / normalize_pitch](../../docs/api/pitch_calibration.md) → [код калибровки](../../src/sk_speech/pitch/calibration.py) и [структуры модели](../../src/sk_speech/pitch/models.py) → [заметка о нейтральном профиле](author-notes/voice.md#neutral-f0-amplitude).

**Подтверждённый контракт:** `calibrate_pitch(PitchTrack) -> PitchProfile`; `normalize_pitch(PitchTrack, PitchProfile) -> NormalizedPitchTrack`; `PitchProfile.save()`/`load()`. `f0_relative = (F0 - mean_f0_hz)/mean_f0_hz`; `f0_delta_hz` и `intensity_delta_db` имеют свои единицы. Нейтральный эталон привязан к **говорящему, микрофону, условиям записи и конфигурации**.

**Смежные источники:** [F0 в эмоциональной речи, src-0402](catalog/prosody.md#src-0402), [эмоции и положение формант, src-0495](catalog/prosody.md#src-0495), [эффект отрицательных эмоций, src-0499](catalog/prosody.md#src-0499), [авторское изменение профиля](author-notes/voice.md#voice-profile-volume).

**Степень проверки:** код нейтрального профиля реализован и описан; **автоматического определения семантической эмоции** по этим нормировкам нет. Воспринимаемая эмоция — отдельная задача, см. [просодию](catalog/prosody.md).

<a id="route-r03"></a>
## R03 — Найти паузы и исследовать дыхательный ритм

**Куда идти:** [дыхательная модель](../../docs/physiological-modeling.md) → [эвристики и доля тишины](../../docs/api/sk_detection.md), [Respiratory](../../docs/api/regulators.md) → [код детекции](../../src/sk_speech/sk_detection.py), [регулятор](../../src/sk_speech/regulators.py) → [авторские исследования пауз](author-notes/breathing.md#breath-pause-estimate), [выполненная кластеризация пауз](author-notes/breathing.md#pause-clustering), [дерево пауз](author-notes/breathing.md#pause-hierarchy-graph).

**Что есть:** `sk_detection.silence_percentage(y, sr, threshold_db=-30)` вычисляет **долю тихих кадров**, а не полноценные временные границы вдохов; `Respiratory` — **модель** дыхательных состояний, а не обученный детектор физиологических вдохов в WAV. Исторический анализ коротких/длинных пауз документирован в заметке; его нельзя выдавать за полностью воспроизводимый `sk_speech.detect_breath_pauses()`, которого здесь нет.

**Релевантные работы:** [психосоциальный стресс и речь, src-0076](catalog/prosody.md#src-0076), [медленное дыхание, src-0283](catalog/breath.md#src-0283), [связь мозга и дыхания, src-1171](catalog/breath.md#src-1171), [прогноз длины фразы и просодия, src-3683](catalog/prosody.md#src-3683). Связанный [авторский DOCX «Два типа речи»](author-documents/two-types-of-speech/index.html).

**Степень проверки:** исходные авторские измерения описаны; **тождество «тишина = вдох» не установлено**. Для нового опыта нужны совместные метки вдоха, пауз, выдохов, громкости, F0 и слов.

<a id="route-r04"></a>
## R04 — Изменить длительность гласных, темп речи и сравнить WSOLA

**Куда идти:** [преобразование аудио](../../docs/audio-transformation.md), [sk_vowels API](../../docs/api/sk_vowels.md), [практическое видео и схемы](../README.md) → [sk_vowels.wsola и stretch_vowels_preserve_pitch*](../../src/sk_speech/sk_vowels.py), [sk_pitch.change_audio_speed](../../src/sk_speech/sk_pitch.py) → [авторский анализ градиентов](author-notes/gradients.md#dbscan-frequency-gradients), [наблюдения о переходах F1/F2](author-notes/voice.md#phoneme-formant-transitions).

**Подтверждённые символы:** `sk_vowels.detect_vowel_boundaries()`, `sk_vowels.wsola()`, `sk_vowels.stretch_vowels_preserve_pitch()` (и варианты `*2…*7`), `sk_pitch.change_audio_speed()`. Изменение времени **меняет число сэмплов** и требует контроля переходных областей и артефактов.

**Внешние технические аналоги:** [ProMo — высота и длительность, src-0337](catalog/acoustics.md#src-0337), [PyTSMod / WSOLA, src-3659](catalog/acoustics.md#src-3659), [примеры PyTSMod, src-3665](catalog/acoustics.md#src-3665). Присутствие похожих алгоритмов в каталоге **не является доказательством общего кода**; качество надо сравнивать на одинаковых записях.

**Степень проверки:** функции описаны в коде, но их качество не доказано универсальным бенчмарком. Концепция «растягивать устойчивые участки сильнее переходов» — исследовательская гипотеза.

<a id="route-r05"></a>
## R05 — Провести гамматонную / ERB-фильтрацию

**Куда идти:** [API фильтрации](../../docs/api/sk_gammatone.md), [практический видеоразбор](../README.md), [слуховой каталог](catalog/hearing.md) → [sk_gammatone.py](../../src/sk_speech/sk_gammatone.py) → [реальные авторские тесты по сравнению кластеров](author-notes/gradients.md#gammatone-cluster-comparison).

**Подтверждённые функции:** `adjust_center_frequencies_limited()`, `apply_erb_filterbank()`, `combine_filtered_signals()` и `filter_center_frequencies()`. Гамматонный/ERB банк используется для анализа частотных каналов; центральные частоты могут корректироваться по F0/формантам. Не называть его обученным универсальным шумоподавителем или готовым ASR.

**Внешние технические аналоги:** [gammatone-граммы, src-1350](catalog/hearing.md#src-1350), [эффективная реализация, src-1352](catalog/hearing.md#src-1352), [обучаемый банк, src-1415](catalog/hearing.md#src-1415), [сравнение слуховых представлений, src-1416](catalog/hearing.md#src-1416).

**Степень проверки:** функции существуют; [видео демонстрирует изменение спектра](../README.md#гамматонная-фильтрация), но **увеличение точности ASR** таким фильтром в репозитории не подтверждено контрольным бенчмарком.

## Смежные исследовательские направления

| Направление | Исследование, код и степень проверки |
| --- | --- |
| **Эмоциональная интонация, шёпот и крик** | [Просодия](catalog/prosody.md), [голосовые заметки](author-notes/voice.md#affective-pitch-contour), [sk_detection](../../docs/api/sk_detection.md); эвристики требуют настройки порогов |
| **Дыхание и физиология** | [История пауз](author-notes/breathing.md), [Respiratory](../../docs/api/regulators.md), [каталог дыхания](catalog/breath.md); физиологическая модель не медицинская диагностика |
| **Фонетика и происхождение языка** | [Форма1: HTML](author-documents/forma1/index.html), [обсуждение F01–F20](author-documents/forma1/review.md), [фонетические публикации](catalog/phonetics.md); гипотезы не доказаны их перечислением |
| **Сравнительная биоакустика** | [внешние вокализации и корпуса](catalog/bio.md), [графики межвидового сравнения](author-documents/six-layer-model/gradient-records-4.13.md), [заметка о дельфине](author-notes/gradients.md#dolphin-pitch-tracking); исторические WAV не идентифицированы до записи |
| **Нейрокортикальная шестислойная модель** | [авторская HTML-статья](author-documents/six-layer-model/index.html), [инженерный аудит](author-documents/six-layer-model/review.md#engineering-411), [математический аудит](author-documents/six-layer-model/review.md#math-412), [нейроисточники](catalog/neuro.md); **нейросеть на FFN/Mamba/HysteresisResidual не реализована как runtime пакета** |
| **Синтез и голосовые агенты** | [каталог синтеза](catalog/synthesis.md), [практические преобразования](../../docs/audio-transformation.md); пакет не заменяет TTS |
| **История исследовательских тестов** | [исходная хронология](<raw/История - весь список ссылок и описаний.txt>), [карточки ссылок](catalog/history.md), [научные утверждения](author-notes/claims.tsv); только часть гипотез верифицирована независимыми данными |

<a id="route-questions"></a>
## Проверка навигации на четырёх контрольных вопросах

**Где реализована калибровка F0?** [pitch/calibration.py](../../src/sk_speech/pitch/calibration.py), функции `calibrate_pitch`/`normalize_pitch`; [API](../../docs/api/pitch_calibration.md), [нейтральный профиль в документации](../../docs/calibration-and-timeseries.md), [авторская заметка](author-notes/voice.md#neutral-f0-amplitude). **Код подтверждён**.

**Какие работы мотивируют анализ пауз?** [Обзор влияния стресса на речь, src-0076](catalog/prosody.md#src-0076), [дыхательная физиология, src-0283](catalog/breath.md#src-0283), [просодия/длина фразы, src-3683](catalog/prosody.md#src-3683) и [авторский анализ пауз](author-notes/breathing.md#pause-clustering). Это **мотивация и контекст**, а не доказательство, что конкретный DOI был использован в реализационных коммитах.

**Что из «Шестислойной модели» есть в коде?** Отдельные примитивы извлечения акустики, FFN/гистерезиса как класс **не реализованы** в `src/sk_speech`. Подробности: [E01–E06](author-documents/six-layer-model/review.md#engineering-411), [математическая ошибка исходных формул](author-documents/six-layer-model/review.md#math-412-open), [поисковая транскрипция формул](author-documents/six-layer-model/formulas-search-4.14.md). **Реализация модели не подтверждена**.

**Где найти записи вокализаций для нового эксперимента?** [Реальная запись дельфина, src-2800](catalog/bio.md#src-2800), [корпус афалин, src-3380](catalog/bio.md#src-3380), [ESC-50, src-3373](catalog/bio.md#src-3373), [NABat, src-3499](catalog/bio.md#src-3499), [архив шимпанзе, src-3508](catalog/bio.md#src-3508). Проверьте лицензии, частоту дискретизации, способ отбора и формантную применимость; **новые корпуса не следует выдавать за оригинальные исторические WAV**. Полный [акт проверки происхождения аудио](author-documents/six-layer-model/gradient-records-4.13.md#4-конкретные-ссылки-на-записи-что-найдено).

---
[Весь каталог карточек](catalog/README.md) · [Авторские заметки](author-notes/README.md) · [Индекс исходных DOCX](README.md) · [Документация пакета](../../docs/README.md)
