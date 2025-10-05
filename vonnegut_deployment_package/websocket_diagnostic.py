#!/usr/bin/env python3
"""
WebSocket Registration Diagnostic Script

This script diagnoses WebSocket registration issues in the Observatory server.
"""

import json
import logging
import asyncio
import websockets
import traceback
from pathlib import Path
from typing import Dict, List, Any
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketDiagnostic:
    """Comprehensive WebSocket diagnostic tool."""
    
    def __init__(self):
        self.base_url = "http://localhost:8888"
        self.test_results = {}
    
    def run_diagnostics(self):
        """Run comprehensive WebSocket diagnostics."""
        logger.info("🔍 Starting WebSocket diagnostic checks...")
        
        results = {
            "timestamp": "2025-01-27T13:14:30Z",
            "base_url": self.base_url,
            "tests": {}
        }
        
        # Test 1: Check if server is running
        results["tests"]["server_health"] = self._test_server_health()
        
        # Test 2: Check OpenAPI schema for WebSocket endpoints
        results["tests"]["openapi_schema"] = self._test_openapi_schema()
        
        # Test 3: Test WebSocket upgrade requests
        results["tests"]["websocket_upgrade"] = self._test_websocket_upgrade()
        
        # Test 4: Test WebSocket endpoints individually
        results["tests"]["websocket_endpoints"] = self._test_websocket_endpoints()
        
        # Generate summary
        results["summary"] = self._generate_summary(results["tests"])
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _test_server_health(self):
        """Test if the Observatory server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "PASS",
                    "details": "Server is running and healthy",
                    "health_data": health_data
                }
            else:
                return {
                    "status": "FAIL",
                    "details": f"Server returned status {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "status": "FAIL",
                "details": f"Cannot connect to server: {e}",
                "error": str(e)
            }
    
    def _test_openapi_schema(self):
        """Test OpenAPI schema for WebSocket endpoints."""
        try:
            response = requests.get(f"{self.base_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                schema = response.json()
                paths = schema.get("paths", {})
                websocket_paths = [path for path in paths.keys() if "/ws/" in path]
                
                return {
                    "status": "PASS" if websocket_paths else "FAIL",
                    "details": f"Found {len(websocket_paths)} WebSocket endpoints in schema",
                    "websocket_paths": websocket_paths,
                    "total_paths": len(paths),
                    "all_paths": list(paths.keys())
                }
            else:
                return {
                    "status": "FAIL",
                    "details": f"Cannot retrieve OpenAPI schema: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "status": "FAIL",
                "details": f"Error retrieving OpenAPI schema: {e}",
                "error": str(e)
            }
    
    def _test_websocket_upgrade(self):
        """Test WebSocket upgrade requests."""
        endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                import subprocess
                cmd = [
                    "curl", "-I", "-N",
                    "-H", "Connection: Upgrade",
                    "-H", "Upgrade: websocket", 
                    "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
                    "-H", "Sec-WebSocket-Version: 13",
                    f"{self.base_url}{endpoint}"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if "101 Switching Protocols" in result.stdout:
                    status = "PASS"
                    details = "WebSocket upgrade successful"
                elif "400 Bad Request" in result.stdout:
                    status = "FAIL"
                    details = "WebSocket upgrade failed - 400 Bad Request"
                elif "404 Not Found" in result.stdout:
                    status = "FAIL"
                    details = "WebSocket endpoint not found - 404"
                else:
                    status = "FAIL"
                    details = f"Unexpected response: {result.stdout.split()[0] if result.stdout else 'No response'}"
                
                results[endpoint] = {
                    "status": status,
                    "details": details,
                    "response": result.stdout,
                    "error": result.stderr if result.stderr else None
                }
                
            except Exception as e:
                results[endpoint] = {
                    "status": "ERROR",
                    "details": f"Error testing endpoint: {e}",
                    "error": str(e)
                }
        
        return results
    
    def _test_websocket_endpoints(self):
        """Test WebSocket endpoints with actual connections."""
        endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory",
            "/ws/anomalies", 
            "/ws/doctor-status"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                # Use direct socket connection test since we can't use asyncio easily here
                import socket
                import ssl
                
                # Parse URL
                ws_url = f"ws://localhost:8888{endpoint}"
                
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                
                try:
                    sock.connect(("localhost", 8888))
                    
                    # Send WebSocket handshake
                    handshake = (
                        f"GET {endpoint} HTTP/1.1\r\n"
                        "Host: localhost:8888\r\n"
                        "Upgrade: websocket\r\n"
                        "Connection: Upgrade\r\n"
                        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                        "Sec-WebSocket-Version: 13\r\n"
                        "\r\n"
                    )
                    
                    sock.send(handshake.encode())
                    response = sock.recv(1024).decode()
                    
                    if "101 Switching Protocols" in response:
                        status = "PASS"
                        details = "WebSocket connection successful"
                    elif "400 Bad Request" in response:
                        status = "FAIL"
                        details = "WebSocket connection failed - 400 Bad Request"
                    elif "404 Not Found" in response:
                        status = "FAIL"
                        details = "WebSocket endpoint not found - 404"
                    else:
                        status = "FAIL"
                        details = f"Unexpected response: {response.split()[1] if len(response.split()) > 1 else 'Unknown'}"
                    
                    results[endpoint] = {
                        "status": status,
                        "details": details,
                        "response": response.strip(),
                        "connection_type": "direct_socket"
                    }
                    
                except Exception as e:
                    results[endpoint] = {
                        "status": "ERROR",
                        "details": f"Socket connection error: {e}",
                        "error": str(e),
                        "connection_type": "direct_socket"
                    }
                finally:
                    sock.close()
                    
            except Exception as e:
                results[endpoint] = {
                    "status": "ERROR",
                    "details": f"Error testing endpoint: {e}",
                    "error": str(e)
                }
        
        return results
    
    def _generate_summary(self, tests: Dict[str, Any]):
        """Generate diagnostic summary."""
        summary = {
            "overall_status": "UNKNOWN",
            "issues_found": [],
            "recommendations": []
        }
        
        # Check server health
        if tests["server_health"]["status"] != "PASS":
            summary["issues_found"].append("Server health check failed")
            summary["recommendations"].append("Ensure Observatory server is running on port 8888")
        
        # Check OpenAPI schema
        openapi_test = tests["openapi_schema"]
        if openapi_test["status"] != "PASS":
            summary["issues_found"].append("No WebSocket endpoints found in OpenAPI schema")
            summary["recommendations"].append("WebSocket endpoints are not properly registered in FastAPI")
        
        # Check WebSocket upgrades
        upgrade_tests = tests["websocket_upgrade"]
        failed_upgrades = [ep for ep, result in upgrade_tests.items() if result["status"] != "PASS"]
        if failed_upgrades:
            summary["issues_found"].append(f"WebSocket upgrade failed for {len(failed_upgrades)} endpoints")
            summary["recommendations"].append("Check WebSocket endpoint registration in _setup_websockets() method")
        
        # Check WebSocket connections
        connection_tests = tests["websocket_endpoints"]
        failed_connections = [ep for ep, result in connection_tests.items() if result["status"] != "PASS"]
        if failed_connections:
            summary["issues_found"].append(f"WebSocket connection failed for {len(failed_connections)} endpoints")
            summary["recommendations"].append("Debug WebSocket handler initialization and registration")
        
        # Determine overall status
        if not summary["issues_found"]:
            summary["overall_status"] = "PASS"
        elif tests["server_health"]["status"] != "PASS":
            summary["overall_status"] = "CRITICAL"
        else:
            summary["overall_status"] = "FAIL"
        
        return summary
    
    def _save_results(self, results: Dict[str, Any]):
        """Save diagnostic results to file."""
        output_file = "websocket_diagnostic_results.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📄 Diagnostic results saved to {output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

def main():
    """Main diagnostic function."""
    print("🔍 WebSocket Registration Diagnostic Tool")
    print("=" * 50)
    
    diagnostic = WebSocketDiagnostic()
    results = diagnostic.run_diagnostics()
    
    print("\n📊 Diagnostic Results Summary:")
    print("-" * 30)
    
    summary = results["summary"]
    print(f"Overall Status: {summary['overall_status']}")
    
    if summary["issues_found"]:
        print("\n❌ Issues Found:")
        for issue in summary["issues_found"]:
            print(f"  • {issue}")
        
        print("\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")
    else:
        print("\n✅ All diagnostic tests passed!")
    
    print(f"\n📄 Detailed results saved to: websocket_diagnostic_results.json")
    
    return results

if __name__ == "__main__":
    main()
