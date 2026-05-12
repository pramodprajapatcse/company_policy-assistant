#!/bin/bash
set -e

# Choose ports for backend and Streamlit.
API_PORT=${API_PORT:-8000}
STREAMLIT_PORT=${PORT:-8501}

if [ "$API_PORT" = "$STREAMLIT_PORT" ]; then
  API_PORT=8001
fi

export API_PORT
export API_URL="http://127.0.0.1:${API_PORT}/api/v1"
export PYTHONPATH="/app"

python -m app.main &
backend_pid=$!

# Wait for backend to become available.
for i in {1..30}; do
  if python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + '${API_PORT}' + '/api', timeout=5)" >/dev/null 2>&1; then
    break
  fi
  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "Backend did not start in time" >&2
    exit 1
  fi
done

exec streamlit run app/frontend/streamlit_app.py --server.port "$STREAMLIT_PORT" --server.address 0.0.0.0
