"""
Ingestion module for AyurPedia.
Provides document parsing, chunking, embedding, and loading functionality.
"""

from .parser import Parser
from .chunker import Chunker
from .embedder import Embedder
from .loader import DocumentLoader

__all__ = ['Parser', 'Chunker', 'Embedder', 'DocumentLoader']