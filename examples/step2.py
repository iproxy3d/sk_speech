import os
from sk_speech import sk_volume as vm

def count_folders_in_directory(directory):
    folder_count = 0
    # Walk through the directory tree
    for root, dirs, files in os.walk(directory):
        folder_count += len(dirs)
    return folder_count

def count_wav_files_in_directory(directory):
    wav_file_count = 0
    # Walk through the directory tree
    for root, dirs, files in os.walk(directory):
        # Count .wav files
        wav_file_count += sum(1 for file in files if file.endswith('.wav'))
    return wav_file_count

def remove_empty_folders(directory):
    # Walk through the directory from the bottom to the top
    for root, dirs, files in os.walk(directory, topdown=False):
        # Check each subdirectory
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # Remove the directory if it is empty
            if not os.listdir(dir_path):
                print(f"Removing empty folder: {dir_path}")
                os.rmdir(dir_path)
def process_speaker_files(speaker_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Walk through the speaker directory
    is_start = False
    count = 0
    count_speaker = 0
    old_speaker_id = 0
    for root, dirs, files in os.walk(speaker_dir):
        for file in files:
            if file.endswith(".wav"):
                # Extract speaker ID from the folder name
                speaker_id = os.path.basename(root).split('_')[-1]
                count += 1
                if speaker_id != old_speaker_id:
                    count_speaker += 1
                old_speaker_id = speaker_id
                # if speaker_id == '2455':
                #     is_start = True
                print(f'speaker_id: {speaker_id} count: {count} count_speaker: {count_speaker}')
                # if not is_start:
                #     continue
                # Construct paths for the input file and output folder
                file_input = os.path.join(root, file)
                speaker_output_folder = os.path.join(output_dir, f'speaker_{speaker_id}')

                # Ensure the speaker-specific output folder exists
                os.makedirs(speaker_output_folder, exist_ok=True)

                # Process the audio file and store segments in the corresponding speaker folder
                vm.process_audio(file_input, speaker_output_folder, min_total_speech_duration=1.5)


# Define paths to the speaker directory and output directory for segments
speaker_dir = "speaker"
output_dir = "speaker_seg"

# Process all wav files in the speaker directory
process_speaker_files(speaker_dir, output_dir)

remove_empty_folders(output_dir)

folder_count = count_folders_in_directory(output_dir)
wav_file_count = count_wav_files_in_directory(output_dir)

print(f"Кол-во спикеров в '{output_dir}': {folder_count}")
print(f"кол-во аудио .wav файлов в '{output_dir}': {wav_file_count}")
