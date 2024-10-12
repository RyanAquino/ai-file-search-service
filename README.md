# AI File Search Service
A file search service that embeds file URLs texts and allows similarity search

### Requirements
- Python 3
- Docker
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

| Method |                      URL                      | Description                                                                                                                                                                                  |                                             Example payload                                             |
|--------|:---------------------------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------:| 
| `POST` |              `/api/v1/register`               | Register a user with username and password                                                                                                                                                   |                              `{"username": "admin", "password": "admin"}`                               | 
| `POST` |                `/api/v1/login`                | Authenticates a user <br/><br/> Content-type is `application/x-www-form-urlencoded`                                                                                                          |                              `{"username": "admin", "password": "admin"}`                               | 
| `POST` |               `/api/v1/upload`                | Receive a file of types (pdf, png, jpg, tiff). Since                                                                                                                                         |                                      `{"files": [<file object>]}`                                       | 
| `POST` | (Mock endpoint) <br>            `/api/v1/ocr` | Perform a mock OCR on image file, embeds and saves the embedding to pinecone vector database. <br><br> Make sure that the OCR filename in the URL matches the one in `ocr` results directory | `["https://storage.googleapis.com/ai-file-search-service_new-bucket/建築基準法施行令.json?Expires=1728795108"]` | 
| `POST` |               `/api/v1/extract`               | Extract relevant parts from given file id and query text                                                                                                                                     |                           `{"query_text": "建物", "file_id": "建築基準法施行令.json"}`                            | 
---
### Setup servers with Docker
##### Set necessary env variables 
```
vi docker-compose.yaml
```
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
##### Run server
```
python main.py
```
#### Access API docs on browser
```
http://localhost:3000/docs
```
