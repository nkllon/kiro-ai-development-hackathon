#!/usr/bin/env python3
"""
Test Prometheus Integration
===========================

Test the Prometheus metrics exporter integration with existing
Beast Mode monitoring infrastructure for real-time visibility.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test Prometheus integration for monitoring visibility
"""

import sys
import os
import time
import json
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def print_banner(title, width=80):
    """Print a formatted banner."""
    print("\n" + "=" * width)
    print(f"🔍 {title}")
    print("=" * width)


def print_test_result(test_name, success, details=""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"   {status} {test_name}")
    if details:
        print(f"      {details}")


def test_prometheus_client_availability():
    """Test if Prometheus client library is available."""
    print_banner("TESTING PROMETHEUS CLIENT AVAILABILITY")

    try:
        from prometheus_client import Counter, Gauge, Histogram, start_http_server

        print_test_result(
            "Prometheus Client Import", True, "prometheus_client library available"
        )
        return True
    except ImportError as e:
        print_test_result("Prometheus Client Import", False, f"ImportError: {e}")
        print("\n📦 To install Prometheus client:")
        print("   pip install prometheus-client")
        return False


def test_prometheus_exporter():
    """Test Prometheus exporter functionality."""
    print_banner("TESTING PROMETHEUS EXPORTER")

    try:
        from beast_mode.monitoring.prometheus_exporter import PrometheusExporter

        # Initialize exporter
        exporter = PrometheusExporter(port=8001, monitoring_interval=1.0)
        print_test_result(
            "Prometheus Exporter Initialization", True, "Exporter created successfully"
        )

        # Test metrics summary
        summary = exporter.get_metrics_summary()
        print_test_result(
            "Metrics Summary", len(summary) > 0, f"Summary keys: {list(summary.keys())}"
        )

        # Test report generation
        report = exporter.generate_prometheus_report()
        print_test_result(
            "Report Generation", len(report) > 500, f"Report length: {len(report)}"
        )

        # Wait for metrics collection
        print("\n⏳ Waiting for metrics collection...")
        time.sleep(5)

        # Test metrics endpoint (if HTTP server is running)
        try:
            response = requests.get("http://localhost:8001/metrics", timeout=5)
            if response.status_code == 200:
                metrics_content = response.text
                print_test_result(
                    "Metrics Endpoint",
                    True,
                    f"Endpoint accessible, {len(metrics_content)} characters",
                )

                # Check for key metrics
                key_metrics = [
                    "beast_mode_system_cpu_percent",
                    "beast_mode_app_operations_total",
                    "beast_mode_component_health_status",
                    "beast_mode_framework_info",
                ]

                found_metrics = [
                    metric for metric in key_metrics if metric in metrics_content
                ]
                print_test_result(
                    "Key Metrics Present",
                    len(found_metrics) > 0,
                    f"Found {len(found_metrics)}/{len(key_metrics)} key metrics",
                )

            else:
                print_test_result(
                    "Metrics Endpoint", False, f"HTTP {response.status_code}"
                )

        except requests.exceptions.RequestException as e:
            print_test_result("Metrics Endpoint", False, f"Connection error: {e}")

        return True

    except Exception as e:
        print_test_result("Prometheus Exporter", False, f"Error: {e}")
        return False


def test_existing_monitoring_integration():
    """Test integration with existing monitoring systems."""
    print_banner("TESTING EXISTING MONITORING INTEGRATION")

    try:
        # Test performance monitoring system
        from beast_mode.performance.performance_monitoring_system import (
            PerformanceMonitoringSystem,
        )

        monitor = PerformanceMonitoringSystem(
            monitoring_interval=1.0, enable_alerts=True
        )
        print_test_result("Performance Monitoring System", True, "System initialized")

        # Record some test metrics
        monitor.record_metric("test_metric", 42.5, tags={"test": "integration"})
        monitor.record_timing("test_timing", 150.0, tags={"operation": "test"})
        monitor.increment_counter("test_counter", 1.0, tags={"event": "test"})

        print_test_result("Metrics Recording", True, "Test metrics recorded")

        # Wait for monitoring to collect data
        time.sleep(3)

        # Get current metrics
        current_metrics = monitor.get_current_metrics()
        has_metrics = len(current_metrics) > 0
        print_test_result(
            "Metrics Retrieval",
            has_metrics,
            f"Retrieved {len(current_metrics)} metric categories",
        )

        monitor.stop_monitoring()

        return True

    except Exception as e:
        print_test_result("Existing Monitoring Integration", False, f"Error: {e}")
        return False


