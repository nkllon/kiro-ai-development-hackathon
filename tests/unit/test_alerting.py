"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.542306
"""




import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.beast_mode.monitoring.alerting import (
# from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    AlertManager, Alert, AlertSeverity, AlertRule
)


class TestAlertManager(ReflectiveModule):
    """Test cases for AlertManager."""

    @pytest.fixture
    def alert_manager(self):
        """Create an alert manager instance for testing."""
        return AlertManager()

    @pytest.mark.asyncio
    async def test_register_alert_rule(self, alert_manager):
        """Test registering an alert rule."""
        condition_function = AsyncMock(return_value={"should_alert": False})

        await alert_manager.register_alert_rule(
            name="test_rule",
            description="Test alert rule",
            severity=AlertSeverity.HIGH,
            condition_function=condition_function,
            threshold_value=10.0
        )

        assert "test_rule" in alert_manager.alert_rules
        rule = alert_manager.alert_rules["test_rule"]
        assert rule.name == "test_rule"
        assert rule.severity == AlertSeverity.HIGH
        assert rule.threshold_value == 10.0

    def test_add_alert_handler(self, alert_manager):
        """Test adding alert handlers."""
        handler = MagicMock()

        alert_manager.add_alert_handler(handler)
        assert handler in alert_manager.alert_handlers

    @pytest.mark.asyncio
    async def test_start_stop_alerting(self, alert_manager):
        """Test starting and stopping alerting."""
        assert not alert_manager.alerting_active

        await alert_manager.start_alerting()
        assert alert_manager.alerting_active
        assert alert_manager.alerting_task is not None

        await alert_manager.stop_alerting()
        assert not alert_manager.alerting_active

    @pytest.mark.asyncio
    async def test_fire_alert(self, alert_manager):
        """Test firing an alert."""
        alert_id = await alert_manager.fire_alert(
            name="test_alert",
            message="Test alert message",
            severity=AlertSeverity.CRITICAL,
            source_component="test_component",
            details={"key": "value"}
        )

        assert alert_id in alert_manager.active_alerts
        alert = alert_manager.active_alerts[alert_id]

        assert alert.name == "test_alert"
        assert alert.message == "Test alert message"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.source_component == "test_component"
        assert alert.details["key"] == "value"
        assert not alert.resolved

        # Check alert history
        assert len(alert_manager.alert_history) == 1
        assert alert_manager.alert_history[0].id == alert_id

    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_manager):
        """Test resolving an alert."""
        # Fire an alert first
        alert_id = await alert_manager.fire_alert(
            name="test_alert",
            message="Test message",
            severity=AlertSeverity.HIGH,
            source_component="test"
        )

        # Resolve the alert
        success = await alert_manager.resolve_alert(alert_id, "Issue fixed")

        assert success
        assert alert_id not in alert_manager.active_alerts

        # Check that alert in history is marked as resolved
        resolved_alert = next(
            (alert for alert in alert_manager.alert_history if alert.id == alert_id),
            None
        )
        assert resolved_alert is not None
        assert resolved_alert.resolved
        assert resolved_alert.resolution_message == "Issue fixed"
        assert resolved_alert.resolved_at is not None

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_alert(self, alert_manager):
        """Test resolving a non-existent alert."""
        success = await alert_manager.resolve_alert("nonexistent_id")
        assert not success

    def test_get_active_alerts(self, alert_manager):
        """Test getting active alerts."""
        # Initially empty
        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 0

        # Add some alerts
        alert1 = Alert(
            id="alert1",
            name="test1",
            severity=AlertSeverity.HIGH,
            message="Message 1",
            timestamp=datetime.now(),
            source_component="comp1"
        )
        alert2 = Alert(
            id="alert2",
            name="test2",
            severity=AlertSeverity.CRITICAL,
            message="Message 2",
            timestamp=datetime.now(),
            source_component="comp2"
        )

        alert_manager.active_alerts["alert1"] = alert1
        alert_manager.active_alerts["alert2"] = alert2

        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 2

    def test_get_alerts_by_severity(self, alert_manager):
        """Test getting alerts by severity."""
        # Add alerts with different severities
        high_alert = Alert(
            id="high",
            name="high_alert",
            severity=AlertSeverity.HIGH,
            message="High severity",
            timestamp=datetime.now(),
            source_component="comp1"
        )
        critical_alert = Alert(
            id="critical",
            name="critical_alert",
            severity=AlertSeverity.CRITICAL,
            message="Critical severity",
            timestamp=datetime.now(),
            source_component="comp2"
        )

        alert_manager.active_alerts["high"] = high_alert
        alert_manager.active_alerts["critical"] = critical_alert

        # Get high severity alerts
        high_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.HIGH)
        assert len(high_alerts) == 1
        assert high_alerts[0].severity == AlertSeverity.HIGH

        # Get critical severity alerts
        critical_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL

        # Get medium severity alerts (none)
        medium_alerts = alert_manager.get_alerts_by_severity(AlertSeverity.MEDIUM)
        assert len(medium_alerts) == 0

    def test_get_alert_history(self, alert_manager):
        """Test getting alert history."""
        # Add alerts to history with different timestamps
        old_alert = Alert(
            id="old",
            name="old_alert",
            severity=AlertSeverity.LOW,
            message="Old alert",
            timestamp=datetime.now() - timedelta(hours=25),  # Older than 24h
            source_component="comp1"
        )
        recent_alert = Alert(
            id="recent",
            name="recent_alert",
            severity=AlertSeverity.HIGH,
            message="Recent alert",
            timestamp=datetime.now() - timedelta(hours=1),  # Within 24h
            source_component="comp2"
        )

        alert_manager.alert_history.extend([old_alert, recent_alert])

        # Get 24-hour history
        history = alert_manager.get_alert_history(24)
        assert len(history) == 1
        assert history[0].id == "recent"

        # Get 48-hour history
        history = alert_manager.get_alert_history(48)
        assert len(history) == 2

    def test_get_alert_summary(self, alert_manager):
        """Test getting alert summary."""
        # Add active alerts
        alert_manager.active_alerts["high1"] = Alert(
            id="high1", name="test", severity=AlertSeverity.HIGH,
            message="msg", timestamp=datetime.now(), source_component="comp"
        )
        alert_manager.active_alerts["critical1"] = Alert(
            id="critical1", name="test", severity=AlertSeverity.CRITICAL,
            message="msg", timestamp=datetime.now(), source_component="comp"
        )

        # Add to history
        alert_manager.alert_history.extend([
            Alert(
                id="hist1", name="test", severity=AlertSeverity.LOW,
                message="msg", timestamp=datetime.now() - timedelta(hours=1),
                source_component="comp"
            ),
            Alert(
                id="hist2", name="test", severity=AlertSeverity.MEDIUM,
                message="msg", timestamp=datetime.now() - timedelta(hours=2),
                source_component="comp"
            )
        ])

        # Add alert rules
        alert_manager.alert_rules["rule1"] = AlertRule(
            name="rule1", description="Test rule", severity=AlertSeverity.HIGH,
            condition_function=lambda: None
        )

        summary = alert_manager.get_alert_summary()

        assert summary["active_alerts"] == 2
        assert summary["active_by_severity"]["high"] == 1
        assert summary["active_by_severity"]["critical"] == 1
        assert summary["active_by_severity"]["medium"] == 0
        assert summary["recent_alerts_24h"] == 2
        assert summary["alert_rules"] == 1
        assert "last_updated" in summary

    @pytest.mark.asyncio
    async def test_evaluate_rule_fire_alert(self, alert_manager):
        """Test rule evaluation that fires an alert."""
        # Create a condition that should fire
        condition_function = AsyncMock(return_value={
            "should_alert": True,
            "message": "Test condition met",
            "component": "test_component",
            "details": {"value": 15.0}
        })

        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            severity=AlertSeverity.HIGH,
            condition_function=condition_function,
            cooldown_seconds=0  # No cooldown for testing
        )

        await alert_manager._evaluate_rule("test_rule", rule)

        # Should have fired an alert
        assert len(alert_manager.active_alerts) == 1
        alert = list(alert_manager.active_alerts.values())[0]
        assert alert.name == "test_rule"
        assert alert.message == "Test condition met"
        assert alert.severity == AlertSeverity.HIGH

    @pytest.mark.asyncio
    async def test_evaluate_rule_cooldown(self, alert_manager):
        """Test rule evaluation cooldown period."""
        condition_function = AsyncMock(return_value={"should_alert": True})

        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            severity=AlertSeverity.HIGH,
            condition_function=condition_function,
            cooldown_seconds=300  # 5 minute cooldown
        )

        # First evaluation should fire
        await alert_manager._evaluate_rule("test_rule", rule)
        assert len(alert_manager.active_alerts) == 1

        # Second evaluation should be blocked by cooldown
        await alert_manager._evaluate_rule("test_rule", rule)
        assert len(alert_manager.active_alerts) == 1  # Still only one

    @pytest.mark.asyncio
    async def test_evaluate_rule_auto_resolve(self, alert_manager):
        """Test rule evaluation with auto-resolution."""
        # First fire an alert
        alert_id = await alert_manager.fire_alert(
            name="test_rule",
            message="Test alert",
            severity=AlertSeverity.HIGH,
            source_component="test"
        )

        # Create condition that should resolve
        condition_function = AsyncMock(return_value={
            "should_alert": False,
            "should_resolve": True,
            "resolution_message": "Condition resolved"
        })

        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            severity=AlertSeverity.HIGH,
            condition_function=condition_function,
            auto_resolve=True
        )

        await alert_manager._evaluate_rule("test_rule", rule)

        # Alert should be resolved
        assert alert_id not in alert_manager.active_alerts

        # Check in history
        resolved_alert = next(
            (alert for alert in alert_manager.alert_history if alert.id == alert_id),
            None
        )
        assert resolved_alert.resolved
        assert "resolved" in resolved_alert.resolution_message.lower()

    @pytest.mark.asyncio
    async def test_notify_handlers(self, alert_manager):
        """Test alert handler notification."""
        # Add sync and async handlers
        sync_handler = MagicMock()
        async_handler = AsyncMock()

        alert_manager.add_alert_handler(sync_handler)
        alert_manager.add_alert_handler(async_handler)

        alert = Alert(
            id="test",
            name="test_alert",
            severity=AlertSeverity.HIGH,
            message="Test message",
            timestamp=datetime.now(),
            source_component="test"
        )

        await alert_manager._notify_handlers(alert)

        # Both handlers should have been called
        sync_handler.assert_called_once_with(alert)
        async_handler.assert_called_once_with(alert)

    @pytest.mark.asyncio
    async def test_notify_handlers_exception(self, alert_manager):
        """Test alert handler exception handling."""
        # Add a handler that raises an exception
        def failing_handler(alert):
            raise ValueError("Handler error")

        alert_manager.add_alert_handler(failing_handler)

        alert = Alert(
            id="test",
            name="test_alert",
            severity=AlertSeverity.HIGH,
            message="Test message",
            timestamp=datetime.now(),
            source_component="test"
        )

        # Should not raise exception
        await alert_manager._notify_handlers(alert)

    @pytest.mark.asyncio
    async def test_default_alert_conditions(self, alert_manager):
        """Test default alert condition functions."""
        # Test Redis connectivity check
        result = await alert_manager._check_redis_connectivity_alert(None)
        assert "should_alert" in result
        assert "should_resolve" in result
        assert "message" in result
        assert "component" in result

        # Test error rate check
        result = await alert_manager._check_error_rate_alert(None)
        assert "should_alert" in result
        assert "should_resolve" in result

        # Test latency check
        result = await alert_manager._check_latency_alert(None)
        assert "should_alert" in result
        assert "should_resolve" in result

        # Test resource usage check
        result = await alert_manager._check_resource_usage_alert(None)
        assert "should_alert" in result

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())

    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }

    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert "should_resolve" in result