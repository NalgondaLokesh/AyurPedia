"""
API module for AyurPedia.
Handles FastAPI route handlers.
"""

from .chat import router as chat_router
from .classify import router as classify_router
from .health import router as health_router

__all__ = ['chat_router', 'classify_router', 'health_router']
