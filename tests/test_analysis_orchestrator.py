"""
Tests for AnalysisOrchestratorRM

OPERATOR SAFETY: All tests validate safety guarantees and read-only operations
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import tempfile
from pathlib import Path

from src.beast_mode.analysis.rm_rdi.orchestrator import AnalysisOrchestratorRM, AnalysisWorkflow, WorkflowResult
from src.beast_mode.analysis.rm_rdi.base import BaseAnalyzer, SafetyViolationError
from src.beast_mode.analysis.rm_rdi.data_models import AnalysisResult, AnalysisStatus
from src.beast_mode.analysis.rm_rdi.workflow import AggregatedResult


class MockAnalyzer(BaseAnalyzer):
    """Mock analyzer for testing"""
    
    def __init__(self, name: str, should_fail: bool = False):
        super().__init__(name)
        self.should_fail = should_fail
        self.execution_count = 0
        
    def _execute_analysis(self, **kwargs) -> AnalysisResult:
        """Mock analysis execution"""
        self.execution_count += 1
        
        if self.should_fail:
            raise Exception(f"Mock failure in {self.analyzer_name}")
            
        return AnalysisResult(
            analysis_id=f"mock_{self.analyzer_name}_{self.execution_count}",
            timestamp=datetime.now(),
            analysis_types=[self.analyzer_name],
            status=AnalysisStatus.SUCCESS,
            findings=[f"Mock finding from {self.analyzer_name}"],
            metrics={"mock_metric": 42},
            recommendations=[f"Mock recommendation from {self.analyzer_name}"],
            safety_validated=True,
            emergency_shutdown_available=True,
            can_be_safely_ignored=True
        )


class TestAnalysisOrchestratorRM:
    """Test suite for AnalysisOrchestratorRM"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return AnalysisOrchestratorRM()
        
    @pytest.fixture
    def mock_analyzers(self):
        """Create mock analyzers for testing"""
        return {
            "analyzer1": MockAnalyzer("analyzer1"),
            "analyzer2": MockAnalyzer("analyzer2"),
            "failing_analyzer": MockAnalyzer("failing_analyzer", should_fail=True)
        }
        
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes with safety guarantees"""
        # Check basic initialization
        assert orchestrator.orchestrator_name == "analysis_orchestrator"
        assert orchestrator.module_name == "rm_rdi_orchestrator_analysis_orchestrator"
        
        # Check safety systems
        assert orchestrator.safety_manager is not None
        assert hasattr(orchestrator, 'workflow_coordinator')
        assert hasattr(orchestrator, 'workflow_executor')
        
        # Check status
        status = orchestrator.get_module_status()
        assert status["orchestrator_name"] == "analysis_orchestrator"
        assert "safety_status" in status
        assert "guarantees" in status
        
    def test_orchestrator_health_check(self, orchestrator):
        """Test orchestrator health checking"""
        # Should be healthy initially
        assert orchestrator.is_healthy()
        
        # Get health indicators
        health = orchestrator.get_health_indicators()
        assert "orchestrator_health" in health
        assert "safety_health" in health
        assert "analyzer_health" in health
        
    def test_analyzer_registration(self, orchestrator, mock_analyzers):
        """Test analyzer registration with safety validation"""
        analyzer = mock_analyzers["analyzer1"]
        
        # Register analyzer
        orchestrator.register_analyzer(analyzer)
        
        # Verify registration
        assert "analyzer1" in orchestrator.registered_analyzers
        assert orchestrator.registered_analyzers["analyzer1"] == analyzer
        
        # Check status includes registered analyzer
        status = orchestrator.get_module_status()
        assert "analyzer1" in status["registered_analyzers"]
        
    def test_analyzer_registration_validation(self, orchestrator):
        """Test analyzer registration validates input"""
        # Try to register invalid object
        with pytest.raises(ValueError, match="Only BaseAnalyzer instances"):
            orchestrator.register_analyzer("not_an_analyzer")
            
    def test_parameter_configuration_safety(self, orchestrator):
        """Test parameter configuration enforces safety"""
        # Safe parameters should work
        orchestrator.configure_analysis_parameters(
            timeout=300,
            max_files=1000,
            analysis_type="readonly"
        )
        
        # Unsafe parameters should be rejected
        with pytest.raises(SafetyViolationError, match="Unsafe parameter"):
            orchestrator.configure_analysis_parameters(write_mode=True)
            
        with pytest.raises(SafetyViolationError, match="Unsafe value"):
            orchestrator.configure_analysis_parameters(operation="delete_files")
            
    def test_workflow_creation(self, orchestrator, mock_analyzers):
        """Test workflow creation with safety validation"""
        # Register analyzers
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create workflow
        workflow = orchestrator.create_analysis_workflow(
            workflow_id="test_workflow",
            analyzer_names=["analyzer1", "analyzer2"],
            parallel_execution=True,
            timeout_seconds=300
        )
        
        # Verify workflow
        assert workflow.workflow_id == "test_workflow"
        assert workflow.analyzer_names == ["analyzer1", "analyzer2"]
        assert workflow.parallel_execution is True
        assert workflow.timeout_seconds == 300
        
        # Check workflow is tracked
        assert "test_workflow" in orchestrator.active_workflows
        
    def test_workflow_creation_validation(self, orchestrator):
        """Test workflow creation validates inputs"""
        # Missing analyzers should fail
        with pytest.raises(ValueError, match="Analyzers not registered"):
            orchestrator.create_analysis_workflow(
                workflow_id="invalid_workflow",
                analyzer_names=["nonexistent_analyzer"]
            )
            
        # Excessive timeout should fail
        with pytest.raises(SafetyViolationError, match="Timeout too long"):
            orchestrator.create_analysis_workflow(
                workflow_id="timeout_workflow",
                analyzer_names=[],
                timeout_seconds=3600  # 1 hour
            )
            
    def test_workflow_execution_parallel(self, orchestrator, mock_analyzers):
        """Test parallel workflow execution"""
        # Register analyzers
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create and execute workflow
        orchestrator.create_analysis_workflow(
            workflow_id="parallel_test",
            analyzer_names=["analyzer1", "analyzer2"],
            parallel_execution=True
        )
        
        result = orchestrator.execute_workflow("parallel_test")
        
        # Verify result
        assert isinstance(result, WorkflowResult)
        assert result.workflow_id == "parallel_test"
        assert result.status == AnalysisStatus.SUCCESS
        assert len(result.results) == 2
        assert "analyzer1" in result.results
        assert "analyzer2" in result.results
        assert result.safety_validated is True
        assert result.emergency_shutdown_available is True
        
    def test_workflow_execution_sequential(self, orchestrator, mock_analyzers):
        """Test sequential workflow execution"""
        # Register analyzers
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create and execute workflow
        orchestrator.create_analysis_workflow(
            workflow_id="sequential_test",
            analyzer_names=["analyzer1", "analyzer2"],
            parallel_execution=False
        )
        
        result = orchestrator.execute_workflow("sequential_test")
        
        # Verify result
        assert result.status == AnalysisStatus.SUCCESS
        assert len(result.results) == 2
        
    def test_workflow_execution_with_failure(self, orchestrator, mock_analyzers):
        """Test workflow execution handles failures gracefully"""
        # Register analyzers including failing one
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create and execute workflow with failing analyzer
        orchestrator.create_analysis_workflow(
            workflow_id="failure_test",
            analyzer_names=["analyzer1", "failing_analyzer"],
            parallel_execution=True
        )
        
        result = orchestrator.execute_workflow("failure_test")
        
        # Should have partial success
        assert result.status == AnalysisStatus.PARTIAL_SUCCESS
        assert len(result.results) == 1  # Only successful analyzer
        assert len(result.errors) > 0
        assert result.safety_validated is True
        
    def test_coordinated_workflow_creation(self, orchestrator, mock_analyzers):
        """Test coordinated workflow with dependencies"""
        # Register analyzers
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create coordinated workflow
        analyzer_configs = [
            {
                "analyzer_name": "analyzer1",
                "parameters": {"param1": "value1"},
                "dependencies": []
            },
            {
                "analyzer_name": "analyzer2", 
                "parameters": {"param2": "value2"},
                "dependencies": ["test_workflow_step_0"]  # Depends on first step
            }
        ]
        
        workflow_plan = orchestrator.create_coordinated_workflow(
            workflow_id="coordinated_test",
            analyzer_configs=analyzer_configs,
            aggregation_strategy="merge"
        )
        
        # Verify workflow plan
        assert workflow_plan["workflow_id"] == "coordinated_test"
        assert len(workflow_plan["steps"]) == 2
        assert workflow_plan["aggregation_strategy"] == "merge"
        
    def test_coordinated_workflow_execution(self, orchestrator, mock_analyzers):
        """Test coordinated workflow execution with result aggregation"""
        # Register analyzers
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create and execute coordinated workflow
        analyzer_configs = [
            {"analyzer_name": "analyzer1", "dependencies": []},
            {"analyzer_name": "analyzer2", "dependencies": []}
        ]
        
        orchestrator.create_coordinated_workflow(
            workflow_id="aggregation_test",
            analyzer_configs=analyzer_configs
        )
        
        result = orchestrator.execute_coordinated_workflow("aggregation_test")
        
        # Verify aggregated result
        assert isinstance(result, AggregatedResult)
        assert result.workflow_id == "aggregation_test"
        assert result.overall_status == AnalysisStatus.SUCCESS
        assert len(result.step_results) == 2
        assert result.safety_validated is True
        
    def test_workflow_status_tracking(self, orchestrator, mock_analyzers):
        """Test workflow status tracking"""
        # Register analyzer
        orchestrator.register_analyzer(mock_analyzers["analyzer1"])
        
        # Create workflow
        orchestrator.create_analysis_workflow(
            workflow_id="status_test",
            analyzer_names=["analyzer1"]
        )
        
        # Check active status
        status = orchestrator.get_workflow_status("status_test")
        assert status["status"] == "active"
        assert status["workflow_id"] == "status_test"
        
        # Execute workflow
        orchestrator.execute_workflow("status_test")
        
        # Check completed status
        status = orchestrator.get_workflow_status("status_test")
        assert status["status"] == "completed"
        
    def test_workflow_listing(self, orchestrator, mock_analyzers):
        """Test workflow listing functionality"""
        # Register analyzer
        orchestrator.register_analyzer(mock_analyzers["analyzer1"])
        
        # Initially no workflows
        workflows = orchestrator.list_workflows()
        assert len(workflows["active_workflows"]) == 0
        assert len(workflows["completed_workflows"]) == 0
        
        # Create workflow
        orchestrator.create_analysis_workflow(
            workflow_id="list_test",
            analyzer_names=["analyzer1"]
        )
        
        # Should show active workflow
        workflows = orchestrator.list_workflows()
        assert len(workflows["active_workflows"]) == 1
        assert "list_test" in workflows["active_workflows"]
        
        # Execute workflow
        orchestrator.execute_workflow("list_test")
        
        # Should show completed workflow
        workflows = orchestrator.list_workflows()
        assert len(workflows["active_workflows"]) == 0
        assert len(workflows["completed_workflows"]) == 1
        assert "list_test" in workflows["completed_workflows"]
        
    def test_configuration_management(self, orchestrator):
        """Test analysis configuration management"""
        # Configure thresholds
        orchestrator.configure_analysis_thresholds(
            max_file_size=1000,
            complexity_threshold=10.0,
            coverage_minimum=0.8
        )
        
        # Get configuration
        config = orchestrator.get_analysis_configuration()
        assert "default_config" in config
        assert config["default_config"]["analysis_thresholds"]["max_file_size"] == 1000
        
    def test_analyzer_validation(self, orchestrator, mock_analyzers):
        """Test analyzer configuration validation"""
        # Register analyzer
        orchestrator.register_analyzer(mock_analyzers["analyzer1"])
        
        # Validate registered analyzer
        validation = orchestrator.validate_analyzer_configuration("analyzer1")
        assert validation["is_valid"] is True
        assert validation["is_healthy"] is True
        assert validation["safety_validated"] is True
        
        # Validate non-existent analyzer
        validation = orchestrator.validate_analyzer_configuration("nonexistent")
        assert validation["is_valid"] is False
        assert "not registered" in validation["error"]
        
    def test_cleanup_old_results(self, orchestrator, mock_analyzers):
        """Test cleanup of old workflow results"""
        # Register analyzer
        orchestrator.register_analyzer(mock_analyzers["analyzer1"])
        
        # Create workflow with timestamp in ID
        old_timestamp = int((datetime.now() - timedelta(days=2)).timestamp())
        workflow_id = f"old_workflow_{old_timestamp}"
        
        orchestrator.create_analysis_workflow(
            workflow_id=workflow_id,
            analyzer_names=["analyzer1"]
        )
        
        # Execute workflow
        orchestrator.execute_workflow(workflow_id)
        
        # Should have result
        assert workflow_id in orchestrator.workflow_results
        
        # Cleanup old results (max age 1 hour)
        cleaned = orchestrator.cleanup_old_results(max_age_hours=1)
        
        # Should have cleaned up the old result
        assert cleaned == 1
        assert workflow_id not in orchestrator.workflow_results
        
    def test_emergency_shutdown(self, orchestrator, mock_analyzers):
        """Test emergency shutdown functionality"""
        # Register analyzers
        for analyzer in mock_analyzers.values():
            orchestrator.register_analyzer(analyzer)
            
        # Create active workflow
        orchestrator.create_analysis_workflow(
            workflow_id="emergency_test",
            analyzer_names=["analyzer1"]
        )
        
        # Verify workflow is active
        assert "emergency_test" in orchestrator.active_workflows
        
        # Trigger emergency shutdown
        orchestrator.emergency_shutdown_all()
        
        # Verify shutdown
        assert len(orchestrator.active_workflows) == 0
        assert orchestrator.workflow_executor._shutdown
        
        # Verify analyzers were shutdown
        for analyzer in mock_analyzers.values():
            assert analyzer.safety_manager.emergency_shutdown_triggered
            
    def test_safety_violation_handling(self, orchestrator):
        """Test safety violation handling"""
        # Mock safety manager to trigger violation
        with patch.object(orchestrator.safety_manager, 'get_safety_status') as mock_status:
            mock_status.return_value.is_safe = False
            mock_status.return_value.violations = ["TEST_VIOLATION"]
            
            # Should not be healthy
            assert not orchestrator.is_healthy()
            
            # Should include violation in health indicators
            health = orchestrator.get_health_indicators()
            assert "TEST_VIOLATION" in health["safety_health"]["safety_violations"]
            
    def test_resource_monitoring(self, orchestrator):
        """Test resource usage monitoring"""
        # Get health indicators
        health = orchestrator.get_health_indicators()
        
        # Should include resource monitoring
        assert "safety_health" in health
        assert "resource_usage" in health["safety_health"]
        
        # Should include workflow performance metrics
        assert "workflow_health" in health
        assert "performance_metrics" in health["workflow_health"]
        
    def test_primary_responsibility(self, orchestrator):
        """Test primary responsibility reporting"""
        responsibility = orchestrator._get_primary_responsibility()
        assert responsibility == "safe_readonly_analysis_workflow_coordination"
        
        # Check single responsibility maintenance
        responsibility_check = orchestrator.maintain_single_responsibility()
        assert responsibility_check["primary_responsibility"] == responsibility
        assert responsibility_check["single_responsibility_score"] >= 0.8
        
    def test_read_only_operations_only(self, orchestrator, mock_analyzers):
        """Test that all operations are read-only"""
        # Register analyzer
        orchestrator.register_analyzer(mock_analyzers["analyzer1"])
        
        # Execute workflow
        orchestrator.create_analysis_workflow(
            workflow_id="readonly_test",
            analyzer_names=["analyzer1"]
        )
        
        result = orchestrator.execute_workflow("readonly_test")
        
        # Verify result guarantees read-only operations
        assert result.safety_validated is True
        assert result.emergency_shutdown_available is True
        
        # Verify analyzer result is also read-only
        analyzer_result = result.results["analyzer1"]
        assert analyzer_result.safety_validated is True
        assert analyzer_result.can_be_safely_ignored is True