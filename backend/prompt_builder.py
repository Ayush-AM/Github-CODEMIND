from .models import SearchResult


class PromptBuilder:
    SYSTEM_PROMPT = """You are CodeMind AI, a repository analysis assistant.
Answer only from the supplied repository context. Never invent implementation details.
Mention relevant file names, classes, functions, and methods. If the context is insufficient,
say exactly what is unavailable. End with a short Evidence section listing cited file paths."""

    def build(self, question: str, results: list[SearchResult]) -> str:
        context = "\n\n".join(
            f"[{item.chunk.file}:{item.chunk.start_line}-{item.chunk.end_line}] "
            f"{item.chunk.type} {item.chunk.name}\n{item.chunk.content}"
            for item in results
        )
        return f"Repository Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer with citations."
