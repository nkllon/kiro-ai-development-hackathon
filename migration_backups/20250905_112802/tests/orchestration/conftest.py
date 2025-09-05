"""
Orchestration-specific test fixtures
Provides fixtures for tool orchestration and execution testing
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for tool execution testing"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            stdout="test output",
            stderr="",
            returncode=0
        )
        yield mock_run


@pytest.fixture
def failing_tool_definition(sample_tool_definition):
    """Tool definition that will fail execution"""
    failing_tool = sample_tool_definition
    failing_tool.tool_id = "failing_tool"
    failing_tool.name = "Failing Tool"
    failing_tool.command_template = "exit 1"
    return failing_tool


@pytest.fixture
def fast_tool_definition():
    """Fast tool definition for performance testing"""
    from tests.conftest import ToolDefinition, ToolType
    return ToolDefinition(
        tool_id="fast_tool",
        name="Fast Tool",
        tool_type=ToolType.BUILD_TOOL,
        command_template="echo fast",
        systematic_constraints={
            "no_ad_hoc_commands": True,
            "systematic_error_handling": True
        },
        performance_profile={"typical_execution_time_ms": 500}
    )


@pytest.fixture
def slow_tool_definition():
    """Slow tool definition for performance testing"""
    from tests.conftest import ToolDefinition, ToolType
    return ToolDefinition(
        tool_id="slow_tool",
        name="Slow Tool",
        tool_type=ToolType.BUILD_TOOL,
        command_template="sleep 1 && echo slow",
        systematic_constraints={
            "no_ad_hoc_commands": True,
            "systematic_error_handling": True
        },
        performance_profile={"typical_execution_time_ms": 5000}
    )


@pytest.fixture
def orchestrator_with_tools(orchestrator, sample_tool_definition, fast_tool_definition, slow_tool_definition):
    """Orchestrator pre-loaded with test tools"""
    orchestrator.register_tool(sample_tool_definition)
    orchestrator.register_tool(fast_tool_definition)
    orchestrator.register_tool(slow_tool_definition)
    
    # Initialize tool metrics
    from tests.conftest import ToolHealthMetrics
    orchestrator.tool_metrics[sample_tool_definition.tool_id] = ToolHealthMetrics(sample_tool_definition.tool_id)
    orchestrator.tool_metrics[fast_tool_definition.tool_id] = ToolHealthMetrics(fast_tool_definition.tool_id)
    orchestrator.tool_metrics[slow_tool_definition.tool_id] = ToolHealthMetrics(slow_tool_definition.tool_id)
    
    return orchestrator


@pytest.fixture
def mock_tool_health_metrics():
    """Mock tool health metrics for testing"""
    from tests.conftest import ToolHealthMetrics
    metrics = ToolHealthMetrics("test_tool")
    metrics.success_rate = 0.9
    metrics.systematic_compliance_rate = 0.95
    metrics.availability_percentage = 98.0
    metrics.average_execution_time_ms = 1500
    metrics.performance_trend = "stable"
    metrics.last_health_check = datetime.now() - timedelta(minutes=5)
    metrics.error_patterns = ["timeout error", "permission denied"]
    return metrics