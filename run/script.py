import os
import aiohttp
import asyncio
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

# API endpoint
url = "http://localhost:1234/"

# Change the image directory as needed
image_directory = "images/cheque_return_memo"

async def send_request(session, image_path, filename):
    try:
        with open(image_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('file', file)
            data.add_field('word_check_list', '["return memo", "memo", "return"]')
            data.add_field('distance_cutoff', '1')
            # if NER extraction needed
            data.add_field('doc_type', 'cheque_return_memo')
            data.add_field('extract_data', 'true')

            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"Failed to process {filename}. Status code: {response.status}")
    except Exception as e:
        logger.error(f"An error occurred while processing {filename}: {e}")
    return None

async def save_result(result, output_dir, filename):
    if result is not None:
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save results for {filename}: {e}")

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            # Output directory run/output/<image_directory>/{filename}.json
            output_dir = f'run/output/{os.path.basename(image_directory)}'
            os.makedirs(output_dir, exist_ok=True)

            for filename in [f for f in os.listdir(image_directory) if f.endswith(('.jpg', '.png'))]:
                image_path = os.path.join(image_directory, filename)
                result = await send_request(session, image_path, filename)
                if result:
                    await save_result(result, output_dir, filename)

    except Exception as e:
        logger.error(f"An error occurred during the execution of main function: {e}")

    print(f"Results have been saved in {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())