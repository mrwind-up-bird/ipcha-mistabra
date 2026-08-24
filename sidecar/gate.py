# ipcha/gate.py
"""The protocol gate (Definition 5).

G(F) = 1 iff no finding survives unrefuted at severity >= high.
"""

from typing import Iterable, List, Tuple

#: Severities that block the gate when a finding is not refuted.
BLOCKING_SEVERITIES = frozenset({"critical", "high"})

#: The only status that clears a finding out of the gate's way.
CLEARING_STATUS = "refuted"


def blocking_findings(findings: Iterable[dict]) -> List[dict]:
    """Return the findings that hold the gate shut."""
    return [
        f
        for f in findings
        if str(f.get("severity", "")).lower() in BLOCKING_SEVERITIES
        and str(f.get("status", "")).lower() != CLEARING_STATUS
    ]


def default_gate(findings: Iterable[dict]) -> Tuple[str, List[dict]]:
    """Evaluate the gate.

    Returns ("PASS" | "BLOCK", blocking_findings). The blockers are returned
    alongside the verdict so callers can explain a BLOCK without re-deriving it.
    """
    blockers = blocking_findings(findings)
    return ("BLOCK" if blockers else "PASS"), blockers
