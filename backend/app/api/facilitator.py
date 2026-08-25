"""
Facilitator escalation API endpoint.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ..core.mongodb import get_mongodb

router = APIRouter(prefix="/api/facilitator", tags=["Facilitator"])

class FacilitatorRequest(BaseModel):
    name: str = Field(..., min_length=1, description="User full name")
    email: str = Field(..., min_length=3, description="User email or contact")
    phone: Optional[str] = Field(None, description="Optional phone number")
    topic: str = Field(..., description="Query topic or formulation name")
    message: str = Field(..., description="Detailed description of regulatory/IPR issue")
    jurisdiction: Optional[str] = Field("India", description="Applicable jurisdiction")
    conversation_id: Optional[str] = Field(None, description="Optional linked chat session ID")

@router.post("/request")
async def submit_facilitator_request(request: FacilitatorRequest):
    """Submit a request for human legal facilitator assistance."""
    mongo = get_mongodb()
    record_id = await mongo.save_facilitator_request(request.model_dump())
    return {
        "status": "success",
        "ticket_id": record_id,
        "message": "Your legal facilitator escalation request has been submitted successfully. A specialist will review your inquiry."
    }
