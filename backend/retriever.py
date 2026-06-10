from .embeddings import EmbeddingProvider
from .models import SearchResult
from .vector_store import FaissVectorStore


class Retriever:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: FaissVectorStore) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(self, repo_id: str, question: str, top_k: int = 5) -> list[SearchResult]:
        query = self.embeddings.embed([question])
        return self.vector_store.search(repo_id, query, top_k)
