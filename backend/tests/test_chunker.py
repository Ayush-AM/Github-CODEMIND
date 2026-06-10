from pathlib import Path

from backend.chunker import SemanticChunker
from backend.parser import SemanticParser


def test_python_chunks_follow_semantic_boundaries(tmp_path: Path) -> None:
    source = tmp_path / "service.py"
    source.write_text(
        "class AuthService:\n"
        "    def login(self):\n"
        "        return True\n\n"
        "def health():\n"
        "    return 'ok'\n",
        encoding="utf-8",
    )

    chunks = SemanticChunker(SemanticParser()).chunk_file(source, tmp_path)

    assert [(chunk.type, chunk.name) for chunk in chunks] == [
        ("class", "AuthService"),
        ("function", "login"),
        ("function", "health"),
    ]
    assert chunks[1].start_line == 2


def test_markdown_chunks_follow_headings(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text("# Overview\nHello\n## Setup\nRun it\n", encoding="utf-8")

    chunks = SemanticChunker(SemanticParser()).chunk_file(source, tmp_path)

    assert [chunk.name for chunk in chunks] == ["Overview", "Setup"]
