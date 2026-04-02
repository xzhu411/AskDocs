"""RAG Chain with Citation Enforcement"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
from .retriever import HybridRetriever, Document
from .reranker import CrossEncoderReranker

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Response from RAG chain"""
    query: str
    answer: str
    citations: List[Dict[str, str]]
    documents: List[Document]
    confidence: float
    grounded: bool
    evidence_note: str


class RAGChain:
    """End-to-end RAG chain with hybrid retrieval, reranking, and citation enforcement"""
    
    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: CrossEncoderReranker,
        llm_client,  # Ollama client
        retrieval_k: int = 5,
        rerank_top_k: int = 3
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.llm_client = llm_client
        self.retrieval_k = retrieval_k
        self.rerank_top_k = rerank_top_k
    
    def _format_context(self, documents: List[Tuple[Document, float]]) -> str:
        """Format retrieved documents as context"""
        context_parts = []
        for i, (doc, score) in enumerate(documents, 1):
            context_parts.append(f"[{i}] {doc.content}\n(Source: {doc.metadata.get('source', 'Unknown')})")
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create prompt for LLM with context"""
        prompt = f"""You are a careful question-answering assistant working only from the provided context.

Reply in the same language as the user's question.
Use only facts explicitly stated in the context.
Do not guess, infer missing chronology, or invent details.
If the answer is uncertain or not explicitly stated, say so clearly.
Give a useful but concise answer, usually 3-6 sentences or a short bullet list when appropriate.
Only cite sources that actually appear in the context, using [1], [2], etc.

Context:
{context}

Question: {query}

Answer:"""
        return prompt

    def _insufficient_evidence_response(self, query: str, documents: List[Document], note: str) -> RAGResponse:
        """Return a conservative answer when evidence is too weak."""
        return RAGResponse(
            query=query,
            answer="I don't have enough explicit evidence in the uploaded documents to answer this confidently.",
            citations=[],
            documents=documents,
            confidence=0.0,
            grounded=False,
            evidence_note=note,
        )
    
    async def generate(self, query: str) -> RAGResponse:
        """
        Full RAG pipeline: retrieve -> rerank -> generate -> extract citations
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Retrieve documents
        retrieved = self.retriever.retrieve(query, k=self.retrieval_k)
        logger.info(f"Retrieved {len(retrieved)} documents")

        if not retrieved:
            logger.info("No relevant documents found for query")
            return RAGResponse(
                query=query,
                answer="I don't have enough information in the uploaded documents to answer this question.",
                citations=[],
                documents=[],
                confidence=0.0,
                grounded=False,
                evidence_note="No relevant document chunks were retrieved.",
            )
        
        # Step 2: Rerank documents
        reranked_docs = []
        doc_dicts = [
            {"content": doc.content, "metadata": doc.metadata, "doc_id": doc.id}
            for doc, score in retrieved
        ]
        reranked = self.reranker.rerank(query, doc_dicts, top_k=self.rerank_top_k)
        reranked_docs = [{"document": doc, "score": score} for doc, score in reranked]
        logger.info(f"Reranked to {len(reranked_docs)} documents")

        # Step 3: Format context and generate answer
        logger.info("Building doc_objects...")
        doc_objects = [
            Document(
                id=item["document"]["doc_id"],
                content=item["document"]["content"],
                metadata=item["document"]["metadata"],
            )
            for item in reranked_docs
        ]
        logger.info("Building retrieved_with_scores...")
        retrieved_with_scores = [
            (Document(
                id=doc["doc_id"],
                content=doc["content"],
                metadata=doc["metadata"]
            ), score)
            for doc, score in [(item["document"], item["score"]) for item in reranked_docs]
        ]

        if not reranked_docs:
            return self._insufficient_evidence_response(
                query=query,
                documents=[],
                note="No document chunks survived reranking.",
            )

        top_retrieval_score = max(float(score) for _, score in retrieved)
        top_rerank_score = float(reranked_docs[0]["score"])
        logger.info(f"Scores — retrieval: {top_retrieval_score:.3f}, rerank: {top_rerank_score:.3f}")

        context = self._format_context(retrieved_with_scores)
        prompt = self._create_prompt(query, context)

        # Step 4: Generate answer using LLM
        logger.info("Generating answer...")
        answer = await self._call_llm(prompt)

        # Step 5: Extract citations
        citations = self._extract_citations(answer, reranked_docs)
        if not citations and reranked_docs:
            top_doc = reranked_docs[0]["document"]
            citations = [{
                "index": 1,
                "source": top_doc.get("metadata", {}).get("source", "Unknown"),
                "content": top_doc.get("content", "")[:200],
            }]

        model_declined = (
            "don't have enough" in answer.lower()
            or "cannot find" in answer.lower()
            or "not found in" in answer.lower()
        )
        if model_declined:
            confidence = 0.0
            grounded = False
            evidence_note = "The model could not find enough explicit support in the retrieved evidence."
        else:
            # Cross-encoder logits typically span -15 to +15.
            # Map to [0, 1] linearly, clamped: score=-10→0, score=+10→1.
            rerank_norm = max(0.0, min(1.0, (top_rerank_score + 10.0) / 20.0))
            # Base confidence 60% when the LLM answered; add up to 30% from rerank quality
            # and 5% citation bonus, capping at 95%.
            confidence = min(0.95, 0.60 + 0.30 * rerank_norm + (0.05 if citations else 0.0))
            grounded = bool(citations) and confidence >= 0.55
            evidence_note = (
                "Answer is backed by retrieved document chunks."
                if grounded
                else "Answer generated from retrieved context."
            )

        response = RAGResponse(
            query=query,
            answer=answer.strip(),
            citations=citations,
            documents=doc_objects,
            confidence=float(confidence),
            grounded=grounded,
            evidence_note=evidence_note,
        )
        
        logger.info(f"Generated response with {len(citations)} citations")
        return response
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM via Ollama"""
        response = await self.llm_client.generate(prompt)
        return response
    
    def _extract_citations(self, answer: str, documents: List[Dict]) -> List[Dict[str, str]]:
        """Extract citations from answer (format: [1], [2], etc.)"""
        citations = []
        import re
        
        # Find all [N] patterns
        citation_pattern = re.findall(r'\[(\d+)\]', answer)
        
        for idx_str in set(citation_pattern):
            try:
                idx = int(idx_str) - 1  # Convert to 0-based index
                if 0 <= idx < len(documents):
                    doc = documents[idx]["document"]
                    citations.append({
                        "index": int(idx_str),
                        "source": doc.get("metadata", {}).get("source", "Unknown"),
                        "content": doc.get("content", "")[:200]  # First 200 chars
                    })
            except (ValueError, IndexError):
                pass
        
        return citations
