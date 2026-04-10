# src/arbitration/models.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ArbitrationStatus(str, Enum):
    """Enumeration for the final status of a claim after arbitration."""
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNCERTAIN = "UNCERTAIN"

class AssessmentInput(BaseModel):
    """
    Represents the essential data from an assessment needed for arbitration.
    """
    id: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class ArbitrationResult(BaseModel):
    """
    Represents the output of the confidence arbitration process.
    """
    final_confidence: Optional[float]
    status: ArbitrationStatus
    contributing_assessment_ids: List[str]
