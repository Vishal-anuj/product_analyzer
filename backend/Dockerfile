# === Backend Dockerfile ===
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files first (better caching)
COPY backend/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY backend/ /app/

# Expose FastAPI port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
