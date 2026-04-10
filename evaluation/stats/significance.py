# ipcha/evaluation/stats/significance.py

"""
Statistical significance tests for IPCHA evaluation.

Provides paired comparison (t-test / Wilcoxon) and McNemar's test for
binary outcomes, suitable for before/after empirical evaluation in the paper.
"""

from typing import List, Literal

import numpy as np
from scipy import stats


def paired_comparison(
    before: List[float],
    after: List[float],
    test: Literal["auto", "t-test", "wilcoxon"] = "auto",
) -> dict:
    """
    Compare paired before/after measurements.

    Automatically selects:
    - Paired t-test if both samples pass Shapiro-Wilk normality (p > 0.05)
    - Wilcoxon signed-rank test otherwise

    Args:
        before: Scores from the baseline / before condition.
        after:  Scores from the new / after condition.
        test:   Force a specific test, or "auto" (default).

    Returns:
        dict with keys:
            test (str), statistic (float), p_value (float),
            effect_size_d (float), mean_difference (float),
            ci_95 (tuple[float, float]), n (int), significant (bool)

    Raises:
        ValueError: If n < 5 or the two lists have different lengths.
    """
    if len(before) != len(after):
        raise ValueError(
            f"before and after must have the same length "
            f"(got {len(before)} vs {len(after)})"
        )
    n = len(before)
    if n < 5:
        raise ValueError(f"Requires n >= 5, got n={n}")

    before_arr = np.array(before, dtype=float)
    after_arr = np.array(after, dtype=float)
    diff = after_arr - before_arr

    # --- choose test ---
    if test == "auto":
        _, p_before = stats.shapiro(before_arr)
        _, p_after = stats.shapiro(after_arr)
        chosen_test = "t-test" if (p_before > 0.05 and p_after > 0.05) else "wilcoxon"
    else:
        chosen_test = test

    if chosen_test == "t-test":
        stat, p_value = stats.ttest_rel(after_arr, before_arr)
    else:
        chosen_test = "wilcoxon"
        stat, p_value = stats.wilcoxon(diff)

    # --- Cohen's d for paired samples ---
    mean_diff = float(np.mean(diff))
    std_diff = float(np.std(diff, ddof=1))
    effect_size_d = mean_diff / std_diff if std_diff != 0.0 else 0.0

    # --- 95 % CI on the mean difference (t-based) ---
    se = std_diff / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=n - 1)
    ci_95 = (float(mean_diff - t_crit * se), float(mean_diff + t_crit * se))

    return {
        "test": chosen_test,
        "statistic": float(stat),
        "p_value": float(p_value),
        "effect_size_d": round(effect_size_d, 4),
        "mean_difference": round(mean_diff, 4),
        "ci_95": (round(ci_95[0], 4), round(ci_95[1], 4)),
        "n": n,
        "significant": bool(p_value < 0.05),
    }


def mcnemar_test(
    before_correct: List[bool],
    after_correct: List[bool],
) -> dict:
    """
    McNemar's test for paired binary outcomes with continuity correction.

    Measures whether the proportion of correct classifications changed
    significantly between the before and after conditions.

    Args:
        before_correct: Boolean list — True if the baseline was correct.
        after_correct:  Boolean list — True if the new method was correct.

    Returns:
        dict with keys:
            test (str), statistic (float), p_value (float), n (int),
            improved (int), degraded (int), significant (bool)

    Raises:
        ValueError: If the two lists have different lengths.
    """
    if len(before_correct) != len(after_correct):
        raise ValueError(
            f"before_correct and after_correct must have the same length "
            f"(got {len(before_correct)} vs {len(after_correct)})"
        )

    n = len(before_correct)

    # Discordant pairs
    improved = sum(
        1 for b, a in zip(before_correct, after_correct) if not b and a
    )
    degraded = sum(
        1 for b, a in zip(before_correct, after_correct) if b and not a
    )

    # McNemar chi-squared with continuity correction
    discordant = improved + degraded
    if discordant == 0:
        stat = 0.0
        p_value = 1.0
    else:
        stat = (abs(improved - degraded) - 1) ** 2 / discordant
        p_value = float(stats.chi2.sf(stat, df=1))

    return {
        "test": "mcnemar",
        "statistic": round(float(stat), 4),
        "p_value": round(p_value, 4),
        "n": n,
        "improved": improved,
        "degraded": degraded,
        "significant": bool(p_value < 0.05),
    }
