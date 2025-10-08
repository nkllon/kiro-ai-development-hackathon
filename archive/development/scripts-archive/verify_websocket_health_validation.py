#!/usr/bin/env python3
"""Verification script for WebSocket health validation implementation."""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def log_action(action, details):
    """Log action in JSON format as required."""
    log_data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'task': '2.3',
        'action': f'verification_{action}',
        'status': 'in_progress',
        'details': details
    }
    print(json.dumps(log_data))

def verify_files_exist():
    """Verify all required files exist."""
    log_action("checking_files_exist", {})
    
    required_files = [
        'src/beast_mode/observatory/websocket/health_validator.py',
        'src/beast_mode/observatory/websocket/endpoint_monitor.py',
        'src/beast_mode/observatory/websocket/quality_metrics.py',
        'src/beast_mode/observatory/websocket/failure_detector.py',
        'tests/unit/websocket/test_health_validator.py',
        'tests/unit/websocket/test_endpoint_monitor.py',
        'tests/unit/websocket/test_quality_metrics.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        log_action("files_missing", {"missing_files": missing_files})
        return False
    
    log_action("all_files_exist", {"file_count": len(required_files)})
    return True

def verify_file_sizes():
    """Verify files have substantial content."""
    log_action("checking_file_sizes", {})
    
    file_size_requirements = {
        'src/beast_mode/observatory/websocket/health_validator.py': 50,
        'src/beast_mode/observatory/websocket/endpoint_monitor.py': 30,
        'src/beast_mode/observatory/websocket/quality_metrics.py': 40,
        'tests/unit/websocket/test_health_validator.py': 30
    }
    
    size_issues = []
    for file_path, min_lines in file_size_requirements.items():
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if len(lines) < min_lines:
                    size_issues.append(f"{file_path}: {len(lines)} lines (minimum: {min_lines})")
    
    if size_issues:
        log_action("file_size_issues", {"issues": size_issues})
        return False
    
    log_action("file_sizes_adequate", {"checked_files": len(file_size_requirements)})
    return True

def verify_imports():
    """Verify imports work correctly."""
    log_action("checking_imports", {})
    
    try:
        # Test health validator imports
        from src.beast_mode.observatory.websocket.health_validator import (
            WebSocketHealthValidator,
            HealthStatus,
            QualityMetrics,
            FailureIndicator,
            HealthCheckResult
        )
        
        # Test endpoint monitor imports
        from src.beast_mode.observatory.websocket.endpoint_monitor import (
            EndpointMonitor,
            MonitoringConfig,
            Alert
        )
        
        # Test quality metrics imports
        from src.beast_mode.observatory.websocket.quality_metrics import (
            QualityMetricsCollector,
            MetricsSnapshot,
            MetricsAggregation,
            QualityThresholds
        )
        
        # Test failure detector imports
        from src.beast_mode.observatory.websocket.failure_detector import (
            FailureDetector,
            FailureRule,
            FailureType,
            FailureSeverity
        )
        
        log_action("imports_successful", {"modules_imported": 4})
        return True
        
    except Exception as e:
        log_action("import_failed", {"error": str(e)})
        return False

def verify_class_functionality():
    """Verify basic class functionality."""
    log_action("checking_class_functionality", {})
    
    try:
        # Test WebSocketHealthValidator
        validator = WebSocketHealthValidator(timeout=1.0, max_retries=2)
        assert validator.endpoints == [
            '/ws/emoji-rain',
            '/ws/observatory',
            '/ws/anomalies',
            '/ws/doctor-status'
        ]
        assert validator.timeout == 1.0
        assert validator.max_retries == 2
        
        # Test EndpointMonitor
        monitor = EndpointMonitor()
        assert monitor.health_validator is not None
        assert monitor._monitoring_active is False
        
        # Test QualityMetricsCollector
        collector = QualityMetricsCollector()
        assert collector.max_history_size == 10000
        assert collector._quality_thresholds is not None
        
        # Test FailureDetector
        detector = FailureDetector()
        assert len(detector._failure_rules) > 0
        
        log_action("class_functionality_verified", {"classes_tested": 4})
        return True
        
    except Exception as e:
        log_action("class_functionality_failed", {"error": str(e)})
        return False

def verify_json_logging():
    """Verify JSON logging functionality."""
    log_action("checking_json_logging", {})
    
    try:
        # Test health validator logging
        validator = WebSocketHealthValidator()
        validator._log_action("test_action", {"test": "data"})
        
        # Test endpoint monitor logging
        monitor = EndpointMonitor()
        monitor._log_action("test_action", {"test": "data"})
        
        # Test quality metrics logging
        collector = QualityMetricsCollector()
        collector._log_action("test_action", {"test": "data"})
        
        # Test failure detector logging
        detector = FailureDetector()
        detector._log_action("test_action", {"test": "data"})
        
        log_action("json_logging_verified", {"components_tested": 4})
        return True
        
    except Exception as e:
        log_action("json_logging_failed", {"error": str(e)})
        return False

def main():
    """Run all verification checks."""
    log_action("verification_started", {"checks": 5})
    
    checks = [
        ("files_exist", verify_files_exist),
        ("file_sizes", verify_file_sizes),
        ("imports", verify_imports),
        ("class_functionality", verify_class_functionality),
        ("json_logging", verify_json_logging)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            log_action(f"{check_name}_error", {"error": str(e)})
            results.append((check_name, False))
    
    # Calculate summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    log_action("verification_completed", {
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": total - passed,
        "success_rate": f"{(passed/total)*100:.1f}%"
    })
    
    if passed == total:
        log_action("verification_successful", {
            "status": "completed",
            "summary": "Endpoint health validation implemented successfully"
        })
        return 0
    else:
        log_action("verification_failed", {
            "status": "error",
            "summary": "Some verification checks failed"
        })
        return 1

if __name__ == "__main__":
    sys.exit(main())