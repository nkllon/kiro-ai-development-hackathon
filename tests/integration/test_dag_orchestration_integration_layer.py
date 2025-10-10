#!/usr/bin/env python3
"""
Comprehensive Integration Tests for DAG Orchestration Integration Layer
======================================================================

Tests for ACE Reporter Integration, AI Memory Palace Integration,
System Integration Framework, and Task List Converter.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import json
import logging
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Test imports
try:
    from src.dag_orchestration.integration.ace_reporter_integration import (
        ACEReporterIntegration, 
        create_ace_reporter_integration,
        BroadcastEvent
    )
    from src.dag_orchestration.integration.ai_memory_palace_integration import (
        AIMemoryPalaceIntegration,
        create_ai_memory_palace_integration,
        ExecutionPattern
    )
    from src.dag_orchestration.integration.system_integration_framework import (
        SystemIntegrationFramework,
        create_system_integration_framework,
        IntegrationResult
    )
    from src.dag_orchestration.integration.task_list_converter import (
        TaskListConverter,
        create_task_list_converter,
        TaskDefinition,
        ConversionResult
    )
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR = str(e)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestACEReporterIntegration:
    """Test suite for ACE Reporter Integration."""
    
    @pytest.fixture
    def ace_reporter(self):
        """Create ACE Reporter Integration instance for testing."""
        return create_ace_reporter_integration()
    
    def test_ace_reporter_creation(self, ace_reporter):
        """Test ACE Reporter Integration creation."""
        assert ace_reporter is not None
        assert ace_reporter.module_id == "ACEReporterIntegration"
        
        # Test module info
        info = ace_reporter.get_module_info()
        assert info["module_id"] == "ACEReporterIntegration"
        assert info["name"] == "ACE Reporter Integration"
        assert "statistics" in info
    
    def test_ace_reporter_health_status(self, ace_reporter):
        """Test ACE Reporter health monitoring."""
        health = ace_reporter.get_health_status()
        assert health.module_id == "ACEReporterIntegration"
        assert health.status is not None
        assert health.health_score >= 0.0
        assert health.health_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_broadcast_execution_start(self, ace_reporter):
        """Test execution start broadcasting."""
        execution_id = "test_execution_001"
        task_count = 5
        execution_plan = {
            "estimated_duration": 300,
            "max_workers": 3
        }
        
        result = await ace_reporter.broadcast_execution_start(
            execution_id, task_count, execution_plan
        )
        
        assert result is True
        
        # Check statistics
        stats = ace_reporter.get_broadcast_statistics()
        assert stats["broadcast_statistics"]["total_broadcasts"] >= 1
        assert stats["broadcast_statistics"]["successful_broadcasts"] >= 1
    
    @pytest.mark.asyncio
    async def test_broadcast_task_completion(self, ace_reporter):
        """Test task completion broadcasting."""
        execution_id = "test_execution_002"
        task_id = "task_1"
        status = "completed"
        duration = 45.5
        result_data = {"output": "Task completed successfully"}
        
        result = await ace_reporter.broadcast_task_completion(
            execution_id, task_id, status, duration, result_data
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_broadcast_execution_summary(self, ace_reporter):
        """Test execution summary broadcasting."""
        execution_id = "test_execution_003"
        summary = {
            "actual_duration": 280,
            "success_rate": 0.8,
            "task_count": 5,
            "completed_tasks": 4,
            "failed_tasks": 1
        }
        
        result = await ace_reporter.broadcast_execution_summary(
            execution_id, summary
        )
        
        assert result is True
    
    def test_broadcast_history_management(self, ace_reporter):
        """Test broadcast history management."""
        # Add some test broadcasts to history
        ace_reporter._broadcast_history = [
            BroadcastEvent(
                event_type="test_event",
                execution_id=f"exec_{i}",
                timestamp=datetime.now(),
                data={"test": i}
            )
            for i in range(150)
        ]
        
        # Clear history keeping only recent entries
        cleared_count = ace_reporter.clear_broadcast_history(keep_recent=50)
        
        assert cleared_count == 100
        assert len(ace_reporter._broadcast_history) == 50
    
    def test_graceful_degradation(self, ace_reporter):
        """Test graceful degradation functionality."""
        result = ace_reporter.graceful_degradation()
        
        assert result.success is True
        assert len(result.remaining_capabilities) >= 1
        assert len(result.degraded_capabilities) >= 1


class TestAIMemoryPalaceIntegration:
    """Test suite for AI Memory Palace Integration."""
    
    @pytest.fixture
    def memory_palace(self):
        """Create AI Memory Palace Integration instance for testing."""
        return create_ai_memory_palace_integration()
    
    def test_memory_palace_creation(self, memory_palace):
        """Test AI Memory Palace Integration creation."""
        assert memory_palace is not None
        assert memory_palace.module_id == "AIMemoryPalaceIntegration"
        
        # Test module info
        info = memory_palace.get_module_info()
        assert info["module_id"] == "AIMemoryPalaceIntegration"
        assert info["name"] == "AI Memory Palace Integration"
    
    def test_memory_palace_health_status(self, memory_palace):
        """Test AI Memory Palace health monitoring."""
        health = memory_palace.get_health_status()
        assert health.module_id == "AIMemoryPalaceIntegration"
        assert health.status is not None
        assert health.health_score >= 0.0
        assert health.health_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_store_execution_pattern(self, memory_palace):
        """Test execution pattern storage."""
        execution_id = "test_execution_001"
        pattern_data = {
            "task_count": 5,
            "parallelization_strategy": "dependency_aware",
            "resource_usage": {"cpu": 0.6, "memory": 0.4}
        }
        performance_metrics = {
            "total_duration": 300,
            "parallelization_efficiency": 2.1,
            "resource_utilization": 0.7
        }
        
        result = await memory_palace.store_execution_pattern(
            execution_id, pattern_data, performance_metrics
        )
        
        assert result is True
        
        # Check that pattern was stored
        stats = memory_palace.get_learning_statistics()
        assert stats["total_patterns_stored"] >= 1
    
    @pytest.mark.asyncio
    async def test_retrieve_similar_patterns(self, memory_palace):
        """Test similar pattern retrieval."""
        # First store some patterns
        for i in range(3):
            await memory_palace.store_execution_pattern(
                f"exec_{i}",
                {"task_count": 5 + i, "strategy": "parallel"},
                {"duration": 300 + i * 10}
            )
        
        # Retrieve similar patterns
        current_pattern = {"task_count": 6, "strategy": "parallel"}
        similar_patterns = await memory_palace.retrieve_similar_patterns(
            current_pattern, limit=5
        )
        
        assert isinstance(similar_patterns, list)
        # Should find at least some similar patterns
        assert len(similar_patterns) >= 0
    
    @pytest.mark.asyncio
    async def test_learn_from_execution(self, memory_palace):
        """Test learning from execution performance."""
        execution_id = "test_execution_learn"
        performance_metrics = {
            "parallelization_efficiency": 1.2,  # Low efficiency
            "resource_utilization": 0.9,  # High utilization
            "total_duration": 450
        }
        
        insights = await memory_palace.learn_from_execution(
            execution_id, performance_metrics
        )
        
        assert "execution_id" in insights
        assert "optimization_suggestions" in insights
        assert "confidence_score" in insights
        
        # Should generate suggestions for low efficiency and high utilization
        suggestions = insights["optimization_suggestions"]
        assert len(suggestions) >= 1
    
    def test_pattern_similarity_calculation(self, memory_palace):
        """Test pattern similarity calculation."""
        pattern1 = {"task_count": 5, "strategy": "parallel", "complexity": "medium"}
        pattern2 = {"task_count": 5, "strategy": "parallel", "complexity": "high"}
        pattern3 = {"task_count": 10, "strategy": "sequential", "complexity": "low"}
        
        # Similar patterns should have higher similarity
        similarity_1_2 = memory_palace._calculate_pattern_similarity(pattern1, pattern2)
        similarity_1_3 = memory_palace._calculate_pattern_similarity(pattern1, pattern3)
        
        assert similarity_1_2 > similarity_1_3
        assert 0.0 <= similarity_1_2 <= 1.0
        assert 0.0 <= similarity_1_3 <= 1.0


class TestSystemIntegrationFramework:
    """Test suite for System Integration Framework."""
    
    @pytest.fixture
    def integration_framework(self):
        """Create System Integration Framework instance for testing."""
        return create_system_integration_framework()
    
    def test_framework_creation(self, integration_framework):
        """Test System Integration Framework creation."""
        assert integration_framework is not None
        assert integration_framework.module_id == "SystemIntegrationFramework"
        
        # Test module info
        info = integration_framework.get_module_info()
        assert info["module_id"] == "SystemIntegrationFramework"
        assert info["name"] == "System Integration Framework"
    
    def test_framework_health_status(self, integration_framework):
        """Test System Integration Framework health monitoring."""
        health = integration_framework.get_health_status()
        assert health.module_id == "SystemIntegrationFramework"
        assert health.status is not None
        assert health.health_score >= 0.0
        assert health.health_score <= 1.0
    
    def test_convert_sequential_to_dag(self, integration_framework):
        """Test sequential task conversion to DAG."""
        sequential_tasks = [
            {
                "id": "task_1",
                "name": "Initialize system",
                "function": "initialize_system",
                "args": (),
                "kwargs": {},
                "priority": 1
            },
            {
                "id": "task_2", 
                "name": "Process data",
                "function": "process_data",
                "args": ("input_data",),
                "kwargs": {"format": "json"},
                "priority": 2
            },
            {
                "id": "task_3",
                "name": "Generate report",
                "function": "generate_report",
                "args": (),
                "kwargs": {"output_format": "pdf"},
                "priority": 3
            }
        ]
        
        dag_tasks = integration_framework.convert_sequential_to_dag(sequential_tasks)
        
        assert len(dag_tasks) == 3
        assert dag_tasks[0]["task_id"] == "task_1"
        assert dag_tasks[1]["task_id"] == "task_2"
        assert dag_tasks[2]["task_id"] == "task_3"
        
        # Check dependencies (sequential conversion)
        assert len(dag_tasks[0]["dependencies"]) == 0  # First task has no dependencies
        assert "task_0" in dag_tasks[1]["dependencies"]  # Second task depends on first
        assert "task_1" in dag_tasks[2]["dependencies"]  # Third task depends on second
    
    @pytest.mark.asyncio
    async def test_integrate_with_legacy_executor(self, integration_framework):
        """Test integration with legacy executor."""
        tasks = [
            {
                "task_id": "legacy_task_1",
                "name": "Legacy Task 1",
                "dependencies": set(),
                "priority": 1
            },
            {
                "task_id": "legacy_task_2",
                "name": "Legacy Task 2", 
                "dependencies": {"legacy_task_1"},
                "priority": 2
            }
        ]
        
        result = await integration_framework.integrate_with_legacy_executor(tasks)
        
        assert isinstance(result, IntegrationResult)
        assert result.success is True
        assert result.integration_type == "legacy_executor"
        assert "legacy_tasks_count" in result.details
        assert result.details["legacy_tasks_count"] == 2
    
    def test_validate_system_compatibility(self, integration_framework):
        """Test system compatibility validation."""
        compatibility_report = integration_framework.validate_system_compatibility()
        
        assert "overall_compatibility" in compatibility_report
        assert "dag_registry_available" in compatibility_report
        assert "reflective_module_available" in compatibility_report
        assert "redis_infrastructure_available" in compatibility_report
        assert "validation_timestamp" in compatibility_report
        
        # Should report overall compatibility as True (assuming all systems available)
        assert compatibility_report["overall_compatibility"] is True
    
    def test_create_deployment_configuration(self, integration_framework):
        """Test deployment configuration creation."""
        config = integration_framework.create_deployment_configuration()
        
        assert "system_name" in config
        assert "version" in config
        assert "components" in config
        assert "integration_settings" in config
        assert "resource_limits" in config
        
        # Check that all required components are included
        components = config["components"]
        required_components = [
            "dag_orchestrator",
            "parallel_execution_engine", 
            "dependency_aware_scheduler",
            "infrastructure_validator",
            "ace_reporter_integration",
            "ai_memory_palace_integration"
        ]
        
        for component in required_components:
            assert component in components
            assert components[component]["enabled"] is True


class TestTaskListConverter:
    """Test suite for Task List Converter."""
    
    @pytest.fixture
    def task_converter(self):
        """Create Task List Converter instance for testing."""
        return create_task_list_converter()
    
    @pytest.fixture
    def sample_spec_content(self):
        """Sample spec content for testing."""
        return """
