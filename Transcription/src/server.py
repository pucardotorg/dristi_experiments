from string import ascii_uppercase

import websockets
import uuid
import json
import ssl
import random

from src.audio_utils import save_audio_to_file
from src.client import Client

class Server:
    """
    Represents the WebSocket server for handling real-time audio transcription.

    This class manages WebSocket connections, processes incoming audio data,
    and interacts with VAD and ASR pipelines for voice activity detection and
    speech recognition.

    Attributes:
        vad_pipeline: An instance of a voice activity detection pipeline.
        asr_pipeline: An instance of an automatic speech recognition pipeline.
        host (str): Host address of the server.
        port (int): Port on which the server listens.
        sampling_rate (int): The sampling rate of audio data in Hz.
        samples_width (int): The width of each audio sample in bits.
        connected_clients (dict): A dictionary mapping client IDs to Client objects.
    """
    def __init__(self, vad_pipeline, asr_pipeline, host='localhost', port=8765, sampling_rate=16000, samples_width=2, certfile = None, keyfile = None):
        self.vad_pipeline = vad_pipeline
        self.asr_pipeline = asr_pipeline
        self.host = host
        self.port = port
        self.sampling_rate = sampling_rate
        self.samples_width = samples_width
        self.certfile = certfile
        self.keyfile = keyfile
        self.rooms = {}  # Dictionary to manage rooms

    async def handle_audio(self, websocket):
        while True:
            message = await websocket.recv()
            config = json.loads(message)
            room = self.rooms[config.get('room_id')]
            room_id = config.get('room_id')

            if room is not None:
                if config.get('type') == 'audio':
                    room.append_audio_data(config.get('data'))
                elif config.get('type') == 'config':
                    room.update_config(config['data'])
                    continue
                elif config.get('type') == 'join_room':
                    room_id = config['room_id']
                    client_id = self.join_room(room_id)
                    await websocket.send(json.dumps({'type': 'joined_room', 'room_id': room_id, 'client_id': client_id}))
                    continue
                elif config.get('type') == 'leave_room':
                    room_id = config['room_id']
                    client_id = config['client_id']
                    room.leave_room(client_id)
                    await websocket.send(json.dumps({'type': 'left_room', 'room_id': room_id}))
                    continue
                else:
                    print(f"Unexpected message type from {room.room_id}")
            elif config.get('type') == 'create_room':
                room_id = self.generate_unique_code(6)
                client_id = self.join_room(room_id)
                await websocket.send(json.dumps({'type': 'joined_room', 'room_id': room_id, 'client_id': client_id}))
                continue
            else:
                print(f"Invalid room {room_id}")

            # this is synchronous, any async operation is in BufferingStrategy
            room.process_audio(websocket, self.vad_pipeline, self.asr_pipeline)

    def generate_unique_code(self, length):
        while True:
            code = ""
            for _ in range(length):
                code += random.choice(ascii_uppercase)

            if code not in self.rooms:
                break

        return code

    def get_client_room(self, client_id):
        for room_id, room_clients in self.rooms.items():
            if client_id in room_clients:
                return room_id
        return None


    def join_room(self, room_id):
        if room_id not in self.rooms:
            room = Room(room_id, self.sampling_rate, self.samples_width)
            self.rooms[room_id] = room
        client_id = str(uuid.uuid4())
        client = Client(client_id, self.sampling_rate, self.samples_width)
        room.join_room(client)
        return client_id

    def get_current_client_id(self):
        # Return the current client_id being handled
        if self.connected_clients:
            return next(iter(self.connected_clients))
        return None
    
    async def handle_websocket(self, websocket, path):
        # client_id = str(uuid.uuid4())
        # client = Client(client_id, self.sampling_rate, self.samples_width)
        # self.connected_clients[client_id] = client
        # await websocket.send(json.dumps({'type': 'client_id', 'client_id': client_id}))
        # print(f"client {client_id} connected")
        try:
            await self.handle_audio(websocket)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

    def start(self):
        if self.certfile:
            # Create an SSL context to enforce encrypted connections
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            
            # Load your server's certificate and private key
            # Replace 'your_cert_path.pem' and 'your_key_path.pem' with the actual paths to your files
            ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

            print(f"WebSocket server ready to accept secure connections on {self.host}:{self.port}")
            
            # Pass the SSL context to the serve function along with the host and port
            # Ensure the secure flag is set to True if using a secure WebSocket protocol (wss://)
            return websockets.serve(self.handle_websocket, self.host, self.port, ssl=ssl_context)
        else:
            print(f"WebSocket server ready to accept secure connections on {self.host}:{self.port}")
            return websockets.serve(self.handle_websocket, self.host, self.port)

