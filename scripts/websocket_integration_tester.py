#!/usr/bin/env python3
"""
WebSocket Integration Tester
Specialized script for testing WebSocket integration scenarios

Tests:
- Dashboard WebSocket connections
- Real-time emoji rain functionality
- Live status updates streaming
- Anomaly detection streaming
- Cross-endpoint communication
- Client-server message flow
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
import os
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class IntegrationTestResult:
    test_name: str
    status: str
    duration: float
    messages_sent: int
    messages_received: int
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

class WebSocketIntegrationTester:
    """Tests WebSocket integration scenarios."""
    
    def __init__(self, base_url: str = "wss://observatory.nkllon.com"):
        self.base_url = base_url
        self.local_url = "ws://localhost:8888"
        self.test_results: List[IntegrationTestResult] = []
        
    async def run_all_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        logger.info("🔗 Starting WebSocket Integration Tests")
        
        # Test 1: Dashboard Integration
        await self._test_dashboard_integration()
        
        # Test 2: Real-time Emoji Rain
        await self._test_emoji_rain_integration()
        
        # Test 3: Live Status Updates
        await self._test_status_updates_integration()
        
        # Test 4: Anomaly Detection Streaming
        await self._test_anomaly_detection_integration()
        
        # Test 5: Cross-endpoint Communication
        await self._test_cross_endpoint_communication()
        
        # Test 6: Client-Server Message Flow
        await self._test_client_server_message_flow()
        
        # Test 7: Multi-client Scenarios
        await self._test_multi_client_scenarios()
        
        return self._generate_integration_report()
    
    async def _test_dashboard_integration(self):
        """Test dashboard WebSocket integration."""
        logger.info("🖥️ Testing Dashboard Integration...")
        
        test_name = "dashboard_integration"
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        
        try:
            # Connect to emoji rain endpoint (primary dashboard WebSocket)
            full_url = f"{self.base_url}/ws/emoji-rain"
            websocket = await websockets.connect(full_url)
            
            # Send dashboard connection message
            dashboard_message = {
                "type": "client_connected",
                "timestamp": datetime.utcnow().isoformat(),
                "user_agent": "WebSocket-Integration-Tester/1.0",
                "client_type": "dashboard",
                "features": ["emoji_rain", "real_time_updates"]
            }
            
            await websocket.send(json.dumps(dashboard_message))
            messages_sent += 1
            
            # Wait for initial state
            initial_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            initial_data = json.loads(initial_response)
            messages_received += 1
            
            # Verify initial state
            if initial_data.get("type") != "initial_state":
                raise AssertionError(f"Expected initial_state, got {initial_data.get('type')}")
            
            # Verify initial state structure
            data = initial_data.get("data", {})
            required_fields = ["active_effects", "performance_stats"]
            for field in required_fields:
                if field not in data:
                    raise AssertionError(f"Missing required field: {field}")
            
            # Wait for emoji rain frames
            frames_received = 0
            frame_start = time.time()
            
            while frames_received < 5 and time.time() - frame_start < 10:
                try:
                    frame_response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    frame_data = json.loads(frame_response)
                    messages_received += 1
                    
                    if frame_data.get("type") == "emoji_rain_frame":
                        frames_received += 1
                        
                        # Verify frame structure
                        frame_data_content = frame_data.get("data", {})
                        if "frame_id" not in frame_data_content:
                            logger.warning("Frame missing frame_id")
                        
                except asyncio.TimeoutError:
                    break
            
            await websocket.close()
            
            # Verify we received frames
            if frames_received == 0:
                raise AssertionError("No emoji rain frames received")
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                details={
                    "frames_received": frames_received,
                    "initial_state_valid": True,
                    "endpoint": "/ws/emoji-rain"
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                error_message=str(e),
                details={"endpoint": "/ws/emoji-rain"}
            )
    
    async def _test_emoji_rain_integration(self):
        """Test real-time emoji rain functionality integration."""
        logger.info("🎨 Testing Real-time Emoji Rain Integration...")
        
        test_name = "emoji_rain_integration"
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        
        try:
            full_url = f"{self.base_url}/ws/emoji-rain"
            websocket = await websockets.connect(full_url)
            
            # Send emoji rain control message
            control_message = {
                "type": "emoji_rain_control",
                "action": "start",
                "intensity": "medium",
                "duration": 30,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send(json.dumps(control_message))
            messages_sent += 1
            
            # Collect frames for analysis
            frames_collected = []
            frame_types = set()
            collection_start = time.time()
            
            while time.time() - collection_start < 15:  # Collect for 15 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    messages_received += 1
                    
                    message_type = data.get("type")
                    frame_types.add(message_type)
                    
                    if message_type == "emoji_rain_frame":
                        frames_collected.append(data)
                        
                        # Verify frame has required data
                        frame_data = data.get("data", {})
                        if "frame_id" not in frame_data:
                            logger.warning("Frame missing frame_id")
                        
                except asyncio.TimeoutError:
                    break
            
            await websocket.close()
            
            # Analyze collected data
            if len(frames_collected) == 0:
                raise AssertionError("No emoji rain frames collected")
            
            # Calculate frame rate
            if len(frames_collected) > 1:
                frame_times = [f.get("timestamp", 0) for f in frames_collected if f.get("timestamp")]
                if len(frame_times) > 1:
                    frame_intervals = [frame_times[i] - frame_times[i-1] for i in range(1, len(frame_times))]
                    avg_frame_interval = sum(frame_intervals) / len(frame_intervals)
                    fps = 1.0 / avg_frame_interval if avg_frame_interval > 0 else 0
                else:
                    fps = 0
            else:
                fps = 0
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                details={
                    "frames_collected": len(frames_collected),
                    "frame_types": list(frame_types),
                    "estimated_fps": fps,
                    "collection_duration": 15
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                error_message=str(e),
                details={"endpoint": "/ws/emoji-rain"}
            )
    
    async def _test_status_updates_integration(self):
        """Test live status updates streaming integration."""
        logger.info("📡 Testing Live Status Updates Integration...")
        
        test_name = "status_updates_integration"
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        
        try:
            # Test observatory status endpoint
            full_url = f"{self.base_url}/ws/observatory"
            websocket = await websockets.connect(full_url)
            
            # Send status request
            status_request = {
                "type": "status_request",
                "timestamp": datetime.utcnow().isoformat(),
                "requested_metrics": ["health", "uptime", "performance"]
            }
            
            await websocket.send(json.dumps(status_request))
            messages_sent += 1
            
            # Collect status updates
            status_updates = []
            update_types = set()
            collection_start = time.time()
            
            while time.time() - collection_start < 20:  # Collect for 20 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(message)
                    messages_received += 1
                    
                    message_type = data.get("type")
                    update_types.add(message_type)
                    
                    if "status" in message_type or "health" in message_type:
                        status_updates.append(data)
                        
                        # Verify status structure
                        if "data" in data:
                            status_data = data["data"]
                            if "health_score" in status_data:
                                health_score = status_data["health_score"]
                                if not isinstance(health_score, (int, float)) or health_score < 0 or health_score > 100:
                                    logger.warning(f"Invalid health score: {health_score}")
                        
                except asyncio.TimeoutError:
                    break
            
            await websocket.close()
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                details={
                    "status_updates": len(status_updates),
                    "update_types": list(update_types),
                    "collection_duration": 20,
                    "endpoint": "/ws/observatory"
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                error_message=str(e),
                details={"endpoint": "/ws/observatory"}
            )
    
    async def _test_anomaly_detection_integration(self):
        """Test anomaly detection streaming integration."""
        logger.info("🚨 Testing Anomaly Detection Integration...")
        
        test_name = "anomaly_detection_integration"
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        
        try:
            full_url = f"{self.base_url}/ws/anomalies"
            websocket = await websockets.connect(full_url)
            
            # Send anomaly detection request
            anomaly_request = {
                "type": "anomaly_detection_request",
                "timestamp": datetime.utcnow().isoformat(),
                "detection_mode": "continuous",
                "sensitivity": "medium"
            }
            
            await websocket.send(json.dumps(anomaly_request))
            messages_sent += 1
            
            # Collect anomaly data
            anomaly_alerts = []
            detection_types = set()
            collection_start = time.time()
            
            while time.time() - collection_start < 20:  # Collect for 20 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(message)
                    messages_received += 1
                    
                    message_type = data.get("type")
                    detection_types.add(message_type)
                    
                    if "anomaly" in message_type:
                        anomaly_alerts.append(data)
                        
                        # Verify anomaly structure
                        if "data" in data:
                            anomaly_data = data["data"]
                            if "severity" in anomaly_data:
                                severity = anomaly_data["severity"]
                                valid_severities = ["low", "medium", "high", "critical"]
                                if severity not in valid_severities:
                                    logger.warning(f"Invalid anomaly severity: {severity}")
                        
                except asyncio.TimeoutError:
                    break
            
            await websocket.close()
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                details={
                    "anomaly_alerts": len(anomaly_alerts),
                    "detection_types": list(detection_types),
                    "collection_duration": 20,
                    "endpoint": "/ws/anomalies"
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                error_message=str(e),
                details={"endpoint": "/ws/anomalies"}
            )
    
    async def _test_cross_endpoint_communication(self):
        """Test communication across multiple endpoints simultaneously."""
        logger.info("🔗 Testing Cross-Endpoint Communication...")
        
        test_name = "cross_endpoint_communication"
        start_time = time.time()
        total_messages_sent = 0
        total_messages_received = 0
        
        try:
            # Connect to multiple endpoints simultaneously
            endpoints = ["/ws/emoji-rain", "/ws/observatory", "/ws/anomalies", "/ws/doctor-status"]
            websockets_connections = {}
            
            # Establish connections
            for endpoint in endpoints:
                full_url = f"{self.base_url}{endpoint}"
                websockets_connections[endpoint] = await websockets.connect(full_url)
            
            # Send messages to all endpoints
            for endpoint, websocket in websockets_connections.items():
                test_message = {
                    "type": "cross_endpoint_test",
                    "endpoint": endpoint,
                    "timestamp": datetime.utcnow().isoformat(),
                    "test_id": f"cross_test_{int(time.time())}"
                }
                
                await websocket.send(json.dumps(test_message))
                total_messages_sent += 1
            
            # Collect responses from all endpoints
            responses_received = 0
            collection_start = time.time()
            
            while responses_received < len(endpoints) and time.time() - collection_start < 10:
                for endpoint, websocket in websockets_connections.items():
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        total_messages_received += 1
                        responses_received += 1
                        
                    except asyncio.TimeoutError:
                        continue
            
            # Close all connections
            for websocket in websockets_connections.values():
                await websocket.close()
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=total_messages_sent,
                messages_received=total_messages_received,
                details={
                    "endpoints_tested": len(endpoints),
                    "responses_received": responses_received,
                    "endpoints": endpoints
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=total_messages_sent,
                messages_received=total_messages_received,
                error_message=str(e),
                details={"endpoints": endpoints}
            )
    
    async def _test_client_server_message_flow(self):
        """Test client-server message flow patterns."""
        logger.info("💬 Testing Client-Server Message Flow...")
        
        test_name = "client_server_message_flow"
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        
        try:
            full_url = f"{self.base_url}/ws/emoji-rain"
            websocket = await websockets.connect(full_url)
            
            # Test different message types
            test_messages = [
                {"type": "ping", "timestamp": datetime.utcnow().isoformat()},
                {"type": "client_info", "user_agent": "Integration-Tester", "version": "1.0"},
                {"type": "request_status", "component": "emoji_engine"},
                {"type": "control_message", "action": "pause", "duration": 5}
            ]
            
            for message in test_messages:
                await websocket.send(json.dumps(message))
                messages_sent += 1
                
                # Wait for response or timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    messages_received += 1
                    
                    # Verify response is valid JSON
                    if "type" not in data:
                        logger.warning(f"Response missing type field: {data}")
                        
                except asyncio.TimeoutError:
                    # Some messages might not have responses
                    pass
                
                await asyncio.sleep(0.5)  # Small delay between messages
            
            await websocket.close()
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                details={
                    "test_messages": len(test_messages),
                    "response_rate": messages_received / messages_sent if messages_sent > 0 else 0,
                    "endpoint": "/ws/emoji-rain"
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=messages_sent,
                messages_received=messages_received,
                error_message=str(e),
                details={"endpoint": "/ws/emoji-rain"}
            )
    
    async def _test_multi_client_scenarios(self):
        """Test multi-client scenarios."""
        logger.info("👥 Testing Multi-Client Scenarios...")
        
        test_name = "multi_client_scenarios"
        start_time = time.time()
        total_messages_sent = 0
        total_messages_received = 0
        
        try:
            # Simulate multiple clients connecting to the same endpoint
            client_count = 3
            full_url = f"{self.base_url}/ws/emoji-rain"
            
            # Create multiple connections
            clients = []
            for i in range(client_count):
                websocket = await websockets.connect(full_url)
                clients.append({
                    "id": i,
                    "websocket": websocket,
                    "messages_sent": 0,
                    "messages_received": 0
                })
            
            # Send messages from each client
            for client in clients:
                client_message = {
                    "type": "multi_client_test",
                    "client_id": client["id"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await client["websocket"].send(json.dumps(client_message))
                client["messages_sent"] += 1
                total_messages_sent += 1
            
            # Collect responses from all clients
            collection_start = time.time()
            while time.time() - collection_start < 10:
                for client in clients:
                    try:
                        message = await asyncio.wait_for(client["websocket"].recv(), timeout=1.0)
                        data = json.loads(message)
                        client["messages_received"] += 1
                        total_messages_received += 1
                        
                    except asyncio.TimeoutError:
                        continue
            
            # Close all client connections
            for client in clients:
                await client["websocket"].close()
            
            # Analyze results
            successful_clients = len([c for c in clients if c["messages_received"] > 0])
            
            self._record_test_result(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                messages_sent=total_messages_sent,
                messages_received=total_messages_received,
                details={
                    "client_count": client_count,
                    "successful_clients": successful_clients,
                    "client_success_rate": successful_clients / client_count,
                    "endpoint": "/ws/emoji-rain"
                }
            )
            
        except Exception as e:
            self._record_test_result(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                messages_sent=total_messages_sent,
                messages_received=total_messages_received,
                error_message=str(e),
                details={"endpoint": "/ws/emoji-rain"}
            )
    
    def _record_test_result(self, test_name: str, status: str, duration: float,
                           messages_sent: int, messages_received: int,
                           error_message: Optional[str] = None, details: Dict[str, Any] = None):
        """Record a test result."""
        result = IntegrationTestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            messages_sent=messages_sent,
            messages_received=messages_received,
            error_message=error_message,
            details=details or {}
        )
        
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "passed" else "❌"
        logger.info(f"{status_emoji} {test_name}: {status} ({duration:.3f}s, {messages_sent} sent, {messages_received} received)")
        
        if error_message:
            logger.error(f"   Error: {error_message}")
    
    def _generate_integration_report(self) -> Dict[str, Any]:
        """Generate integration test report."""
        logger.info("📊 Generating Integration Test Report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_messages_sent = sum(r.messages_sent for r in self.test_results)
        total_messages_received = sum(r.messages_received for r in self.test_results)
        
        report = {
            "integration_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "total_messages_sent": total_messages_sent,
                "total_messages_received": total_messages_received,
                "message_success_rate": total_messages_received / total_messages_sent if total_messages_sent > 0 else 0
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "messages_sent": r.messages_sent,
                    "messages_received": r.messages_received,
                    "error_message": r.error_message,
                    "details": r.details
                }
                for r in self.test_results
            ]
        }
        
        return report

async def main():
    """Main execution function."""
    print("🔗 WebSocket Integration Tester")
    print("=" * 50)
    
    tester = WebSocketIntegrationTester()
    
    try:
        report = await tester.run_all_integration_tests()
        
        # Print summary
        print("\n📊 INTEGRATION TEST SUMMARY")
        print("=" * 50)
        summary = report["integration_summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Messages Sent: {summary['total_messages_sent']}")
        print(f"Messages Received: {summary['total_messages_received']}")
        print(f"Message Success Rate: {summary['message_success_rate']:.1f}%")
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"websocket_integration_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: {filename}")
        
        # Exit with appropriate code
        if summary['failed_tests'] > 0:
            print("\n❌ Some integration tests failed.")
            sys.exit(1)
        else:
            print("\n✅ All integration tests passed!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Integration testing failed: {e}")
        logger.exception("Integration testing failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())