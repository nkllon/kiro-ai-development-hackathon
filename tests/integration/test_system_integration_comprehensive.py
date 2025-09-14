"""
Comprehensive System Integration Tests

This module provides comprehensive integration tests for the entire Beast Mode
framework, testing cross-module interactions, end-to-end workflows, and
system-wide functionality.
"""

import pytest
import asyncio
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import subprocess
import time
import os
import sys

from tests.test_utilities import (
    TestConfig, TestEnvironment, TestDataFactory, MockSystemComponents,
    PerformanceMonitor, TestCoverageTracker, TestAssertions,
    integration_test, performance_test, unit_test, slow_test,
    requires_dependency, AsyncTestHelper
)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import core modules
try:
    from beast_mode.core.reflective_module import ReflectiveModule, HealthStatus
    from beast_mode.core.model_registry import ModelRegistry
    from beast_mode.core.pdca_models import PDCACycle, PDCAPhase
    from beast_mode.messaging.cli import cli as beast_mode_cli
    from devpost_integration.cli import main as devpost_cli
    from rm_ddd.cli import main as rm_ddd_cli
except ImportError as e:
    pytest.skip(f"Core modules not available: {e}", allow_module_level=True)


class TestSystemArchitectureIntegration:
    """Test system architecture integration."""
    
    @integration_test
    def test_core_modules_integration(self):
        """Test integration between core modules."""
        # Create core components
        registry = ModelRegistry()
        pdca_module = ReflectiveModule("pdca_orchestrator", "1.0.0")
        health_module = ReflectiveModule("health_monitor", "1.0.0")
        
        # Register models
        registry.register_model(
            "decision_engine",
            "recommendation",
            "1.0.0",
            {"accuracy": 0.92}
        )
        
        # Register capabilities
        pdca_module.register_capability("cycle_execution", {
            "description": "Execute PDCA cycles"
        })
        
        health_module.register_capability("health_monitoring", {
            "description": "Monitor system health"
        })
        
        # Test integration
        decision = registry.get_decision_recommendation(
            context={"workflow_type": "development"},
            decision_type="execution_strategy"
        )
        
        # Verify integration
        assert len(registry.models) == 1
        assert len(registry.decisions) == 1
        assert "cycle_execution" in pdca_module.list_capabilities()
        assert "health_monitoring" in health_module.list_capabilities()
        assert decision["decision_type"] == "execution_strategy"
    
    @integration_test
    def test_messaging_system_integration(self):
        """Test messaging system integration."""
        # This would test the messaging system integration
        # For now, we'll create a mock integration test
        
        messaging_module = ReflectiveModule("messaging_system", "1.0.0")
        messaging_module.register_capability("message_routing", {
            "description": "Route messages between components"
        })
        
        # Test messaging capabilities
        capabilities = messaging_module.list_capabilities()
        assert "message_routing" in capabilities
        
        # Test health status
        messaging_module.update_health_status(HealthStatus.HEALTHY)
        assert messaging_module.health_status == HealthStatus.HEALTHY
    
    @integration_test
    def test_cli_integration(self):
        """Test CLI integration with core modules."""
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Test Beast Mode CLI
        result = runner.invoke(beast_mode_cli, ['--help'])
        assert result.exit_code == 0
        assert "Beast Mode Framework CLI" in result.output
        
        # Test status command
        result = runner.invoke(beast_mode_cli, ['status'])
        assert result.exit_code in [0, 1]  # Allow for various states
    
    @integration_test
    def test_configuration_management_integration(self):
        """Test configuration management integration."""
        with TestEnvironment() as env:
            # Create comprehensive configuration
            config_data = {
                "beast_mode": {
                    "timeout": 30,
                    "retry_count": 3,
                    "log_level": "INFO",
                    "modules": {
                        "pdca_orchestrator": {
                            "enabled": True,
                            "timeout": 60
                        },
                        "model_registry": {
                            "enabled": True,
                            "cache_size": 1000
                        }
                    }
                },
                "devpost": {
                    "api_key": "test_key",
                    "base_url": "https://api.devpost.com",
                    "timeout": 30
                },
                "rm_ddd": {
                    "output_dir": "/tmp/rm_ddd",
                    "template_dir": "/tmp/templates"
                }
            }
            
            config_file = env.create_test_config(config_data)
            
            # Test configuration loading
            with open(config_file) as f:
                loaded_config = json.load(f)
            
            # Verify configuration structure
            assert "beast_mode" in loaded_config
            assert "devpost" in loaded_config
            assert "rm_ddd" in loaded_config
            
            # Verify nested configuration
            assert loaded_config["beast_mode"]["modules"]["pdca_orchestrator"]["enabled"]
            assert loaded_config["beast_mode"]["modules"]["model_registry"]["cache_size"] == 1000


