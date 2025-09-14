"""
Comprehensive Unit Tests for Beast Mode Core Components

This module provides comprehensive unit tests for all core Beast Mode framework
components including PDCA orchestration, model registry, health monitoring,
and reflective modules.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from tests.test_utilities import (
    TestConfig, TestEnvironment, TestDataFactory, MockSystemComponents,
    PerformanceMonitor, TestCoverageTracker, TestAssertions,
    integration_test, performance_test, unit_test, slow_test,
    requires_dependency
)

# Import core components
try:
    from beast_mode.core.exceptions import BeastModeError
    from beast_mode.core.reflective_module import ReflectiveModule, HealthStatus
    from beast_mode.core.model_registry import ModelRegistry
    from beast_mode.core.pdca_models import PDCACycle, PDCAPhase
    from beast_mode.core.interfaces import ComponentInterface
except ImportError as e:
    pytest.skip(f"Core modules not available: {e}", allow_module_level=True)


class TestBeastModeExceptions:
    """Test Beast Mode exception handling."""
    
    @unit_test
    def test_beast_mode_error_creation(self):
        """Test BeastModeError creation and properties."""
        error = BeastModeError("Test error message")
        
        assert isinstance(error, Exception)
        assert "Test error message" in str(error)
        assert hasattr(error, 'component')
        assert hasattr(error, 'operation')
    
    @unit_test
    def test_beast_mode_error_with_context(self):
        """Test BeastModeError with additional context."""
        error = BeastModeError(
            "Configuration error",
            component="test_component",
            operation="test_operation"
        )
        
        assert "Configuration error" in str(error)
        assert error.component == "test_component"
        assert error.operation == "test_operation"
    
    @unit_test
    def test_exception_inheritance_hierarchy(self):
        """Test exception inheritance hierarchy."""
        error = BeastModeError("Test error")
        
        assert isinstance(error, Exception)
        assert isinstance(error, BeastModeError)
    
    @unit_test
    def test_exception_chaining(self):
        """Test exception chaining."""
        original_error = ValueError("Original error")
        beast_error = BeastModeError("Beast mode error")
        beast_error.__cause__ = original_error
        
        assert beast_error.__cause__ == original_error
        assert "Original error" in str(beast_error)


class TestReflectiveModule:
    """Test ReflectiveModule base class."""
    
    @unit_test
    def test_reflective_module_initialization(self):
        """Test ReflectiveModule initialization."""
        module = ReflectiveModule(
            module_id="test_module",
            version="1.0.0",
            description="Test module"
        )
        
        assert module.module_id == "test_module"
        assert module.version == "1.0.0"
        assert module.description == "Test module"
        assert module.health_status == HealthStatus.UNKNOWN
        assert module.created_at is not None
    
    @unit_test
    def test_health_status_management(self):
        """Test health status management."""
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Test status updates
        module.update_health_status(HealthStatus.HEALTHY)
        assert module.health_status == HealthStatus.HEALTHY
        
        module.update_health_status(HealthStatus.DEGRADED)
        assert module.health_status == HealthStatus.DEGRADED
        
        module.update_health_status(HealthStatus.UNHEALTHY)
        assert module.health_status == HealthStatus.UNHEALTHY
    
    @unit_test
    def test_module_metadata(self):
        """Test module metadata management."""
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Test metadata updates
        module.update_metadata({"key1": "value1", "key2": "value2"})
        assert module.metadata["key1"] == "value1"
        assert module.metadata["key2"] == "value2"
        
        # Test metadata retrieval
        metadata = module.get_metadata()
        assert metadata["key1"] == "value1"
        assert metadata["key2"] == "value2"
    
    @unit_test
    def test_module_capabilities(self):
        """Test module capabilities management."""
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Test capability registration
        module.register_capability("test_capability", {"description": "Test capability"})
        assert "test_capability" in module.capabilities
        
        # Test capability retrieval
        capability = module.get_capability("test_capability")
        assert capability["description"] == "Test capability"
        
        # Test capability listing
        capabilities = module.list_capabilities()
        assert "test_capability" in capabilities
    
    @unit_test
    def test_module_dependencies(self):
        """Test module dependency management."""
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Test dependency registration
        module.add_dependency("other_module", "1.0.0")
        assert "other_module" in module.dependencies
        
        # Test dependency checking
        assert module.has_dependency("other_module")
        assert not module.has_dependency("nonexistent_module")
        
        # Test dependency listing
        dependencies = module.list_dependencies()
        assert "other_module" in dependencies


class TestModelRegistry:
    """Test Model Registry functionality."""
    
    @unit_test
    def test_registry_initialization(self):
        """Test ModelRegistry initialization."""
        registry = ModelRegistry()
        
        assert registry.models == {}
        assert registry.decisions == []
        assert registry.created_at is not None
    
    @unit_test
    def test_model_registration(self):
        """Test model registration."""
        registry = ModelRegistry()
        
        model_info = registry.register_model(
            model_id="test_model",
            model_type="classification",
            version="1.0.0",
            metadata={"accuracy": 0.92}
        )
        
        assert model_info["model_id"] == "test_model"
        assert model_info["model_type"] == "classification"
        assert model_info["version"] == "1.0.0"
        assert model_info["metadata"]["accuracy"] == 0.92
        assert model_info["status"] == "active"
        assert "test_model" in registry.models
    
    @unit_test
    def test_model_retrieval(self):
        """Test model retrieval."""
        registry = ModelRegistry()
        
        # Register a model
        registry.register_model("test_model", "classification", "1.0.0")
        
        # Retrieve the model
        model = registry.get_model("test_model")
        assert model is not None
        assert model["model_id"] == "test_model"
        
        # Test non-existent model
        non_existent = registry.get_model("non_existent")
        assert non_existent is None
    
    @unit_test
    def test_model_versioning(self):
        """Test model versioning."""
        registry = ModelRegistry()
        
        # Register multiple versions
        registry.register_model("test_model", "classification", "1.0.0")
        registry.register_model("test_model", "classification", "1.1.0")
        registry.register_model("test_model", "classification", "2.0.0")
        
        # Test version listing
        versions = registry.get_model_versions("test_model")
        assert len(versions) == 3
        assert "1.0.0" in versions
        assert "1.1.0" in versions
        assert "2.0.0" in versions
        
        # Test specific version retrieval
        v1 = registry.get_model_version("test_model", "1.0.0")
        v2 = registry.get_model_version("test_model", "2.0.0")
        
        assert v1["version"] == "1.0.0"
        assert v2["version"] == "2.0.0"
    
    @unit_test
    def test_decision_recommendation(self):
        """Test decision recommendation generation."""
        registry = ModelRegistry()
        
        # Register a decision model
        registry.register_model(
            "decision_engine",
            "recommendation",
            "1.0.0",
            {"accuracy": 0.89}
        )
        
        context = {
            "project_type": "web_application",
            "team_size": 5,
            "complexity": "medium"
        }
        
        decision = registry.get_decision_recommendation(
            context=context,
            decision_type="architecture_choice"
        )
        
        assert decision["decision_type"] == "architecture_choice"
        assert decision["context"] == context
        assert "recommendation" in decision
        assert "confidence" in decision
        assert "reasoning" in decision
    
    @unit_test
    def test_decision_history_tracking(self):
        """Test decision history tracking."""
        registry = ModelRegistry()
        
        # Make multiple decisions
        contexts = [
            {"scenario": "database_choice", "data_size": "large"},
            {"scenario": "deployment_strategy", "environment": "cloud"},
            {"scenario": "testing_approach", "coverage_target": 90}
        ]
        
        for i, context in enumerate(contexts):
            registry.get_decision_recommendation(
                context=context,
                decision_type=f"decision_type_{i}"
            )
        
        # Verify history
        assert len(registry.decisions) == 3
        for i, decision in enumerate(registry.decisions):
            assert decision["decision_type"] == f"decision_type_{i}"
            assert decision["context"] == contexts[i]
    
    @unit_test
    def test_model_metadata_validation(self):
        """Test model metadata validation."""
        registry = ModelRegistry()
        
        # Test valid metadata
        valid_metadata = {
            "accuracy": 0.92,
            "training_data_size": 10000,
            "features": ["feature1", "feature2"]
        }
        
        model_info = registry.register_model(
            "test_model",
            "classification",
            "1.0.0",
            valid_metadata
        )
        
        assert model_info["metadata"] == valid_metadata
        
        # Test invalid metadata (should still work but log warning)
        invalid_metadata = {"invalid_key": None}
        model_info2 = registry.register_model(
            "test_model2",
            "classification",
            "1.0.0",
            invalid_metadata
        )
        
        assert model_info2["metadata"] == invalid_metadata


class TestPDCAModels:
    """Test PDCA models and phases."""
    
    @unit_test
    def test_pdca_cycle_creation(self):
        """Test PDCA cycle creation."""
        cycle = PDCACycle(
            cycle_id="test_cycle_1",
            objective="test_implementation",
            created_at=datetime.now()
        )
        
        assert cycle.cycle_id == "test_cycle_1"
        assert cycle.objective == "test_implementation"
        assert cycle.current_phase == PDCAPhase.PLAN
        assert cycle.status == "active"
    
    @unit_test
    def test_pdca_phase_transitions(self):
        """Test PDCA phase transitions."""
        cycle = PDCACycle("test_cycle", "test_objective")
        
        # Test phase progression
        assert cycle.current_phase == PDCAPhase.PLAN
        
        cycle.transition_to_phase(PDCAPhase.DO)
        assert cycle.current_phase == PDCAPhase.DO
        
        cycle.transition_to_phase(PDCAPhase.CHECK)
        assert cycle.current_phase == PDCAPhase.CHECK
        
        cycle.transition_to_phase(PDCAPhase.ACT)
        assert cycle.current_phase == PDCAPhase.ACT
    
    @unit_test
    def test_pdca_cycle_completion(self):
        """Test PDCA cycle completion."""
        cycle = PDCACycle("test_cycle", "test_objective")
        
        # Complete the cycle
        cycle.complete_cycle(success=True, results={"success_rate": 0.95})
        
        assert cycle.status == "completed"
        assert cycle.completed_at is not None
        assert cycle.results["success_rate"] == 0.95
    
    @unit_test
    def test_pdca_cycle_validation_criteria(self):
        """Test PDCA cycle validation criteria."""
        cycle = PDCACycle("test_cycle", "test_objective")
        
        # Add validation criteria
        criteria = [
            "unit_tests_pass",
            "integration_tests_pass",
            "code_coverage_90_percent"
        ]
        
        cycle.add_validation_criteria(criteria)
        assert cycle.validation_criteria == criteria
        
        # Test criteria validation
        validation_results = {
            "unit_tests_pass": True,
            "integration_tests_pass": True,
            "code_coverage_90_percent": True
        }
        
        cycle.validate_criteria(validation_results)
        assert cycle.validation_passed == True
    
    @unit_test
    def test_pdca_cycle_improvement_actions(self):
        """Test PDCA cycle improvement actions."""
        cycle = PDCACycle("test_cycle", "test_objective")
        
        # Add improvement actions
        actions = [
            "optimize_performance",
            "enhance_documentation",
            "add_monitoring"
        ]
        
        cycle.add_improvement_actions(actions)
        assert cycle.improvement_actions == actions
        
        # Test action execution
        execution_results = {
            "optimize_performance": "completed",
            "enhance_documentation": "in_progress",
            "add_monitoring": "pending"
        }
        
        cycle.execute_improvement_actions(execution_results)
        assert cycle.improvement_results == execution_results


class TestComponentInterface:
    """Test ComponentInterface base class."""
    
    @unit_test
    def test_interface_initialization(self):
        """Test ComponentInterface initialization."""
        interface = ComponentInterface("test_interface")
        
        assert interface.interface_id == "test_interface"
        assert interface.is_active == False
        assert interface.created_at is not None
    
    @unit_test
    def test_interface_activation(self):
        """Test interface activation."""
        interface = ComponentInterface("test_interface")
        
        # Test activation
        interface.activate()
        assert interface.is_active == True
        assert interface.activated_at is not None
        
        # Test deactivation
        interface.deactivate()
        assert interface.is_active == False
        assert interface.deactivated_at is not None
    
    @unit_test
    def test_interface_health_check(self):
        """Test interface health checking."""
        interface = ComponentInterface("test_interface")
        
        # Test health check when inactive
        health = interface.check_health()
        assert health["status"] == "inactive"
        
        # Test health check when active
        interface.activate()
        health = interface.check_health()
        assert health["status"] == "healthy"
    
    @unit_test
    def test_interface_metrics(self):
        """Test interface metrics collection."""
        interface = ComponentInterface("test_interface")
        
        # Test metrics collection
        metrics = interface.collect_metrics()
        assert "interface_id" in metrics
        assert "is_active" in metrics
        assert "uptime" in metrics
        assert "created_at" in metrics


class TestIntegratedCoreFunctionality:
    """Test integrated core functionality."""
    
    @unit_test
    def test_systematic_workflow_integration(self):
        """Test integrated systematic workflow."""
        # Create components
        registry = ModelRegistry()
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Register model for decision making
        registry.register_model(
            "workflow_optimizer",
            "optimization",
            "1.0.0",
            {"accuracy": 0.94}
        )
        
        # Register module capability
        module.register_capability("workflow_execution", {
            "description": "Execute systematic workflows"
        })
        
        # Get decision recommendation
        decision = registry.get_decision_recommendation(
            context={"workflow_type": "development", "complexity": "high"},
            decision_type="execution_strategy"
        )
        
        # Verify integration
        assert len(registry.models) == 1
        assert len(registry.decisions) == 1
        assert "workflow_execution" in module.list_capabilities()
        assert decision["decision_type"] == "execution_strategy"
    
    @unit_test
    def test_error_recovery_integration(self):
        """Test error recovery integration."""
        registry = ModelRegistry()
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Register recovery model
        registry.register_model(
            "recovery_engine",
            "recovery",
            "1.0.0",
            {"success_rate": 0.88}
        )
        
        # Simulate error condition
        module.update_health_status(HealthStatus.UNHEALTHY)
        
        # Get recovery recommendation
        recovery_decision = registry.get_decision_recommendation(
            context={
                "health_status": "unhealthy",
                "error_type": "system_failure"
            },
            decision_type="recovery_strategy"
        )
        
        # Verify recovery process
        assert recovery_decision["decision_type"] == "recovery_strategy"
        assert module.health_status == HealthStatus.UNHEALTHY
        assert len(registry.decisions) == 1
    
    @unit_test
    def test_continuous_improvement_integration(self):
        """Test continuous improvement integration."""
        registry = ModelRegistry()
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Register improvement model
        registry.register_model(
            "improvement_engine",
            "optimization",
            "1.0.0",
            {"improvement_rate": 0.15}
        )
        
        # Create improvement cycle
        cycle = PDCACycle("improvement_cycle", "continuous_improvement")
        
        # Get improvement recommendations
        improvement_decision = registry.get_decision_recommendation(
            context={
                "cycle_id": cycle.cycle_id,
                "current_performance": 0.85
            },
            decision_type="improvement_strategy"
        )
        
        # Execute improvement actions
        cycle.add_improvement_actions([
            "optimize_performance",
            "enhance_monitoring"
        ])
        
        # Verify improvement process
        assert improvement_decision["decision_type"] == "improvement_strategy"
        assert len(cycle.improvement_actions) == 2
        assert len(registry.decisions) == 1


class TestPerformanceAndScalability:
    """Test performance and scalability aspects."""
    
    @performance_test
    def test_large_model_registry_performance(self):
        """Test performance with large model registry."""
        registry = ModelRegistry()
        
        # Register many models
        start_time = datetime.now()
        for i in range(1000):
            registry.register_model(
                f"model_{i}",
                "classification",
                "1.0.0",
                {"index": i}
            )
        
        registration_time = (datetime.now() - start_time).total_seconds()
        
        # Test retrieval performance
        start_time = datetime.now()
        for i in range(100):
            registry.get_model(f"model_{i}")
        
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        # Performance assertions
        TestAssertions.assert_performance_within_bounds(registration_time, 5.0)
        TestAssertions.assert_performance_within_bounds(retrieval_time, 1.0)
    
    @performance_test
    def test_concurrent_decision_processing(self):
        """Test concurrent decision processing."""
        registry = ModelRegistry()
        registry.register_model("decision_engine", "recommendation", "1.0.0")
        
        async def make_decision(context_id):
            return registry.get_decision_recommendation(
                context={"id": context_id, "type": "test"},
                decision_type="test_decision"
            )
        
        async def test_concurrent_decisions():
            tasks = [make_decision(i) for i in range(100)]
            results = await asyncio.gather(*tasks)
            return results
        
        # Run concurrent test
        start_time = datetime.now()
        results = asyncio.run(test_concurrent_decisions())
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Verify results
        assert len(results) == 100
        TestAssertions.assert_performance_within_bounds(total_time, 2.0)
    
    @slow_test
    def test_memory_usage_with_large_datasets(self):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large registry
        registry = ModelRegistry()
        for i in range(10000):
            registry.register_model(
                f"model_{i}",
                "classification",
                "1.0.0",
                {"data": "x" * 1000}  # 1KB per model
            )
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory usage should be reasonable (less than 100MB increase)
        assert memory_increase < 100, f"Memory usage increased by {memory_increase}MB"


class TestErrorHandlingAndResilience:
    """Test error handling and resilience."""
    
    @unit_test
    def test_registry_error_handling(self):
        """Test registry error handling."""
        registry = ModelRegistry()
        
        # Test invalid model registration
        with pytest.raises(ValueError):
            registry.register_model("", "classification", "1.0.0")
        
        with pytest.raises(ValueError):
            registry.register_model("test_model", "", "1.0.0")
        
        with pytest.raises(ValueError):
            registry.register_model("test_model", "classification", "")
    
    @unit_test
    def test_module_error_recovery(self):
        """Test module error recovery."""
        module = ReflectiveModule("test_module", "1.0.0")
        
        # Simulate error condition
        module.update_health_status(HealthStatus.UNHEALTHY)
        
        # Test recovery
        module.update_health_status(HealthStatus.HEALTHY)
        assert module.health_status == HealthStatus.HEALTHY
    
    @unit_test
    def test_cycle_error_handling(self):
        """Test PDCA cycle error handling."""
        cycle = PDCACycle("test_cycle", "test_objective")
        
        # Test invalid phase transition
        with pytest.raises(ValueError):
            cycle.transition_to_phase("invalid_phase")
        
        # Test completion with error
        cycle.complete_cycle(success=False, error="Test error")
        assert cycle.status == "failed"
        assert cycle.error == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
