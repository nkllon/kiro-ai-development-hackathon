"""Pytest configuration and shared fixtures."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from src.rm_ddd.core.base_reflective_module import ReflectiveModule


# Mock classes for testing when modules aren't available
class MockTextProtocolHandler(ReflectiveModule):
    """Mock TextProtocolHandler for testing."""

    def __init__(self, instance_id: str):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        self.instance_id = instance_id


class MockStructuredAction(ReflectiveModule):
    """Mock StructuredAction for testing."""

    def __init__(
        self,
        verb: str,
        noun: str,
        modifiers: list = None,
        parameters: dict = None,
        source_instance: str = None,
    ):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        self.verb = verb
        self.noun = noun
        self.modifiers = modifiers or []
        self.parameters = parameters or {}
        self.source_instance = source_instance
        self.correlation_id = f"test-{datetime.now().timestamp()}"


class MockActionResult(ReflectiveModule):
    """Mock ActionResult for testing."""

    def __init__(
        self,
        success: bool,
        message: str,
        execution_time: timedelta,
        correlation_id: str,
    ):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        self.success = success
        self.message = message
        self.execution_time = execution_time
        self.correlation_id = correlation_id


@pytest.fixture
def protocol_handler():
    """Create a MockTextProtocolHandler instance for testing."""
    return MockTextProtocolHandler("test-instance-1")


@pytest.fixture
def sample_action():
    """Create a sample MockStructuredAction for testing."""
    return MockStructuredAction(
        verb="run",
        noun="task",
        modifiers=["beast-mode"],
        parameters={"task_id": "test-task-123"},
        source_instance="test-instance-1",
    )


@pytest.fixture
def mock_handler():
    """Create a mock action handler for testing."""

    def handler(action: MockStructuredAction) -> MockActionResult:
        return MockActionResult(
            success=True,
            message=f"Executed {action.verb} {action.noun}",
            execution_time=timedelta(seconds=1.5),
            correlation_id=action.correlation_id,
        )

    return handler


@pytest.fixture
def failing_handler():
    """Create a failing action handler for testing."""

    def handler(action: MockStructuredAction) -> MockActionResult:
        return MockActionResult(
            success=False,
            message="Handler failed",
            execution_time=timedelta(seconds=0.5),
            correlation_id=action.correlation_id,
        )

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": [],
            "capabilities": [],
        }

    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, "register"):
            registry.register(self.get_interface_metadata())

    def health_check(self):
        """Perform health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "module_id": getattr(self, "module_id", self.__class__.__name__),
        }

    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

    return handler
