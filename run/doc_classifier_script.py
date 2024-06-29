import os
import aiohttp
import asyncio
import json
import logging
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# API endpoint
url = "http://localhost:8000/classify_image"

# Image directories
cheque_return_memo_dir = "images/cheque_return_memo"
vakalatnama_dir = "images/vakalatnama"

async def send_request(session, image_path):
    try:
        with open(image_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('im_file', file)

            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"Failed to process {image_path}. Status code: {response.status}")
    except Exception as e:
        logger.error(f"An error occurred while processing {image_path}: {e}")
    return None

async def classify_images(image_directory, label):
    predictions = []
    true_labels = []
    filenames = []
    async with aiohttp.ClientSession() as session:
        for filename in [f for f in os.listdir(image_directory) if f.endswith(('.jpg', '.png'))]:
            image_path = os.path.join(image_directory, filename)
            result = await send_request(session, image_path)
            if result and 'classification' in result:
                predictions.append(result['classification'])
                true_labels.append(label)
                filenames.append(filename)
    return predictions, true_labels, filenames

async def main():
    try:
        cheque_return_memo_predictions, cheque_return_memo_labels, cheque_return_memo_filenames = await classify_images(cheque_return_memo_dir, 'cheque return memo')
        vakalatnama_predictions, vakalatnama_labels, vakalatnama_filenames = await classify_images(vakalatnama_dir, 'vakalatnama')

        all_predictions = cheque_return_memo_predictions + vakalatnama_predictions
        all_labels = cheque_return_memo_labels + vakalatnama_labels
        all_filenames = cheque_return_memo_filenames + vakalatnama_filenames

        accuracy = accuracy_score(all_labels, all_predictions)
        f1 = f1_score(all_labels, all_predictions, average='weighted')
        conf_matrix = confusion_matrix(all_labels, all_predictions)

        logger.info(f"Accuracy: {accuracy}")
        logger.info(f"F1 Score: {f1}")
        logger.info(f"Confusion Matrix:\n{conf_matrix}")

        output_dir = "run/classification_results"
        os.makedirs(output_dir, exist_ok=True)
        results = {
            'filenames': all_filenames,
            'predictions': all_predictions,
            'true_labels': all_labels,
            'accuracy': accuracy,
            'f1_score': f1,
            'confusion_matrix': conf_matrix.tolist()
        }
        with open(os.path.join(output_dir, 'results.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        
        print(f"Results have been saved in {output_dir}")

    except Exception as e:
        logger.error(f"An error occurred during the execution of main function: {e}")

if __name__ == "__main__":
    asyncio.run(main())