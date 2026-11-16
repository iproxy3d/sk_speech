
# Этап 5 — связи корпуса с кодом и итоговая навигационная приёмка

**Дата:** 16.11.2026. **Ветка:** `docs/research-sources-stage4`. Требования: [PLAN.md §5](PLAN.md#этап-5-связать-корпус-с-кодом-и-проверить-навигацию). **Состояние: все четыре пункта этапа 5 выполнены как проверка навигации, реестра и наличия кода**. GitHub Actions **не запускались**; все коммиты содержат `[skip ci]`.

## 5.1. Пять маршрутов «задача → API/код → источники → заметки»

Создан [task-routes.md](task-routes.md) и краткая [таблица маршрутов в README](README.md#быстрые-маршруты-от-задачи-к-реализации-и-исследованиям).

| Маршрут | Проверенный символ / файл | API | Авторские и внешние основания | Статус |
| --- | --- | --- | --- | --- |
| [R01 — F0 и F1–F5](task-routes.md#route-r01) | [`PitchExtractor.from_file`](../../src/sk_speech/pitch/extractor.py), [`sk_formants.get_formant_info`](../../src/sk_speech/sk_formants.py), [`get_formant_frequency_by_index`](../../src/sk_speech/sk_formants.py) | [Извлекатель](../../docs/api/pitch_extractor.md), [форманты](../../docs/api/sk_formants.md) | [voice.md](author-notes/voice.md#phoneme-formant-transitions); [Praat/Pitch](catalog/acoustics.md#src-0360) | Код/документация найдены; результаты внешних работ не приписаны реализации |
| [R02 — нейтральный профиль](task-routes.md#route-r02) | [`calibrate_pitch`, `normalize_pitch`](../../src/sk_speech/pitch/calibration.py), `PitchProfile` | [Калибровка](../../docs/api/pitch_calibration.md) | [Нейтральный профиль](author-notes/voice.md#neutral-f0-amplitude), [просодия](catalog/prosody.md#src-0402) | Реальные функции найдены; семантическая эмоция ими не распознаётся |
| [R03 — дыхательные паузы](task-routes.md#route-r03) | [`silence_percentage`](../../src/sk_speech/sk_detection.py), [`Respiratory`](../../src/sk_speech/regulators.py) | [Детекция](../../docs/api/sk_detection.md), [регуляторы](../../docs/api/regulators.md) | [Анализ реальных пауз](author-notes/breathing.md#pause-clustering), [стресс и речь](catalog/prosody.md#src-0076) | Различены доля тишины и фактическое обнаружение вдоха; готовый детектор вдохов **не найден** |
| [R04 — длительность и WSOLA](task-routes.md#route-r04) | [`sk_vowels.wsola`, `stretch_vowels_preserve_pitch`](../../src/sk_speech/sk_vowels.py), [`change_audio_speed`](../../src/sk_speech/sk_pitch.py) | [Гласные](../../docs/api/sk_vowels.md) | [PyTSMod](catalog/acoustics.md#src-3659), [ProMo](catalog/acoustics.md#src-0337), [градиенты](author-notes/gradients.md) | Аналоги не выданы за историческое происхождение конкретного кода |
| [R05 — гамматон/ERB](task-routes.md#route-r05) | [`adjust_center_frequencies_limited`, `apply_erb_filterbank`, `combine_filtered_signals`](../../src/sk_speech/sk_gammatone.py) | [Фильтрбанк](../../docs/api/sk_gammatone.md) | [Фильтрбанк, src-1350](catalog/hearing.md#src-1350), [исследовательские тесты](author-notes/gradients.md#gammatone-cluster-comparison) | Код найден; прирост точности ASR без независимого benchmark не заявлен |

**Проверка степени связи:** **существует код/символ** ≠ **алгоритм независимо воспроизведён на исторических WAV** ≠ **научная работа доказывает результат конкретной реализации**. Для [«Шестислойной модели»](author-documents/six-layer-model/review.md#engineering-411) готовая архитектура FFN/Mamba/HysteresisResidual в `src/sk_speech` не подтверждена; примерный код внутри рисунков DOCX нельзя объявлять кодом установленного пакета.

## 5.2. Точки входа и полнота смежных маршрутов

- [Оглавление документации](../../docs/README.md) ссылается на задачи и источники. Также обновлены четыре тематические страницы: [анализ аудио](../../docs/audio-analysis.md), [калибровка](../../docs/calibration-and-timeseries.md), [преобразование](../../docs/audio-transformation.md), [дыхание и голосообразование](../../docs/physiological-modeling.md).
- [Галерея материалов](../README.md) теперь **называет корпус с HTML, первоисточниками и редакторскими разборами**, а не просто будущую заготовку базы знаний, и ведёт в [маршруты задач](task-routes.md).
- [README корпуса](README.md) содержит таблицу R01–R05, а [каталог источников](catalog/README.md) и [оглавление авторских заметок](author-notes/README.md) — перекрёстные входы.
- **Все девять** тематических страниц `catalog/{acoustics,breath,prosody,hearing,synthesis,phonetics,bio,neuro,other}.md` связаны **со всеми восемью соседними темами**, с [API-маршрутами](task-routes.md) и [авторскими заметками](author-notes/README.md).

## 5.3. Проверка реестра, ссылок, оригиналов и упаковки

Проверены таблицы `catalog/sources.tsv`, `source-occurrences.tsv`, `history-urls.tsv`, `history-attachments.tsv` и 9 каталогов Markdown. При учёте суффиксов `src-3889-1`/`src-3889-2`:

| Проверка | Результат |
| --- | --- |
| Карточки `## src-...` | **476**, уникальных **476**, дублей **0** |
| Реестр `sources.tsv` | **476** строк, уникальных ID **476**, у каждой строки карточка совпадает с `source_id` |
| `source-occurrences.tsv` | **503** вхождения, потерянных ID/ссылок на свою карточку **0** |
| `history-urls.tsv` | **503** записи |
| `history-attachments.tsv` | **62** записи |
| Тематические страницы | **9/9** связаны с другими темами |
| Новые центральные страницы (маршруты, 2 README, каталог README, заметки README, docs README) | **273** Markdown-ссылки в сумме, **0** отсутствующих относительных файлов/директорий; отдельно карточки и якоря источников, использованные в 26 переходах R01–R05, существуют |
| Исходные оригиналы | **4/4** файла сверены с зарегистрированным Git blob SHA-1 и размером по дереву Git; поля SHA-256 в [манифесте](manifest.json) **не менялись** |

**Публикуемые файлы не являются данными пакета:** в [pyproject.toml](../../pyproject.toml) поиск модулей ограничен `src/`, а `package-data` — `sk_speech/data/**/*.json`, `data/**/*.wav`, `py.typed`. В [MANIFEST.in](../../MANIFEST.in) добавлено **`prune materials/research_sources`** для явного исключения исследовательского архива из исходного дистрибутива. **Готовые wheel/sdist в этом запуске не собирались**, поэтому результат описан как проверка конфигурации, не как инструментальная инспекция собранных архивов.

**Оговорка про навигацию:** проверено существование локальных относительных файлов по дереву GitHub; это не имитация запуска браузера, сборки Python-пакета или самостоятельной репликации акустических экспериментов. Отдельный **не закрытый** критерий офлайн-браузерной визуальной приёмки этапа [4.14](author-documents/stage-4.14-acceptance.md) **остаётся открытым** и не замаскирован статусом этапа 5.

## 5.4. Контрольные вопросы — ответы по существующим источникам

| Вопрос | Куда ведёт маршрут | Уровень проверки |
| --- | --- | --- |
| **Где реализована калибровка F0?** | [calibrate_pitch и normalize_pitch](../../src/sk_speech/pitch/calibration.py) → [API](../../docs/api/pitch_calibration.md) → [нейтральный эталон](../../docs/calibration-and-timeseries.md) | **Подтверждено по коду и документации** |
| **Какие работы мотивируют анализ пауз?** | [Стресс и речь](catalog/prosody.md#src-0076), [медленное дыхание](catalog/breath.md#src-0283), [длина фразы](catalog/prosody.md#src-3683) → [авторские реальные наблюдения](author-notes/breathing.md#pause-clustering) | **Исследовательский контекст**, причинная связь с конкретным кодом не доказана |
| **Что из шестислойной модели есть в коде?** | [Оригинальный HTML](author-documents/six-layer-model/index.html), [E01–E06](author-documents/six-layer-model/review.md#engineering-411), [формулы](author-documents/six-layer-model/formulas-search-4.14.md) | **Концепция и разбор есть; обучаемого шестислойного runtime в пакете нет** |
| **Где найти записи вокализаций для нового эксперимента?** | [Дельфин](catalog/bio.md#src-2800), [афалины WAV](catalog/bio.md#src-3380), [ESC-50](catalog/bio.md#src-3373), [NABat](catalog/bio.md#src-3499), [шимпанзе](catalog/bio.md#src-3508) | **Указатели на реальные источники**, лицензии/доступ к аудио проверять отдельно; источники **не объявлены историческими записями автора** |

Полные ответы и дополнительные соседние пути — [конец task-routes.md](task-routes.md#route-questions).

## 5.5. Итоговые ограничения и статус

**Все четыре задания этапа 5 по PLAN.md выполнены**: созданы маршруты, добавлены точки входа и смежные темы, проверены 476 ID и 503 URL-вхождения, связи с кодом/пакетными файлами, контрольные вопросы отсылают к конкретным источникам с квалификацией.

**Не заявлено:** исполнение GitHub Actions, построение wheel/sdist в CI, воспроизведение полного архива исследований, устранение математических проблем HysteresisResidual, самостоятельный пересчёт отсутствующих исторических WAV или офлайн-браузерная проверка из 4.14.

**Запуск закрыт**; следующая работа возможна отдельно, без автоматического продолжения.
