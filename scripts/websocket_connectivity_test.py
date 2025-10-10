#!/usr/bin/env python3
"""
WebSocket Connectivity Test Script

This script provides comprehensive testing for WebSocket connectivity
through Cloudflare tunnels with detailed diagnostics.
"""

import asyncio
import json
import sys
import time
import websockets
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketConnectivityTester:
    """Comprehensive WebSocket connectivity tester"""
    
    def __init__(self):
        self.test_results = []
        self.endpoints = [
            "wss://observatory.nkllon.com/ws/emoji-rain",
            "ws://localhost:8888/ws/emoji-rain"
        ]
        
    async def test_websocket_connection(self, endpoint: str) -> Dict[str, Any]:
        """Test WebSocket connection with detailed diagnostics"""
        start_time = time.time()
        result = {
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response_time_ms": 0,
            "error": None,
            "diagnostics": {}
        }
        
        try:
            logger.info(f"🔍 Testing WebSocket connection: {endpoint}")
            
            # Test connection
            async with websockets.connect(
                endpoint,
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                
                # Send test message
                test_message = json.dumps({
                    "type": "connectivity_test",
                    "timestamp": datetime.now().isoformat(),
                    "source": "connectivity_tester"
                })
                
                await websocket.send(test_message)
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                result["success"] = True
                result["response_time_ms"] = (time.time() - start_time) * 1000
                result["diagnostics"]["response"] = response_data
                result["diagnostics"]["connection_id"] = response_data.get("connection_id")
                
                logger.info(f"✅ WebSocket connection successful: {endpoint}")
                
        except asyncio.TimeoutError:
            result["error"] = "Connection timeout"
            result["response_time_ms"] = (time.time() - start_time) * 1000
            logger.error(f"❌ WebSocket connection timeout: {endpoint}")
            
        except Exception as e:
            result["error"] = str(e)
            result["response_time_ms"] = (time.time() - start_time) * 1000
            logger.error(f"❌ WebSocket connection failed: {endpoint} - {e}")
        
        return result
    
    async def test_http_fallback(self, endpoint: str) -> Dict[str, Any]:
        """Test HTTP fallback endpoints"""
        start_time = time.time()
        result = {
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response_time_ms": 0,
            "error": None,
            "diagnostics": {}
        }
        
        try:
            # Convert WebSocket endpoint to HTTP endpoint
            http_endpoint = endpoint.replace("wss://", "https://").replace("ws://", "http://").replace("/ws/emoji-rain", "/api/emoji-rain/stats")
            
            # Test with bot-safe headers
            headers = {
                "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
                "X-Observatory-Client": "internal-polling",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
                "X-Polling-Reason": "websocket-fallback"
            }
            
            response = requests.get(http_endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result["success"] = True
                result["response_time_ms"] = (time.time() - start_time) * 1000
                result["diagnostics"]["response_data"] = response.json()
                logger.info(f"✅ HTTP fallback successful: {http_endpoint}")
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text}"
                result["response_time_ms"] = (time.time() - start_time) * 1000
                logger.error(f"❌ HTTP fallback failed: {http_endpoint} - {result['error']}")
                
        except Exception as e:
            result["error"] = str(e)
            result["response_time_ms"] = (time.time() - start_time) * 1000
            logger.error(f"❌ HTTP fallback error: {endpoint} - {e}")
        
        return result
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive connectivity test"""
        logger.info("🚀 Starting comprehensive WebSocket connectivity test")
        
        test_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "results": []
        }
        
        # Test WebSocket connections
        for endpoint in self.endpoints:
            ws_result = await self.test_websocket_connection(endpoint)
            test_summary["results"].append(ws_result)
            test_summary["total_tests"] += 1
            
            if ws_result["success"]:
                test_summary["successful_tests"] += 1
            else:
                test_summary["failed_tests"] += 1
            
            # Test HTTP fallback
            http_result = await self.test_http_fallback(endpoint)
            test_summary["results"].append(http_result)
            test_summary["total_tests"] += 1
            
            if http_result["success"]:
                test_summary["successful_tests"] += 1
            else:
                test_summary["failed_tests"] += 1
        
        # Calculate success rate
        test_summary["success_rate"] = test_summary["successful_tests"] / test_summary["total_tests"] if test_summary["total_tests"] > 0 else 0
        
        return test_summary
    
    def generate_test_report(self, test_summary: Dict[str, Any]) -> str:
        """Generate human-readable test report"""
        report = []
        report.append("🔧 WebSocket Connectivity Test Report")
        report.append("=" * 50)
        report.append(f"Timestamp: {test_summary['timestamp']}")
        report.append(f"Total Tests: {test_summary['total_tests']}")
        report.append(f"Successful: {test_summary['successful_tests']}")
        report.append(f"Failed: {test_summary['failed_tests']}")
        report.append(f"Success Rate: {test_summary['success_rate']:.1%}")
        report.append("")
        
        # Detailed results
        report.append("📋 Detailed Results:")
        for result in test_summary["results"]:
            status = "✅" if result["success"] else "❌"
            report.append(f"{status} {result['endpoint']}")
            report.append(f"   Response Time: {result['response_time_ms']:.1f}ms")
            if result["error"]:
                report.append(f"   Error: {result['error']}")
            if result["diagnostics"]:
                report.append(f"   Diagnostics: {json.dumps(result['diagnostics'], indent=2)}")
            report.append("")
        
        # Recommendations
        report.append("💡 Recommendations:")
        if test_summary["success_rate"] < 1.0:
            report.append("   • Enable WebSockets in Cloudflare dashboard")
            report.append("   • Configure bot protection rules")
            report.append("   • Check tunnel configuration")
        else:
            report.append("   • All tests passed - WebSocket connectivity is working")
        
        return "\n".join(report)

async def main():
    """Main test function"""
    print("🔧 WebSocket Connectivity Tester")
    print("=" * 40)
    
    tester = WebSocketConnectivityTester()
    
    try:
        # Run comprehensive test
        test_summary = await tester.run_comprehensive_test()
        
        # Generate and display report
        report = tester.generate_test_report(test_summary)
        print(report)
        
        # Save results
        results_dir = Path("logs/connectivity_tests")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"websocket_test_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(test_summary, f, indent=2)
        
        print(f"\n📁 Test results saved to: {results_file}")
        
        # Return exit code based on success rate
        if test_summary["success_rate"] >= 0.5:  # At least 50% success
            return 0
        else:
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test execution error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
