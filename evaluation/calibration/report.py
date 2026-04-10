"""
Generates a markdown calibration report from the two calibration result JSON files.

Usage:
    python -m ipcha.calibration.report
    generate_report(
        bands_path="calibration_results.json",
        weights_path="weight_calibration_results.json",
        output_path="calibration_report.md",
    )
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger("ipcha.calibration.report")


def _load_json(path: str) -> dict[str, Any] | None:
    """Load a JSON file, returning None if it does not exist."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("File not found: %s", path)
        return None


def _bands_section(data: dict[str, Any] | None) -> str:
    if data is None:
        return "## IS Interpretation Bands\n\nNot yet computed.\n"

    n = data.get("n", "?")
    mean = data.get("mean")
    std = data.get("std")
    median = data.get("median")
    bands = data.get("bands", {})
    normality = data.get("normality_test")

    lines = [
        "## IS Interpretation Bands",
        "",
        f"**Samples (n):** {n}  ",
        f"**Mean:** {mean:.4f}  " if mean is not None else "",
        f"**Std:** {std:.4f}  " if std is not None else "",
        f"**Median:** {median:.4f}" if median is not None else "",
        "",
        "| Band | Min | Max |",
        "|------|-----|-----|",
    ]

    band_order = ["low", "mid", "mid_high", "high"]
    for band in band_order:
        if band in bands:
            bmin = bands[band].get("min")
            bmax = bands[band].get("max")
            bmin_str = f"{bmin:.4f}" if bmin is not None else "—"
            bmax_str = f"{bmax:.4f}" if bmax is not None else "—"
            lines.append(f"| {band} | {bmin_str} | {bmax_str} |")

    lines.append("")

    if normality:
        test_name = normality.get("test", "unknown").replace("-", " ").title()
        stat = normality.get("statistic")
        pval = normality.get("p_value")
        is_normal = normality.get("is_normal")
        normal_str = "yes (p ≥ 0.05)" if is_normal else "no (p < 0.05)"
        stat_str = f"{stat:.4f}" if stat is not None else "—"
        pval_str = f"{pval:.4f}" if pval is not None else "—"
        lines += [
            f"**Normality test ({test_name}):** statistic={stat_str}, p={pval_str}, normal={normal_str}",
            "",
        ]
    else:
        lines += ["*Normality test skipped (n < 8).*", ""]

    return "\n".join(line for line in lines if line is not None)


def _weights_section(data: dict[str, Any] | None) -> str:
    if data is None:
        return "## Contradiction Weight Calibration\n\nNot yet computed.\n"

    n = data.get("n", "?")
    opt_w = data.get("optimal_weight")
    corr_r = data.get("correlation_r")
    p_val = data.get("p_value")
    sensitivity = data.get("sensitivity", {})
    all_results = data.get("all_results", [])

    opt_w_str = f"{opt_w:.2f}" if opt_w is not None else "—"
    corr_r_str = f"{corr_r:.4f}" if corr_r is not None else "—"
    p_val_str = f"{p_val:.4f}" if p_val is not None else "—"

    s_min = sensitivity.get("weight_min")
    s_max = sensitivity.get("weight_max")
    s_n = sensitivity.get("n_weights_in_range", "?")
    s_thresh = sensitivity.get("threshold_abs_r")

    lines = [
        "## Contradiction Weight Calibration",
        "",
        f"**Samples (n):** {n}  ",
        f"**Optimal weight:** {opt_w_str}  ",
        f"**Point-biserial r:** {corr_r_str}  ",
        f"**p-value:** {p_val_str}",
        "",
    ]

    if s_min is not None and s_max is not None:
        thresh_str = f"{s_thresh:.4f}" if s_thresh is not None else "—"
        lines += [
            "### Sensitivity",
            "",
            f"Weights with |r| ≥ {thresh_str} (95% of optimum): "
            f"**[{s_min:.2f}, {s_max:.2f}]** ({s_n} values)",
            "",
        ]

    # Show top-10 candidates by |r|
    if all_results:
        top = sorted(all_results, key=lambda x: x.get("abs_r", 0.0), reverse=True)[:10]
        lines += [
            "### Top Candidates (by |r|)",
            "",
            "| Weight | r | p |",
            "|--------|---|---|",
        ]
        for row in top:
            w_str = f"{row.get('weight', '?'):.2f}"
            r_str = f"{row.get('correlation_r', 0.0):.4f}"
            p_str = f"{row.get('p_value', 1.0):.4f}"
            lines.append(f"| {w_str} | {r_str} | {p_str} |")
        lines.append("")

    return "\n".join(lines)


def generate_report(
    bands_path: str = "calibration_results.json",
    weights_path: str = "weight_calibration_results.json",
    output_path: str = "calibration_report.md",
) -> str:
    """
    Generate a markdown calibration report from pre-computed result JSON files.

    Args:
        bands_path:   Path to calibration_results.json (IS band results).
        weights_path: Path to weight_calibration_results.json (weight grid results).
        output_path:  Destination markdown file.

    Returns:
        The generated markdown string.
    """
    bands_data = _load_json(bands_path)
    weights_data = _load_json(weights_path)

    report_parts = [
        "# IPCHA Metric Calibration Report",
        "",
        "> Auto-generated from production data. Do not edit manually.",
        "",
        _bands_section(bands_data),
        _weights_section(weights_data),
    ]
    report = "\n".join(report_parts)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(report)

    logger.info("Calibration report written to %s", output_path)
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(generate_report())
