# MSP SSL Chaos Tamer - Docker Container
# Multi-stage build for optimized production image

# Build stage
FROM python:3.9-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /build

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY README.md .

# Install the application
RUN pip install --no-cache-dir --user .

# Production stage
FROM python:3.9-slim

# Set metadata labels
LABEL maintainer="MSP SSL Chaos Tamer Team" \
      org.label-schema.name="msp-ssl-chaos-tamer" \
      org.label-schema.description="Zero-trust certificate management for MSPs" \
      org.label-schema.version="${VERSION}" \
      org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.schema-version="1.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r mspssl && useradd -r -g mspssl -d /app -s /bin/bash mspssl

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/mspssl/.local

# Copy application files
COPY --from=builder /build/src ./src
COPY docker-entrypoint.sh .
COPY healthcheck.sh .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config /app/backups \
    && chown -R mspssl:mspssl /app \
    && chmod +x docker-entrypoint.sh healthcheck.sh

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    MSP_SSL_DATA_DIR=/app/data \
    MSP_SSL_LOG_DIR=/app/logs \
    MSP_SSL_CONFIG_DIR=/app/config \
    MSP_SSL_BACKUP_DIR=/app/backups \
    PATH=/home/mspssl/.local/bin:$PATH

# Switch to non-root user
USER mspssl

# Expose ports
EXPOSE 8080 8443 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ./healthcheck.sh

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["server"]