# ipcha/content.py
"""Full-protocol orchestration for POST /content (Algorithm 1).

The protocol runs once over the whole artifact, not once per claim. That is a
deliberate defence: the denial-of-wallet vector recorded in
backcheck/critics.md is claim inflation — a document stuffed with thousands of
trivial claims driving a per-claim fan-out into an unbounded API spiral. Running
whole-artifact caps the cost at four LLM calls regardless of claim count.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ipcha.budget import check_and_update_budget
from ipcha.gate import default_gate
from ipcha.llm.factory import (
    MissingCredentialsError,
    build_client,
    missing_providers,
    provider_for_model,
)
from ipcha.models import Claim, User
from ipcha.protocol import DebateSession, check_invocation_cost
from ipcha.roles import audit_and_resolve, extract_claims, ipcha_contradict, proponent_review
from ipcha.sanitize import SanitizerConfig, sanitize_artifact
from ipcha.score import get_scorer

logger = logging.getLogger("ipcha.content")

DEFAULT_PROPONENT_MODEL = "claude-opus-5"
DEFAULT_IPCHA_MODEL = "gpt-4o"

#: Sanitizer anomalies that abort the run before any LLM call is made.
#: Only prompt-injection hits are fatal; Unicode normalisation and stripped
#: markup are recorded and the run continues on the cleaned text, because NFKC
#: rewrites plenty of legitimate prose (ligatures, non-breaking spaces).
FATAL_ANOMALY_TYPES = frozenset({"HeuristicDetection"})

JOB_KEY_PREFIX = "ipcha:content:job:"
JOB_TTL_SECONDS = 3600


@dataclass
class ProtocolConfig:
    proponent_model: str = DEFAULT_PROPONENT_MODEL
    ipcha_model: str = DEFAULT_IPCHA_MODEL
    auditor_model: Optional[str] = None  # defaults to the proponent model
    authority: List[str] = field(default_factory=list)
    sanitize: bool = True

    def resolved_auditor_model(self) -> str:
        return self.auditor_model or self.proponent_model


class SanitizationRejected(Exception):
    """Raised when the artifact carries a fatal sanitizer anomaly."""

    def __init__(self, anomalies: List[Dict[str, Any]]):
        self.anomalies = anomalies
        super().__init__("Artifact rejected by sanitizer")


def run_protocol(
    text: str,
    config: ProtocolConfig,
    keys: Optional[Dict[str, str]] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the trialectic end to end and return only the verdict.

    Intermediate artefacts (proponent text, ipcha text, claim list) are used and
    discarded; the caller receives the gate decision, the merged findings, the
    Ipcha Score and provenance metadata.
    """
    started = time.monotonic()

    artifact = text
    anomalies: List[Dict[str, Any]] = []
    if config.sanitize:
        result = sanitize_artifact(text, SanitizerConfig())
        anomalies = [
            {"type": a.anomaly_type, "description": a.description, "pattern": a.triggered_pattern}
            for a in result.anomalies_detected
        ]
        fatal = [a for a in anomalies if a["type"] in FATAL_ANOMALY_TYPES]
        if fatal:
            raise SanitizationRejected(fatal)
        artifact = result.sanitized_content

    # --- Cheap, local checks first: a request that cannot run must not be
    # --- metered, so a misconfigured caller never burns a tenant's budget.
    # --- Model diversity is a protocol constraint, not a preference.
    DebateSession(config.proponent_model, config.ipcha_model)

    auditor_model = config.resolved_auditor_model()
    models = [config.proponent_model, config.ipcha_model, auditor_model]

    # Report every provider that lacks a key at once, rather than failing on
    # whichever role happens to run first.
    absent = missing_providers(models, keys)
    if absent:
        raise MissingCredentialsError(
            "No credentials for provider(s): "
            + ", ".join(absent)
            + ". Send keys.<provider> in the request body, the matching header, "
            "or configure the server environment.",
            provider=absent[0],
            model=models[0],
        )

    # --- Denial-of-wallet defence, both layers, before any spend -------------
    user = User(id=tenant_id or "anonymous")
    check_invocation_cost(Claim(id="artifact", text=artifact, components=[]), user)
    budget_remaining = check_and_update_budget(user)

    # One client per provider, not per role: the client is model-agnostic (the
    # model is a per-call argument), and sharing it means a key rejected in one
    # role stays rejected for the rest of the run instead of being retried once
    # per role.
    by_provider: Dict[str, Any] = {}

    def client_for(model_name: str):
        provider = provider_for_model(model_name)
        if provider not in by_provider:
            by_provider[provider] = build_client(model_name, keys)
        return by_provider[provider]

    proponent_client = client_for(config.proponent_model)
    ipcha_client = client_for(config.ipcha_model)
    auditor_client = client_for(auditor_model)

    claims = extract_claims(proponent_client, config.proponent_model, artifact)
    proponent = proponent_review(
        proponent_client, config.proponent_model, artifact, claims, config.authority
    )
    ipcha = ipcha_contradict(
        ipcha_client, config.ipcha_model, artifact, claims, proponent, config.authority
    )
    audit = audit_and_resolve(auditor_client, auditor_model, artifact, proponent, ipcha)

    findings = audit.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    gate, blockers = default_gate(findings)

    score = get_scorer("nli").calculate(
        proponent.get("review", ""), audit.get("summary", "")
    )

    return {
        "gate": gate,
        "ipcha_score": score.score,
        "summary": audit.get("summary", ""),
        "findings": findings,
        "meta": {
            "models": {
                "proponent": config.proponent_model,
                "ipcha": config.ipcha_model,
                "auditor": auditor_model,
            },
            "claims_extracted": len(claims),
            "blocking_findings": len(blockers),
            "score_metric": score.metric_name,
            "sanitizer_anomalies": anomalies,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "budget_remaining": budget_remaining,
        },
    }


# --- Async job store --------------------------------------------------------

def new_job_id() -> str:
    return uuid.uuid4().hex


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


def store_job(redis_client, job_id: str, payload: Dict[str, Any]) -> None:
    redis_client.setex(_job_key(job_id), JOB_TTL_SECONDS, json.dumps(payload))


def load_job(redis_client, job_id: str) -> Optional[Dict[str, Any]]:
    raw = redis_client.get(_job_key(job_id))
    return json.loads(raw) if raw else None
