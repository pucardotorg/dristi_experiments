from .asr_interface import ASRInterface
from src.audio_utils import save_audio_to_file
import os
import json
import requests
import base64
from src.transcription_utils import save_audio_file

language_codes = {
    "afrikaans": "af",
    "amharic": "am",
    "arabic": "ar",
    "assamese": "as",
    "azerbaijani": "az",
    "bashkir": "ba",
    "belarusian": "be",
    "bulgarian": "bg",
    "bengali": "bn",
    "tibetan": "bo",
    "breton": "br",
    "bosnian": "bs",
    "catalan": "ca",
    "czech": "cs",
    "welsh": "cy",
    "danish": "da",
    "german": "de",
    "greek": "el",
    "english": "en",
    "spanish": "es",
    "estonian": "et",
    "basque": "eu",
    "persian": "fa",
    "finnish": "fi",
    "faroese": "fo",
    "french": "fr",
    "galician": "gl",
    "gujarati": "gu",
    "hausa": "ha",
    "hawaiian": "haw",
    "hebrew": "he",
    "hindi": "hi",
    "croatian": "hr",
    "haitian": "ht",
    "hungarian": "hu",
    "armenian": "hy",
    "indonesian": "id",
    "icelandic": "is",
    "italian": "it",
    "japanese": "ja",
    "javanese": "jw",
    "georgian": "ka",
    "kazakh": "kk",
    "khmer": "km",
    "kannada": "kn",
    "korean": "ko",
    "latin": "la",
    "luxembourgish": "lb",
    "lingala": "ln",
    "lao": "lo",
    "lithuanian": "lt",
    "latvian": "lv",
    "malagasy": "mg",
    "maori": "mi",
    "macedonian": "mk",
    "malayalam": "ml",
    "mongolian": "mn",
    "marathi": "mr",
    "malay": "ms",
    "maltese": "mt",
    "burmese": "my",
    "nepali": "ne",
    "dutch": "nl",
    "norwegian nynorsk": "nn",
    "norwegian": "no",
    "occitan": "oc",
    "punjabi": "pa",
    "polish": "pl",
    "pashto": "ps",
    "portuguese": "pt",
    "romanian": "ro",
    "russian": "ru",
    "sanskrit": "sa",
    "sindhi": "sd",
    "sinhalese": "si",
    "slovak": "sk",
    "slovenian": "sl",
    "shona": "sn",
    "somali": "so",
    "albanian": "sq",
    "serbian": "sr",
    "sundanese": "su",
    "swedish": "sv",
    "swahili": "sw",
    "tamil": "ta",
    "telugu": "te",
    "tajik": "tg",
    "thai": "th",
    "turkmen": "tk",
    "tagalog": "tl",
    "turkish": "tr",
    "tatar": "tt",
    "ukrainian": "uk",
    "urdu": "ur",
    "uzbek": "uz",
    "vietnamese": "vi",
    "yiddish": "yi",
    "yoruba": "yo",
    "chinese": "zh",
    "cantonese": "yue",
}


class BhashiniASR(ASRInterface):
    def __init__(self, **kwargs):
        self.user_id = os.getenv('BHASHINI_USER_ID')
        self.ulca_api_key = os.getenv('BHASHINI_API_KEY')
        self.pipeline_id = os.getenv('BHASHINI_PIPELINE_ID')

    def convert_to_base64(self, file_path):
        with open(file_path, 'rb') as file:
            file_content = file.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        return base64_content

    def transcribe_audio(self, base64encoded_audio, source_language):
        url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": self.pipeline_id
            }
        })
        headers = {
            'userID': self.user_id,
            'ulcaApiKey': self.ulca_api_key,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                reponse_json = json.loads(response.text)
            else:
                reponse_json = json.loads(response.text)
                print(response.text)
        except Exception as e:
            print(f"API failed", e)

        url = reponse_json['pipelineInferenceAPIEndPoint']['callbackUrl']

        if 'pipelineResponseConfig' in reponse_json:
            for item in reponse_json['pipelineResponseConfig']:
                if 'config' in item and isinstance(item['config'], list) and len(item['config']) == 1:
                    item['config'] = item['config'][0]

        payload = json.dumps({
            "pipelineTasks": reponse_json['pipelineResponseConfig'],
            "inputData": {
                "audio": [
                    {
                        "audioContent": base64encoded_audio
                    }
                ]
            }
        })

        headers = {
            'Accept': '*/*',
            'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
            reponse_json['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']:
                reponse_json['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value'],
            'Content-Type': 'application/json'
        }

        retries = 0
        max_retries = 5

        while retries < max_retries:
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    transcribed_output = json.loads(response.text)['pipelineResponse'][0]['output'][0]['source']
                    return transcribed_output
                else:
                    print(f"Request failed with status code {response.status_code}. Retrying...")
                    retries += 1
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                retries += 1

        return "Transcription failed after maximum retries."

    def transcribe_translate_audio(self, base64encoded_audio, source_language, target_language):
        if (source_language == target_language):
            return self.transcribe_audio(base64encoded_audio, source_language)

        url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language
                        }
                    }
                },
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language,
                            "targetLanguage": target_language
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": self.pipeline_id
            }
        })
        headers = {
            'userID': self.user_id,
            'ulcaApiKey': self.ulca_api_key,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                reponse_json = json.loads(response.text)
            else:
                reponse_json = json.loads(response.text)
                print(response.text)
        except Exception as e:
            print(f"API failed", e)

        url = reponse_json['pipelineInferenceAPIEndPoint']['callbackUrl']

        if 'pipelineResponseConfig' in reponse_json:
            for item in reponse_json['pipelineResponseConfig']:
                if 'config' in item and isinstance(item['config'], list) and len(item['config']) == 1:
                    item['config'] = item['config'][0]

        payload = json.dumps({
            "pipelineTasks": reponse_json['pipelineResponseConfig'],
            "inputData": {
                "audio": [
                    {
                        "audioContent": base64encoded_audio
                    }
                ]
            }
        })

        headers = {
            'Accept': '*/*',
            'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
            reponse_json['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']:
                reponse_json['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value'],
            'Content-Type': 'application/json'
        }

        retries = 0
        max_retries = 5

        while retries < max_retries:
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    transcribed_output = json.loads(response.text)['pipelineResponse'][1]['output'][0]['target']
                    return transcribed_output
                else:
                    print(f"Request failed with status code {response.status_code}. Retrying...")
                    retries += 1
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                retries += 1

        return "Transcription failed after maximum retries."

    async def transcribe(self, client):
        file_path = await save_audio_to_file(client.scratch_buffer, client.get_file_name())

        language = None if client.config['language'] is None else language_codes.get(client.config['language'].lower())
        base64encoded_audio = self.convert_to_base64(file_path)
        if client.config['language'] is not None:
            to_return = self.transcribe_translate_audio(base64encoded_audio, source_language=language,
                                                        target_language="en")
        else:
            to_return = ""

        save_audio_file(file_path)

        os.remove(file_path)

        to_return = {
            "language": "en",
            "language_probability": 100,
            "text": to_return.strip(),
            "words": []
        }
        return to_return
