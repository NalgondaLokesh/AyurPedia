"""
LLM client module for AyurPedia.
Handles LLM integration with fallback support between Groq and NVIDIA NIM.
"""

import logging
from typing import Optional, Any
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI
from .config import get_config
from ..ingestion.embedder import Embedder


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client with Groq support."""
    
    def __init__(self) -> None:
        """Initialize LLM client with Groq configuration and NVIDIA NIM fallback."""
        config = get_config()
        
        # Initialize Groq LLM (primary)
        self.primary_llm = None
        self.fallback_llm = None
        self.using_fallback = False
        self.openai_client = None  # Direct OpenAI client for NVIDIA NIM
        
        try:
            if config.groq_api_key:
                self.primary_llm = ChatGroq(
                    model=config.groq_model,
                    api_key=config.groq_api_key,
                    temperature=0.4,
                    max_tokens=4096
                )
                logger.info(f"Primary LLM initialized: {config.groq_model}")
            else:
                logger.warning("Groq API key not set, primary LLM unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize primary LLM: {e}")
        
        # Initialize NVIDIA NIM LLM (fallback) using LangChain
        try:
            if config.nvidia_nim_api_key and config.nvidia_nim_base_url:
                self.fallback_llm = ChatOpenAI(
                    model=config.fallback_model,
                    api_key=config.nvidia_nim_api_key,
                    base_url=config.nvidia_nim_base_url,
                    temperature=0.4,
                    max_tokens=4096
                )
                logger.info(f"Fallback LLM initialized: {config.fallback_model}")
            else:
                logger.warning("NVIDIA NIM credentials not set, fallback LLM unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize fallback LLM: {e}")
        
        # Initialize direct OpenAI client for NVIDIA NIM (for direct API calls)
        try:
            if config.nvidia_nim_api_key and config.nvidia_nim_base_url:
                self.openai_client = OpenAI(
                    base_url=config.nvidia_nim_base_url,
                    api_key=config.nvidia_nim_api_key
                )
                logger.info("Direct OpenAI client initialized for NVIDIA NIM")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize embedding model (Cohere from Phase 1)
        self.embedder = None
        try:
            if config.cohere_api_key:
                self.embedder = Embedder(api_key=config.cohere_api_key)
                logger.info("Embedding model initialized: Cohere")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
    
    def get_llm(self) -> Optional[ChatGroq]:
        """Get the primary Groq LLM.
        
        Returns:
            Primary LLM instance or None if unavailable
        """
        return self.primary_llm
    
    def get_llm_with_fallback(self) -> Any:
        """Get LLM with automatic fallback to NVIDIA NIM on rate limit errors.
        
        Returns:
            Primary LLM if available, otherwise fallback LLM
            
        Raises:
            RuntimeError: If no LLM is available
        """
        if self.primary_llm:
            return self.primary_llm
        elif self.fallback_llm:
            self.using_fallback = True
            logger.info("Using fallback LLM (NVIDIA NIM)")
            return self.fallback_llm
        else:
            raise RuntimeError("No LLM available (both primary and fallback unavailable)")
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error.
        
        Args:
            error: Exception to check
            
        Returns:
            True if rate limit error, False otherwise
        """
        error_str = str(error).lower()
        rate_limit_indicators = [
            'rate limit', '429', 'quota', 'too many requests',
            'rate_limit_exceeded', 'resource_exhausted'
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)

    def invoke_nvidia_nim_direct(self, prompt: str, extra_body: Optional[dict] = None) -> str:
        """Invoke NVIDIA NIM using direct OpenAI client.
        
        Args:
            prompt:The prompt to send to the LLM
            extra_body: Extra body parameters for NVIDIA NIM (e.g., thinking, reasoning_effort)
            
        Returns:
            LLM response string
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized for NVIDIA NIM")
        
        config = get_config()
        try:
            completion = self.openai_client.chat.completions.create(
                model=config.fallback_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                top_p=0.95,
                max_tokens=16384,
                extra_body=extra_body or {},
                stream=False
            )
            
            # Extract reasoning if available
            reasoning = getattr(completion.choices[0].message, "reasoning", None) or getattr(completion.choices[0].message, "reasoning_content", None)
            if reasoning:
                logger.info(f"Reasoning from NVIDIA NIM: {reasoning[:200]}...")
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Direct NVIDIA NIM invocation failed: {e}")
            raise
    
    def invoke_with_fallback(self, prompt: str) -> str:
        """Invoke LLM with automatic fallback on rate limit errors.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response string
            
        Raises:
            RuntimeError: If no LLM is available
        """
        # Try primary LLM first
        if self.primary_llm:
            try:
                logger.info("Using Gemini LLM")
                response = self.primary_llm.invoke([HumanMessage(content=prompt)])
                self.using_fallback = False
                return response.content
            except Exception as e:
                if self._is_rate_limit_error(e):
                    logger.warning(f"Rate limit error on primary LLM: {e}")
                    if self.fallback_llm:
                        logger.info("Switching to fallback LLM (NVIDIA NIM)")
                        self.using_fallback = True
                        try:
                            response = self.fallback_llm.invoke([HumanMessage(content=prompt)])
                            return response.content
                        except Exception as fallback_error:
                            logger.error(f"Fallback LLM also failed: {fallback_error}")
                            raise RuntimeError(f"Both LLMs failed: Primary - {e}, Fallback - {fallback_error}")
                    else:
                        logger.error("Rate limit hit but no fallback LLM available")
                        raise RuntimeError(f"Rate limit error and no fallback available: {e}")
                else:
                    logger.error(f"LLM invocation failed (non-rate-limit): {e}")
                    raise RuntimeError(f"LLM invocation failed: {e}")
        
        # Use fallback if primary is unavailable
        elif self.fallback_llm:
            logger.info("Primary LLM unavailable, using fallback LLM")
            self.using_fallback = True
            try:
                response = self.fallback_llm.invoke([HumanMessage(content=prompt)])
                return response.content
            except Exception as e:
                logger.error(f"Fallback LLM invocation failed: {e}")
                raise RuntimeError(f"Fallback LLM invocation failed: {e}")
        
        raise RuntimeError("No LLM available for invocation")
    
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
            "primary_model": config.groq_model if self.primary_llm else None,
            "fallback_available": self.fallback_llm is not None,
            "fallback_model": config.fallback_model if self.fallback_llm else None,
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
