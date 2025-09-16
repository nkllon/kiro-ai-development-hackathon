#!/usr/bin/env python3
"""
Beast Mode Metrics Server
========================

Simple HTTP server to expose Beast Mode Prometheus metrics
through the nginx reverse proxy setup.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Expose metrics via HTTP for Prometheus scraping
"""

import sys
import os
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from beast_mode.monitoring.prometheus_exporter import PrometheusExporter
from beast_mode.monitoring.prometheus_config import get_prometheus_config


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for metrics endpoint."""

    def __init__(self, *args, prometheus_exporter=None, **kwargs):
        self.prometheus_exporter = prometheus_exporter
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/metrics":
            self.handle_metrics()
        elif parsed_path.path == "/health":
            self.handle_health()
        else:
            self.send_error(404, "Not Found")

    def handle_metrics(self):
        """Handle /metrics endpoint."""
        try:
            if self.prometheus_exporter:
                # Get metrics from Prometheus exporter
                metrics_data = self.prometheus_exporter.get_metrics_summary()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()

                # For now, return a simple metrics format
                # In a real implementation, you'd use generate_latest()
                response = f"""# HELP beast_mode_info Beast Mode framework information
# TYPE beast_mode_info gauge
beast_mode_info{{version="1.0.0",framework="beast-mode"}} 1

# HELP beast_mode_uptime_seconds Beast Mode uptime in seconds
# TYPE beast_mode_uptime_seconds gauge
beast_mode_uptime_seconds{{service="metrics-server"}} {int(time.time())}

# HELP beast_mode_requests_total Total number of requests
# TYPE beast_mode_requests_total counter
beast_mode_requests_total{{endpoint="/metrics"}} 1
"""
                self.wfile.write(response.encode("utf-8"))
            else:
                self.send_error(503, "Prometheus exporter not available")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

    def handle_health(self):
        """Handle /health endpoint."""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": time.time(),
                "service": "beast-mode-metrics",
                "prometheus_available": self.prometheus_exporter is not None,
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            import json

            self.wfile.write(json.dumps(health_data).encode("utf-8"))
        except Exception as e:
            self.send_error(500, f"Health check failed: {str(e)}")

    def log_message(self, format, *args):
        """Override to reduce logging noise."""
        pass


def create_handler(prometheus_exporter):
    """Create a handler with the Prometheus exporter."""

    def handler(*args, **kwargs):
        return MetricsHandler(*args, prometheus_exporter=prometheus_exporter, **kwargs)

    return handler


def main():
    """Main function to start the metrics server."""
    print("Starting Beast Mode Metrics Server...")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("beast_mode_metrics_server")

    try:
        # Get configuration
        config = get_prometheus_config()
        logger.info(f"Configuration loaded: {config.mode.value} mode")

        # Initialize Prometheus exporter
        prometheus_exporter = None
        if config.enabled:
            try:
                prometheus_exporter = PrometheusExporter(
                    port=8001,  # Use different port to avoid conflicts
                    enable_http_server=False,  # We'll handle HTTP ourselves
                )
                logger.info("Prometheus exporter initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Prometheus exporter: {e}")

        # Start HTTP server
        port = int(os.getenv("BEAST_MODE_METRICS_PORT", "8001"))
        host = os.getenv("BEAST_MODE_METRICS_HOST", "0.0.0.0")

        handler_class = create_handler(prometheus_exporter)
        httpd = HTTPServer((host, port), handler_class)

        logger.info(f"Metrics server starting on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  http://{host}:{port}/metrics - Prometheus metrics")
        logger.info(f"  http://{host}:{port}/health - Health check")

        # Start server
        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info("Shutting down metrics server...")
        if prometheus_exporter:
            prometheus_exporter.stop_metrics_export()
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
