# Google Calendar MCP Integration - Docker Container
FROM python:3.9-slim

# Security: Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/google-calendar-mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY docker/google-calendar-mcp/entrypoint.sh ./entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/credentials /app/logs /app/cache && \
    chown -R mcp:mcp /app

# Make entrypoint executable
RUN chmod +x ./entrypoint.sh

# Security: Switch to non-root user
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${GOOGLE_CALENDAR_PORT:-3000}/health || exit 1

# Expose port
EXPOSE 3000

# Set environment variables
ENV PYTHONPATH=/app
ENV GOOGLE_CALENDAR_PORT=3000
ENV GOOGLE_CALENDAR_LOG_LEVEL=info

# Start the MCP server
ENTRYPOINT ["./entrypoint.sh"]