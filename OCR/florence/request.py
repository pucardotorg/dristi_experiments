import json

class ModelRequest:
    def __init__(self, image_file, word_check_list, doc_type='', distance_cutoff=0, extract_data=False):
        self.image_file = image_file
        self.word_check_list = word_check_list
        self.distance_cutoff = distance_cutoff
        self.doc_type = doc_type
        self.extract_data = extract_data

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)