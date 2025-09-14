"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.578701
"""




import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from beast_mode.core.model_registry import ModelRegistry
from beast_mode.core.pdca_models import (
    PDCATask, CheckResult, ActResult, Pattern, ValidationLevel,
    create_basic_task, calculate_systematic_score
)

# Import the test orchestrator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from test_pdca_integration import PDCAOrchestrator


class TestPDCAOrchestratorFixes:
    """Test suite for PDCA orchestrator critical fixes"""
    
    @pytest.fixture
    def model_registry(self):
        """Model registry instance for testing"""
        return ModelRegistry("project_model_registry.json")
    
    @pytest.fixture
    def orchestrator(self, model_registry):
        """PDCA orchestrator instance"""
        return PDCAOrchestrator(model_registry)
    
    @pytest.fixture
    def test_task(self):
        """Standard test task"""
        return create_basic_task(
            task_id="test-fix-001",
            description="Test systematic learning threshold fixes",
            domain="systematic_testing"
        )
    
    def test_learning_threshold_boundary_fix(self, orchestrator, test_task):
        """Test that 0.75+ scores generate learning patterns (Issue 1 & 3 fix)"""
        # Create a check result with exactly 0.75 systematic score
        check_result = CheckResult(
            task_id=test_task.task_id,
            validation_results={
                "requirements_met": True,
                "tests_pass": True,
                "code_quality": True,
                "systematic_compliance": True,
                "rm_pattern_implemented": True
            },
            systematic_score=0.75,  # Boundary case
            rca_findings=[],
            quality_metrics={"overall_quality": 7.5},
            validation_level=ValidationLevel.MEDIUM
        )
        
        # Execute ACT phase
        act_result = orchestrator._act_phase(test_task, check_result)
        
        # Should generate learning patterns with >= 0.75 threshold
        assert len(act_result.learning_patterns) > 0, "Should generate learning patterns for 0.75 score"
        
        pattern = act_result.learning_patterns[0]
        assert pattern.domain == test_task.domain
        assert pattern.confidence_score > 0.0
        assert "systematic_score" in pattern.success_metrics
        assert pattern.success_metrics["systematic_score"] == 0.75
    
    def test_learning_threshold_graduated_levels(self, orchestrator, test_task):
        """Test graduated learning thresholds work correctly"""
        test_scores = [0.74, 0.75, 0.85, 0.95]
        expected_patterns = [0, 1, 1, 1]  # Only 0.75+ should generate patterns
        
        for score, expected_count in zip(test_scores, expected_patterns):
            check_result = CheckResult(
                task_id=f"{test_task.task_id}-{score}",
                validation_results={"systematic_compliance": True},
                systematic_score=score,
                rca_findings=[],
                quality_metrics={"overall_quality": score * 10},
                validation_level=ValidationLevel.HIGH if score >= 0.9 else ValidationLevel.MEDIUM
            )
            
            act_result = orchestrator._act_phase(test_task, check_result)
            
            assert len(act_result.learning_patterns) == expected_count, \
                f"Score {score} should generate {expected_count} patterns, got {len(act_result.learning_patterns)}"
    
    def test_act_phase_scoring_decoupling(self, orchestrator, test_task):
        """Test ACT phase scoring is decoupled from learning pattern generation (Issue 5 fix)"""
        # Test case 1: High systematic score but no learning patterns generated
        check_result_high = CheckResult(
            task_id=test_task.task_id,
            validation_results={"systematic_compliance": True},
            systematic_score=0.74,  # Below learning threshold
            rca_findings=[],
            quality_metrics={"overall_quality": 7.4},
            validation_level=ValidationLevel.MEDIUM
        )
        
        act_result_high = orchestrator._act_phase(test_task, check_result_high)
        
        # Should have improvement recommendations even without learning patterns
        assert len(act_result_high.improvement_recommendations) > 0
        assert len(act_result_high.model_registry_updates) == 0  # No patterns to update
        
        # Test case 2: Calculate systematic score with ACT phase
        plan_result = Mock()
        plan_result.confidence_score = 0.8
        
        do_result = Mock()
        do_result.systematic_compliance = 0.8
        
        # ACT score should be based on improvement actions, not learning patterns
        systematic_score = orchestrator._calculate_systematic_score(
            plan_result, do_result, check_result_high, act_result_high
        )
        
        # Should be reasonable score despite no learning patterns
        assert systematic_score > 0.7, f"Systematic score {systematic_score} should not be penalized for no learning"
    
    def test_systematic_score_calculation_weighting(self, orchestrator):
        """Test systematic score calculation uses proper weighting (Issue 4 fix)"""
        # Create mock results
        plan_result = Mock()
        plan_result.confidence_score = 0.9
        
        do_result = Mock()
        do_result.systematic_compliance = 0.85
        
        check_result = Mock()
        check_result.systematic_score = 0.8
        
        act_result = Mock()
        act_result.improvement_recommendations = ["rec1", "rec2"]
        act_result.model_registry_updates = ["update1"]
        
        # Calculate systematic score
        systematic_score = orchestrator._calculate_systematic_score(
            plan_result, do_result, check_result, act_result
        )
        
        # Verify weighting: plan=0.25, do=0.35, check=0.25, act=0.15
        expected_act_score = min(1.0, 0.7 + (3 * 0.1))  # 3 improvement actions
        expected_score = (0.9 * 0.25) + (0.85 * 0.35) + (0.8 * 0.25) + (expected_act_score * 0.15)
        
        assert abs(systematic_score - expected_score) < 0.01, \
            f"Expected {expected_score}, got {systematic_score}"
    
    def test_systematic_superiority_achievement(self, orchestrator, model_registry):
        """Test that fixes achieve systematic superiority (0.8+ target)"""
        # Run multiple PDCA cycles to test systematic superiority
        test_tasks = [
            create_basic_task("superiority-001", "Test systematic approach 1", "testing"),
            create_basic_task("superiority-002", "Test systematic approach 2", "implementation"),
            create_basic_task("superiority-003", "Test systematic approach 3", "validation")
        ]
        
        results = []
        for task in test_tasks:
            result = orchestrator.execute_pdca_cycle(task)
            results.append(result)
        
        # Calculate average systematic score
        avg_systematic_score = sum(r.systematic_score for r in results) / len(results)
        
        # Should achieve systematic superiority
        assert avg_systematic_score >= 0.8, \
            f"Average systematic score {avg_systematic_score:.3f} should be >= 0.8 for superiority"
        
        # All individual scores should be reasonable
        for i, result in enumerate(results):
            assert result.systematic_score > 0.7, \
                f"Task {i+1} systematic score {result.systematic_score:.3f} should be > 0.7"
    
    def test_model_registry_learning_accumulation(self, orchestrator, model_registry):
        """Test that learning patterns accumulate correctly in model registry"""
        initial_stats = model_registry.get_registry_stats()
        initial_patterns = initial_stats.get("cached_intelligence", 0)
        
        # Execute a successful PDCA cycle
        task = create_basic_task("learning-001", "Test learning accumulation", "learning_test")
        result = orchestrator.execute_pdca_cycle(task)
        
        # Should have generated learning patterns
        assert len(result.act_result.learning_patterns) > 0
        
        # Model registry should have accumulated learning
        final_stats = model_registry.get_registry_stats()
        final_intelligence = final_stats.get("cached_intelligence", 0)
        
        assert final_intelligence > initial_patterns, \
            "Model registry should accumulate intelligence from learning patterns"
        
        # Check learning insights
        insights = model_registry.get_learning_insights()
        assert insights["total_patterns"] > 0
        assert insights["avg_confidence"] > 0.0
    
    def test_boundary_score_exact_values(self, orchestrator, test_task):
        """Test exact boundary values for learning thresholds"""
        boundary_scores = [0.749, 0.750, 0.799, 0.800, 0.849, 0.850, 0.949, 0.950]
        
        for score in boundary_scores:
            check_result = CheckResult(
                task_id=f"{test_task.task_id}-{score}",
                validation_results={"systematic_compliance": True},
                systematic_score=score,
                rca_findings=[],
                quality_metrics={"overall_quality": score * 10},
                validation_level=ValidationLevel.HIGH
            )
            
            act_result = orchestrator._act_phase(test_task, check_result)
            
            # Should generate patterns for >= 0.75
            expected_patterns = 1 if score >= 0.75 else 0
            actual_patterns = len(act_result.learning_patterns)
            
            assert actual_patterns == expected_patterns, \
                f"Score {score} should generate {expected_patterns} patterns, got {actual_patterns}"
    
    def test_improvement_factor_calculation(self, orchestrator, test_task):
        """Test improvement factor calculation is reasonable"""
        result = orchestrator.execute_pdca_cycle(test_task)
        
        # Improvement factor should be > 1.0 for systematic approach
        assert result.improvement_factor > 1.0, \
            f"Improvement factor {result.improvement_factor} should be > 1.0"
        
        # Should be reasonable (not too high)
        assert result.improvement_factor < 2.0, \
            f"Improvement factor {result.improvement_factor} should be realistic (< 2.0)"
        
        # Should correlate with systematic score
        expected_factor = 1.0 + (result.systematic_score - 0.5) * 0.5
        assert abs(result.improvement_factor - expected_factor) < 0.1, \
            f"Improvement factor should correlate with systematic score"
    
    def test_execution_summary_accuracy(self, orchestrator):
        """Test execution summary provides accurate metrics"""
        # Execute multiple cycles
        tasks = [
            create_basic_task(f"summary-{i}", f"Test task {i}", "summary_test")
            for i in range(3)
        ]
        
        for task in tasks:
            orchestrator.execute_pdca_cycle(task)
        
        summary = orchestrator.get_execution_summary()
        
        # Verify summary accuracy
        assert summary["total_executions"] == 3
        assert 0.0 <= summary["avg_systematic_score"] <= 1.0
        assert 0.0 <= summary["avg_success_rate"] <= 1.0
        assert summary["avg_improvement_factor"] > 1.0
        
        # Should achieve systematic superiority
        assert summary["systematic_superiority"] == True, \
            "Should achieve systematic superiority with fixed thresholds"
    
    def test_regression_prevention(self, orchestrator, test_task):
        """Test that fixes don't break existing functionality"""
        # Execute a complete PDCA cycle
        result = orchestrator.execute_pdca_cycle(test_task)
        
        # Verify all phases completed
        assert result.plan_result is not None
        assert result.do_result is not None
        assert result.check_result is not None
        assert result.act_result is not None
        
        # Verify result structure
        assert result.task_id == test_task.task_id
        assert result.cycle_duration > timedelta(0)
        assert 0.0 <= result.systematic_score <= 1.0
        assert 0.0 <= result.success_rate <= 1.0
        assert result.improvement_factor > 0.0
        
        # Verify timestamps
        assert result.created_at is not None
        assert result.plan_result.created_at is not None
        assert result.do_result.created_at is not None
        assert result.check_result.created_at is not None
        assert result.act_result.created_at is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])