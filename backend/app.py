"""
FastAPI REST API for SRAG (Semantic Retrieval-Augmented Generation).

Exposes the RAG system via HTTP endpoints for:
- Document management (upload, list, delete)
- Chat with semantic retrieval
- Chat history
- System status
"""

import os
import uuid
from datetime import datetime
from typing import Optional
import logging

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import SRAG components
from srag import (
    DocumentProcessor,
    split_documents,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
    get_llm_backend,
    SRAGConfig,
)

# Import backend modules
from .models import (
    ChatRequest,
    ChatResponse,
    SourceDocument,
    ChatHistoryResponse,
    ChatMessage,
    DocumentResponse,
    DocumentsResponse,
    SystemStatus,
    HealthResponse,
    ErrorResponse,
)
from .database import init_db, get_db
from . import crud

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="SRAG API",
    description="Semantic Retrieval-Augmented Generation API",
    version="0.2.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global State (RAG Pipeline)
# ============================================================================

class RAGPipeline:
    """Singleton for RAG pipeline components."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGPipeline, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing RAG pipeline...")
        
        # Load configuration
        self.config = SRAGConfig()
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.embedding_manager = EmbeddingManager(
            model_name=self.config.embedding_model
        )
        self.vector_store = VectorStore(
            collection_name="srag_documents",
            persist_directory=self.config.vector_db_path,
        )
        self.retriever = RAGRetriever(
            self.vector_store,
            self.embedding_manager,
        )
        self.llm = get_llm_backend(self.config.llm_backend)
        
        # Preload existing documents
        data_dir = "./data/text_files"
        if os.path.exists(data_dir):
            try:
                logger.info(f"Preloading documents from {data_dir}...")
                documents = self.document_processor.load_text_files(data_dir)
                if documents:
                    logger.info(f"Loaded {len(documents)} documents")
                    self._index_documents(documents)
            except Exception as e:
                logger.warning(f"Failed to preload documents: {e}")
        
        self._initialized = True
        logger.info("RAG pipeline initialized successfully!")
    
    def _index_documents(self, documents):
        """Index documents into vector store."""
        try:
            chunks = split_documents(documents)
            texts = [doc.page_content for doc in chunks]
            embeddings = self.embedding_manager.generate_embeddings(texts)
            self.vector_store.add_documents(chunks, embeddings)
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            raise


# Initialize RAG pipeline on startup
rag_pipeline = None


@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG pipeline."""
    global rag_pipeline
    
    logger.info("Starting up SRAG API...")
    init_db()
    rag_pipeline = RAGPipeline()
    logger.info("SRAG API ready!")


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if API is running."""
    return HealthResponse(status="healthy")


@app.get("/api/status", response_model=SystemStatus, tags=["System"])
async def get_status():
    """Get system status and model information."""
    try:
        doc_count = rag_pipeline.vector_store.get_count()
        return SystemStatus(
            status="ready",
            embedding_model=rag_pipeline.config.embedding_model,
            llm_model=rag_pipeline.config.llm_model,
            vector_db=rag_pipeline.config.vector_db_type,
            documents_loaded=doc_count,
            vector_store_size=doc_count,
            ready=True,
        )
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint with semantic retrieval.
    
    Retrieves relevant documents and generates answer using LLM.
    """
    try:
        query = request.query
        top_k = request.top_k
        score_threshold = request.score_threshold
        
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant documents
        retrieved = rag_pipeline.retriever.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        
        # Build context from retrieved documents
        context = "\n\n".join([doc["content"] for doc in retrieved])
        
        # Generate answer
        answer = rag_pipeline.llm.generate_with_context(query, context)
        
        # Convert retrieved docs to response format
        sources = [
            SourceDocument(
                id=doc.get("id", ""),
                content=doc.get("content", "")[:500],  # Truncate for response
                metadata=doc.get("metadata", {}),
                similarity_score=doc.get("similarity_score", 0.0),
            )
            for doc in retrieved
        ]
        
        # Create response
        response = ChatResponse(
            query=query,
            answer=answer,
            sources=sources,
            model=rag_pipeline.config.llm_model,
        )
        
        # Save to database
        try:
            crud.create_chat_message(
                db,
                query=query,
                answer=answer,
                sources=[s.dict() for s in sources],
                model=rag_pipeline.config.llm_model,
            )
        except Exception as e:
            logger.warning(f"Failed to save chat message: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history", response_model=ChatHistoryResponse, tags=["Chat"])
