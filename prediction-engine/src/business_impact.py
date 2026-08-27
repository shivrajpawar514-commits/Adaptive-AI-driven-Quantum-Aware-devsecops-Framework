"""Deterministic business impact estimator.

Derives operational, financial, compliance, availability, and reputation
impact scores from the current URS, the 24-hour projected URS, and the
severity distribution of open findings.

All calculations are deterministic and reproducible.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Category base weights — how sensitive each category is to URS
# These are research-configurable constants.
# ---------------------------------------------------------------------------
CATEGORY_SENSITIVITY: Dict[str, float] = {
    "operational":  1.0,   # direct correlation with URS
    "financial":    0.8,   # somewhat correlated
    "compliance":   0.9,   # heavily influenced by findings
    "availability": 0.85,  # influenced by exposure and severity
    "reputation":   0.7,   # lagging indicator
}

# Finding severity bonus points (added to the base URS-derived score)
SEVERITY_BONUS: Dict[str, Dict[str, float]] = {
    "operational":  {"Critical": 15, "High": 8, "Medium": 3, "Low": 1},
    "financial":    {"Critical": 12, "High": 6, "Medium": 2, "Low": 0},
    "compliance":   {"Critical": 18, "High": 10, "Medium": 5, "Low": 2},
    "availability": {"Critical": 14, "High": 7, "Medium": 3, "Low": 1},
    "reputation":   {"Critical": 10, "High": 5, "Medium": 2, "Low": 0},
}


def calculate_business_impact(
    current_urs: float,
    projected_urs_24h: float,
    finding_counts: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    """Calculate business impact scores deterministically.

    Parameters
    ----------
    current_urs : float
        Current Unified Risk Score (0–100).
    projected_urs_24h : float
        Projected URS at the 24-hour horizon.
    finding_counts : dict, optional
        Mapping of severity level to count, e.g.
        ``{"Critical": 1, "High": 2, "Medium": 3, "Low": 1}``.

    Returns
    -------
    dict
        ``scores``          – per-category impact scores (0–100).
        ``overall``         – weighted average overall impact (0–100).
        ``level``           – ``"Critical"`` | ``"High"`` | ``"Medium"`` | ``"Low"``.
        ``trend``           – ``"increasing"`` | ``"stable"`` | ``"decreasing"``.
        ``explanation``     – list of human-readable impact factors.
    """
    counts = finding_counts or {}

    # --- Per-category scores -----------------------------------------------
    scores: Dict[str, float] = {}
    for category, sensitivity in CATEGORY_SENSITIVITY.items():
        # Base score derived from the higher of current or projected URS
        base = max(current_urs, projected_urs_24h) * sensitivity

        # Add severity bonuses from open findings
        bonus = 0.0
        category_bonuses = SEVERITY_BONUS.get(category, {})
        for sev, count in counts.items():
            bonus += category_bonuses.get(sev, 0) * count

        scores[category] = round(min(base + bonus, 100.0), 2)

    # --- Overall impact score (equal-weighted average) ---------------------
    overall = round(sum(scores.values()) / max(len(scores), 1), 2)

    # --- Impact level ------------------------------------------------------
    if overall >= 80:
        level = "Critical"
    elif overall >= 60:
        level = "High"
    elif overall >= 35:
        level = "Medium"
    else:
        level = "Low"

    # --- Trend -------------------------------------------------------------
    if projected_urs_24h > current_urs * 1.05:
        trend = "increasing"
    elif projected_urs_24h < current_urs * 0.95:
        trend = "decreasing"
    else:
        trend = "stable"

    # --- Explanation -------------------------------------------------------
    explanation: list[str] = []

    top_category = max(scores, key=scores.get)  # type: ignore[arg-type]
    explanation.append(
        f"Highest impact category: {top_category} ({scores[top_category]:.1f}/100)"
    )

    total_findings = sum(counts.values())
    if total_findings > 0:
        explanation.append(
            f"{total_findings} open finding(s) contribute to impact scores"
        )
        for sev in ("Critical", "High", "Medium", "Low"):
            cnt = counts.get(sev, 0)
            if cnt > 0:
                explanation.append(f"  {cnt} {sev}-severity finding(s)")

    if trend == "increasing":
        explanation.append(
            "Risk trend is increasing — projected 24h URS "
            f"({projected_urs_24h:.1f}) exceeds current ({current_urs:.1f})"
        )
    elif trend == "decreasing":
        explanation.append(
            "Risk trend is decreasing — remediation progress detected"
        )

    logger.info(
        "Business impact: overall=%.2f level=%s trend=%s scores=%s",
        overall,
        level,
        trend,
        scores,
    )

    return {
        "scores":      scores,
        "overall":     overall,
        "level":       level,
        "trend":       trend,
        "explanation": explanation,
    }
