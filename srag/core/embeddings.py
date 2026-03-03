"""
Embedding generation and management using SentenceTransformers.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from srag.exceptions import EmbeddingException
from srag.logging_config import logger


class EmbeddingManager:
    """Manages document embedding generation using SentenceTransformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: HuggingFace model name for sentence embeddings
        
        Raises:
            EmbeddingException: If model loading fails
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            embedding_dim = self.get_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise EmbeddingException(f"Failed to load embedding model: {e}") from e
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            Numpy array of embeddings with shape (len(texts), embedding_dim)
        
        Raises:
            EmbeddingException: If embedding generation fails
        """
        if not self.model:
            raise EmbeddingException("Model not loaded")
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts...")
            embeddings = self.model.encode(texts, show_progress_bar=True)
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise EmbeddingException(f"Failed to generate embeddings: {e}") from e
    
    def get_embedding_dimension(self) -> int:
        """
        Get the embedding dimension of the model.
        
        Returns:
            Dimension of the embedding vectors
        
        Raises:
            EmbeddingException: If model is not loaded
        """
        if not self.model:
            raise EmbeddingException("Model not loaded")
        return self.model.get_sentence_embedding_dimension()