async def get_chat_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get chat history with pagination."""
    try:
        messages, total = crud.get_chat_history(db, limit=limit, offset=offset)
        
        chat_messages = [
            ChatMessage(
                id=msg.id,
                query=msg.query,
                answer=msg.answer,
                sources=msg.sources or [],
                timestamp=msg.timestamp,
                model=msg.model,
            )
            for msg in messages
        ]
        
        return ChatHistoryResponse(
            messages=chat_messages,
            total_messages=total,
        )
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/history", tags=["Chat"])
async def clear_chat_history(db: Session = Depends(get_db)):
    """Clear all chat history."""
    try:
        count = crud.clear_all_chat_history(db)
        return {"success": True, "message": f"Cleared {count} messages"}
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Document Endpoints
# ============================================================================

@app.post("/api/documents/upload", response_model=DocumentResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document (PDF, TXT, or Markdown).
    
    The document will be split into chunks, embedded, and added to vector store.
    """
    try:
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Determine file type
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ["pdf", "txt", "md", "markdown"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: pdf, txt, md",
            )
        
        file_type = "markdown" if file_ext == "md" else file_ext
        
        # Save file
        upload_dir = "./data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Uploaded file: {file.filename}")
        
        # Load and process document
        documents = []
        if file_type == "pdf":
            # Load single PDF
            documents = rag_pipeline.document_processor.load_pdfs(upload_dir)
        else:
            # Load single text file
            documents = rag_pipeline.document_processor.load_text_files(upload_dir)
        
        if not documents:
            raise HTTPException(status_code=400, detail="Failed to load document")
        
        # Split into chunks
        chunks = split_documents(documents)
        num_chunks = len(chunks)
        
        # Generate embeddings and add to vector store
        texts = [doc.page_content for doc in chunks]
        embeddings = rag_pipeline.embedding_manager.generate_embeddings(texts)
        rag_pipeline.vector_store.add_documents(chunks, embeddings)
        
        # Save to database
        doc_id = str(uuid.uuid4())
        db_doc = crud.create_document(
            db,
            filename=file.filename,
            file_type=file_type,
            file_path=file_path,
            size_bytes=len(content),
            num_chunks=num_chunks,
            metadata={"source_file": file.filename},
        )
        
        return DocumentResponse(
            id=db_doc.id,
            filename=db_doc.filename,
            file_type=db_doc.file_type,
            size_bytes=db_doc.size_bytes,
            upload_time=db_doc.upload_time,
            num_chunks=db_doc.num_chunks,
            metadata=db_doc.metadata,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents", response_model=DocumentsResponse, tags=["Documents"])
async def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all uploaded documents."""
    try:
        documents, total = crud.get_documents(db, limit=limit, offset=offset)
        total_size = crud.get_total_documents_size(db)
        
        doc_responses = [
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                size_bytes=doc.size_bytes,
                upload_time=doc.upload_time,
                num_chunks=doc.num_chunks,
                metadata=doc.metadata,
            )
            for doc in documents
        ]
        
        return DocumentsResponse(
            documents=doc_responses,
            total_documents=total,
            total_size_bytes=total_size,
        )
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{document_id}", tags=["Documents"])
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Delete a document."""
    try:
        # Check if document exists
        doc = crud.get_document(db, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from database
        crud.delete_document(db, document_id)
        
        # Delete file if it exists
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            logger.info(f"Deleted file: {doc.file_path}")
        
        return {
            "success": True,
            "message": f"Deleted document: {doc.filename}",
            "document_id": document_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "name": "SRAG API",
        "version": "0.2.0",
        "description": "Semantic Retrieval-Augmented Generation API",
        "docs": "/api/docs",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "chat": "/api/chat",
            "chat_history": "/api/chat/history",
            "documents": "/api/documents",
            "upload": "/api/documents/upload",
        },
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return ErrorResponse(
        error=exc.detail,
        detail=str(exc),
        code=str(exc.status_code),
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
