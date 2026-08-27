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
from pydantic import BaseModel
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

app = FastAPI(title="Policy Recommendation Engine API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection helper
class RecommendationDatabase:
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
            print("Connected to MongoDB for recommendations successfully.")
        except Exception:
            self.is_mock = True
            print("MongoDB unavailable for recommendations. Falling back to Mock Database.")
            
    def insert_recommendation_run(self, doc):
        if self.is_mock:
            self.mock_db.append(doc)
            return True
        try:
            self.db.recommendations.insert_one(doc)
            return True
        except Exception as e:
            print(f"MongoDB write failed for recommendations: {str(e)}")
            self.mock_db.append(doc)
            return False

db_helper = RecommendationDatabase()

class PolicyRequest(BaseModel):
    urs: float
    decision: str
    topContributor: Optional[str] = "Unknown"
    anomaly_score: float
    reconstruction_error: float
    context: Optional[dict] = None
    quantumReadiness: Optional[dict] = None
    cryptography: Optional[list] = None
    attackProfile: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "OK", "service": "Intelligent Policy Recommendation Engine"}

@app.post("/policy/recommend")
def recommend_policy(req: PolicyRequest):
    try:
        inputs = req.model_dump()
        recs = evaluate_rules(inputs)
        
        # Log recommendation execution in MongoDB
        doc = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "inputs": inputs,
            "recommendations": recs
        }
        db_helper.insert_recommendation_run(doc)
        
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy generation failure: {str(e)}")

