#!/usr/bin/env bash
set -e

# Start the FastAPI backend on port 8000 in the background.
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit frontend on the Render-assigned port.
streamlit run app/frontend/streamlit_app.py --server.port "${PORT:-3000}" --server.address 0.0.0.0
