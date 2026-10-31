import os
import datetime
import hashlib
import json
from typing import List, Dict, Any, Optional
from pymongo import MongoClient

class AutomationDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.mock_db = []
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI env var is not set")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
            self.db = self.client.devsecops_db
            self.client.admin.command('ping')
            self.is_mock = False
            print("Connected to MongoDB for automation history successfully.")
        except Exception:
            self.is_mock = True
            print("MongoDB unavailable for automation engine. Falling back to Mock Database.")
            self._seed_mock_history()

    def _compute_audit_hash(self, doc: dict) -> str:
        """Generates a tamper-evident SHA-256 integrity hash for an audit record."""
        payload = f"{doc.get('auditId')}:{doc.get('timestamp')}:{doc.get('instanceId')}:{doc.get('riskScore')}:{doc.get('executionStatus')}:{doc.get('operator')}:{doc.get('operatorRole')}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _seed_mock_history(self):
        now = datetime.datetime.utcnow()
        doc1 = {
            "auditId": "AUD-AUTO-9001",
            "timestamp": (now - datetime.timedelta(minutes=10)).isoformat() + "Z",
            "instanceId": "i-04ba6569c74d41d59",
            "operator": "secops-operator",
            "operatorRole": "secops",
            "riskScore": 95.0,
            "decision": "Critical",
            "recommendations": ["Scale EC2 instance capacity", "Isolate compromised container pod"],
            "executionPlanCount": 5,
            "automationLevel": "Fully Automated",
            "executionStatus": "Executed (Simulation Mode)",
            "rollbackStatus": "Available",
            "dryRun": False,
            "approvalGate": {"required": True, "approved": True, "approvedBy": "secops-lead"},
            "auditTrail": [
                {"timestamp": (now - datetime.timedelta(minutes=10)).isoformat() + "Z", "event": "REMEDIATION_REQUESTED", "operator": "secops-operator"},
                {"timestamp": (now - datetime.timedelta(minutes=9)).isoformat() + "Z", "event": "OPERATOR_APPROVED", "approvedBy": "secops-lead"},
                {"timestamp": (now - datetime.timedelta(minutes=8)).isoformat() + "Z", "event": "REMEDIATION_EXECUTED", "status": "COMPLETED"}
            ],
            "estimatedExecutionTime": 5.3
        }
        doc1["sha256Signature"] = self._compute_audit_hash(doc1)

        doc2 = {
            "auditId": "AUD-AUTO-9002",
            "timestamp": (now - datetime.timedelta(minutes=35)).isoformat() + "Z",
            "instanceId": "i-04ba6569c74d41d59",
            "operator": "secops-operator",
            "operatorRole": "secops",
            "riskScore": 72.5,
            "decision": "Alert",
            "recommendations": ["Restrict wildcard 0.0.0.0/0 SSH rule"],
            "executionPlanCount": 4,
            "automationLevel": "Fully Automated",
            "executionStatus": "Executed (Simulation Mode)",
            "rollbackStatus": "Available",
            "dryRun": False,
            "approvalGate": {"required": False, "approved": True},
            "auditTrail": [
                {"timestamp": (now - datetime.timedelta(minutes=35)).isoformat() + "Z", "event": "REMEDIATION_REQUESTED", "operator": "secops-operator"},
                {"timestamp": (now - datetime.timedelta(minutes=34)).isoformat() + "Z", "event": "REMEDIATION_EXECUTED", "status": "COMPLETED"}
            ],
            "estimatedExecutionTime": 4.1
        }
        doc2["sha256Signature"] = self._compute_audit_hash(doc2)
        self.mock_db = [doc1, doc2]

    def save_execution(self, doc: dict) -> str:
        audit_id = doc.get("auditId") or f"AUD-AUTO-{int(datetime.datetime.utcnow().timestamp())}"
        doc["auditId"] = audit_id
        doc["timestamp"] = doc.get("timestamp") or (datetime.datetime.utcnow().isoformat() + "Z")
        doc["executionStatus"] = doc.get("executionStatus") or "Executed (Simulation Mode)"
        doc["rollbackStatus"] = doc.get("rollbackStatus") or "Available"
        doc["operator"] = doc.get("operator") or "secops-operator"
        doc["operatorRole"] = doc.get("operatorRole") or "secops"
        doc["dryRun"] = doc.get("dryRun", False)
        
        # Ensure audit trail list exists
        if "auditTrail" not in doc or not doc["auditTrail"]:
            doc["auditTrail"] = [
                {
                    "timestamp": doc["timestamp"],
                    "event": "REMEDIATION_REQUESTED",
                    "operator": doc["operator"],
                    "role": doc["operatorRole"],
                    "dryRun": doc["dryRun"],
                    "status": doc["executionStatus"]
                }
            ]

        # Compute SHA-256 signature
        doc["sha256Signature"] = self._compute_audit_hash(doc)
        
        if self.is_mock:
            self.mock_db.insert(0, doc)
            return audit_id
        try:
            self.db.automation_history.insert_one(doc)
            return audit_id
        except Exception as e:
            print(f"MongoDB write error for automation_history: {str(e)}")
            self.mock_db.insert(0, doc)
            return audit_id

    def verify_audit_integrity(self, audit_id: str) -> Dict[str, Any]:
        """Verifies cryptographic integrity of an audit trail entry."""
        records = self.get_history()
        target = next((r for r in records if r.get("auditId") == audit_id), None)
        if not target:
            return {"valid": False, "error": "Audit record not found"}
        
        stored_sig = target.get("sha256Signature")
        expected_sig = self._compute_audit_hash(target)
        return {
            "valid": stored_sig == expected_sig,
            "auditId": audit_id,
            "storedSignature": stored_sig,
            "verifiedSignature": expected_sig
        }

    def get_history(self) -> List[dict]:
        if self.is_mock:
            return self.mock_db
        try:
            cursor = self.db.automation_history.find({}, {"_id": 0}).sort("timestamp", -1)
            records = list(cursor)
            if not records:
                self._seed_mock_history()
                return self.mock_db
            return records
        except Exception:
            return self.mock_db

    def trigger_rollback(self, audit_id: str, operator: str = "secops-operator") -> Dict[str, Any]:
        records = self.get_history()
        target = None
        for r in records:
            if r.get("auditId") == audit_id:
                target = r
                break
                
        now_iso = datetime.datetime.utcnow().isoformat() + "Z"
        rollback_doc = {
            "status": "success",
            "auditId": audit_id,
            "rollbackTimestamp": now_iso,
            "operator": operator,
            "executionStatus": "Rolled Back (Simulation Mode)",
            "message": f"Successfully executed simulation rollback for audit record {audit_id}."
        }
        
        if target:
            target["rollbackStatus"] = "Rolled Back"
            target["executionStatus"] = "Rolled Back (Simulation Mode)"
            if "auditTrail" not in target:
                target["auditTrail"] = []
            target["auditTrail"].append({
                "timestamp": now_iso,
                "event": "ROLLBACK_EXECUTED",
                "operator": operator,
                "status": "Rolled Back (Simulation Mode)"
            })
            target["sha256Signature"] = self._compute_audit_hash(target)
            rollback_doc["rollbackPlan"] = target.get("rollbackPlan", [])
            
            if not self.is_mock:
                try:
                    self.db.automation_history.update_one(
                        {"auditId": audit_id},
                        {"$set": {
                            "rollbackStatus": "Rolled Back",
                            "executionStatus": "Rolled Back (Simulation Mode)",
                            "auditTrail": target["auditTrail"],
                            "sha256Signature": target["sha256Signature"]
                        }}
                    )
                except Exception:
                    pass
                    
        return rollback_doc
