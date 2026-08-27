import os
import datetime
import time
import json
from typing import List, Optional, Callable
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from .providers.aws_adapter import AWSAdapter

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

app = FastAPI(title="Cloud Adapter Microservice API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize providers
aws_provider = AWSAdapter()

# MongoDB Client helper
class CloudDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.mock_db = {
            "cloud_assets": [],
            "cloud_metrics": [],
            "cloud_security_findings": [],
            "cloud_monitoring_target": [],
            "cloud_security_history": []
        }
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI env var is not set")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
            self.db = self.client.devsecops_db
            self.client.admin.command('ping')
            self.is_mock = False
            print("Connected to MongoDB for cloud adapter successfully.")
        except Exception:
            self.is_mock = True
            print("MongoDB unavailable for cloud adapter. Falling back to Mock Database.")

    def save_assets(self, assets: List[dict]):
        if self.is_mock:
            self.mock_db["cloud_assets"] = assets
            return
        try:
            self.db.cloud_assets.delete_many({})
            if assets:
                import copy
                self.db.cloud_assets.insert_many(copy.deepcopy(assets))
        except Exception as e:
            print(f"MongoDB write failed for cloud_assets: {str(e)}")

    def get_assets(self) -> List[dict]:
        if self.is_mock:
            return self.mock_db["cloud_assets"]
        try:
            cursor = self.db.cloud_assets.find({}, {"_id": 0})
            return list(cursor)
        except Exception:
            return self.mock_db["cloud_assets"]

    def save_metric(self, metric_doc: dict):
        if self.is_mock:
            self.mock_db["cloud_metrics"].append(metric_doc)
            return
        self.db.cloud_metrics.insert_one(metric_doc)

    def save_security_findings(self, findings: List[dict]):
        if self.is_mock:
            self.mock_db["cloud_security_findings"] = findings
            return
        # Clean collection first to represent current live findings only
        try:
            self.db.cloud_security_findings.delete_many({})
            if findings:
                import copy
                self.db.cloud_security_findings.insert_many(copy.deepcopy(findings))
        except Exception as e:
            print(f"MongoDB findings save failed: {str(e)}")

    def save_security_history(self, record: dict):
        if self.is_mock:
            self.mock_db["cloud_security_history"].append(record)
            self.mock_db["cloud_security_history"] = self.mock_db["cloud_security_history"][-50:]
            return
        try:
            import copy
            self.db.cloud_security_history.insert_one(copy.deepcopy(record))
        except Exception as e:
            print(f"MongoDB write failed for security history: {str(e)}")

    def get_security_history(self, limit=50) -> List[dict]:
        if self.is_mock:
            return sorted(self.mock_db["cloud_security_history"], key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        try:
            cursor = self.db.cloud_security_history.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception:
            return sorted(self.mock_db["cloud_security_history"], key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

    def get_security_findings(self) -> List[dict]:
        if self.is_mock:
            return self.mock_db["cloud_security_findings"]
        try:
            cursor = self.db.cloud_security_findings.find({}, {"_id": 0})
            return list(cursor)
        except Exception:
            return self.mock_db["cloud_security_findings"]

    def register_target(self, instance_id: str):
        doc = {"active": True, "instanceId": instance_id, "timestamp": datetime.datetime.utcnow().isoformat()}
        if self.is_mock:
            self.mock_db["cloud_monitoring_target"] = [doc]
            return
        self.db.cloud_monitoring_target.update_one(
            {"active": True},
            {"$set": doc},
            upsert=True
        )

    def get_registered_target(self) -> Optional[str]:
        if self.is_mock:
            targets = self.mock_db["cloud_monitoring_target"]
            return targets[0]["instanceId"] if targets else None
        try:
            target = self.db.cloud_monitoring_target.find_one({"active": True})
            return target["instanceId"] if target else None
        except Exception:
            return None

db_helper = CloudDatabase()

class RegisterRequest(BaseModel):
    instanceId: str

@app.get("/health")
def health():
    return {"status": "OK", "service": "Cloud Adapter Layer"}

@app.get("/cloud/providers")
def get_providers():
    return {
        "status": "success",
        "providers": [
            {"name": "aws", "supported": True, "adapter": "AWSAdapter"},
            {"name": "azure", "supported": False, "adapter": "AzureAdapter"},
            {"name": "gcp", "supported": False, "adapter": "GCPAdapter"}
        ]
    }

def process_and_save_findings_and_history(assets):
    db_helper.save_assets(assets)
    all_findings = []
    for asset in assets:
        assessment = asset.get("securityAssessment", {})
        inst_id = asset.get("instanceId")
        findings = assessment.get("findings", [])
        all_findings.extend(findings)
        
        if assessment.get("overallScore") is not None:
            crit_count = sum(1 for f in findings if f.get("severity") == "Critical")
            high_count = sum(1 for f in findings if f.get("severity") == "High")
            med_count = sum(1 for f in findings if f.get("severity") == "Medium")
            low_count = sum(1 for f in findings if f.get("severity") == "Low")
            
            history_doc = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "instanceId": inst_id,
                "securityScore": assessment.get("overallScore"),
                "ursContribution": 100 - assessment.get("overallScore"),
                "critical": crit_count,
                "high": high_count,
                "medium": med_count,
                "low": low_count,
                "findings": findings
            }
            db_helper.save_security_history(history_doc)
            
    if all_findings:
        db_helper.save_security_findings(all_findings)

@app.get("/cloud/assets")
def get_assets():
    try:
        assets = aws_provider.discover_assets()
        process_and_save_findings_and_history(assets)
        for asset in assets:
            asset.pop("_id", None)
        return {
            "status": "success",
            "data": assets,
            "instances": assets,
            "count": len(assets)
        }
    except Exception as e:
        print(f"Exception in get_assets: {str(e)}")
        return {
            "status": "success",
            "data": [],
            "instances": [],
            "count": 0
        }

@app.get("/cloud/aws/discover")
def discover_aws():
    try:
        assets = aws_provider.discover_assets()
        process_and_save_findings_and_history(assets)
        for asset in assets:
            asset.pop("_id", None)
        return {
            "status": "success",
            "data": assets,
            "instances": assets,
            "count": len(assets)
        }
    except Exception as e:
        print(f"Exception in discover_aws: {str(e)}")
        return {
            "status": "success",
            "data": [],
            "instances": [],
            "count": 0
        }

@app.get("/cloud/security/history")
def get_security_history(limit: int = 50):
    try:
        records = db_helper.get_security_history(limit)
        return {"status": "success", "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch security history: {str(e)}")

@app.get("/cloud/aws/metrics")
def get_aws_metrics(instanceId: Optional[str] = None):
    try:
        target_id = instanceId or db_helper.get_registered_target()
        
        if not target_id:
            assets = db_helper.get_assets()
            if not assets:
                assets = aws_provider.discover_assets()
                db_helper.save_assets(assets)
            if assets:
                target_id = assets[0]["instanceId"]
                
        if not target_id:
            raise HTTPException(status_code=404, detail="No AWS EC2 instance found or registered for metrics.")
            
        metrics = aws_provider.get_metrics(target_id)
        
        metric_doc = {
            "instanceId": target_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "metrics": metrics
        }
        db_helper.save_metric(metric_doc)
        
        return {
            "status": "success",
            "instanceId": target_id,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@app.get("/cloud/aws/metrics/{instanceId}")
def get_cloudwatch_metrics_for_instance(instanceId: str):
    try:
        cw_telemetry = aws_provider.get_cloudwatch_metrics(instanceId)
        full_metrics = aws_provider.get_metrics(instanceId)
        
        metric_doc = {
            "instanceId": instanceId,
            "timestamp": cw_telemetry["timestamp"],
            "cpu_usage": cw_telemetry["cpu_usage"],
            "network_in": cw_telemetry["network_in"],
            "network_out": cw_telemetry["network_out"],
            "disk_read_ops": cw_telemetry["disk_read_ops"],
            "disk_write_ops": cw_telemetry["disk_write_ops"],
            "status_failed": cw_telemetry["status_failed"],
            "provider": cw_telemetry["provider"],
            "region": cw_telemetry["region"],
            "mode": cw_telemetry["mode"],
            "metrics": full_metrics
        }
        db_helper.save_metric(metric_doc)
        
        return {
            "status": "success",
            "mode": cw_telemetry["mode"],
            "data": cw_telemetry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CloudWatch metrics collection failed: {str(e)}")

@app.get("/cloud/aws/live")
def get_aws_live_cloudwatch_telemetry():
    try:
        assets = aws_provider.discover_assets()
        db_helper.save_assets(assets)
        
        results = []
        overall_mode = "LIVE"
        
        for inst in assets:
            inst_id = inst["instanceId"]
            cw_metrics = aws_provider.get_cloudwatch_metrics(inst_id)
            if cw_metrics.get("mode") == "SIMULATION MODE":
                overall_mode = "SIMULATION MODE"
                
            full_metrics = aws_provider.get_metrics(inst_id)
            
            metric_doc = {
                "instanceId": inst_id,
                "timestamp": cw_metrics["timestamp"],
                "cpu_usage": cw_metrics["cpu_usage"],
                "network_in": cw_metrics["network_in"],
                "network_out": cw_metrics["network_out"],
                "disk_read_ops": cw_metrics["disk_read_ops"],
                "disk_write_ops": cw_metrics["disk_write_ops"],
                "status_failed": cw_metrics["status_failed"],
                "provider": cw_metrics["provider"],
                "region": cw_metrics["region"],
                "mode": cw_metrics["mode"],
                "metrics": full_metrics
            }
            db_helper.save_metric(metric_doc)
            
            results.append({
                "instance": inst,
                "metrics": cw_metrics,
                "full_metrics": full_metrics
            })
            
        return {
            "status": "success",
            "mode": overall_mode,
            "instances": results
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch live CloudWatch telemetry: {str(e)}")

@app.get("/cloud/security-posture")
def get_security_posture(instanceId: Optional[str] = None):
    try:
        target_id = instanceId
        findings = []
        
        if target_id:
            findings = aws_provider.assess_security_posture(target_id)
        else:
            assets = db_helper.get_assets()
            if not assets:
                assets = aws_provider.discover_assets()
                db_helper.save_assets(assets)
            for asset in assets:
                asset_findings = aws_provider.assess_security_posture(asset["instanceId"])
                findings.extend(asset_findings)
                
        db_helper.save_security_findings(findings)
        return {"status": "success", "data": findings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security posture assessment failed: {str(e)}")

@app.post("/cloud/aws/register")
def register_aws_instance(req: RegisterRequest):
    try:
        db_helper.register_target(req.instanceId)
        
        # Capture initial metrics run to seed telemetry pipeline if available
        try:
            metrics = aws_provider.get_metrics(req.instanceId)
            metric_doc = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "instanceId": req.instanceId,
                "metrics": metrics
            }
            db_helper.save_metric(metric_doc)
        except Exception as err:
            print(f"Metrics capture warning during instance registration: {str(err)}")
        
        return {"status": "success", "message": f"Successfully registered AWS instance {req.instanceId} for active pipeline telemetry."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
