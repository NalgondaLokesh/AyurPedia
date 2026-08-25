"""
Data models for AyurPedia document processing.
Defines Pydantic models for document chunks and metadata.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class DocumentMetadata(BaseModel):
    """Metadata model for document information."""
    
    source_name: str = Field(..., description="Name of the source document")
    jurisdiction: str = Field(..., description="Jurisdiction (India/International)")
    document_type: str = Field(..., description="Type of document (Act/Treaty/Regulation)")
    year: int = Field(..., description="Year of the document")
    citation_format: str = Field(default="", description="Citation format for the document")
    file_name: str = Field(..., description="Original filename")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "source_name": "Patents Act 1970",
                "jurisdiction": "India",
                "document_type": "Act",
                "year": 1970,
                "citation_format": "Act No. 39 of 1970",
                "file_name": "patents_act_1970.pdf"
            }
        }


class DocumentChunk(BaseModel):
    """Model for a chunk of text from a document."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the chunk")
    text: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(..., description="Metadata associated with the chunk")
    embedding: List[float] = Field(default_factory=list, description="Embedding vector for the chunk")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "text": "Section 1: Short title, extent and commencement...",
                "metadata": {
                    "source": "Patents Act 1970",
                    "section": "Section 1",
                    "jurisdiction": "India",
                    "year": 1970,
                    "document_type": "Act",
                    "chunk_id": "section_1_0"
                },
                "embedding": None
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DocumentChunk to dictionary format.
        
        Returns:
            Dictionary representation of the chunk
        """
        return {
            'id': self.id,
            'text': self.text,
            'source': self.metadata.get('source', ''),
            'section': self.metadata.get('section', ''),
            'jurisdiction': self.metadata.get('jurisdiction', ''),
            'year': self.metadata.get('year', 0),
            'chunk_id': self.metadata.get('chunk_id', ''),
            'document_type': self.metadata.get('document_type', '')
        }
    
    @classmethod
    def from_text(
        cls,
        text: str,
        metadata: Dict[str, Any],
        chunk_id: Optional[str] = None
    ) -> 'DocumentChunk':
        """Create a DocumentChunk from text and metadata.
        
        Args:
            text: Text content for the chunk
            metadata: Metadata dictionary
            chunk_id: Optional custom chunk ID
            
        Returns:
            DocumentChunk instance
        """
        if chunk_id:
            metadata['chunk_id'] = chunk_id
        elif 'chunk_id' not in metadata:
            metadata['chunk_id'] = str(uuid4())
        
        return cls(text=text, metadata=metadata)


class DocumentProcessingResult(BaseModel):
    """Model for document processing results."""
    
    source_name: str = Field(..., description="Name of the processed document")
    file_name: str = Field(..., description="Original filename")
    pages_extracted: int = Field(..., description="Number of pages extracted from PDF")
    chunks_created: int = Field(..., description="Number of chunks created")
    embeddings_generated: int = Field(..., description="Number of embeddings generated")
    chunks_stored: int = Field(..., description="Number of chunks stored in database")
    collection_name: str = Field(..., description="Name of the collection used")
    processing_time_seconds: float = Field(..., description="Time taken to process document")
    success: bool = Field(..., description="Whether processing was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "source_name": "Patents Act 1970",
                "file_name": "patents_act_1970.pdf",
                "pages_extracted": 245,
                "chunks_created": 156,
                "embeddings_generated": 156,
                "chunks_stored": 156,
                "collection_name": "india_corpus",
                "processing_time_seconds": 45.2,
                "success": True,
                "error_message": None
            }
        }


class IngestionSummary(BaseModel):
    """Model for overall ingestion summary."""
    
    total_documents_processed: int = Field(..., description="Total number of documents processed")
    total_chunks: int = Field(..., description="Total number of chunks across all documents")
    india_collection_chunks: int = Field(..., description="Number of chunks in India collection")
    international_collection_chunks: int = Field(..., description="Number of chunks in International collection")
    vector_dimension: int = Field(..., description="Dimension of embedding vectors")
    storage_url: str = Field(..., description="URL of the vector database")
    processing_time_seconds: float = Field(..., description="Total time taken for ingestion")
    document_results: List[DocumentProcessingResult] = Field(
        default_factory=list,
        description="List of individual document processing results"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "total_documents_processed": 6,
                "total_chunks": 423,
                "india_collection_chunks": 276,
                "international_collection_chunks": 147,
                "vector_dimension": 768,
                "storage_url": "https://your-cluster.qdrant.io",
                "processing_time_seconds": 154.2,
                "document_results": []
            }
        }