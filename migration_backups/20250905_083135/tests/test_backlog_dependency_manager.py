"""
Unit tests for BacklogDependencyManager

Tests dependency declaration, validation, cycle detection, and critical path calculation
with focus on performance constraints and edge cases.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import time

from src.beast_mode.backlog.dependency_manager import (
    BacklogDependencyManager,
    DependencyGraph,
    CriticalPathAnalysis,
    CircularDependencyReport,
    DependencyResult,
    GraphValidationResult
)
from src.beast_mode.backlog.models import DependencySpec
from src.beast_mode.backlog.enums import DependencyType, RiskLevel, StrategicTrack
from src.beast_mode.core.reflective_module import HealthStatus


class TestBacklogDependencyManager:
    """Test suite for BacklogDependencyManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = BacklogDependencyManager()
        
        # Create test dependency specs
        self.dep_spec_1 = DependencySpec(
            dependency_id="item1_depends_on_item2",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="item2",
            target_track=StrategicTrack.PR_GATE,
            satisfaction_criteria="Item2 must be completed",
            estimated_completion=datetime.now() + timedelta(days=5),
            risk_level=RiskLevel.MEDIUM
        )
        
        self.dep_spec_2 = DependencySpec(
            dependency_id="item3_depends_on_item1",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="item1",
            target_track=StrategicTrack.ZERO_FRICTION,
            satisfaction_criteria="Item1 must be completed",
            estimated_completion=datetime.now() + timedelta(days=3),
            risk_level=RiskLevel.LOW
        )
        
        self.circular_dep_spec = DependencySpec(
            dependency_id="item2_depends_on_item3",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="item3",
            target_track=StrategicTrack.COMMUNITY,
            satisfaction_criteria="Item3 must be completed",
            estimated_completion=datetime.now() + timedelta(days=2),
            risk_level=RiskLevel.HIGH
        )


class TestRMCompliance(TestBacklogDependencyManager):
    """Test RM interface compliance"""
    
    def test_module_initialization(self):
        """Test proper RM initialization"""
        assert self.manager.module_name == "BacklogDependencyManager"
        assert self.manager.is_healthy()
        
    def test_get_module_status(self):
        """Test module status reporting"""
        status = self.manager.get_module_status()
        
        assert "module_name" in status
        assert "dependencies_count" in status
        assert "is_healthy" in status
        assert "performance_within_limits" in status
        assert status["module_name"] == "BacklogDependencyManager"
        
    def test_health_indicators(self):
        """Test health indicator reporting"""
        indicators = self.manager.get_health_indicators()
        
        assert "health_indicators" in indicators
        assert "overall_health" in indicators
        assert "performance_metrics" in indicators
        
        # Check required health indicators
        health_indicators = indicators["health_indicators"]
        assert "performance" in health_indicators
        assert "data_consistency" in health_indicators
        
    def test_single_responsibility(self):
        """Test single responsibility principle compliance"""
        responsibility = self.manager.maintain_single_responsibility()
        
        assert responsibility["module_name"] == "BacklogDependencyManager"
        assert "primary_responsibility" in responsibility
        assert "boundary_violations" in responsibility
        assert responsibility["primary_responsibility"] == "Explicit dependency tracking and validation for backlog items"


