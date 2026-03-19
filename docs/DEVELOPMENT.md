# AskMyDocs - Developer Guide

## 🛠️ Development Setup

### Backend Development

#### Local Python Environment
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start Qdrant (Docker only)
docker run -d -p 6333:6333 qdrant/qdrant

# Start Ollama (Docker only)
docker run -d -p 11434:11434 ollama/ollama
docker exec -it <container_id> ollama pull mistral

# Run backend
python -m uvicorn app.main:app --reload --port 8000
```

#### API Documentation
- OpenAPI Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Install Tailwind CSS (if not already done)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

#### File Structure
```
src/
├── App.tsx              # Main component
├── api.ts              # API client
├── main.tsx            # Entry point
├── index.css           # Tailwind styles
├── components.tsx      # Reusable UI components
├── FileUpload.tsx      # Upload handler
├── QueryInput.tsx      # Query form
└── Answer.tsx          # Answer display
```

## 🧪 Testing RAG Pipeline

### 1. Test Retriever

```python
from app.rag.retriever import HybridRetriever, Document

retriever = HybridRetriever(
    qdrant_url="http://localhost:6333",
    embedding_model="nomic-embed-text"
)

# Add test documents
docs = [
    Document(
        id="doc1",
        content="RAG improves LLM accuracy by using retrieved documents.",
        metadata={"source": "test.md"}
    ),
    Document(
        id="doc2",
        content="Hybrid search combines BM25 and vector search.",
        metadata={"source": "test.md"}
    ),
]

retriever.add_documents(docs)

# Test retrieval
results = retriever.retrieve("What is RAG?", k=2)
for doc, score in results:
    print(f"{doc.id}: {score:.2f}")
```

### 2. Test Reranker

```python
from app.rag.reranker import CrossEncoderReranker

reranker = CrossEncoderReranker()

documents = [
    {"content": "RAG is a technique...", "metadata": {}},
    {"content": "BM25 is a ranking algorithm...", "metadata": {}},
]

reranked = reranker.rerank("What is RAG?", documents, top_k=1)
```

### 3. Test RAG Chain

```python
from app.rag.rag_chain import RAGChain

rag_response = await rag_chain.generate("What is RAG?")
print(rag_response.answer)
print(rag_response.citations)
```

## 📊 Evaluation Scripts

### Run Full Evaluation

```python
import asyncio
from app.evaluation.evaluator import RAGEvaluator, EvalPipeline
import json

async def run_eval():
    # Load test cases
    with open("docs/eval_sample.json") as f:
        cases = json.load(f)
    
    # Run evaluation
    evaluator = RAGEvaluator()
    pipeline = EvalPipeline(evaluator)
    
    results = await pipeline.run_evaluation(cases)
    
    print("Evaluation Results:")
    print(f"Overall Score: {results['summary']['overall_score']:.2f}")
    print(f"Faithfulness: {results['summary']['avg_faithfulness']:.2f}")
    print(f"Relevance: {results['summary']['avg_answer_relevance']:.2f}")

asyncio.run(run_eval())
```

## 🔍 Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Backend Logs

```bash
# Docker
docker-compose logs -f backend

# Local
# Set DEBUG=true in .env

# Or in Python
from app.config import get_settings
settings = get_settings()
print(settings.debug)
```

### Frontend Debugging

```bash
# Browser console
Open DevTools -> Console tab

# Log API calls
Check Network tab for requests to http://localhost:8000

# React DevTools
Install React DevTools browser extension
```

### Common Issues

#### 1. Connection Refused to Qdrant
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# If not, start it
docker run -d -p 6333:6333 qdrant/qdrant
```

#### 2. Ollama Model Not Found
```bash
# List available models
docker-compose exec ollama ollama list

# Pull model
docker-compose exec ollama ollama pull mistral

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hello"
}'
```

#### 3. CORS Errors in Frontend
Check `backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173
```

Make sure frontend URL matches exactly.

#### 4. File Upload Fails
Ensure upload directory exists:
```bash
mkdir -p backend/uploads
chmod 755 backend/uploads
```

## 🚀 Performance Optimization

### Backend Optimization

1. **Increase Ollama Workers**
   ```env
   OLLAMA_NUM_PARALLEL=4
   ```

2. **Batch Processing**
   ```python
   # Process multiple queries together
   queries = ["Q1", "Q2", "Q3"]
   results = await asyncio.gather(*[
       rag_chain.generate(q) for q in queries
   ])
   ```

3. **Caching**
   - Cache embeddings for repeated documents
   - Cache reranker scores

### Frontend Optimization

1. **Lazy Loading**
   - Load components on demand
   - Implement pagination for results

2. **Debouncing**
   - Debounce query input to reduce API calls

## 📦 Adding New Features

### Add Custom Retriever

```python
# backend/app/rag/custom_retriever.py
from .retriever import BaseRetriever

class CustomRetriever(BaseRetriever):
    def add_documents(self, documents):
        # Your implementation
        pass
    
    def retrieve(self, query, k):
        # Your implementation
        pass
```

### Add New API Endpoint

```python
# backend/app/main.py
@app.post("/custom-endpoint")
async def custom_endpoint(request: CustomRequest):
    # Your logic
    return custom_response
```

### Add Frontend Component

```typescript
// frontend/src/CustomComponent.tsx
import { FC } from 'react'
import { Card } from './components'

export const CustomComponent: FC = () => {
  return (
    <Card>
      {/* Your component */}
    </Card>
  )
}
```

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints
- Docstrings for functions

```python
def my_function(query: str, k: int = 5) -> List[Document]:
    """Retrieve documents for query.
    
    Args:
        query: User query string
        k: Number of documents to retrieve
    
    Returns:
        List of relevant documents
    """
    pass
```

### TypeScript/React
- Use functional components
- Props with TypeScript interfaces
- Descriptive variable names

```typescript
interface Props {
  onSubmit: (query: string) => Promise<void>
  disabled?: boolean
}

export const Component: FC<Props> = ({ onSubmit, disabled }) => {
  return <div>{/* Component */}</div>
}
```

## 🔗 Useful Commands

```bash
# Backend
cd backend
python -m pytest                      # Run tests (when added)
python -m black .                     # Format code
python -m pylint app/                 # Lint code

# Frontend
cd frontend
npm run lint                          # Run ESLint
npm run build                         # Production build

# Docker
docker-compose up -d                  # Start services
docker-compose down                   # Stop services
docker-compose logs -f                # View logs
docker-compose exec backend bash      # Shell into container
```

## 📚 Additional Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [LangChain Docs](https://docs.langchain.com/)
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Qdrant HTTP API](https://qdrant.tech/documentation/concepts/api/)
