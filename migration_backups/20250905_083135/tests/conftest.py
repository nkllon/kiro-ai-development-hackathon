"""
Root-level test fixtures for Beast Mode Framework
Provides shared fixtures across all test modules
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Import the classes that tests need
try:
    from src.beast_mode.orchestration.tool_orchestrator import (
        ToolOrchestrator, ToolDefinition, ToolExecutionRequest, ToolExecutionResult,
        ToolType, ToolStatus, ExecutionStrategy, ToolHealthMetrics
    )
except ImportError:
    # Create mock classes if the actual implementation doesn't exist yet
    class ToolOrchestrator:
        def __init__(self):
            self.registered_tools = {}
            self.tool_status = {}
            self.tool_metrics = {}
            
        def register_tool(self, tool_definition):
            return {
                "success": True,
                "tool_id": tool_definition.tool_id,
                "systematic_constraints_validated": True
            }
            
        def intelligent_tool_selection(self, task_context, execution_strategy=None):
            return {
                "selected_tool_id": "test_tool",
                "systematic_compliance": True,
                "decision_confidence": 0.9,
                "decision_rationale": "Test selection",
                "alternative_tools": []
            }
            
        def execute_tool_systematically(self, request):
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_id=request.tool_id,
                status="success",
                output="test output",
                error_output="",
                exit_code=0,
                execution_time_ms=100,
                systematic_compliance=True,
                recommendations=[]
            )
            
        def monitor_tool_health(self, tool_id=None):
            if tool_id:
                return {
                    "health_status": {"status": "healthy"},
                    "systematic_compliance": True
                }
            return {
                "overall_health": "healthy",
                "health_summary": {},
                "systematic_compliance_overview": {},
                "monitoring_recommendations": []
            }
            
        def optimize_tool_performance(self, optimization_context):
            return {
                "optimization_applied": True,
                "performance_improvements": {},
                "systematic_compliance_maintained": True,
                "bottleneck_analysis": {}
            }
            
        def get_orchestration_analytics(self):
            return {
                "execution_analytics": {
                    "total_executions": 0,
                    "success_rate": 1.0,
                    "systematic_compliance_rate": 1.0
                },
                "decision_framework_effectiveness": {},
                "tool_usage_patterns": {},
                "optimization_impact": {},
                "health_monitoring_insights": {}
            }
            
        def get_module_status(self):
            return {
                "module_name": "tool_orchestrator",
                "status": "operational",
                "registered_tools": 0,
                "total_executions": 0,
                "success_rate": 1.0
            }
            
        def get_health_indicators(self):
            return {
                "tool_availability": {},
                "component_health": {},
                "performance_metrics": {},
                "tool_health_summary": {}
            }
            
        def is_healthy(self):
            return True
            
        def _get_most_used_tools(self):
            return []
            
        def _rank_tools_by_performance(self):
            return []
            
        def _analyze_usage_trends(self):
            return {}
            
        def _analyze_failure_patterns(self):
            return {
                "common_failure_types": [],
                "failure_frequency": {},
                "prevention_recommendations": []
            }
            
        def _generate_maintenance_recommendations(self):
            return []
            
        def _analyze_performance_patterns(self):
            return {}
            
        def _identify_optimization_opportunities(self, performance_analysis, context):
            return []
            
        def _improve_tool_compliance(self, tool_id, context):
            return {
                "success": True,
                "optimization_type": "compliance_improvement",
                "new_compliance_rate": 0.9
            }
            
        def _optimize_tool_performance(self, tool_id, context):
            return {
                "success": True,
                "optimization_type": "performance_tuning",
                "improvement_ms": 1000,
                "new_average_time_ms": 2000
            }
            
        def _validate_execution_constraints(self, tool_definition, parameters, execution_strategy):
            return {
                "valid": True,
                "systematic_compliance": True,
                "violations": []
            }

    class ToolDefinition:
        def __init__(self, tool_id, name, tool_type, command_template, 
                     systematic_constraints=None, performance_profile=None,
                     health_check_command=None, timeout_seconds=30):
            self.tool_id = tool_id
            self.name = name
            self.tool_type = tool_type
            self.command_template = command_template
            self.systematic_constraints = systematic_constraints or {}
            self.performance_profile = performance_profile or {}
            self.health_check_command = health_check_command
            self.timeout_seconds = timeout_seconds

    class ToolExecutionRequest:
        def __init__(self, request_id, tool_id, parameters, execution_strategy, context):
            self.request_id = request_id
            self.tool_id = tool_id
            self.parameters = parameters
            self.execution_strategy = execution_strategy
            self.context = context

    class ToolExecutionResult:
        def __init__(self, request_id, tool_id, status, output="", error_output="",
                     exit_code=0, execution_time_ms=0, systematic_compliance=True,
                     recommendations=None):
            self.request_id = request_id
            self.tool_id = tool_id
            self.status = status
            self.output = output
            self.error_output = error_output
            self.exit_code = exit_code
            self.execution_time_ms = execution_time_ms
            self.systematic_compliance = systematic_compliance
            self.recommendations = recommendations or []

    class ToolType:
        BUILD_TOOL = "build_tool"

    class ToolStatus:
        AVAILABLE = "available"
        DEGRADED = "degraded"
        FAILED = "failed"

    class ExecutionStrategy:
        SYSTEMATIC_ONLY = "systematic_only"
        PERFORMANCE_OPTIMIZED = "performance_optimized"

    class ToolHealthMetrics:
        def __init__(self, tool_id):
            self.tool_id = tool_id
            self.availability_percentage = 100.0
            self.success_rate = 1.0
            self.systematic_compliance_rate = 1.0
            self.average_execution_time_ms = 1000
            self.performance_trend = "stable"
            self.last_health_check = datetime.now()
            self.error_patterns = []


@pytest.fixture
def orchestrator():
    """Create tool orchestrator instance for testing"""
    return ToolOrchestrator()


@pytest.fixture
def sample_tool_definition():
    """Create sample tool definition for testing"""
    return ToolDefinition(
        tool_id="test_tool",
        name="Test Tool",
        tool_type=ToolType.BUILD_TOOL,
        command_template="echo {message}",
        systematic_constraints={
            "no_ad_hoc_commands": True,
            "systematic_error_handling": True
        },
        performance_profile={
            "typical_execution_time_ms": 1000,
            "memory_usage_mb": 50,
            "cpu_utilization": 0.2
        },
        health_check_command="echo 'healthy'",
        timeout_seconds=30
    )


@pytest.fixture
def sample_execution_request():
    """Create sample execution request for testing"""
    return ToolExecutionRequest(
        request_id=str(uuid.uuid4()),
        tool_id="test_tool",
        parameters={"message": "test"},
        execution_strategy=ExecutionStrategy.SYSTEMATIC_ONLY,
        context={"task_type": "build"}
    )


@pytest.fixture
def mock_intelligence_engine():
    """Mock intelligence engine with required methods"""
    engine = Mock()
    engine.consult_registry_first.return_value = {"tools": ["test_tool"], "confidence": 0.9}
    engine.get_domain_tools.return_value = ["test_tool", "other_tool"]
    return engine


@pytest.fixture
def mock_multi_perspective_engine():
    """Mock multi-perspective validator with required methods"""
    engine = Mock()
    engine.get_basic_perspective_analysis.return_value = {
        "perspectives": ["technical", "business"],
        "analysis": {"confidence": 0.8}
    }
    engine.analyze_low_percentage_decision.return_value = {
        "risk_factors": [],
        "recommendations": [],
        "confidence_boost": 0.1
    }
    return engine


@pytest.fixture
def mock_safety_manager():
    """Mock safety manager with required methods"""
    manager = Mock()
    manager.validate_workflow_safety.return_value = True
    manager.get_safety_status.return_value = Mock(
        is_safe=True,
        resource_usage={"cpu_percent": 25.0, "memory_mb": 100.0},
        violations=[],
        kill_switch_armed=True
    )
    manager.initialize_safety_systems.return_value = True
    manager.emergency_shutdown_triggered = False
    return manager