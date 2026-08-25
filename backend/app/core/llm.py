"""
LLM client module for AyurPedia.
Handles LLM integration with fallback support between Gemini and NVIDIA NIM.
"""

import logging
from typing import Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import get_config
from ..ingestion.embedder import Embedder


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client with Gemini support."""
    
    def __init__(self) -> None:
        """Initialize LLM client with Gemini configuration."""
        config = get_config()
        
        # Initialize Gemini LLM
        self.primary_llm = None
        self.using_fallback = False
        
        try:
            if config.gemini_api_key:
                self.primary_llm = ChatGoogleGenerativeAI(
                    model=config.gemini_model,
                    api_key=config.gemini_api_key,
                    temperature=0.4,
                    max_output_tokens=4096
                )
                logger.info(f"Primary LLM initialized: {config.gemini_model}")
            else:
                logger.warning("Gemini API key not set, primary LLM unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize primary LLM: {e}")
        
        # Initialize embedding model (Cohere from Phase 1)
        self.embedder = None
        try:
            if config.cohere_api_key:
                self.embedder = Embedder(api_key=config.cohere_api_key)
                logger.info("Embedding model initialized: Cohere")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
    
    def get_llm(self) -> Optional[ChatGoogleGenerativeAI]:
        """Get the primary Gemini LLM.
        
        Returns:
            Primary LLM instance or None if unavailable
        """
        return self.primary_llm
    
    def get_llm_with_fallback(self) -> Any:
        """Get LLM (Gemini only for now).
        
        Returns:
            Primary LLM if available
            
        Raises:
            RuntimeError: If LLM is not available
        """
        if self.primary_llm:
            return self.primary_llm
        else:
            raise RuntimeError("LLM not available")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type(Exception)
    )
    def invoke_with_fallback(self, prompt: str) -> str:
        """Invoke LLM with retry logic.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response string
            
        Raises:
            RuntimeError: If LLM is not available
        """
        if self.primary_llm:
            try:
                logger.info("Using Gemini LLM")
                response = self.primary_llm.invoke([HumanMessage(content=prompt)])
                return response.content
            except Exception as e:
                logger.error(f"LLM invocation failed: {e}")
                raise RuntimeError(f"LLM invocation failed: {e}")
        
        raise RuntimeError("LLM not available for invocation")
    
    def is_primary_available(self) -> bool:
        """Check if primary Gemini LLM is available.
        
        Returns:
            True if primary LLM is available, False otherwise
        """
        if self.primary_llm is None:
            return False
        
        try:
            # Simple health check
            response = self.primary_llm.invoke([HumanMessage(content="test")])
            return response.content is not None
        except Exception as e:
            logger.warning(f"Primary LLM health check failed: {e}")
            return False
    
    def get_embedding_model(self) -> Optional[Embedder]:
        """Get the embedding model (Cohere from Phase 1).
        
        Returns:
            Embedder instance or None if unavailable
        """
        return self.embedder
    
    def get_status(self) -> dict:
        """Get the status of all LLM components.
        
        Returns:
            Dictionary with status information
        """
        config = get_config()
        return {
            "primary_available": self.primary_llm is not None,
            "primary_model": config.gemini_model if self.primary_llm else None,
            "fallback_available": False,
            "fallback_model": None,
            "embedding_available": self.embedder is not None,
            "using_fallback": self.using_fallback
        }


# Global LLM client instance (lazy loaded)
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance.
    
    Returns:
        Global LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
