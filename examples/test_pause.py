import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from hdbscan import HDBSCAN
from sklearn.cluster import DBSCAN
from scipy.stats import skew
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.mixture import BayesianGaussianMixture
from sklearn.neighbors import KernelDensity
from sklearn.cluster import KMeans
from sk_speech import sk_noise as ns
from sk_speech import sk_filters as fl
from collections import Counter

def cluster_pauses(pause_info, max_clusters=3):
    """
    Кластеризует паузы по их длительности и возвращает информацию о кластерах.

    Параметры:
        pause_info (list): Список пауз, где каждый элемент [duration, start, end].
        max_clusters (int): Максимальное количество кластеров для анализа.

    Возвращает:
        dict: Информация о кластерах, содержащая центры, минимальные и максимальные границы.
    """
    # Извлекаем только длительности пауз
    durations = np.array([p[0] for p in pause_info]).reshape(-1, 1)

    # Кластеризация с оптимальным числом кластеров
    try:
        kmeans = KMeans(n_clusters=max_clusters, random_state=42)
        labels = kmeans.fit_predict(durations)
        cluster_centers = kmeans.cluster_centers_.flatten()
    except:
        return []

    # Сбор информации о кластерах
    cluster_info = []
    for cluster_id in range(max_clusters):
        # Фильтрация длительностей, принадлежащих текущему кластеру
        cluster_durations = durations[labels == cluster_id].flatten()

        # Проверка, чтобы избежать пустых кластеров
        if len(cluster_durations) > 0:
            cluster_info.append({
                "center": cluster_centers[cluster_id],
                "min": np.min(cluster_durations),
                "max": np.max(cluster_durations),
            })


    # Сортировка кластеров по "center"
    cluster_info = sorted(cluster_info, key=lambda x: x["center"])

    return cluster_info

def kmeans_with_normalization(pause_info, max_clusters=3):
    durations = np.array([p[0] for p in pause_info])
    median_duration = np.median(durations)
    durations = durations / median_duration  # Нормализация
    durations = durations.reshape(-1, 1)

    try:
        kmeans = KMeans(n_clusters=max_clusters, random_state=42)
        labels = kmeans.fit_predict(durations)
        cluster_centers = kmeans.cluster_centers_.flatten()
    except:
        return []

    is_noise = False
    for cluster_id in range(max_clusters):
        cluster_durations = durations[labels == cluster_id].flatten() * median_duration
        skewness = skew(cluster_durations)
        if abs(skewness) > 2:  # Слишком большая асимметрия
            # Кластер шумный
            is_noise = True
            break
    if is_noise:
        return []

    cluster_info = []
    for cluster_id in range(max_clusters):
        cluster_durations = durations[labels == cluster_id].flatten() * median_duration

        if len(cluster_durations) > 0:
            cluster_info.append({
                "center": np.mean(cluster_durations),
                "min": np.min(cluster_durations),
                "max": np.max(cluster_durations),
            })

    return sorted(cluster_info, key=lambda x: x["center"])

def cluster_pauses_DBSCAN(pause_info, eps=50, min_samples=2):
    """
    Кластеризует паузы по их длительности с использованием DBSCAN и возвращает информацию о кластерах.

    Параметры:
        pause_info (list): Список пауз, где каждый элемент [duration, start, end].
        eps (float): Максимальное расстояние между двумя образцами для их объединения в кластер.
        min_samples (int): Минимальное количество образцов в кластере.

    Возвращает:
        list: Информация о кластерах, содержащая центры, минимальные и максимальные границы.
    """
    # Извлекаем только длительности пауз
    durations = np.array([p[0] for p in pause_info]).reshape(-1, 1)

    # Кластеризация с использованием DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(durations)

    unique_labels = set(labels)
    cluster_info = []

    for label in unique_labels:
        if label == -1:  # Пропуск шума
            continue

        cluster_durations = durations[labels == label].flatten()
        cluster_info.append({
            "center": np.mean(cluster_durations),
            "min": np.min(cluster_durations),
            "max": np.max(cluster_durations),
        })

    # Сортировка кластеров по "center"
    cluster_info = sorted(cluster_info, key=lambda x: x["center"])

    return cluster_info

