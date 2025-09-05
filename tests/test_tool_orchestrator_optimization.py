"""
Unit tests for ToolOrchestrator optimization methods
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.beast_mode.orchestration.tool_orchestrator import ToolOrchestrator, ToolDefinition, ToolType


class TestToolOrchestratorOptimization:
    """Test ToolOrchestrator optimization methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.orchestrator = ToolOrchestrator()
        
        # Add some test tools
        self.orchestrator.registered_tools = {
            "test_tool_1": ToolDefinition(
                tool_id="test_tool_1",
                name="Test Tool 1",
                tool_type=ToolType.BUILD_TOOL,
                command_template="test command 1",
                systematic_constraints={
                    "no_ad_hoc_commands": True,
                    "systematic_error_handling": True
                },
                performance_profile={
                    "typical_execution_time_ms": 2000,
                    "success_rate": 0.95
                }
            ),
            "test_tool_2": ToolDefinition(
                tool_id="test_tool_2", 
                name="Test Tool 2",
                tool_type=ToolType.TEST_TOOL,
                command_template="test command 2",
                systematic_constraints={},  # Empty constraints to test compliance gaps
                performance_profile={
                    "typical_execution_time_ms": 8000,
                    "success_rate": 0.75
                }
            )
        }
        
        # Add some test metrics
        self.orchestrator.tool_metrics = {
            "test_tool_1": {
                "success_rate": 0.95,
                "average_execution_time_ms": 2000,
                "total_executions": 100
            },
            "test_tool_2": {
                "success_rate": 0.75,
                "average_execution_time_ms": 8000,
                "total_executions": 50
            }
        }
        
        # Set some orchestration metrics
        self.orchestrator.orchestration_metrics.update({
            'total_executions': 150,
            'successful_executions': 135,
            'systematic_compliance_rate': 0.8
        })
    
    def test_improve_tool_compliance_method_exists(self):
        """Test that _improve_tool_compliance method exists and is callable"""
        assert hasattr(self.orchestrator, '_improve_tool_compliance')
        assert callable(self.orchestrator._improve_tool_compliance)
    
    def test_optimize_tool_performance_method_exists(self):
        """Test that _optimize_tool_performance method exists and is callable"""
        assert hasattr(self.orchestrator, '_optimize_tool_performance')
        assert callable(self.orchestrator._optimize_tool_performance)
    
    def test_improve_tool_compliance_returns_expected_structure(self):
        """Test that _improve_tool_compliance returns expected data structure"""
        result = self.orchestrator._improve_tool_compliance()
        
        # Check required keys
        assert isinstance(result, dict)
        assert "compliance_score" in result
        assert "improvement_suggestions" in result
        assert "compliance_metrics" in result
        assert "systematic_compliance_rate" in result
        assert "tools_analyzed" in result
        assert "compliance_status" in result
        
        # Check data types
        assert isinstance(result["compliance_score"], float)
        assert isinstance(result["improvement_suggestions"], list)
        assert isinstance(result["compliance_metrics"], dict)
        assert isinstance(result["systematic_compliance_rate"], float)
        assert isinstance(result["tools_analyzed"], int)
        assert isinstance(result["compliance_status"], str)
    
    def test_optimize_tool_performance_returns_expected_structure(self):
        """Test that _optimize_tool_performance returns expected data structure"""
        result = self.orchestrator._optimize_tool_performance()
        
        # Check required keys
        assert isinstance(result, dict)
        assert "performance_score" in result
        assert "optimization_suggestions" in result
        assert "performance_metrics" in result
        assert "average_execution_time" in result
        assert "tools_optimized" in result
        assert "optimization_status" in result
        
        # Check data types
        assert isinstance(result["performance_score"], float)
        assert isinstance(result["optimization_suggestions"], list)
        assert isinstance(result["performance_metrics"], dict)
        assert isinstance(result["tools_optimized"], int)
        assert isinstance(result["optimization_status"], str)
    
    def test_compliance_score_calculation(self):
        """Test compliance score calculation logic"""
        result = self.orchestrator._improve_tool_compliance()
        
        # Should calculate compliance based on tools with systematic_constraints
        # test_tool_1 has constraints (compliant), test_tool_2 doesn't (non-compliant)
        # Expected: (1.0 + 0.0) / 2 = 0.5
        assert 0.4 <= result["compliance_score"] <= 0.6  # Allow some tolerance
        
        # Should analyze all registered tools
        assert result["tools_analyzed"] == 2
        
        # Should have improvement suggestions
        assert len(result["improvement_suggestions"]) > 0
    
    def test_performance_score_calculation(self):
        """Test performance score calculation logic"""
        result = self.orchestrator._optimize_tool_performance()
        
        # Should calculate performance based on success rate and execution time
        # test_tool_1: high success rate (0.95), fast execution (2000ms) = good performance
        # test_tool_2: lower success rate (0.75), slow execution (8000ms) = poor performance
        assert 0.0 <= result["performance_score"] <= 1.0
        
        # Should analyze all tools with metrics
        assert result["tools_optimized"] == 2
        
        # Should have optimization suggestions
        assert len(result["optimization_suggestions"]) > 0
    
    def test_compliance_improvement_suggestions(self):
        """Test that compliance improvement suggestions are relevant"""
        result = self.orchestrator._improve_tool_compliance()
        suggestions = result["improvement_suggestions"]
        
        # Should have suggestions for tools without systematic constraints
        assert any("Test Tool 2" in suggestion for suggestion in suggestions)
        
        # Should limit to reasonable number of suggestions
        assert len(suggestions) <= 5
    
    def test_performance_optimization_suggestions(self):
        """Test that performance optimization suggestions are relevant"""
        result = self.orchestrator._optimize_tool_performance()
        suggestions = result["optimization_suggestions"]
        
        # Should suggest improvements for tools with poor performance
        # test_tool_2 has low success rate and high execution time
        assert any("test_tool_2" in suggestion for suggestion in suggestions)
        
        # Should limit to reasonable number of suggestions
        assert len(suggestions) <= 5
    
    def test_compliance_metrics_accuracy(self):
        """Test that compliance metrics are accurate"""
        result = self.orchestrator._improve_tool_compliance()
        metrics = result["compliance_metrics"]
        
        assert metrics["total_tools"] == 2
        assert metrics["compliant_tools"] == 1  # Only test_tool_1 has systematic_constraints
        assert metrics["compliance_gaps"] == 1   # test_tool_2 lacks systematic_constraints
        assert metrics["systematic_compliance_rate"] == 0.8  # From orchestration_metrics
    
    def test_performance_metrics_accuracy(self):
        """Test that performance metrics are accurate"""
        result = self.orchestrator._optimize_tool_performance()
        metrics = result["performance_metrics"]
        
        assert metrics["total_executions"] == 150
        assert metrics["successful_executions"] == 135
        assert metrics["success_rate"] == 135 / 150  # 0.9
        assert metrics["tools_with_metrics"] == 2
    
    def test_compliance_status_determination(self):
        """Test compliance status determination logic"""
        # Test with high compliance score
        self.orchestrator.registered_tools = {
            "compliant_tool": ToolDefinition(
                tool_id="compliant_tool",
                name="Compliant Tool",
                tool_type=ToolType.BUILD_TOOL,
                command_template="compliant command",
                systematic_constraints={
                    "no_ad_hoc_commands": True,
                    "systematic_error_handling": True
                },
                performance_profile={
                    "typical_execution_time_ms": 1000,
                    "success_rate": 0.98
                }
            )
        }
        
        result = self.orchestrator._improve_tool_compliance()
        assert result["compliance_status"] == "improving"  # Score should be > 0.7
    
    def test_optimization_status_determination(self):
        """Test optimization status determination logic"""
        # Test with high performance metrics
        self.orchestrator.tool_metrics = {
            "fast_tool": {
                "success_rate": 0.98,
                "average_execution_time_ms": 500,
                "total_executions": 100
            }
        }
        
        result = self.orchestrator._optimize_tool_performance()
        assert result["optimization_status"] in ["optimized", "optimization_needed"]
    
    def test_empty_tools_handling(self):
        """Test handling of empty tools and metrics"""
        # Test with no registered tools
        empty_orchestrator = ToolOrchestrator()
        empty_orchestrator.registered_tools = {}
        empty_orchestrator.tool_metrics = {}
        
        compliance_result = empty_orchestrator._improve_tool_compliance()
        performance_result = empty_orchestrator._optimize_tool_performance()
        
        # Should handle empty state gracefully
        assert compliance_result["compliance_score"] == 0.0
        assert compliance_result["tools_analyzed"] == 0
        
        assert performance_result["performance_score"] == 0.8  # Default score
        assert performance_result["tools_optimized"] == 0
    
    def test_helper_methods_exist(self):
        """Test that helper methods exist and are callable"""
        helper_methods = [
            '_calculate_compliance_score',
            '_generate_compliance_improvements', 
            '_get_compliance_metrics',
            '_calculate_performance_score',
            '_generate_performance_optimizations',
            '_get_performance_metrics'
        ]
        
        for method_name in helper_methods:
            assert hasattr(self.orchestrator, method_name)
            assert callable(getattr(self.orchestrator, method_name))


