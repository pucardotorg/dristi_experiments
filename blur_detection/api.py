import json
from quart import Quart, request, Response
from model import Model

app = Quart(__name__)

model = None

@app.before_serving
async def startup():
    """Initialize the model once before the server starts."""
    global model
    model = await Model.create(app)

@app.route('/classify_image', methods=['POST'])
async def classify_image():
    """Endpoint to classify an image as blurry or not."""
    global model

    files = await request.files
    uploaded_im_file = files.get('im_file')

    if not uploaded_im_file:
        return Response(json.dumps({"error": "Missing file"}), status=400, mimetype='application/json')

    is_blur = await model.classify_image(uploaded_im_file)

    return Response(json.dumps({"is_blur": is_blur}), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run()