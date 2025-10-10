# Beast Mode AI Development Framework - Production Container
# ========================================================
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim AS builder

# Set build arguments
ARG BUILD_ENV=production
ARG INSTALL_DEV=false

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt ./
COPY requirements-dev.txt ./

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Install development dependencies if requested
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --user --no-warn-script-location -r requirements-dev.txt; \
    fi

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser examples/ ./examples/
COPY --chown=appuser:appuser docs/ ./docs/

# Create scripts directory and copy validator
RUN mkdir -p ./scripts
COPY --chown=appuser:appuser scripts/installation_validator.py ./scripts/

# Copy configuration files
COPY --chown=appuser:appuser pyproject.toml ./

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8080 9090 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 scripts/installation_validator.py --quick || exit 1

# Default command
CMD ["python3", "-m", "src.beast_mode.api.main"]

# Labels
LABEL maintainer="Beast Mode Framework Team" \
      description="Beast Mode AI Development Framework" \
      version="1.0.0" \
      org.opencontainers.image.title="Beast Mode AI Framework" \
      org.opencontainers.image.description="AI-Powered Spec-Driven Development Framework" \
      org.opencontainers.image.vendor="Beast Mode Framework" \
      org.opencontainers.image.licenses="MIT"