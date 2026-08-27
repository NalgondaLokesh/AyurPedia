"""
Classification API endpoint for AyurPedia.
Handles formulation classification under regulatory categories using AI and RAG.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from ..core.mongodb import get_mongodb
from ..core.llm import get_llm_client
from ..rag.retriever import Retriever
from ..core.database import QdrantDB
from ..core.config import get_config
from ..utils.validators import validate_classification, sanitize_input


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create router
router = APIRouter()


# Request/Response Models
class ClassificationRequest(BaseModel):
    """Request model for formulation classification."""
    
    # Support both the original format and the frontend format
    formulation_name: Optional[str] = Field(None, description="Name of the herbal formulation")
    formulation_description: Optional[str] = Field(None, description="Description of the formulation (frontend format)")
    ingredients: Optional[List[str]] = Field(None, description="List of ingredients in the formulation")
    dosage_form: Optional[str] = Field(None, description="Dosage form (tablet, liquid, powder, etc.)")
    intended_use: Optional[str] = Field(None, description="Intended use/indication")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    additional_info: Optional[str] = Field(None, description="Any additional information")


class ClassificationResponse(BaseModel):
    """Response model for classification results."""
    
    classification: str = Field(..., description="Classification category")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation for the classification")
    regulatory_requirements: Optional[List[str]] = Field(None, description="Applicable regulatory requirements")
    key_factors: Optional[List[str]] = Field(None, description="Key factors considered in classification")
    id: str = Field(..., description="Classification record ID")
    ai_generated: bool = Field(True, description="Whether classification was AI-generated")


class ClassificationListResponse(BaseModel):
    """Response model for classification list."""
    
    classifications: List[Dict[str, Any]] = Field(..., description="List of classification records")
    total: int = Field(..., description="Total number of records")


# Valid classification categories
VALID_CLASSIFICATIONS = [
    "Classical",
    "Proprietary", 
    "Ayurveda-Aahar",
    "Cosmetic",
    "Phytopharmaceutical",
    "Nutraceutical",
    "Unknown"
]


def ai_classify_formulation(
    formulation_text: str,
    ingredients: List[str],
    intended_use: str,
    llm_client,
    retriever: Retriever
) -> Dict[str, Any]:
    """Classify a formulation using AI and RAG.
    
    This uses the LLM to analyze the formulation and retrieves relevant
    regulatory context from the vector database for accurate classification.
    
    Args:
        formulation_text: Description or name of the formulation
        ingredients: List of ingredients
        intended_use: Intended use of the formulation
        llm_client: LLM client for AI classification
        retriever: Retriever for RAG context
        
    Returns:
        Dictionary with AI-powered classification results
    """
    try:
        # Build comprehensive formulation description for AI analysis
        formulation_analysis = f"""
Formulation Analysis Request:
- Formulation: {formulation_text}
- Ingredients: {', '.join(ingredients) if ingredients else 'Not specified'}
- Intended Use: {intended_use if intended_use else 'Not specified'}

Please classify this Ayurvedic formulation under Indian regulatory frameworks and provide detailed reasoning.
"""
        
        # Retrieve relevant regulatory context using RAG
        logger.info("Retrieving regulatory context for classification...")
        
        # Search for relevant regulatory information
        regulatory_docs = retriever.search(
            query=f"formulation classification regulatory ayurvedic {formulation_text}",
            jurisdiction="India",
            use_hierarchical=True
        )
        
        # Format RAG context
        rag_context = ""
        if regulatory_docs:
            rag_context = "Relevant Regulatory Context:\n"
            for i, doc in enumerate(regulatory_docs[:3], 1):
                rag_context += f"{i}. {doc.text[:200]}...\n"
        else:
            rag_context = "No specific regulatory documents found. Using general knowledge of Indian Ayurvedic regulatory frameworks."
        
        # AI Classification Prompt
        classification_prompt = f"""You are an expert in Indian Ayurvedic regulatory frameworks and intellectual property law. 

{rag_context}

Formulation to Classify:
{formulation_analysis}

Classification Categories:
1. **Classical**: Traditional formulations from ancient Ayurvedic texts
2. **Proprietary**: Novel, patented, or unique formulations
3. **Ayurveda-Aahar**: Food and nutritional products (FSSAI regulations)
4. **Cosmetic**: External application products for skin, hair, beauty care
5. **Phytopharmaceutical**: Plant-based drug products with therapeutic applications
6. **Nutraceutical**: Dietary supplements with health benefits
7. **Unknown**: Cannot be determined with available information

