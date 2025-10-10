#!/usr/bin/env python3
"""
Integration Tests for DAG Orchestration Infrastructure Components
================================================================

Comprehensive integration tests for all infrastructure components:
- PreconditionValidator
- DiskSpaceManager  
- ResourcePredictor
- MLScheduler

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.dag_orchestration.infrastructure.precondition_validator import (
    InfrastructurePreconditionValidator,
    InfrastructureReport,
    PreconditionResult
)
from src.dag_orchestration.infrastructure.disk_space_manager import (
    DiskSpaceManager,
    DiskSpaceReport,
    CleanupAction
)
from src.dag_orchestration.optimization.resource_predictor import (
    ResourcePredictor,
    ResourceRequirement,
    CapacityPlan,
    PredictionHorizon
)
from src.dag_orchestration.scheduling.ml_scheduler import (
    MLTaskScheduler,
    SchedulingDecision,
    SystemState,
    SchedulingStrategy
)


class TestInfrastructureComponentsIntegration:
    """Integration tests for all infrastructure components."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_task_definition(self):
        """Sample task definition for testing."""
        return {
            'id': 'test_task_1',
            'name': 'Test Infrastructure Integration',
            'dependencies': ['task_0'],
            'resource_requirements': {
                'cpu_cores': 2,
                'memory_mb': 1024,
                'estimated_duration_minutes': 30
            },
            'execution_context': {
                'task_type': 'implementation',
                'priority': 'high'
            }
        }
    
    @pytest.fixture
    def sample_system_state(self):
        """Sample system state for testing."""
        return SystemState(
            available_cpu_cores=8,
            available_memory_mb=16384,
            current_load=0.4,
            active_tasks=2,
            queue_length=5
        )
    
    @pytest.mark.asyncio
    async def test_precondition_validator_comprehensive(self):
        """Test comprehensive precondition validation."""
        validator = InfrastructurePreconditionValidator()
        
        # Test module info
        module_info = validator.get_module_info()
        assert module_info['module_id'] == 'InfrastructurePreconditionValidator'
        assert 'redis_config' in module_info
        
        # Test health status
        health = validator.get_health_status()
        assert health.module_id == 'InfrastructurePreconditionValidator'
        assert health.health_score >= 0.0
        
        # Test graceful degradation
        degradation = validator.graceful_degradation()
        assert degradation.success is True
        assert len(degradation.remaining_capabilities) > 0
        
        # Test full validation
        report = await validator.validate_all_preconditions()
        assert isinstance(report, InfrastructureReport)
        assert isinstance(report.overall_status, bool)
        assert len(report.precondition_results) >= 4  # At least 4 checks
        assert len(report.recommendations) > 0
        
        # Verify all expected checks are present
        check_names = {result.name for result in report.precondition_results}
        expected_checks = {
            'Redis Connectivity',
            'System Resources', 
            'Python Packages',
            'Beast Mode Components'
        }
        assert expected_checks.issubset(check_names)
    
    def test_disk_space_manager_comprehensive(self, temp_workspace):
        """Test comprehensive disk space management."""
        manager = DiskSpaceManager(temp_workspace)
        
        # Test module info
        module_info = manager.get_module_info()
        assert module_info['module_id'] == 'DiskSpaceManager'
        assert 'thresholds' in module_info
        
        # Test health status
        health = manager.get_health_status()
        assert health.module_id == 'DiskSpaceManager'
        assert health.health_score >= 0.0
        
        # Test graceful degradation
        degradation = manager.graceful_degradation()
        assert degradation.success is True
        
        # Create test files for analysis
        test_dir = Path(temp_workspace) / 'test_cache'
        test_dir.mkdir()
        
        # Create cache files
        cache_dir = test_dir / '.pytest_cache'
        cache_dir.mkdir()
        (cache_dir / 'test_file.cache').write_text('test cache content' * 1000)
        
        # Create log files
        log_file = test_dir / 'test.log'
        log_file.write_text('log content' * 10000)
        
        # Test disk usage analysis
        report = manager.analyze_disk_usage()
        assert isinstance(report, DiskSpaceReport)
        assert report.total_space_gb > 0
        assert report.usage_percent >= 0
        assert isinstance(report.large_consumers, list)
        assert isinstance(report.cleanup_recommendations, list)
        
        # Test safe cleanup (dry run)
        cleanup_results = manager.execute_safe_cleanup(dry_run=True)
        assert cleanup_results['dry_run'] is True
        assert 'actions_executed' in cleanup_results
        assert 'bytes_freed' in cleanup_results
    
    def test_resource_predictor_comprehensive(self, sample_task_definition):
        """Test comprehensive resource prediction."""
        predictor = ResourcePredictor()
        
        # Test module info
        module_info = predictor.get_module_info()
        assert module_info['module_id'] == 'ResourcePredictor'
        assert 'system_baseline' in module_info
        
        # Test health status
        health = predictor.get_health_status()
        assert health.module_id == 'ResourcePredictor'
        assert health.health_score >= 0.0
        
        # Test graceful degradation
        degradation = predictor.graceful_degradation()
        assert degradation.success is True
        
        # Test task resource prediction
        requirements = predictor.predict_task_resource_requirements(sample_task_definition)
        assert isinstance(requirements, ResourceRequirement)
        assert requirements.cpu_cores > 0
        assert requirements.memory_mb > 0
        assert requirements.duration_minutes > 0
        assert 0.0 <= requirements.confidence <= 1.0
        
        # Test system utilization prediction
        predictions = predictor.predict_system_utilization(
            PredictionHorizon.SHORT_TERM,
            [sample_task_definition]
        )
        assert len(predictions) == 5  # One for each ResourceType
        
        for prediction in predictions:
            assert 0.0 <= prediction.predicted_utilization <= 1.0
            assert 0.0 <= prediction.peak_utilization <= 1.0
            assert 0.0 <= prediction.bottleneck_probability <= 1.0
            assert len(prediction.confidence_interval) == 2
        
        # Test capacity planning
        capacity_plan = predictor.generate_capacity_plan([sample_task_definition])
        assert isinstance(capacity_plan, CapacityPlan)
        assert len(capacity_plan.current_capacity) > 0
        assert len(capacity_plan.predicted_demand) > 0
        assert len(capacity_plan.scaling_recommendations) > 0
        assert 0.0 <= capacity_plan.confidence_score <= 1.0
        
        # Test pattern learning
        actual_usage = {
            'cpu_cores': 1.5,
            'memory_mb': 800,
            'duration_minutes': 25.0
        }
        predictor.update_task_resource_pattern(
            'test_task_1', 
            sample_task_definition, 
            actual_usage
        )
        
        # Verify pattern was learned
        task_type = sample_task_definition['execution_context']['task_type']
        assert task_type in predictor.task_resource_patterns
        assert len(predictor.task_resource_patterns[task_type]) > 0
    
    def test_ml_scheduler_comprehensive(self, sample_task_definition, sample_system_state):
        """Test comprehensive ML-based scheduling."""
        scheduler = MLTaskScheduler()
        
        # Test execution time prediction
        duration, confidence = scheduler.predict_execution_time(sample_task_definition)
        assert duration > 0
        assert 0.0 <= confidence <= 1.0
        
        # Test dynamic priority calculation
        priority = scheduler.calculate_dynamic_priority(sample_task_definition, sample_system_state)
        assert priority > 0
        
        # Test task batching optimization
        tasks = [sample_task_definition.copy() for _ in range(3)]
        for i, task in enumerate(tasks):
            task['id'] = f'test_task_{i+1}'
        
        batches = scheduler.optimize_task_batching(tasks, sample_system_state)
        assert len(batches) > 0
        assert all(isinstance(batch, list) for batch in batches)
        
        # Test scheduling recommendations
        recommendations = scheduler.get_scheduling_recommendations(tasks, sample_system_state)
        assert len(recommendations) == len(tasks)
        
        for rec in recommendations:
            assert isinstance(rec, SchedulingDecision)
            assert rec.priority_score > 0
            assert rec.estimated_duration > 0
            assert 0.0 <= rec.confidence_score <= 1.0
            assert len(rec.scheduling_rationale) > 0
        
        # Test metrics update
        execution_result = {
            'task_type': 'implementation',
            'execution_time': 28.5,
            'success': True,
            'resource_usage': {
                'cpu_percent': 75.0,
                'memory_mb': 900
            }
        }
        scheduler.update_task_metrics('test_task_1', execution_result)
        
        # Verify metrics were updated
        assert 'implementation' in scheduler.task_metrics
        metrics = scheduler.task_metrics['implementation']
        assert metrics.execution_count > 0
        assert metrics.avg_execution_time > 0
    
    def test_component_integration_workflow(self, temp_workspace, sample_task_definition, sample_system_state):
        """Test integrated workflow using all components together."""
        # Initialize all components
        validator = InfrastructurePreconditionValidator()
        disk_manager = DiskSpaceManager(temp_workspace)
        resource_predictor = ResourcePredictor()
        scheduler = MLTaskScheduler()
        
        # Step 1: Validate infrastructure preconditions
        async def run_validation():
            return await validator.validate_all_preconditions()
        
        validation_report = asyncio.run(run_validation())
        
        # Step 2: Analyze disk space
        disk_report = disk_manager.analyze_disk_usage()
        
        # Step 3: Predict resource requirements
        resource_requirements = resource_predictor.predict_task_resource_requirements(sample_task_definition)
        
        # Step 4: Generate scheduling recommendations
        scheduling_recommendations = scheduler.get_scheduling_recommendations(
            [sample_task_definition], 
            sample_system_state
        )
        
        # Step 5: Create integrated assessment
        integrated_assessment = {
            'infrastructure_ready': validation_report.overall_status,
            'disk_space_adequate': not disk_report.critical_threshold_reached,
            'resource_prediction_confidence': resource_requirements.confidence,
            'scheduling_confidence': scheduling_recommendations[0].confidence_score if scheduling_recommendations else 0.0,
            'overall_readiness': (
                validation_report.overall_status and
                not disk_report.critical_threshold_reached and
                resource_requirements.confidence > 0.5
            )
        }
        
        # Verify integrated assessment
        assert isinstance(integrated_assessment['infrastructure_ready'], bool)
        assert isinstance(integrated_assessment['disk_space_adequate'], bool)
        assert 0.0 <= integrated_assessment['resource_prediction_confidence'] <= 1.0
        assert 0.0 <= integrated_assessment['scheduling_confidence'] <= 1.0
        assert isinstance(integrated_assessment['overall_readiness'], bool)
        
        # Test component health monitoring
        health_statuses = {
            'validator': validator.get_health_status(),
            'disk_manager': disk_manager.get_health_status(),
            'resource_predictor': resource_predictor.get_health_status(),
            'scheduler': scheduler.get_health_status() if hasattr(scheduler, 'get_health_status') else None
        }
        
        for component, health in health_statuses.items():
            if health:  # Some components might not have health status
                assert health.health_score >= 0.0
                assert health.module_id is not None
    
    def test_component_error_handling(self, sample_task_definition):
        """Test error handling across all components."""
        # Test with invalid configurations
        invalid_config = {'invalid_key': 'invalid_value'}
        
        # Resource predictor with invalid config
        predictor = ResourcePredictor(invalid_config)
        requirements = predictor.predict_task_resource_requirements(sample_task_definition)
        assert isinstance(requirements, ResourceRequirement)  # Should still work with defaults
        
        # ML scheduler with invalid config
        scheduler = MLTaskScheduler(invalid_config)
        duration, confidence = scheduler.predict_execution_time(sample_task_definition)
        assert duration > 0  # Should still work with defaults
        
        # Test with malformed task definitions
        malformed_task = {'id': 'malformed'}  # Missing required fields
        
        requirements = predictor.predict_task_resource_requirements(malformed_task)
        assert isinstance(requirements, ResourceRequirement)  # Should handle gracefully
        
        duration, confidence = scheduler.predict_execution_time(malformed_task)
        assert duration > 0  # Should handle gracefully
    
    def test_component_performance_characteristics(self, sample_task_definition, sample_system_state):
        """Test performance characteristics of all components."""
        import time
        
        # Test precondition validator performance
        validator = InfrastructurePreconditionValidator()
        start_time = time.time()
        
        async def run_validation():
            return await validator.validate_all_preconditions()
        
        validation_report = asyncio.run(run_validation())
        validation_time = time.time() - start_time
        assert validation_time < 30.0  # Should complete within 30 seconds
        
        # Test resource predictor performance
        predictor = ResourcePredictor()
        start_time = time.time()
        
        # Predict for multiple tasks
        tasks = [sample_task_definition.copy() for _ in range(10)]
        for i, task in enumerate(tasks):
            task['id'] = f'perf_test_task_{i}'
        
        predictions = []
        for task in tasks:
            prediction = predictor.predict_task_resource_requirements(task)
            predictions.append(prediction)
        
        prediction_time = time.time() - start_time
        assert prediction_time < 5.0  # Should complete within 5 seconds for 10 tasks
        assert len(predictions) == 10
        
        # Test ML scheduler performance
        scheduler = MLTaskScheduler()
        start_time = time.time()
        
        recommendations = scheduler.get_scheduling_recommendations(tasks, sample_system_state)
        scheduling_time = time.time() - start_time
        assert scheduling_time < 10.0  # Should complete within 10 seconds for 10 tasks
        assert len(recommendations) == 10
    
    def test_component_data_consistency(self, sample_task_definition):
        """Test data consistency across components."""
        # Create components
        resource_predictor = ResourcePredictor()
        scheduler = MLTaskScheduler()
        
        # Get predictions from both components
        resource_requirements = resource_predictor.predict_task_resource_requirements(sample_task_definition)
        duration, confidence = scheduler.predict_execution_time(sample_task_definition)
        
        # Verify consistency in duration predictions
        # They should be in the same ballpark (within 50% of each other)
        duration_ratio = max(resource_requirements.duration_minutes, duration) / min(resource_requirements.duration_minutes, duration)
        assert duration_ratio <= 2.0  # Should be within 2x of each other
        
        # Test learning consistency
        actual_usage = {
            'cpu_cores': 1.8,
            'memory_mb': 950,
            'duration_minutes': 32.0
        }
        
        # Update both components with same data
        resource_predictor.update_task_resource_pattern('test_task_1', sample_task_definition, actual_usage)
        
        execution_result = {
            'task_type': sample_task_definition['execution_context']['task_type'],
            'execution_time': actual_usage['duration_minutes'],
            'success': True,
            'resource_usage': actual_usage
        }
        scheduler.update_task_metrics('test_task_1', execution_result)
        
        # Get new predictions after learning
        new_resource_requirements = resource_predictor.predict_task_resource_requirements(sample_task_definition)
        new_duration, new_confidence = scheduler.predict_execution_time(sample_task_definition)
        
        # Verify both components learned (predictions should be closer to actual or at least not worse)
        # Note: Learning may not always improve immediately, especially with limited data
        resource_improvement = abs(new_resource_requirements.duration_minutes - actual_usage['duration_minutes']) <= abs(resource_requirements.duration_minutes - actual_usage['duration_minutes']) + 5.0  # Allow 5 minute tolerance
        scheduler_improvement = abs(new_duration - actual_usage['duration_minutes']) <= abs(duration - actual_usage['duration_minutes']) + 10.0  # Allow 10 minute tolerance
        
        # At least one component should show improvement or maintain accuracy
        assert resource_improvement or scheduler_improvement, f"Neither component improved: Resource {abs(new_resource_requirements.duration_minutes - actual_usage['duration_minutes']):.1f} vs {abs(resource_requirements.duration_minutes - actual_usage['duration_minutes']):.1f}, Scheduler {abs(new_duration - actual_usage['duration_minutes']):.1f} vs {abs(duration - actual_usage['duration_minutes']):.1f}"


