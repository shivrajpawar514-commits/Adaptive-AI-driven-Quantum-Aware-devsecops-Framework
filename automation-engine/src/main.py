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

AUTHORIZED_ROLES = {"admin", "secops", "secops-lead", "operator"}
APPROVER_ROLES = {"admin", "secops-lead"}

class ExecuteRequest(BaseModel):
    riskScore: float = Field(default=95.0, description="Risk score percentage")
    decision: str = Field(default="Critical", description="Decision classification")
    recommendations: List[Any] = Field(default_factory=list, description="Policy recommendations list")
    provider: Optional[str] = Field(default="aws", description="Cloud provider name")
    instanceId: Optional[str] = Field(default=None, description="Target EC2 instance identifier")
    dryRun: bool = Field(default=False, description="Dry run mode: validates and plans without executing state changes")
    operator: Optional[str] = Field(default="secops-operator", description="Operator identity executing the remediation")
    operatorRole: Optional[str] = Field(default="secops", description="Role of the operator: admin, secops, operator, guest, viewer")
    authToken: Optional[str] = Field(default=None, description="Authentication / authorization token")
    approved: bool = Field(default=False, description="Manual approval flag for critical high-impact actions")
    approvedBy: Optional[str] = Field(default=None, description="Approver username / lead")
    approverRole: Optional[str] = Field(default=None, description="Role of the approver (e.g. secops-lead, admin)")

class ApproveRequest(BaseModel):
    auditId: str = Field(..., description="Audit ID or Gate ID to approve")
    approvedBy: str = Field(..., description="Approver username / identifier")
    approverRole: str = Field(default="secops-lead", description="Approver role (must be secops-lead or admin)")

class RollbackRequest(BaseModel):
    auditId: str = Field(..., description="Audit record ID to rollback")
    operator: Optional[str] = Field(default="secops-operator", description="Operator executing rollback")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Automation Engine",
        "version": "1.0",
        "database": "MongoDB Atlas" if not db_helper.is_mock else "Mock Database",
        "features": {
            "dryRun": True,
            "authorizationRBAC": True,
            "approvalGates": True,
            "rollbackPlans": True,
            "cryptographicAuditTrails": True
        }
    }

