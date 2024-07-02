import cv2
import tensorflow as tf
import numpy as np

class ModelClassifier:
    def __init__(self, context, model):
        self.context = context
        self.model = model

    @classmethod
    async def create(cls, context, model_path='models/model.keras'):
        """Class method to initialize the model from the local path."""

        model = tf.keras.models.load_model(model_path)
        
        return cls(context, model)

    async def classify_image(self, uploaded_im_file):
        """Classify the uploaded image as cheque return memo or vakalatnama."""
        nparr = np.frombuffer(uploaded_im_file.read(), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (224, 224))
        image = image / 255.0  
        image = image.reshape((1, 224, 224, 3))

        predictions = self.model.predict(image)
        class_index = np.argmax(predictions[0])
        classification = "vakalatnama" if class_index == 0 else "cheque return memo"
        
        return classification