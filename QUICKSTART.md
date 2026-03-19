# AskMyDocs - Quick Start Guide (5 minutes)

## 🎯 Goal
Get your RAG application running locally with sample documents.

## ⚡ Prerequisites
- Docker Desktop (https://www.docker.com/products/docker-desktop)
- Running macOS/Linux/Windows with bash

## 🚀 Start in 5 Steps

### Step 1: Clone and Navigate
```bash
cd /Users/zhuxiaoai/Projects/AskMyDocs
```

### Step 2: Make Scripts Executable
```bash
chmod +x setup.sh stop.sh clean.sh
```

### Step 3: Run Setup
```bash
./setup.sh
```
This will:
- ✅ Create `.env` file
- ✅ Start all services (takes 2-3 minutes)
- ✅ Pull AI models

### Step 4: Create Sample Document
```bash
cat > /tmp/sample.md << 'EOF'
# What is RAG?

RAG (Retrieval-Augmented Generation) combines document retrieval with language models.

## Key Benefits
- Reduced hallucinations
- Current information
- Verifiable citations
- Domain-specific knowledge

## How It Works
1. Retrieve relevant documents
2. Pass to LLM with documents
3. LLM generates grounded answer
4. Citations provided
EOF
```

### Step 5: Access the App
1. Open browser: **http://localhost:5173**
2. Upload `/tmp/sample.md`
3. Ask: "What is RAG?"
4. Get answer with citations! ✨

## 📍 Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Vector DB | http://localhost:6333 |

## 🛑 Stop Services
```bash
./stop.sh
```

## 🧹 Reset Everything
```bash
./clean.sh
docker-compose up -d  # Restart
```

## 📊 Check Status
```bash
docker-compose ps
docker-compose logs backend
```

## ✅ What's Working Now

- ✅ React frontend with modern UI
- ✅ FastAPI backend with RAG pipeline
- ✅ Hybrid search (BM25 + Vector)
- ✅ Cross-encoder reranking
- ✅ Citation enforcement
- ✅ Document upload (.md, .txt, .pdf)
- ✅ Local LLM (Mistral via Ollama)
- ✅ Qdrant vector database

## 🎓 Next Steps

1. **Upload more documents**
   - Create markdown files with your content
   - Try different question types

2. **Customize RAG settings** (`backend/.env`)
   - Change `RETRIEVAL_K` (number of documents)
   - Adjust `BM25_WEIGHT` vs `VECTOR_WEIGHT`

3. **Run evaluation**
   - See `docs/DEVELOPMENT.md` for evaluation scripts

4. **Deploy to cloud**
   - See `README.md` for deployment guide

## 🆘 Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
# Check for missing dependencies or port conflicts
```

### Frontend blank page
```
# Clear browser cache or open in incognito mode
```

### Ollama pulling models slowly
```bash
# Models are being downloaded (1-2GB each)
docker-compose logs ollama
```

### Out of disk space
```bash
docker system prune -a  # Clean unused images
```

## 💡 Pro Tips

- 🎯 Ask specific questions for better answers
- 📝 Use markdown for organized documents  
- 🔄 Upload multiple files to build knowledge base
- ⚡ Check confidence score for answer quality
- 🔗 Click citations to verify sources

---

**That's it! You now have a production RAG system running locally. Enjoy! 🎉**