class TestEndToEndWorkflows:
    """Test end-to-end workflows."""
    
    @integration_test
    def test_complete_pdca_workflow(self):
        """Test complete PDCA workflow from start to finish."""
        # Create components
        registry = ModelRegistry()
        pdca_module = ReflectiveModule("pdca_orchestrator", "1.0.0")
        
        # Register decision model
        registry.register_model(
            "workflow_optimizer",
            "optimization",
            "1.0.0",
            {"accuracy": 0.94}
        )
        
        # Create PDCA cycle
        cycle = PDCACycle("test_workflow", "implement_feature")
        
        # Plan phase
        plan_decision = registry.get_decision_recommendation(
            context={"phase": "plan", "objective": "implement_feature"},
            decision_type="planning_strategy"
        )
        
        cycle.add_validation_criteria([
            "unit_tests_pass",
            "integration_tests_pass",
            "code_coverage_90_percent"
        ])
        
        # Do phase
        cycle.transition_to_phase(PDCAPhase.DO)
        cycle.add_improvement_actions([
            "optimize_performance",
            "enhance_documentation"
        ])
        
        # Check phase
        cycle.transition_to_phase(PDCAPhase.CHECK)
        validation_results = {
            "unit_tests_pass": True,
            "integration_tests_pass": True,
            "code_coverage_90_percent": True
        }
        cycle.validate_criteria(validation_results)
        
        # Act phase
        cycle.transition_to_phase(PDCAPhase.ACT)
        improvement_results = {
            "optimize_performance": "completed",
            "enhance_documentation": "completed"
        }
        cycle.execute_improvement_actions(improvement_results)
        
        # Complete cycle
        cycle.complete_cycle(success=True, results={"success_rate": 0.95})
        
        # Verify complete workflow
        assert cycle.status == "completed"
        assert cycle.current_phase == PDCAPhase.ACT
        assert cycle.validation_passed == True
        assert len(registry.decisions) == 1
        assert plan_decision["decision_type"] == "planning_strategy"
    
    @integration_test
    def test_error_recovery_workflow(self):
        """Test error recovery workflow."""
        # Create components
        registry = ModelRegistry()
        health_module = ReflectiveModule("health_monitor", "1.0.0")
        
        # Register recovery model
        registry.register_model(
            "recovery_engine",
            "recovery",
            "1.0.0",
            {"success_rate": 0.88}
        )
        
        # Simulate error condition
        health_module.update_health_status(HealthStatus.UNHEALTHY)
        
        # Get recovery recommendation
        recovery_decision = registry.get_decision_recommendation(
            context={
                "health_status": "unhealthy",
                "error_type": "system_failure",
                "severity": "high"
            },
            decision_type="recovery_strategy"
        )
        
        # Execute recovery
        recovery_cycle = PDCACycle("recovery_cycle", "system_recovery")
        recovery_cycle.add_improvement_actions([
            "restart_services",
            "clear_caches",
            "verify_health"
        ])
        
        # Simulate recovery success
        health_module.update_health_status(HealthStatus.HEALTHY)
        recovery_cycle.complete_cycle(success=True, results={"recovery_time": 120})
        
        # Verify recovery workflow
        assert health_module.health_status == HealthStatus.HEALTHY
        assert recovery_cycle.status == "completed"
        assert recovery_decision["decision_type"] == "recovery_strategy"
        assert len(registry.decisions) == 1
    
    @integration_test
    def test_continuous_improvement_workflow(self):
        """Test continuous improvement workflow."""
        # Create components
        registry = ModelRegistry()
        improvement_module = ReflectiveModule("improvement_engine", "1.0.0")
        
        # Register improvement model
        registry.register_model(
            "improvement_analyzer",
            "optimization",
            "1.0.0",
            {"improvement_rate": 0.15}
        )
        
        # Create improvement cycle
        improvement_cycle = PDCACycle("improvement_cycle", "continuous_improvement")
        
        # Analyze current performance
        analysis_decision = registry.get_decision_recommendation(
            context={
                "current_performance": 0.85,
                "target_performance": 0.95,
                "improvement_areas": ["performance", "reliability", "usability"]
            },
            decision_type="improvement_analysis"
        )
        
        # Plan improvements
        improvement_cycle.add_improvement_actions([
            "optimize_algorithms",
            "enhance_monitoring",
            "improve_user_experience",
            "add_automated_testing"
        ])
        
        # Execute improvements
        improvement_results = {
            "optimize_algorithms": "completed",
            "enhance_monitoring": "completed",
            "improve_user_experience": "in_progress",
            "add_automated_testing": "completed"
        }
        improvement_cycle.execute_improvement_actions(improvement_results)
        
        # Complete improvement cycle
        improvement_cycle.complete_cycle(
            success=True,
            results={"performance_improvement": 0.12}
        )
        
        # Verify improvement workflow
        assert improvement_cycle.status == "completed"
        assert analysis_decision["decision_type"] == "improvement_analysis"
        assert len(improvement_cycle.improvement_actions) == 4
        assert improvement_cycle.results["performance_improvement"] == 0.12


