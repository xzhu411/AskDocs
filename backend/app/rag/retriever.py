"""Hybrid Retriever with BM25 + Vector Search"""
from typing import List, Tuple
from abc import ABC, abstractmethod
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
from dataclasses import dataclass
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document representation"""
    id: str
    content: str
    metadata: dict
    embedding: List[float] = None
    score: float = 0.0


class BaseRetriever(ABC):
    """Abstract base class for retrievers"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to retriever"""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve documents for query"""
        pass


class BM25Retriever(BaseRetriever):
    """BM25 Full-text search retriever"""
    
    def __init__(self):
        self.documents: List[Document] = []
        self.bm25 = None
        self.corpus = []
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to BM25 index"""
        self.documents = documents
        self.corpus = [doc.content.split() for doc in documents]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None
        logger.info(f"BM25 index created with {len(documents)} documents")

    def clear(self) -> None:
        """Clear BM25 index."""
        self.documents = []
        self.corpus = []
        self.bm25 = None
    
    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve top-k documents using BM25"""
        if not self.bm25:
            return []
        
        query_tokens = query.split()
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = [
            (self.documents[idx], float(scores[idx]))
            for idx in top_indices
            if scores[idx] > 0
        ]
        
        return results


class VectorRetriever(BaseRetriever):
    """Vector similarity search retriever using Qdrant"""
    
    def __init__(self, qdrant_url: str, embedding_model: str, collection_name: str = "documents"):
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(embedding_model)
        self.documents: List[Document] = []
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize collection if exists
        try:
            self.client.get_collection(collection_name)
        except:
            self._create_collection()
        
        logger.info(f"Vector retriever initialized with model: {embedding_model}")
    
    def _create_collection(self) -> None:
        """Create Qdrant collection"""
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created Qdrant collection: {self.collection_name}")

    def reset_collection(self) -> None:
        """Reset the Qdrant collection contents."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            logger.info("Qdrant collection did not exist during reset")
        self._create_collection()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to vector store"""
        self.documents = documents

        if not documents:
            self.reset_collection()
            logger.info("Vector store cleared")
            return
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(
            [doc.content for doc in documents],
            show_progress_bar=True
        )
        
        # Prepare points for Qdrant
        points = []
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding.tolist()
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding.tolist(),
                    payload={"doc_id": doc.id, "content": doc.content, "metadata": doc.metadata}
                )
            )
        
        self.reset_collection()

        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve top-k documents using vector similarity"""
        query_embedding = self.embedding_model.encode(query).tolist()

        # qdrant-client 1.17 uses query_points instead of search.
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=k,
                with_payload=True,
            )
            results = getattr(response, "points", response)
        else:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k
            )
        
        retrieved_docs = []
        for hit in results:
            doc_id = hit.payload["doc_id"]
            # Find original document
            doc = next((d for d in self.documents if d.id == doc_id), None)
            if doc is None:
                doc = Document(
                    id=doc_id,
                    content=hit.payload.get("content", ""),
                    metadata=hit.payload.get("metadata", {}),
                )
            if doc:
                retrieved_docs.append((doc, hit.score))
        
        return retrieved_docs


class HybridRetriever:
    """Hybrid Retriever combining BM25 and Vector Search"""
    
    def __init__(
        self, 
        qdrant_url: str, 
        embedding_model: str,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5
    ):
        self.bm25_retriever = BM25Retriever()
        self.vector_retriever = VectorRetriever(qdrant_url, embedding_model)
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to both retrievers"""
        self.bm25_retriever.add_documents(documents)
        self.vector_retriever.add_documents(documents)

    def replace_documents(self, documents: List[Document]) -> None:
        """Replace the entire in-memory and vector indexes."""
        self.add_documents(documents)

    def clear_documents(self) -> None:
        """Clear all indexed documents."""
        self.bm25_retriever.clear()
        self.vector_retriever.add_documents([])
    
    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Hybrid retrieval with weighted combination"""
        # Get results from both retrievers
        bm25_results = self.bm25_retriever.retrieve(query, k)
        vector_results = self.vector_retriever.retrieve(query, k)
        
        # Combine scores (normalize both to 0-1 range)
        all_docs = {}
        
        # Add BM25 scores
        if bm25_results:
            max_bm25_score = max(score for _, score in bm25_results) + 1e-6
            for doc, score in bm25_results:
                normalized_score = (score / max_bm25_score) * self.bm25_weight
                if doc.id not in all_docs:
                    all_docs[doc.id] = {"doc": doc, "score": 0}
                all_docs[doc.id]["score"] += normalized_score
        
        # Add vector scores
        if vector_results:
            for doc, score in vector_results:
                normalized_score = score * self.vector_weight
                if doc.id not in all_docs:
                    all_docs[doc.id] = {"doc": doc, "score": 0}
                all_docs[doc.id]["score"] += normalized_score
        
        # Sort by combined score and return top-k
        sorted_docs = sorted(all_docs.items(), key=lambda x: x[1]["score"], reverse=True)
        results = [(item[1]["doc"], item[1]["score"]) for item in sorted_docs[:k]]
        
        logger.info(f"Hybrid retrieval returned {len(results)} documents")
        return results