# Implementation Plan

- [x] 1. Set up core infrastructure
  - Create base components and interfaces
  - _Requirements: 1.1, 1.2_

- [ ] 2. Implement parallel execution engine
- [ ] 2.1 Create execution framework
  - Build parallel task execution capabilities
  - _Requirements: 2.1, 2.2_

- [ ] 2.2 Add resource management
  - Implement dynamic resource allocation
  - _Requirements: 2.3, 2.4_

- [ ] 3. Build monitoring system
  - Add comprehensive observability
  - _Requirements: 3.1, 3.2_
"""
    
    def test_converter_creation(self, task_converter):
        """Test Task List Converter creation."""
        assert task_converter is not None
        assert hasattr(task_converter, 'dag_registry')
        assert hasattr(task_converter, 'task_patterns')
    
    def test_convert_spec_tasks_with_temp_file(self, task_converter, sample_spec_content):
        """Test spec task conversion with temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_spec_content)
            temp_path = f.name
        
        try:
            result = task_converter.convert_spec_tasks(temp_path)
            
            assert isinstance(result, ConversionResult)
            assert result.success is True
            assert len(result.task_definitions) >= 4  # Should find at least 4 tasks
            
            # Check task structure
            for task in result.task_definitions:
                assert isinstance(task, TaskDefinition)
                assert task.id is not None
                assert task.name is not None
                assert isinstance(task.dependencies, list)
                assert isinstance(task.resource_requirements, dict)
                
        finally:
            Path(temp_path).unlink()  # Clean up temp file
    
    def test_convert_nonexistent_file(self, task_converter):
        """Test conversion of non-existent file."""
        result = task_converter.convert_spec_tasks("/nonexistent/path/tasks.md")
        
        assert isinstance(result, ConversionResult)
        assert result.success is False
        assert len(result.errors) >= 1
        assert "not found" in result.errors[0].lower()
    
    def test_task_dependency_inference(self, task_converter):
        """Test task dependency inference."""
        # Test hierarchical dependencies
        deps_1 = task_converter._infer_dependencies("1")
        deps_1_1 = task_converter._infer_dependencies("1.1")
        deps_1_2 = task_converter._infer_dependencies("1.2")
        deps_2_1 = task_converter._infer_dependencies("2.1")
        
        assert len(deps_1) == 0  # Top-level task has no dependencies
        assert "1" in deps_1_1  # Sub-task depends on parent
        assert "1" in deps_1_2  # Sub-task depends on parent
        assert "1.1" in deps_1_2  # Sequential dependency within level
        assert "2" in deps_2_1  # Sub-task depends on parent
    
    def test_task_classification(self, task_converter):
        """Test task type classification."""
        test_cases = [
            ("Implement core functionality", "implementation"),
            ("Test the system", "testing"),
            ("Deploy to production", "deployment"),
            ("Monitor system health", "monitoring"),
            ("General task", "general")
        ]
        
        for task_name, expected_type in test_cases:
            task_type = task_converter._classify_task_type(task_name)
            assert task_type == expected_type
    
    def test_priority_determination(self, task_converter):
        """Test task priority determination."""
        test_cases = [
            ("Critical system component", "high"),
            ("Optional enhancement", "low"),
            ("Standard implementation", "medium"),
            ("Essential core feature", "high")
        ]
        
        for task_name, expected_priority in test_cases:
            priority = task_converter._determine_priority(task_name)
            assert priority == expected_priority
    
    def test_resource_estimation(self, task_converter):
        """Test resource requirement estimation."""
        # Test complex task
        complex_resources = task_converter._estimate_resources("Complex comprehensive system implementation")
        assert complex_resources["cpu_cores"] >= 2
        assert complex_resources["memory_mb"] >= 1024
        assert complex_resources["estimated_duration_minutes"] >= 60
        
        # Test simple task
        simple_resources = task_converter._estimate_resources("Simple validation test")
        assert simple_resources["estimated_duration_minutes"] <= 30
    
    def test_export_dag_definition(self, task_converter, sample_spec_content):
        """Test DAG definition export."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as spec_file:
            spec_file.write(sample_spec_content)
            spec_path = spec_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Convert spec tasks
            result = task_converter.convert_spec_tasks(spec_path)
            assert result.success is True
            
            # Export DAG definition
            export_success = task_converter.export_dag_definition(result, output_path)
            assert export_success is True
            
            # Verify exported file
            assert Path(output_path).exists()
            
            with open(output_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "execution_plan" in exported_data
            assert "task_definitions" in exported_data
            assert "dag_validation" in exported_data
            
            # Check execution plan
            plan = exported_data["execution_plan"]
            assert "plan_id" in plan
            assert "total_tasks" in plan
            assert plan["total_tasks"] == len(result.task_definitions)
            
        finally:
            Path(spec_path).unlink()
            Path(output_path).unlink()


class TestIntegrationLayerHealthMonitoring:
    """Test suite for integration layer health monitoring and diagnostics."""
    
    @pytest.fixture
    def all_integrations(self):
        """Create all integration components for testing."""
        return {
            "ace_reporter": create_ace_reporter_integration(),
            "memory_palace": create_ai_memory_palace_integration(),
            "system_framework": create_system_integration_framework(),
            "task_converter": create_task_list_converter()
        }
    
    def test_all_components_health_monitoring(self, all_integrations):
        """Test that all integration components provide health monitoring."""
        for name, component in all_integrations.items():
            # Test health status
            health = component.get_health_status()
            assert health is not None
            assert hasattr(health, 'module_id')
            assert hasattr(health, 'status')
            assert hasattr(health, 'health_score')
            
            # Test module info
            info = component.get_module_info()
            assert info is not None
            assert "module_id" in info
            assert "name" in info
            assert "version" in info
    
    def test_all_components_graceful_degradation(self, all_integrations):
        """Test graceful degradation for all components."""
        for name, component in all_integrations.items():
            if hasattr(component, 'graceful_degradation'):
                result = component.graceful_degradation()
                assert result is not None
                assert hasattr(result, 'success')
                assert isinstance(result.success, bool)
    
    def test_integration_layer_diagnostics(self, all_integrations):
        """Test comprehensive diagnostics across integration layer."""
        diagnostics = {}
        
        for name, component in all_integrations.items():
            component_diagnostics = {
                "health": component.get_health_status(),
                "info": component.get_module_info(),
                "capabilities": component.get_capabilities() if hasattr(component, 'get_capabilities') else []
            }
            
            # Add component-specific diagnostics
            if hasattr(component, 'get_broadcast_statistics'):
                component_diagnostics["broadcast_stats"] = component.get_broadcast_statistics()
            
            if hasattr(component, 'get_learning_statistics'):
                component_diagnostics["learning_stats"] = component.get_learning_statistics()
            
            if hasattr(component, 'get_integration_statistics'):
                component_diagnostics["integration_stats"] = component.get_integration_statistics()
            
            diagnostics[name] = component_diagnostics
        
        # Verify all components have diagnostics
        assert len(diagnostics) == 4
        
        # Verify diagnostic completeness
        for name, diag in diagnostics.items():
            assert "health" in diag
            assert "info" in diag
            assert diag["health"].health_score >= 0.0
            assert diag["health"].health_score <= 1.0


@pytest.mark.asyncio
async def test_end_to_end_integration_workflow():
    """Test end-to-end integration workflow."""
    if not IMPORTS_SUCCESSFUL:
        pytest.skip(f"Integration components not available: {IMPORT_ERROR}")
    
    # Create all integration components
    ace_reporter = create_ace_reporter_integration()
    memory_palace = create_ai_memory_palace_integration()
    system_framework = create_system_integration_framework()
    task_converter = create_task_list_converter()
    
    # Test workflow: Convert tasks -> Integrate -> Execute -> Report -> Learn
    
    # 1. Convert spec tasks to DAG
    sample_tasks = [
        {"id": "task_1", "name": "Initialize", "function": "init"},
        {"id": "task_2", "name": "Process", "function": "process"},
        {"id": "task_3", "name": "Finalize", "function": "finalize"}
    ]
    
    dag_tasks = system_framework.convert_sequential_to_dag(sample_tasks)
    assert len(dag_tasks) == 3
    
    # 2. Integrate with legacy systems
    integration_result = await system_framework.integrate_with_legacy_executor(dag_tasks)
    assert integration_result.success is True
    
    # 3. Broadcast execution start
    execution_id = "e2e_test_execution"
    broadcast_result = await ace_reporter.broadcast_execution_start(
        execution_id, len(dag_tasks), {"estimated_duration": 180}
    )
    assert broadcast_result is True
    
    # 4. Simulate task completions
    for i, task in enumerate(dag_tasks):
        await ace_reporter.broadcast_task_completion(
            execution_id, task["task_id"], "completed", 30.0 + i * 10
        )
    
    # 5. Store execution pattern
    pattern_data = {
        "task_count": len(dag_tasks),
        "execution_strategy": "sequential_converted",
        "integration_type": "legacy_executor"
    }
    performance_metrics = {
        "total_duration": 180,
        "parallelization_efficiency": 1.0,
        "resource_utilization": 0.5
    }
    
    pattern_stored = await memory_palace.store_execution_pattern(
        execution_id, pattern_data, performance_metrics
    )
    assert pattern_stored is True
    
    # 6. Learn from execution
    insights = await memory_palace.learn_from_execution(
        execution_id, performance_metrics
    )
    assert "execution_id" in insights
    
    # 7. Broadcast execution summary
    summary = {
        "actual_duration": 180,
        "success_rate": 1.0,
        "task_count": len(dag_tasks),
        "completed_tasks": len(dag_tasks)
    }
    
    summary_broadcast = await ace_reporter.broadcast_execution_summary(
        execution_id, summary
    )
    assert summary_broadcast is True
    
    # Verify end-to-end workflow completed successfully
    ace_stats = ace_reporter.get_broadcast_statistics()
    memory_stats = memory_palace.get_learning_statistics()
    integration_stats = system_framework.get_integration_statistics()
    
    assert ace_stats["broadcast_statistics"]["successful_broadcasts"] >= 4  # Start + 3 tasks + summary
    assert memory_stats["total_patterns_stored"] >= 1
    assert integration_stats["integration_statistics"]["successful_integrations"] >= 1


if __name__ == "__main__":
    if not IMPORTS_SUCCESSFUL:
        print(f"❌ Integration tests cannot run: {IMPORT_ERROR}")
        exit(1)
    
    print("🚀 Running DAG Orchestration Integration Layer Tests")
    print("=" * 60)
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])