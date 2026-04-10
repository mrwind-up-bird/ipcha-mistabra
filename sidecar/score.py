# ipcha/score.py

import abc
from typing import List, Dict, Any, Literal, TypedDict, NamedTuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# From #01: Finding-weighted IS_w scoring (TF-IDF based)
# ---------------------------------------------------------------------------

# Define the structure for a single piece of evidence or "finding"
FindingType = Literal["SUPPORTING", "CONTRADICTING", "NEUTRAL"]

class Finding(TypedDict):
    text: str
    type: FindingType

# Externalized weights for different finding types.
# This allows for tuning without code changes.
FINDING_WEIGHTS: Dict[FindingType, float] = {
    "SUPPORTING": 1.0,
    "CONTRADICTING": -1.5, # Contradictions are weighted more heavily
    "NEUTRAL": 0.0,
}

def calculate_is_w(claim: str, evidence: List[Finding]) -> float:
    """
    Calculates the finding-weighted Integrity Score (IS_w).

    This metric computes the cosine similarity between the claim and each piece of
    evidence, then combines them using a weighted sum based on the finding 'type'.
    This hardens scoring against evidence spamming with irrelevant text.

    Args:
        claim: The claim statement being evaluated.
        evidence: A list of structured findings, each with text and a type.

    Returns:
        A normalized score between -1.5 and 1.0 (based on default weights).
        Returns 0.0 if there is no valid evidence to score.
    """
    if not claim or not evidence:
        return 0.0

    vectorizer = TfidfVectorizer()

    # Collect all text snippets for vectorization
    corpus = [claim] + [e['text'] for e in evidence if e.get('text')]

    # If only the claim exists or no evidence has text, cannot compare.
    if len(corpus) < 2:
        return 0.0

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Handles case where vocabulary is empty (e.g., all stop words)
        return 0.0

    claim_vector = tfidf_matrix[0]
    evidence_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(claim_vector, evidence_vectors).flatten()

    weighted_score = 0.0
    total_weight_magnitude = 0.0

    valid_evidence_count = 0
    for i, e in enumerate(evidence):
        finding_type = e.get('type')
        if finding_type in FINDING_WEIGHTS and e.get('text'):
            weight = FINDING_WEIGHTS[finding_type]
            similarity = similarities[valid_evidence_count]

            weighted_score += weight * similarity
            total_weight_magnitude += abs(weight)
            valid_evidence_count += 1

    if total_weight_magnitude == 0:
        return 0.0

    # Normalize the score by the sum of the absolute weights of processed findings
    # to keep the score bounded and comparable across different evidence sets.
    normalized_score = weighted_score / total_weight_magnitude

    return float(np.round(normalized_score, 4))

# ---------------------------------------------------------------------------
# From #07: Scoring abstraction layer (Jaccard distance based)
# ---------------------------------------------------------------------------

class ScoreResult(NamedTuple):
    """
    Represents the result of a scoring operation, indicating opposition.
    A score of 1.0 represents maximum opposition/contradiction.
    A score of 0.0 represents minimum opposition/equivalence.
    """
    score: float
    metric_name: str
    metadata: Dict[str, Any] | None = None

class ScoringMetric(abc.ABC):
    """
    Abstract base class for all scoring metrics that measure the degree of
    opposition between a proponent's text and the IPCHA system's text.
    """

    @abc.abstractmethod
    def calculate(self, proponent_text: str, ipcha_text: str) -> ScoreResult:
        """
        Calculates the opposition score between two texts.

        Args:
            proponent_text: The text from the proponent.
            ipcha_text: The text from the IPCHA system.

        Returns:
            A ScoreResult object containing the opposition score and metadata.
        """
        pass

class ISwScorer(ScoringMetric):
    """
    Implements the incumbent IS_w (Inverse Similarity by words) scoring metric.

    This implementation uses the Jaccard distance (1 - Jaccard similarity) based
    on word sets as a proxy for opposition. A higher score indicates stronger
    opposition (less word overlap).
    """
    def calculate(self, proponent_text: str, ipcha_text: str) -> ScoreResult:
        """
        Calculates opposition score based on inverse word set similarity.
        """
        proponent_words = set(proponent_text.lower().split())
        ipcha_words = set(ipcha_text.lower().split())

        if not proponent_words or not ipcha_words:
            return ScoreResult(score=0.0, metric_name="is_w")

        intersection_len = len(proponent_words.intersection(ipcha_words))
        union_len = len(proponent_words.union(ipcha_words))

        # Jaccard similarity = |A ∩ B| / |A ∪ B|
        similarity = intersection_len / union_len if union_len > 0 else 0.0

        # Opposition score is the Jaccard distance (1 - similarity)
        opposition_score = 1.0 - similarity

        return ScoreResult(
            score=opposition_score,
            metric_name="is_w",
            metadata={"intersection": intersection_len, "union": union_len}
        )

# This factory function prepares for Phase 4 (Integration)
_SCORERS: Dict[str, ScoringMetric] = {
    "is_w": ISwScorer(),
}

def _ensure_nli_scorer() -> None:
    """Lazily register NliScorer to avoid circular imports at module load time."""
    if "nli" not in _SCORERS:
        from ipcha.nli_scorer import NliScorer as _NliScorer  # noqa: PLC0415
        _SCORERS["nli"] = _NliScorer()


def get_scorer(metric_name: str) -> ScoringMetric:
    """
    Factory function to retrieve a scorer instance by its registered name.

    Args:
        metric_name: The name of the metric to retrieve (e.g., "is_w").

    Returns:
        An instance of a ScoringMetric implementation.

    Raises:
        ValueError: If the requested metric_name is not registered.
    """
    # Register NLI scorer lazily to avoid a circular import at module load time
    # (nli_scorer.py imports from score.py, so top-level cross-import would fail).
    _ensure_nli_scorer()

    scorer = _SCORERS.get(metric_name)
    if not scorer:
        raise ValueError(
            f"Unknown metric: '{metric_name}'. "
            f"Available: {list(_SCORERS.keys())}"
        )
    return scorer