Provide your analysis in this exact JSON format:
{{
    "classification": "category_name",
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation (2-3 sentences)",
    "regulatory_requirements": ["requirement1", "requirement2"],
    "key_factors": ["factor1", "factor2"]
}}

Consider: Traditional knowledge vs novelty (Section 3(p)), intended use, ingredients, regulatory framework. Keep reasoning concise."""

        # Get AI classification
        logger.info("Requesting AI classification...")
        llm = llm_client.get_llm_with_fallback()
        response = llm.invoke([HumanMessage(content=classification_prompt)])
        response_text = response.content.strip()
        
        # Parse AI response
        logger.info(f"AI response: {response_text[:200]}...")
        
        # Try to extract JSON from response
        import json
        import re
        
        # Look for JSON pattern in response
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        if json_match:
            try:
                classification_result = json.loads(json_match.group())
                
                # Validate required fields
                required_fields = ["classification", "confidence", "reasoning"]
                for field in required_fields:
                    if field not in classification_result:
                        classification_result[field] = "Unknown" if field == "classification" else 0.0 if field == "confidence" else "AI analysis incomplete"
                
                if "regulatory_requirements" not in classification_result:
                    classification_result["regulatory_requirements"] = []
                
                # Ensure classification is valid
                valid_classifications = ["Classical", "Proprietary", "Ayurveda-Aahar", "Cosmetic", "Phytopharmaceutical", "Nutraceutical", "Unknown"]
                if classification_result["classification"] not in valid_classifications:
                    classification_result["classification"] = "Unknown"
                    classification_result["reasoning"] += " [Normalized to Unknown due to invalid category]"
                
                logger.info(f"AI classification completed: {classification_result['classification']} (confidence: {classification_result['confidence']})")
                return classification_result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI JSON response: {e}")
        
        # Fallback if JSON parsing fails
        logger.warning("Using fallback classification due to AI response parsing issues")
        return {
            "classification": "Unknown",
            "confidence": 0.4,
            "reasoning": "AI analysis completed but response format was unclear. Manual review recommended.",
            "regulatory_requirements": ["Regulatory assessment requires manual review"],
            "key_factors": ["AI response parsing issue"]
        }
        
    except Exception as e:
        logger.error(f"AI classification failed: {e}")
        return {
            "classification": "Unknown",
            "confidence": 0.3,
            "reasoning": f"AI classification encountered an error: {str(e)}",
            "regulatory_requirements": ["Manual review required due to system error"],
            "key_factors": ["System error during AI processing"]
        }


@router.post("/classify", response_model=ClassificationResponse, status_code=status.HTTP_200_OK)
async def classify_formulation_endpoint(
    request: ClassificationRequest,
    mongodb = Depends(get_mongodb)
) -> ClassificationResponse:
    """Classify an Ayurvedic formulation under regulatory categories using AI and RAG.
    
    This endpoint uses AI-powered classification with retrieval-augmented generation
    to provide accurate regulatory categorization based on:
    - LLM analysis of formulation characteristics
    - RAG context from legal/regulatory documents
    - Vector database similarity to known formulations
    
    Categories:
    - Classical: Traditional formulations from ancient texts
    - Proprietary: Novel or patented formulations
    - Ayurveda-Aahar: Food/nutritional products per FSSAI
    - Cosmetic: External application products
    - Phytopharmaceutical: Plant-based drug products
    - Nutraceutical: Dietary supplements with health benefits
    - Unknown: Cannot be determined with available information
    
    Args:
        request: Formulation classification request
        mongodb: MongoDB dependency injection
        
    Returns:
        Classification result with AI-powered confidence and regulatory requirements
    """
    try:
        # Log the full request for debugging
        logger.info(f"AI Classification request received - full data: {request.model_dump()}")
        
        # Validate that we have at least some formulation data
        if not request.formulation_name and not request.formulation_description:
            logger.error("No formulation name or description provided")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either formulation_name or formulation_description is required"
            )
        
        # Initialize AI components
        config = get_config()
        llm_client = get_llm_client()
        
        # Initialize retriever with Qdrant
        qdrant_db = QdrantDB(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            embedding_dimension=config.embedding_dimension
        )
        retriever = Retriever(qdrant_db, top_k=5)
        
        # Prepare formulation data for AI analysis
        formulation_text = request.formulation_description or request.formulation_name or ""
        ingredients = request.ingredients or []
        intended_use = request.intended_use or ""
        
        # Perform AI-based classification with RAG
        logger.info("Starting AI-based classification with RAG...")
        classification_result = ai_classify_formulation(
            formulation_text=formulation_text,
            ingredients=ingredients,
            intended_use=intended_use,
            llm_client=llm_client,
            retriever=retriever
        )
        
        # Prepare classification data for storage
        classification_data = {
            "formulation_name": request.formulation_name or request.formulation_description,
            "formulation_description": request.formulation_description,
            "ingredients": request.ingredients or [],
            "dosage_form": request.dosage_form,
            "intended_use": request.intended_use,
            "manufacturer": request.manufacturer,
            "additional_info": request.additional_info,
            "classification": classification_result["classification"],
            "confidence": classification_result["confidence"],
            "reasoning": classification_result["reasoning"],
            "regulatory_requirements": classification_result.get("regulatory_requirements", []),
            "key_factors": classification_result.get("key_factors", []),
            "ai_generated": True
        }
        
        # Save to MongoDB
        classification_id = await mongodb.save_classification(classification_data)
        
        logger.info(f"AI Classification saved with ID: {classification_id}")
        
        return ClassificationResponse(
            classification=classification_result["classification"],
            confidence=classification_result["confidence"],
            reasoning=classification_result["reasoning"],
            regulatory_requirements=classification_result.get("regulatory_requirements", []),
            key_factors=classification_result.get("key_factors", []),
            id=classification_id,
            ai_generated=True
        )
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


@router.get("/classify", response_model=ClassificationListResponse, status_code=status.HTTP_200_OK)
async def list_classifications(
    limit: int = 20,
    mongodb = Depends(get_mongodb)
) -> ClassificationListResponse:
    """List recent formulation classifications.
    
    Args:
        limit: Maximum number of classifications to return
        mongodb: MongoDB dependency injection
        
    Returns:
        List of recent classification records
    """
    try:
        logger.info(f"Listing classifications with limit: {limit}")
        
        classifications = await mongodb.list_classifications(limit=limit)
        
        return ClassificationListResponse(
            classifications=classifications,
            total=len(classifications)
        )
        
    except Exception as e:
        logger.error(f"Failed to list classifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list classifications: {str(e)}"
        )


@router.get("/classify/categories", status_code=status.HTTP_200_OK)
async def get_classification_categories() -> Dict[str, Any]:
    """Get available classification categories.
    
    Returns:
        Dictionary with valid classification categories and their descriptions
    """
    categories = {
        "Classical": "Traditional formulations from ancient Ayurvedic texts like Charaka Samhita, Sushruta Samhita",
        "Proprietary": "Novel, patented, or unique formulations developed through research",
        "Ayurveda-Aahar": "Food and nutritional products regulated under FSSAI Ayurveda-Aahar regulations",
        "Cosmetic": "External application products for skin, hair, and beauty care",
        "Phytopharmaceutical": "Plant-based drug products with therapeutic applications",
        "Nutraceutical": "Dietary supplements providing health benefits beyond basic nutrition",
        "Unknown": "Classification cannot be determined with available information"
    }
    
    return {
        "categories": categories,
        "total": len(categories)
    }


@router.get("/classify/explanation", status_code=status.HTTP_200_OK)
async def get_classification_explanation(jurisdiction: str = "India") -> Dict[str, Any]:
    """Get AI + RAG powered explanation of classification system.
    
    Uses RAG to retrieve relevant regulatory context and AI to generate
    a dynamic, context-aware explanation of the classification system.
    
    Args:
        jurisdiction: Jurisdiction for context-specific explanation
        
    Returns:
        Dictionary with AI-generated explanation and key insights
    """
    try:
        # Initialize AI components
        config = get_config()
        llm_client = get_llm_client()
        
        # Initialize retriever with Qdrant
        qdrant_db = QdrantDB(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            embedding_dimension=config.embedding_dimension
        )
        retriever = Retriever(qdrant_db, top_k=3)
        
        # Retrieve relevant regulatory context using RAG
        logger.info(f"Retrieving classification explanation context for jurisdiction: {jurisdiction}")
        regulatory_docs = retriever.search(
            query=f"formulation classification regulatory categories ayurvedic {jurisdiction}",
            jurisdiction=jurisdiction,
            use_hierarchical=True
        )
        
        # Format RAG context
        rag_context = ""
        if regulatory_docs:
            rag_context = "Relevant Regulatory Context:\n"
            for i, doc in enumerate(regulatory_docs[:2], 1):
                rag_context += f"{i}. {doc.text[:150]}...\n"
        else:
            rag_context = "Using general knowledge of Indian Ayurvedic regulatory frameworks."
        
        # AI Explanation Generation Prompt
        explanation_prompt = f"""You are an expert in Indian Ayurvedic regulatory frameworks and intellectual property law.