def adaptive_dbscan(pause_info, min_samples=2):
    durations = np.array([p[0] for p in pause_info]).reshape(-1, 1)
    median_duration = np.median(durations)
    eps = median_duration * 1.5  # Динамическое значение eps

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(durations)

    unique_labels = set(labels)
    cluster_info = []

    for label in unique_labels:
        if label == -1:  # Пропуск шума
            continue

        cluster_durations = durations[labels == label].flatten()
        cluster_info.append({
            "center": np.mean(cluster_durations),
            "min": np.min(cluster_durations),
            "max": np.max(cluster_durations),
        })

    return sorted(cluster_info, key=lambda x: x["center"])

def hierarchical_clustering(pause_info, max_distance=200):
    durations = np.array([p[0] for p in pause_info])

    try:
        # Создание дендрограммы
        Z = linkage(durations.reshape(-1, 1), method='ward')

        # Кластеризация на основе заданного порога расстояния
        labels = fcluster(Z, t=max_distance, criterion='distance')
    except:
        return []

    cluster_info = []
    unique_labels = set(labels)
    for label in unique_labels:
        cluster_durations = durations[labels == label]
        cluster_info.append({
            "center": np.mean(cluster_durations),
            "min": np.min(cluster_durations),
            "max": np.max(cluster_durations),
        })

    return sorted(cluster_info, key=lambda x: x["center"])

def bayesian_gmm_clustering(pause_info):
    durations = np.array([p[0] for p in pause_info]).reshape(-1, 1)

    try:
        bgmm = BayesianGaussianMixture(n_components=5, random_state=42)
        labels = bgmm.fit_predict(durations)
        cluster_centers = bgmm.means_.flatten()
    except:
        return []

    cluster_info = []
    unique_labels = set(labels)
    for label in unique_labels:
        cluster_durations = durations[labels == label].flatten()
        cluster_info.append({
            "center": np.mean(cluster_durations),
            "min": np.min(cluster_durations),
            "max": np.max(cluster_durations),
        })

    return sorted(cluster_info, key=lambda x: x["center"])

def process_wav_files(base_folder):
    speakers = []

    for root, dirs, files in os.walk(base_folder):
        for file_name in files:
            if file_name.endswith('.wav'):
                wav_path = os.path.join(root, file_name)
                speakers.append(wav_path)
    return speakers

def build_graph(counter):
    # Получение отсортированных ключей и значений из counter
    keys = list(counter.keys())
    values = list(counter.values())

    # Построение графика
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(keys, values, width=0.75, align='center', color='skyblue')

    # Добавление текста с точными значениями над каждым столбиком
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height * 1.01, f'{value}', ha='center', va='bottom')

    # Добавление заголовка и подписей осей
    ax.set_title('Частота встречаемости кол-ва слов')
    ax.set_xlabel('Кол-во слов')
    ax.set_ylabel('Частота')

    # Настройка положения меток на оси X
    ax.set_xticks(keys)

    # Отображение сетки
    ax.grid(axis='y')

    # Показ графика
    plt.show()

