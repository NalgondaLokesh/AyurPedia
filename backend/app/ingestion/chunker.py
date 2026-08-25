"""
Chunker module for AyurPedia.
Handles text chunking with different strategies for legal documents, treaties, and regulations.
"""

import re
from typing import List, Dict, Any, Optional
from app.models.document import DocumentChunk, DocumentMetadata


class Chunker:
    """Text chunker with different strategies for document types."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """Initialize chunker with configuration.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_by_sections(self, text: str) -> List[str]:
        """Split text by legal sections (Section X, Article X, Regulation X).
        
        Args:
            text: Full text content
            
        Returns:
            List of section-based chunks
        """
        # Pattern for legal sections (Section X, Article X, etc.)
        section_pattern = r'(?:Section|Article|Regulation|Chapter|Part)\s+\d+[A-Za-z]*\.?\s+'
        
        # Find all section headers
        sections = re.split(section_pattern, text)
        headers = re.findall(section_pattern, text)
        
        chunks = []
        for i, (header, section) in enumerate(zip(headers, sections)):
            if section.strip():
                chunk_text = header + section.strip()
                chunks.append(chunk_text)
        
        # Handle any text before the first section
        if sections and sections[0].strip():
            chunks.insert(0, sections[0].strip())
        
        return chunks if chunks else [text]
    
    def chunk_by_headers(self, text: str) -> List[str]:
        """Split text by headers for FSSAI and similar documents.
        
        Args:
            text: Full text content
            
        Returns:
            List of header-based chunks
        """
        # Pattern for headers (all caps, followed by colon or new line)
        header_pattern = r'^[A-Z][A-Z\s]{3,}:\s*$'
        
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        
        for line in lines:
            if re.match(header_pattern, line.strip()):
                # Save previous chunk if it exists
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                # Start new chunk with header
                current_chunk.append(line)
            else:
                current_chunk.append(line)
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks if chunks else [text]
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks of specified size.
        
        Args:
            text: Full text content
            
        Returns:
            List of overlapping text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Adjust end to not cut in the middle of a word
            if end < text_length:
                # Find the last space before the end
                last_space = text.rfind(' ', start, end)
                if last_space != -1:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
        
        return chunks
    
    def detect_section_type(self, text: str) -> str:
        """Determine the document type based on text structure.
        
        Args:
            text: Full text content
            
        Returns:
            Document type: 'legal', 'treaty', 'regulation', or 'general'
        """
        text_lower = text.lower()
        
        # Check for legal sections
        if re.search(r'section\s+\d+', text_lower):
            return 'legal'
        
        # Check for treaty articles
        if re.search(r'article\s+\d+', text_lower):
            return 'treaty'
        
        # Check for regulations
        if re.search(r'regulation\s+\d+|schedule\s+[ivx]+', text_lower):
            return 'regulation'
        
        return 'general'
    
    def create_chunks(
        self,
        text: str,
        metadata: DocumentMetadata
    ) -> List[DocumentChunk]:
        """Create DocumentChunk objects with proper IDs and metadata.
        
        Args:
            text: Full text content
            metadata: DocumentMetadata object
            
        Returns:
            List of DocumentChunk objects
        """
        # Determine chunking strategy based on document type
        section_type = self.detect_section_type(text)
        
        if section_type == 'legal':
            raw_chunks = self.chunk_by_sections(text)
        elif section_type == 'treaty':
            raw_chunks = self.chunk_by_sections(text)  # Same strategy for treaties
        elif section_type == 'regulation':
            raw_chunks = self.chunk_by_headers(text)
        else:
            raw_chunks = self.chunk_text(text)
        
        # Create DocumentChunk objects
        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            # Extract section/article number if present
            section_number = self._extract_section_number(chunk_text, section_type)
            
            # Create chunk metadata
            chunk_metadata = {
                'source': metadata.source_name,
                'section': section_number,
                'jurisdiction': metadata.jurisdiction,
                'year': metadata.year,
                'document_type': metadata.document_type,
                'chunk_id': f"{metadata.file_name.replace('.pdf', '')}_chunk_{i}",
                'file_name': metadata.file_name
            }
            
            # Create DocumentChunk
            chunk = DocumentChunk.from_text(
                text=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_metadata['chunk_id']
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_section_number(self, text: str, section_type: str) -> str:
        """Extract section/article number from text.
        
        Args:
            text: Chunk text
            section_type: Type of section (legal, treaty, regulation)
            
        Returns:
            Section number as string
        """
        if section_type == 'legal':
            match = re.search(r'Section\s+(\d+[A-Za-z]*)', text, re.IGNORECASE)
            if match:
                return f"Section {match.group(1)}"
        elif section_type == 'treaty':
            match = re.search(r'Article\s+(\d+[A-Za-z]*)', text, re.IGNORECASE)
            if match:
                return f"Article {match.group(1)}"
        elif section_type == 'regulation':
            match = re.search(r'Regulation\s+(\d+[A-Za-z]*)', text, re.IGNORECASE)
            if match:
                return f"Regulation {match.group(1)}"
            match = re.search(r'Schedule\s+([IVX]+)', text, re.IGNORECASE)
            if match:
                return f"Schedule {match.group(1)}"
        
        return "General"
    
    def chunk_with_tables(self, text: str, metadata: DocumentMetadata) -> List[DocumentChunk]:
        """Special chunking for documents with tables (like FSSAI regulations).
        
        Args:
            text: Full text content
            metadata: DocumentMetadata object
            
        Returns:
            List of DocumentChunk objects with tables preserved
        """
        # Identify table sections (markdown tables)
        table_pattern = r'\|.*\|.*\n\|[-:]+\|.*\n(?:\|.*\|.*\n)+'
        tables = re.findall(table_pattern, text, re.MULTILINE)
        
        # Split text by tables
        non_table_text = re.sub(table_pattern, '<<TABLE>>', text)
        non_table_chunks = self.chunk_by_headers(non_table_text)
        
        chunks = []
        table_index = 0
        
        for chunk_text in non_table_chunks:
            if '<<TABLE>>' in chunk_text and table_index < len(tables):
                # Replace table marker with actual table
                chunk_text = chunk_text.replace('<<TABLE>>', tables[table_index], 1)
                table_index += 1
            
            # Create chunk metadata
            chunk_metadata = {
                'source': metadata.source_name,
                'section': self._extract_section_number(chunk_text, 'regulation'),
                'jurisdiction': metadata.jurisdiction,
                'year': metadata.year,
                'document_type': metadata.document_type,
                'chunk_id': f"{metadata.file_name.replace('.pdf', '')}_chunk_{len(chunks)}",
                'file_name': metadata.file_name,
                'contains_table': '<<TABLE>>' in chunk_text or table_index > 0
            }
            
            chunk = DocumentChunk.from_text(
                text=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_metadata['chunk_id']
            )
            chunks.append(chunk)
        
        return chunks
    
    def process_document(
        self,
        text: str,
        metadata: DocumentMetadata,
        preserve_tables: bool = False
    ) -> List[DocumentChunk]:
        """Process document text into chunks based on metadata.
        
        Args:
            text: Full text content
            metadata: DocumentMetadata object
            preserve_tables: Whether to use special table-preserving chunking
            
        Returns:
            List of DocumentChunk objects
        """
        if preserve_tables and metadata.document_type == "Regulation":
            return self.chunk_with_tables(text, metadata)
        else:
            return self.create_chunks(text, metadata)