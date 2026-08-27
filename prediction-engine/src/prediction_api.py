"""Prediction Engine API.

Exposes ``GET /prediction/{resource_id}`` for deterministic URS forecasting
using the Composite Threat Propagation Score (CTPS) model.

All placeholder values from Sprint 27 have been removed.
Confidence and business impact are derived from request context.
"""

import datetime
import logging
import os
import time
import json
from typing import Any, Dict, List, Optional, Callable

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from .forecast_engine import PredictiveForecastEngine
from .risk_projection import RiskProjection
from .timeline_builder import TimelineBuilder
from .confidence import calculate_confidence
from .business_impact import calculate_business_impact
from .mongo_repository import MongoRepository
from .prediction_models import ALGORITHM_VERSION, DEFAULT_HORIZONS

logger = logging.getLogger(__name__)

class StandardAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()
            req_id = request.headers.get("x-request-id") or request.headers.get("x-correlation-id") or "REQ-UNKNOWN"
            
            if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
                return await original_route_handler(request)
                
            try:
                response = await original_route_handler(request)
                execution_time = (time.time() - start_time) * 1000.0
                
                if isinstance(response, (JSONResponse, Response)):
                    # Parse body
                    body_bytes = getattr(response, "body", b"")
                    try:
                        data = json.loads(body_bytes.decode("utf-8"))
                    except Exception:
                        data = None
                        
                    if isinstance(data, dict) and "service" in data and "status" in data:
                        return response
                        
                    status = "success"
                    errors = None
                    if response.status_code >= 400:
                        status = "error"
                        errors = data.get("detail") if isinstance(data, dict) else str(data)
                        data = None
                        
                    standardized = {
                        "status": status,
                        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                        "request_id": req_id,
                        "service": request.app.title,
                        "version": request.app.version,
                        "execution_time": f"{execution_time:.2f}ms",
                        "data": data,
                        "errors": errors
                    }
                    
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if k not in standardized or k == "data":
                                standardized[k] = v
                                
                    return JSONResponse(content=standardized, status_code=response.status_code)
                return response
            except RequestValidationError as exc:
                execution_time = (time.time() - start_time) * 1000.0
                standardized = {
                    "status": "error",
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "request_id": req_id,
                    "service": request.app.title,
                    "version": request.app.version,
                    "execution_time": f"{execution_time:.2f}ms",
                    "data": None,
                    "errors": exc.errors()
                }
                return JSONResponse(content=standardized, status_code=422)
            except HTTPException as exc:
                execution_time = (time.time() - start_time) * 1000.0
                standardized = {
                    "status": "error",
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "request_id": req_id,
                    "service": request.app.title,
                    "version": request.app.version,
                    "execution_time": f"{execution_time:.2f}ms",
                    "data": None,
                    "errors": exc.detail
                }
                return JSONResponse(content=standardized, status_code=exc.status_code)
            except Exception as exc:
                execution_time = (time.time() - start_time) * 1000.0
                standardized = {
                    "status": "error",
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "request_id": req_id,
                    "service": request.app.title,
                    "version": request.app.version,
                    "execution_time": f"{execution_time:.2f}ms",
                    "data": None,
                    "errors": str(exc)
                }
                return JSONResponse(content=standardized, status_code=500)

        return custom_route_handler

app = FastAPI(
    title="Prediction Engine API",
    description="Deterministic URS forecasting using the CTPS model",
    version="1.1.0",
)
app.router.route_class = StandardAPIRoute

from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
repo = MongoRepository(MONGO_URI)

request_counter = 0

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    global request_counter
    request_counter += 1
    req_id = request.headers.get("x-request-id") or request.headers.get("x-correlation-id") or f"REQ-PRED-{request_counter}"
    
    # Extract resource_id if possible
    parts = request.url.path.split("/")
    resource_id = "None"
    if len(parts) > 2 and parts[-2] == "prediction":
        resource_id = parts[-1]

    start_time = time.time()
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    
    logger.info(
        "[%s] [Prediction Engine] Request ID: %s | Resource: %s | Path: %s %s | Summary: Initiating forecast evaluation",
        timestamp,
        req_id,
        resource_id,
        request.method,
        request.url.path
    )
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000.0
        timestamp_resp = datetime.datetime.utcnow().isoformat() + "Z"
        logger.info(
            "[%s] [Prediction Engine] Request ID: %s | Resource: %s | Status: %d | Duration: %.2fms | Summary: Successfully generated forecast",
            timestamp_resp,
            req_id,
            resource_id,
            response.status_code,
            duration
        )
        return response
    except Exception as err:
        duration = (time.time() - start_time) * 1000.0
        timestamp_err = datetime.datetime.utcnow().isoformat() + "Z"
        logger.error(
            "[%s] [Prediction Engine] Request ID: %s | Resource: %s | Duration: %.2fms | Error: %s",
            timestamp_err,
            req_id,
            resource_id,
            duration,
            str(err)
        )
        raise err


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class ForecastResult(BaseModel):
    """Complete forecast response."""
    resource_id: str
    current_urs: float
    projected_urs: Dict[str, float]
    ctps: float
    factors: Dict[str, float]
    risk_trend: str
    timeline: List[Dict[str, Any]]
    confidence: Dict[str, Any]
    business_impact: Dict[str, Any]
    explanation: List[str]
    algorithm_version: str
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "OK", "service": "Prediction Engine", "version": "1.1.0"}


