FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install uv

# Install the Google Workspace MCP server
RUN uv tool install workspace-mcp

# Create non-root user
RUN useradd -m -u 1000 mcpuser
USER mcpuser

# Expose the MCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the server in HTTP mode
CMD ["uvx", "workspace-mcp", "--tools", "calendar", "--transport", "streamable-http", "--single-user"]