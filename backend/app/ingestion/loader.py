"""
Loader module for AyurPedia.
Handles loading document chunks with embeddings into Qdrant vector database.
"""

import json
import os
import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from app.core.database import QdrantDB
from app.ingestion.embedder import Embedder
from app.models.document import DocumentChunk


class DocumentLoader:
    """Document loader for processing and loading chunks into Qdrant."""
    
    def __init__(self, qdrant_db: QdrantDB, embedder: Embedder, checkpoint_dir: str = "checkpoints") -> None:
        """Initialize document loader.
        
        Args:
            qdrant_db: QdrantDB instance for vector storage
            embedder: Embedder instance for generating embeddings
            checkpoint_dir: Directory to store checkpoint files
        """
        self.qdrant_db = qdrant_db
        self.embedder = embedder
        self.success_count = 0
        self.failure_count = 0
        self.checkpoint_dir = checkpoint_dir
        
        # Create checkpoint directory if it doesn't exist
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
    
    def prepare_payload(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """Prepare Qdrant payload from DocumentChunk.
        
        Args:
            chunk: DocumentChunk object
            
        Returns:
            Dictionary formatted for Qdrant payload
        """
        return {
            'text': chunk.text,
            'source': chunk.metadata.get('source', ''),
            'section': chunk.metadata.get('section', ''),
            'jurisdiction': chunk.metadata.get('jurisdiction', ''),
            'year': chunk.metadata.get('year', 0),
            'chunk_id': chunk.metadata.get('chunk_id', ''),
            'document_type': chunk.metadata.get('document_type', ''),
            'file_name': chunk.metadata.get('file_name', '')
        }
    
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
        show_progress: bool = True,
        document_name: str = None,
        ignore_checkpoints: bool = False
    ) -> int:
        """Generate embeddings and load chunks into Qdrant with checkpointing.
        
        Args:
            chunks: List of DocumentChunk objects
            collection_name: Name of the Qdrant collection
            show_progress: Whether to show progress bar
            document_name: Name of document for checkpointing
            ignore_checkpoints: Whether to ignore existing checkpoints
            
        Returns:
            Number of successfully loaded chunks
        """
        if not chunks:
            print("No chunks to load.")
            return 0
        
        # Check for existing checkpoint
        start_index = 0
        if document_name and not ignore_checkpoints:
            checkpoint = self.load_checkpoint(document_name)
            if checkpoint and checkpoint['processed_chunks'] < len(chunks):
                start_index = checkpoint['processed_chunks']
                print(f"Resuming from chunk {start_index} of {len(chunks)}")
            elif checkpoint and checkpoint['processed_chunks'] >= len(chunks):
                print(f"Document already fully processed ({checkpoint['processed_chunks']} chunks)")
                return checkpoint['processed_chunks']
        
        # Process from checkpoint
        chunks_to_process = chunks[start_index:]
        if not chunks_to_process:
            print("No new chunks to process.")
            return start_index
        
        # Extract text from chunks
        texts = [chunk.text for chunk in chunks_to_process]
        
        # Generate embeddings with rate limit handling
        print(f"Generating embeddings for {len(texts)} chunks (starting from {start_index})...")
        embeddings = []
        
        for i in range(0, len(texts), self.qdrant_db.batch_size):
            batch = texts[i:i + self.qdrant_db.batch_size]
            batch_number = start_index + i
            
            try:
                batch_embeddings = self.embedder.embed_batch(batch)
                embeddings.extend(batch_embeddings)
                
                # Save checkpoint after each batch
                if document_name:
                    self.save_checkpoint(document_name, start_index + i + len(batch), len(chunks))
                
                # Add delay between batches
                if i + self.qdrant_db.batch_size < len(texts):
                    time.sleep(2)
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"\nRATE LIMIT HIT at chunk {batch_number}")
                    print(f"Checkpoint saved at {start_index + i} chunks")
                    print("Resume after quota resets to continue from this point")
                    raise
                else:
                    print(f"Error processing batch {batch_number}: {e}")
                    # Add zero vectors for failed batch
                    zero_vectors = [[0.0] * self.embedder.embedding_dimension] * len(batch)
                    embeddings.extend(zero_vectors)
        
        # Combine with previously processed chunks if resuming
        all_embeddings = []
        all_chunks = []
        
        if start_index > 0:
            # Assume previous chunks were already loaded successfully
            all_embeddings = [[0.0] * self.embedder.embedding_dimension] * start_index
            all_chunks = chunks[:start_index]
        
        all_embeddings.extend(embeddings)
        all_chunks.extend(chunks_to_process)
        
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
        
        # Clear checkpoint on successful completion
        if document_name and success_count == len(chunks):
            self.clear_checkpoint(document_name)
        
        return success_count
    
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
    
    def save_checkpoint(self, document_name: str, processed_chunks: int, total_chunks: int) -> None:
        """Save checkpoint for document processing progress.
        
        Args:
            document_name: Name of the document being processed
            processed_chunks: Number of chunks processed so far
            total_chunks: Total number of chunks in document
        """
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{document_name.replace('.pdf', '')}_checkpoint.json")
        checkpoint_data = {
            'document_name': document_name,
            'processed_chunks': processed_chunks,
            'total_chunks': total_chunks,
            'timestamp': str(time.time())
        }
        
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f)
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
    
    def load_checkpoint(self, document_name: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for document processing progress.
        
        Args:
            document_name: Name of the document to load checkpoint for
            
        Returns:
            Checkpoint data if exists, None otherwise
        """
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{document_name.replace('.pdf', '')}_checkpoint.json")
        
        try:
            if os.path.exists(checkpoint_file):
                with open(checkpoint_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
        
        return None
    
    def clear_checkpoint(self, document_name: str) -> None:
        """Clear checkpoint for a document.
        
        Args:
            document_name: Name of the document to clear checkpoint for
        """
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{document_name.replace('.pdf', '')}_checkpoint.json")
        
        try:
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
        except Exception as e:
            print(f"Error clearing checkpoint: {e}")
    
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
        """Load chunks for a single document with detailed reporting and checkpointing.
        
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
        
        # Load chunks with checkpointing (ignore old checkpoints for fresh start)
        loaded_count = self.load_chunks(valid_chunks, collection_name, show_progress=True, document_name=document_name, ignore_checkpoints=True)
        
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