"""Cross-Encoder Reranking"""
from typing import List, Tuple
from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Rerank documents using cross-encoder"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
        logger.info(f"Loaded cross-encoder model: {model_name}")
    
    def rerank(
        self, 
        query: str, 
        documents: List[dict],
        top_k: int = 3
    ) -> List[Tuple[dict, float]]:
        """
        Rerank documents using cross-encoder
        
        Args:
            query: User query
            documents: List of document dicts with 'content' and 'metadata' keys
            top_k: Number of documents to return
        
        Returns:
            List of (document, score) tuples sorted by relevance score
        """
        
        if not documents:
            return []
        
        # Prepare pairs for cross-encoder
        pairs = [(query, doc.get("content", "")) for doc in documents]
        
        # Get scores
        scores = self.model.predict(pairs)
        
        # Combine documents with scores
        scored_docs = list(zip(documents, scores))
        
        # Sort by score descending and return top_k
        reranked = sorted(scored_docs, key=lambda x: x[1], reverse=True)[:top_k]
        
        logger.info(f"Reranked {len(documents)} documents, returned top {len(reranked)}")
        
        return reranked
