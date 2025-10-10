#!/usr/bin/env python3
"""Simple test runner for WebSocket health validation tests."""

import sys
import os
import json
from datetime import datetime

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, project_root)

def log_action(action, details):
    """Log action in JSON format as required."""
    log_data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'task': '2.3',
        'action': f'test_runner_{action}',
        'status': 'in_progress',
        'details': details
    }
    print(json.dumps(log_data))

def run_health_validator_tests():
    """Run health validator tests."""
    log_action("running_health_validator_tests", {"test_file": "test_health_validator.py"})
    
    try:
        from test_health_validator import TestWebSocketHealthValidator, TestQualityMetrics, TestFailureIndicator, TestHealthCheckResult
        
        # Test WebSocketHealthValidator initialization
        validator = TestWebSocketHealthValidator()
        test_validator = validator.validator()
        
        # Test basic functionality
        assert test_validator.endpoints == [
            '/ws/emoji-rain',
            '/ws/observatory',
            '/ws/anomalies',
            '/ws/doctor-status'
        ]
        assert test_validator.timeout == 1.0
        assert test_validator.max_retries == 2
        
        # Test QualityMetrics
        metrics_test = TestQualityMetrics()
        metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        assert metrics.endpoint == '/ws/emoji-rain'
        assert metrics.response_time_ms == 100.0
        
        # Test FailureIndicator
        failure_test = TestFailureIndicator()
        failure = FailureIndicator(
            endpoint='/ws/emoji-rain',
            failure_type='slow_response',
            severity='medium',
            description='Response time exceeds threshold',
            metadata={'response_time_ms': 2000.0}
        )
        assert failure.endpoint == '/ws/emoji-rain'
        assert failure.failure_type == 'slow_response'
        
        # Test HealthCheckResult
        result_test = TestHealthCheckResult()
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0,
            quality_metrics=metrics
        )
        assert result.endpoint == '/ws/emoji-rain'
        assert result.status == HealthStatus.HEALTHY
        
        log_action("health_validator_tests_passed", {"tests_run": 4})
        return True
        
    except Exception as e:
        log_action("health_validator_tests_failed", {"error": str(e)})
        return False

def run_endpoint_monitor_tests():
    """Run endpoint monitor tests."""
    log_action("running_endpoint_monitor_tests", {"test_file": "test_endpoint_monitor.py"})
    
    try:
        from test_endpoint_monitor import TestMonitoringConfig, TestAlert, TestEndpointMonitor
        
        # Test MonitoringConfig
        config_test = TestMonitoringConfig()
        config = MonitoringConfig()
        assert config.check_interval_seconds == 30.0
        assert config.health_check_timeout == 5.0
        
        # Test Alert
        alert_test = TestAlert()
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='endpoint_unhealthy',
            severity='critical',
            message='Endpoint is unhealthy',
            metadata={'response_time_ms': 5000.0}
        )
        assert alert.endpoint == '/ws/emoji-rain'
        assert alert.alert_type == 'endpoint_unhealthy'
        
        # Test EndpointMonitor
        monitor_test = TestEndpointMonitor()
        monitor = monitor_test.monitor()
        assert monitor.config.check_interval_seconds == 1.0
        assert monitor.health_validator is not None
        
        log_action("endpoint_monitor_tests_passed", {"tests_run": 3})
        return True
        
    except Exception as e:
        log_action("endpoint_monitor_tests_failed", {"error": str(e)})
        return False

def run_quality_metrics_tests():
    """Run quality metrics tests."""
    log_action("running_quality_metrics_tests", {"test_file": "test_quality_metrics.py"})
    
    try:
        from test_quality_metrics import (
            TestMetricsSnapshot, 
            TestMetricsAggregation, 
            TestQualityThresholds, 
            TestQualityMetricsCollector
        )
        
        # Test MetricsSnapshot
        snapshot_test = TestMetricsSnapshot()
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0,
            active_connections=5,
            message_count=100,
            bytes_sent=5000,
            bytes_received=3000
        )
        assert snapshot.endpoint == '/ws/emoji-rain'
        assert snapshot.response_time_ms == 100.0
        
        # Test QualityThresholds
        thresholds_test = TestQualityThresholds()
        thresholds = QualityThresholds()
        assert thresholds.response_time_ms == 1000.0
        assert thresholds.error_rate == 0.05
        
        # Test QualityMetricsCollector
        collector_test = TestQualityMetricsCollector()
        collector = collector_test.collector()
        assert collector.max_history_size == 1000
        assert collector._quality_thresholds is not None
        
        log_action("quality_metrics_tests_passed", {"tests_run": 3})
        return True
        
    except Exception as e:
        log_action("quality_metrics_tests_failed", {"error": str(e)})
        return False

def main():
    """Run all WebSocket health validation tests."""
    log_action("test_suite_started", {"total_test_files": 3})
    
    results = []
    
    # Run all test suites
    results.append(("health_validator", run_health_validator_tests()))
    results.append(("endpoint_monitor", run_endpoint_monitor_tests()))
    results.append(("quality_metrics", run_quality_metrics_tests()))
    
    # Calculate summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    log_action("test_suite_completed", {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "success_rate": f"{(passed/total)*100:.1f}%"
    })
    
    if passed == total:
        log_action("all_tests_passed", {"status": "success"})
        return 0
    else:
        log_action("some_tests_failed", {"status": "failure"})
        return 1

if __name__ == "__main__":
    sys.exit(main())