# ipcha/api.py
import os
import logging
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

import redis as redis_lib

logger = logging.getLogger("ipcha.api")

from ipcha.score import calculate_is_w, Finding, ISwScorer, ScoreResult
from ipcha.nli_scorer import NliScorer
from ipcha.sanitize import sanitize_artifact, SanitizerConfig
from ipcha.authority.validator import CrossChunkValidator
from ipcha.sycophancy_monitor import SycophancyMonitor, MonitorConfig
from ipcha.routing import from_config as load_router
from ipcha.arbitration.confmad import run_confidence_arbitration
from ipcha.arbitration.models import AssessmentInput
from ipcha.content import (
    ProtocolConfig,
    SanitizationRejected,
    DEFAULT_IPCHA_MODEL,
    DEFAULT_PROPONENT_MODEL,
    load_job,
    new_job_id,
    run_protocol,
    store_job,
)
from ipcha.exceptions import (
    BudgetLimitExceededError,
    InvocationCostExceededError,
    ModelDiversityError,
)
from ipcha.llm.base import LLMError
from ipcha.llm.factory import MissingCredentialsError, UnknownModelError
from ipcha.redact import redact_secrets

# --- Globals initialized at startup ---
claim_router = None
sycophancy_monitor = None
redis_client = None
isw_scorer = ISwScorer()
nli_scorer = NliScorer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global claim_router, sycophancy_monitor, redis_client
    # Initialize ClaimRouter from config
    config_path = os.getenv("IPCHA_CONFIG_PATH", "config.yml")
    if os.path.exists(config_path):
        claim_router = load_router(config_path)
    # Initialize SycophancyMonitor
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    monitor_config = MonitorConfig()
    redis_client = redis_lib.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    sycophancy_monitor = SycophancyMonitor(monitor_config, redis_client)
    yield

app = FastAPI(title="IPCHA Sidecar", lifespan=lifespan)

# --- Request/Response Models ---

class ScoreRequest(BaseModel):
    claim: str
    evidence: List[Dict[str, str]]

class OppositionRequest(BaseModel):
    proponent_text: str
    ipcha_text: str

class SanitizeRequest(BaseModel):
    content: str
    config: Optional[Dict[str, Any]] = None

class ValidateRequest(BaseModel):
    chunks: List[str]
    original_query: str
    model: Optional[str] = "gpt-3.5-turbo"

class ArbitrateRequest(BaseModel):
    assessments: List[Dict[str, Any]]

class RouteRequest(BaseModel):
    claim: Dict[str, str]
    classification: str

class ContentRequest(BaseModel):
    content: str
    # Bring-your-own-key. One or more keys per provider; several enable
    # failover. Never stored, logged, or echoed back.
    keys: Dict[str, List[str]] = Field(default_factory=dict)
    proponent_model: str = DEFAULT_PROPONENT_MODEL
    ipcha_model: str = DEFAULT_IPCHA_MODEL
    auditor_model: Optional[str] = None
    authority: List[str] = Field(default_factory=list)
    sanitize: bool = True


class EvaluateRequest(BaseModel):
    dataset: str
    variant: str
    metrics: List[str]
    seed: int = 42

# --- Endpoints ---

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/score")
async def score(req: ScoreRequest):
    findings = [Finding(text=e.get("text", ""), type=e.get("type", "NEUTRAL")) for e in req.evidence]
    weights_used = {"SUPPORTING": 1.0, "CONTRADICTING": -1.5, "NEUTRAL": 0.0}

    # Always compute TF-IDF baseline
    tfidf_result = calculate_is_w(req.claim, findings)

    # Try NLI scorer first; fall back to TF-IDF on failure
    try:
        nli_score = nli_scorer.score_evidence(req.claim, findings)
        return {
            "score": nli_score,
            "score_tfidf": tfidf_result,
            "scorer": "nli",
            "weights_used": weights_used,
        }
    except Exception:
        return {
            "score": tfidf_result,
            "score_tfidf": tfidf_result,
            "scorer": "tfidf",
            "weights_used": weights_used,
        }

@app.post("/score/opposition")
async def score_opposition(req: OppositionRequest):
    result = isw_scorer.calculate(req.proponent_text, req.ipcha_text)
    return {"score": result.score, "metric_name": result.metric_name, "metadata": result.metadata}

@app.post("/sanitize")
async def sanitize(req: SanitizeRequest):
    config = SanitizerConfig()
    if req.config:
        config = SanitizerConfig(
            allowed_tags=req.config.get("allowed_tags", config.allowed_tags),
            ipi_patterns=req.config.get("ipi_patterns", config.ipi_patterns),
        )
    result = sanitize_artifact(req.content, config)
    if not result.is_clean:
        _log_sanitize_rejection(result.anomalies_detected)
    return {
        "sanitized_content": result.sanitized_content,
        "is_clean": result.is_clean,
        "anomalies": [{"type": a.anomaly_type, "description": a.description, "pattern": a.triggered_pattern} for a in result.anomalies_detected],
        "original_hash": result.original_hash,
    }

