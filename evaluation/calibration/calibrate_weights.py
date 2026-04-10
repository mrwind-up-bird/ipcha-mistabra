"""
Grid search over the ISce contradiction weight to find the value that maximises
point-biserial correlation with the binary gate decision.

Input JSON must have per-run fields:
    evidence_scores : list[dict] — each entry has at least
                      {"type": "SUPPORTING"|"CONTRADICTING"|"NEUTRAL",
                       "similarity": float}
    gate_binary     : int  — 1 = gate passed, 0 = gate failed

Usage:
    python -m ipcha.calibration.calibrate_weights
    calibrate_contradiction_weight(input_path="calibration_data.json", ...)
"""

import json
import logging
import warnings
from typing import Any

import numpy as np
from scipy import stats

logger = logging.getLogger("ipcha.calibration.weights")

MIN_RECOMMENDED_N = 10

# Search range: contradiction weight in [-3.0, -0.5], step 0.1
_WEIGHT_MIN = -3.0
_WEIGHT_MAX = -0.5
_WEIGHT_STEP = 0.1

# Fixed weights for non-contradiction findings (held constant during search)
_SUPPORTING_WEIGHT = 1.0
_NEUTRAL_WEIGHT = 0.0


def _compute_isce(evidence_scores: list[dict[str, Any]], contradiction_weight: float) -> float:
    """
    Recompute ISce for a single run given a candidate contradiction weight.

    Args:
        evidence_scores:      List of finding dicts with 'type' and 'similarity'.
        contradiction_weight: The weight to apply to CONTRADICTING findings.

    Returns:
        Normalised ISce score. Returns 0.0 for empty/invalid input.
    """
    weights = {
        "SUPPORTING": _SUPPORTING_WEIGHT,
        "CONTRADICTING": contradiction_weight,
        "NEUTRAL": _NEUTRAL_WEIGHT,
    }
    weighted_sum = 0.0
    total_magnitude = 0.0

    for item in evidence_scores:
        ftype = item.get("type")
        similarity = item.get("similarity")
        if ftype not in weights or similarity is None:
            continue
        w = weights[ftype]
        weighted_sum += w * float(similarity)
        total_magnitude += abs(w)

    if total_magnitude == 0.0:
        return 0.0

    return weighted_sum / total_magnitude


def calibrate_contradiction_weight(
    input_path: str = "calibration_data.json",
    output_path: str = "weight_calibration_results.json",
) -> dict[str, Any]:
    """
    Grid-search over contradiction_weight ∈ [−3.0, −0.5] (step 0.1) and pick the
    value that maximises |point-biserial correlation| between ISce and gate_binary.

    Args:
        input_path:  Path to calibration_data.json — runs must include
                     'evidence_scores' and 'gate_binary' fields.
        output_path: Destination for weight_calibration_results.json.

    Returns:
        Dictionary with: optimal_weight, correlation_r, p_value, n,
        all_results (list), sensitivity.
    """
    with open(input_path) as f:
        runs: list[dict[str, Any]] = json.load(f)

    usable = [
        r for r in runs
        if "evidence_scores" in r and "gate_binary" in r
        and r["evidence_scores"] is not None
        and r["gate_binary"] is not None
    ]
    n = len(usable)

    if n == 0:
        raise ValueError(
            "No runs with both 'evidence_scores' and 'gate_binary' found. "
            "Pre-compute these fields and add them to calibration_data.json."
        )

    if n < MIN_RECOMMENDED_N:
        warnings.warn(
            f"Only {n} samples available — weight calibration may not be reliable "
            f"(recommended minimum: {MIN_RECOMMENDED_N}).",
            UserWarning,
            stacklevel=2,
        )
        logger.warning("Low sample count: n=%d (recommended >= %d)", n, MIN_RECOMMENDED_N)

    gate_labels = np.array([int(r["gate_binary"]) for r in usable], dtype=float)

    # Build candidate weight list (inclusive of both endpoints)
    n_steps = round((_WEIGHT_MAX - _WEIGHT_MIN) / _WEIGHT_STEP) + 1
    candidates = [round(_WEIGHT_MIN + i * _WEIGHT_STEP, 10) for i in range(n_steps)]

    all_results: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for w in candidates:
        isce_scores = np.array(
            [_compute_isce(r["evidence_scores"], w) for r in usable],
            dtype=float,
        )

        # Point-biserial correlation requires variance in both arrays
        if np.std(isce_scores) == 0 or np.std(gate_labels) == 0:
            r_val, p_val = 0.0, 1.0
        else:
            r_val, p_val = stats.pointbiserialr(gate_labels, isce_scores)
            r_val, p_val = float(r_val), float(p_val)

        entry: dict[str, Any] = {
            "weight": round(w, 2),
            "correlation_r": round(r_val, 6),
            "p_value": round(p_val, 6),
            "abs_r": round(abs(r_val), 6),
        }
        all_results.append(entry)

        if best is None or abs(r_val) > abs(best["correlation_r"]):
            best = entry

    assert best is not None  # guaranteed: candidates non-empty

    # Sensitivity: range of weights whose |r| is within 5% of the optimum
    threshold = best["abs_r"] * 0.95
    sensitive = [e for e in all_results if e["abs_r"] >= threshold]
    sensitivity = {
        "threshold_abs_r": round(threshold, 6),
        "weight_min": min(e["weight"] for e in sensitive),
        "weight_max": max(e["weight"] for e in sensitive),
        "n_weights_in_range": len(sensitive),
    }

    result: dict[str, Any] = {
        "n": n,
        "optimal_weight": best["weight"],
        "correlation_r": best["correlation_r"],
        "p_value": best["p_value"],
        "all_results": all_results,
        "sensitivity": sensitivity,
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(
        "Weight calibration complete: optimal_weight=%.2f, r=%.4f, p=%.4f, n=%d",
        best["weight"], best["correlation_r"], best["p_value"], n,
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    calibrate_contradiction_weight()
