#!/usr/bin/env python3
"""
WebSocket Validation Suite - Phase 3 Implementation
Tests WebSocket endpoints according to remediation requirements
"""

import asyncio
import json
import time
import subprocess
import websockets
from datetime import datetime
from typing import Dict, List, Any

class WebSocketValidator:
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
    
    async def test_websocket_upgrade(self, endpoint: str) -> Dict[str, Any]:
        """Test WebSocket upgrade request using curl."""
        
        start_time = time.time()
        
        try:
            cmd = [
                "curl", "-I", "-N",
                "-H", "Connection: Upgrade",
                "-H", "Upgrade: websocket",
                "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
                "-H", "Sec-WebSocket-Version: 13",
                f"https://{self.domain}{endpoint}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            response_time = time.time() - start_time
            
            test_result = {
                "endpoint": endpoint,
                "response_time": response_time,
                "status_code": "unknown",
                "success": False,
                "error": None
            }
            
            if result.stdout:
                first_line = result.stdout.split('\n')[0]
                if "HTTP/" in first_line:
                    status_code = first_line.split()[1]
                    test_result["status_code"] = status_code
                    
                    if status_code == "101":
                        test_result["success"] = True
                        print(f"✅ {endpoint}: HTTP/1.1 101 Switching Protocols")
                    else:
                        print(f"❌ {endpoint}: HTTP/{status_code}")
                else:
                    test_result["error"] = "Invalid HTTP response format"
            else:
                test_result["error"] = "No response received"
            
            return test_result
            
        except Exception as e:
            print(f"💥 {endpoint}: {str(e)}")
            return {
                "endpoint": endpoint,
                "response_time": time.time() - start_time,
                "status_code": "error",
                "success": False,
                "error": str(e)
            }
    
    async def test_websocket_connection(self, endpoint: str) -> Dict[str, Any]:
        """Test actual WebSocket connection."""
        
        ws_url = f"wss://{self.domain}{endpoint}"
        connection_results = {
            "endpoint": endpoint,
            "connection_time": None,
            "success": False,
            "error": None
        }
        
        try:
            connect_start = time.time()
            
            async with websockets.connect(ws_url) as websocket:
                connection_time = time.time() - connect_start
                connection_results["connection_time"] = connection_time
                connection_results["success"] = True
                
                print(f"🔌 {endpoint}: Connected in {connection_time:.3f}s")
                
                # Send test message
                test_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                print(f"📨 {endpoint}: Test message sent")
                
        except Exception as e:
            connection_results["error"] = str(e)
            print(f"💥 {endpoint}: Connection error: {e}")
        
        return connection_results
    
    async def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all WebSocket endpoints."""
        
        print("🚀 Starting WebSocket validation...")
        
        # Test WebSocket upgrade requests
        print("📡 Testing WebSocket upgrade requests...")
        upgrade_tasks = [self.test_websocket_upgrade(endpoint) for endpoint in self.endpoints]
        upgrade_results = await asyncio.gather(*upgrade_tasks)
        
        # Test WebSocket connections
        print("🔌 Testing WebSocket connections...")
        connection_tasks = [self.test_websocket_connection(endpoint) for endpoint in self.endpoints]
        connection_results = await asyncio.gather(*connection_tasks)
        
        # Compile results
        validation_summary = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "upgrade_tests": upgrade_results,
            "connection_tests": connection_results,
            "overall_status": "unknown"
        }
        
        # Analyze results
        successful_upgrades = sum(1 for result in upgrade_results if result["success"])
        successful_connections = sum(1 for result in connection_results if result["success"])
        
        if successful_upgrades == len(self.endpoints) and successful_connections == len(self.endpoints):
            validation_summary["overall_status"] = "fully_functional"
            print("🎉 All WebSocket endpoints functional!")
        elif successful_upgrades > 0 or successful_connections > 0:
            validation_summary["overall_status"] = "partially_functional"
            print(f"⚠️ Partial functionality: {successful_upgrades}/{len(self.endpoints)} upgrades, {successful_connections}/{len(self.endpoints)} connections")
        else:
            validation_summary["overall_status"] = "non_functional"
            print("❌ No WebSocket endpoints functional")
        
        return validation_summary

async def main():
    """Main execution function."""
    
    print("🧪 WebSocket Validation Suite")
    print("=" * 40)
    
    validator = WebSocketValidator()
    results = await validator.test_all_endpoints()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"websocket_validation_{timestamp}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Validation results saved to: {report_filename}")
    print(f"Overall Status: {results['overall_status']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
