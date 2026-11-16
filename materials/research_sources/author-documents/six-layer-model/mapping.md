# Соответствие DOCX → HTML: «Шестислойная модель»

**Статус: предварительный структурный реестр этапа 4.7.** Исходные 381 блока, 56 PNG и 3 таблицы сопоставлены по проверенному [инвентарю](../inventory.md#шестислойная-модель). Содержимое бинарного DOCX в этом запуске недоступно для извлечения: не выдавать эту структуру за сверенный перенос. Генератор `../extract_six_layer.py` предназначен для локального запуска с оригинальным DOCX и выдаёт полнотекстовый снимок, изображения и расширенную карту. Пакеты 4.8/4.9 остаются ожидающими ручной сверки.

| Пакет | Исходные блоки | HTML-секция | Назначение |
| --- | --- | --- | --- |
| S01 | B001–B019 | [#S01](index.html#S01) | Титульная таблица и классическая модель неокортекса |
| S02 | B020–B040 | [#S02](index.html#S02) | Формирование кластеров и связь слоёв 2 и 3 |
| S03 | B041–B063 | [#S03](index.html#S03) | Реализация слоёв 2 и 3: последовательные и пространственные признаки |
| S04 | B064–B079 | [#S04](index.html#S04) | Инженерная реализация кластеров в слоях 2 и 3 |
| S05 | B080–B104 | [#S05](index.html#S05) | Модуляция слоёв 2 и 3 сигналами других зон |
| S06 | B105–B124 | [#S06](index.html#S06) | Слой 5: обобщение, выбор сигнала и модуляция |
| S07 | B125–B145 | [#S07](index.html#S07) | Входы слоя 4 и локальная ошибка слоя 6 |
| S08 | B146–B163 | [#S08](index.html#S08) | Слой 1 и модулирующие обратные связи |
| S09 | B164–B181 | [#S09](index.html#S09) | Сопоставление с Transformer, FFN и Mamba |
| S10 | B182–B200 | [#S10](index.html#S10) | Иерархический гистерезис, асимметрия и таблицы механизмов |
| S11 | B201–B217 | [#S11](index.html#S11) | Архитектурная модель и схемы прохождения сигналов |
| S12 | B218–B255 | [#S12](index.html#S12) | Флуктуации, закон Вебера и биологические параллели |
| S13 | B256–B274 | [#S13](index.html#S13) | Фазовое пространство градиентов и иерархия пауз |
| S14 | B275–B309 | [#S14](index.html#S14) | Функции активации с флуктуациями |
| S15 | B310–B322 | [#S15](index.html#S15) | Контрастность и селективное усиление |
| S16 | B323–B357 | [#S16](index.html#S16) | Мембранная инерция и HysteresisResidual |
| S17 | B358–B381 | [#S17](index.html#S17) | Волновые свойства и пример амплитудного гистерезиса |

## Поштучные якоря

| Блок DOCX | Пакет | Якорь HTML | Объекты в блоке | Статус текста |
| --- | --- | --- | --- | --- |
| B001 | S01 | [#B001](index.html#B001) | Рис. 1, Табл. 1 | Ожидает извлечения из DOCX |
| B002 | S01 | [#B002](index.html#B002) | — | Ожидает извлечения из DOCX |
| B003 | S01 | [#B003](index.html#B003) | — | Ожидает извлечения из DOCX |
| B004 | S01 | [#B004](index.html#B004) | Рис. 2 | Ожидает извлечения из DOCX |
| B005 | S01 | [#B005](index.html#B005) | — | Ожидает извлечения из DOCX |
| B006 | S01 | [#B006](index.html#B006) | — | Ожидает извлечения из DOCX |
| B007 | S01 | [#B007](index.html#B007) | — | Ожидает извлечения из DOCX |
| B008 | S01 | [#B008](index.html#B008) | — | Ожидает извлечения из DOCX |
| B009 | S01 | [#B009](index.html#B009) | — | Ожидает извлечения из DOCX |
| B010 | S01 | [#B010](index.html#B010) | Рис. 3 | Ожидает извлечения из DOCX |
| B011 | S01 | [#B011](index.html#B011) | — | Ожидает извлечения из DOCX |
| B012 | S01 | [#B012](index.html#B012) | — | Ожидает извлечения из DOCX |
| B013 | S01 | [#B013](index.html#B013) | — | Ожидает извлечения из DOCX |
| B014 | S01 | [#B014](index.html#B014) | — | Ожидает извлечения из DOCX |
| B015 | S01 | [#B015](index.html#B015) | — | Ожидает извлечения из DOCX |
| B016 | S01 | [#B016](index.html#B016) | Рис. 4 | Ожидает извлечения из DOCX |
| B017 | S01 | [#B017](index.html#B017) | — | Ожидает извлечения из DOCX |
| B018 | S01 | [#B018](index.html#B018) | — | Ожидает извлечения из DOCX |
| B019 | S01 | [#B019](index.html#B019) | Рис. 5 | Ожидает извлечения из DOCX |
| B020 | S02 | [#B020](index.html#B020) | — | Ожидает извлечения из DOCX |
| B021 | S02 | [#B021](index.html#B021) | — | Ожидает извлечения из DOCX |
| B022 | S02 | [#B022](index.html#B022) | — | Ожидает извлечения из DOCX |
| B023 | S02 | [#B023](index.html#B023) | — | Ожидает извлечения из DOCX |
| B024 | S02 | [#B024](index.html#B024) | — | Ожидает извлечения из DOCX |
| B025 | S02 | [#B025](index.html#B025) | — | Ожидает извлечения из DOCX |
| B026 | S02 | [#B026](index.html#B026) | — | Ожидает извлечения из DOCX |
| B027 | S02 | [#B027](index.html#B027) | Рис. 6 | Ожидает извлечения из DOCX |
| B028 | S02 | [#B028](index.html#B028) | — | Ожидает извлечения из DOCX |
| B029 | S02 | [#B029](index.html#B029) | — | Ожидает извлечения из DOCX |
| B030 | S02 | [#B030](index.html#B030) | — | Ожидает извлечения из DOCX |
| B031 | S02 | [#B031](index.html#B031) | — | Ожидает извлечения из DOCX |
| B032 | S02 | [#B032](index.html#B032) | Рис. 7 | Ожидает извлечения из DOCX |
| B033 | S02 | [#B033](index.html#B033) | — | Ожидает извлечения из DOCX |
| B034 | S02 | [#B034](index.html#B034) | — | Ожидает извлечения из DOCX |
| B035 | S02 | [#B035](index.html#B035) | Рис. 8 | Ожидает извлечения из DOCX |
| B036 | S02 | [#B036](index.html#B036) | — | Ожидает извлечения из DOCX |
| B037 | S02 | [#B037](index.html#B037) | Рис. 9 | Ожидает извлечения из DOCX |
| B038 | S02 | [#B038](index.html#B038) | — | Ожидает извлечения из DOCX |
| B039 | S02 | [#B039](index.html#B039) | — | Ожидает извлечения из DOCX |
| B040 | S02 | [#B040](index.html#B040) | Рис. 10 | Ожидает извлечения из DOCX |
| B041 | S03 | [#B041](index.html#B041) | — | Ожидает извлечения из DOCX |
| B042 | S03 | [#B042](index.html#B042) | — | Ожидает извлечения из DOCX |
| B043 | S03 | [#B043](index.html#B043) | — | Ожидает извлечения из DOCX |
| B044 | S03 | [#B044](index.html#B044) | — | Ожидает извлечения из DOCX |
| B045 | S03 | [#B045](index.html#B045) | — | Ожидает извлечения из DOCX |
| B046 | S03 | [#B046](index.html#B046) | — | Ожидает извлечения из DOCX |
| B047 | S03 | [#B047](index.html#B047) | — | Ожидает извлечения из DOCX |
| B048 | S03 | [#B048](index.html#B048) | — | Ожидает извлечения из DOCX |
| B049 | S03 | [#B049](index.html#B049) | — | Ожидает извлечения из DOCX |
| B050 | S03 | [#B050](index.html#B050) | Рис. 11 | Ожидает извлечения из DOCX |
| B051 | S03 | [#B051](index.html#B051) | — | Ожидает извлечения из DOCX |
| B052 | S03 | [#B052](index.html#B052) | — | Ожидает извлечения из DOCX |
| B053 | S03 | [#B053](index.html#B053) | — | Ожидает извлечения из DOCX |
| B054 | S03 | [#B054](index.html#B054) | — | Ожидает извлечения из DOCX |
| B055 | S03 | [#B055](index.html#B055) | — | Ожидает извлечения из DOCX |
| B056 | S03 | [#B056](index.html#B056) | — | Ожидает извлечения из DOCX |
| B057 | S03 | [#B057](index.html#B057) | — | Ожидает извлечения из DOCX |
| B058 | S03 | [#B058](index.html#B058) | Рис. 12 | Ожидает извлечения из DOCX |
| B059 | S03 | [#B059](index.html#B059) | — | Ожидает извлечения из DOCX |
| B060 | S03 | [#B060](index.html#B060) | — | Ожидает извлечения из DOCX |
| B061 | S03 | [#B061](index.html#B061) | — | Ожидает извлечения из DOCX |
| B062 | S03 | [#B062](index.html#B062) | Рис. 13 | Ожидает извлечения из DOCX |
| B063 | S03 | [#B063](index.html#B063) | — | Ожидает извлечения из DOCX |
| B064 | S04 | [#B064](index.html#B064) | — | Ожидает извлечения из DOCX |
| B065 | S04 | [#B065](index.html#B065) | — | Ожидает извлечения из DOCX |
| B066 | S04 | [#B066](index.html#B066) | Рис. 14 | Ожидает извлечения из DOCX |
| B067 | S04 | [#B067](index.html#B067) | — | Ожидает извлечения из DOCX |
| B068 | S04 | [#B068](index.html#B068) | — | Ожидает извлечения из DOCX |
| B069 | S04 | [#B069](index.html#B069) | — | Ожидает извлечения из DOCX |
| B070 | S04 | [#B070](index.html#B070) | — | Ожидает извлечения из DOCX |
| B071 | S04 | [#B071](index.html#B071) | — | Ожидает извлечения из DOCX |
| B072 | S04 | [#B072](index.html#B072) | — | Ожидает извлечения из DOCX |
| B073 | S04 | [#B073](index.html#B073) | — | Ожидает извлечения из DOCX |
| B074 | S04 | [#B074](index.html#B074) | — | Ожидает извлечения из DOCX |
| B075 | S04 | [#B075](index.html#B075) | — | Ожидает извлечения из DOCX |
| B076 | S04 | [#B076](index.html#B076) | — | Ожидает извлечения из DOCX |
| B077 | S04 | [#B077](index.html#B077) | — | Ожидает извлечения из DOCX |
| B078 | S04 | [#B078](index.html#B078) | — | Ожидает извлечения из DOCX |
| B079 | S04 | [#B079](index.html#B079) | Рис. 15 | Ожидает извлечения из DOCX |
| B080 | S05 | [#B080](index.html#B080) | — | Ожидает извлечения из DOCX |
| B081 | S05 | [#B081](index.html#B081) | — | Ожидает извлечения из DOCX |
| B082 | S05 | [#B082](index.html#B082) | — | Ожидает извлечения из DOCX |
| B083 | S05 | [#B083](index.html#B083) | — | Ожидает извлечения из DOCX |
| B084 | S05 | [#B084](index.html#B084) | — | Ожидает извлечения из DOCX |
| B085 | S05 | [#B085](index.html#B085) | — | Ожидает извлечения из DOCX |
| B086 | S05 | [#B086](index.html#B086) | Рис. 16 | Ожидает извлечения из DOCX |
| B087 | S05 | [#B087](index.html#B087) | — | Ожидает извлечения из DOCX |
| B088 | S05 | [#B088](index.html#B088) | Рис. 17 | Ожидает извлечения из DOCX |
| B089 | S05 | [#B089](index.html#B089) | — | Ожидает извлечения из DOCX |
| B090 | S05 | [#B090](index.html#B090) | Рис. 18 | Ожидает извлечения из DOCX |
| B091 | S05 | [#B091](index.html#B091) | Рис. 19 | Ожидает извлечения из DOCX |
| B092 | S05 | [#B092](index.html#B092) | — | Ожидает извлечения из DOCX |
| B093 | S05 | [#B093](index.html#B093) | — | Ожидает извлечения из DOCX |
| B094 | S05 | [#B094](index.html#B094) | — | Ожидает извлечения из DOCX |
| B095 | S05 | [#B095](index.html#B095) | — | Ожидает извлечения из DOCX |
| B096 | S05 | [#B096](index.html#B096) | — | Ожидает извлечения из DOCX |
| B097 | S05 | [#B097](index.html#B097) | Рис. 20 | Ожидает извлечения из DOCX |
| B098 | S05 | [#B098](index.html#B098) | — | Ожидает извлечения из DOCX |
| B099 | S05 | [#B099](index.html#B099) | — | Ожидает извлечения из DOCX |
| B100 | S05 | [#B100](index.html#B100) | — | Ожидает извлечения из DOCX |
| B101 | S05 | [#B101](index.html#B101) | — | Ожидает извлечения из DOCX |
| B102 | S05 | [#B102](index.html#B102) | — | Ожидает извлечения из DOCX |
| B103 | S05 | [#B103](index.html#B103) | — | Ожидает извлечения из DOCX |
| B104 | S05 | [#B104](index.html#B104) | Рис. 21 | Ожидает извлечения из DOCX |
| B105 | S06 | [#B105](index.html#B105) | — | Ожидает извлечения из DOCX |
| B106 | S06 | [#B106](index.html#B106) | — | Ожидает извлечения из DOCX |
| B107 | S06 | [#B107](index.html#B107) | — | Ожидает извлечения из DOCX |
| B108 | S06 | [#B108](index.html#B108) | — | Ожидает извлечения из DOCX |
| B109 | S06 | [#B109](index.html#B109) | — | Ожидает извлечения из DOCX |
| B110 | S06 | [#B110](index.html#B110) | — | Ожидает извлечения из DOCX |
| B111 | S06 | [#B111](index.html#B111) | — | Ожидает извлечения из DOCX |
| B112 | S06 | [#B112](index.html#B112) | — | Ожидает извлечения из DOCX |
| B113 | S06 | [#B113](index.html#B113) | — | Ожидает извлечения из DOCX |
| B114 | S06 | [#B114](index.html#B114) | Рис. 22 | Ожидает извлечения из DOCX |
| B115 | S06 | [#B115](index.html#B115) | — | Ожидает извлечения из DOCX |
| B116 | S06 | [#B116](index.html#B116) | — | Ожидает извлечения из DOCX |
| B117 | S06 | [#B117](index.html#B117) | — | Ожидает извлечения из DOCX |
| B118 | S06 | [#B118](index.html#B118) | — | Ожидает извлечения из DOCX |
| B119 | S06 | [#B119](index.html#B119) | — | Ожидает извлечения из DOCX |
| B120 | S06 | [#B120](index.html#B120) | Рис. 23 | Ожидает извлечения из DOCX |
| B121 | S06 | [#B121](index.html#B121) | — | Ожидает извлечения из DOCX |
| B122 | S06 | [#B122](index.html#B122) | — | Ожидает извлечения из DOCX |
| B123 | S06 | [#B123](index.html#B123) | — | Ожидает извлечения из DOCX |
| B124 | S06 | [#B124](index.html#B124) | — | Ожидает извлечения из DOCX |
| B125 | S07 | [#B125](index.html#B125) | Рис. 24 | Ожидает извлечения из DOCX |
| B126 | S07 | [#B126](index.html#B126) | — | Ожидает извлечения из DOCX |
| B127 | S07 | [#B127](index.html#B127) | — | Ожидает извлечения из DOCX |
| B128 | S07 | [#B128](index.html#B128) | — | Ожидает извлечения из DOCX |
| B129 | S07 | [#B129](index.html#B129) | — | Ожидает извлечения из DOCX |
| B130 | S07 | [#B130](index.html#B130) | — | Ожидает извлечения из DOCX |
| B131 | S07 | [#B131](index.html#B131) | — | Ожидает извлечения из DOCX |
| B132 | S07 | [#B132](index.html#B132) | — | Ожидает извлечения из DOCX |
| B133 | S07 | [#B133](index.html#B133) | — | Ожидает извлечения из DOCX |
| B134 | S07 | [#B134](index.html#B134) | — | Ожидает извлечения из DOCX |
| B135 | S07 | [#B135](index.html#B135) | Рис. 25 | Ожидает извлечения из DOCX |
| B136 | S07 | [#B136](index.html#B136) | — | Ожидает извлечения из DOCX |
| B137 | S07 | [#B137](index.html#B137) | — | Ожидает извлечения из DOCX |
| B138 | S07 | [#B138](index.html#B138) | — | Ожидает извлечения из DOCX |
| B139 | S07 | [#B139](index.html#B139) | — | Ожидает извлечения из DOCX |
| B140 | S07 | [#B140](index.html#B140) | — | Ожидает извлечения из DOCX |
| B141 | S07 | [#B141](index.html#B141) | — | Ожидает извлечения из DOCX |
| B142 | S07 | [#B142](index.html#B142) | — | Ожидает извлечения из DOCX |
| B143 | S07 | [#B143](index.html#B143) | — | Ожидает извлечения из DOCX |
| B144 | S07 | [#B144](index.html#B144) | — | Ожидает извлечения из DOCX |
| B145 | S07 | [#B145](index.html#B145) | — | Ожидает извлечения из DOCX |
| B146 | S08 | [#B146](index.html#B146) | Рис. 26 | Ожидает извлечения из DOCX |
| B147 | S08 | [#B147](index.html#B147) | — | Ожидает извлечения из DOCX |
| B148 | S08 | [#B148](index.html#B148) | — | Ожидает извлечения из DOCX |
| B149 | S08 | [#B149](index.html#B149) | — | Ожидает извлечения из DOCX |
| B150 | S08 | [#B150](index.html#B150) | — | Ожидает извлечения из DOCX |
| B151 | S08 | [#B151](index.html#B151) | — | Ожидает извлечения из DOCX |
| B152 | S08 | [#B152](index.html#B152) | — | Ожидает извлечения из DOCX |
| B153 | S08 | [#B153](index.html#B153) | — | Ожидает извлечения из DOCX |
| B154 | S08 | [#B154](index.html#B154) | — | Ожидает извлечения из DOCX |
| B155 | S08 | [#B155](index.html#B155) | — | Ожидает извлечения из DOCX |
| B156 | S08 | [#B156](index.html#B156) | — | Ожидает извлечения из DOCX |
| B157 | S08 | [#B157](index.html#B157) | — | Ожидает извлечения из DOCX |
| B158 | S08 | [#B158](index.html#B158) | — | Ожидает извлечения из DOCX |
| B159 | S08 | [#B159](index.html#B159) | — | Ожидает извлечения из DOCX |
| B160 | S08 | [#B160](index.html#B160) | — | Ожидает извлечения из DOCX |
| B161 | S08 | [#B161](index.html#B161) | — | Ожидает извлечения из DOCX |
| B162 | S08 | [#B162](index.html#B162) | — | Ожидает извлечения из DOCX |
| B163 | S08 | [#B163](index.html#B163) | — | Ожидает извлечения из DOCX |
| B164 | S09 | [#B164](index.html#B164) | Рис. 27 | Ожидает извлечения из DOCX |
| B165 | S09 | [#B165](index.html#B165) | — | Ожидает извлечения из DOCX |
| B166 | S09 | [#B166](index.html#B166) | Рис. 28 | Ожидает извлечения из DOCX |
| B167 | S09 | [#B167](index.html#B167) | — | Ожидает извлечения из DOCX |
| B168 | S09 | [#B168](index.html#B168) | — | Ожидает извлечения из DOCX |
| B169 | S09 | [#B169](index.html#B169) | — | Ожидает извлечения из DOCX |
| B170 | S09 | [#B170](index.html#B170) | — | Ожидает извлечения из DOCX |
| B171 | S09 | [#B171](index.html#B171) | — | Ожидает извлечения из DOCX |
| B172 | S09 | [#B172](index.html#B172) | — | Ожидает извлечения из DOCX |
| B173 | S09 | [#B173](index.html#B173) | — | Ожидает извлечения из DOCX |
| B174 | S09 | [#B174](index.html#B174) | — | Ожидает извлечения из DOCX |
| B175 | S09 | [#B175](index.html#B175) | — | Ожидает извлечения из DOCX |
| B176 | S09 | [#B176](index.html#B176) | Рис. 29 | Ожидает извлечения из DOCX |
| B177 | S09 | [#B177](index.html#B177) | — | Ожидает извлечения из DOCX |
| B178 | S09 | [#B178](index.html#B178) | — | Ожидает извлечения из DOCX |
| B179 | S09 | [#B179](index.html#B179) | — | Ожидает извлечения из DOCX |
| B180 | S09 | [#B180](index.html#B180) | — | Ожидает извлечения из DOCX |
| B181 | S09 | [#B181](index.html#B181) | — | Ожидает извлечения из DOCX |
| B182 | S10 | [#B182](index.html#B182) | — | Ожидает извлечения из DOCX |
| B183 | S10 | [#B183](index.html#B183) | Рис. 30 | Ожидает извлечения из DOCX |
| B184 | S10 | [#B184](index.html#B184) | — | Ожидает извлечения из DOCX |
| B185 | S10 | [#B185](index.html#B185) | — | Ожидает извлечения из DOCX |
| B186 | S10 | [#B186](index.html#B186) | — | Ожидает извлечения из DOCX |
| B187 | S10 | [#B187](index.html#B187) | — | Ожидает извлечения из DOCX |
| B188 | S10 | [#B188](index.html#B188) | — | Ожидает извлечения из DOCX |
| B189 | S10 | [#B189](index.html#B189) | — | Ожидает извлечения из DOCX |
| B190 | S10 | [#B190](index.html#B190) | — | Ожидает извлечения из DOCX |
| B191 | S10 | [#B191](index.html#B191) | — | Ожидает извлечения из DOCX |
| B192 | S10 | [#B192](index.html#B192) | Табл. 2 | Ожидает извлечения из DOCX |
| B193 | S10 | [#B193](index.html#B193) | — | Ожидает извлечения из DOCX |
| B194 | S10 | [#B194](index.html#B194) | — | Ожидает извлечения из DOCX |
| B195 | S10 | [#B195](index.html#B195) | — | Ожидает извлечения из DOCX |
| B196 | S10 | [#B196](index.html#B196) | — | Ожидает извлечения из DOCX |
| B197 | S10 | [#B197](index.html#B197) | — | Ожидает извлечения из DOCX |
| B198 | S10 | [#B198](index.html#B198) | — | Ожидает извлечения из DOCX |
| B199 | S10 | [#B199](index.html#B199) | — | Ожидает извлечения из DOCX |
| B200 | S10 | [#B200](index.html#B200) | Табл. 3 | Ожидает извлечения из DOCX |
| B201 | S11 | [#B201](index.html#B201) | — | Ожидает извлечения из DOCX |
| B202 | S11 | [#B202](index.html#B202) | — | Ожидает извлечения из DOCX |
| B203 | S11 | [#B203](index.html#B203) | — | Ожидает извлечения из DOCX |
| B204 | S11 | [#B204](index.html#B204) | — | Ожидает извлечения из DOCX |
| B205 | S11 | [#B205](index.html#B205) | — | Ожидает извлечения из DOCX |
| B206 | S11 | [#B206](index.html#B206) | — | Ожидает извлечения из DOCX |
| B207 | S11 | [#B207](index.html#B207) | — | Ожидает извлечения из DOCX |
| B208 | S11 | [#B208](index.html#B208) | Рис. 31 | Ожидает извлечения из DOCX |
| B209 | S11 | [#B209](index.html#B209) | — | Ожидает извлечения из DOCX |
| B210 | S11 | [#B210](index.html#B210) | Рис. 32 | Ожидает извлечения из DOCX |
| B211 | S11 | [#B211](index.html#B211) | — | Ожидает извлечения из DOCX |
| B212 | S11 | [#B212](index.html#B212) | Рис. 33 | Ожидает извлечения из DOCX |
| B213 | S11 | [#B213](index.html#B213) | — | Ожидает извлечения из DOCX |
| B214 | S11 | [#B214](index.html#B214) | Рис. 34 | Ожидает извлечения из DOCX |
| B215 | S11 | [#B215](index.html#B215) | — | Ожидает извлечения из DOCX |
| B216 | S11 | [#B216](index.html#B216) | Рис. 35 | Ожидает извлечения из DOCX |
| B217 | S11 | [#B217](index.html#B217) | — | Ожидает извлечения из DOCX |
| B218 | S12 | [#B218](index.html#B218) | — | Ожидает извлечения из DOCX |
| B219 | S12 | [#B219](index.html#B219) | — | Ожидает извлечения из DOCX |
| B220 | S12 | [#B220](index.html#B220) | — | Ожидает извлечения из DOCX |
| B221 | S12 | [#B221](index.html#B221) | — | Ожидает извлечения из DOCX |
| B222 | S12 | [#B222](index.html#B222) | — | Ожидает извлечения из DOCX |
| B223 | S12 | [#B223](index.html#B223) | — | Ожидает извлечения из DOCX |
| B224 | S12 | [#B224](index.html#B224) | — | Ожидает извлечения из DOCX |
| B225 | S12 | [#B225](index.html#B225) | — | Ожидает извлечения из DOCX |
| B226 | S12 | [#B226](index.html#B226) | — | Ожидает извлечения из DOCX |
| B227 | S12 | [#B227](index.html#B227) | — | Ожидает извлечения из DOCX |
| B228 | S12 | [#B228](index.html#B228) | — | Ожидает извлечения из DOCX |
| B229 | S12 | [#B229](index.html#B229) | Рис. 36 | Ожидает извлечения из DOCX |
| B230 | S12 | [#B230](index.html#B230) | — | Ожидает извлечения из DOCX |
| B231 | S12 | [#B231](index.html#B231) | — | Ожидает извлечения из DOCX |
| B232 | S12 | [#B232](index.html#B232) | — | Ожидает извлечения из DOCX |
| B233 | S12 | [#B233](index.html#B233) | — | Ожидает извлечения из DOCX |
| B234 | S12 | [#B234](index.html#B234) | — | Ожидает извлечения из DOCX |
| B235 | S12 | [#B235](index.html#B235) | — | Ожидает извлечения из DOCX |
| B236 | S12 | [#B236](index.html#B236) | — | Ожидает извлечения из DOCX |
| B237 | S12 | [#B237](index.html#B237) | Рис. 37 | Ожидает извлечения из DOCX |
| B238 | S12 | [#B238](index.html#B238) | — | Ожидает извлечения из DOCX |
| B239 | S12 | [#B239](index.html#B239) | — | Ожидает извлечения из DOCX |
| B240 | S12 | [#B240](index.html#B240) | — | Ожидает извлечения из DOCX |
| B241 | S12 | [#B241](index.html#B241) | — | Ожидает извлечения из DOCX |
| B242 | S12 | [#B242](index.html#B242) | — | Ожидает извлечения из DOCX |
| B243 | S12 | [#B243](index.html#B243) | — | Ожидает извлечения из DOCX |
| B244 | S12 | [#B244](index.html#B244) | — | Ожидает извлечения из DOCX |
| B245 | S12 | [#B245](index.html#B245) | — | Ожидает извлечения из DOCX |
| B246 | S12 | [#B246](index.html#B246) | Рис. 38 | Ожидает извлечения из DOCX |
| B247 | S12 | [#B247](index.html#B247) | — | Ожидает извлечения из DOCX |
| B248 | S12 | [#B248](index.html#B248) | — | Ожидает извлечения из DOCX |
| B249 | S12 | [#B249](index.html#B249) | — | Ожидает извлечения из DOCX |
| B250 | S12 | [#B250](index.html#B250) | Рис. 39 | Ожидает извлечения из DOCX |
| B251 | S12 | [#B251](index.html#B251) | — | Ожидает извлечения из DOCX |
| B252 | S12 | [#B252](index.html#B252) | — | Ожидает извлечения из DOCX |
| B253 | S12 | [#B253](index.html#B253) | — | Ожидает извлечения из DOCX |
| B254 | S12 | [#B254](index.html#B254) | — | Ожидает извлечения из DOCX |
| B255 | S12 | [#B255](index.html#B255) | — | Ожидает извлечения из DOCX |
| B256 | S13 | [#B256](index.html#B256) | — | Ожидает извлечения из DOCX |
| B257 | S13 | [#B257](index.html#B257) | Рис. 40 | Ожидает извлечения из DOCX |
| B258 | S13 | [#B258](index.html#B258) | — | Ожидает извлечения из DOCX |
| B259 | S13 | [#B259](index.html#B259) | — | Ожидает извлечения из DOCX |
| B260 | S13 | [#B260](index.html#B260) | — | Ожидает извлечения из DOCX |
| B261 | S13 | [#B261](index.html#B261) | — | Ожидает извлечения из DOCX |
| B262 | S13 | [#B262](index.html#B262) | — | Ожидает извлечения из DOCX |
| B263 | S13 | [#B263](index.html#B263) | — | Ожидает извлечения из DOCX |
| B264 | S13 | [#B264](index.html#B264) | — | Ожидает извлечения из DOCX |
| B265 | S13 | [#B265](index.html#B265) | Рис. 41 | Ожидает извлечения из DOCX |
| B266 | S13 | [#B266](index.html#B266) | Рис. 42 | Ожидает извлечения из DOCX |
| B267 | S13 | [#B267](index.html#B267) | Рис. 43 | Ожидает извлечения из DOCX |
| B268 | S13 | [#B268](index.html#B268) | — | Ожидает извлечения из DOCX |
| B269 | S13 | [#B269](index.html#B269) | — | Ожидает извлечения из DOCX |
| B270 | S13 | [#B270](index.html#B270) | — | Ожидает извлечения из DOCX |
| B271 | S13 | [#B271](index.html#B271) | — | Ожидает извлечения из DOCX |
| B272 | S13 | [#B272](index.html#B272) | — | Ожидает извлечения из DOCX |
| B273 | S13 | [#B273](index.html#B273) | — | Ожидает извлечения из DOCX |
| B274 | S13 | [#B274](index.html#B274) | — | Ожидает извлечения из DOCX |
| B275 | S14 | [#B275](index.html#B275) | — | Ожидает извлечения из DOCX |
| B276 | S14 | [#B276](index.html#B276) | — | Ожидает извлечения из DOCX |
| B277 | S14 | [#B277](index.html#B277) | — | Ожидает извлечения из DOCX |
| B278 | S14 | [#B278](index.html#B278) | — | Ожидает извлечения из DOCX |
| B279 | S14 | [#B279](index.html#B279) | — | Ожидает извлечения из DOCX |
| B280 | S14 | [#B280](index.html#B280) | — | Ожидает извлечения из DOCX |
| B281 | S14 | [#B281](index.html#B281) | Рис. 44 | Ожидает извлечения из DOCX |
| B282 | S14 | [#B282](index.html#B282) | — | Ожидает извлечения из DOCX |
| B283 | S14 | [#B283](index.html#B283) | — | Ожидает извлечения из DOCX |
| B284 | S14 | [#B284](index.html#B284) | — | Ожидает извлечения из DOCX |
| B285 | S14 | [#B285](index.html#B285) | — | Ожидает извлечения из DOCX |
| B286 | S14 | [#B286](index.html#B286) | Рис. 45 | Ожидает извлечения из DOCX |
| B287 | S14 | [#B287](index.html#B287) | — | Ожидает извлечения из DOCX |
| B288 | S14 | [#B288](index.html#B288) | — | Ожидает извлечения из DOCX |
| B289 | S14 | [#B289](index.html#B289) | — | Ожидает извлечения из DOCX |
| B290 | S14 | [#B290](index.html#B290) | — | Ожидает извлечения из DOCX |
| B291 | S14 | [#B291](index.html#B291) | — | Ожидает извлечения из DOCX |
| B292 | S14 | [#B292](index.html#B292) | — | Ожидает извлечения из DOCX |
| B293 | S14 | [#B293](index.html#B293) | — | Ожидает извлечения из DOCX |
| B294 | S14 | [#B294](index.html#B294) | — | Ожидает извлечения из DOCX |
| B295 | S14 | [#B295](index.html#B295) | — | Ожидает извлечения из DOCX |
| B296 | S14 | [#B296](index.html#B296) | — | Ожидает извлечения из DOCX |
| B297 | S14 | [#B297](index.html#B297) | — | Ожидает извлечения из DOCX |
| B298 | S14 | [#B298](index.html#B298) | — | Ожидает извлечения из DOCX |
| B299 | S14 | [#B299](index.html#B299) | — | Ожидает извлечения из DOCX |
| B300 | S14 | [#B300](index.html#B300) | — | Ожидает извлечения из DOCX |
| B301 | S14 | [#B301](index.html#B301) | — | Ожидает извлечения из DOCX |
| B302 | S14 | [#B302](index.html#B302) | — | Ожидает извлечения из DOCX |
| B303 | S14 | [#B303](index.html#B303) | — | Ожидает извлечения из DOCX |
| B304 | S14 | [#B304](index.html#B304) | — | Ожидает извлечения из DOCX |
| B305 | S14 | [#B305](index.html#B305) | — | Ожидает извлечения из DOCX |
| B306 | S14 | [#B306](index.html#B306) | — | Ожидает извлечения из DOCX |
| B307 | S14 | [#B307](index.html#B307) | — | Ожидает извлечения из DOCX |
| B308 | S14 | [#B308](index.html#B308) | — | Ожидает извлечения из DOCX |
| B309 | S14 | [#B309](index.html#B309) | Рис. 46 | Ожидает извлечения из DOCX |
| B310 | S15 | [#B310](index.html#B310) | — | Ожидает извлечения из DOCX |
| B311 | S15 | [#B311](index.html#B311) | Рис. 47 | Ожидает извлечения из DOCX |
| B312 | S15 | [#B312](index.html#B312) | — | Ожидает извлечения из DOCX |
| B313 | S15 | [#B313](index.html#B313) | Рис. 48 | Ожидает извлечения из DOCX |
| B314 | S15 | [#B314](index.html#B314) | Рис. 49 | Ожидает извлечения из DOCX |
| B315 | S15 | [#B315](index.html#B315) | Рис. 50 | Ожидает извлечения из DOCX |
| B316 | S15 | [#B316](index.html#B316) | Рис. 51 | Ожидает извлечения из DOCX |
| B317 | S15 | [#B317](index.html#B317) | Рис. 52 | Ожидает извлечения из DOCX |
| B318 | S15 | [#B318](index.html#B318) | — | Ожидает извлечения из DOCX |
| B319 | S15 | [#B319](index.html#B319) | — | Ожидает извлечения из DOCX |
| B320 | S15 | [#B320](index.html#B320) | — | Ожидает извлечения из DOCX |
| B321 | S15 | [#B321](index.html#B321) | — | Ожидает извлечения из DOCX |
| B322 | S15 | [#B322](index.html#B322) | Рис. 53 | Ожидает извлечения из DOCX |
| B323 | S16 | [#B323](index.html#B323) | — | Ожидает извлечения из DOCX |
| B324 | S16 | [#B324](index.html#B324) | — | Ожидает извлечения из DOCX |
| B325 | S16 | [#B325](index.html#B325) | — | Ожидает извлечения из DOCX |
| B326 | S16 | [#B326](index.html#B326) | — | Ожидает извлечения из DOCX |
| B327 | S16 | [#B327](index.html#B327) | — | Ожидает извлечения из DOCX |
| B328 | S16 | [#B328](index.html#B328) | — | Ожидает извлечения из DOCX |
| B329 | S16 | [#B329](index.html#B329) | — | Ожидает извлечения из DOCX |
| B330 | S16 | [#B330](index.html#B330) | — | Ожидает извлечения из DOCX |
| B331 | S16 | [#B331](index.html#B331) | — | Ожидает извлечения из DOCX |
| B332 | S16 | [#B332](index.html#B332) | — | Ожидает извлечения из DOCX |
| B333 | S16 | [#B333](index.html#B333) | — | Ожидает извлечения из DOCX |
| B334 | S16 | [#B334](index.html#B334) | — | Ожидает извлечения из DOCX |
| B335 | S16 | [#B335](index.html#B335) | — | Ожидает извлечения из DOCX |
| B336 | S16 | [#B336](index.html#B336) | — | Ожидает извлечения из DOCX |
| B337 | S16 | [#B337](index.html#B337) | — | Ожидает извлечения из DOCX |
| B338 | S16 | [#B338](index.html#B338) | — | Ожидает извлечения из DOCX |
| B339 | S16 | [#B339](index.html#B339) | — | Ожидает извлечения из DOCX |
| B340 | S16 | [#B340](index.html#B340) | — | Ожидает извлечения из DOCX |
| B341 | S16 | [#B341](index.html#B341) | — | Ожидает извлечения из DOCX |
| B342 | S16 | [#B342](index.html#B342) | — | Ожидает извлечения из DOCX |
| B343 | S16 | [#B343](index.html#B343) | — | Ожидает извлечения из DOCX |
| B344 | S16 | [#B344](index.html#B344) | — | Ожидает извлечения из DOCX |
| B345 | S16 | [#B345](index.html#B345) | — | Ожидает извлечения из DOCX |
| B346 | S16 | [#B346](index.html#B346) | — | Ожидает извлечения из DOCX |
| B347 | S16 | [#B347](index.html#B347) | — | Ожидает извлечения из DOCX |
| B348 | S16 | [#B348](index.html#B348) | Рис. 54 | Ожидает извлечения из DOCX |
| B349 | S16 | [#B349](index.html#B349) | — | Ожидает извлечения из DOCX |
| B350 | S16 | [#B350](index.html#B350) | — | Ожидает извлечения из DOCX |
| B351 | S16 | [#B351](index.html#B351) | — | Ожидает извлечения из DOCX |
| B352 | S16 | [#B352](index.html#B352) | — | Ожидает извлечения из DOCX |
| B353 | S16 | [#B353](index.html#B353) | — | Ожидает извлечения из DOCX |
| B354 | S16 | [#B354](index.html#B354) | — | Ожидает извлечения из DOCX |
| B355 | S16 | [#B355](index.html#B355) | — | Ожидает извлечения из DOCX |
| B356 | S16 | [#B356](index.html#B356) | — | Ожидает извлечения из DOCX |
| B357 | S16 | [#B357](index.html#B357) | — | Ожидает извлечения из DOCX |
| B358 | S17 | [#B358](index.html#B358) | — | Ожидает извлечения из DOCX |
| B359 | S17 | [#B359](index.html#B359) | — | Ожидает извлечения из DOCX |
| B360 | S17 | [#B360](index.html#B360) | — | Ожидает извлечения из DOCX |
| B361 | S17 | [#B361](index.html#B361) | — | Ожидает извлечения из DOCX |
| B362 | S17 | [#B362](index.html#B362) | — | Ожидает извлечения из DOCX |
| B363 | S17 | [#B363](index.html#B363) | — | Ожидает извлечения из DOCX |
| B364 | S17 | [#B364](index.html#B364) | — | Ожидает извлечения из DOCX |
| B365 | S17 | [#B365](index.html#B365) | — | Ожидает извлечения из DOCX |
| B366 | S17 | [#B366](index.html#B366) | — | Ожидает извлечения из DOCX |
| B367 | S17 | [#B367](index.html#B367) | — | Ожидает извлечения из DOCX |
| B368 | S17 | [#B368](index.html#B368) | — | Ожидает извлечения из DOCX |
| B369 | S17 | [#B369](index.html#B369) | — | Ожидает извлечения из DOCX |
| B370 | S17 | [#B370](index.html#B370) | — | Ожидает извлечения из DOCX |
| B371 | S17 | [#B371](index.html#B371) | — | Ожидает извлечения из DOCX |
| B372 | S17 | [#B372](index.html#B372) | — | Ожидает извлечения из DOCX |
| B373 | S17 | [#B373](index.html#B373) | — | Ожидает извлечения из DOCX |
| B374 | S17 | [#B374](index.html#B374) | — | Ожидает извлечения из DOCX |
| B375 | S17 | [#B375](index.html#B375) | — | Ожидает извлечения из DOCX |
| B376 | S17 | [#B376](index.html#B376) | — | Ожидает извлечения из DOCX |
| B377 | S17 | [#B377](index.html#B377) | Рис. 55 | Ожидает извлечения из DOCX |
| B378 | S17 | [#B378](index.html#B378) | — | Ожидает извлечения из DOCX |
| B379 | S17 | [#B379](index.html#B379) | Рис. 56 | Ожидает извлечения из DOCX |
| B380 | S17 | [#B380](index.html#B380) | — | Ожидает извлечения из DOCX |
| B381 | S17 | [#B381](index.html#B381) | — | Ожидает извлечения из DOCX |

## Изображения (56 PNG)

| № | DOCX-блок | Relationship | Файл внутри DOCX | HTML-якорь и целевой локальный путь |
| ---: | --- | --- | --- | --- |
| 1 | B001 | `rId8` | `word/media/image1.png` | [#figure-1](index.html#figure-1), `media/image1.png` |
| 2 | B004 | `rId9` | `word/media/image2.png` | [#figure-2](index.html#figure-2), `media/image2.png` |
| 3 | B010 | `rId10` | `word/media/image3.png` | [#figure-3](index.html#figure-3), `media/image3.png` |
| 4 | B016 | `rId11` | `word/media/image4.png` | [#figure-4](index.html#figure-4), `media/image4.png` |
| 5 | B019 | `rId12` | `word/media/image5.png` | [#figure-5](index.html#figure-5), `media/image5.png` |
| 6 | B027 | `rId13` | `word/media/image6.png` | [#figure-6](index.html#figure-6), `media/image6.png` |
| 7 | B032 | `rId14` | `word/media/image7.png` | [#figure-7](index.html#figure-7), `media/image7.png` |
| 8 | B035 | `rId15` | `word/media/image8.png` | [#figure-8](index.html#figure-8), `media/image8.png` |
| 9 | B037 | `rId16` | `word/media/image9.png` | [#figure-9](index.html#figure-9), `media/image9.png` |
| 10 | B040 | `rId17` | `word/media/image10.png` | [#figure-10](index.html#figure-10), `media/image10.png` |
| 11 | B050 | `rId18` | `word/media/image11.png` | [#figure-11](index.html#figure-11), `media/image11.png` |
| 12 | B058 | `rId19` | `word/media/image12.png` | [#figure-12](index.html#figure-12), `media/image12.png` |
| 13 | B062 | `rId20` | `word/media/image13.png` | [#figure-13](index.html#figure-13), `media/image13.png` |
| 14 | B066 | `rId21` | `word/media/image14.png` | [#figure-14](index.html#figure-14), `media/image14.png` |
| 15 | B079 | `rId22` | `word/media/image15.png` | [#figure-15](index.html#figure-15), `media/image15.png` |
| 16 | B086 | `rId23` | `word/media/image16.png` | [#figure-16](index.html#figure-16), `media/image16.png` |
| 17 | B088 | `rId24` | `word/media/image17.png` | [#figure-17](index.html#figure-17), `media/image17.png` |
| 18 | B090 | `rId25` | `word/media/image18.png` | [#figure-18](index.html#figure-18), `media/image18.png` |
| 19 | B091 | `rId26` | `word/media/image19.png` | [#figure-19](index.html#figure-19), `media/image19.png` |
| 20 | B097 | `rId27` | `word/media/image20.png` | [#figure-20](index.html#figure-20), `media/image20.png` |
| 21 | B104 | `rId28` | `word/media/image21.png` | [#figure-21](index.html#figure-21), `media/image21.png` |
| 22 | B114 | `rId29` | `word/media/image22.png` | [#figure-22](index.html#figure-22), `media/image22.png` |
| 23 | B120 | `rId30` | `word/media/image23.png` | [#figure-23](index.html#figure-23), `media/image23.png` |
| 24 | B125 | `rId31` | `word/media/image24.png` | [#figure-24](index.html#figure-24), `media/image24.png` |
| 25 | B135 | `rId32` | `word/media/image25.png` | [#figure-25](index.html#figure-25), `media/image25.png` |
| 26 | B146 | `rId33` | `word/media/image26.png` | [#figure-26](index.html#figure-26), `media/image26.png` |
| 27 | B164 | `rId34` | `word/media/image27.png` | [#figure-27](index.html#figure-27), `media/image27.png` |
| 28 | B166 | `rId35` | `word/media/image28.png` | [#figure-28](index.html#figure-28), `media/image28.png` |
| 29 | B176 | `rId36` | `word/media/image29.png` | [#figure-29](index.html#figure-29), `media/image29.png` |
| 30 | B183 | `rId37` | `word/media/image30.png` | [#figure-30](index.html#figure-30), `media/image30.png` |
| 31 | B208 | `rId38` | `word/media/image31.png` | [#figure-31](index.html#figure-31), `media/image31.png` |
| 32 | B210 | `rId39` | `word/media/image32.png` | [#figure-32](index.html#figure-32), `media/image32.png` |
| 33 | B212 | `rId40` | `word/media/image33.png` | [#figure-33](index.html#figure-33), `media/image33.png` |
| 34 | B214 | `rId41` | `word/media/image34.png` | [#figure-34](index.html#figure-34), `media/image34.png` |
| 35 | B216 | `rId42` | `word/media/image35.png` | [#figure-35](index.html#figure-35), `media/image35.png` |
| 36 | B229 | `rId43` | `word/media/image36.png` | [#figure-36](index.html#figure-36), `media/image36.png` |
| 37 | B237 | `rId44` | `word/media/image37.png` | [#figure-37](index.html#figure-37), `media/image37.png` |
| 38 | B246 | `rId45` | `word/media/image38.png` | [#figure-38](index.html#figure-38), `media/image38.png` |
| 39 | B250 | `rId46` | `word/media/image39.png` | [#figure-39](index.html#figure-39), `media/image39.png` |
| 40 | B257 | `rId47` | `word/media/image40.png` | [#figure-40](index.html#figure-40), `media/image40.png` |
| 41 | B265 | `rId48` | `word/media/image41.png` | [#figure-41](index.html#figure-41), `media/image41.png` |
| 42 | B266 | `rId49` | `word/media/image42.png` | [#figure-42](index.html#figure-42), `media/image42.png` |
| 43 | B267 | `rId50` | `word/media/image43.png` | [#figure-43](index.html#figure-43), `media/image43.png` |
| 44 | B281 | `rId51` | `word/media/image44.png` | [#figure-44](index.html#figure-44), `media/image44.png` |
| 45 | B286 | `rId52` | `word/media/image45.png` | [#figure-45](index.html#figure-45), `media/image45.png` |
| 46 | B309 | `rId53` | `word/media/image46.png` | [#figure-46](index.html#figure-46), `media/image46.png` |
| 47 | B311 | `rId54` | `word/media/image47.png` | [#figure-47](index.html#figure-47), `media/image47.png` |
| 48 | B313 | `rId55` | `word/media/image48.png` | [#figure-48](index.html#figure-48), `media/image48.png` |
| 49 | B314 | `rId56` | `word/media/image49.png` | [#figure-49](index.html#figure-49), `media/image49.png` |
| 50 | B315 | `rId57` | `word/media/image50.png` | [#figure-50](index.html#figure-50), `media/image50.png` |
| 51 | B316 | `rId58` | `word/media/image51.png` | [#figure-51](index.html#figure-51), `media/image51.png` |
| 52 | B317 | `rId59` | `word/media/image52.png` | [#figure-52](index.html#figure-52), `media/image52.png` |
| 53 | B322 | `rId60` | `word/media/image53.png` | [#figure-53](index.html#figure-53), `media/image53.png` |
| 54 | B348 | `rId61` | `word/media/image54.png` | [#figure-54](index.html#figure-54), `media/image54.png` |
| 55 | B377 | `rId62` | `word/media/image55.png` | [#figure-55](index.html#figure-55), `media/image55.png` |
| 56 | B379 | `rId63` | `word/media/image56.png` | [#figure-56](index.html#figure-56), `media/image56.png` |

## Таблицы (3)

| № | DOCX-блок | Размер | Назначение | HTML-якорь |
| ---: | --- | --- | --- | --- |
| 1 | B001 | 1 строка × 2 | Титульные данные и изображение 1 | [#table-1](index.html#table-1) |
| 2 | B192 | 6 строк × 2 | Слой и функция в модели асимметрии | [#table-2](index.html#table-2) |
| 3 | B200 | 4 строки × 3 | Механизм, биологическая аналогия и назначение в модели | [#table-3](index.html#table-3) |

### Инварианты для локального генератора

- Источник: `materials/research_sources/raw/Шестислойная модель.docx`, SHA-256 `dc53a11c90c1f6a2d7855c010f3a4f6126d39c5e75c5ccc733cb2a3430cf23fb`.
- 381 прямой блок `w:body` без завершающего `w:sectPr`; таблицы B001, B192, B200.
- 56 отдельных PNG по 56 употреблениям `a:blip` в порядке документа; изображение 1 внутри таблицы B001.
- Вывод HTML: `six-layer-model/index.html`; текстовый снимок: `snapshots/Шестислойная модель.extracted.md`; изображения: `six-layer-model/media/`.
- В DOCX нет OMML; текстовые формулы не переводить автоматически в LaTeX и не подменять обозначения. Формулы и геометрию рисунков сверить в 4.8/4.9.
