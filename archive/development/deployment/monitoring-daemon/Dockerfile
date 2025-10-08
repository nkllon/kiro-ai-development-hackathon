FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/logs /tmp

# Expose monitoring daemon port
EXPOSE 8000

# Health check - daemon exposes /metrics endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/metrics || exit 1

# Run monitoring daemon
CMD ["python", "-m", "src.beast_mode.monitoring.daemon", "--start", "--foreground", "--port", "8000"]
