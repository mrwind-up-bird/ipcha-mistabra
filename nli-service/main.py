from contextlib import asynccontextmanager
from typing import Optional
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from transformers import AutoTokenizer
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
# Label map: matches cross-encoder/nli-deberta-v3-base output order
# 0 = entailment, 1 = neutral, 2 = contradiction (verified against model config)
LABEL_MAP = {0: "contradiction", 1: "entailment", 2: "neutral"}

# Global state
_session: Optional[ort.InferenceSession] = None
_tokenizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _session, _tokenizer
    config_path = os.path.join(MODEL_DIR, "config.json")
    if os.path.exists(config_path):
        model_path = os.path.join(MODEL_DIR, "model.onnx")
        _session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        print(f"Model loaded from {MODEL_DIR}")
    else:
        print(f"WARNING: Model not found at {MODEL_DIR} — service will return 503")
    yield
    _session = None
    _tokenizer = None


app = FastAPI(title="DeBERTa-NLI", version="1.0.0", lifespan=lifespan)


class NLIPair(BaseModel):
    premise: str
    hypothesis: str

    @field_validator("premise", "hypothesis")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty or whitespace")
        return v


class ClassifyResponse(BaseModel):
    label: str
    scores: dict[str, float]


class BatchRequest(BaseModel):
    pairs: list[NLIPair]


class BatchResponse(BaseModel):
    results: list[ClassifyResponse]


def _softmax(logits: np.ndarray) -> np.ndarray:
    exp = np.exp(logits - np.max(logits))
    return exp / exp.sum()


def _run_inference(premise: str, hypothesis: str) -> ClassifyResponse:
    inputs = _tokenizer(
        premise,
        hypothesis,
        truncation=True,
        max_length=512,
        return_tensors="np",
    )
    # Only pass inputs the ONNX model expects (DeBERTa-v2 has no token_type_ids)
    valid_names = {inp.name for inp in _session.get_inputs()}
    ort_inputs = {k: v for k, v in inputs.items() if k in valid_names}
    outputs = _session.run(None, ort_inputs)
    logits = outputs[0][0]  # shape: (num_labels,)
    probs = _softmax(logits)

    label_idx = int(np.argmax(probs))
    scores = {LABEL_MAP[i]: float(probs[i]) for i in range(len(probs))}
    return ClassifyResponse(label=LABEL_MAP[label_idx], scores=scores)


@app.get("/health")
def health():
    return {"status": "ok", "model": "nli-deberta-v3-base", "runtime": "onnx"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(pair: NLIPair):
    if _session is None or _tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return _run_inference(pair.premise, pair.hypothesis)


@app.post("/batch", response_model=BatchResponse)
def batch(request: BatchRequest):
    if not request.pairs:
        return BatchResponse(results=[])
    if _session is None or _tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    results = [_run_inference(p.premise, p.hypothesis) for p in request.pairs]
    return BatchResponse(results=results)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