def HDBSCAN_pause_short(pause_short):
    index = np.zeros(len(pause_short), dtype=np.float32)
    data = np.column_stack((index, pause_short))

    # HDBSCAN
    # Инициализация HDBSCAN
    clusterer = HDBSCAN(min_cluster_size=100, min_samples=5, metric='euclidean')
    labels = clusterer.fit_predict(data)

    # Ядровая оценка плотности (KDE)
    kde = KernelDensity(kernel='gaussian', bandwidth=2.0).fit(data)
    density = np.exp(kde.score_samples(data))

    # Находим минимальное, максимальное значения и максимальную плотность
    min_value = np.min(pause_short)
    max_value = np.max(pause_short)
    max_density_index = np.argmax(density)
    x_max_density, y_max_density = data[max_density_index]

    # Визуализация результатов
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(data[:, 0], data[:, 1], c=density, cmap='viridis', alpha=0.8, edgecolor='k')
    cbar = fig.colorbar(ax.collections[0], label='Плотность')

    # Добавляем аннотации для минимального, максимального значений и максимальной плотности
    ax.annotate(f'Минимальная пауза: {min_value:.2f}',
                xy=(0, 0),
                xycoords='axes fraction',
                xytext=(0.05, 0.95),
                textcoords='axes fraction',
                horizontalalignment='left',
                verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w"))

    ax.annotate(f'Максимальная пауза: {max_value:.2f}',
                xy=(0, 0),
                xycoords='axes fraction',
                xytext=(0.05, 0.90),
                textcoords='axes fraction',
                horizontalalignment='left',
                verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w"))

    ax.annotate(f'Максимальная плотность ({y_max_density:.2f})',
                xy=(x_max_density, y_max_density),
                xytext=(-50, 20),  # Сдвигаем надпись левее
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"),  # Увеличиваем длину стрелки
                horizontalalignment='right',  # Левое выравнивание
                verticalalignment='bottom')

    ax.set_xlabel('Длительность паузы между словами')
    ax.set_ylabel('Плотность')
    ax.set_title('HDBSCAN + KDE: Плотность значений')

    plt.show()

def HDBSCAN_pause_long(pause_long):
    index = np.zeros(len(pause_long), dtype=np.float32)
    data = np.column_stack((index, pause_long))

    # HDBSCAN
    # Инициализация HDBSCAN
    clusterer = HDBSCAN(min_cluster_size=100, min_samples=5, metric='euclidean')
    labels = clusterer.fit_predict(data)

    # Ядровая оценка плотности (KDE)
    kde = KernelDensity(kernel='gaussian', bandwidth=2.0).fit(data)
    density = np.exp(kde.score_samples(data))

    # Находим минимальное, максимальное значения и максимальную плотность
    min_value = np.min(pause_long)
    max_value = np.max(pause_long)
    max_density_index = np.argmax(density)
    x_max_density, y_max_density = data[max_density_index]

    # Визуализация результатов
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(data[:, 0], data[:, 1], c=density, cmap='viridis', alpha=0.8, edgecolor='k')
    cbar = fig.colorbar(ax.collections[0], label='Плотность')

    # Добавляем аннотации для минимального, максимального значений и максимальной плотности
    ax.annotate(f'Минимальная пауза: {min_value:.2f}',
                xy=(0, 0),
                xycoords='axes fraction',
                xytext=(0.05, 0.95),
                textcoords='axes fraction',
                horizontalalignment='left',
                verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w"))

    ax.annotate(f'Максимальная пауза: {max_value:.2f}',
                xy=(0, 0),
                xycoords='axes fraction',
                xytext=(0.05, 0.90),
                textcoords='axes fraction',
                horizontalalignment='left',
                verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w"))

    ax.annotate(f'Максимальная плотность ({y_max_density:.2f})',
                xy=(x_max_density, y_max_density),
                xytext=(-50, 20),  # Сдвигаем надпись левее
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"),  # Увеличиваем длину стрелки
                horizontalalignment='right',  # Левое выравнивание
                verticalalignment='bottom')

    plt.xlabel('Длительность паузы на вдохе')
    plt.ylabel('Плотность')
    plt.title('HDBSCAN + KDE: Плотность значений')

    plt.show()

def HDBSCAN_word_count(word_count):
    index = np.zeros(len(word_count), dtype=np.float32)
    data = np.column_stack((index, word_count))

    # HDBSCAN
    # Инициализация HDBSCAN
    clusterer = HDBSCAN(min_cluster_size=100, min_samples=5, metric='euclidean')
    labels = clusterer.fit_predict(data)

    # Ядровая оценка плотности (KDE)
    kde = KernelDensity(kernel='gaussian', bandwidth=2.0).fit(data)
    density = np.exp(kde.score_samples(data))

    # Находим минимальное, максимальное значения и максимальную плотность
    min_value = np.min(word_count)
    max_value = np.max(word_count)
    max_density_index = np.argmax(density)
    x_max_density, y_max_density = data[max_density_index]

    # Визуализация результатов
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(data[:, 0], data[:, 1], c=density, cmap='viridis', alpha=0.8, edgecolor='k')
    cbar = fig.colorbar(ax.collections[0], label='Плотность')

    # Добавляем аннотации для минимального, максимального значений и максимальной плотности
    ax.annotate(f'Минимальное значение: {min_value:.2f}',
                xy=(0, 0),
                xycoords='axes fraction',
                xytext=(0.05, 0.95),
                textcoords='axes fraction',
                horizontalalignment='left',
                verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w"))

    ax.annotate(f'Максимальная значение: {max_value:.2f}',
                xy=(0, 0),
                xycoords='axes fraction',
                xytext=(0.05, 0.90),
                textcoords='axes fraction',
                horizontalalignment='left',
                verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w"))

    ax.annotate(f'Максимальная плотность ({y_max_density:.2f})',
                xy=(x_max_density, y_max_density),
                xytext=(-50, 20),  # Сдвигаем надпись левее
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"),  # Увеличиваем длину стрелки
                horizontalalignment='right',  # Левое выравнивание
                verticalalignment='bottom')

    plt.xlabel('Кол-во слов на выдохе')
    plt.ylabel('Плотность')
    plt.title('HDBSCAN + KDE: Плотность значений')

    plt.show()

def find_word_boundaries(audio_file, max_pause_duration):
    # audio_file = 'dataset/speaker_seg/speaker_27032/caller-de720617b19d40d2c087680a6b884b38-1640464113-in_1.wav'
    # audio_file = 'dataset/speaker_seg/speaker_868/caller-f4dcd85f20455a7fd7dbc9c38f9aee55-1636961941-in_4.wav' # 22
    # audio_file = 'dataset/speaker_seg/speaker_10064/caller-d93c5c4c7f996f42edf27cb46018b961-1637927887-in_6.wav' # 28
    # audio_file = 'dataset/speaker_seg/speaker_5126/caller-d20acc3ba47cd3cb232e05a87c3a95f7-1638152943-in_1.wav' # 18
    # audio_file = 'dataset/speaker_seg/speaker_12738/caller-9358c05d92b5dce3809595112b75f198-1638366752-in_1.wav' # 14
    # Загружаем аудиофайл
    y, sr = librosa.load(audio_file)

    # y, sr = pt.flatten_pitch(y, sr)
    # if y is None:
    #     return [], [], []
    y = np.array(y)
    y = y.astype(np.float32)
    if y.size == 0:
        return [], [], []
    y = ns.noise_reduction_spectral_subtraction_fast(y, sr)
    if y is None:
        return [], [], []
    y = fl.normalize_audio(y)

    # Находим тишину в сигнале
    try:
        top_db = min(20, np.percentile(librosa.amplitude_to_db(np.abs(y)), 90) - np.percentile(librosa.amplitude_to_db(np.abs(y)), 10))
    except:
        top_db = 20
    # top_db = 20
    intervals = librosa.effects.split(y, top_db=top_db)

    pause_info = []
    for i in range(0, len(intervals)-1):
        start = intervals[i][1] * 1000.0 / sr
        end = intervals[i + 1][0] * 1000.0 / sr
        duration = (end - start)
        # duration = min(duration, max_pause_duration)
        pause_info.append([duration, start, end])
    if len(pause_info) == 0:
        return [], [], []
    # pause_info = np.array(pause_info)
    # max_pause = pause_info < max_pause_duration
    # pause_info_norm = pause_info[max_pause]
    # if pause_info_norm.size < 2:
    #     return [], [], []

    # pause_info[pause_info == max_pause_duration] = np.max(pause_info_norm)

    cluster_info = cluster_pauses(pause_info)
    # cluster_info = kmeans_with_normalization(pause_info)
    if len(cluster_info) < 2:
        return [], [], []

    pause_short_center = cluster_info[0]["center"]
    pause_short_min = cluster_info[0]["min"]
    pause_short_max = cluster_info[0]["max"]

    pause_long_center = cluster_info[1]["center"]
    pause_long_min = cluster_info[1]["min"]
    pause_long_max = 99999

    # Вычисляем длительность пауз между словами
    pause_short = []
    pause_long = []
    pause_short_durations = []
    pause_long_durations = []
    for i in range(0, len(intervals)-1):
        start = intervals[i][1] * 1000.0 / sr
        end = intervals[i + 1][0] * 1000.0 / sr
        duration = (end - start)
        # duration = min(duration, max_pause_duration)
        if pause_short_min <= duration <= pause_short_max:
            pause_short.append([duration, start, end])
            pause_short_durations.append(duration)
        if pause_long_min <= duration <= pause_long_max:
            pause_long.append([duration, start, end])
            pause_long_durations.append(duration)
    if len(pause_long) == 0:
        return [], [], []

    # Массив для хранения количества коротких пауз между длинными паузами
    pause_count = []
    last_time_start = 0
    for long_pause in pause_long:
        count = 0
        long_start = long_pause[1]

        for short_pause in pause_short:
            short_start = short_pause[1]
            short_end = short_pause[2]
            if last_time_start <= short_start and short_end <= long_start:
                count += 1

        if count > 0:
            pause_count.append(count)
        last_time_start = long_pause[2]

    # учитываем паузы на конце
    long_start = 99999999
    count = 0
    for short_pause in pause_short:
        short_start = short_pause[1]
        short_end = short_pause[2]
        if last_time_start <= short_start and short_end <= long_start:
            count += 1

    if count > 0:
        pause_count.append(count)

    if len(pause_count) == 0:
        return [], [], []

    if np.max(pause_count) > 8:
        print(f'{np.max(pause_count)}: {audio_file}')
    return pause_short_durations, pause_long_durations, pause_count

# folder = 'd:/projects/animals/cat'
# folder = 'd:/projects/animals/dolphin_audio'
# folder = 'd:/projects/animals/Шимпанзе'
# folder = 'd:/projects/animals/Ворона'
# folder = 'c:/projects/pack'
# folder = 'Животные/Пингвины'
# folder = 'Животные/геккон'
# folder = 'Животные/пчелы'
# folder = 'Животные/Шимпанзе'
# folder = 'Животные/Киты'
# folder = 'Животные/крокодил'
# folder = 'Животные/попугай'
# folder = 'Животные/шмель'
# folder = 'Животные/Ветер'
# folder = 'Животные/Дождь'
folder = 'Животные/cat'
# folder = 'Животные/dolphin_audio'
# folder = 'Животные/Ворона'
# folder = 'Животные/Синицы'
# folder = 'Животные/Летучие мыши'
# folder = 'dataset/source'
# folder = 'dataset/speaker_seg'
# folder = 'слон/мама_мыла'
files = process_wav_files(folder)

# max_pause_duration = 3001
# max_pause_duration = 801
max_pause_duration = 1501

pause_short = []
pause_long = []
pause_count = []
for index, audio_path in enumerate(files):
    pause_short_durations, pause_long_durations, pause_short_count = find_word_boundaries(audio_path, max_pause_duration)

    if len(pause_short_count) > 0:
        pause_short_durations = np.array(pause_short_durations)
        pause_long_durations = np.array(pause_long_durations)
        pause_short_count = np.array(pause_short_count)

        pause_short.extend(pause_short_durations)
        pause_long.extend(pause_long_durations)
        pause_count.extend(pause_short_count)

pause_short = np.array(pause_short)
pause_long = np.array(pause_long)
pause_count = np.array(pause_count)
word_count = pause_count + 1

# print(f"Кол-во пауз между словами (Vosk): {len(vosk_results)}")
print(f"Кол-во пауз между словами (тишина): {len(pause_short)}")
print(f"Кол-во пауз вдохов (тишина): {len(pause_long)}")
print(f"Среднее кол-во слов на выдохе: {np.mean(pause_count)+1}")
print(f"Максимальное кол-во слов на выдохе: {np.max(pause_count)+1}")

mask = np.all([pause_long < max_pause_duration], axis=0)
pause_long = pause_long[mask] # убираем паузы которые выходит за норму

mask = np.all([word_count > 2], axis=0)
word_count = word_count[mask] # убираем одиночные и два слова, так как мешают масштабу статистики

# Подсчет количества каждого элемента
counter = Counter(word_count)
counter = dict(sorted(counter.items())) # сортировка по кол-ву пауз

# Вывод результата
for key, value in counter.items():
    print(f"{key} - встречается {value} раз")

# Вызов функции
build_graph(counter)

# Гистограмма распределения пауз между словами
n, bins, patches = plt.hist(pause_short, bins=30, color='skyblue', edgecolor='black')

# Вычисление среднего значения для каждой группы данных
means = []
for i in range(len(bins) - 1):
    mean = pause_short[(bins[i] <= pause_short) & (pause_short < bins[i + 1])].mean()
    means.append(mean)

# Получаем максимальные высоту столбца гистограммы
max_height = max([rect.get_height() for rect in patches])

# Добавляем метки со средними значениями над каждым столбцом
for rect, mean in zip(patches, means):
    height = rect.get_height()
    if not np.isnan(mean):
        # Добавляем случайное смещение к высоте метки
        random_offset = np.random.uniform(max_height * 0.05, max_height * 0.15)
        plt.text(rect.get_x() + rect.get_width() / 2., height + random_offset,
                 f'{mean:.2f}', ha='center', va='bottom', fontsize=8)

# Оформление графика
plt.xlabel('Длительность паузы')
plt.ylabel('Частота появления паузы')
plt.title('Гистограмма распределения пауз между словами')

plt.tight_layout()
plt.show()

# Гистограмма распределения пауз
n, bins, patches = plt.hist(pause_long, bins=30, color='skyblue', edgecolor='black')

# Вычисление среднего значения для каждой группы данных
means = []
for i in range(len(bins) - 1):
    mean = pause_long[(bins[i] <= pause_long) & (pause_long < bins[i + 1])].mean()
    means.append(mean)

# Получаем максимальные высоту столбца гистограммы
max_height = max([rect.get_height() for rect in patches])

# Добавляем метки со средними значениями над каждым столбцом
for rect, mean in zip(patches, means):
    height = rect.get_height()
    if not np.isnan(mean):
        # Добавляем случайное смещение к высоте метки
        random_offset = np.random.uniform(max_height * 0.05, max_height * 0.15)
        plt.text(rect.get_x() + rect.get_width() / 2., height + random_offset,
                 f'{mean:.2f}', ha='center', va='bottom', fontsize=8)

# Оформление графика
plt.xlabel('Длительность паузы')
plt.ylabel('Частота появления паузы')
plt.title('Гистограмма распределения пауз вдоха')

plt.tight_layout()
plt.show()

# Гистограмма распределения пауз
n, bins, patches = plt.hist(word_count, bins=30, color='skyblue', edgecolor='black')

# Вычисление среднего значения для каждой группы данных
means = []
for i in range(len(bins) - 1):
    mean = word_count[(bins[i] <= word_count) & (word_count < bins[i + 1])].mean()
    means.append(mean)

# Получаем максимальные высоту столбца гистограммы
max_height = max([rect.get_height() for rect in patches])

# Добавляем метки со средними значениями над каждым столбцом
for rect, mean in zip(patches, means):
    height = rect.get_height()
    if not np.isnan(mean):
        # Добавляем случайное смещение к высоте метки
        random_offset = np.random.uniform(max_height * 0.05, max_height * 0.15)
        plt.text(rect.get_x() + rect.get_width() / 2., height + random_offset,
                 f'{mean:.2f}', ha='center', va='bottom', fontsize=8)

# Оформление графика
plt.xlabel('Кол-во слов')
plt.ylabel('Частота появления кол-ва слов')
plt.title('Гистограмма распределения кол-ва слов на выдохе')

plt.tight_layout()
plt.show()


HDBSCAN_pause_short(pause_short)

HDBSCAN_pause_long(pause_long)

HDBSCAN_word_count(word_count)

