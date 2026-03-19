# AskMyDocs Platform - Build from Scratch ✨

A production-grade **Retrieval-Augmented Generation (RAG)** platform with:
- 🔍 **Hybrid Retrieval**: BM25 full-text search + Vector embeddings (Qdrant)
- 🔄 **Cross-Encoder Reranking**: Improve precision with learning-to-rank
- 📝 **Citation Enforcement**: Every answer is backed by sources
- 📊 **Evaluation Pipeline**: RAGAS-based metrics for quality assurance
- 🎨 **Modern Frontend**: React + TypeScript web interface
- 🐳 **Docker Ready**: Local development with docker-compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- ~30GB disk (for models)

### 1. Clone & Setup

```bash
cd /Users/zhuxiaoai/Projects/AskMyDocs
cp backend/.env.example backend/.env
```

### 2. Start Services

```bash
# Start all services (Qdrant, Ollama, Backend, Frontend)
docker-compose up -d

# Wait for services to be ready (2-3 minutes)
docker-compose logs -f

# Pull LLM model
docker-compose exec ollama ollama pull mistral
docker-compose exec ollama ollama pull nomic-embed-text
```

### 3. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant**: http://localhost:6333

### 4. Upload Documents & Ask Questions

1. Go to http://localhost:5173
2. Upload markdown, text, or PDF files
3. Ask questions about your documents
4. Get answers with citations!

## 📁 Project Structure

```
AskMyDocs/
├── backend/
│   ├── app/
│   │   ├── rag/
│   │   │   ├── retriever.py          # Hybrid BM25 + Vector search
│   │   │   ├── reranker.py           # Cross-encoder reranking
│   │   │   ├── rag_chain.py          # End-to-end RAG pipeline
│   │   │   └── document_processor.py # Document ingestion
│   │   ├── evaluation/
│   │   │   └── evaluator.py          # RAGAS evaluation
│   │   ├── api/
│   │   │   └── models.py             # Request/response schemas
│   │   ├── config.py                 # Configuration
│   │   └── main.py                   # FastAPI app
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment template
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api.ts                    # API client
│   │   ├── App.tsx                   # Main component
│   │   ├── FileUpload.tsx            # Upload component
│   │   ├── QueryInput.tsx            # Query component
│   │   ├── Answer.tsx                # Answer display
│   │   └── components.tsx            # Reusable components
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml                # Service orchestration
└── docs/                             # Documentation
```

## 🏗️ Architecture

### RAG Pipeline

```
User Query
    ↓
[Hybrid Retrieval]
  ├─ BM25 (lexical)       50% weight
  └─ Vector Search        50% weight
    ↓
[Reranking]
  └─ Cross-Encoder        Top-3
    ↓
[Context Formation]
    ↓
[LLM Generation]
  └─ Ollama (Mistral)
    ↓
[Citation Extraction]
    ↓
Answer with Citations
```

### Services

| Service | Technology | Purpose |
|---------|-----------|---------|
| **Frontend** | React 18 + TypeScript + Vite | Web interface |
| **Backend** | FastAPI + LangChain | API & RAG logic |
| **Vector DB** | Qdrant | Semantic search |
| **LLM** | Ollama + Mistral | Answer generation |
| **Full-text** | BM25 (rank-bm25) | Keyword search |
| **Reranker** | ms-marco cross-encoder | Ranking |

## 🔧 Configuration

Edit `backend/.env`:

```env
# LLM
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL=mistral
EMBEDDING_MODEL=nomic-embed-text

# Retrieval
RETRIEVAL_K=5
RERANK_TOP_K=3
BM25_WEIGHT=0.5
VECTOR_WEIGHT=0.5

# Chunk Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 📚 Supported Document Types

- 📄 Markdown (.md)
- 📝 Plain text (.txt)
- 📕 PDF (.pdf)

## 💻 API Endpoints

### Query Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "k": 5, "top_k": 3}'
```

### Upload Document
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.md"
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🧪 Evaluation & Testing

```python
from app.evaluation.evaluator import RAGEvaluator, EvalPipeline

evaluator = RAGEvaluator()
pipeline = EvalPipeline(evaluator)

# Run evaluation
results = await pipeline.run_evaluation([
    {
        "query": "What is RAG?",
        "ground_truth": "Retrieval-Augmented Generation...",
        "answer": "Generated answer...",
        "context": "Retrieved context..."
    }
])

print(results["summary"]["overall_score"])
```

## 🚀 Production Deployment

### Deploy to AWS
```bash
# 1. Build Docker images
docker build -t askmydocs-backend backend/
docker build -t askmydocs-frontend frontend/

# 2. Push to ECR
aws ecr create-repository --repository-name askmydocs
docker tag askmydocs-backend:latest YOUR_ECR_URI/askmydocs-backend:latest
docker push YOUR_ECR_URI/askmydocs-backend:latest

# 3. Deploy with ECS/Fargate or EKS
```

### Environment Variables (Production)

```env
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Use managed services
OLLAMA_BASE_URL=https://your-llm-endpoint.com
QDRANT_URL=https://your-qdrant-cloud.com
QDRANT_API_KEY=your-secure-key

CORS_ORIGINS=https://yourdomain.com
```

## 📊 Key Features

1. **Hybrid Retrieval**
   - BM25 for keyword matching
   - Vector similarity for semantic search
   - Weighted combination (configurable)

2. **Reranking**
   - Cross-Encoder model (ms-marco)
   - Improves top-k precision
   - Reduces hallucinations

3. **Citation System**
   - Every answer cites sources
   - [1], [2] formatted citations
   - Source metadata tracking

4. **Evaluation Framework**
   - Faithfulness scoring
   - Answer relevance
   - Context precision
   - CI/CD pipeline ready

5. **Modern Frontend**
   - Real-time query processing
   - File upload support
   - Citation display
   - Confidence scores

## 🔄 Development Workflow

```bash
# Start development
docker-compose up -d

# Watch logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Backend development
cd backend
python -m uvicorn app.main:app --reload

# Frontend development
cd frontend
npm run dev

# Stop services
docker-compose down

# Clean everything
docker-compose down -v
```

## 🐛 Troubleshooting

### Backend connection error
```bash
docker-compose logs qdrant
docker-compose logs ollama
```

### Ollama model not loading
```bash
docker-compose exec ollama ollama list
docker-compose exec ollama ollama pull mistral
```

### Frontend can't reach backend
Check CORS settings in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173
```

### Out of memory
Increase Docker memory allocation in Docker Desktop settings.

## 📚 Documentation & Resources

- [LangChain RAG Tutorial](https://docs.langchain.com/oss/python/langchain/rag)
- [Cohere Rerank Guide](https://docs.cohere.com/docs/rerank-guide)
- [RAGAS Evaluation](https://docs.ragas.io/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Ollama Docs](https://github.com/ollama/ollama)

## 🎯 Next Steps

1. ✅ Local development running
2. 📄 Upload your documents
3. 🧪 Test the RAG system
4. 📊 Run evaluation pipeline
5. 🚀 Deploy to production
6. 📈 Monitor & optimize

## 📝 License

MIT License - feel free to use and modify!

---

**Built with ❤️ using FastAPI, React, LangChain, and Qdrant**
