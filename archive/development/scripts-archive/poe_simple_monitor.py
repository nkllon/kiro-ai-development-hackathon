#!/usr/bin/env python3
"""
Poe Simple Monitor - Basic monitoring service using only standard library
Acts as backup/alternative to Docker-based monitoring
"""

import socket
import time
import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleRedisClient:
    """Basic Redis client using raw sockets."""
    
    def __init__(self, host='192.168.1.146', port=6379, password=os.getenv('REDIS_PASSWORD', '')):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
    
    def connect(self):
        """Connect to Redis server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            
            # Authenticate if password provided
            if self.password:
                auth_cmd = f"AUTH {self.password}\r\n"
                self.socket.send(auth_cmd.encode())
                response = self.socket.recv(1024).decode()
                if not response.startswith('+OK'):
                    raise Exception(f"Authentication failed: {response}")
            
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def send_command(self, command):
        """Send Redis command and get response."""
        if not self.socket:
            if not self.connect():
                return None
        
        try:
            self.socket.send(f"{command}\r\n".encode())
            response = self.socket.recv(4096).decode()
            return response
        except Exception as e:
            logger.error(f"Command failed: {e}")
            self.socket = None
            return None
    
    def keys(self, pattern='*'):
        """Get keys matching pattern."""
        response = self.send_command(f"KEYS {pattern}")
        if not response or not response.startswith('*'):
            return []
        
        # Parse Redis array response
        lines = response.strip().split('\r\n')
        if len(lines) < 2:
            return []
        
        count = int(lines[0][1:])  # Remove '*' prefix
        keys = []
        for i in range(1, min(count + 1, len(lines))):
            if lines[i].startswith('$'):
                # Next line contains the key
                if i + 1 < len(lines):
                    keys.append(lines[i + 1])
        
        return keys
    
    def ping(self):
        """Test connection."""
        response = self.send_command("PING")
        return response and response.startswith('+PONG')

class SimpleMonitor:
    def __init__(self):
        self.redis_client = SimpleRedisClient()
        self.metrics = {}
        self.last_update = None
        
    def collect_metrics(self):
        """Collect basic metrics from Redis."""
        try:
            # Test connection
            if not self.redis_client.ping():
                logger.warning("Redis connection test failed")
                return
            
            # Get all keys
            all_keys = self.redis_client.keys('*')
            if not all_keys:
                all_keys = []
            
            # Analyze patterns (basic string matching)
            checkin_count = sum(1 for k in all_keys if 'checkin' in k.lower())
            execution_count = sum(1 for k in all_keys if 'execution' in k.lower())
            project_count = sum(1 for k in all_keys if 'project' in k.lower())
            
            # Count unique project prefixes
            project_ids = set()
            for key in all_keys:
                if ':' in key:
                    prefix = key.split(':')[0]
                    if any(word in prefix.lower() for word in ['beast', 'project', 'execution']):
                        project_ids.add(prefix)
            
            # Update metrics
            self.metrics = {
                'beast_mode_checkins_total': checkin_count,
                'beast_mode_executions_total': execution_count,
                'beast_mode_active_projects': len(project_ids),
                'beast_mode_total_keys': len(all_keys),
                'beast_mode_active_executions': 0,
                'beast_mode_recent_checkins': 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'poe-simple-monitor'
            }
            
            self.last_update = datetime.now()
            logger.info(f"Metrics updated: {len(all_keys)} keys, {len(project_ids)} projects")
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

class MonitorHandler(BaseHTTPRequestHandler):
    monitor = None  # Will be set by server
    
    def do_GET(self):
        """Handle HTTP GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_health()
        elif parsed_path.path == '/metrics':
            self.send_metrics()
        elif parsed_path.path == '/prometheus':
            self.send_prometheus()
        elif parsed_path.path == '/':
            self.send_dashboard()
        else:
            self.send_error(404, "Not Found")
    
    def send_health(self):
        """Send health check."""
        health = {
            'status': 'healthy' if self.monitor.redis_client.socket else 'unhealthy',
            'last_update': self.monitor.last_update.isoformat() if self.monitor.last_update else None,
            'service': 'poe-simple-monitor'
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health, indent=2).encode())
    
    def send_metrics(self):
        """Send JSON metrics."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(self.monitor.metrics, indent=2).encode())
    
    def send_prometheus(self):
        """Send Prometheus format."""
        lines = []
        for key, value in self.monitor.metrics.items():
            if key not in ['timestamp', 'source'] and isinstance(value, (int, float)):
                lines.append(f"{key} {value}")
        
        prometheus_text = '\n'.join(lines) + '\n'
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(prometheus_text.encode())
    
    def send_dashboard(self):
        """Send HTML dashboard."""
        status_color = 'green' if self.monitor.redis_client.socket else 'red'
        status_text = 'Connected' if self.monitor.redis_client.socket else 'Disconnected'
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Poe Simple Monitor</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .status {{ color: {status_color}; }}
    </style>
</head>
<body>
    <h1>🐺 Poe Simple Monitor</h1>
    <p class="status">Status: {status_text}</p>
    <p>Last Update: {self.monitor.last_update or 'Never'}</p>
    
    <h2>Beast Mode Metrics</h2>'''
        
        for key, value in self.monitor.metrics.items():
            if key not in ['timestamp', 'source']:
                display_name = key.replace('beast_mode_', '').replace('_', ' ').title()
                html += f'''
    <div class="metric">
        <div>{display_name}</div>
        <div class="value">{value}</div>
    </div>'''
        
        html += '''
    <h2>API Endpoints</h2>
    <ul>
        <li><a href="/health">/health</a> - Health check</li>
        <li><a href="/metrics">/metrics</a> - JSON metrics</li>
        <li><a href="/prometheus">/prometheus</a> - Prometheus format</li>
    </ul>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """Main service."""
    logger.info("Starting Poe Simple Monitor...")
    
    # Create monitor
    monitor = SimpleMonitor()
    MonitorHandler.monitor = monitor
    
    # Start metrics collection
    def metrics_loop():
        while True:
            monitor.collect_metrics()
            time.sleep(30)
    
    metrics_thread = threading.Thread(target=metrics_loop, daemon=True)
    metrics_thread.start()
    
    # Start HTTP server
    server_port = 8080
    httpd = HTTPServer(('0.0.0.0', server_port), MonitorHandler)
    
    logger.info(f"Server running on http://0.0.0.0:{server_port}")
    logger.info("Dashboard: http://192.168.1.104:8080/")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        httpd.shutdown()

if __name__ == "__main__":
    main()