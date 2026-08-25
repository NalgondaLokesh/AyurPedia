"""
Classification models for AyurPedia API.
Defines request and response models for classification endpoints.
"""

from typing import List
from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Request model for classification endpoint."""
    formulation_description: str = Field(
        ...,
        description="Description of the formulation to classify",
        min_length=10,
        max_length=2000
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "formulation_description": "A new herbal supplement with ashwagandha and turmeric for stress relief"
            }
        }


class ClassificationResponse(BaseModel):
    """Response model for classification endpoint."""
    category: str = Field(..., description="Classification category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    relevant_laws: List[str] = Field(default_factory=list, description="List of relevant laws")
    description: str = Field(..., description="Explanation of classification")
    jurisdiction: str = Field(default="India", description="Recommended jurisdiction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Ayurveda-Aahar",
                "confidence": 0.85,
                "relevant_laws": [
                    "FSSAI Ayurveda Aahar Regulations 2022",
                    "Patents Act 1970"
                ],
                "description": "This formulation falls under Ayurveda-Aahar category as it uses herbs listed in Schedule A and is intended for dietary use.",
                "jurisdiction": "India"
            }
        }
