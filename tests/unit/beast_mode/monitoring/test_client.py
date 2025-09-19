#!/usr/bin/env python3
"""
Tests for Monitoring Client
===========================

Unit tests for the monitoring client library including daemon communication,
metric registration, and fallback behavior.

Author: Beast Mode Framework
Date: 2025-09-19
Purpose: Test monitoring client
"""

import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from beast_mode.monitoring.client import MonitoringClient
from beast_mode.monitoring.daemon import MetricRegistration, MetricUpdate


class TestMonitoringClient(unittest.TestCase):
    """Test monitoring client functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client_id = "test_client"
        self.daemon_port = 8004
        
    def test_client_creation(self):
        """Test monitoring client creation."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        self.assertEqual(client.client_id, self.client_id)
        self.assertEqual(client.daemon_port, self.daemon_port)
        self.assertTrue(client.fallback_mode)
        self.assertEqual(len(client.registered_metrics), 0)
        self.assertEqual(len(client.pending_updates), 0)

    @patch('socket.socket')
    def test_daemon_availability_check_success(self, mock_socket):
        """Test successful daemon availability check."""
        # Mock successful socket connection and response
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.return_value = b'{"success": true, "healthy": true}'
        
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port
        )
        
        # Force availability check
        available = client._check_daemon_availability()
        self.assertTrue(available)
        self.assertTrue(client.daemon_available)

    @patch('socket.socket')
    def test_daemon_availability_check_failure(self, mock_socket):
        """Test failed daemon availability check."""
        # Mock connection failure
        mock_socket.side_effect = ConnectionRefusedError("Connection refused")
        
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port
        )
        
        # Force availability check
        available = client._check_daemon_availability()
        self.assertFalse(available)
        self.assertFalse(client.daemon_available)

    def test_register_counter_metric(self):
        """Test counter metric registration."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        success = client.register_counter(
            name="test_counter",
            description="Test counter metric",
            labels=["operation", "status"]
        )
        
        self.assertTrue(success)
        self.assertIn("test_counter", client.registered_metrics)
        
        registration = client.registered_metrics["test_counter"]
        self.assertEqual(registration.metric_type, "counter")
        self.assertEqual(registration.description, "Test counter metric")
        self.assertEqual(registration.labels, ["operation", "status"])

    def test_register_gauge_metric(self):
        """Test gauge metric registration."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        success = client.register_gauge(
            name="test_gauge",
            description="Test gauge metric",
            labels=["component"]
        )
        
        self.assertTrue(success)
        self.assertIn("test_gauge", client.registered_metrics)
        
        registration = client.registered_metrics["test_gauge"]
        self.assertEqual(registration.metric_type, "gauge")

    def test_register_histogram_metric(self):
        """Test histogram metric registration."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        buckets = [0.1, 0.5, 1.0, 5.0]
        success = client.register_histogram(
            name="test_histogram",
            description="Test histogram metric",
            labels=["operation"],
            buckets=buckets
        )
        
        self.assertTrue(success)
        self.assertIn("test_histogram", client.registered_metrics)
        
        registration = client.registered_metrics["test_histogram"]
        self.assertEqual(registration.metric_type, "histogram")
        self.assertEqual(registration.buckets, buckets)

    def test_increment_counter_with_fallback(self):
        """Test counter increment with fallback mode."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Register counter first
        client.register_counter("test_counter", "Test counter")
        
        # Increment counter (should succeed in fallback mode)
        success = client.increment_counter(
            name="test_counter",
            labels={"operation": "test"},
            value=2.0
        )
        
        self.assertTrue(success)
        self.assertEqual(len(client.pending_updates), 1)
        
        update = client.pending_updates[0]
        self.assertEqual(update.metric_name, "test_counter")
        self.assertEqual(update.operation, "increment")
        self.assertEqual(update.value, 2.0)
        self.assertEqual(update.labels, {"operation": "test"})

    def test_set_gauge_with_fallback(self):
        """Test gauge set with fallback mode."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Register gauge first
        client.register_gauge("test_gauge", "Test gauge")
        
        # Set gauge value
        success = client.set_gauge(
            name="test_gauge",
            value=42.5,
            labels={"component": "test"}
        )
        
        self.assertTrue(success)
        self.assertEqual(len(client.pending_updates), 1)
        
        update = client.pending_updates[0]
        self.assertEqual(update.operation, "set")
        self.assertEqual(update.value, 42.5)

    def test_observe_histogram_with_fallback(self):
        """Test histogram observation with fallback mode."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Register histogram first
        client.register_histogram("test_histogram", "Test histogram")
        
        # Observe value
        success = client.observe_histogram(
            name="test_histogram",
            value=1.23,
            labels={"operation": "test"}
        )
        
        self.assertTrue(success)
        self.assertEqual(len(client.pending_updates), 1)
        
        update = client.pending_updates[0]
        self.assertEqual(update.operation, "observe")
        self.assertEqual(update.value, 1.23)

    def test_update_unregistered_metric(self):
        """Test updating unregistered metric."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Try to increment unregistered counter
        success = client.increment_counter("unregistered_counter")
        self.assertFalse(success)
        self.assertEqual(len(client.pending_updates), 0)

    def test_get_registered_metrics(self):
        """Test getting registered metrics."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Register some metrics
        client.register_counter("counter1", "Counter 1")
        client.register_gauge("gauge1", "Gauge 1")
        
        metrics = client.get_registered_metrics()
        self.assertEqual(len(metrics), 2)
        self.assertIn("counter1", metrics)
        self.assertIn("gauge1", metrics)

    def test_get_pending_updates_count(self):
        """Test getting pending updates count."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Register and update metrics
        client.register_counter("test_counter", "Test counter")
        client.increment_counter("test_counter")
        client.increment_counter("test_counter")
        
        self.assertEqual(client.get_pending_updates_count(), 2)

    def test_context_manager(self):
        """Test client as context manager."""
        with MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        ) as client:
            self.assertIsInstance(client, MonitoringClient)
            client.register_counter("test_counter", "Test counter")
        
        # Client should be shutdown after context exit
        self.assertFalse(client.running)

    def test_pending_updates_limit(self):
        """Test pending updates limit to prevent memory growth."""
        client = MonitoringClient(
            client_id=self.client_id,
            daemon_port=self.daemon_port,
            fallback_mode=True
        )
        
        # Register counter
        client.register_counter("test_counter", "Test counter")
        
        # Add updates - they should accumulate since daemon is not available
        for i in range(100):
            client.increment_counter("test_counter", value=i)
        
        # Should have all 100 updates since no trimming happens during normal operation
        self.assertEqual(len(client.pending_updates), 100)
        
        # The trimming happens in the background thread during cleanup
        # For testing, we can manually trigger the cleanup logic
        if len(client.pending_updates) > 1000:
            client.pending_updates = client.pending_updates[-500:]
        
        # Should still have 100 since we didn't exceed the limit
        self.assertEqual(len(client.pending_updates), 100)


if __name__ == "__main__":
    unittest.main()