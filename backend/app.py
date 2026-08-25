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

from contextlib import asynccontextmanager

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background task for automatic session cleanup
    async def cleanup_task():
        while True:
            try:
                await asyncio.sleep(60) # Check every minute
                state_store = get_state_store(settings)
                # Clear sessions inactive for more than 15 minutes (900 seconds)
                state_store.clear_expired(settings.repositories_dir, settings.indexes_dir, timeout_seconds=900)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Cleanup task error: {e}")

    task = asyncio.create_task(cleanup_task())
    yield
    # Stop the background task on shutdown
    task.cancel()
    # Automatically delete cloned repositories and indexes on server shutdown
    state_store = get_state_store(settings)
    state_store.clear_all(settings.repositories_dir, settings.indexes_dir)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
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


@app.delete("/clear")
def clear_session(
    state: StateStore = Depends(get_state_store),
    config: Settings = Depends(get_settings),
) -> dict:
    state.clear_all(config.repositories_dir, config.indexes_dir)
    return {"status": "success", "message": "All cloned repositories and indexes have been cleared."}



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
        
        # Delete the raw cloned repository immediately after it has been fully indexed
        # to save disk space and automatically clear the original code.
        import shutil
        shutil.rmtree(repository, ignore_errors=True)
        
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