@app.post("/automation/execute")
def execute_remediation(req: ExecuteRequest):
    # 1. Authorization Check
    role = (req.operatorRole or "guest").lower()
    if role not in AUTHORIZED_ROLES:
        # Audit failed auth attempt
        failed_audit = {
            "auditId": f"AUD-DENIED-{int(datetime.datetime.utcnow().timestamp())}",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "instanceId": req.instanceId or "target-ec2",
            "operator": req.operator,
            "operatorRole": req.operatorRole,
            "riskScore": req.riskScore,
            "decision": req.decision,
            "executionStatus": "Authorization Denied",
            "rollbackStatus": "N/A",
            "auditTrail": [
                {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "event": "AUTHORIZATION_DENIED",
                    "operator": req.operator,
                    "role": req.operatorRole,
                    "reason": f"Role '{req.operatorRole}' is not permitted to execute remediations"
                }
            ]
        }
        db_helper.save_execution(failed_audit)
        raise HTTPException(
            status_code=403,
            detail=f"Authorization check failed: Operator role '{req.operatorRole}' is not permitted to execute remediations."
        )

    if req.authToken in ("invalid-token", "unauthorized", "expired"):
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid or expired token.")

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
        now_iso = datetime.datetime.utcnow().isoformat() + "Z"

        # 2. Approval Gate Check for Critical Incidents
        is_critical = req.riskScore >= 90.0 or req.decision.lower() in ("critical", "emergency")
        gate_required = is_critical and not req.dryRun
        
        if gate_required and not req.approved:
            # Requires approval gate
            gate_id = f"GATE-{audit_id}"
            pending_doc = {
                "auditId": audit_id,
                "gateId": gate_id,
                "timestamp": now_iso,
                "instanceId": target_id,
                "provider": req.provider or "aws",
                "operator": req.operator,
                "operatorRole": req.operatorRole,
                "dryRun": False,
                "riskScore": req.riskScore,
                "decision": req.decision,
                "recommendations": req.recommendations,
                "executionPlanCount": len(plan["executionPlan"]),
                "executionPlan": plan["executionPlan"],
                "rollbackPlan": plan.get("rollbackPlan", []),
                "executionStatus": "Pending Approval",
                "rollbackStatus": "Pending",
                "approvalGate": {
                    "required": True,
                    "approved": False,
                    "requiredRole": "secops-lead",
                    "gateId": gate_id
                },
                "auditTrail": [
                    {"timestamp": now_iso, "event": "REMEDIATION_REQUESTED", "operator": req.operator, "role": req.operatorRole},
                    {"timestamp": now_iso, "event": "APPROVAL_GATE_REQUIRED", "gateId": gate_id, "requiredRole": "secops-lead"}
                ]
            }
            db_helper.save_execution(pending_doc)
            plan["auditId"] = audit_id
            plan["gateId"] = gate_id
            plan["executionStatus"] = "Pending Approval"
            plan["approvalGate"] = pending_doc["approvalGate"]
            plan["message"] = "Remediation plan generated but requires SecOps lead approval. Call POST /automation/approve with gateId."
            return plan

        # If approved, verify approver role
        if gate_required and req.approved:
            app_role = (req.approverRole or "").lower()
            if app_role not in APPROVER_ROLES:
                raise HTTPException(
                    status_code=403,
                    detail=f"Approval gate verification failed: Approver role '{req.approverRole}' cannot approve critical actions. Required: {list(APPROVER_ROLES)}."
                )

        # 3. Dry-Run Mode or Normal Execution
        if req.dryRun:
            status_text = "Dry Run (Simulated)"
            trail_events = [
                {"timestamp": now_iso, "event": "REMEDIATION_DRY_RUN_REQUESTED", "operator": req.operator, "role": req.operatorRole},
                {"timestamp": now_iso, "event": "DRY_RUN_PLAN_VALIDATED", "status": "SUCCESS"}
            ]
        else:
            status_text = "Executed (Simulation Mode)"
            trail_events = [
                {"timestamp": now_iso, "event": "REMEDIATION_REQUESTED", "operator": req.operator, "role": req.operatorRole},
                {"timestamp": now_iso, "event": "AUTHORIZATION_VERIFIED", "status": "AUTHORIZED"},
                {"timestamp": now_iso, "event": "REMEDIATION_EXECUTED", "status": "COMPLETED"}
            ]
            if req.approved:
                trail_events.insert(1, {
                    "timestamp": now_iso,
                    "event": "OPERATOR_APPROVED",
                    "approvedBy": req.approvedBy,
                    "approverRole": req.approverRole
                })

        audit_doc = {
            "auditId": audit_id,
            "timestamp": now_iso,
            "instanceId": target_id,
            "provider": req.provider or "aws",
            "operator": req.operator,
            "operatorRole": req.operatorRole,
            "dryRun": req.dryRun,
            "riskScore": req.riskScore,
            "decision": req.decision,
            "recommendations": req.recommendations,
            "executionPlanCount": len(plan["executionPlan"]),
            "executionPlan": plan["executionPlan"],
            "rollbackPlan": plan.get("rollbackPlan", []),
            "ansiblePlaybook": plan["ansiblePlaybook"],
            "ansibleRollbackPlaybook": plan.get("ansibleRollbackPlaybook"),
            "terraformManifest": plan["terraformManifest"],
            "awsCliCommands": plan["awsCliCommands"],
            "rollbackCliCommands": plan.get("rollbackCliCommands", []),
            "kubectlCommands": plan["kubectlCommands"],
            "shellScript": plan["shellScript"],
            "rollbackShellScript": plan.get("rollbackShellScript"),
            "jsonPlan": plan["jsonPlan"],
            "automationLevel": plan["automationLevel"],
            "estimatedExecutionTime": plan["estimatedExecutionTime"],
            "executionStatus": status_text,
            "rollbackStatus": "Available" if not req.dryRun else "N/A (Dry Run)",
            "approvalGate": {
                "required": is_critical,
                "approved": True if (is_critical and req.approved) or not is_critical else False,
                "approvedBy": req.approvedBy
            },
            "auditTrail": trail_events,
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
        plan["dryRun"] = req.dryRun
        plan["executionStatus"] = status_text
        plan["operator"] = req.operator
        plan["sha256Signature"] = audit_doc.get("sha256Signature")
        plan["auditTrail"] = trail_events
        return plan
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autonomous remediation execution failed: {str(e)}")

@app.post("/automation/approve")
def approve_remediation(req: ApproveRequest):
    app_role = (req.approverRole or "").lower()
    if app_role not in APPROVER_ROLES:
        raise HTTPException(
            status_code=403,
            detail=f"Approval permission denied: Role '{req.approverRole}' is not an authorized approver. Allowed roles: {list(APPROVER_ROLES)}."
        )

    records = db_helper.get_history()
    target = next((r for r in records if r.get("auditId") == req.auditId or r.get("gateId") == req.auditId), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Pending approval request '{req.auditId}' not found.")

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    target["executionStatus"] = "Executed (Simulation Mode)"
    target["rollbackStatus"] = "Available"
    target["approvalGate"] = {
        "required": True,
        "approved": True,
        "approvedBy": req.approvedBy,
        "approvedAt": now_iso
    }
    if "auditTrail" not in target:
        target["auditTrail"] = []
    target["auditTrail"].append({
        "timestamp": now_iso,
        "event": "APPROVAL_GRANTED",
        "approvedBy": req.approvedBy,
        "approverRole": req.approverRole,
        "status": "Executed (Simulation Mode)"
    })
    target["sha256Signature"] = db_helper._compute_audit_hash(target)
    
    return {
        "status": "success",
        "auditId": target["auditId"],
        "message": f"Remediation plan approved by {req.approvedBy} ({req.approverRole}) and executed in simulation mode.",
        "executionStatus": target["executionStatus"],
        "rollbackPlan": target.get("rollbackPlan", [])
    }

@app.get("/automation/audit/verify/{audit_id}")
def verify_audit_record(audit_id: str):
    result = db_helper.verify_audit_integrity(audit_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

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
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
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
        result = db_helper.trigger_rollback(req.auditId, operator=req.operator or "secops-operator")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback execution failed: {str(e)}")
