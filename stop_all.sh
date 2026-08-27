#!/bin/bash

ROOT_DIR="$(pwd)"
PID_FILE="$ROOT_DIR/running_pids.txt"

if [ ! -f "$PID_FILE" ]; then
  echo "No running_pids.txt file found. Checking for lingering services on standard ports..."
  # Clean up ports if script wasn't used
  PORTS=(5000 5001 6001 7000 7001 8000 8005 8500 8600 8700 8800 8900 9000 9100 5173 27017)
  for port in "${PORTS[@]}"; do
    pid=$(lsof -t -i :$port)
    if [ ! -z "$pid" ]; then
      echo "Killing process $pid on port $port"
      kill -9 $pid 2>/dev/null
    fi
  done
  exit 0
fi

echo "=================================================="
echo "  Stopping all background services...             "
echo "=================================================="

# Read PIDs in reverse order and kill them
tail -r "$PID_FILE" | while IFS=: read -r pid name; do
  if [ ! -z "$pid" ]; then
    if kill -0 $pid 2>/dev/null; then
      echo "Stopping $name (PID $pid)..."
      kill $pid
      # Wait a second for graceful shutdown
      sleep 0.5
      if kill -0 $pid 2>/dev/null; then
        echo "Force killing $name (PID $pid)..."
        kill -9 $pid 2>/dev/null
      fi
    else
      echo "$name (PID $pid) already stopped."
    fi
  fi
done

rm -f "$PID_FILE"
echo "All processes stopped."
echo "=================================================="
