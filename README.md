# AskDocs 📚

AskDocs is a local-first RAG app for chatting with your own documents. It combines hybrid retrieval, reranking, citations, and a simple React interface so you can upload files and ask grounded questions about them.

## Features ✨

- Hybrid retrieval with BM25 + vector search
- Cross-encoder reranking for better top-k quality
- Citation-aware answers with retrieved source snippets
- Upload support for `.md`, `.txt`, and `.pdf`
- Local Ollama integration for private, no-API-cost inference
- File browser with open, delete, and clear-all actions
- Query progress, cancel button, and collapsible answer cards

## Tech Stack 🛠️

- Frontend: React, TypeScript, Vite, Tailwind-style utility classes
- Backend: FastAPI, Pydantic
- Vector DB: Qdrant
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- LLM: Ollama with `mistral` by default

## Prerequisites ✅

- Docker and Docker Compose
- Git
- Ollama installed locally if you want the best experience on macOS / Apple Silicon

For MacBook M-series devices, running Ollama on macOS directly is recommended so it can use Metal acceleration.

## Quick Start 🚀

### 1. Clone the repo 📦

```bash
git clone https://github.com/xzhu411/AskDocs.git
cd AskDocs
```

### 2. Create the backend env file ⚙️

```bash
cp backend/.env.example backend/.env
```

### 3. Install and start Ollama on your machine 🧠

Download Ollama for macOS:

`https://ollama.com/download/mac`

Then pull the default model:

```bash
ollama pull mistral
```

You can verify it is running with:

```bash
curl http://localhost:11434/api/tags
```

### 4. Start the app 🐳

```bash
docker compose up -d --build
```

### 5. Open the app 🌐

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Qdrant: `http://localhost:6333`

## Configuration 🔧

Edit `backend/.env.example` or your local `backend/.env`.

Important defaults:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
LLM_MODEL=mistral
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

RETRIEVAL_K=5
RERANK_TOP_K=3
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

If you are not on Docker Desktop for Mac, you may need to change `OLLAMA_BASE_URL`.

## Supported Files 📄

- Markdown `.md`
- Plain text `.txt`
- PDF `.pdf`

## Typical Workflow 🔄

1. Start Ollama locally.
2. Start Docker services with `docker compose up -d --build`.
3. Open the frontend.
4. Upload one or more documents.
5. Ask questions and inspect citations / retrieved sources.

## API Endpoints 🔌

### Health

```bash
curl http://localhost:8000/health
```

### Upload

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

### Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?", "k": 5, "top_k": 3}'
```

### List uploaded files

```bash
curl http://localhost:8000/files
```

### Delete one file

```bash
curl -X DELETE http://localhost:8000/files/<filename>
```

### Clear all files

```bash
curl -X DELETE http://localhost:8000/files
```

## Project Structure 🗂️

```text
AskDocs/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── rag/
│   │   ├── config.py
│   │   └── main.py
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Troubleshooting 🩺

### Backend is up but answers fail

Check backend logs:

```bash
docker compose logs --tail=120 backend
```

### Frontend changes do not appear

The frontend is containerized and not bind-mounted, so rebuild it:

```bash
docker compose build frontend
docker compose up -d frontend
```

### Ollama is slow on Apple Silicon

Make sure Ollama is running on macOS directly, not inside Docker. The backend is configured to use:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Verify Ollama models

```bash
ollama list
```

## Notes 📝

- `backend/.env` is intentionally ignored by git.
- Uploaded files in `backend/uploads/` are also ignored by git.
- This project is designed to run locally without paid LLM API usage.

## License 📄

MIT
