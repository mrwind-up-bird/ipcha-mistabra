# src/arbitration/confmad.py
from typing import List, Optional
from ipcha.arbitration.models import (
    AssessmentInput,
    ArbitrationResult,
    ArbitrationStatus,
)

# Thresholds for determining arbitration status
CONFIDENCE_THRESHOLD_ACCEPT = 0.75
CONFIDENCE_THRESHOLD_REJECT = 0.25

def run_confidence_arbitration(
    assessments: List[AssessmentInput],
) -> ArbitrationResult:
    """
    Runs confidence-weighted arbitration based on a simple average.

    Args:
        assessments: A list of assessment inputs, each with an ID and confidence score.

    Returns:
        An ArbitrationResult object with the final confidence, status, and
        a list of assessment IDs that contributed to the result.
    """
    if not assessments:
        return ArbitrationResult(
            final_confidence=None,
            status=ArbitrationStatus.UNCERTAIN,
            contributing_assessment_ids=[],
        )

    contributing_ids = [assessment.id for assessment in assessments]
    total_confidence = sum(assessment.confidence for assessment in assessments)
    average_confidence = total_confidence / len(assessments)

    status: ArbitrationStatus
    if average_confidence > CONFIDENCE_THRESHOLD_ACCEPT:
        status = ArbitrationStatus.ACCEPTED
    elif average_confidence < CONFIDENCE_THRESHOLD_REJECT:
        status = ArbitrationStatus.REJECTED
    else:
        status = ArbitrationStatus.UNCERTAIN

    return ArbitrationResult(
        final_confidence=average_confidence,
        status=status,
        contributing_assessment_ids=contributing_ids,
    )
