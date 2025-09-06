"""
Tests for Tool Orchestration Engine
Tests UC-03: Model-Driven Decision Making with confidence-based routing
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.beast_mode.orchestration.tool_orchestration_engine import (
    ToolOrchestrationEngine,
    DecisionConfidenceLevel,
    DecisionContext,
    ToolDefinition,
    ToolStatus,
    ToolPriority,
    OrchestrationResult,
    ToolExecutionResult
)

class TestToolOrchestrationEngine:
    """Test tool orchestration functionality"""
    
    @pytest.fixture
    def orchestration_engine(self, tmp_path):
        return ToolOrchestrationEngine(str(tmp_path))
        
    @pytest.fixture
    def sample_decision_context(self):
        return DecisionContext(
            decision_id="test_decision_001",
            problem_statement="Need to check project status",
            available_options=["git status", "make help", "python version"],
            constraints=["Must complete within 30 seconds"],
            stakeholder_requirements={"accuracy": "high", "speed": "medium"},
            time_pressure="normal",
            risk_tolerance="medium",
            domain="development_tools"
        )
        
    @pytest.fixture
    def sample_tool_definition(self):
        return ToolDefinition(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool for validation",
            command="echo 'test output'",
            health_check_command="echo 'healthy'",
            priority=ToolPriority.MEDIUM,
            timeout_seconds=30,
            repair_procedures=["echo 'repair attempt'"]
        )
        
    def test_tool_registration(self, orchestration_engine, sample_tool_definition):
        """Test tool registration functionality"""
        result = orchestration_engine.register_tool(sample_tool_definition)
        
        assert result["success"] is True
        assert result["tool_id"] == "test_tool"
        assert result["name"] == "Test Tool"
        assert "initial_health" in result
        
        # Verify tool is in registry
        assert "test_tool" in orchestration_engine.tools_registry
        assert "test_tool" in orchestration_engine.tool_health_cache
        
    def test_invalid_tool_registration(self, orchestration_engine):
        """Test registration of invalid tool definition"""
        invalid_tool = ToolDefinition(
            tool_id="",  # Invalid empty ID
            name="Invalid Tool",
            description="Invalid tool",
            command="",  # Invalid empty command
            timeout_seconds=-1  # Invalid timeout
        )
        
        result = orchestration_engine.register_tool(invalid_tool)
        assert "error" in result
        
    def test_decision_confidence_assessment(self, orchestration_engine, sample_decision_context):
        """Test decision confidence assessment"""
        # Mock intelligence engine response
        with patch.object(orchestration_engine.intelligence_engine, 'consult_registry_first') as mock_consult:
            mock_consult.return_value = {
                "domain_match": True,
                "requirements_match": True,
                "tool_mappings": True,
                "historical_patterns": False
            }
            
            confidence_result = orchestration_engine._assess_decision_confidence(sample_decision_context)
            
            assert "confidence_level" in confidence_result
            assert "confidence_score" in confidence_result
            assert "confidence_factors" in confidence_result
            assert isinstance(confidence_result["confidence_level"], DecisionConfidenceLevel)
            
    def test_high_confidence_decision_routing(self, orchestration_engine, sample_decision_context):
        """Test high confidence decision routing"""
        # Mock high confidence scenario
        with patch.object(orchestration_engine.intelligence_engine, 'get_domain_tools') as mock_domain_tools:
            mock_domain_tools.return_value = ["git_status", "make_help", "python_version"]
            
            decision_result = orchestration_engine._make_high_confidence_decision(
                sample_decision_context, 
                preferred_tools=["git_status"]
            )
            
            assert "selected_tools" in decision_result
            assert "rationale" in decision_result
            assert "decision_method" in decision_result
            assert decision_result["decision_method"] == "model_registry_domain_intelligence"
            
    def test_medium_confidence_decision_routing(self, orchestration_engine, sample_decision_context):
        """Test medium confidence decision routing"""
        # Mock medium confidence scenario
        with patch.object(orchestration_engine.multi_perspective_engine, 'get_basic_perspective_analysis') as mock_perspective:
            mock_perspective.return_value = {
                "recommended_tools": ["git_status", "python_version"]
            }
            
            with patch.object(orchestration_engine, '_make_high_confidence_decision') as mock_high_confidence:
                mock_high_confidence.return_value = {
                    "selected_tools": ["git_status", "make_help"]
                }
                
                decision_result = orchestration_engine._make_medium_confidence_decision(
                    sample_decision_context
                )
                
                assert "selected_tools" in decision_result
                assert decision_result["decision_method"] == "registry_plus_basic_perspectives"
                
    def test_low_confidence_decision_routing(self, orchestration_engine, sample_decision_context):
        """Test low confidence decision routing with full multi-stakeholder analysis"""
        # Mock low confidence scenario
        with patch.object(orchestration_engine.multi_perspective_engine, 'analyze_low_percentage_decision') as mock_analysis:
            mock_analysis.return_value = {
                "perspectives": [
                    {"recommended_tools": ["git_status", "make_help"]},
                    {"recommended_tools": ["git_status", "python_version"]},
                    {"recommended_tools": ["make_help"]}
                ],
                "synthesized_recommendation": {
                    "tools": ["git_status"]
                }
            }
            
            decision_result = orchestration_engine._make_low_confidence_decision(
                sample_decision_context
            )
            
            assert "selected_tools" in decision_result
            assert decision_result["decision_method"] == "full_multi_stakeholder_analysis"
            assert "stakeholder_analysis" in decision_result
            
    @patch('subprocess.run')
    def test_single_tool_execution(self, mock_subprocess, orchestration_engine, sample_decision_context, sample_tool_definition):
        """Test execution of a single tool"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        # Mock successful subprocess execution
        mock_subprocess.return_value = Mock(
            stdout="test output",
            stderr="",
            returncode=0
        )
        
        result = orchestration_engine._execute_single_tool(
            "test_tool",
            sample_decision_context,
            "test_operation"
        )
        
        assert isinstance(result, ToolExecutionResult)
        assert result.success is True
        assert result.tool_id == "test_tool"
        assert result.output == "test output"
        assert result.health_status == ToolStatus.HEALTHY
        
    @patch('subprocess.run')
    def test_tool_execution_failure(self, mock_subprocess, orchestration_engine, sample_decision_context, sample_tool_definition):
        """Test handling of tool execution failure"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        # Mock failed subprocess execution
        mock_subprocess.return_value = Mock(
            stdout="",
            stderr="command failed",
            returncode=1
        )
        
        result = orchestration_engine._execute_single_tool(
            "test_tool",
            sample_decision_context,
            "test_operation"
        )
        
        assert isinstance(result, ToolExecutionResult)
        assert result.success is False
        assert result.error == "command failed"
        assert result.health_status == ToolStatus.DEGRADED
        
    @patch('subprocess.run')
    def test_tool_execution_timeout(self, mock_subprocess, orchestration_engine, sample_decision_context, sample_tool_definition):
        """Test handling of tool execution timeout"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        # Mock timeout exception
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired("test_command", 30)
        
        result = orchestration_engine._execute_single_tool(
            "test_tool",
            sample_decision_context,
            "test_operation"
        )
        
        assert isinstance(result, ToolExecutionResult)
        assert result.success is False
        assert "timed out" in result.error
        assert result.health_status == ToolStatus.FAILED
        
    def test_tool_health_checking(self, orchestration_engine, sample_tool_definition):
        """Test tool health checking functionality"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock healthy tool
            mock_subprocess.return_value = Mock(returncode=0)
            
            health_result = orchestration_engine._check_tool_health("test_tool")
            
            assert health_result["status"] == ToolStatus.HEALTHY
            assert health_result["tool_id"] == "test_tool"
            
    def test_tool_selection_by_health_and_priority(self, orchestration_engine):
        """Test tool selection based on health and priority"""
        # Register multiple tools with different priorities
        tools = [
            ToolDefinition(
                tool_id="critical_tool",
                name="Critical Tool",
                description="Critical priority tool",
                command="echo critical",
                priority=ToolPriority.CRITICAL
            ),
            ToolDefinition(
                tool_id="high_tool",
                name="High Tool", 
                description="High priority tool",
                command="echo high",
                priority=ToolPriority.HIGH
            ),
            ToolDefinition(
                tool_id="medium_tool",
                name="Medium Tool",
                description="Medium priority tool", 
                command="echo medium",
                priority=ToolPriority.MEDIUM
            )
        ]
        
        for tool in tools:
            orchestration_engine.register_tool(tool)
            
        # Mock all tools as healthy
        with patch.object(orchestration_engine, '_check_tool_health') as mock_health:
            mock_health.return_value = {"status": ToolStatus.HEALTHY}
            
            selected_tools = orchestration_engine._select_tools_by_health_and_priority(
                ["critical_tool", "high_tool", "medium_tool"]
            )
            
            # Should prioritize by priority level
            assert selected_tools[0] == "critical_tool"
            assert selected_tools[1] == "high_tool"
            assert selected_tools[2] == "medium_tool"
            
    def test_systematic_tool_repair(self, orchestration_engine, sample_tool_definition):
        """Test systematic tool repair functionality"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        # Mock RCA result
        mock_rca_result = {
            "root_causes": [
                {"suggested_repairs": ["echo 'rca repair'"]}
            ]
        }
        
        with patch.object(orchestration_engine, '_perform_tool_rca') as mock_rca:
            mock_rca.return_value = mock_rca_result
            
            with patch.object(orchestration_engine, '_execute_repair_procedure') as mock_repair:
                mock_repair.return_value = {"success": True}
                
                with patch.object(orchestration_engine, '_check_tool_health') as mock_health:
                    mock_health.return_value = {"status": ToolStatus.HEALTHY}
                    
                    repair_result = orchestration_engine._attempt_systematic_repair(
                        "test_tool",
                        mock_rca_result
                    )
                    
                    assert repair_result["success"] is True
                    assert "repair_procedure" in repair_result
                    
    def test_full_orchestration_workflow(self, orchestration_engine, sample_decision_context, sample_tool_definition):
        """Test complete orchestration workflow"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        # Mock all dependencies
        with patch.object(orchestration_engine.intelligence_engine, 'consult_registry_first') as mock_consult:
            mock_consult.return_value = {
                "domain_match": True,
                "requirements_match": True,
                "tool_mappings": True,
                "historical_patterns": True
            }
            
            with patch.object(orchestration_engine.intelligence_engine, 'get_domain_tools') as mock_domain_tools:
                mock_domain_tools.return_value = ["test_tool"]
                
                with patch('subprocess.run') as mock_subprocess:
                    mock_subprocess.return_value = Mock(
                        stdout="successful execution",
                        stderr="",
                        returncode=0
                    )
                    
                    result = orchestration_engine.orchestrate_tool_execution(
                        sample_decision_context,
                        preferred_tools=["test_tool"]
                    )
                    
                    assert isinstance(result, OrchestrationResult)
                    assert result.success is True
                    assert result.decision_confidence == DecisionConfidenceLevel.HIGH
                    assert result.primary_result is not None
                    assert len(result.recommendations) > 0
                    
    def test_orchestration_metrics_tracking(self, orchestration_engine, sample_decision_context, sample_tool_definition):
        """Test orchestration metrics tracking"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        initial_metrics = orchestration_engine.orchestration_metrics.copy()
        
        # Mock successful orchestration
        with patch.object(orchestration_engine.intelligence_engine, 'consult_registry_first') as mock_consult:
            mock_consult.return_value = {"domain_match": True, "requirements_match": True}
            
            with patch.object(orchestration_engine.intelligence_engine, 'get_domain_tools') as mock_domain_tools:
                mock_domain_tools.return_value = ["test_tool"]
                
                with patch('subprocess.run') as mock_subprocess:
                    mock_subprocess.return_value = Mock(stdout="success", stderr="", returncode=0)
                    
                    orchestration_engine.orchestrate_tool_execution(sample_decision_context)
                    
        # Verify metrics were updated
        assert orchestration_engine.orchestration_metrics['total_orchestrations'] > initial_metrics['total_orchestrations']
        assert orchestration_engine.orchestration_metrics['successful_orchestrations'] > initial_metrics['successful_orchestrations']
        
    def test_decision_analytics(self, orchestration_engine, sample_decision_context, sample_tool_definition):
        """Test decision analytics functionality"""
        # Register tool and perform some orchestrations
        orchestration_engine.register_tool(sample_tool_definition)
        
        # Add some mock decision history
        orchestration_engine.decision_history = [
            {
                "operation_id": "test_1",
                "confidence_level": "high",
                "success": True,
                "execution_time_ms": 1000
            },
            {
                "operation_id": "test_2", 
                "confidence_level": "medium",
                "success": False,
                "execution_time_ms": 2000
            }
        ]
        
        analytics = orchestration_engine.get_decision_analytics()
        
        assert "total_decisions" in analytics
        assert "confidence_distribution" in analytics
        assert "success_rates_by_confidence" in analytics
        assert "overall_success_rate" in analytics
        assert analytics["total_decisions"] == 2
        
    def test_tool_health_refresh(self, orchestration_engine, sample_tool_definition):
        """Test forced tool health refresh"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            refresh_result = orchestration_engine.force_tool_health_refresh()
            
            assert "refreshed_tools" in refresh_result
            assert "health_status" in refresh_result
            assert refresh_result["refreshed_tools"] > 0
            
    def test_registered_tools_info(self, orchestration_engine, sample_tool_definition):
        """Test getting registered tools information"""
        # Register tool first
        orchestration_engine.register_tool(sample_tool_definition)
        
        tools_info = orchestration_engine.get_registered_tools()
        
        assert "test_tool" in tools_info
        tool_info = tools_info["test_tool"]
        assert "name" in tool_info
        assert "description" in tool_info
        assert "priority" in tool_info
        assert "health_status" in tool_info
        
    def test_module_health_and_status(self, orchestration_engine):
        """Test module health and status reporting"""
        # Test module status
        status = orchestration_engine.get_module_status()
        assert "module_name" in status
        assert "status" in status
        assert "registered_tools" in status
        
        # Test health check
        assert orchestration_engine.is_healthy() is True
        
        # Test health indicators
        health_indicators = orchestration_engine.get_health_indicators()
        assert "orchestration_status" in health_indicators
        assert "decision_framework" in health_indicators
        assert "performance_metrics" in health_indicators

class TestDecisionConfidenceFramework:
    """Test the confidence-based decision framework"""
    
    def test_confidence_level_enum(self):
        """Test confidence level enumeration"""
        assert DecisionConfidenceLevel.HIGH.value == "high"
        assert DecisionConfidenceLevel.MEDIUM.value == "medium"
        assert DecisionConfidenceLevel.LOW.value == "low"
        
    def test_decision_context_creation(self):
        """Test decision context data structure"""
        context = DecisionContext(
            decision_id="test_001",
            problem_statement="Test problem",
            available_options=["option1", "option2"],
            constraints=["constraint1"],
            stakeholder_requirements={"req1": "value1"},
            time_pressure="urgent",
            risk_tolerance="low"
        )
        
        assert context.decision_id == "test_001"
        assert context.problem_statement == "Test problem"
        assert len(context.available_options) == 2
        assert context.time_pressure == "urgent"
        assert context.risk_tolerance == "low"

class TestToolDefinitionAndExecution:
    """Test tool definition and execution components"""
    
    def test_tool_definition_creation(self):
        """Test tool definition data structure"""
        tool_def = ToolDefinition(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            command="echo test",
            health_check_command="echo healthy",
            dependencies=["dep1", "dep2"],
            priority=ToolPriority.HIGH,
            timeout_seconds=60,
            retry_attempts=3,
            fallback_tools=["fallback1"],
            repair_procedures=["repair1", "repair2"]
        )
        
        assert tool_def.tool_id == "test_tool"
        assert tool_def.priority == ToolPriority.HIGH
        assert len(tool_def.dependencies) == 2
        assert len(tool_def.repair_procedures) == 2
        
    def test_tool_execution_result_creation(self):
        """Test tool execution result data structure"""
        result = ToolExecutionResult(
            tool_id="test_tool",
            success=True,
            output="test output",
            error=None,
            execution_time_ms=1500,
            exit_code=0,
            health_status=ToolStatus.HEALTHY
        )
        
        assert result.tool_id == "test_tool"
        assert result.success is True
        assert result.execution_time_ms == 1500
        assert result.health_status == ToolStatus.HEALTHY
        
    def test_orchestration_result_creation(self):
        """Test orchestration result data structure"""
        result = OrchestrationResult(
            operation_id="OP-001",
            success=True,
            decision_confidence=DecisionConfidenceLevel.HIGH,
            decision_rationale="High confidence decision",
            tools_attempted=["tool1", "tool2"],
            total_execution_time_ms=2500,
            recommendations=["rec1", "rec2"]
        )
        
        assert result.operation_id == "OP-001"
        assert result.decision_confidence == DecisionConfidenceLevel.HIGH
        assert len(result.tools_attempted) == 2
        assert len(result.recommendations) == 2

if __name__ == "__main__":
    pytest.main([__file__])