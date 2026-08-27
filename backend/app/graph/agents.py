"""
LangGraph agents for multi-step legal reasoning.
Implements agentic RAG with graph-based retrieval and reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from operator import add
from ..core.neo4j import get_neo4j
from ..core.llm import get_llm_client
from ..rag.retriever import Retriever


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the agent workflow."""
    query: str
    jurisdiction: str
    language: str
    query_analysis: Dict[str, Any]  # Query understanding results
    vector_context: List[Dict[str, Any]]
    reasoning: str
    response: str
    citations: List[Dict[str, str]]
    confidence: str


class QueryUnderstandingAgent:
    """Agent for understanding and analyzing user queries."""
    
    def __init__(self):
        """Initialize query understanding agent."""
        self.llm_client = get_llm_client()
        self.llm = self.llm_client.get_llm_with_fallback()
        logger.info("QueryUnderstandingAgent initialized")
    
    def __call__(self, state: AgentState) -> AgentState:
        """Analyze the query to understand intent and extract key information.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with query analysis
        """
        query = state["query"]
        jurisdiction = state["jurisdiction"]
        language = state["language"]
        
        logger.info(f"QueryUnderstandingAgent analyzing query: {query}")
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(query, jurisdiction, language)
        
        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_text = response.content
            
            # Parse analysis
            analysis = self._parse_analysis(analysis_text)
            
            state["query_analysis"] = analysis
            
            logger.info(f"QueryUnderstandingAgent completed: query_type={analysis.get('query_type')}, "
                       f"concepts={len(analysis.get('concepts', []))}")
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            # Fallback analysis
            state["query_analysis"] = {
                "query_type": "general",
                "concepts": [w for w in query.split() if len(w) > 3][:5],
                "jurisdiction": jurisdiction,
                "language": language,
                "is_multi_part": False,
                "specific_sections": [],
                "urgency": "normal"
            }
        
        return state
    
    def _build_analysis_prompt(self, query: str, jurisdiction: str, language: str) -> str:
        """Build prompt for query analysis."""
        
        lang_name = {
            "hi": "Hindi", "ta": "Tamil", "te": "Telugu", 
            "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati",
            "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi",
            "en": "English"
       }.get(language.lower(), language)
        
        prompt = f"""Analyze this legal query for Ayurvedic IPR and patent law.

QUERY: {query}
JURISDICTION: {jurisdiction}
LANGUAGE: {lang_name}

Provide a JSON-formatted analysis with these fields:
{{
  "query_type": "classification|legal_question|comparison|procedure|general",
  "concepts": ["list of 3-5 key legal concepts"],
  "jurisdiction_match": true/false,
  "is_multi_part": true/false,
  "specific_sections": ["any specific sections mentioned like 3(p), 3(d)"],
  "urgency": "normal|high",
  "entities": ["any specific entities mentioned like companies, herbs, products"]
}}

Return ONLY the JSON, no other text."""
        
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the LLM analysis response."""
        import json
        import re
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Ensure required fields
            defaults = {
                "query_type": "general",
                "concepts": [],
                "jurisdiction_match": True,
                "is_multi_part": False,
                "specific_sections": [],
                "urgency": "normal",
                "entities": []
            }
            
            for key, default_value in defaults.items():
                if key not in analysis:
                    analysis[key] = default_value
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Failed to parse analysis JSON: {e}")
            return {
                "query_type": "general",
                "concepts": [],
                "jurisdiction_match": True,
                "is_multi_part": False,
                "specific_sections": [],
                "urgency": "normal",
                "entities": []
            }


class GraphRetrieverAgent:
    """Agent for retrieving relevant legal concepts from Neo4j knowledge graph."""
    
    def __init__(self):
        """Initialize graph retriever agent."""
        self.neo4j = get_neo4j()
        self.llm_client = get_llm_client()
        self.llm = self.llm_client.get_llm_with_fallback()
        logger.info("GraphRetrieverAgent initialized")
    
    def __call__(self, state: AgentState) -> AgentState:
        """Retrieve relevant graph nodes based on query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with graph context
        """
        query = state["query"]
        jurisdiction = state["jurisdiction"]
        
        logger.info(f"GraphRetrieverAgent processing query: {query}")
        
        # Check if Neo4j is connected
        if not self.neo4j.is_connected:
            logger.warning("Neo4j not connected, skipping graph retrieval")
            state["graph_context"] = []
            state["graph_path"] = []
            return state
        
        # Extract key concepts from query using LLM
        try:
            concepts = self._extract_concepts(query)
        except Exception as e:
            logger.error(f"Concept extraction failed: {e}")
            concepts = [word for word in query.split() if len(word) > 3][:5]
        
        # Search Neo4j for relevant nodes
        graph_context = []
        graph_path = []
        
        for concept in concepts:
            # Search across multiple node types
            for node_type in ["Statute", "Section", "Concept", "Framework"]:
                try:
                    nodes = self.neo4j.search_nodes(
                        label=node_type,
                        property_name="name",
                        search_term=concept,
                        limit=3
                    )
                    
                    for node in nodes:
                        # Filter by jurisdiction if applicable
                        if node.get("jurisdiction") and node["jurisdiction"] != jurisdiction:
                            if jurisdiction != "Both":
                                continue
                        
                        graph_context.append({
                            "type": node_type,
                            "data": node,
                            "matched_concept": concept
                        })
                        graph_path.append(f"{node_type}: {node.get('name', 'N/A')}")
                        
                        # Get relationships for this node
                        node_id = node.get("id") or node.get("name")
                        if node_id:
                            try:
                                rels = self.neo4j.get_node_relationships(node_id, depth=1)
                                if rels:
                                    graph_context[-1]["relationships"] = rels
                            except Exception as e:
                                logger.warning(f"Failed to get relationships for node {node_id}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to search nodes for {node_type}: {e}")
                    continue
        
        state["graph_context"] = graph_context
        state["graph_path"] = graph_path
        
        logger.info(f"GraphRetrieverAgent found {len(graph_context)} relevant nodes")
        return state
    
    def _extract_concepts(self, query: str) -> List[str]:
        """Extract key legal concepts from query.
        
        Args:
            query: User query
            
        Returns:
            List of key concepts
        """
        prompt = f"""Extract 3-5 key legal concepts from this query for searching a legal knowledge graph.
