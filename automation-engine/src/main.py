import os
import datetime
import time
import json
from typing import List, Dict, Any, Optional, Callable
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .actions import ActionGenerator
from .audit import AutomationDatabase
from .execution_repository import InMemoryExecutionRepository
from .execution_manager import ExecutionSession
from .graph_builder import topological_sort
from .progress_tracker import compute_progress
from .verification_engine import verify_playbook
from .rollback_engine import rollback_playbook
from .report_generator import generate_report
from .optimizer import get_optimizer
from .playbook_registry import PLAYBOOKS_REGISTRY, get_playbook_by_id

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

app = FastAPI(title="Autonomous DevSecOps Remediation & Automation Engine API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

action_generator = ActionGenerator()

db_helper = AutomationDatabase()
execution_repo = InMemoryExecutionRepository()
class ExecuteRequest(BaseModel):
    riskScore: float = Field(default=95.0, description="Risk score percentage")
    decision: str = Field(default="Critical", description="Decision classification")
    recommendations: List[Any] = Field(default_factory=list, description="Policy recommendations list")
    provider: Optional[str] = Field(default="aws", description="Cloud provider name")
    instanceId: Optional[str] = Field(default=None, description="Target EC2 instance identifier")

class RollbackRequest(BaseModel):
    auditId: str = Field(..., description="Audit record ID to rollback")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Automation Engine",
        "version": "1.0",
        "database": "MongoDB Atlas" if not db_helper.is_mock else "Mock Database"
    }

@app.post("/automation/execute")
def execute_remediation(req: ExecuteRequest):
    try:
        target_id = req.instanceId or "target-ec2"
        plan = action_generator.generate_plan(
            risk_score=req.riskScore,
            decision=req.decision,
            recommendations=req.recommendations,
            provider=req.provider or "aws",
            instance_id=target_id
        )
        
        audit_id = f"AUD-AUTO-{int(datetime.datetime.utcnow().timestamp())}"
        
        audit_doc = {
            "auditId": audit_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "instanceId": target_id,
            "provider": req.provider or "aws",
            "riskScore": req.riskScore,
            "decision": req.decision,
            "recommendations": req.recommendations,
            "executionPlanCount": len(plan["executionPlan"]),
            "executionPlan": plan["executionPlan"],
            "ansiblePlaybook": plan["ansiblePlaybook"],
            "terraformManifest": plan["terraformManifest"],
            "awsCliCommands": plan["awsCliCommands"],
            "kubectlCommands": plan["kubectlCommands"],
            "shellScript": plan["shellScript"],
            "jsonPlan": plan["jsonPlan"],
            "automationLevel": plan["automationLevel"],
            "estimatedExecutionTime": plan["estimatedExecutionTime"],
            "executionStatus": "Executed (Simulation Mode)",
            "rollbackStatus": "Available",
            # Optimization Run Records
            "metrics": plan.get("metrics"),
            "executionOrder": plan.get("executionOrder"),
            "rejectedPlaybooks": plan.get("rejectedPlaybooks"),
            "ursBefore": plan.get("ursBefore"),
            "ursAfter": plan.get("ursAfter"),
            "ursProjection": plan.get("ursProjection"),
            "dependencyGraph": plan.get("dependencyGraph"),
            "optimizationRationale": plan.get("optimizationRationale"),
            "conflictResolutionExplanation": plan.get("conflictResolutionExplanation")
        }
        
        db_helper.save_execution(audit_doc)
        
        plan["auditId"] = audit_id
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autonomous remediation execution failed: {str(e)}")

@app.post("/automation/optimize")
def optimize_playbooks(req: ExecuteRequest):
    try:
        # Convert incoming recommendations into finding formats
        findings = []
        for rec in req.recommendations:
            if isinstance(rec, dict):
                findings.append({
                    "title": rec.get("title", ""),
                    "resource": rec.get("resource", ""),
                    "severity": rec.get("severity", req.decision),
                })
            else:
                findings.append({"title": str(rec), "resource": "", "severity": req.decision})

        optimizer = get_optimizer("deterministic")
        opt_res = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, req.riskScore)

        if "error" in opt_res:
            raise HTTPException(status_code=404, detail="No compatible playbooks found to optimize.")

        # Save optimization run in audit for verification
        audit_id = f"AUD-OPT-{int(datetime.datetime.utcnow().timestamp())}"
        audit_doc = {
            "auditId": audit_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "instanceId": req.instanceId or "target-ec2",
            "provider": req.provider or "aws",
            "riskScore": req.riskScore,
            "decision": req.decision,
            "recommendations": req.recommendations,
            "executionPlanCount": len(opt_res["executionOrder"]),
            "executionStatus": "Optimized",
            "rollbackStatus": "N/A",
            "metrics": opt_res["metrics"],
            "executionOrder": opt_res["executionOrder"],
            "rejectedPlaybooks": opt_res["rejectedPlaybooks"],
            "ursBefore": opt_res["ursBefore"],
            "ursAfter": opt_res["ursAfter"],
            "ursProjection": opt_res["ursProjection"],
            "dependencyGraph": opt_res["dependencyGraph"],
            "optimizationRationale": opt_res["optimizationRationale"],
            "conflictResolutionExplanation": opt_res["conflictResolutionExplanation"]
        }
        db_helper.save_execution(audit_doc)

        opt_res["auditId"] = audit_id
        return opt_res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Playbook optimization failed: {str(e)}")

@app.get("/automation/history")
def get_automation_history():
    try:
        records = db_helper.get_history()
        return {
            "status": "success",
            "count": len(records),
            "data": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch automation audit history: {str(e)}")

@app.post("/automation/rollback")
def rollback_remediation(req: RollbackRequest):
    try:
        result = db_helper.trigger_rollback(req.auditId)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback execution failed: {str(e)}")
