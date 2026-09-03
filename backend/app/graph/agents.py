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
from ..models.patent import (
    PatentNoveltyRequest,
    PatentNoveltyResponse,
    ComponentNovelty,
    PriorArtReference,
    Section3pAnalysis,
    RiskLevel,
    Section3pStatus
)


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
            
            # Extract reasoning, answer, and citations
            reasoning, final_response, citations = self._parse_response(response_text)
            
            # Fallback: if no citations extracted from LLM response, extract from vector_context
            if not citations and has_retrieval:
                citations = self._extract_citations_from_context(vector_context)
                logger.info(f"Using fallback citation extraction from context: {len(citations)} citations")
            
            state["reasoning"] = reasoning
            state["response"] = final_response
            state["citations"] = citations
            
            logger.info(f"ReasoningAgent completed synthesis with {len(citations)} citations")
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            state["reasoning"] = "Reasoning generation failed"
            state["response"] = "I encountered an error while generating the legal analysis."
            state["citations"] = []
        
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
8. At the very end of your response, add a "References" section listing all sources cited in the format:
   **References:**
   - [Source: Document Name]
   - [Source: Document Name, Section: X.Y]

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
    
    def _parse_response(self, response: str) -> tuple[str, str, List[Dict[str, str]]]:
        """Parse reasoning, answer, and citations from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Tuple of (reasoning, answer, citations)
        """
        import re
        
        # Extract citations in format [Source: Document Name] or [Source: Document Name, Section: X.Y]
        citation_pattern = r'\[Source:\s*([^\]]+)\]'
        citation_matches = re.findall(citation_pattern, response)
        
        # Parse citations into structured format
        citations = []
        for match in citation_matches:
            # Parse source and section
            if ',' in match:
                parts = [p.strip() for p in match.split(',')]
                source = parts[0]
                # Extract section if present
                section = ""
                for part in parts[1:]:
                    if part.strip().lower().startswith('section:'):
                        section = part.split(':', 1)[1].strip()
                        break
            else:
                source = match.strip()
                section = ""
            
            citations.append({
                "source": source,
                "section": section,
                "text": f"[Source: {match}]"  # Keep original citation text for reference
            })
        
        reasoning = f"Answer based on retrieved documents. Citations found: {len(citations)}"
        answer = response.strip()
        
        return reasoning, answer, citations
    
    def _extract_citations_from_context(self, vector_context: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract citations from vector context as fallback.
        
        Args:
            vector_context: Retrieved document context
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        seen_sources = set()
        
        for ctx in vector_context[:5]:  # Top 5 documents
            metadata = ctx.get("metadata", {})
            source = metadata.get("source", "Unknown Source")
            section = metadata.get("section", "")
            
            # Deduplicate by source
            source_key = f"{source}-{section}"
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            
            citations.append({
                "source": source,
                "section": section,
                "text": ctx.get("text", "")[:200]  # First 200 chars as context
            })
        
        return citations


class PatentNoveltyAgent:
    """Agent for analyzing patent novelty and Section 3(p) compliance."""
    
    def __init__(self, retriever: Retriever):
        """Initialize patent novelty agent.
        
        Args:
            retriever: Vector retriever instance for traditional knowledge search
        """
        self.retriever = retriever
        self.llm_client = get_llm_client()
        self.llm = self.llm_client.get_llm_with_fallback()
        logger.info("PatentNoveltyAgent initialized")
    
    def analyze_novelty(self, request: PatentNoveltyRequest) -> PatentNoveltyResponse:
        """Analyze formulation novelty and Section 3(p) compliance.
        
        Args:
            request: Patent novelty analysis request
            
        Returns:
            Patent novelty analysis response
        """
        logger.info(f"PatentNoveltyAgent analyzing formulation: {request.formulation_name}")
        
        # Step 1: Search for traditional knowledge references
        traditional_context = self._search_traditional_knowledge(request)
        
        # Step 2: Analyze component novelty
        component_novelty = self._analyze_component_novelty(request, traditional_context)
        
        # Step 3: Calculate overall novelty score
        novelty_score, risk_level = self._calculate_overall_novelty(component_novelty)
        
        # Step 4: Identify prior art
        prior_art = self._identify_prior_art(request, traditional_context)
        
        # Step 5: Section 3(p) compliance analysis
        section3p_analysis = self._analyze_section3p_compliance(request, component_novelty, prior_art)
        
        # Step 6: Calculate confidence
        confidence = self._calculate_confidence(traditional_context, prior_art)
        
        # Build response
        response = PatentNoveltyResponse(
            formulation_name=request.formulation_name,
            novelty_score=novelty_score,
            risk_level=risk_level,
            component_novelty=component_novelty,
            prior_art=prior_art,
            section3p_analysis=section3p_analysis,
            confidence=confidence,
            ai_generated=True
        )
        
        logger.info(f"PatentNoveltyAgent completed: novelty_score={novelty_score}, risk_level={risk_level}")
        return response
    
    def _search_traditional_knowledge(self, request: PatentNoveltyRequest) -> List[Dict[str, Any]]:
        """Search for traditional knowledge references.
        
        Args:
            request: Patent novelty request
            
        Returns:
            List of traditional knowledge context documents
        """
        context = []
        
        # Build search queries for each ingredient
        for ingredient in request.ingredients[:3]:  # Limit to top 3 ingredients
            try:
                docs = self.retriever.search(
                    query=f"{ingredient} traditional ayurvedic formulation classical text",
                    jurisdiction=request.jurisdiction,
                    use_hierarchical=True
                )
                for doc in docs:
                    context.append({
                        "text": doc.text,
                        "metadata": doc.metadata,
                        "ingredient": ingredient
                    })
            except Exception as e:
                logger.warning(f"Traditional knowledge search failed for {ingredient}: {e}")
        
        # Search for formulation name
        try:
            docs = self.retriever.search(
                query=f"{request.formulation_name} ayurvedic classical text",
                jurisdiction=request.jurisdiction,
                use_hierarchical=True
            )
            for doc in docs:
                context.append({
                    "text": doc.text,
                    "metadata": doc.metadata,
                    "ingredient": "formulation"
                })
        except Exception as e:
            logger.warning(f"Formulation search failed: {e}")
        
        logger.info(f"Found {len(context)} traditional knowledge references")
        return context
    
    def _analyze_component_novelty(self, request: PatentNoveltyRequest, 
                                  traditional_context: List[Dict[str, Any]]) -> List[ComponentNovelty]:
        """Analyze novelty for each component.
        
        Args:
            request: Patent novelty request
            traditional_context: Traditional knowledge context
            
        Returns:
            List of component novelty analyses
        """
        components = []
        
        # Analyze ingredients novelty
        ingredients_analysis = self._analyze_ingredients_novelty(request, traditional_context)
        components.append(ingredients_analysis)
        
        # Analyze process novelty
        process_analysis = self._analyze_process_novelty(request, traditional_context)
        components.append(process_analysis)
        
        # Analyze combination novelty
        combination_analysis = self._analyze_combination_novelty(request, traditional_context)
        components.append(combination_analysis)
        
        return components
    
    def _analyze_ingredients_novelty(self, request: PatentNoveltyRequest,
                                    traditional_context: List[Dict[str, Any]]) -> ComponentNovelty:
        """Analyze ingredients novelty."""
        # Count traditional references for ingredients
        traditional_ingredients = set()
        for ctx in traditional_context:
            if ctx.get("ingredient") != "formulation":
                traditional_ingredients.add(ctx["ingredient"])
        
        # Calculate novelty score based on traditional overlap
        total_ingredients = len(request.ingredients)
        traditional_count = len([ing for ing in request.ingredients if any(t in ing.lower() for t in traditional_ingredients)])
        
        if total_ingredients > 0:
            novelty_score = (1 - (traditional_count / total_ingredients)) * 100
        else:
            novelty_score = 50.0
        
        # Determine risk level
        if novelty_score >= 70:
            risk_level = RiskLevel.LOW
        elif novelty_score >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        # Build analysis
        analysis = f"Ingredients analysis: {traditional_count}/{total_ingredients} ingredients found in traditional knowledge. "
        if novelty_score >= 70:
            analysis += "High novelty - significant new or modified ingredients."
        elif novelty_score >= 40:
            analysis += "Medium novelty - mix of traditional and new ingredients."
        else:
            analysis += "Low novelty - primarily traditional ingredients."
        
        return ComponentNovelty(
            component="Ingredients",
            score=novelty_score,
            risk_level=risk_level,
            analysis=analysis,
            traditional_references=list(traditional_ingredients)
        )
    
    def _analyze_process_novelty(self, request: PatentNoveltyRequest,
                                 traditional_context: List[Dict[str, Any]]) -> ComponentNovelty:
        """Analyze process novelty."""
        # Use LLM to analyze process novelty
        prompt = f"""Analyze the novelty of this Ayurvedic preparation process.

Process: {request.process}
Formulation: {request.formulation_name}
Novelty Claim: {request.novelty_claim or 'None specified'}

Traditional Context:
{chr(10).join([ctx['text'][:300] for ctx in traditional_context[:2]])}

Rate the novelty on a scale of 0-100 based on:
- How different is this from traditional preparation methods?
- Does it involve modern technology (nano-emulsion, extraction, etc.)?
- Is it a significant process innovation?

Provide your response in this JSON format:
{{
  "score": 0-100,
  "analysis": "detailed explanation",
  "traditional_references": ["reference1", "reference2"]
}}"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse JSON
            import json
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                score = result.get("score", 50.0)
                analysis = result.get("analysis", "Process analysis completed")
                traditional_refs = result.get("traditional_references", [])
            else:
                score = 50.0
                analysis = "Could not parse process analysis"
                traditional_refs = []
        except Exception as e:
            logger.warning(f"Process novelty analysis failed: {e}")
            score = 50.0
            analysis = "Process analysis unavailable"
            traditional_refs = []
        
        # Determine risk level
        if score >= 70:
            risk_level = RiskLevel.LOW
        elif score >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        return ComponentNovelty(
            component="Process",
            score=score,
            risk_level=risk_level,
            analysis=analysis,
            traditional_references=traditional_refs
        )
    
    def _analyze_combination_novelty(self, request: PatentNoveltyRequest,
                                    traditional_context: List[Dict[str, Any]]) -> ComponentNovelty:
        """Analyze combination novelty."""
        # Use LLM to analyze combination novelty
        prompt = f"""Analyze the novelty of this Ayurvedic formulation combination.

Formulation: {request.formulation_name}
Ingredients: {', '.join(request.ingredients)}
Intended Use: {request.intended_use}

Traditional Context:
{chr(10).join([ctx['text'][:300] for ctx in traditional_context[:2]])}

Rate the novelty on a scale of 0-100 based on:
- Is this combination found in classical texts?
- Is the intended use traditional or novel?
- Is there synergistic innovation?

Provide your response in this JSON format:
{{
  "score": 0-100,
  "analysis": "detailed explanation",
  "traditional_references": ["reference1", "reference2"]
}}"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse JSON
            import json
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                score = result.get("score", 50.0)
                analysis = result.get("analysis", "Combination analysis completed")
                traditional_refs = result.get("traditional_references", [])
            else:
                score = 50.0
                analysis = "Could not parse combination analysis"
                traditional_refs = []
        except Exception as e:
            logger.warning(f"Combination novelty analysis failed: {e}")
            score = 50.0
            analysis = "Combination analysis unavailable"
            traditional_refs = []
        
        # Determine risk level
        if score >= 70:
            risk_level = RiskLevel.LOW
        elif score >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        return ComponentNovelty(
            component="Combination",
            score=score,
            risk_level=risk_level,
            analysis=analysis,
            traditional_references=traditional_refs
        )
    
    def _calculate_overall_novelty(self, component_novelty: List[ComponentNovelty]) -> tuple[float, RiskLevel]:
        """Calculate overall novelty score from components.
        
        Args:
            component_novelty: List of component novelty analyses
            
        Returns:
            Tuple of (novelty_score, risk_level)
        """
        if not component_novelty:
            return 50.0, RiskLevel.MEDIUM
        
        # Calculate weighted average (ingredients: 40%, process: 30%, combination: 30%)
        weights = {"Ingredients": 0.4, "Process": 0.3, "Combination": 0.3}
        total_weight = 0.0
        weighted_score = 0.0
        
        for component in component_novelty:
            weight = weights.get(component.component, 0.33)
            weighted_score += component.score * weight
            total_weight += weight
        
        novelty_score = weighted_score / total_weight if total_weight > 0 else 50.0
        
        # Determine risk level
        if novelty_score >= 70:
            risk_level = RiskLevel.LOW
        elif novelty_score >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        return novelty_score, risk_level
    
    def _identify_prior_art(self, request: PatentNoveltyRequest,
                          traditional_context: List[Dict[str, Any]]) -> List[PriorArtReference]:
        """Identify prior art references.
        
        Args:
            request: Patent novelty request
            traditional_context: Traditional knowledge context
            
        Returns:
            List of prior art references
        """
        prior_art = []
        
        # Extract from traditional context
        for ctx in traditional_context[:5]:  # Top 5 references
            source = ctx["metadata"].get("source", "Unknown Source")
            section = ctx["metadata"].get("section", "")
            text = ctx["text"][:500]  # Increased from 200 to 500 characters
            
            # Calculate relevance based on score
            score = ctx["metadata"].get("score", 0.5)
            
            prior_art.append(PriorArtReference(
                source=source,
                citation=f"{source}" + (f", {section}" if section else ""),
                relevance=score,
                description=text,
                url=None
            ))
        
        return prior_art
    
    def _analyze_section3p_compliance(self, request: PatentNoveltyRequest,
                                     component_novelty: List[ComponentNovelty],
                                     prior_art: List[PriorArtReference]) -> Section3pAnalysis:
        """Analyze Section 3(p) compliance.
        
        Args:
            request: Patent novelty request
            component_novelty: Component novelty analyses
            prior_art: Prior art references
            
        Returns:
            Section 3(p) compliance analysis
        """
        # Use LLM for Section 3(p) analysis
        prompt = f"""Analyze Section 3(p) compliance for this Ayurvedic formulation.

Formulation: {request.formulation_name}
Ingredients: {', '.join(request.ingredients)}
Process: {request.process}
Intended Use: {request.intended_use}
Novelty Claim: {request.novelty_claim or 'None specified'}

Component Novelty:
{chr(10).join([f"{c.component}: {c.score}/100 - {c.analysis}" for c in component_novelty])}

Prior Art Found: {len(prior_art)} references

Section 3(p) of Indian Patents Act excludes:
- Mere discovery of traditional knowledge
- Mere aggregation of known properties
- Traditional formulations without innovation

But allows:
- Novel combinations with synergistic effects
- Process innovations
- Enhanced bioavailability methods
- New therapeutic applications

Provide your analysis in this JSON format:
{{
  "status": "Patentable|Partially Patentable|Not Patentable|Uncertain",
  "analysis": "detailed explanation of Section 3(p) compliance",
  "patentable_elements": ["element1", "element2"],
  "non_patentable_elements": ["element1", "element2"],
  "recommendations": ["recommendation1", "recommendation2"]
}}"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse JSON
            import json
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                status_str = result.get("status", "Uncertain")
                analysis = result.get("analysis", "Section 3(p) analysis completed")
                patentable_elements = result.get("patentable_elements", [])
                non_patentable_elements = result.get("non_patentable_elements", [])
                recommendations = result.get("recommendations", [])
            else:
                status_str = "Uncertain"
                analysis = "Could not parse Section 3(p) analysis"
                patentable_elements = []
                non_patentable_elements = []
                recommendations = []
        except Exception as e:
            logger.warning(f"Section 3(p) analysis failed: {e}")
            status_str = "Uncertain"
            analysis = "Section 3(p) analysis unavailable"
            patentable_elements = []
            non_patentable_elements = []
            recommendations = []
        
        # Map status string to enum
        status_map = {
            "Patentable": Section3pStatus.PATENTABLE,
            "Partially Patentable": Section3pStatus.PARTIALLY_PATENTABLE,
            "Not Patentable": Section3pStatus.NOT_PATENTABLE,
            "Uncertain": Section3pStatus.UNCERTAIN
        }
        status = status_map.get(status_str, Section3pStatus.UNCERTAIN)
        
        return Section3pAnalysis(
            status=status,
            analysis=analysis,
            patentable_elements=patentable_elements,
            non_patentable_elements=non_patentable_elements,
            recommendations=recommendations
        )
    
    def _calculate_confidence(self, traditional_context: List[Dict[str, Any]],
                             prior_art: List[PriorArtReference]) -> float:
        """Calculate confidence in the analysis.
        
        Args:
            traditional_context: Traditional knowledge context
            prior_art: Prior art references
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence
        confidence = 0.7
        
        # Increase confidence if we found traditional knowledge
        if len(traditional_context) > 0:
            confidence += 0.1
        
        # Increase confidence if we found prior art
        if len(prior_art) > 0:
            confidence += 0.1
        
        # Cap at 0.95
        confidence = min(confidence, 0.95)
        
        return confidence


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
