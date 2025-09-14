#!/usr/bin/env python3
"""
Beast Mode Metrics Server - macOS Compatible
===========================================

Simple HTTP server to expose Beast Mode Prometheus metrics
optimized for macOS walled garden restrictions.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Expose metrics via HTTP for Prometheus scraping on macOS
"""

import sys
import os
import time
import logging
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set macOS restricted mode
os.environ['BEAST_MODE_RESTRICTED_MODE'] = 'true'

from beast_mode.monitoring.prometheus_config import get_prometheus_config


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for metrics endpoint."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/metrics':
            self.handle_metrics()
        elif parsed_path.path == '/health':
            self.handle_health()
        else:
            self.send_error(404, "Not Found")
    
    def handle_metrics(self):
        """Handle /metrics endpoint."""
        try:
            # Generate macOS-compatible metrics
            current_time = int(time.time())
            uptime = current_time - self.server.start_time
            
            response = f"""# HELP beast_mode_info Beast Mode framework information
# TYPE beast_mode_info gauge
beast_mode_info{{version="1.0.0",framework="beast-mode",platform="macos"}} 1

# HELP beast_mode_uptime_seconds Beast Mode uptime in seconds
# TYPE beast_mode_uptime_seconds gauge
beast_mode_uptime_seconds{{service="metrics-server",platform="macos"}} {uptime}

# HELP beast_mode_requests_total Total number of requests
# TYPE beast_mode_requests_total counter
beast_mode_requests_total{{endpoint="/metrics",platform="macos"}} 1

# HELP beast_mode_platform_info Platform information
# TYPE beast_mode_platform_info gauge
beast_mode_platform_info{{platform="{platform.system().lower()}",version="{platform.release()}",architecture="{platform.machine()}"}} 1

# HELP beast_mode_restricted_mode Beast Mode restricted mode status
# TYPE beast_mode_restricted_mode gauge
beast_mode_restricted_mode{{enabled="true",reason="macos-walled-garden"}} 1

# HELP beast_mode_metrics_available Beast Mode metrics availability
# TYPE beast_mode_metrics_available gauge
beast_mode_metrics_available{{type="basic",status="operational"}} 1
"""
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def handle_health(self):
        """Handle /health endpoint."""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": time.time(),
                "service": "beast-mode-metrics-macos",
                "platform": platform.system().lower(),
                "restricted_mode": True,
                "uptime_seconds": int(time.time()) - self.server.start_time
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            import json
            self.wfile.write(json.dumps(health_data).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Health check failed: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to reduce logging noise."""
        pass


class MacOSMetricsServer(HTTPServer):
    """Custom HTTP server with start time tracking."""
    
    def __init__(self, *args, **kwargs):
        self.start_time = int(time.time())
        super().__init__(*args, **kwargs)


def main():
    """Main function to start the macOS-compatible metrics server."""
    print("Starting Beast Mode Metrics Server (macOS Compatible)...")
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('beast_mode_metrics_server_macos')
    
    try:
        # Get configuration
        config = get_prometheus_config()
        logger.info(f"Configuration loaded: {config.mode.value} mode")
        logger.info(f"Platform: {platform.system()} {platform.release()}")
        logger.info("Running in macOS restricted mode")
        
        # Start HTTP server
        port = int(os.getenv('BEAST_MODE_METRICS_PORT', '8001'))
        host = os.getenv('BEAST_MODE_METRICS_HOST', '0.0.0.0')
        
        httpd = MacOSMetricsServer((host, port), MetricsHandler)
        
        logger.info(f"Metrics server starting on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  http://{host}:{port}/metrics - Prometheus metrics")
        logger.info(f"  http://{host}:{port}/health - Health check")
        logger.info("macOS walled garden restrictions applied")
        
        # Start server
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutting down metrics server...")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
