"""
Chat models for AyurPedia API.
Defines request and response models for chat endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation model for referencing sources."""
    text: str = Field(..., description="Citation text")
    source: str = Field(..., description="Source document name")
    section: str = Field(..., description="Section or article reference")
    url: Optional[str] = Field(None, description="Optional URL to source")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., description="User query", min_length=1, max_length=1000)
    jurisdiction: str = Field(default="India", description="Jurisdiction: India, International, or Both")
    language: str = Field(default="en", description="Target response language (e.g. 'en', 'hi', 'ta', 'te', 'mr', 'bn', etc.)")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    classification: Optional[Dict[str, Any]] = Field(None, description="Optional classification override")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the disclosure requirements under WIPO GRATK?",
                "jurisdiction": "International"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Generated response")
    citations: List[Citation] = Field(default_factory=list, description="List of citations")
    confidence: str = Field(..., description="Confidence level: High, Medium, or Low")
    disclaimer: str = Field(
        default="This is information, not legal advice. Consult a qualified legal professional.",
        description="Legal disclaimer"
    )
    classification: Optional[str] = Field(None, description="Classification result if applicable")
    jurisdiction: str = Field(..., description="Jurisdiction used for search")
    reasoning: Optional[str] = Field(None, description="Step-by-step legal reasoning (from agentic RAG)")
    graph_path: Optional[List[str]] = Field(None, description="Reasoning path through knowledge graph")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Under WIPO GRATK Treaty 2024, Article 3 requires disclosure of...",
                "citations": [
                    {
                        "text": "WIPO GRATK Treaty 2024, Article 3.1(a)",
                        "source": "WIPO GRATK Treaty 2024",
                        "section": "Article 3.1(a)"
                    }
                ],
                "confidence": "High",
                "disclaimer": "This is information, not legal advice. Consult a qualified legal professional.",
                "classification": "Proprietary",
                "jurisdiction": "International"
            }
        }
