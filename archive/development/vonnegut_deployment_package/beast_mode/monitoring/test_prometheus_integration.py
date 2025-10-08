#!/usr/bin/env python3
"""
Prometheus Integration Test
==========================

Test script to verify Prometheus integration with base monitoring classes.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test Prometheus integration functionality
"""

import sys
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
)
from beast_mode.monitoring.prometheus_config import (
    get_prometheus_config,
    is_prometheus_enabled,
)
from beast_mode.performance.performance_monitoring_system import (
    PerformanceMonitoringSystem,
)


class TestModule(ReflectiveModule):
    """Test module for Prometheus integration testing."""

    def __init__(self, module_name: str = "test_module"):
        super().__init__()
        self.module_name = module_name
        self.module_id = f"{module_name}_{self.__class__.__name__}"
        self._error_count = 0
        self._warning_count = 0
        self._start_time = datetime.now()

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "version": "1.0.0",
            "class_name": self.__class__.__name__,
        }

    def get_capabilities(self) -> list[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.MONITORING]

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=95.0,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count,
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        from rm_ddd.core.unified_reflective_module import GracefulDegradationResult

        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities(),
        )

    def simulate_activity(self):
        """Simulate module activity."""
        self._update_activity()
        print(f"Module {self.module_id} activity simulated")

    def simulate_error(self):
        """Simulate an error."""
        self._increment_error_count()
        print(f"Module {self.module_id} error simulated")

    def simulate_warning(self):
        """Simulate a warning."""
        self._increment_warning_count()
        print(f"Module {self.module_id} warning simulated")


def test_prometheus_config():
    """Test Prometheus configuration."""
    print("=== Testing Prometheus Configuration ===")

    config = get_prometheus_config()
    print(f"Prometheus enabled: {is_prometheus_enabled()}")
    print(f"Port: {config.port}")
    print(f"Host: {config.host}")
    print(f"Service name: {config.service_name}")
    print(f"Collection interval: {config.collection_interval}s")
    print(f"Module metrics enabled: {config.enable_module_metrics}")
    print()


def test_module_integration():
    """Test module Prometheus integration."""
    print("=== Testing Module Integration ===")

    # Create test modules
    modules = [
        TestModule("test_module_1"),
        TestModule("test_module_2"),
        TestModule("test_module_3"),
    ]

    print(f"Created {len(modules)} test modules")

    # Simulate activity
    for i, module in enumerate(modules):
        print(f"\nTesting module {i+1}: {module.module_id}")

        # Simulate normal activity
        module.simulate_activity()
        time.sleep(0.1)

        # Simulate some errors and warnings
        if i % 2 == 0:
            module.simulate_error()
        if i % 3 == 0:
            module.simulate_warning()

        # Check Prometheus metrics
        metrics = module.get_prometheus_metrics()
        print(f"  Prometheus metrics: {len(metrics)} items")

        # Check health status
        health = module.get_health_status()
        print(f"  Health status: {health.status.value} (score: {health.health_score})")

    print()


def test_performance_monitoring_integration():
    """Test PerformanceMonitoringSystem Prometheus integration."""
    print("=== Testing Performance Monitoring Integration ===")

    try:
        # Create performance monitoring system
        perf_monitor = PerformanceMonitoringSystem(
            monitoring_interval=2.0, enable_alerts=True
        )

        print("Performance monitoring system created")
        print(f"Prometheus integration enabled: {perf_monitor._enable_prometheus}")

        # Let it run for a few cycles
        print("Running monitoring for 10 seconds...")
        time.sleep(10)

        # Get current metrics
        current_metrics = perf_monitor.get_current_metrics()
        print(f"Current metrics collected: {len(current_metrics)} categories")

        # Stop monitoring
        perf_monitor.stop_monitoring()
        print("Performance monitoring stopped")

    except Exception as e:
        print(f"Error testing performance monitoring: {e}")

    print()


def test_prometheus_endpoints():
    """Test Prometheus endpoints."""
    print("=== Testing Prometheus Endpoints ===")

    try:
        import requests

        # Test if Prometheus is running
        prometheus_url = "http://localhost:9090"
        response = requests.get(f"{prometheus_url}/-/ready", timeout=5)
        if response.status_code == 200:
            print("✓ Prometheus is running and ready")
        else:
            print(f"✗ Prometheus not ready (status: {response.status_code})")
            return

        # Test metrics endpoint
        metrics_url = "http://localhost:8000/metrics"
        try:
            response = requests.get(metrics_url, timeout=5)
            if response.status_code == 200:
                print("✓ Metrics endpoint is accessible")
                metrics_text = response.text
                beast_mode_metrics = [
                    line
                    for line in metrics_text.split("\n")
                    if line.startswith("beast_mode_")
                ]
                print(f"  Found {len(beast_mode_metrics)} Beast Mode metrics")

                # Show some example metrics
                for metric in beast_mode_metrics[:5]:
                    print(f"    {metric}")
                if len(beast_mode_metrics) > 5:
                    print(f"    ... and {len(beast_mode_metrics) - 5} more")
            else:
                print(
                    f"✗ Metrics endpoint not accessible (status: {response.status_code})"
                )
        except requests.exceptions.RequestException as e:
            print(f"✗ Could not connect to metrics endpoint: {e}")

    except ImportError:
        print("✗ Requests library not available for endpoint testing")
    except Exception as e:
        print(f"✗ Error testing endpoints: {e}")

    print()


def test_configuration_export():
    """Test configuration export."""
    print("=== Testing Configuration Export ===")

    try:
        from beast_mode.monitoring.prometheus_config import config_manager

        # Export JSON configuration
        json_config = config_manager.export_config("json")
        print("JSON configuration exported:")
        print(json_config[:200] + "..." if len(json_config) > 200 else json_config)

        # Get Docker Compose configuration
        docker_config = config_manager.get_docker_compose_config()
        print(
            f"\nDocker Compose environment variables: {len(docker_config['environment'])} items"
        )

        # Get Prometheus scrape configuration
        scrape_config = config_manager.get_prometheus_scrape_config()
        print(f"Prometheus scrape configuration: {scrape_config['job_name']}")

    except Exception as e:
        print(f"Error testing configuration export: {e}")

    print()


def main() -> None:
    """Run all tests."""
    print("Prometheus Integration Test Suite")
    print("=" * 50)
    print()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Run tests
        test_prometheus_config()
        test_module_integration()
        test_performance_monitoring_integration()
        test_prometheus_endpoints()
        test_configuration_export()

        print("=" * 50)
        print("All tests completed!")

    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
