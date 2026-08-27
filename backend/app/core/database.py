"""
Database module for AyurPedia.
Handles Qdrant vector database operations for storing and retrieving document chunks.
"""

import uuid
from typing import List, Dict, Any, Optional, Sequence
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from .config import get_config


# Payload keys written for every point, with the default used when a chunk omits
# the key. Hierarchy fields MUST be included here: retrieval of parent context
# depends entirely on 'chunk_type' and 'parent_id' surviving the round trip.
PAYLOAD_SCHEMA: Dict[str, Any] = {
    'text': '',
    'source': '',
    'section': '',
    'jurisdiction': '',
    'year': 0,
    'chunk_id': '',
    'document_type': '',
    'file_name': '',
    # --- hierarchical chunking fields ---
    'chunk_type': 'standard',
    'parent_id': '',
    'parent_chunk_id': '',
    'child_ids': [],
    'hierarchy_level': 0,
    'chunk_index': 0,
    'start_char': 0,
    'end_char': 0,
}

# Payload keys that are never persisted (they are transient or redundant).
_PAYLOAD_EXCLUDED = frozenset({'id', 'embedding', 'vector', 'score'})


class QdrantDB:
    """Qdrant database client for vector storage and retrieval."""
    
    def __init__(self, url: str, api_key: str, embedding_dimension: int = 1024, batch_size: int = 100) -> None:
        """Initialize Qdrant client with cloud credentials.
        
        Args:
            url: Qdrant cloud URL
            api_key: Qdrant API key
            embedding_dimension: Dimension of embeddings (default 1024 for cohere embed-english-v3.0)
            batch_size: Batch size for upsert operations
        """
        self.client = QdrantClient(url=url, api_key=api_key)
        self.embedding_dimension = embedding_dimension
        self.batch_size = batch_size
    
    def create_collections(self, collection_names: List[str], recreate: bool = False) -> None:
        """Create collections in Qdrant.
        
        Args:
            collection_names: List of collection names to create
            recreate: Whether to delete and recreate existing collections
        """
        for collection_name in collection_names:
            try:
                # Check if collection already exists
                self.client.get_collection(collection_name)
                if recreate:
                    print(f"Deleting and recreating collection: {collection_name}")
                    self.client.delete_collection(collection_name)
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dimension,
                            distance=Distance.COSINE
                        )
                    )
                    print(f"Recreated collection: {collection_name}")
                else:
                    print(f"Collection '{collection_name}' already exists. Skipping creation.")
            except Exception:
                # Create collection if it doesn't exist
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {collection_name}")

            # Idempotent: needed for hierarchical chunk_type filtering.
            self.create_payload_indexes(collection_name)
    
    def _build_payload(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Build a Qdrant payload from a chunk dictionary.

        Applies PAYLOAD_SCHEMA defaults and then passes through any extra keys,
        so newly added chunk fields are stored rather than silently dropped.

        Args:
            chunk: Flat chunk dictionary (see DocumentChunk.to_dict)

        Returns:
            Payload dictionary to persist alongside the vector
        """
        payload = {key: chunk.get(key, default) for key, default in PAYLOAD_SCHEMA.items()}

        for key, value in chunk.items():
            if key not in payload and key not in _PAYLOAD_EXCLUDED:
                payload[key] = value

        return payload

    @staticmethod
    def _resolve_point_id(chunk: Dict[str, Any]) -> str:
        """Resolve the Qdrant point ID for a chunk.

        Prefers the chunk's own deterministic ID so that re-ingesting a document
        upserts existing points in place instead of creating duplicates, and so
        that child.parent_id resolves to a real point ID.

        Args:
            chunk: Flat chunk dictionary

        Returns:
            A valid Qdrant point ID (UUID string)
        """
        candidate = chunk.get('id')
        if candidate:
            try:
                # Qdrant only accepts unsigned ints or UUIDs as point IDs.
                return str(uuid.UUID(str(candidate)))
            except (ValueError, AttributeError, TypeError):
                # Non-UUID ID: derive a stable UUID from it rather than losing
                # the caller's identity by falling back to a random uuid4.
                return str(uuid.uuid5(uuid.NAMESPACE_URL, f"ayurpedia.point|{candidate}"))
        return str(uuid.uuid4())

    def upsert_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """Upsert document chunks with their embeddings to Qdrant.
        
        Args:
            collection_name: Name of the collection to upsert to
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors corresponding to chunks
            
        Returns:
            Number of successfully upserted points
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                PointStruct(
                    id=self._resolve_point_id(chunk),
                    vector=embedding,
                    payload=self._build_payload(chunk)
                )
            )
        
        # Upsert in batches
        success_count = 0
        
        for i in range(0, len(points), self.batch_size):
            batch = points[i:i + self.batch_size]
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                success_count += len(batch)
            except Exception as e:
                print(f"Error upserting batch {i//self.batch_size}: {e}")
        
        return success_count

    def retrieve_points(
        self,
        collection_name: str,
        point_ids: Sequence[str]
    ) -> List[Dict[str, Any]]:
        """Fetch points by ID using Qdrant's point retrieval API.

        Used by hierarchical retrieval to pull parent chunks for matched
        children. This is a direct ID lookup, unlike scrolling the collection.

        Args:
            collection_name: Name of the collection
            point_ids: Point IDs to fetch

        Returns:
            List of dictionaries with 'id' and 'payload' keys. Missing IDs are
            omitted; an empty list is returned on error.
        """
        if not point_ids:
            return []

        try:
            records = self.client.retrieve(
                collection_name=collection_name,
                ids=list(point_ids),
                with_payload=True,
                with_vectors=False
            )
            return [
                {'id': str(record.id), 'payload': record.payload or {}}
                for record in records
            ]
        except Exception as e:
            print(f"Error retrieving points from collection '{collection_name}': {e}")
            return []
    
    def create_payload_indexes(self, collection_name: str) -> None:
        """Create payload indexes required for efficient filtering.

        Without these, filtering by chunk_type (to search only child chunks) and
        looking documents up by file_name both degrade to full scans.

        Args:
            collection_name: Name of the collection to index
        """
        indexed_fields = ('chunk_type', 'file_name', 'parent_id', 'jurisdiction')

        for field in indexed_fields:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD
                )
                print(f"Created payload index on '{collection_name}.{field}'")
            except Exception as e:
                # Already exists, or the server rejected it. Filtering still
                # works without an index, just more slowly.
                message = str(e).lower()
                if 'already exists' not in message:
                    print(f"Could not create index on '{collection_name}.{field}': {e}")

    @staticmethod
    def build_chunk_type_filter(chunk_types: Sequence[str]) -> Optional[Filter]:
        """Build a Qdrant filter matching any of the given chunk types.

        Args:
            chunk_types: Chunk types to allow, e.g. ``('child',)``

        Returns:
            A Filter, or None when no chunk types were supplied
        """
        if not chunk_types:
            return None

        return Filter(
            should=[
                FieldCondition(key='chunk_type', match=MatchValue(value=chunk_type))
                for chunk_type in chunk_types
            ]
        )

    def search_similar(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.5,
        chunk_types: Optional[Sequence[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in the specified collection.
        
        Args:
            collection_name: Name of the collection to search in
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            chunk_types: Optional chunk types to restrict the search to, e.g.
                ``('child',)`` to search only leaf chunks in a hierarchy
            
        Returns:
            List of similar chunks with their metadata and scores
        """
        query_filter = self.build_chunk_type_filter(chunk_types) if chunk_types else None

        try:
            search_result = self._execute_search(
                collection_name, query_embedding, limit, score_threshold, query_filter
            )
        except Exception as e:
            print(f"Error searching in collection '{collection_name}': {e}")
            if query_filter is None:
                return []
            # A filtered search can fail on older servers or a missing index.
            # Degrade to an unfiltered search rather than returning nothing.
            print(f"Retrying search in '{collection_name}' without chunk_type filter")
            try:
                search_result = self._execute_search(
                    collection_name, query_embedding, limit, score_threshold, None
                )
            except Exception as retry_error:
                print(f"Unfiltered retry also failed for '{collection_name}': {retry_error}")
                return []

        return [
            {'id': str(result.id), 'score': result.score, 'payload': result.payload or {}}
            for result in search_result
        ]

    def _execute_search(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int,
        score_threshold: float,
        query_filter: Optional[Filter]
    ) -> List[Any]:
        """Run a vector search against Qdrant, handling client API differences.

        Args:
            collection_name: Name of the collection to search in
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            query_filter: Optional payload filter

        Returns:
            Raw scored points from the Qdrant client
        """
        if hasattr(self.client, 'query_points'):
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            return response.points

        return self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold
        )
    
    def search_with_filter(
        self,
        collection_name: str,
        query_embedding: List[float],
        filter_field: str,
        filter_value: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search with additional metadata filtering.
        
        Args:
            collection_name: Name of the collection to search in
            query_embedding: Query embedding vector
            filter_field: Field to filter on (e.g., 'jurisdiction', 'document_type')
            filter_value: Value to match
            limit: Maximum number of results to return
            
        Returns:
            List of similar chunks matching the filter criteria
        """
        try:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key=filter_field,
                        match=MatchValue(value=filter_value)
                    )
                ]
            )
            
            if hasattr(self.client, 'query_points'):
                response = self.client.query_points(
                    collection_name=collection_name,
                    query=query_embedding,
                    query_filter=query_filter,
                    limit=limit
                )
                search_result = response.points
            else:
                search_result = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_embedding,
                    query_filter=query_filter,
                    limit=limit
                )
            
            results = []
            for result in search_result:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            return results
        except Exception as e:
            print(f"Error searching with filter in collection '{collection_name}': {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any] | None:
        """Get collection statistics and information.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information or None if collection doesn't exist
        """
        try:
            collection_info = self.client.get_collection(collection_name)
            config_data = {
                'params': collection_info.config.params
            }
            # Try to get vectors_config if it exists
            if hasattr(collection_info.config, 'vectors_config'):
                config_data['vectors_config'] = collection_info.config.vectors_config
            else:
                config_data['vector_size'] = self.embedding_dimension
                
            return {
                'name': collection_name,
                'points_count': collection_info.points_count,
                'status': collection_info.status,
                'config': config_data
            }
        except Exception as e:
            print(f"Error getting collection info for '{collection_name}': {e}")
            return None
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from Qdrant.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name)
            print(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            print(f"Error deleting collection '{collection_name}': {e}")
            return False
    
    def count_points(self, collection_name: str) -> int:
        """Count the number of points in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of points in the collection
        """
        try:
            count_result = self.client.count(collection_name)
            return count_result.count
        except Exception as e:
            print(f"Error counting points in collection '{collection_name}': {e}")
            return 0
    
    def document_exists(self, collection_name: str, file_name: str) -> bool:
        """Check if a document already exists in the collection.
        
        Args:
            collection_name: Name of the collection
            file_name: Name of the file to check
            
        Returns:
            True if document exists, False otherwise
        """
        try:
            # Scroll through points and check file_name manually (avoids index requirement)
            result = self.client.scroll(
                collection_name=collection_name,
                limit=100,
                with_payload=True
            )
            
            points = result[0]
            for point in points:
                if point.payload and point.payload.get('file_name') == file_name:
                    return True
            
            # If not found in first batch, check if there are more points
            while len(points) == 100:
                offset = points[-1].id
                result = self.client.scroll(
                    collection_name=collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True
                )
                points = result[0]
                
                for point in points:
                    if point.payload and point.payload.get('file_name') == file_name:
                        return True
                
                if len(points) < 100:
                    break
            
            return False
        except Exception as e:
            print(f"Error checking if document exists in collection '{collection_name}': {e}")
            return False
    
    def get_processed_documents(self, collection_name: str) -> List[str]:
        """Get list of already processed document file names.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of file names that have been processed
        """
        try:
            # Scroll through all points and collect unique file names
            all_points = []
            limit = 100
            offset = None
            
            while True:
                if offset is None:
                    result = self.client.scroll(
                        collection_name=collection_name,
                        limit=limit,
                        with_payload=True
                    )
                else:
                    result = self.client.scroll(
                        collection_name=collection_name,
                        limit=limit,
                        offset=offset,
                        with_payload=True
                    )
                
                points = result[0]
                if not points:
                    break
                
                all_points.extend(points)
                offset = points[-1].id
                
                if len(points) < limit:
                    break
            
            # Extract unique file names
            file_names = set()
            for point in all_points:
                if point.payload and 'file_name' in point.payload:
                    file_names.add(point.payload['file_name'])
            
            return list(file_names)
        except Exception as e:
            print(f"Error getting processed documents from collection '{collection_name}': {e}")
            return []