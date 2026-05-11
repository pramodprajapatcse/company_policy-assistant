FROM python:3.9-slim

WORKDIR /app

# Reduce CPU thread usage in containerized environments
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV TORCH_NUM_THREADS=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Download NLTK data during build
RUN python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Copy application
COPY app/ ./app/
COPY data/ ./data/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p /app/data/processed /app/logs

# Expose port
EXPOSE 8000

# Copy startup script and make sure it can run
COPY ./docker/start.sh ./start.sh
RUN chmod +x ./start.sh

# Run the startup script that launches FastAPI and Streamlit together
CMD ["bash", "./start.sh"]