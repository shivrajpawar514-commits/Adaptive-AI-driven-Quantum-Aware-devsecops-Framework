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
from pymongo import MongoClient

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

app = FastAPI(title="Digital Twin Architecture Graph API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection helper
class TwinDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.mock_db = {
            "digital_twin_assets": [],
            "digital_twin_relationships": [],
            "digital_twin_history": []
        }
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI env var is not set")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
            self.db = self.client.devsecops_db
            self.client.admin.command('ping')
            self.is_mock = False
            print("Connected to MongoDB for digital twin successfully.")
        except Exception:
            self.is_mock = True
            print("MongoDB unavailable for digital twin. Falling back to Mock Database.")
            self._seed_mock_twin()

    def _seed_mock_twin(self):
        # Seed mock topology assets and relationships representing cloud layers
        now = datetime.datetime.utcnow().isoformat()
        
        # 1. Assets
        self.mock_db["digital_twin_assets"] = [
            {
                "assetId": "i-09f1a238b7e456cde",
                "instanceName": "production-web-node-01",
                "provider": "aws",
                "region": "us-east-1",
                "instanceType": "t3.medium",
                "riskScore": 61.25,
                "adaptiveURS": 61.25,
                "staticURS": 51.55,
                "quantumReadiness": 15,
                "topContributor": "CPU",
                "recommendedPolicies": ["REC-CRYPTO-001", "REC-K8S-001", "REC-DOCKER-001"],
                "currentTelemetry": {
                    "cpu_usage": 85.0,
                    "memory_usage": 70.0,
                    "disk_usage": 40.0,
                    "network_usage": 500000.0
                },
                "historicalRiskTrend": [50.0, 52.0, 61.25],
                "attackHistory": [
                    {
                        "timestamp": now,
                        "attack": "Crypto Mining",
                        "severity": "Critical",
                        "detected": True
                    }
                ],
                "currentStatus": "Running"
            },
            {
                "assetId": "i-0a8b9c12d34e56f78",
                "instanceName": "dev-build-node",
                "provider": "aws",
                "region": "us-east-1",
                "instanceType": "t3.small",
                "riskScore": 15.5,
                "adaptiveURS": 15.5,
                "staticURS": 15.5,
                "quantumReadiness": 95,
                "topContributor": "N/A",
                "recommendedPolicies": ["REC-MONITOR-100", "REC-LOG-100"],
                "currentTelemetry": {
                    "cpu_usage": 15.0,
                    "memory_usage": 30.0,
                    "disk_usage": 30.0,
                    "network_usage": 20000.0
                },
                "historicalRiskTrend": [15.0, 15.5],
                "attackHistory": [],
                "currentStatus": "Running"
            }
        ]
        
        # 2. Relationships
        self.mock_db["digital_twin_relationships"] = [
            {"source": "aws", "target": "us-east-1", "relationType": "Contains", "label": "contains"},
            {"source": "us-east-1", "target": "vpc-12345", "relationType": "Contains", "label": "contains"},
            {"source": "vpc-12345", "target": "subnet-5678a", "relationType": "Contains", "label": "contains"},
            {"source": "subnet-5678a", "target": "sg-prod-web", "relationType": "Restricts", "label": "restricts"},
            {"source": "sg-prod-web", "target": "i-09f1a238b7e456cde", "relationType": "Protects", "label": "protects"},
            {"source": "subnet-5678a", "target": "i-0a8b9c12d34e56f78", "relationType": "Protects", "label": "protects"},
            {"source": "i-09f1a238b7e456cde", "target": "container-prod-web", "relationType": "Hosts", "label": "hosts"},
            {"source": "container-prod-web", "target": "core-api-app", "relationType": "Runs", "label": "runs"},
            {"source": "core-api-app", "target": "urs-risk-engine", "relationType": "Evaluates", "label": "evaluates"},
            {"source": "urs-risk-engine", "target": "ipre-policy-engine", "relationType": "Triggers", "label": "triggers"},
            {"source": "urs-risk-engine", "target": "qrae-quantum-engine", "relationType": "Checks", "label": "checks"}
        ]

    def save_assets(self, assets: List[dict]):
        if self.is_mock:
            self.mock_db["digital_twin_assets"] = assets
            return
        for asset in assets:
            self.db.digital_twin_assets.update_one(
                {"assetId": asset["assetId"]},
                {"$set": asset},
                upsert=True
            )

    def save_relationships(self, relationships: List[dict]):
        if self.is_mock:
            self.mock_db["digital_twin_relationships"] = relationships
            return
        # Overwrite all relationships on sync to keep clean topology
        self.db.digital_twin_relationships.delete_many({})
        if relationships:
            self.db.digital_twin_relationships.insert_many(relationships)

    def log_history(self, history_doc: dict):
        if self.is_mock:
            self.mock_db["digital_twin_history"].append(history_doc)
            return
        self.db.digital_twin_history.insert_one(history_doc)

    def get_assets(self) -> List[dict]:
        if self.is_mock:
            return self.mock_db["digital_twin_assets"]
        try:
            cursor = self.db.digital_twin_assets.find({}, {"_id": 0})
            assets = list(cursor)
            if not assets:
                self._seed_mock_twin()
                for doc in self.mock_db["digital_twin_assets"]:
                    self.db.digital_twin_assets.insert_one(doc)
                return self.mock_db["digital_twin_assets"]
            return assets
        except Exception:
            return self.mock_db["digital_twin_assets"]

    def get_relationships(self) -> List[dict]:
        if self.is_mock:
            return self.mock_db["digital_twin_relationships"]
        try:
            cursor = self.db.digital_twin_relationships.find({}, {"_id": 0})
            rels = list(cursor)
            if not rels:
                self._seed_mock_twin()
                self.db.digital_twin_relationships.insert_many(self.mock_db["digital_twin_relationships"])
                return self.mock_db["digital_twin_relationships"]
            return rels
        except Exception:
            return self.mock_db["digital_twin_relationships"]

    def get_history(self, asset_id: str) -> List[dict]:
        if self.is_mock:
            return [h for h in self.mock_db["digital_twin_history"] if h.get("assetId") == asset_id]
        try:
            cursor = self.db.digital_twin_history.find({"assetId": asset_id}, {"_id": 0}).sort("timestamp", -1)
            return list(cursor)
        except Exception:
            return []

db_helper = TwinDatabase()

@app.get("/health")
def health():
    return {"status": "OK", "service": "Cloud Digital Twin"}

@app.post("/digital-twin/sync")
def sync_twin():
    try:
        # 1. Fetch discovered cloud inventory assets
        if db_helper.is_mock:
            # Under Mock, just trigger seeding or updates
            db_helper._seed_mock_twin()
            return {"status": "success", "message": "Successfully synchronized cloud digital twin in Mock Mode."}
            
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri)
        db = client.devsecops_db
        
        # Read EC2 nodes
        ec2_assets = list(db.cloud_assets.find({}, {"_id": 0}))
        
        # 2. Build assets topology structures
        twin_assets = []
        relationships = [
            {"source": "aws", "target": "us-east-1", "relationType": "Contains", "label": "contains"},
            {"source": "us-east-1", "target": "vpc-12345", "relationType": "Contains", "label": "contains"},
            {"source": "vpc-12345", "target": "subnet-5678a", "relationType": "Contains", "label": "contains"},
            {"source": "subnet-5678a", "target": "sg-prod-web", "relationType": "Restricts", "label": "restricts"},
            {"source": "core-api-app", "target": "urs-risk-engine", "relationType": "Evaluates", "label": "evaluates"},
            {"source": "urs-risk-engine", "target": "ipre-policy-engine", "relationType": "Triggers", "label": "triggers"},
            {"source": "urs-risk-engine", "target": "qrae-quantum-engine", "relationType": "Checks", "label": "checks"}
        ]
        
        # Gathers evaluations, recommendations, simulations
        evaluations = list(db.evaluations.find({}, {"_id": 0}).sort("timestamp", -1))
        simulations = list(db.simulations.find({}, {"_id": 0}).sort("timestamp", -1))
        
        for ec2 in ec2_assets:
            inst_id = ec2["instanceId"]
            name = ec2.get("instanceName", inst_id)
            
            # Find URS risk evaluations
            urs_score = 15.0 # baseline normal
            static_urs = 15.0
            top_contributor = "N/A"
            recs = []
            telemetry = {}
            history_trend = []
            attack_hist = []
            
            # Check latest evaluations matching this inst_id or global metrics
            if evaluations:
                latest = evaluations[0]
                urs_score = latest.get("urs", urs_score)
                static_urs = latest.get("comparison", {}).get("staticURS", static_urs)
                top_contributor = latest.get("topContributor", top_contributor)
                recs = [r.get("recommendationId") for r in latest.get("recommendations", [])]
                telemetry = latest.get("telemetry", {})
                
                # Risk trend across last 5 evaluations
                history_trend = [round(e.get("urs", 15.0), 2) for e in reversed(evaluations[:5])]
                
            # Check simulations
            for sim in simulations:
                if sim.get("results", {}).get("attackName") != "Normal Workload":
                    attack_hist.append({
                        "timestamp": sim.get("timestamp"),
                        "attack": sim.get("attackProfile"),
                        "severity": sim.get("results", {}).get("decision", "Alert"),
                        "detected": sim.get("results", {}).get("detected", True)
                    })
                    
            # Compute quantum posture average
            qr_score = 95 # default excellent
            if ec2.get("securityGroups"):
                # Link SG -> Instance relationships
                for sg in ec2.get("securityGroups"):
                    relationships.append({"source": "sg-prod-web", "target": inst_id, "relationType": "Protects", "label": "protects"})
                    
            relationships.append({"source": "subnet-5678a", "target": inst_id, "relationType": "Contains", "label": "contains"})
            relationships.append({"source": inst_id, "target": "container-prod-web", "relationType": "Hosts", "label": "hosts"})
            relationships.append({"source": "container-prod-web", "target": "core-api-app", "relationType": "Runs", "label": "runs"})
            
            # Build twin object
            twin_obj = {
                "assetId": inst_id,
                "instanceName": name,
                "provider": "aws",
                "region": ec2.get("region", "us-east-1"),
                "instanceType": ec2.get("instanceType", "t3.medium"),
                "riskScore": round(urs_score, 2),
                "adaptiveURS": round(urs_score, 2),
                "staticURS": round(static_urs, 2),
                "quantumReadiness": qr_score,
                "topContributor": top_contributor,
                "recommendedPolicies": recs,
                "currentTelemetry": telemetry,
                "historicalRiskTrend": history_trend,
                "attackHistory": attack_hist,
                "currentStatus": "Running" if urs_score < 80 else "Compromised"
            }
            
            twin_assets.append(twin_obj)
            db_helper.save_assets([twin_obj])
            
            # Save history document log
            db_helper.log_history({
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "assetId": inst_id,
                "riskScore": urs_score,
                "status": twin_obj["currentStatus"]
            })
            
        db_helper.save_relationships(relationships)
        return {"status": "success", "message": "Successfully synchronized cloud digital twin graphs."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.get("/digital-twin/assets")
def get_assets():
    assets = db_helper.get_assets()
    return {"status": "success", "data": assets}

@app.get("/digital-twin/asset/{id}")
def get_asset(id: str):
    assets = db_helper.get_assets()
    for a in assets:
        if a["assetId"] == id:
            return {"status": "success", "data": a}
    raise HTTPException(status_code=404, detail=f"Asset ID {id} not found in Digital Twin.")

@app.get("/digital-twin/history/{id}")
def get_history(id: str):
    history = db_helper.get_history(id)
    return {"status": "success", "data": history}

@app.get("/digital-twin/topology")
def get_topology():
    # Return structured layer representations
    assets = db_helper.get_assets()
    rels = db_helper.get_relationships()
    return {
        "status": "success",
        "layers": {
            "provider": "aws",
            "region": "us-east-1",
            "vpc": "vpc-12345",
            "subnet": "subnet-5678a",
            "securityGroups": ["sg-prod-web"],
            "instances": [a.get("assetId") for a in assets]
        },
        "relationships": rels
    }

@app.get("/digital-twin/graph")
def get_graph():
    assets = db_helper.get_assets()
    rels = db_helper.get_relationships()
    
    # Compile visual graph JSON (Phase 8)
    nodes = [
        {"id": "aws", "label": "AWS Provider", "type": "Provider", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "cloud", "group": "Infrastructure"},
        {"id": "us-east-1", "label": "Region: us-east-1", "type": "Region", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "map", "group": "Infrastructure"},
        {"id": "vpc-12345", "label": "VPC: vpc-12345", "type": "VPC", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "shield", "group": "Network"},
        {"id": "subnet-5678a", "label": "Subnet: subnet-5678a", "type": "Subnet", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "network", "group": "Network"},
        {"id": "sg-prod-web", "label": "Security Group: sg-prod-web", "type": "Security Group", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "lock", "group": "Network"},
        {"id": "container-prod-web", "label": "Docker Container", "type": "Container", "status": "Running", "risk": "Low", "riskColor": "green", "icon": "docker", "group": "Runtime"},
        {"id": "core-api-app", "label": "Core API App", "type": "Application", "status": "Running", "risk": "Low", "riskColor": "green", "icon": "code", "group": "Application"},
        {"id": "urs-risk-engine", "label": "URS Risk Engine", "type": "Security", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "shield-alert", "group": "Security"},
        {"id": "ipre-policy-engine", "label": "IPRE Policy Controller", "type": "Security", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "cog", "group": "Security"},
        {"id": "qrae-quantum-engine", "label": "QRAE Posture Engine", "type": "Security", "status": "Active", "risk": "Low", "riskColor": "green", "icon": "key", "group": "Security"}
    ]
    
    for a in assets:
        risk = a.get("riskScore", 0.0)
        risk_color = "green" if risk < 30 else ("yellow" if risk < 60 else ("orange" if risk < 80 else "red"))
        status = a.get("currentStatus", "Running")
        
        nodes.append({
            "id": a["assetId"],
            "label": a.get("instanceName", a["assetId"]),
            "type": "EC2 Instance",
            "status": status,
            "risk": f"{risk}% URS",
            "riskColor": risk_color,
            "icon": "server",
            "group": "Compute"
        })
        
    edges = []
    for r in rels:
        edges.append({
            "source": r["source"],
            "target": r["target"],
            "relationType": r["relationType"],
            "label": r.get("label", r["relationType"].lower())
        })
        
    return {
        "status": "success",
        "data": {
            "nodes": nodes,
            "edges": edges
        }
    }
