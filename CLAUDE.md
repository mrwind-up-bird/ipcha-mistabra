# CLAUDE.md – Ipcha Mistabra Protocol: Backcheck & Implementation

## Context

You are working on the **Ipcha Mistabra Protocol** — a trialectic verification
system for epistemically robust text reviews. The paper is at `./main.tex`.
The protocol has three roles: **Proponent** (thesis), **Ipcha Agent** (antithesis),
**Auditor** (synthesis). The key metric is the **Ipcha Score** (cosine-divergence
between Proponent and Auditor outputs).

This project has two objectives:
1. **Backcheck**: Validate the paper's claims against its own protocol.
2. **Implementation**: Build a working Python reference implementation.

---

## Objective 1: Paper Backcheck (Ipcha-on-Ipcha)

Run the IM Protocol on the paper itself. Use `main.tex` as the text artifact $T$.

### Step 1 — Claim Extraction
Extract all atomic, verifiable claims from `main.tex`. Output as JSON:
```json
[
  {
    "id": "C001",
    "claim": "<atomic statement>",
    "source_location": "<section/line reference>",
    "assumptions": [
      {"id": "A001", "text": "<unstated prerequisite>"}
    ]
  }
]
```
Save to `backcheck/claims.json`.

Focus on:
- Novelty claims (Section 1.1 Research Gap)
- The Ipcha Score definition and its claimed properties (Section 5)
- Domain-agnosticity claims
- The differentiation table (Table 1) — verify each checkmark/dash
- Evaluation hypotheses (Table 3)
- IP/legal statements (Section 7.4)

### Step 2 — Contradict (Ipcha Pass)
For each claim in `claims.json`, construct the strongest counter-argument.
Check against these authority documents:
- Fagan 1976 (original inspection paper)
- Bai et al. 2022 (Constitutional AI)
- Du et al. 2024 (Multi-Agent Debate)
- Sharma et al. 2024 (Sycophancy)
- PatG §3 / EPC Art. 54 (novelty law)

Output findings to `backcheck/findings.json`:
```json
[
  {
    "id": "F001",
    "claim_id": "C001",
    "counter_hypothesis": "<strongest objection>",
    "authority_violations": [],
    "missing_evidence": ["<what's needed>"],
    "severity": "critical|high|medium|low",
    "status": "accepted|refuted|needs-evidence"
  }
]
```

### Step 3 — Audit Resolution
Merge findings. Apply gate rule:
$G(F) = 0$ if any finding with status ≠ refuted AND severity ≥ high.

