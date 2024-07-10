# Docker
### 1. Build the Docker Image

```sh
docker build -t flo-app .
```


### 2. Run the Docker Image

```sh
docker run --gpus all -p 1234:8000 flo-app
```

# Sample Curl Requests

### For Data Extraction 

```sh
curl -X POST http://localhost:1234/ \
  -F "file=@1c_cheque_return_memo_1.jpg" \
  -F 'word_check_list=["return memo", "memo"]' \
  -F "distance_cutoff=1" \
  -F "doc_type=cheque_return_memo" \
  -F "extract_data=true"
  ```
  

### For Data Validation

```sh
curl -X POST http://localhost:1234/ \
  -F "file=@1c_cheque_return_memo_1.jpg" \
  -F 'word_check_list=["return memo", "memo"]' \
  -F "distance_cutoff=1"
```

