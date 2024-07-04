import torch
import os
from PIL import Image
import re
from Levenshtein import distance as levenshtein_distance
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from transformers import AutoModelForCausalLM, AutoProcessor
from typing import Union

class Model:
    def __init__(self, context):
        self.context = context
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def fixed_get_imports(self, filename: Union[str, os.PathLike]) -> list[str]:
        if not str(filename).endswith("modeling_florence2.py"):
            return get_imports(filename)
        imports = get_imports(filename)
        imports.remove("flash_attn")
        return imports

    def load_florence2_model(self, model_name='microsoft/Florence-2-base', precision='fp32', attention='sdpa'):
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
    
    def extract_cheque_return_memo(self, text):
        cheque_amount = re.search(r'For Rs\.? ([\d,\.]+)|Amount[: ]\s*([\d,\.]+)', text)
        date_submission = re.search(r'DATE[ :.-]+([\dA-Za-z-]+)|Date[ :]+([\dA-Za-z-]+)', text)
        date_return = re.search(r'Return Date[ :]+([\dA-Za-z-]+)', text)

        extracted_data = {
            "Cheque Amount": cheque_amount.group(1) if cheque_amount else None,
            "Date of Cheque Submission": date_submission.group(1) if date_submission else None,
            "Date of Cheque Return": date_return.group(1) if date_return else None
        }

        return extracted_data

    def extract_vakalatnama(self, text):
        advocate_name = re.search(r'Advocate\.?\s*(.*?)(?:\n|$)', text)
        party_name = re.search(r'Between\s*(.*?)\s+and\s+', text, re.IGNORECASE)

        extracted_data = {
            "Advocate Name": advocate_name.group(1).strip() if advocate_name else None,
            "Party Name": party_name.group(1).strip() if party_name else None
        }

        return extracted_data 

    def run_ocr(self, image_path, florence2_model, keywords=[], lev_distance_threshold=1, doc_type=None, extract_data=False):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        task_prompt = '<OCR_WITH_REGION>'

        image = Image.open(image_path).convert('RGB')

        processor = florence2_model['processor']
        model = florence2_model['model']
        dtype = florence2_model['dtype']
        model.to(device)

        inputs = processor(text=task_prompt, images=image, return_tensors="pt", do_rescale=False).to(dtype).to(device)

        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=True,
            num_beams=3,
        )

        results = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

        cleaned_text = self.clean_text(results)
        print(f"Cleaned Text: {cleaned_text}")

        contains_keywords = self.check_keywords(cleaned_text, keywords, lev_distance_threshold)

        extracted_data = {}
        if extract_data:
            if doc_type == 'cheque_return_memo':
                extracted_data = self.extract_cheque_return_memo(cleaned_text)
            elif doc_type == 'vakalatnama':
                extracted_data = self.extract_vakalatnama(cleaned_text)

        if extract_data and extracted_data:
            return {
                "Contains Keywords": contains_keywords,
                "Extracted Data": extracted_data
            }
        else:
            return {
                "Contains Keywords": contains_keywords
            }