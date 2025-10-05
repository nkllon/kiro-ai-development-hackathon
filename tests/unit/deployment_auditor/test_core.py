"""
Unit tests for deployment auditor core functionality.

Tests the main DeploymentAuditor class and its Beast Mode integration.
"""

import pytest
import tempfile
import os
import shutil
from datetime import datetime
from pathlib import Path

from src.deployment_auditor.core import DeploymentAuditor
from src.deployment_auditor.models import MonitoringStatus, ComplianceReport


class TestDeploymentAuditor:
    """Test DeploymentAuditor core functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.deployment_dir = os.path.join(self.temp_dir, "deployment")
        os.makedirs(self.deployment_dir, exist_ok=True)
        
        # Create test config file
        self.config_path = os.path.join(self.temp_dir, "test-config.yml")
        with open(self.config_path, 'w') as f:
            f.write("""
monitoring:
  watch_paths:
    - "{}"
  scan_interval: 30

patterns:
  database_files:
    patterns: ["*.db", "*.sqlite"]
    severity: "CRITICAL"

remediation:
  auto_gitignore: true
  auto_quarantine: false

prometheus:
  enabled: true
  port: 9091
""".format(self.deployment_dir))
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test DeploymentAuditor initialization."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        assert auditor.config_path == self.config_path
        assert isinstance(auditor.monitoring_status, MonitoringStatus)
        assert auditor.monitoring_status.is_active is False
        assert auditor.monitoring_status.events_processed == 0
        assert auditor.monitoring_status.violations_detected == 0
    
    def test_load_configuration(self):
        """Test configuration loading."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        result = auditor.load_configuration()
        assert result is True
        
        # Check that configuration was loaded
        assert auditor.config.monitoring["scan_interval"] == 30
        assert auditor.config.prometheus["port"] == 9091
    
    def test_load_configuration_missing_file(self):
        """Test configuration loading with missing file."""
        auditor = DeploymentAuditor(config_path="/nonexistent/config.yml")
        
        result = auditor.load_configuration()
        assert result is True  # Should succeed with defaults
    
    def test_start_monitoring(self):
        """Test starting monitoring."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        result = auditor.start_monitoring()
        assert result is True
        assert auditor.monitoring_status.is_active is True
        assert len(auditor.monitoring_status.watched_paths) > 0
        assert auditor.monitoring_status.last_scan is not None
    
    def test_start_monitoring_no_valid_paths(self):
        """Test starting monitoring with no valid paths."""
        # Create config with non-existent paths
        bad_config_path = os.path.join(self.temp_dir, "bad-config.yml")
        with open(bad_config_path, 'w') as f:
            f.write("""
monitoring:
  watch_paths:
    - "/nonexistent/path"
""")
        
        auditor = DeploymentAuditor(config_path=bad_config_path)
        
        result = auditor.start_monitoring()
        assert result is False
        assert auditor.monitoring_status.is_active is False
    
    def test_stop_monitoring(self):
        """Test stopping monitoring."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        # Start first
        auditor.start_monitoring()
        assert auditor.monitoring_status.is_active is True
        
        # Then stop
        result = auditor.stop_monitoring()
        assert result is True
        assert auditor.monitoring_status.is_active is False
    
    def test_scan_directory(self):
        """Test directory scanning functionality."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        # Create some test files
        test_file1 = os.path.join(self.deployment_dir, "test.txt")
        test_file2 = os.path.join(self.deployment_dir, "database.db")  # Should be violation
        test_file3 = os.path.join(self.deployment_dir, "app.log")      # Should be violation
        
        with open(test_file1, 'w') as f:
            f.write("normal file")
        with open(test_file2, 'w') as f:
            f.write("database content")
        with open(test_file3, 'w') as f:
            f.write("log content")
        
        # Scan directory
        report = auditor.scan_directory(self.deployment_dir)
        
        assert isinstance(report, ComplianceReport)
        assert report.total_files_scanned == 3
        assert report.violations_found >= 2  # At least the .db and .log files
        assert isinstance(report.scan_timestamp, datetime)
    
    def test_scan_nonexistent_directory(self):
        """Test scanning a non-existent directory."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        report = auditor.scan_directory("/nonexistent/directory")
        
        assert isinstance(report, ComplianceReport)
        assert report.total_files_scanned == 0
        assert report.violations_found == 0
    
    def test_is_violation_basic_patterns(self):
        """Test basic violation detection patterns."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        # Test database files
        assert auditor._is_violation("database.db") is True
        assert auditor._is_violation("data.sqlite") is True
        
        # Test log files
        assert auditor._is_violation("app.log") is True
        assert auditor._is_violation("logs/error.log") is True
        
        # Test monitoring data
        assert auditor._is_violation("prometheus-data/chunks") is True
        assert auditor._is_violation("grafana-data/grafana.db") is True
        
        # Test normal files
        assert auditor._is_violation("README.md") is False
        assert auditor._is_violation("docker-compose.yml") is False
        assert auditor._is_violation("config.json") is False
    
    def test_get_health_status(self):
        """Test health status reporting."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        auditor.start_monitoring()
        
        health = auditor.get_health_status()
        
        assert "status" in health
        assert "monitoring" in health
        assert "configuration" in health
        assert "metrics" in health
        assert "errors" in health
        
        assert health["monitoring"]["active"] is True
        assert health["monitoring"]["watched_paths"] > 0
        assert health["configuration"]["config_path"] == self.config_path
    
    def test_get_metrics(self):
        """Test Prometheus metrics export."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        auditor.start_monitoring()
        
        metrics = auditor.get_metrics()
        
        # Check for expected metric names
        expected_metrics = [
            "deployment_auditor_violations_detected_total",
            "deployment_auditor_files_scanned_total",
            "deployment_auditor_remediation_actions_total",
            "deployment_auditor_scan_duration_seconds",
            "deployment_auditor_monitoring_active",
            "deployment_auditor_watched_paths_count"
        ]
        
        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
    
    def test_is_ready(self):
        """Test readiness check."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        # Should be ready after initialization
        assert auditor.is_ready() is True
        
        # Add many errors to make it not ready
        auditor.monitoring_status.errors = ["error"] * 15
        assert auditor.is_ready() is False
    
    def test_shutdown(self):
        """Test graceful shutdown."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        auditor.start_monitoring()
        
        assert auditor.monitoring_status.is_active is True
        
        result = auditor.shutdown()
        assert result is True
        assert auditor.monitoring_status.is_active is False
    
    def test_beast_mode_integration(self):
        """Test Beast Mode ReflectiveModule integration."""
        auditor = DeploymentAuditor(config_path=self.config_path)
        
        # Test that it inherits from ReflectiveModule
        assert hasattr(auditor, 'logger')
        assert hasattr(auditor, 'get_health_status')
        assert hasattr(auditor, 'get_metrics')
        assert hasattr(auditor, 'is_ready')
        
        # Test logging functionality
        auditor.logger.info("Test log message")
        
        # Test health status structure
        health = auditor.get_health_status()
        assert isinstance(health, dict)
        
        # Test metrics structure
        metrics = auditor.get_metrics()
        assert isinstance(metrics, dict)
        
        # Test readiness
        assert isinstance(auditor.is_ready(), bool)