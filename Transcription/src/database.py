from minio import Minio
import os
import sqlite3
from dotenv import load_dotenv
from datetime import timedelta
from minio.error import S3Error

load_dotenv()

ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MINIO_HOST = os.environ.get('MINIO_HOST')


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("JanSarathi.db")
        self.minio_client = Minio(MINIO_HOST, ACCESS_KEY, SECRET_KEY, secure=True)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS JanSarathi (session_id STRING, audio_file TEXT, original_transcription TEXT, updated_transcription TEXT, start_time datetime, end_time datetime)")

    def upload_audio_file(self, file_name, file_path):
        try:
            self.minio_client.fput_object(BUCKET_NAME, file_name, file_path, content_type="audio/wav")
        except S3Error as e:
            print(f"Error occurred: {e}")
            return None

    def upload_text_file(self, file_name, file_path):
        try:
            self.minio_client.fput_object(BUCKET_NAME, file_name, file_path)
        except S3Error as e:
            print(f"Error occurred: {e}")
            return None

    def fetch_audio_file(self, room_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT audio_file FROM JanSarathi WHERE session_id = ?", (room_id,))
            result = cursor.fetchall()
            url = self.minio_client.presigned_get_object(BUCKET_NAME, result[0][0], expires=timedelta(days=1))
            return url
        except S3Error as e:
            print(f"Error occurred: {e}")
            return None

    def fetch_transcript_file(self, room_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT updated_transcription from JanSarathi WHERE session_id = '{room_id}'")
            result = cursor.fetchall()
            url = self.minio_client.presigned_get_object(BUCKET_NAME, result[0][0], expires=timedelta(days=1))
            return url
        except S3Error as e:
            print(f"Error occurred: {e}")
            return None

    def fetch_room_info(self, room_id):
        try:
            transcript_url = self.fetch_transcript_file(room_id)
            if transcript_url is None:
                transcript_url = ""
            audio_url = self.fetch_audio_file(room_id)
            print("Transcription Url ", transcript_url, audio_url)
            if audio_url is None:
                audio_url = ""
            message = {
                'room_id': room_id,
                'transcript_url': transcript_url,
                'audio_url': audio_url
            }
            return message
        except Exception as error:
            print("Failed to update session details", error)
            return {
                'room_id': room_id,
                'transcript_url': "",
                'audio_url': ""
            }

    def add_session(self, room_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO JanSarathi (session_id) VALUES ('{room_id}')")
            self.connection.commit()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)

    def update_session(self, room_id):
        try:

            project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            # Define the path to the text_files directory
            audio_file_name = f"{room_id}.wav"
            audio_file_dir = os.path.join(project_dir, 'audio_uploads')
            audio_file_path = os.path.join(audio_file_dir, audio_file_name)
            self.upload_audio_file(audio_file_name, audio_file_path)

            update_transcription_file_name = room_id + "_modified.txt"
            update_transcription_dir = os.path.join(project_dir, f'modified_text_files')
            update_file_path = os.path.join(update_transcription_dir, update_transcription_file_name)
            self.upload_text_file(update_transcription_file_name, update_file_path)

            original_transcription_file_name = room_id + "_original.txt"
            original_transcription_dir = os.path.join(project_dir, f'original_text_files')
            original_file_path = os.path.join(original_transcription_dir, original_transcription_file_name)
            self.upload_text_file(original_transcription_file_name, original_file_path)

            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE JanSarathi SET original_transcription = ?, audio_file = ?, updated_transcription = ? WHERE session_id = ?",
                (original_transcription_file_name, audio_file_name, update_transcription_file_name, room_id))
            self.connection.commit()
        except Exception as error:
            print("Failed to update session details", error)
