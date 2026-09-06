from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeMind AI"
    cors_origins: str = "http://localhost:5173"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = "auto"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str | None = None
    groq_model: str = "groq/compound-mini"
    xai_api_key: str | None = None
    xai_model: str = "grok-3-mini"
    top_k: int = 5
    max_file_bytes: int = 1_000_000
    storage_root: Path | None = None
    frontend_dist_dir: Path | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def backend_dir(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def repositories_dir(self) -> Path:
        return self.storage_base / "repositories"

    @property
    def indexes_dir(self) -> Path:
        return self.storage_base / "indexes"

    @property
    def data_dir(self) -> Path:
        return self.storage_base / "data"

    @property
    def storage_base(self) -> Path:
        return self.storage_root or self.backend_dir

    @property
    def frontend_dir(self) -> Path:
        return self.frontend_dist_dir or self.backend_dir.parent / "frontend" / "dist"

    @property
    def embedding_cache_dir(self) -> Path:
        return self.data_dir / "embedding-models"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_directories(self) -> None:
        for path in (self.repositories_dir, self.indexes_dir, self.data_dir, self.embedding_cache_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
