#!/bin/bash
# MSP SSL Chaos Tamer - Health Check Script

set -e

# Configuration
HEALTH_URL="http://localhost:8080/health"
TIMEOUT=5

# Check if the main service is responding
if curl -f -s --max-time $TIMEOUT "$HEALTH_URL" > /dev/null 2>&1; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed"
    exit 1
fi