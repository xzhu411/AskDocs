"""API Models"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Document metadata"""
    source: str
    file_type: str
    created_at: Optional[datetime] = None


class Document(BaseModel):
    """Document representation"""
    id: str
    content: str
    metadata: DocumentMetadata
    score: float = 0.0


class QueryRequest(BaseModel):
    """Query request from frontend"""
    query: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)
    top_k: int = Field(default=3, ge=1, le=10)


class Citation(BaseModel):
    """Citation in the answer"""
    index: int
    source: str
    snippet: str = ""


class RAGResponse(BaseModel):
    """RAG response to frontend"""
    query: str
    answer: str
    citations: List[Citation]
    documents: List[Document]
    confidence: float
    grounded: bool = True
    evidence_note: str = ""
    processing_time: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    message: str = ""


class UploadResponse(BaseModel):
    """Document upload response"""
    message: str
    documents_processed: int
    total_chunks: int


class FileUploadRequest(BaseModel):
    """File upload request"""
    filename: str
    content: str


class UploadedFileInfo(BaseModel):
    """Uploaded file metadata for the frontend file browser"""
    name: str
    size: int
    file_type: str
    uploaded_at: datetime