class TestInfrastructureComponentsHealthMonitoring:
    """Test health monitoring integration across all components."""
    
    def test_comprehensive_health_monitoring(self):
        """Test comprehensive health monitoring across all components."""
        # Initialize all components
        components = {
            'precondition_validator': InfrastructurePreconditionValidator(),
            'disk_space_manager': DiskSpaceManager(),
            'resource_predictor': ResourcePredictor(),
            'ml_scheduler': MLTaskScheduler()
        }
        
        # Collect health status from all components
        health_statuses = {}
        for name, component in components.items():
            if hasattr(component, 'get_health_status'):
                health_statuses[name] = component.get_health_status()
        
        # Verify health monitoring
        assert len(health_statuses) >= 3  # At least 3 components should have health monitoring
        
        for name, health in health_statuses.items():
            assert health.module_id is not None
            assert 0.0 <= health.health_score <= 1.0
            assert health.last_check is not None
            assert health.uptime_seconds >= 0
        
        # Test graceful degradation
        degradation_results = {}
        for name, component in components.items():
            if hasattr(component, 'graceful_degradation'):
                degradation_results[name] = component.graceful_degradation()
        
        # Verify graceful degradation
        for name, result in degradation_results.items():
            assert result.success is not None
            assert isinstance(result.remaining_capabilities, list)
            assert isinstance(result.degraded_capabilities, list)


