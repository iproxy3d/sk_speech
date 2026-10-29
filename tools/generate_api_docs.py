"""Generate the complete Markdown API reference without importing heavy dependencies."""

from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "sk_speech"
OUTPUT = ROOT / "docs" / "API.md"

MODULES = {
    "pitch/calibration.py": ("Калибровка F0 и интенсивности", "Нейтральный профиль и относительные покадровые отклонения."),
    "pitch/extractor.py": ("Покадровое извлечение F0 и интенсивности", "Высокоуровневое извлечение синхронизированных временных рядов через Praat."),
    "pitch/models.py": ("Модели данных временных рядов", "Контейнеры исходных и нормализованных последовательностей."),
    "regulators.py": ("Физиологические регуляторы", "Экспериментальные модели гормонов, сердца, дыхания, давления и метаболизма."),
    "sk_detection.py": ("Классификация режима речи", "Эвристические детекторы тихой и громкой речи, шёпота, крика, пауз и ясности формант."),
    "sk_filters.py": ("Фильтры и ERB-преобразования", "Временные и частотные фильтры, эффекты, LMS и коэффициенты гамматонного банка."),
    "sk_formants.py": ("Форманты F1–F5", "Извлечение, измерение, динамика, паттерны, синтез и преобразование формант."),
    "sk_gammatone.py": ("Адаптивная гамматонная обработка", "ERB-фильтрация с настройкой центральных частот по F0 и формантам."),
    "sk_noise.py": ("Шум", "Оценка шума, спектральная плоскость, PSD и несколько вариантов шумоподавления."),
    "sk_pitch.py": ("Основной тон и просодия", "Расширенное извлечение и преобразование F0, интенсивности, наклона, периода, ритма и тембра."),
    "sk_plot.py": ("Визуализация", "Графики траекторий, спектров, спектрограмм, гласных и результатов преобразования."),
    "sk_signal.py": ("Генерация сигналов", "Гармонические компоненты, временные оси, сборка и сохранение синтетического сигнала."),
    "sk_vocal_cords.py": ("Голосовая щель и воздушный поток", "Физические оценки площади голосовой щели, сопротивления, потока, давления и SPL."),
    "sk_vocal_tract.py": ("Голосовой тракт", "Связь длины голосового тракта и резонансных частот формант."),
    "sk_volume.py": ("Комплексный профиль и преобразование речи", "Объединение акустических признаков, профили, векторы, пакетная обработка и комплексное изменение речи."),
    "sk_vowels.py": ("Гласные", "Поиск границ и типов гласных, их статистика, формантные преобразования и изменение длительности."),
}

PARAMETERS = {
    "y": "одномерный аудиосигнал `numpy.ndarray`",
    "signal": "одномерный аудиосигнал `numpy.ndarray`",
    "audio": "аудиосигнал",
    "audio_data": "массив аудиосэмплов",
    "audio_signal": "массив аудиосэмплов",
    "sr": "частота дискретизации, Гц",
    "sample_rate": "частота дискретизации, Гц",
    "rate": "частота дискретизации, Гц",
    "fs": "частота дискретизации, Гц",
    "path": "путь к файлу",
    "input_file": "путь к входному аудиофайлу",
    "output_file": "путь к выходному аудиофайлу",
    "file_path": "путь к файлу",
    "filename": "имя или путь к файлу",
    "folder_path": "путь к каталогу с аудиофайлами",
    "formant_index": "номер форманты: 1 соответствует F1",
    "index": "индекс анализируемого элемента",
    "formants": "заранее рассчитанные данные формант; `None` запускает расчёт",
    "pitch": "заранее рассчитанные данные F0; `None` запускает расчёт",
    "speech": "режим или структура профиля речи — зависит от функции",
    "time_step": "временной шаг анализа, с",
    "frame_length": "длина кадра в сэмплах или секундах согласно функции",
    "hop_length": "шаг между кадрами, сэмплы",
    "window_size": "размер окна обработки",
    "window_length": "длина оконной функции",
    "threshold": "порог принятия решения",
    "threshold_db": "порог уровня в децибелах",
    "pitch_from": "нижняя граница F0, Гц",
    "pitch_to": "верхняя граница F0, Гц",
    "f0_min": "нижняя граница F0, Гц",
    "f0_max": "верхняя граница F0, Гц",
    "factor": "множитель преобразования",
    "options": "словарь включаемых признаков и параметров расчёта",
    "track": "объект `PitchTrack` с покадровыми F0 и интенсивностью",
    "profile": "объект нейтрального профиля `PitchProfile`",
    "config": "конфигурация извлечения признаков",
    "sound": "объект аудиосигнала Praat или Pydub согласно функции",
    "volume": "уровень или коэффициент громкости",
    "emotion": "управляющая координата, используемая комплексным преобразованием",
    "vectors": "набор эталонных векторов признаков",
    "norm_params": "параметры нейтрального эталона",
    "vowel_boundaries": "интервалы и метки обнаруженных гласных",
    "frequencies": "частоты или последовательности частот",
    "times": "временные координаты, с",
    "bandwidths": "ширины частотных полос, Гц",
    "intensities": "значения интенсивности",
    "duration": "длительность, с",
    "delta_time": "шаг времени, с",
    "gender": "пол или голосовая категория, используемая моделью",
    "height": "рост, используемый физической моделью",
}


