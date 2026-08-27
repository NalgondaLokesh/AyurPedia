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


CHUNK_TYPE_PARENT = "parent"
CHUNK_TYPE_CHILD = "child"
CHUNK_TYPE_STANDARD = "standard"


class DocumentChunk(BaseModel):
    """A chunk of text from a document, with parent-child hierarchy support.

    Hierarchical chunking stores two levels of granularity:

    * ``parent`` chunks are large (~2000 chars) and provide the context handed
      to the LLM. They list their children in ``child_ids``.
    * ``child`` chunks are small (~400 chars), are what the vector search
      matches against, and point back at their parent via ``parent_id``.
    * ``standard`` chunks are flat, non-hierarchical chunks.

    ``start_char``/``end_char`` are absolute offsets into the source document,
    which makes ordering and de-duplication of retrieved context deterministic.
    A child's span is always contained within its parent's span.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the chunk")
    text: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(..., description="Metadata associated with the chunk")
    embedding: List[float] = Field(default_factory=list, description="Embedding vector for the chunk")
    parent_id: Optional[str] = Field(default=None, description="ID of parent chunk (set on child chunks)")
    child_ids: List[str] = Field(default_factory=list, description="IDs of child chunks (set on parent chunks)")
    chunk_type: str = Field(default=CHUNK_TYPE_STANDARD, description="Type of chunk: 'parent', 'child', or 'standard'")
    hierarchy_level: int = Field(default=0, description="Depth in the hierarchy: 0 for parent/standard, 1 for child")
    chunk_index: int = Field(default=0, description="Ordinal position of the chunk within its hierarchy level")
    start_char: int = Field(default=0, description="Absolute start offset of the chunk in the source document")
    end_char: int = Field(default=0, description="Absolute end offset of the chunk in the source document")

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
                    "chunk_id": "patents_act_1970_parent_0",
                    "file_name": "patents_act_1970.pdf"
                },
                "embedding": None,
                "parent_id": None,
                "child_ids": ["6f1c2d3e-4a5b-5c6d-8e9f-0a1b2c3d4e5f"],
                "chunk_type": "parent",
                "hierarchy_level": 0,
                "chunk_index": 0,
                "start_char": 0,
                "end_char": 1987
            }
        }

    @property
    def is_parent(self) -> bool:
        """Whether this chunk is a parent chunk."""
        return self.chunk_type == CHUNK_TYPE_PARENT

    @property
    def is_child(self) -> bool:
        """Whether this chunk is a child chunk."""
        return self.chunk_type == CHUNK_TYPE_CHILD

    @property
    def score(self) -> float:
        """Similarity score assigned by the retriever, 0.0 when unscored."""
        return float(self.metadata.get('score', 0.0) or 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert DocumentChunk to a flat dictionary (Qdrant payload shape).

        Returns:
            Dictionary representation of the chunk including hierarchy fields.
        """
        return {
            'id': self.id,
            'text': self.text,
            'source': self.metadata.get('source', ''),
            'section': self.metadata.get('section', ''),
            'jurisdiction': self.metadata.get('jurisdiction', ''),
            'year': self.metadata.get('year', 0),
            'chunk_id': self.metadata.get('chunk_id', ''),
            'document_type': self.metadata.get('document_type', ''),
            'file_name': self.metadata.get('file_name', ''),
            'parent_id': self.parent_id or '',
            'parent_chunk_id': self.metadata.get('parent_chunk_id', ''),
            'child_ids': self.child_ids,
            'chunk_type': self.chunk_type,
            'hierarchy_level': self.hierarchy_level,
            'chunk_index': self.chunk_index,
            'start_char': self.start_char,
            'end_char': self.end_char
        }

    @classmethod
    def from_text(
        cls,
        text: str,
        metadata: Dict[str, Any],
        chunk_id: Optional[str] = None,
        **kwargs: Any
    ) -> 'DocumentChunk':
        """Create a DocumentChunk from text and metadata.

        Args:
            text: Text content for the chunk
            metadata: Metadata dictionary
            chunk_id: Optional custom chunk ID
            **kwargs: Additional DocumentChunk fields (e.g. ``parent_id``,
                ``chunk_type``, ``start_char``)

        Returns:
            DocumentChunk instance
        """
        if chunk_id:
            metadata['chunk_id'] = chunk_id
        elif 'chunk_id' not in metadata:
            metadata['chunk_id'] = str(uuid4())

        return cls(text=text, metadata=metadata, **kwargs)

    @classmethod
    def from_payload(
        cls,
        payload: Dict[str, Any],
        point_id: Optional[str] = None,
        score: float = 0.0,
        default_jurisdiction: str = ''
    ) -> 'DocumentChunk':
        """Rebuild a DocumentChunk from a Qdrant payload.

        Single source of truth for payload -> chunk mapping, shared by every
        retriever so hierarchy fields can never be silently dropped again.

        Args:
            payload: Qdrant point payload.
            point_id: Qdrant point ID, used as the chunk ID when present.
            score: Similarity score to record in metadata.
            default_jurisdiction: Fallback when the payload omits jurisdiction.

        Returns:
            DocumentChunk instance.
        """
        payload = payload or {}

        metadata: Dict[str, Any] = {
            'source': payload.get('source', ''),
            'section': payload.get('section', ''),
            'jurisdiction': payload.get('jurisdiction', default_jurisdiction),
            'year': payload.get('year', 0),
            'chunk_id': payload.get('chunk_id', ''),
            'document_type': payload.get('document_type', ''),
            'file_name': payload.get('file_name', ''),
            'score': score
        }
        if payload.get('parent_chunk_id'):
            metadata['parent_chunk_id'] = payload['parent_chunk_id']

        chunk_id = str(point_id) if point_id is not None else payload.get('id') or str(uuid4())

        return cls(
            id=chunk_id,
            text=payload.get('text', ''),
            metadata=metadata,
            parent_id=payload.get('parent_id') or None,
            child_ids=payload.get('child_ids') or [],
            chunk_type=payload.get('chunk_type') or CHUNK_TYPE_STANDARD,
            hierarchy_level=int(payload.get('hierarchy_level', 0) or 0),
            chunk_index=int(payload.get('chunk_index', 0) or 0),
            start_char=int(payload.get('start_char', 0) or 0),
            end_char=int(payload.get('end_char', 0) or 0)
        )


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