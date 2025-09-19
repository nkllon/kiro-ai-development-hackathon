#!/usr/bin/env python3
"""
Tests for Prometheus Monitor Daemon
===================================

Unit tests for the daemon infrastructure including PID management,
service lifecycle, and metric registration.

Author: Beast Mode Framework
Date: 2025-09-19
Purpose: Test daemon infrastructure
"""

import os
import sys
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from beast_mode.monitoring.daemon import (
    DaemonManager,
    PrometheusMonitorDaemon,
    MetricRegistration,
    MetricUpdate
)


class TestDaemonManager(unittest.TestCase):
    """Test daemon process management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = os.path.join(self.temp_dir, "test_daemon.pid")
        self.daemon_manager = DaemonManager(self.pid_file)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any test PID files
        if os.path.exists(self.pid_file):
            os.unlink(self.pid_file)
        os.rmdir(self.temp_dir)

    def test_write_and_read_pid_file(self):
        """Test PID file write and read operations."""
        test_pid = 12345
        
        # Write PID file
        self.daemon_manager.write_pid_file(test_pid)
        self.assertTrue(os.path.exists(self.pid_file))
        
        # Read PID file
        read_pid = self.daemon_manager.read_pid_file()
        self.assertEqual(read_pid, test_pid)

    def test_read_nonexistent_pid_file(self):
        """Test reading non-existent PID file."""
        read_pid = self.daemon_manager.read_pid_file()
        self.assertIsNone(read_pid)

    def test_cleanup_stale_pid(self):
        """Test cleanup of stale PID file."""
        # Create a PID file
        self.daemon_manager.write_pid_file(12345)
        self.assertTrue(os.path.exists(self.pid_file))
        
        # Clean up
        self.daemon_manager.cleanup_stale_pid()
        self.assertFalse(os.path.exists(self.pid_file))

    @patch('os.kill')
    def test_is_daemon_running_with_valid_process(self, mock_kill):
        """Test daemon running check with valid process."""
        # Mock successful signal send (process exists)
        mock_kill.return_value = None
        
        # Write PID file
        self.daemon_manager.write_pid_file(12345)
        
        # Check if daemon is running
        is_running = self.daemon_manager.is_daemon_running()
        self.assertTrue(is_running)
        mock_kill.assert_called_once_with(12345, 0)

    @patch('os.kill')
    def test_is_daemon_running_with_invalid_process(self, mock_kill):
        """Test daemon running check with invalid process."""
        # Mock OSError (process doesn't exist)
        mock_kill.side_effect = OSError("No such process")
        
        # Write PID file
        self.daemon_manager.write_pid_file(12345)
        
        # Check if daemon is running
        is_running = self.daemon_manager.is_daemon_running()
        self.assertFalse(is_running)
        
        # PID file should be cleaned up
        self.assertFalse(os.path.exists(self.pid_file))


class TestMetricRegistration(unittest.TestCase):
    """Test metric registration data model."""
    
    def test_metric_registration_creation(self):
        """Test creating metric registration."""
        registration = MetricRegistration(
            client_id="test_client",
            metric_name="test_counter",
            metric_type="counter",
            description="Test counter metric",
            labels=["label1", "label2"]
        )
        
        self.assertEqual(registration.client_id, "test_client")
        self.assertEqual(registration.metric_name, "test_counter")
        self.assertEqual(registration.metric_type, "counter")
        self.assertEqual(registration.description, "Test counter metric")
        self.assertEqual(registration.labels, ["label1", "label2"])
        self.assertIsNotNone(registration.created_at)

    def test_histogram_registration_with_buckets(self):
        """Test histogram registration with custom buckets."""
        buckets = [0.1, 0.5, 1.0, 5.0]
        registration = MetricRegistration(
            client_id="test_client",
            metric_name="test_histogram",
            metric_type="histogram",
            description="Test histogram metric",
            labels=["operation"],
            buckets=buckets
        )
        
        self.assertEqual(registration.buckets, buckets)


class TestMetricUpdate(unittest.TestCase):
    """Test metric update data model."""
    
    def test_metric_update_creation(self):
        """Test creating metric update."""
        labels = {"operation": "test", "status": "success"}
        update = MetricUpdate(
            client_id="test_client",
            metric_name="test_counter",
            operation="increment",
            value=1.0,
            labels=labels
        )
        
        self.assertEqual(update.client_id, "test_client")
        self.assertEqual(update.metric_name, "test_counter")
        self.assertEqual(update.operation, "increment")
        self.assertEqual(update.value, 1.0)
        self.assertEqual(update.labels, labels)
        self.assertIsNotNone(update.timestamp)


class TestPrometheusMonitorDaemon(unittest.TestCase):
    """Test Prometheus monitor daemon."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = os.path.join(self.temp_dir, "test_daemon.pid")
        self.socket_path = os.path.join(self.temp_dir, "test_daemon.sock")
        self.log_file = os.path.join(self.temp_dir, "test_daemon.log")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test files
        for file_path in [self.pid_file, self.socket_path, self.log_file]:
            if os.path.exists(file_path):
                os.unlink(file_path)
        os.rmdir(self.temp_dir)

    @patch('beast_mode.monitoring.daemon.PROMETHEUS_AVAILABLE', False)
    def test_daemon_creation_without_prometheus(self):
        """Test daemon creation when Prometheus is not available."""
        daemon = PrometheusMonitorDaemon(
            port=8001,
            pid_file=self.pid_file,
            socket_path=self.socket_path,
            log_file=self.log_file
        )
        
        self.assertEqual(daemon.port, 8001)
        self.assertEqual(daemon.pid_file, self.pid_file)
        self.assertIsNone(daemon.registry)

    @patch('beast_mode.monitoring.daemon.PROMETHEUS_AVAILABLE', True)
    def test_daemon_creation_with_prometheus(self):
        """Test daemon creation when Prometheus is available."""
        with patch('beast_mode.monitoring.daemon.CollectorRegistry') as mock_registry:
            daemon = PrometheusMonitorDaemon(
                port=8002,
                pid_file=self.pid_file,
                socket_path=self.socket_path,
                log_file=self.log_file
            )
            
            self.assertEqual(daemon.port, 8002)
            self.assertIsNotNone(daemon.registry)
            mock_registry.assert_called_once()

    def test_metric_registration(self):
        """Test metric registration functionality."""
        with patch('beast_mode.monitoring.daemon.PROMETHEUS_AVAILABLE', True), \
             patch('beast_mode.monitoring.daemon.Counter') as mock_counter, \
             patch('beast_mode.monitoring.daemon.CollectorRegistry'):
            
            daemon = PrometheusMonitorDaemon(
                pid_file=self.pid_file,
                socket_path=self.socket_path,
                log_file=self.log_file
            )
            
            registration = MetricRegistration(
                client_id="test_client",
                metric_name="test_counter",
                metric_type="counter",
                description="Test counter",
                labels=["label1"]
            )
            
            success = daemon.register_metric(registration)
            self.assertTrue(success)
            
            # Verify metric was registered
            metric_key = "test_client:test_counter"
            self.assertIn(metric_key, daemon.registered_metrics)
            self.assertIn("test_client", daemon.registered_clients)

    def test_get_status(self):
        """Test daemon status reporting."""
        daemon = PrometheusMonitorDaemon(
            port=8003,
            pid_file=self.pid_file,
            socket_path=self.socket_path,
            log_file=self.log_file
        )
        
        status = daemon.get_status()
        
        self.assertFalse(status.is_running)  # Daemon not started
        self.assertEqual(status.port, 8003)
        self.assertEqual(status.registered_clients, [])
        self.assertEqual(status.total_metrics, 0)


if __name__ == "__main__":
    unittest.main()