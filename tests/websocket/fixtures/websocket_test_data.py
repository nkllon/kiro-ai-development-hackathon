"""Test fixtures and data for WebSocket connectivity tests."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class WebSocketTestConfig:
    """Configuration for WebSocket tests."""
    base_url: str = "ws://localhost:8000"
    tunnel_url: str = "wss://observatory.nkllon.com"
    connection_timeout: float = 10.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    max_connections: int = 100
    message_timeout: float = 5.0
    heartbeat_interval: float = 20.0
    health_check_interval: float = 30.0


@dataclass
class TestMessage:
    """Test message structure."""
    id: str
    type: str
    payload: Dict[str, Any]
    timestamp: str
    priority: int = 1


class WebSocketTestData:
    """Test data generator for WebSocket tests."""
    
    @staticmethod
    def get_test_endpoints() -> List[str]:
        """Get list of test endpoints."""
        return [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
    
    @staticmethod
    def get_test_headers() -> Dict[str, str]:
        """Get test headers for WebSocket connections."""
        return {
            "User-Agent": "BeastMode-TestSuite/1.0",
            "X-Test-Session": "test-session-123",
            "Authorization": "Bearer test-token-456"
        }
    
    @staticmethod
    def get_test_messages(count: int = 10) -> List[TestMessage]:
        """Generate test messages."""
        messages = []
        for i in range(count):
            message = TestMessage(
                id=f"test-msg-{i}",
                type="test_message",
                payload={
                    "data": f"test_data_{i}",
                    "sequence": i,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timestamp=datetime.utcnow().isoformat(),
                priority=i % 3 + 1
            )
            messages.append(message)
        return messages
    
    @staticmethod
    def get_large_message(size_kb: int = 100) -> TestMessage:
        """Generate a large test message."""
        large_data = "x" * (size_kb * 1024)
        return TestMessage(
            id="large-message",
            type="large_data",
            payload={"data": large_data, "size_kb": size_kb},
            timestamp=datetime.utcnow().isoformat(),
            priority=1
        )
    
    @staticmethod
    def get_rapid_messages(count: int = 1000) -> List[TestMessage]:
        """Generate rapid test messages for throughput testing."""
        messages = []
        base_time = datetime.utcnow()
        for i in range(count):
            message = TestMessage(
                id=f"rapid-msg-{i}",
                type="rapid_test",
                payload={
                    "sequence": i,
                    "batch_id": i // 100,
                    "data": f"rapid_data_{i}"
                },
                timestamp=(base_time + timedelta(milliseconds=i)).isoformat(),
                priority=1
            )
            messages.append(message)
        return messages
    
    @staticmethod
    def get_error_scenarios() -> List[Dict[str, Any]]:
        """Get error scenarios for testing."""
        return [
            {
                "name": "connection_timeout",
                "error_type": "ConnectionTimeoutError",
                "description": "Simulate connection timeout"
            },
            {
                "name": "authentication_failure",
                "error_type": "AuthenticationError", 
                "description": "Simulate authentication failure"
            },
            {
                "name": "rate_limit_exceeded",
                "error_type": "RateLimitError",
                "description": "Simulate rate limit exceeded"
            },
            {
                "name": "protocol_error",
                "error_type": "ProtocolError",
                "description": "Simulate protocol error"
            },
            {
                "name": "network_unavailable",
                "error_type": "ConnectionFailedError",
                "description": "Simulate network unavailable"
            }
        ]
    
    @staticmethod
    def get_load_test_scenarios() -> List[Dict[str, Any]]:
        """Get load test scenarios."""
        return [
            {
                "name": "light_load",
                "concurrent_connections": 10,
                "messages_per_second": 100,
                "duration_seconds": 60
            },
            {
                "name": "medium_load", 
                "concurrent_connections": 50,
                "messages_per_second": 500,
                "duration_seconds": 300
            },
            {
                "name": "heavy_load",
                "concurrent_connections": 100,
                "messages_per_second": 1000,
                "duration_seconds": 600
            },
            {
                "name": "stress_test",
                "concurrent_connections": 200,
                "messages_per_second": 2000,
                "duration_seconds": 1800
            }
        ]
    
    @staticmethod
    def get_health_check_data() -> Dict[str, Any]:
        """Get health check test data."""
        return {
            "healthy_endpoint": {
                "status": "healthy",
                "response_time_ms": 25.5,
                "last_check": datetime.utcnow().isoformat(),
                "error_count": 0
            },
            "unhealthy_endpoint": {
                "status": "unhealthy", 
                "response_time_ms": 5000.0,
                "last_check": datetime.utcnow().isoformat(),
                "error_count": 5,
                "error_message": "Connection timeout"
            },
            "degraded_endpoint": {
                "status": "degraded",
                "response_time_ms": 2000.0,
                "last_check": datetime.utcnow().isoformat(),
                "error_count": 2,
                "warning_message": "High latency detected"
            }
        }


class MockWebSocketServer:
    """Mock WebSocket server for testing."""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.clients = []
        self.message_history = []
        self.is_running = False
    
    async def start(self):
        """Start the mock server."""
        self.is_running = True
        # In a real implementation, this would start a WebSocket server
    
    async def stop(self):
        """Stop the mock server."""
        self.is_running = False
        self.clients.clear()
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to a client."""
        self.message_history.append({
            "client_id": client_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all clients."""
        for client in self.clients:
            await self.send_message(client["id"], message)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            "connected_clients": len(self.clients),
            "total_messages": len(self.message_history),
            "is_running": self.is_running,
            "uptime_seconds": 0  # Would be calculated in real implementation
        }


class WebSocketTestMetrics:
    """Metrics collector for WebSocket tests."""
    
    def __init__(self):
        self.metrics = {
            "connection_attempts": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "connection_durations": [],
            "message_latencies": [],
            "error_counts": {},
            "start_time": datetime.utcnow()
        }
    
    def record_connection_attempt(self, success: bool, duration_ms: float):
        """Record a connection attempt."""
        self.metrics["connection_attempts"] += 1
        if success:
            self.metrics["successful_connections"] += 1
        else:
            self.metrics["failed_connections"] += 1
        self.metrics["connection_durations"].append(duration_ms)
    
    def record_message(self, sent: bool, latency_ms: float):
        """Record a message."""
        if sent:
            self.metrics["messages_sent"] += 1
        else:
            self.metrics["messages_received"] += 1
        self.metrics["message_latencies"].append(latency_ms)
    
    def record_error(self, error_type: str):
        """Record an error."""
        if error_type not in self.metrics["error_counts"]:
            self.metrics["error_counts"][error_type] = 0
        self.metrics["error_counts"][error_type] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test metrics summary."""
        total_time = (datetime.utcnow() - self.metrics["start_time"]).total_seconds()
        
        return {
            "test_duration_seconds": total_time,
            "connection_success_rate": (
                self.metrics["successful_connections"] / self.metrics["connection_attempts"]
                if self.metrics["connection_attempts"] > 0 else 0
            ),
            "average_connection_duration_ms": (
                sum(self.metrics["connection_durations"]) / len(self.metrics["connection_durations"])
                if self.metrics["connection_durations"] else 0
            ),
            "messages_per_second": (
                (self.metrics["messages_sent"] + self.metrics["messages_received"]) / total_time
                if total_time > 0 else 0
            ),
            "average_message_latency_ms": (
                sum(self.metrics["message_latencies"]) / len(self.metrics["message_latencies"])
                if self.metrics["message_latencies"] else 0
            ),
            "total_errors": sum(self.metrics["error_counts"].values()),
            "error_breakdown": self.metrics["error_counts"]
        }