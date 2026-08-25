"""
Retriever module for AyurPedia.
Handles document retrieval from Qdrant vector database.
"""

import logging
from typing import List, Dict, Any, Optional
from ..core.database import QdrantDB
from ..core.llm import get_llm_client
from ..models.document import DocumentChunk


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Retriever:
    """Document retriever for RAG system."""
    
    def __init__(self, qdrant_db: QdrantDB, top_k: int = 5) -> None:
        """Initialize retriever with Qdrant database.
        
        Args:
            qdrant_db: QdrantDB instance for vector search
            top_k: Number of top results to retrieve
        """
        self.qdrant_db = qdrant_db
        self.top_k = top_k
        self.llm_client = get_llm_client()
        logger.info(f"Retriever initialized with top_k={top_k}")
    
    def search(self, query: str, jurisdiction: str = "India") -> List[DocumentChunk]:
        """Search for relevant documents based on jurisdiction.
        
        Args:
            query: Search query text
            jurisdiction: Jurisdiction to search (India, International, or Both)
            
        Returns:
            List of relevant DocumentChunk objects with similarity scores
        """
        logger.info(f"Searching for query: '{query}' in jurisdiction: {jurisdiction}")
        
        # Get embedding for query
        embedder = self.llm_client.get_embedding_model()
        if not embedder:
            logger.error("Embedding model not available")
            return []
        
        try:
            query_embedding = embedder.embed_query(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return []
        
        # Search based on jurisdiction
        if jurisdiction.lower() == "india":
            return self.search_india(query_embedding)
        elif jurisdiction.lower() == "international":
            return self.search_international(query_embedding)
        elif jurisdiction.lower() == "both":
            # Search both collections and combine results
            india_results = self.search_india(query_embedding)
            international_results = self.search_international(query_embedding)
            combined = india_results + international_results
            # Sort by score and return top_k
            combined.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
            return combined[:self.top_k]
        else:
            logger.warning(f"Unknown jurisdiction: {jurisdiction}, defaulting to India")
            return self.search_india(query_embedding)
    
    def search_india(self, query_embedding: List[float]) -> List[DocumentChunk]:
        """Search in India collection.
        
        Args:
            query_embedding: Query embedding vector
            
        Returns:
            List of relevant DocumentChunk objects
        """
        from ..core.config import get_config
        config = get_config()
        
        results = self.qdrant_db.search_similar(
            collection_name=config.india_collection,
            query_embedding=query_embedding,
            limit=self.top_k,
            score_threshold=0.25
        )
        
        return self.format_results(results, "India")
    
    def search_international(self, query_embedding: List[float]) -> List[DocumentChunk]:
        """Search in International collection.
        
        Args:
            query_embedding: Query embedding vector
            
        Returns:
            List of relevant DocumentChunk objects
        """
        from ..core.config import get_config
        config = get_config()
        
        results = self.qdrant_db.search_similar(
            collection_name=config.international_collection,
            query_embedding=query_embedding,
            limit=self.top_k,
            score_threshold=0.25
        )
        
        return self.format_results(results, "International")
    
    def format_results(self, results: List[Dict[str, Any]], jurisdiction: str) -> List[DocumentChunk]:
        """Format Qdrant results into DocumentChunk objects.
        
        Args:
            results: Raw Qdrant search results
            jurisdiction: Jurisdiction of the results
            
        Returns:
            List of formatted DocumentChunk objects
        """
        formatted_chunks = []
        
        for result in results:
            payload = result.get('payload', {})
            chunk = DocumentChunk(
                text=payload.get('text', ''),
                metadata={
                    'source': payload.get('source', ''),
                    'section': payload.get('section', ''),
                    'jurisdiction': payload.get('jurisdiction', jurisdiction),
                    'year': payload.get('year', 0),
                    'chunk_id': payload.get('chunk_id', ''),
                    'document_type': payload.get('document_type', ''),
                    'file_name': payload.get('file_name', ''),
                    'score': result.get('score', 0.0)
                }
            )
            formatted_chunks.append(chunk)
        
        logger.info(f"Formatted {len(formatted_chunks)} chunks from {jurisdiction} collection")
        return formatted_chunks
