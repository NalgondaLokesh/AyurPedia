"""
Chunker module for AyurPedia.

Implements a hierarchical (parent-child) chunking strategy for legal documents,
treaties and regulations.

Strategy
--------
1. The document is split into large *parent* windows (default 2000 chars) that
   carry enough surrounding context for an LLM to reason over.
2. Each parent is then split into small *child* windows (default 400 chars).
   Children are always derived *from their own parent's text*, which means the
   parent-child relationship is correct by construction - there is no guessing.
3. Children are what get matched at query time (small = precise embeddings);
   the parent is what gets handed to the LLM (large = complete context).
   This is the classic "small-to-big" / parent-document retrieval pattern.

Every chunk records its absolute character span in the source document
(``start_char`` / ``end_char``) so ordering, de-duplication and context
stitching are all deterministic.

Chunk IDs are deterministic (UUIDv5 derived from file name + level + index) so
that re-ingesting the same document overwrites the same Qdrant points instead of
creating duplicates.
"""

import re
import uuid
from typing import List, Dict, Any, Optional, Tuple

from app.models.document import DocumentChunk, DocumentMetadata


# Stable namespace for deterministic chunk IDs. Never change this value or all
# previously ingested point IDs will change.
CHUNK_ID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "ayurpedia.chunks")

# Ordered break candidates used to avoid cutting a chunk mid-word/mid-sentence.
# Each entry is (delimiter, characters to keep before starting the next chunk).
_BREAK_CANDIDATES: Tuple[Tuple[str, int], ...] = (
    ("\n\n", 2),   # paragraph
    ("\n", 1),     # line
    (". ", 2),     # sentence
    ("; ", 2),     # clause
    (" ", 1),      # word
)

# Ordered (label, pattern) pairs for section detection. Order matters: the first
# match wins, so the most specific legal constructs are listed first.
_SECTION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("Section", r'Section\s+(\d+[A-Za-z]*(?:\(\d+\))?(?:\([a-z]\))?)'),
    ("Article", r'Article\s+(\d+[A-Za-z]*)'),
    ("Regulation", r'Regulation\s+(\d+[A-Za-z]*)'),
    ("Chapter", r'Chapter\s+([IVXLC]+|\d+[A-Za-z]*)'),
    ("Part", r'Part\s+([IVXLC]+|\d+[A-Za-z]*)'),
    ("Schedule", r'Schedule\s+([IVXLC]+|[A-Z]\b)'),
)

_GENERAL_SECTION = "General"


