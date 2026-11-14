# Авторские заметки из истории диалогов

Заметки подготовлены по [исходной хронологии][history]. Ссылки на строки закреплены за ревизией `6347655`. Дата указана там, где её можно отнести к сообщению. Для комментариев и вставок с неясным авторством это отмечено в тексте.

Начать можно с [оценки дыхательной паузы](breathing.md#breath-pause-estimate), [изменения громкости по акустическому профилю](voice.md#voice-profile-volume) и [фазовых распределений градиентов](gradients.md#cross-species-acoustic-gradients).

[Реестр утверждений](claims.tsv) · [Указатель исходных фрагментов первого этапа](fragments.md) · [Реестр меток вложений](../catalog/history-attachments.tsv).

## [Дыхание, паузы и планирование фразы](breathing.md)

- [Оценка дыхательной паузы по соседним фразам](breathing.md#breath-pause-estimate)
- [Паузы при физической и психосоциальной нагрузке](breathing.md#stress-breathing-pause)
- [Связь просодии с ЧСС и ЧДД](breathing.md#prosody-physiology-mapping)
- [Модель суммарной альвеолы](breathing.md#equivalent-alveolus)
- [Условие дополнительного вдоха](breathing.md#oxygen-breath-trigger)
- [Периоды модуляции F0, дыхания и пульса](breathing.md#f0-heart-breath-periods)
- [Кластеризация коротких и длинных пауз](breathing.md#pause-clustering)
- [Длительность выдоха и выбор формулировки](breathing.md#expiration-and-phrase-choice)
- [Дерево пауз и ритмических границ](breathing.md#pause-hierarchy-graph)

## [Акустический профиль, просодия и синтез](voice.md)

- [Изменение громкости по акустическому профилю](voice.md#voice-profile-volume)
- [Линейные зависимости от уровня громкости](voice.md#formants-volume-linear)
- [Изменение F3 в профессиональной озвучке](voice.md#formant-pattern-observations)
- [Оценка отклонения от нейтрального голоса](voice.md#neutral-f0-amplitude)
- [Контур F0, волнение и воспринимаемая эмоция](voice.md#affective-pitch-contour)
- [Переключение речевого режима в синтезе](voice.md#two-speech-modes-synthesis)
- [Переходы F1 и F2 на примере слова «слон»](voice.md#phoneme-formant-transitions)

## [Градиенты частоты, гамматон и биоакустика](gradients.md)

- [Фазовые распределения градиентов в разнородных записях](gradients.md#cross-species-acoustic-gradients)
- [DBSCAN по частотному градиенту и длительности](gradients.md#dbscan-frequency-gradients)
- [Центры кластеров и гамматонные полосы](gradients.md#gammatone-cluster-comparison)
- [Распределения природных звуков и вокализаций](gradients.md#animal-sound-distributions)
- [Проверка трекера частоты на записи дельфина](gradients.md#dolphin-pitch-tracking)

## [Модели обработки и освоения речи](models.md)

- [Извлечение признаков и закономерностей в модели коры](models.md#cortical-feature-hierarchy)
- [Выравнивание просодии перед поиском самоподобия](models.md#prosody-normalization-fractal)
- [Звуковые паттерны и контекст отвращения](models.md#sound-patterns-disgust)
- [Внимание и переключение маршрутов обработки](models.md#attention-routing-analogy)
- [Предсказуемость фонем и порядок их освоения](models.md#phoneme-entropy-acquisition)

## Как читать статусы

Поле `statement_type` описывает происхождение или роль утверждения.

| Значение | Роль |
|---|---|
| `observation` | Наблюдение из диалога. |
| `calculation` | Численный расчёт или подстановка. |
| `procedure` | Описанный способ обработки или опыт. |
| `heuristic` | Рабочее правило или черновая модель. |
| `hypothesis` | Предположение, требующее проверки. |
| `analogy` | Сопоставление механизмов или представлений. |
| `external_summary` | Изложение содержания внешнего материала. |
| `dialogue_summary` | Изложение ответа собеседника или LLM. |
| `research_question` | Открытый исследовательский вопрос. |

Поле `evidence_status` фиксирует основание и объём проверки.

| Значение | Основание |
|---|---|
| `arithmetic_checked` | Повторена арифметика на значениях из TXT. |
| `source_checked` | Изложение сверено с указанным источником. |
| `partially_checked` | Подтверждена часть утверждения или его контекст. |
| `code_partial` | В указанной ревизии найдена часть описанной процедуры. |
| `reported` | Результат или процедура зафиксированы в TXT, данные для воспроизведения не приложены. |
| `missing_material` | Для чтения или повторения нужны отсутствующие материалы. |
| `proposal` | Параметры или правило предложены в хронологии. |
| `unverified` | Эмпирического подтверждения по доступным материалам нет. |
| `open` | Ответ или критерий ещё предстоит определить. |

В TSV поля `source_start` и `source_end` указывают на включительный диапазон строк оригинала. Поле `note` ведёт к утверждению, `related_sources` содержит ссылки на его основание или ближайший технический аналог. Для внешних источников объём проверки доступен в карточках каталога.

[history]: https://github.com/iproxy3d/sk_speech/blob/6347655391f1ab904dfd6f10f7b5a2a41c517c30/materials/research_sources/raw/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20-%20%D0%B2%D0%B5%D1%81%D1%8C%20%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D1%81%D1%8B%D0%BB%D0%BE%D0%BA%20%D0%B8%20%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9.txt
