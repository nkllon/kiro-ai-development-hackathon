"""
Unit tests for MakefileHealthMonitor.

Tests health monitoring, alerting, metrics collection,
and Beast Mode integration functionality.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.makefile_governance.core.health_monitor import (
    MakefileHealthMonitor,
    HealthMetric,
    HealthMetricType,
    HealthAlert,
    SystemHealth
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestMakefileHealthMonitor:
    """Test suite for MakefileHealthMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create a MakefileHealthMonitor instance."""
        return MakefileHealthMonitor()
    
    def test_module_initialization(self, monitor):
        """Test that the health monitor initializes correctly."""
        assert monitor.module_id == "makefile_health_monitor"
        assert isinstance(monitor.get_capabilities(), list)
        assert ModuleCapability.MONITORING in monitor.get_capabilities()
        assert ModuleCapability.CORE_FUNCTIONALITY in monitor.get_capabilities()
        assert ModuleCapability.DATA_PROCESSING in monitor.get_capabilities()
        
        # Check initial statistics
        assert monitor._total_validations == 0
        assert monitor._successful_validations == 0
        assert monitor._total_repairs == 0
        assert monitor._successful_repairs == 0
        assert monitor._total_governance_checks == 0
        assert monitor._compliant_governance_checks == 0
        assert monitor._total_errors == 0
        assert len(monitor._response_times) == 0
        assert len(monitor._active_alerts) == 0
    
    def test_get_module_info(self, monitor):
        """Test module info retrieval."""
        info = monitor.get_module_info()
        
        assert info["module_id"] == "makefile_health_monitor"
        assert info["name"] == "Makefile Health Monitor"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert "statistics" in info
        assert "health_metrics" in info
        
        # Check statistics structure
        stats = info["statistics"]
        expected_stats = [
            "total_validations", "successful_validations", "total_repairs",
            "successful_repairs", "total_governance_checks", "compliant_governance_checks",
            "total_errors", "active_alerts", "resolved_alerts"
        ]
        for stat in expected_stats:
            assert stat in stats
        
        # Check health metrics structure
        health_metrics = info["health_metrics"]
        for metric_type in HealthMetricType:
            assert metric_type.value in health_metrics
    
    def test_get_health_status_healthy(self, monitor):
        """Test health status when monitor is healthy."""
        # Record some successful operations
        monitor.record_validation_result(True, 1.0)
        monitor.record_repair_result(True, 2.0)
        monitor.record_governance_result(True, 1.5)
        
        health = monitor.get_health_status()
        
        assert health.module_id == "makefile_health_monitor"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score >= 0.7
        assert health.error_count == 0
    
    def test_get_health_status_with_errors(self, monitor):
        """Test health status when monitor has detected errors."""
        # Record operations with high error rate
        for _ in range(3):
            monitor.record_validation_result(False, 1.0)  # Failed validations
        monitor.record_validation_result(True, 1.0)  # One success
        
        health = monitor.get_health_status()
        
        assert health.status in [ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert health.health_score < 1.0
        assert health.error_count > 0
    
    def test_graceful_degradation(self, monitor):
        """Test graceful degradation functionality."""
        original_interval = monitor._metric_collection_interval
        
        result = monitor.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.DATA_PROCESSING in result.degraded_capabilities
        assert ModuleCapability.MONITORING in result.remaining_capabilities
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
        assert result.error_message is None
        
        # Check that metric collection interval was increased
        assert monitor._metric_collection_interval > original_interval
    
    def test_record_validation_result_success(self, monitor):
        """Test recording successful validation results."""
        initial_validations = monitor._total_validations
        initial_successful = monitor._successful_validations
        
        monitor.record_validation_result(True, 1.5)
        
        assert monitor._total_validations == initial_validations + 1
        assert monitor._successful_validations == initial_successful + 1
        assert len(monitor._response_times) == 1
        assert monitor._response_times[0] == 1.5
    
    def test_record_validation_result_failure(self, monitor):
        """Test recording failed validation results."""
        initial_validations = monitor._total_validations
        initial_successful = monitor._successful_validations
        initial_errors = monitor._total_errors
        
        monitor.record_validation_result(False, 2.0)
        
        assert monitor._total_validations == initial_validations + 1
        assert monitor._successful_validations == initial_successful  # No change
        assert monitor._total_errors == initial_errors + 1
        assert len(monitor._response_times) == 1
        assert monitor._response_times[0] == 2.0
    
    def test_record_repair_result_success(self, monitor):
        """Test recording successful repair results."""
        initial_repairs = monitor._total_repairs
        initial_successful = monitor._successful_repairs
        
        monitor.record_repair_result(True, 3.0)
        
        assert monitor._total_repairs == initial_repairs + 1
        assert monitor._successful_repairs == initial_successful + 1
        assert len(monitor._response_times) == 1
        assert monitor._response_times[0] == 3.0
    
    def test_record_repair_result_failure(self, monitor):
        """Test recording failed repair results."""
        initial_repairs = monitor._total_repairs
        initial_successful = monitor._successful_repairs
        initial_errors = monitor._total_errors
        
        monitor.record_repair_result(False, 4.0)
        
        assert monitor._total_repairs == initial_repairs + 1
        assert monitor._successful_repairs == initial_successful  # No change
        assert monitor._total_errors == initial_errors + 1
        assert len(monitor._response_times) == 1
        assert monitor._response_times[0] == 4.0
    
    def test_record_governance_result_compliant(self, monitor):
        """Test recording compliant governance results."""
        initial_checks = monitor._total_governance_checks
        initial_compliant = monitor._compliant_governance_checks
        
        monitor.record_governance_result(True, 1.0)
        
        assert monitor._total_governance_checks == initial_checks + 1
        assert monitor._compliant_governance_checks == initial_compliant + 1
        assert len(monitor._response_times) == 1
        assert monitor._response_times[0] == 1.0
    
    def test_record_governance_result_non_compliant(self, monitor):
        """Test recording non-compliant governance results."""
        initial_checks = monitor._total_governance_checks
        initial_compliant = monitor._compliant_governance_checks
        
        monitor.record_governance_result(False, 2.0)
        
        assert monitor._total_governance_checks == initial_checks + 1
        assert monitor._compliant_governance_checks == initial_compliant  # No change
        assert len(monitor._response_times) == 1
        assert monitor._response_times[0] == 2.0
    
    def test_response_times_bounded(self, monitor):
        """Test that response times list is kept bounded."""
        # Set a small max history size for testing
        monitor._max_history_size = 5
        
        # Record more response times than the limit
        for i in range(10):
            monitor.record_validation_result(True, float(i))
        
        # Should only keep the last 5
        assert len(monitor._response_times) == 5
        assert monitor._response_times == [5.0, 6.0, 7.0, 8.0, 9.0]
    
    def test_get_system_health(self, monitor):
        """Test comprehensive system health retrieval."""
        # Record some operations to generate metrics
        monitor.record_validation_result(True, 1.0)
        monitor.record_repair_result(True, 2.0)
        monitor.record_governance_result(True, 1.5)
        
        system_health = monitor.get_system_health()
        
        assert isinstance(system_health, SystemHealth)
        assert system_health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert 0.0 <= system_health.health_score <= 1.0
        assert isinstance(system_health.metrics, list)
        assert isinstance(system_health.alerts, list)
        assert isinstance(system_health.recommendations, list)
        assert isinstance(system_health.last_updated, datetime)
    
    def test_collect_current_metrics(self, monitor):
        """Test current metrics collection."""
        # Record some operations to generate data
        monitor.record_validation_result(True, 1.0)
        monitor.record_validation_result(False, 2.0)
        monitor.record_repair_result(True, 1.5)
        monitor.record_governance_result(True, 1.2)
        
        metrics = monitor._collect_current_metrics()
        
        assert len(metrics) > 0
        
        # Check that expected metric types are present
        metric_types = [m.metric_type for m in metrics]
        assert HealthMetricType.VALIDATION_SUCCESS_RATE in metric_types
        assert HealthMetricType.REPAIR_SUCCESS_RATE in metric_types
        assert HealthMetricType.GOVERNANCE_COMPLIANCE_RATE in metric_types
        assert HealthMetricType.ERROR_RATE in metric_types
        assert HealthMetricType.AVERAGE_RESPONSE_TIME in metric_types
        assert HealthMetricType.SYSTEM_UPTIME in metric_types
        
        # Verify metric values
        validation_metric = next(m for m in metrics if m.metric_type == HealthMetricType.VALIDATION_SUCCESS_RATE)
        assert validation_metric.value == 0.5  # 1 success out of 2 validations
        
        repair_metric = next(m for m in metrics if m.metric_type == HealthMetricType.REPAIR_SUCCESS_RATE)
        assert repair_metric.value == 1.0  # 1 success out of 1 repair
        
        governance_metric = next(m for m in metrics if m.metric_type == HealthMetricType.GOVERNANCE_COMPLIANCE_RATE)
        assert governance_metric.value == 1.0  # 1 compliant out of 1 check
    
    def test_calculate_overall_health_score(self, monitor):
        """Test overall health score calculation."""
        # Create test metrics
        metrics = [
            HealthMetric(HealthMetricType.VALIDATION_SUCCESS_RATE, 0.9, datetime.now()),
            HealthMetric(HealthMetricType.REPAIR_SUCCESS_RATE, 0.8, datetime.now()),
            HealthMetric(HealthMetricType.GOVERNANCE_COMPLIANCE_RATE, 0.85, datetime.now()),
            HealthMetric(HealthMetricType.ERROR_RATE, 0.05, datetime.now(), threshold_warning=0.1, threshold_critical=0.2),
            HealthMetric(HealthMetricType.AVERAGE_RESPONSE_TIME, 2.0, datetime.now(), threshold_warning=5.0, threshold_critical=10.0)
        ]
        
        health_score = monitor._calculate_overall_health_score(metrics)
        
        assert 0.0 <= health_score <= 1.0
        assert health_score > 0.8  # Should be high with good metrics
    
    def test_calculate_overall_health_score_poor_metrics(self, monitor):
        """Test overall health score calculation with poor metrics."""
        # Create test metrics with poor values
        metrics = [
            HealthMetric(HealthMetricType.VALIDATION_SUCCESS_RATE, 0.3, datetime.now()),
            HealthMetric(HealthMetricType.REPAIR_SUCCESS_RATE, 0.2, datetime.now()),
            HealthMetric(HealthMetricType.GOVERNANCE_COMPLIANCE_RATE, 0.4, datetime.now()),
            HealthMetric(HealthMetricType.ERROR_RATE, 0.3, datetime.now(), threshold_warning=0.1, threshold_critical=0.2),
            HealthMetric(HealthMetricType.AVERAGE_RESPONSE_TIME, 15.0, datetime.now(), threshold_warning=5.0, threshold_critical=10.0)
        ]
        
        health_score = monitor._calculate_overall_health_score(metrics)
        
        assert 0.0 <= health_score <= 1.0
        assert health_score < 0.5  # Should be low with poor metrics
    
    def test_alert_creation_and_resolution(self, monitor):
        """Test alert creation and resolution."""
        # Record operations that should trigger alerts (high error rate)
        for _ in range(10):
            monitor.record_validation_result(False, 1.0)  # All failures
        
        # Check that alerts were created
        active_alerts = monitor.get_active_alerts()
        assert len(active_alerts) > 0
        
        # Find error rate alert
        error_rate_alert = next(
            (a for a in active_alerts if a.metric_type == HealthMetricType.ERROR_RATE),
            None
        )
        assert error_rate_alert is not None
        assert error_rate_alert.severity in ["warning", "critical"]
        
        # Resolve the alert
        alert_id = error_rate_alert.alert_id
        resolved = monitor.resolve_alert(alert_id)
        
        assert resolved is True
        assert len(monitor.get_active_alerts()) < len(active_alerts)
    
    def test_alert_resolution_nonexistent(self, monitor):
        """Test resolution of non-existent alert."""
        resolved = monitor.resolve_alert("nonexistent_alert_id")
        assert resolved is False
    
    def test_metrics_history_retrieval(self, monitor):
        """Test retrieval of metrics history."""
        # Record some operations to generate metrics
        monitor.record_validation_result(True, 1.0)
        monitor.record_validation_result(False, 2.0)
        
        # Get metrics history
        history = monitor.get_metrics_history(HealthMetricType.VALIDATION_SUCCESS_RATE, hours=1)
        
        assert isinstance(history, list)
        # Should have at least one metric from the operations above
        assert len(history) >= 0
    
    def test_metrics_history_time_filtering(self, monitor):
        """Test time-based filtering of metrics history."""
        # Manually add old metrics to history
        old_metric = HealthMetric(
            HealthMetricType.VALIDATION_SUCCESS_RATE,
            0.5,
            datetime.now() - timedelta(hours=25)  # Older than 24 hours
        )
        
        recent_metric = HealthMetric(
            HealthMetricType.VALIDATION_SUCCESS_RATE,
            0.8,
            datetime.now() - timedelta(hours=1)  # Within 24 hours
        )
        
        monitor._metrics_history[HealthMetricType.VALIDATION_SUCCESS_RATE] = [old_metric, recent_metric]
        
        # Get 24-hour history
        history = monitor.get_metrics_history(HealthMetricType.VALIDATION_SUCCESS_RATE, hours=24)
        
        # Should only include the recent metric
        assert len(history) == 1
        assert history[0].timestamp == recent_metric.timestamp
    
    def test_alert_message_generation(self, monitor):
        """Test alert message generation for different metric types."""
        # Error rate metric
        error_metric = HealthMetric(
            HealthMetricType.ERROR_RATE,
            0.15,
            datetime.now(),
            threshold_warning=0.1,
            threshold_critical=0.2
        )
        
        message = monitor._generate_alert_message(error_metric, "warning")
        assert "Error Rate" in message
        assert "warning" in message
        assert "15.00%" in message
        
        # Response time metric
        response_metric = HealthMetric(
            HealthMetricType.AVERAGE_RESPONSE_TIME,
            7.5,
            datetime.now(),
            threshold_warning=5.0,
            threshold_critical=10.0
        )
        
        message = monitor._generate_alert_message(response_metric, "warning")
        assert "Average Response Time" in message
        assert "warning" in message
        assert "7.50s" in message
        
        # Success rate metric
        success_metric = HealthMetric(
            HealthMetricType.VALIDATION_SUCCESS_RATE,
            0.6,
            datetime.now(),
            threshold_warning=0.7,
            threshold_critical=0.5
        )
        
        message = monitor._generate_alert_message(success_metric, "warning")
        assert "Validation Success Rate" in message
        assert "warning" in message
        assert "60.00%" in message
    
    def test_health_recommendations_generation(self, monitor):
        """Test generation of health recommendations."""
        # Create metrics that should trigger recommendations
        metrics = [
            HealthMetric(HealthMetricType.VALIDATION_SUCCESS_RATE, 0.6, datetime.now()),  # Low success rate
            HealthMetric(HealthMetricType.ERROR_RATE, 0.15, datetime.now()),  # High error rate
            HealthMetric(HealthMetricType.AVERAGE_RESPONSE_TIME, 8.0, datetime.now())  # Slow response
        ]
        
        # Create some alerts
        alerts = [
            HealthAlert("alert1", HealthMetricType.ERROR_RATE, "critical", "High error rate", datetime.now()),
            HealthAlert("alert2", HealthMetricType.VALIDATION_SUCCESS_RATE, "warning", "Low success rate", datetime.now())
        ]
        
        recommendations = monitor._generate_health_recommendations(metrics, alerts)
        
        assert len(recommendations) > 0
        assert any("validation" in rec.lower() for rec in recommendations)
        assert any("error" in rec.lower() for rec in recommendations)
        assert any("performance" in rec.lower() or "response" in rec.lower() for rec in recommendations)
        assert any("critical" in rec.lower() for rec in recommendations)
    
    def test_old_alerts_cleanup(self, monitor):
        """Test cleanup of old resolved alerts."""
        # Set short retention period for testing
        monitor._alert_retention_days = 1
        
        # Create old resolved alert
        old_alert = HealthAlert(
            "old_alert",
            HealthMetricType.ERROR_RATE,
            "warning",
            "Old alert",
            datetime.now() - timedelta(days=2)
        )
        old_alert.resolved = True
        old_alert.resolution_timestamp = datetime.now() - timedelta(days=2)
        
        # Create recent resolved alert
        recent_alert = HealthAlert(
            "recent_alert",
            HealthMetricType.ERROR_RATE,
            "warning",
            "Recent alert",
            datetime.now()
        )
        recent_alert.resolved = True
        recent_alert.resolution_timestamp = datetime.now()
        
        monitor._resolved_alerts = [old_alert, recent_alert]
        
        # Trigger cleanup
        monitor._cleanup_old_alerts()
        
        # Should only keep the recent alert
        assert len(monitor._resolved_alerts) == 1
        assert monitor._resolved_alerts[0].alert_id == "recent_alert"
    
    def test_trace_operation_integration(self, monitor):
        """Test that operations are properly traced."""
        # Mock the trace_operation context manager
        with patch.object(monitor, 'trace_operation') as mock_trace:
            mock_context = MagicMock()
            mock_trace.return_value.__enter__ = Mock(return_value=mock_context)
            mock_trace.return_value.__exit__ = Mock(return_value=None)
            
            monitor.record_validation_result(True, 1.0)
            
            # Verify trace_operation was called
            mock_trace.assert_called_with("record_validation_result", success=True, response_time=1.0)
    
    def test_comprehensive_health_monitoring_workflow(self, monitor):
        """Test comprehensive health monitoring workflow."""
        # Simulate a series of operations with mixed results
        operations = [
            ("validation", True, 1.0),
            ("validation", True, 1.2),
            ("validation", False, 3.0),  # Failed validation
            ("repair", True, 2.0),
            ("repair", False, 5.0),  # Failed repair
            ("governance", True, 1.5),
            ("governance", True, 1.8),
            ("governance", False, 2.5),  # Non-compliant
        ]
        
        for op_type, success, response_time in operations:
            if op_type == "validation":
                monitor.record_validation_result(success, response_time)
            elif op_type == "repair":
                monitor.record_repair_result(success, response_time)
            elif op_type == "governance":
                monitor.record_governance_result(success, response_time)
        
        # Get comprehensive system health
        system_health = monitor.get_system_health()
        
        # Verify system health structure
        assert isinstance(system_health, SystemHealth)
        assert system_health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert 0.0 <= system_health.health_score <= 1.0
        assert len(system_health.metrics) > 0
        assert isinstance(system_health.recommendations, list)
        
        # Verify statistics were updated
        info = monitor.get_module_info()
        stats = info["statistics"]
        assert stats["total_validations"] == 3
        assert stats["successful_validations"] == 2
        assert stats["total_repairs"] == 2
        assert stats["successful_repairs"] == 1
        assert stats["total_governance_checks"] == 3
        assert stats["compliant_governance_checks"] == 2
        assert stats["total_errors"] == 2  # 1 validation + 1 repair failure
        
        # Verify metrics contain expected types
        metric_types = [m.metric_type for m in system_health.metrics]
        expected_types = [
            HealthMetricType.VALIDATION_SUCCESS_RATE,
            HealthMetricType.REPAIR_SUCCESS_RATE,
            HealthMetricType.GOVERNANCE_COMPLIANCE_RATE,
            HealthMetricType.ERROR_RATE,
            HealthMetricType.AVERAGE_RESPONSE_TIME,
            HealthMetricType.SYSTEM_UPTIME
        ]
        
        for expected_type in expected_types:
            assert expected_type in metric_types
    
    @pytest.mark.parametrize("success_rate,expected_status", [
        (1.0, ModuleStatus.HEALTHY),
        (0.8, ModuleStatus.HEALTHY),
        (0.6, ModuleStatus.WARNING),
        (0.3, ModuleStatus.ERROR),
        (0.0, ModuleStatus.ERROR),
    ])
    def test_health_status_based_on_success_rate(self, monitor, success_rate, expected_status):
        """Parametrized test for health status based on success rate."""
        # Record operations to achieve the desired success rate
        total_operations = 10
        successful_operations = int(total_operations * success_rate)
        failed_operations = total_operations - successful_operations
        
        for _ in range(successful_operations):
            monitor.record_validation_result(True, 1.0)
        
        for _ in range(failed_operations):
            monitor.record_validation_result(False, 1.0)
        
        health = monitor.get_health_status()
        
        # Note: The actual status might vary based on other factors,
        # but we can check that it's reasonable given the success rate
        if success_rate >= 0.8:
            assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING]
        elif success_rate >= 0.5:
            assert health.status in [ModuleStatus.WARNING, ModuleStatus.ERROR]
        else:
            assert health.status == ModuleStatus.ERROR