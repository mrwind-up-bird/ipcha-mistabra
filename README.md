# Ipcha Mistabra Protocol

**Structured Adversarial Verification as a Defense Against Sycophancy in Multi-Agent LLM Systems**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-2026.XXXXX-b31b1b.svg)](https://arxiv.org/)
[![Academia](https://img.shields.io/badge/Academia-41454A)](#)

---

## What is this?

IPCHA is a structured adversarial verification protocol that elevates sycophancy defense from a model property to an architectural constraint. Instead of relying on model-internal alignment (RLHF, Constitutional AI), IPCHA enforces mandatory adversarial challenge through a three-agent pipeline with model diversity enforcement and authority grounding.

The protocol is described in our paper: *"Ipcha Mistabra: Structured Adversarial Verification as a Defense Against Sycophancy in Multi-Agent LLM Systems"* (Baer, 2026).

## Architecture

```
                    ┌─────────────────────┐
                    │   Your Application  │
                    └──────────┬──────────┘
                               │ REST API
                    ┌──────────▼──────────┐
                    │   IPCHA Sidecar     │  Port 8100
                    │   (FastAPI/Python)  │
                    │                     │
                    │  ┌─Claim Router───┐ │
                    │  │ SDRLAgent      │ │──── Authority Docs
                    │  │ PromptAgent    │ │     (Axiom RAG)
                    │  │ DefaultAgent   │ │
                    │  └────────────────┘ │
                    │  ┌─Scoring────────┐ │
                    │  │ IS_w (TF-IDF)  │ │
                    │  │ IS_ce (NLI) ───┼─┼──┐
                    │  └────────────────┘ │  │
                    │  ┌─Defense─────────┐│  │
                    │  │ Sanitizer      ││  │
                    │  │ DoW Budget     ││  │
                    │  │ Sycophancy Mon ││  │
                    │  └────────────────┘│  │
                    └────────────────────┘  │
                               │            │
                    ┌──────────▼──────────┐ │
                    │   DeBERTa-NLI      │◄┘  Port 8200
                    │   (ONNX/FastAPI)   │
                    └─────────────────────┘
```

## Repository Structure

```
ipcha-mistabra/
├── sidecar/                    # IPCHA verification sidecar (Port 8100)
│   ├── api.py                  # FastAPI entry point
│   ├── protocol.py             # DebateSession, model diversity enforcement
│   ├── score.py                # IS_w metric (TF-IDF baseline)
│   ├── nli_scorer.py           # IS_ce metric (NLI-based)
│   ├── nli_client.py           # HTTP client for NLI microservice
│   ├── claim_classifier.py     # VERIFIABLE/INTERPRETIVE/UNCLASSIFIABLE
│   ├── routing.py              # Claim routing to specialized agents
│   ├── sanitize.py             # 3-layer input sanitization
│   ├── sycophancy_monitor.py   # Redis-backed behavioral monitoring
│   ├── agents/                 # Verification agent implementations
│   │   ├── base.py             # Abstract VerificationAgent
│   │   └── implementations.py  # SDRLAgent, PromptBasedAgent, DefaultAgent
│   ├── authority/              # Cross-chunk coherence validation
│   └── Dockerfile
├── nli-service/                # DeBERTa NLI microservice (Port 8200)
│   ├── main.py                 # FastAPI NLI service
│   ├── export_model.py         # HuggingFace → ONNX export
│   ├── test_main.py            # Service tests
│   └── Dockerfile              # Multi-stage: export + runtime
├── evaluation/                 # Paper evaluation suite
│   ├── run_all.py              # Orchestrator
│   ├── corpus/                 # Synthetic test corpus generator
│   ├── runners/                # Metric comparison (RQ1)
│   ├── stats/                  # Statistical tests
│   ├── calibration/            # IS band & weight calibration
│   └── results/                # Pre-computed results (JSON)
├── paper/                      # LaTeX sources (arXiv submission)
│   ├── ipcha-paper.tex
│   └── references.bib
└── LICENSE                     # Apache 2.0
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Redis (for sycophancy monitoring & DoW defense)

### Run the NLI Service

```bash
cd nli-service
docker build -t ipcha-nli .
docker run -p 8200:8200 ipcha-nli
```

### Run the IPCHA Sidecar

Every module imports absolutely as `ipcha.*`, so the package must be importable
under that name. In Docker this is handled by the Dockerfile (`COPY . ./ipcha/`):

```bash
docker build -t ipcha-sidecar ./sidecar
docker run -p 8100:8100 ipcha-sidecar
```

To run it directly, expose `sidecar/` as `ipcha` first:

```bash
pip install -r sidecar/requirements.txt
ln -s sidecar ipcha
uvicorn ipcha.api:app --host 0.0.0.0 --port 8100
```

Only `/health`, `/score`, `/score/opposition`, `/sanitize` and `/arbitrate` work
without further setup. `/route` needs a `config.yml`, `/sycophancy/metrics` needs
Redis, `/audit/rejections` needs `DATABASE_URL`, and `/validate` needs an OpenAI
key — see [`docs/api/API.md`](docs/api/API.md).

### Run the Evaluation

```bash
cd evaluation
python run_all.py
```

This generates the synthetic corpus, runs all three scoring methods (TF-IDF, SBERT, NLI), and produces the statistical comparison reported in the paper.

## API Integration

Integrating IPCHA into another project? See **[`docs/api/API.md`](docs/api/API.md)** for the full REST reference — every endpoint, parameter, payload and response for both services, plus configuration, integration flows and verified limitations.

A ready-to-run Postman collection is included:

```bash
newman run docs/api/ipcha-api.postman_collection.json \
  -e docs/api/ipcha-api.postman_environment.json
```

Both services also expose their OpenAPI schema at `/openapi.json` and Swagger UI at `/docs`.

## Key Metrics

| Metric | Method | Score Separation | Cohen's d |
|--------|--------|-----------------|-----------|
| IS_w | TF-IDF cosine | 0.224 | baseline |
| IS_sbert | SBERT cosine | 0.897 | 0.12 (n.s.) |
| IS_ce | NLI (DeBERTa) | **0.923** | **-0.80** (large) |

NLI classification provides significantly different score distributions from both TF-IDF (p < 0.001) and SBERT (p < 0.001, large effect), with the advantage coming from the entailment/contradiction classification task rather than merely using a better text encoder.

## Citation

```bibtex
@article{baer2026ipcha,
  author  = {Baer, Oliver},
  title   = {Ipcha Mistabra: Structured Adversarial Verification
             as a Defense Against Sycophancy in Multi-Agent LLM Systems},
  journal = {arXiv preprint},
  year    = {2026},
}
```

## License

This project is licensed under the Apache License 2.0 -- see [LICENSE](LICENSE) for details.

The IPCHA protocol is a standalone verification framework. It does not require the nyxCore platform to operate; the sidecar and NLI service can be integrated into any application via their REST APIs.
