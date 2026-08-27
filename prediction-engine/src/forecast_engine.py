"""Deterministic Predictive Forecast Engine.

Uses the Composite Threat Propagation Score (CTPS) to project the Unified
Risk Score (URS) over configurable future time horizons.

All outputs are deterministic and reproducible from the same inputs.
"""

import logging
from typing import Any, Dict, List, Optional

from .prediction_models import (
    ALGORITHM_VERSION,
    DEFAULT_HORIZONS,
    compute_ctps,
    default_context,
    project_urs,
)

logger = logging.getLogger(__name__)


class PredictiveForecastEngine:
    """Multi-factor deterministic forecast engine for URS projection.

    The engine accepts a *context* dict describing the current security
    posture (finding counts, severity, exposure, telemetry trend, …) and
    produces a forecast mapping each horizon to a projected URS value
    together with an explainability payload.

    Parameters
    ----------
    horizons : list[int], optional
        Time horizons in hours.  Defaults to ``[1, 3, 6, 12, 24]``.
    """

    def __init__(self, horizons: Optional[List[int]] = None) -> None:
        self.horizons: List[int] = horizons or list(DEFAULT_HORIZONS)
        logger.debug("ForecastEngine initialized with horizons %s", self.horizons)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_forecast(
        self,
        resource_id: str,
        current_urs: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete forecast for *resource_id*.

        Parameters
        ----------
        resource_id : str
            Identifier of the resource being evaluated.
        current_urs : float
            Current Unified Risk Score (0–100).
        context : dict, optional
            Finding-level context.  See :func:`prediction_models.default_context`
            for the full schema.  Missing keys are filled with deterministic
            defaults.

        Returns
        -------
        dict
            ``projected_urs``  – mapping horizon (int) → projected URS (float).
            ``ctps``           – computed Composite Threat Propagation Score.
            ``factors``        – individual CTPS factor values.
            ``risk_trend``     – ``"increasing"`` | ``"stable"`` | ``"decreasing"``.
            ``explanation``    – list of human-readable reasons.
            ``algorithm``      – algorithm version string.
        """
        ctx = {**default_context(), **(context or {})}
        ctps_result = compute_ctps(ctx)
        ctps_value = ctps_result["ctps"]
        trend = ctx.get("telemetry_trend", "stable")

        projected: Dict[int, float] = {}
        for h in self.horizons:
            projected[h] = project_urs(current_urs, ctps_value, h, trend)

        # Determine overall risk trend from the 24-h projection
        urs_24h = projected.get(24, projected.get(self.horizons[-1], current_urs))
        if urs_24h > current_urs * 1.05:
            risk_trend = "increasing"
        elif urs_24h < current_urs * 0.95:
            risk_trend = "decreasing"
        else:
            risk_trend = "stable"

        logger.info(
            "Forecast for %s: URS=%.2f → 24h=%.2f  trend=%s  CTPS=%.4f",
            resource_id,
            current_urs,
            urs_24h,
            risk_trend,
            ctps_value,
        )

        return {
            "projected_urs": projected,
            "ctps":          ctps_value,
            "factors":       ctps_result["factors"],
            "risk_trend":    risk_trend,
            "explanation":   ctps_result["explanation"],
            "algorithm":     ALGORITHM_VERSION,
        }
