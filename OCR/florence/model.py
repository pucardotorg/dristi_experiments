import torch
import os
from PIL import Image
import re
from Levenshtein import distance as levenshtein_distance
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from transformers import AutoModelForCausalLM, AutoProcessor
import Database
import torch.nn.functional as F
from dateutil.parser import parse as date_parse
from dateutil.parser import ParserError
from typing import Union

class Model:
    def __init__(self, context):
        self.context = context
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        try:
            self.db = Database.Database()
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            self.db = None
        self.uid = None
        self.florence_model = None
        self.model_output = {}
    
    def fixed_get_imports(self, filename: Union[str, os.PathLike]) -> list[str]:
        if not str(filename).endswith("modeling_florence2.py"):
            return get_imports(filename)
        imports = get_imports(filename)
        imports.remove("flash_attn")
        return imports

    def load_florence2_model(self, model_name='Sarvesh2003/florence_ft_on_check_memo_return', precision='fp32', attention='sdpa'):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[precision]

        model_path = os.path.join("models", model_name.replace('/', '-'))

        if not os.path.exists(model_path):
            print(f"Downloading Florence2 model to: {model_path}")
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id=model_name, local_dir=model_path, local_dir_use_symlinks=False)

        print(f"Using {attention} for attention")
        with patch("transformers.dynamic_module_utils.get_imports", self.fixed_get_imports):  # workaround for unnecessary flash_attn requirement
            model = AutoModelForCausalLM.from_pretrained(model_path, attn_implementation=attention, device_map=device, torch_dtype=dtype, trust_remote_code=True)
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

        florence2_model = {
            'model': model,
            'processor': processor,
            'dtype': dtype
        }

        return florence2_model

    def clean_text(self, text):
        text = re.sub(r'</?s>|<[^>]*>', '\n', text)
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    def is_valid_date(self, date_str):
        try:
            date_obj = date_parse(date_str, fuzzy=True)
            return date_obj.strftime('%Y-%m-%d')
        except (ParserError, ValueError):
            return None
    def check_keywords(self, text, keywords, threshold):
        cleaned_text = text.lower()
        words = cleaned_text.split()
        results = {}

        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_split = keyword_lower.split() if ' ' in keyword_lower else [keyword_lower]
            min_distances = []

            for k in keyword_split:
                min_distance = min(levenshtein_distance(k, word) for word in words)
                min_distances.append(min_distance)
                results[k] = 1 if min_distance <= threshold else 0

            avg_dist = sum(min_distances) / len(min_distances)
            results[keyword] = 1 if avg_dist <= threshold else 0

        return results

    def extract_cheque_return_memo(self, florence2_model, text, image):
        average_confidence, results = self.run_example_with_probs(florence2_model, "<DocVQA>What is the date present in the provided document?", image)
        cleaned_text = self.clean_text(results)
        cheque_amount = re.search(r'For Rs\.? ([\d,\.]+)|Amount[: ]\s*([\d,\.]+)', text)
        date_submission = re.search(r'DATE[ :.-]+([\dA-Za-z-]+)|Date[ :]+([\dA-Za-z-]+)', text)
        date_return = self.is_valid_date(cleaned_text)
        extracted_data = {
            "Cheque Amount": cheque_amount.group(1) if cheque_amount else None,
            "Date of Cheque Submission": date_submission.group(1) if date_submission else None,
            "Date of Cheque Return": date_return if average_confidence > 0.9 else None
        }
        self.model_output['DocVQA_average_confidence'] = average_confidence
        self.model_output['DocVQA output'] = cleaned_text
        return extracted_data

    def extract_vakalatnama(self, text):
        advocate_name = re.search(r'Advocate\.?\s*(.*?)(?:\n|$)', text)
        party_name = re.search(r'Between\s*(.*?)\s+and\s+', text, re.IGNORECASE)

        extracted_data = {
            "Advocate Name": advocate_name.group(1).strip() if advocate_name else None,
            "Party Name": party_name.group(1).strip() if party_name else None
        }

        return extracted_data

    def run_example_with_probs(self, florence2_model, task_prompt, image):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        processor = florence2_model['processor']
        model = florence2_model['model']
        dtype = florence2_model['dtype']
        model.to(self.device)

        inputs = processor(text=task_prompt, images=image, return_tensors="pt", do_rescale=False).to(dtype).to(self.device)
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
            output_scores=True,
            return_dict_in_generate=True
        )
        generated_ids = outputs.sequences
        logits = outputs.scores
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        probs = [F.softmax(logit, dim=-1) for logit in logits]
        max_probs = [prob.max().item() for prob in probs]
        avg_confidence = sum(max_probs) / len(max_probs)
        return avg_confidence, generated_text

    def run_ocr(self, image_path, florence2_model, keywords=[], lev_distance_threshold=1, doc_type=None, extract_data=False):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(device)
        task_prompt = '<OCR_WITH_REGION>'

        image = Image.open(image_path).convert('RGB')

        average_confidence, results = self.run_example_with_probs(florence2_model, task_prompt, image)
        cleaned_text = self.clean_text(results)
        self.model_output['OCR_average_confidence'] = average_confidence
        self.model_output['OCR output'] = cleaned_text
        if average_confidence < 0.65:
            try:
                if self.db:
                    self.uid = self.db.upload_data(image_path, self.model_output)
                else:
                    print("Database not initialized. Unable to upload data.")
                    self.uid = None
            except Exception as e:
                print(f"Error uploading data to database: {str(e)}")
                self.uid = None
            return {"Message": "Retry with a better quality image",
                    "UID": self.uid}
        print(f"Cleaned Text: {cleaned_text}")
        contains_keywords = self.check_keywords(cleaned_text, keywords, lev_distance_threshold)
        extracted_data = {}
        if extract_data:
            if doc_type == 'cheque_return_memo':
                extracted_data = self.extract_cheque_return_memo(florence2_model, cleaned_text, image)
            elif doc_type == 'vakalatnama':
                extracted_data = self.extract_vakalatnama(cleaned_text)
        self.model_output['Contains Keywords'] = contains_keywords
        self.model_output['Extracted Data'] = extracted_data

        try:
            if self.db:
                self.uid = self.db.upload_data(image_path, self.model_output)
            else:
                print("Database not initialized. Unable to upload data.")
                self.uid = None
        except Exception as e:
            print(f"Error uploading data to database: {str(e)}")
            self.uid = None
        
        if extract_data and extracted_data:
            return {
                "Contains Keywords": contains_keywords,
                "Extracted Data": extracted_data,
                "UID": self.uid
            }
        else:
            return {
                "Contains Keywords": contains_keywords,
                "UID": self.uid
            }
