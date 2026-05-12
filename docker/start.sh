#!/bin/bash
set -e

# Required Render port for the public web process
if [ -z "$PORT" ]; then
  echo "ERROR: Render did not provide PORT environment variable" >&2
  exit 1
fi

API_PORT=${API_PORT:-8000}
STREAMLIT_PORT=${PORT}

if [ "$API_PORT" = "$STREAMLIT_PORT" ]; then
  API_PORT=8001
fi

export API_PORT
export API_URL="http://127.0.0.1:${API_PORT}/api/v1"
export PYTHONPATH="/app"

echo "Starting backend on http://127.0.0.1:${API_PORT}"
echo "Starting Streamlit on http://0.0.0.0:${STREAMLIT_PORT}"

python -m app.main &
backend_pid=$!
trap "kill $backend_pid" EXIT

# Start Streamlit immediately so Render can detect the public port quickly.
exec streamlit run app/frontend/streamlit_app.py --server.port "$STREAMLIT_PORT" --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false
