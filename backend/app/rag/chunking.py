"""
Advanced document chunking strategies for improved retrieval precision and recall.
"""

import logging
from typing import List, Dict, Any, Optional
import re


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalDocumentChunker:
    """Specialized chunker for legal documents with semantic awareness."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize legal document chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"LegalDocumentChunker initialized (size: {chunk_size}, overlap: {chunk_overlap})")
    
    def chunk_document(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk a legal document with semantic boundaries.
        
        Args:
            text: Document text to chunk
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        logger.info(f"Chunking document: {metadata.get('source', 'Unknown')}")
        
        # Use semantic chunking for legal documents
        chunks = self._semantic_chunking(text, metadata)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _semantic_chunking(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk document based on semantic boundaries (sections, paragraphs).
        
        Args:
            text: Document text
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # First, try to split by legal sections
        section_splits = self._split_by_sections(text)
        
        if len(section_splits) > 1:
            # Process each section separately
            for section_text, section_info in section_splits:
                section_chunks = self._chunk_section(section_text, section_info, metadata)
                chunks.extend(section_chunks)
        else:
            # Fall back to paragraph-based chunking
            chunks = self._chunk_by_paragraphs(text, metadata)
        
        # Ensure chunks are within size limits
        chunks = self._normalize_chunk_sizes(chunks)
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[tuple[str, Dict[str, Any]]]:
        """Split text by legal section boundaries.
        
        Args:
            text: Document text
            
        Returns:
            List of (section_text, section_info) tuples
        """
        sections = []
        
        # Legal section patterns
        section_patterns = [
            r'Section\s+\d+[a-z]?\s*[:\-\.]?',  # Section 3(p):
            r'\d+\.\s+',  # 1. 
            r'\([a-z]\)\s+',  # (a) 
            r'Article\s+\d+',  # Article 5
            r'Chapter\s+[IVX]+\s*[:\-\.]?',  # Chapter II:
            r'Part\s+[IVX]+\s*[:\-\.]?',  # Part IV:
        ]
        
        # Find all section boundaries
        section_boundaries = []
        for pattern in section_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                section_boundaries.append((match.start(), match.group()))
        
        # Sort by position
        section_boundaries.sort(key=lambda x: x[0])
        
        # Split text at boundaries
        if section_boundaries:
            prev_pos = 0
            for i, (pos, header) in enumerate(section_boundaries):
                if i > 0:
                    section_text = text[prev_pos:pos].strip()
                    if section_text:
                        prev_header = section_boundaries[i-1][1]
                        sections.append((section_text, {"section_header": prev_header}))
                prev_pos = pos
            
            # Add final section
            if prev_pos < len(text):
                final_section = text[prev_pos:].strip()
                if final_section:
                    final_header = section_boundaries[-1][1]
                    sections.append((final_section, {"section_header": final_header}))
        else:
            # No sections found, return entire text as single section
            sections.append((text, {"section_header": "Introduction"}))
        
        return sections
    
    def _chunk_section(self, section_text: str, section_info: Dict, doc_metadata: Dict) -> List[Dict[str, Any]]:
        """Chunk a section into appropriate-sized pieces.
        
        Args:
            section_text: Section text
            section_info: Section-specific information
            doc_metadata: Document metadata
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', section_text.strip())
        
        current_chunk = ""
        chunk_number = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if adding this paragraph would exceed chunk size
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunk_metadata = doc_metadata.copy()
                    chunk_metadata.update(section_info)
                    chunk_metadata.update({
                        "chunk_id": f"{doc_metadata.get('source', 'doc')}_{section_info.get('section_header', 'intro')}_{chunk_number}",
                        "chunk_number": chunk_number,
                        "chunk_type": "section"
                    })
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": chunk_metadata
                    })
                    chunk_number += 1
                
                # Start new chunk
                current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunk_metadata = doc_metadata.copy()
            chunk_metadata.update(section_info)
            chunk_metadata.update({
                "chunk_id": f"{doc_metadata.get('source', 'doc')}_{section_info.get('section_header', 'intro')}_{chunk_number}",
                "chunk_number": chunk_number,
                "chunk_type": "section"
            })
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def _chunk_by_paragraphs(self, text: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Fallback chunking by paragraphs when section splitting fails.
        
        Args:
            text: Document text
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        current_chunk = ""
        chunk_number = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk_id": f"{metadata.get('source', 'doc')}_para_{chunk_number}",
                        "chunk_number": chunk_number,
                        "chunk_type": "paragraph"
                    })
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": chunk_metadata
                    })
                    chunk_number += 1
                current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": f"{metadata.get('source', 'doc')}_para_{chunk_number}",
                "chunk_number": chunk_number,
                "chunk_type": "paragraph"
            })
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def _normalize_chunk_sizes(self, chunks: List[Dict]) -> List[Dict]:
        """Ensure all chunks are within size limits.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Normalized chunks
        """
        normalized = []
        
        for chunk in chunks:
            text = chunk["text"]
            metadata = chunk["metadata"]
            
            # If chunk is too large, split it further
            if len(text) > self.chunk_size * 1.5:  # Allow some flexibility
                sub_chunks = self._split_large_chunk(text, metadata)
                normalized.extend(sub_chunks)
            else:
                normalized.append(chunk)
        
        return normalized
    
    def _split_large_chunk(self, text: str, metadata: Dict) -> List[Dict]:
        """Split a chunk that's too large.
        
        Args:
            text: Chunk text
            metadata: Chunk metadata
            
        Returns:
            List of smaller chunks
        """
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        sub_chunk_number = 1
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    sub_metadata = metadata.copy()
                    sub_metadata["chunk_id"] += f"_sub{sub_chunk_number}"
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": sub_metadata
                    })
                    sub_chunk_number += 1
                current_chunk = sentence + " "
        
        # Add final chunk
        if current_chunk.strip():
            sub_metadata = metadata.copy()
            sub_metadata["chunk_id"] += f"_sub{sub_chunk_number}"
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": sub_metadata
            })
        
        return chunks


class MetadataEnricher:
    """Enrich document metadata for better retrieval."""
    
    def __init__(self):
        """Initialize metadata enricher."""
        self.legal_keywords = {
            "patent_law": ["patent", "invention", "claims", "novelty", "prior art", "inventive step"],
            "traditional_knowledge": ["traditional", "knowledge", "indigenous", "community", "folklore"],
            "regulatory": ["regulation", "compliance", "authority", "approval", "filing", "procedure"],
            "ayurvedic": ["ayurvedic", "herbal", "formulation", "medicine", "classical", "proprietary"],
            "international": ["wipo", "treaty", "convention", "international", "gratk", "trips"]
        }
    
    def enrich_metadata(self, metadata: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Enrich metadata with extracted information.
        
        Args:
            metadata: Original metadata
            text: Document text
            
        Returns:
            Enriched metadata
        """
        enriched = metadata.copy()
        text_lower = text.lower()
        
        # Add keyword categories
        for category, keywords in self.legal_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                enriched[f"keywords_{category}"] = True
        
        # Add text statistics
        enriched["text_length"] = len(text)
        enriched["word_count"] = len(text.split())
        
        # Add legal entity extraction (simplified)
        enriched["mentions_section"] = bool(re.search(r'section\s+\d+', text_lower))
        enriched["mentions_act"] = bool(re.search(r'act\s+\d{4}', text_lower))
        enriched["mentions_traditional_knowledge"] = any(kw in text_lower for kw in self.legal_keywords["traditional_knowledge"])
        
        return enriched