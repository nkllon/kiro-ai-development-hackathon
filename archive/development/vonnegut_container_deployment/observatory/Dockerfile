FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and run import validation script
COPY deployment/observatory/validate_imports.py .
RUN python3 validate_imports.py

# Copy source code
COPY src/ ./src/
COPY start_observatory.py .
COPY start_observatory_minimal.py .
COPY start_observatory_diagnostic.py .
COPY scripts/start_observatory_cross_platform.py ./scripts/

# Copy templates and static files for web interface
COPY src/beast_mode/observatory/templates/ ./src/beast_mode/observatory/templates/

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Expose ports
EXPOSE 8888 8889 8890

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Run Observatory service with diagnostic logging
CMD ["python", "start_observatory_diagnostic.py"]