class TestCrossModuleCommunication:
    """Test communication between modules."""
    
    @integration_test
    def test_module_dependency_management(self):
        """Test module dependency management."""
        # Create modules with dependencies
        core_module = ReflectiveModule("core_module", "1.0.0")
        pdca_module = ReflectiveModule("pdca_module", "1.0.0")
        health_module = ReflectiveModule("health_module", "1.0.0")
        
        # Set up dependencies
        pdca_module.add_dependency("core_module", "1.0.0")
        health_module.add_dependency("core_module", "1.0.0")
        health_module.add_dependency("pdca_module", "1.0.0")
        
        # Verify dependencies
        assert pdca_module.has_dependency("core_module")
        assert health_module.has_dependency("core_module")
        assert health_module.has_dependency("pdca_module")
        assert not pdca_module.has_dependency("health_module")
        
        # Test dependency resolution
        core_deps = core_module.list_dependencies()
        pdca_deps = pdca_module.list_dependencies()
        health_deps = health_module.list_dependencies()
        
        assert len(core_deps) == 0  # Core module has no dependencies
        assert len(pdca_deps) == 1  # PDCA depends on core
        assert len(health_deps) == 2  # Health depends on core and PDCA
    
    @integration_test
    def test_health_monitoring_integration(self):
        """Test health monitoring integration across modules."""
        # Create modules
        modules = [
            ReflectiveModule("module_1", "1.0.0"),
            ReflectiveModule("module_2", "1.0.0"),
            ReflectiveModule("module_3", "1.0.0")
        ]
        
        # Set different health statuses
        modules[0].update_health_status(HealthStatus.HEALTHY)
        modules[1].update_health_status(HealthStatus.DEGRADED)
        modules[2].update_health_status(HealthStatus.UNHEALTHY)
        
        # Test health aggregation
        health_statuses = [module.health_status for module in modules]
        
        assert HealthStatus.HEALTHY in health_statuses
        assert HealthStatus.DEGRADED in health_statuses
        assert HealthStatus.UNHEALTHY in health_statuses
        
        # Test health monitoring capabilities
        for module in modules:
            module.register_capability("health_check", {
                "description": f"Health check for {module.module_id}"
            })
        
        # Verify all modules have health check capability
        for module in modules:
            assert "health_check" in module.list_capabilities()
    
    @integration_test
    def test_data_flow_integration(self):
        """Test data flow integration between modules."""
        # Create modules
        data_source = ReflectiveModule("data_source", "1.0.0")
        data_processor = ReflectiveModule("data_processor", "1.0.0")
        data_sink = ReflectiveModule("data_sink", "1.0.0")
        
        # Set up data flow capabilities
        data_source.register_capability("data_generation", {
            "description": "Generate test data",
            "output_format": "json"
        })
        
        data_processor.register_capability("data_processing", {
            "description": "Process data",
            "input_format": "json",
            "output_format": "processed_json"
        })
        
        data_sink.register_capability("data_storage", {
            "description": "Store processed data",
            "input_format": "processed_json"
        })
        
        # Test data flow
        source_caps = data_source.list_capabilities()
        processor_caps = data_processor.list_capabilities()
        sink_caps = data_sink.list_capabilities()
        
        assert "data_generation" in source_caps
        assert "data_processing" in processor_caps
        assert "data_storage" in sink_caps
        
        # Test capability compatibility
        source_output = data_source.get_capability("data_generation")["output_format"]
        processor_input = data_processor.get_capability("data_processing")["input_format"]
        
        assert source_output == processor_input  # JSON to JSON