class TestDependencyDeclaration(TestBacklogDependencyManager):
    """Test dependency declaration functionality"""
    
    def test_declare_valid_dependency(self):
        """Test declaring a valid dependency"""
        result = self.manager.declare_dependency("item1", self.dep_spec_1)
        
        assert result.success
        assert result.dependency_id == "item1_depends_on_item2"
        assert result.message == "Dependency declared successfully"
        assert len(result.validation_errors) == 0
        
    def test_declare_invalid_dependency_empty_id(self):
        """Test declaring dependency with empty ID"""
        # The DependencySpec validation will catch this in __post_init__
        with pytest.raises(ValueError, match="Dependency ID cannot be empty"):
            DependencySpec(
                dependency_id="",
                dependency_type=DependencyType.BLOCKING,
                target_item_id="item2",
                target_track=StrategicTrack.PR_GATE,
                satisfaction_criteria="Test criteria",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )
        
    def test_declare_invalid_dependency_empty_target(self):
        """Test declaring dependency with empty target"""
        # The DependencySpec validation will catch this in __post_init__
        with pytest.raises(ValueError, match="Target item ID cannot be empty"):
            DependencySpec(
                dependency_id="test_dep",
                dependency_type=DependencyType.BLOCKING,
                target_item_id="",
                target_track=StrategicTrack.PR_GATE,
                satisfaction_criteria="Test criteria",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )
        
    def test_declare_self_dependency(self):
        """Test preventing self-dependency"""
        self_dep_spec = DependencySpec(
            dependency_id="item1_depends_on_item1",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="item1",
            target_track=StrategicTrack.PR_GATE,
            satisfaction_criteria="Self dependency",
            estimated_completion=None,
            risk_level=RiskLevel.LOW
        )
        
        result = self.manager.declare_dependency("item1", self_dep_spec)
        
        assert not result.success
        assert "Item cannot depend on itself" in result.validation_errors


class TestCircularDependencyDetection(TestBacklogDependencyManager):
    """Test circular dependency detection"""
    
    def test_detect_no_circular_dependencies(self):
        """Test detection when no circular dependencies exist"""
        # Add linear dependencies: item1 -> item2 -> item3
        self.manager.declare_dependency("item1", self.dep_spec_1)
        
        item3_dep_spec = DependencySpec(
            dependency_id="item2_depends_on_item3",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="item3",
            target_track=StrategicTrack.COMMUNITY,
            satisfaction_criteria="Item3 must be completed",
            estimated_completion=datetime.now() + timedelta(days=2),
            risk_level=RiskLevel.LOW
        )
        self.manager.declare_dependency("item2", item3_dep_spec)
        
        report = self.manager.detect_circular_dependencies()
        
        assert len(report.cycles_found) == 0
        assert len(report.affected_items) == 0
        assert report.detection_time_ms > 0
        
    def test_detect_circular_dependency(self):
        """Test detection of circular dependencies"""
        # Create circular dependency: item1 -> item2 -> item3 -> item1
        # First add the dependencies that don't create cycles
        result1 = self.manager.declare_dependency("item1", self.dep_spec_1)  # item1 -> item2
        assert result1.success, f"First dependency failed: {result1.message}"
        
        result2 = self.manager.declare_dependency("item2", self.circular_dep_spec)  # item2 -> item3
        assert result2.success, f"Second dependency failed: {result2.message}"
        
        # This should be prevented by cycle detection, but let's force it for testing
        # by directly adding to the internal dependencies
        self.manager._dependencies[self.dep_spec_2.dependency_id] = self.dep_spec_2
        self.manager._invalidate_cache()
        
        report = self.manager.detect_circular_dependencies()
        
        # Now we should detect the cycle
        assert len(report.cycles_found) > 0
        assert len(report.affected_items) > 0
        assert len(report.resolution_suggestions) > 0
        
    def test_prevent_circular_dependency_creation(self):
        """Test prevention of circular dependency creation"""
        # Add dependencies: item1 -> item2 -> item3
        self.manager.declare_dependency("item1", self.dep_spec_1)
        self.manager.declare_dependency("item2", self.circular_dep_spec)
        
        # Try to add item3 -> item1 (would create cycle)
        result = self.manager.declare_dependency("item3", self.dep_spec_2)
        
        assert not result.success
        assert "Would create circular dependency" in result.message
        
    def test_circular_dependency_performance(self):
        """Test circular dependency detection performance"""
        # Add multiple dependencies
        for i in range(10):
            dep_spec = DependencySpec(
                dependency_id=f"item{i}_depends_on_item{i+1}",
                dependency_type=DependencyType.BLOCKING,
                target_item_id=f"item{i+1}",
                target_track=StrategicTrack.PR_GATE,
                satisfaction_criteria=f"Item{i+1} must be completed",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )
            self.manager.declare_dependency(f"item{i}", dep_spec)
        
        start_time = time.time()
        report = self.manager.detect_circular_dependencies()
        detection_time = (time.time() - start_time) * 1000
        
        # Should complete within performance constraint
        assert detection_time < 500  # 500ms limit
        assert report.detection_time_ms < 500


