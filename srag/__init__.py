"""
SRAG: Semantic Retrieval-Augmented Generation
A production-grade RAG platform for intelligent document retrieval and LLM-powered Q&A.
"""

__version__ = "0.1.0"

from srag.core import (
    split_documents,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
)
from srag.loaders import DocumentProcessor
from srag.llm import (
    LLMBackendBase,
    GeminiBackend,
    get_llm_backend,
)
from srag.config import SRAGConfig
from srag.exceptions import (
    SRAGException,
    EmbeddingException,
    VectorStoreException,
    RetrieverException,
    LLMException,
    DocumentLoadingException,
    ConfigurationException,
)

__all__ = [
    # Version
    "__version__",
    
    # Core
    "split_documents",
    "EmbeddingManager",
    "VectorStore",
    "RAGRetriever",
    
    # Loaders
    "DocumentProcessor",
    
    # LLM
    "LLMBackendBase",
    "GeminiBackend",
    "get_llm_backend",
    
    # Config
    "SRAGConfig",
    
    # Exceptions
    "SRAGException",
    "EmbeddingException",
    "VectorStoreException",
    "RetrieverException",
    "LLMException",
    "DocumentLoadingException",
    "ConfigurationException",
]
