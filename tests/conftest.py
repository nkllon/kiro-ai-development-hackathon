"""Pytest configuration and shared fixtures."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.multi_instance_orchestration.protocol.handler import TextProtocolHandler
from src.multi_instance_orchestration.protocol.models import StructuredAction, ActionResult


@pytest.fixture
def protocol_handler():
    """Create a TextProtocolHandler instance for testing."""
    return TextProtocolHandler("test-instance-1")


@pytest.fixture
def sample_action():
    """Create a sample StructuredAction for testing."""
    return StructuredAction(
        verb="run",
        noun="task",
        modifiers=["beast-mode"],
        parameters={"task_id": "test-task-123"},
        source_instance="test-instance-1"
    )


@pytest.fixture
def mock_handler():
    """Create a mock action handler for testing."""
    def handler(action: StructuredAction) -> ActionResult:
        return ActionResult(
            success=True,
            message=f"Executed {action.verb} {action.noun}",
            execution_time=timedelta(seconds=1.5),
            correlation_id=action.correlation_id
        )
    return handler


@pytest.fixture
def failing_handler():
    """Create a failing action handler for testing."""
    def handler(action: StructuredAction) -> ActionResult:
        return ActionResult(
            success=False,
            message="Handler failed",
            execution_time=timedelta(seconds=0.5),
            correlation_id=action.correlation_id
        )
    return handler