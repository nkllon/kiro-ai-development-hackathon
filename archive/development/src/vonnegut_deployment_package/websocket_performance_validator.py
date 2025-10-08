#!/usr/bin/env python3
"""
WebSocket Performance Validator
Tests WebSocket performance under load according to requirements
"""

import asyncio
import json
import time
import websockets
import statistics
from datetime import datetime
from typing import Dict, List, Any
import argparse

class WebSocketPerformanceValidator:
    def __init__(self, domain: str = "observatory.nkllon.com", connections: int = 10, duration: int = 60):
        self.domain = domain
        self.endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        self.connections = connections
        self.duration = duration
        self.results = {}
    
    async def single_connection_test(self, endpoint: str, connection_id: int) -> Dict[str, Any]:
        """Test a single WebSocket connection with performance metrics."""
        
        ws_url = f"wss://{self.domain}{endpoint}"
        connection_results = {
            "endpoint": endpoint,
            "connection_id": connection_id,
            "connection_time": None,
            "messages_sent": 0,
            "messages_received": 0,
            "message_latencies": [],
            "errors": [],
            "success": False
        }
        
        try:
            # Measure connection time
            connect_start = time.time()
            
            async with websockets.connect(ws_url) as websocket:
                connection_time = time.time() - connect_start
                connection_results["connection_time"] = connection_time
                connection_results["success"] = True
                
                print(f"🔌 Connection {connection_id} to {endpoint}: {connection_time:.3f}s")
                
                # Send messages for the specified duration
                end_time = time.time() + self.duration
                message_count = 0
                
                while time.time() < end_time:
                    try:
                        # Send test message
                        test_message = {
                            "type": "ping",
                            "connection_id": connection_id,
                            "message_id": message_count,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        send_start = time.time()
                        await websocket.send(json.dumps(test_message))
                        connection_results["messages_sent"] += 1
                        message_count += 1
                        
                        # Try to receive response
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                            latency = time.time() - send_start
                            connection_results["message_latencies"].append(latency)
                            connection_results["messages_received"] += 1
                            
                        except asyncio.TimeoutError:
                            connection_results["errors"].append("Response timeout")
                        
                        # Small delay between messages
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        connection_results["errors"].append(str(e))
                
                print(f"📊 Connection {connection_id}: {connection_results['messages_sent']} sent, {connection_results['messages_received']} received")
                
        except Exception as e:
            connection_results["errors"].append(str(e))
            print(f"💥 Connection {connection_id} failed: {e}")
        
        return connection_results
    
    async def test_endpoint_performance(self, endpoint: str) -> Dict[str, Any]:
        """Test performance for a single endpoint with multiple connections."""
        
        print(f"🚀 Testing {endpoint} with {self.connections} connections for {self.duration}s...")
        
        # Create multiple connection tasks
        connection_tasks = [
            self.single_connection_test(endpoint, i) 
            for i in range(self.connections)
        ]
        
        # Run all connections concurrently
        connection_results = await asyncio.gather(*connection_tasks)
        
        # Analyze results
        successful_connections = [r for r in connection_results if r["success"]]
        failed_connections = [r for r in connection_results if not r["success"]]
        
        if not successful_connections:
            return {
                "endpoint": endpoint,
                "success_rate": 0.0,
                "total_connections": self.connections,
                "successful_connections": 0,
                "failed_connections": self.connections,
                "status": "failed"
            }
        
        # Calculate performance metrics
        connection_times = [r["connection_time"] for r in successful_connections if r["connection_time"]]
        all_latencies = []
        total_messages_sent = 0
        total_messages_received = 0
        total_errors = 0
        
        for result in successful_connections:
            if result["message_latencies"]:
                all_latencies.extend(result["message_latencies"])
            total_messages_sent += result["messages_sent"]
            total_messages_received += result["messages_received"]
            total_errors += len(result["errors"])
        
        # Performance analysis
        avg_connection_time = statistics.mean(connection_times) if connection_times else 0
        max_connection_time = max(connection_times) if connection_times else 0
        avg_latency = statistics.mean(all_latencies) if all_latencies else 0
        max_latency = max(all_latencies) if all_latencies else 0
        success_rate = len(successful_connections) / self.connections
        
        performance_result = {
            "endpoint": endpoint,
            "success_rate": success_rate,
            "total_connections": self.connections,
            "successful_connections": len(successful_connections),
            "failed_connections": len(failed_connections),
            "avg_connection_time": avg_connection_time,
            "max_connection_time": max_connection_time,
            "avg_message_latency": avg_latency,
            "max_message_latency": max_latency,
            "total_messages_sent": total_messages_sent,
            "total_messages_received": total_messages_received,
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_messages_sent, 1),
            "status": "passed" if success_rate >= 0.95 and max_connection_time < 2.0 and max_latency < 0.1 else "failed"
        }
        
        print(f"📊 {endpoint} Results:")
        print(f"  Success Rate: {success_rate:.1%}")
        print(f"  Avg Connection Time: {avg_connection_time:.3f}s")
        print(f"  Max Connection Time: {max_connection_time:.3f}s")
        print(f"  Avg Message Latency: {avg_latency:.3f}s")
        print(f"  Max Message Latency: {max_latency:.3f}s")
        print(f"  Error Rate: {performance_result['error_rate']:.1%}")
        print(f"  Status: {performance_result['status']}")
        
        return performance_result
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests for all endpoints."""
        
        print("🧪 WebSocket Performance Validator")
        print("=" * 50)
        print(f"Domain: {self.domain}")
        print(f"Connections per endpoint: {self.connections}")
        print(f"Test duration: {self.duration}s")
        print()
        
        start_time = time.time()
        
        # Test each endpoint
        endpoint_results = []
        for endpoint in self.endpoints:
            result = await self.test_endpoint_performance(endpoint)
            endpoint_results.append(result)
            print()
        
        total_time = time.time() - start_time
        
        # Overall analysis
        overall_success_rate = statistics.mean([r["success_rate"] for r in endpoint_results])
        overall_status = "passed" if overall_success_rate >= 0.95 else "failed"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "test_config": {
                "connections_per_endpoint": self.connections,
                "test_duration": self.duration,
                "total_test_time": total_time
            },
            "endpoint_results": endpoint_results,
            "overall_success_rate": overall_success_rate,
            "overall_status": overall_status,
            "requirements_met": {
                "connection_time_under_2s": all(r["max_connection_time"] < 2.0 for r in endpoint_results),
                "message_latency_under_100ms": all(r["max_message_latency"] < 0.1 for r in endpoint_results),
                "error_rate_under_5_percent": all(r["error_rate"] < 0.05 for r in endpoint_results),
                "success_rate_over_95_percent": overall_success_rate >= 0.95
            }
        }
        
        print("📊 Overall Performance Summary:")
        print(f"Overall Success Rate: {overall_success_rate:.1%}")
        print(f"Overall Status: {overall_status}")
        print()
        print("✅ Requirements Met:")
        for req, met in summary["requirements_met"].items():
            status = "✅" if met else "❌"
            print(f"  {status} {req.replace('_', ' ').title()}")
        
        return summary

async def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="WebSocket Performance Validator")
    parser.add_argument("--connections", type=int, default=10, help="Number of connections per endpoint")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--domain", type=str, default="observatory.nkllon.com", help="Domain to test")
    
    args = parser.parse_args()
    
    validator = WebSocketPerformanceValidator(
        domain=args.domain,
        connections=args.connections,
        duration=args.duration
    )
    
    results = await validator.run_performance_tests()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"websocket_performance_{timestamp}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Performance results saved to: {report_filename}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())