def clean_doc(text: str | None) -> str:
    if not text:
        return ""
    paragraph = re.split(r"\n\s*\n|\n\s*:param|\n\s*:return|\n\s*Args:", text.strip(), maxsplit=1)[0]
    return " ".join(line.strip() for line in paragraph.splitlines()).strip()


def doc_params(text: str | None) -> dict[str, str]:
    if not text:
        return {}
    result: dict[str, str] = {}
    for name, description in re.findall(r":param\s+([\w_]+)\s*:\s*([^\n]+)", text):
        result[name] = description.strip()
    return result


def purpose(name: str, doc: str | None) -> str:
    documented = clean_doc(doc)
    if documented:
        return documented
    exact = {
        "save": "Сохраняет объект в файл и возвращает путь к созданному файлу.",
        "load": "Загружает объект из файла.",
        "from_file": "Читает аудиофайл и извлекает из него признаки.",
        "extract": "Извлекает признаки из массива аудиосэмплов.",
        "to_csv": "Сохраняет временную последовательность в CSV.",
    }
    if name in exact:
        return exact[name]
    actions = {
        "is_": "Проверяет, соответствует ли сигнал заданному режиму речи.",
        "get_": "Получает рассчитанное представление или характеристику.",
        "extract_": "Извлекает признак или временную последовательность из сигнала.",
        "calculate_": "Рассчитывает указанную акустическую или физическую характеристику.",
        "compute_": "Вычисляет указанную характеристику.",
        "change_": "Изменяет указанное свойство аудиосигнала.",
        "modify_": "Изменяет указанное свойство аудиосигнала.",
        "apply_": "Применяет указанное преобразование или фильтр.",
        "analyze_": "Анализирует сигнал и возвращает связанные показатели.",
        "detect_": "Обнаруживает указанные события или интервалы.",
        "find_": "Находит указанные элементы или интервалы.",
        "remove_": "Удаляет или подавляет указанную составляющую.",
        "filter_": "Фильтрует входные данные по заданным условиям.",
        "plot_": "Строит график указанной характеристики.",
        "visualize_": "Визуализирует указанную характеристику или сравнение.",
        "generate_": "Генерирует сигнал или последовательность параметров.",
        "create_": "Создаёт структуру данных, маску или сигнал.",
        "load_": "Загружает данные из файла.",
        "save_": "Сохраняет результат в файл.",
        "process_": "Выполняет полный цикл обработки входных данных.",
        "classify_": "Классифицирует входную структуру.",
        "compare_": "Сравнивает входные структуры.",
        "simplify_": "Упрощает входную последовательность паттернов.",
        "print_": "Выводит данные в читаемом виде.",
        "normalize": "Нормализует входное значение или сигнал.",
        "normalize_": "Нормализует входное значение или сигнал.",
        "amplify_": "Усиливает выбранные составляющие сигнала.",
        "boost_": "Усиливает выбранные частотные составляющие.",
        "stretch_": "Изменяет длительность выбранных участков сигнала.",
        "scale_": "Масштабирует указанную характеристику.",
        "mix_": "Смешивает несколько сигналов или представлений.",
        "combine_": "Объединяет несколько сигналов или представлений.",
        "trim_": "Обрезает сигнал по заданному условию.",
        "train_": "Обучает адаптивный компонент на эталонных данных.",
        "update": "Обновляет внутреннее состояние модели.",
        "update_": "Обновляет внутреннее состояние или накопленную статистику.",
        "draw": "Рисует текущее состояние модели.",
    }
    for prefix, description in actions.items():
        if name.startswith(prefix):
            return description
    return f"Выполняет операцию `{name}` над переданными данными."


class ReturnCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.values: list[ast.expr | None] = []
        self.yields = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Return(self, node: ast.Return) -> None:
        self.values.append(node.value)

    def visit_Yield(self, node: ast.Yield) -> None:
        self.yields = True


def output_description(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    collector = ReturnCollector()
    for statement in node.body:
        collector.visit(statement)
    name = node.name
    if node.returns is not None:
        annotation = ast.unparse(node.returns).strip("'\"")
        return f"`{annotation}`"
    if collector.yields:
        return "контекстный итератор или последовательность значений"
    values = [value for value in collector.values if value is not None]
    if not values:
        if name.startswith(("plot_", "visualize_", "print_", "save", "draw", "update", "process_wav", "set_speed", "shift_formants_vowels", "apply_adaptive_filter", "change_volume_linear")):
            return "`None`; результат отображается, записывается в файл или сохраняется во внутреннем состоянии"
        return "`None`; функция изменяет состояние объекта или выполняет побочный эффект"
    text = " | ".join(dict.fromkeys(ast.unparse(value) for value in values))
    if any(isinstance(value, ast.Dict) for value in values):
        return "`dict` со структурированными результатами расчёта"
    if any(isinstance(value, ast.Tuple) for value in values):
        tuples = [value for value in values if isinstance(value, ast.Tuple)]
        names = ", ".join(ast.unparse(item) for item in tuples[0].elts)
        return f"`tuple` со значениями: `{names}`"
    if name.startswith("is_") or set(text.split(" | ")) <= {"True", "False"}:
        return "`bool` — результат проверки"
    if "np.array" in text or "np.concatenate" in text or "np.convolve" in text or "_signal" in text or text in {"y", "y_filtered", "y_shifted", "audio_signal", "signal"}:
        return "`numpy.ndarray` — рассчитанный или преобразованный сигнал/ряд"
    if any(token in text for token in ("PitchTrack(", "NormalizedPitchTrack(", "PitchProfile(")):
        match = re.search(r"(PitchTrack|NormalizedPitchTrack|PitchProfile)\(", text)
        return f"`{match.group(1)}`" if match else "объект модели данных"
    if name.startswith(("classify_", "determine_")):
        return "`str` — метка или текстовый результат классификации"
    if name.startswith(("calculate_", "compute_", "get_frequency", "get_tract_length", "find_max", "transition", "normalize")):
        return "числовое значение, массив либо структура, указанная в описании метода"
    if len(text) <= 100:
        return f"результат выражения `{text}`"
    return "рассчитанные данные; конкретная структура определяется указанной сигнатурой и назначением метода"


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef, drop_receiver: bool = False) -> str:
    arguments = ast.unparse(node.args)
    if drop_receiver:
        arguments = re.sub(r"^(self|cls)(,\s*)?", "", arguments)
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    result = f"{prefix}{node.name}({arguments})"
    if node.returns is not None:
        result += f" -> {ast.unparse(node.returns)}"
    return result


