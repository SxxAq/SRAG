"""
Vector store management using ChromaDB for persistent document storage.
"""

import os
from typing import List, Dict, Any
import uuid
import numpy as np
import chromadb
from langchain_core.documents import Document
from srag.exceptions import VectorStoreException
from srag.logging_config import logger


class VectorStore:
    """Manages document embeddings in a ChromaDB vector store."""
    
    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: str = "./data/vector_store"
    ):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector store
        
        Raises:
            VectorStoreException: If initialization fails
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persistent ChromaDB client
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
            
            logger.info(f"Vector store initialized. Collection: {self.collection_name}")
            logger.info(f"Existing documents in collection: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise VectorStoreException(f"Failed to initialize vector store: {e}") from e
    
    def add_documents(
        self,
        documents: List[Document],
        embeddings: np.ndarray
    ) -> None:
        """
        Add documents and their embeddings to the vector store.
        
        Args:
            documents: List of LangChain documents
            embeddings: Corresponding embeddings as numpy array
        
        Raises:
            VectorStoreException: If adding documents fails
        """
        if len(documents) != len(embeddings):
            raise VectorStoreException(
                f"Number of documents ({len(documents)}) must match "
                f"number of embeddings ({len(embeddings)})"
            )
        
        logger.info(f"Adding {len(documents)} documents to vector store...")
        
        try:
            # Prepare data for ChromaDB
            ids = []
            metadatas = []
            documents_text = []
            embeddings_list = []
            
            for i, (doc, emb) in enumerate(zip(documents, embeddings)):
                # Generate unique ID
                doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
                ids.append(doc_id)
                
                # Prepare metadata
                metadata = dict(doc.metadata) if doc.metadata else {}
                metadata['doc_index'] = i
                metadata['content_length'] = len(doc.page_content)
                metadatas.append(metadata)
                
                # Document content
                documents_text.append(doc.page_content)
                
                # Embeddings
                embeddings_list.append(emb.tolist())
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            logger.info(f"Total documents in collection: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise VectorStoreException(f"Failed to add documents: {e}") from e
    
    def query(
        self,
        query_embeddings: List[List[float]],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.
        
        Args:
            query_embeddings: List of query embeddings
            top_k: Number of top results to return
        
        Returns:
            Query results from ChromaDB
        
        Raises:
            VectorStoreException: If query fails
        """
        try:
            logger.info(f"Querying vector store with top_k={top_k}")
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k
            )
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            raise VectorStoreException(f"Failed to query vector store: {e}") from e
    
    def get_count(self) -> int:
        """Get total number of documents in collection."""
        return self.collection.count()
