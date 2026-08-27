import datetime
import os
import time
import json
from typing import Callable
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

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
                                
                    log_time = datetime.datetime.utcnow().isoformat() + "Z"
                    print(f"[{log_time}] [{request.app.title}] [{req_id}] [N/A] [{request.method}] [{request.url.path}] [{execution_time:.2f}ms] [{response.status_code}] Request processed successfully")
                    return JSONResponse(content=standardized, status_code=response.status_code)
                log_time = datetime.datetime.utcnow().isoformat() + "Z"
                print(f"[{log_time}] [{request.app.title}] [{req_id}] [N/A] [{request.method}] [{request.url.path}] [{execution_time:.2f}ms] [{response.status_code}] Success")
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
                log_time = datetime.datetime.utcnow().isoformat() + "Z"
                print(f"[{log_time}] [{request.app.title}] [{req_id}] [N/A] [{request.method}] [{request.url.path}] [{execution_time:.2f}ms] [422] Validation Error")
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
                log_time = datetime.datetime.utcnow().isoformat() + "Z"
                print(f"[{log_time}] [{request.app.title}] [{req_id}] [N/A] [{request.method}] [{request.url.path}] [{execution_time:.2f}ms] [{exc.status_code}] HTTP Exception: {exc.detail}")
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
                log_time = datetime.datetime.utcnow().isoformat() + "Z"
                print(f"[{log_time}] [{request.app.title}] [{req_id}] [N/A] [{request.method}] [{request.url.path}] [{execution_time:.2f}ms] [500] Exception: {str(exc)}")
                return JSONResponse(content=standardized, status_code=500)

        return custom_route_handler

from src.risk.calculator import URSCalculator
from src.decision.engine import DecisionEngine
from src.database.db_connection import RiskDatabase
from src.explainability.explainer import RiskExplainer
from src.quantum.readiness_engine import QuantumReadinessEngine