def describe_parameter(name: str, parsed: dict[str, str]) -> str:
    if name in parsed:
        return parsed[name]
    if name in PARAMETERS:
        return PARAMETERS[name]
    if name.startswith("output_") or name.endswith("_output"):
        return "путь или контейнер для выходных данных"
    if name.startswith("input_"):
        return "входные данные или путь к ним"
    if "threshold" in name:
        return "порог принятия решения"
    if "factor" in name or "ratio" in name or "percent" in name:
        return "коэффициент или доля преобразования"
    if "freq" in name:
        return "частота или последовательность частот, Гц"
    if "bandwidth" in name or name.startswith("bw"):
        return "ширина полосы или набор ширин, Гц"
    if "amplitude" in name:
        return "амплитуда или коэффициент амплитуды"
    if "energy" in name:
        return "энергия или коэффициент энергии"
    if "intensity" in name:
        return "интенсивность или её параметры"
    if "time" in name or "period" in name or "duration" in name:
        return "временной параметр, с, если функция не указывает другую единицу"
    if "formant" in name:
        return "данные или параметры формант"
    if "pitch" in name or "f0" in name:
        return "данные или параметры основного тона F0"
    if name.startswith("file_") or name.startswith("folder_") or name.endswith("_file") or name.endswith("_path"):
        return "путь к файлу или каталогу"
    if name in {"data", "values", "value", "params", "current", "phonema", "phonems"}:
        return "входные данные соответствующего метода"
    return f"входной параметр `{name}`"


def function_block(node: ast.FunctionDef | ast.AsyncFunctionDef, *, owner: str | None = None) -> list[str]:
    shown_name = f"{owner}.{node.name}" if owner else node.name
    lines = [f"#### `{shown_name}`", "", "```python", signature(node, drop_receiver=owner is not None), "```", ""]
    lines += [purpose(node.name, ast.get_docstring(node)), ""]
    parsed = doc_params(ast.get_docstring(node))
    args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    args = [arg for arg in args if arg.arg not in {"self", "cls"}]
    if node.args.vararg:
        args.append(node.args.vararg)
    if node.args.kwarg:
        args.append(node.args.kwarg)
    if args:
        lines.append("**Параметры:**")
        lines.append("")
        for arg in args:
            annotation = f" (`{ast.unparse(arg.annotation)}`)" if arg.annotation is not None else ""
            lines.append(f"- `{arg.arg}`{annotation} — {describe_parameter(arg.arg, parsed)}.")
        lines.append("")
    lines += [f"**Возвращает:** {output_description(node)}.", ""]
    return lines


def class_constructor(node: ast.ClassDef) -> str:
    init = next((item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == "__init__"), None)
    if init:
        args = re.sub(r"^self(,\s*)?", "", ast.unparse(init.args))
        return f"{node.name}({args})"
    fields = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            default = f" = {ast.unparse(item.value)}" if item.value is not None else ""
            fields.append(f"{item.target.id}: {ast.unparse(item.annotation)}{default}")
    return f"{node.name}({', '.join(fields)})"


def render() -> str:
    lines = [
        "# API пакета `sk_speech`",
        "",
        "Эта справка описывает публичные классы, функции и методы пакета по их фактическим сигнатурам в исходном коде.",
        "",
        "## Соглашения",
        "",
        "- `y`, `signal`, `audio_data` — одномерный массив аудиосэмплов `numpy.ndarray`;",
        "- `sr`, `fs`, `sample_rate` — частота дискретизации в герцах;",
        "- F0 и частоты формант задаются в герцах;",
        "- временные значения задаются в секундах, если явно не указаны сэмплы;",
        "- функции преобразования обычно возвращают новый сигнал и не изменяют входной массив;",
        "- варианты методов с суффиксами `2`, `3` и далее являются отдельными алгоритмами и сохраняются как самостоятельные публичные функции.",
        "",
        "## Навигация по модулям",
        "",
        "| Модуль | Область |",
        "|---|---|",
    ]
    for relative, (title, _) in MODULES.items():
        module = relative.removesuffix(".py").replace("/", ".")
        anchor = title.lower().replace(" ", "-").replace("–", "")
        lines.append(f"| `sk_speech.{module}` | [{title}](#{anchor}) |")
    lines.append("")

    for relative, (title, summary) in MODULES.items():
        path = SOURCE / relative
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        module = relative.removesuffix(".py").replace("/", ".")
        lines += [f"## {title}", "", f"Модуль: `sk_speech.{module}`.", "", summary, ""]
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                lines += [f"### Класс `{node.name}`", "", clean_doc(ast.get_docstring(node)) or "Контейнер данных или модель состояния.", "", "```python", class_constructor(node), "```", ""]
                public_methods = [item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_")]
                for method in public_methods:
                    lines.extend(function_block(method, owner=node.name))
        functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")]
        if functions:
            lines += ["### Функции", ""]
            for function in functions:
                lines.extend(function_block(function))
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"written: {OUTPUT}")
