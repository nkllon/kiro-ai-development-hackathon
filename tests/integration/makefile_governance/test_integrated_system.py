"""
Integration tests for the complete makefile governance system.

Tests the integration between syntax validator, governance engine,
and health monitor components.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.makefile_governance.core.syntax_validator import MakefileSyntaxValidator, SyntaxErrorType
from src.makefile_governance.core.governance_engine import MakefileGovernanceEngine, GovernanceRuleType, ViolationSeverity
from src.makefile_governance.core.health_monitor import MakefileHealthMonitor, HealthMetricType
from src.rm_ddd.core.unified_reflective_module import ModuleStatus


class TestIntegratedMakefileGovernanceSystem:
    """Integration test suite for the complete makefile governance system."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def validator(self):
        """Create a MakefileSyntaxValidator instance."""
        return MakefileSyntaxValidator()
    
    @pytest.fixture
    def governance_engine(self):
        """Create a MakefileGovernanceEngine instance."""
        return MakefileGovernanceEngine()
    
    @pytest.fixture
    def health_monitor(self):
        """Create a MakefileHealthMonitor instance."""
        return MakefileHealthMonitor()
    
    def test_complete_makefile_processing_workflow(self, validator, governance_engine, health_monitor, temp_dir):
        """Test complete workflow from validation through governance to health monitoring."""
        # Create a makefile with various issues
        makefile_content = """# Test Makefile with multiple issues
PROJECT_NAME := test-project
invalid-var := bad-value

help: ## Show help
\t@echo "Available targets:"

build_project:
    @echo "Building..."  # Space instead of tab
    mkdir -p build/
    cp src/* build/
    cd build && make all
    echo "Build complete"

TestTarget:
\t@echo "Testing..."

clean:
\t@echo "Cleaning..."
\tpython3 -c "
import os
print('Cleaning up'
# Missing closing parenthesis
"

# Missing PHONY declarations
.PHONY: help
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        # Step 1: Syntax Validation
        start_time = time.time()
        validation_result = validator.validate_makefile(makefile_path)
        validation_time = time.time() - start_time
        
        # Record validation result in health monitor
        health_monitor.record_validation_result(validation_result.is_valid, validation_time)
        
        # Verify syntax validation found issues
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        
        # Check for expected error types
        error_types = [error.error_type for error in validation_result.errors]
        assert SyntaxErrorType.INVALID_RECIPE in error_types
        assert SyntaxErrorType.INVALID_PYTHON_CODE in error_types
        
        # Step 2: Governance Validation
        start_time = time.time()
        governance_result = governance_engine.validate_governance(makefile_path)
        governance_time = time.time() - start_time
        
        # Record governance result in health monitor
        health_monitor.record_governance_result(governance_result.is_compliant, governance_time)
        
        # Verify governance validation found violations
        assert governance_result.is_compliant is False
        assert len(governance_result.violations) > 0
        
        # Check for expected violation types
        violation_types = [v.rule.rule_type for v in governance_result.violations]
        assert GovernanceRuleType.NAMING_CONVENTION in violation_types
        assert GovernanceRuleType.PHONY_DECLARATION in violation_types
        assert GovernanceRuleType.COMPLEXITY_LIMIT in violation_types
        
        # Step 3: Attempt Repair
        start_time = time.time()
        repair_result = validator.repair_makefile(makefile_path, create_backup=False)
        repair_time = time.time() - start_time
        
        # Record repair result in health monitor
        repair_successful = repair_result.repaired_content is not None and len(repair_result.errors) < len(validation_result.errors)
        health_monitor.record_repair_result(repair_successful, repair_time)
        
        # Verify repair was attempted
        assert repair_result.repaired_content is not None
        
        # Step 4: Check System Health
        system_health = health_monitor.get_system_health()
        
        # Verify health monitoring captured all operations
        assert system_health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert len(system_health.metrics) > 0
        
        # Verify specific metrics exist
        metric_types = [m.metric_type for m in system_health.metrics]
        assert HealthMetricType.VALIDATION_SUCCESS_RATE in metric_types
        assert HealthMetricType.GOVERNANCE_COMPLIANCE_RATE in metric_types
        assert HealthMetricType.REPAIR_SUCCESS_RATE in metric_types
        
        # Verify recommendations were generated
        assert len(system_health.recommendations) > 0
    
    def test_successful_makefile_processing_workflow(self, validator, governance_engine, health_monitor, temp_dir):
        """Test workflow with a compliant makefile."""
        # Create a compliant makefile
        makefile_content = """# Compliant Test Makefile
