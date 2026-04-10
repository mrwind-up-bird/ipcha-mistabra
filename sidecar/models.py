# ipcha/models.py

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class User:
    id: str


@dataclass
class Claim:
    id: str
    text: str
    components: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class VerificationResult:
    """Represents the outcome of a verification process."""
    is_verified: bool
    confidence: float
    reason: str
    agent_name: str
