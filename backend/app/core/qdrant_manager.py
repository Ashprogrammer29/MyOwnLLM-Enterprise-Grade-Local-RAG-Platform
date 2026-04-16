import uuid
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

class QdrantManager:
    def __init__(self):
        # Service name 'qdrant' must match docker-compose.yml
        self.client = QdrantClient(host="qdrant", port=6333)
        self.collection_name = "document_chunks"
        # host.docker.internal allows the container to talk to Ollama on your Windows host
        self.embedding_url = "http://host.docker.internal:11434/api/embeddings"
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(size=768, distance=rest.Distance.COSINE),
            )

    def get_embedding(self, text: str):
        payload = {"model": "nomic-embed-text", "prompt": text}
        res = requests.post(self.embedding_url, json=payload)
        res.raise_for_status()
        return res.json()["embedding"]

    def index_document(self, text: str, filename: str, user_id: str):
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        points = []
        for chunk in chunks:
            vector = self.get_embedding(chunk)
            points.append(rest.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk,
                    "filename": filename,
                    "user_id": user_id
                }
            ))
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, user_id, limit=5):
        """ This is the function your Traceback was screaming for """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="user_id",
                        match=rest.MatchValue(value=user_id),
                    )
                ]
            ),
            limit=limit,
        )
        return [res.payload["text"] for res in results if "text" in res.payload]