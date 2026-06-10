import json
import shutil
from pathlib import Path

import faiss
import numpy as np

from .models import CodeChunk, SearchResult


class FaissVectorStore:
    def __init__(self, indexes_dir: Path) -> None:
        self.indexes_dir = indexes_dir

    def save(self, repo_id: str, embeddings: np.ndarray, chunks: list[CodeChunk]) -> None:
        target = self.indexes_dir / repo_id
        staging = self.indexes_dir / f".{repo_id}.staging"
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(np.ascontiguousarray(embeddings, dtype=np.float32))
        faiss.write_index(index, str(staging / "index.faiss"))
        (staging / "chunks.json").write_text(
            json.dumps([chunk.model_dump() for chunk in chunks], indent=2),
            encoding="utf-8",
        )
        shutil.rmtree(target, ignore_errors=True)
        staging.replace(target)

    def exists(self, repo_id: str) -> bool:
        path = self.indexes_dir / repo_id
        return (path / "index.faiss").exists() and (path / "chunks.json").exists()

    def search(self, repo_id: str, query: np.ndarray, top_k: int) -> list[SearchResult]:
        path = self.indexes_dir / repo_id
        if not self.exists(repo_id):
            raise FileNotFoundError(f"No index found for repository '{repo_id}'.")
        index = faiss.read_index(str(path / "index.faiss"))
        chunks = [CodeChunk.model_validate(item) for item in json.loads((path / "chunks.json").read_text(encoding="utf-8"))]
        scores, ids = index.search(np.ascontiguousarray(query, dtype=np.float32), min(top_k, len(chunks)))
        return [
            SearchResult(chunk=chunks[int(chunk_id)], score=float(score))
            for score, chunk_id in zip(scores[0], ids[0])
            if chunk_id >= 0
        ]
