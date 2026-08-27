"""
AyurPedia Application Package.
Main application package for the AyurPedia backend.
"""

__version__ = "2.0.0"
__author__ = "AyurPedia Team"

# Initialize package modules
from app.core import config, database, llm
from app.rag import retriever, chains, prompts
from app.models import chat
from app.services import chat_service
from app.api import chat, health