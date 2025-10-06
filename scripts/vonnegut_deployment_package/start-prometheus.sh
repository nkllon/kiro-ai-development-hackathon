#!/bin/bash
"""
Start Prometheus Monitoring Daemon
=================================

Simple daemon script to run Prometheus metrics server.
No embedding, no singleton patterns, just a clean daemon process.
"""

set -e

PROMETHEUS_PORT=${PROMETHEUS_PORT:-8000}
PROMETHEUS_PID_FILE="/tmp/beast_mode_prometheus.pid"
PROMETHEUS_LOG_FILE="/tmp/beast_mode_prometheus.log"

echo "🚀 Starting Beast Mode Prometheus Daemon"
echo "Port: $PROMETHEUS_PORT"
echo "PID File: $PROMETHEUS_PID_FILE"
echo "Log File: $PROMETHEUS_LOG_FILE"

# Check if already running
if [ -f "$PROMETHEUS_PID_FILE" ]; then
    PID=$(cat "$PROMETHEUS_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Prometheus daemon already running (PID: $PID)"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file"
        rm -f "$PROMETHEUS_PID_FILE"
    fi
fi

# Start the daemon
echo "🔄 Starting Prometheus metrics server..."
nohup uv run python -c "
import time
import logging
from src.beast_mode.monitoring.prometheus_exporter import PrometheusExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('prometheus_daemon')

logger.info('Starting Prometheus daemon on port $PROMETHEUS_PORT')

# Create single exporter instance
exporter = PrometheusExporter(port=$PROMETHEUS_PORT, enable_http_server=True)

logger.info('Prometheus daemon started - serving metrics at http://localhost:$PROMETHEUS_PORT/metrics')

# Keep daemon running
try:
    while True:
        time.sleep(60)  # Sleep for 1 minute
        logger.debug('Prometheus daemon heartbeat')
except KeyboardInterrupt:
    logger.info('Prometheus daemon shutting down')
except Exception as e:
    logger.error(f'Prometheus daemon error: {e}')
    raise
" > "$PROMETHEUS_LOG_FILE" 2>&1 &

# Save PID
echo $! > "$PROMETHEUS_PID_FILE"

echo "✅ Prometheus daemon started (PID: $(cat $PROMETHEUS_PID_FILE))"
echo "📊 Metrics available at: http://localhost:$PROMETHEUS_PORT/metrics"
echo "📋 Logs: tail -f $PROMETHEUS_LOG_FILE"
echo "🛑 Stop with: ./scripts/stop-prometheus.sh"