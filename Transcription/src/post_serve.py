from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import glob
from pydub import AudioSegment
from faster_whisper import WhisperModel

def transcribe_file(file_path, model_size="large-v3", device="cuda", compute_type="float16"):
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _ = model.transcribe(file_path)
    transcript = " ".join([segment.text for segment in segments])
    return transcript

# Example usage

def find_client_directory(base_path, client_id):
    for root, dirs, files in os.walk(base_path):
        print(dirs)
        if client_id in dirs:
            return os.path.join(root, client_id)
    return None

def merge_wav_files(wav_files):
    combined = AudioSegment.empty()
    for wav_file in sorted(wav_files):
        sound = AudioSegment.from_wav(wav_file)
        combined += sound
    return combined

def save_merged_wav(merged_wav, output_path):
    merged_wav.export(output_path, format="wav")

def merge(base_path, client_id, len):
    # Find the client directory
    client_dir = find_client_directory(base_path, client_id)
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
    output_filename = f"{client_id}_{len}.wav"
    output_path = os.path.join(os.path.dirname(client_dir), output_filename)

    # Save the merged wav file
    save_merged_wav(merged_wav, output_path)

    print(f"Merged file saved as {output_path}")


def write_txt_file(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)
def create_app():
    app = Flask(__name__)
    CORS(app)
    @app.route('/submit', methods=['POST'])
    def submit():
        data = request.json
        original_text = data.get('original', '')
        edited_text = data.get('edited', '')
        client_id = data.get('client_id', '')
        start = data.get('start_time', '')
        end = data.get('end_time', '')
        print(f"Client ID: {client_id}")

        print(original_text)
 
        len = start[0]*3600 + start[1]*60 + start[2] - end[0]*3600 + end[1]*60 + end[2]
        print(len)
        filename = f"{client_id}_{len}_modified.txt"
        write_txt_file(os.path.join("../modified_text_files", filename), edited_text)
        filename_orig = f"{client_id}_{len}original.txt"
        write_txt_file(os.path.join("../original_text_files", filename_orig), original_text)
        merge("../audio_uploads",client_id,len)
        response = {
            'message': 'Data received and saved in minio bucket.'
        }
        
        return jsonify(response)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)