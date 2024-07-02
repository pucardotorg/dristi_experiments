import cv2
import numpy as np
import aiohttp
import joblib
import io
from utilities import normalize_image, compute_edge_features

class Model:
    def __init__(self, context, svm_model):
        self.context = context
        self.svm_model = svm_model

    @classmethod
    async def create(cls, context):
        """Class method to initialize the model and load the SVM model from Hugging Face."""
        model_url = 'https://huggingface.co/smokeyScraper/blur_detection/resolve/main/svm_model.pkl'

        async with aiohttp.ClientSession() as session:
            async with session.get(model_url) as response:
                svm_model_bytes = await response.read()
                svm_model = joblib.load(io.BytesIO(svm_model_bytes))
                return cls(context, svm_model)

    async def classify_image(self, uploaded_im_file):
        """Classify the uploaded image as blurry or not blurry."""
        nparr = np.frombuffer(uploaded_im_file.read(), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        normalized_image = normalize_image(image)
        features = compute_edge_features(normalized_image)
        
        decision_scores = self.svm_model.decision_function([features])
        sigmoid_scores = 1 / (1 + np.exp(-decision_scores))
        
        # custom threshold for classification 
        custom_threshold = 0.4
        is_blur = (sigmoid_scores >= custom_threshold).astype(int)[0]
        
        return bool(is_blur)