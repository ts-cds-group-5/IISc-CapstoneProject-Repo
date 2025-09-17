#!/bin/bash
# Script to start the Streamlit UI with uv3135 virtual environment

cd "$(dirname "$0")"
source uv3135/bin/activate
cd chatUI
echo "🚀 Starting Streamlit UI with uv3135 virtual environment..."
echo "Logs will be displayed in this terminal..."
echo "==============================================="
streamlit run streamlit-ui.py
