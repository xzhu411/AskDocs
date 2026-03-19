# Getting Started - Your AskMyDocs Platform is Ready! 🎉

## What Has Been Built

Your complete **Production RAG (Retrieval-Augmented Generation) Application** with:

### Backend (Python + FastAPI)
- ✅ Hybrid retrieval (BM25 + vector search)
- ✅ Cross-encoder reranking
- ✅ Citation enforcement
- ✅ Document processing (MD, TXT, PDF)
- ✅ Evaluation pipeline (RAGAS framework)
- ✅ REST API with FastAPI
- ✅ Async/await support

### Frontend (React + TypeScript)
- ✅ Modern UI with Tailwind CSS
- ✅ File upload component
- ✅ Query interface
- ✅ Citation display
- ✅ Confidence scoring
- ✅ Source document references
- ✅ Real-time feedback

### Infrastructure
- ✅ Docker Compose orchestration
- ✅ Qdrant vector database
- ✅ Ollama local LLM server
- ✅ Automated setup scripts
- ✅ Production deployment guide

---

## 🚀 Start Here (5 Minutes)

### Step 1: Make Scripts Executable
```bash
cd /Users/zhuxiaoai/Projects/AskMyDocs
chmod +x setup.sh stop.sh clean.sh check.sh
```

### Step 2: Start Everything
```bash
./setup.sh
```
This will:
- Create `.env` configuration
- Start all Docker services
- Pull AI models (2-3 minutes)
- Initialize databases

### Step 3: Open the App
Visit: **http://localhost:5173**

### Step 4: Create a Test Document
```bash
cat > /tmp/test.md << 'EOF'
# My First Test Document

## What is RAG?
RAG (Retrieval-Augmented Generation) is a technique that combines:
1. Document retrieval
2. Language model generation
3. Citation references

## Benefits
- Accurate and grounded answers
- Verifiable sources
- Domain-specific knowledge
- Reduced hallucinations
EOF
```

### Step 5: Upload & Ask Questions
1. Upload `/tmp/test.md` in the browser
2. Ask: "What is RAG?"
3. See the answer with citations!

---

## 📋 Project Structure

```
/Users/zhuxiaoai/Projects/AskMyDocs/
├── backend/
│   ├── app/
│   │   ├── main.py                 ← FastAPI app entry
│   │   ├── config.py               ← Configuration
│   │   ├── rag/
│   │   │   ├── retriever.py        ← Hybrid search
│   │   │   ├── reranker.py         ← Cross-encoder
│   │   │   ├── rag_chain.py        ← RAG pipeline
│   │   │   └── document_processor.py ← Doc ingestion
│   │   ├── api/models.py           ← API schemas
│   │   └── evaluation/evaluator.py ← Quality metrics
│   ├── requirements.txt            ← Python dependencies
│   ├── .env.example                ← Config template
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 ← Main React component
│   │   ├── api.ts                  ← API client
│   │   ├── FileUpload.tsx          ← Upload UI
│   │   ├── QueryInput.tsx          ← Search UI
│   │   ├── Answer.tsx              ← Results display
│   │   └── components.tsx          ← Reusable UI
│   ├── package.json                ← Dependencies
│   └── Dockerfile
├── docker-compose.yml              ← Service orchestration
├── setup.sh, stop.sh, clean.sh     ← Management scripts
├── README.md                        ← Full documentation
├── QUICKSTART.md                    ← 5-minute guide
└── docs/
    ├── ARCHITECTURE.md             ← System design
    ├── DEVELOPMENT.md              ← Dev guide
    ├── DEPLOYMENT.md               ← Production guide
    ├── SAMPLE_DOCUMENTS.md         ← Test data
    ├── eval_sample.json            ← Evaluation data
    └── README.md                   ← Docs index
```

---

## 🔗 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | User interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Documentation** | http://localhost:8000/docs | Swagger UI |
| **Vector Database** | http://localhost:6333 | Qdrant management |
| **LLM Server** | http://localhost:11434 | Ollama API |

---

## 🎯 Key Features Explained

### 1. Hybrid Search
Combines:
- **BM25**: Keyword/lexical matching (fast, precise)
- **Vector Search**: Semantic similarity (understands meaning)
- **Result**: Best of both worlds!

### 2. Reranking
- Cross-Encoder model re-scores results
- Improves precision significantly
- Reduces hallucinations

### 3. Citations
- Every answer references source documents
- [1], [2] format
- Users can verify information

### 4. Document Processing
- Automatic chunking (1000 tokens)
- Overlap handling (200 tokens)
- Supports: Markdown, Text, PDF

---

## 🛠️ Common Commands

