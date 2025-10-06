"""
Unit tests for DeploymentAuditor API functionality.
"""

import pytest
import json
import threading
import time
from unittest.mock import Mock, patch
from http.server import HTTPServer

from src.deployment_auditor.api import HealthAPIHandler, HealthAPIServer, run_health_api
from src.deployment_auditor.core import DeploymentAuditor
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleHealth


class TestHealthAPIFunctionality:
    """Test cases for API functionality without HTTP handler complexity."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = DeploymentAuditor()

    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'auditor'):
            self.auditor.shutdown()

    def test_auditor_health_status_for_api(self):
        """Test that auditor provides proper health status for API."""
        health = self.auditor.get_health_status()
        
        assert health.module_id == "deployment_auditor"
        assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.DEGRADED, ModuleStatus.ERROR]
        assert 0.0 <= health.health_score <= 1.0
        assert health.uptime_seconds >= 0
        assert health.error_count >= 0
        assert health.warning_count >= 0
        assert health.last_check is not None

    def test_auditor_readiness_for_api(self):
        """Test that auditor provides readiness status for API."""
        ready = self.auditor.is_ready()
        assert isinstance(ready, bool)

    def test_auditor_metrics_for_api(self):
        """Test that auditor provides metrics for API."""
        metrics = self.auditor.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "deployment_auditor_violations_detected_total" in metrics
        assert "deployment_auditor_files_scanned_total" in metrics
        assert "deployment_auditor_monitoring_active" in metrics
        
        # All metrics should be numeric
        for key, value in metrics.items():
            assert isinstance(value, (int, float)), f"Metric {key} should be numeric"

    def test_prometheus_metrics_format(self):
        """Test that metrics can be formatted for Prometheus."""
        metrics = self.auditor.get_metrics()
        
        # Format as Prometheus text
        lines = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                lines.append(f"{key} {value}")
        
        prometheus_output = "\n".join(lines)
        
        # Validate format
        for line in lines:
            parts = line.split(' ')
            assert len(parts) == 2, f"Invalid Prometheus format: {line}"
            metric_name, value = parts
            
            # Metric name should be valid
            assert metric_name.startswith("deployment_auditor_")
            
            # Value should be numeric
            try:
                float(value)
            except ValueError:
                pytest.fail(f"Metric value should be numeric: {value}")

    def test_health_status_json_serializable(self):
        """Test that health status can be JSON serialized."""
        health = self.auditor.get_health_status()
        
        # Create JSON response like the API would
        response = {
            "status": health.status.value,
            "module_id": health.module_id,
            "health_score": health.health_score,
            "uptime_seconds": health.uptime_seconds,
            "error_count": health.error_count,
            "warning_count": health.warning_count,
            "last_check": health.last_check.isoformat(),
            "issues": health.issues[-5:] if health.issues else []
        }
        
        # Should be JSON serializable
        json_str = json.dumps(response)
        parsed = json.loads(json_str)
        
        assert parsed["module_id"] == "deployment_auditor"
        assert "status" in parsed
        assert "health_score" in parsed

    def test_readiness_json_serializable(self):
        """Test that readiness status can be JSON serialized."""
        ready = self.auditor.is_ready()
        
        response = {
            "ready": ready,
            "timestamp": "2025-10-05T14:00:00.000000"
        }
        
        # Should be JSON serializable
        json_str = json.dumps(response)
        parsed = json.loads(json_str)
        
        assert "ready" in parsed
        assert isinstance(parsed["ready"], bool)


class TestHealthAPIServer:
    """Test cases for HealthAPIServer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = DeploymentAuditor()

    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'auditor'):
            self.auditor.shutdown()

    def test_server_initialization(self):
        """Test server initialization."""
        server = HealthAPIServer(self.auditor, "127.0.0.1", 8080)
        
        assert server.auditor == self.auditor
        assert server.host == "127.0.0.1"
        assert server.port == 8080
        assert server.server is None
        assert HealthAPIHandler.auditor == self.auditor

    def test_server_start_stop(self):
        """Test server start and stop."""
        server = HealthAPIServer(self.auditor, "127.0.0.1", 0)  # Use port 0 for auto-assignment
        
        # Mock the HTTPServer
        with patch('src.deployment_auditor.api.HTTPServer') as mock_http_server:
            mock_server_instance = Mock()
            mock_http_server.return_value = mock_server_instance
            
            # Test start (in a separate thread to avoid blocking)
            def start_server():
                server.start()
            
            thread = threading.Thread(target=start_server)
            thread.daemon = True
            thread.start()
            
            # Give it a moment to start
            time.sleep(0.1)
            
            # Test stop
            server.stop()
            
            # Verify HTTPServer was created and methods called
            mock_http_server.assert_called_once_with(("127.0.0.1", 0), HealthAPIHandler)
            mock_server_instance.shutdown.assert_called_once()

    @patch('src.deployment_auditor.api.HealthAPIServer')
    def test_run_health_api(self, mock_server_class):
        """Test run_health_api function."""
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        mock_server.start.side_effect = KeyboardInterrupt()  # Simulate Ctrl+C
        
        run_health_api(self.auditor, "0.0.0.0", 8080)
        
        # Verify server was created and started
        mock_server_class.assert_called_once_with(self.auditor, "0.0.0.0", 8080)
        mock_server.start.assert_called_once()
        mock_server.stop.assert_called_once()

    @patch('src.deployment_auditor.api.HealthAPIServer')
    def test_run_health_api_keyboard_interrupt(self, mock_server_class):
        """Test run_health_api with KeyboardInterrupt."""
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        mock_server.start.side_effect = KeyboardInterrupt()
        
        # Should handle KeyboardInterrupt gracefully
        run_health_api(self.auditor, "0.0.0.0", 8080)
        
        # Should call stop on KeyboardInterrupt
        mock_server.stop.assert_called_once()


class TestAPIIntegration:
    """Integration tests for API functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = DeploymentAuditor()

    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'auditor'):
            self.auditor.shutdown()

    def test_api_data_integration(self):
        """Test that API can get data from auditor properly."""
        # Test health data
        health = self.auditor.get_health_status()
        assert health.module_id == "deployment_auditor"
        
        # Test readiness
        ready = self.auditor.is_ready()
        assert isinstance(ready, bool)
        
        # Test metrics
        metrics = self.auditor.get_metrics()
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
        
        # Test with monitoring active
        with patch('os.path.exists', return_value=True):
            self.auditor.start_monitoring()
            
        metrics_active = self.auditor.get_metrics()
        assert metrics_active["deployment_auditor_monitoring_active"] == 1
        
        self.auditor.stop_monitoring()
        metrics_inactive = self.auditor.get_metrics()
        assert metrics_inactive["deployment_auditor_monitoring_active"] == 0