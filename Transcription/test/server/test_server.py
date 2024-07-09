import unittest
import os
import json
import asyncio
import websockets
import base64
from pydub import AudioSegment
from sentence_transformers import SentenceTransformer, util
import time
from src.server import Server
from src.vad.vad_factory import VADFactory
from src.asr.asr_factory import ASRFactory

class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asr_type = os.getenv('ASR_TYPE', 'bhashini')
        cls.vad_type = os.getenv('VAD_TYPE', 'pyannote')

    def setUp(self):
        self.vad_pipeline = VADFactory.create_vad_pipeline(self.vad_type)
        asr_pipeline_map = {
        "faster_whisper": ASRFactory.create_asr_pipeline("faster_whisper"),
        "whisper": ASRFactory.create_asr_pipeline("whisper"),
        "bhashini": ASRFactory.create_asr_pipeline("bhashini")
        }
        self.asr_pipeline = asr_pipeline_map
        self.server = Server(self.vad_pipeline, self.asr_pipeline, host='127.0.0.1', port=8765)
        self.annotations_path = os.path.join(os.path.dirname(__file__), "../audio_files/annotations.json")
        self.received_transcriptions = []
        self.similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    async def receive_messages(self, websocket):
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if 'text' in data:
                    self.received_transcriptions.append(data['text'])
                else:
                    pass
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"Error in receive_messages: {str(e)}")

    async def create_room(self):
        uri = "ws://127.0.0.1:8765"
        async with websockets.connect(uri) as websocket:
            create_room_message = {
                "type": "create_room",
                "room_id": None
            }
            await websocket.send(json.dumps(create_room_message))
            response = await websocket.recv()
            return json.loads(response)

    async def mock_client(self, audio_file):
        uri = "ws://127.0.0.1:8765"
        async with websockets.connect(uri) as websocket:
            create_room_message = {
                "type": "create_room",
                "room_id": None
            }
            await websocket.send(json.dumps(create_room_message))
            response = await websocket.recv()
            data = json.loads(response)
            self.room_id = data['room_id']
            self.client_id = data['client_id']
            receive_task = asyncio.create_task(self.receive_messages(websocket))
            config_message = {
                "type": "config",
                "room_id": self.room_id,
                "client_id": self.client_id,
                "data": {
                    "sampleRate": 16000,
                    "bufferSize": 4096,
                    "channels": 1,
                    "language": "English",
                    "processing_strategy": "silence_at_end_of_chunk",
                    "asr_model": self.asr_type,
                    "processing_args": {
                        "chunk_length_seconds": 1,
                        "chunk_offset_seconds": 0.1
                    }
                }
            }
            await websocket.send(json.dumps(config_message))
            chunk_size = 4096  # This should match your client-side buffer size
            with open(audio_file, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    audio_message = {
                        "type": "audio",
                        "data": base64.b64encode(chunk).decode('utf-8'),
                        "room_id": self.room_id,
                        "client_id": self.client_id,
                    }
                    await websocket.send(json.dumps(audio_message))
                    await asyncio.sleep(0.1) 
            await asyncio.sleep(5)  
            receive_task.cancel()

    async def join_room(self, room_id):
        uri = "ws://127.0.0.1:8765"
        async with websockets.connect(uri) as websocket:
            join_room_message = {
                "type": "join_room",
                "room_id": room_id
            }
            await websocket.send(json.dumps(join_room_message))
            response = await websocket.recv()
            return json.loads(response)

    def test_create_and_join_room(self):
        print("Starting server...")
        start_server = self.server.start()
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))
        # Create room
        create_response = asyncio.get_event_loop().run_until_complete(self.create_room())
        self.assertEqual(create_response['type'], 'joined_room')
        room_id = create_response['room_id']
        time.sleep(3)
        join_response = asyncio.get_event_loop().run_until_complete(self.join_room(room_id))
        print("Another client joining the room " + room_id)
        self.assertEqual(join_response['type'], 'joined_room')
        self.assertEqual(join_response['room_id'], room_id)
        self.assertIsNotNone(join_response['client_id'])
        self.assertIsNotNone(join_response['transcript_url'])
        self.assertIsNotNone(join_response['audio_url'])
        print(f"Joined room successfully. Room ID: {join_response['room_id']}, Client ID: {join_response['client_id']}")

    def test_server_response(self):
        print("Starting server...")
        annotations = self.load_annotations()
        for audio_file_name, data in annotations.items():
            audio_file_path = os.path.join(os.path.dirname(__file__), f"../audio_files/{audio_file_name}")
            asyncio.get_event_loop().run_until_complete(self.mock_client(audio_file_path))
            expected_transcriptions = ' '.join([seg["transcription"] for seg in data['segments']])
            received_transcriptions = ' '.join(self.received_transcriptions)
            embedding_1 = self.similarity_model.encode(expected_transcriptions.lower().strip(), convert_to_tensor=True)
            embedding_2 = self.similarity_model.encode(received_transcriptions.lower().strip(), convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(embedding_1, embedding_2).item()
            print(f"Test file: {audio_file_name}")
            print(f"Expected Transcriptions: {expected_transcriptions}")
            print(f"Received Transcriptions: {received_transcriptions}")
            print(f"Similarity Score: {similarity}")
            self.received_transcriptions = []
            self.assertGreaterEqual(similarity, 0.6)

    def load_annotations(self):
        with open(self.annotations_path, 'r') as file:
            print(f"Loading annotations from {self.annotations_path}")
            return json.load(file)

if __name__ == '__main__':
    unittest.main()