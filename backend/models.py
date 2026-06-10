from typing import Any, Literal

from pydantic import BaseModel, Field


class CodeChunk(BaseModel):
    file: str
    content: str
    language: str
    type: str
    name: str
    start_line: int = 1
    end_line: int = 1

    def embedding_text(self) -> str:
        return f"{self.file}\n{self.type}: {self.name}\n{self.content}"


class SearchResult(BaseModel):
    chunk: CodeChunk
    score: float


class CloneRequest(BaseModel):
    repo_url: str


class RepositoryRequest(BaseModel):
    repo_id: str | None = None


class AskRequest(RepositoryRequest):
    question: str = Field(min_length=2)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Source(BaseModel):
    file: str
    type: str
    name: str
    start_line: int
    end_line: int
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: Literal["High", "Medium", "Low"]


class RepositoryState(BaseModel):
    active_repo_id: str | None = None
    repositories: dict[str, dict[str, Any]] = Field(default_factory=dict)
