"""
Database module for AyurPedia.
Handles Qdrant vector database operations for storing and retrieving document chunks.
"""

import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from .config import get_config


class QdrantDB:
    """Qdrant database client for vector storage and retrieval."""
    
    def __init__(self, url: str, api_key: str, embedding_dimension: int = 768, batch_size: int = 100) -> None:
        """Initialize Qdrant client with cloud credentials.
        
        Args:
            url: Qdrant cloud URL
            api_key: Qdrant API key
            embedding_dimension: Dimension of embeddings (default 768 for gemini-embedding-001)
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
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    'text': chunk.get('text', ''),
                    'source': chunk.get('source', ''),
                    'section': chunk.get('section', ''),
                    'jurisdiction': chunk.get('jurisdiction', ''),
                    'year': chunk.get('year', 0),
                    'chunk_id': chunk.get('chunk_id', ''),
                    'document_type': chunk.get('document_type', ''),
                    'file_name': chunk.get('file_name', '')
                }
            )
            points.append(point)
        
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
    
    def search_similar(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in the specified collection.
        
        Args:
            collection_name: Name of the collection to search in
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of similar chunks with their metadata and scores
        """
        try:
            if hasattr(self.client, 'query_points'):
                response = self.client.query_points(
                    collection_name=collection_name,
                    query=query_embedding,
                    limit=limit,
                    score_threshold=score_threshold
                )
                search_result = response.points
            else:
                search_result = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    score_threshold=score_threshold
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
            print(f"Error searching in collection '{collection_name}': {e}")
            return []
    
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