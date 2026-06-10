import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".tsx", ".jsx", ".cpp", ".c", ".h",
    ".md", ".json", ".yaml", ".yml",
}
IGNORED_DIRECTORIES = {
    "node_modules", "build", "dist", "target", ".git", ".next", "venv",
    ".venv", "__pycache__", "coverage",
}


class FileScanner:
    def __init__(self, max_file_bytes: int = 1_000_000) -> None:
        self.max_file_bytes = max_file_bytes

    def scan(self, repository: Path) -> list[Path]:
        files: list[Path] = []
        for path in repository.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if any(part in IGNORED_DIRECTORIES for part in path.relative_to(repository).parts):
                continue
            try:
                if path.stat().st_size <= self.max_file_bytes:
                    files.append(path)
            except OSError:
                logger.warning("Could not inspect %s", path)
        return sorted(files)
