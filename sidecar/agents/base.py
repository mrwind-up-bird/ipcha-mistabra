# ipcha/agents/base.py
from abc import ABC, abstractmethod
from ipcha.models import Claim, VerificationResult

class VerificationAgent(ABC):
    """Abstract base class for all verification agents."""

    @abstractmethod
    def verify(self, claim: Claim) -> VerificationResult:
        """
        Verifies a given claim and returns a result.

        Args:
            claim: The Claim object to be verified.

        Returns:
            A VerificationResult object.
        """
        pass
