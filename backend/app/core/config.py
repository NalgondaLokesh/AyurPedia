"""
Configuration module for AyurPedia.
Loads and validates environment variables from .env file.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for AyurPedia application settings."""
    
    def __init__(self) -> None:
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self._validate_required_vars()
        self._print_config()
    
    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are set."""
        required_vars = [
            'LLAMAPARSE_API_KEY',
            'COHERE_API_KEY',
            'QDRANT_URL',
            'QDRANT_API_KEY',
            'GROQ_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please set them in your .env file."
            )
    
    @property
    def llamaparse_api_key(self) -> str:
        """Get LlamaParse API key."""
        return os.getenv('LLAMAPARSE_API_KEY', '')
    
    @property
    def cohere_api_key(self) -> str:
        """Get Cohere API key."""
        return os.getenv('COHERE_API_KEY', '')
    
    @property
    def qdrant_url(self) -> str:
        """Get Qdrant cloud URL."""
        return os.getenv('QDRANT_URL', '')
    
    @property
    def qdrant_api_key(self) -> str:
        """Get Qdrant API key."""
        return os.getenv('QDRANT_API_KEY', '')
    
    @property
    def parent_chunk_size(self) -> int:
        """Get parent chunk size for hierarchical chunking."""
        return int(os.getenv('PARENT_CHUNK_SIZE', '2000'))
    
    @property
    def child_chunk_size(self) -> int:
        """Get child chunk size for hierarchical chunking."""
        return int(os.getenv('CHILD_CHUNK_SIZE', '400'))
    
    @property
    def chunk_overlap(self) -> int:
        """Get chunk overlap for text splitting."""
        return int(os.getenv('CHUNK_OVERLAP', '100'))
    
    @property
    def parent_overlap(self) -> int:
        """Get parent chunk overlap for hierarchical chunking."""
        return int(os.getenv('PARENT_OVERLAP', '200'))
    
    @property
    def chunk_size(self) -> int:
        """Get chunk size for text splitting (legacy, kept for compatibility)."""
        return int(os.getenv('CHUNK_SIZE', '800'))
    
    @property
    def batch_size(self) -> int:
        """Get batch size for embedding generation."""
        return int(os.getenv('BATCH_SIZE', '100'))
    
    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension for Cohere embed-english-v3.0."""
        return 1024
    
    @property
    def india_collection(self) -> str:
        """Get India collection name."""
        return 'india_corpus'
    
    @property
    def international_collection(self) -> str:
        """Get International collection name."""
        return 'international_corpus'
    
    @property
    def gemini_api_key(self) -> str:
        """Get Gemini API key."""
        return os.getenv('GEMINI_API_KEY', '')
    
    @property
    def gemini_model(self) -> str:
        """Get Gemini model name."""
        return os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    
    @property
    def groq_api_key(self) -> str:
        """Get Groq API key."""
        return os.getenv('GROQ_API_KEY', '')
    
    @property
    def groq_model(self) -> str:
        """Get Groq model name."""
        return os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    @property
    def nvidia_nim_api_key(self) -> str:
        """Get NVIDIA NIM API key."""
        return os.getenv('NVIDIA_NIM_API_KEY', '')
    
    @property
    def nvidia_nim_base_url(self) -> str:
        """Get NVIDIA NIM base URL."""
        return os.getenv('NVIDIA_NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    
    @property
    def fallback_model(self) -> str:
        """Get fallback model name."""
        return os.getenv('FALLBACK_MODEL', 'deepseek-ai/deepseek-v4-flash-0731')
    
    @property
    def top_k_results(self) -> int:
        """Get top-k results for retrieval."""
        return int(os.getenv('TOP_K_RESULTS', '15'))
    
    @property
    def confidence_threshold(self) -> float:
        """Get confidence threshold for responses."""
        return float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
    
    @property
    def mongodb_uri(self) -> str:
        """Get MongoDB Atlas connection string."""
        return os.getenv('MONGODB_URI', '')
    
    @property
    def mongodb_db_name(self) -> str:
        """Get MongoDB database name."""
        return os.getenv('MONGODB_DB_NAME', 'ayurpedia')
    
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key for token generation."""
        return os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    @property
    def jwt_algorithm(self) -> str:
        """Get JWT algorithm."""
        return os.getenv('JWT_ALGORITHM', 'HS256')
    
    @property
    def jwt_access_token_expire_minutes(self) -> int:
        """Get JWT access token expiration in minutes."""
        return int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    @property
    def jwt_refresh_token_expire_days(self) -> int:
        """Get JWT refresh token expiration in days."""
        return int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    @property
    def sentry_dsn(self) -> str:
        """Get Sentry DSN for error tracking."""
        return os.getenv('SENTRY_DSN', '')
    
    @property
    def rate_limit_per_minute(self) -> int:
        """Get rate limit per minute."""
        return int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    @property
    def frontend_url(self) -> str:
        """Get frontend URL for CORS."""
        return os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    @property
    def neo4j_uri(self) -> str:
        """Get Neo4j connection URI."""
        return os.getenv('NEO4J_URI', 'neo4j+s://localhost:7687')
    
    @property
    def neo4j_user(self) -> str:
        """Get Neo4j username."""
        return os.getenv('NEO4J_USER', 'neo4j')
    
    @property
    def neo4j_password(self) -> str:
        """Get Neo4j password."""
        return os.getenv('NEO4J_PASSWORD', 'password')
    
    def _print_config(self) -> None:
        """Log loaded configuration for debugging (without exposing keys)."""
        logger.debug("Configuration loaded successfully:")
        logger.debug(f"  - LlamaParse API Key: {'*' * 20 if self.llamaparse_api_key else 'NOT SET'}")
        logger.debug(f"  - Cohere API Key: {'*' * 20 if self.cohere_api_key else 'NOT SET'}")
        logger.debug(f"  - Groq API Key: {'*' * 20 if self.groq_api_key else 'NOT SET'}")
        logger.debug(f"  - Groq Model: {self.groq_model}")
        logger.debug(f"  - Gemini API Key: {'*' * 20 if self.gemini_api_key else 'NOT SET'}")
        logger.debug(f"  - Gemini Model: {self.gemini_model}")
        logger.debug(f"  - NVIDIA NIM API Key: {'*' * 20 if self.nvidia_nim_api_key else 'NOT SET'}")
        logger.debug(f"  - NVIDIA NIM Base URL: {self.nvidia_nim_base_url}")
        logger.debug(f"  - Fallback Model: {self.fallback_model}")
        logger.debug(f"  - Qdrant URL: {self.qdrant_url[:30]}...{self.qdrant_url[-10:] if len(self.qdrant_url) > 40 else self.qdrant_url}")
        logger.debug(f"  - Qdrant API Key: {'*' * 20 if self.qdrant_api_key else 'NOT SET'}")
        logger.debug(f"  - MongoDB URI: {'*' * 20 if self.mongodb_uri else 'NOT SET (In-memory fallback)'}")
        logger.debug(f"  - MongoDB DB Name: {self.mongodb_db_name}")
        logger.debug(f"  - Chunk Size: {self.chunk_size}")
        logger.debug(f"  - Chunk Overlap: {self.chunk_overlap}")
        logger.debug(f"  - Batch Size: {self.batch_size}")
        logger.debug(f"  - Embedding Dimension: {self.embedding_dimension}")
        logger.debug(f"  - Top K Results: {self.top_k_results}")
        logger.debug(f"  - Confidence Threshold: {self.confidence_threshold}")
        logger.debug(f"  - India Collection: {self.india_collection}")
        logger.debug(f"  - International Collection: {self.international_collection}")
        logger.debug(f"  - Neo4j URI: {self.neo4j_uri}")
        logger.debug(f"  - Neo4j User: {self.neo4j_user}")
        logger.debug(f"  - Neo4j Password: {'*' * 10 if self.neo4j_password else 'NOT SET'}")


# Global configuration instance (lazy loaded)
_config = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config