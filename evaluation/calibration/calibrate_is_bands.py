"""
Derives IS interpretation bands from production data using a quartile-based approach.

Usage:
    python -m ipcha.calibration.calibrate_is_bands
    calibrate(input_path="calibration_data.json", output_path="calibration_results.json")
"""

import json
import logging
import warnings
from typing import Any

import numpy as np
from scipy import stats

logger = logging.getLogger("ipcha.calibration.is_bands")

MIN_RECOMMENDED_N = 10


def calibrate(
    input_path: str = "calibration_data.json",
    output_path: str = "calibration_results.json",
) -> dict[str, Any]:
    """
    Compute quartile-based IS interpretation bands from exported calibration data.

    Each run in the input JSON must have a pre-computed ``is_score`` field.
    Bands are derived as:
        low      : [min,  Q25)
        mid      : [Q25,  Q50)
        mid_high : [Q50,  Q75)
        high     : [Q75,  max]

    A Shapiro-Wilk normality test is run when n >= 8.

    Args:
        input_path:  Path to the calibration_data.json file produced by
                     export_historical_runs.py (possibly with is_score added).
        output_path: Destination JSON for the calibration results.

    Returns:
        Dictionary with keys: n, mean, std, median, bands, normality_test.
    """
    with open(input_path) as f:
        runs: list[dict[str, Any]] = json.load(f)

    scores = [r["is_score"] for r in runs if "is_score" in r and r["is_score"] is not None]
    n = len(scores)

    if n == 0:
        raise ValueError(
            "No 'is_score' values found in calibration data. "
            "Pre-compute IS scores and add them to calibration_data.json before running."
        )

    if n < MIN_RECOMMENDED_N:
        warnings.warn(
            f"Only {n} samples available — calibration may not be reliable "
            f"(recommended minimum: {MIN_RECOMMENDED_N}).",
            UserWarning,
            stacklevel=2,
        )
        logger.warning("Low sample count: n=%d (recommended >= %d)", n, MIN_RECOMMENDED_N)

    arr = np.array(scores, dtype=float)

    q25, q50, q75 = float(np.percentile(arr, 25)), float(np.percentile(arr, 50)), float(np.percentile(arr, 75))

    bands = {
        "low":      {"min": float(arr.min()), "max": q25},
        "mid":      {"min": q25,              "max": q50},
        "mid_high": {"min": q50,              "max": q75},
        "high":     {"min": q75,              "max": float(arr.max())},
    }

    normality_test: dict[str, Any] | None = None
    if n >= 8:
        stat, p_value = stats.shapiro(arr)
        normality_test = {
            "test": "shapiro-wilk",
            "statistic": float(stat),
            "p_value": float(p_value),
            "is_normal": bool(p_value >= 0.05),
        }
        logger.info(
            "Shapiro-Wilk: W=%.4f, p=%.4f (%s)",
            stat, p_value,
            "normal" if normality_test["is_normal"] else "non-normal",
        )

    result: dict[str, Any] = {
        "n": n,
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1) if n > 1 else 0.0),
        "median": q50,
        "q25": q25,
        "q75": q75,
        "bands": bands,
        "normality_test": normality_test,
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(
        "IS band calibration complete: n=%d, mean=%.4f, std=%.4f, bands=%s",
        n, result["mean"], result["std"],
        {k: f"[{v['min']:.3f}, {v['max']:.3f}]" for k, v in bands.items()},
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    calibrate()
