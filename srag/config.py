"""
Configuration management for SRAG.
Uses Pydantic for validation and environment variable support.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class SRAGConfig(BaseModel):
    """Main configuration class for SRAG application."""
    
    # Document Processing
    chunk_size: int = Field(
        default=1000,
        description="Size of document chunks in characters"
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between chunks in characters"
    )
    
    # Embeddings
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="SentenceTransformer model name"
    )
    
    # Vector Store
    vector_db_type: str = Field(
        default="chroma",
        description="Vector database type (chroma, faiss, etc.)"
    )
    vector_db_path: str = Field(
        default="./data/vector_store",
        description="Path to persist vector store"
    )
    collection_name: str = Field(
        default="documents",
        description="Vector store collection name"
    )
    
    # Retrieval
    top_k: int = Field(
        default=5,
        description="Number of top documents to retrieve"
    )
    similarity_threshold: float = Field(
        default=0.0,
        description="Minimum similarity score threshold"
    )
    
    # LLM
    llm_backend: str = Field(
        default="gemini",
        description="LLM backend to use (gemini, openai, local)"
    )
    llm_model: str = Field(
        default="gemini-2.5-flash",
        description="LLM model name"
    )
    max_context_length: int = Field(
        default=4000,
        description="Maximum context length for LLM"
    )
    
    # API Keys
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Gemini API key"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    class Config:
        env_prefix = "SRAG_"
        case_sensitive = False
    
    @classmethod
    def from_env(cls) -> "SRAGConfig":
        """Load configuration from environment variables."""
        return cls(
            chunk_size=int(os.getenv("SRAG_CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("SRAG_CHUNK_OVERLAP", 200)),
            embedding_model=os.getenv("SRAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            vector_db_type=os.getenv("SRAG_VECTOR_DB_TYPE", "chroma"),
            vector_db_path=os.getenv("SRAG_VECTOR_DB_PATH", "./data/vector_store"),
            llm_backend=os.getenv("SRAG_LLM_BACKEND", "gemini"),
            llm_model=os.getenv("SRAG_LLM_MODEL", "gemini-2.5-flash"),
            top_k=int(os.getenv("SRAG_TOP_K", 5)),
            similarity_threshold=float(os.getenv("SRAG_SIMILARITY_THRESHOLD", 0.0)),
            max_context_length=int(os.getenv("SRAG_MAX_CONTEXT_LENGTH", 4000)),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            log_level=os.getenv("SRAG_LOG_LEVEL", "INFO"),
        )


# Default config instance
default_config = SRAGConfig()
