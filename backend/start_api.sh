#!/bin/bash

# Start the FastAPI backend server
# Usage: ./start_api.sh [--reload] [--port PORT]

# Default values
PORT=8000
RELOAD=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --reload)
      RELOAD="--reload"
      shift
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./start_api.sh [--reload] [--port PORT]"
      exit 1
      ;;
  esac
done

echo "Starting Mock Web3 Wallet API..."
echo "Port: $PORT"
echo "Reload: ${RELOAD:-disabled}"
echo ""
echo "API Documentation will be available at:"
echo "  - Swagger UI: http://localhost:$PORT/docs"
echo "  - ReDoc: http://localhost:$PORT/redoc"
echo ""

# Start the server
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT $RELOAD
