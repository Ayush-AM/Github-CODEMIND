from .embeddings import EmbeddingProvider
from .models import SearchResult
from .vector_store import FaissVectorStore


class Retriever:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: FaissVectorStore) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(self, repo_id: str, question: str, top_k: int = 5) -> list[SearchResult]:
        candidate_count = max(top_k * 3, 20)
        query = self.embeddings.embed([question])
        candidates = self.vector_store.search(repo_id, query, candidate_count)

        q_lower = question.lower()
        is_broad = any(
            phrase in q_lower
            for phrase in [
                "explain", "overview", "what does", "architecture", "summary",
                "how does", "walkthrough", "about", "describe", "codebase", "structure"
            ]
        )
        if is_broad:
            overview_query = self.embeddings.embed(["main app index server architecture core components router entrypoint"])
            overview_results = self.vector_store.search(repo_id, overview_query, candidate_count)
            seen_keys = {(r.chunk.file, r.chunk.start_line) for r in candidates}
            for res in overview_results:
                key = (res.chunk.file, res.chunk.start_line)
                if key not in seen_keys:
                    candidates.append(res)
                    seen_keys.add(key)

        docs_count = 0
        selected: list[SearchResult] = []
        code_chunks: list[SearchResult] = []

        for item in candidates:
            is_doc = item.chunk.file.lower().endswith((".md", ".txt"))
            if is_doc:
                if docs_count < 2:
                    selected.append(item)
                    docs_count += 1
            else:
                code_chunks.append(item)

        needed = top_k - len(selected)
        if needed > 0:
            selected.extend(code_chunks[:needed])

        if len(selected) < top_k:
            selected_keys = {(r.chunk.file, r.chunk.start_line) for r in selected}
            for item in candidates:
                if (item.chunk.file, item.chunk.start_line) not in selected_keys:
                    selected.append(item)
                    if len(selected) >= top_k:
                        break

        selected.sort(key=lambda x: x.score, reverse=True)
        return selected[:top_k]
