import requests
from app.core.qdrant_manager import QdrantManager


class RagService:
    def __init__(self):
        self.qdrant = QdrantManager()
        self.llm_url = "http://host.docker.internal:11434/api/generate"

    async def get_answer(self, message: str, user_id: str):
        # 1. Get embedding for the question
        query_vector = self.qdrant.get_embedding(message)

        # 2. Retrieve relevant chunks from Qdrant
        context_chunks = self.qdrant.search(query_vector=query_vector, user_id=user_id)
        context_text = "\n\n".join(context_chunks)

        # 3. Construct the prompt for the LLM
        prompt = f"""
        You are a helpful assistant. Use the following pieces of context to answer the user's question.
        If you don't know the answer, just say you don't know.

        Context:
        {context_text}

        Question: {message}
        Answer:
        """

        # 4. Call Llama3 via Ollama
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }

        try:
            res = requests.post(self.llm_url, json=payload)
            res.raise_for_status()
            answer = res.json().get("response", "I encountered an error generating an answer.")
            return answer, ["resume.pdf"] if context_chunks else []
        except Exception as e:
            return f"LLM Error: {str(e)}", []