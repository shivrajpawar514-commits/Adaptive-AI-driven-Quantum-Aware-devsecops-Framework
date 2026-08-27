"""Deterministic security timeline builder.

Generates a sequence of projected cyber-security events for each forecast
horizon.  Events are selected deterministically based on finding types,
URS thresholds, and the computed CTPS.

No randomness.  Identical inputs always produce identical timelines.
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


# ---------------------------------------------------------------------------
# Deterministic event catalogue
# ---------------------------------------------------------------------------
# Events are keyed by (min_urs_threshold, attack_phase).  The builder walks
# the catalogue and emits events whose URS threshold is met at a given
# horizon.  This ensures reproducibility.

_EVENT_CATALOGUE: List[Dict[str, Any]] = [
    # --- Reconnaissance phase (URS ≥ 10) ---
    {
        "urs_min": 10,
        "attack_phase": "Reconnaissance",
        "event": "Exposed services detected by external scanners",
        "affected_services": ["public-facing endpoints"],
        "requires_finding": None,
    },
    # --- Initial Access phase (URS ≥ 25) ---
    {
        "urs_min": 25,
        "attack_phase": "Initial Access",
        "event": "SSH/RDP brute-force likelihood increases",
        "affected_services": ["SSH", "RDP"],
        "requires_finding": "Network",
    },
    {
        "urs_min": 25,
        "attack_phase": "Initial Access",
        "event": "Credential exposure risk from open management ports",
        "affected_services": ["authentication services"],
        "requires_finding": None,
    },
    # --- Persistence phase (URS ≥ 45) ---
    {
        "urs_min": 45,
        "attack_phase": "Persistence",
        "event": "Credential compromise risk increases significantly",
        "affected_services": ["IAM", "authentication services"],
        "requires_finding": None,
    },
    {
        "urs_min": 45,
        "attack_phase": "Persistence",
        "event": "Unencrypted storage enables data exfiltration",
        "affected_services": ["EBS", "S3", "storage"],
        "requires_finding": "Storage",
    },
    # --- Privilege Escalation phase (URS ≥ 65) ---
    {
        "urs_min": 65,
        "attack_phase": "Privilege Escalation",
        "event": "Privilege escalation becomes likely via misconfigured IAM",
        "affected_services": ["IAM", "EC2"],
        "requires_finding": None,
    },
    # --- Impact phase (URS ≥ 80) ---
    {
        "urs_min": 80,
        "attack_phase": "Impact",
        "event": "Business impact becomes High — potential data breach",
        "affected_services": ["all production services"],
        "requires_finding": None,
    },
    {
        "urs_min": 90,
        "attack_phase": "Impact",
        "event": "Critical operational disruption imminent",
        "affected_services": ["all services", "compliance"],
        "requires_finding": None,
    },
]

# Business impact level thresholds (deterministic mapping)
_IMPACT_LEVELS: List[tuple[float, str]] = [
    (80, "Critical"),
    (65, "High"),
    (45, "Medium"),
    (25, "Low"),
    (0,  "Informational"),
]


def _impact_level(urs: float) -> str:
    """Return the business impact level for a given URS value."""
    for threshold, level in _IMPACT_LEVELS:
        if urs >= threshold:
            return level
    return "Informational"


class TimelineBuilder:
    """Build a deterministic security event timeline.

    Parameters
    ----------
    current_urs : float
        Current Unified Risk Score.
    context : dict, optional
        Finding-level context for CTPS computation.
    horizons : list[int], optional
        Forecast horizons in hours.  Defaults to ``[1, 3, 6, 12, 24]``.
    """

    def __init__(
        self,
        current_urs: float,
        context: Optional[Dict[str, Any]] = None,
        horizons: Optional[List[int]] = None,
    ) -> None:
        self.current_urs = current_urs
        self.context = {**default_context(), **(context or {})}
        self.horizons = horizons or list(DEFAULT_HORIZONS)

        ctps_result = compute_ctps(self.context)
        self._ctps = ctps_result["ctps"]
        self._trend = self.context.get("telemetry_trend", "stable")
        self._explanation_base = ctps_result["explanation"]

        logger.debug(
            "TimelineBuilder: URS=%.3f  CTPS=%.4f  horizons=%s",
            current_urs,
            self._ctps,
            self.horizons,
        )

    def _select_events(
        self, projected_urs: float
    ) -> List[Dict[str, Any]]:
        """Select applicable events for a given projected URS."""
        events = []
        finding_categories: set[str] = set()

        # Derive finding categories from context
        if self.context.get("critical_count", 0) > 0:
            finding_categories.add("Network")
            finding_categories.add("Storage")
        if self.context.get("high_count", 0) > 0:
            finding_categories.add("Network")
            finding_categories.add("Storage")
        if self.context.get("medium_count", 0) > 0:
            finding_categories.add("Network")
        if self.context.get("internet_exposed"):
            finding_categories.add("Network")

        for entry in _EVENT_CATALOGUE:
            if projected_urs < entry["urs_min"]:
                continue
            req_finding = entry["requires_finding"]
            if req_finding and req_finding not in finding_categories:
                continue
            events.append({
                "event":             entry["event"],
                "attack_phase":      entry["attack_phase"],
                "affected_services": entry["affected_services"],
            })

        return events

    def build(self) -> List[Dict[str, Any]]:
        """Build the complete timeline.

        Returns
        -------
        list[dict]
            Each entry contains:
            - ``horizon_hours`` (int)
            - ``projected_urs`` (float)
            - ``confidence`` (float, 0–100)
            - ``business_impact_level`` (str)
            - ``events`` (list of event dicts)
            - ``explanation`` (str)
        """
        timeline: List[Dict[str, Any]] = []

        for h in self.horizons:
            projected = project_urs(
                self.current_urs, self._ctps, h, self._trend
            )
            events = self._select_events(projected)

            # Confidence degrades linearly with horizon (deterministic)
            confidence = max(100.0 - h * 2.5, 40.0)

            # Build explanation for this horizon
            if projected > self.current_urs:
                direction = "increases"
            elif projected < self.current_urs:
                direction = "decreases"
            else:
                direction = "remains stable"

            explanation = (
                f"URS {direction} from {self.current_urs:.1f} to "
                f"{projected:.1f} at {h}h horizon. "
                + "; ".join(self._explanation_base)
            )

            entry = {
                "horizon_hours":       h,
                "projected_urs":       projected,
                "confidence":          round(confidence, 1),
                "business_impact_level": _impact_level(projected),
                "events":              events,
                "explanation":         explanation,
            }
            timeline.append(entry)
            logger.debug("Timeline %dh: URS=%.2f events=%d", h, projected, len(events))

        return timeline
