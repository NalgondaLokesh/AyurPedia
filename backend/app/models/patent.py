"""
Pydantic models for Patent Novelty Checker.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level for patent novelty."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Section3pStatus(str, Enum):
    """Section 3(p) compliance status."""
    PATENTABLE = "Patentable"
    PARTIALLY_PATENTABLE = "Partially Patentable"
    NOT_PATENTABLE = "Not Patentable"
    UNCERTAIN = "Uncertain"


class PriorArtReference(BaseModel):
    """Reference to prior art found during search."""
    source: str = Field(..., description="Source of prior art (e.g., 'Charaka Samhita', 'Patent IN2023XXXXXXA')")
    citation: str = Field(..., description="Specific citation or reference")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    description: str = Field(..., description="Description of the prior art")
    url: Optional[str] = Field(None, description="URL to the source if available")


class ComponentNovelty(BaseModel):
    """Novelty analysis for a formulation component."""
    component: str = Field(..., description="Component name (e.g., 'Ingredients', 'Process', 'Combination')")
    score: float = Field(..., ge=0.0, le=100.0, description="Novelty score (0-100)")
    risk_level: RiskLevel = Field(..., description="Risk level for this component")
    analysis: str = Field(..., description="Detailed analysis of novelty")
    traditional_references: List[str] = Field(default_factory=list, description="References to traditional knowledge")


class Section3pAnalysis(BaseModel):
    """Section 3(p) compliance analysis."""
    status: Section3pStatus = Field(..., description="Compliance status")
    analysis: str = Field(..., description="Detailed analysis of Section 3(p) compliance")
    patentable_elements: List[str] = Field(default_factory=list, description="Elements that are patentable")
    non_patentable_elements: List[str] = Field(default_factory=list, description="Elements that are not patentable")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for patent filing")


class PatentNoveltyRequest(BaseModel):
    """Request for patent novelty analysis."""
    formulation_name: str = Field(..., description="Name of the formulation")
    ingredients: List[str] = Field(..., description="List of ingredients")
    process: str = Field(..., description="Preparation process or method")
    intended_use: str = Field(..., description="Intended therapeutic or commercial use")
    novelty_claim: Optional[str] = Field(None, description="Specific novelty claim (e.g., enhanced bioavailability)")
    jurisdiction: str = Field(default="India", description="Jurisdiction for analysis")


class PatentNoveltyResponse(BaseModel):
    """Response from patent novelty analysis."""
    formulation_name: str = Field(..., description="Name of the formulation analyzed")
    novelty_score: float = Field(..., ge=0.0, le=100.0, description="Overall novelty score (0-100)")
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    component_novelty: List[ComponentNovelty] = Field(..., description="Novelty breakdown by component")
    prior_art: List[PriorArtReference] = Field(..., description="Prior art references found")
    section3p_analysis: Section3pAnalysis = Field(..., description="Section 3(p) compliance analysis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the analysis (0-1)")
    ai_generated: bool = Field(default=True, description="Whether the analysis was AI-generated")
    disclaimer: str = Field(default="This analysis is for informational purposes only and does not constitute legal advice. Consult a qualified patent attorney for professional guidance.", description="Legal disclaimer")


__all__ = [
    'RiskLevel',
    'Section3pStatus',
    'PriorArtReference',
    'ComponentNovelty',
    'Section3pAnalysis',
    'PatentNoveltyRequest',
    'PatentNoveltyResponse',
]
