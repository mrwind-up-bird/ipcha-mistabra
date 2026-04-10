# ipcha/evaluation/runners/metric_eval.py

"""
RQ1: Metric comparison — NLI-based ISce vs TF-IDF baseline (IS_w).

Loads the synthetic corpus, scores each case with both metrics, then runs
a paired statistical comparison to test whether NLI scoring differs
significantly from the TF-IDF baseline.

Also computes classification metrics (accuracy, precision, recall, F1)
using the median score as a threshold, and McNemar's test for binary
classification improvement.
"""

import json
import logging
import os
from typing import Any, Dict, List

import numpy as np

from ipcha.score import Finding, calculate_is_w
from ipcha.nli_scorer import NliScorer
from ipcha.evaluation.stats.significance import mcnemar_test, paired_comparison

logger = logging.getLogger("ipcha.evaluation.runners.metric_eval")


def _classify_gate(scores: List[float], threshold: float) -> List[bool]:
    """
    Classify cases as ACCEPTED (score > threshold) or REJECTED (score <= threshold).

    Returns a list of booleans: True = predicted ACCEPTED, False = predicted REJECTED.
    The threshold is the decision boundary: cases with scores above it are predicted
    as having legitimate (ACCEPTED) claims.
    """
    return [s > threshold for s in scores]


def _compute_classification_metrics(
    predicted: List[bool],
    actual: List[int],
) -> Dict[str, Any]:
    """
    Compute accuracy, precision, recall, F1 for binary classification.

    actual: 1 = ACCEPTED (positive), 0 = REJECTED (negative)
    predicted: True = predicted ACCEPTED, False = predicted REJECTED
    """
    n = len(predicted)
    tp = sum(1 for p, a in zip(predicted, actual) if p and a == 1)
    fp = sum(1 for p, a in zip(predicted, actual) if p and a == 0)
    tn = sum(1 for p, a in zip(predicted, actual) if not p and a == 0)
    fn = sum(1 for p, a in zip(predicted, actual) if not p and a == 1)

    accuracy = (tp + tn) / n if n > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def run_metric_comparison(
    corpus_path: str,
    output_path: str,
) -> Dict[str, Any]:
    """
    Compare TF-IDF (IS_w) vs NLI scoring across the synthetic corpus.

    For each case the function:
    1. Scores with calculate_is_w (TF-IDF-based)
    2. Scores with NliScorer.score_evidence (NLI-based)
    3. Records the binary expected gate (1=ACCEPTED, 0=REJECTED)

    Then runs:
    - Paired statistical comparison between the two score vectors
    - Classification metrics (accuracy, precision, recall, F1) for each metric
    - McNemar's test comparing binary classification performance

    Args:
        corpus_path: Path to the JSON corpus produced by generate_all().
        output_path: Destination path for the JSON results file.

    Returns:
        dict with keys:
            n, tfidf_mean, nli_mean, paired_comparison, classification,
            mcnemar, per_case
    """
    with open(corpus_path, "r", encoding="utf-8") as fh:
        raw_cases = json.load(fh)

    nli_scorer = NliScorer()

    tfidf_scores: List[float] = []
    nli_scores: List[float] = []
    gate_binary: List[int] = []
    per_case: List[Dict[str, Any]] = []

    for case in raw_cases:
        case_id: str = case["id"]
        claim: str = case["claim"]
        evidence: List[Finding] = [
            {"text": e["text"], "type": e["type"]}
            for e in case.get("evidence", [])
        ]
        expected_gate: str = case.get("expected_gate", "REJECTED")

        # --- TF-IDF score ---
        try:
            tfidf_score = calculate_is_w(claim, evidence)
        except Exception as exc:
            logger.warning("TF-IDF scoring failed for %s: %s", case_id, exc)
            tfidf_score = 0.0

        # --- NLI score ---
        try:
            nli_score = nli_scorer.score_evidence(claim, evidence)
        except Exception as exc:
            logger.warning("NLI scoring failed for %s: %s", case_id, exc)
            nli_score = 0.0

        gate_int = 1 if expected_gate == "ACCEPTED" else 0

        tfidf_scores.append(tfidf_score)
        nli_scores.append(nli_score)
        gate_binary.append(gate_int)

        per_case.append(
            {
                "id": case_id,
                "category": case.get("category", ""),
                "expected_gate": expected_gate,
                "gate_binary": gate_int,
                "tfidf_score": tfidf_score,
                "nli_score": nli_score,
            }
        )

        logger.info(
            "case=%s tfidf=%.4f nli=%.4f gate=%s",
            case_id,
            tfidf_score,
            nli_score,
            expected_gate,
        )

    n = len(tfidf_scores)
    tfidf_mean = round(float(np.mean(tfidf_scores)), 4) if n > 0 else 0.0
    nli_mean = round(float(np.mean(nli_scores)), 4) if n > 0 else 0.0

    # --- Paired statistical comparison (requires n >= 5) ---
    comparison: Dict[str, Any] = {}
    if n >= 5:
        try:
            comparison = paired_comparison(tfidf_scores, nli_scores)
        except Exception as exc:
            logger.warning("paired_comparison failed: %s", exc)
            comparison = {"error": str(exc)}
    else:
        comparison = {
            "error": f"n={n} < 5; paired_comparison requires at least 5 observations"
        }

    # --- Classification metrics ---
    # Use median of each metric's scores as the threshold for ACCEPTED/REJECTED
    tfidf_median = float(np.median(tfidf_scores)) if n > 0 else 0.0
    nli_median = float(np.median(nli_scores)) if n > 0 else 0.0

    tfidf_predicted = _classify_gate(tfidf_scores, tfidf_median)
    nli_predicted = _classify_gate(nli_scores, nli_median)

    tfidf_classification = _compute_classification_metrics(tfidf_predicted, gate_binary)
    nli_classification = _compute_classification_metrics(nli_predicted, gate_binary)

    classification: Dict[str, Any] = {
        "tfidf": {
            "threshold": round(tfidf_median, 4),
            **tfidf_classification,
        },
        "nli": {
            "threshold": round(nli_median, 4),
            **nli_classification,
        },
    }

    # --- McNemar's test: did NLI improve classification over TF-IDF? ---
    tfidf_correct = [
        (p and a == 1) or (not p and a == 0)
        for p, a in zip(tfidf_predicted, gate_binary)
    ]
    nli_correct = [
        (p and a == 1) or (not p and a == 0)
        for p, a in zip(nli_predicted, gate_binary)
    ]

    mcnemar: Dict[str, Any] = {}
    try:
        mcnemar = mcnemar_test(tfidf_correct, nli_correct)
    except Exception as exc:
        logger.warning("mcnemar_test failed: %s", exc)
        mcnemar = {"error": str(exc)}

    results: Dict[str, Any] = {
        "n": n,
        "tfidf_mean": tfidf_mean,
        "nli_mean": nli_mean,
        "paired_comparison": comparison,
        "classification": classification,
        "mcnemar": mcnemar,
        "per_case": per_case,
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    logger.info(
        "Metric comparison complete: n=%d tfidf_mean=%.4f nli_mean=%.4f "
        "tfidf_acc=%.2f%% nli_acc=%.2f%%",
        n, tfidf_mean, nli_mean,
        tfidf_classification["accuracy"] * 100,
        nli_classification["accuracy"] * 100,
    )

    return results
