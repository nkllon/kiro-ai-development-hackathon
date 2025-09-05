"""
Unit tests for HealthAlert constructor parameters and validation
Tests for task 5.2: Fix health alert constructor parameters
"""

import pytest
from datetime import datetime
from src.beast_mode.core.health_monitoring import HealthAlert, AlertSeverity


class TestHealthAlertConstructor:
    """Test HealthAlert constructor with required parameters"""
    
    def test_health_alert_creation_with_required_parameters(self):
        """Test that HealthAlert can be created with all required parameters"""
        alert = HealthAlert(
            module_name="test_module",
            severity=AlertSeverity.WARNING,
            message="Test alert message",
            timestamp=datetime.now(),
            metric_value=0.3,
            threshold_value=0.5
        )
        
        assert alert.module_name == "test_module"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "Test alert message"
        assert isinstance(alert.timestamp, datetime)
        assert alert.metric_value == 0.3
        assert alert.threshold_value == 0.5
        assert alert.resolved is False
        assert alert.resolution_time is None
    
    def test_health_alert_creation_with_optional_parameters(self):
        """Test that HealthAlert can be created with optional parameters"""
        resolution_time = datetime.now()
        alert = HealthAlert(
            module_name="test_module",
            severity=AlertSeverity.CRITICAL,
            message="Critical alert",
            timestamp=datetime.now(),
            metric_value=0.1,
            threshold_value=0.8,
            resolved=True,
            resolution_time=resolution_time
        )
        
        assert alert.resolved is True
        assert alert.resolution_time == resolution_time
    
    def test_health_alert_missing_metric_value_raises_error(self):
        """Test that missing metric_value raises TypeError"""
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'metric_value'"):
            HealthAlert(
                module_name="test_module",
                severity=AlertSeverity.WARNING,
                message="Test message",
                timestamp=datetime.now(),
                threshold_value=0.5
            )
    
    def test_health_alert_missing_threshold_value_raises_error(self):
        """Test that missing threshold_value raises TypeError"""
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'threshold_value'"):
            HealthAlert(
                module_name="test_module",
                severity=AlertSeverity.WARNING,
                message="Test message",
                timestamp=datetime.now(),
                metric_value=0.3
            )
    
    def test_health_alert_validation_invalid_metric_value_type(self):
        """Test that invalid metric_value type raises ValueError"""
        with pytest.raises(ValueError, match="metric_value must be a number"):
            HealthAlert(
                module_name="test_module",
                severity=AlertSeverity.WARNING,
                message="Test message",
                timestamp=datetime.now(),
                metric_value="invalid",
                threshold_value=0.5
            )
    
    def test_health_alert_validation_invalid_threshold_value_type(self):
        """Test that invalid threshold_value type raises ValueError"""
        with pytest.raises(ValueError, match="threshold_value must be a number"):
            HealthAlert(
                module_name="test_module",
                severity=AlertSeverity.WARNING,
                message="Test message",
                timestamp=datetime.now(),
                metric_value=0.3,
                threshold_value="invalid"
            )
    
    def test_health_alert_validation_negative_metric_value(self):
        """Test that negative metric_value raises ValueError"""
        with pytest.raises(ValueError, match="metric_value must be non-negative"):
            HealthAlert(
                module_name="test_module",
                severity=AlertSeverity.WARNING,
                message="Test message",
                timestamp=datetime.now(),
                metric_value=-0.1,
                threshold_value=0.5
            )
    
    def test_health_alert_validation_negative_threshold_value(self):
        """Test that negative threshold_value raises ValueError"""
        with pytest.raises(ValueError, match="threshold_value must be non-negative"):
            HealthAlert(
                module_name="test_module",
                severity=AlertSeverity.WARNING,
                message="Test message",
                timestamp=datetime.now(),
                metric_value=0.3,
                threshold_value=-0.5
            )
    
    def test_health_alert_validation_accepts_zero_values(self):
        """Test that zero values are accepted for metric and threshold"""
        alert = HealthAlert(
            module_name="test_module",
            severity=AlertSeverity.INFO,
            message="Test message",
            timestamp=datetime.now(),
            metric_value=0.0,
            threshold_value=0.0
        )
        
        assert alert.metric_value == 0.0
        assert alert.threshold_value == 0.0
    
    def test_health_alert_validation_accepts_integer_values(self):
        """Test that integer values are accepted for metric and threshold"""
        alert = HealthAlert(
            module_name="test_module",
            severity=AlertSeverity.INFO,
            message="Test message",
            timestamp=datetime.now(),
            metric_value=1,
            threshold_value=2
        )
        
        assert alert.metric_value == 1
        assert alert.threshold_value == 2
    
    def test_health_alert_validation_accepts_float_values(self):
        """Test that float values are accepted for metric and threshold"""
        alert = HealthAlert(
            module_name="test_module",
            severity=AlertSeverity.INFO,
            message="Test message",
            timestamp=datetime.now(),
            metric_value=0.75,
            threshold_value=0.85
        )
        
        assert alert.metric_value == 0.75
        assert alert.threshold_value == 0.85


class TestHealthAlertIntegration:
    """Test HealthAlert integration with health monitoring system"""
    
    def test_health_alert_in_monitoring_context(self):
        """Test that HealthAlert works correctly in monitoring context"""
        # This simulates the usage in the health monitoring system
        component_name = "test_component"
        error_message = "Component health check failed"
        health_score = 0.2
        health_threshold = 0.5
        
        alert = HealthAlert(
            module_name=component_name,
            severity=AlertSeverity.CRITICAL,
            message=f"Component degraded: {error_message}. Graceful degradation applied.",
            timestamp=datetime.now(),
            metric_value=health_score,
            threshold_value=health_threshold
        )
        
        assert alert.module_name == component_name
        assert alert.severity == AlertSeverity.CRITICAL
        assert "Component degraded" in alert.message
        assert alert.metric_value == health_score
        assert alert.threshold_value == health_threshold
        assert alert.metric_value < alert.threshold_value  # Health is below threshold
    
    def test_health_alert_severity_levels(self):
        """Test HealthAlert with different severity levels"""
        severities = [
            AlertSeverity.INFO,
            AlertSeverity.WARNING,
            AlertSeverity.CRITICAL,
            AlertSeverity.EMERGENCY
        ]
        
        for severity in severities:
            alert = HealthAlert(
                module_name="test_module",
                severity=severity,
                message=f"Test {severity.value} alert",
                timestamp=datetime.now(),
                metric_value=0.4,
                threshold_value=0.6
            )
            
            assert alert.severity == severity
            assert severity.value in alert.message