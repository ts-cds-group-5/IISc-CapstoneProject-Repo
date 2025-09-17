#!/bin/bash
# Script to start the FastAPI server with uv3135 virtual environment

cd "$(dirname "$0")"
source uv3135/bin/activate
cd server
echo "Starting FastAPI server with uv3135 virtual environment..."
echo "Logs will be displayed in this terminal..."
echo "==============================================="
fastapi dev server_api.py