def evaluate_rules(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    recs = []
    
    urs = inputs.get("urs", 0.0)
    decision = inputs.get("decision", "Normal")
    top_contributor = inputs.get("topContributor", "")
    anomaly_score = inputs.get("anomaly_score", 0.0)
    reconstruction_error = inputs.get("reconstruction_error", 0.0)
    attack_profile = inputs.get("attackProfile", "")
    
    context = inputs.get("context") or {}
    context_profile = context.get("profile", "Standard")
    
    qr = inputs.get("quantumReadiness") or {}
    qr_risk = qr.get("overallQuantumRisk", "Low")
    
    # 1. CRYPTOGRAPHIC POSTURE RULES
    if qr_risk in ("Very High", "High"):
        recs.append({
            "recommendationId": "REC-CRYPTO-001",
            "title": "Migrate Legacy Cryptography to Post-Quantum Algorithms",
            "description": "Identify systems using legacy algorithms (such as RSA-2048) and upgrade them to quantum-safe alternatives (ML-KEM/Kyber hybrid TLS key exchange or ML-DSA signature schemes).",
            "category": "Cryptography",
            "priority": "High" if qr_risk == "High" else "Critical",
            "confidence": 0.95,
            "estimatedRiskReduction": 75.0,
            "automationSupported": False,
            "reasoning": f"Assets currently run legacy cryptography with {qr_risk} quantum risk. Upgrading to PQC secures authentication keys from Shor's algorithm."
        })
    elif qr_risk == "Medium":
        recs.append({
            "recommendationId": "REC-CRYPTO-002",
            "title": "Implement Hybrid Post-Quantum Key Exchange",
            "description": "Deploy hybrid key exchange mechanisms combining ECC P-256/384 with lattice-based algorithms in preparation for transition to full PQC.",
            "category": "Cryptography",
            "priority": "Medium",
            "confidence": 0.90,
            "estimatedRiskReduction": 40.0,
            "automationSupported": True,
            "reasoning": "Standard elliptic curve cryptosystems present medium quantum risk and require proactive transition policies."
        })

    # 2. RESOURCE THREAT RULES (CPU Spike / Crypto Mining)
    if attack_profile == "Crypto Mining" or (top_contributor == "CPU" and decision in ("Alert", "High Risk", "Critical")):
        recs.append({
            "recommendationId": "REC-K8S-001",
            "title": "Apply Kubernetes CPU Resource Quotas and Limits",
            "description": "Configure LimitRanges and resource quotas in the target namespace. Set container cpu limits to 1.0 core and memory to 2Gi to prevent runaway processing.",
            "category": "Kubernetes",
            "priority": "Critical" if decision == "Critical" else "High",
            "confidence": 0.95,
            "estimatedRiskReduction": 60.0,
            "automationSupported": True,
            "reasoning": f"Sustained CPU spike detected during {context_profile} context. Limiting CPU resources prevents cluster-wide denial of service."
        })
        recs.append({
            "recommendationId": "REC-DOCKER-001",
            "title": "Enforce Container CPU-Shares and Restrict Execution Limits",
            "description": "Add '--cpu-shares=512' and '--cpus=1.0' parameters to the container launch daemon to cap CPU access in multitenant resource sharing.",
            "category": "Docker",
            "priority": "High",
            "confidence": 0.92,
            "estimatedRiskReduction": 50.0,
            "automationSupported": True,
            "reasoning": "Limiting container CPU shares at the Docker daemon level isolates resource depletion threats to a container."
        })
        recs.append({
            "recommendationId": "REC-ANSIBLE-001",
            "title": "Trigger Automated Node Lockdown Playbook",
            "description": "Run the node quarantine Ansible playbook to isolate the compromised host, terminate unauthorized mining daemons, and dump memory forensics.",
            "category": "Ansible Playbooks",
            "priority": "High",
            "confidence": 0.88,
            "estimatedRiskReduction": 70.0,
            "automationSupported": True,
            "reasoning": "Automated playbook isolation provides rapid response, reducing containment window latency to seconds."
        })
        recs.append({
            "recommendationId": "REC-MONITOR-001",
            "title": "Elevate Prometheus Monitoring Scraping Resolution",
            "description": "Increase metrics scraping resolution from 30s to 5s for the affected node to capture high-frequency system telemetry for forensics.",
            "category": "Monitoring",
            "priority": "Medium",
            "confidence": 0.95,
            "estimatedRiskReduction": 10.0,
            "automationSupported": True,
            "reasoning": "High-resolution metrics are critical to identify crypto-mining spikes and trace execution parents."
        })

    # 3. MEMORY EXHAUSTION RULES (Memory Leak)
    if attack_profile == "Memory Leak" or (top_contributor == "Memory" and decision in ("Alert", "High Risk", "Critical")):
        recs.append({
            "recommendationId": "REC-K8S-002",
            "title": "Define Kubernetes Pod Memory Limits and Eviction Policies",
            "description": "Define memory request parameters and limits (e.g. limit: 512Mi) and set eviction thresholds to reclaim resources before Out-Of-Memory (OOM) killer triggers.",
            "category": "Kubernetes",
            "priority": "High",
            "confidence": 0.90,
            "estimatedRiskReduction": 55.0,
            "automationSupported": True,
            "reasoning": f"Critical memory consumption detected under {context_profile} profile. Resource limits prevent nodes from crashing due to OOM conditions."
        })
        recs.append({
            "recommendationId": "REC-MONITOR-002",
            "title": "Enable Out-of-Memory (OOM) Kernel Alerts",
            "description": "Configure systemd-oomd or node-exporter alerts to trigger notifications when processes approach memory depletion limits.",
            "category": "Monitoring",
            "priority": "Medium",
            "confidence": 0.95,
            "estimatedRiskReduction": 15.0,
            "automationSupported": True,
            "reasoning": "Proactive OOM alerts allow operators to isolate leaking containers before service degradation."
        })

    # 4. STORAGE THREAT RULES (Disk Exhaustion / Ransomware)
    if attack_profile in ("Disk Exhaustion", "Ransomware Behaviour") or (top_contributor == "Disk" and decision in ("Alert", "High Risk", "Critical")):
        recs.append({
            "recommendationId": "REC-DOCKER-002",
            "title": "Enforce Read-Only Container Root Filesystem",
            "description": "Run the container with '--read-only' flag and restrict directory volume mounts to write-once parameters to block encryption writes.",
            "category": "Docker",
            "priority": "Critical" if attack_profile == "Ransomware Behaviour" else "High",
            "confidence": 0.96,
            "estimatedRiskReduction": 85.0,
            "automationSupported": True,
            "reasoning": "Ransomware payloads require write capability to encrypt files. Enforcing read-only root filesystems completely blocks ransomware execution."
        })
        recs.append({
            "recommendationId": "REC-IAM-001",
            "title": "Audit and Restrict Storage Delete/Write IAM Permissions",
            "description": "Restrict IAM role permissions on cloud object storage (e.g., AWS S3 bucket policies). Disable DeleteBucket and PutObject permissions for runtime instances.",
            "category": "IAM",
            "priority": "High",
            "confidence": 0.94,
            "estimatedRiskReduction": 65.0,
            "automationSupported": False,
            "reasoning": "Restricting IAM permissions prevents compromised container software from altering or encrypting backing database storage."
        })
        recs.append({
            "recommendationId": "REC-LOG-001",
            "title": "Redirect Container Audit Logs to Immutable Storage",
            "description": "Configure log shippers (e.g., Fluentd) to redirect container execution logs directly to write-once-read-many (WORM) storage systems.",
            "category": "Logging",
            "priority": "High",
            "confidence": 0.98,
            "estimatedRiskReduction": 30.0,
            "automationSupported": True,
            "reasoning": "Ransomware payloads often try to delete system audit logs to conceal operational traces. Immutable storage preserves forensics."
        })

    # 5. TRAFFIC FLOOD RULES (Network Flood)
    if attack_profile == "Network Flood" or (top_contributor == "Network" and decision in ("Alert", "High Risk", "Critical")):
        recs.append({
            "recommendationId": "REC-NETPOL-001",
            "title": "Apply Kubernetes Ingress Rate Limits and NetworkPolicy",
            "description": "Deploy a Kubernetes NetworkPolicy blocking non-essential pod ingress/egress connections and apply ingress controller traffic shaping/rate-limiting.",
            "category": "Network Policies",
            "priority": "Critical" if decision == "Critical" else "High",
            "confidence": 0.94,
            "estimatedRiskReduction": 75.0,
            "automationSupported": True,
            "reasoning": "Network flooding indicates a denial of service or active data exfiltration. Strict network policies restrict the attack vector."
        })
        recs.append({
            "recommendationId": "REC-SG-001",
            "title": "Restrict AWS Security Group Ingress Rules",
            "description": "Revoke wildcard ingress mappings (0.0.0.0/0) in security groups and restrict ingress access only to verified load balancer CIDR blocks.",
            "category": "AWS Security Groups",
            "priority": "High",
            "confidence": 0.90,
            "estimatedRiskReduction": 60.0,
            "automationSupported": True,
            "reasoning": "Wildcard ingress rules expose container runtimes directly to malicious scanning and flooding attacks."
        })
        recs.append({
            "recommendationId": "REC-EC2-001",
            "title": "Enable AWS VPC Flow Logs and Traffic Mirroring",
            "description": "Activate VPC Flow Logs for network packet analysis and capture raw traffic mirroring on the affected EC2 instances for anomaly audits.",
            "category": "AWS EC2",
            "priority": "Medium",
            "confidence": 0.95,
            "estimatedRiskReduction": 20.0,
            "automationSupported": True,
            "reasoning": "VPC flow logging gives netflow visibility, allowing engineers to identify source flooding IPs."
        })

    # 6. RUNTIME ESCAPE RULES (Container Escape Attempt)
    if attack_profile == "Container Escape Attempt" or (decision == "Critical" and reconstruction_error > 0.20):
        recs.append({
            "recommendationId": "REC-K8S-003",
            "title": "Drop Container Linux Capabilities and Restrict Privilege Escalation",
            "description": "Set securityContext parameters in the deployment spec: drop ALL Linux capabilities, set runAsNonRoot to true, and allowPrivilegeEscalation to false.",
            "category": "Kubernetes",
            "priority": "Critical",
            "confidence": 0.98,
            "estimatedRiskReduction": 90.0,
            "automationSupported": True,
            "reasoning": "Container escapes rely on broad Linux kernel capabilities (e.g. SYS_ADMIN) and root escalation. Dropping capabilities halts breakout exploits."
        })
        recs.append({
            "recommendationId": "REC-ANSIBLE-002",
            "title": "Run Host Kernel Vulnerability Audit and Patching",
            "description": "Trigger an automated Ansible patching playbook to check host system kernel releases, update kernel releases, and apply reboot patches.",
            "category": "Ansible Playbooks",
            "priority": "High",
            "confidence": 0.92,
            "estimatedRiskReduction": 80.0,
            "automationSupported": True,
            "reasoning": "Breakout attempts target unpatched kernel vulnerabilities to achieve host node privileges."
        })

    # 7. DEFAULT BASELINE (Normal Workload / Low Risk)
    if not recs or decision == "Normal":
        recs.append({
            "recommendationId": "REC-MONITOR-100",
            "title": "Enable DevSecOps Baseline Telemetry Audits",
            "description": "Keep standard Prometheus scraping intervals and configure automated log integrity monitoring across all container daemon events.",
            "category": "Monitoring",
            "priority": "Low",
            "confidence": 0.99,
            "estimatedRiskReduction": 5.0,
            "automationSupported": True,
            "reasoning": "Telemetry levels are currently normal. Baseline monitoring provides data for future drift detection."
        })
        recs.append({
            "recommendationId": "REC-LOG-100",
            "title": "Standardize Logging Level and Rotation Parameters",
            "description": "Configure log rotation to restrict log sizes on node hosts to 10MB per container, keeping a maximum of 5 logs to optimize storage.",
            "category": "Logging",
            "priority": "Low",
            "confidence": 0.99,
            "estimatedRiskReduction": 5.0,
            "automationSupported": True,
            "reasoning": "Normal workload logging profile keeps operational volumes clean and stable."
        })

    return recs
