"""
Classification node module for AyurPedia.
Handles formulation classification using LLM.
"""

import logging
import re
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from ..rag.prompts import CLASSIFICATION_PROMPT


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassificationNode:
    """Classification node for LangGraph workflow."""
    
    def __init__(self, llm: Any) -> None:
        """Initialize classification node with LLM.
        
        Args:
            llm: LLM instance for classification
        """
        self.llm = llm
        self.categories = [
            "Classical",
            "Proprietary",
            "Ayurveda-Aahar",
            "Cosmetic",
            "Phytopharmaceutical",
            "Nutraceutical",
            "Unknown"
        ]
        logger.info("ClassificationNode initialized")
    
    def classify(self, formulation_description: str) -> Dict[str, Any]:
        """Classify a formulation description.
        
        Args:
            formulation_description: Description of the formulation
            
        Returns:
            Dictionary with classification result
        """
        logger.info(f"Classifying formulation: '{formulation_description[:100]}...'")
        
        try:
            # Generate classification using LLM
            prompt = CLASSIFICATION_PROMPT.format(
                formulation_description=formulation_description
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse classification from response
            classification = self._parse_classification(response_text)
            
            logger.info(f"Classification result: {classification['category']} (confidence: {classification['confidence']})")
            
            return classification
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "relevant_laws": [],
                "description": "Classification failed due to an error"
            }
    
    def _parse_classification(self, response: str) -> Dict[str, Any]:
        """Parse classification from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Dictionary with parsed classification
        """
        # Default values
        result = {
            "category": "Unknown",
            "confidence": 0.0,
            "relevant_laws": [],
            "description": ""
        }
        
        try:
            # Extract category
            category_match = re.search(r'Category:\s*(.+)', response, re.IGNORECASE)
            if category_match:
                category = category_match.group(1).strip()
                # Validate category
                if category in self.categories:
                    result["category"] = category
                else:
                    # Try to find closest match
                    for valid_category in self.categories:
                        if valid_category.lower() in category.lower():
                            result["category"] = valid_category
                            break
            
            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*([0-9.]+)', response, re.IGNORECASE)
            if confidence_match:
                try:
                    result["confidence"] = float(confidence_match.group(1))
                except ValueError:
                    result["confidence"] = 0.5
            
            # Extract relevant laws
            laws_match = re.search(r'Relevant Laws:\s*(.+)', response, re.IGNORECASE)
            if laws_match:
                laws_text = laws_match.group(1)
                # Split by common delimiters
                laws = re.split(r'[,;]\s*', laws_text)
                result["relevant_laws"] = [law.strip() for law in laws if law.strip()]
            
            # Extract description
            desc_match = re.search(r'Description:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
            if desc_match:
                result["description"] = desc_match.group(1).strip()
            
        except Exception as e:
            logger.warning(f"Failed to parse classification response: {e}")
        
        return result
    
    def map_to_jurisdiction(self, category: str) -> str:
        """Map classification to relevant jurisdiction.
        
        Args:
            category: Classification category
            
        Returns:
            Jurisdiction: India, International, or Both
        """
        jurisdiction_map = {
            "Classical": "India",
            "Proprietary": "India",
            "Ayurveda-Aahar": "India",
            "Cosmetic": "India",
            "Phytopharmaceutical": "India",
            "Nutraceutical": "India",
            "Unknown": "India"
        }
        
        return jurisdiction_map.get(category, "India")
