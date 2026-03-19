"""Document processing and ingestion"""
import re
from typing import List
import logging
import os
from pathlib import Path
from .retriever import Document

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk documents"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_text(self, text: str, metadata: dict = None) -> List[Document]:
        """Split text into chunks"""
        if metadata is None:
            metadata = {}
        
        chunks = self._chunk_text(self._normalize_text(text))
        documents = [
            Document(
                id=f"{metadata.get('source', 'unknown')}_chunk_{i}",
                content=chunk,
                metadata=metadata
            )
            for i, chunk in enumerate(chunks)
        ]
        
        logger.info(f"Created {len(documents)} chunks from text")
        return documents

    def _normalize_text(self, text: str) -> str:
        """Normalize extracted text while preserving paragraph structure."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into paragraph-aware overlapping chunks."""
        if not text:
            return []

        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        if not paragraphs:
            paragraphs = [text]

        chunks: List[str] = []
        current_parts: List[str] = []
        current_words = 0

        for paragraph in paragraphs:
            paragraph_words = len(paragraph.split())

            if paragraph_words >= self.chunk_size:
                if current_parts:
                    chunks.append("\n\n".join(current_parts).strip())
                    current_parts = []
                    current_words = 0

                words = paragraph.split()
                step = max(1, self.chunk_size - self.chunk_overlap)
                for i in range(0, len(words), step):
                    chunk = " ".join(words[i:i + self.chunk_size]).strip()
                    if chunk:
                        chunks.append(chunk)
                continue

            if current_words and current_words + paragraph_words > self.chunk_size:
                chunks.append("\n\n".join(current_parts).strip())

                overlap_parts: List[str] = []
                overlap_words = 0
                for part in reversed(current_parts):
                    overlap_parts.insert(0, part)
                    overlap_words += len(part.split())
                    if overlap_words >= self.chunk_overlap:
                        break

                current_parts = overlap_parts
                current_words = overlap_words

            current_parts.append(paragraph)
            current_words += paragraph_words

        if current_parts:
            chunks.append("\n\n".join(current_parts).strip())

        return chunks
    
    def load_markdown_file(self, file_path: str) -> List[Document]:
        """Load and process markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract filename as source
        filename = os.path.basename(file_path)
        metadata = {"source": filename, "file_type": "markdown"}
        
        return self.process_text(content, metadata)
    
    def load_txt_file(self, file_path: str) -> List[Document]:
        """Load and process text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(file_path)
        metadata = {"source": filename, "file_type": "text"}
        
        return self.process_text(content, metadata)
    
    def load_pdf_file(self, file_path: str) -> List[Document]:
        """Load and process PDF file (requires PyPDF2)"""
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return []
        
        pdf_reader = PdfReader(file_path)
        all_text_parts = []
        
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                all_text_parts.append(page_text)
        
        filename = os.path.basename(file_path)
        metadata = {"source": filename, "file_type": "pdf"}
        
        return self.process_text("\n\n".join(all_text_parts), metadata)
    
    def load_directory(self, directory: str) -> List[Document]:
        """Load all supported files from directory"""
        all_documents = []
        
        for file_path in Path(directory).rglob("*"):
            if file_path.is_file():
                try:
                    if file_path.suffix.lower() == ".md":
                        docs = self.load_markdown_file(str(file_path))
                    elif file_path.suffix.lower() == ".txt":
                        docs = self.load_txt_file(str(file_path))
                    elif file_path.suffix.lower() == ".pdf":
                        docs = self.load_pdf_file(str(file_path))
                    else:
                        continue
                    
                    all_documents.extend(docs)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Loaded {len(all_documents)} documents from directory")
        return all_documents
