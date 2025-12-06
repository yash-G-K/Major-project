# Dockerfile for AI Skin Analysis & Cosmetics Recommendation System
# Targeting Python 3.11 (stable for TensorFlow 2.15 + OpenCV wheels)

FROM python:3.11-slim

# Prevent interactive tzdata prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for OpenCV (basic image libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libgomp1 \
        libglib2.0-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency spec first (better layer caching)
COPY requirements-cloud.txt requirements.txt

# Install dependencies (no cache to reduce image size)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py ./
COPY enhanced_cosmetics.csv ./
COPY templates ./templates
COPY static ./static

# Expose Flask default port
EXPOSE 5000

# Healthcheck (simple TCP check)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',5000)); s.close()" || exit 1

# Run the application
CMD ["python", "app.py"]
