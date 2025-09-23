# Google Calendar MCP Server - Using Existing Implementation
# Beast Mode compliant containerization of proven MCP server

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

# Install the proven Google Calendar MCP server
# Using @cocal/google-calendar-mcp which has extensive features and recent updates
RUN npm install -g @cocal/google-calendar-mcp@1.4.9

# Create necessary directories
RUN mkdir -p /app/credentials /app/logs /app/tokens

# Set proper permissions for credentials
RUN chmod 700 /app/credentials /app/tokens

# Create a simple wrapper script for Beast Mode compliance
COPY <<EOF /app/start-server.sh
#!/bin/sh

# Beast Mode startup logging
echo "$(date): Starting Google Calendar MCP Server (Beast Mode compliant)"
echo "$(date): Server: @cocal/google-calendar-mcp@1.4.9"
echo "$(date): Port: \${GOOGLE_CALENDAR_PORT:-3000}"
echo "$(date): Credentials: \${GOOGLE_OAUTH_CREDENTIALS}"

# Create config directory for the user
mkdir -p /home/mcpuser/.config/google-calendar-mcp

# Set up credentials in the user's config directory
if [ -f "\${GOOGLE_OAUTH_CREDENTIALS}" ]; then
    echo "$(date): Setting up credentials in user config directory"
    cp "\${GOOGLE_OAUTH_CREDENTIALS}" /home/mcpuser/.config/google-calendar-mcp/gcp-oauth.keys.json
    chmod 600 /home/mcpuser/.config/google-calendar-mcp/gcp-oauth.keys.json
    
    # Set environment variable for the MCP server
    export GOOGLE_OAUTH_CREDENTIALS=/home/mcpuser/.config/google-calendar-mcp/gcp-oauth.keys.json
else
    echo "$(date): WARNING - No credentials file found at \${GOOGLE_OAUTH_CREDENTIALS}"
    echo "$(date): Server will run in stub mode"
fi

# Start the MCP server with proper environment
exec google-calendar-mcp
EOF

RUN chmod +x /app/start-server.sh

# Expose MCP port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-oauth.keys.json

# Run as non-root user for security
RUN addgroup -g 1001 -S mcpuser && \
    adduser -S mcpuser -u 1001 -G mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Start the server
CMD ["/app/start-server.sh"]