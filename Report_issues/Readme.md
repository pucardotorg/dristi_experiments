# Sample Curl Requests

# Reporting Transcription Issues
curl -X POST http://localhost:8002/submit-issue \
     -H "Content-Type: application/json" \
     -d '{"category": "transcription", "text": "There is an error in the transcription"}'

# Reporting OCR Issues
curl -X POST http://localhost:8002/submit-issue \
     -H "Content-Type: application/json" \
     -d '{"category": "ocr", "text": "OCR misread the text }'

# Reporting Validation Issues
curl -X POST http://localhost:8002/submit-issue \
     -H "Content-Type: application/json" \
     -d '{"category": "validation", "text": "Data validation failed"}'
