FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Copy application
COPY app/ ./app/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p /app/data/processed /app/logs

# Expose port
EXPOSE 8000

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}