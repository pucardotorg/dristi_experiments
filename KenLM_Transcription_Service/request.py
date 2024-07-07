import requests
import json


class ModelRequest():
    def __init__(self, text, BEAM_WIDTH, SCORE_THRESHOLD, max_distance, lang='ory'):
        self.text = text
        self.BEAM_WIDTH = BEAM_WIDTH
        self.SCORE_THRESHOLD = SCORE_THRESHOLD
        self.max_distance = max_distance
        self.lang = lang  

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ModelUpdateRequest():
    def __init__(self, text, lang='ory'):
        self.text = text
        self.lang = lang

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    

class ModelWERRequest():
    def __init__(self, asr_transcription, kenlm_transcription):
        self.asr_transcription = asr_transcription
        self.kenlm_transcription = kenlm_transcription

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)