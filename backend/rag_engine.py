from pathlib import Path

from .chunker import SemanticChunker
from .embeddings import EmbeddingProvider
from .file_scanner import FileScanner
from .llm_provider import LLMProvider
from .models import AskResponse, Source
from .prompt_builder import PromptBuilder
from .retriever import Retriever
from .vector_store import FaissVectorStore


class RagEngine:
    def __init__(
        self,
        scanner: FileScanner,
        chunker: SemanticChunker,
        embeddings: EmbeddingProvider,
        vector_store: FaissVectorStore,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        llm: LLMProvider,
    ) -> None:
        self.scanner = scanner
        self.chunker = chunker
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = llm

    def index(self, repo_id: str, repository: Path) -> tuple[int, int]:
        files = self.scanner.scan(repository)
        chunks = [chunk for file in files for chunk in self.chunker.chunk_file(file, repository)]
        if not chunks:
            raise ValueError("No supported source files were found in the repository.")
        vectors = self.embeddings.embed([chunk.embedding_text() for chunk in chunks])
        self.vector_store.save(repo_id, vectors, chunks)
        return len(files), len(chunks)

    async def ask(self, repo_id: str, question: str, top_k: int) -> AskResponse:
        results = self.retriever.retrieve(repo_id, question, top_k)
        prompt = self.prompt_builder.build(question, results)
        answer = await self.llm.generate(self.prompt_builder.SYSTEM_PROMPT, prompt, results)
        confidence = "High" if results and results[0].score >= 0.55 else "Medium" if results and results[0].score >= 0.3 else "Low"
        sources = [
            Source(
                file=item.chunk.file,
                type=item.chunk.type,
                name=item.chunk.name,
                start_line=item.chunk.start_line,
                end_line=item.chunk.end_line,
                score=round(item.score, 4),
            )
            for item in results
        ]
        return AskResponse(answer=answer, sources=sources, confidence=confidence)
