"""Deterministic risk projection using the CTPS model.

Provides a convenience wrapper around :func:`prediction_models.project_urs`
so that callers can obtain projections without constructing a full forecast.
"""

import logging
from typing import Any, Dict, List, Optional

from .prediction_models import (
    DEFAULT_HORIZONS,
    compute_ctps,
    default_context,
    project_urs,
)

logger = logging.getLogger(__name__)


class RiskProjection:
    """Project URS values over future horizons using the CTPS model.

    Parameters
    ----------
    current_urs : float
        Current Unified Risk Score (0–100).
    context : dict, optional
        Finding-level context for CTPS computation.
    """

    def __init__(
        self,
        current_urs: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.current_urs = current_urs
        self.context = {**default_context(), **(context or {})}
        self._ctps_result = compute_ctps(self.context)
        self._ctps = self._ctps_result["ctps"]
        self._trend = self.context.get("telemetry_trend", "stable")
        logger.debug(
            "RiskProjection: URS=%.3f  CTPS=%.4f  trend=%s",
            current_urs,
            self._ctps,
            self._trend,
        )

    @property
    def ctps(self) -> float:
        """Return the computed CTPS value."""
        return self._ctps

    @property
    def factors(self) -> Dict[str, float]:
        """Return the individual CTPS factor breakdown."""
        return self._ctps_result["factors"]

    def project(self, hours: int) -> float:
        """Project URS forward by *hours*.

        Returns
        -------
        float
            Projected URS clamped to [0, 100].
        """
        return project_urs(self.current_urs, self._ctps, hours, self._trend)

    def full_projection(
        self, horizons: Optional[List[int]] = None
    ) -> Dict[int, float]:
        """Return a mapping of each horizon to its projected URS.

        Parameters
        ----------
        horizons : list[int], optional
            Defaults to ``[1, 3, 6, 12, 24]``.
        """
        hrs = horizons or list(DEFAULT_HORIZONS)
        return {h: self.project(h) for h in hrs}
