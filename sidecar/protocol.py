# ipcha/protocol.py

import logging
import time
from typing import Dict, Any

from ipcha.utils.models import get_model_family
from ipcha.config import DOW_INVOCATION_COST_CEILING
from ipcha.models import Claim, User
from ipcha.exceptions import ModelDiversityError, InvocationCostExceededError

logger = logging.getLogger(__name__)


class DebateSession:
    """
    Represents a debate session, enforcing protocol rules upon initialization.
    """
    def __init__(self, proponent_model: str, ipcha_model: str):
        """
        Initializes a new debate session, validating the configuration.

        Args:
            proponent_model: The model name for the Proponent agent.
            ipcha_model: The model name for the Ipcha (fact-checker) agent.

        Raises:
            ModelDiversityError: If both models belong to the same family.
        """
        self.proponent_model = proponent_model
        self.ipcha_model = ipcha_model

        proponent_family = get_model_family(self.proponent_model)
        ipcha_family = get_model_family(self.ipcha_model)

        if proponent_family and ipcha_family and proponent_family == ipcha_family:
            error_msg = (
                f"Model diversity violation: Proponent and Ipcha Agent cannot "
                f"use models from the same family ('{proponent_family}'). "
                f"Proponent: '{self.proponent_model}', Ipcha: '{self.ipcha_model}'."
            )
            raise ModelDiversityError(error_msg, family=proponent_family)

        # Session is valid, proceed with other initializations
        self.is_active = True
        self.history = []


def estimate_claim_cost(claim: Claim) -> int:
    """
    Estimates the computational cost of processing a claim.
    This is a preliminary model based on text length and component count.
    """
    # Weight character count
    text_cost = len(claim.text)
    # Weight number of components, assuming each adds significant overhead
    component_cost = len(claim.components) * 150
    return text_cost + component_cost


def check_invocation_cost(claim: Claim, user: User):
    """
    Enforces the per-invocation cost ceiling.

    Raises:
        InvocationCostExceededError: If the estimated cost exceeds the ceiling.
    """
    estimated_cost = estimate_claim_cost(claim)

    if estimated_cost > DOW_INVOCATION_COST_CEILING:
        log_payload: Dict[str, Any] = {
            "event": "dow_rejection",
            "userID": user.id,
            "timestamp": time.time(),
            "rejectionType": "invocation_cost_ceiling",
            "observedValue": estimated_cost,
            "limitValue": DOW_INVOCATION_COST_CEILING,
        }
        logger.warning(log_payload)
        raise InvocationCostExceededError(
            "Claim cost exceeds the maximum allowed limit.",
            user_id=user.id,
            observed_value=estimated_cost,
            limit_value=DOW_INVOCATION_COST_CEILING
        )
