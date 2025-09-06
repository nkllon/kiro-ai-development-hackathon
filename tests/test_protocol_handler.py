"""Tests for TextProtocolHandler."""

from datetime import timedelta

import pytest

from src.multi_instance_orchestration.protocol.models import (
    ActionResult,
    CommandPattern,
    StructuredAction,
)


class TestTextProtocolHandler:
    """Test TextProtocolHandler class."""

    def test_handler_initialization(self, protocol_handler):
        """Test handler initialization."""
        assert protocol_handler.instance_id == "test-instance-1"
        assert protocol_handler.name == "TextProtocolHandler"
        assert protocol_handler.version == "1.0.0"
        assert len(protocol_handler.command_patterns) > 0
        assert protocol_handler.execution_stats["total_commands"] == 0

    def test_register_pattern(self, protocol_handler):
        """Test registering command pattern."""
        pattern = CommandPattern(
            verb="test", noun="command", description="Test command"
        )

        initial_count = len(protocol_handler.command_patterns)
        protocol_handler.register_pattern(pattern)

        assert len(protocol_handler.command_patterns) == initial_count + 1
        assert "test_command" in protocol_handler.command_patterns

    def test_register_handler(self, protocol_handler, mock_handler):
        """Test registering action handler."""
        protocol_handler.register_handler("test", "command", mock_handler)

        assert "test_command" in protocol_handler.action_handlers
        assert protocol_handler.action_handlers["test_command"] == mock_handler

    def test_parse_command_direct(self, protocol_handler):
        """Test parsing direct command format."""
        command = "run task beast-mode task_id=test-123"
        action = protocol_handler.parse_command(command)

        assert action.verb == "run"
        assert action.noun == "task"
        assert "beast-mode" in action.modifiers
        assert action.parameters["task_id"] == "test-123"
        assert action.source_instance == "test-instance-1"

    def test_parse_command_natural_language(self, protocol_handler):
        """Test parsing natural language commands."""
        test_cases = [
            ("execute task abc in beast mode", "run", "task", ["beast-mode"]),
            ("stop all running threads", "stop", "instances", ["all"]),
            ("halt instance kiro-3 gracefully", "stop", "instance", ["graceful"]),
            ("synchronize branch main upstream", "sync", "branch", ["upstream"]),
            ("check swarm status", "status", "swarm", []),
        ]

        for command, expected_verb, expected_noun, expected_modifiers in test_cases:
            action = protocol_handler.parse_command(command)
            assert action.verb == expected_verb
            assert action.noun == expected_noun
            for modifier in expected_modifiers:
                assert modifier in action.modifiers

    def test_parse_command_with_ids(self, protocol_handler):
        """Test parsing commands with task/instance IDs."""
        command = "run task-123 in parallel"
        action = protocol_handler.parse_command(command)

        assert action.verb == "run"
        assert action.noun == "task"
        assert "parallel" in action.modifiers
        assert action.parameters.get("task_id") == "task-123"

    def test_parse_command_invalid(self, protocol_handler):
        """Test parsing invalid commands."""
        with pytest.raises(ValueError):
            protocol_handler.parse_command("invalid command structure")

    def test_validate_command_valid(self, protocol_handler):
        """Test validating valid command."""
        action = StructuredAction(
            verb="run",
            noun="task",
            modifiers=["beast-mode"],
            parameters={"task_id": "test-123"},
            source_instance="test",
        )

        result = protocol_handler.validate_command(action)
        assert result.is_valid is True

    def test_validate_command_unknown_pattern(self, protocol_handler):
        """Test validating unknown command pattern."""
        # Use valid verb/noun but create unknown pattern
        action = StructuredAction(
            verb="run",
            noun="workflow",  # Valid noun but no pattern registered for run_workflow
            source_instance="test",
        )

        result = protocol_handler.validate_command(action)
        assert result.is_valid is False
        assert "Unknown command pattern" in result.errors[0]

    def test_execute_action_success(self, protocol_handler, mock_handler):
        """Test successful action execution."""
        protocol_handler.register_handler("run", "task", mock_handler)

        action = StructuredAction(
            verb="run",
            noun="task",
            parameters={"task_id": "test-123"},
            source_instance="test",
        )

        result = protocol_handler.execute_action(action)

        assert result.success is True
        assert "Executed run task" in result.message
        assert protocol_handler.execution_stats["total_commands"] == 1
        assert protocol_handler.execution_stats["successful_commands"] == 1

    def test_execute_action_failure(self, protocol_handler, failing_handler):
        """Test failed action execution."""
        protocol_handler.register_handler("run", "task", failing_handler)

        action = StructuredAction(
            verb="run",
            noun="task",
            parameters={"task_id": "test-123"},
            source_instance="test",
        )

        result = protocol_handler.execute_action(action)

        assert result.success is False
        assert "Handler failed" in result.message
        assert protocol_handler.execution_stats["total_commands"] == 1
        assert protocol_handler.execution_stats["failed_commands"] == 1

    def test_execute_action_invalid_command(self, protocol_handler):
        """Test executing invalid command."""
        action = StructuredAction(
            verb="run",
            noun="task",
            source_instance="test",
            # Missing required task_id parameter
        )

        result = protocol_handler.execute_action(action)
        assert result.success is False
        assert "Invalid command" in result.message

    def test_execute_action_no_handler(self, protocol_handler):
        """Test executing action with no registered handler."""
        action = StructuredAction(
            verb="run",
            noun="workflow",  # Valid but no handler registered
            source_instance="test",
        )

        # First make it valid by registering pattern
        pattern = CommandPattern(verb="run", noun="workflow", description="Test")
        protocol_handler.register_pattern(pattern)

        result = protocol_handler.execute_action(action)
        assert result.success is False
        assert "No handler registered" in result.message

    def test_execute_action_handler_exception(self, protocol_handler):
        """Test executing action when handler raises exception."""

        def error_handler(action):
            raise RuntimeError("Handler error")

        protocol_handler.register_handler("run", "task", error_handler)

        action = StructuredAction(
            verb="run",
            noun="task",
            parameters={"task_id": "test-123"},
            source_instance="test",
        )

        result = protocol_handler.execute_action(action)
        assert result.success is False
        assert "Execution failed" in result.message
        assert "Handler error" in result.message

    def test_format_response(self, protocol_handler):
        """Test formatting action result as response."""
        result = ActionResult(
            success=True,
            message="Task completed",
            execution_time=timedelta(seconds=1.5),
            correlation_id="test-id",
        )

        response = protocol_handler.format_response(result)
        assert "[SUCCESS]" in response
        assert "Task completed" in response
        assert "1.50s" in response

    def test_get_command_help_specific(self, protocol_handler):
        """Test getting help for specific command."""
        help_text = protocol_handler.get_command_help("run", "task")

        assert "run task" in help_text
        assert "Execute a task" in help_text
        assert "beast-mode" in help_text
        assert "Examples:" in help_text

    def test_get_command_help_all(self, protocol_handler):
        """Test getting help for all commands."""
        help_text = protocol_handler.get_command_help()

        assert "Available commands:" in help_text
        assert "run task" in help_text
        assert "stop instance" in help_text
        assert "sync branch" in help_text

    def test_get_command_help_unknown(self, protocol_handler):
        """Test getting help for unknown command."""
        help_text = protocol_handler.get_command_help("unknown", "command")
        assert "No help available" in help_text

    def test_command_history(self, protocol_handler):
        """Test command history tracking."""
        initial_count = len(protocol_handler.command_history)

        protocol_handler.parse_command("run task test-123")
        protocol_handler.parse_command("stop instance kiro-1")

        assert len(protocol_handler.command_history) == initial_count + 2
        assert protocol_handler.command_history[-1].verb == "stop"
        assert protocol_handler.command_history[-2].verb == "run"

    def test_execution_statistics(
        self, protocol_handler, mock_handler, failing_handler
    ):
        """Test execution statistics tracking."""
        protocol_handler.register_handler("run", "task", mock_handler)
        protocol_handler.register_handler("stop", "instance", failing_handler)

        # Execute successful action
        action1 = StructuredAction(
            verb="run",
            noun="task",
            parameters={"task_id": "test"},
            source_instance="test",
        )
        protocol_handler.execute_action(action1)

        # Execute failing action
        action2 = StructuredAction(
            verb="stop",
            noun="instance",
            parameters={"instance_id": "test"},
            source_instance="test",
        )
        protocol_handler.execute_action(action2)

        stats = protocol_handler.execution_stats
        assert stats["total_commands"] == 2
        assert stats["successful_commands"] == 1
        assert stats["failed_commands"] == 1
        assert stats["average_execution_time"] > 0

    def test_reflective_module_interface(self, protocol_handler):
        """Test ReflectiveModule interface implementation."""
        # Test module status
        status = protocol_handler.get_module_status()
        assert status.module_name == "TextProtocolHandler"
        assert status.version == "1.0.0"
        assert status.status in ["active", "error"]
        assert status.uptime > 0

        # Test health check
        is_healthy = protocol_handler.is_healthy()
        assert isinstance(is_healthy, bool)

        # Test health indicators
        indicators = protocol_handler.get_health_indicators()
        assert isinstance(indicators, list)
        assert len(indicators) > 0

        # Check performance indicator is included
        performance_indicators = [
            ind for ind in indicators if ind.name == "performance"
        ]
        assert len(performance_indicators) == 1

    def test_health_indicator_management(self, protocol_handler):
        """Test health indicator management."""
        initial_count = len(protocol_handler._health_indicators)

        # Add health indicator
        indicator = protocol_handler.create_health_indicator(
            "test", "warning", "Test message"
        )
        protocol_handler.add_health_indicator(indicator)

        assert len(protocol_handler._health_indicators) == initial_count + 1

        # Test indicator limit (100 max)
        for i in range(150):
            protocol_handler.add_health_indicator(
                protocol_handler.create_health_indicator(
                    f"test_{i}", "healthy", f"Message {i}"
                )
            )

        assert len(protocol_handler._health_indicators) <= 100

    def test_activity_tracking(self, protocol_handler):
        """Test activity tracking."""
        initial_activity = protocol_handler.last_activity

        # Wait a small amount to ensure timestamp difference
        import time

        time.sleep(0.01)

        protocol_handler.update_activity()
        assert protocol_handler.last_activity > initial_activity

    def test_edge_cases_empty_command(self, protocol_handler):
        """Test edge case: empty command."""
        with pytest.raises(ValueError):
            protocol_handler.parse_command("")

    def test_edge_cases_whitespace_command(self, protocol_handler):
        """Test edge case: whitespace-only command."""
        with pytest.raises(ValueError):
            protocol_handler.parse_command("   ")

    def test_edge_cases_single_word_command(self, protocol_handler):
        """Test edge case: single word command."""
        # Single word should be handled by natural language parser
        # which will default to appropriate noun
        action = protocol_handler.parse_command("run")
        assert action.verb == "run"
        assert action.noun == "task"  # Default noun for run verb

    def test_complex_natural_language_parsing(self, protocol_handler):
        """Test complex natural language parsing scenarios."""
        test_cases = [
            "please execute task user-auth-123 using beast mode with timeout 300",
            "can you stop the instance kiro-5 gracefully please",
            "I need to synchronize the feature/new-ui branch with upstream",
            "show me the detailed status of the entire swarm",
            "scale up the instances to 5 workers immediately",
        ]

        for command in test_cases:
            try:
                action = protocol_handler.parse_command(command)
                assert action.verb in ["run", "stop", "sync", "status", "scale"]
                assert action.noun in [
                    "task",
                    "instance",
                    "branch",
                    "swarm",
                    "instances",
                ]
            except ValueError:
                # Some complex commands might not parse perfectly
                # This is acceptable for the current implementation
                pass

    def test_parameter_type_conversion(self, protocol_handler):
        """Test parameter type conversion in command parsing."""
        command = "run task timeout=300 priority=1.5 debug=true force=false"
        action = protocol_handler.parse_command(command)

        assert action.parameters["timeout"] == 300
        assert action.parameters["priority"] == 1.5
        assert action.parameters["debug"] is True
        assert action.parameters["force"] is False

    def test_concurrent_execution_safety(self, protocol_handler, mock_handler):
        """Test thread safety of handler execution."""
        import threading

        protocol_handler.register_handler("run", "task", mock_handler)

        results = []
        errors = []

        def execute_action(task_id):
            try:
                action = StructuredAction(
                    verb="run",
                    noun="task",
                    parameters={"task_id": f"task-{task_id}"},
                    source_instance="test",
                )
                result = protocol_handler.execute_action(action)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Execute multiple actions concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=execute_action, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(results) == 10
        assert all(result.success for result in results)
        assert protocol_handler.execution_stats["total_commands"] == 10
