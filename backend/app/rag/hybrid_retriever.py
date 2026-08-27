"""
Hybrid retriever combining semantic and keyword search for improved precision and recall.
"""

import logging
from typing import List, Dict, Any, Optional
import cohere
from ..core.database import QdrantDB
from ..core.llm import get_llm_client
from ..core.config import get_config
from ..models.document import DocumentChunk


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retriever combining semantic vector search with keyword matching."""
    
    def __init__(self, qdrant_db: QdrantDB, top_k: int = 5, use_rerank: bool = True) -> None:
        """Initialize hybrid retriever.
        
        Args:
            qdrant_db: QdrantDB instance for vector search
            top_k: Number of top results to retrieve
            use_rerank: Whether to use Cohere rerank API
        """
        self.qdrant_db = qdrant_db
        self.top_k = top_k
        self.llm_client = get_llm_client()
        self.semantic_weight = 0.5  # Weight for semantic search (reduced for better precision)
        self.keyword_weight = 0.5   # Weight for keyword search (increased for legal terminology)
        self.use_rerank = use_rerank
        
        # Initialize Cohere client for reranking
        config = get_config()
        if self.use_rerank and config.cohere_api_key:
            try:
                self.cohere_client = cohere.Client(config.cohere_api_key)
                logger.info("Cohere rerank client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere client: {e}. Reranking disabled.")
                self.use_rerank = False
                self.cohere_client = None
        else:
            self.cohere_client = None
            if self.use_rerank:
                logger.warning("Cohere API key not found. Reranking disabled.")
        
        logger.info(f"HybridRetriever initialized (semantic: {self.semantic_weight}, keyword: {self.keyword_weight}, rerank: {self.use_rerank})")
    
    def search(self, query: str, jurisdiction: str = "India", use_hierarchical: bool = True) -> List[DocumentChunk]:
        """Hybrid search combining semantic and keyword approaches with hierarchical retrieval.
        
        Args:
            query: Search query text
            jurisdiction: Jurisdiction to search
            use_hierarchical: Whether to use parent-child hierarchical retrieval
            
        Returns:
            List of relevant DocumentChunk objects with combined scores
        """
        logger.info(f"Hybrid search for query: '{query}' in jurisdiction: {jurisdiction}")
        
        # Get embedding for semantic search
        embedder = self.llm_client.get_embedding_model()
        if not embedder:
            logger.error("Embedding model not available")
            return []
        
        try:
            query_embedding = embedder.embed_query(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return []
        
        # Perform both searches
        semantic_results = self._semantic_search(query_embedding, jurisdiction)
        keyword_results = self._keyword_search(query, jurisdiction)
        
        # Combine and re-rank results
        combined_results = self._combine_results(semantic_results, keyword_results)
        
        # Apply Cohere rerank if enabled (before formatting to DocumentChunk)
        if self.use_rerank and self.cohere_client and len(combined_results) > 1:
            # Rerank the raw Dict results before formatting
            raw_results = combined_results
            combined_results = self._cohere_rerank(query, raw_results)
        
        # Format results to DocumentChunk
        formatted_results = self._format_results(combined_results, jurisdiction)
        
        # Apply hierarchical retrieval if enabled
        if use_hierarchical:
            formatted_results = self._apply_hierarchical_retrieval(formatted_results)
        
        logger.info(f"Hybrid search found {len(formatted_results)} results")
        return formatted_results[:self.top_k]
    
    def _apply_hierarchical_retrieval(self, results: List[DocumentChunk]) -> List[DocumentChunk]:
        """Apply hierarchical retrieval: search child chunks, return parent chunks.
        
        Args:
            results: Search results from hybrid search
            
        Returns:
            List of parent DocumentChunk objects with context
        """
        from .hierarchical import expand_to_parents
        from ..core.config import get_config
        
        config = get_config()
        
        # Determine collection name from jurisdiction context
        # For now, default to India collection - could be improved by passing jurisdiction
        collection_name = config.india_collection
        
        # Use the shared hierarchical helper to expand children to parents
        parents = expand_to_parents(
            child_chunks=results,
            qdrant_db=self.qdrant_db,
            collection_name=collection_name,
            fail_open=True
        )
        
        return parents[:self.top_k]
    
    def _semantic_search(self, query_embedding: List[float], jurisdiction: str) -> List[Dict]:
        """Perform semantic vector search.
        
        Args:
            query_embedding: Query embedding vector
            jurisdiction: Jurisdiction to search
            
        Returns:
            List of semantic search results with scores
        """
        from ..core.config import get_config
        config = get_config()
        
        collection_name = config.india_collection if jurisdiction.lower() == "india" else config.international_collection
        
        # Get more results for better combination
        results = self.qdrant_db.search_similar(
            collection_name=collection_name,
            query_embedding=query_embedding,
            limit=self.top_k * 2,
            score_threshold=0.15
        )
        
        # Normalize scores to 0-1 range
        max_score = max([r.get('score', 0) for r in results]) if results else 1.0
        for result in results:
            result['semantic_score'] = result.get('score', 0) / max_score if max_score > 0 else 0
            result['keyword_score'] = 0.0  # Will be updated in combination
        
        return results
    
    def _keyword_search(self, query: str, jurisdiction: str) -> Dict[str, float]:
        """Perform keyword-based search using exact matching.
        
        Args:
            query: Search query text
            jurisdiction: Jurisdiction to search
            
        Returns:
            Dictionary mapping document IDs to keyword scores
        """
        from ..core.config import get_config
        config = get_config()
        
        collection_name = config.india_collection if jurisdiction.lower() == "india" else config.international_collection
        
        # Extract key terms from query
        key_terms = self._extract_key_terms(query)
        logger.info(f"Extracted key terms: {key_terms}")
        
        if not key_terms:
            return {}
        
        # Build keyword filter for Qdrant
        # This is a simplified approach - in production, you'd use Qdrant's filtering capabilities
        keyword_scores = {}
        
        # Get all documents from collection (limit for performance)
        try:
            all_docs = self.qdrant_db.search_similar(
                collection_name=collection_name,
                query_embedding=[0.0] * 1024,  # Dummy embedding
                limit=100,  # Reasonable limit for keyword matching
                score_threshold=0.0  # Get all documents
            )
            
            for doc in all_docs:
                payload = doc.get('payload', {})
                text = payload.get('text', '').lower()
                doc_id = payload.get('chunk_id', '')
                
                # Calculate keyword match score
                keyword_score = self._calculate_keyword_score(text, key_terms)
                if keyword_score > 0:
                    keyword_scores[doc_id] = keyword_score
            
        except Exception as e:
            logger.warning(f"Keyword search failed: {e}")
        
        return keyword_scores
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract important key terms from query.
        
        Args:
            query: Search query text
            
        Returns:
            List of key terms
        """
        # Legal domain-specific terms to prioritize
        legal_terms = {
            'section', 'act', 'patent', 'traditional', 'knowledge', 'ayurvedic',
            'formulation', 'herbal', 'medicine', 'drug', 'regulatory', 'compliance',
            'novelty', 'prior art', 'inventive', 'industrial', 'application',
            'biological', 'diversity', 'authority', 'fssai', 'wipo', 'gratk'
        }
        
        # Extract terms
        words = query.lower().split()
        key_terms = []
        
        for word in words:
            # Prioritize legal terms
            if word in legal_terms:
                key_terms.append(word)
            # Include longer words (likely more specific)
            elif len(word) > 4:
                key_terms.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:10]  # Limit to top 10 terms
    
    def _calculate_keyword_score(self, text: str, key_terms: List[str]) -> float:
        """Calculate keyword match score.
        
        Args:
            text: Document text
            key_terms: List of key terms to match
            
        Returns:
            Keyword match score (0-1)
        """
        if not key_terms:
            return 0.0
        
        matches = 0
        for term in key_terms:
            if term in text:
                matches += 1
        
        # Score based on term coverage
        score = matches / len(key_terms)
        
        # Boost score for exact phrase matches
        text_lower = text.lower()
        for i in range(len(key_terms)):
            phrase = ' '.join(key_terms[i:i+2])  # Check 2-word phrases
            if phrase in text_lower:
                score += 0.2
        
        return min(score, 1.0)
    
    def _combine_results(self, semantic_results: List[Dict], keyword_scores: Dict[str, float]) -> List[Dict]:
        """Combine semantic and keyword results with weighted scoring.
        
        Args:
            semantic_results: Results from semantic search
            keyword_scores: Results from keyword search
            
        Returns:
            Combined and re-ranked results (as Dict, not DocumentChunk)
        """
        combined = []
        
        for result in semantic_results:
            payload = result.get('payload', {})
            chunk_id = payload.get('chunk_id', '')
            
            # Get scores from both methods
            semantic_score = result.get('semantic_score', 0.0)
            keyword_score = keyword_scores.get(chunk_id, 0.0)
            
            # Calculate combined score
            combined_score = (
                self.semantic_weight * semantic_score +
                self.keyword_weight * keyword_score
            )
            
            # Update result with combined score
            result['combined_score'] = combined_score
            result['keyword_score'] = keyword_score
            combined.append(result)
        
        # Sort by combined score
        combined.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        
        return combined
    
    def _format_results(self, results: List[Dict], jurisdiction: str = "India") -> List[DocumentChunk]:
        """Format raw Dict results into DocumentChunk objects.
        
        Args:
            results: Raw search results (Dict format)
            jurisdiction: Jurisdiction of the results
            
        Returns:
            Formatted DocumentChunk objects
        """
        from ..core.config import get_config
        config = get_config()
        
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
                    'score': result.get('combined_score', result.get('score', 0.0)),
                    'semantic_score': result.get('semantic_score', 0.0),
                    'keyword_score': result.get('keyword_score', 0.0),
                    'rerank_score': result.get('rerank_score', None)
                },
                parent_id=payload.get('parent_id', ''),
                child_ids=payload.get('child_ids', []),
                chunk_type=payload.get('chunk_type', 'standard')
            )
            formatted_chunks.append(chunk)
        
        return formatted_chunks
    
    def update_weights(self, semantic_weight: float, keyword_weight: float) -> None:
        """Update the weights for semantic and keyword search.
        
        Args:
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
        """
        total = semantic_weight + keyword_weight
        if total != 1.0:
            # Normalize weights
            semantic_weight = semantic_weight / total
            keyword_weight = keyword_weight / total
        
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        logger.info(f"Updated weights - semantic: {self.semantic_weight}, keyword: {self.keyword_weight}")
    
    def _cohere_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Re-rank results using Cohere rerank API.
        
        Args:
            query: Original search query
            results: Results to re-rank
            
        Returns:
            Re-ranked results
        """
        try:
            # Extract documents for reranking
            documents = [r['payload']['text'] for r in results]
            
            # Limit to top 20 for efficiency
            documents = documents[:20]
            results_subset = results[:20]
            
            # Call Cohere rerank API
            rerank_response = self.cohere_client.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=min(self.top_k * 2, len(documents))
            )
            
            # Reorder results based on rerank scores
            reranked_indices = [result.index for result in rerank_response.results]
            reranked_results = [results_subset[i] for i in reranked_indices]
            
            # Add rerank scores to metadata
            for i, result in enumerate(rerank_response.results):
                reranked_results[i]['rerank_score'] = result.relevance_score
            
            logger.info(f"Cohere rerank completed: {len(reranked_results)} results re-ranked")
            return reranked_results
            
        except Exception as e:
            logger.warning(f"Cohere rerank failed: {e}. Returning original results.")
            return results