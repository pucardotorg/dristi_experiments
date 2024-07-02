import json
from quart import Quart, request, Response
from model import ModelClassifier

app = Quart(__name__)

model = None

@app.before_serving
async def startup():
    """Initialize the model once before the server starts."""
    global model
    model = await ModelClassifier.create(app)

@app.route('/classify_image', methods=['POST'])
async def classify_image():
    """Endpoint to classify an image as cheque return memo or vakalatnama."""
    global model

    files = await request.files
    uploaded_im_file = files.get('im_file')

    if not uploaded_im_file:
        return Response(json.dumps({"error": "Missing file"}), status=400, mimetype='application/json')

    classification = await model.classify_image(uploaded_im_file)

    return Response(json.dumps({"classification": classification}), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run()