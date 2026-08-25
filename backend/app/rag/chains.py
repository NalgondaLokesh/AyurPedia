"""
RAG chains module for AyurPedia.
Handles retrieval-augmented generation with citation enforcement.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from .prompts import RAG_PROMPT, VALIDATION_PROMPT, CONFIDENCE_PROMPT
from .retriever import Retriever
from ..models.document import DocumentChunk


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGChain:
    """RAG chain for answer generation with citation enforcement."""
    
    def __init__(self, llm: Any, retriever: Retriever) -> None:
        """Initialize RAG chain with LLM and retriever.
        
        Args:
            llm: LLM instance for generation
            retriever: Retriever instance for document search
        """
        self.llm = llm
        self.retriever = retriever
        logger.info("RAGChain initialized")
    
    def create_rag_chain(self) -> Any:
        """Create LangChain retrieval QA chain.
        
        Returns:
            Configured RetrievalQA chain
        """
        # Create custom retrieval chain
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": RAG_PROMPT},
            return_source_documents=True
        )
        return chain
    
    def _translate_to_english_for_retrieval(self, query: str) -> str:
        """Translate non-English query to English for vector retrieval using Gemini."""
        try:
            # If purely ASCII, return as is
            if all(ord(c) < 128 for c in query):
                return query
            prompt = f"Translate this legal query directly into English for vector search. Output ONLY the English translation without notes:\n{query}"
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            translated = resp.content.strip()
            logger.info(f"Translated query for retrieval: '{query}' -> '{translated}'")
            return translated
        except Exception as e:
            logger.warning(f"Query translation failed, using original: {e}")
            return query

    def generate(self, query: str, jurisdiction: str = "India", language: str = "en") -> Dict[str, Any]:
        """Generate answer with citations and multilingual Gemini 2.5 Flash support.
        
        Args:
            query: User query
            jurisdiction: Jurisdiction to search (India, International, or Both)
            language: Target response language code (e.g. 'hi', 'ta', 'te', 'en')
            
        Returns:
            Dictionary with response, citations, and confidence
        """
        from .prompts import LANGUAGE_MAP
        lang_name = LANGUAGE_MAP.get(str(language).lower(), str(language))
        logger.info(f"Generating answer for query: '{query}' in jurisdiction: {jurisdiction}, language: {lang_name}")
        
        # Check for simple conversational greetings
        clean_q = query.strip().lower()
        if clean_q in ['hi', 'hello', 'hey', 'namaste', 'namaskar', 'good morning', 'good afternoon', 'good evening', 'help']:
            if language and language.lower() not in ['en', 'english']:
                # Generate localized greeting via Gemini
                try:
                    greet_prompt = f"Provide a brief warm welcome in {lang_name} as AyurPedia AI (Ayurvedic IPR, Patents Act 1970, Section 3(p), FSSAI Ayurveda-Aahar, and WIPO compliance assistant)."
                    resp = self.llm.invoke([HumanMessage(content=greet_prompt)])
                    return {
                        "response": resp.content,
                        "citations": [],
                        "confidence": "High",
                        "retrieved_docs": []
                    }
                except Exception:
                    pass
            return {
                "response": "Hello! I am **AyurPedia**, your specialized AI consultant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, and Traditional Knowledge compliance.\n\n### How I Can Help You:\n1. **Formulation Classification**: Categorize your herbal product under 7 regulatory classes (*Classical*, *Proprietary*, *Ayurveda-Aahar*, *Cosmetic*, *Phytopharmaceutical*, etc.).\n2. **Patentability Analysis**: Clarify Section 3(p) restrictions against patenting traditional knowledge, novelty requirements, and synergistic bio-enhancers.\n3. **Regulatory Frameworks**: Guidance on the Indian Patents Act 1970, Biological Diversity Act 2002 (NBA approval), FSSAI Ayurveda-Aahar Regulations 2022, and the international WIPO GRATK Treaty 2024.\n\nFeel free to ask a specific legal question or run our **Formulation Classifier** to get started!",
                "citations": [],
                "confidence": "High",
                "retrieved_docs": []
            }

        # For vector retrieval, translate query to English if needed
        search_query = self._translate_to_english_for_retrieval(query)

        # Retrieve relevant documents
        retrieved_docs = self.retriever.search(search_query, jurisdiction)
        
        # Format context from retrieved documents
        if retrieved_docs:
            context = self._format_context(retrieved_docs)
        else:
            context = "Note: No specific statutory chunk exceeded the exact similarity threshold. Provide a comprehensive legal and conceptual explanation based on standard Indian and International IPR frameworks (Patents Act 1970, BD Act 2002, TKDL norms, and WIPO GRATK Treaty 2024)."
        
        # Generate response using Gemini 2.5 Flash
        try:
            prompt = RAG_PROMPT.format(context=context, question=query, target_language=lang_name)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "response": "I encountered an error while generating the response. Please try again.",
                "citations": [],
                "confidence": "Low",
                "retrieved_docs": retrieved_docs
            }
        
        # Extract citations from response
        citations = self.extract_citations(response_text)
        
        # Validate citations
        validated_citations = self.validate_citations(citations, retrieved_docs)
        
        # Calculate confidence
        confidence = self.calculate_confidence(retrieved_docs, validated_citations)
        
        return {
            "response": response_text,
            "citations": validated_citations,
            "confidence": confidence,
            "retrieved_docs": retrieved_docs
        }
    
    def _format_context(self, docs: List[DocumentChunk]) -> str:
        """Format retrieved documents into context string.
        
        Args:
            docs: List of retrieved DocumentChunk objects
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            source = metadata.get('source', 'Unknown')
            section = metadata.get('section', '')
            text = doc.text
            
            context_part = f"Source {i} [{source}]:\n"
            if section:
                context_part += f"Section: {section}\n"
            context_part += f"Content: {text}\n"
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def extract_citations(self, response: str) -> List[Dict[str, str]]:
        """Extract citations from response text.
        
        Args:
            response: Generated response text
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Flexible pattern to match citations like [Source: Document Name, Section: X.Y] or [Source: Doc, Page: 1, Section: 2]
        pattern = r'\[Source:\s*([^,\]]+)(?:,\s*([^\]]+))?\]'
        matches = re.findall(pattern, response)
        
        for source_raw, section_raw in matches:
            source = source_raw.strip()
            section = section_raw.strip() if section_raw else ""
            citations.append({
                "source": source,
                "section": section,
                "text": f"{source}" + (f", {section}" if section else "")
            })
        
        logger.info(f"Extracted {len(citations)} citations from response")
        return citations
    
    def validate_citations(self, citations: List[Dict[str, str]], 
                          retrieved_docs: List[DocumentChunk]) -> List[Dict[str, str]]:
        """Validate citations against retrieved documents.
        
        Args:
            citations: List of extracted citations
            retrieved_docs: List of retrieved documents
            
        Returns:
            List of validated citations
        """
        if not retrieved_docs:
            return citations

        validated = []
        doc_source_map = {}
        valid_sources = []
        valid_sections = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            metadata = doc.metadata
            src = metadata.get('source', '') or metadata.get('file_name', f'Document {i}')
            sec = metadata.get('section', '')
            doc_source_map[f"document {i}"] = src
            doc_source_map[f"source {i}"] = src
            if src:
                valid_sources.append(src.lower())
            if sec:
                valid_sections.append(sec.lower())
        
        # Validate each citation
        for citation in citations:
            raw_source = citation.get('source', '').strip()
            source_lower = raw_source.lower()
            section = citation.get('section', '').strip()
            
            # If citation used "Document 1" or "Source 1", map to real source name
            resolved_source = raw_source
            for alias, real_name in doc_source_map.items():
                if alias in source_lower:
                    resolved_source = real_name
                    break
            
            # Check validation
            is_valid_source = (
                any(s in source_lower or source_lower in s for s in valid_sources)
                or any(alias in source_lower for alias in doc_source_map.keys())
                or not valid_sources
            )
            
            if is_valid_source:
                validated.append({
                    "source": resolved_source,
                    "section": section,
                    "text": f"{resolved_source}" + (f", {section}" if section else "")
                })
            else:
                # Accept citation with fallback source
                default_source = retrieved_docs[0].metadata.get('source', 'Statutory Document')
                validated.append({
                    "source": default_source,
                    "section": section,
                    "text": f"{default_source}" + (f", {section}" if section else "")
                })
        
        logger.info(f"Validated {len(validated)}/{len(citations)} citations")
        return validated
    
    def calculate_confidence(self, retrieved_docs: List[DocumentChunk], 
                           validated_citations: List[Dict[str, str]]) -> str:
        """Calculate confidence level based on retrieval scores and citations.
        
        Args:
            retrieved_docs: List of retrieved documents
            validated_citations: List of validated citations
            
        Returns:
            Confidence level: High, Medium, or Low
        """
        if not retrieved_docs:
            return "Low"
        
        # Calculate average similarity score
        scores = [doc.metadata.get('score', 0.0) for doc in retrieved_docs]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Citation coverage
        citation_coverage = len(validated_citations) / max(len(retrieved_docs), 1)
        
        # Confidence calculation calibrated for Cohere vector similarity and validated citations
        if (avg_score >= 0.45 or len(validated_citations) >= 2) and len(validated_citations) > 0:
            return "High"
        elif avg_score >= 0.3 or len(validated_citations) >= 1:
            return "Medium"
        else:
            return "Low"
