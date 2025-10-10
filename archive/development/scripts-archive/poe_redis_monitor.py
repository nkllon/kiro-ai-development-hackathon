#!/usr/bin/env python3
"""
Poe Redis Monitor - Lightweight monitoring service for Beast Mode data
Acts as backup/alternative to Docker-based monitoring
"""

import redis
import time
import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedisMonitor:
    def __init__(self, redis_host='192.168.1.146', redis_port=6379, redis_password=os.getenv('REDIS_PASSWORD', '')):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_client = None
        self.metrics = {}
        self.last_update = None
        
    def connect_redis(self):
        """Connect to Redis with error handling."""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    def collect_metrics(self):
        """Collect Beast Mode metrics from Redis."""
        if not self.redis_client:
            if not self.connect_redis():
                return
        
        try:
            # Get all keys
            all_keys = self.redis_client.keys('*')
            
            # Analyze Beast Mode patterns
            checkin_keys = [k for k in all_keys if 'checkin' in k.lower()]
            execution_keys = [k for k in all_keys if 'execution' in k.lower()]
            project_keys = [k for k in all_keys if 'project' in k.lower()]
            
            # Count active projects (unique project identifiers)
            project_ids = set()
            for key in all_keys:
                if 'project' in key.lower() or 'beast_mode' in key.lower():
                    # Extract project ID patterns
                    parts = key.split(':')
                    if len(parts) > 1:
                        project_ids.add(parts[0])
            
            # Update metrics
            self.metrics = {
                'beast_mode_checkins_total': len(checkin_keys),
                'beast_mode_executions_total': len(execution_keys),
                'beast_mode_active_projects': len(project_ids),
                'beast_mode_total_keys': len(all_keys),
                'beast_mode_active_executions': 0,  # Could be enhanced to check TTL
                'beast_mode_recent_checkins': 0,    # Could be enhanced with timestamps
                'timestamp': datetime.now().isoformat(),
                'source': 'poe-monitor'
            }
            
            self.last_update = datetime.now()
            logger.info(f"Metrics updated: {len(all_keys)} total keys, {len(project_ids)} projects")
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            # Try to reconnect
            self.redis_client = None

class MonitorHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, monitor, *args, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle HTTP GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_health_response()
        elif parsed_path.path == '/metrics':
            self.send_metrics_response()
        elif parsed_path.path == '/prometheus':
            self.send_prometheus_response()
        elif parsed_path.path == '/':
            self.send_dashboard_response()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send health check response."""
        health_status = {
            'status': 'healthy' if self.monitor.redis_client else 'unhealthy',
            'last_update': self.monitor.last_update.isoformat() if self.monitor.last_update else None,
            'redis_host': self.monitor.redis_host,
            'service': 'poe-redis-monitor'
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health_status, indent=2).encode())
    
    def send_metrics_response(self):
        """Send metrics in JSON format."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(self.monitor.metrics, indent=2).encode())
    
    def send_prometheus_response(self):
        """Send metrics in Prometheus format."""
        prometheus_metrics = []
        
        for key, value in self.monitor.metrics.items():
            if key not in ['timestamp', 'source'] and isinstance(value, (int, float)):
                prometheus_metrics.append(f"{key} {value}")
        
        prometheus_text = "\n".join(prometheus_metrics) + "\n"
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(prometheus_text.encode())
    
    def send_dashboard_response(self):
        """Send simple HTML dashboard."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Poe Redis Monitor</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
                .status {{ color: {'green' if self.monitor.redis_client else 'red'}; }}
            </style>
        </head>
        <body>
            <h1>🐺 Poe Redis Monitor</h1>
            <p class="status">Status: {'Connected' if self.monitor.redis_client else 'Disconnected'}</p>
            <p>Last Update: {self.monitor.last_update or 'Never'}</p>
            
            <h2>Beast Mode Metrics</h2>
        """
        
        for key, value in self.monitor.metrics.items():
            if key not in ['timestamp', 'source']:
                display_name = key.replace('beast_mode_', '').replace('_', ' ').title()
                html += f"""
                <div class="metric">
                    <div>{display_name}</div>
                    <div class="value">{value}</div>
                </div>
                """
        
        html += """
            <h2>API Endpoints</h2>
            <ul>
                <li><a href="/health">/health</a> - Health check</li>
                <li><a href="/metrics">/metrics</a> - JSON metrics</li>
                <li><a href="/prometheus">/prometheus</a> - Prometheus format</li>
            </ul>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")

def create_handler(monitor):
    """Create HTTP handler with monitor instance."""
    def handler(*args, **kwargs):
        return MonitorHTTPHandler(monitor, *args, **kwargs)
    return handler

def main():
    """Main monitoring service."""
    logger.info("Starting Poe Redis Monitor...")
    
    # Create monitor
    monitor = RedisMonitor()
    
    # Start metrics collection thread
    def metrics_loop():
        while True:
            monitor.collect_metrics()
            time.sleep(30)  # Update every 30 seconds
    
    metrics_thread = threading.Thread(target=metrics_loop, daemon=True)
    metrics_thread.start()
    
    # Start HTTP server
    server_port = 8080
    handler = create_handler(monitor)
    httpd = HTTPServer(('0.0.0.0', server_port), handler)
    
    logger.info(f"Poe Redis Monitor running on http://0.0.0.0:{server_port}")
    logger.info("Endpoints:")
    logger.info("  http://192.168.1.104:8080/ - Dashboard")
    logger.info("  http://192.168.1.104:8080/health - Health check")
    logger.info("  http://192.168.1.104:8080/metrics - JSON metrics")
    logger.info("  http://192.168.1.104:8080/prometheus - Prometheus format")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Poe Redis Monitor...")
        httpd.shutdown()

if __name__ == "__main__":
    main()