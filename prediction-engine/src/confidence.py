"""Deterministic confidence scoring for prediction forecasts.

Confidence is computed as a weighted sum of five input factors.
The result includes a numerical score (0–100), a categorical level,
and a human-readable explanation of contributing factors.

Weights (approved Sprint 27 design):
    Telemetry Completeness  = 30 %
    Finding Stability       = 25 %
    Asset Criticality       = 25 %
    Historical Evidence     = 20 %

An optional fifth factor — telemetry freshness — can reduce the overall
confidence when telemetry data is stale.

All calculations are deterministic and reproducible.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Weight configuration (must sum to 1.0 for the four primary factors)
# ---------------------------------------------------------------------------
WEIGHTS: Dict[str, float] = {
    "telemetry":  0.30,
    "stability":  0.25,
    "criticality": 0.25,
    "historical": 0.20,
}

# Freshness discount — applied as a multiplier to the final score
# (100 = perfectly fresh, 0 = completely stale)
FRESHNESS_FLOOR: float = 0.5  # freshness never reduces score below 50 %


def calculate_confidence(
    metrics: Dict[str, float],
    freshness: float = 100.0,
) -> Dict[str, Any]:
    """Calculate deterministic confidence score with explanation.

    Parameters
    ----------
    metrics : dict
        Must contain keys ``telemetry``, ``stability``, ``criticality``,
        ``historical`` — each a float in [0, 100].
    freshness : float, optional
        Telemetry freshness indicator (0–100).  Defaults to 100 (fully
        fresh).  When < 100 the final score is discounted.

    Returns
    -------
    dict
        ``score``       – float 0–100 (numerical confidence).
        ``level``       – ``"High"`` | ``"Medium"`` | ``"Low"``.
        ``explanation`` – list[str] of contributing factors.

    Raises
    ------
    ValueError
        If any required key is missing from *metrics*.
    """
    required = set(WEIGHTS.keys())
    missing = required - metrics.keys()
    if missing:
        raise ValueError(f"Missing confidence metrics: {missing}")

    # --- Normalize each metric to [0, 1] ---
    normalized = {
        k: max(min(v / 100.0, 1.0), 0.0) for k, v in metrics.items()
        if k in WEIGHTS
    }

    # --- Weighted sum ---
    raw_score = sum(normalized[k] * w for k, w in WEIGHTS.items()) * 100.0

    # --- Freshness discount ---
    freshness_factor = max(freshness / 100.0, FRESHNESS_FLOOR)
    score = round(raw_score * freshness_factor, 2)

    # --- Categorical level ---
    if score >= 80:
        level = "High"
    elif score >= 50:
        level = "Medium"
    else:
        level = "Low"

    # --- Explanation ---
    explanation: list[str] = []

    # Report each factor's contribution
    for key, weight in sorted(WEIGHTS.items(), key=lambda x: -x[1]):
        value = metrics.get(key, 0.0)
        pct = weight * 100
        if value >= 80:
            explanation.append(
                f"{key.capitalize()} ({pct:.0f}% weight): strong — {value:.0f}/100"
            )
        elif value >= 50:
            explanation.append(
                f"{key.capitalize()} ({pct:.0f}% weight): moderate — {value:.0f}/100"
            )
        else:
            explanation.append(
                f"{key.capitalize()} ({pct:.0f}% weight): weak — {value:.0f}/100"
            )

    if freshness < 100.0:
        explanation.append(
            f"Telemetry freshness: {freshness:.0f}/100 "
            f"(discount factor {freshness_factor:.2f})"
        )

    logger.debug(
        "Confidence: raw=%.2f freshness_factor=%.2f final=%.2f level=%s",
        raw_score,
        freshness_factor,
        score,
        level,
    )

    return {
        "score":       score,
        "level":       level,
        "explanation": explanation,
    }