@app.post("/validate")
async def validate(req: ValidateRequest, request: Request):
    # Accept API key from X-LLM-Api-Key header (injected by Next.js proxy from BYOK)
    api_key = request.headers.get("x-llm-api-key")
    # The OpenAI client is built in the validator's constructor, outside its
    # fail-closed try block. Report a missing credential as a configuration
    # error instead of letting it surface as an opaque 500.
    if not (api_key or os.getenv("OPENAI_API_KEY")):
        raise HTTPException(
            status_code=503,
            detail="No LLM credentials configured; send X-LLM-Api-Key or set OPENAI_API_KEY",
        )
    validator = CrossChunkValidator(api_key=api_key, model=req.model or "gpt-3.5-turbo")
    result = validator.validate(req.chunks, req.original_query)
    metadata = {
        k: redact_secrets(v) if isinstance(v, str) else v
        for k, v in result["metadata"].items()
    }
    return {
        "status": result["status"].value,
        "reason": result["reason"].value if result["reason"] else None,
        "metadata": metadata,
    }

@app.post("/arbitrate")
async def arbitrate(req: ArbitrateRequest):
    assessments = [AssessmentInput(id=a["id"], confidence=a["confidence"]) for a in req.assessments]
    result = run_confidence_arbitration(assessments)
    return {
        "final_confidence": result.final_confidence,
        "status": result.status.value,
        "contributing_ids": result.contributing_assessment_ids,
    }

@app.post("/route")
async def route_claim(req: RouteRequest):
    if not claim_router:
        raise HTTPException(status_code=503, detail="ClaimRouter not initialized")
    from ipcha.models import Claim
    claim = Claim(id=req.claim.get("id", ""), text=req.claim.get("text", ""), components=[])
    result = claim_router.route(claim, req.classification)
    return {
        "is_verified": result.is_verified,
        "confidence": result.confidence,
        "reason": result.reason,
        "agent_name": result.agent_name,
    }

@app.get("/sycophancy/metrics")
async def sycophancy_metrics():
    if not sycophancy_monitor:
        raise HTTPException(status_code=503, detail="SycophancyMonitor not initialized")
    metrics = sycophancy_monitor._calculate_metrics()
    metrics["window_size"] = sycophancy_monitor.config.window_size
    return metrics

@app.get("/audit/rejections")
async def audit_rejections(page: int = 1, limit: int = 20, reason_code: str = None):
    """Query rejection logs from the SQLAlchemy audit database."""
    from ipcha.audit.models import Base, RejectionLog, RejectionReason
    from sqlalchemy import create_engine, desc
    from sqlalchemy.orm import sessionmaker

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        raise HTTPException(status_code=503, detail="DATABASE_URL not configured")

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        query = session.query(RejectionLog).order_by(desc(RejectionLog.created_at))
        if reason_code:
            query = query.filter(RejectionLog.reason_code == RejectionReason(reason_code))
        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()
        return {
            "items": [
                {
                    "id": log.id,
                    "finding_id": log.finding_id,
                    "rejection_source": log.rejection_source,
                    "reason_code": log.reason_code.value,
                    "justification": log.justification,
                    "tenant_id": log.tenant_id,
                    "created_at": str(log.created_at),
                }
                for log in items
            ],
            "total": total,
            "page": page,
        }
    finally:
        session.close()

@app.post("/evaluate")
async def evaluate(req: EvaluateRequest):
    """Run evaluation synchronously. Next.js handles async job wrapping."""
    import importlib
    try:
        ds_mod = importlib.import_module(f"tests.evaluation.datasets.{req.dataset.replace('-', '_')}")
        dataset = ds_mod.get_dataset()
        var_mod = importlib.import_module(f"tests.evaluation.variants.{req.variant.replace('-', '_')}")
        variant = var_mod.get_variant()
        metric_objs = []
        for m in req.metrics:
            m_mod = importlib.import_module(f"tests.evaluation.metrics.{m.replace('-', '_')}")
            metric_objs.append(m_mod.get_metric())
    except (ImportError, AttributeError) as e:
        raise HTTPException(status_code=400, detail=f"Plugin not found: {e}")

    results = []
    for puzzle in dataset:
        output = variant.run(puzzle, seed=req.seed)
        metric_results = [metric.calculate(puzzle, output) for metric in metric_objs]
        results.append({
            "puzzle_id": puzzle["id"],
            "variant_output": output,
            "metric_results": metric_results,
        })
    return {"results": results, "puzzle_count": len(results)}


# --- Full protocol (Algorithm 1) --------------------------------------------