class TestToolOrchestratorOptimizationIntegration:
    """Integration tests for ToolOrchestrator optimization methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.orchestrator = ToolOrchestrator()
    
    def test_optimization_methods_work_with_real_tools(self):
        """Test that optimization methods work with real tool definitions"""
        # The orchestrator should have default tools from initialization
        assert len(self.orchestrator.registered_tools) > 0
        
        # Both methods should work without errors
        compliance_result = self.orchestrator._improve_tool_compliance()
        performance_result = self.orchestrator._optimize_tool_performance()
        
        # Results should be valid
        assert isinstance(compliance_result, dict)
        assert isinstance(performance_result, dict)
        
        # Should have analyzed the default tools
        assert compliance_result["tools_analyzed"] > 0
        assert performance_result["tools_optimized"] >= 0  # May be 0 if no metrics yet
    
    def test_optimization_methods_integration_with_orchestration(self):
        """Test that optimization methods integrate properly with orchestration analytics"""
        # Get orchestration analytics which should include optimization data
        analytics = self.orchestrator.get_orchestration_analytics()
        
        # Should include optimization impact section
        assert "optimization_impact" in analytics
        optimization_impact = analytics["optimization_impact"]
        
        # Should have performance improvements tracking
        assert "performance_improvements" in optimization_impact
        assert "optimization_roi" in optimization_impact


if __name__ == "__main__":
    pytest.main([__file__, "-v"])