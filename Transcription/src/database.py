from minio import Minio
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
BUCKET_NAME= os.environ.get('BUCKET_NAME')

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("JanSarathi.db")
        self.minio_client = Minio("cdn.dev.bhasai.samagra.io", ACCESS_KEY, SECRET_KEY)
        self.connection.execute("CREATE TABLE IF NOT EXISTS JanSarathi (session_id STRING, audio_file TEXT, original_transcription TEXT, updated_transcription TEXT, startTime datetime, endTime dateTime)")

    def upload_audio_file(self, file_name, file_path):
        result = self.minio_client.fput_object(BUCKET_NAME, file_name, file_path)
        return result

    def upload_text_file(self, file_name, file_path):
        result = self.minio_client.fput_object(BUCKET_NAME, file_name, file_path)
        return result

    def fetch_audio_file(self, room_id):
        pass

    def fetch_transcript_file(self, room_id):
        pass

    def fetch_room_info(self, room_id):
        pass

    def add_session(self, room_id):
        result = self.connection.execute(f"INSERT INTO JanSarathi (session_id) VALUES ('{room_id}')")


    def update_session(self, room_id, audio_file_path, original_transcription_path, updated_transcription_path, start_time, end_time):
        audio_file_name = audio_file_path.split('/')[-1].split('.')[0]
        original_transcription_name = original_transcription_path.split('/')[-1].split('.')[0]
        updated_transcription_name = updated_transcription_path.split('/')[-1].split('.')[0]
        self.upload_text_file(original_transcription_name, original_transcription_path)
        self.upload_text_file(updated_transcription_name, updated_transcription_path)
        self.upload_audio_file(audio_file_name, audio_file_path)

        cursor = self.connection.execute(f"UPDATE JanSarathi SET original_transcription = {original_transcription_name}, audio_file = {audio_file_name}, updated_transcription = {updated_transcription_name} WHERE session_id = {room_id}")
