"""
Unit tests for Alert Manager

Tests real-time alert management functionality including
alert rules, notification channels, and alert lifecycle management.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.beast_mode.observatory.monitoring.alert_manager import (
    AlertManager, Alert, AlertRule, AlertSeverity, AlertStatus
)


class TestAlertManager:
    """Test cases for AlertManager"""

    @pytest.fixture
    def alert_manager(self):
        """Create an alert manager instance for testing"""
        return AlertManager()

    @pytest.fixture
    def mock_notification_callback(self):
        """Create a mock notification callback"""
        return Mock()

    def test_initialization(self, alert_manager):
        """Test alert manager initialization"""
        assert len(alert_manager._alerts) == 0
        assert len(alert_manager._alert_rules) > 0  # Should have default rules
        assert len(alert_manager._alert_history) == 0
        assert len(alert_manager._suppressed_alerts) == 0
        assert alert_manager._alert_id_counter == 0
        
        # Check default rules exist
        assert "high_error_rate" in alert_manager._alert_rules
        assert "critical_error_rate" in alert_manager._alert_rules
        assert "high_latency" in alert_manager._alert_rules
        assert "critical_latency" in alert_manager._alert_rules
        assert "low_throughput" in alert_manager._alert_rules
        assert "connection_failure" in alert_manager._alert_rules

    def test_add_alert_rule(self, alert_manager):
        """Test adding custom alert rules"""
        def test_condition(metrics):
            return metrics.get('test_metric', 0) > 100
        
        alert_manager.add_alert_rule(
            name="test_rule",
            condition=test_condition,
            severity=AlertSeverity.WARNING,
            message_template="Test alert: {test_metric}",
            cooldown_sec=60,
            max_alerts_per_hour=5,
            enabled=True
        )
        
        assert "test_rule" in alert_manager._alert_rules
        rule = alert_manager._alert_rules["test_rule"]
        assert rule.name == "test_rule"
        assert rule.severity == AlertSeverity.WARNING
        assert rule.cooldown_sec == 60
        assert rule.max_alerts_per_hour == 5
        assert rule.enabled is True

    def test_add_notification_channel(self, alert_manager, mock_notification_callback):
        """Test adding notification channels"""
        alert_manager.add_notification_channel(AlertSeverity.WARNING, mock_notification_callback)
        
        channels = alert_manager._notification_channels[AlertSeverity.WARNING]
        assert mock_notification_callback in channels

    @pytest.mark.asyncio
    async def test_trigger_alert_success(self, alert_manager):
        """Test successful alert triggering"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        severity = AlertSeverity.WARNING
        
        alert = await alert_manager.trigger_alert(endpoint, alert_type, details, severity)
        
        assert alert is not None
        assert alert.endpoint == endpoint
        assert alert.alert_type == alert_type
        assert alert.severity == severity
        assert alert.message == f"{alert_type} alert for {endpoint}"
        assert alert.details == {"issues": details}
        assert alert.status == AlertStatus.ACTIVE
        assert alert.id in alert_manager._alerts

    @pytest.mark.asyncio
    async def test_trigger_alert_with_notification(self, alert_manager, mock_notification_callback):
        """Test alert triggering with notification"""
        alert_manager.add_notification_channel(AlertSeverity.WARNING, mock_notification_callback)
        
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        alert = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        
        # Verify notification was called
        mock_notification_callback.assert_called_once_with(alert)

    @pytest.mark.asyncio
    async def test_trigger_alert_cooldown(self, alert_manager):
        """Test alert cooldown functionality"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        # Trigger first alert
        alert1 = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert1 is not None
        
        # Immediately trigger second alert (should be suppressed due to cooldown)
        alert2 = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert2 is None

    @pytest.mark.asyncio
    async def test_trigger_alert_rate_limiting(self, alert_manager):
        """Test alert rate limiting"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        # Add a rule with low rate limit
        alert_manager.add_alert_rule(
            name="test_alert",
            condition=lambda metrics: True,
            severity=AlertSeverity.WARNING,
            message_template="Test alert",
            max_alerts_per_hour=1
        )
        
        # Trigger first alert
        alert1 = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert1 is not None
        
        # Trigger second alert (should be rate limited)
        alert2 = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert2 is None

    @pytest.mark.asyncio
    async def test_trigger_alert_suppressed(self, alert_manager):
        """Test suppressed alert functionality"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        # Suppress alerts for this endpoint and type
        alert_manager.suppress_alert(endpoint, alert_type, 3600)
        
        # Try to trigger alert (should be suppressed)
        alert = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert is None

    @pytest.mark.asyncio
    async def test_check_metrics_alerts(self, alert_manager):
        """Test checking metrics against alert rules"""
        endpoint = "test_endpoint"
        
        # Test metrics that should trigger high error rate alert
        metrics = {
            'error_rate': 0.15,  # Above 0.1 threshold
            'avg_latency_ms': 100,
            'throughput_msgs_per_sec': 5.0
        }
        
        triggered_alerts = await alert_manager.check_metrics_alerts(endpoint, metrics)
        
        # Should trigger high_error_rate alert
        assert len(triggered_alerts) >= 1
        assert any(alert.alert_type == "high_error_rate" for alert in triggered_alerts)

    @pytest.mark.asyncio
    async def test_check_metrics_alerts_multiple_triggers(self, alert_manager):
        """Test multiple alert triggers from metrics"""
        endpoint = "test_endpoint"
        
        # Test metrics that should trigger multiple alerts
        metrics = {
            'error_rate': 0.3,  # Above critical threshold
            'avg_latency_ms': 3000,  # Above critical threshold
            'throughput_msgs_per_sec': 0.05  # Below low threshold
        }
        
        triggered_alerts = await alert_manager.check_metrics_alerts(endpoint, metrics)
        
        # Should trigger multiple alerts
        assert len(triggered_alerts) >= 3
        alert_types = [alert.alert_type for alert in triggered_alerts]
        assert "critical_error_rate" in alert_types
        assert "critical_latency" in alert_types
        assert "low_throughput" in alert_types

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, alert_manager):
        """Test alert acknowledgment"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        # Trigger alert
        alert = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert is not None
        
        # Acknowledge alert
        acknowledged_by = "admin"
        notes = "Investigating issue"
        success = await alert_manager.acknowledge_alert(alert.id, acknowledged_by, notes)
        
        assert success is True
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == acknowledged_by
        assert alert.resolution_notes == notes
        assert alert.acknowledged_at is not None

    @pytest.mark.asyncio
    async def test_acknowledge_nonexistent_alert(self, alert_manager):
        """Test acknowledging non-existent alert"""
        success = await alert_manager.acknowledge_alert("nonexistent_id", "admin")
        assert success is False

    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_manager):
        """Test alert resolution"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        # Trigger alert
        alert = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert is not None
        
        # Resolve alert
        resolution_notes = "Issue fixed"
        success = await alert_manager.resolve_alert(alert.id, resolution_notes)
        
        assert success is True
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolution_notes == resolution_notes
        assert alert.resolved_at is not None

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_alert(self, alert_manager):
        """Test resolving non-existent alert"""
        success = await alert_manager.resolve_alert("nonexistent_id", "Fixed")
        assert success is False

    def test_suppress_alert(self, alert_manager):
        """Test alert suppression"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        duration_sec = 1800  # 30 minutes
        
        alert_manager.suppress_alert(endpoint, alert_type, duration_sec)
        
        alert_key = f"{endpoint}:{alert_type}"
        assert alert_key in alert_manager._suppressed_alerts

    @pytest.mark.asyncio
    async def test_remove_suppression_after_delay(self, alert_manager):
        """Test automatic suppression removal after delay"""
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        duration_sec = 0.1  # Very short delay for testing
        
        alert_manager.suppress_alert(endpoint, alert_type, duration_sec)
        
        alert_key = f"{endpoint}:{alert_type}"
        assert alert_key in alert_manager._suppressed_alerts
        
        # Wait for suppression to be removed
        await asyncio.sleep(0.2)
        
        assert alert_key not in alert_manager._suppressed_alerts

    def test_get_active_alerts(self, alert_manager):
        """Test getting active alerts"""
        # Initially no active alerts
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 0
        
        # Add some alerts with different statuses
        alert1 = Alert(
            id="alert1",
            endpoint="endpoint1",
            alert_type="type1",
            severity=AlertSeverity.WARNING,
            message="Test message 1",
            details={},
            created_at=datetime.now(),
            status=AlertStatus.ACTIVE
        )
        
        alert2 = Alert(
            id="alert2",
            endpoint="endpoint2",
            alert_type="type2",
            severity=AlertSeverity.CRITICAL,
            message="Test message 2",
            details={},
            created_at=datetime.now(),
            status=AlertStatus.ACKNOWLEDGED
        )
        
        alert_manager._alerts["alert1"] = alert1
        alert_manager._alerts["alert2"] = alert2
        
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].id == "alert1"

    def test_get_alerts_by_endpoint(self, alert_manager):
        """Test getting alerts by endpoint"""
        endpoint = "test_endpoint"
        
        # Add alerts for different endpoints
        alert1 = Alert(
            id="alert1",
            endpoint=endpoint,
            alert_type="type1",
            severity=AlertSeverity.WARNING,
            message="Test message 1",
            details={},
            created_at=datetime.now()
        )
        
        alert2 = Alert(
            id="alert2",
            endpoint="other_endpoint",
            alert_type="type2",
            severity=AlertSeverity.CRITICAL,
            message="Test message 2",
            details={},
            created_at=datetime.now()
        )
        
        alert_manager._alerts["alert1"] = alert1
        alert_manager._alerts["alert2"] = alert2
        
        endpoint_alerts = alert_manager.get_alerts_by_endpoint(endpoint)
        assert len(endpoint_alerts) == 1
        assert endpoint_alerts[0].id == "alert1"

    def test_get_alerts_by_severity(self, alert_manager):
        """Test getting alerts by severity"""
        # Add alerts with different severities
        alert1 = Alert(
            id="alert1",
            endpoint="endpoint1",
            alert_type="type1",
            severity=AlertSeverity.WARNING,
            message="Test message 1",
            details={},
            created_at=datetime.now()
        )
        
        alert2 = Alert(
            id="alert2",
            endpoint="endpoint2",
            alert_type="type2",
            severity=AlertSeverity.CRITICAL,
            message="Test message 2",
            details={},
            created_at=datetime.now()
        )
        
        alert_manager._alerts["alert1"] = alert1
        alert_manager._alerts["alert2"] = alert2
        
        warning_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.WARNING)
        assert len(warning_alerts) == 1
        assert warning_alerts[0].id == "alert1"
        
        critical_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].id == "alert2"

    def test_get_alert_summary(self, alert_manager):
        """Test getting alert summary"""
        # Add alerts with different statuses
        alert1 = Alert(
            id="alert1",
            endpoint="endpoint1",
            alert_type="type1",
            severity=AlertSeverity.WARNING,
            message="Test message 1",
            details={},
            created_at=datetime.now(),
            status=AlertStatus.ACTIVE
        )
        
        alert2 = Alert(
            id="alert2",
            endpoint="endpoint2",
            alert_type="type2",
            severity=AlertSeverity.CRITICAL,
            message="Test message 2",
            details={},
            created_at=datetime.now(),
            status=AlertStatus.ACKNOWLEDGED
        )
        
        alert3 = Alert(
            id="alert3",
            endpoint="endpoint3",
            alert_type="type3",
            severity=AlertSeverity.INFO,
            message="Test message 3",
            details={},
            created_at=datetime.now(),
            status=AlertStatus.RESOLVED
        )
        
        alert_manager._alerts["alert1"] = alert1
        alert_manager._alerts["alert2"] = alert2
        alert_manager._alerts["alert3"] = alert3
        
        summary = alert_manager.get_alert_summary()
        
        assert summary['total_alerts'] == 3
        assert summary['active_alerts'] == 1
        assert summary['acknowledged_alerts'] == 1
        assert summary['resolved_alerts'] == 1
        assert summary['severity_breakdown']['warning'] == 1
        assert summary['severity_breakdown']['critical'] == 1
        assert summary['severity_breakdown']['info'] == 1
        assert summary['suppressed_alerts'] == 0
        assert summary['alert_rules'] > 0

    @pytest.mark.asyncio
    async def test_send_notifications_error_handling(self, alert_manager):
        """Test notification error handling"""
        def failing_callback(alert):
            raise Exception("Notification failed")
        
        alert_manager.add_notification_channel(AlertSeverity.WARNING, failing_callback)
        
        endpoint = "test_endpoint"
        alert_type = "test_alert"
        details = ["Test issue detected"]
        
        # Should not raise exception despite notification failure
        alert = await alert_manager.trigger_alert(endpoint, alert_type, details, AlertSeverity.WARNING)
        assert alert is not None

    def test_log_action(self, alert_manager, capsys):
        """Test JSON logging functionality"""
        alert_manager._log_action("test_action", {"key": "value"})
        
        captured = capsys.readouterr()
        log_output = captured.out.strip()
        
        # Should be valid JSON
        import json
        log_data = json.loads(log_output)
        
        assert log_data["task"] == "3.1"
        assert log_data["action"] == "alert_manager_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["key"] == "value"
        assert "timestamp" in log_data


