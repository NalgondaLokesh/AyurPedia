"""
Parser module for AyurPedia.
Handles PDF parsing using LlamaParse for document extraction.
"""

import os
from typing import Dict, Any, Optional
from llama_parse import LlamaParse
from app.models.document import DocumentMetadata


class Parser:
    """PDF parser using LlamaParse for document extraction."""
    
    def __init__(self, api_key: str) -> None:
        """Initialize LlamaParse client.
        
        Args:
            api_key: LlamaParse API key
        """
        self.parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",  # Return markdown format
            num_workers=4,  # Number of workers for parallel processing
            verbose=True,
            language="en"  # English language
        )
    
    def parse_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using LlamaParse.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as markdown string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If parsing fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Parse the PDF
            documents = self.parser.load_data(pdf_path)
            
            # Combine all pages into a single text
            if documents:
                full_text = "\n\n".join([doc.text for doc in documents])
                return full_text
            else:
                raise Exception("No content extracted from PDF")
                
        except Exception as e:
            raise Exception(f"Failed to parse PDF '{pdf_path}': {str(e)}")
    
    def parse_pdf_structured(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text with structure preserved (sections, tables).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with structured content:
            - text: Full text content
            - pages: List of page contents
            - metadata: Basic metadata
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If parsing fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Parse the PDF
            documents = self.parser.load_data(pdf_path)
            
            if not documents:
                raise Exception("No content extracted from PDF")
            
            # Extract structured information
            pages = []
            full_text_parts = []
            
            for i, doc in enumerate(documents):
                page_content = {
                    'page_number': i + 1,
                    'text': doc.text,
                    'metadata': doc.metadata if hasattr(doc, 'metadata') else {}
                }
                pages.append(page_content)
                full_text_parts.append(doc.text)
            
            full_text = "\n\n".join(full_text_parts)
            
            return {
                'text': full_text,
                'pages': pages,
                'total_pages': len(pages),
                'metadata': {
                    'file_name': os.path.basename(pdf_path),
                    'file_path': pdf_path
                }
            }
                
        except Exception as e:
            raise Exception(f"Failed to parse PDF with structure '{pdf_path}': {str(e)}")
    
    def get_document_metadata(self, pdf_path: str) -> DocumentMetadata:
        """Extract metadata from filename and content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            DocumentMetadata object with extracted information
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        file_name = os.path.basename(pdf_path)
        file_name_lower = file_name.lower()
        
        # Determine jurisdiction based on filename
        jurisdiction = "International"  # Default
        if any(keyword in file_name_lower for keyword in ['india', 'patents_act', 'biological_diversity', 'fssai']):
            jurisdiction = "India"
        
        # Determine document type
        document_type = "Act"  # Default
        if 'treaty' in file_name_lower or 'protocol' in file_name_lower:
            document_type = "Treaty"
        elif 'regulation' in file_name_lower or 'regulations' in file_name_lower:
            document_type = "Regulation"
        elif 'agreement' in file_name_lower:
            document_type = "Agreement"
        
        # Extract year from filename
        year = 2000  # Default year
        import re
        year_match = re.search(r'19\d{2}|20\d{2}', file_name)
        if year_match:
            year = int(year_match.group())
        
        # Generate source name from filename
        source_name = file_name.replace('.pdf', '').replace('_', ' ').title()
        
        # Determine citation format based on document type
        citation_format = ""
        if jurisdiction == "India":
            if document_type == "Act":
                citation_format = f"Act No. X of {year}"
            elif document_type == "Regulation":
                citation_format = f"FSSAI Regulation {year}"
        else:
            if document_type == "Treaty":
                citation_format = f"International Treaty {year}"
            elif document_type == "Agreement":
                citation_format = f"International Agreement {year}"
        
        return DocumentMetadata(
            source_name=source_name,
            jurisdiction=jurisdiction,
            document_type=document_type,
            year=year,
            citation_format=citation_format,
            file_name=file_name
        )
    
    def parse_and_extract(self, pdf_path: str) -> Dict[str, Any]:
        """Parse PDF and extract both text and metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with:
            - text: Extracted text content
            - metadata: DocumentMetadata object
            - pages: List of page contents (if structured parsing)
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If parsing fails
        """
        # Get metadata
        metadata = self.get_document_metadata(pdf_path)
        
        # Parse with structure
        structured_content = self.parse_pdf_structured(pdf_path)
        
        return {
            'text': structured_content['text'],
            'metadata': metadata,
            'pages': structured_content['pages'],
            'total_pages': structured_content['total_pages']
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        artifacts = [
            '\x0c',  # Form feed
            '\ufeff',  # BOM
        ]
        
        for artifact in artifacts:
            text = text.replace(artifact, '')
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()