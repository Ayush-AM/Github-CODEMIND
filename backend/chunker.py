from pathlib import Path

from .models import CodeChunk
from .parser import SemanticParser

LANGUAGES = {
    ".py": "python", ".java": "java", ".js": "javascript", ".ts": "typescript",
    ".tsx": "tsx", ".jsx": "jsx", ".cpp": "cpp", ".c": "c", ".h": "header",
    ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
}


class SemanticChunker:
    def __init__(self, parser: SemanticParser, max_lines: int = 180) -> None:
        self.parser = parser
        self.max_lines = max_lines

    def chunk_file(self, file_path: Path, repository: Path) -> list[CodeChunk]:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []
        relative = file_path.relative_to(repository).as_posix()
        language = LANGUAGES.get(file_path.suffix.lower(), "text")
        lines = content.splitlines()
        nodes = self.parser.parse(content, language)
        chunks = [
            self._make_chunk(relative, language, node.type, node.name, lines, node.start_line, node.end_line)
            for node in nodes
            if node.end_line >= node.start_line
        ]
        if not chunks:
            chunks = self._module_chunks(relative, language, lines)
        return [chunk for chunk in chunks if chunk.content.strip()]

    def _module_chunks(self, file: str, language: str, lines: list[str]) -> list[CodeChunk]:
        if not lines:
            return []
        return [
            self._make_chunk(file, language, "module", Path(file).name, lines, start, min(start + self.max_lines - 1, len(lines)))
            for start in range(1, len(lines) + 1, self.max_lines)
        ]

    @staticmethod
    def _make_chunk(
        file: str, language: str, chunk_type: str, name: str, lines: list[str], start: int, end: int
    ) -> CodeChunk:
        return CodeChunk(
            file=file,
            content="\n".join(lines[start - 1:end]),
            language=language,
            type=chunk_type,
            name=name,
            start_line=start,
            end_line=end,
        )
