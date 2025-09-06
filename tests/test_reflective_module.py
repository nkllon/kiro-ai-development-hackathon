"""Tests for ReflectiveModule base class."""

from datetime import datetime

import pytest

from src.multi_instance_orchestration.core.reflective_module import (
    HealthIndicator,
    ModuleStatus,
    ReflectiveModule,
)


class TestReflectiveModule:
    """Test ReflectiveModule base class."""

    def test_health_indicator_creation(self):
        """Test HealthIndicator model creation."""
        indicator = HealthIndicator(
            name="test_indicator",
            status="healthy",
            message="All systems operational",
            timestamp=datetime.now(),
            details={"cpu_usage": 45.2},
        )

        assert indicator.name == "test_indicator"
        assert indicator.status == "healthy"
        assert indicator.message == "All systems operational"
        assert isinstance(indicator.timestamp, datetime)
        assert indicator.details["cpu_usage"] == 45.2

    def test_module_status_creation(self):
        """Test ModuleStatus model creation."""
        indicators = [
            HealthIndicator(
                name="health", status="healthy", message="OK", timestamp=datetime.now()
            )
        ]

        status = ModuleStatus(
            module_name="TestModule",
            version="1.0.0",
            status="active",
            uptime=3600.0,
            last_activity=datetime.now(),
            health_indicators=indicators,
            performance_metrics={"requests_per_second": 100},
        )

        assert status.module_name == "TestModule"
        assert status.version == "1.0.0"
        assert status.status == "active"
        assert status.uptime == 3600.0
        assert len(status.health_indicators) == 1
        assert status.performance_metrics["requests_per_second"] == 100


class ConcreteReflectiveModule(ReflectiveModule):
    """Concrete implementation for testing."""

    def __init__(self, name: str = "TestModule", version: str = "1.0.0"):
        super().__init__(name, version)
        self.is_healthy_flag = True

    def get_module_status(self) -> ModuleStatus:
        return ModuleStatus(
            module_name=self.name,
            version=self.version,
            status="active" if self.is_healthy_flag else "error",
            uptime=self.get_uptime(),
            last_activity=self.last_activity,
            health_indicators=self.get_health_indicators(),
            performance_metrics={"test_metric": 42},
        )

    def is_healthy(self) -> bool:
        return self.is_healthy_flag

    def get_health_indicators(self) -> list:
        return self._health_indicators.copy()

    def set_health_status(self, healthy: bool):
        """Helper method for testing."""
        self.is_healthy_flag = healthy


