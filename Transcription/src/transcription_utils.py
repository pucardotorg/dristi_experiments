import os
from pydub import AudioSegment
import glob
import shutil
import json
import requests

def create_directories():
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    original_text_files_dir = os.path.join(project_dir, 'original_text_files')
    modified_text_files_dir = os.path.join(project_dir, 'modified_text_files')

    os.makedirs(original_text_files_dir, exist_ok=True)
    os.makedirs(modified_text_files_dir, exist_ok=True)

def append_transcription(room_id, text):
    file_name = f"{room_id}_original.txt"
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Define the path to the text_files directory
    text_files_dir = os.path.join(project_dir, 'original_text_files')
    text_file_path = os.path.join(text_files_dir, file_name)
    with open(text_file_path, 'a') as f:
        f.write(text)

    file_name = f"{room_id}_modified.txt"
    text_files_dir = os.path.join(project_dir, 'modified_text_files')
    text_file_path = os.path.join(text_files_dir, file_name)
    with open(text_file_path, 'a') as f:
        f.write(text)


def read_transcription(room_id):
    file_name = f"{room_id}_modified.txt"
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Define the path to the text_files directory
    text_files_dir = os.path.join(project_dir, 'modified_text_files')
    text_file_path = os.path.join(text_files_dir, file_name)
    with open(text_file_path) as f:
        text = f.read()
        return text


def update_transcription_file(room_id, file_type, text):
    file_name = f"{room_id}_{file_type}.txt"
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Define the path to the text_files directory
    text_files_dir = os.path.join(project_dir, f'{file_type}_text_files')
    text_file_path = os.path.join(text_files_dir, file_name)
    with open(text_file_path, 'w') as f:
        f.write(text)


def find_client_directory(client_id):
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../audio_uploads'))
    if os.path.exists(os.path.join(project_dir, client_id)):
        return os.path.join(project_dir, client_id)
    return None


def merge_wav_files(wav_files):
    combined = AudioSegment.empty()
    for wav_file in sorted(wav_files):
        sound = AudioSegment.from_wav(wav_file)
        combined += sound
    return combined


def save_merged_wav(merged_wav, output_path):
    merged_wav.export(output_path, format="wav")


def merge(client_id):
    # Find the client directory
    client_dir = find_client_directory(client_id)

    if client_dir is None:
        print(f"Directory for client_id {client_id} not found.")
        return

    # Find all .wav files in the client directory
    wav_files = glob.glob(os.path.join(client_dir, "*.wav"))
    if not wav_files:
        print(f"No .wav files found in directory {client_dir}.")
        return

    # Merge all .wav files
    merged_wav = merge_wav_files(wav_files)

    # Create output file name
    output_filename = f"{client_id}.wav"
    output_path = os.path.join(os.path.dirname(client_dir), output_filename)

    # Save the merged wav file
    save_merged_wav(merged_wav, output_path)

    print(f"Merged file saved as {output_path}")


def save_audio_file(file_path):
    identifier = file_path.split('/')[1].split('_')[0]
    dest_folder_path = f"audio_uploads/{identifier}"
    os.makedirs(dest_folder_path, exist_ok=True)
    dest_file_path = os.path.join(dest_folder_path, os.path.basename(file_path))
    shutil.copy2(file_path, dest_file_path)

def process_kenlm_transcription(asr_transcription):
    kenlm_url = os.getenv('KENLM_URL')
    payload = json.dumps({
        "text": asr_transcription,
        "BEAM_WIDTH": 5,
        "SCORE_THRESHOLD": 1.5,
        "max_distance": 1,
        "lang": "eng"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", kenlm_url, headers=headers, data=payload)
    return response.text