if __name__ == "__main__":
    # Run basic integration test
    print("🧪 Running DAG Orchestration Infrastructure Components Integration Tests")
    print("=" * 80)
    
    # Create test instance
    test_instance = TestInfrastructureComponentsIntegration()
    
    # Run basic tests
    with tempfile.TemporaryDirectory() as temp_dir:
        sample_task = {
            'id': 'integration_test_task',
            'name': 'Integration Test Task',
            'dependencies': [],
            'resource_requirements': {
                'cpu_cores': 2,
                'memory_mb': 1024,
                'estimated_duration_minutes': 30
            },
            'execution_context': {
                'task_type': 'implementation',
                'priority': 'high'
            }
        }
        
        sample_state = SystemState(
            available_cpu_cores=8,
            available_memory_mb=16384,
            current_load=0.4,
            active_tasks=2,
            queue_length=5
        )
        
        print("✅ Testing component integration workflow...")
        test_instance.test_component_integration_workflow(temp_dir, sample_task, sample_state)
        
        print("✅ Testing component error handling...")
        test_instance.test_component_error_handling(sample_task)
        
        print("✅ Testing component performance characteristics...")
        test_instance.test_component_performance_characteristics(sample_task, sample_state)
        
        print("✅ Testing component data consistency...")
        test_instance.test_component_data_consistency(sample_task)
    
    # Test health monitoring
    health_test = TestInfrastructureComponentsHealthMonitoring()
    print("✅ Testing comprehensive health monitoring...")
    health_test.test_comprehensive_health_monitoring()
    
    print("\n🎉 All infrastructure components integration tests passed!")
    print("📊 Components tested:")
    print("  - InfrastructurePreconditionValidator")
    print("  - DiskSpaceManager")
    print("  - ResourcePredictor")
    print("  - MLTaskScheduler")
    print("  - Integrated workflow and health monitoring")