class Chunker:
    """Text chunker implementing hierarchical parent-child chunking."""

    def __init__(
        self,
        parent_chunk_size: int = 2000,
        child_chunk_size: int = 400,
        chunk_overlap: int = 100,
        parent_overlap: Optional[int] = None,
        boundary_search_ratio: float = 0.3,
    ) -> None:
        """Initialize chunker with hierarchical configuration.

        Args:
            parent_chunk_size: Maximum size of parent chunks in characters.
            child_chunk_size: Maximum size of child chunks in characters.
            chunk_overlap: Characters of overlap between sibling child chunks.
            parent_overlap: Characters of overlap between parent chunks.
                Defaults to ``chunk_overlap`` when not supplied.
            boundary_search_ratio: Fraction of the tail of a window that may be
                given up in order to land on a clean text boundary.

        Raises:
            ValueError: If sizes are non-positive or a child is larger than a
                parent (which would make the hierarchy meaningless).
        """
        if parent_chunk_size <= 0 or child_chunk_size <= 0:
            raise ValueError("parent_chunk_size and child_chunk_size must be positive")
        if child_chunk_size > parent_chunk_size:
            raise ValueError(
                f"child_chunk_size ({child_chunk_size}) must not exceed "
                f"parent_chunk_size ({parent_chunk_size})"
            )
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")

        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        # Clamp overlaps so the sliding window is always guaranteed to advance.
        self.chunk_overlap = min(chunk_overlap, child_chunk_size - 1)
        raw_parent_overlap = chunk_overlap if parent_overlap is None else parent_overlap
        self.parent_overlap = max(0, min(raw_parent_overlap, parent_chunk_size - 1))
        self.boundary_search_ratio = min(max(boundary_search_ratio, 0.0), 0.9)

    # ------------------------------------------------------------------
    # Core splitting primitives
    # ------------------------------------------------------------------

    def split_with_offsets(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[Tuple[str, int, int]]:
        """Split text into overlapping windows, preserving character offsets.

        Args:
            text: Text to split.
            chunk_size: Maximum window size in characters.
            overlap: Characters of overlap between consecutive windows.

        Returns:
            List of ``(chunk_text, start_char, end_char)`` tuples where the
            offsets index into ``text`` and ``text[start:end] == chunk_text``.
        """
        if not text:
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        # Guarantee forward progress even with a pathological overlap value.
        overlap = max(0, min(overlap, chunk_size - 1))

        spans: List[Tuple[str, int, int]] = []
        length = len(text)
        start = 0

        while start < length:
            hard_end = min(start + chunk_size, length)

            # Only hunt for a nicer boundary if we are not at the very end.
            end = hard_end if hard_end >= length else self._find_break(text, start, hard_end)

            window = text[start:end]
            stripped = window.strip()
            if stripped:
                lead = len(window) - len(window.lstrip())
                abs_start = start + lead
                spans.append((stripped, abs_start, abs_start + len(stripped)))

            if end >= length:
                break

            next_start = end - overlap
            if next_start <= start:
                # Overlap would stall or rewind the window; force progress.
                next_start = start + 1
            start = next_start

        return spans

    def _find_break(self, text: str, start: int, hard_end: int) -> int:
        """Find a clean break position at or before ``hard_end``.

        Args:
            text: Text being split.
            start: Start offset of the current window.
            hard_end: Maximum allowed end offset.

        Returns:
            Offset to end the current window at. Falls back to ``hard_end`` when
            no suitable boundary exists in the search window.
        """
        span = hard_end - start
        search_floor = max(start + 1, hard_end - int(span * self.boundary_search_ratio))

        for delimiter, keep in _BREAK_CANDIDATES:
            index = text.rfind(delimiter, search_floor, hard_end)
            if index != -1:
                return index + keep

        return hard_end

    def chunk_text(self, text: str, chunk_size: Optional[int] = None) -> List[str]:
        """Split text into overlapping chunks of a given size.

        Retained for backwards compatibility; prefer :meth:`split_with_offsets`
        when offsets are needed.

        Args:
            text: Full text content.
            chunk_size: Optional custom size, defaults to ``parent_chunk_size``.

        Returns:
            List of overlapping text chunks.
        """
        size = self.parent_chunk_size if chunk_size is None else chunk_size
        overlap = self.chunk_overlap if size <= self.child_chunk_size else self.parent_overlap
        return [chunk for chunk, _, _ in self.split_with_offsets(text, size, overlap)]

    # ------------------------------------------------------------------
    # Hierarchical chunking
    # ------------------------------------------------------------------

    def create_hierarchical_chunks(
        self,
        text: str,
        metadata: DocumentMetadata,
    ) -> List[DocumentChunk]:
        """Create hierarchical parent-child DocumentChunk objects.

        Parents tile the document once. Children are then carved out of each
        parent's own text, so ``child.parent_id`` is exact rather than inferred.

        Args:
            text: Full text content of the document.
            metadata: DocumentMetadata describing the source document.

        Returns:
            Flat list of DocumentChunk objects ordered parent-then-its-children.
            Parents carry ``chunk_type='parent'``, children ``chunk_type='child'``.
        """
        if not text or not text.strip():
            return []

        stem = self._document_stem(metadata)
        parent_spans = self.split_with_offsets(
            text, self.parent_chunk_size, self.parent_overlap
        )

        chunks: List[DocumentChunk] = []
        child_counter = 0

        for parent_index, (parent_text, parent_start, parent_end) in enumerate(parent_spans):
            parent_section = self._extract_section_number_simple(parent_text)
            parent_chunk_ref = f"{stem}_parent_{parent_index}"
            parent_id = self._make_chunk_id(stem, "parent", parent_index)

            parent = DocumentChunk(
                id=parent_id,
                text=parent_text,
                metadata=self._build_metadata(
                    metadata,
                    section=parent_section,
                    chunk_ref=parent_chunk_ref,
                ),
                chunk_type="parent",
                hierarchy_level=0,
                chunk_index=parent_index,
                start_char=parent_start,
                end_char=parent_end,
            )

            child_spans = self.split_with_offsets(
                parent_text, self.child_chunk_size, self.chunk_overlap
            )

            # A parent shorter than one child window is its own leaf; emitting a
            # child that duplicates it verbatim would double embedding cost for
            # zero recall benefit.
            if len(child_spans) == 1 and child_spans[0][0] == parent_text:
                chunks.append(parent)
                continue

            children: List[DocumentChunk] = []
            for child_text, local_start, local_end in child_spans:
                child_section = self._extract_section_number_simple(child_text)
                if child_section == _GENERAL_SECTION:
                    # Inherit the parent's section so citations stay meaningful
                    # for fragments that do not restate their own heading.
                    child_section = parent_section

                child_chunk_ref = f"{stem}_child_{child_counter}"
                child_id = self._make_chunk_id(stem, "child", child_counter)

                child_metadata = self._build_metadata(
                    metadata,
                    section=child_section,
                    chunk_ref=child_chunk_ref,
                )
                child_metadata["parent_chunk_id"] = parent_chunk_ref

                children.append(
                    DocumentChunk(
                        id=child_id,
                        text=child_text,
                        metadata=child_metadata,
                        parent_id=parent_id,
                        chunk_type="child",
                        hierarchy_level=1,
                        chunk_index=child_counter,
                        # Convert parent-relative offsets to document-absolute.
                        start_char=parent_start + local_start,
                        end_char=parent_start + local_end,
                    )
                )
                parent.child_ids.append(child_id)
                child_counter += 1

            chunks.append(parent)
            chunks.extend(children)

        return chunks

    def create_chunks(
        self,
        text: str,
        metadata: DocumentMetadata,
    ) -> List[DocumentChunk]:
        """Create DocumentChunk objects using the hierarchical strategy.

        Args:
            text: Full text content.
            metadata: DocumentMetadata object.

        Returns:
            List of DocumentChunk objects.
        """
        return self.create_hierarchical_chunks(text, metadata)

    def process_document(
        self,
        text: str,
        metadata: DocumentMetadata,
        preserve_tables: bool = False,
    ) -> List[DocumentChunk]:
        """Process document text into hierarchical chunks.

        Args:
            text: Full text content.
            metadata: DocumentMetadata object.
            preserve_tables: Deprecated, retained for signature compatibility.

        Returns:
            List of DocumentChunk objects.
        """
        return self.create_chunks(text, metadata)

    # ------------------------------------------------------------------
    # Hierarchy helpers / diagnostics
    # ------------------------------------------------------------------

    @staticmethod
    def _document_stem(metadata: DocumentMetadata) -> str:
        """Derive a stable document key from metadata.

        Args:
            metadata: DocumentMetadata object.

        Returns:
            File name without extension, falling back to the source name.
        """
        base = metadata.file_name or metadata.source_name or "document"
        return re.sub(r"\.pdf$", "", base, flags=re.IGNORECASE)

    @staticmethod
    def _make_chunk_id(stem: str, level: str, index: int) -> str:
        """Build a deterministic UUIDv5 chunk ID.

        Using UUIDv5 keeps IDs valid Qdrant point IDs while making them stable
        across runs, so re-ingestion upserts in place instead of duplicating.

        Args:
            stem: Document stem (file name without extension).
            level: Either ``'parent'`` or ``'child'``.
            index: Ordinal of the chunk within its level.

        Returns:
            Deterministic UUID string.
        """
        return str(uuid.uuid5(CHUNK_ID_NAMESPACE, f"{stem}|{level}|{index}"))

    @staticmethod
    def _build_metadata(
        metadata: DocumentMetadata,
        section: str,
        chunk_ref: str,
    ) -> Dict[str, Any]:
        """Build the per-chunk metadata dictionary.

        Args:
            metadata: Source document metadata.
            section: Detected section label for this chunk.
            chunk_ref: Human readable chunk reference.

        Returns:
            Metadata dictionary for a DocumentChunk.
        """
        return {
            "source": metadata.source_name,
            "section": section,
            "jurisdiction": metadata.jurisdiction,
            "year": metadata.year,
            "document_type": metadata.document_type,
            "chunk_id": chunk_ref,
            "file_name": metadata.file_name,
        }

    def validate_hierarchy(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Validate structural invariants of a hierarchical chunk list.

        Args:
            chunks: Chunks produced by :meth:`create_hierarchical_chunks`.

        Returns:
            Dictionary with an ``errors`` list plus counts. An empty ``errors``
            list means the hierarchy is internally consistent.
        """
        parents = {c.id: c for c in chunks if c.chunk_type == "parent"}
        children = [c for c in chunks if c.chunk_type == "child"]
        errors: List[str] = []

        ids = [c.id for c in chunks]
        if len(ids) != len(set(ids)):
            errors.append("duplicate chunk IDs detected")

        for child in children:
            if not child.parent_id:
                errors.append(f"child {child.metadata.get('chunk_id')} has no parent_id")
                continue
            parent = parents.get(child.parent_id)
            if parent is None:
                errors.append(
                    f"child {child.metadata.get('chunk_id')} references unknown "
                    f"parent {child.parent_id}"
                )
                continue
            if child.id not in parent.child_ids:
                errors.append(
                    f"parent {parent.metadata.get('chunk_id')} is missing back-link "
                    f"to child {child.metadata.get('chunk_id')}"
                )
            if child.text not in parent.text:
                errors.append(
                    f"child {child.metadata.get('chunk_id')} text is not contained "
                    f"in parent {parent.metadata.get('chunk_id')}"
                )
            if not (parent.start_char <= child.start_char and child.end_char <= parent.end_char):
                errors.append(
                    f"child {child.metadata.get('chunk_id')} span "
                    f"[{child.start_char},{child.end_char}) escapes parent span "
                    f"[{parent.start_char},{parent.end_char})"
                )

        for parent in parents.values():
            for child_id in parent.child_ids:
                if child_id not in {c.id for c in children}:
                    errors.append(
                        f"parent {parent.metadata.get('chunk_id')} links to missing "
                        f"child {child_id}"
                    )

        return {
            "valid": not errors,
            "errors": errors,
            "parents": len(parents),
            "children": len(children),
        }

    def get_chunk_stats(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Compute size and coverage statistics for a chunk list.

        Args:
            chunks: Chunks to summarise.

        Returns:
            Dictionary of statistics useful for tuning and regression checks.
        """
        parents = [c for c in chunks if c.chunk_type == "parent"]
        children = [c for c in chunks if c.chunk_type == "child"]

        def _avg(items: List[DocumentChunk]) -> float:
            return round(sum(len(c.text) for c in items) / len(items), 1) if items else 0.0

        orphans = sum(1 for c in children if not c.parent_id)
        childless = sum(1 for p in parents if not p.child_ids)

        return {
            "total_chunks": len(chunks),
            "parent_chunks": len(parents),
            "child_chunks": len(children),
            "orphan_children": orphans,
            "childless_parents": childless,
            "avg_parent_chars": _avg(parents),
            "avg_child_chars": _avg(children),
            "max_parent_chars": max((len(c.text) for c in parents), default=0),
            "max_child_chars": max((len(c.text) for c in children), default=0),
            "avg_children_per_parent": (
                round(len(children) / len(parents), 2) if parents else 0.0
            ),
            "total_embedded_chars": sum(len(c.text) for c in chunks),
        }

    # ------------------------------------------------------------------
    # Section / structure detection
    # ------------------------------------------------------------------

    def detect_section_type(self, text: str) -> str:
        """Determine the document type based on text structure.

        Args:
            text: Text content to inspect.

        Returns:
            One of ``'legal'``, ``'treaty'``, ``'regulation'``, ``'general'``.
        """
        text_lower = text.lower()

        if re.search(r'section\s+\d+', text_lower):
            return 'legal'
        if re.search(r'article\s+\d+', text_lower):
            return 'treaty'
        if re.search(r'regulation\s+\d+|schedule\s+[ivx]+', text_lower):
            return 'regulation'
        return 'general'

    def _extract_section_number_simple(self, text: str) -> str:
        """Extract a section/article label from text.

        Args:
            text: Chunk text.

        Returns:
            Label such as ``'Section 3(p)'`` or ``'General'`` when none found.
        """
        for label, pattern in _SECTION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{label} {match.group(1)}"

        numbered = re.search(r'(?:^|\n)\s*(\d+[A-Za-z]*)\.\s+', text)
        if numbered:
            return f"Point {numbered.group(1)}"

        return _GENERAL_SECTION

    def _extract_section_number(self, text: str, section_type: str) -> str:
        """Extract a section label constrained to a document type.

        Args:
            text: Chunk text.
            section_type: One of ``'legal'``, ``'treaty'``, ``'regulation'``.

        Returns:
            Section label, or ``'General'`` when no match is found.
        """
        allowed = {
            'legal': ("Section",),
            'treaty': ("Article",),
            'regulation': ("Regulation", "Schedule"),
        }.get(section_type, ())

        for label, pattern in _SECTION_PATTERNS:
            if label not in allowed:
                continue
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{label} {match.group(1)}"

        return _GENERAL_SECTION

    def chunk_by_sections(self, text: str) -> List[str]:
        """Split text on legal section headers, keeping each header with its body.

        Args:
            text: Full text content.

        Returns:
            List of section-based chunks.
        """
        section_pattern = r'(?:Section|Article|Regulation|Chapter|Part)\s+\d+[A-Za-z]*\.?\s+'

        matches = list(re.finditer(section_pattern, text))
        if not matches:
            return [text] if text.strip() else []

        chunks: List[str] = []

        preamble = text[: matches[0].start()].strip()
        if preamble:
            chunks.append(preamble)

        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.start():end].strip()
            if body:
                chunks.append(body)

        return chunks

    def chunk_by_headers(self, text: str) -> List[str]:
        """Split text on all-caps headers.

        Args:
            text: Full text content.

        Returns:
            List of header-based chunks.
        """
        header_pattern = r'^[A-Z][A-Z\s]{3,}:\s*$'

        chunks: List[str] = []
        current_chunk: List[str] = []

        for line in text.split('\n'):
            if re.match(header_pattern, line.strip()) and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
            current_chunk.append(line)

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks if chunks else [text]
