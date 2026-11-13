"""Choose a real embedding provider (API or local) and implement this contract."""
import os
from typing import Protocol
from dotenv import load_dotenv
import openai

load_dotenv()

class Embedder(Protocol):
    model_name: str
    dimensions: int
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, question: str) -> list[float]: ...
class MyEmbedder:
    def __init__(self, model_name: str = "text-embedding-3-small") -> None:
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Không tìm thấy OPENAI_API_KEY trong file .env")
        self.client = openai.OpenAI(api_key=api_key)
        self.dimensions = 1536
    def embed_documents(self, texts: list[str], batch_size: int = 50) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            resp = self.client.embeddings.create(model=self.model_name, input=batch)
            embeddings.extend([item.embedding for item in resp.data])
        return embeddings
    def embed_query(self, question: str) -> list[float]:
        resp = self.client.embeddings.create(model=self.model_name, input=[question])
        return resp.data[0].embedding