# ipcha/claim_classifier.py

import re
from typing import Literal

# Patterns that indicate a factually verifiable claim (checked first — higher priority)
_VERIFIABLE_PATTERNS = [
    re.compile(r'\b\d+(\.\d+)+\b'),                          # version numbers: 1.3, 2.0.1
    re.compile(r'\bRFC\s*\d+\b', re.IGNORECASE),             # RFC references
    re.compile(r'\bISO\s*[\w/-]+\b', re.IGNORECASE),         # ISO standards
    re.compile(r'\bCVE-\d{4}-\d+\b', re.IGNORECASE),        # CVE identifiers
    re.compile(r'\bCWE-\d+\b', re.IGNORECASE),               # CWE identifiers
    re.compile(r'\b(must|shall|requires|mandatory)\b', re.IGNORECASE),  # normative keywords
    re.compile(r'\b\d+(\.\d+)?\s*(ms|seconds?|minutes?|hours?|days?|bytes?|kb|mb|gb|tb|%|percent|hz|mhz|ghz|rpm|req/s|rps|ops)\b', re.IGNORECASE),  # quantitative measurements
    re.compile(r'\b(AES|RSA|SHA-?\d*|TLS|HTTPS?|JWT|OAuth\d*)\b', re.IGNORECASE),  # technical protocol names
]

# Patterns that indicate an interpretive/opinion claim
_INTERPRETIVE_PATTERNS = [
    re.compile(r'\b(elegant|well-designed|clean|beautiful|ugly|messy|poor)\b', re.IGNORECASE),  # opinion words
    re.compile(r'\b(should consider|might want|could improve|arguably)\b', re.IGNORECASE),       # hedging phrases
    re.compile(r'\b(best practice|anti-pattern|code smell|technical debt)\b', re.IGNORECASE),    # meta-patterns
]

_MIN_CLAIM_LENGTH = 5


def classify_claim(claim_text: str) -> Literal["VERIFIABLE", "INTERPRETIVE", "UNCLASSIFIABLE"]:
    """
    Classifies a claim as VERIFIABLE, INTERPRETIVE, or UNCLASSIFIABLE.

    Uses heuristic pattern matching only (NLI tie-breaker deferred).
    VERIFIABLE patterns take priority over INTERPRETIVE ones.

    Args:
        claim_text: The raw text of the claim to classify.

    Returns:
        "VERIFIABLE" if the claim contains verifiable factual indicators,
        "INTERPRETIVE" if it contains opinion or hedging language,
        "UNCLASSIFIABLE" if it is too short, empty, or matches no patterns.
    """
    if not claim_text or len(claim_text.strip()) < _MIN_CLAIM_LENGTH:
        return "UNCLASSIFIABLE"

    # Verifiable patterns take priority
    for pattern in _VERIFIABLE_PATTERNS:
        if pattern.search(claim_text):
            return "VERIFIABLE"

    # Interpretive patterns checked second
    for pattern in _INTERPRETIVE_PATTERNS:
        if pattern.search(claim_text):
            return "INTERPRETIVE"

    return "UNCLASSIFIABLE"
