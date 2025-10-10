"""
Unit tests for WebSocket Health Monitor

Tests the core health monitoring functionality including connection tracking,
performance analysis, and health status determination.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.beast_mode.observatory.monitoring.health_monitor import (
    WebSocketHealthMonitor, HealthStatus, ConnectionHealth
)


class TestWebSocketHealthMonitor:
    """Test cases for WebSocketHealthMonitor"""

    @pytest.fixture
    def health_monitor(self):
        """Create a health monitor instance for testing"""
        return WebSocketHealthMonitor()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket for testing"""
        websocket = Mock()
        websocket.close = AsyncMock()
        websocket.send = AsyncMock()
        websocket.recv = AsyncMock()
        return websocket

    def test_initialization(self, health_monitor):
        """Test health monitor initialization"""
        assert health_monitor.metrics['websocket_connections_active'] == 0
        assert health_monitor.metrics['websocket_connection_failures'] == 0
        assert health_monitor.metrics['websocket_message_latency_ms'] == []
        assert health_monitor.metrics['websocket_throughput_msgs_per_sec'] == 0.0
        assert health_monitor.metrics['websocket_error_rate'] == 0.0
        
        assert len(health_monitor._monitoring_active) == 0
        assert len(health_monitor._connection_health) == 0

    @pytest.mark.asyncio
    async def test_monitor_connection_success(self, health_monitor, mock_websocket):
        """Test successful connection monitoring"""
        endpoint = "test_endpoint"
        
        with patch.object(health_monitor.connection_tracker, 'track_connection', new_callable=AsyncMock) as mock_track:
            await health_monitor.monitor_connection(endpoint, mock_websocket)
            
            # Verify connection tracking was called
            mock_track.assert_called_once_with(endpoint, mock_websocket)
            
            # Verify monitoring state
            assert endpoint in health_monitor._monitoring_active
            assert endpoint in health_monitor._connection_health
            assert health_monitor.metrics['websocket_connections_active'] == 1
            
            # Verify health status initialization
            health = health_monitor._connection_health[endpoint]
            assert health.endpoint == endpoint
            assert health.status == HealthStatus.UNKNOWN

    @pytest.mark.asyncio
    async def test_monitor_connection_failure(self, health_monitor, mock_websocket):
        """Test connection monitoring failure"""
        endpoint = "test_endpoint"
        
        with patch.object(health_monitor.connection_tracker, 'track_connection', 
                         side_effect=Exception("Connection failed")):
            
            with pytest.raises(Exception):
                await health_monitor.monitor_connection(endpoint, mock_websocket)
            
            # Verify failure metrics
            assert health_monitor.metrics['websocket_connection_failures'] == 1
            assert endpoint not in health_monitor._monitoring_active

    @pytest.mark.asyncio
    async def test_record_message_sent(self, health_monitor):
        """Test recording message sent events"""
        endpoint = "test_endpoint"
        timestamp = time.time()
        
        with patch.object(health_monitor.performance_analyzer, 'record_message_sent', new_callable=AsyncMock) as mock_perf:
            with patch.object(health_monitor.metrics_collector, 'increment_counter', new_callable=AsyncMock) as mock_metrics:
                
                await health_monitor.record_message_sent(endpoint, timestamp)
                
                mock_perf.assert_called_once_with(endpoint, timestamp)
                mock_metrics.assert_called_once_with(f"messages_sent_{endpoint}")

    @pytest.mark.asyncio
    async def test_record_message_received(self, health_monitor):
        """Test recording message received events"""
        endpoint = "test_endpoint"
        timestamp = time.time()
        
        with patch.object(health_monitor.performance_analyzer, 'record_message_received', new_callable=AsyncMock) as mock_perf:
            with patch.object(health_monitor.metrics_collector, 'increment_counter', new_callable=AsyncMock) as mock_metrics:
                with patch.object(health_monitor.performance_analyzer, 'calculate_latency', 
                                 new_callable=AsyncMock, return_value=50.0) as mock_latency:
                    
                    await health_monitor.record_message_received(endpoint, timestamp)
                    
                    mock_perf.assert_called_once_with(endpoint, timestamp)
                    mock_metrics.assert_called_once_with(f"messages_received_{endpoint}")
                    mock_latency.assert_called_once_with(endpoint, timestamp)
                    
                    # Verify latency was recorded
                    assert 50.0 in health_monitor.metrics['websocket_message_latency_ms']

    def test_get_health_status(self, health_monitor):
        """Test getting health status for endpoints"""
        endpoint = "test_endpoint"
        
        # Test unknown endpoint
        assert health_monitor.get_health_status(endpoint) == HealthStatus.UNKNOWN
        
        # Test known endpoint
        health_monitor._connection_health[endpoint] = ConnectionHealth(
            endpoint=endpoint,
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )
        
        assert health_monitor.get_health_status(endpoint) == HealthStatus.HEALTHY

    def test_get_performance_metrics(self, health_monitor):
        """Test getting performance metrics"""
        # Add some test data
        health_monitor.metrics['websocket_message_latency_ms'] = [10.0, 20.0, 30.0, 40.0, 50.0]
        health_monitor._monitoring_active.add("test_endpoint")
        
        metrics = health_monitor.get_performance_metrics()
        
        assert 'connection_count' in metrics
        assert 'endpoints_monitored' in metrics
        assert 'latency_stats' in metrics
        assert 'health_summary' in metrics
        
        assert metrics['connection_count'] == 1
        assert "test_endpoint" in metrics['endpoints_monitored']
        
        # Check latency stats
        latency_stats = metrics['latency_stats']
        assert latency_stats['min'] == 10.0
        assert latency_stats['max'] == 50.0
        assert latency_stats['avg'] == 30.0
        assert latency_stats['count'] == 5

    def test_get_connection_health(self, health_monitor):
        """Test getting connection health information"""
        endpoint = "test_endpoint"
        
        # Test unknown endpoint
        assert health_monitor.get_connection_health(endpoint) is None
        
        # Test known endpoint
        health_info = ConnectionHealth(
            endpoint=endpoint,
            status=HealthStatus.DEGRADED,
            last_check=datetime.now(),
            score=75.0,
            issues=["High latency"]
        )
        health_monitor._connection_health[endpoint] = health_info
        
        retrieved_health = health_monitor.get_connection_health(endpoint)
        assert retrieved_health == health_info

    def test_get_all_health_status(self, health_monitor):
        """Test getting all health status information"""
        # Add test data
        health_monitor._connection_health["endpoint1"] = ConnectionHealth(
            endpoint="endpoint1",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )
        health_monitor._connection_health["endpoint2"] = ConnectionHealth(
            endpoint="endpoint2",
            status=HealthStatus.CRITICAL,
            last_check=datetime.now()
        )
        
        all_health = health_monitor.get_all_health_status()
        
        assert len(all_health) == 2
        assert all_health["endpoint1"].status == HealthStatus.HEALTHY
        assert all_health["endpoint2"].status == HealthStatus.CRITICAL

    @pytest.mark.asyncio
    async def test_stop_monitoring(self, health_monitor):
        """Test stopping monitoring for an endpoint"""
        endpoint = "test_endpoint"
        health_monitor._monitoring_active.add(endpoint)
        
        with patch.object(health_monitor.connection_tracker, 'stop_tracking', new_callable=AsyncMock) as mock_stop:
            await health_monitor.stop_monitoring(endpoint)
            
            mock_stop.assert_called_once_with(endpoint)
            assert endpoint not in health_monitor._monitoring_active
            assert health_monitor.metrics['websocket_connections_active'] == 0

    def test_calculate_health_score(self, health_monitor):
        """Test health score calculation"""
        # Test healthy metrics
        healthy_metrics = {
            'error_rate': 0.01,
            'avg_latency_ms': 100,
            'throughput_msgs_per_sec': 10.0
        }
        
        score = health_monitor._calculate_health_score(healthy_metrics, healthy_metrics)
        assert score > 80  # Should be healthy
        
        # Test degraded metrics
        degraded_metrics = {
            'error_rate': 0.05,
            'avg_latency_ms': 1500,
            'throughput_msgs_per_sec': 0.5
        }
        
        score = health_monitor._calculate_health_score(degraded_metrics, degraded_metrics)
        assert 60 <= score < 80  # Should be degraded
        
        # Test critical metrics
        critical_metrics = {
            'error_rate': 0.3,
            'avg_latency_ms': 3000,
            'throughput_msgs_per_sec': 0.1
        }
        
        score = health_monitor._calculate_health_score(critical_metrics, critical_metrics)
        assert score < 60  # Should be critical

    def test_determine_health_status(self, health_monitor):
        """Test health status determination"""
        # Test healthy status
        status = health_monitor._determine_health_status(85.0, {}, {})
        assert status == HealthStatus.HEALTHY
        
        # Test degraded status
        status = health_monitor._determine_health_status(70.0, {}, {})
        assert status == HealthStatus.DEGRADED
        
        # Test critical status
        status = health_monitor._determine_health_status(50.0, {}, {})
        assert status == HealthStatus.CRITICAL

    def test_identify_issues(self, health_monitor):
        """Test issue identification"""
        # Test no issues
        healthy_metrics = {
            'error_rate': 0.01,
            'avg_latency_ms': 100,
            'throughput_msgs_per_sec': 10.0
        }
        
        issues = health_monitor._identify_issues(healthy_metrics, healthy_metrics)
        assert len(issues) == 0
        
        # Test multiple issues
        problematic_metrics = {
            'error_rate': 0.1,
            'avg_latency_ms': 2000,
            'throughput_msgs_per_sec': 0.5
        }
        
        issues = health_monitor._identify_issues(problematic_metrics, problematic_metrics)
        assert len(issues) == 3
        assert any("High error rate" in issue for issue in issues)
        assert any("High latency" in issue for issue in issues)
        assert any("Low throughput" in issue for issue in issues)

    def test_calculate_latency_stats(self, health_monitor):
        """Test latency statistics calculation"""
        # Test empty latencies
        stats = health_monitor._calculate_latency_stats([])
        assert stats['min'] == 0.0
        assert stats['max'] == 0.0
        assert stats['avg'] == 0.0
        assert stats['count'] == 0
        
        # Test with data
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = health_monitor._calculate_latency_stats(latencies)
        
        assert stats['min'] == 10.0
        assert stats['max'] == 50.0
        assert stats['avg'] == 30.0
        assert stats['count'] == 5
        assert stats['p95'] == 50.0
        assert stats['p99'] == 50.0

    def test_get_health_summary(self, health_monitor):
        """Test health summary generation"""
        # Add test data
        health_monitor._connection_health["endpoint1"] = ConnectionHealth(
            endpoint="endpoint1",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )
        health_monitor._connection_health["endpoint2"] = ConnectionHealth(
            endpoint="endpoint2",
            status=HealthStatus.DEGRADED,
            last_check=datetime.now()
        )
        health_monitor._connection_health["endpoint3"] = ConnectionHealth(
            endpoint="endpoint3",
            status=HealthStatus.CRITICAL,
            last_check=datetime.now()
        )
        
        summary = health_monitor._get_health_summary()
        
        assert summary['healthy'] == 1
        assert summary['degraded'] == 1
        assert summary['critical'] == 1
        assert summary['unknown'] == 0

    @pytest.mark.asyncio
    async def test_continuous_monitor_cancellation(self, health_monitor):
        """Test that continuous monitoring can be cancelled"""
        endpoint = "test_endpoint"
        health_monitor._monitoring_active.add(endpoint)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(
            health_monitor._continuous_monitor(endpoint, Mock())
        )
        
        # Cancel after short delay
        await asyncio.sleep(0.1)
        monitor_task.cancel()
        
        # Should complete without error
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass  # Expected

    def test_log_action(self, health_monitor, capsys):
        """Test JSON logging functionality"""
        health_monitor._log_action("test_action", {"key": "value"})
        
        captured = capsys.readouterr()
        log_output = captured.out.strip()
        
        # Should be valid JSON
        import json
        log_data = json.loads(log_output)
        
        assert log_data["task"] == "3.1"
        assert log_data["action"] == "test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["key"] == "value"
        assert "timestamp" in log_data


class TestHealthStatus:
    """Test cases for HealthStatus enum"""
    
    def test_health_status_values(self):
        """Test health status enum values"""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestConnectionHealth:
    """Test cases for ConnectionHealth dataclass"""
    
    def test_connection_health_creation(self):
        """Test ConnectionHealth creation"""
        health = ConnectionHealth(
            endpoint="test_endpoint",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now(),
            score=85.0,
            issues=["No issues"]
        )
        
        assert health.endpoint == "test_endpoint"
        assert health.status == HealthStatus.HEALTHY
        assert health.score == 85.0
        assert health.issues == ["No issues"]
        assert isinstance(health.last_check, datetime)