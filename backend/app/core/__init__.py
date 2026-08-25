"""
Core module for AyurPedia.
Provides configuration and database functionality.
"""

from .config import Config, get_config
from .database import QdrantDB

__all__ = ['Config', 'get_config', 'QdrantDB']