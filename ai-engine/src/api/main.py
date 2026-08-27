import datetime
import os
import time
import json
from typing import List, Optional, Dict, Any, Callable
import pandas as pd
import torch
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

from src.preprocessing.pipeline import PreprocessingPipeline
from src.training.trainer import AutoencoderTrainer
from src.api.db_utils import load_data_from_mongodb

app = FastAPI(title="AI Anomaly Engine API")
app.router.route_class = StandardAPIRoute

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

saved_models_dir = "./saved_models"
pipeline = None
trainer = None

class PredictRequest(BaseModel):
    cpu_utilization: float
    memory_usage_percent: float
    disk_usage_percent: float
    packet_rate_in: float
    packet_rate_out: float

class TrainRequest(BaseModel):
    epochs: int = 10
    batch_size: int = 16
    lr: float = 0.001

def load_saved_model():
    global pipeline, trainer
    try:
        if os.path.exists(os.path.join(saved_models_dir, 'autoencoder.pt')):
            pipeline = PreprocessingPipeline()
            pipeline.load(saved_models_dir)
            
            trainer = AutoencoderTrainer()
            trainer.load(saved_models_dir)
            print("Model files successfully loaded from directory.")
        else:
            print("No pre-trained model found. Pipeline is uninitialized.")
    except Exception as e:
        print(f"Error loading saved model: {str(e)}")

@app.on_event("startup")
def startup_event():
    load_saved_model()

@app.get("/health")
def health():
    return {"status": "OK", "version": "1.0.0"}

@app.post("/train")
def train(req: TrainRequest):
    global pipeline, trainer
    try:
        df = load_data_from_mongodb()
        
        pipeline = PreprocessingPipeline()
        X_pca = pipeline.fit_transform(df)
        
        split_idx = int(len(X_pca) * 0.8)
        X_train = X_pca[:split_idx]
        X_val = X_pca[split_idx:]
        
        if len(X_train) == 0 or len(X_val) == 0:
            raise HTTPException(status_code=400, detail="Insufficient metrics dataset for training split.")
            
        trainer = AutoencoderTrainer()
        history, train_time = trainer.train(
            X_train, X_val, 
            epochs=req.epochs, 
            batch_size=req.batch_size, 
            lr=req.lr
        )
        
        pipeline.save(saved_models_dir)
        trainer.save(saved_models_dir)
        
        return {
            "status": "success",
            "message": "Model trained and saved successfully.",
            "metrics": {
                "training_time_seconds": train_time,
                "final_train_loss": history['train_loss'][-1],
                "final_val_loss": history['val_loss'][-1],
                "anomaly_threshold": trainer.threshold
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failure: {str(e)}")

@app.post("/predict")
def predict(req: PredictRequest):
    global pipeline, trainer
    if not pipeline or not trainer:
        raise HTTPException(status_code=400, detail="Autoencoder model not trained yet. Call POST /train first.")
        
    try:
        df = pd.DataFrame([req.dict()])
        X_pca = pipeline.transform(df)
        
        tensor = torch.tensor(X_pca, dtype=torch.float32)
        with torch.no_grad():
            reconstructed = trainer.model(tensor)
            reconstruction_loss = float(torch.mean((tensor - reconstructed) ** 2, dim=1).numpy()[0])
            
        is_anomaly = reconstruction_loss > trainer.threshold
        
        return {
            "status": "success",
            "is_anomaly": is_anomaly,
            "reconstruction_loss": reconstruction_loss,
            "threshold": trainer.threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")

@app.get("/model/info")
def model_info():
    global trainer
    if not trainer or not trainer.model:
        return {"status": "uninitialized", "message": "Model not trained yet."}
        
    return {
        "status": "active",
        "input_features": trainer.model.encoder[0].in_features,
        "latent_dimension": trainer.latent_dim,
        "anomaly_threshold": trainer.threshold
    }

@app.get("/dataset/stats")
def dataset_stats():
    try:
        df = load_data_from_mongodb()
        stats = {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading stats: {str(e)}")

class AnalyzeRequest(BaseModel):
    telemetry: dict
    findings: List[dict]
    cloud_posture: Optional[dict] = None

@app.post("/ai/analyze")
def ai_analyze(req: AnalyzeRequest):
    findings_str = " ".join([f.get("title", "") for f in req.findings]).lower()
    
    threat_level = "LOW"
    confidence = 99.2
    primary_cause = "Normal System Operations"
    secondary_causes = []
    mitre = "N/A"
    business_impact = "None"
    urs_increase = 0
    recommended_playbook = []

    for f in req.findings:
        title = f.get("title", "")
        urs_increase += f.get("ursPenalty", 0)
        if f.get("mitigation"):
            recommended_playbook.append(f.get("mitigation"))
        secondary_causes.append(f"{title} ({f.get('category', 'Cloud')})")

    if "all traffic" in findings_str or "all-traffic" in findings_str:
        threat_level = "CRITICAL"
        primary_cause = "Wildcard 'All Traffic' ingress rule exposed publicly"
        mitre = "T1190"
        business_impact = "High"
        confidence = 98.6
    elif "ssh" in findings_str:
        threat_level = "HIGH"
        primary_cause = "SSH exposed to Internet (port 22)"
        mitre = "T1190"
        business_impact = "Medium"
        confidence = 97.2
    elif "rdp" in findings_str:
        threat_level = "CRITICAL"
        primary_cause = "RDP exposed to Internet (port 3389)"
        mitre = "T1110"
        business_impact = "High"
        confidence = 96.5
    elif "unencrypted" in findings_str:
        threat_level = "MEDIUM"
        primary_cause = "EBS storage volumes unencrypted"
        mitre = "T1486"
        business_impact = "Medium"
        confidence = 93.0
    elif len(req.findings) > 0:
        threat_level = "MEDIUM"
        primary_cause = req.findings[0].get("title", "Misconfigured AWS assets")
        mitre = "T1078"
        business_impact = "Low"
        confidence = 90.0

    return {
        "status": "success",
        "threatLevel": threat_level,
        "confidence": confidence,
        "primaryCause": primary_cause,
        "secondaryCauses": secondary_causes,
        "mitreMapping": mitre,
        "businessImpact": business_impact,
        "estimatedUrsIncrease": urs_increase,
        "recommendedPlaybook": recommended_playbook
    }
