"""
Hierarchical retrieval helper for parent-child chunk expansion.

Provides a shared implementation for expanding child chunks to their parent
context, used by both Retriever and HybridRetriever to ensure consistent
behavior across the codebase.
"""

import logging
from typing import List, Set, Optional
from ..models.document import DocumentChunk, CHUNK_TYPE_PARENT, CHUNK_TYPE_CHILD

logger = logging.getLogger(__name__)


def expand_to_parents(
    child_chunks: List[DocumentChunk],
    all_chunks: Optional[List[DocumentChunk]] = None,
    qdrant_db=None,
    collection_name: Optional[str] = None,
    fail_open: bool = True
) -> List[DocumentChunk]:
    """Expand child chunks to their parent chunks for context.

    When child chunks are matched during retrieval, we want to return the
    larger parent chunks to the LLM for better context. This function:
    1. Collects unique parent IDs from matched children
    2. Retrieves parent chunks (from provided list or Qdrant)
    3. Deduplicates by parent ID
    4. Returns parent chunks with scores inherited from their children

    Args:
        child_chunks: List of child chunks that were matched
        all_chunks: Optional list of all chunks (for in-memory parent lookup)
        qdrant_db: Optional QdrantDB instance for parent retrieval
        collection_name: Collection name to retrieve parents from
        fail_open: If True, return original chunks on failure rather than raising

    Returns:
        List of parent DocumentChunk objects, deduplicated by ID
    """
    if not child_chunks:
        return []

    # Separate child chunks from any mixed results
    children = [c for c in child_chunks if c.chunk_type == CHUNK_TYPE_CHILD]
    if not children:
        # No child chunks, return as-is (might already be parents)
        return child_chunks

    # Collect unique parent IDs
    parent_ids: Set[str] = set()
    for child in children:
        if child.parent_id:
            parent_ids.add(child.parent_id)

    if not parent_ids:
        logger.warning("Child chunks have no parent_id references")
        if fail_open:
            return child_chunks
        return []

    # Retrieve parent chunks
    parents: List[DocumentChunk] = []
    
    # Try in-memory lookup first if all_chunks provided
    if all_chunks:
        parent_map = {c.id: c for c in all_chunks if c.chunk_type == CHUNK_TYPE_PARENT}
        for parent_id in parent_ids:
            if parent_id in parent_map:
                parents.append(parent_map[parent_id])
            else:
                logger.warning(f"Parent {parent_id} not found in all_chunks")
    
    # Fall back to Qdrant retrieval if needed
    if len(parents) < len(parent_ids) and qdrant_db and collection_name:
        missing_ids = parent_ids - {p.id for p in parents}
        if missing_ids:
            try:
                retrieved = qdrant_db.retrieve_points(collection_name, list(missing_ids))
                for record in retrieved:
                    parent_chunk = DocumentChunk.from_payload(
                        record['payload'],
                        point_id=record['id']
                    )
                    if parent_chunk.chunk_type == CHUNK_TYPE_PARENT:
                        parents.append(parent_chunk)
            except Exception as e:
                logger.error(f"Failed to retrieve parents from Qdrant: {e}")
                if not fail_open:
                    raise

    if not parents:
        logger.warning("No parent chunks retrieved")
        if fail_open:
            return child_chunks
        return []

    # Deduplicate by parent ID
    seen_ids: Set[str] = set()
    unique_parents: List[DocumentChunk] = []
    for parent in parents:
        if parent.id not in seen_ids:
            seen_ids.add(parent.id)
            unique_parents.append(parent)

    # Score parents based on their children's scores
    for parent in unique_parents:
        parent_children = [c for c in children if c.parent_id == parent.id]
        if parent_children:
            # Use the best child score for the parent
            best_child_score = max(c.metadata.get('score', 0.0) for c in parent_children)
            parent.metadata['score'] = best_child_score
            parent.metadata['original_score'] = parent.metadata.get('score', 0.0)
            # Track which children contributed
            parent.metadata['matched_child_ids'] = [c.id for c in parent_children]

    # Sort by score (highest first)
    unique_parents.sort(key=lambda x: x.metadata.get('score', 0.0), reverse=True)

    logger.info(f"Expanded {len(children)} child chunks to {len(unique_parents)} parent chunks")
    return unique_parents


def filter_by_chunk_type(
    chunks: List[DocumentChunk],
    chunk_types: List[str]
) -> List[DocumentChunk]:
    """Filter chunks by their chunk_type field.

    Args:
        chunks: List of chunks to filter
        chunk_types: List of chunk types to keep (e.g., ['child', 'parent'])

    Returns:
        Filtered list of chunks
    """
    return [c for c in chunks if c.chunk_type in chunk_types]


def validate_parent_child_relationships(
    chunks: List[DocumentChunk]
) -> dict:
    """Validate that parent-child relationships are consistent.

    Args:
        chunks: List of chunks to validate

    Returns:
        Dictionary with validation results and any errors found
    """
    parents = {c.id: c for c in chunks if c.chunk_type == CHUNK_TYPE_PARENT}
    children = [c for c in chunks if c.chunk_type == CHUNK_TYPE_CHILD]
    errors: List[str] = []

    # Check that all children have valid parent references
    for child in children:
        if not child.parent_id:
            errors.append(f"Child {c.metadata.get('chunk_id', child.id)} has no parent_id")
        elif child.parent_id not in parents:
            errors.append(
                f"Child {c.metadata.get('chunk_id', child.id)} references "
                f"unknown parent {child.parent_id}"
            )

    # Check that all parents have back-links to their children
    for parent in parents.values():
        for child_id in parent.child_ids:
            child_exists = any(c.id == child_id for c in children)
            if not child_exists:
                errors.append(
                    f"Parent {parent.metadata.get('chunk_id', parent.id)} links to "
                    f"missing child {child_id}"
                )

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'parent_count': len(parents),
        'child_count': len(children)
    }