Focus on: statutes, sections, legal concepts, frameworks.

Query: {query}

Return ONLY a comma-separated list of concepts (e.g., "novelty, prior art, patents act")"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            concepts_str = response.content.strip()
            concepts = [c.strip() for c in concepts_str.split(",") if c.strip()]
            return concepts[:5]  # Limit to top 5
        except Exception as e:
            logger.error(f"Concept extraction failed: {e}")
            # Fallback: extract words from query
            words = query.split()
            return [w for w in words if len(w) > 3][:5]


class VectorRetrieverAgent:
    """Agent for retrieving detailed legal text from vector database."""
    
    def __init__(self, retriever: Retriever):
        """Initialize vector retriever agent.
        
        Args:
            retriever: Vector retriever instance
        """
        self.retriever = retriever
        logger.info("VectorRetrieverAgent initialized")
    
    def __call__(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from vector database.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with vector context
        """
        query = state["query"]
        jurisdiction = state["jurisdiction"]
        
        logger.info(f"VectorRetrieverAgent processing query: {query}")
        
        # Use existing retriever with error handling
        try:
            retrieved_docs = self.retriever.search(query, jurisdiction)
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
            retrieved_docs = []
        
        # Format for context
        vector_context = []
        for doc in retrieved_docs:
            vector_context.append({
                "text": doc.text,
                "metadata": doc.metadata,
                "score": doc.metadata.get("score", 0.0)
            })
        
        state["vector_context"] = vector_context
        
        logger.info(f"VectorRetrieverAgent retrieved {len(vector_context)} documents")
        return state


class ReasoningAgent:
    """Agent for synthesizing multi-step legal reasoning."""
    
    def __init__(self):
        """Initialize reasoning agent."""
        self.llm_client = get_llm_client()
        self.llm = self.llm_client.get_llm_with_fallback()
        logger.info("ReasoningAgent initialized")
    
    def __call__(self, state: AgentState) -> AgentState:
        """Synthesize legal reasoning from vector context.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with reasoning and response
        """
        query = state["query"]
        vector_context = state["vector_context"]
        language = state["language"]
        
        logger.info("ReasoningAgent synthesizing response")
        
        # Check if any retrieval happened
        has_retrieval = len(vector_context) > 0
        if not has_retrieval:
            logger.warning("No retrieval results - using general knowledge for response")
        
        # Build reasoning prompt
        reasoning_prompt = self._build_reasoning_prompt(
            query, vector_context, language, has_retrieval
        )
        
        try:
            response = self.llm.invoke([HumanMessage(content=reasoning_prompt)])
            response_text = response.content
            
            # Extract reasoning and answer
            reasoning, final_response = self._parse_response(response_text)
            
            state["reasoning"] = reasoning
            state["response"] = final_response
            
            logger.info("ReasoningAgent completed synthesis")
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            state["reasoning"] = "Reasoning generation failed"
            state["response"] = "I encountered an error while generating the legal analysis."
        
        return state
    
    def _build_reasoning_prompt(self, query: str, vector_context: List[Dict],
                               language: str, has_retrieval: bool = True) -> str:
        """Build reasoning prompt with vector context."""
        
        # Format vector context
        vector_summary = "\n\n".join([
            f"Document {i+1} (score: {ctx['score']:.2f}):\n{ctx['text'][:500]}"
            for i, ctx in enumerate(vector_context[:5])
        ])
        
        lang_name = {
            "hi": "Hindi", "ta": "Tamil", "te": "Telugu", 
            "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati",
            "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi",
            "en": "English"
        }.get(language.lower(), language)
        
        if has_retrieval:
            # Build source mapping for citations
            source_mapping = ""
            for i, ctx in enumerate(vector_context[:5]):
                source = ctx["metadata"].get("source", "Unknown Source")
                section = ctx["metadata"].get("section", "")
                source_mapping += f"Document {i+1}: {source}"
                if section:
                    source_mapping += f" - {section}"
                source_mapping += "\n"
            
            prompt = f"""You are an expert legal analyst for Ayurvedic Intellectual Property law.
Answer the user's question using the retrieved document context.

USER QUERY: {query}
TARGET LANGUAGE: {lang_name}

RETRIEVED DOCUMENTS:
{vector_summary if vector_summary else "No document context available"}

SOURCE MAPPING FOR CITATIONS:
{source_mapping}

INSTRUCTIONS:
1. Provide a clear, direct answer to the user's question
2. Reference specific information from the documents using the citation format: [Source: Document Name] or [Source: Document Name, Section: X.Y]
3. Use the exact document names from the SOURCE MAPPING above
4. IMPORTANT: You MUST include at least 2-3 citations in your response using the format [Source: Document Name]
5. Format your response in {lang_name}
6. Keep it concise but comprehensive
7. Include a brief disclaimer at the end

Example citation format: "According to the Patents Act [Source: Patents Act 1970], traditional knowledge cannot be patented."

Provide your answer directly below:"""
        else:
            prompt = f"""You are an expert legal analyst for Ayurvedic Intellectual Property law.
Answer the user's question based on your general legal knowledge.

USER QUERY: {query}
TARGET LANGUAGE: {lang_name}

INSTRUCTIONS:
1. Provide a clear, direct answer to the user's question
2. Reference relevant laws like the Patents Act 1970, Biological Diversity Act 2002, FSSAI regulations, and international treaties like WIPO GRATK
3. Explain key concepts clearly with examples
4. Format your response in {lang_name}
5. Keep it concise but comprehensive
6. Include a brief disclaimer at the end

Provide your answer directly below:"""
        
        return prompt
    
    def _parse_response(self, response: str) -> tuple[str, str]:
        """Parse reasoning and answer from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Tuple of (reasoning, answer)
        """
        # For simplified prompt, use entire response as answer
        # Extract any citations for reasoning
        import re
        citations = re.findall(r'\[Source:[^\]]+\]', response)
        
        reasoning = f"Answer based on retrieved documents. Citations found: {len(citations)}"
        answer = response.strip()
        
        return reasoning, answer


class CitationAgent:
    """Agent for validating and formatting citations."""
    
    def __init__(self):
        """Initialize citation agent."""
        self.llm_client = get_llm_client()
        self.llm = self.llm_client.get_llm_with_fallback()
        logger.info("CitationAgent initialized")
    
    def __call__(self, state: AgentState) -> AgentState:
        """Extract and validate citations from response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validated citations and confidence
        """
        response = state["response"]
        vector_context = state["vector_context"]
        
        logger.info("CitationAgent processing citations")
        
        # Extract citations using multiple regex patterns
        import re
        citations = []
        
        # Pattern 1: [Source: Document Name, Section: X.Y]
        citation_pattern1 = r'\[Source:\s*([^,\]]+)(?:,\s*([^\]]+))?\]'
        matches1 = re.findall(citation_pattern1, response)
        
        # Pattern 2: [Source: Document Name]
        citation_pattern2 = r'\[Source:\s*([^\]]+)\]'
        matches2 = re.findall(citation_pattern2, response)
        
        # Pattern 3: (Source: Document Name)
        citation_pattern3 = r'\(Source:\s*([^)]+)\)'
        matches3 = re.findall(citation_pattern3, response)
        
        # Process matches from pattern 1
        for source_raw, section_raw in matches1:
            source = source_raw.strip()
            section = section_raw.strip() if section_raw else ""
            citations.append({
                "source": source,
                "section": section,
                "text": f"{source}" + (f", {section}" if section else "")
            })
        
        # Process matches from pattern 2 (if not already captured)
        for source_raw in matches2:
            source = source_raw.strip()
            # Avoid duplicates
            if not any(c["source"] == source for c in citations):
                citations.append({
                    "source": source,
                    "section": "",
                    "text": source
                })
        
        # Process matches from pattern 3 (if not already captured)
        for source_raw in matches3:
            source = source_raw.strip()
            # Avoid duplicates
            if not any(c["source"] == source for c in citations):
                citations.append({
                    "source": source,
                    "section": "",
                    "text": source
                })
        
        # Fallback: if no citations found, generate from vector context
        if not citations and vector_context:
            logger.warning("No citations found in response, generating from vector context")
            unique_sources = set()
            for ctx in vector_context[:3]:  # Top 3 documents
                source = ctx["metadata"].get("source", "Unknown Source")
                section = ctx["metadata"].get("section", "")
                if source not in unique_sources:
                    unique_sources.add(source)
                    citations.append({
                        "source": source,
                        "section": section,
                        "text": f"{source}" + (f", {section}" if section else "")
                    })
        
        # Validate citations against context
        validated = self._validate_citations(citations, vector_context)
        
        state["citations"] = validated
        
        # Calculate confidence
        confidence = self._calculate_confidence(vector_context, validated)
        state["confidence"] = confidence
        
        logger.info(f"CitationAgent validated {len(validated)} citations, confidence: {confidence}")
        return state
    
    def _validate_citations(self, citations: List[Dict], vector_context: List[Dict]) -> List[Dict]:
        """Validate citations against retrieved context.
        
        Args:
            citations: Extracted citations
            vector_context: Vector context
            
        Returns:
            Validated citations
        """
        if not citations:
            return []
        
        # Build list of valid sources
        valid_sources = set()
        for ctx in vector_context:
            valid_sources.add(ctx["metadata"].get("source", "").lower())
        
        validated = []
        for citation in citations:
            source_lower = citation["source"].lower()
            if any(vs in source_lower or source_lower in vs for vs in valid_sources):
                validated.append(citation)
        
        return validated
    
    def _calculate_confidence(self, vector_context: List[Dict],
                           citations: List[Dict]) -> str:
        """Calculate confidence level.
        
        Args:
            vector_context: Vector context
            citations: Validated citations
            
        Returns:
            Confidence level (High/Medium/Low)
        """
        # Calculate average vector score
        vector_scores = [ctx.get("score", 0.0) for ctx in vector_context]
        avg_score = sum(vector_scores) / len(vector_scores) if vector_scores else 0.0
        
        # Confidence calculation
        if avg_score >= 0.45 or len(citations) >= 2:
            return "High"
        elif avg_score >= 0.3 or len(citations) >= 1:
            return "Medium"
        else:
            return "Low"


class AgenticRAGWorkflow:
    """Agentic RAG workflow using LangGraph."""
    
    def __init__(self, retriever: Retriever):
        """Initialize agentic RAG workflow.
        
        Args:
            retriever: Vector retriever instance
        """
        self.retriever = retriever
        self.query_agent = QueryUnderstandingAgent()
        self.vector_retriever = VectorRetrieverAgent(retriever)
        self.reasoning_agent = ReasoningAgent()
        self.citation_agent = CitationAgent()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        logger.info("AgenticRAGWorkflow initialized (with query understanding)")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Define the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("query_understanding", self.query_agent)
        workflow.add_node("vector_retriever", self.vector_retriever)
        workflow.add_node("reasoning", self.reasoning_agent)
        workflow.add_node("citation", self.citation_agent)
        
        # Define edges
        workflow.set_entry_point("query_understanding")
        workflow.add_edge("query_understanding", "vector_retriever")
        workflow.add_edge("vector_retriever", "reasoning")
        workflow.add_edge("reasoning", "citation")
        workflow.add_edge("citation", END)
        
        return workflow.compile()
    
    def invoke(self, query: str, jurisdiction: str = "India", 
               language: str = "en") -> Dict[str, Any]:
        """Invoke the agentic RAG workflow.
        
        Args:
            query: User query
            jurisdiction: Jurisdiction to search
            language: Target language
            
        Returns:
            Complete response with reasoning, citations, and graph path
        """
        # Check for simple conversational greetings
        clean_q = query.strip().lower()
        greetings = ['hi', 'hello', 'hey', 'namaste', 'namaskar', 'good morning', 'good afternoon', 'good evening', 'help']
        # Check if query consists only of greeting words (handles multi-word greetings like "hey hello")
        words = clean_q.split()
        if all(word in greetings for word in words) and len(words) <= 3:
            logger.info("Detected greeting query, returning welcome message")
            
            lang_name = {
                "hi": "Hindi", "ta": "Tamil", "te": "Telugu", 
                "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati",
                "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi",
                "en": "English"
            }.get(language.lower(), language)
            
            if language and language.lower() not in ['en', 'english']:
                # Generate localized greeting
                try:
                    llm_client = get_llm_client()
                    llm = llm_client.get_llm_with_fallback()
                    greet_prompt = f"Provide a brief warm welcome in {lang_name} as AyurPedia AI (Ayurvedic IPR, Patents Act 1970, Section 3(p), FSSAI Ayurveda-Aahar, and WIPO compliance assistant). Keep it under 100 words."
                    response = llm.invoke([HumanMessage(content=greet_prompt)])
                    return {
                        "response": response.content,
                        "reasoning": "Greeting detected",
                        "citations": [],
                        "confidence": "High"
                    }
                except Exception:
                    pass
            
            return {
                "response": "Hello! I am **AyurPedia**, your specialized AI consultant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, and Traditional Knowledge compliance.\n\n### How I Can Help You:\n1. **Formulation Classification**: Categorize your herbal product under 7 regulatory classes (*Classical*, *Proprietary*, *Ayurveda-Aahar*, *Cosmetic*, *Phytopharmaceutical*, etc.).\n2. **Patentability Analysis**: Clarify Section 3(p) restrictions against patenting traditional knowledge, novelty requirements, and synergistic bio-enhancers.\n3. **Regulatory Frameworks**: Guidance on the Indian Patents Act 1970, Biological Diversity Act 2002 (NBA approval), FSSAI Ayurveda-Aahar Regulations 2022, and the international WIPO GRATK Treaty 2024.\n\nFeel free to ask a specific legal question or run our **Formulation Classifier** to get started!",
                "reasoning": "Greeting detected",
                "citations": [],
                "confidence": "High"
            }
        
        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "jurisdiction": jurisdiction,
            "language": language,
            "query_analysis": {},
            "vector_context": [],
            "reasoning": "",
            "response": "",
            "citations": [],
            "confidence": "Low"
        }
        
        # Invoke workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "response": final_state["response"],
                "reasoning": final_state["reasoning"],
                "citations": final_state["citations"],
                "confidence": final_state["confidence"],
                "query_analysis": final_state.get("query_analysis", {}),
                "vector_context": final_state["vector_context"]
            }
        except Exception as e:
            logger.error(f"Workflow invocation failed: {e}")
            return {
                "response": "I encountered an error while processing your query.",
                "reasoning": "Workflow execution failed",
                "citations": [],
                "confidence": "Low",
                "query_analysis": {},
                "vector_context": []
            }


# Global workflow instance
_agentic_rag: Optional[AgenticRAGWorkflow] = None


def get_agentic_rag(retriever: Retriever) -> AgenticRAGWorkflow:
    """Get or initialize global agentic RAG workflow."""
    global _agentic_rag
    if _agentic_rag is None:
        _agentic_rag = AgenticRAGWorkflow(retriever)
    return _agentic_rag
