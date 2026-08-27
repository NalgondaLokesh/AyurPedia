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
    
    def search(self, query: str, jurisdiction: str = "India", use_hierarchical: bool = True) -> List[DocumentChunk]:
        """Search for relevant documents based on jurisdiction with hierarchical retrieval.
        
        Args:
            query: Search query text
            jurisdiction: Jurisdiction to search (India, International, or Both)
            use_hierarchical: Whether to use parent-child hierarchical retrieval
            
        Returns:
            List of relevant DocumentChunk objects with similarity scores
        """
        logger.info(f"Searching for query: '{query}' in jurisdiction: {jurisdiction}")
        
        # Expand query with legal terms for better retrieval
        expanded_query = self._expand_query(query)
        logger.info(f"Expanded query: '{expanded_query}'")
        
        # Get embedding for query
        embedder = self.llm_client.get_embedding_model()
        if not embedder:
            logger.error("Embedding model not available")
            return []
        
        try:
            query_embedding = embedder.embed_query(expanded_query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return []
        
        # Search based on jurisdiction
        if jurisdiction.lower() == "india":
            raw_results = self.search_india(query_embedding)
        elif jurisdiction.lower() == "international":
            raw_results = self.search_international(query_embedding)
        elif jurisdiction.lower() == "both":
            # Search both collections and combine results
            india_results = self.search_india(query_embedding)
            international_results = self.search_international(query_embedding)
            combined = india_results + international_results
            # Sort by score and return top_k
            combined.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
            raw_results = combined[:self.top_k * 3]  # Get more for hierarchical processing
        else:
            logger.warning(f"Unknown jurisdiction: {jurisdiction}, defaulting to India")
            raw_results = self.search_india(query_embedding)
        
        # Apply hierarchical retrieval if enabled
        if use_hierarchical:
            return self.apply_hierarchical_retrieval(raw_results)
        else:
            return raw_results[:self.top_k]
    
    def search_india(self, query_embedding: List[float]) -> List[DocumentChunk]:
        """Search in India collection.
        
        Args:
            query_embedding: Query embedding vector
            
        Returns:
            List of relevant DocumentChunk objects
        """
        from ..core.config import get_config
        config = get_config()
        
        # Try with lower threshold first, then filter results
        results = self.qdrant_db.search_similar(
            collection_name=config.india_collection,
            query_embedding=query_embedding,
            limit=self.top_k * 3,  # Get more candidates for better recall
            score_threshold=0.10  # Lower threshold to get more candidates
        )
        
        # Filter by score and apply relevance boosting
        filtered_results = self._filter_and_boost(results)
        
        return self.format_results(filtered_results[:self.top_k], "India")
    
    def search_international(self, query_embedding: List[float]) -> List[DocumentChunk]:
        """Search in International collection.
        
        Args:
            query_embedding: Query embedding vector
            
        Returns:
            List of relevant DocumentChunk objects
        """
        from ..core.config import get_config
        config = get_config()
        
        # Try with lower threshold first, then filter results
        results = self.qdrant_db.search_similar(
            collection_name=config.international_collection,
            query_embedding=query_embedding,
            limit=self.top_k * 3,  # Get more candidates for better recall
            score_threshold=0.10  # Lower threshold to get more candidates
        )
        
        # Filter by score and apply relevance boosting
        filtered_results = self._filter_and_boost(results)
        
        return self.format_results(filtered_results[:self.top_k], "International")
    
    def _filter_and_boost(self, results: List[Dict]) -> List[Dict]:
        """Filter results and apply relevance boosting for better precision.
        
        Args:
            results: Raw Qdrant search results
            
        Returns:
            Filtered and boosted results
        """
        if not results:
            return []
        
        boosted_results = []
        
        for result in results:
            payload = result.get('payload', {})
            text = payload.get('text', '').lower()
            score = result.get('score', 0.0)
            
            # Base filtering - minimum score threshold
            if score < 0.15:
                continue
            
            # Boost factors for precision
            boost = 1.0
            
            # Boost if text contains legal section numbers (e.g., "section 3(p)")
            if 'section' in text and any(char.isdigit() for char in text):
                boost += 0.1
            
            # Boost if text contains legal acts/regulations
            legal_sources = ['patents act', 'biological diversity', 'fssai', 'wipo', 'trips', 'nagoya']
            if any(source in text for source in legal_sources):
                boost += 0.15
            
            # Boost if text contains key legal terms
            key_terms = ['patentability', 'novelty', 'prior art', 'inventive step', 'traditional knowledge']
            if any(term in text for term in key_terms):
                boost += 0.1
            
            # Apply boost to score
            result['boosted_score'] = min(score * boost, 1.0)
            boosted_results.append(result)
        
        # Sort by boosted score for better precision
        boosted_results.sort(key=lambda x: x.get('boosted_score', 0), reverse=True)
        
        return boosted_results
    
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
                },
                parent_id=payload.get('parent_id', ''),
                child_ids=payload.get('child_ids', []),
                chunk_type=payload.get('chunk_type', 'standard')
            )
            formatted_chunks.append(chunk)
        
        logger.info(f"Formatted {len(formatted_chunks)} chunks from {jurisdiction} collection")
        return formatted_chunks
    
    def apply_hierarchical_retrieval(self, raw_results: List[DocumentChunk]) -> List[DocumentChunk]:
        """Apply hierarchical retrieval: search child chunks, return parent chunks.
        
        Args:
            raw_results: Raw search results from vector database
            
        Returns:
            List of parent DocumentChunk objects with context
        """
        from .hierarchical import expand_to_parents
        from ..core.config import get_config
        
        config = get_config()
        
        # Use the shared hierarchical helper to expand children to parents
        parents = expand_to_parents(
            child_chunks=raw_results,
            qdrant_db=self.qdrant_db,
            collection_name=config.india_collection,  # Will need to determine from context
            fail_open=True
        )
        
        return parents[:self.top_k]
    
    def _retrieve_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        """Retrieve chunks by their IDs from Qdrant.
        
        Args:
            chunk_ids: List of chunk IDs to retrieve
            
        Returns:
            List of DocumentChunk objects
        """
        from ..core.config import get_config
        config = get_config()
        
        # For now, implement a simple filter-based retrieval
        # In production, you'd want to use Qdrant's point retrieval API
        all_chunks = []
        
        # Search in both collections
        for collection_name in [config.india_collection, config.international_collection]:
            try:
                # Get all points and filter by ID (inefficient but works for now)
                results = self.qdrant_db.client.scroll(
                    collection_name=collection_name,
                    limit=1000,  # Adjust based on your collection size
                    with_payload=True,
                    with_vectors=False
                )
                
                for point in results[0]:
                    if str(point.id) in chunk_ids:
                        chunk = self._qdrant_point_to_chunk(point)
                        all_chunks.append(chunk)
            except Exception as e:
                logger.warning(f"Failed to retrieve chunks from {collection_name}: {e}")
        
        return all_chunks
    
    def _qdrant_point_to_chunk(self, point) -> DocumentChunk:
        """Convert Qdrant point to DocumentChunk.
        
        Args:
            point: Qdrant point object
            
        Returns:
            DocumentChunk object
        """
        payload = point.payload
        return DocumentChunk(
            id=str(point.id),
            text=payload.get('text', ''),
            metadata={
                'source': payload.get('source', ''),
                'section': payload.get('section', ''),
                'jurisdiction': payload.get('jurisdiction', ''),
                'year': payload.get('year', 0),
                'chunk_id': payload.get('chunk_id', ''),
                'document_type': payload.get('document_type', ''),
                'file_name': payload.get('file_name', ''),
                'score': 0.0  # Will be set by retrieval method
            },
            parent_id=payload.get('parent_id', ''),
            child_ids=payload.get('child_ids', []),
            chunk_type=payload.get('chunk_type', 'standard')
        )
    
    def _expand_query(self, query: str) -> str:
        """Expand query with legal terms for better retrieval.
        
        Args:
            query: Original query
            
        Returns:
            Expanded query with relevant legal terms
        """
        # Enhanced legal term expansions for Ayurvedic IPR domain
        term_expansions = {
            "section 3(p)": "section 3(p) traditional knowledge patentability novelty prior art inventive step non-patentable subject matter",
            "3(p)": "section 3(p) traditional knowledge patentability novelty prior art inventive step",
            "patent": "patent intellectual property invention claims novelty prior art inventive step industrial application patentability",
            "ayurvedic": "ayurvedic traditional medicine herbal formulation classical knowledge ancient texts pharmacopoeia",
            "formulation": "formulation preparation medicine drug herbal ayurvedic composition ingredients dosage",
            "fssai": "fssai food safety authority ayurveda aahar nutraceutical regulation schedule a food products",
            "nba": "national biodiversity authority biological diversity act benefit sharing traditional knowledge access genetic resources",
            "wipo": "wipo world intellectual property organization gratk genetic resources traditional knowledge patent law international treaty",
            "traditional knowledge": "traditional knowledge tk prior art indigenous community folklore cultural heritage oral traditions",
            "classification": "classification category regulatory ayurveda aahar cosmetic phytopharmaceutical nutraceutical proprietary classical",
            "prior art": "prior art existing knowledge novelty anticipation public disclosure state of the art",
            "novelty": "novelty new invention inventive step non-obviousness patentable subject matter",
            "biological diversity": "biological diversity act 2002 benefit sharing access genetic resources national biodiversity authority",
            "intellectual property": "intellectual property rights patent trademark copyright trade secret ipr protection"
        }
        
        expanded_query = query.lower()
        
        # Add relevant expansions with more sophisticated matching
        for term, expansion in term_expansions.items():
            # Check for partial matches as well
            if term in expanded_query or any(word in expanded_query for word in term.split()):
                # Add expansion terms if not already present
                expansion_terms = [t for t in expansion.split() if t not in expanded_query]
                if expansion_terms:
                    expanded_query += " " + " ".join(expansion_terms[:5])  # Add top 5 terms instead of 3
        
        # Add domain-specific terms based on query analysis
        expanded_query = self._add_domain_terms(expanded_query)
        
        return expanded_query
    
    def _add_domain_terms(self, query: str) -> str:
        """Add domain-specific terms based on query content analysis.
        
        Args:
            query: Current query (potentially expanded)
            
        Returns:
            Query with additional domain terms
        """
        # Domain-specific term groups
        domain_terms = {
            "legal_procedural": ["application", "filing", "procedure", "compliance", "regulatory", "approval", "authority"],
            "patent_concepts": ["claims", "specification", "embodiment", "invention", "disclosure", "enablement"],
            "ayurvedic_specific": ["herb", "mineral", "metal", "rasa", "guna", "virya", "vipaka", "prabhava"],
            "regulatory_bodies": ["ayush", "cdsco", "fssai", "nba", "patent office", "controller general"],
            "international_frameworks": ["trips", "convention", "treaty", "agreement", "protocol", "declaration"]
        }
        
        enhanced_query = query
        
        # Add relevant domain terms based on query content
        for domain, terms in domain_terms.items():
            # Check if any term in this domain is already present
            if any(term in enhanced_query for term in terms[:3]):  # Check first few terms
                # Add missing terms from this domain
                missing_terms = [t for t in terms if t not in enhanced_query]
                if missing_terms:
                    enhanced_query += " " + " ".join(missing_terms[:2])  # Add top 2 missing terms
        
        return enhanced_query
