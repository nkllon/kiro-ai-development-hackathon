#!/usr/bin/env python3
"""
Simple WebSocket Validator
Quick validation of WebSocket endpoints for Phase 3 testing
"""

import asyncio
import json
import time
import websockets
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleWebSocketValidator:
    """Simple WebSocket validator for quick testing."""
    
    def __init__(self, base_url: str = "wss://observatory.nkllon.com"):
        self.base_url = base_url
        self.local_url = "ws://localhost:8888"
        self.endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        self.results = []
    
    async def validate_all_endpoints(self) -> Dict[str, Any]:
        """Validate all WebSocket endpoints."""
        logger.info("🔌 Starting Simple WebSocket Validation")
        
        for endpoint in self.endpoints:
            await self._test_endpoint(endpoint)
        
        return self._generate_report()
    
    async def _test_endpoint(self, endpoint: str):
        """Test a single WebSocket endpoint."""
        logger.info(f"Testing {endpoint}...")
        
        # Test production endpoint
        await self._test_single_connection(f"{self.base_url}{endpoint}", endpoint, "production")
        
        # Test local endpoint
        await self._test_single_connection(f"{self.local_url}{endpoint}", endpoint, "local")
    
    async def _test_single_connection(self, url: str, endpoint: str, url_type: str):
        """Test a single WebSocket connection."""
        test_name = f"{endpoint}_{url_type}"
        start_time = time.time()
        
        try:
            # Test connection establishment
            connection_start = time.time()
            websocket = await websockets.connect(url, ping_interval=20, ping_timeout=10)
            connection_time = time.time() - connection_start
            
            # Test message exchange
            test_message = {
                "type": "test",
                "timestamp": datetime.utcnow().isoformat(),
                "test_id": f"simple_validation_{int(time.time())}"
            }
            
            await websocket.send(json.dumps(test_message))
            
            # Try to receive a message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                message_received = True
            except asyncio.TimeoutError:
                message_received = False
                response_data = None
            
            await websocket.close()
            
            # Record result
            result = {
                "test_name": test_name,
                "status": "passed",
                "connection_time": connection_time,
                "message_received": message_received,
                "duration": time.time() - start_time,
                "url": url,
                "response_type": response_data.get("type") if response_data else None
            }
            
            self.results.append(result)
            logger.info(f"✅ {test_name}: {connection_time:.3f}s connection, message: {message_received}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time,
                "url": url
            }
            
            self.results.append(result)
            logger.error(f"❌ {test_name}: {e}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "passed"])
        failed_tests = len([r for r in self.results if r["status"] == "failed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate connection time metrics
        connection_times = [r["connection_time"] for r in self.results if "connection_time" in r]
        max_connection_time = max(connection_times) if connection_times else 0
        avg_connection_time = sum(connection_times) / len(connection_times) if connection_times else 0
        
        # Check requirements
        connection_time_requirement = max_connection_time < 2.0 if connection_times else False
        
        report = {
            "validation_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "max_connection_time": max_connection_time,
                "avg_connection_time": avg_connection_time,
                "connection_time_requirement_met": connection_time_requirement,
                "timestamp": datetime.utcnow().isoformat()
            },
            "test_results": self.results,
            "requirements_status": {
                "connection_time_under_2s": {
                    "requirement": "< 2 seconds",
                    "status": "passed" if connection_time_requirement else "failed",
                    "max_time": max_connection_time,
                    "details": f"Max connection time: {max_connection_time:.3f}s"
                }
            }
        }
        
        return report

async def main():
    """Main execution function."""
    print("🔌 Simple WebSocket Validator")
    print("=" * 40)
    
    validator = SimpleWebSocketValidator()
    
    try:
        report = await validator.validate_all_endpoints()
        
        # Print summary
        print("\n📊 VALIDATION SUMMARY")
        print("=" * 40)
        summary = report["validation_summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Max Connection Time: {summary['max_connection_time']:.3f}s")
        print(f"Avg Connection Time: {summary['avg_connection_time']:.3f}s")
        
        print("\n🎯 REQUIREMENTS STATUS")
        print("=" * 40)
        for req_name, req_data in report["requirements_status"].items():
            status_emoji = "✅" if req_data["status"] == "passed" else "❌"
            print(f"{status_emoji} {req_name.replace('_', ' ').title()}: {req_data['details']}")
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"simple_websocket_validation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: {filename}")
        
        # Exit with appropriate code
        if summary['failed_tests'] > 0:
            print("\n❌ Some tests failed.")
            return 1
        else:
            print("\n✅ All tests passed!")
            return 0
            
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        logger.exception("Validation failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)