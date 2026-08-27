#!/bin/bash

# Configuration
export MONGO_URI="mongodb://127.0.0.1:27017/devsecops"
export JWT_SECRET="devsecops_jwt_secret_key"
export NODE_ENV="development"
export PORT=5001

ROOT_DIR="$(pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_FILE="$ROOT_DIR/running_pids.txt"

mkdir -p "$LOG_DIR"
rm -f "$PID_FILE"
touch "$PID_FILE"

echo "=================================================="
echo "  Starting DevSecOps SOAR Framework (Local macOS) "
echo "=================================================="

# Helper function to track PID
track_pid() {
  local pid=$1
  local name=$2
  echo "$pid:$name" >> "$PID_FILE"
}

# 1. MongoDB Memory Server (Port 27017)
echo "[1/14] Starting MongoDB Memory Server on port 27017..."
cd "$ROOT_DIR/scratch/scratch-db"
node db.js > "$LOG_DIR/mongodb.log" 2>&1 &
MONGO_PID=$!
track_pid $MONGO_PID "MongoDB Memory Server"

# Wait for MongoDB to start listening
echo "Waiting for MongoDB to initialize..."
for i in {1..15}; do
  if nc -z 127.0.0.1 27017; then
    echo "✔ MongoDB is ready."
    break
  fi
  sleep 1
done

if ! nc -z 127.0.0.1 27017; then
  echo "❌ MongoDB failed to start on port 27017. Check $LOG_DIR/mongodb.log."
  exit 1
fi

# 2. Backend Gateway (Port 5001)
echo "[2/14] Starting Backend Gateway on port 5001..."
cd "$ROOT_DIR/backend"
npm start > "$LOG_DIR/backend.log" 2>&1 &
track_pid $! "Backend Gateway"

# 3. Monitoring Service (Port 6001)
echo "[3/14] Starting Monitoring Service on port 6001..."
cd "$ROOT_DIR/monitoring-service"
PORT=6001 npm start > "$LOG_DIR/monitoring.log" 2>&1 &
track_pid $! "Monitoring Service"

# Python Services
PYTHON_EXEC="$ROOT_DIR/.venv/bin/python"

# 4. Cloud Adapter (Port 7001)
echo "[4/14] Starting Cloud Adapter on port 7001..."
cd "$ROOT_DIR/cloud-adapter"
$PYTHON_EXEC -m uvicorn src.main:app --port 7001 --host 127.0.0.1 > "$LOG_DIR/cloud-adapter.log" 2>&1 &
track_pid $! "Cloud Adapter"

# 5. AI Engine (Port 8000)
echo "[5/14] Starting AI Engine on port 8000..."
cd "$ROOT_DIR/ai-engine"
$PYTHON_EXEC -m uvicorn src.api.main:app --port 8000 --host 127.0.0.1 > "$LOG_DIR/ai-engine.log" 2>&1 &
track_pid $! "AI Engine"

# 6. Risk Engine (Port 8500)
echo "[6/14] Starting Risk Engine on port 8500..."
cd "$ROOT_DIR/risk-engine"
$PYTHON_EXEC -m uvicorn src.api.main:app --port 8500 --host 127.0.0.1 > "$LOG_DIR/risk-engine.log" 2>&1 &
track_pid $! "Risk Engine"

# 7. Attack Simulator (Port 8600)
echo "[7/14] Starting Attack Simulator on port 8600..."
cd "$ROOT_DIR/attack-simulator"
$PYTHON_EXEC -m uvicorn src.main:app --port 8600 --host 127.0.0.1 > "$LOG_DIR/attack-simulator.log" 2>&1 &
track_pid $! "Attack Simulator"

# 8. Policy Engine (Port 8700)
echo "[8/14] Starting Policy Engine on port 8700..."
cd "$ROOT_DIR/policy-engine"
$PYTHON_EXEC -m uvicorn src.main:app --port 8700 --host 127.0.0.1 > "$LOG_DIR/policy-engine.log" 2>&1 &
track_pid $! "Policy Engine"

# 9. Research Evaluator (Port 8800)
echo "[9/14] Starting Research Evaluator on port 8800..."
cd "$ROOT_DIR/research-evaluator"
$PYTHON_EXEC -m uvicorn src.main:app --port 8800 --host 127.0.0.1 > "$LOG_DIR/research-evaluator.log" 2>&1 &
track_pid $! "Research Evaluator"

# 10. Digital Twin (Port 8900)
echo "[10/14] Starting Digital Twin on port 8900..."
cd "$ROOT_DIR/digital-twin"
$PYTHON_EXEC -m uvicorn src.main:app --port 8900 --host 127.0.0.1 > "$LOG_DIR/digital-twin.log" 2>&1 &
track_pid $! "Digital Twin"

# 11. Report Generator (Port 9000)
echo "[11/14] Starting Report Generator on port 9000..."
cd "$ROOT_DIR/report-generator"
$PYTHON_EXEC -m uvicorn src.main:app --port 9000 --host 127.0.0.1 > "$LOG_DIR/report-generator.log" 2>&1 &
track_pid $! "Report Generator"

# 12. Prediction Engine (Port 8005)
echo "[12/14] Starting Prediction Engine on port 8005..."
cd "$ROOT_DIR/prediction-engine"
$PYTHON_EXEC -m uvicorn src.prediction_api:app --port 8005 --host 127.0.0.1 > "$LOG_DIR/prediction-engine.log" 2>&1 &
track_pid $! "Prediction Engine"

# 13. Automation Engine (Port 9100)
echo "[13/14] Starting Automation Engine on port 9100..."
cd "$ROOT_DIR/automation-engine"
$PYTHON_EXEC -m uvicorn src.main:app --port 9100 --host 127.0.0.1 > "$LOG_DIR/automation-engine.log" 2>&1 &
track_pid $! "Automation Engine"

# 14. Dashboard React UI (Port 5173)
echo "[14/14] Starting Dashboard React UI on port 5173..."
cd "$ROOT_DIR/dashboard"
npm run dev > "$LOG_DIR/dashboard.log" 2>&1 &
track_pid $! "Dashboard UI"

echo "--------------------------------------------------"
echo " Waiting for services to initialize..."
sleep 25

echo "Performing quick service health checks:"
SERVICES=(
  "5001:Backend Gateway"
  "6001:Telemetry Ingestor"
  "7001:Cloud Adapter"
  "8000:AI Engine"
  "8005:Prediction Engine"
  "8500:Risk Engine"
  "8600:Attack Simulator"
  "8700:Policy Engine"
  "8800:Research Evaluator"
  "8900:Digital Twin"
  "9000:Report Generator"
  "9100:Automation Engine"
  "5173:Dashboard UI"
)

ALL_OK=true
for svc in "${SERVICES[@]}"; do
  PORT="${svc%%:*}"
  NAME="${svc#*:}"
  if nc -z 127.0.0.1 $PORT; then
    echo "✔ [OK] $NAME listening on port $PORT."
  else
    echo "❌ [FAILED] $NAME not responding on port $PORT. Check $LOG_DIR logs."
    ALL_OK=false
  fi
done

if [ "$ALL_OK" = true ]; then
  echo "=================================================="
  echo " All services started successfully!"
  echo " Dashboard UI is available at: http://localhost:5173"
  echo "=================================================="
else
  echo "=================================================="
  echo " WARNING: Some services failed to start or respond."
  echo " Please check files in $LOG_DIR/ for details."
  echo "=================================================="
fi
