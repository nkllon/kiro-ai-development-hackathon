"""
Unit tests for DeploymentAuditor core functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from src.deployment_auditor.core import DeploymentAuditor
from src.deployment_auditor.models import MonitoringStatus, Severity
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestDeploymentAuditor:
    """Test cases for DeploymentAuditor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = DeploymentAuditor()

    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'auditor'):
            self.auditor.shutdown()

    def test_initialization(self):
        """Test auditor initialization."""
        assert self.auditor.config_path == "deployment-auditor-config.yml"
        assert self.auditor.config is not None
        assert self.auditor.monitoring_status is not None
        assert not self.auditor.monitoring_status.is_active
        assert self.auditor.monitoring_status.events_processed == 0
        assert self.auditor.monitoring_status.violations_detected == 0

    def test_initialization_with_custom_config(self):
        """Test auditor initialization with custom config path."""
        custom_path = "custom-config.yml"
        auditor = DeploymentAuditor(config_path=custom_path)
        assert auditor.config_path == custom_path
        auditor.shutdown()

    def test_get_health_status(self):
        """Test health status reporting."""
        health = self.auditor.get_health_status()
        
        assert health.module_id == "deployment_auditor"
        assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.DEGRADED, ModuleStatus.ERROR]
        assert 0.0 <= health.health_score <= 1.0
        assert health.uptime_seconds >= 0
        assert health.error_count >= 0
        assert health.warning_count >= 0
        assert health.last_check is not None

    def test_get_capabilities(self):
        """Test module capabilities reporting."""
        capabilities = self.auditor.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert ModuleCapability.CORE_FUNCTIONALITY in capabilities
        assert ModuleCapability.DATA_PROCESSING in capabilities
        assert ModuleCapability.VALIDATION in capabilities
        assert ModuleCapability.MONITORING in capabilities

    def test_get_module_info(self):
        """Test module information reporting."""
        info = self.auditor.get_module_info()
        
        assert info["module_name"] == "deployment_auditor"
        assert info["module_type"] == "governance_auditor"
        assert info["version"] == "1.0.0"
        assert "configuration" in info
        assert "status" in info

    def test_is_ready(self):
        """Test readiness check."""
        ready = self.auditor.is_ready()
        assert isinstance(ready, bool)
        # Should be ready with default configuration
        assert ready is True

    def test_get_metrics(self):
        """Test metrics collection."""
        metrics = self.auditor.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "deployment_auditor_violations_detected_total" in metrics
        assert "deployment_auditor_files_scanned_total" in metrics
        assert "deployment_auditor_remediation_actions_total" in metrics
        assert "deployment_auditor_scan_duration_seconds" in metrics
        assert "deployment_auditor_monitoring_active" in metrics
        assert "deployment_auditor_watched_paths_count" in metrics

    def test_graceful_degradation(self):
        """Test graceful degradation functionality."""
        result = self.auditor.graceful_degradation()
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'degraded_capabilities')
        assert hasattr(result, 'remaining_capabilities')
        assert isinstance(result.success, bool)
        assert isinstance(result.degraded_capabilities, list)
        assert isinstance(result.remaining_capabilities, list)

    def test_scan_directory_nonexistent(self):
        """Test scanning a non-existent directory."""
        report = self.auditor.scan_directory("/nonexistent/path")
        
        assert report.total_files_scanned == 0
        assert report.violations_found == 0
        assert report.scan_timestamp is not None

    def test_scan_directory_empty(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            report = self.auditor.scan_directory(temp_dir)
            
            assert report.total_files_scanned == 0
            assert report.violations_found == 0
            assert report.scan_timestamp is not None

    def test_scan_directory_with_violations(self):
        """Test scanning a directory with governance violations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some violation files
            violation_files = [
                "test.db",
                "app.log",
                "prometheus-data/chunks_head/000001",
                "grafana-data/grafana.db",
                "cache/session.cache"
            ]
            
            for file_path in violation_files:
                full_path = Path(temp_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text("test content")
            
            # Create some non-violation files
            clean_files = [
                "docker-compose.yml",
                "nginx.conf",
                "README.md"
            ]
            
            for file_path in clean_files:
                full_path = Path(temp_dir) / file_path
                full_path.write_text("clean content")
            
            report = self.auditor.scan_directory(temp_dir)
            
            assert report.total_files_scanned == len(violation_files) + len(clean_files)
            assert report.violations_found == len(violation_files)
            assert report.scan_timestamp is not None

    def test_violation_detection(self):
        """Test the internal violation detection logic."""
        # Test violation patterns
        violation_paths = [
            "/path/to/file.db",
            "/path/to/file.sqlite",
            "/path/to/file.log",
            "/path/prometheus-data/chunks",
            "/path/grafana-data/grafana.db",
            "/path/cache/session.cache",
            "/path/tmp/temp.file",
            "/path/temp/temporary.txt"
        ]
        
        for path in violation_paths:
            assert self.auditor._is_violation(path), f"Should detect violation in {path}"
        
        # Test clean patterns
        clean_paths = [
            "/path/to/docker-compose.yml",
            "/path/to/nginx.conf",
            "/path/to/README.md",
            "/path/to/script.py",
            "/path/to/config.json"
        ]
        
        for path in clean_paths:
            assert not self.auditor._is_violation(path), f"Should not detect violation in {path}"

    def test_start_stop_monitoring(self):
        """Test monitoring lifecycle."""
        # Initially not active
        assert not self.auditor.monitoring_status.is_active
        
        # Start monitoring
        with patch('os.path.exists', return_value=True):
            success = self.auditor.start_monitoring()
            assert success
            assert self.auditor.monitoring_status.is_active
            assert len(self.auditor.monitoring_status.watched_paths) > 0
        
        # Stop monitoring
        success = self.auditor.stop_monitoring()
        assert success
        assert not self.auditor.monitoring_status.is_active

    def test_load_configuration_missing_file(self):
        """Test loading configuration when file doesn't exist."""
        success = self.auditor.load_configuration("nonexistent-config.yml")
        # Should succeed with defaults
        assert success

    def test_load_configuration_invalid_file(self):
        """Test loading configuration with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            success = self.auditor.load_configuration(temp_path)
            # Should handle gracefully
            assert not success
        finally:
            os.unlink(temp_path)

    def test_shutdown(self):
        """Test graceful shutdown."""
        # Start monitoring first
        with patch('os.path.exists', return_value=True):
            self.auditor.start_monitoring()
        
        # Shutdown should stop monitoring
        success = self.auditor.shutdown()
        assert success
        assert not self.auditor.monitoring_status.is_active

    def test_metrics_tracking(self):
        """Test that metrics are properly tracked during operations."""
        initial_metrics = self.auditor.get_metrics()
        initial_files_scanned = initial_metrics["deployment_auditor_files_scanned_total"]
        initial_violations = initial_metrics["deployment_auditor_violations_detected_total"]
        
        # Perform a scan
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a violation file
            violation_file = Path(temp_dir) / "test.db"
            violation_file.write_text("test content")
            
            self.auditor.scan_directory(temp_dir)
        
        # Check metrics were updated
        updated_metrics = self.auditor.get_metrics()
        assert updated_metrics["deployment_auditor_files_scanned_total"] > initial_files_scanned
        assert updated_metrics["deployment_auditor_violations_detected_total"] > initial_violations
        assert updated_metrics["deployment_auditor_scan_duration_seconds"] > 0

    def test_health_score_calculation(self):
        """Test health score calculation under different conditions."""
        # Initially should have good health
        health = self.auditor.get_health_status()
        initial_score = health.health_score
        
        # Simulate some errors
        self.auditor.monitoring_status.errors = ["Error 1", "Error 2", "Error 3"]
        
        health_with_errors = self.auditor.get_health_status()
        assert health_with_errors.health_score < initial_score
        assert health_with_errors.error_count == 3

    def test_prometheus_metrics_format(self):
        """Test that metrics are in proper Prometheus format."""
        metrics = self.auditor.get_metrics()
        
        # All metric names should start with the prefix
        prefix = "deployment_auditor_"
        for key in metrics.keys():
            assert key.startswith(prefix), f"Metric {key} should start with {prefix}"
        
        # All metric values should be numeric
        for key, value in metrics.items():
            assert isinstance(value, (int, float)), f"Metric {key} value should be numeric, got {type(value)}"


class TestDeploymentAuditorIntegration:
    """Integration tests for DeploymentAuditor."""

    def test_full_workflow(self):
        """Test complete auditor workflow."""
        auditor = DeploymentAuditor()
        
        try:
            # Check initial state
            assert auditor.is_ready()
            health = auditor.get_health_status()
            assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING]
            
            # Perform a scan
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create mixed content
                (Path(temp_dir) / "docker-compose.yml").write_text("version: '3'")
                (Path(temp_dir) / "violation.db").write_text("database content")
                
                report = auditor.scan_directory(temp_dir)
                assert report.total_files_scanned == 2
                assert report.violations_found == 1
            
            # Check metrics were updated
            metrics = auditor.get_metrics()
            assert metrics["deployment_auditor_files_scanned_total"] >= 2
            assert metrics["deployment_auditor_violations_detected_total"] >= 1
            
            # Test graceful degradation
            degradation = auditor.graceful_degradation()
            assert degradation.success is not None
            
        finally:
            auditor.shutdown()

    def test_beast_mode_compliance(self):
        """Test Beast Mode framework compliance."""
        auditor = DeploymentAuditor()
        
        try:
            # Test ReflectiveModule interface
            assert hasattr(auditor, 'get_health_status')
            assert hasattr(auditor, 'get_capabilities')
            assert hasattr(auditor, 'get_module_info')
            assert hasattr(auditor, 'graceful_degradation')
            assert hasattr(auditor, 'is_ready')
            assert hasattr(auditor, 'get_metrics')
            
            # Test all methods return expected types
            health = auditor.get_health_status()
            assert hasattr(health, 'status')
            assert hasattr(health, 'health_score')
            
            capabilities = auditor.get_capabilities()
            assert isinstance(capabilities, list)
            
            info = auditor.get_module_info()
            assert isinstance(info, dict)
            
            degradation = auditor.graceful_degradation()
            assert hasattr(degradation, 'success')
            
            ready = auditor.is_ready()
            assert isinstance(ready, bool)
            
            metrics = auditor.get_metrics()
            assert isinstance(metrics, dict)
            
        finally:
            auditor.shutdown()