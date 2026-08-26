"""
Configuration module for AyurPedia.
Loads and validates environment variables from .env file.
"""

import os
from dotenv import load_dotenv


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
            'GEMINI_API_KEY'
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
    def chunk_size(self) -> int:
        """Get chunk size for text splitting."""
        return int(os.getenv('CHUNK_SIZE', '1000'))
    
    @property
    def chunk_overlap(self) -> int:
        """Get chunk overlap for text splitting."""
        return int(os.getenv('CHUNK_OVERLAP', '200'))
    
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
    def nvidia_nim_api_key(self) -> str:
        """Get NVIDIA NIM API key."""
        return os.getenv('NVIDIA_NIM_API_KEY', '')
    
    @property
    def nvidia_nim_base_url(self) -> str:
        """Get NVIDIA NIM base URL."""
        return os.getenv('NVIDIA_NIM_BASE_URL', 'https://api.nvidia.com/v1')
    
    @property
    def fallback_model(self) -> str:
        """Get fallback model name."""
        return os.getenv('FALLBACK_MODEL', 'deepseek-ai/deepseek-v4-flash-0731')
    
    @property
    def top_k_results(self) -> int:
        """Get top-k results for retrieval."""
        return int(os.getenv('TOP_K_RESULTS', '5'))
    
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
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        return os.getenv('REDIS_URL', 'redis://localhost:6379')
    
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
    
    def _print_config(self) -> None:
        """Print loaded configuration for debugging (without exposing keys)."""
        print("Configuration loaded successfully:")
        print(f"  - LlamaParse API Key: {'*' * 20 if self.llamaparse_api_key else 'NOT SET'}")
        print(f"  - Cohere API Key: {'*' * 20 if self.cohere_api_key else 'NOT SET'}")
        print(f"  - Gemini API Key: {'*' * 20 if self.gemini_api_key else 'NOT SET'}")
        print(f"  - Gemini Model: {self.gemini_model}")
        print(f"  - NVIDIA NIM API Key: {'*' * 20 if self.nvidia_nim_api_key else 'NOT SET'}")
        print(f"  - NVIDIA NIM Base URL: {self.nvidia_nim_base_url}")
        print(f"  - Fallback Model: {self.fallback_model}")
        print(f"  - Qdrant URL: {self.qdrant_url[:30]}...{self.qdrant_url[-10:] if len(self.qdrant_url) > 40 else self.qdrant_url}")
        print(f"  - Qdrant API Key: {'*' * 20 if self.qdrant_api_key else 'NOT SET'}")
        print(f"  - MongoDB URI: {'*' * 20 if self.mongodb_uri else 'NOT SET (In-memory fallback)'}")
        print(f"  - MongoDB DB Name: {self.mongodb_db_name}")
        print(f"  - Chunk Size: {self.chunk_size}")
        print(f"  - Chunk Overlap: {self.chunk_overlap}")
        print(f"  - Batch Size: {self.batch_size}")
        print(f"  - Embedding Dimension: {self.embedding_dimension}")
        print(f"  - Top K Results: {self.top_k_results}")
        print(f"  - Confidence Threshold: {self.confidence_threshold}")
        print(f"  - India Collection: {self.india_collection}")
        print(f"  - International Collection: {self.international_collection}")


# Global configuration instance (lazy loaded)
_config = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config