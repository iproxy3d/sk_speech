# Исторический реестр исходных блоков этапа 4

> В этом файле сохранены результаты первичной инвентаризации DOCX; для чтения текста использовать [три Markdown-издания](../README.md#каталог-документов). Оригинальные DOCX удалены из текущей ветки.

[Журнал и границы пакетов](progress.md) · [Манифест оригиналов](../manifest.json)

## Как найти блок в оригинале

`Bnnn` — порядковый номер дочернего элемента `w:body` в `word/document.xml`, начиная с 1. Пустые абзацы и таблицы учитываются. Завершающий `w:sectPr` пропускается. Текст и таблицы открывайте по номеру блока. Изображения перечислены в порядке появления, включая вложенные в таблицу. Имя файла берётся из связи `word/_rels/document.xml.rels`. Блоки с изображением и без текста остаются в диапазонах пакетов.

После удаления DOCX исследуемые блоки доступны прямо в Markdown по якорям `Bnnn`. Например, [B001 «Происхождение речи и языка»](speech-language-origins/README.md#B001), [B019](speech-language-origins/README.md#B019). Историческая нумерация Word сохранена для совместимости протоколов, но повторно извлечь OOXML из текущего дерева нельзя. Архивная исходная ревизия: `c2980b7bb116e1a3bd048bac64b8e39c33417b8d`.

## Два типа речи

Три абзаца с Word-стилем заголовка: B097 «Роль ритма и темпа» (уровень 3), B099 «Монологическая речь» и B102 «Диалогическая речь» (уровень 4). Ниже приведены более широкие диапазоны для чтения.

| Блоки | Раздел или смежные блоки |
| --- | --- |
| B001–B034 | Монолог и диалог, дыхание и ритм речи |
| B035–B067 | ЧСС, ЧДД и когнитивный контроль |
| B068–B112 | Два режима синтеза, примеры интонации и акценты |
| B113–B136 | Эмоциональная выраженность, громкость и контекст |
| B137–B215 | Авторский разбор исследования Сбера и заключение |

| Изображение | Блок | Связь | Файл в DOCX |
| ---: | --- | --- | --- |
| 1 | B002 | `rId5` | `word/media/image1.png` |
| 2 | B008 | `rId6` | `word/media/image2.png` |
| 3 | B018 | `rId7` | `word/media/image3.png` |
| 4 | B028 | `rId8` | `word/media/image4.png` |
| 5 | B039 | `rId9` | `word/media/image5.png` |
| 6 | B042 | `rId10` | `word/media/image6.jpeg` |
| 7 | B048 | `rId11` | `word/media/image7.jpeg` |
| 8 | B068 | `rId12` | `word/media/image8.png` |
| 9 | B080 | `rId13` | `word/media/image9.png` |
| 10 | B126 | `rId14` | `word/media/image10.png` |
| 11 | B128 | `rId15` | `word/media/image11.png` |
| 12 | B131 | `rId16` | `word/media/image12.png` |

Таблиц в DOCX нет. Из 12 файлов 10 PNG и два JPEG. Повторных ссылок на изображения и одинаковых файлов по контрольной сумме нет.

## Происхождение речи и языка

В 694 блоках 602 непустых текстовых абзаца. Встроенных изображений и таблиц нет. Тематические переходы в обычных абзацах и пунктах списка отмечены в [пакетах F01–F20](progress.md#происхождение-речи-и-языка--пакеты-45-и-46).

## Шестислойная модель

Границы 17 смежных разделов указаны в [пакетах S01–S17](progress.md#шестислойная-модель--пакеты-переноса-48). Единственный абзац со стилем заголовка — B118 «Реализация модуляции» (уровень 4). В остальных разделах границы выделены по тексту и форматированию оригинала.

| Изображение | Блок | Связь | Файл в DOCX |
| ---: | --- | --- | --- |
| 1 | B001 | `rId8` | `word/media/image1.png` |
| 2 | B004 | `rId9` | `word/media/image2.png` |
| 3 | B010 | `rId10` | `word/media/image3.png` |
| 4 | B016 | `rId11` | `word/media/image4.png` |
| 5 | B019 | `rId12` | `word/media/image5.png` |
| 6 | B027 | `rId13` | `word/media/image6.png` |
| 7 | B032 | `rId14` | `word/media/image7.png` |
| 8 | B035 | `rId15` | `word/media/image8.png` |
| 9 | B037 | `rId16` | `word/media/image9.png` |
| 10 | B040 | `rId17` | `word/media/image10.png` |
| 11 | B050 | `rId18` | `word/media/image11.png` |
| 12 | B058 | `rId19` | `word/media/image12.png` |
| 13 | B062 | `rId20` | `word/media/image13.png` |
| 14 | B066 | `rId21` | `word/media/image14.png` |
| 15 | B079 | `rId22` | `word/media/image15.png` |
| 16 | B086 | `rId23` | `word/media/image16.png` |
| 17 | B088 | `rId24` | `word/media/image17.png` |
| 18 | B090 | `rId25` | `word/media/image18.png` |
| 19 | B091 | `rId26` | `word/media/image19.png` |
| 20 | B097 | `rId27` | `word/media/image20.png` |
| 21 | B104 | `rId28` | `word/media/image21.png` |
| 22 | B114 | `rId29` | `word/media/image22.png` |
| 23 | B120 | `rId30` | `word/media/image23.png` |
| 24 | B125 | `rId31` | `word/media/image24.png` |
| 25 | B135 | `rId32` | `word/media/image25.png` |
| 26 | B146 | `rId33` | `word/media/image26.png` |
| 27 | B164 | `rId34` | `word/media/image27.png` |
| 28 | B166 | `rId35` | `word/media/image28.png` |
| 29 | B176 | `rId36` | `word/media/image29.png` |
| 30 | B183 | `rId37` | `word/media/image30.png` |
| 31 | B208 | `rId38` | `word/media/image31.png` |
| 32 | B210 | `rId39` | `word/media/image32.png` |
| 33 | B212 | `rId40` | `word/media/image33.png` |
| 34 | B214 | `rId41` | `word/media/image34.png` |
| 35 | B216 | `rId42` | `word/media/image35.png` |
| 36 | B229 | `rId43` | `word/media/image36.png` |
| 37 | B237 | `rId44` | `word/media/image37.png` |
| 38 | B246 | `rId45` | `word/media/image38.png` |
| 39 | B250 | `rId46` | `word/media/image39.png` |
| 40 | B257 | `rId47` | `word/media/image40.png` |
| 41 | B265 | `rId48` | `word/media/image41.png` |
| 42 | B266 | `rId49` | `word/media/image42.png` |
| 43 | B267 | `rId50` | `word/media/image43.png` |
| 44 | B281 | `rId51` | `word/media/image44.png` |
| 45 | B286 | `rId52` | `word/media/image45.png` |
| 46 | B309 | `rId53` | `word/media/image46.png` |
| 47 | B311 | `rId54` | `word/media/image47.png` |
| 48 | B313 | `rId55` | `word/media/image48.png` |
| 49 | B314 | `rId56` | `word/media/image49.png` |
| 50 | B315 | `rId57` | `word/media/image50.png` |
| 51 | B316 | `rId58` | `word/media/image51.png` |
| 52 | B317 | `rId59` | `word/media/image52.png` |
| 53 | B322 | `rId60` | `word/media/image53.png` |
| 54 | B348 | `rId61` | `word/media/image54.png` |
| 55 | B377 | `rId62` | `word/media/image55.png` |
| 56 | B379 | `rId63` | `word/media/image56.png` |

Все 56 вложенных файлов — PNG. Повторных ссылок на изображения и одинаковых файлов по контрольной сумме нет. Изображение 1 вложено в титульную таблицу.

| Таблица | Блок | Размер | Содержание |
| ---: | --- | --- | --- |
| 1 | B001 | 1 строка × 2 ячейки | Титульные данные и изображение 1 |
| 2 | B192 | 6 строк × 2 столбца | Слой и функция в модели асимметрии |
| 3 | B200 | 4 строки × 3 столбца | Механизм, биологическая аналогия и назначение в модели |

Во всех трёх DOCX отсутствуют отдельные объекты формул OMML. В «Шестислойной модели» выражения есть в тексте, например B331 и B350, и требуют сверки записанных обозначений. Иллюстрации с формулами проверяются визуально на подэтапе 4.9.
