# AskMyDocs - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                │
│                  (http://localhost:5173)                        │
│                                                                  │
│   ┌──────────────────────────────────────────────────────┐      │
│   │  React Frontend (Vite)                               │      │
│   │  ├── App.tsx (Main)                                  │      │
│   │  ├── FileUpload.tsx (Document ingestion)             │      │
│   │  ├── QueryInput.tsx (Query interface)                │      │
│   │  ├── Answer.tsx (Results display)                    │      │
│   │  └── Components (UI library)                         │      │
│   └──────────┬───────────────────────┬────────────────────┘      │
└──────────────┼───────────────────────┼──────────────────────────┘
               │ HTTP REST API         │
               │                       │
┌──────────────┼───────────────────────┼──────────────────────────┐
│   Backend (Python - FastAPI)          │                         │
│   (http://localhost:8000)             │                         │
│   ┌─────────────────────────────────┐ │                        │
│   │ FastAPI Application             │ │                        │
│   │ ├── /query        POST          │ │                        │
│   │ ├── /upload       POST          │ │                        │
│   │ ├── /health       GET           │ │                        │
│   │ └── /docs         GET (Swagger) │ │                        │
│   └────────────┬────────────────────┘ │                        │
│                │                       │                        │
│   ┌────────────▼─────────────────────────────────────────┐     │
│   │ RAG Pipeline                                         │     │
│   │                                                      │     │
│   │  Query Input                                        │     │
│   │       │                                             │     │
│   │       ▼                                             │     │
│   │  ┌─────────────────────────────┐                   │     │
│   │  │ Hybrid Retrieval            │                   │     │
│   │  │ ├─ BM25 (Keyword Match)     │──┐                │     │
│   │  │ └─ Vector Search (Semantic) │──┤                │     │
│   │  └──────────────────────────────┘  │                │     │
│   │                                     │                │     │
│   │  ┌──────────────────────────────┐  │                │     │
│   │  │ Cross-Encoder Reranking      │◀─┘                │     │
│   │  │ (ms-marco-MiniLM-L-6-v2)     │                   │     │
│   │  └──────────┬───────────────────┘                   │     │
│   │             │                                       │     │
│   │  ┌──────────▼───────────────────┐                   │     │
│   │  │ LLM Generation               │                   │     │
│   │  │ (Ollama + Mistral/Llama)     │                   │     │
│   │  └──────────┬───────────────────┘                   │     │
│   │             │                                       │     │
│   │  ┌──────────▼───────────────────┐                   │     │
│   │  │ Citation Extraction          │                   │     │
│   │  │ & Formatting                 │                   │     │
│   │  └──────────┬───────────────────┘                   │     │
│   │             │                                       │     │
│   │  Response with Citations                           │     │
│   │                                                     │     │
│   └─────────────┬──────────────────────────────────────┘     │
└─────────────────┼──────────────────────────────────────────────┘
                  │
│  ┌──────────────┴─────────────────────────────────────┐  │
│  │ Data Storage & Processing Layer                   │  │
│  │                                                   │  │
│  │  ┌──────────────────────────────────────┐        │  │
│  │  │ Qdrant (Vector Database)              │        │  │
│  │  │ http://localhost:6333                 │        │  │
│  │  │ └─ Dense embeddings of documents      │        │  │
│  │  └──────────────────────────────────────┘        │  │
│  │                                                   │  │
│  │  ┌──────────────────────────────────────┐        │  │
│  │  │ Ollama (Local LLM Server)             │        │  │
│  │  │ http://localhost:11434                │        │  │
│  │  │ ├─ Mistral (default)                  │        │  │
│  │  │ ├─ Llama2 (alternative)               │        │  │
│  │  │ └─ nomic-embed-text (embeddings)      │        │  │
│  │  └──────────────────────────────────────┘        │  │
│  │                                                   │  │
│  │  ┌──────────────────────────────────────┐        │  │
│  │  │ File Storage                          │        │  │
│  │  │ └─ backend/uploads/ (documents)       │        │  │
│  │  └──────────────────────────────────────┘        │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Document Upload Flow
```
User Upload
    │
    ▼
Frontend: FileUpload component
    │
    ▼
POST /upload
    │
    ▼
Backend: Document Processor
    │
    ├─ Split into chunks (1000 tokens)
    ├─ Create embeddings (nomic-embed-text)
    │
    ├─ BM25 Index
    │
    └─ Vector Store (Qdrant)
         │
         ▼
    Response: "Processed X chunks"
```

### 2. Query Flow
```
User Query
    │
    ▼
Frontend: QueryInput component
    │
    ▼
POST /query {"query": "...", "k": 5, "top_k": 3}
    │
    ▼
Backend: RAG Chain
    │
    ├─ Step 1: Hybrid Retrieval
    │   ├─ BM25 Search (50%)
    │   ├─ Vector Search (50%)
    │   └─ Combine & rank top 5
    │
    ├─ Step 2: Reranking
    │   └─ Cross-encoder: Select top 3
    │
    ├─ Step 3: Context Formation
    │   └─ Format retrieved docs as context
    │
    ├─ Step 4: LLM Generation
    │   ├─ Call Ollama/Mistral
    │   └─ Generate answer with context
    │
    ├─ Step 5: Citation Extraction
    │   ├─ Parse [1], [2], etc. from answer
    │   └─ Map to source documents
    │
    └─ Response JSON
         {
           "answer": "Generated answer...",
           "citations": [...],
           "documents": [...],
           "confidence": 0.85,
           "processing_time": 2.34
         }
    │
    ▼
Frontend: Answer component
    │
    ├─ Display answer
    ├─ Show citations
    ├─ List source documents
    └─ Display confidence score
```

## Component Details

### Backend Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Retriever** | rank-bm25, sentence-transformers | BM25 + Vector search |
| **Reranker** | sentence-transformers | Cross-encoder reranking |
| **LLM Client** | Ollama HTTP API | Local LLM inference |
| **Vector Store** | Qdrant | Persistent embeddings |
| **Document Processor** | Custom | Chunking & ingestion |
| **FastAPI** | FastAPI + Uvicorn | REST API server |

### Frontend Components

| Component | Purpose |
|-----------|---------|
| App.tsx | Main application container |
| FileUpload.tsx | Document upload UI |
| QueryInput.tsx | Query interface |
| Answer.tsx | Results display with citations |
| api.ts | Backend API client |
| components.tsx | Reusable UI components |

## Configuration Points

### RAG Tuning (backend/.env)
```
RETRIEVAL_K=5              # Docs to retrieve
RERANK_TOP_K=3             # Docs after reranking
BM25_WEIGHT=0.5            # Keyword search weight
VECTOR_WEIGHT=0.5          # Semantic search weight
CHUNK_SIZE=1000            # Doc chunk size
CHUNK_OVERLAP=200          # Chunk overlap
```

### Model Selection
```
LLM_MODEL=mistral          # Can use: mistral, llama2, neural-chat
EMBEDDING_MODEL=nomic-embed-text
```

### API Configuration
```
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

## Performance Characteristics

- **Query Speed**: 1-5 seconds (depends on document count)
- **Upload Speed**: depends on file size
- **Memory**: ~4GB (with Ollama + models)
- **Storage**: Depends on document count
- **Throughput**: ~10-20 queries/sec (single instance)

## Security Considerations

1. ✅ No credentials in frontend
2. ✅ CORS configured
3. ✅ Input validation on API
4. ✅ Environment variables for secrets
5. ⚠️ Consider: Auth/authentication layer
6. ⚠️ Consider: Rate limiting
7. ⚠️ Consider: API key management

## Scaling Strategy

### Horizontal
- Multiple backend instances with load balancer
- Managed Qdrant Cloud
- Managed LLM endpoints

### Vertical
- Increase CPU/memory per container
- Faster embedding models
- Better hardware

## Monitoring Needs

1. **API Health**: /health endpoint
2. **Performance**: Query latency, throughput
3. **Quality**: Answer confidence scores
4. **Resources**: CPU, memory, disk usage
5. **Errors**: Exception tracking (Sentry)
