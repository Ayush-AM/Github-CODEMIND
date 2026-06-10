import logging
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RepositoryError(RuntimeError):
    pass


class GitHubLoader:
    def __init__(self, repositories_dir: Path) -> None:
        self.repositories_dir = repositories_dir

    @staticmethod
    def validate_url(repo_url: str) -> str:
        parsed = urlparse(repo_url.strip())
        if parsed.scheme != "https" or parsed.hostname not in {"github.com", "www.github.com"}:
            raise RepositoryError("Only public HTTPS GitHub repository URLs are supported.")
        path = parsed.path.strip("/").removesuffix(".git")
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", path):
            raise RepositoryError("Expected a GitHub URL in the form https://github.com/owner/repository.")
        return f"https://github.com/{path}.git"

    def clone(self, repo_url: str) -> tuple[str, Path]:
        safe_url = self.validate_url(repo_url)
        repo_name = Path(urlparse(safe_url).path).stem
        repo_id = f"{repo_name}-{uuid.uuid4().hex[:8]}".lower()
        destination = self.repositories_dir / repo_id
        staging = self.repositories_dir / f".{repo_id}.staging"
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", safe_url, str(staging)],
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
            staging.replace(destination)
            logger.info("Cloned %s into %s", safe_url, destination)
            return repo_id, destination
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            message = getattr(exc, "stderr", None) or str(exc)
            raise RepositoryError(f"Unable to clone repository: {message.strip()}") from exc
        finally:
            if staging.exists():
                try:
                    shutil.rmtree(staging, ignore_errors=True)
                except OSError:
                    logger.warning("Could not remove temporary clone directory %s", staging)