{rag_context}

Jurisdiction: {jurisdiction}

Provide a concise, educational explanation of Ayurvedic formulation classification for users who may be new to regulatory compliance. 

Focus on:
1. Why classification matters for regulatory compliance
2. Brief overview of the main regulatory categories
3. Key factors that determine classification
4. Business impact of correct classification

Keep it under 150 words, simple and accessible for Ayurvedic practitioners, researchers, and small business owners. Avoid legal jargon where possible.

Provide your response in this exact JSON format:
{{
    "headline": "engaging headline",
    "explanation": "150-word explanation",
    "key_categories": ["Classical", "Proprietary", "Ayurveda-Aahar", "Others"],
    "business_impact": "2-3 sentences on business impact"
}}"""

        # Get AI explanation
        llm = llm_client.get_llm_with_fallback()
        response = llm.invoke([HumanMessage(content=explanation_prompt)])
        response_text = response.content.strip()
        
        # Parse AI response
        import json
        import re
        
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                explanation_data = json.loads(json_match.group())
                
                # Ensure required fields
                if "headline" not in explanation_data:
                    explanation_data["headline"] = "Understanding Ayurvedic Regulatory Classification"
                if "explanation" not in explanation_data:
                    explanation_data["explanation"] = "Classification determines which regulatory framework applies to your Ayurvedic formulation."
                if "key_categories" not in explanation_data:
                    explanation_data["key_categories"] = ["Classical", "Proprietary", "Ayurveda-Aahar", "Others"]
                if "business_impact" not in explanation_data:
                    explanation_data["business_impact"] = "Correct classification ensures proper regulatory compliance and market access."
                
                logger.info("AI classification explanation generated successfully")
                return {
                    "ai_generated": True,
                    "jurisdiction": jurisdiction,
                    **explanation_data
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI explanation JSON: {e}")
        
        # Fallback explanation
        return {
            "ai_generated": False,
            "jurisdiction": jurisdiction,
            "headline": "Understanding Ayurvedic Regulatory Classification",
            "explanation": "Classification determines which regulatory framework applies to your Ayurvedic formulation. Different categories have different licensing requirements, approval processes, and compliance standards based on ingredients, intended use, and manufacturing processes.",
            "key_categories": ["Classical", "Proprietary", "Ayurveda-Aahar", "Others"],
            "business_impact": "Correct classification ensures proper regulatory compliance, avoids legal issues, and determines market access requirements."
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI explanation: {e}")
        return {
            "ai_generated": False,
            "jurisdiction": jurisdiction,
            "headline": "Understanding Ayurvedic Regulatory Classification",
            "explanation": "Classification determines which regulatory framework applies to your Ayurvedic formulation. Different categories have different licensing requirements, approval processes, and compliance standards.",
            "key_categories": ["Classical", "Proprietary", "Ayurveda-Aahar", "Others"],
            "business_impact": "Correct classification ensures proper regulatory compliance and market access."
        }


@router.post("/classify/test", status_code=status.HTTP_200_OK)
async def test_classification() -> Dict[str, Any]:
    """Test endpoint to verify classification endpoint is working.
    
    Returns a sample classification request and response for testing.
    """
    # Both formats are now supported
    sample_request_frontend = {
        "formulation_description": "New/proprietary herbal formulation containing herbs: Shatavari intended for dietary use."
    }
    
    sample_request_original = {
        "formulation_name": "Ashwagandha Churna",
        "ingredients": ["Ashwagandha root", "Ginger", "Turmeric"],
        "dosage_form": "Powder",
        "intended_use": "Stress relief and immunity booster",
        "manufacturer": "AyurPharma Ltd",
        "additional_info": "Classical formulation with modern processing"
    }
    
    return {
        "message": "Classification endpoint is working. Use POST /api/classify with either format:",
        "frontend_format": sample_request_frontend,
        "original_format": sample_request_original,
        "required_fields": ["formulation_description (frontend) OR formulation_name + ingredients (original)"],
        "optional_fields": ["dosage_form", "intended_use", "manufacturer", "additional_info"]
    }