"""
Loader module for AyurPedia.
Handles loading document chunks with embeddings into Qdrant vector database.
"""

import os
import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from app.core.database import QdrantDB
from app.ingestion.embedder import Embedder
from app.models.document import DocumentChunk


class DocumentLoader:
    """Document loader for processing and loading chunks into Qdrant."""
    
    def __init__(self, qdrant_db: QdrantDB, embedder: Embedder) -> None:
        """Initialize document loader.
        
        Args:
            qdrant_db: QdrantDB instance for vector storage
            embedder: Embedder instance for generating embeddings
        """
        self.qdrant_db = qdrant_db
        self.embedder = embedder
        self.success_count = 0
        self.failure_count = 0
    
    def prepare_payload(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """Prepare Qdrant payload from DocumentChunk with hierarchical support.
        
        Delegates to DocumentChunk.to_dict() so the payload shape stays in sync
        with the model. The returned dict includes 'id' so QdrantDB can use the
        chunk's deterministic ID as the point ID, which is what makes
        child.parent_id resolvable at query time.
        
        Args:
            chunk: DocumentChunk object
            
        Returns:
            Dictionary formatted for Qdrant payload
        """
        return chunk.to_dict()
    
    def chunk_to_payload(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """Convert DocumentChunk to Qdrant payload format.
        
        Args:
            chunk: DocumentChunk object
            
        Returns:
            Payload dictionary for Qdrant
        """
        return self.prepare_payload(chunk)
    
    def load_chunks(
        self,
        chunks: List[DocumentChunk],
        collection_name: str,
        show_progress: bool = True
    ) -> int:
        """Generate embeddings and load chunks into Qdrant.
        
        Args:
            chunks: List of DocumentChunk objects
            collection_name: Name of the Qdrant collection
            show_progress: Whether to show progress bar
            
        Returns:
            Number of successfully loaded chunks
        """
        if not chunks:
            print("No chunks to load.")
            return 0
        
        chunks_to_process = chunks
        
        # Extract text from chunks
        texts = [chunk.text for chunk in chunks_to_process]
        
        # Generate embeddings with rate limit handling
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = []
        
        for i in range(0, len(texts), self.qdrant_db.batch_size):
            batch = texts[i:i + self.qdrant_db.batch_size]
            batch_number = i
            
            try:
                batch_embeddings = self.embedder.embed_batch(batch)
                embeddings.extend(batch_embeddings)
                
                # Add delay between batches
                if i + self.qdrant_db.batch_size < len(texts):
                    time.sleep(2)
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"\nRATE LIMIT HIT at chunk {batch_number}")
                    print("Resume after quota resets to continue from this point")
                    raise
                else:
                    print(f"Error processing batch {batch_number}: {e}")
                    # Add zero vectors for failed batch
                    zero_vectors = [[0.0] * self.embedder.embedding_dimension] * len(batch)
                    embeddings.extend(zero_vectors)
        
        all_embeddings = embeddings
        all_chunks = chunks_to_process
        
        # Validate embeddings
        valid_embeddings = []
        valid_chunks = []
        for chunk, embedding in zip(all_chunks, all_embeddings):
            if self.embedder.validate_embedding(embedding):
                valid_embeddings.append(embedding)
                valid_chunks.append(chunk)
            else:
                print(f"Invalid embedding for chunk {chunk.metadata.get('chunk_id', 'unknown')}")
                self.failure_count += 1
        
        # Prepare payloads
        payloads = [self.chunk_to_payload(chunk) for chunk in valid_chunks]
        
        # A dropped parent orphans its children, which silently breaks
        # parent-child retrieval for those chunks. Surface it loudly.
        self._report_hierarchy(chunks_to_process, valid_chunks)
        
        # Load into Qdrant
        print(f"Loading {len(valid_chunks)} chunks into collection '{collection_name}'...")
        
        if show_progress:
            with tqdm(total=len(valid_chunks), desc="Loading chunks") as pbar:
                success_count = self.qdrant_db.upsert_chunks(
                    collection_name=collection_name,
                    chunks=payloads,
                    embeddings=valid_embeddings
                )
                pbar.update(success_count)
        else:
            success_count = self.qdrant_db.upsert_chunks(
                collection_name=collection_name,
                chunks=payloads,
                embeddings=valid_embeddings
            )
        
        self.success_count += success_count
        self.failure_count += len(valid_chunks) - success_count
        
        return success_count
    
    def _report_hierarchy(
        self,
        submitted: List[DocumentChunk],
        valid: List[DocumentChunk]
    ) -> None:
        """Print a parent/child breakdown and warn about orphaned children.
        
        Args:
            submitted: Chunks handed to the loader
            valid: Chunks that survived embedding validation
        """
        parents = [c for c in valid if c.chunk_type == 'parent']
        children = [c for c in valid if c.chunk_type == 'child']
        
        if not parents and not children:
            return
        
        print(f"  Hierarchy: {len(parents)} parent + {len(children)} child chunks")
        
        surviving_parent_ids = {c.id for c in parents}
        orphaned = [
            c for c in children
            if c.parent_id and c.parent_id not in surviving_parent_ids
        ]
        
        if orphaned:
            dropped = len(submitted) - len(valid)
            print(
                f"  WARNING: {len(orphaned)} child chunks are orphaned "
                f"({dropped} chunks failed validation). Their parent context "
                f"will not be retrievable."
            )
    
    def process_and_load(
        self,
        chunks: List[DocumentChunk],
        collection_name: str
    ) -> Dict[str, int]:
        """Process all chunks and load them into Qdrant with statistics.
        
        Args:
            chunks: List of DocumentChunk objects
            collection_name: Name of the Qdrant collection
            
        Returns:
            Dictionary with processing statistics
        """
        print(f"\nProcessing {len(chunks)} chunks for collection '{collection_name}'...")
        
        # Reset counters
        self.success_count = 0
        self.failure_count = 0
        
        # Load chunks
        loaded_count = self.load_chunks(chunks, collection_name, show_progress=True)
        
        # Print statistics
        print(f"\nLoading Statistics:")
        print(f"  - Total chunks processed: {len(chunks)}")
        print(f"  - Successfully loaded: {loaded_count}")
        print(f"  - Failed: {self.failure_count}")
        print(f"  - Success rate: {(loaded_count/len(chunks)*100):.1f}%" if chunks else "  - Success rate: 0%")
        
        return {
            'total_chunks': len(chunks),
            'loaded_chunks': loaded_count,
            'failed_chunks': self.failure_count,
            'success_rate': (loaded_count/len(chunks)*100) if chunks else 0
        }
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a specific collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection statistics
        """
        return self.qdrant_db.get_collection_info(collection_name)
    
    def get_loading_stats(self) -> Dict[str, int]:
        """Get overall loading statistics.
        
        Returns:
            Dictionary with loading statistics
        """
        return {
            'total_success': self.success_count,
            'total_failures': self.failure_count,
            'total_processed': self.success_count + self.failure_count
        }
    
    def reset_stats(self) -> None:
        """Reset loading statistics counters."""
        self.success_count = 0
        self.failure_count = 0
    
    def validate_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Validate chunks before loading.
        
        Args:
            chunks: List of DocumentChunk objects to validate
            
        Returns:
            List of valid chunks
        """
        valid_chunks = []
        
        for chunk in chunks:
            # Check if chunk has required fields
            if not chunk.text or not chunk.text.strip():
                print(f"Skipping chunk with empty text: {chunk.metadata.get('chunk_id', 'unknown')}")
                self.failure_count += 1
                continue
            
            if not chunk.metadata.get('source'):
                print(f"Skipping chunk without source: {chunk.metadata.get('chunk_id', 'unknown')}")
                self.failure_count += 1
                continue
            
            valid_chunks.append(chunk)
        
        return valid_chunks
    
    def load_single_document(
        self,
        chunks: List[DocumentChunk],
        collection_name: str,
        document_name: str
    ) -> Dict[str, Any]:
        """Load chunks for a single document with detailed reporting.
        
        Args:
            chunks: List of DocumentChunk objects
            collection_name: Name of the Qdrant collection
            document_name: Name of the document being loaded
            
        Returns:
            Dictionary with detailed loading results
        """
        print(f"\n{'='*50}")
        print(f"Loading document: {document_name}")
        print(f"{'='*50}")
        
        # Validate chunks
        valid_chunks = self.validate_chunks(chunks)
        print(f"Valid chunks: {len(valid_chunks)}/{len(chunks)}")
        
        if not valid_chunks:
            print("No valid chunks to load.")
            return {
                'document_name': document_name,
                'total_chunks': len(chunks),
                'valid_chunks': 0,
                'loaded_chunks': 0,
                'success': False
            }
        
        # Load chunks
        loaded_count = self.load_chunks(valid_chunks, collection_name, show_progress=True)
        
        result = {
            'document_name': document_name,
            'total_chunks': len(chunks),
            'valid_chunks': len(valid_chunks),
            'loaded_chunks': loaded_count,
            'success': loaded_count > 0,
            'collection_name': collection_name
        }
        
        print(f"\n{'='*50}")
        print(f"Document loading complete: {document_name}")
        print(f"  - Loaded: {loaded_count}/{len(valid_chunks)} chunks")
        print(f"{'='*50}")
        
        return result