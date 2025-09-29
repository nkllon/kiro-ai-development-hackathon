"""Mock tunnel configuration for WebSocket testing."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MockTunnelConfig:
    """Mock tunnel configuration for testing."""
    hostname: str = "observatory.nkllon.com"
    port: int = 443
    protocol: str = "wss"
    endpoints: List[str] = None
    authentication: Dict[str, str] = None
    timeout: float = 30.0
    retry_attempts: int = 3
    health_check_interval: float = 60.0
    
    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = [
                "/ws/emoji-rain",
                "/ws/observatory",
                "/ws/anomalies", 
                "/ws/doctor-status"
            ]
        if self.authentication is None:
            self.authentication = {
                "type": "bearer",
                "token": "test-token-123"
            }


class MockTunnelEndpoint:
    """Mock tunnel endpoint for testing."""
    
    def __init__(self, path: str, config: MockTunnelConfig):
        self.path = path
        self.config = config
        self.is_healthy = True
        self.response_time_ms = 25.0
        self.error_count = 0
        self.last_check = datetime.utcnow()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        self.last_check = datetime.utcnow()
        
        # Simulate health check
        if self.is_healthy:
            return {
                "status": "healthy",
                "response_time_ms": self.response_time_ms,
                "last_check": self.last_check.isoformat(),
                "error_count": self.error_count
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": self.response_time_ms,
                "last_check": self.last_check.isoformat(),
                "error_count": self.error_count,
                "error_message": "Simulated failure"
            }
    
    def simulate_failure(self):
        """Simulate endpoint failure."""
        self.is_healthy = False
        self.error_count += 1
        self.response_time_ms = 5000.0
    
    def simulate_recovery(self):
        """Simulate endpoint recovery."""
        self.is_healthy = True
        self.response_time_ms = 25.0


class MockTunnelManager:
    """Mock tunnel manager for testing."""
    
    def __init__(self, config: MockTunnelConfig):
        self.config = config
        self.endpoints = {}
        self.is_connected = False
        self.connection_count = 0
        
        # Initialize endpoints
        for path in config.endpoints:
            self.endpoints[path] = MockTunnelEndpoint(path, config)
    
    async def connect(self) -> bool:
        """Connect to tunnel."""
        self.is_connected = True
        self.connection_count += 1
        return True
    
    async def disconnect(self):
        """Disconnect from tunnel."""
        self.is_connected = False
    
    async def get_endpoint_health(self, path: str) -> Dict[str, Any]:
        """Get health status for endpoint."""
        if path not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {path}")
        
        return await self.endpoints[path].health_check()
    
    async def get_all_endpoints_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all endpoints."""
        results = {}
        for path, endpoint in self.endpoints.items():
            results[path] = await endpoint.health_check()
        return results
    
    def simulate_endpoint_failure(self, path: str):
        """Simulate endpoint failure."""
        if path in self.endpoints:
            self.endpoints[path].simulate_failure()
    
    def simulate_endpoint_recovery(self, path: str):
        """Simulate endpoint recovery."""
        if path in self.endpoints:
            self.endpoints[path].simulate_recovery()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tunnel statistics."""
        healthy_endpoints = sum(1 for ep in self.endpoints.values() if ep.is_healthy)
        
        return {
            "is_connected": self.is_connected,
            "total_endpoints": len(self.endpoints),
            "healthy_endpoints": healthy_endpoints,
            "unhealthy_endpoints": len(self.endpoints) - healthy_endpoints,
            "connection_count": self.connection_count,
            "hostname": self.config.hostname,
            "protocol": self.config.protocol
        }


class MockWebSocketUpgradeValidator:
    """Mock WebSocket upgrade validator for testing."""
    
    def __init__(self):
        self.validation_count = 0
        self.successful_validations = 0
        self.failed_validations = 0
    
    async def validate_upgrade_request(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate WebSocket upgrade request."""
        self.validation_count += 1
        
        # Simulate validation
        required_headers = ["Upgrade", "Connection", "Sec-WebSocket-Key", "Sec-WebSocket-Version"]
        missing_headers = [h for h in required_headers if h not in headers]
        
        if missing_headers:
            self.failed_validations += 1
            return {
                "valid": False,
                "errors": [f"Missing header: {h}" for h in missing_headers],
                "validation_time_ms": 15.2
            }
        
        # Check WebSocket version
        if headers.get("Sec-WebSocket-Version") != "13":
            self.failed_validations += 1
            return {
                "valid": False,
                "errors": ["Unsupported WebSocket version"],
                "validation_time_ms": 12.8
            }
        
        self.successful_validations += 1
        return {
            "valid": True,
            "accept_key": "mock-accept-key-123",
            "validation_time_ms": 8.5,
            "protocol_version": "13"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        success_rate = (
            self.successful_validations / self.validation_count
            if self.validation_count > 0 else 0
        )
        
        return {
            "total_validations": self.validation_count,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "success_rate": success_rate
        }


class MockConnectionPool:
    """Mock connection pool for testing."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = []
        self.connection_count = 0
        self.active_connections = 0
    
    async def acquire_connection(self) -> Optional[str]:
        """Acquire a connection from the pool."""
        if self.active_connections >= self.max_connections:
            return None
        
        connection_id = f"conn-{self.connection_count}"
        self.connections.append(connection_id)
        self.connection_count += 1
        self.active_connections += 1
        
        return connection_id
    
    async def release_connection(self, connection_id: str):
        """Release a connection back to the pool."""
        if connection_id in self.connections:
            self.connections.remove(connection_id)
            self.active_connections -= 1
    
    async def close_all_connections(self):
        """Close all connections in the pool."""
        self.connections.clear()
        self.active_connections = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "available_connections": self.max_connections - self.active_connections,
            "total_connections_created": self.connection_count,
            "utilization_rate": self.active_connections / self.max_connections
        }


class MockRetryStrategy:
    """Mock retry strategy for testing."""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.current_attempt = 0
        self.total_attempts = 0
    
    def should_retry(self, error: Exception) -> bool:
        """Check if retry should be attempted."""
        self.total_attempts += 1
        return self.current_attempt < self.max_attempts
    
    def calculate_delay(self) -> float:
        """Calculate retry delay."""
        self.current_attempt += 1
        return self.base_delay * (2 ** (self.current_attempt - 1))
    
    def reset(self):
        """Reset retry state."""
        self.current_attempt = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            "max_attempts": self.max_attempts,
            "current_attempt": self.current_attempt,
            "total_attempts": self.total_attempts,
            "base_delay": self.base_delay
        }