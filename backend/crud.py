"""
CRUD operations for database models.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .database import ChatHistory, DocumentInfo
from .models import ChatMessage, DocumentResponse


# ============================================================================
# Chat History Operations
# ============================================================================

def create_chat_message(
    db: Session,
    query: str,
    answer: str,
    sources: Optional[List[dict]] = None,
    model: str = "gemini-2.5-flash",
    session_id: Optional[str] = None,
) -> ChatHistory:
    """Create a new chat history record."""
    message_id = str(uuid.uuid4())
    
    db_message = ChatHistory(
        id=message_id,
        query=query,
        answer=answer,
        sources=sources or [],
        model=model,
        session_id=session_id,
        timestamp=datetime.utcnow(),
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


def get_chat_history(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    session_id: Optional[str] = None,
) -> tuple[List[ChatHistory], int]:
    """Get chat history with pagination."""
    query = db.query(ChatHistory)
    
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)
    
    total = query.count()
    messages = query.order_by(desc(ChatHistory.timestamp)).offset(offset).limit(limit).all()
    
    return messages, total


def get_chat_message(db: Session, message_id: str) -> Optional[ChatHistory]:
    """Get a specific chat message."""
    return db.query(ChatHistory).filter(ChatHistory.id == message_id).first()


def delete_chat_history(db: Session, session_id: Optional[str] = None) -> int:
    """Delete chat history. If session_id provided, delete only that session."""
    query = db.query(ChatHistory)
    
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)
    
    count = query.delete()
    db.commit()
    
    return count


def clear_all_chat_history(db: Session) -> int:
    """Clear all chat history."""
    count = db.query(ChatHistory).delete()
    db.commit()
    return count


# ============================================================================
# Document Operations
# ============================================================================

def create_document(
    db: Session,
    filename: str,
    file_type: str,
    file_path: str,
    size_bytes: int,
    num_chunks: int = 0,
    metadata: Optional[dict] = None,
) -> DocumentInfo:
    """Create a new document record."""
    doc_id = str(uuid.uuid4())
    
    db_doc = DocumentInfo(
        id=doc_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        size_bytes=size_bytes,
        num_chunks=num_chunks,
        doc_metadata=metadata or {},
        upload_time=datetime.utcnow(),
    )
    
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    return db_doc


def get_documents(
    db: Session,
    limit: int = 100,
    offset: int = 0,
) -> tuple[List[DocumentInfo], int]:
    """Get all documents with pagination."""
    total = db.query(DocumentInfo).count()
    documents = (
        db.query(DocumentInfo)
        .order_by(desc(DocumentInfo.upload_time))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return documents, total


def get_document(db: Session, document_id: str) -> Optional[DocumentInfo]:
    """Get a specific document."""
    return db.query(DocumentInfo).filter(DocumentInfo.id == document_id).first()


def get_document_by_path(db: Session, file_path: str) -> Optional[DocumentInfo]:
    """Get document by file path."""
    return db.query(DocumentInfo).filter(DocumentInfo.file_path == file_path).first()


def update_document(
    db: Session,
    document_id: str,
    **kwargs,
) -> Optional[DocumentInfo]:
    """Update a document record."""
    db_doc = db.query(DocumentInfo).filter(DocumentInfo.id == document_id).first()
    
    if db_doc:
        # Update allowed fields
        for key, value in kwargs.items():
            if hasattr(db_doc, key) and key not in ["id", "file_path", "upload_time"]:
                setattr(db_doc, key, value)
        
        db_doc.last_accessed = datetime.utcnow()
        db.commit()
        db.refresh(db_doc)
    
    return db_doc


def delete_document(db: Session, document_id: str) -> bool:
    """Delete a document record."""
    db_doc = db.query(DocumentInfo).filter(DocumentInfo.id == document_id).first()
    
    if db_doc:
        db.delete(db_doc)
        db.commit()
        return True
    
    return False


def get_documents_by_type(
    db: Session,
    file_type: str,
) -> List[DocumentInfo]:
    """Get all documents of a specific type."""
    return db.query(DocumentInfo).filter(DocumentInfo.file_type == file_type).all()


def get_total_documents_size(db: Session) -> int:
    """Get total size of all documents."""
    result = db.query(DocumentInfo).with_entities(
        db.func.sum(DocumentInfo.size_bytes)
    ).scalar()
    
    return result or 0


def get_total_chunks(db: Session) -> int:
    """Get total number of chunks across all documents."""
    result = db.query(DocumentInfo).with_entities(
        db.func.sum(DocumentInfo.num_chunks)
    ).scalar()
    
    return result or 0
