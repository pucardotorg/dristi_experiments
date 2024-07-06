
```
docker build -t testmodel .
docker run -p 8000:8000 testmodel
```


**curl request :**

curl -X POST -H "Content-Type: application/json" -d '{
"text": "ପାମ ମିଶନରୀ ଉପରେ କେତେ % ରିହାତି ଧୈର୍ଯ ହୋଇଛି",
"BEAM_WIDTH": 5,
"SCORE_THRESHOLD": 1.5,
"max_distance": 1,
"lang" : "ory"
}' http://localhost:8000/

curl -X POST -H "Content-Type: application/json" -d '{
"text": "ପାମ ମିଶନରୀ ଉପରେ କେତେ % ରିହାତି ଧୈର୍ଯ ହୋଇଛି",
"BEAM_WIDTH": 5,
"SCORE_THRESHOLD": 1.5,
"max_distance": 1
}' http://localhost:8000/

curl -X POST -H "Content-Type: application/json" -d '{
"text": "how to apply for go-sugem scheme for my paddi crop",
"BEAM_WIDTH": 5,
"SCORE_THRESHOLD": 1.5,
"max_distance": 1,
"lang" : "eng"
}' http://localhost:8000/

**curl request for update:**

curl -X PUT -H "Content-Type: application/json" -d '{
"text": "ମିଶନରୀ",
"lang" : "ory"
}' http://localhost:8000/

curl -X PUT -H "Content-Type: application/json" -d '{
"text": ["ପାମ ମିଶନରୀ ଉପରେ", "ରିହାତି ଧୈର୍ଯ ହୋଇଛି"]
}' http://localhost:8000/

curl -X PUT -H "Content-Type: application/json" -d '{
"text": "go-sugem go'sugem",
"lang" : "eng"
}' http://localhost:8000/

curl -X PUT -H "Content-Type: application/json" -d '{
"text": ["how to apply for", "scheme for my rabi crop"],
"lang" : "eng"
}' http://localhost:8000/
