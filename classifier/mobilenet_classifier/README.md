Model to classify images as cheque return memo / vakalatnama

> docker build -t testmodel .
docker run -p 8000:8000 testmodel
curl -X POST -F "image.jpg" <http://localhost:8000/classify_image>

Server will respond with JSON response as

> {
    "classification": "vakalatnama"
}

or

> {
    "classification": "cheque return memo"
}
\n