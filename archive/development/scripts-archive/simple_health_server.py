#!/usr/bin/env python3
"""
Simple Health Server for Observatory Recovery
Provides basic health endpoints to restore 502 errors
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "mode": "emergency",
                "message": "Observatory emergency health server"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/observatory/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "degraded",
                "mode": "emergency",
                "timestamp": datetime.utcnow().isoformat(),
                "health": {
                    "status": "ok",
                    "health_score": 0.5,
                    "issues": ["Running in emergency mode"]
                },
                "services": {
                    "health": "ok",
                    "api": "limited"
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "service": "Observatory Emergency Health Server",
                "status": "running",
                "endpoints": ["/health", "/api/observatory/status"]
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        print(f"{datetime.now().isoformat()} - {format % args}")

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8888), HealthHandler)
    print("🚨 Emergency Observatory Health Server starting on port 8888")
    print("📊 Endpoints: /health, /api/observatory/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()