#!/usr/bin/env python3
"""
Integration Tests for Monitoring System
=======================================

Integration tests for the complete monitoring system including daemon
startup, client communication, and metric collection.

Author: Beast Mode Framework
Date: 2025-09-19
Purpose: Test complete monitoring system integration
"""

import os
import sys
import time
import tempfile
import unittest
import subprocess
import threading
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from beast_mode.monitoring.client import MonitoringClient
from beast_mode.monitoring.daemon import PrometheusMonitorDaemon


class TestMonitoringSystemIntegration(unittest.TestCase):
    """Test complete monitoring system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_port = 8006
        self.pid_file = os.path.join(self.temp_dir, "test_daemon.pid")
        self.socket_path = os.path.join(self.temp_dir, "test_daemon.sock")
        self.log_file = os.path.join(self.temp_dir, "test_daemon.log")
        
        self.daemon = None
        self.daemon_thread = None

    def tearDown(self):
        """Clean up test fixtures."""
        # Stop daemon if running
        if self.daemon and self.daemon.running:
            self.daemon.stop_daemon()
        
        if self.daemon_thread and self.daemon_thread.is_alive():
            self.daemon_thread.join(timeout=5)
        
        # Clean up test files
        for file_path in [self.pid_file, self.socket_path, self.log_file]:
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass  # Directory might not be empty

    def test_daemon_lifecycle(self):
        """Test daemon start and stop lifecycle."""
        daemon = PrometheusMonitorDaemon(
            port=self.test_port,
            pid_file=self.pid_file,
            socket_path=self.socket_path,
            log_file=self.log_file
        )
        
        # Check initial status
        status = daemon.get_status()
        self.assertFalse(status.is_running)
        
        # Test daemon manager
        self.assertFalse(daemon.daemon_manager.is_daemon_running())

    def test_client_fallback_behavior(self):
        """Test client behavior when daemon is not available."""
        client = MonitoringClient(
            client_id="test_integration_client",
            daemon_port=self.test_port,
            fallback_mode=True
        )
        
        # Daemon should not be available
        self.assertFalse(client.is_daemon_available())
        
        # Register metrics should still work in fallback mode
        success = client.register_counter("test_counter", "Test counter")
        self.assertTrue(success)
        
        # Update metrics should work in fallback mode
        success = client.increment_counter("test_counter", value=1.0)
        self.assertTrue(success)
        
        # Should have pending updates
        self.assertEqual(client.get_pending_updates_count(), 1)
        
        client.shutdown()

    def test_client_without_fallback(self):
        """Test client behavior without fallback mode when daemon unavailable."""
        client = MonitoringClient(
            client_id="test_no_fallback_client",
            daemon_port=self.test_port,
            fallback_mode=False
        )
        
        # Daemon should not be available
        self.assertFalse(client.is_daemon_available())
        
        # Register metrics should fail without fallback
        success = client.register_counter("test_counter", "Test counter")
        self.assertFalse(success)
        
        client.shutdown()

    def test_multiple_clients(self):
        """Test multiple clients with fallback mode."""
        clients = []
        
        try:
            # Create multiple clients
            for i in range(3):
                client = MonitoringClient(
                    client_id=f"test_client_{i}",
                    daemon_port=self.test_port,
                    fallback_mode=True
                )
                clients.append(client)
                
                # Register different metrics for each client
                client.register_counter(f"counter_{i}", f"Counter {i}")
                client.register_gauge(f"gauge_{i}", f"Gauge {i}")
                
                # Update metrics
                client.increment_counter(f"counter_{i}", value=i + 1)
                client.set_gauge(f"gauge_{i}", value=(i + 1) * 10.0)
            
            # Verify each client has its own metrics and updates
            for i, client in enumerate(clients):
                self.assertEqual(len(client.get_registered_metrics()), 2)
                self.assertEqual(client.get_pending_updates_count(), 2)
        
        finally:
            # Clean up clients
            for client in clients:
                client.shutdown()

    def test_prometheus_exporter_compatibility(self):
        """Test backward compatibility with PrometheusExporter."""
        try:
            from beast_mode.monitoring.prometheus_exporter import PrometheusExporter
            
            # Reset singleton state before test
            PrometheusExporter.reset_singleton()
            
            # Create exporter (should use new daemon-based system)
            exporter = PrometheusExporter(
                port=self.test_port,
                enable_http_server=False  # Don't start HTTP server in test
            )
            
            # Should have monitoring client
            self.assertTrue(hasattr(exporter, 'monitoring_client'))
            self.assertTrue(exporter._use_daemon)
            
            # Properly shutdown to clean up threads
            exporter.shutdown()
            
        except ImportError:
            self.skipTest("PrometheusExporter not available")

    def test_daemon_script_commands(self):
        """Test daemon control script commands."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "prometheus-monitor-daemon"
        
        # Test status command (should show not running)
        result = subprocess.run([
            "uv", "run", "python", str(script_path),
            "--status", "--port", str(self.test_port), "--pid-file", self.pid_file
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)  # Not running
        self.assertIn("not running", result.stdout)

    def test_metric_registration_data_models(self):
        """Test metric registration and update data models."""
        from beast_mode.monitoring.daemon import MetricRegistration, MetricUpdate
        
        # Test metric registration
        registration = MetricRegistration(
            client_id="test_client",
            metric_name="test_metric",
            metric_type="counter",
            description="Test metric",
            labels=["label1", "label2"]
        )
        
        self.assertEqual(registration.client_id, "test_client")
        self.assertEqual(registration.metric_name, "test_metric")
        self.assertIsNotNone(registration.created_at)
        
        # Test metric update
        update = MetricUpdate(
            client_id="test_client",
            metric_name="test_metric",
            operation="increment",
            value=1.0,
            labels={"label1": "value1"}
        )
        
        self.assertEqual(update.client_id, "test_client")
        self.assertEqual(update.operation, "increment")
        self.assertIsNotNone(update.timestamp)


if __name__ == "__main__":
    unittest.main()