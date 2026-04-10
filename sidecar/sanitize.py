import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import bleach

# --- Data Structures ---

@dataclass(frozen=True)
class Anomaly:
    """Represents a single detected anomaly in the input content."""
    anomaly_type: str
    description: str
    triggered_pattern: Optional[str] = None

@dataclass(frozen=True)
class SanitizerConfig:
    """Configuration for the sanitization pipeline."""
    allowed_tags: List[str] = field(default_factory=lambda: [
        'p', 'b', 'i', 'ul', 'ol', 'li', 'blockquote', 'a'
    ])
    allowed_attributes: Dict[str, List[str]] = field(default_factory=lambda: {
        'a': ['href']
    })
    allowed_protocols: List[str] = field(default_factory=lambda: ['http', 'https'])
    ipi_patterns: List[str] = field(default_factory=lambda: [
        r"ignore .* and follow new instructions",
        r"ignore all previous instructions",
        r"your new instructions are",
        r"stop your task and do this instead",
        r"disregard the above and do the following",
    ])

@dataclass(frozen=True)
class SanitizationResult:
    """The result of a sanitization operation."""
    sanitized_content: str
    is_clean: bool
    anomalies_detected: List[Anomaly]
    original_hash: str

# --- Sanitization Pipeline ---

def sanitize_artifact(content: str, config: SanitizerConfig) -> SanitizationResult:
    """
    Processes input content through a multi-layer sanitization pipeline.

    Layers:
    1. Unicode Normalization: Normalizes form and strips dangerous characters.
    2. Structural Cleaning: Uses bleach to remove disallowed HTML tags/attributes.
    3. Heuristic Detection: Scans for known IPI phrases using regex.
    """
    anomalies: List[Anomaly] = []
    original_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Layer 1: Unicode Normalization
    # NFKC is chosen for its aggressive compatibility normalization.
    normalized_content = unicodedata.normalize('NFKC', content)
    # Strip control characters (category C) and non-space separators (Zl, Zp).
    # Preserve normal spaces (Zs) to avoid collapsing readable text.
    cleaned_unicode_content = "".join(
        ch for ch in normalized_content
        if unicodedata.category(ch)[0] != "C" and unicodedata.category(ch) not in ("Zl", "Zp")
    )

    if cleaned_unicode_content != content:
        anomalies.append(Anomaly(
            anomaly_type="UnicodeNormalization",
            description="Input contained non-standard Unicode characters or formatting that was removed."
        ))

    # Layer 2: Structural Sanitization (HTML)
    structurally_sanitized_content = bleach.clean(
        cleaned_unicode_content,
        tags=config.allowed_tags,
        attributes=config.allowed_attributes,
        protocols=config.allowed_protocols,
        strip=True
    )

    if structurally_sanitized_content != cleaned_unicode_content:
        anomalies.append(Anomaly(
            anomaly_type="StructuralViolation",
            description="Disallowed HTML tags or attributes were stripped from the content."
        ))

    # Layer 3: Heuristic Instruction Detection
    for pattern in config.ipi_patterns:
        if re.search(pattern, structurally_sanitized_content, re.IGNORECASE):
            anomalies.append(Anomaly(
                anomaly_type="HeuristicDetection",
                description="Potential IPI phrase detected.",
                triggered_pattern=pattern
            ))

    is_clean = not bool(anomalies)

    return SanitizationResult(
        sanitized_content=structurally_sanitized_content,
        is_clean=is_clean,
        anomalies_detected=anomalies,
        original_hash=original_hash
    )
