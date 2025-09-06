"""Tests for protocol data models."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.multi_instance_orchestration.protocol.models import (
    ActionResult,
    CommandPattern,
    StructuredAction,
    ValidationResult,
)


class TestStructuredAction:
    """Test StructuredAction model."""

    def test_valid_action_creation(self):
        """Test creating a valid StructuredAction."""
        action = StructuredAction(
            verb="run",
            noun="task",
            modifiers=["beast-mode"],
            parameters={"task_id": "test-123"},
            source_instance="test-instance",
        )

        assert action.verb == "run"
        assert action.noun == "task"
        assert action.modifiers == ["beast-mode"]
        assert action.parameters == {"task_id": "test-123"}
        assert action.source_instance == "test-instance"
        assert isinstance(action.timestamp, datetime)
        assert action.correlation_id is not None

    def test_invalid_verb_validation(self):
        """Test validation of invalid verbs."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredAction(verb="invalid_verb", noun="task", source_instance="test")

        assert "not in allowed verbs" in str(exc_info.value)

    def test_invalid_noun_validation(self):
        """Test validation of invalid nouns."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredAction(verb="run", noun="invalid_noun", source_instance="test")

        assert "not in allowed nouns" in str(exc_info.value)

    def test_to_command_string(self):
        """Test converting action to command string."""
        action = StructuredAction(
            verb="run",
            noun="task",
            modifiers=["beast-mode", "parallel"],
            parameters={"task_id": "test-123", "timeout": 300},
            source_instance="test",
        )

        command = action.to_command_string()
        assert "run task beast-mode parallel" in command
        assert "task_id=test-123" in command
        assert "timeout=300" in command

    def test_from_command_string_basic(self):
        """Test parsing basic command string."""
        command = "run task beast-mode task_id=test-123"
        action = StructuredAction.from_command_string(command, "test-instance")

        assert action.verb == "run"
        assert action.noun == "task"
        assert "beast-mode" in action.modifiers
        assert action.parameters["task_id"] == "test-123"
        assert action.source_instance == "test-instance"

    def test_from_command_string_with_types(self):
        """Test parsing command string with different parameter types."""
        command = "scale instances up count=5 timeout=30.5 force=true"
        action = StructuredAction.from_command_string(command, "test")

        assert action.verb == "scale"
        assert action.noun == "instances"
        assert "up" in action.modifiers
        assert action.parameters["count"] == 5
        assert action.parameters["timeout"] == 30.5
        assert action.parameters["force"] is True

    def test_from_command_string_invalid(self):
        """Test parsing invalid command string."""
        with pytest.raises(ValueError):
            StructuredAction.from_command_string("run", "test")

    def test_round_trip_conversion(self):
        """Test round-trip conversion between action and command string."""
        original = StructuredAction(
            verb="stop",
            noun="instance",
            modifiers=["graceful"],
            parameters={"instance_id": "kiro-3", "timeout": 60},
            source_instance="test",
        )

        command = original.to_command_string()
        parsed = StructuredAction.from_command_string(command, "test")

        assert parsed.verb == original.verb
        assert parsed.noun == original.noun
        assert set(parsed.modifiers) == set(original.modifiers)
        assert parsed.parameters == original.parameters


class TestActionResult:
    """Test ActionResult model."""

    def test_successful_result(self):
        """Test creating successful action result."""
        result = ActionResult(
            success=True,
            message="Task completed successfully",
            data={"output": "test output"},
            execution_time=timedelta(seconds=2.5),
            correlation_id="test-correlation-id",
        )

        assert result.success is True
        assert result.message == "Task completed successfully"
        assert result.data == {"output": "test output"}
        assert result.execution_time == timedelta(seconds=2.5)
        assert result.correlation_id == "test-correlation-id"

    def test_failed_result(self):
        """Test creating failed action result."""
        result = ActionResult(
            success=False,
            message="Task failed",
            execution_time=timedelta(seconds=1.0),
            correlation_id="test-id",
            side_effects=["cleanup performed"],
        )

        assert result.success is False
        assert result.message == "Task failed"
        assert result.side_effects == ["cleanup performed"]

    def test_to_response_string_success(self):
        """Test converting successful result to response string."""
        result = ActionResult(
            success=True,
            message="Task completed",
            execution_time=timedelta(seconds=1.5),
            correlation_id="test-id",
        )

        response = result.to_response_string()
        assert "[SUCCESS]" in response
        assert "Task completed" in response
        assert "1.50s" in response

    def test_to_response_string_failure(self):
        """Test converting failed result to response string."""
        result = ActionResult(
            success=False,
            message="Task failed",
            execution_time=timedelta(seconds=0.5),
            correlation_id="test-id",
            data={"error_code": 500},
            side_effects=["rollback performed"],
        )

        response = result.to_response_string()
        assert "[FAILED]" in response
        assert "Task failed" in response
        assert "0.50s" in response
        assert "error_code" in response
        assert "rollback performed" in response


class TestValidationResult:
    """Test ValidationResult model."""

    def test_valid_result(self):
        """Test creating valid validation result."""
        result = ValidationResult(is_valid=True, warnings=["Minor warning"])

        assert result.is_valid is True
        assert result.warnings == ["Minor warning"]
        assert result.errors == []

    def test_invalid_result(self):
        """Test creating invalid validation result."""
        result = ValidationResult(
            is_valid=False,
            errors=["Missing parameter", "Invalid format"],
            suggestions=["Try adding parameter X"],
        )

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.suggestions == ["Try adding parameter X"]

    def test_to_string_valid(self):
        """Test converting valid result to string."""
        result = ValidationResult(is_valid=True, warnings=["Minor issue"])

        string_result = result.to_string()
        assert "VALID" in string_result
        assert "Minor issue" in string_result

    def test_to_string_invalid(self):
        """Test converting invalid result to string."""
        result = ValidationResult(
            is_valid=False, errors=["Error 1", "Error 2"], suggestions=["Suggestion 1"]
        )

        string_result = result.to_string()
        assert "INVALID" in string_result
        assert "Error 1" in string_result
        assert "Error 2" in string_result
        assert "Suggestion 1" in string_result


class TestCommandPattern:
    """Test CommandPattern model."""

    def test_pattern_creation(self):
        """Test creating command pattern."""
        pattern = CommandPattern(
            verb="run",
            noun="task",
            allowed_modifiers=["beast-mode", "parallel"],
            required_parameters=["task_id"],
            optional_parameters=["timeout"],
            description="Execute a task",
            examples=["run task abc beast-mode"],
        )

        assert pattern.verb == "run"
        assert pattern.noun == "task"
        assert "beast-mode" in pattern.allowed_modifiers
        assert "task_id" in pattern.required_parameters
        assert pattern.description == "Execute a task"

    def test_pattern_matches(self):
        """Test pattern matching."""
        pattern = CommandPattern(verb="run", noun="task", description="Test")

        matching_action = StructuredAction(
            verb="run", noun="task", source_instance="test"
        )
        non_matching_action = StructuredAction(
            verb="stop", noun="instance", source_instance="test"
        )

        assert pattern.matches(matching_action) is True
        assert pattern.matches(non_matching_action) is False

    def test_validate_action_success(self):
        """Test successful action validation."""
        pattern = CommandPattern(
            verb="run",
            noun="task",
            allowed_modifiers=["beast-mode"],
            required_parameters=["task_id"],
            description="Test",
        )

        action = StructuredAction(
            verb="run",
            noun="task",
            modifiers=["beast-mode"],
            parameters={"task_id": "test-123"},
            source_instance="test",
        )

        result = pattern.validate_action(action)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_action_missing_parameter(self):
        """Test validation with missing required parameter."""
        pattern = CommandPattern(
            verb="run", noun="task", required_parameters=["task_id"], description="Test"
        )

        action = StructuredAction(verb="run", noun="task", source_instance="test")

        result = pattern.validate_action(action)
        assert result.is_valid is False
        assert "Missing required parameter: task_id" in result.errors

    def test_validate_action_unknown_modifier(self):
        """Test validation with unknown modifier."""
        pattern = CommandPattern(
            verb="run",
            noun="task",
            allowed_modifiers=["beast-mode"],
            description="Test",
        )

        action = StructuredAction(
            verb="run",
            noun="task",
            modifiers=["unknown-modifier"],
            source_instance="test",
        )

        result = pattern.validate_action(action)
        assert result.is_valid is True  # Warnings don't make it invalid
        assert "Unknown modifier: unknown-modifier" in result.warnings
        assert "Available modifiers: beast-mode" in result.suggestions
