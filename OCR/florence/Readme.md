# OCR and Document Analysis Service
This service allows for OCR (Optical Character Recognition) and document analysis through a REST API built with Quart. It uses a Florence2 model to extract text from images and perform various checks and data extraction.


## Installation
To set up and run the service, follow these steps:

For setting up just the model you can follow the following steps: 

```
git clone https://github.com/pucardotorg/dristi_experiments.git
```

Navigate to this folder : 
```
cd OCR/florence/
```

Build the docker container : 
```
docker build -t pucar_ocr .
```

Run the docker container: 
```
docker run -p 8000:8000 pucar_ocr 
```


## Usage
### API Endpoints
POST /
This endpoint accepts an image file along with various parameters to perform OCR and document analysis.

Request Parameters:

- file (required): The image file to be processed.

- word_check_list (optional): A JSON list of words to check for in the extracted text.

- distance_cutoff (optional): The Levenshtein distance threshold for keyword checking.

- doc_type (optional): The type of document (e.g., 'cheque_return_memo', 'vakalatnama').

- extract_data (optional): Boolean flag to extract specific data based on doc_type.

### For Data Validation

```
curl -X POST <url> \
  -F 'file=@/path/to/your/image.jpg' \
  -F 'word_check_list=["keyword1", "keyword2"]' \
  -F 'distance_cutoff=1' \
  -F 'doc_type= none' \
  -F 'extract_data=false'
  ```

### For Data Extraction 

```
curl -X POST <url> \
  -F 'file=@/path/to/your/image.jpg' \
  -F 'word_check_list=["keyword1", "keyword2"]' \
  -F 'distance_cutoff=2' \
  -F 'doc_type=cheque_return_memo' \
  -F 'extract_data=true'
  ```

  It supports only one doc type right now for data extraction - cheque_return_memo

### Flowchart: 

<img width="287" alt="image" src="https://github.com/user-attachments/assets/899c74d2-11b9-4251-9b2b-487da2dc1a1a">



#### Key points : 
There is a check on confidence overall of OCR .. it should be more than the decided cutoff

The image extraction is hit only if extraction argument is passed . 


