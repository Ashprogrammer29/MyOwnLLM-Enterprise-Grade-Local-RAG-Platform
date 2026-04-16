import uuid
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client.http import models as qdrant_models
from app.core.qdrant_manager import QdrantManager


class IngestionService:
    def __init__(self):
        self.qdrant = QdrantManager()
        # Why Recursive? It preserves semantic context by splitting
        # at paragraphs, then sentences, then words.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100  # Increased overlap to ensure context flow
        )
        # We define the model as a constant to avoid magic strings
        self.EMBED_MODEL = "nomic-embed-text"

    async def process_and_upload(self, text: str, user_id: str, filename: str):
        # 1. Chunking
        chunks = self.splitter.split_text(text)

        points = []

        # 2. Batch Embedding (Senior Optimization)
        # We loop through chunks and get embeddings from local Ollama
        for chunk in chunks:
            response = ollama.embeddings(
                model=self.EMBED_MODEL,
                prompt=chunk
            )
            vector = response["embedding"]

            # 3. Create the Point Struct
            # id: UUID ensures uniqueness in the HNSW graph
            # vector: The semantic fingerprint
            # payload: The metadata used for Bitmask filtering
            points.append(qdrant_models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "user_id": user_id,
                    "filename": filename,
                    "content": chunk
                }
            ))
        self.client = QdrantClient(host="qdrant", port=6333)

        # 4. Upsert into Qdrant
        # This triggers the HNSW map update we discussed
        self.qdrant.client.upsert(
            collection_name=self.qdrant.collection_name,
            points=points
        )

        return len(points)