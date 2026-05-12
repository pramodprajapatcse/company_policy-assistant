#!/bin/bash
set -e

# Start the backend (if needed) and then the Streamlit frontend.
# If you do not want the backend to run in the same container, remove the backend startup.
python app/main.py &

# Give the backend a moment to start before launching the UI.
sleep 2

exec streamlit run app/frontend/streamlit_app.py --server.port "${PORT:-8000}" --server.address 0.0.0.0
