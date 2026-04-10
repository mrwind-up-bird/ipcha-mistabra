import os
import pytest
from fastapi.testclient import TestClient

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PRESENT = os.path.exists(os.path.join(MODEL_DIR, "config.json"))

pytestmark = pytest.mark.skipif(
    not MODEL_PRESENT,
    reason="Model not present — skipping NLI tests (run export_model.py first)",
)

# Import after the skip mark so startup doesn't fail in CI without the model
from main import app  # noqa: E402

client = TestClient(app)


class TestHealth:
    def test_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["model"] == "nli-deberta-v3-base"
        assert body["runtime"] == "onnx"


class TestClassify:
    def test_entailment(self):
        resp = client.post(
            "/classify",
            json={"premise": "A man is eating pizza.", "hypothesis": "A man is eating food."},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["label"] == "entailment"
        assert "entailment" in body["scores"]
        assert "neutral" in body["scores"]
        assert "contradiction" in body["scores"]

    def test_contradiction(self):
        resp = client.post(
            "/classify",
            json={"premise": "A man is eating pizza.", "hypothesis": "A man is sleeping."},
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "contradiction"

    def test_neutral(self):
        resp = client.post(
            "/classify",
            json={
                "premise": "A man is eating pizza.",
                "hypothesis": "Pizza costs ten dollars.",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "neutral"

    def test_empty_premise_returns_422(self):
        resp = client.post(
            "/classify",
            json={"premise": "", "hypothesis": "Some hypothesis."},
        )
        assert resp.status_code == 422

    def test_empty_hypothesis_returns_422(self):
        resp = client.post(
            "/classify",
            json={"premise": "Some premise.", "hypothesis": ""},
        )
        assert resp.status_code == 422

    def test_whitespace_only_returns_422(self):
        resp = client.post(
            "/classify",
            json={"premise": "   ", "hypothesis": "Some hypothesis."},
        )
        assert resp.status_code == 422


class TestBatch:
    def test_two_pairs(self):
        resp = client.post(
            "/batch",
            json={
                "pairs": [
                    {
                        "premise": "A man is eating pizza.",
                        "hypothesis": "A man is eating food.",
                    },
                    {
                        "premise": "A man is eating pizza.",
                        "hypothesis": "A man is sleeping.",
                    },
                ]
            },
        )
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 2
        assert results[0]["label"] == "entailment"
        assert results[1]["label"] == "contradiction"

    def test_empty_batch_returns_empty_results(self):
        resp = client.post("/batch", json={"pairs": []})
        assert resp.status_code == 200
        assert resp.json()["results"] == []
