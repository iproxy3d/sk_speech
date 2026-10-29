import os
import shutil
import re


# Функция для извлечения hash из имени файла
# def extract_unique_id(file_name):
#     match = re.search(r'([a-f0-9]{32}-\d+)', file_name)
#     return match.group(1) if match else None

def extract_unique_id(file_name):
    match = re.search(r'([a-f0-9]{32})', file_name)
    return match.group(1) if match else None

# Функция для загрузки списка спикеров из файла
def load_speakers(file_path):
    speakers = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                id_, hash_ = line.strip().split(',')
                speakers.append((int(id_), hash_))
    return speakers


# Функция для сохранения списка спикеров в файл
def save_speakers(speakers, file_path):
    with open(file_path, 'w') as f:
        for id_, hash_ in speakers:
            f.write(f"{id_},{hash_}\n")


# Функция для обработки файлов
def process_wav_files(base_folder, dest_folder, speakers_file):
    speakers = load_speakers(speakers_file)

    max_id = max([s[0] for s in speakers], default=0)  # Определяем максимальный id

    for root, dirs, files in os.walk(base_folder):
        for file_name in files:
            if file_name.endswith('.wav'):
                wav_path = os.path.join(root, file_name)
                file_hash = extract_unique_id(file_name)

                if file_hash is None:
                    continue  # Пропускаем файлы с некорректными именами

                # Проверяем, существует ли спикер с таким hash
                speaker_id = None
                for id_, hash_ in speakers:
                    if hash_ == file_hash:
                        speaker_id = id_
                        break

                # Если спикера нет, добавляем его
                if speaker_id is None:
                    max_id += 1
                    speaker_id = max_id
                    speakers.append((speaker_id, file_hash))

                    # Сохраняем обновленный список спикеров
                    save_speakers(speakers, speakers_file)
                    print(f"speaker_id: {speaker_id} hash: {file_hash}")

                # Создаем папку для спикера, если она не существует
                speaker_folder = os.path.join(dest_folder, f"speaker_{speaker_id}")
                os.makedirs(speaker_folder, exist_ok=True)

                # Копируем файл в папку спикера
                new_file_path = os.path.join(speaker_folder, file_name)
                shutil.move(wav_path, new_file_path)

    # Сохраняем обновленный список спикеров
    save_speakers(speakers, speakers_file)


base_folder = 'source'
dest_folder = 'speaker'
speakers_file = os.path.join(dest_folder, 'list_speaker.txt')  # Путь к файлу с спикерами

# Запуск обработки
process_wav_files(base_folder, dest_folder, speakers_file)

