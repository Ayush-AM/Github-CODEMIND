from .models import SearchResult


class PromptBuilder:
    SYSTEM_PROMPT = """You are CodeMind AI, an expert software engineer and repository analysis assistant.
Answer the user's question thoroughly, clearly, and accurately based on the provided repository context.
- When asked to explain or provide an overview of the codebase, synthesize the project's purpose, key features, architecture, components, and tech stack from the available files.
- Walk through the key functions, classes, and logic present in the context.
- Cite specific file paths and line ranges (e.g. `src/App.tsx:1-40`).
- Conclude with a clear Evidence section summarizing the cited files and components."""

    def build(self, question: str, results: list[SearchResult]) -> str:
        context = "\n\n".join(
            f"[{item.chunk.file}:{item.chunk.start_line}-{item.chunk.end_line}] "
            f"{item.chunk.type} {item.chunk.name}\n{item.chunk.content}"
            for item in results
        )
        return f"Repository Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer with citations."