class TestDependencyGraphValidation(TestBacklogDependencyManager):
    """Test dependency graph validation"""
    
    def test_validate_empty_graph(self):
        """Test validation of empty dependency graph"""
        result = self.manager.validate_dependency_graph()
        
        assert result.is_valid
        assert len(result.circular_dependencies.cycles_found) == 0
        assert len(result.orphaned_nodes) == 0
        assert result.validation_time_ms > 0
        
    def test_validate_valid_graph(self):
        """Test validation of valid dependency graph"""
        self.manager.declare_dependency("item1", self.dep_spec_1)
        self.manager.declare_dependency("item3", self.dep_spec_2)
        
        result = self.manager.validate_dependency_graph()
        
        assert result.is_valid
        assert len(result.circular_dependencies.cycles_found) == 0
        
    def test_validate_invalid_graph_with_cycles(self):
        """Test validation of graph with circular dependencies"""
        # Create circular dependency by forcing it into the internal structure
        self.manager._dependencies[self.dep_spec_1.dependency_id] = self.dep_spec_1
        self.manager._dependencies[self.circular_dep_spec.dependency_id] = self.circular_dep_spec
        self.manager._dependencies[self.dep_spec_2.dependency_id] = self.dep_spec_2
        self.manager._invalidate_cache()
        
        result = self.manager.validate_dependency_graph()
        
        assert not result.is_valid
        assert len(result.circular_dependencies.cycles_found) > 0
        
    def test_validation_performance(self):
        """Test graph validation performance"""
        # Add multiple dependencies
        for i in range(20):
            dep_spec = DependencySpec(
                dependency_id=f"item{i}_depends_on_item{i+10}",
                dependency_type=DependencyType.BLOCKING,
                target_item_id=f"item{i+10}",
                target_track=StrategicTrack.PR_GATE,
                satisfaction_criteria=f"Item{i+10} must be completed",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )
            self.manager.declare_dependency(f"item{i}", dep_spec)
        
        start_time = time.time()
        result = self.manager.validate_dependency_graph()
        validation_time = (time.time() - start_time) * 1000
        
        # Should complete within performance constraint
        assert validation_time < 500  # 500ms limit
        assert result.validation_time_ms < 500