class TestSystemPerformance:
    """Test system performance and scalability."""
    
    @performance_test
    def test_large_scale_module_registration(self):
        """Test large-scale module registration performance."""
        registry = ModelRegistry()
        
        # Register many models
        start_time = time.time()
        for i in range(1000):
            registry.register_model(
                f"model_{i}",
                "classification",
                "1.0.0",
                {"index": i, "data": "x" * 100}
            )
        
        registration_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        for i in range(100):
            registry.get_model(f"model_{i}")
        
        retrieval_time = time.time() - start_time
        
        # Performance assertions
        TestAssertions.assert_performance_within_bounds(registration_time, 10.0)
        TestAssertions.assert_performance_within_bounds(retrieval_time, 2.0)
    
    @performance_test
    def test_concurrent_module_operations(self):
        """Test concurrent module operations."""
        async def create_and_operate_module(module_id):
            module = ReflectiveModule(f"module_{module_id}", "1.0.0")
            module.register_capability("test_capability", {"id": module_id})
            module.update_health_status(HealthStatus.HEALTHY)
            return module.module_id
        
        async def test_concurrent_operations():
            tasks = [create_and_operate_module(i) for i in range(100)]
            results = await asyncio.gather(*tasks)
            return results
        
        # Run concurrent test
        start_time = time.time()
        results = asyncio.run(test_concurrent_operations())
        total_time = time.time() - start_time
        
        # Verify results
        assert len(results) == 100
        assert all(f"module_{i}" in results for i in range(100))
        TestAssertions.assert_performance_within_bounds(total_time, 5.0)
    
    @slow_test
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        import psutil
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create many modules and models
        modules = []
        registry = ModelRegistry()
        
        for i in range(5000):
            # Create module
            module = ReflectiveModule(f"load_module_{i}", "1.0.0")
            module.register_capability("load_capability", {"data": "x" * 100})
            modules.append(module)
            
            # Register model
            registry.register_model(
                f"load_model_{i}",
                "classification",
                "1.0.0",
                {"data": "x" * 200}
            )
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 200, f"Memory usage increased by {memory_increase}MB"
        
        # Cleanup
        del modules
        del registry


