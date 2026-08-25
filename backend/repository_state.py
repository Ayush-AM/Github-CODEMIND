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
        
        import time
        state.repositories[repo_id]["last_accessed"] = time.time()
        self.save(state)
        
        return repo_id

    def register(self, repo_id: str, repo_url: str, path: Path) -> None:
        state = self.load()
        import time
        state.repositories[repo_id] = {"url": repo_url, "path": str(path), "indexed": False, "last_accessed": time.time()}
        state.active_repo_id = repo_id
        self.save(state)

    def mark_indexed(self, repo_id: str, chunks: int) -> None:
        state = self.load()
        state.repositories[repo_id]["indexed"] = True
        state.repositories[repo_id]["chunks"] = chunks
        self.save(state)

    def clear_all(self, repos_dir: Path, indexes_dir: Path) -> None:
        import shutil
        if repos_dir.exists():
            for child in repos_dir.iterdir():
                if child.is_dir() and not child.name.startswith("."):
                    shutil.rmtree(child, ignore_errors=True)
        if indexes_dir.exists():
            for child in indexes_dir.iterdir():
                if child.is_dir() and not child.name.startswith("."):
                    shutil.rmtree(child, ignore_errors=True)
        if self.path.exists():
            self.path.unlink(missing_ok=True)

    def clear_expired(self, repos_dir: Path, indexes_dir: Path, timeout_seconds: int = 1800) -> None:
        import time
        import shutil
        state = self.load()
        now = time.time()
        expired = []
        for repo_id, data in state.repositories.items():
            last = data.get("last_accessed", now)
            if now - last > timeout_seconds:
                expired.append(repo_id)
        
        if not expired:
            return
            
        for repo_id in expired:
            repo_path = Path(state.repositories[repo_id]["path"])
            index_path = indexes_dir / repo_id
            if repo_path.exists():
                shutil.rmtree(repo_path, ignore_errors=True)
            if index_path.exists():
                shutil.rmtree(index_path, ignore_errors=True)
            del state.repositories[repo_id]
            if state.active_repo_id == repo_id:
                state.active_repo_id = None
                
        self.save(state)