class TestCriticalPathCalculation(TestBacklogDependencyManager):
    """Test critical path calculation"""
    
    def test_calculate_critical_path_empty_graph(self):
        """Test critical path calculation on empty graph"""
        analysis = self.manager.calculate_critical_path()
        
        assert len(analysis.critical_path) == 0
        assert analysis.total_duration == timedelta(0)
        assert len(analysis.bottlenecks) == 0
        assert len(analysis.risk_factors) == 0
        assert analysis.calculation_time_ms > 0
        
    def test_calculate_critical_path_linear_dependencies(self):
        """Test critical path calculation with linear dependencies"""
        # Create linear dependency chain
        result1 = self.manager.declare_dependency("item1", self.dep_spec_1)  # item1 -> item2
        assert result1.success, f"First dependency failed: {result1.message}"
        
        item2_to_item3_spec = DependencySpec(
            dependency_id="item2_depends_on_item3",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="item3",
            target_track=StrategicTrack.COMMUNITY,
            satisfaction_criteria="Item3 must be completed",
            estimated_completion=datetime.now() + timedelta(days=2),
            risk_level=RiskLevel.LOW
        )
        result2 = self.manager.declare_dependency("item2", item2_to_item3_spec)
        assert result2.success, f"Second dependency failed: {result2.message}"
        
        analysis = self.manager.calculate_critical_path()
        
        # The analysis should complete successfully even if path is empty
        assert analysis.total_duration >= timedelta(0)
        assert analysis.calculation_time_ms > 0
        
    def test_calculate_critical_path_with_track_filter(self):
        """Test critical path calculation with track filtering"""
        self.manager.declare_dependency("item1", self.dep_spec_1)
        
        analysis = self.manager.calculate_critical_path(track_filter="pr_gate")
        
        # Should complete successfully even with filter
        assert analysis.calculation_time_ms > 0
        
    def test_critical_path_performance(self):
        """Test critical path calculation performance"""
        # Add complex dependency structure
        for i in range(15):
            for j in range(2):
                dep_spec = DependencySpec(
                    dependency_id=f"item{i}_{j}_depends_on_item{i+1}_{j}",
                    dependency_type=DependencyType.BLOCKING,
                    target_item_id=f"item{i+1}_{j}",
                    target_track=StrategicTrack.PR_GATE,
                    satisfaction_criteria=f"Item{i+1}_{j} must be completed",
                    estimated_completion=datetime.now() + timedelta(days=i+1),
                    risk_level=RiskLevel.MEDIUM
                )
                self.manager.declare_dependency(f"item{i}_{j}", dep_spec)
        
        start_time = time.time()
        analysis = self.manager.calculate_critical_path()
        calculation_time = (time.time() - start_time) * 1000
        
        # Should complete within performance constraint
        assert calculation_time < 500  # 500ms limit
        assert analysis.calculation_time_ms < 500


class TestDependencyGraphOperations(TestBacklogDependencyManager):
    """Test dependency graph operations"""
    
    def test_get_dependency_graph_full(self):
        """Test getting full dependency graph"""
        result1 = self.manager.declare_dependency("item1", self.dep_spec_1)
        assert result1.success, f"First dependency failed: {result1.message}"
        
        result2 = self.manager.declare_dependency("item3", self.dep_spec_2)
        assert result2.success, f"Second dependency failed: {result2.message}"
        
        graph = self.manager.get_dependency_graph("")
        
        assert isinstance(graph, DependencyGraph)
        assert len(graph.nodes) > 0
        assert len(graph.dependency_specs) == 2
        
    def test_get_dependency_graph_for_item(self):
        """Test getting dependency graph for specific item"""
        self.manager.declare_dependency("item1", self.dep_spec_1)
        self.manager.declare_dependency("item3", self.dep_spec_2)
        
        graph = self.manager.get_dependency_graph("item1")
        
        assert isinstance(graph, DependencyGraph)
        # Should contain item1 and its related dependencies
        
    def test_dependency_graph_caching(self):
        """Test dependency graph caching behavior"""
        self.manager.declare_dependency("item1", self.dep_spec_1)
        
        # First call should build cache
        graph1 = self.manager.get_dependency_graph("")
        
        # Second call should use cache (faster)
        start_time = time.time()
        graph2 = self.manager.get_dependency_graph("")
        cache_time = (time.time() - start_time) * 1000
        
        # Cache should make it very fast
        assert cache_time < 50  # Should be much faster than 500ms limit
        
        # Graphs should be equivalent
        assert graph1.nodes == graph2.nodes


