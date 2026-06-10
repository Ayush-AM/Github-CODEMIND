import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import Settings, get_settings
from .dependencies import get_loader, get_rag_engine, get_state_store
from .github_loader import GitHubLoader, RepositoryError
from .models import AskRequest, AskResponse, CloneRequest, RepositoryRequest
from .rag_engine import RagEngine
from .repository_state import StateStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health(state: StateStore = Depends(get_state_store)) -> dict:
    current = state.load()
    return {"status": "healthy", "active_repo_id": current.active_repo_id}


@app.post("/clone")
async def clone_repository(
    request: CloneRequest,
    loader: GitHubLoader = Depends(get_loader),
    state: StateStore = Depends(get_state_store),
) -> dict:
    try:
        repo_id, path = await run_in_threadpool(loader.clone, request.repo_url)
        state.register(repo_id, request.repo_url, path)
        return {"status": "success", "repo_id": repo_id}
    except RepositoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/index")
async def index_repository(
    request: RepositoryRequest,
    state: StateStore = Depends(get_state_store),
    rag: RagEngine = Depends(get_rag_engine),
) -> dict:
    try:
        repo_id = state.active_repo_id(request.repo_id)
        repository = Path(state.load().repositories[repo_id]["path"])
        files, chunks = await run_in_threadpool(rag.index, repo_id, repository)
        state.mark_indexed(repo_id, chunks)
        return {"status": "success", "repo_id": repo_id, "files": files, "chunks": chunks}
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/ask", response_model=AskResponse)
async def ask_repository(
    request: AskRequest,
    state: StateStore = Depends(get_state_store),
    rag: RagEngine = Depends(get_rag_engine),
    config: Settings = Depends(get_settings),
) -> AskResponse:
    try:
        repo_id = state.active_repo_id(request.repo_id)
        return await rag.ask(repo_id, request.question, request.top_k or config.top_k)
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if settings.frontend_dir.exists():
    app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
