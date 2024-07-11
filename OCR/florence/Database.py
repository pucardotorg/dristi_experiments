import json
import os
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from dotenv import load_dotenv
import random
from string import ascii_uppercase
import io

load_dotenv()

ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
BUCKET_NAME = os.environ.get('OCR_BUCKET_NAME')
MINIO_HOST = os.environ.get('MINIO_HOST')

class Database:
    def __init__(self):
        self.minio_client = Minio(MINIO_HOST, ACCESS_KEY, SECRET_KEY, secure=True)
        self.session_file_path = os.environ.get('SESSION_FILE_PATH', '/app/session.json')
        self.uid = None

    def upload_image_file(self, file_name, file_path):
        try:
            self.minio_client.fput_object(BUCKET_NAME, file_name, file_path, content_type="image/jpeg")
        except S3Error as e:
            print(f"Error uploading image: {e}")
            raise

    def upload_json_file(self, file_name, json_data):
        try:
            json_str = json.dumps(json_data)
            json_bytes = json_str.encode('utf-8')
            self.minio_client.put_object(BUCKET_NAME, file_name, io.BytesIO(json_bytes), len(json_bytes), content_type="application/json")
        except S3Error as e:
            print(f"Error uploading JSON: {e}")
            raise


    def generate_unique_code(self, length):
        while True:
            code = ''.join(random.choice(ascii_uppercase) for _ in range(length))
            if os.path.exists(self.session_file_path):
                with open(self.session_file_path, 'r') as f:
                    session_data = json.load(f)
                if not any(code in entry['filename'] for entry in session_data):
                    break
            else:
                break
        self.uid = code
        return code

    def upload_data(self, image_path, additional_info):
        try:
            unique_id = self.generate_unique_code(6)
            image_file_name = f"{unique_id}_ocr.jpg"
            self.upload_image_file(image_file_name, image_path)
            json_file_name = f"{unique_id}_info_ocr.json"
            json_data = {
                "image_file_name": image_file_name,
                "additional_info": additional_info
            }
            self.upload_json_file(json_file_name, json_data)
            print("Uploaded successfully")

        except Exception as error:
            print(f"Failed to upload data: {error}")
        return self.uid