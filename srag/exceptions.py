"""
Custom exception classes for SRAG.
Provides specific exception types for different error scenarios.
"""


class SRAGException(Exception):
    """Base exception class for all SRAG errors."""
    pass


class EmbeddingException(SRAGException):
    """Raised when embedding generation fails."""
    pass


class VectorStoreException(SRAGException):
    """Raised when vector store operations fail."""
    pass


class RetrieverException(SRAGException):
    """Raised when document retrieval fails."""
    pass


class LLMException(SRAGException):
    """Raised when LLM operations fail."""
    pass


class DocumentLoadingException(SRAGException):
    """Raised when document loading fails."""
    pass


class ConfigurationException(SRAGException):
    """Raised when configuration is invalid."""
    pass