Output `backcheck/audit_report.md` with:
- Finding table (ID, severity, status, remediation)
- Gate decision (PASS/BLOCK)
- Diff against the F1–F9 findings from the original Ipcha review (documented
  in the paper's changelog — were all findings adequately addressed?)

### Step 4 — Compute Ipcha Score
Compare the v1.0.0 paper (pre-fix) against v1.1.0 (post-fix).
Use `text-embedding-3-large` (as specified in the paper).
Report: IS value, interpretation band, and whether the score aligns with
the actual correction magnitude.

---

## Objective 2: Reference Implementation

Build a Python package `ipcha/` that implements the protocol.

### Project Structure
```
ipcha/
  __init__.py
  protocol.py        # Main orchestrator (Algorithm 1)
  extract.py          # ExtractClaims (Algorithm 2)
  contradict.py       # IpchaContradict (Algorithm 3)
  audit.py            # AuditAndResolve + MergeAndNormalize
  score.py            # Ipcha Score computation
  gate.py             # Gate rule evaluation
  models.py           # Pydantic models: Claim, Assumption, Evidence, Finding
  prompts/
    extract.txt       # Prompt template from Appendix C
    contradict.txt    # Prompt template from Appendix C
    proponent.txt     # Proponent review prompt
    auditor.txt       # Auditor synthesis prompt
  authority/          # Authority document store (placeholder)
tests/
  test_models.py      # Pydantic model validation
  test_score.py       # Ipcha Score unit tests
  test_gate.py        # Gate rule unit tests
  test_protocol.py    # Integration test with mock LLM
backcheck/            # Output from Objective 1
  claims.json
  findings.json
  audit_report.md
pyproject.toml
README.md
```

### Key Implementation Details

#### models.py — Data Structures (Definition 1–5)
```python
from pydantic import BaseModel
from enum import Enum
from typing import Optional

class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class FindingStatus(str, Enum):
    accepted = "accepted"
    refuted = "refuted"
    needs_evidence = "needs-evidence"

class Assumption(BaseModel):
    id: str
    text: str

class Claim(BaseModel):
    id: str
    claim: str
    source_sentence: str
    assumptions: list[Assumption] = []

class Evidence(BaseModel):
    id: str
    source: str  # e.g., "BSI 100-2, Section 4.3"
    content: str
    supports_or_refutes: str  # "supports" | "refutes"

class Finding(BaseModel):
    id: str
    claim_id: str
    severity: Severity
    rationale: str
    evidence: list[Evidence] = []
    remediation: Optional[str] = None
    status: FindingStatus
```

#### score.py — Ipcha Score (Equation 1)
```python
import numpy as np
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-large"

def embed(text: str, client: OpenAI) -> np.ndarray:
    resp = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return np.array(resp.data[0].embedding)

def ipcha_score(proponent_output: str, auditor_output: str,
                client: OpenAI) -> float:
    """IS = 1 - cos(embed(Ap), embed(Af))"""
    e_p = embed(proponent_output, client)
    e_f = embed(auditor_output, client)
    cos_sim = np.dot(e_p, e_f) / (np.linalg.norm(e_p) * np.linalg.norm(e_f))
    return float(1.0 - cos_sim)

def finding_weighted_score(findings_delta: list, severity_weights: dict = None) -> float:
    """IS_w = sum of w(f.sev) for findings that changed status."""
    if severity_weights is None:
        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return sum(severity_weights.get(f.severity, 1) for f in findings_delta)
```

#### gate.py — Gate Rule (Definition 5)
```python
from .models import Finding, FindingStatus, Severity

def default_gate(findings: list[Finding]) -> bool:
    """G(F) = 1 iff no unrefuted finding with severity >= high."""
    for f in findings:
        if f.status != FindingStatus.refuted:
            if f.severity in (Severity.critical, Severity.high):
                return False  # BLOCK
    return True  # PASS
```

#### protocol.py — Main Orchestrator (Algorithm 1)
Use the Anthropic Python SDK (`anthropic`) for LLM calls.
Each role gets its own system prompt (from `prompts/`).
The orchestrator:
1. Calls `extract.extract_claims(T)` → claims.json
2. Calls `proponent_review(T, K, C, A)` → proponent_output
3. Calls `contradict.ipcha_contradict(T, K, C, A, O_p, F_p)` → ipcha_output
4. Calls `audit.merge_and_resolve(...)` → final findings
5. Calls `gate.default_gate(F)` → PASS/BLOCK
6. Calls `score.ipcha_score(O_p, O_f)` → IS value
7. Assembles report

### Testing Strategy
- `test_models.py`: Validate Pydantic models accept/reject correct shapes.
- `test_score.py`: Test IS computation with known vectors (mock embeddings).
  Include edge cases: identical texts (IS≈0), orthogonal texts (IS≈1),
  paraphrase (IS should be low — test for false-positive awareness).
- `test_gate.py`: Gate blocks on high+accepted, passes on all-refuted.
- `test_protocol.py`: Mock LLM responses, run full pipeline, verify output schema.

### Environment
- Python 3.12+
- Dependencies: `anthropic`, `openai` (for embeddings), `pydantic>=2.0`, `numpy`
- Use `uv` for dependency management
- All LLM calls must be behind an abstract interface for testing with mocks

### Important Constraints
- The Ipcha Agent prompt MUST include: "Assume the claim is FALSE until proven
  otherwise. Ground every objection in authority docs or logic. Do NOT generate
  contrarian noise without substance."
- All outputs must be structured JSON (Pydantic-validated), not free text.
- Every finding must reference at least one authority document or logical argument.
- The protocol is mandatory: no step can be skipped. If the LLM refuses to
  contradict, log a warning and flag the claim as "needs-evidence."

---

## Quality Gate for This Task

Before marking this task complete, verify:
- [ ] `backcheck/claims.json` contains ≥10 extracted claims from the paper
- [ ] `backcheck/findings.json` contains counter-arguments for each claim
- [ ] `backcheck/audit_report.md` includes gate decision and F1–F9 diff
- [ ] All Pydantic models validate correctly
- [ ] `score.py` handles edge cases (identical, orthogonal, paraphrase)
- [ ] `gate.py` correctly blocks on high+accepted findings
- [ ] `test_protocol.py` passes with mock LLM
- [ ] No hardcoded API keys anywhere
- [ ] README.md explains setup and usage