class TestAlert:
    """Test cases for Alert dataclass"""
    
    def test_alert_creation(self):
        """Test Alert creation"""
        alert = Alert(
            id="test_alert",
            endpoint="test_endpoint",
            alert_type="test_type",
            severity=AlertSeverity.WARNING,
            message="Test message",
            details={"key": "value"},
            created_at=datetime.now(),
            status=AlertStatus.ACTIVE,
            acknowledged_at=datetime.now(),
            resolved_at=datetime.now(),
            acknowledged_by="admin",
            resolution_notes="Fixed"
        )
        
        assert alert.id == "test_alert"
        assert alert.endpoint == "test_endpoint"
        assert alert.alert_type == "test_type"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "Test message"
        assert alert.details == {"key": "value"}
        assert alert.status == AlertStatus.ACTIVE
        assert alert.acknowledged_by == "admin"
        assert alert.resolution_notes == "Fixed"

    def test_alert_defaults(self):
        """Test Alert default values"""
        alert = Alert(
            id="test_alert",
            endpoint="test_endpoint",
            alert_type="test_type",
            severity=AlertSeverity.WARNING,
            message="Test message",
            details={},
            created_at=datetime.now()
        )
        
        assert alert.status == AlertStatus.ACTIVE
        assert alert.acknowledged_at is None
        assert alert.resolved_at is None
        assert alert.acknowledged_by is None
        assert alert.resolution_notes is None


