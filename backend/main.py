"""
FastAPI entry point for AyurPedia Phase 2 Backend.
Handles API initialization and server startup.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import get_config
from app.core.database import QdrantDB
from app.core.llm import get_llm_client
from app.core.mongodb import get_mongodb
from app.core.redis import get_redis
from app.core.rate_limit import get_rate_limiter
from app.core.sentry import init_sentry
from app.rag.retriever import Retriever
from app.rag.chains import RAGChain
from app.graph.classification import ClassificationNode
from app.api.chat import set_chat_service
from app.api.classify import set_classification_service
from app.api import chat_router, classify_router, health_router, conversations_router, facilitator_router, auth_router, conversations_auth_router
from app.services.chat_service import ChatService
from app.services.classification_service import ClassificationService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
config = None
qdrant_db = None
llm_client = None
retriever = None
rag_chain = None
classification_node = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events.
    
    Args:
        app: FastAPI application instance
    """
    global config, qdrant_db, llm_client, retriever, rag_chain, classification_node
    
    # Startup
    logger.info("Starting AyurPedia Phase 2 Backend...")
    print("\n" + "=" * 60)
    print("Starting AyurPedia Phase 2 Backend...")
    print("=" * 60 + "\n")
    
    try:
        # Load configuration
        config = get_config()
        print("[OK] Configuration loaded")
        
        # Initialize Sentry
        init_sentry()

        # Initialize MongoDB
        mongo = get_mongodb()
        mongo_ok = await mongo.connect()
        if mongo_ok:
            print(f"[OK] MongoDB Atlas connected ({config.mongodb_db_name})")
        else:
            print("[OK] MongoDB (in-memory mode ready)")
        
        # Initialize Redis
        redis_client = get_redis()
        redis_ok = await redis_client.connect()
        if redis_ok:
            print("[OK] Redis connected (caching enabled)")
        else:
            print("[OK] Redis (running without caching)")
        
        # Initialize Qdrant database
        qdrant_db = QdrantDB(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            embedding_dimension=config.embedding_dimension
        )
        
        # Check Qdrant collections
        india_info = qdrant_db.get_collection_info(config.india_collection)
        international_info = qdrant_db.get_collection_info(config.international_collection)
        
        india_count = india_info["points_count"] if india_info else 0
        international_count = international_info["points_count"] if international_info else 0
        
        print(f"[OK] Qdrant connected: {config.india_collection} ({india_count} vectors), "
              f"{config.international_collection} ({international_count} vectors)")
        
        # Initialize LLM client
        llm_client = get_llm_client()
        print(f"[OK] Gemini LLM initialized ({config.gemini_model})")
        
        # Initialize retriever
        retriever = Retriever(qdrant_db, top_k=config.top_k_results)
        print(f"[OK] Retriever initialized (top_k={config.top_k_results})")
        
        # Initialize RAG chain
        rag_chain = RAGChain(llm_client.get_llm_with_fallback(), retriever)
        print("[OK] RAG chain created")
        
        # Initialize classification node
        classification_node = ClassificationNode(llm_client.get_llm_with_fallback())
        print("[OK] Classification node created")
        
        # Initialize services
        chat_service = ChatService(rag_chain)
        classification_service = ClassificationService(classification_node)
        
        # Set services in API modules
        set_chat_service(chat_service)
        set_classification_service(classification_service)
        
        print("\nAPI Endpoints:")
        print("  POST /api/classify             - Formulation classification")
        print("  POST /api/chat                 - AI assistant chat with citations")
        print("  GET  /api/conversations        - List session history")
        print("  GET  /api/conversations/{id}   - Fetch session messages")
        print("  POST /api/facilitator/request  - Submit human facilitator ticket")
        print("  GET  /api/health               - Service health check")
        print("  POST /api/auth/register        - User registration")
        print("  POST /api/auth/login           - User login")
        print("  GET  /api/auth/me              - Get current user")
        
        print(f"\n[OK] FastAPI server starting at http://localhost:8000")
        print("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        print(f"[ERROR] Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AyurPedia Phase 2 Backend...")
    await get_mongodb().close()
    await get_redis().close()
    print("\nShutting down AyurPedia Phase 2 Backend...")


# Create FastAPI application
app = FastAPI(
    title="AyurPedia API",
    description="RAG-based legal assistant for IP and traditional knowledge with MongoDB persistence",
    version="2.0.0",
    lifespan=lifespan
)

# Add rate limiting middleware
rate_limiter = get_rate_limiter()
app.middleware("http")(rate_limiter)

# Add CORS middleware (will be updated after config loads)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be updated in lifespan
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,
)

# Include routers
app.include_router(chat_router)
app.include_router(classify_router)
app.include_router(health_router)
app.include_router(conversations_router)
app.include_router(facilitator_router)
app.include_router(auth_router, prefix="/api")
app.include_router(conversations_auth_router, prefix="/api")


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions.
    
    Args:
        request: Request instance
        exc: HTTPException instance
        
    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions.
    
    Args:
        request: Request instance
        exc: Exception instance
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AyurPedia API",
        "version": "2.0.0",
        "description": "RAG-based legal assistant for IP and traditional knowledge",
        "endpoints": {
            "health": "/api/health",
            "classify": "/api/classify",
            "chat": "/api/chat"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )