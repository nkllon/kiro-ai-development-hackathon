#!/bin/bash

# Test the MCP server properly via stdio
echo "Testing Google Calendar MCP Server..."

# Build and run container for testing
docker-compose build google-calendar-mcp

# Test MCP initialize
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | \
docker run --rm -i \
  -v $(pwd)/credentials:/app/credentials:ro \
  google-calendar-mcp-google-calendar-mcp \
  timeout 5 google-calendar-mcp

echo "MCP test complete."