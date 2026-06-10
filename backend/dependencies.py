from functools import lru_cache

from .chunker import SemanticChunker
from .config import get_settings
from .embeddings import SentenceTransformerEmbeddings
from .file_scanner import FileScanner
from .github_loader import GitHubLoader
from .llm_provider import create_llm_provider
from .parser import SemanticParser
from .prompt_builder import PromptBuilder
from .rag_engine import RagEngine
from .repository_state import StateStore
from .retriever import Retriever
from .vector_store import FaissVectorStore


@lru_cache
def get_state_store() -> StateStore:
    settings = get_settings()
    return StateStore(settings.data_dir / "state.json")


@lru_cache
def get_loader() -> GitHubLoader:
    return GitHubLoader(get_settings().repositories_dir)


@lru_cache
def get_rag_engine() -> RagEngine:
    settings = get_settings()
    embeddings = SentenceTransformerEmbeddings(settings.embedding_model, settings.embedding_cache_dir)
    vector_store = FaissVectorStore(settings.indexes_dir)
    return RagEngine(
        scanner=FileScanner(settings.max_file_bytes),
        chunker=SemanticChunker(SemanticParser()),
        embeddings=embeddings,
        vector_store=vector_store,
        retriever=Retriever(embeddings, vector_store),
        prompt_builder=PromptBuilder(),
        llm=create_llm_provider(settings),
    )