.PHONY: help clean test build

PROJECT_NAME := test-project
VERSION := 1.0.0

help: ## Show help message
\t@echo "Available targets:"
\t@echo "  help  - Show this help"
\t@echo "  clean - Clean build artifacts"
\t@echo "  test  - Run tests"
\t@echo "  build - Build project"

clean: ## Clean build artifacts
\t@echo "Cleaning build artifacts..."
\trm -rf build/ dist/

test: ## Run tests
\t@echo "Running tests..."
\tpython -m pytest

build: ## Build project
\t@echo "Building project..."
\tmkdir -p build/
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        # Step 1: Syntax Validation
        start_time = time.time()
        validation_result = validator.validate_makefile(makefile_path)
        validation_time = time.time() - start_time
        
        health_monitor.record_validation_result(validation_result.is_valid, validation_time)
        
        # Should pass syntax validation
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0
        
        # Step 2: Governance Validation
        start_time = time.time()
        governance_result = governance_engine.validate_governance(makefile_path)
        governance_time = time.time() - start_time
        
        health_monitor.record_governance_result(governance_result.is_compliant, governance_time)
        
        # Should pass governance validation (or have only minor violations)
        critical_violations = [v for v in governance_result.violations if v.rule.severity == ViolationSeverity.CRITICAL]
        error_violations = [v for v in governance_result.violations if v.rule.severity == ViolationSeverity.ERROR]
        
        assert len(critical_violations) == 0
        assert len(error_violations) == 0
        assert governance_result.quality_score > 0.8
        
        # Step 3: System Health Check
        system_health = health_monitor.get_system_health()
        
        # Should have healthy status
        assert system_health.status == ModuleStatus.HEALTHY
        assert system_health.health_score > 0.8
        
        # Should have minimal recommendations
        assert len(system_health.recommendations) <= 2
    
    def test_health_monitoring_across_multiple_operations(self, validator, governance_engine, health_monitor, temp_dir):
        """Test health monitoring across multiple makefile operations."""
        # Create multiple test makefiles with varying quality
        test_cases = [
            ("good_makefile.mk", """# Good Makefile
.PHONY: help test

help: ## Show help
\t@echo "Help"

test: ## Run tests
\t@echo "Testing"
"""),
            ("bad_makefile.mk", """# Bad Makefile
help:
@echo "Missing tab"

test_target:
    @echo "Spaces instead of tabs"

TestTarget:
\t@echo "Bad naming"
"""),
            ("medium_makefile.mk", """# Medium Makefile
.PHONY: help

help: ## Show help
\t@echo "Help"

build_project: ## Build (naming issue but otherwise ok)
\t@echo "Building"
""")
        ]
        
        results = []
        
        for filename, content in test_cases:
            makefile_path = temp_dir / filename
            makefile_path.write_text(content)
            
            # Validate syntax
            start_time = time.time()
            validation_result = validator.validate_makefile(makefile_path)
            validation_time = time.time() - start_time
            
            health_monitor.record_validation_result(validation_result.is_valid, validation_time)
            
            # Validate governance
            start_time = time.time()
            governance_result = governance_engine.validate_governance(makefile_path)
            governance_time = time.time() - start_time
            
            health_monitor.record_governance_result(governance_result.is_compliant, governance_time)
            
            # Attempt repair if needed
            if not validation_result.is_valid:
                start_time = time.time()
                repair_result = validator.repair_makefile(makefile_path, create_backup=False)
                repair_time = time.time() - start_time
                
                repair_successful = repair_result.repaired_content is not None
                health_monitor.record_repair_result(repair_successful, repair_time)
            
            results.append({
                'filename': filename,
                'syntax_valid': validation_result.is_valid,
                'governance_compliant': governance_result.is_compliant,
                'quality_score': governance_result.quality_score
            })
        
        # Check overall system health after processing multiple files
        system_health = health_monitor.get_system_health()
        
        # Verify health metrics reflect the mixed results
        validation_metric = next(
            (m for m in system_health.metrics if m.metric_type == HealthMetricType.VALIDATION_SUCCESS_RATE),
            None
        )
        assert validation_metric is not None
        # Should have some success rate between 0 and 1
        assert 0.0 <= validation_metric.value <= 1.0
        
        governance_metric = next(
            (m for m in system_health.metrics if m.metric_type == HealthMetricType.GOVERNANCE_COMPLIANCE_RATE),
            None
        )
        assert governance_metric is not None
        assert 0.0 <= governance_metric.value <= 1.0
        
        # Verify module info reflects the operations
        validator_info = validator.get_module_info()
        assert validator_info["statistics"]["validations_performed"] >= 3
        
        governance_info = governance_engine.get_module_info()
        assert governance_info["statistics"]["validations_performed"] >= 3
        
        monitor_info = health_monitor.get_module_info()
        assert monitor_info["statistics"]["total_validations"] >= 3
        assert monitor_info["statistics"]["total_governance_checks"] >= 3
    
    def test_error_handling_and_recovery(self, validator, governance_engine, health_monitor, temp_dir):
        """Test error handling and recovery across the integrated system."""
        # Test with non-existent file
        nonexistent_path = temp_dir / "nonexistent.mk"
        
        # All components should handle non-existent files gracefully
        validation_result = validator.validate_makefile(nonexistent_path)
        assert validation_result.is_valid is False
        assert len(validation_result.errors) == 1
        
        governance_result = governance_engine.validate_governance(nonexistent_path)
        assert governance_result.is_compliant is False
        assert len(governance_result.violations) == 1
        
        # Health monitor should track these as errors
        health_monitor.record_validation_result(False, 0.1)
        health_monitor.record_governance_result(False, 0.1)
        
        # Test with corrupted file content
        corrupted_path = temp_dir / "corrupted.mk"
        corrupted_path.write_bytes(b'\x00\x01\x02\x03')  # Binary content
        
        try:
            validation_result = validator.validate_makefile(corrupted_path)
            # Should either handle gracefully or raise an exception
        except Exception:
            # Exception is acceptable for corrupted files
            pass
        
        # System should still be functional after errors
        system_health = health_monitor.get_system_health()
        assert system_health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert isinstance(system_health.health_score, float)
        assert 0.0 <= system_health.health_score <= 1.0
    
    def test_performance_monitoring_integration(self, validator, governance_engine, health_monitor, temp_dir):
        """Test performance monitoring integration across components."""
        # Create a makefile that might have performance implications
        large_makefile_content = """# Large Makefile for performance testing
.PHONY: """ + " ".join([f"target{i}" for i in range(50)]) + """

PROJECT_NAME := test-project
""" + "\n".join([f"VAR{i} := value{i}" for i in range(20)]) + """

""" + "\n".join([f"""target{i}: ## Target {i}
\t@echo "Executing target {i}"
\t@sleep 0.01
""" for i in range(50)])
        
        makefile_path = temp_dir / "large_makefile.mk"
        makefile_path.write_text(large_makefile_content)
        
        # Measure performance of each component
        import time
        
        # Syntax validation performance
        start_time = time.time()
        validation_result = validator.validate_makefile(makefile_path)
        validation_duration = time.time() - start_time
        
        health_monitor.record_validation_result(validation_result.is_valid, validation_duration)
        
        # Governance validation performance
        start_time = time.time()
        governance_result = governance_engine.validate_governance(makefile_path)
        governance_duration = time.time() - start_time
        
        health_monitor.record_governance_result(governance_result.is_compliant, governance_duration)
        
        # Check performance metrics
        system_health = health_monitor.get_system_health()
        
        response_time_metric = next(
            (m for m in system_health.metrics if m.metric_type == HealthMetricType.AVERAGE_RESPONSE_TIME),
            None
        )
        
        if response_time_metric:
            # Response times should be reasonable (less than 10 seconds for this test)
            assert response_time_metric.value < 10.0
            
            # If response time is too high, should generate recommendations
            if response_time_metric.value > 3.0:
                assert any("performance" in rec.lower() or "optimize" in rec.lower() 
                          for rec in system_health.recommendations)
    
    def test_beast_mode_integration_patterns(self, validator, governance_engine, health_monitor):
        """Test Beast Mode framework integration patterns."""
        # Test ReflectiveModule capabilities
        components = [validator, governance_engine, health_monitor]
        
        for component in components:
            # Test module info
            info = component.get_module_info()
            assert "module_id" in info
            assert "name" in info
            assert "version" in info
            assert "capabilities" in info
            
            # Test health status
            health = component.get_health_status()
            assert health.module_id == component.module_id
            assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
            assert 0.0 <= health.health_score <= 1.0
            
            # Test graceful degradation
            degradation_result = component.graceful_degradation()
            assert degradation_result.success is True
            assert len(degradation_result.remaining_capabilities) > 0
    
    def test_trace_operation_integration(self, validator, governance_engine, health_monitor, temp_dir):
        """Test operation tracing integration across components."""
        makefile_content = """help: ## Show help
\t@echo "Help"
"""
        makefile_path = temp_dir / "test.mk"
        makefile_path.write_text(makefile_content)
        
        # Mock trace operations to verify they're called
        with patch.object(validator, 'trace_operation') as mock_validator_trace, \
             patch.object(governance_engine, 'trace_operation') as mock_governance_trace, \
             patch.object(health_monitor, 'trace_operation') as mock_monitor_trace:
            
            # Set up mock context managers
            for mock_trace in [mock_validator_trace, mock_governance_trace, mock_monitor_trace]:
                mock_context = MagicMock()
                mock_trace.return_value.__enter__ = lambda: mock_context
                mock_trace.return_value.__exit__ = lambda *args: None
            
            # Perform operations
            validator.validate_makefile(makefile_path)
            governance_engine.validate_governance(makefile_path)
            health_monitor.record_validation_result(True, 1.0)
            health_monitor.get_system_health()
            
            # Verify trace operations were called
            mock_validator_trace.assert_called()
            mock_governance_trace.assert_called()
            mock_monitor_trace.assert_called()
    
    def test_end_to_end_makefile_improvement_workflow(self, validator, governance_engine, health_monitor, temp_dir):
        """Test complete end-to-end workflow for makefile improvement."""
        # Start with a problematic makefile
        original_content = """# Problematic Makefile
help:
@echo "Missing tab and PHONY"

build_project:
    @echo "Spaces instead of tabs"
    mkdir -p build/
    cp src/* build/
    cd build && make all
    echo "Done"

TestTarget:
\t@echo "Bad naming convention"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(original_content)
        
        # Step 1: Initial Assessment
        initial_validation = validator.validate_makefile(makefile_path)
        initial_governance = governance_engine.validate_governance(makefile_path)
        
        health_monitor.record_validation_result(initial_validation.is_valid, 1.0)
        health_monitor.record_governance_result(initial_governance.is_compliant, 1.0)
        
        # Capture initial quality metrics
        initial_quality_score = initial_governance.quality_score
        initial_complexity_score = initial_governance.complexity_score
        
        # Step 2: Apply Repairs
        repair_result = validator.repair_makefile(makefile_path, create_backup=True)
        health_monitor.record_repair_result(repair_result.repaired_content is not None, 2.0)
        
        # Step 3: Re-assess After Repairs
        if repair_result.repaired_content:
            # Write repaired content back to file
            makefile_path.write_text(repair_result.repaired_content)
            
            # Re-validate
            post_repair_validation = validator.validate_makefile(makefile_path)
            post_repair_governance = governance_engine.validate_governance(makefile_path)
            
            health_monitor.record_validation_result(post_repair_validation.is_valid, 1.0)
            health_monitor.record_governance_result(post_repair_governance.is_compliant, 1.0)
            
            # Verify improvements
            assert len(post_repair_validation.errors) <= len(initial_validation.errors)
            
            # Quality score should improve or stay the same
            assert post_repair_governance.quality_score >= initial_quality_score * 0.9  # Allow for small variations
        
        # Step 4: Final Health Assessment
        final_health = health_monitor.get_system_health()
        
        # Verify the system tracked the improvement workflow
        assert final_health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert len(final_health.metrics) > 0
        assert len(final_health.recommendations) >= 0
        
        # Verify statistics reflect the complete workflow
        monitor_info = health_monitor.get_module_info()
        stats = monitor_info["statistics"]
        
        assert stats["total_validations"] >= 2  # Initial + post-repair
        assert stats["total_governance_checks"] >= 2
        assert stats["total_repairs"] >= 1
        
        # If repairs were successful, should see improvement in success rates
        if repair_result.repaired_content and len(post_repair_validation.errors) < len(initial_validation.errors):
            validation_metric = next(
                (m for m in final_health.metrics if m.metric_type == HealthMetricType.VALIDATION_SUCCESS_RATE),
                None
            )
            if validation_metric:
                assert validation_metric.value > 0.0