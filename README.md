# CodeMind AI

CodeMind AI is a local-first GitHub repository intelligence MVP. It clones a public repository, identifies semantic code sections, embeds them with `sentence-transformers/all-MiniLM-L6-v2`, persists them in FAISS, and answers questions with source citations.

## Architecture

```text
GitHub URL -> safe clone -> file scanner -> semantic parser/chunker
           -> embeddings -> persisted FAISS index -> retrieval
           -> grounded prompt -> Groq / OpenAI / Grok -> answer + citations
```

The backend uses small provider interfaces for embeddings and LLMs. `FaissVectorStore`, `SentenceTransformerEmbeddings`, and `OpenAICompatibleProvider` can be replaced later with Qdrant/Pinecone, another embedding model, or another model API without changing the API layer.

## Run with Docker

1. Copy `.env.example` to `.env` and add `GROQ_API_KEY`, `OPENAI_API_KEY`, or `XAI_API_KEY`.
2. Run:

```bash
docker compose up --build
```

Open `http://localhost:5173`. The backend API and Swagger documentation are available at `http://localhost:8000` and `http://localhost:8000/docs`.

An API key is optional. Without one, retrieval and citations still work, and CodeMind returns the most relevant code sections instead of a generated explanation.

To use Groq, set:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

## Run locally

Backend:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The embedding model downloads on the first indexing request. Repository clones, indexes, model cache, and state are stored under `backend/repositories`, `backend/indexes`, and `backend/data`.

## API

- `POST /clone` with `{"repo_url":"https://github.com/owner/repository.git"}`
- `POST /index` with `{"repo_id":"..."}`; omitting `repo_id` uses the active repository
- `POST /ask` with `{"repo_id":"...","question":"Where is JWT implemented?","top_k":5}`
- `GET /health`

## Tests

```bash
pip install pytest
pytest backend/tests
```

The MVP deliberately leaves hybrid search, reranking, dependency graphs, visualizations, private repositories, and multi-repository retrieval as extension points rather than partially implementing them.

## Production Deployment (AWS Elastic Beanstalk)

CodeMind AI is deployed live on **AWS Elastic Beanstalk** (`ap-south-1` region) as a single container application using Docker:

- **Live Web App**: [http://codemind-prod.ap-south-1.elasticbeanstalk.com/](http://codemind-prod.ap-south-1.elasticbeanstalk.com/)
- **Health Check**: [http://codemind-prod.ap-south-1.elasticbeanstalk.com/health](http://codemind-prod.ap-south-1.elasticbeanstalk.com/health)

See [DEPLOYMENT.md](file:///c:/Ayush/Desktop/codemind-deploy/DEPLOYMENT.md) for full step-by-step instructions, infrastructure architecture, environment variable configuration, and maintenance commands.