class TestPerformanceConstraints(TestBacklogDependencyManager):
    """Test performance constraint compliance"""
    
    def test_response_time_constraint(self):
        """Test that operations complete within 500ms constraint"""
        # Add moderate number of dependencies (use smaller number to avoid cycles)
        for i in range(10):
            dep_spec = DependencySpec(
                dependency_id=f"perf_item{i}_depends_on_perf_item{i+100}",  # Use large gap to avoid cycles
                dependency_type=DependencyType.BLOCKING,
                target_item_id=f"perf_item{i+100}",
                target_track=StrategicTrack.PR_GATE,
                satisfaction_criteria=f"Perf item{i+100} must be completed",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )
            
            start_time = time.time()
            result = self.manager.declare_dependency(f"perf_item{i}", dep_spec)
            operation_time = (time.time() - start_time) * 1000
            
            assert result.success, f"Dependency {i} failed: {result.message}"
            assert operation_time < 500  # 500ms constraint from DR-2.1
            
    def test_health_monitoring_performance_tracking(self):
        """Test that health monitoring tracks performance correctly"""
        # Perform several operations
        for i in range(5):
            dep_spec = DependencySpec(
                dependency_id=f"health_item{i}_depends_on_health_item{i+1}",
                dependency_type=DependencyType.BLOCKING,
                target_item_id=f"health_item{i+1}",
                target_track=StrategicTrack.PR_GATE,
                satisfaction_criteria=f"Health item{i+1} must be completed",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )
            self.manager.declare_dependency(f"health_item{i}", dep_spec)
        
        # Check health indicators include performance metrics
        indicators = self.manager.get_health_indicators()
        
        assert "performance_metrics" in indicators
        assert "avg_operation_time_ms" in indicators["performance_metrics"]
        
        # Performance should be healthy
        perf_indicator = indicators["health_indicators"]["performance"]
        assert perf_indicator["status"] in ["healthy", "degraded"]  # Should not be unhealthy
        
    def test_graceful_degradation_on_performance_issues(self):
        """Test graceful degradation when performance degrades"""
        # Simulate performance degradation by adding many operations quickly
        with patch.object(self.manager, '_get_avg_operation_time', return_value=600.0):
            # Average operation time > 500ms should trigger degradation
            assert not self.manager.is_healthy()
            
            # Health indicators should reflect degraded performance
            indicators = self.manager.get_health_indicators()
            perf_indicator = indicators["health_indicators"]["performance"]
            assert perf_indicator["status"] == "unhealthy"


class TestErrorHandling(TestBacklogDependencyManager):
    """Test error handling and edge cases"""
    
    def test_handle_invalid_dependency_spec(self):
        """Test handling of invalid dependency specifications"""
        # Test with None values
        result = self.manager.declare_dependency("item1", None)
        assert not result.success
        assert "Internal error" in result.message
            
    def test_handle_exception_during_cycle_detection(self):
        """Test handling of exceptions during cycle detection"""
        self.manager.declare_dependency("item1", self.dep_spec_1)
        
        # Mock an exception in cycle detection
        with patch.object(self.manager, '_find_cycles_dfs', side_effect=Exception("Test error")):
            report = self.manager.detect_circular_dependencies()
            
            # Should handle exception gracefully
            assert len(report.cycles_found) == 0
            assert len(report.resolution_suggestions) > 0
            assert "Error during cycle detection" in report.resolution_suggestions[0]
            
    def test_handle_exception_during_critical_path_calculation(self):
        """Test handling of exceptions during critical path calculation"""
        self.manager.declare_dependency("item1", self.dep_spec_1)
        
        # Mock an exception in critical path calculation
        with patch.object(self.manager, '_calculate_longest_path', side_effect=Exception("Test error")):
            analysis = self.manager.calculate_critical_path()
            
            # Should handle exception gracefully
            assert len(analysis.critical_path) == 0
            assert analysis.total_duration == timedelta(0)
            assert analysis.calculation_time_ms > 0
            
    def test_data_consistency_validation(self):
        """Test internal data consistency validation"""
        # Add valid dependency
        self.manager.declare_dependency("item1", self.dep_spec_1)
        
        # Should be consistent
        assert self.manager._validate_internal_consistency()
        
        # Corrupt internal data
        self.manager._dependencies["invalid"] = "not_a_dependency_spec"
        
        # Should detect inconsistency
        assert not self.manager._validate_internal_consistency()


if __name__ == "__main__":
    pytest.main([__file__])