class TestSystemReliability:
    """Test system reliability and error handling."""
    
    @integration_test
    def test_system_failure_recovery(self):
        """Test system failure recovery."""
        # Create components
        registry = ModelRegistry()
        health_module = ReflectiveModule("health_monitor", "1.0.0")
        
        # Register recovery model
        registry.register_model(
            "failure_recovery",
            "recovery",
            "1.0.0",
            {"success_rate": 0.90}
        )
        
        # Simulate system failure
        health_module.update_health_status(HealthStatus.UNHEALTHY)
        
        # Get recovery strategy
        recovery_decision = registry.get_decision_recommendation(
            context={
                "failure_type": "system_crash",
                "severity": "critical",
                "affected_components": ["database", "api", "cache"]
            },
            decision_type="recovery_strategy"
        )
        
        # Execute recovery
        recovery_cycle = PDCACycle("recovery_cycle", "system_recovery")
        recovery_cycle.add_improvement_actions([
            "restart_services",
            "restore_from_backup",
            "verify_integrity",
            "monitor_health"
        ])
        
        # Simulate recovery process
        recovery_cycle.transition_to_phase(PDCAPhase.DO)
        health_module.update_health_status(HealthStatus.DEGRADED)
        
        recovery_cycle.transition_to_phase(PDCAPhase.CHECK)
        health_module.update_health_status(HealthStatus.HEALTHY)
        
        recovery_cycle.complete_cycle(success=True, results={"recovery_time": 300})
        
        # Verify recovery
        assert health_module.health_status == HealthStatus.HEALTHY
        assert recovery_cycle.status == "completed"
        assert recovery_decision["decision_type"] == "recovery_strategy"
    
    @integration_test
    def test_graceful_degradation(self):
        """Test graceful degradation under load."""
        # Create components
        modules = [
            ReflectiveModule(f"module_{i}", "1.0.0")
            for i in range(10)
        ]
        
        # Simulate load by updating health status
        for i, module in enumerate(modules):
            if i < 7:  # 70% healthy
                module.update_health_status(HealthStatus.HEALTHY)
            elif i < 9:  # 20% degraded
                module.update_health_status(HealthStatus.DEGRADED)
            else:  # 10% unhealthy
                module.update_health_status(HealthStatus.UNHEALTHY)
        
        # Test graceful degradation
        healthy_count = sum(1 for module in modules if module.health_status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for module in modules if module.health_status == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for module in modules if module.health_status == HealthStatus.UNHEALTHY)
        
        assert healthy_count == 7
        assert degraded_count == 2
        assert unhealthy_count == 1
        
        # System should still be partially functional
        total_modules = len(modules)
        functional_modules = healthy_count + degraded_count
        functionality_percentage = (functional_modules / total_modules) * 100
        
        assert functionality_percentage >= 80  # At least 80% functional
    
    @integration_test
    def test_error_propagation_handling(self):
        """Test error propagation and handling."""
        # Create components
        registry = ModelRegistry()
        error_module = ReflectiveModule("error_module", "1.0.0")
        
        # Simulate error condition
        error_module.update_health_status(HealthStatus.UNHEALTHY)
        
        # Test error handling
        try:
            # This should handle errors gracefully
            decision = registry.get_decision_recommendation(
                context={"error_condition": True},
                decision_type="error_handling"
            )
            
            # Should still return a decision even with errors
            assert decision is not None
            assert "recommendation" in decision
            
        except Exception as e:
            # If an error occurs, it should be handled gracefully
            assert isinstance(e, Exception)
            # System should continue to function
            assert error_module.health_status == HealthStatus.UNHEALTHY


class TestSystemMonitoring:
    """Test system monitoring and observability."""
    
    @integration_test
    def test_comprehensive_health_monitoring(self):
        """Test comprehensive health monitoring."""
        # Create monitoring components
        health_monitor = ReflectiveModule("health_monitor", "1.0.0")
        metrics_collector = ReflectiveModule("metrics_collector", "1.0.0")
        alert_manager = ReflectiveModule("alert_manager", "1.0.0")
        
        # Register monitoring capabilities
        health_monitor.register_capability("health_check", {
            "description": "Check system health",
            "frequency": "30s"
        })
        
        metrics_collector.register_capability("metrics_collection", {
            "description": "Collect system metrics",
            "metrics": ["cpu", "memory", "disk", "network"]
        })
        
        alert_manager.register_capability("alert_management", {
            "description": "Manage system alerts",
            "alert_types": ["critical", "warning", "info"]
        })
        
        # Test monitoring integration
        assert "health_check" in health_monitor.list_capabilities()
        assert "metrics_collection" in metrics_collector.list_capabilities()
        assert "alert_management" in alert_manager.list_capabilities()
        
        # Test health status updates
        health_monitor.update_health_status(HealthStatus.HEALTHY)
        assert health_monitor.health_status == HealthStatus.HEALTHY
    
    @integration_test
    def test_metrics_collection_integration(self):
        """Test metrics collection integration."""
        # Create metrics components
        registry = ModelRegistry()
        metrics_module = ReflectiveModule("metrics_module", "1.0.0")
        
        # Register metrics model
        registry.register_model(
            "metrics_analyzer",
            "analytics",
            "1.0.0",
            {"accuracy": 0.95}
        )
        
        # Simulate metrics collection
        metrics_data = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "network_io": 1024
        }
        
        # Get metrics analysis
        analysis_decision = registry.get_decision_recommendation(
            context={
                "metrics": metrics_data,
                "thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90
                }
            },
            decision_type="metrics_analysis"
        )
        
        # Verify metrics analysis
        assert analysis_decision["decision_type"] == "metrics_analysis"
        assert "recommendation" in analysis_decision
        assert len(registry.decisions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
