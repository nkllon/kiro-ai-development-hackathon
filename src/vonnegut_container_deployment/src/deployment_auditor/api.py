"""
Health monitoring API endpoints for Deployment Auditor.

Provides HTTP endpoints for health checks, readiness, and Prometheus metrics.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

from .core import DeploymentAuditor


class HealthAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health monitoring endpoints."""

    auditor: Optional[DeploymentAuditor] = None

    def do_GET(self):
        """Handle GET requests for health endpoints."""
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/ready":
            self._handle_ready()
        elif self.path == "/metrics":
            self._handle_metrics()
        else:
            self._handle_not_found()

    def _handle_health(self):
        """Handle /health endpoint."""
        try:
            if not self.auditor:
                self._send_error_response(503, "Auditor not initialized")
                return

            health = self.auditor.get_health_status()

            response = {
                "status": health.status.value,
                "module_id": health.module_id,
                "health_score": health.health_score,
                "uptime_seconds": health.uptime_seconds,
                "error_count": health.error_count,
                "warning_count": health.warning_count,
                "last_check": health.last_check.isoformat(),
                "issues": health.issues[-5:] if health.issues else []
            }

            self._send_json_response(200, response)

        except Exception as e:
            self._send_error_response(500, f"Health check failed: {e}")

    def _handle_ready(self):
        """Handle /ready endpoint."""
        try:
            if not self.auditor:
                self._send_error_response(503, "Auditor not initialized")
                return

            is_ready = self.auditor.is_ready()

            response = {
                "ready": is_ready,
                "timestamp": datetime.now().isoformat()
            }

            status_code = 200 if is_ready else 503
            self._send_json_response(status_code, response)

        except Exception as e:
            self._send_error_response(500, f"Readiness check failed: {e}")

    def _handle_metrics(self):
        """Handle /metrics endpoint (Prometheus format)."""
        try:
            if not self.auditor:
                self._send_error_response(503, "Auditor not initialized")
                return

            metrics = self.auditor.get_metrics()

            # Format as Prometheus text format
            lines = []
            for key, value in metrics.items():
                # Convert metric to Prometheus format
                if isinstance(value, (int, float)):
                    lines.append(f"{key} {value}")
                elif isinstance(value, dict):
                    # Handle nested metrics
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, (int, float)):
                            lines.append(f"{key}_{subkey} {subvalue}")

            prometheus_output = "\n".join(lines)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(prometheus_output.encode('utf-8'))

        except Exception as e:
            self._send_error_response(500, f"Metrics collection failed: {e}")

    def _handle_not_found(self):
        """Handle 404 Not Found."""
        response = {
            "error": "Not Found",
            "path": self.path,
            "available_endpoints": ["/health", "/ready", "/metrics"]
        }
        self._send_json_response(404, response)

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_error_response(self, status_code: int, message: str):
        """Send error response."""
        response = {
            "error": message,
            "timestamp": datetime.now().isoformat()
        }
        self._send_json_response(status_code, response)

    def log_message(self, format, *args):
        """Override to suppress request logging."""
        pass


class HealthAPIServer:
    """Health monitoring API server."""

    def __init__(self, auditor: DeploymentAuditor, host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize health API server.

        Args:
            auditor: DeploymentAuditor instance to monitor
            host: Host to bind to
            port: Port to listen on
        """
        self.auditor = auditor
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None

        # Set the auditor on the handler class
        HealthAPIHandler.auditor = auditor

    def start(self):
        """Start the health API server."""
        self.server = HTTPServer((self.host, self.port), HealthAPIHandler)
        print(f"Health API server started on {self.host}:{self.port}")
        print(f"Endpoints: /health, /ready, /metrics")
        self.server.serve_forever()

    def stop(self):
        """Stop the health API server."""
        if self.server:
            self.server.shutdown()
            print("Health API server stopped")


def run_health_api(auditor: DeploymentAuditor, host: str = "0.0.0.0", port: int = 8080):
    """
    Run the health API server.

    Args:
        auditor: DeploymentAuditor instance to monitor
        host: Host to bind to
        port: Port to listen on
    """
    server = HealthAPIServer(auditor, host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
