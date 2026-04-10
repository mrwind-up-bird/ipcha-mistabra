# ipcha/nli_scorer.py

import logging
from typing import Dict, List, Optional

from ipcha.score import (
    Finding,
    FINDING_WEIGHTS,
    ISwScorer,
    ScoreResult,
    ScoringMetric,
)
import ipcha.nli_client as nli_client

logger = logging.getLogger("ipcha.nli_scorer")


class NliScorer(ScoringMetric):
    """
    NLI-based scoring metric using the DeBERTa-NLI microservice.

    Implements opposition scoring via natural language inference:
    - calculate(): measures opposition between proponent and IPCHA text using
      contradiction confidence as the opposition signal.
    - score_evidence(): scores a claim against a list of evidence findings,
      weighting by finding type (SUPPORTING/CONTRADICTING/NEUTRAL).

    Falls back to ISwScorer (Jaccard) when the NLI service is unavailable.
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        self._base_url = base_url
        self._fallback = ISwScorer()

    def calculate(self, proponent_text: str, ipcha_text: str) -> ScoreResult:
        """
        Calculates opposition score between two texts using NLI.

        Uses ipcha_text as premise and proponent_text as hypothesis.
        Opposition score = contradiction confidence from the NLI model.

        Falls back to ISwScorer on service unavailability.
        """
        try:
            result = nli_client.classify(
                premise=ipcha_text,
                hypothesis=proponent_text,
                base_url=self._base_url,
            )
            scores = result.get("scores", result)
            contradiction_score = float(scores.get("contradiction", 0.0))
            entailment_score = float(scores.get("entailment", 0.0))
            neutral_score = float(scores.get("neutral", 0.0))
            return ScoreResult(
                score=round(contradiction_score, 4),
                metric_name="nli",
                metadata={
                    "entailment": entailment_score,
                    "neutral": neutral_score,
                    "contradiction": contradiction_score,
                },
            )
        except Exception as exc:
            logger.warning("NLI service unavailable, falling back to ISwScorer: %s", exc)
            return self._fallback.calculate(proponent_text, ipcha_text)

    def score_evidence(
        self,
        claim: str,
        evidence: List[Finding],
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Scores a claim against a list of evidence findings using NLI.

        For each finding, classifies (premise=evidence_text, hypothesis=claim)
        and weights by finding type using FINDING_WEIGHTS (or caller-supplied
        weights). Normalizes by the sum of absolute weights.

        Returns 0.0 when evidence is empty or NLI service fails.
        """
        if not evidence:
            return 0.0

        effective_weights = weights if weights is not None else FINDING_WEIGHTS

        try:
            weighted_score = 0.0
            total_weight_magnitude = 0.0

            for finding in evidence:
                finding_type = finding.get("type")
                evidence_text = finding.get("text", "")
                if not evidence_text or finding_type not in effective_weights:
                    continue

                weight = effective_weights[finding_type]

                # Classify evidence relative to the claim
                result = nli_client.classify(
                    premise=evidence_text,
                    hypothesis=claim,
                    base_url=self._base_url,
                )

                # Use the NLI label confidence that best matches the finding type
                scores = result.get("scores", result)
                if finding_type == "SUPPORTING":
                    confidence = float(scores.get("entailment", 0.0))
                elif finding_type == "CONTRADICTING":
                    confidence = float(scores.get("contradiction", 0.0))
                else:
                    # NEUTRAL — NLI neutral confidence
                    confidence = float(scores.get("neutral", 0.0))

                weighted_score += weight * confidence
                total_weight_magnitude += abs(weight)

            if total_weight_magnitude == 0.0:
                return 0.0

            return round(weighted_score / total_weight_magnitude, 4)

        except Exception as exc:
            logger.warning("NLI service unavailable in score_evidence: %s", exc)
            return 0.0
