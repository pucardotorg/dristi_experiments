'''
Room will have the config that should be used.
A list of client - Since i dont need client id to process messages. I can use room id
A function to broadcast messages.
'''

from src.buffering_strategy.buffering_strategy_factory import BufferingStrategyFactory


class Room:
    """
    Represents a client connected to the VoiceStreamAI server.

    This class maintains the state for each connected client, including their
    unique identifier, audio buffer, configuration, and a counter for processed audio files.

    Attributes:
        room_id (str): A unique identifier for the room.
        connected_clients(array): An array to store all connected clients
        buffer (bytearray): A buffer to store incoming audio data.
        config (dict): Configuration settings for the room, like chunk length and offset.
        file_counter (int): Counter for the number of audio files processed.
        total_samples (int): Total number of audio samples received for this room.
        sampling_rate (int): The sampling rate of the audio data in Hz.
        samples_width (int): The width of each audio sample in bits.
    """

    def __init__(self, room_id, sampling_rate, samples_width):
        self.room_id = room_id
        self.connected_clients = {}
        self.buffer = bytearray()
        self.scratch_buffer = bytearray()
        self.config = {"language": None,
                       "processing_strategy": "silence_at_end_of_chunk",
                       "processing_args": {
                           "chunk_length_seconds": 5,
                           "chunk_offset_seconds": 0.1
                       }
                       }
        self.file_counter = 0
        self.total_samples = 0
        self.sampling_rate = sampling_rate
        self.samples_width = samples_width
        self.buffering_strategy = BufferingStrategyFactory.create_buffering_strategy(self.config['processing_strategy'],
                                                                                     self,
                                                                                     **self.config['processing_args'])

    def update_config(self, config_data):
        self.config.update(config_data)
        self.buffering_strategy = BufferingStrategyFactory.create_buffering_strategy(self.config['processing_strategy'],
                                                                                     self,
                                                                                     **self.config['processing_args'])

    def append_audio_data(self, audio_data):
        self.buffer.extend(audio_data)
        self.total_samples += len(audio_data) / self.samples_width

    def clear_buffer(self):
        self.buffer.clear()

    def increment_file_counter(self):
        self.file_counter += 1

    def get_file_name(self):
        return f"{self.room_id}_{self.file_counter}.wav"

    def process_audio(self, websocket, vad_pipeline, asr_pipeline):
        self.buffering_strategy.process_audio(websocket, vad_pipeline, asr_pipeline)

    async def broadcast_to_room(self, message):
        for client_id, client in self.connected_clients.items():
            await client.websocket.send(json.dumps({'type': 'transcription', 'data': message}))

    def join_room(self, client):
        self.connected_clients[client.client_id] = client
        print(f"Client {client.client_id} joined room {self.room_id}")

    def leave_room(self, client_id):
        if client_id in self.connected_clients:
            del self.connected_clients[client.client_id]
            print(f"Client {client.client_id} left room {self.room_id}")