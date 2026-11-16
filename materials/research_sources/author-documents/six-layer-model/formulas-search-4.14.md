
# Формулы из изображений «Шестислойной модели» — поисковая транскрипция 4.14

**Редакторская транскрипция, сверенная с оригинальными PNG**, не исправление DOCX, не исполняемый код и не независимая валидация архитектуры. Оригинальные обозначения и их несоответствия сохранены. Этот файл дополняет [поисковый снимок](../../snapshots/Шестислойная%20модель.extracted.md) и [разбор](review.md), в котором зафиксированы неопределённости.

## Модуляция слоёв

- [Рис. 20, B097](README.md#figure-20): `Слой 2 = Слой 2 @ Softmax(M2)`, `Слой 3 = Слой 3 @ Softmax(M3)`.
- [Рис. 23, B120](README.md#figure-23): `Слой 5 = Слой 5 @ Softmax(M5)`.
- [Рис. 24, B125](README.md#figure-24): схема `Layer 4 (*) Softmax(M4) → Output`, входящие `Thalamus`, `brain area`, `Error (from Layer 6)`.
- [Рис. 26, B146](README.md#figure-26): `Mamba(Brain)`, `M_global`, `Mamba(B23)`, `Mamba(B5)`, `M_2`, `M_3`, `M_5`, подписи `cat(M23, M_L3)`, `cat(M5, M_global)`. Связанные текстовые [B148–B155](README.md#B148) записывают `M_global = Mamba(Brain)`, `M2 = Mamba(cat(M23,M_L3,M_global))`, `M3 = Mamba(cat(M23,M_global))`, `M5 = Mamba(cat(M5,M_global))`. Последняя запись самоссылочная.

## Предиктор и остаток

- [Рис. 33, B212](README.md#figure-33): `F4(X) - Predict(Xout)`, основная цепь `F4(X) → F2(X) → F3(X) → Xout`, выход `F5(X)`.
- [Рис. 56, B379](README.md#figure-56): `F6(X) = F4(X) - Predict(F5(X))`. Подписи «более вероятный» и «менее вероятный» сигнал относятся к авторской интерпретации, разность сама не есть вероятность.

## Код из рисунков, не из Python-пакета

[Рис. 44, B281](README.md#figure-44):

```python
def sigmoid_fluct(x, sigma=0.01, training=True):
    if training:
        noise = torch.randn_like(x)
        factor = 1 + sigma * noise
        return 1 / (1 + torch.exp(-(x * factor)))
    else:
        return F.sigmoid(x)
```

[Рис. 45, B286](README.md#figure-45):

```python
def gelu_fluct(x, sigma=0.01, training=True):
    if training:
        noise = torch.randn_like(x)
        factor = 1 + sigma * noise
        return x * 0.5 * (1 + torch.erf((x * factor) / math.sqrt(2)))
    else:
        return F.gelu(x)
```

В GELU множитель `factor` применяется **внутри** `erf`, но не к внешнему множителю `x`; это не то же самое, что `GELU(x * factor)`. На скриншотах `sigma=0.01`; не подменять значением 10% из другого раздела. Обнаруженные разночтения — в [E06](review.md#e06).

## Гистерезис и фазовые величины

[Рис. 54, B348](README.md#figure-54):

```text
alpha_amp   = alpha_rise, если x_t > x_prev; иначе alpha_fall (x_t <= x_prev)
alpha_freq  = alpha_rise, если |Δx_t| > |Δx_prev|; иначе alpha_fall
alpha_phase = alpha_rise, если «фазовый переход»; иначе alpha_fall
```

«Фазовый переход» — дословная словесная ветвь, формула определения отсутствует. Разность соседних значений не равна частоте в Гц. [Сверка H02](review.md#h02).

[Рис. 55, B377](README.md#figure-55):

```text
GELU_hyst(x_t, y_(t-1)) = alpha_t * y_(t-1) + (1 - alpha_t) * GELU_fluct(x_t)
alpha_t = alpha_rise, если GELU_fluct(x_t) > y_(t-1)
          alpha_fall, если GELU_fluct(x_t) <= y_(t-1)
alpha_rise > alpha_fall
y = alpha_t * y_prev + (1 - alpha_t) * GELU_fluct(x_t)
```

Эта рекурсия **не** равна оригинальному тексту [B331](README.md#B331)/[B350](README.md#B350): `x_t = (1 + alpha_total) * x_prev + (1 - alpha_total) * x_t`. Математическая ошибка и отличие разобраны в [H02](review.md#h02) и [H03](review.md#h03); транскрипция их не исправляет.

## Границы покрытия

Транскрибированы ключевые формулы и программные фрагменты **10 изображений**: 20, 23, 24, 26, 33, 44, 45, 54, 55, 56. Все 56 исходных PNG со смысловыми описаниями доступны в [HTML](README.md) и [review.md](review.md). **Не утверждается**, что абсолютно весь мелкий текст каждой картинки извлечён или что найденные формулы биологически подтверждены.
