# Sample Documents for Testing

## Document 1: RAG Fundamentals (in docs/sample_rag.md when you create it)

**Content:**
```markdown
# Retrieval-Augmented Generation (RAG)

RAG is a powerful technique that combines the strengths of information retrieval with large language models (LLMs).

## What is RAG?

RAG stands for Retrieval-Augmented Generation. It's a technique in natural language processing that enhances the capabilities of language models by incorporating external knowledge retrieval.

The basic workflow:
1. User query is received
2. Relevant documents are retrieved from a knowledge base
3. Retrieved documents are passed as context to the LLM
4. LLM generates an answer based on the context
5. Answer is returned with citations to source documents

## Why Use RAG?

### Reduces Hallucinations
Language models can generate plausible-sounding but incorrect information. RAG grounds responses in actual documents.

### Incorporates Current Information
LLMs are trained on static datasets. RAG allows them to use updated information from recent documents.

### Provides Citations
Every claim in the answer can be traced back to a source document, increasing trust and verifiability.

### Cost-Effective
RAG is more cost-effective than fine-tuning LLMs for each domain because you can use a single general-purpose LLM.

## Components of RAG

### 1. Document Store
A collection of documents that contains domain-specific information.

### 2. Retriever
Finds relevant documents for a given query. Can be:
- Lexical: BM25, TF-IDF
- Semantic: Dense embeddings

### 3. Language Model
Generates answers based on the retrieved context.

### 4. Reranker
Improves quality by re-scoring retrieval results to find truly relevant documents.

## Hybrid Retrieval

The AskMyDocs system uses hybrid retrieval combining:
- **BM25**: Keyword-based matching (50%)
- **Vector Search**: Semantic similarity (50%)

This balances precision from keywords with semantic understanding.
```

## How to Use These Files

1. **Create test documents:**
```bash
mkdir -p docs/test_files
cat > docs/test_files/rag_guide.md << 'EOF'
[paste content above]
EOF
```

2. **Upload via UI:**
   - Go to http://localhost:5173
   - Upload the file
   - Ask questions about it

3. **Test queries:**
   - "What is RAG?"
   - "Why should I use RAG?"
   - "What are components of RAG?"
   - "What is hybrid retrieval?"

## Expected Behavior

- ✅ Documents are split into chunks
- ✅ Chunks are indexed in Qdrant
- ✅ Queries retrieve relevant chunks
- ✅ Answers are generated with citations
- ✅ Citations link to source documents
- ✅ Confidence score indicates quality

## Customize for Your Use Case

Edit these files to match your domain:
- Create domain-specific markdown files
- Upload PDFs of your documentation
- Add text files with domain knowledge

The system will learn from your documents and answer domain-specific questions.
