"""
Tests for Beast Mode Framework - Tool Orchestrator
Tests UC-12, UC-13, UC-14, UC-15 implementation
"""

import pytest
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.orchestration.tool_orchestrator import (
    ToolOrchestrator, ToolDefinition, ToolExecutionRequest, ToolExecutionResult,
    ToolType, ToolStatus, ExecutionStrategy, ToolHealthMetrics
)

class TestToolOrchestrator:
    """Test suite for Tool Orchestrator functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create tool orchestrator instance for testing"""
        return ToolOrchestrator()
        
    @pytest.fixture
    def sample_tool_definition(self):
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
    def sample_execution_request(self):
        """Create sample execution request for testing"""
        return ToolExecutionRequest(
            request_id=str(uuid.uuid4()),
            tool_id="test_tool",
            parameters={"message": "test"},
            execution_strategy=ExecutionStrategy.SYSTEMATIC_ONLY,
            context={"task_type": "build"}
        )

class TestToolRegistration:
    """Test tool registration functionality"""
    
    def test_register_valid_tool(self, orchestrator, sample_tool_definition):
        """Test UC-12: Register tool with valid systematic constraints"""
        result = orchestrator.register_tool(sample_tool_definition)
        
        assert result["success"] is True
        assert result["tool_id"] == "test_tool"
        assert result["systematic_constraints_validated"] is True
        assert "test_tool" in orchestrator.registered_tools
        assert orchestrator.tool_status["test_tool"] == ToolStatus.AVAILABLE
        
    def test_register_tool_invalid_constraints(self, orchestrator):
        """Test tool registration with invalid systematic constraints"""
        invalid_tool = ToolDefinition(
            tool_id="invalid_tool",
            name="Invalid Tool",
            tool_type=ToolType.BUILD_TOOL,
            command_template="rm -rf /",  # Dangerous command
            systematic_constraints={
                "no_ad_hoc_commands": False,  # Invalid
                "systematic_error_handling": False  # Invalid
            },
            performance_profile={}
        )
        
        with pytest.raises(ValueError, match="does not meet systematic constraints"):
            orchestrator.register_tool(invalid_tool)
            
    def test_tool_metrics_initialization(self, orchestrator, sample_tool_definition):
        """Test that tool metrics are properly initialized"""
        orchestrator.register_tool(sample_tool_definition)
        
        metrics = orchestrator.tool_metrics["test_tool"]
        assert isinstance(metrics, ToolHealthMetrics)
        assert metrics.tool_id == "test_tool"
        assert metrics.availability_percentage == 100.0
        assert metrics.success_rate == 1.0
        assert metrics.systematic_compliance_rate == 1.0