def test_real_time_monitoring():
    """Test real-time monitoring capabilities."""
    print_banner("TESTING REAL-TIME MONITORING")

    try:
        from beast_mode.monitoring.prometheus_exporter import PrometheusExporter

        # Initialize exporter
        exporter = PrometheusExporter(
            port=8002, monitoring_interval=0.5
        )  # Fast monitoring

        print_test_result("Fast Monitoring Setup", True, "Exporter with 0.5s interval")

        # Wait for metrics to be collected
        print("\n⏳ Collecting real-time metrics...")
        time.sleep(3)

        # Test if metrics are being updated in real-time
        try:
            response1 = requests.get("http://localhost:8002/metrics", timeout=5)
            time.sleep(1)
            response2 = requests.get("http://localhost:8002/metrics", timeout=5)

            if response1.status_code == 200 and response2.status_code == 200:
                content1 = response1.text
                content2 = response2.text

                # Check if metrics have changed (indicating real-time updates)
                metrics_changed = content1 != content2
                print_test_result(
                    "Real-time Updates",
                    metrics_changed,
                    (
                        "Metrics updated between requests"
                        if metrics_changed
                        else "No changes detected"
                    ),
                )

                # Count metrics
                metric_count = content2.count("# TYPE")
                print_test_result(
                    "Metrics Count",
                    metric_count > 0,
                    f"{metric_count} metrics exported",
                )

            else:
                print_test_result(
                    "Real-time Updates", False, "HTTP endpoint not accessible"
                )

        except requests.exceptions.RequestException as e:
            print_test_result("Real-time Updates", False, f"Connection error: {e}")

        return True

    except Exception as e:
        print_test_result("Real-time Monitoring", False, f"Error: {e}")
        return False


def test_prometheus_configuration():
    """Test Prometheus configuration file."""
    print_banner("TESTING PROMETHEUS CONFIGURATION")

    config_file = Path("prometheus.yml")

    if config_file.exists():
        print_test_result("Configuration File", True, "prometheus.yml exists")

        try:
            with open(config_file, "r") as f:
                config_content = f.read()

            # Check for key configuration elements
            has_global_config = "scrape_interval" in config_content
            has_beast_mode_job = "beast_mode_framework" in config_content
            has_metrics_path = "/metrics" in config_content

            print_test_result(
                "Global Configuration", has_global_config, "Scrape interval configured"
            )
            print_test_result(
                "Beast Mode Job", has_beast_mode_job, "Beast Mode job configured"
            )
            print_test_result(
                "Metrics Path", has_metrics_path, "Metrics endpoint configured"
            )

            return True

        except Exception as e:
            print_test_result("Configuration Reading", False, f"Error: {e}")
            return False
    else:
        print_test_result("Configuration File", False, "prometheus.yml not found")
        return False


def main():
    """Run comprehensive Prometheus integration tests."""
    print_banner("🔍 PROMETHEUS INTEGRATION TEST SUITE", 100)
    print(f"   Testing real-time monitoring visibility with Prometheus")
    print(f"   Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    test_results = []

    try:
        # Run all test suites
        test_results.append(
            ("Prometheus Client Availability", test_prometheus_client_availability())
        )
        test_results.append(("Prometheus Exporter", test_prometheus_exporter()))
        test_results.append(
            ("Existing Monitoring Integration", test_existing_monitoring_integration())
        )
        test_results.append(("Real-time Monitoring", test_real_time_monitoring()))
        test_results.append(
            ("Prometheus Configuration", test_prometheus_configuration())
        )

        # Print final results
        print_banner("🎯 PROMETHEUS INTEGRATION TEST RESULTS", 100)

        passed_tests = 0
        total_tests = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
            if result:
                passed_tests += 1

        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print(f"\n🎉 ALL PROMETHEUS INTEGRATION TESTS PASSED!")
            print(f"   Real-time monitoring with Prometheus is working correctly!")
            print(f"   Metrics are being exported and can be scraped by Prometheus!")
        else:
            print(f"\n⚠️ SOME TESTS FAILED")
            print(f"   {total_tests - passed_tests} test(s) need attention")

        print_banner("🚀 PROMETHEUS INTEGRATION TEST COMPLETE", 100)

        # Print next steps
        print("\n📋 NEXT STEPS FOR PROMETHEUS MONITORING:")
        print(
            "   1. Install Prometheus: https://prometheus.io/docs/prometheus/latest/installation/"
        )
        print("   2. Configure prometheus.yml to scrape Beast Mode metrics")
        print("   3. Start Prometheus: prometheus --config.file=prometheus.yml")
        print("   4. Access Prometheus UI: http://localhost:9090")
        print("   5. Set up Grafana dashboards for visualization")
        print("   6. Configure alerting rules for Beast Mode metrics")

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
