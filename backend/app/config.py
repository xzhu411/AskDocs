from functools import lru_cache
from typing import Annotated, Any

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    """Application Configuration"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    # Basic
    debug: bool = True
    log_level: str = "INFO"
    app_name: str = "AskMyDocs"
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost",
        "http://frontend:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
    ]
    
    # LLM provider: "claude" or "ollama"
    llm_provider: str = "claude"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Ollama (Local LLM, fallback)
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "mistral"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ollama_timeout_seconds: int = 180
    ollama_num_predict: int = 160
    
    # Qdrant Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    
    # Document Processing
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # RAG Configuration
    retrieval_k: int = 5
    rerank_top_k: int = 3
    bm25_weight: float = 0.5
    vector_weight: float = 0.5
    
    # Evaluation
    enable_evaluation: bool = True
    eval_dataset_path: str = "./eval_data"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        """Accept both JSON arrays and comma-separated origin lists."""
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("["):
                return value
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
