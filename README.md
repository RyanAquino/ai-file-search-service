# AI File Search Service
A file search service that performs OCR on files and embeds the text to enable similarity searches.

### Requirements
- Python 3
- Docker-compose
- Google Cloud Storage API
- OpenAI API
- Pinecone
---
### Technology
- Python 3
- OpenAI embeddings
- GCS Cloud Storage
- Pinecone vector database
- Redis caching and rate limits
---
### Endpoints
API endpoints documentation also available upon running - http://localhost:3000/docs

| Method |                      URL                      | Description                                                                                                                                                                             |                                                Example payload                                                 |
|--------|:---------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------:| 
| `POST` |              `/api/v1/register`               | Register a user with username and password                                                                                                                                              |                                  `{"username": "admin", "password": "admin"}`                                  | 
| `POST` |                `/api/v1/login`                | Authenticates a user <br/><br/> Content-type is `application/x-www-form-urlencoded`                                                                                                     |                                  `{"username": "admin", "password": "admin"}`                                  | 
| `POST` |               `/api/v1/upload`                | Receive files of types (pdf, png, jpg, tiff) and uploads to google cloud storage                                                                                                        |                                          `{"files": [<file object>]}`                                          | 
| `POST` | (Mock endpoint) <br>            `/api/v1/ocr` | Perform a mock OCR on files, embeds and saves the embedding to Pinecone vector database. <br><br> Make sure that the OCR filename in the URL matches the one in `ocr` results directory | `{"url": "https://storage.googleapis.com/ai-file-search-service_new-bucket/建築基準法施行令.json?Expires=1728795108"}` | 
| `POST` |               `/api/v1/extract`               | Extract relevant parts from given file id and query text                                                                                                                                |                               `{"query_text": "建物", "file_id": "建築基準法施行令.json"}`                               | 
---
### Setup with Docker
##### Copy google credentials to app root as `credentials.json`
```
cp <path-to-your-credentials> credentials.json
```

##### Set necessary environment variables on docker-compose.yaml
```
api:
    ...
    PINECONE_API_KEY=
    OPENAI_API_KEY=
```
##### Set OCR Results - Make sure there are mock OCR results present in `ocr` directory
##### Run servers
```
docker-compose up -d
```
---
### Setup manually (Alternative)
##### Create `.env` and adjust based on needs
```
cp .env.example .env
```
##### Install dependencies
```
pip install -r requirements.txt
```
##### Run server
```
python main.py
```
#### Access API docs on browser
```
http://localhost:3000/docs
```

### Running tests
```
pytest . -v
```