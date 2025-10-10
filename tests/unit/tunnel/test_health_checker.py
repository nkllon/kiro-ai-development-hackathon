"""
Unit tests for HealthChecker module.

Tests automated health monitoring, retry mechanisms, alert generation,
and health trend analysis for tunnel connectivity.
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.observatory.tunnel.health_checker import (
    HealthChecker, 
    HealthCheckConfig, 
    HealthCheckResult
)


class TestHealthChecker:
    """Test cases for HealthChecker class."""
    
    @pytest.fixture
    def health_checker(self):
        """Create HealthChecker instance for testing."""
        config = HealthCheckConfig(
            check_interval_seconds=1,
            timeout_seconds=5,
            retry_count=2,
            alert_threshold=2
        )
        return HealthChecker(config)
    
    @pytest.fixture
    def default_health_checker(self):
        """Create HealthChecker with default config."""
        return HealthChecker()
    
    def test_initialization(self, health_checker):
        """Test HealthChecker initialization."""
        assert health_checker.module_id == "tunnel_health_checker"
        assert health_checker.config.check_interval_seconds == 1
        assert health_checker.config.timeout_seconds == 5
        assert health_checker.config.retry_count == 2
        assert health_checker.config.alert_threshold == 2
        assert health_checker._is_monitoring is False
        assert health_checker._total_checks == 0
        assert health_checker._successful_checks == 0
        assert health_checker._failed_checks == 0
        assert health_checker._warning_checks == 0
    
    def test_initialization_default_config(self, default_health_checker):
        """Test HealthChecker initialization with default config."""
        assert default_health_checker.config.check_interval_seconds == 30
        assert default_health_checker.config.timeout_seconds == 10
        assert default_health_checker.config.retry_count == 3
        assert default_health_checker.config.alert_threshold == 3
    
    @pytest.mark.asyncio
    async def test_start_monitoring_success(self, health_checker):
        """Test successful monitoring start."""
        result = await health_checker.start_monitoring()
        
        assert result is True
        assert health_checker._is_monitoring is True
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_running(self, health_checker):
        """Test starting monitoring when already running."""
        health_checker._is_monitoring = True
        
        result = await health_checker.start_monitoring()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_success(self, health_checker):
        """Test successful monitoring stop."""
        health_checker._is_monitoring = True
        
        result = await health_checker.stop_monitoring()
        
        assert result is True
        assert health_checker._is_monitoring is False
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_not_running(self, health_checker):
        """Test stopping monitoring when not running."""
        result = await health_checker.stop_monitoring()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_run_health_check_comprehensive_success(self, health_checker):
        """Test successful comprehensive health check."""
        with patch.object(health_checker, '_run_comprehensive_check') as mock_check:
            mock_check.return_value = HealthCheckResult(
                check_name="comprehensive",
                status="healthy",
                message="All systems operational",
                timestamp=datetime.now(),
                duration_ms=100.0,
                details={"test": "data"}
            )
            
            result = await health_checker.run_health_check("comprehensive")
            
            assert result.status == "healthy"
            assert result.message == "All systems operational"
            assert health_checker._total_checks == 1
            assert health_checker._successful_checks == 1
            assert health_checker._failed_checks == 0
            assert health_checker._consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_run_health_check_comprehensive_failure(self, health_checker):
        """Test comprehensive health check failure."""
        with patch.object(health_checker, '_run_comprehensive_check') as mock_check:
            mock_check.return_value = HealthCheckResult(
                check_name="comprehensive",
                status="error",
                message="System failure",
                timestamp=datetime.now(),
                duration_ms=100.0,
                details={"error": "test error"}
            )
            
            result = await health_checker.run_health_check("comprehensive")
            
            assert result.status == "error"
            assert result.message == "System failure"
            assert health_checker._total_checks == 1
            assert health_checker._successful_checks == 0
            assert health_checker._failed_checks == 1
            assert health_checker._consecutive_failures == 1
    
    @pytest.mark.asyncio
    async def test_run_health_check_warning(self, health_checker):
        """Test health check with warning status."""
        with patch.object(health_checker, '_run_comprehensive_check') as mock_check:
            mock_check.return_value = HealthCheckResult(
                check_name="comprehensive",
                status="warning",
                message="System warning",
                timestamp=datetime.now(),
                duration_ms=100.0,
                details={"warning": "test warning"}
            )
            
            result = await health_checker.run_health_check("comprehensive")
            
            assert result.status == "warning"
            assert result.message == "System warning"
            assert health_checker._warning_checks == 1
            assert health_checker._consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_run_health_check_exception(self, health_checker):
        """Test health check with exception."""
        with patch.object(health_checker, '_run_comprehensive_check') as mock_check:
            mock_check.side_effect = Exception("Test error")
            
            result = await health_checker.run_health_check("comprehensive")
            
            assert result.status == "error"
            assert "Health check failed" in result.message
            assert health_checker._failed_checks == 1
            assert health_checker._consecutive_failures == 1
    
    @pytest.mark.asyncio
    async def test_run_quick_check_success(self, health_checker):
        """Test successful quick health check."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="12345\n")
            
            result = await health_checker._run_quick_check()
            
            assert result.status == "healthy"
            assert result.message == "Cloudflared process is running"
            assert result.details["is_running"] is True
    
    @pytest.mark.asyncio
    async def test_run_quick_check_failure(self, health_checker):
        """Test quick health check failure."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            
            result = await health_checker._run_quick_check()
            
            assert result.status == "error"
            assert result.message == "Cloudflared process not found"
            assert result.details["is_running"] is False
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_check_success(self, health_checker):
        """Test successful comprehensive check."""
        with patch('src.beast_mode.observatory.tunnel.diagnostics.TunnelDiagnostics') as mock_diagnostics:
            mock_instance = MagicMock()
            mock_diagnostics.return_value = mock_instance
            mock_instance.run_comprehensive_diagnostics.return_value = {
                "health_assessment": {"status": "healthy"},
                "diagnostics": {"test": "data"}
            }
            
            result = await health_checker._run_comprehensive_check()
            
            assert result.status == "healthy"
            assert result.message == "All tunnel systems operational"
            assert "diagnostics" in result.details
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_check_warning(self, health_checker):
        """Test comprehensive check with warning."""
        with patch('src.beast_mode.observatory.tunnel.diagnostics.TunnelDiagnostics') as mock_diagnostics:
            mock_instance = MagicMock()
            mock_diagnostics.return_value = mock_instance
            mock_instance.run_comprehensive_diagnostics.return_value = {
                "health_assessment": {"status": "warning"},
                "diagnostics": {"test": "data"}
            }
            
            result = await health_checker._run_comprehensive_check()
            
            assert result.status == "warning"
            assert result.message == "Tunnel systems have warnings"
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_check_error(self, health_checker):
        """Test comprehensive check with error."""
        with patch('src.beast_mode.observatory.tunnel.diagnostics.TunnelDiagnostics') as mock_diagnostics:
            mock_instance = MagicMock()
            mock_diagnostics.return_value = mock_instance
            mock_instance.run_comprehensive_diagnostics.return_value = {
                "health_assessment": {"status": "error"},
                "diagnostics": {"test": "data"}
            }
            
            result = await health_checker._run_comprehensive_check()
            
            assert result.status == "error"
            assert result.message == "Critical tunnel issues detected"
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_check_exception(self, health_checker):
        """Test comprehensive check with exception."""
        with patch('src.beast_mode.observatory.tunnel.diagnostics.TunnelDiagnostics') as mock_diagnostics:
            mock_diagnostics.side_effect = Exception("Import error")
            
            result = await health_checker._run_comprehensive_check()
            
            assert result.status == "error"
            assert "Comprehensive check failed" in result.message
    
    @pytest.mark.asyncio
    async def test_check_alert_conditions_no_alert(self, health_checker):
        """Test alert conditions when no alert should be triggered."""
        health_checker._consecutive_failures = 1
        health_checker._alert_callbacks = []
        
        result = HealthCheckResult(
            check_name="test",
            status="error",
            message="Test error",
            timestamp=datetime.now(),
            duration_ms=100.0,
            details={}
        )
        
        await health_checker._check_alert_conditions(result)
        
        # Should not trigger alert with only 1 failure
        assert health_checker._consecutive_failures == 1
    
    @pytest.mark.asyncio
    async def test_check_alert_conditions_trigger_alert(self, health_checker):
        """Test alert conditions when alert should be triggered."""
        health_checker._consecutive_failures = 3  # Above threshold
        health_checker._last_successful_check = datetime.now() - timedelta(minutes=5)
        
        alert_callback_called = False
        
        def mock_callback(result):
            nonlocal alert_callback_called
            alert_callback_called = True
            assert result.check_name == "alert"
            assert result.status == "error"
            assert "consecutive failures" in result.message
        
        health_checker._alert_callbacks = [mock_callback]
        
        result = HealthCheckResult(
            check_name="test",
            status="error",
            message="Test error",
            timestamp=datetime.now(),
            duration_ms=100.0,
            details={}
        )
        
        await health_checker._check_alert_conditions(result)
        
        assert alert_callback_called is True
    
    @pytest.mark.asyncio
    async def test_check_alert_conditions_callback_exception(self, health_checker):
        """Test alert conditions with callback exception."""
        health_checker._consecutive_failures = 3
        
        def failing_callback(result):
            raise Exception("Callback error")
        
        health_checker._alert_callbacks = [failing_callback]
        
        result = HealthCheckResult(
            check_name="test",
            status="error",
            message="Test error",
            timestamp=datetime.now(),
            duration_ms=100.0,
            details={}
        )
        
        # Should not raise exception
        await health_checker._check_alert_conditions(result)
    
    def test_add_alert_callback(self, health_checker):
        """Test adding alert callback."""
        def test_callback(result):
            pass
        
        initial_count = len(health_checker._alert_callbacks)
        health_checker.add_alert_callback(test_callback)
        
        assert len(health_checker._alert_callbacks) == initial_count + 1
        assert test_callback in health_checker._alert_callbacks
    
    def test_get_health_summary_no_history(self, health_checker):
        """Test health summary with no history."""
        summary = health_checker.get_health_summary()
        
        assert summary["status"] == "unknown"
        assert summary["total_checks"] == 0
        assert summary["success_rate"] == 0.0
        assert summary["last_check"] is None
        assert summary["consecutive_failures"] == 0
    
    def test_get_health_summary_with_history(self, health_checker):
        """Test health summary with history."""
        # Add some test results
        health_checker._total_checks = 10
        health_checker._successful_checks = 8
        health_checker._failed_checks = 1
        health_checker._warning_checks = 1
        health_checker._consecutive_failures = 0
        
        # Add a recent result
        recent_result = HealthCheckResult(
            check_name="test",
            status="healthy",
            message="Test",
            timestamp=datetime.now(),
            duration_ms=100.0,
            details={}
        )
        health_checker._health_history = [recent_result]
        
        summary = health_checker.get_health_summary()
        
        assert summary["status"] == "healthy"
        assert summary["total_checks"] == 10
        assert summary["successful_checks"] == 8
        assert summary["failed_checks"] == 1
        assert summary["warning_checks"] == 1
        assert summary["success_rate"] == 0.8
        assert summary["consecutive_failures"] == 0
        assert summary["last_status"] == "healthy"
    
    def test_get_health_summary_warning_status(self, health_checker):
        """Test health summary with warning status."""
        health_checker._total_checks = 10
        health_checker._successful_checks = 7
        health_checker._failed_checks = 2
        health_checker._warning_checks = 1
        
        summary = health_checker.get_health_summary()
        
        assert summary["status"] == "warning"
        assert summary["success_rate"] == 0.7
    
    def test_get_health_summary_error_status(self, health_checker):
        """Test health summary with error status."""
        health_checker._total_checks = 10
        health_checker._successful_checks = 3
        health_checker._failed_checks = 7
        health_checker._warning_checks = 0
        
        summary = health_checker.get_health_summary()
        
        assert summary["status"] == "error"
        assert summary["success_rate"] == 0.3
    
    def test_log_action(self, health_checker, capsys):
        """Test logging action functionality."""
        health_checker.log_action("test_action", "completed", {"test": "data"})
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.out.strip())
        
        assert log_data["task"] == "3.2"
        assert log_data["action"] == "test_action"
        assert log_data["status"] == "completed"
        assert log_data["details"]["test"] == "data"
        assert "timestamp" in log_data
    
    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self, health_checker):
        """Test get_health_status when healthy."""
        health_checker._total_checks = 10
        health_checker._successful_checks = 10
        health_checker._failed_checks = 0
        health_checker._warning_checks = 0
        
        health = await health_checker.get_health_status()
        
        assert health.module_id == "tunnel_health_checker"
        assert health.status.value == "healthy"
        assert health.health_score == 1.0
        assert health.issues == []
    
    @pytest.mark.asyncio
    async def test_get_health_status_warning(self, health_checker):
        """Test get_health_status with warning."""
        health_checker._total_checks = 10
        health_checker._successful_checks = 7
        health_checker._failed_checks = 2
        health_checker._warning_checks = 1
        
        health = await health_checker.get_health_status()
        
        assert health.status.value == "warning"
        assert health.health_score == 0.7
        assert len(health.issues) == 1
        assert "warnings detected" in health.issues[0]
    
    @pytest.mark.asyncio
    async def test_get_health_status_error(self, health_checker):
        """Test get_health_status with error."""
        health_checker._total_checks = 10
        health_checker._successful_checks = 3
        health_checker._failed_checks = 7
        health_checker._warning_checks = 0
        health_checker._consecutive_failures = 5
        
        health = await health_checker.get_health_status()
        
        assert health.status.value == "error"
        assert health.health_score == 0.3
        assert len(health.issues) == 1
        assert "failures: 5 consecutive" in health.issues[0]
    
    @pytest.mark.asyncio
    async def test_get_health_status_exception(self, health_checker):
        """Test get_health_status with exception."""
        # Force an exception by corrupting internal state
        health_checker._total_checks = -1
        
        health = await health_checker.get_health_status()
        
        assert health.status.value == "error"
        assert health.health_score == 0.0
        assert "Health status check failed" in health.issues[0]