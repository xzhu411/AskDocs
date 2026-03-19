"""
AskMyDocs Platform - Project Structure Summary
"""

project_structure = {
    "AskMyDocs/": {
        "Backend": {
            "path": "backend/",
            "components": {
                "app/": {
                    "rag/": [
                        "retriever.py - Hybrid BM25 + Vector search",
                        "reranker.py - Cross-encoder reranking",
                        "rag_chain.py - Complete RAG pipeline",
                        "document_processor.py - Document ingestion"
                    ],
                    "evaluation/": [
                        "evaluator.py - RAGAS evaluation pipeline"
                    ],
                    "api/": [
                        "models.py - Request/response schemas"
                    ],
                    "main.py": "FastAPI application",
                    "config.py": "Configuration management"
                },
                "requirements.txt": "Python dependencies",
                ".env.example": "Environment template",
                "Dockerfile": "Container image"
            }
        },
        "Frontend": {
            "path": "frontend/",
            "components": {
                "src/": {
                    "components": [
                        "App.tsx - Main component",
                        "api.ts - API client",
                        "FileUpload.tsx - Upload handler",
                        "QueryInput.tsx - Query interface",
                        "Answer.tsx - Answer display",
                        "components.tsx - Reusable UI"
                    ],
                    "index.css": "Tailwind styles"
                },
                "vite.config.ts": "Build configuration",
                "tsconfig.json": "TypeScript config",
                "package.json": "Dependencies",
                "Dockerfile": "Container image"
            }
        },
        "Infrastructure": {
            "docker-compose.yml": "Service orchestration",
            "setup.sh": "Automated setup",
            "stop.sh": "Stop services",
            "clean.sh": "Reset everything",
            "check.sh": "Status check"
        },
        "Documentation": {
            "README.md": "Full documentation",
            "QUICKSTART.md": "5-minute quick start",
            "docs/": {
                "DEVELOPMENT.md": "Developer guide",
                "SAMPLE_DOCUMENTS.md": "Test data",
                "eval_sample.json": "Evaluation dataset"
            }
        },
        "Config": {
            ".gitignore": "Git ignore rules",
            ".env.example": "Environment template"
        }
    }
}

# Key Features
features = [
    "✅ Hybrid Retrieval (BM25 + Vector)",
    "✅ Cross-Encoder Reranking",
    "✅ Citation Enforcement",
    "✅ Local LLM (Ollama + Mistral)",
    "✅ Vector Database (Qdrant)",
    "✅ React Frontend",
    "✅ FastAPI Backend",
    "✅ Docker Compose Setup",
    "✅ Evaluation Pipeline",
    "✅ Document Upload (.md, .txt, .pdf)",
    "✅ CORS Enabled",
    "✅ Production Ready"
]

# Quick Start
quick_start = """
1. cd /Users/zhuxiaoai/Projects/AskMyDocs
2. chmod +x setup.sh
3. ./setup.sh
4. Open http://localhost:5173
5. Upload documents and ask questions!
"""

# API Endpoints
endpoints = {
    "POST /query": "Query documents with RAG",
    "POST /upload": "Upload and process documents",
    "GET /health": "Health check",
    "GET /docs": "Interactive API documentation"
}

# Services
services = {
    "Frontend": "http://localhost:5173",
    "Backend": "http://localhost:8000",
    "API Docs": "http://localhost:8000/docs",
    "Qdrant": "http://localhost:6333",
    "Ollama": "http://localhost:11434"
}

print("AskMyDocs Platform - Production RAG Application")
print("=" * 50)
print("\nKey Features:")
for feature in features:
    print(f"  {feature}")

print("\nServices:")
for service, url in services.items():
    print(f"  {service}: {url}")

print("\nAPI Endpoints:")
for endpoint, description in endpoints.items():
    print(f"  {endpoint}: {description}")

print("\nQuick Start:")
print(quick_start)
