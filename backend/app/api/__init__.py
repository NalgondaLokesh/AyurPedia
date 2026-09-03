"""
API module for AyurPedia.
Handles FastAPI route handlers.
"""

from .chat import router as chat_router
from .health import router as health_router
from .conversations import router as conversations_router
from .facilitator import router as facilitator_router
from .auth import router as auth_router
from .conversations_auth import router as conversations_auth_router
from .classify import router as classify_router
from .patent import router as patent_router

__all__ = [
    'chat_router',
    'health_router',
    'conversations_router',
    'facilitator_router',
    'auth_router',
    'conversations_auth_router',
    'classify_router',
    'patent_router'
]
