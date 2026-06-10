from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

import numpy as np


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: Sequence[str]) -> np.ndarray:
        raise NotImplementedError


class SentenceTransformerEmbeddings(EmbeddingProvider):
    def __init__(self, model_name: str, cache_dir: Path | None = None) -> None:
        self.model_name = model_name
        self.cache_dir = cache_dir
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, cache_folder=str(self.cache_dir) if self.cache_dir else None)
        return self._model

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        vectors = self._load().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)
