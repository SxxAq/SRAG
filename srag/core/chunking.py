"""
Document chunking utilities for splitting text into manageable pieces.
"""

from typing import List, Any
try:
    # Newer LangChain splitters package
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Backward compatibility with older langchain releases
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from srag.logging_config import logger


def split_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split documents into smaller chunks for better RAG performance.
    
    Args:
        documents: List of LangChain Document objects to split
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between chunks to maintain context
    
    Returns:
        List of Document objects with split content
    
    Raises:
        ValueError: If documents list is empty
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    logger.info(f"Splitting {len(documents)} documents (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    splitted_docs = text_splitter.split_documents(documents)
    logger.info(f"Split into {len(splitted_docs)} chunks")
    
    if splitted_docs:
        logger.debug(f"Sample chunk preview: {splitted_docs[0].page_content[:100]}...")
    
    return splitted_docs
