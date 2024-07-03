Model to detect whether if an image of document is blur or not.

> docker build -t testmodel .
docker run -p 8000:8000 testmodel
curl -X POST -F "image.jpg" http://localhost:8000/classify_image

Server will respond with JSON response as 

> {
   "is_blur": true
}

or 

> {
   "error": "Missing file"
 }