app = FastAPI(title="Adaptive Risk Engine API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_helper = RiskDatabase()
calculator = URSCalculator()
decision_engine = DecisionEngine(thresholds=calculator.config["thresholds"])
explainer = RiskExplainer(calculator)
quantum_engine = QuantumReadinessEngine()

class EvaluateRequest(BaseModel):
    anomaly_score: float
    reconstruction_error: float
    confidence_score: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    timestamp: str = None
    workload_profile: str = "Development"
    cryptography: list = None
    resource_id: str = None  # Optional: identifies the resource being evaluated

@app.get("/health")
def health():
    return {"status": "OK", "version": "1.0.0"}

@app.post("/risk/evaluate")
def evaluate(req: EvaluateRequest, request: Request):
    try:
        req_id = request.headers.get("x-request-id") or request.headers.get("x-correlation-id") or "REQ-UNKNOWN"
        history = db_helper.get_history(100)
        if history:
            anomalous = sum(1 for e in history if e.get("decision") != "Normal")
            historical_frequency = anomalous / len(history)
        else:
            historical_frequency = 0.0

        # Calculate Adaptive URS (which also computes Static URS internally)
        urs = calculator.calculate(
            anomaly_score=req.anomaly_score,
            reconstruction_error=req.reconstruction_error,
            confidence_score=req.confidence_score,
            cpu_usage=req.cpu_usage,
            memory_usage=req.memory_usage,
            network_usage=req.network_usage,
            historical_frequency=historical_frequency,
            disk_usage=req.disk_usage,
            timestamp=req.timestamp,
            workload_profile=req.workload_profile
        )

        # Apply real cloud security assessment findings penalties to URS score
        findings_penalty = 0.0
        try:
            if not db_helper.is_mock:
                findings = list(db_helper.db.cloud_security_findings.find({}, {"_id": 0}))
                for f in findings:
                    findings_penalty += f.get("ursPenalty", 0)
        except Exception as err:
            print(f"Error querying cloud findings for URS calculation: {str(err)}")

        urs = min(urs + findings_penalty, 100.0)

        telemetry = {
            "cpu_usage": req.cpu_usage,
            "memory_usage": req.memory_usage,
            "disk_usage": req.disk_usage,
            "network_usage": req.network_usage
        }

        # Retrieve context metadata from current evaluation
        meta = calculator.get_context_metadata()
        adaptive_thresholds = meta["adaptive_thresholds"]

        # Evaluate decision logic using adaptive thresholds
        decision, reason = decision_engine.evaluate(urs, telemetry, req.reconstruction_error, thresholds=adaptive_thresholds)

        explanation = explainer.generate_explanation(urs)
        timestamp_str = req.timestamp or datetime.datetime.utcnow().isoformat()

        static_urs = meta["static_urs"]
        rounded_static = round(static_urs, 2)
        rounded_adaptive = round(urs, 2)
        diff = rounded_adaptive - rounded_static

        # Calculate comparative research metrics
        if diff < 0:
            improvement = f"Reduced false positives during {explanation['context']['profile'].lower()} workload."
        elif diff > 0:
            improvement = "Increased sensitivity to threats during high-activity context."
        else:
            improvement = "No deviation from static baseline."

        comparison_data = {
            "staticURS": rounded_static,
            "adaptiveURS": rounded_adaptive,
            "difference": round(diff, 2),
            "improvement": improvement
        }

        # Calculate Quantum Readiness
        q_result = quantum_engine.evaluate_posture(req.cryptography)

        # Fetch Policy Recommendations
        recommendations = []
        policy_url = os.getenv("POLICY_ENGINE_URL", "http://localhost:8700")
        try:
            policy_payload = {
                "urs": urs,
                "decision": decision,
                "topContributor": explanation["topContributor"],
                "anomaly_score": req.anomaly_score,
                "reconstruction_error": req.reconstruction_error,
                "context": explanation["context"],
                "quantumReadiness": q_result["quantumReadiness"],
                "cryptography": q_result["cryptography"]
            }
            import httpx
            with httpx.Client() as client:
                headers = {"X-Correlation-Id": req_id, "X-Request-Id": req_id}
                policy_res = client.post(f"{policy_url}/policy/recommend", json=policy_payload, headers=headers, timeout=2.0)
                if policy_res.status_code == 200:
                    recommendations = policy_res.json()
        except Exception as err:
            print(f"Policy Engine unreachable during evaluation: {str(err)}. Using fallback mockup.")
            if decision != "Normal":
                recommendations = [
                    {
                        "recommendationId": "REC-FALLBACK-001",
                        "title": f"Mitigate {explanation['topContributor']} Anomaly",
                        "description": "Trigger local containment playbook to isolate container and restrict resource bounds.",
                        "category": "Kubernetes",
                        "priority": "High",
                        "confidence": 0.85,
                        "estimatedRiskReduction": 45.0,
                        "automationSupported": True,
                        "reasoning": f"Anomaly detected in {explanation['topContributor']} with URS score {urs}."
                    }
                ]
            else:
                recommendations = [
                    {
                        "recommendationId": "REC-FALLBACK-100",
                        "title": "Enable DevSecOps Baseline Telemetry Audits",
                        "description": "Keep standard Prometheus scraping intervals and configure automated log integrity monitoring.",
                        "category": "Monitoring",
                        "priority": "Low",
                        "confidence": 0.99,
                        "estimatedRiskReduction": 5.0,
                        "automationSupported": True,
                        "reasoning": "Baseline metrics are normal."
                    }
                ]

        # Fetch Prediction Summary from Prediction Engine
        prediction_url = os.getenv("PREDICTION_ENGINE_URL", "http://127.0.0.1:8005")
        pred_resource_id = req.resource_id or f"{req.workload_profile}-{timestamp_str}"
        print(f"DEBUG: prediction_url = {prediction_url}, pred_resource_id = {pred_resource_id}")

        # Gather finding context from cloud_security_findings (already queried above)
        finding_context_params = {"current_urs": urs}
        try:
            if not db_helper.is_mock:
                cloud_findings = list(db_helper.db.cloud_security_findings.find({}, {"_id": 0}))
            else:
                cloud_findings = []
            crit_c = sum(1 for f in cloud_findings if f.get("severity") == "Critical")
            high_c = sum(1 for f in cloud_findings if f.get("severity") == "High")
            med_c  = sum(1 for f in cloud_findings if f.get("severity") == "Medium")
            low_c  = sum(1 for f in cloud_findings if f.get("severity") == "Low")
            total_f = len(cloud_findings)
            max_sev = "Critical" if crit_c else "High" if high_c else "Medium" if med_c else "Low" if low_c else "None"
            has_public = any(f.get("id") == "EC2-PUBLIC-IP" for f in cloud_findings)
            finding_context_params.update({
                "finding_count": total_f,
                "critical_count": crit_c,
                "high_count": high_c,
                "medium_count": med_c,
                "low_count": low_c,
                "finding_max_severity": max_sev,
                "internet_exposed": has_public,
            })
        except Exception as ctx_err:
            print(f"Warning: could not gather finding context: {ctx_err}")

        try:
            import httpx
            pred_resp = httpx.get(
                f"{prediction_url}/prediction/{pred_resource_id}",
                params=finding_context_params,
                headers={"X-Correlation-Id": req_id, "X-Request-Id": req_id},
                timeout=15.0,
            )
            if pred_resp.status_code == 200:
                prediction_summary = pred_resp.json()
            else:
                prediction_summary = {"error": f"Prediction service returned {pred_resp.status_code}"}
        except Exception as err:
            prediction_summary = {"error": str(err)}
        
        doc = {
            "timestamp": timestamp_str,
            "telemetry": telemetry,
            "anomaly_score": req.anomaly_score,
            "confidence": req.confidence_score,
            "urs": urs,
            "decision": decision,
            "reason": reason,
            "contributors": explanation["contributors"],
            "topContributor": explanation["topContributor"],
            "context": explanation["context"],
            "adaptiveWeights": explanation["adaptiveWeights"],
            "comparison": comparison_data,
            "contextConfidence": meta["context_confidence"],
            "profileVersion": meta["profile_version"],
            "adaptationReason": meta["adaptation_reason"],
            "quantumReadiness": q_result["quantumReadiness"],
            "cryptography": q_result["cryptography"],
            "quantumExplanation": q_result["quantumExplanation"],
            "dashboardData": q_result["dashboardData"],
            "recommendations": recommendations,
            "prediction_summary": prediction_summary,
        }

        db_helper.insert_evaluation(doc)

        return {
            "status": "success",
            "urs": urs,
            "risk_score": urs,
            "decision": decision,
            "reason": reason,
            "contributors": explanation["contributors"],
            "topContributor": explanation["topContributor"],
            "timestamp": timestamp_str,
            "context": explanation["context"],
            "adaptiveWeights": explanation["adaptiveWeights"],
            "comparison": comparison_data,
            "contextConfidence": meta["context_confidence"],
            "profileVersion": meta["profile_version"],
            "adaptationReason": meta["adaptation_reason"],
            "quantumReadiness": q_result["quantumReadiness"],
            "cryptography": q_result["cryptography"],
            "quantumExplanation": q_result["quantumExplanation"],
            "dashboardData": q_result["dashboardData"],
            "recommendations": recommendations,
            "prediction_summary": prediction_summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk evaluation failure: {str(e)}")

@app.get("/risk/history")
def history(limit: int = 20):
    try:
        records = db_helper.get_history(limit)
        return {"status": "success", "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.get("/risk/latest")
def latest():
    try:
        record = db_helper.get_latest()
        if not record:
            raise HTTPException(status_code=404, detail="No risk evaluations recorded yet.")
        return {"status": "success", "data": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest: {str(e)}")

@app.get("/risk/statistics")
def statistics():
    try:
        stats = db_helper.get_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
