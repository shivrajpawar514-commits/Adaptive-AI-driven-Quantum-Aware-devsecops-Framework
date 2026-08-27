from __future__ import annotations

import datetime
import uuid
import httpx
from .service_config import CLOUD_ADAPTER_URL, RISK_ENGINE_URL, DIGITAL_TWIN_URL, AI_ENGINE_URL
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class ExecutionSession:
    executionId: str = field(default_factory=lambda: str(uuid.uuid4()))
    playbookId: str = ""
    resourceId: str = ""
    status: str = "RECOMMENDED"
    operator: Optional[str] = None
    approvedAt: Optional[datetime.datetime] = None
    startedAt: Optional[datetime.datetime] = None
    completedAt: Optional[datetime.datetime] = None
    verificationResult: Optional[Dict[str, Any]] = None
    rollbackAvailable: bool = False
    rollbackExecuted: bool = False
    logs: List[str] = field(default_factory=list)
    ursBefore: float = 0.0
    ursAfter: Optional[float] = None
    riskReduction: Optional[float] = None
    cloudProvider: str = "aws"
    simulationMode: bool = False
    # Graph execution fields
    graph: List[Dict[str, Any]] = field(default_factory=list)
    currentStepIndex: int = -1
    totalSteps: int = 0
    progress: int = 0  # percent
    remainingTime: int = 0  # seconds
    auditTrail: List[Dict[str, Any]] = field(default_factory=list)
    awsApiCalls: List[Dict[str, Any]] = field(default_factory=list)

    def add_log(self, message: str, level: str = "INFO"):
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        entry = f"{timestamp} {level} {message}"
        self.logs.append(entry)

    def add_audit_event(self, event_type: str, details: Dict[str, Any]):
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        self.auditTrail.append({"timestamp": timestamp, "eventType": event_type, "details": details})

    def record_api_call(self, api_name: str, http_status: int, request_id: str, duration_ms: int, outcome: str):
        call = {
            "apiName": api_name,
            "httpStatus": http_status,
            "requestId": request_id,
            "durationMs": duration_ms,
            "outcome": outcome,
        }
        self.awsApiCalls.append(call)
        self.add_log(f"API CALL {api_name} status={http_status} requestId={request_id} duration={duration_ms}ms outcome={outcome}")

    def start(self):
        self.startedAt = datetime.datetime.utcnow()
        self.status = "EXECUTING_GRAPH"
        self.add_audit_event("ExecutionStarted", {"executionId": self.executionId})

    def approve(self, operator: str):
        self.operator = operator
        self.approvedAt = datetime.datetime.utcnow()
        self.status = "APPROVED"
        self.add_audit_event("OperatorApproved", {"operator": operator})

    def advance_step(self):
        if self.currentStepIndex + 1 < len(self.graph):
            self.currentStepIndex += 1
            step = self.graph[self.currentStepIndex]
            self.add_log(f"Starting playbook step {self.currentStepIndex + 1}/{len(self.graph)}: {step.get('playbookId')}")
            # Update progress based on estimated times
            elapsed = (datetime.datetime.utcnow() - self.startedAt).total_seconds() if self.startedAt else 0
            total_est = sum(s.get('estimatedExecutionTime', 0) for s in self.graph)
            self.progress = int((elapsed / total_est) * 100) if total_est > 0 else 0
            self.remainingTime = max(int(total_est - elapsed), 0)
        else:
            self.complete_success()

    def complete_success(self):
        self.completedAt = datetime.datetime.utcnow()
        self.status = "COMPLETED"
        self.add_audit_event("ExecutionCompleted", {"success": True})
        self.post_execution_sync()

        # calculate URS reduction if applicable
        if self.ursAfter is not None and self.ursBefore is not None:
            self.riskReduction = self.ursBefore - self.ursAfter

    def fail(self, reason: str):
        self.completedAt = datetime.datetime.utcnow()
        self.status = "FAILED"
        self.add_audit_event("ExecutionFailed", {"reason": reason})
        self.add_log(f"Execution failed: {reason}", level="ERROR")

    def initiate_rollback(self, operator: str):
        if not self.rollbackAvailable:
            raise ValueError("Rollback not available for this session")
        self.operator = operator
        self.status = "ROLLBACK_EXECUTING"
        self.add_audit_event("RollbackStarted", {"operator": operator})

    def complete_rollback(self, success: bool):
        self.rollbackExecuted = True
        self.completedAt = datetime.datetime.utcnow()
        self.status = "ROLLED_BACK" if success else "FAILED"
        self.add_audit_event("RollbackCompleted", {"success": success})

    def post_execution_sync(self):
        """Orchestrate post-execution synchronization across services.
        Called after execution reaches COMPLETED status.
        Performs:
        1. Refresh cloud findings.
        2. Recalculate URS.
        3. Incremental Digital Twin update.
        4. Trigger AI analysis.
        5. Generate final report.
        Errors are logged without interrupting flow.
        """
        try:
            cloud_resp = httpx.get(f"{CLOUD_ADAPTER_URL}/cloud/aws/discover")
            self.add_log(f"Cloud findings refresh status: {cloud_resp.status_code}")
        except Exception as e:
            self.add_log(f"Cloud findings refresh failed: {e}", level="ERROR")
        try:
            risk_payload = {"executionId": self.executionId, "resourceId": self.resourceId}
            risk_resp = httpx.post(f"{RISK_ENGINE_URL}/risk/evaluate", json=risk_payload)
            if risk_resp.status_code == 200:
                urs_data = risk_resp.json()
                self.ursAfter = urs_data.get("urs", self.ursAfter)
                self.add_log(f"URS recalculated: {self.ursAfter}")
            else:
                self.add_log(f"URS recalculation failed with status {risk_resp.status_code}", level="ERROR")
        except Exception as e:
            self.add_log(f"URS recalculation error: {e}", level="ERROR")
        try:
            dt_payload = {"resourceId": self.resourceId, "status": "remediated"}
            dt_resp = httpx.patch(f"{DIGITAL_TWIN_URL}/digital-twin/assets/{self.resourceId}", json=dt_payload)
            self.add_log(f"Digital Twin update status: {dt_resp.status_code}")
        except Exception as e:
            self.add_log(f"Digital Twin update failed: {e}", level="ERROR")
        try:
            ai_payload = {"executionId": self.executionId, "resourceId": self.resourceId}
            ai_resp = httpx.post(f"{AI_ENGINE_URL}/ai/analyze", json=ai_payload)
            self.add_log(f"AI analysis trigger status: {ai_resp.status_code}")
        except Exception as e:
            self.add_log(f"AI analysis trigger error: {e}", level="ERROR")
        try:
            from .report_generator import generate_report
            report = generate_report(self)
            self.add_log("Final execution report generated.")
        except Exception as e:
            self.add_log(f"Report generation failed: {e}", level="ERROR")
        self.add_log("Post-execution synchronization completed.")