class TestConcreteReflectiveModule:
    """Test concrete ReflectiveModule implementation."""

    @pytest.fixture
    def module(self):
        """Create test module instance."""
        return ConcreteReflectiveModule()

    def test_module_initialization(self, module):
        """Test module initialization."""
        assert module.name == "TestModule"
        assert module.version == "1.0.0"
        assert isinstance(module.start_time, datetime)
        assert isinstance(module.last_activity, datetime)
        assert module._health_indicators == []

    def test_uptime_calculation(self, module):
        """Test uptime calculation."""
        import time

        time.sleep(0.01)  # Small delay to ensure uptime > 0

        uptime = module.get_uptime()
        assert uptime > 0
        assert isinstance(uptime, float)

    def test_activity_update(self, module):
        """Test activity timestamp update."""
        initial_activity = module.last_activity

        import time

        time.sleep(0.01)

        module.update_activity()
        assert module.last_activity > initial_activity

    def test_health_indicator_creation(self, module):
        """Test health indicator creation."""
        indicator = module.create_health_indicator(
            "test_check",
            "warning",
            "Test warning message",
            {"detail_key": "detail_value"},
        )

        assert indicator.name == "test_check"
        assert indicator.status == "warning"
        assert indicator.message == "Test warning message"
        assert indicator.details["detail_key"] == "detail_value"
        assert isinstance(indicator.timestamp, datetime)

    def test_health_indicator_management(self, module):
        """Test adding and managing health indicators."""
        # Add indicators
        indicator1 = module.create_health_indicator("test1", "healthy", "OK")
        indicator2 = module.create_health_indicator("test2", "warning", "Warning")

        module.add_health_indicator(indicator1)
        module.add_health_indicator(indicator2)

        indicators = module.get_health_indicators()
        assert len(indicators) == 2
        assert indicators[0].name == "test1"
        assert indicators[1].name == "test2"

    def test_health_indicator_limit(self, module):
        """Test health indicator limit (100 max)."""
        # Add more than 100 indicators
        for i in range(150):
            indicator = module.create_health_indicator(
                f"test_{i}", "healthy", f"Message {i}"
            )
            module.add_health_indicator(indicator)

        indicators = module.get_health_indicators()
        assert len(indicators) <= 100

        # Check that latest indicators are kept
        assert indicators[-1].name == "test_149"

    def test_module_status_healthy(self, module):
        """Test module status when healthy."""
        module.set_health_status(True)

        status = module.get_module_status()
        assert status.module_name == "TestModule"
        assert status.version == "1.0.0"
        assert status.status == "active"
        assert status.uptime > 0
        assert isinstance(status.last_activity, datetime)
        assert status.performance_metrics["test_metric"] == 42

    def test_module_status_unhealthy(self, module):
        """Test module status when unhealthy."""
        module.set_health_status(False)

        status = module.get_module_status()
        assert status.status == "error"

    def test_is_healthy_method(self, module):
        """Test is_healthy method."""
        module.set_health_status(True)
        assert module.is_healthy() is True

        module.set_health_status(False)
        assert module.is_healthy() is False

    def test_health_indicators_with_status(self, module):
        """Test health indicators integration with status."""
        # Add some health indicators
        healthy_indicator = module.create_health_indicator(
            "system", "healthy", "System OK"
        )
        warning_indicator = module.create_health_indicator(
            "memory", "warning", "Memory usage high"
        )

        module.add_health_indicator(healthy_indicator)
        module.add_health_indicator(warning_indicator)

        status = module.get_module_status()
        assert len(status.health_indicators) == 2

        # Check that indicators are properly included
        indicator_names = [ind.name for ind in status.health_indicators]
        assert "system" in indicator_names
        assert "memory" in indicator_names

    def test_custom_name_and_version(self):
        """Test custom module name and version."""
        module = ConcreteReflectiveModule("CustomModule", "2.1.0")

        assert module.name == "CustomModule"
        assert module.version == "2.1.0"

        status = module.get_module_status()
        assert status.module_name == "CustomModule"
        assert status.version == "2.1.0"

    def test_health_indicator_details_optional(self, module):
        """Test health indicator creation with optional details."""
        # Without details
        indicator1 = module.create_health_indicator("test1", "healthy", "OK")
        assert indicator1.details == {}

        # With None details
        indicator2 = module.create_health_indicator("test2", "healthy", "OK", None)
        assert indicator2.details == {}

        # With empty dict details
        indicator3 = module.create_health_indicator("test3", "healthy", "OK", {})
        assert indicator3.details == {}

    def test_concurrent_health_indicator_access(self, module):
        """Test concurrent access to health indicators."""
        import threading
        import time

        def add_indicators(thread_id):
            for i in range(10):
                indicator = module.create_health_indicator(
                    f"thread_{thread_id}_indicator_{i}",
                    "healthy",
                    f"Thread {thread_id} indicator {i}",
                )
                module.add_health_indicator(indicator)
                time.sleep(0.001)  # Small delay

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_indicators, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that indicators were added (may be limited to 100)
        indicators = module.get_health_indicators()
        assert len(indicators) <= 100

        # Check that we have indicators from different threads
        thread_ids = set()
        for indicator in indicators:
            if indicator.name.startswith("thread_"):
                thread_id = indicator.name.split("_")[1]
                thread_ids.add(thread_id)

        assert len(thread_ids) > 1  # Should have indicators from multiple threads

    def test_timestamp_accuracy(self, module):
        """Test timestamp accuracy in health indicators."""
        before = datetime.now()
        indicator = module.create_health_indicator("test", "healthy", "OK")
        after = datetime.now()

        assert before <= indicator.timestamp <= after

    def test_health_indicator_status_values(self, module):
        """Test different health indicator status values."""
        statuses = ["healthy", "warning", "critical", "unknown"]

        for status in statuses:
            indicator = module.create_health_indicator(
                f"test_{status}", status, f"Status: {status}"
            )
            assert indicator.status == status

    def test_performance_metrics_in_status(self, module):
        """Test performance metrics inclusion in status."""
        status = module.get_module_status()

        assert "performance_metrics" in status.model_dump()
        assert isinstance(status.performance_metrics, dict)
        assert status.performance_metrics["test_metric"] == 42
