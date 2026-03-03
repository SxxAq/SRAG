"""
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Chat Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")


class SourceDocument(BaseModel):
    """Retrieved source document."""
    id: str
    content: str = Field(..., description="Document content")
    metadata: dict = Field(default_factory=dict, description="Document metadata")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    query: str
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Retrieved documents")
    model: str = Field(default="gemini-2.5-flash", description="LLM model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(BaseModel):
    """A single message in chat history."""
    id: str
    query: str
    answer: str
    sources: List[SourceDocument] = Field(default_factory=list)
    timestamp: datetime
    model: str


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[ChatMessage]
    total_messages: int


# ============================================================================
# Document Models
# ============================================================================

class DocumentMetadata(BaseModel):
    """Document metadata."""
    source_file: str
    file_type: str  # pdf, txt, markdown
    upload_time: datetime
    size_bytes: int


class DocumentResponse(BaseModel):
    """Response model for document."""
    id: str
    filename: str
    file_type: str
    size_bytes: int
    upload_time: datetime
    num_chunks: int
    metadata: dict = Field(default_factory=dict)


class DocumentsResponse(BaseModel):
    """Response model for documents list."""
    documents: List[DocumentResponse] = Field(default_factory=list)
    total_documents: int
    total_size_bytes: int


class DocumentDeleteRequest(BaseModel):
    """Request model for deleting document."""
    document_id: str


class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion."""
    success: bool
    message: str
    document_id: str


# ============================================================================
# System Status Models
# ============================================================================

class ModelInfo(BaseModel):
    """Information about a model."""
    name: str
    type: str  # embedding, llm
    status: str  # ready, loading, error


class SystemStatus(BaseModel):
    """System status response."""
    status: str = Field(..., description="Overall system status")
    api_version: str = Field(default="0.2.0")
    embedding_model: str
    llm_model: str
    vector_db: str
    documents_loaded: int
    vector_store_size: int
    ready: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Generic error response."""
    error: str
    detail: Optional[str] = None
    code: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error response."""
    error: str = "Validation Error"
    detail: str
    field: Optional[str] = None
