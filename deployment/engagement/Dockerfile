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
COPY scripts/start_engagement_manager.py .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Expose ports
EXPOSE 8891

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8891/health || exit 1

# Run Engagement Manager service
CMD ["python", "start_engagement_manager.py"]