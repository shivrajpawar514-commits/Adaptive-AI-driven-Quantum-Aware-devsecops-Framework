"""Deterministic multi-factor prediction models for the Prediction Engine.

This module defines the Composite Threat Propagation Score (CTPS) and all
shared constants, weights, and helper functions used by the forecast engine,
risk projection, and timeline builder.

All calculations are deterministic and reproducible.  No randomness, no ML,
no external APIs.

CTPS Formula
------------
CTPS = (severity_weight
        × exposure_weight
        × criticality_weight
        × age_weight
        × trend_weight
        × persistence_weight
        × remediation_weight)

Projected URS = f(current_urs, CTPS, horizon_hours)
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Severity weights  –  derived from CVSS v3 qualitative severity mapping
# ---------------------------------------------------------------------------
SEVERITY_WEIGHTS: Dict[str, float] = {
    "Critical": 1.8,
    "High":     1.4,
    "Medium":   1.0,
    "Low":      0.6,
    "None":     0.3,
}

# ---------------------------------------------------------------------------
# Exposure weights  –  Internet-facing assets propagate risk faster
# ---------------------------------------------------------------------------
EXPOSURE_WEIGHTS: Dict[bool, float] = {
    True:  1.3,   # publicly reachable
    False: 1.0,   # internal only
}

# ---------------------------------------------------------------------------
# Asset criticality weights
# ---------------------------------------------------------------------------
CRITICALITY_WEIGHTS: Dict[str, float] = {
    "critical": 1.5,
    "high":     1.2,
    "medium":   1.0,
    "low":      0.8,
}

# ---------------------------------------------------------------------------
# Telemetry trend weights
# ---------------------------------------------------------------------------
TREND_WEIGHTS: Dict[str, float] = {
    "worsening": 1.4,
    "stable":    1.0,
    "improving": 0.7,
}

# ---------------------------------------------------------------------------
# Base decay rate per hour (natural risk change when no remediation occurs)
# ---------------------------------------------------------------------------
BASE_RATE_PER_HOUR: float = 0.02

# ---------------------------------------------------------------------------
# Vulnerability age scaling  –  older findings increase risk, capped at 2×
# Age is measured in hours; 168 h = 1 week.
# ---------------------------------------------------------------------------
AGE_NORMALIZATION_HOURS: float = 168.0
AGE_WEIGHT_CAP: float = 2.0

# ---------------------------------------------------------------------------
# Default horizons (hours)
# ---------------------------------------------------------------------------
DEFAULT_HORIZONS: list[int] = [1, 3, 6, 12, 24]

# ---------------------------------------------------------------------------
# Algorithm version string  –  persisted with every forecast for traceability
# ---------------------------------------------------------------------------
ALGORITHM_VERSION: str = "CTPS-v1.0"


# ---------------------------------------------------------------------------
# Default context  –  used when the caller does not supply finding context
# ---------------------------------------------------------------------------
def default_context() -> Dict[str, Any]:
    """Return a default context dict with safe deterministic values.

    This is used when the prediction engine receives a request without
    finding-level detail.  Every default is documented so that research
    validation can reproduce the same outputs.
    """
    return {
        "finding_count":            0,
        "critical_count":           0,
        "high_count":               0,
        "medium_count":             0,
        "low_count":                0,
        "finding_max_severity":     "None",
        "internet_exposed":         False,
        "remediation_rate":         0.5,    # assume 50 % remediation rate
        "telemetry_trend":          "stable",
        "asset_criticality":        "medium",
        "vulnerability_age_hours":  0.0,
    }


# ---------------------------------------------------------------------------
# CTPS calculation
# ---------------------------------------------------------------------------
def compute_ctps(context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compute the Composite Threat Propagation Score.

    Parameters
    ----------
    context : dict, optional
        Keys described in :func:`default_context`.  Missing keys are filled
        from defaults.

    Returns
    -------
    dict
        ``ctps``         – the composite score (float).
        ``factors``      – individual factor values used (dict).
        ``explanation``  – human-readable list of contributing reasons.
    """
    ctx = {**default_context(), **(context or {})}

    # --- Individual factors ------------------------------------------------
    severity_w   = SEVERITY_WEIGHTS.get(ctx["finding_max_severity"], 1.0)
    exposure_w   = EXPOSURE_WEIGHTS.get(ctx["internet_exposed"], 1.0)
    criticality_w = CRITICALITY_WEIGHTS.get(ctx["asset_criticality"], 1.0)
    trend_w      = TREND_WEIGHTS.get(ctx["telemetry_trend"], 1.0)

    # Persistence: more open findings → slower natural decay → higher risk
    persistence_w = 1.0 + ctx["finding_count"] * 0.05

    # Remediation: higher rate → lower risk propagation
    remediation_w = max(1.0 - ctx["remediation_rate"] * 0.5, 0.3)

    # Vulnerability age: older findings increase risk, capped
    age_w = min(
        1.0 + ctx["vulnerability_age_hours"] / AGE_NORMALIZATION_HOURS,
        AGE_WEIGHT_CAP,
    )

    ctps = (
        severity_w
        * exposure_w
        * criticality_w
        * trend_w
        * persistence_w
        * remediation_w
        * age_w
    )

    factors = {
        "severity":     severity_w,
        "exposure":     exposure_w,
        "criticality":  criticality_w,
        "trend":        trend_w,
        "persistence":  persistence_w,
        "remediation":  remediation_w,
        "age":          age_w,
    }

    # --- Explainability ----------------------------------------------------
    explanation: list[str] = []
    if ctx["finding_max_severity"] in ("Critical", "High"):
        explanation.append(
            f"{ctx['finding_max_severity']}-severity finding remains open"
        )
    if ctx["internet_exposed"]:
        explanation.append("Asset is Internet-facing")
    if ctx["asset_criticality"] in ("critical", "high"):
        explanation.append(
            f"Asset criticality is {ctx['asset_criticality']}"
        )
    if ctx["telemetry_trend"] == "worsening":
        explanation.append("Telemetry trend is worsening")
    elif ctx["telemetry_trend"] == "improving":
        explanation.append("Telemetry trend is improving")
    if ctx["finding_count"] > 3:
        explanation.append(
            f"{ctx['finding_count']} open findings increase persistence risk"
        )
    if ctx["remediation_rate"] < 0.3:
        explanation.append("Historical remediation effectiveness is low")
    if ctx["vulnerability_age_hours"] > AGE_NORMALIZATION_HOURS:
        explanation.append(
            f"Oldest vulnerability is {ctx['vulnerability_age_hours']:.0f}h old"
        )
    if not explanation:
        explanation.append("Baseline risk factors are within normal ranges")

    logger.info("CTPS=%.4f factors=%s", ctps, factors)

    return {
        "ctps":        round(ctps, 6),
        "factors":     factors,
        "explanation": explanation,
    }


def project_urs(
    current_urs: float,
    ctps: float,
    hours: int,
    trend: str = "stable",
) -> float:
    """Project URS forward using the CTPS.

    Parameters
    ----------
    current_urs : float
        Current Unified Risk Score (0–100).
    ctps : float
        Composite Threat Propagation Score.
    hours : int
        Forecast horizon in hours.
    trend : str
        ``"worsening"`` | ``"stable"`` | ``"improving"``

    Returns
    -------
    float
        Projected URS clamped to [0, 100].

    Formula
    -------
    ::

        effective_rate = BASE_RATE_PER_HOUR * ctps

        worsening  → projected = URS × (1 + effective_rate × hours)
        stable     → projected = URS × (1 + effective_rate × hours × 0.3)
        improving  → projected = URS × (1 - effective_rate × hours)
    """
    effective_rate = BASE_RATE_PER_HOUR * ctps

    if trend == "worsening":
        projected = current_urs * (1.0 + effective_rate * hours)
    elif trend == "improving":
        projected = current_urs * (1.0 - effective_rate * hours)
    else:
        # stable: slight upward drift to model unattended risk
        projected = current_urs * (1.0 + effective_rate * hours * 0.3)

    return round(max(min(projected, 100.0), 0.0), 4)
