"""
Database setup and models for chat history and documents.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment or use SQLite in data folder
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/chat_history.db"
)

# Create directory if using SQLite
if DATABASE_URL.startswith("sqlite://"):
    db_path = DATABASE_URL.replace("sqlite:///./", "")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ============================================================================
# Database Models
# ============================================================================

class ChatHistory(Base):
    """Model for storing chat messages."""
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Store retrieved documents as JSON
    model = Column(String, default="gemini-2.5-flash")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String, nullable=True, index=True)  # For grouping conversations


class DocumentInfo(Base):
    """Model for tracking uploaded documents."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    file_type = Column(String, nullable=False)  # pdf, txt, markdown
    file_path = Column(String, nullable=False, unique=True)
    size_bytes = Column(Integer, nullable=False)
    num_chunks = Column(Integer, default=0)
    doc_metadata = Column("metadata", JSON, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow, index=True)
    last_accessed = Column(DateTime, nullable=True)


# ============================================================================
# Dependency: Get Database Session
# ============================================================================

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


if __name__ == "__main__":
    init_db()
