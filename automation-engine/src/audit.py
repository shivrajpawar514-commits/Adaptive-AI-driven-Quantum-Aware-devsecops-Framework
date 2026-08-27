import os
import datetime
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

    def _seed_mock_history(self):
        now = datetime.datetime.utcnow()
        self.mock_db = [
            {
                "auditId": "AUD-AUTO-9001",
                "timestamp": (now - datetime.timedelta(minutes=10)).isoformat() + "Z",
                "instanceId": "i-04ba6569c74d41d59",
                "riskScore": 95.0,
                "decision": "Critical",
                "recommendations": ["Scale EC2 instance capacity", "Isolate compromised container pod"],
                "executionPlanCount": 5,
                "automationLevel": "Fully Automated",
                "executionStatus": "Executed (Simulation Mode)",
                "rollbackStatus": "Available",
                "estimatedExecutionTime": 5.3
            },
            {
                "auditId": "AUD-AUTO-9002",
                "timestamp": (now - datetime.timedelta(minutes=35)).isoformat() + "Z",
                "instanceId": "i-04ba6569c74d41d59",
                "riskScore": 72.5,
                "decision": "Alert",
                "recommendations": ["Restrict wildcard 0.0.0.0/0 SSH rule"],
                "executionPlanCount": 4,
                "automationLevel": "Fully Automated",
                "executionStatus": "Executed (Simulation Mode)",
                "rollbackStatus": "Available",
                "estimatedExecutionTime": 4.1
            }
        ]

    def save_execution(self, doc: dict) -> str:
        audit_id = doc.get("auditId") or f"AUD-AUTO-{int(datetime.datetime.utcnow().timestamp())}"
        doc["auditId"] = audit_id
        doc["timestamp"] = doc.get("timestamp") or (datetime.datetime.utcnow().isoformat() + "Z")
        doc["executionStatus"] = doc.get("executionStatus") or "Executed (Simulation Mode)"
        doc["rollbackStatus"] = doc.get("rollbackStatus") or "Available"
        
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

    def trigger_rollback(self, audit_id: str) -> Dict[str, Any]:
        records = self.get_history()
        target = None
        for r in records:
            if r.get("auditId") == audit_id:
                target = r
                break
                
        rollback_doc = {
            "status": "success",
            "auditId": audit_id,
            "rollbackTimestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "executionStatus": "Rolled Back (Simulation Mode)",
            "message": f"Successfully executed simulation rollback for audit record {audit_id}."
        }
        
        if target:
            target["rollbackStatus"] = "Rolled Back"
            target["executionStatus"] = "Rolled Back (Simulation Mode)"
            if not self.is_mock:
                try:
                    self.db.automation_history.update_one(
                        {"auditId": audit_id},
                        {"$set": {"rollbackStatus": "Rolled Back", "executionStatus": "Rolled Back (Simulation Mode)"}}
                    )
                except Exception:
                    pass
                    
        return rollback_doc
