"""
RAG module for AyurPedia.
Handles retrieval-augmented generation with citation enforcement.
"""

from .retriever import Retriever
from .chains import RAGChain
from .prompts import (
    CLASSIFICATION_PROMPT,
    RAG_PROMPT,
    VALIDATION_PROMPT,
    ABSTENTION_PROMPT
)

__all__ = [
    'Retriever',
    'RAGChain',
    'CLASSIFICATION_PROMPT',
    'RAG_PROMPT',
    'VALIDATION_PROMPT',
    'ABSTENTION_PROMPT'
]
