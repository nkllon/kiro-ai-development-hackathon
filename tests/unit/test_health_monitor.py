"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.697163
"""



import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.monitoring.health_monitor import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    HealthMonitor, HealthStatus, ComponentHealth, HealthCheck
)


class TestHealthMonitor(ReflectiveModule):
    """Test cases for HealthMonitor."""
    
    @pytest.fixture
    def health_monitor(self):
        """Create a health monitor instance for testing."""
        return HealthMonitor("redis://localhost:6379")
        
    @pytest.mark.asyncio
    async def test_register_health_check(self, health_monitor):
        """Test registering a health check."""
        check_function = AsyncMock(return_value={"healthy": True})
        
        await health_monitor.register_health_check(
            name="test_check",
            check_function=check_function,
            interval_seconds=30
        )
        
        assert "test_check" in health_monitor.health_checks
        assert "test_check" in health_monitor.component_health
        assert health_monitor.component_health["test_check"].status == HealthStatus.UNKNOWN
        
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, health_monitor):
        """Test starting and stopping monitoring."""
        assert not health_monitor.monitoring_active
        
        await health_monitor.start_monitoring()
        assert health_monitor.monitoring_active
        assert health_monitor.monitoring_task is not None
        
        await health_monitor.stop_monitoring()
        assert not health_monitor.monitoring_active
        
    @pytest.mark.asyncio
    async def test_get_system_health(self, health_monitor):
        """Test getting system health status."""
        # Add a test component
        health_monitor.component_health["test"] = ComponentHealth(
            component_name="test",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now(),
            message="Test component OK"
        )
        
        health = await health_monitor.get_system_health()
        assert "test" in health
        assert health["test"].status == HealthStatus.HEALTHY
        
    @pytest.mark.asyncio
    async def test_is_system_healthy(self, health_monitor):
        """Test system health evaluation."""
        # All healthy
        health_monitor.component_health["comp1"] = ComponentHealth(
            component_name="comp1",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )
        health_monitor.component_health["comp2"] = ComponentHealth(
            component_name="comp2",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )
        
        assert await health_monitor.is_system_healthy()
        
        # One unhealthy
        health_monitor.component_health["comp2"].status = HealthStatus.UNHEALTHY
        assert not await health_monitor.is_system_healthy()
        
    @pytest.mark.asyncio
    async def test_get_health_summary(self, health_monitor):
        """Test health summary generation."""
        # Add test components
        health_monitor.component_health["healthy"] = ComponentHealth(
            component_name="healthy",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )
        health_monitor.component_health["degraded"] = ComponentHealth(
            component_name="degraded",
            status=HealthStatus.DEGRADED,
            last_check=datetime.now()
        )
        health_monitor.component_health["unhealthy"] = ComponentHealth(
            component_name="unhealthy",
            status=HealthStatus.UNHEALTHY,
            last_check=datetime.now()
        )
        
        summary = await health_monitor.get_health_summary()
        
        assert summary["total_components"] == 3
        assert summary["healthy"] == 1
        assert summary["degraded"] == 1
        assert summary["unhealthy"] == 1
        assert summary["overall_status"] == HealthStatus.UNHEALTHY
        
    @pytest.mark.asyncio
    async def test_handle_check_success(self, health_monitor):
        """Test handling successful health checks."""
        # Register a check
        check_function = AsyncMock(return_value={"healthy": True})
        await health_monitor.register_health_check(
            name="test_check",
            check_function=check_function,
            recovery_threshold=2
        )
        
        # Simulate successful checks
        await health_monitor._handle_check_success(
            "test_check",
            {"healthy": True, "message": "All good"},
            50.0
        )
        
        health = health_monitor.component_health["test_check"]
        assert health.status == HealthStatus.DEGRADED  # Still recovering
        assert health.check_duration_ms == 50.0
        
        # Another success should make it healthy
        await health_monitor._handle_check_success(
            "test_check",
            {"healthy": True, "message": "All good"},
            45.0
        )
        
        health = health_monitor.component_health["test_check"]
        assert health.status == HealthStatus.HEALTHY
        
    @pytest.mark.asyncio
    async def test_handle_check_failure(self, health_monitor):
        """Test handling failed health checks."""
        # Register a check
        check_function = AsyncMock(return_value={"healthy": False})
        await health_monitor.register_health_check(
            name="test_check",
            check_function=check_function,
            failure_threshold=2
        )
        
        # First failure
        await health_monitor._handle_check_failure(
            "test_check",
            {"healthy": False, "message": "Something wrong"},
            100.0
        )
        
        health = health_monitor.component_health["test_check"]
        assert health.status == HealthStatus.DEGRADED
        
        # Second failure should make it unhealthy
        await health_monitor._handle_check_failure(
            "test_check",
            {"healthy": False, "message": "Still wrong"},
            120.0
        )
        
        health = health_monitor.component_health["test_check"]
        assert health.status == HealthStatus.UNHEALTHY
        
    @pytest.mark.asyncio
    @patch('redis.asyncio.from_url')
    async def test_redis_connectivity_check(self, mock_redis, health_monitor):
        """Test Redis connectivity health check."""
        # Mock successful Redis connection
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock()
        mock_client.info = AsyncMock(return_value={
            "redis_version": "6.2.0",
            "connected_clients": 5,
            "used_memory_human": "1.5M"
        })
        mock_client.close = AsyncMock()
        mock_redis.return_value = mock_client
        
        result = await health_monitor._check_redis_connectivity()
        
        assert result["healthy"] is True
        assert "Redis connectivity OK" in result["message"]
        assert "redis_version" in result["details"]
        
        # Test failure
        mock_client.ping.side_effect = Exception("Connection failed")
        
        result = await health_monitor._check_redis_connectivity()
        
        assert result["healthy"] is False
        assert "Connection failed" in result["message"]
        
    @pytest.mark.asyncio
    @patch('redis.asyncio.from_url')
    async def test_redis_pubsub_check(self, mock_redis, health_monitor):
        """Test Redis pub/sub health check."""
        # Mock successful pub/sub
        mock_client = AsyncMock()
        mock_client.publish = AsyncMock(return_value=2)  # 2 subscribers
        mock_client.close = AsyncMock()
        mock_redis.return_value = mock_client
        
        result = await health_monitor._check_redis_pubsub()
        
        assert result["healthy"] is True
        assert "Redis pub/sub OK" in result["message"]
        assert result["details"]["subscribers"] == 2
        
    @pytest.mark.asyncio
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    async def test_system_resources_check(self, mock_disk, mock_memory, mock_cpu, health_monitor):
        """Test system resources health check."""
        # Mock normal resource usage
        mock_cpu.return_value = 50.0
        mock_memory.return_value = MagicMock(percent=60.0, available=4*1024**3)
        mock_disk.return_value = MagicMock(percent=70.0, free=100*1024**3)
        
        result = await health_monitor._check_system_resources()
        
        assert result["healthy"] is True
        assert "System resources OK" in result["message"]
        
        # Mock high resource usage
        mock_cpu.return_value = 95.0
        mock_memory.return_value = MagicMock(percent=95.0, available=1*1024**3)
        
        result = await health_monitor._check_system_resources()
        
        assert result["healthy"] is False
        assert "High CPU usage" in result["message"]
        assert "High memory usage" in result["message"]
        
    @pytest.mark.asyncio
    async def test_run_health_check_timeout(self, health_monitor):
        """Test health check timeout handling."""
        # Create a check that times out
        async def slow_check():
            await asyncio.sleep(10)  # Longer than timeout
            return {"healthy": True}
            
        await health_monitor.register_health_check(
            name="slow_check",
            check_function=slow_check,
            timeout_seconds=1
        )
        
        # Run the check
        health_check = health_monitor.health_checks["slow_check"]
        await health_monitor._run_health_check("slow_check", health_check)
        
        # Should have failed due to timeout
        health = health_monitor.component_health["slow_check"]
        assert health.status == HealthStatus.DEGRADED
        assert "timed out" in health.message.lower()
        
    @pytest.mark.asyncio
    async def test_run_health_check_exception(self, health_monitor):
        """Test health check exception handling."""
        # Create a check that raises an exception
        async def failing_check():
            raise ValueError("Test error")
            
        await health_monitor.register_health_check(
            name="failing_check",
            check_function=failing_check
        )
        
        # Run the check
        health_check = health_monitor.health_checks["failing_check"]
        await health_monitor._run_health_check("failing_check", health_check)
        
        # Should have failed due to exception
        health = health_monitor.component_health["failing_check"]
        assert health.status == HealthStatus.DEGRADED

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert "Test error" in health.message