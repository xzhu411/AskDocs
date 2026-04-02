"""Main FastAPI application"""
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import logging
import time
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from app.config import get_settings, Settings
from app.api.models import QueryRequest, RAGResponse, HealthResponse, Citation, Document as DocumentModel, UploadResponse, UploadedFileInfo
from app.rag.retriever import HybridRetriever, Document
from app.rag.reranker import CrossEncoderReranker
from app.rag.rag_chain import RAGChain
from app.rag.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
retriever: Optional[HybridRetriever] = None
reranker: Optional[CrossEncoderReranker] = None
rag_chain: Optional[RAGChain] = None
doc_processor: Optional[DocumentProcessor] = None
llm_client: Optional[object] = None


class ClaudeClient:
    """Anthropic Claude client using native async for fast, reliable LLM inference"""

    def __init__(self, api_key: str, model: str):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Claude client: model={model}")

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except asyncio.CancelledError:
            logger.info("Claude generation cancelled")
            raise
        except Exception as e:
            logger.error(f"Claude client error: {repr(e)}")
            return "I apologize, but I encountered an error generating a response."


class OllamaClient:
    """Ollama client for local LLM inference"""
    
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 180, num_predict: int = 256):
        self.base_url = base_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.num_predict = num_predict
        logger.info(
            f"Initialized Ollama client: {base_url}, model: {model}, timeout={timeout_seconds}s, num_predict={num_predict}"
        )
    
    async def generate(self, prompt: str) -> str:
        """Generate response using Ollama"""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": self.num_predict
                        }
                    },
                    timeout=httpx.Timeout(self.timeout_seconds, connect=10.0)
                )
                
                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    logger.error(f"Ollama error: {response.status_code}, body={response.text[:500]}")
                    return "I apologize, but I encountered an error generating a response."
        except asyncio.CancelledError:
            logger.info("Ollama generation cancelled")
            raise
        except Exception as e:
            logger.error(f"Ollama client error: {repr(e)}")
            return "I apologize, but I'm unable to process your question at the moment."


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global retriever, reranker, rag_chain, doc_processor, llm_client
    
    logger.info("Starting AskMyDocs application...")
    
    settings = get_settings()
    
    try:
        # Initialize components
        logger.info("Initializing RAG components...")
        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
        
        doc_processor = DocumentProcessor(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        retriever = HybridRetriever(
            qdrant_url=settings.qdrant_url,
            embedding_model=settings.embedding_model,
            bm25_weight=settings.bm25_weight,
            vector_weight=settings.vector_weight
        )
        
        reranker = CrossEncoderReranker()
        
        if settings.llm_provider == "claude" and settings.anthropic_api_key:
            llm_client = ClaudeClient(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
            )
        else:
            logger.warning("Claude API key not set, falling back to Ollama")
            llm_client = OllamaClient(
                base_url=settings.ollama_base_url,
                model=settings.llm_model,
                timeout_seconds=settings.ollama_timeout_seconds,
                num_predict=settings.ollama_num_predict,
            )
        
        rag_chain = RAGChain(
            retriever=retriever,
            reranker=reranker,
            llm_client=llm_client,
            retrieval_k=settings.retrieval_k,
            rerank_top_k=settings.rerank_top_k
        )

        existing_documents = doc_processor.load_directory(settings.upload_dir)
        if existing_documents:
            retriever.replace_documents(existing_documents)
            logger.info("Loaded %s chunks from existing uploaded files", len(existing_documents))
        else:
            retriever.clear_documents()
        
        logger.info("RAG components initialized successfully")
    
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise
    
    yield
    
    logger.info("Shutting down AskMyDocs application...")


# Create FastAPI app
app = FastAPI(
    title="AskMyDocs API",
    description="Production RAG Application with Hybrid Retrieval",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        message="AskMyDocs is running"
    )



def _load_documents_for_file(processor: DocumentProcessor, file_path: Path) -> list[Document]:
    """Load a supported file into chunked documents."""
    suffix = file_path.suffix.lower()
    if suffix == ".md":
        return processor.load_markdown_file(str(file_path))
    if suffix == ".txt":
        return processor.load_txt_file(str(file_path))
    if suffix == ".pdf":
        return processor.load_pdf_file(str(file_path))
    raise HTTPException(status_code=400, detail="Unsupported file type. Supported types: .md, .txt, .pdf")


def _reindex_uploaded_documents() -> int:
    """Rebuild the retriever index from the persisted upload directory."""
    if not (retriever and doc_processor):
        raise HTTPException(status_code=503, detail="Upload system not initialized")

    settings = get_settings()
    all_documents = doc_processor.load_directory(settings.upload_dir)
    if all_documents:
        retriever.replace_documents(all_documents)
    else:
        retriever.clear_documents()
    logger.info("Reindexed %s chunks from upload directory", len(all_documents))
    return len(all_documents)


@app.post("/query", response_model=RAGResponse)
async def query_documents(request: QueryRequest, http_request: Request):
    """Query the document database with RAG"""

    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        start_time = time.time()
        logger.info(f"Query received: {request.query[:80]}")
        rag_response = await rag_chain.generate(request.query)
        processing_time = time.time() - start_time
        logger.info(f"Query completed in {processing_time:.2f}s")

        citations = [
            Citation(
                index=c["index"],
                source=c["source"],
                snippet=c.get("content", "")[:100],
            )
            for c in rag_response.citations
        ]

        documents = [
            DocumentModel(
                id=doc.id,
                content=doc.content[:500],
                metadata={
                    "source": doc.metadata.get("source", "Unknown") if isinstance(doc.metadata, dict) else "Unknown",
                    "file_type": doc.metadata.get("file_type", "unknown") if isinstance(doc.metadata, dict) else "unknown",
                },
                score=0.0,
            )
            for doc in rag_response.documents
        ]

        return RAGResponse(
            query=request.query,
            answer=rag_response.answer,
            citations=citations,
            documents=documents,
            confidence=rag_response.confidence,
            grounded=rag_response.grounded,
            evidence_note=rag_response.evidence_note,
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query ({type(e).__name__}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(file: UploadFile = File(...)):
    """Upload and process documents"""
    
    if not (retriever and doc_processor):
        raise HTTPException(status_code=503, detail="Upload system not initialized")
    
    try:
        # Read file
        content = await file.read()
        
        settings = get_settings()
        filename = Path(file.filename or "upload").name
        suffix = Path(filename).suffix.lower()
        saved_path = Path(settings.upload_dir) / filename
        saved_path.write_bytes(content)

        if suffix not in {".md", ".txt", ".pdf"}:
            saved_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Unsupported file type. Supported types: .md, .txt, .pdf")

        documents = _load_documents_for_file(doc_processor, saved_path)
        total_chunks = _reindex_uploaded_documents()
        
        return UploadResponse(
            message="Documents processed successfully",
            documents_processed=len(set(doc.id.split('_chunk_')[0] for doc in documents)),
            total_chunks=total_chunks
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files", response_model=list[UploadedFileInfo])
async def list_uploaded_files():
    """List uploaded files available in the browser."""
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for file_path in sorted(upload_dir.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True):
        if not file_path.is_file():
            continue
        files.append(
            UploadedFileInfo(
                name=file_path.name,
                size=file_path.stat().st_size,
                file_type=file_path.suffix.lower().lstrip(".") or "file",
                uploaded_at=datetime.fromtimestamp(file_path.stat().st_mtime),
            )
        )
    return files


@app.get("/files/{filename:path}")
async def get_uploaded_file(filename: str):
    """Serve an uploaded file for in-browser viewing."""
    settings = get_settings()
    upload_dir = Path(settings.upload_dir).resolve()
    requested_path = (upload_dir / Path(filename).name).resolve()

    if requested_path.parent != upload_dir:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=requested_path, filename=requested_path.name)


@app.delete("/files/{filename:path}")
async def delete_uploaded_file(filename: str):
    """Delete one uploaded file and rebuild the retriever index."""
    settings = get_settings()
    upload_dir = Path(settings.upload_dir).resolve()
    requested_path = (upload_dir / Path(filename).name).resolve()

    if requested_path.parent != upload_dir:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    requested_path.unlink()
    remaining_chunks = _reindex_uploaded_documents()
    remaining_files = sum(1 for file_path in upload_dir.iterdir() if file_path.is_file())

    return JSONResponse(
        {
            "message": f"Deleted {requested_path.name}",
            "remaining_files": remaining_files,
            "remaining_chunks": remaining_chunks,
        }
    )


@app.delete("/files")
async def clear_uploaded_files():
    """Delete all uploaded files and clear the retriever index."""
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    deleted_files = 0
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            file_path.unlink()
            deleted_files += 1

    remaining_chunks = _reindex_uploaded_documents()
    return JSONResponse(
        {
            "message": "Cleared uploaded files",
            "deleted_files": deleted_files,
            "remaining_chunks": remaining_chunks,
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AskMyDocs API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
