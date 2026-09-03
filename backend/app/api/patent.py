"""
Patent Novelty Checker API endpoints.
Analyzes Ayurvedic formulations for patent novelty and Section 3(p) compliance.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from ..models.patent import PatentNoveltyRequest, PatentNoveltyResponse
from ..graph.agents import PatentNoveltyAgent
from ..rag.retriever import Retriever
from ..core.database import QdrantDB
from ..core.config import get_config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/patent", tags=["Patent Novelty Checker"])


# Global agent instance
_patent_agent: PatentNoveltyAgent = None


def get_patent_agent() -> PatentNoveltyAgent:
    """Get or initialize global patent novelty agent."""
    global _patent_agent
    if _patent_agent is None:
        config = get_config()
        qdrant_db = QdrantDB(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            embedding_dimension=config.embedding_dimension
        )
        retriever = Retriever(qdrant_db, top_k=5)
        _patent_agent = PatentNoveltyAgent(retriever)
    return _patent_agent


@router.post("/novelty-check", status_code=status.HTTP_200_OK, response_model=PatentNoveltyResponse)
async def check_patent_novelty(request: PatentNoveltyRequest) -> PatentNoveltyResponse:
    """
    Analyze formulation novelty and Section 3(p) compliance.
    
    This endpoint analyzes Ayurvedic formulations to determine:
    - Overall novelty score (0-100)
    - Risk level (High/Medium/Low)
    - Component-wise novelty breakdown (Ingredients, Process, Combination)
    - Prior art references from traditional knowledge
    - Section 3(p) compliance status and recommendations
    
    Args:
        request: Patent novelty analysis request with formulation details
        
    Returns:
        Patent novelty analysis response with scores, prior art, and recommendations
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Patent novelty check request for: {request.formulation_name}")
        
        # Get patent agent
        agent = get_patent_agent()
        
        # Perform novelty analysis
        response = agent.analyze_novelty(request)
        
        logger.info(f"Patent novelty check completed: score={response.novelty_score}, "
                   f"risk={response.risk_level}, status={response.section3p_analysis.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Patent novelty check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Patent novelty analysis failed: {str(e)}"
        )


@router.get("/section3p-info", status_code=status.HTTP_200_OK)
async def get_section3p_info() -> Dict[str, Any]:
    """
    Get information about Section 3(p) of the Indian Patents Act.
    
    Returns educational information about Section 3(p) exclusions
    and what can/cannot be patented under Indian law.
    
    Returns:
        Dictionary with Section 3(p) information and examples
    """
    return {
        "section": "3(p)",
        "act": "Indian Patents Act 1970",
        "title": "Exclusions from Patentability",
        "description": "Section 3(p) excludes from patentability the mere discovery of any new property or new use for a known substance, or the mere use of a known process, machine or apparatus unless such known process results in a new product or employs at least one new reactant.",
        "exclusions": [
            "Mere discovery of traditional knowledge",
            "Mere aggregation of known properties",
            "Traditional formulations without innovation",
            "Known substances with new properties only",
            "Known processes without new products or reactants"
        ],
        "patentable_elements": [
            "Novel combinations with synergistic effects",
            "Process innovations with new products or reactants",
            "Enhanced bioavailability methods",
            "New therapeutic applications",
            "Isolation of active compounds with novel properties"
        ],
        "examples": {
            "not_patentable": [
                "Turmeric powder for wound healing (traditional use)",
                "Ashwagandha churna as described in classical texts",
                "Traditional decoction method without modification"
            ],
            "patentable": [
                "Novel nano-emulsion formulation for enhanced absorption",
                "Isolated compound with new therapeutic mechanism",
                "Process yielding a new compound or using new reactant",
                "Synergistic combination with proven enhanced effect"
            ]
        },
        "key_considerations": [
            "Check TKDL (Traditional Knowledge Digital Library) for prior art",
            "Document experimental evidence for novelty claims",
            "Focus on process innovations and novel combinations",
            "Avoid claiming traditional knowledge as novel"
        ]
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def patent_health_check() -> Dict[str, Any]:
    """
    Health check for patent novelty checker.
    
    Returns:
        Health status of patent novelty checker components
    """
    try:
        agent = get_patent_agent()
        return {
            "status": "healthy",
            "patent_agent_initialized": agent is not None,
            "retriever_available": agent.retriever is not None if agent else False
        }
    except Exception as e:
        logger.error(f"Patent health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
