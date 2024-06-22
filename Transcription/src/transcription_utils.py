import os


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
    with open(text_file_path, 'r') as f:
        text = f.read()
        return text


def update_transcription(room_id, file_type, text):
    file_name = f"{room_id}_{file_type}.txt"
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Define the path to the text_files directory
    text_files_dir = os.path.join(project_dir, f'{file_type}_text_files')
    text_file_path = os.path.join(text_files_dir, file_name)
    with open(text_file_path, 'w') as f:
        f.write(text)