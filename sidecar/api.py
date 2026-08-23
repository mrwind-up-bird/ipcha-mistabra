# ipcha/api.py
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
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

# --- Globals initialized at startup ---
claim_router = None
sycophancy_monitor = None
isw_scorer = ISwScorer()
nli_scorer = NliScorer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global claim_router, sycophancy_monitor
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
    return {
        "status": result["status"].value,
        "reason": result["reason"].value if result["reason"] else None,
        "metadata": result["metadata"],
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
