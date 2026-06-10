import json
from pathlib import Path

from .models import RepositoryState


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> RepositoryState:
        if not self.path.exists():
            return RepositoryState()
        return RepositoryState.model_validate_json(self.path.read_text(encoding="utf-8"))

    def save(self, state: RepositoryState) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def active_repo_id(self, requested: str | None = None) -> str:
        state = self.load()
        repo_id = requested or state.active_repo_id
        if not repo_id or repo_id not in state.repositories:
            raise KeyError("No repository is active. Clone a repository first.")
        return repo_id

    def register(self, repo_id: str, repo_url: str, path: Path) -> None:
        state = self.load()
        state.repositories[repo_id] = {"url": repo_url, "path": str(path), "indexed": False}
        state.active_repo_id = repo_id
        self.save(state)

    def mark_indexed(self, repo_id: str, chunks: int) -> None:
        state = self.load()
        state.repositories[repo_id]["indexed"] = True
        state.repositories[repo_id]["chunks"] = chunks
        self.save(state)