def _collect_keys(request: Request, body_keys: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Merge caller-supplied provider keys.

    Precedence per provider: request body wins, then the matching header, then
    (inside the LLM factory) the server environment. Body and header are not
    concatenated — a caller that brings its own keys never silently falls
    through to another party's credentials.
    """
    keys: Dict[str, List[str]] = {
        provider: [k for k in supplied if k and k.strip()]
        for provider, supplied in (body_keys or {}).items()
    }
    keys = {p: v for p, v in keys.items() if v}

    header_keys = {
        "anthropic": request.headers.get("x-anthropic-api-key"),
        "openai": request.headers.get("x-llm-api-key") or request.headers.get("x-openai-api-key"),
    }
    for provider, value in header_keys.items():
        if value and provider not in keys:
            keys[provider] = [value]
    return keys


def _execute_protocol(text, config, keys, tenant_id) -> Dict[str, Any]:
    """Run the protocol, translating domain errors into HTTP semantics."""
    try:
        return run_protocol(text, config, keys=keys, tenant_id=tenant_id)
    except SanitizationRejected as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": "Artifact rejected by sanitizer", "anomalies": exc.anomalies},
        ) from exc
    except ModelDiversityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InvocationCostExceededError as exc:
        raise HTTPException(
            status_code=413,
            detail={
                "error": str(exc),
                "observed": exc.observed_value,
                "limit": exc.limit_value,
            },
        ) from exc
    except BudgetLimitExceededError as exc:
        raise HTTPException(
            status_code=429,
            detail={
                "error": str(exc),
                "observed": exc.observed_value,
                "limit": exc.limit_value,
            },
            headers={"Retry-After": str(os.getenv("DOW_BUDGET_PERIOD_SECONDS", "3600"))},
        ) from exc
    except UnknownModelError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except MissingCredentialsError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMError as exc:
        # Provider error text can carry the offending key — redact before it
        # reaches the client.
        raise HTTPException(
            status_code=502,
            detail={
                "error": "LLM provider call failed",
                "provider": exc.provider,
                "model": exc.model,
                "provider_status": exc.status_code,
                "detail": redact_secrets(str(exc)),
            },
        ) from exc
    except redis_lib.exceptions.RedisError as exc:
        # Fail closed: without Redis the rolling budget cannot be metered, and
        # the whole point of the DoW layer is to never spend unmetered.
        raise HTTPException(
            status_code=503,
            detail="Budget store unavailable; refusing to run unmetered",
        ) from exc


def _run_job(job_id: str, text: str, config, keys, tenant_id) -> None:
    """Background worker for mode=async. Never raises — failures land in the job."""
    try:
        store_job(redis_client, job_id, {"status": "running", "job_id": job_id})
        result = run_protocol(text, config, keys=keys, tenant_id=tenant_id)
        store_job(redis_client, job_id, {"status": "done", "job_id": job_id, "result": result})
    except Exception as exc:  # noqa: BLE001
        # The job store outlives the request (1h TTL), so an unredacted provider
        # message here would persist a key at rest.
        reason = redact_secrets(str(exc))
        logger.warning("Protocol job %s failed: %s", job_id, reason)
        failure: Dict[str, Any] = {
            "status": "failed",
            "job_id": job_id,
            "error": reason,
            "error_type": type(exc).__name__,
        }
        if isinstance(exc, LLMError):
            failure.update({"provider": exc.provider, "model": exc.model})
        store_job(redis_client, job_id, failure)


@app.post("/content")
def content(
    req: ContentRequest,
    request: Request,
    response: Response,
    background: BackgroundTasks,
    mode: Literal["sync", "async"] = "sync",
):
    """Apply the full Ipcha protocol to a text and return only the verdict."""
    tenant_id = request.headers.get("x-tenant-id")
    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-Id header is required for denial-of-wallet accounting",
        )

    config = ProtocolConfig(
        proponent_model=req.proponent_model,
        ipcha_model=req.ipcha_model,
        auditor_model=req.auditor_model,
        authority=req.authority,
        sanitize=req.sanitize,
    )
    keys = _collect_keys(request, req.keys)

    if mode == "async":
        if redis_client is None:
            raise HTTPException(
                status_code=503, detail="Redis not available; async mode requires it"
            )
        job_id = new_job_id()
        store_job(redis_client, job_id, {"status": "pending", "job_id": job_id})
        background.add_task(_run_job, job_id, req.content, config, keys, tenant_id)
        response.status_code = 202
        return {"job_id": job_id, "status": "pending"}

    result = _execute_protocol(req.content, config, keys, tenant_id)
    response.headers["X-DoW-Budget-Remaining"] = str(result["meta"]["budget_remaining"])
    return result


@app.get("/content/{job_id}")
def content_job(job_id: str):
    """Collect an async protocol run. The gate decision is identical to sync."""
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis not available")
    job = load_job(redis_client, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown or expired job_id")
    return job


def _log_sanitize_rejection(anomalies) -> None:
    """
    Best-effort logging of sanitization anomalies. Never raises.
    """
    try:
        for a in anomalies:
            logger.warning(
                "Sanitization anomaly: type=%s pattern=%s",
                a.anomaly_type,
                a.triggered_pattern,
            )
    except Exception:
        pass
