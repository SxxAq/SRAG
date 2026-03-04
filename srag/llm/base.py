"""
Base class for LLM backends and implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import os
from srag.exceptions import LLMException
from srag.logging_config import logger


class LLMBackendBase(ABC):
    """Abstract base class for LLM backends."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize LLM backend.
        
        Args:
            model_name: Name of the model to use
            api_key: Optional API key (can use env vars)
        """
        self.model_name = model_name
        self.api_key = api_key
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt for the LLM
        
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response with context.
        
        Args:
            query: User query
            context: Retrieved context
            system_prompt: Optional system prompt
        
        Returns:
            Generated response
        """
        pass


class GeminiBackend(LLMBackendBase):
    """Google Gemini LLM backend."""
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key: Optional[str] = None
    ):
        """
        Initialize Gemini backend.
        
        Args:
            model_name: Gemini model to use
            api_key: Gemini API key (uses GEMINI_API_KEY env var if not provided)
        
        Raises:
            LLMException: If initialization fails
        """
        super().__init__(model_name, api_key)
        
        try:
            # Use provided key or get from environment
            key = api_key or os.getenv("GEMINI_API_KEY")
            if not key:
                raise LLMException("GEMINI_API_KEY not provided and not found in environment")

            # Prefer the newer google-genai SDK when available, but keep
            # compatibility with google-generativeai used by older dependency sets.
            try:
                from google import genai

                self._sdk = "google-genai"
                self.client = genai.Client(api_key=key)
                logger.info(f"Gemini backend initialized with {self._sdk}: {model_name}")
            except ImportError:
                import google.generativeai as genai_legacy

                self._sdk = "google-generativeai"
                genai_legacy.configure(api_key=key)
                self.client = genai_legacy.GenerativeModel(model_name)
                logger.info(f"Gemini backend initialized with {self._sdk}: {model_name}")
        except ImportError as e:
            raise LLMException(
                "Neither google-genai nor google-generativeai is installed"
            ) from e
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            raise LLMException(f"Failed to initialize Gemini: {e}") from e
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using Gemini.
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        
        Raises:
            LLMException: If generation fails
        """
        try:
            logger.info(f"Generating response with Gemini ({self.model_name})")

            if self._sdk == "google-genai":
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
            else:
                response = self.client.generate_content(prompt)

            return getattr(response, "text", str(response))
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise LLMException(f"Failed to generate response: {e}") from e
    
    def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response with retrieved context.
        
        Args:
            query: User query
            context: Retrieved document context
            system_prompt: Optional system instruction
        
        Returns:
            Generated response
        """
        if not system_prompt:
            system_prompt = (
                "You are an expert technical assistant. "
                "Using the provided context, answer the user's question accurately and concisely. "
                "If the answer is not in the context, say so clearly."
            )
        
        prompt = f"""{system_prompt}

Context:
{context}

Question:
{query}

Answer:"""
        
        return self.generate(prompt)


def get_llm_backend(
    backend_type: str = "gemini",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> LLMBackendBase:
    """
    Factory function to get LLM backend.
    
    Args:
        backend_type: Type of backend (gemini, openai, local)
        model_name: Optional model name
        api_key: Optional API key
    
    Returns:
        LLM backend instance
    
    Raises:
        LLMException: If backend type is unknown
    """
    backend_type = backend_type.lower()
    
    if backend_type == "gemini":
        model = model_name or "gemini-2.5-flash"
        return GeminiBackend(model_name=model, api_key=api_key)
    else:
        raise LLMException(f"Unknown LLM backend: {backend_type}")
