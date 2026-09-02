# Agentic RAG

Agentic RAG is a full-stack application for querying a local document knowledge base through a chat interface. It routes arithmetic expressions to a local evaluator; for other questions, it retrieves relevant document chunks when available and uses a local Ollama model to generate a structured answer. The project is contained in this single repository, with the React frontend and FastAPI backend running as separate local services.

## Features

- LangGraph workflow that routes arithmetic, retrieval-backed, and direct-answer paths
- PDF and text document ingestion from the local knowledge base
- Text chunking and semantic embeddings with `BAAI/bge-small-en-v1.5`
- Persistent local Qdrant vector store with top-result retrieval and source metadata
- Ollama-powered answer generation with a grounded RAG prompt when context is relevant
- Structured chat responses with answer text, sources, route, relevance score, and timings
- React chat UI with loading, empty, and request-error states
- FastAPI API with validation, CORS configuration, health endpoints, and Swagger documentation

Web search and conversation memory are not implemented.

## Architecture

```text
User
  ↓
React + Vite frontend
  ↓  POST /chat
FastAPI backend
  ↓
LangGraph router
  ├── Arithmetic evaluator
  └── Vector retrieval (Qdrant)
        ↓
   Context + Ollama LLM
        ↓
Structured API response
  ↓
React chat UI
```

- **Frontend** collects a question and sends it to the configured FastAPI base URL.
- **FastAPI** validates the request and returns a predictable chat response or a clear HTTP error.
- **LangGraph router** identifies simple arithmetic locally; all other questions attempt retrieval first and fall back to a direct LLM answer for low-relevance or empty results.
- **Vector store** loads documents, splits them into chunks, embeds them, and stores/searches vectors locally through Qdrant.
- **Ollama** produces the final answer as JSON, using retrieved context only on the RAG path.

## Project Structure

```text
agentic-rag/
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── config.py            # Environment-based settings
│   ├── langgraph_rag.py     # LangGraph routing and answer generation
│   ├── vector_store.py      # Qdrant indexing and retrieval
│   ├── load_docs.py         # PDF and text document loading
│   ├── chunking.py          # Document chunking
│   ├── embeddings.py        # SentenceTransformer model loader
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # Chat and message UI
│   │   └── services/api.js  # Central frontend API client
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── data/research_papers/    # PDF and text knowledge-base documents
├── architecture.txt         # Architecture reference diagram
├── .gitignore
└── README.md
```

The local `.vector_store/` directory is created automatically after the first retrieval and is intentionally ignored by Git.

## Tech Stack

### Frontend

- React 19
- Vite 8
- JavaScript
- CSS

### Backend

- Python 3.9+
- FastAPI and Uvicorn
- LangGraph and LangChain Community
- Qdrant local vector store
- Sentence Transformers (`BAAI/bge-small-en-v1.5`)
- Ollama (`phi` by default)
- PyMuPDF document loader

## Prerequisites

