#!/usr/bin/env python3
"""
WebSocket Integration Tester
Tests WebSocket integration with Observatory dashboard
"""

import asyncio
import json
import time
import websockets
from datetime import datetime
from typing import Dict, List, Any

class WebSocketIntegrationTester:
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
    
    async def test_endpoint_integration(self, endpoint: str) -> Dict[str, Any]:
        """Test integration for a specific endpoint."""
        
        ws_url = f"wss://{self.domain}{endpoint}"
        result = {
            "endpoint": endpoint,
            "connection_successful": False,
            "messages_sent": 0,
            "messages_received": 0,
            "integration_score": 0,
            "errors": []
        }
        
        try:
            print(f"🔌 Testing integration for {endpoint}...")
            
            async with websockets.connect(ws_url) as websocket:
                result["connection_successful"] = True
                print(f"✅ Connected to {endpoint}")
                
                # Send test messages
                test_messages = [
                    {"type": "ping", "timestamp": datetime.now().isoformat()},
                    {"type": "test", "action": "integration_test"},
                    {"type": "query", "action": "status"}
                ]
                
                for message in test_messages:
                    await websocket.send(json.dumps(message))
                    result["messages_sent"] += 1
                    
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        response_data = json.loads(response)
                        result["messages_received"] += 1
                        print(f"📨 Received: {response_data.get('type', 'unknown')}")
                        
                    except asyncio.TimeoutError:
                        result["errors"].append("Response timeout")
                    except json.JSONDecodeError:
                        result["errors"].append("Invalid JSON response")
                
                # Calculate integration score
                if result["messages_sent"] > 0:
                    result["integration_score"] = result["messages_received"] / result["messages_sent"]
                
                print(f"📊 {endpoint}: {result['messages_sent']} sent, {result['messages_received']} received")
                
        except Exception as e:
            result["errors"].append(str(e))
            print(f"💥 Integration test failed for {endpoint}: {e}")
        
        return result
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for all endpoints."""
        
        print("🧪 WebSocket Integration Tester")
        print("=" * 40)
        print(f"Domain: {self.domain}")
        print()
        
        start_time = time.time()
        
        # Test each endpoint
        endpoint_results = []
        for endpoint in self.endpoints:
            result = await self.test_endpoint_integration(endpoint)
            endpoint_results.append(result)
            print()
        
        total_time = time.time() - start_time
        
        # Overall analysis
        successful_endpoints = sum(1 for r in endpoint_results if r["connection_successful"])
        avg_integration_score = sum(r["integration_score"] for r in endpoint_results) / len(endpoint_results)
        
        overall_status = "passed" if successful_endpoints == len(self.endpoints) and avg_integration_score >= 0.5 else "failed"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "test_duration": total_time,
            "endpoint_results": endpoint_results,
            "successful_endpoints": successful_endpoints,
            "total_endpoints": len(self.endpoints),
            "average_integration_score": avg_integration_score,
            "overall_status": overall_status
        }
        
        print("📊 Integration Test Summary:")
        print(f"Successful Endpoints: {successful_endpoints}/{len(self.endpoints)}")
        print(f"Average Integration Score: {avg_integration_score:.1%}")
        print(f"Overall Status: {overall_status}")
        
        return summary

async def main():
    """Main execution function."""
    
    tester = WebSocketIntegrationTester()
    results = await tester.run_integration_tests()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"websocket_integration_{timestamp}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Integration test results saved to: {report_filename}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