class TestIntelligentToolSelection:
    """Test intelligent tool selection (UC-12)"""
    
    def test_systematic_tool_selection(self, orchestrator, sample_tool_definition):
        """Test systematic tool selection with single candidate"""
        orchestrator.register_tool(sample_tool_definition)
        
        task_context = {
            "task_type": "build",
            "tool_types": ["build_tool"],
            "systematic_only": True
        }
        
        result = orchestrator.intelligent_tool_selection(
            task_context, ExecutionStrategy.SYSTEMATIC_ONLY
        )
        
        assert result["selected_tool_id"] == "test_tool"
        assert result["systematic_compliance"] is True
        assert result["decision_confidence"] > 0.0
        assert "decision_rationale" in result
        
    def test_tool_selection_multiple_candidates(self, orchestrator):
        """Test tool selection with multiple candidates"""
        # Register multiple tools
        tool1 = ToolDefinition(
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
        
        tool2 = ToolDefinition(
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
        
        orchestrator.register_tool(tool1)
        orchestrator.register_tool(tool2)
        
        task_context = {
            "task_type": "build",
            "tool_types": ["build_tool"],
            "performance": {"priority": "speed"}
        }
        
        result = orchestrator.intelligent_tool_selection(
            task_context, ExecutionStrategy.PERFORMANCE_OPTIMIZED
        )
        
        # Should select faster tool for performance-optimized strategy
        assert result["selected_tool_id"] in ["fast_tool", "slow_tool"]
        assert len(result["alternative_tools"]) >= 1
        
    def test_tool_selection_no_candidates(self, orchestrator):
        """Test tool selection when no suitable tools available"""
        task_context = {
            "task_type": "nonexistent",
            "tool_types": ["nonexistent_tool"]
        }
        
        result = orchestrator.intelligent_tool_selection(task_context)
        
        assert "error" in result
        assert "fallback_recommendation" in result
        
    def test_decision_framework_criteria_weighting(self, orchestrator, sample_tool_definition):
        """Test that decision framework applies correct criteria weighting"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Modify tool metrics to test scoring
        metrics = orchestrator.tool_metrics["test_tool"]
        metrics.success_rate = 0.9
        metrics.systematic_compliance_rate = 0.95
        metrics.availability_percentage = 98.0
        
        task_context = {"task_type": "build", "tool_types": ["build_tool"]}
        
        result = orchestrator.intelligent_tool_selection(task_context)
        
        assert result["decision_confidence"] > 0.8  # Should be high with good metrics

class TestSystematicToolExecution:
    """Test systematic tool execution (UC-13)"""
    
    @patch('subprocess.run')
    def test_successful_tool_execution(self, mock_subprocess, orchestrator, 
                                     sample_tool_definition, sample_execution_request):
        """Test successful systematic tool execution"""
        # Setup
        orchestrator.register_tool(sample_tool_definition)
        
        mock_subprocess.return_value = Mock(
            stdout="test output",
            stderr="",
            returncode=0
        )
        
        # Execute
        result = orchestrator.execute_tool_systematically(sample_execution_request)
        
        # Verify
        assert result.status == "success"
        assert result.output == "test output"
        assert result.systematic_compliance is True
        assert result.exit_code == 0
        assert result.execution_time_ms > 0
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert "echo test" in call_args[0][0]
        
    @patch('subprocess.run')
    def test_failed_tool_execution(self, mock_subprocess, orchestrator,
                                 sample_tool_definition, sample_execution_request):
        """Test failed tool execution handling"""
        orchestrator.register_tool(sample_tool_definition)
        
        mock_subprocess.return_value = Mock(
            stdout="",
            stderr="command failed",
            returncode=1
        )
        
        result = orchestrator.execute_tool_systematically(sample_execution_request)
        
        assert result.status == "error"
        assert result.error_output == "command failed"
        assert result.exit_code == 1
        assert len(result.recommendations) > 0
        
    def test_execution_constraint_validation(self, orchestrator, sample_tool_definition):
        """Test systematic constraint validation during execution"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Create request with systematic-only strategy
        request = ToolExecutionRequest(
            request_id=str(uuid.uuid4()),
            tool_id="test_tool",
            parameters={"message": "test"},
            execution_strategy=ExecutionStrategy.SYSTEMATIC_ONLY,
            context={}
        )
        
        # Should validate constraints before execution
        validation = orchestrator._validate_execution_constraints(
            sample_tool_definition, request.parameters, request.execution_strategy
        )
        
        assert validation["valid"] is True
        assert validation["systematic_compliance"] is True
        assert len(validation["violations"]) == 0
        
    def test_execution_unregistered_tool(self, orchestrator, sample_execution_request):
        """Test execution of unregistered tool"""
        result = orchestrator.execute_tool_systematically(sample_execution_request)
        
        assert result.status == "error"
        assert "not registered" in result.error_output
        assert result.systematic_compliance is False
        
    @patch('subprocess.run')
    def test_execution_timeout_handling(self, mock_subprocess, orchestrator,
                                      sample_tool_definition, sample_execution_request):
        """Test timeout handling during execution"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Simulate timeout
        import subprocess
        mock_subprocess.side_effect = subprocess.TimeoutExpired("echo test", 30)
        
        result = orchestrator.execute_tool_systematically(sample_execution_request)
        
        assert result.status == "error"
        assert "timed out" in result.error_output
        assert result.exit_code == -1

class TestToolHealthMonitoring:
    """Test tool health monitoring (UC-14)"""
    
    @patch('subprocess.run')
    def test_tool_health_check_success(self, mock_subprocess, orchestrator, sample_tool_definition):
        """Test successful tool health check"""
        orchestrator.register_tool(sample_tool_definition)
        
        mock_subprocess.return_value = Mock(
            stdout="healthy",
            stderr="",
            returncode=0
        )
        
        result = orchestrator.monitor_tool_health("test_tool")
        
        assert result["health_status"]["status"] == "healthy"
        assert result["systematic_compliance"] is True
        assert orchestrator.tool_status["test_tool"] == ToolStatus.AVAILABLE
        
    @patch('subprocess.run')
    def test_tool_health_check_failure(self, mock_subprocess, orchestrator, sample_tool_definition):
        """Test failed tool health check"""
        orchestrator.register_tool(sample_tool_definition)
        
        mock_subprocess.return_value = Mock(
            stdout="",
            stderr="tool not found",
            returncode=1
        )
        
        result = orchestrator.monitor_tool_health("test_tool")
        
        assert result["health_status"]["status"] == "degraded"
        assert result["systematic_compliance"] is False
        assert orchestrator.tool_status["test_tool"] == ToolStatus.DEGRADED
        
    def test_overall_health_monitoring(self, orchestrator, sample_tool_definition):
        """Test overall health monitoring across all tools"""
        orchestrator.register_tool(sample_tool_definition)
        
        result = orchestrator.monitor_tool_health()
        
        assert "overall_health" in result
        assert "health_summary" in result
        assert "systematic_compliance_overview" in result
        assert "monitoring_recommendations" in result
        
    def test_health_metrics_tracking(self, orchestrator, sample_tool_definition, sample_execution_request):
        """Test that health metrics are properly tracked"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Simulate some executions to update metrics
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(stdout="ok", stderr="", returncode=0)
            
            # Execute multiple times
            for i in range(3):
                request = ToolExecutionRequest(
                    request_id=str(uuid.uuid4()),
                    tool_id="test_tool",
                    parameters={"message": f"test{i}"},
                    execution_strategy=ExecutionStrategy.SYSTEMATIC_ONLY,
                    context={}
                )
                orchestrator.execute_tool_systematically(request)
                
        # Check metrics were updated
        metrics = orchestrator.tool_metrics["test_tool"]
        assert metrics.success_rate > 0.9  # Should be high for successful executions
        assert metrics.systematic_compliance_rate > 0.9

class TestToolPerformanceOptimization:
    """Test tool performance optimization (UC-15)"""
    
    def test_performance_optimization_execution(self, orchestrator, sample_tool_definition):
        """Test performance optimization execution"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Set up metrics that need optimization
        metrics = orchestrator.tool_metrics["test_tool"]
        metrics.average_execution_time_ms = 10000  # Slow
        metrics.systematic_compliance_rate = 0.7   # Low compliance
        
        optimization_context = {
            "target_performance_improvement": 20,
            "maintain_systematic_compliance": True
        }
        
        result = orchestrator.optimize_tool_performance(optimization_context)
        
        assert "optimization_applied" in result
        assert "performance_improvements" in result
        assert "systematic_compliance_maintained" in result
        assert "bottleneck_analysis" in result
        
    def test_optimization_opportunity_identification(self, orchestrator, sample_tool_definition):
        """Test identification of optimization opportunities"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Create performance analysis data
        performance_analysis = orchestrator._analyze_performance_patterns()
        
        opportunities = orchestrator._identify_optimization_opportunities(
            performance_analysis, {"focus": "performance"}
        )
        
        assert isinstance(opportunities, list)
        # Should identify opportunities based on performance patterns
        
    def test_systematic_compliance_optimization(self, orchestrator, sample_tool_definition):
        """Test systematic compliance optimization"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Simulate low compliance
        metrics = orchestrator.tool_metrics["test_tool"]
        metrics.systematic_compliance_rate = 0.6
        
        # Apply compliance optimization
        result = orchestrator._improve_tool_compliance("test_tool", {"target_compliance": 0.9})
        
        assert result["success"] is True
        assert result["optimization_type"] == "compliance_improvement"
        assert result["new_compliance_rate"] > 0.6
        
    def test_performance_tuning_optimization(self, orchestrator, sample_tool_definition):
        """Test performance tuning optimization"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Simulate slow performance
        metrics = orchestrator.tool_metrics["test_tool"]
        metrics.average_execution_time_ms = 15000
        
        # Apply performance optimization
        result = orchestrator._optimize_tool_performance("test_tool", {"target_reduction_ms": 3000})
        
        assert result["success"] is True
        assert result["optimization_type"] == "performance_tuning"
        assert result["improvement_ms"] > 0
        assert result["new_average_time_ms"] < 15000

class TestOrchestrationAnalytics:
    """Test orchestration analytics and reporting"""
    
    def test_orchestration_analytics_generation(self, orchestrator, sample_tool_definition):
        """Test comprehensive orchestration analytics"""
        orchestrator.register_tool(sample_tool_definition)
        
        analytics = orchestrator.get_orchestration_analytics()
        
        # Verify all required sections are present
        assert "execution_analytics" in analytics
        assert "decision_framework_effectiveness" in analytics
        assert "tool_usage_patterns" in analytics
        assert "optimization_impact" in analytics
        assert "health_monitoring_insights" in analytics
        
        # Verify execution analytics
        exec_analytics = analytics["execution_analytics"]
        assert "total_executions" in exec_analytics
        assert "success_rate" in exec_analytics
        assert "systematic_compliance_rate" in exec_analytics
        
    def test_tool_usage_pattern_analysis(self, orchestrator, sample_tool_definition):
        """Test tool usage pattern analysis"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Get usage patterns
        most_used = orchestrator._get_most_used_tools()
        performance_ranking = orchestrator._rank_tools_by_performance()
        usage_trends = orchestrator._analyze_usage_trends()
        
        assert isinstance(most_used, list)
        assert isinstance(performance_ranking, list)
        assert isinstance(usage_trends, dict)
        
        if most_used:
            assert "tool_id" in most_used[0]
            assert "usage_count" in most_used[0]
            
    def test_failure_pattern_analysis(self, orchestrator, sample_tool_definition):
        """Test failure pattern analysis"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Add some error patterns
        metrics = orchestrator.tool_metrics["test_tool"]
        metrics.error_patterns = ["timeout error", "permission denied", "file not found"]
        
        failure_analysis = orchestrator._analyze_failure_patterns()
        
        assert "common_failure_types" in failure_analysis
        assert "failure_frequency" in failure_analysis
        assert "prevention_recommendations" in failure_analysis
        
        # Should identify common failure types
        assert len(failure_analysis["common_failure_types"]) > 0
        
    def test_maintenance_recommendations(self, orchestrator, sample_tool_definition):
        """Test maintenance recommendation generation"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Set up conditions that need maintenance
        metrics = orchestrator.tool_metrics["test_tool"]
        metrics.success_rate = 0.7  # Low success rate
        metrics.performance_trend = "degrading"
        metrics.last_health_check = datetime.now() - timedelta(hours=2)  # Overdue
        
        recommendations = orchestrator._generate_maintenance_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should recommend maintenance for low success rate
        maintenance_needed = any("maintenance" in rec.lower() for rec in recommendations)
        assert maintenance_needed

class TestOrchestrationIntegration:
    """Test integration between orchestration components"""
    
    def test_end_to_end_tool_workflow(self, orchestrator, sample_tool_definition):
        """Test complete workflow from selection to execution to monitoring"""
        # Register tool
        orchestrator.register_tool(sample_tool_definition)
        
        # Select tool
        task_context = {"task_type": "build", "tool_types": ["build_tool"]}
        selection_result = orchestrator.intelligent_tool_selection(task_context)
        
        assert selection_result["selected_tool_id"] == "test_tool"
        
        # Execute tool
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(stdout="success", stderr="", returncode=0)
            
            request = ToolExecutionRequest(
                request_id=str(uuid.uuid4()),
                tool_id=selection_result["selected_tool_id"],
                parameters={"message": "test"},
                execution_strategy=ExecutionStrategy.SYSTEMATIC_ONLY,
                context=task_context
            )
            
            execution_result = orchestrator.execute_tool_systematically(request)
            
        assert execution_result.status == "success"
        
        # Monitor health
        health_result = orchestrator.monitor_tool_health("test_tool")
        assert health_result["health_status"]["status"] in ["healthy", "unknown"]
        
    def test_orchestrator_module_status(self, orchestrator):
        """Test orchestrator module status reporting"""
        status = orchestrator.get_module_status()
        
        assert status["module_name"] == "tool_orchestrator"
        assert "status" in status
        assert "registered_tools" in status
        assert "total_executions" in status
        assert "success_rate" in status
        
    def test_orchestrator_health_indicators(self, orchestrator):
        """Test orchestrator health indicators"""
        health = orchestrator.get_health_indicators()
        
        assert "tool_availability" in health
        assert "component_health" in health
        assert "performance_metrics" in health
        assert "tool_health_summary" in health
        
    def test_orchestrator_degradation_handling(self, orchestrator, sample_tool_definition):
        """Test orchestrator behavior under degraded conditions"""
        orchestrator.register_tool(sample_tool_definition)
        
        # Simulate tool failure
        orchestrator.tool_status["test_tool"] = ToolStatus.FAILED
        
        # Should still be able to provide status
        status = orchestrator.get_module_status()
        assert status["status"] == "degraded"
        
        # Should handle failed tool in selection
        task_context = {"task_type": "build", "tool_types": ["build_tool"]}
        result = orchestrator.intelligent_tool_selection(task_context)
        
        # Should provide fallback or error
        assert "error" in result or "selected_tool_id" in result

if __name__ == "__main__":
    pytest.main([__file__])