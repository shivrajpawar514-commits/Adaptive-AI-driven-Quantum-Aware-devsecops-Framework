import os
import time
import random
import datetime
import json
from typing import List, Optional, Dict, Any, Callable
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

app = FastAPI(title="Attack Simulation Engine API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Scenario Library & MITRE Mapping Data
# ---------------------------------------------------------
SCENARIOS = {
    "crypto-mining": {
        "id": "crypto-mining",
        "name": "Crypto Mining Malware",
        "threat_level": "High",
        "description": "Cryptojacking script hijacking system resources to mine Monero (XMR).",
        "estimated_duration": "45s",
        "affected_assets": "EC2 Production, Gateway, Cloud Adapter",
        "difficulty": "Medium",
        "mitre_ids": "T1496 (Resource Hijacking), T1059 (Command and Scripting)",
        "recommended_response": "Kill process, Quarantine Host, Block Mining Pool",
    },
    "ransomware": {
        "id": "ransomware",
        "name": "Ransomware Attack",
        "threat_level": "Critical",
        "description": "Malicious payload encrypting system volume and staging extortion.",
        "estimated_duration": "45s",
        "affected_assets": "EC2 Production, Digital Twin DB, File Storage",
        "difficulty": "High",
        "mitre_ids": "T1486 (Data Encrypted), T1491 (Defacement)",
        "recommended_response": "Snapshot VM, Detach Volume, Isolate Host",
    },
    "ddos": {
        "id": "ddos",
        "name": "DDoS Saturation",
        "threat_level": "High",
        "description": "SYN Flood flooding gateway interfaces to disrupt availability.",
        "estimated_duration": "45s",
        "affected_assets": "Gateway, Subnet, Client Interface",
        "difficulty": "Medium",
        "mitre_ids": "T1498 (Network Denial of Service)",
        "recommended_response": "WAF Rules, Scale Target Group, Enable Rate Limit",
    },
    "credential-theft": {
        "id": "credential-theft",
        "name": "Credential Theft & Privilege Escalation",
        "threat_level": "High",
        "description": "Brute-force account takeover resulting in administrative token staging.",
        "estimated_duration": "45s",
        "affected_assets": "IAM, Admin Console, Database",
        "difficulty": "Hard",
        "mitre_ids": "T1110 (Brute Force), T1068 (Exploitation for Privilege)",
        "recommended_response": "Disable IAM User, Rotate Keys, Invalidate Session",
    },
    "data-exfiltration": {
        "id": "data-exfiltration",
        "name": "Data Exfiltration to Threat Actor",
        "threat_level": "Critical",
        "description": "Abnormal volume queries exfiltrating customer DB dumps to external IP.",
        "estimated_duration": "45s",
        "affected_assets": "Database, Cloud Gateway, IAM Role",
        "difficulty": "Hard",
        "mitre_ids": "T1048 (Exfiltration Over Alternative Protocol)",
        "recommended_response": "Block Security Group, Rotate Secrets, Disable IAM Role",
    }
}

# Predefined keyframes for 10-phase smooth interpolation
KEYFRAMES = {
    "crypto-mining": [
        {"t": 0, "cpu": 18, "memory": 40, "network": 5, "disk": 15, "latency": 5, "risk": 10, "anomaly_score": 0.02, "confidence": 0.0},
        {"t": 5, "cpu": 22, "memory": 42, "network": 12, "disk": 15, "latency": 5, "risk": 12, "anomaly_score": 0.05, "confidence": 0.1},
        {"t": 10, "cpu": 40, "memory": 48, "network": 1200, "disk": 16, "latency": 5, "risk": 20, "anomaly_score": 0.25, "confidence": 0.4},
        {"t": 15, "cpu": 75, "memory": 60, "network": 4500, "disk": 16, "latency": 5, "risk": 35, "anomaly_score": 0.65, "confidence": 0.7},
        {"t": 20, "cpu": 96, "memory": 72, "network": 12000, "disk": 17, "latency": 6, "risk": 70, "anomaly_score": 0.95, "confidence": 0.92},
        {"t": 25, "cpu": 98, "memory": 75, "network": 15000, "disk": 17, "latency": 6, "risk": 90, "anomaly_score": 0.99, "confidence": 0.98},
        {"t": 30, "cpu": 95, "memory": 74, "network": 14500, "disk": 17, "latency": 6, "risk": 91, "anomaly_score": 0.99, "confidence": 0.98},
        {"t": 35, "cpu": 55, "memory": 65, "network": 150, "disk": 16, "latency": 5, "risk": 40, "anomaly_score": 0.15, "confidence": 0.5},
        {"t": 40, "cpu": 25, "memory": 55, "network": 10, "disk": 15, "latency": 5, "risk": 12, "anomaly_score": 0.04, "confidence": 0.1},
        {"t": 45, "cpu": 18, "memory": 43, "network": 5, "disk": 15, "latency": 5, "risk": 10, "anomaly_score": 0.02, "confidence": 0.0},
    ],
    "ransomware": [
        {"t": 0, "cpu": 12, "memory": 35, "network": 8, "disk": 10, "latency": 6, "risk": 8, "anomaly_score": 0.01, "confidence": 0.0},
        {"t": 5, "cpu": 18, "memory": 37, "network": 20, "disk": 25, "latency": 6, "risk": 12, "anomaly_score": 0.06, "confidence": 0.15},
        {"t": 10, "cpu": 35, "memory": 42, "network": 50, "disk": 55, "latency": 6, "risk": 25, "anomaly_score": 0.35, "confidence": 0.5},
        {"t": 15, "cpu": 65, "memory": 55, "network": 80, "disk": 88, "latency": 7, "risk": 58, "anomaly_score": 0.78, "confidence": 0.82},
        {"t": 20, "cpu": 85, "memory": 68, "network": 95, "disk": 98, "latency": 8, "risk": 88, "anomaly_score": 0.98, "confidence": 0.95},
        {"t": 25, "cpu": 88, "memory": 70, "network": 120, "disk": 99, "latency": 8, "risk": 98, "anomaly_score": 0.99, "confidence": 0.98},
        {"t": 30, "cpu": 82, "memory": 65, "network": 100, "disk": 40, "latency": 7, "risk": 92, "anomaly_score": 0.90, "confidence": 0.90},
        {"t": 35, "cpu": 30, "memory": 48, "network": 25, "disk": 18, "latency": 6, "risk": 42, "anomaly_score": 0.20, "confidence": 0.4},
        {"t": 40, "cpu": 15, "memory": 38, "network": 10, "disk": 12, "latency": 6, "risk": 15, "anomaly_score": 0.05, "confidence": 0.1},
        {"t": 45, "cpu": 12, "memory": 35, "network": 8, "disk": 10, "latency": 6, "risk": 8, "anomaly_score": 0.01, "confidence": 0.0},
    ],
    "ddos": [
        {"t": 0, "cpu": 8, "memory": 30, "network": 50, "disk": 8, "latency": 5, "risk": 6, "anomaly_score": 0.01, "confidence": 0.0},
        {"t": 5, "cpu": 15, "memory": 35, "network": 150000, "disk": 8, "latency": 45, "risk": 15, "anomaly_score": 0.10, "confidence": 0.2},
        {"t": 10, "cpu": 40, "memory": 45, "network": 450000, "disk": 9, "latency": 450, "risk": 45, "anomaly_score": 0.50, "confidence": 0.6},
        {"t": 15, "cpu": 75, "memory": 55, "network": 850000, "disk": 9, "latency": 1800, "risk": 80, "anomaly_score": 0.88, "confidence": 0.88},
        {"t": 20, "cpu": 92, "memory": 62, "network": 980000, "disk": 10, "latency": 2800, "risk": 95, "anomaly_score": 0.99, "confidence": 0.96},
        {"t": 25, "cpu": 95, "memory": 65, "network": 999000, "disk": 10, "latency": 2900, "risk": 96, "anomaly_score": 0.99, "confidence": 0.98},
        {"t": 30, "cpu": 88, "memory": 60, "network": 250000, "disk": 9, "latency": 1200, "risk": 90, "anomaly_score": 0.92, "confidence": 0.94},
        {"t": 35, "cpu": 25, "memory": 40, "network": 2000, "disk": 8, "latency": 35, "risk": 35, "anomaly_score": 0.15, "confidence": 0.3},
        {"t": 40, "cpu": 12, "memory": 33, "network": 150, "disk": 8, "latency": 8, "risk": 12, "anomaly_score": 0.03, "confidence": 0.1},
        {"t": 45, "cpu": 8, "memory": 30, "network": 50, "disk": 8, "latency": 5, "risk": 6, "anomaly_score": 0.01, "confidence": 0.0},
    ],
    "credential-theft": [
        {"t": 0, "cpu": 10, "memory": 35, "network": 10, "disk": 12, "latency": 5, "risk": 10, "anomaly_score": 0.01, "confidence": 0.0},
        {"t": 5, "cpu": 12, "memory": 35, "network": 12, "disk": 12, "latency": 5, "risk": 15, "anomaly_score": 0.04, "confidence": 0.1},
        {"t": 10, "cpu": 14, "memory": 36, "network": 15, "disk": 12, "latency": 5, "risk": 35, "anomaly_score": 0.25, "confidence": 0.3},
        {"t": 15, "cpu": 16, "memory": 36, "network": 18, "disk": 13, "latency": 5, "risk": 68, "anomaly_score": 0.68, "confidence": 0.72},
        {"t": 20, "cpu": 18, "memory": 37, "network": 22, "disk": 13, "latency": 5, "risk": 92, "anomaly_score": 0.95, "confidence": 0.96},
        {"t": 25, "cpu": 20, "memory": 38, "network": 25, "disk": 13, "latency": 5, "risk": 94, "anomaly_score": 0.96, "confidence": 0.97},
        {"t": 30, "cpu": 18, "memory": 37, "network": 20, "disk": 13, "latency": 5, "risk": 90, "anomaly_score": 0.91, "confidence": 0.92},
        {"t": 35, "cpu": 15, "memory": 36, "network": 15, "disk": 12, "latency": 5, "risk": 42, "anomaly_score": 0.22, "confidence": 0.3},
        {"t": 40, "cpu": 12, "memory": 35, "network": 12, "disk": 12, "latency": 5, "risk": 18, "anomaly_score": 0.05, "confidence": 0.1},
        {"t": 45, "cpu": 10, "memory": 35, "network": 10, "disk": 12, "latency": 5, "risk": 10, "anomaly_score": 0.01, "confidence": 0.0},
    ],
    "data-exfiltration": [
        {"t": 0, "cpu": 12, "memory": 30, "network": 15, "disk": 15, "latency": 7, "risk": 8, "anomaly_score": 0.01, "confidence": 0.0},
        {"t": 5, "cpu": 15, "memory": 32, "network": 450, "disk": 22, "latency": 7, "risk": 15, "anomaly_score": 0.05, "confidence": 0.1},
        {"t": 10, "cpu": 28, "memory": 38, "network": 12000, "disk": 45, "latency": 7, "risk": 38, "anomaly_score": 0.32, "confidence": 0.45},
        {"t": 15, "cpu": 42, "memory": 48, "network": 280000, "disk": 62, "latency": 7, "risk": 75, "anomaly_score": 0.74, "confidence": 0.8},
        {"t": 20, "cpu": 50, "memory": 55, "network": 650000, "disk": 70, "latency": 8, "risk": 95, "anomaly_score": 0.95, "confidence": 0.94},
        {"t": 25, "cpu": 52, "memory": 56, "network": 720000, "disk": 72, "latency": 8, "risk": 96, "anomaly_score": 0.96, "confidence": 0.96},
        {"t": 30, "cpu": 48, "memory": 52, "network": 680000, "disk": 68, "latency": 8, "risk": 92, "anomaly_score": 0.88, "confidence": 0.9},
        {"t": 35, "cpu": 22, "memory": 38, "network": 1000, "disk": 25, "latency": 7, "risk": 40, "anomaly_score": 0.18, "confidence": 0.3},
        {"t": 40, "cpu": 15, "memory": 32, "network": 80, "disk": 18, "latency": 7, "risk": 15, "anomaly_score": 0.04, "confidence": 0.1},
        {"t": 45, "cpu": 12, "memory": 30, "network": 15, "disk": 15, "latency": 7, "risk": 8, "anomaly_score": 0.01, "confidence": 0.0},
    ]
}

def lerp(start: float, end: float, amt: float) -> float:
    return (1 - amt) * start + amt * end

def get_telemetry_for_tick(scenario_id: str, elapsed: int) -> dict:
    keyframes = KEYFRAMES.get(scenario_id, KEYFRAMES["crypto-mining"])
    elapsed = max(0, min(elapsed, 45))
    
    low_idx = 0
    for i in range(len(keyframes) - 1):
        if keyframes[i]["t"] <= elapsed <= keyframes[i+1]["t"]:
            low_idx = i
            break
            
    t_low = keyframes[low_idx]
    t_high = keyframes[low_idx + 1]
    
    dt = t_high["t"] - t_low["t"]
    factor = 0.0 if dt == 0 else (elapsed - t_low["t"]) / dt
    
    cpu = round(lerp(t_low["cpu"], t_high["cpu"], factor), 2)
    memory = round(lerp(t_low["memory"], t_high["memory"], factor), 2)
    network = round(lerp(t_low["network"], t_high["network"], factor), 2)
    disk = round(lerp(t_low["disk"], t_high["disk"], factor), 2)
    latency = round(lerp(t_low["latency"], t_high["latency"], factor), 2)
    risk = round(lerp(t_low["risk"], t_high["risk"], factor), 2)
    anomaly_score = round(lerp(t_low["anomaly_score"], t_high["anomaly_score"], factor), 3)
    confidence = round(lerp(t_low["confidence"], t_high["confidence"], factor), 3)
    
    if elapsed < 5:
        phase = "NORMAL"
    elif elapsed < 10:
        phase = "ATTACK STARTED"
    elif elapsed < 15:
        phase = "ATTACK PROGRESSING"
    elif elapsed < 20:
        phase = "AI DETECTED ANOMALY"
    elif elapsed < 25:
        phase = "URS RISK UPDATED"
    elif elapsed < 30:
        phase = "AUTOMATION TRIGGERED"
    elif elapsed < 35:
        phase = "MITIGATION RUNNING"
    elif elapsed < 40:
        phase = "RECOVERY"
    else:
        phase = "POST INCIDENT REPORT"

    return {
        "cpu": cpu,
        "memory": memory,
        "network": network,
        "disk": disk,
        "latency": latency,
        "risk": risk,
        "anomaly_score": anomaly_score,
        "confidence": confidence,
        "phase": phase
    }

def get_timeline_for_tick(scenario_id: str, elapsed: int) -> list:
    all_events = {
        "crypto-mining": [
            {"time": "12:15:00", "event": "Pre Attack: Infrastructure Healthy.", "status": "info", "t_trigger": 0},
            {"time": "12:15:05", "event": "Initial Compromise: Suspicious PowerShell execution on EC2 Production (MITRE T1059).", "status": "warning", "t_trigger": 5},
            {"time": "12:15:10", "event": "Attack Progressing: CPU utilization rises. Binary process 'xmrig' launched.", "status": "warning", "t_trigger": 10},
            {"time": "12:15:14", "event": "Outbound stratum pool traffic connection to 45.77.102.13 (Russia).", "status": "critical", "t_trigger": 14},
            {"time": "12:15:15", "event": "Threat signature matched: Cryptomining Pool payload execution.", "status": "critical", "t_trigger": 15},
            {"time": "12:15:20", "event": "AI Engine anomaly score peaks at 0.993. Severity classified: Critical.", "status": "critical", "t_trigger": 20},
            {"time": "12:15:22", "event": "Risk Engine recalculating Unified Risk Score (URS) to 91%.", "status": "critical", "t_trigger": 22},
            {"time": "12:15:25", "event": "Policy Engine playbook triggered. Remediations sent to Automation Engine.", "status": "info", "t_trigger": 25},
            {"time": "12:15:28", "event": "Remediation Playbook: Freezing instance & killing miner process.", "status": "info", "t_trigger": 28},
            {"time": "12:15:30", "event": "Mitigation: Compromised miner process terminated successfully.", "status": "success", "t_trigger": 30},
            {"time": "12:15:35", "event": "Recovery: System resources stabilized. Incident response metrics captured.", "status": "success", "t_trigger": 35},
            {"time": "12:15:40", "event": "Incident contained. Post-Incident Report generated.", "status": "success", "t_trigger": 40}
        ],
        "ransomware": [
            {"time": "12:15:00", "event": "Pre Attack: Volume reads normal.", "status": "info", "t_trigger": 0},
            {"time": "12:15:05", "event": "Initial Compromise: Phishing macro drops payload 'ransom.exe'.", "status": "warning", "t_trigger": 5},
            {"time": "12:15:10", "event": "Attack Progressing: Disk IOPS spikes to 95%. CPU spikes to 75%.", "status": "warning", "t_trigger": 10},
            {"time": "12:15:14", "event": "Sensitive directories modified. File encryption counter incrementing rapidly.", "status": "critical", "t_trigger": 14},
            {"time": "12:15:15", "event": "AI Engine anomaly flag raised. Invariant error detected.", "status": "critical", "t_trigger": 15},
            {"time": "12:15:20", "event": "Risk Engine recalculating URS score to 98% (Critical shadow hazard).", "status": "critical", "t_trigger": 20},
            {"time": "12:15:25", "event": "Automation Engine runs VM Volume snapshot.", "status": "info", "t_trigger": 25},
            {"time": "12:15:28", "event": "Active containment: Host isolated from gateway subnet.", "status": "success", "t_trigger": 28},
            {"time": "12:15:30", "event": "Containment complete. Attacking volume detached.", "status": "success", "t_trigger": 30},
            {"time": "12:15:35", "event": "Recovery: Restoring clean volume from immutable snapshot.", "status": "success", "t_trigger": 35},
            {"time": "12:15:40", "event": "Incident contained. Data recovery successful.", "status": "success", "t_trigger": 40}
        ],
        "ddos": [
            {"time": "12:15:00", "event": "Pre Attack: Standard network ingress checks healthy.", "status": "info", "t_trigger": 0},
            {"time": "12:15:05", "event": "Initial Compromise: Traffic surge from multiple suspicious client subnets.", "status": "warning", "t_trigger": 5},
            {"time": "12:15:10", "event": "SYN flood reaches 450 MB/s. Web interface latency reaches 450ms.", "status": "warning", "t_trigger": 10},
            {"time": "12:15:14", "event": "Total gateway saturation. Latency spikes to 2800ms.", "status": "critical", "t_trigger": 14},
            {"time": "12:15:15", "event": "AI flags DDoS packet pattern (99% anomaly score).", "status": "critical", "t_trigger": 15},
            {"time": "12:15:20", "event": "Risk Engine URS weight reaches 95%. Traffic block playbook activated.", "status": "critical", "t_trigger": 20},
            {"time": "12:15:25", "event": "Automation Engine deploys WAF rate limits & IP range block.", "status": "info", "t_trigger": 25},
            {"time": "12:15:30", "event": "Mitigation: Flood packets dropped at boundary router.", "status": "success", "t_trigger": 30},
            {"time": "12:15:35", "event": "Gateway capacity auto-scaling triggered. Latency drops to 8ms.", "status": "success", "t_trigger": 35},
            {"time": "12:15:40", "event": "Recovery complete. Normal client traffic flows resumed.", "status": "success", "t_trigger": 40}
        ],
        "credential-theft": [
            {"time": "12:15:00", "event": "Pre Attack: User login patterns regular.", "status": "info", "t_trigger": 0},
            {"time": "12:15:05", "event": "Initial Compromise: Brute-force login attempts detected on admin portal.", "status": "warning", "t_trigger": 5},
            {"time": "12:15:10", "event": "Takeover detected: Impossible travel login success (MITRE T1078).", "status": "warning", "t_trigger": 10},
            {"time": "12:15:14", "event": "Sensitive privilege escalation API calls initiated (MITRE T1068).", "status": "critical", "t_trigger": 14},
            {"time": "12:15:15", "event": "AI Engine flags credential theft profile (96% confidence).", "status": "critical", "t_trigger": 15},
            {"time": "12:15:20", "event": "Risk Engine recalculates URS score to 92% (High threat class).", "status": "critical", "t_trigger": 20},
            {"time": "12:15:25", "event": "Automation Engine disables compromised user credentials.", "status": "info", "t_trigger": 25},
            {"time": "12:15:30", "event": "Remediation: Target user session invalidated & rotated API keys.", "status": "success", "t_trigger": 30},
            {"time": "12:15:35", "event": "Active containment: Security group updated. MFA enforcement required.", "status": "success", "t_trigger": 35},
            {"time": "12:15:40", "event": "Incident contained. User credentials rotated.", "status": "success", "t_trigger": 40}
        ],
        "data-exfiltration": [
            {"time": "12:15:00", "event": "Pre Attack: Database read/write profiles stable.", "status": "info", "t_trigger": 0},
            {"time": "12:15:05", "event": "Initial Compromise: Unauthorized backup SQL dump query executed.", "status": "warning", "t_trigger": 5},
            {"time": "12:15:10", "event": "Exfiltration start: Ingress dump reading (T1048) rises to 12MB/s.", "status": "warning", "t_trigger": 10},
            {"time": "12:15:14", "event": "Outbound DB dump transfer initiated to foreign IP.", "status": "critical", "t_trigger": 14},
            {"time": "12:15:15", "event": "AI flags anomaly (0.95 score).", "status": "critical", "t_trigger": 15},
            {"time": "12:15:20", "event": "Risk Engine raises URS to 95%. Outbound block playbook active.", "status": "critical", "t_trigger": 20},
            {"time": "12:15:25", "event": "Automation Engine blocks target IP range at gateway security group.", "status": "info", "t_trigger": 25},
            {"time": "12:15:30", "event": "Mitigation: Outbound DB exfiltration session terminated.", "status": "success", "t_trigger": 30},
            {"time": "12:15:35", "event": "Active recovery: Compromised database secret keys rotated.", "status": "success", "t_trigger": 35},
            {"time": "12:15:40", "event": "Incident contained. Secrets rotated & audit logged.", "status": "success", "t_trigger": 40}
        ]
    }
    events = all_events.get(scenario_id, all_events["crypto-mining"])
    return [e for e in events if e["t_trigger"] <= elapsed]

def get_automation_for_tick(scenario_id: str, elapsed: int) -> list:
    all_actions = {
        "crypto-mining": [
            {"timestamp": "12:15:25", "action": "Freeze instance", "duration": "1.2s", "t_trigger": 25},
            {"timestamp": "12:15:26", "action": "Capture Memory Dump", "duration": "3.5s", "t_trigger": 26},
            {"timestamp": "12:15:27", "action": "Create Snapshot", "duration": "4.1s", "t_trigger": 27},
            {"timestamp": "12:15:28", "action": "Block Security Group", "duration": "0.8s", "t_trigger": 28},
            {"timestamp": "12:15:29", "action": "Rotate IAM Keys", "duration": "1.5s", "t_trigger": 29},
            {"timestamp": "12:15:30", "action": "Kill Malware", "duration": "0.5s", "t_trigger": 30},
            {"timestamp": "12:15:32", "action": "Notify SOC", "duration": "0.2s", "t_trigger": 32},
            {"timestamp": "12:15:35", "action": "Generate Report", "duration": "1.1s", "t_trigger": 35}
        ],
        "ransomware": [
            {"timestamp": "12:15:25", "action": "Snapshot VM", "duration": "2.8s", "t_trigger": 25},
            {"timestamp": "12:15:27", "action": "Detach Volume", "duration": "1.4s", "t_trigger": 27},
            {"timestamp": "12:15:29", "action": "Isolate Host", "duration": "0.9s", "t_trigger": 29},
            {"timestamp": "12:15:33", "action": "Restore Snapshot", "duration": "5.6s", "t_trigger": 33}
        ],
        "ddos": [
            {"timestamp": "12:15:25", "action": "Apply WAF Rule", "duration": "1.1s", "t_trigger": 25},
            {"timestamp": "12:15:27", "action": "Scale Target Group", "duration": "4.2s", "t_trigger": 27},
            {"timestamp": "12:15:29", "action": "Enable Rate Limit", "duration": "0.5s", "t_trigger": 29},
            {"timestamp": "12:15:32", "action": "Block IP Range", "duration": "0.9s", "t_trigger": 32}
        ],
        "credential-theft": [
            {"timestamp": "12:15:25", "action": "Disable IAM User", "duration": "1.1s", "t_trigger": 25},
            {"timestamp": "12:15:27", "action": "Rotate Keys", "duration": "1.8s", "t_trigger": 27},
            {"timestamp": "12:15:29", "action": "Invalidate Session", "duration": "0.6s", "t_trigger": 29},
            {"timestamp": "12:15:32", "action": "Force MFA", "duration": "1.2s", "t_trigger": 32}
        ],
        "data-exfiltration": [
            {"timestamp": "12:15:25", "action": "Block Security Group", "duration": "0.8s", "t_trigger": 25},
            {"timestamp": "12:15:27", "action": "Rotate Secrets", "duration": "2.1s", "t_trigger": 27},
            {"timestamp": "12:15:29", "action": "Disable IAM Role", "duration": "1.4s", "t_trigger": 29},
            {"timestamp": "12:15:32", "action": "Terminate Session", "duration": "0.5s", "t_trigger": 32}
        ]
    }
    
    actions = all_actions.get(scenario_id, all_actions["crypto-mining"])
    result = []
    triggered_actions = [a for a in actions if a["t_trigger"] <= elapsed]
    
    for idx, act in enumerate(triggered_actions):
        is_last = (idx == len(triggered_actions) - 1)
        status = "Running" if (is_last and elapsed - act["t_trigger"] < 3) else "Completed"
        
        result.append({
            "auditId": f"AUD-AUTO-{1000 + act['t_trigger']}",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "instanceId": "i-084c883d3f70e6f7f",
            "riskScore": 91.0 if scenario_id == "crypto-mining" else 95.0,
            "decision": "Critical",
            "recommendations": [act["action"]],
            "executionPlanCount": 1,
            "automationLevel": "Fully Automated",
            "executionStatus": status,
            "rollbackStatus": "Available",
            "estimatedExecutionTime": float(act["duration"].replace("s", "")),
            "action": act["action"],
            "duration": act["duration"]
        })
        
    return result

def get_topology_highlights(scenario_id: str, elapsed: int) -> dict:
    res = {
        "affectedNodes": ["attack-simulator"],
        "criticalNodes": [],
        "warningNodes": [],
        "criticalEdges": [],
        "warningEdges": []
    }
    if elapsed < 5:
        return res
    elif elapsed < 10:
        res["warningNodes"] = ["attack-simulator", "core-api-app"]
        res["warningEdges"] = ["dashboard->core-api-app"]
    elif elapsed < 15:
        res["warningNodes"] = ["core-api-app", "monitoring"]
        res["criticalNodes"] = ["mongodb"]
        res["warningEdges"] = ["dashboard->core-api-app", "core-api-app->monitoring"]
    elif elapsed < 20:
        res["warningNodes"] = ["ai-engine"]
        res["criticalNodes"] = ["mongodb", "core-api-app"]
        res["criticalEdges"] = ["monitoring->ai-engine"]
    elif elapsed < 30:
        res["criticalNodes"] = ["urs-risk-engine", "ipre-policy-engine", "automation-engine", "mongodb"]
        res["criticalEdges"] = [
            "ai-engine->urs-risk-engine", 
            "urs-risk-engine->ipre-policy-engine", 
            "ipre-policy-engine->automation-engine"
        ]
    elif elapsed < 40:
        res["warningNodes"] = ["automation-engine", "core-api-app"]
        res["warningEdges"] = ["ipre-policy-engine->automation-engine"]
    else:
        # Recovered
        pass
    return res

def get_incident_report(scenario_id: str) -> dict:
    sc = SCENARIOS.get(scenario_id, SCENARIOS["crypto-mining"])
    return {
        "incidentId": "INC-2026-0017",
        "attackType": sc["name"],
        "started": "12:15:00",
        "detected": "12:15:15",
        "contained": "12:15:30",
        "recovered": "12:15:45",
        "affectedAssets": sc["affected_assets"],
        "maxRiskScore": "91%" if scenario_id == "crypto-mining" else "95%",
        "automationSuccess": "100%",
        "mitreMapping": sc["mitre_ids"],
        "executiveSummary": f"Autonomous detection and remediation of active {sc['name']} threat targeting critical cloud infrastructure interfaces. The compromise was flagged within 15 seconds by the AI Anomaly Engine and successfully mitigated by the Policy-Automation remediation loop with zero manual intervention.",
        "rootCause": f"Exploitation of external-facing port bindings allowing command injection and script execution.",
        "recommendations": [
            f"Rotate all active IAM Credentials and enforce multi-factor authentication (MFA).",
            f"Apply WAF rate limiting policies and update firewall/Security Group outbound restrictions.",
            f"Deploy hybrid post-quantum cryptographic keys for TLS handshakes.",
            f"Restrict console execution commands via restricted IAM roles."
        ]
    }

# ---------------------------------------------------------
# Simulation Session Controller
# ---------------------------------------------------------
class SimulationSession:
    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        self.start_time = time.time()
        self.paused = False
        self.pause_time = 0.0
        self.accumulated_pause_duration = 0.0

    def get_elapsed_seconds(self) -> int:
        if self.paused:
            elapsed = self.pause_time - self.start_time - self.accumulated_pause_duration
        else:
            elapsed = time.time() - self.start_time - self.accumulated_pause_duration
        return max(0, int(elapsed))

    def pause(self):
        if not self.paused:
            self.paused = True
            self.pause_time = time.time()

    def resume(self):
        if self.paused:
            self.paused = False
            self.accumulated_pause_duration += time.time() - self.pause_time

active_session: Optional[SimulationSession] = None

# ---------------------------------------------------------
# MongoDB client helper for historical metrics (Existing Compatibility)
# ---------------------------------------------------------
class SimulationDatabase:
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
            print("Connected to MongoDB for simulations successfully.")
        except Exception:
            self.is_mock = True
            print("MongoDB unavailable for simulations. Falling back to Mock Database.")
            
    def insert_simulation(self, doc):
        if self.is_mock:
            self.mock_db.append(doc)
            return True
        try:
            self.db.simulations.insert_one(doc)
            return True
        except Exception as e:
            print(f"MongoDB write failed for simulation: {str(e)}")
            self.mock_db.append(doc)
            return False
            
    def get_history(self, limit=100):
        if self.is_mock:
            return sorted(self.mock_db, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        try:
            cursor = self.db.simulations.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception:
            return sorted(self.mock_db, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

db_helper = SimulationDatabase()

class SimulationRequest(BaseModel):
    attackProfile: Optional[str] = None
    profileName: Optional[str] = None
    workloadProfile: Optional[str] = "Development"
    timestamp: Optional[str] = None
    cryptography: Optional[List[str]] = None

class SessionStartRequest(BaseModel):
    scenarioId: str

@app.get("/health")
def health():
    return {"status": "OK", "service": "Attack Simulation Engine"}

# Scenario Library endpoint
@app.get("/simulation/scenarios")
def get_scenarios():
    return {"status": "success", "data": list(SCENARIOS.values())}

# Start simulation session
@app.post("/simulation/start")
def start_simulation(req: SessionStartRequest):
    global active_session
    if req.scenarioId not in SCENARIOS:
        raise HTTPException(status_code=400, detail="Invalid scenarioId")
    active_session = SimulationSession(req.scenarioId)
    return {"status": "success", "message": f"Simulation session started for scenario: {req.scenarioId}"}

# Pause simulation session
@app.post("/simulation/pause")
def pause_simulation():
    global active_session
    if not active_session:
        raise HTTPException(status_code=400, detail="No active simulation session")
    active_session.pause()
    return {"status": "success", "message": "Simulation session paused"}

# Resume simulation session
@app.post("/simulation/resume")
def resume_simulation():
    global active_session
    if not active_session:
        raise HTTPException(status_code=400, detail="No active simulation session")
    active_session.resume()
    return {"status": "success", "message": "Simulation session resumed"}

# Reset simulation session
@app.post("/simulation/reset")
def reset_simulation():
    global active_session
    active_session = None
    return {"status": "success", "message": "Simulation session reset"}

# Get current simulation tick state
@app.get("/simulation/state")
def get_simulation_state():
    global active_session
    if not active_session:
        return {"status": "idle", "service": "Attack Simulation Engine"}
        
    elapsed = active_session.get_elapsed_seconds()
    is_finished = elapsed >= 45
    
    # Calculate interpolated metrics
    metrics = get_telemetry_for_tick(active_session.scenario_id, elapsed)
    timeline = get_timeline_for_tick(active_session.scenario_id, elapsed)
    automation = get_automation_for_tick(active_session.scenario_id, elapsed)
    highlights = get_topology_highlights(active_session.scenario_id, elapsed)
    
    # Generate AI metrics
    anomaly_score = metrics["anomaly_score"]
    confidence = metrics["confidence"]
    
    sc = SCENARIOS[active_session.scenario_id]
    
    ai_state = {
        "threatType": sc["name"],
        "threatConfidence": round(confidence * 100, 1),
        "detectionConfidence": round(anomaly_score * 100, 1),
        "decision": "Anomaly Detected" if elapsed >= 15 else "Clear",
        "mitigationRecommendation": sc["recommended_response"],
        "quantumReadinessImpact": "High (Shor's threat to legacy keys)" if active_session.scenario_id == "crypto-mining" else "Moderate",
        "mitreMapping": sc["mitre_ids"],
        "severity": "Critical" if elapsed >= 20 else ("Medium" if elapsed >= 10 else "Low"),
        "riskCategory": "Resource Abuse" if active_session.scenario_id == "crypto-mining" else "Access Integrity"
    }
    
    report = get_incident_report(active_session.scenario_id) if is_finished else None
    
    # Generate dynamic prediction summary based on CTPS model
    urs_val = float(metrics["risk"])
    if active_session.scenario_id == "crypto-mining":
        ctps_val = 1.62
        factors = {"severity": 1.8, "exposure": 1.0, "criticality": 1.2, "trend": 1.4, "persistence": 1.1, "remediation": 0.75, "age": 1.0}
        risk_trend = "increasing" if elapsed >= 10 else "stable"
        confidence_obj = {"score": 78.5, "level": "Medium", "explanation": ["Telemetry: strong", "Stability: moderate"]}
        business_impact = {"overall": 72.0, "level": "High", "trend": risk_trend}
    elif active_session.scenario_id == "ransomware":
        ctps_val = 1.95
        factors = {"severity": 1.8, "exposure": 1.3, "criticality": 1.2, "trend": 1.4, "persistence": 1.2, "remediation": 0.75, "age": 1.0}
        risk_trend = "increasing" if elapsed >= 10 else "stable"
        confidence_obj = {"score": 82.0, "level": "High", "explanation": ["Telemetry: strong", "Stability: critical"]}
        business_impact = {"overall": 85.0, "level": "Critical", "trend": risk_trend}
    else:
        ctps_val = 1.0
        factors = {"severity": 1.0, "exposure": 1.0, "criticality": 1.0, "trend": 1.0, "persistence": 1.0, "remediation": 1.0, "age": 1.0}
        risk_trend = "stable"
        confidence_obj = {"score": 60.0, "level": "Medium", "explanation": ["Telemetry: stable", "Stability: normal"]}
        business_impact = {"overall": 35.0, "level": "Low", "trend": "stable"}
        
    proj_24 = round(min(100.0, urs_val * (1.0 + 0.02 * ctps_val * 24 if risk_trend == "increasing" else 1.0 + 0.02 * ctps_val * 24 * 0.3)), 1)
    
    pred_summary = {
        "resource_id": f"SIM-{active_session.scenario_id}",
        "current_urs": urs_val,
        "projected_urs": {"1": round(urs_val * 1.01, 1), "3": round(urs_val * 1.03, 1), "6": round(urs_val * 1.06, 1), "12": round(urs_val * 1.12, 1), "24": proj_24},
        "ctps": ctps_val,
        "factors": factors,
        "risk_trend": risk_trend,
        "confidence": confidence_obj,
        "business_impact": business_impact,
        "algorithm_version": "CTPS-v1.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

    return {
        "status": "active",
        "service": "Attack Simulation Engine",
        "scenarioId": active_session.scenario_id,
        "elapsed": elapsed,
        "paused": active_session.paused,
        "phase": metrics["phase"],
        "isFinished": is_finished,
        "telemetry": {
            "cpu": metrics["cpu"],
            "memory": metrics["memory"],
            "disk": metrics["disk"],
            "network": metrics["network"],
            "latency": metrics["latency"],
            "risk": metrics["risk"],
            "anomaly_score": anomaly_score,
            "confidence": confidence
        },
        "ai": ai_state,
        "timeline": timeline,
        "automation": automation,
        "highlights": highlights,
        "report": report,
        "prediction_summary": pred_summary
    }

# ---------------------------------------------------------
# Legacy APIs kept fully intact to avoid breaking local_validation.py
# ---------------------------------------------------------
@app.post("/simulation/run")
def run_simulation(req: SimulationRequest):
    profile_name = req.attackProfile or req.profileName
    if not profile_name:
        profile_name = "Crypto Mining"
    
    # Make sure we map standard naming conventions
    if profile_name == "Crypto Mining":
        sc_id = "crypto-mining"
    elif "Ransomware" in profile_name:
        sc_id = "ransomware"
    elif "DDoS" in profile_name:
        sc_id = "ddos"
    elif "Credential" in profile_name:
        sc_id = "credential-theft"
    else:
        sc_id = "data-exfiltration"
        
    metrics = get_telemetry_for_tick(sc_id, 25) # mid-attack snapshot
    
    results = {
        "attackName": profile_name,
        "detected": True,
        "latencyMs": 150,
        "confidence": metrics["confidence"],
        "riskScore": metrics["risk"],
        "decision": "Critical",
        "topContributor": "CPU",
        "quantumReadiness": 35,
        "recommendation": "Migrate to hybrid TLS."
    }
    
    doc = {
        "timestamp": req.timestamp or datetime.datetime.utcnow().isoformat(),
        "attackProfile": profile_name,
        "workloadProfile": req.workloadProfile,
        "telemetry": {
            "cpu_usage": metrics["cpu"],
            "memory_usage": metrics["memory"],
            "disk_usage": metrics["disk"],
            "network_usage": metrics["network"],
            "anomaly_score": metrics["anomaly_score"],
            "reconstruction_error": 0.15,
            "confidence_score": metrics["confidence"]
        },
        "urs": metrics["risk"],
        "static_urs": metrics["risk"],
        "decision": "Critical",
        "reason": "Simulation run snapshot.",
        "topContributor": "CPU",
        "contextProfile": "Business Hours",
        "quantumReadinessScore": 35,
        "recommendedMitigation": "Migrate to hybrid TLS.",
        "latencyMs": 150,
        "results": results
    }
    db_helper.insert_simulation(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return {"status": "success", "results": results, "detail": doc}

@app.get("/simulation/history")
def get_simulation_history(limit: int = 50):
    records = db_helper.get_history(limit)
    return {"status": "success", "data": records}

@app.get("/simulation/results")
def get_simulation_results(limit: int = 50):
    records = db_helper.get_history(limit)
    comparative_results = [r.get("results") for r in records if r.get("results")]
    return {"status": "success", "data": comparative_results}
