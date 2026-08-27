"""
Main ingestion script for AyurPedia Phase 1.
Processes PDF documents, creates chunks, generates embeddings, and loads into Qdrant.
"""

import os
import sys
import time
import argparse
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import get_config
from app.core.database import QdrantDB
from app.ingestion.parser import Parser
from app.ingestion.chunker import Chunker
from app.ingestion.embedder import Embedder
from app.ingestion.loader import DocumentLoader
from app.models.document import DocumentProcessingResult, IngestionSummary


# Document mapping configuration
DOCUMENT_MAPPING = {
    'India': {
        'patents_act_1970.pdf': 'Patents Act 1970',
        'biological_diversity_act_2002.pdf': 'Biological Diversity Act 2002',
        'FSSAI_Ayurveda_Aahar_Regulations_2022.pdf': 'FSSAI Ayurveda Aahar Regulations 2022'
    },
    'International': {
        'wipo_gratk_treaty_2024.pdf': 'WIPO GRATK Treaty 2024',
        'trips_agreement_official.pdf': 'TRIPS Agreement',
        'nagoya_protocol_en.pdf': 'Nagoya Protocol'
    }
}


def print_header() -> None:
    """Print ingestion header."""
    print("\n" + "="*60)
    print("Starting AyurPedia Ingestion Phase 1...")
    print("="*60 + "\n")


def print_section(title: str) -> None:
    """Print section header.
    
    Args:
        title: Section title
    """
    print("\n" + "="*60)
    print(title)
    print("="*60 + "\n")


def process_pdf(
    pdf_path: str,
    source_name: str,
    collection_name: str,
    parser: Parser,
    chunker: Chunker,
    loader: DocumentLoader,
    qdrant_db: QdrantDB,
    skip_if_exists: bool = True
) -> DocumentProcessingResult:
    """Process a single PDF document.
    
    Args:
        pdf_path: Path to the PDF file
        source_name: Human-readable name of the document
        collection_name: Name of the Qdrant collection
        parser: Parser instance
        chunker: Chunker instance
        loader: DocumentLoader instance
        qdrant_db: QdrantDB instance for checking existing documents
        skip_if_exists: Whether to skip processing if document already exists
        
    Returns:
        DocumentProcessingResult with processing statistics
    """
    start_time = time.time()
    file_name = os.path.basename(pdf_path)
    
    # Check if document already exists and skip if enabled
    if skip_if_exists:
        if qdrant_db.document_exists(collection_name, file_name):
            print(f"  SKIP Document already exists in collection")
            return DocumentProcessingResult(
                source_name=source_name,
                file_name=file_name,
                pages_extracted=0,
                chunks_created=0,
                embeddings_generated=0,
                chunks_stored=0,
                collection_name=collection_name,
                processing_time_seconds=0,
                success=True,
                error_message=None
            )
    
    try:
        print(f"[{file_name}]")
        print(f"-> Parsing...")
        
        # Parse PDF
        parsed_data = parser.parse_and_extract(pdf_path)
        pages_extracted = parsed_data['total_pages']
        print(f"  OK {pages_extracted} pages extracted")
        
        # Create chunks
        print(f"-> Chunking...")
        metadata = parsed_data['metadata']
        chunks = chunker.create_chunks(parsed_data['text'], metadata)
        chunks_created = len(chunks)
        print(f"  OK {chunks_created} chunks created")
        
        # Generate embeddings and load
        print(f"-> Embedding & Loading...")
        loading_result = loader.load_single_document(chunks, collection_name, source_name)
        
        processing_time = time.time() - start_time
        
        return DocumentProcessingResult(
            source_name=source_name,
            file_name=file_name,
            pages_extracted=pages_extracted,
            chunks_created=chunks_created,
            embeddings_generated=loading_result['loaded_chunks'],
            chunks_stored=loading_result['loaded_chunks'],
            collection_name=collection_name,
            processing_time_seconds=processing_time,
            success=loading_result['success'],
            error_message=None
        )
        
    except FileNotFoundError as e:
        processing_time = time.time() - start_time
        print(f"  FAIL File not found: {str(e)}")
        return DocumentProcessingResult(
            source_name=source_name,
            file_name=file_name,
            pages_extracted=0,
            chunks_created=0,
            embeddings_generated=0,
            chunks_stored=0,
            collection_name=collection_name,
            processing_time_seconds=processing_time,
            success=False,
            error_message=str(e) if e else "File not found"
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"  FAIL Processing failed: {str(e)}")
        return DocumentProcessingResult(
            source_name=source_name,
            file_name=file_name,
            pages_extracted=0,
            chunks_created=0,
            embeddings_generated=0,
            chunks_stored=0,
            collection_name=collection_name,
            processing_time_seconds=processing_time,
            success=False,
            error_message=str(e) if e else "Processing failed"
        )


