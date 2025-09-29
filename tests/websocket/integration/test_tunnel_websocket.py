"""Integration tests for tunnel WebSocket connectivity."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.beast_mode.observatory.tunnel.websocket_validator import (
    WebSocketValidator,
    WebSocketValidationError
)
from src.beast_mode.observatory.websocket.manager import (
    WebSocketManager,
    WebSocketManagerConfig
)
from tests.websocket.fixtures.mock_tunnel_config import (
    MockTunnelConfig,
    MockTunnelManager,
    MockWebSocketUpgradeValidator
)
from tests.websocket.fixtures.websocket_test_data import (
    WebSocketTestConfig,
    WebSocketTestData,
    WebSocketTestMetrics
)


class TestTunnelWebSocketIntegration:
    """Test tunnel WebSocket integration functionality."""
    
    @pytest.fixture
    def tunnel_config(self):
        """Create tunnel configuration."""
        return MockTunnelConfig(
            hostname="observatory.nkllon.com",
            protocol="wss",
            timeout=30.0
        )
    
    @pytest.fixture
    def tunnel_manager(self, tunnel_config):
        """Create tunnel manager."""
        return MockTunnelManager(tunnel_config)
    
    @pytest.fixture
    def websocket_validator(self):
        """Create WebSocket validator."""
        return WebSocketValidator("observatory.nkllon.com")
    
    @pytest.fixture
    def websocket_manager_config(self):
        """Create WebSocket manager configuration."""
        return WebSocketManagerConfig(
            base_url="wss://observatory.nkllon.com",
            max_connections_per_endpoint=10,
            connection_timeout=30.0,
            retry_max_attempts=5,
            health_check_interval=60.0
        )
    
    @pytest.fixture
    def websocket_manager(self, websocket_manager_config):
        """Create WebSocket manager."""
        return WebSocketManager(websocket_manager_config)
    
    @pytest.mark.asyncio
    async def test_tunnel_connection_success(self, tunnel_manager):
        """Test successful tunnel connection."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_connection_success",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Test tunnel connection
        success = await tunnel_manager.connect()
        assert success is True
        assert tunnel_manager.is_connected is True
        assert tunnel_manager.connection_count == 1
        
        # Test tunnel disconnection
        await tunnel_manager.disconnect()
        assert tunnel_manager.is_connected is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_connection_success",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_tunnel_endpoint_health_check(self, tunnel_manager):
        """Test tunnel endpoint health checking."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_endpoint_health_check",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Test individual endpoint health
        health = await tunnel_manager.get_endpoint_health("/ws/emoji-rain")
        assert "status" in health
        assert "response_time_ms" in health
        assert "last_check" in health
        
        # Test all endpoints health
        all_health = await tunnel_manager.get_all_endpoints_health()
        assert len(all_health) == len(tunnel_manager.endpoints)
        
        for endpoint in tunnel_manager.endpoints:
            assert endpoint in all_health
            assert "status" in all_health[endpoint]
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_endpoint_health_check",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_tunnel_endpoint_failure_recovery(self, tunnel_manager):
        """Test tunnel endpoint failure and recovery."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_endpoint_failure_recovery",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        endpoint = "/ws/emoji-rain"
        
        # Test initial health
        health = await tunnel_manager.get_endpoint_health(endpoint)
        assert health["status"] == "healthy"
        
        # Simulate failure
        tunnel_manager.simulate_endpoint_failure(endpoint)
        health = await tunnel_manager.get_endpoint_health(endpoint)
        assert health["status"] == "unhealthy"
        assert health["error_count"] > 0
        
        # Simulate recovery
        tunnel_manager.simulate_endpoint_recovery(endpoint)
        health = await tunnel_manager.get_endpoint_health(endpoint)
        assert health["status"] == "healthy"
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_endpoint_failure_recovery",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_websocket_upgrade_validation(self, websocket_validator):
        """Test WebSocket upgrade validation."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_upgrade_validation",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Test successful validation
        result = await websocket_validator.validate_websocket_upgrade()
        
        assert "validation_status" in result
        assert "header_validation" in result
        assert "handshake_validation" in result
        assert "latency_ms" in result
        assert "recommendations" in result
        
        # Test validation with custom URL
        custom_url = "wss://observatory.nkllon.com/ws/custom"
        result = await websocket_validator.validate_websocket_upgrade(custom_url)
        assert result["url"] == custom_url
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_upgrade_validation",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_websocket_connectivity_test(self, websocket_validator):
        """Test WebSocket connectivity testing."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_connectivity_test",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Test connectivity
        result = await websocket_validator.test_websocket_connectivity()
        
        assert "connectivity_status" in result
        assert "connection_latency_ms" in result
        assert "handshake_duration_ms" in result
        assert "protocol_version" in result
        assert "message_exchange_test" in result
        assert "close_handshake" in result
        
        # Test with custom timeout
        result = await websocket_validator.test_websocket_connectivity(timeout_seconds=5)
        assert "connectivity_status" in result
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_connectivity_test",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_websocket_manager_tunnel_integration(self, websocket_manager, tunnel_manager):
        """Test WebSocket manager integration with tunnel."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_manager_tunnel_integration",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Start both managers
        await websocket_manager.start()
        await tunnel_manager.connect()
        
        # Test endpoint connectivity through tunnel
        tunnel_endpoints = tunnel_manager.config.endpoints
        websocket_endpoints = websocket_manager.endpoints
        
        # Verify endpoints match
        for endpoint in websocket_endpoints:
            assert endpoint in tunnel_endpoints
        
        # Test health status integration
        tunnel_health = await tunnel_manager.get_all_endpoints_health()
        websocket_health = await websocket_manager.get_health_status()
        
        assert len(tunnel_health) == len(websocket_endpoints)
        
        # Cleanup
        await websocket_manager.stop()
        await tunnel_manager.disconnect()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_manager_tunnel_integration",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_tunnel_failure_scenarios(self, tunnel_manager):
        """Test tunnel failure scenarios."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_failure_scenarios",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Test multiple endpoint failures
        endpoints_to_fail = ["/ws/emoji-rain", "/ws/anomalies"]
        
        for endpoint in endpoints_to_fail:
            tunnel_manager.simulate_endpoint_failure(endpoint)
        
        # Check health of all endpoints
        all_health = await tunnel_manager.get_all_endpoints_health()
        
        failed_count = 0
        healthy_count = 0
        
        for endpoint, health in all_health.items():
            if health["status"] == "unhealthy":
                failed_count += 1
            elif health["status"] == "healthy":
                healthy_count += 1
        
        assert failed_count == len(endpoints_to_fail)
        assert healthy_count == len(tunnel_manager.endpoints) - len(endpoints_to_fail)
        
        # Test recovery
        for endpoint in endpoints_to_fail:
            tunnel_manager.simulate_endpoint_recovery(endpoint)
        
        # Verify recovery
        all_health = await tunnel_manager.get_all_endpoints_health()
        healthy_count = sum(1 for health in all_health.values() if health["status"] == "healthy")
        assert healthy_count == len(tunnel_manager.endpoints)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_failure_scenarios",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_tunnel_statistics(self, tunnel_manager):
        """Test tunnel statistics collection."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_statistics",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Connect and get initial stats
        await tunnel_manager.connect()
        stats = tunnel_manager.get_stats()
        
        assert "is_connected" in stats
        assert "total_endpoints" in stats
        assert "healthy_endpoints" in stats
        assert "unhealthy_endpoints" in stats
        assert "connection_count" in stats
        assert "hostname" in stats
        assert "protocol" in stats
        
        assert stats["is_connected"] is True
        assert stats["total_endpoints"] == len(tunnel_manager.endpoints)
        assert stats["connection_count"] == 1
        
        # Simulate some failures and check stats
        tunnel_manager.simulate_endpoint_failure("/ws/emoji-rain")
        tunnel_manager.simulate_endpoint_failure("/ws/anomalies")
        
        stats = tunnel_manager.get_stats()
        assert stats["unhealthy_endpoints"] == 2
        assert stats["healthy_endpoints"] == len(tunnel_manager.endpoints) - 2
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_statistics",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_websocket_validator_statistics(self, websocket_validator):
        """Test WebSocket validator statistics."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_validator_statistics",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Perform some validations
        await websocket_validator.validate_websocket_upgrade()
        await websocket_validator.validate_websocket_upgrade("wss://test.example.com/ws")
        await websocket_validator.test_websocket_connectivity()
        
        # Get health status
        health = await websocket_validator.get_health_status()
        
        assert health.module_id == "websocket_validator"
        assert health.health_score >= 0.0
        assert health.health_score <= 1.0
        assert health.error_count >= 0
        assert health.warning_count >= 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_validator_statistics",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_end_to_end_tunnel_websocket_flow(self, websocket_manager, tunnel_manager, websocket_validator):
        """Test end-to-end tunnel WebSocket flow."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_end_to_end_tunnel_websocket_flow",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Step 1: Connect tunnel
        await tunnel_manager.connect()
        assert tunnel_manager.is_connected is True
        
        # Step 2: Validate WebSocket upgrade
        validation_result = await websocket_validator.validate_websocket_upgrade()
        assert validation_result["validation_status"] == "success"
        
        # Step 3: Test connectivity
        connectivity_result = await websocket_validator.test_websocket_connectivity()
        assert connectivity_result["connectivity_status"] == "success"
        
        # Step 4: Start WebSocket manager
        await websocket_manager.start()
        assert websocket_manager._is_running is True
        
        # Step 5: Check health of all components
        tunnel_health = await tunnel_manager.get_all_endpoints_health()
        websocket_health = await websocket_manager.get_health_status()
        validator_health = await websocket_validator.get_health_status()
        
        # Verify all components are healthy
        healthy_endpoints = sum(1 for health in tunnel_health.values() if health["status"] == "healthy")
        assert healthy_endpoints == len(tunnel_manager.endpoints)
        
        # Step 6: Cleanup
        await websocket_manager.stop()
        await tunnel_manager.disconnect()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_end_to_end_tunnel_websocket_flow",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_tunnel_websocket_error_handling(self, tunnel_manager, websocket_validator):
        """Test error handling in tunnel WebSocket integration."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_websocket_error_handling",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "tunnel_websocket"}
        }))
        
        # Test invalid endpoint
        with pytest.raises(ValueError):
            await tunnel_manager.get_endpoint_health("/ws/invalid")
        
        # Test validation with invalid URL
        invalid_url = "invalid://not-a-websocket-url"
        result = await websocket_validator.validate_websocket_upgrade(invalid_url)
        assert result["validation_status"] in ["failed", "error"]
        
        # Test connectivity with invalid URL
        result = await websocket_validator.test_websocket_connectivity(invalid_url)
        assert result["connectivity_status"] == "failed"
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_tunnel_websocket_error_handling",
            "status": "completed",
            "details": {"test_type": "integration", "component": "tunnel_websocket", "result": "passed"}
        }))