- Python 3.9 or later
- Node.js 20.19+, 22.13+, or later (required by the installed ESLint/Vite tooling)
- npm
- [Ollama](https://ollama.com/) installed locally

No API key is required: the application uses local Ollama and a local Qdrant store.

## Environment Variables

Example files are provided separately for the backend and frontend. They contain placeholders/defaults only and should be copied before local customization:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Backend (`backend/.env`)

| Variable | Required | Purpose |
| --- | --- | --- |
| `OLLAMA_MODEL` | No | Ollama model name. Defaults to `phi`. |
| `OLLAMA_BASE_URL` | No | Custom Ollama server URL. Uses Ollama's local default when omitted. |
| `CORS_ORIGINS` | No | Comma-separated frontend origins allowed to call the API. |
| `VECTOR_STORE_PATH` | No | Local Qdrant data directory. Defaults to `.vector_store` at the repository root. |

### Frontend (`frontend/.env`)

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | No | FastAPI base URL. Defaults to `http://localhost:8000`. |

Never commit `.env` files or credentials. `.env.example` is safe to commit because it contains no secrets.

## Backend Setup

From the repository root:

```bash
cd backend
python3 -m venv .venv
```

Activate the virtual environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Install dependencies and configure the optional environment file:

```bash
pip install -r requirements.txt
cp .env.example .env
```

Start Ollama in a separate terminal and download the default model once:

```bash
ollama serve
ollama pull phi
```

Start the API:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup

In a second terminal, from the repository root:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Useful frontend checks:

```bash
npm run lint
npm run build
```

## Running the Application

Use three terminals for local development:

1. Run `ollama serve` (and `ollama pull phi` once).
2. Start FastAPI from `backend/` with `uvicorn main:app --reload --host 127.0.0.1 --port 8000`.
3. Start Vite from `frontend/` with `npm run dev`.

Open http://localhost:5173 in a browser. The services are available at:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger API documentation: http://localhost:8000/docs

On the first non-arithmetic query, the backend builds the local vector index. This can take longer than subsequent queries because the documents are chunked and embedded once.

## Frontend ↔ Backend Configuration

The frontend does not scatter API URLs across React components. [`frontend/src/services/api.js`](frontend/src/services/api.js) reads `VITE_API_URL` and sends `POST /chat` requests to that base URL. Its default is `http://localhost:8000`; change `frontend/.env` when the backend runs elsewhere, then restart Vite.

The backend allows `http://localhost:5173` and `http://127.0.0.1:5173` by default. Change `CORS_ORIGINS` in `backend/.env` if the frontend uses another origin.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Returns API status and a short message. |
| `GET` | `/health` | Basic health check. |
| `POST` | `/chat` | Sends a question through the Agentic RAG workflow. |
| `POST` | `/debug/route` | Returns routing, retrieval, and timing metadata without the generated answer. |

### `POST /chat`

Request body:

```json
{
  "question": "What does the company policy say about leave?"
}
```

Successful response shape:

```json
{
  "question": "What does the company policy say about leave?",
  "answer": {
    "summary": "...",
    "details": "...",
    "key_points": ["..."]
  },
  "sources": ["..."],
  "route": "rag",
  "relevance_score": 0.0,
  "timings": {
    "analyze": 0.0,
    "retrieve": 0.0,
    "llm_invoke": 0.0,
    "generate": 0.0,
    "total": 0.0
  }
}
```

Questions must be non-empty and at most 4,000 characters. A missing Ollama service or unavailable knowledge base returns HTTP `503`; unexpected processing errors return HTTP `500` without exposing internal details.

## Agentic RAG Flow

```text
User question
→ React chat interface
→ FastAPI POST /chat
→ LangGraph analysis
→ arithmetic evaluator OR vector retrieval
→ relevant context OR direct-answer fallback
→ Ollama JSON response generation
→ sources, route, score, and timings returned to the UI
```

Arithmetic expressions such as `2 + 2` are calculated locally. Other questions search the knowledge base; retrieval is used only when the top result meets the configured relevance threshold (`0.55`). Otherwise, the system requests a direct Ollama answer.

## Knowledge Base and Document Ingestion

Documents live in `data/research_papers/`. The loader supports `.pdf` and `.txt` files recursively, so additional supported files can be placed in that directory or its subdirectories.

```text
PDF/TXT documents
→ PyMuPDF/Text loader
→ Recursive character chunking (500 characters, 100 overlap)
→ BAAI/bge-small-en-v1.5 embeddings
→ Local Qdrant collection
→ Similarity retrieval for chat requests
```

The index is created lazily the first time retrieval is required and reused from `.vector_store/` afterwards. To rebuild it after changing source documents, stop the backend, delete the local `.vector_store/` directory, then start the backend and submit a document question.

## API Documentation

FastAPI exposes interactive Swagger documentation at http://localhost:8000/docs. Use it to inspect schemas and test the available endpoints directly.

## Error Handling

- FastAPI validates empty and oversized questions.
- The backend returns HTTP `503` when Ollama or retrieval is unavailable and HTTP `500` for unexpected failures.
- Document-loading/indexing failures are surfaced as retrieval errors rather than crashing the API process.
- The React UI disables duplicate sends while a request is active and displays loading, empty, and request-error states.

## Security

- Keep configuration and any future credentials in local `.env` files.
- Do not commit `.env`, local vector data, virtual environments, or `node_modules`.
- Commit only `.env.example` files with safe placeholder/default values.
- Never add API keys, tokens, or passwords to this public repository.
