"""Pytest configuration and shared fixtures."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

# Mock classes for testing when modules aren't available
class MockTextProtocolHandler:
    """Mock TextProtocolHandler for testing."""
    def __init__(self, instance_id: str):
        self.instance_id = instance_id

class MockStructuredAction:
    """Mock StructuredAction for testing."""
    def __init__(self, verb: str, noun: str, modifiers: list = None, 
                 parameters: dict = None, source_instance: str = None):
        self.verb = verb
        self.noun = noun
        self.modifiers = modifiers or []
        self.parameters = parameters or {}
        self.source_instance = source_instance
        self.correlation_id = f"test-{datetime.now().timestamp()}"

class MockActionResult:
    """Mock ActionResult for testing."""
    def __init__(self, success: bool, message: str, execution_time: timedelta, 
                 correlation_id: str):
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
        source_instance="test-instance-1"
    )


@pytest.fixture
def mock_handler():
    """Create a mock action handler for testing."""
    def handler(action: MockStructuredAction) -> MockActionResult:
        return MockActionResult(
            success=True,
            message=f"Executed {action.verb} {action.noun}",
            execution_time=timedelta(seconds=1.5),
            correlation_id=action.correlation_id
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
            correlation_id=action.correlation_id
        )
    return handler