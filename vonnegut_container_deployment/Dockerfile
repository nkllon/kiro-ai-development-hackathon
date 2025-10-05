# Cloudflare Custom Error Pages CLI - Docker Container
# ===================================================

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY cloudflare-error-pages-cli.py .
COPY cloudflare-config.yaml .
COPY verify_deployment.py .
COPY cloudflare/ ./cloudflare/

# Make CLI executable
RUN chmod +x cloudflare-error-pages-cli.py

# Create directories for logs and backups
RUN mkdir -p logs backups temp

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default command
ENTRYPOINT ["./cloudflare-error-pages-cli.py"]
CMD ["--help"]

# Labels
LABEL maintainer="Kiro AI Assistant"
LABEL description="Cloudflare Custom Error Pages CLI"
LABEL version="1.0.0"