@app.get("/prediction/{resource_id}", response_model=ForecastResult)
async def get_prediction(
    resource_id: str,
    current_urs: float = Query(0.0, ge=0, le=100, description="Current URS"),
    # --- Finding context (passed by the Risk Engine) ---
    finding_count: int = Query(0, ge=0),
    critical_count: int = Query(0, ge=0),
    high_count: int = Query(0, ge=0),
    medium_count: int = Query(0, ge=0),
    low_count: int = Query(0, ge=0),
    finding_max_severity: str = Query("None"),
    internet_exposed: bool = Query(False),
    remediation_rate: float = Query(0.5, ge=0, le=1),
    telemetry_trend: str = Query("stable"),
    asset_criticality: str = Query("medium"),
    vulnerability_age_hours: float = Query(0.0, ge=0),
) -> ForecastResult:
    """Return a complete predictive forecast for a given resource.

    All parameters beyond ``resource_id`` and ``current_urs`` are optional
    and default to safe deterministic values when not supplied.
    """
    # --- Build context from query parameters ---
    context: Dict[str, Any] = {
        "finding_count":           finding_count,
        "critical_count":          critical_count,
        "high_count":              high_count,
        "medium_count":            medium_count,
        "low_count":               low_count,
        "finding_max_severity":    finding_max_severity,
        "internet_exposed":        internet_exposed,
        "remediation_rate":        remediation_rate,
        "telemetry_trend":         telemetry_trend,
        "asset_criticality":       asset_criticality,
        "vulnerability_age_hours": vulnerability_age_hours,
    }

    # --- 1. Forecast (CTPS-based) ---
    engine = PredictiveForecastEngine()
    forecast = engine.generate_forecast(resource_id, current_urs, context)

    # --- 2. Risk projection ---
    projection = RiskProjection(current_urs, context)
    risk_proj = projection.full_projection(engine.horizons)

    # --- 3. Timeline with security events ---
    timeline_builder = TimelineBuilder(current_urs, context)
    timeline = timeline_builder.build()

    # --- 4. Confidence (derived from context, not hardcoded) ---
    #
    # Telemetry completeness: higher finding count → more telemetry data
    telemetry_score = min(50.0 + finding_count * 5.0, 100.0)
    # Stability: fewer critical/high findings → more stable
    instability = (critical_count * 20 + high_count * 10
                   + medium_count * 5 + low_count * 2)
    stability_score = max(100.0 - instability, 10.0)
    # Criticality awareness: known criticality boosts confidence
    criticality_scores = {"critical": 90, "high": 75, "medium": 60, "low": 40}
    crit_score = float(criticality_scores.get(asset_criticality, 60))
    # Historical: remediation rate indicates evidence depth
    historical_score = remediation_rate * 100.0

    confidence = calculate_confidence(
        metrics={
            "telemetry":   telemetry_score,
            "stability":   stability_score,
            "criticality": crit_score,
            "historical":  historical_score,
        },
        freshness=min(100.0, max(0.0, 100.0 - vulnerability_age_hours * 0.5)),
    )

    # --- 5. Business impact (derived from URS + findings) ---
    projected_24h = forecast["projected_urs"].get(24, current_urs)
    finding_counts = {
        "Critical": critical_count,
        "High":     high_count,
        "Medium":   medium_count,
        "Low":      low_count,
    }
    business_impact = calculate_business_impact(
        current_urs, projected_24h, finding_counts
    )

    # --- 6. Timestamp ---
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    # Convert integer keys to strings for JSON and BSON compatibility
    projected_str = {str(k): v for k, v in forecast["projected_urs"].items()}

    # --- 7. Persist complete forecast ---
    forecast_doc = {
        "timestamp":         timestamp,
        "urs_before":        current_urs,
        "projected_urs":     projected_str,
        "ctps":              forecast["ctps"],
        "factors":           forecast["factors"],
        "risk_trend":        forecast["risk_trend"],
        "timeline":          timeline,
        "confidence":        confidence,
        "business_impact":   business_impact,
        "explanation":       forecast["explanation"],
        "algorithm_version": ALGORITHM_VERSION,
    }
    try:
        await repo.upsert_forecast(resource_id, forecast_doc)
    except Exception as err:
        logger.warning("Failed to persist forecast: %s", err)

    # --- Build response ---
    return ForecastResult(
        resource_id=resource_id,
        current_urs=current_urs,
        projected_urs=projected_str,
        ctps=forecast["ctps"],
        factors=forecast["factors"],
        risk_trend=forecast["risk_trend"],
        timeline=timeline,
        confidence=confidence,
        business_impact=business_impact,
        explanation=forecast["explanation"],
        algorithm_version=ALGORITHM_VERSION,
        timestamp=timestamp,
    )