```bash
# Start services
./setup.sh

# Stop services (keep data)
./stop.sh

# Clean everything (reset)
./clean.sh

# Check status
./check.sh

# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend

# Shell into backend
docker-compose exec backend bash

# Shell into ollama
docker-compose exec ollama ollama list
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete feature documentation |
| `QUICKSTART.md` | 5-minute getting started (you are here) |
| `docs/ARCHITECTURE.md` | System design & data flow |
| `docs/DEVELOPMENT.md` | Development setup & testing |
| `docs/DEPLOYMENT.md` | Production deployment guide |

---

## 🔧 Configuration

Edit `backend/.env` to customize:

```env
# LLM Settings
LLM_MODEL=mistral                           # or llama2
EMBEDDING_MODEL=nomic-embed-text

# Retrieval Tuning
RETRIEVAL_K=5                               # Docs to retrieve
RERANK_TOP_K=3                              # Final docs
BM25_WEIGHT=0.5                             # Keyword weight
VECTOR_WEIGHT=0.5                           # Semantic weight

# Processing
CHUNK_SIZE=1000                             # Tokens per chunk
CHUNK_OVERLAP=200                           # Overlap tokens

# API
CORS_ORIGINS=http://localhost:5173
API_PORT=8000
```

---

## 🧪 Testing the RAG System

### Test 1: Upload a Document
```bash
# Create a test document
echo "# Test\nThis is a test document." > /tmp/test.txt

# Upload via UI or API
curl -X POST http://localhost:8000/upload \
  -F "file=@/tmp/test.txt"
```

### Test 2: Query the System
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is in the document?", "k": 5}'
```

### Test 3: Evaluate Quality
See `docs/DEVELOPMENT.md` for running evaluation metrics

---

## 🚀 Next Steps

### Immediate (After setup)
1. ✅ Run `./setup.sh`
2. ✅ Upload a document
3. ✅ Ask questions
4. ✅ Review citations

### Short-term (Next hours)
- [ ] Upload multiple documents to build knowledge base
- [ ] Experiment with different questions
- [ ] Adjust RAG parameters in .env
- [ ] Test with your own documents

### Medium-term (Next days)
- [ ] Read `docs/DEVELOPMENT.md` for deeper understanding
- [ ] Run evaluation pipeline
- [ ] Customize rerank models
- [ ] Add more document types (integrate PyPDF2)

### Long-term (Production)
- [ ] Review `docs/DEPLOYMENT.md`
- [ ] Set up monitoring & logging
- [ ] Configure authentication
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Set up CI/CD pipeline

---

## 🆘 Troubleshooting

### Services won't start
```bash
# Check if ports are in use
lsof -i :8000 -i :5173 -i :6333 -i :11434

# Stop conflicting services and try again
./stop.sh && ./setup.sh
```

### Ollama models won't download
```bash
# Check available disk space
df -h

# Manually pull model
docker-compose exec ollama ollama pull mistral
```

### Frontend blank page
```bash
# Clear cache
# Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

# Check console for errors
# Open DevTools: F12 -> Console tab
```

### Backend connection error
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend
```

---

## 📊 Understanding the Response

When you submit a query, you get:

```json
{
  "answer": "Your generated answer here...",
  "citations": [
    {
      "index": 1,
      "source": "document_name.md",
      "snippet": "Excerpt from source..."
    }
  ],
  "documents": [
    {
      "id": "doc_id",
      "content": "First 500 chars of document",
      "metadata": {"source": "file.md"}
    }
  ],
  "confidence": 0.85,   # 0-1, higher is better
  "processing_time": 2.34  # seconds
}
```

**Confidence Score Meaning:**
- **0.9+** : Very confident, well-grounded answer
- **0.7-0.9** : Good confidence, reliable answer
- **0.5-0.7** : Moderate confidence, check citations
- **<0.5** : Low confidence, may need more docs

---

## 💡 Tips & Tricks

1. **Ask specific questions**: "What is RAG?" works better than "Tell me about things"
2. **Use multiple documents**: Upload vary your knowledge base
3. **Check citations**: Click on [1], [2] to verify sources
4. **Adjust parameters**: Experiment with RETRIEVAL_K and RERANK_TOP_K
5. **Monitor response time**: Aim for <3 seconds per query

---

## 🎓 Learn More

- **LangChain**: https://docs.langchain.com/oss/python/langchain/rag
- **Qdrant**: https://qdrant.tech/documentation/
- **Ollama**: https://github.com/ollama/ollama
- **FastAPI**: https://fastapi.tiangolo.com/

---

## 🎉 You're All Set!

Your production RAG application is ready. Now:

```bash
cd /Users/zhuxiaoai/Projects/AskMyDocs
chmod +x setup.sh
./setup.sh
# Then open http://localhost:5173
```

**Happy building! 🚀**

---

**Questions?** Check:
- `README.md` for full documentation
- `docs/DEVELOPMENT.md` for technical details
- `docs/ARCHITECTURE.md` for system design