class TestAlertRule:
    """Test cases for AlertRule dataclass"""
    
    def test_alert_rule_creation(self):
        """Test AlertRule creation"""
        def test_condition(metrics):
            return True
        
        rule = AlertRule(
            name="test_rule",
            condition=test_condition,
            severity=AlertSeverity.WARNING,
            message_template="Test: {value}",
            cooldown_sec=300,
            max_alerts_per_hour=10,
            enabled=True
        )
        
        assert rule.name == "test_rule"
        assert rule.condition == test_condition
        assert rule.severity == AlertSeverity.WARNING
        assert rule.message_template == "Test: {value}"
        assert rule.cooldown_sec == 300
        assert rule.max_alerts_per_hour == 10
        assert rule.enabled is True

    def test_alert_rule_defaults(self):
        """Test AlertRule default values"""
        def test_condition(metrics):
            return True
        
        rule = AlertRule(
            name="test_rule",
            condition=test_condition,
            severity=AlertSeverity.WARNING,
            message_template="Test: {value}"
        )
        
        assert rule.cooldown_sec == 300
        assert rule.max_alerts_per_hour == 10
        assert rule.enabled is True


class TestAlertSeverity:
    """Test cases for AlertSeverity enum"""
    
    def test_alert_severity_values(self):
        """Test AlertSeverity enum values"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"
        assert AlertSeverity.EMERGENCY.value == "emergency"


class TestAlertStatus:
    """Test cases for AlertStatus enum"""
    
    def test_alert_status_values(self):
        """Test AlertStatus enum values"""
        assert AlertStatus.ACTIVE.value == "active"
        assert AlertStatus.ACKNOWLEDGED.value == "acknowledged"
        assert AlertStatus.RESOLVED.value == "resolved"
        assert AlertStatus.SUPPRESSED.value == "suppressed"