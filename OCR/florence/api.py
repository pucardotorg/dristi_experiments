from model import Model
from request import ModelRequest
from quart import Quart, request, jsonify
from quart_cors import cors
import aiohttp
import os
import tempfile
import ast
import logging

logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__)
app = cors(app)

@app.before_serving
async def startup():
    app.client = aiohttp.ClientSession()
    global model
    try:
        global model
        model = Model(app)
        model.florence2_model = model.load_florence2_model()
    except Exception as e:
        model = None
        logging.debug(f"Model not initialized: {e}")

@app.route('/', methods=['POST'])
async def embed():
    temp_dir = tempfile.mkdtemp()
    files = await request.files
    uploaded_file = files.get('file')
    if not uploaded_file:
        return {"error": "File is missing"}, 400

    image_file = os.path.join(temp_dir, uploaded_file.filename)
    await uploaded_file.save(image_file)

    form = await request.form
    word_check_list = ast.literal_eval(form.get('word_check_list', '[]'))
    distance_cutoff = int(form.get('distance_cutoff', 0))
    doc_type = str(form.get('doc_type', ''))
    extract_data = form.get('extract_data', 'false').lower() == 'true'

    req = ModelRequest(
        image_file=image_file,
        word_check_list=word_check_list,
        distance_cutoff=distance_cutoff,
        doc_type=doc_type,
        extract_data=extract_data
    )

    response = model.run_ocr(req.image_file, model.florence2_model, keywords=req.word_check_list, lev_distance_threshold=req.distance_cutoff, doc_type=req.doc_type, extract_data=req.extract_data)

    os.remove(image_file)
    os.rmdir(temp_dir)

    return jsonify(response)

if __name__ == "__main__":
    app.run()