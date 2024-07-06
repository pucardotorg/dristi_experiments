from model import Model
from update import UpdationModel
from request import ModelRequest, ModelUpdateRequest, ModelWERRequest
from quart import Quart, request
from quart_cors import cors
import aiohttp

app = Quart(__name__)
app = cors(app, allow_origin="*")

model = None

model_paths = {
    'ory': '5gram_model.bin',
    'eng': '5gram_model_eng.bin'
}

vocab_paths = {
    'ory': 'lexicon.txt',
    'eng': 'lexicon_eng.txt'
}

texts_paths = {
    'ory': 'texts.txt',
    'eng': 'texts_eng.txt'
}


@app.before_serving
async def startup():
    app.client = aiohttp.ClientSession()
    global model
    model = Model(app, model_paths, vocab_paths)


@app.route('/', methods=['POST'])
async def embed():
    global model
    data = await request.get_json()
    req = ModelRequest(**data)
    result = await model.inference(req)
    return result

@app.route('/wer', methods=['POST'])
async def calculate_wer():
    global model
    data = await request.get_json()
    req = ModelWERRequest(**data)
    result = await model.calculate_wer(req)
    return result

@app.route('/', methods=['PUT'])
async def update():
    global model
    data = await request.get_json()
    req = ModelUpdateRequest(**data)
    result = await UpdationModel(model_paths, vocab_paths, texts_paths).update(req)

    if result:
        model = Model(app, model_paths, vocab_paths)

    return result

if __name__ == "__main__":
    app.run()