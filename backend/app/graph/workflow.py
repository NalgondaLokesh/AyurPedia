"""
LangGraph workflow module for AyurPedia.
Handles the main workflow orchestration for classification and RAG.
"""

import logging
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from .classification import ClassificationNode
from .routing import RoutingNode
from .validation import ValidationNode
from ..models.document import DocumentChunk


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """State for the LangGraph workflow."""
    query: str
    classification: Optional[str]
    jurisdiction: str
    retrieved_docs: List[DocumentChunk]
    response: Optional[str]
    citations: List[Dict[str, str]]
    confidence: str
    error: Optional[str]


class GraphWorkflow:
    """Main LangGraph workflow for AyurPedia."""
    
    def __init__(self, llm: Any, retriever: Any) -> None:
        """Initialize the workflow with LLM and retriever.
        
        Args:
            llm: LLM instance
            retriever: Retriever instance
        """
        self.llm = llm
        self.retriever = retriever
        
        # Initialize nodes
        self.classification_node = ClassificationNode(llm)
        self.routing_node = RoutingNode()
        self.validation_node = ValidationNode()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        logger.info("LangGraph workflow created")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("route", self._route_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("abstain", self._abstain_node)
        
        # Define edges
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "route")
        workflow.add_conditional_edges(
            "route",
            self._should_retrieve,
            {
                "retrieve": "retrieve",
                "abstain": "abstain"
            }
        )
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "validate")
        workflow.add_conditional_edges(
            "validate",
            self._should_abstain,
            {
                "end": END,
                "abstain": "abstain"
            }
        )
        workflow.add_edge("abstain", END)
        
        return workflow.compile()
    
    def _classify_node(self, state: GraphState) -> GraphState:
        """Classification node: classify the query.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with classification
        """
        logger.info("Executing classification node")
        try:
            classification_result = self.classification_node.classify(state["query"])
            state["classification"] = classification_result["category"]
            state["error"] = None
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            state["classification"] = "Unknown"
            state["error"] = str(e)
        
        return state
    
    def _route_node(self, state: GraphState) -> GraphState:
        """Routing node: determine jurisdiction and workflow path.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with jurisdiction
        """
        logger.info("Executing routing node")
        try:
            routing_result = self.routing_node.route(
                state["query"],
                state["classification"],
                state.get("jurisdiction", "India")
            )
            state["jurisdiction"] = routing_result["jurisdiction"]
            state["error"] = None
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            state["jurisdiction"] = "India"
            state["error"] = str(e)
        
        return state
    
    def _retrieve_node(self, state: GraphState) -> GraphState:
        """Retrieve node: fetch relevant documents.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with retrieved documents
        """
        logger.info("Executing retrieve node")
        try:
            retrieved_docs = self.retriever.search(
                state["query"],
                state["jurisdiction"]
            )
            state["retrieved_docs"] = retrieved_docs
            state["error"] = None
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            state["retrieved_docs"] = []
            state["error"] = str(e)
        
        return state
    
    def _generate_node(self, state: GraphState) -> GraphState:
        """Generate node: generate response with citations.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with response and citations
        """
        logger.info("Executing generate node")
        try:
            from ..rag.chains import RAGChain
            rag_chain = RAGChain(self.llm, self.retriever)
            result = rag_chain.generate(state["query"], state["jurisdiction"])
            
            state["response"] = result["response"]
            state["citations"] = result["citations"]
            state["confidence"] = result["confidence"]
            state["error"] = None
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            state["response"] = "I encountered an error while generating the response."
            state["citations"] = []
            state["confidence"] = "Low"
            state["error"] = str(e)
        
        return state
    
    def _validate_node(self, state: GraphState) -> GraphState:
        """Validate node: validate citations and confidence.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with validation results
        """
        logger.info("Executing validate node")
        try:
            validation_result = self.validation_node.validate(
                state["response"],
                state["citations"],
                state["retrieved_docs"],
                state["confidence"]
            )
            state["confidence"] = validation_result["confidence"]
            state["error"] = None
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            state["confidence"] = "Low"
            state["error"] = str(e)
        
        return state
    
    def _abstain_node(self, state: GraphState) -> GraphState:
        """Abstain node: handle out-of-scope queries.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with abstention response
        """
        logger.info("Executing abstain node")
        state["response"] = "I'm sorry, but I cannot provide information on this topic as it falls outside the scope of the available legal documents. I can help with questions related to intellectual property law, traditional knowledge protection, genetic resources, and related regulatory frameworks in India and international treaties."
        state["citations"] = []
        state["confidence"] = "Low"
        
        return state
    
    def _should_retrieve(self, state: GraphState) -> str:
        """Determine if retrieval should proceed.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node: "retrieve" or "abstain"
        """
        # If no documents retrieved or classification is Unknown, abstain
        if state["classification"] == "Unknown":
            return "abstain"
        
        # Otherwise proceed with retrieval
        return "retrieve"
    
    def _should_abstain(self, state: GraphState) -> str:
        """Determine if workflow should abstain.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node: "end" or "abstain"
        """
        # If confidence is too low, abstain
        from ..core.config import get_config
        config = get_config()
        
        confidence_map = {"High": 0.8, "Medium": 0.6, "Low": 0.4}
        confidence_score = confidence_map.get(state["confidence"], 0.5)
        
        if confidence_score < config.confidence_threshold:
            return "abstain"
        
        return "end"
    
    def run(self, query: str, jurisdiction: str = "India", 
            classification_override: Optional[str] = None) -> Dict[str, Any]:
        """Execute the workflow.
        
        Args:
            query: User query
            jurisdiction: Jurisdiction to search
            classification_override: Optional classification override
            
        Returns:
            Dictionary with workflow results
        """
        logger.info(f"Running workflow for query: '{query}'")
        
        # Initialize state
        initial_state: GraphState = {
            "query": query,
            "classification": classification_override,
            "jurisdiction": jurisdiction,
            "retrieved_docs": [],
            "response": None,
            "citations": [],
            "confidence": "Low",
            "error": None
        }
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            logger.info("Workflow completed successfully")
            
            return {
                "query": final_state["query"],
                "classification": final_state["classification"],
                "jurisdiction": final_state["jurisdiction"],
                "response": final_state["response"],
                "citations": final_state["citations"],
                "confidence": final_state["confidence"],
                "error": final_state["error"],
                "success": final_state["error"] is None
            }
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "query": query,
                "classification": "Unknown",
                "jurisdiction": jurisdiction,
                "response": "I encountered an error while processing your request.",
                "citations": [],
                "confidence": "Low",
                "error": str(e),
                "success": False
            }
