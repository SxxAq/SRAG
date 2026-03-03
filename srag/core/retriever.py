"""
RAG Retriever for semantic document retrieval and ranking.
"""

from typing import List, Dict, Any
from srag.core.vector_store import VectorStore
from srag.core.embeddings import EmbeddingManager
from srag.exceptions import RetrieverException
from srag.logging_config import logger


class RAGRetriever:
    """Handles query-based retrieval from the vector store."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_manager: EmbeddingManager
    ):
        """
        Initialize the RAG retriever.
        
        Args:
            vector_store: VectorStore instance containing document embeddings
            embedding_manager: EmbeddingManager for generating query embeddings
        
        Raises:
            RetrieverException: If initialization fails
        """
        if not vector_store or not embedding_manager:
            raise RetrieverException("Both vector_store and embedding_manager are required")
        
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
        logger.info("RAG Retriever initialized")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query string
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
        
        Returns:
            List of dictionaries containing retrieved documents and metadata
        
        Raises:
            RetrieverException: If retrieval fails
        """
        try:
            logger.info(f"Retrieving documents for query: '{query}'")
            logger.info(f"Parameters: top_k={top_k}, score_threshold={score_threshold}")
            
            # Generate query embedding
            query_embedding = self.embedding_manager.generate_embeddings([query])[0]
            
            # Search in vector store
            results = self.vector_store.query(
                query_embeddings=[query_embedding.tolist()],
                top_k=top_k
            )
            
            # Process results
            retrieved_docs = []
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]
                
                for i, (doc_id, document, metadata, distance) in enumerate(
                    zip(ids, documents, metadatas, distances)
                ):
                    # Convert distance to similarity score
                    similarity_score = 1 - distance
                    
                    if similarity_score >= score_threshold:
                        retrieved_docs.append({
                            'id': doc_id,
                            'content': document,
                            'metadata': metadata,
                            'similarity_score': similarity_score,
                            'distance': distance,
                            'rank': i + 1
                        })
                
                logger.info(f"Retrieved {len(retrieved_docs)} documents (after filtering)")
            else:
                logger.warning("No documents found in vector store")
            
            return retrieved_docs
        except RetrieverException:
            raise
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            raise RetrieverException(f"Failed to retrieve documents: {e}") from e
