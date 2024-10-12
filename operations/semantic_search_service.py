import json

from fastapi import status
from fastapi.responses import JSONResponse


class SemanticSearchService:

    def __init__(self, settings, pinecone_index, embedding_client, redis_client):
        self.settings = settings
        self.pinecone_index = pinecone_index
        self.embedding_client = embedding_client
        self.redis_client = redis_client

    def search(self, search_term, file_id):
        search_key = f"{search_term}_{file_id}"

        if self.redis_client.get(search_key) is not None:
            response_data = self.redis_client.get(search_key)
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=json.loads(response_data)
            )

        term_embedding = self.embedding_client.embed_query(search_term)

        result = self.pinecone_index.query(
            filter={"file_id": {"$eq": file_id}},
            vector=term_embedding,
            top_k=5,
            include_values=False,
            namespace=self.settings.embedding_namespace,
            include_metadata=True,
        )

        match_texts = []

        for text in result.matches:
            metadata = text.metadata
            match_texts.append(
                {
                    "score": text.score,
                    "text": metadata.get("text"),
                }
            )

        response_data = {"data": match_texts}
        self.redis_client.set(search_key, json.dumps(response_data), ex=86400)

        return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)