def main() -> None:
    """Main ingestion function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AyurPedia Document Ingestion')
    parser.add_argument('--recreate', action='store_true', 
                       help='Delete and recreate Qdrant collections before ingestion')
    parser.add_argument('--parent-overlap', type=int, default=None,
                       help='Override parent chunk overlap from config')
    args = parser.parse_args()
    
    print_header()
    
    # Load configuration
    config = get_config()
    
    # Override parent_overlap if provided
    parent_overlap = args.parent_overlap if args.parent_overlap is not None else config.parent_overlap
    
    # Initialize components
    print("Initializing components...")
    parser = Parser(api_key=config.llamaparse_api_key)
    chunker = Chunker(
        parent_chunk_size=config.parent_chunk_size,
        child_chunk_size=config.child_chunk_size,
        chunk_overlap=config.chunk_overlap,
        parent_overlap=parent_overlap
    )
    embedder = Embedder(api_key=config.cohere_api_key)
    qdrant_db = QdrantDB(
        url=config.qdrant_url,
        api_key=config.qdrant_api_key,
        embedding_dimension=config.embedding_dimension,
        batch_size=config.batch_size
    )
    loader = DocumentLoader(qdrant_db=qdrant_db, embedder=embedder)
    
    print("OK Components initialized successfully\n")
    
    # Create Qdrant collections
    print_section("Creating Qdrant Collections")
    collections = [config.india_collection, config.international_collection]
    qdrant_db.create_collections(collections, recreate=args.recreate)
    print(f"OK Qdrant collections created: {', '.join(collections)}")
    
    # Process PDFs
    print_section("Processing PDFs")
    
    # Check which documents are already processed
    print("Checking for already processed documents...")
    india_processed = qdrant_db.get_processed_documents(config.india_collection)
    international_processed = qdrant_db.get_processed_documents(config.international_collection)
    
    print(f"India collection: {len(india_processed)} documents already processed")
    print(f"International collection: {len(international_processed)} documents already processed")
    
    document_results = []
    total_chunks = 0
    india_chunks = 0
    international_chunks = 0
    
    # Get data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    data_dir = os.path.abspath(data_dir)
    
    # Process India documents
    print("\n--- India Documents ---")
    for pdf_file, source_name in DOCUMENT_MAPPING['India'].items():
        pdf_path = os.path.join(data_dir, pdf_file)
        pdf_path = os.path.abspath(pdf_path)
        result = process_pdf(
            pdf_path=pdf_path,
            source_name=source_name,
            collection_name=config.india_collection,
            parser=parser,
            chunker=chunker,
            loader=loader,
            qdrant_db=qdrant_db,
            skip_if_exists=False
        )
        document_results.append(result)
        
        if result.success:
            total_chunks += result.chunks_stored
            india_chunks += result.chunks_stored
            if result.chunks_stored > 0:
                print(f"  -> OK {result.chunks_stored} chunks stored ({config.india_collection})")
        else:
            print(f"  -> FAIL Failed: {result.error_message}")
    
    # Process International documents
    print("\n--- International Documents ---")
    for pdf_file, source_name in DOCUMENT_MAPPING['International'].items():
        pdf_path = os.path.join(data_dir, pdf_file)
        pdf_path = os.path.abspath(pdf_path)
        result = process_pdf(
            pdf_path=pdf_path,
            source_name=source_name,
            collection_name=config.international_collection,
            parser=parser,
            chunker=chunker,
            loader=loader,
            qdrant_db=qdrant_db,
            skip_if_exists=False
        )
        document_results.append(result)
        
        if result.success:
            total_chunks += result.chunks_stored
            international_chunks += result.chunks_stored
            if result.chunks_stored > 0:
                print(f"  -> OK {result.chunks_stored} chunks stored ({config.international_collection})")
        else:
            print(f"  -> FAIL Failed: {result.error_message}")
    
    # Print final summary
    print_section("INGESTION COMPLETE")
    
    # Calculate total processing time
    total_time = sum(result.processing_time_seconds for result in document_results)
    
    print("Summary:")
    print(f"├─ Total chunks: {total_chunks}")
    print(f"├─ India collection: {india_chunks} chunks")
    print(f"├─ International collection: {international_chunks} chunks")
    print(f"├─ Vector dimension: {config.embedding_dimension}")
    print(f"└─ Storage: Qdrant Cloud ({config.qdrant_url})")
    
    print("\nCollection Status:")
    india_info = qdrant_db.get_collection_info(config.india_collection)
    international_info = qdrant_db.get_collection_info(config.international_collection)
    
    if india_info:
        print(f"├─ {config.india_collection}: OK Active ({india_info['points_count']} vectors)")
    else:
        print(f"├─ {config.india_collection}: FAIL Not accessible")
    
    if international_info:
        print(f"└─ {config.international_collection}: OK Active ({international_info['points_count']} vectors)")
    else:
        print(f"└─ {config.international_collection}: FAIL Not accessible")
    
    print(f"\nTime taken: {total_time:.1f}s ({total_time/60:.1f}m)")
    
    # Create ingestion summary
    summary = IngestionSummary(
        total_documents_processed=len(document_results),
        total_chunks=total_chunks,
        india_collection_chunks=india_chunks,
        international_collection_chunks=international_chunks,
        vector_dimension=config.embedding_dimension,
        storage_url=config.qdrant_url,
        processing_time_seconds=total_time,
        document_results=document_results
    )
    
    print("\n" + "="*60)
    print("SUCCESS INGESTION COMPLETE!")
    print("="*60 + "\n")
    
    return summary


if __name__ == "__main__":
    try:
        summary = main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nIngestion interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFAIL Ingestion failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)