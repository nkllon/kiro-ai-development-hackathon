# Beast Mode Metrics Exporter
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only what we need for metrics
COPY src/ ./src/
COPY pyproject.toml .
COPY deployment/beast-mode-metrics/start_metrics.py .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 metrics && chown -R metrics:metrics /app
USER metrics

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/metrics || exit 1

# Expose metrics port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PROMETHEUS_PORT=8000
ENV BEAST_MODE_PROMETHEUS_ENABLED=true

# Start Beast Mode metrics exporter
CMD ["python", "start_metrics.py"]