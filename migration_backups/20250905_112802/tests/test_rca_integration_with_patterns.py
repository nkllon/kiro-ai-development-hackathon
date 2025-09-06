"""
Integration tests for RCA Integration with Test Pattern Library
Tests the integration between TestRCAIntegrationEngine and TestPatternLibrary
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.testing.rca_integration import TestRCAIntegrationEngine, TestFailureData
from src.beast_mode.testing.test_pattern_library import TestPatternLibrary
from src.beast_mode.analysis.rca_engine import (
    RCAEngine, Failure, RootCause, SystematicFix, PreventionPattern, 
    FailureCategory, RootCauseType
)

class TestRCAIntegrationWithPatterns:
    """Test suite for RCA integration with test pattern library"""
    
    @pytest.fixture
    def mock_rca_engine(self):
        """Create mock RCA engine"""
        engine = Mock(spec=RCAEngine)
        engine.is_healthy.return_value = True
        engine.get_module_status.return_value = {"status": "operational"}
        engine.match_existing_patterns.return_value = []
        engine.perform_systematic_rca.return_value = Mock()
        return engine
        
    @pytest.fixture
    def test_pattern_library(self, tmp_path):
        """Create test pattern library with temporary directory"""
        library = TestPatternLibrary()
        library.test_patterns_path = str(tmp_path / "test_patterns.json")
        library.pattern_metrics_path = str(tmp_path / "metrics.json")
        library.learning_data_path = str(tmp_path / "learning.json")
        return library
        
    @pytest.fixture
    def rca_integrator(self, mock_rca_engine, test_pattern_library):
        """Create RCA integrator with mocked dependencies"""
        # Create mock performance monitor
        mock_perf_monitor = Mock()
        mock_perf_monitor.is_healthy.return_value = True
        mock_perf_monitor.get_module_status.return_value = {"status": "operational"}
        mock_perf_monitor.start_monitoring.return_value = None
        
        # Create mock context manager for monitoring
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=Mock(
            start_time=datetime.now(),
            duration_seconds=1.0,
            memory_usage_mb=100.0,
            peak_memory_mb=120.0,
            timeout_occurred=False,
            graceful_degradation=False,
            operation_status=Mock(value="completed")
        ))
        mock_context.__exit__ = Mock(return_value=None)
        mock_perf_monitor.monitor_operation.return_value = mock_context
        
        # Create mock timeout handler
        mock_timeout_handler = Mock()
        mock_timeout_handler.is_healthy.return_value = True
        mock_timeout_handler.get_module_status.return_value = {"status": "operational"}
        
        # Create mock timeout context manager
        mock_timeout_context = Mock()
        mock_timeout_context.__enter__ = Mock(return_value=None)
        mock_timeout_context.__exit__ = Mock(return_value=None)
        mock_timeout_handler.manage_operation_timeout.return_value = mock_timeout_context
        mock_timeout_handler.get_timeout_recommendations.return_value = {"degradation_suggested": False}
        
        integrator = TestRCAIntegrationEngine(
            rca_engine=mock_rca_engine,
            test_pattern_library=test_pattern_library,
            performance_monitor=mock_perf_monitor,
            timeout_handler=mock_timeout_handler
        )
        return integrator
            
    @pytest.fixture
    def sample_test_failure(self):
        """Create sample test failure data"""
        return TestFailureData(
            test_name="test_import_functionality",
            test_file="tests/test_example.py",
            failure_type="import_error",
            error_message="ImportError: No module named 'missing_module'",
            stack_trace="Traceback...",
            test_function="test_import_functionality",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={"test_type": "unit"},
            pytest_node_id="tests/test_example.py::test_import_functionality"
        )
        
    def test_pattern_library_integration_in_status(self, rca_integrator):
        """Test that pattern library status is included in module status"""
        status = rca_integrator.get_module_status()
        
        assert "test_pattern_library_status" in status
        assert status["test_pattern_library_status"]["module_name"] == "test_pattern_library"
        
    def test_pattern_matching_during_analysis(self, test_pattern_library, sample_test_failure):
        """Test that test pattern library can match patterns correctly"""
        from src.beast_mode.analysis.rca_engine import Failure, FailureCategory
        
        # Convert test failure to RCA failure for pattern matching
        rca_failure = Failure(
            failure_id="test_001",
            timestamp=sample_test_failure.failure_timestamp,
            component=f"test:{sample_test_failure.test_file}",
            error_message=sample_test_failure.error_message,
            stack_trace=sample_test_failure.stack_trace,
            context={
                "test_file": sample_test_failure.test_file,
                "test_function": sample_test_failure.test_function,
                "test_context": sample_test_failure.test_context
            },
            category=FailureCategory.DEPENDENCY_ISSUE
        )
        
        # Generate the actual signature that would be created
        actual_signature = test_pattern_library._generate_test_failure_signature(rca_failure)
        print(f"Actual signature: {actual_signature}")
        
        # Add a test pattern with the correct signature
        test_pattern = PreventionPattern(
            pattern_id="test_pattern_001",
            pattern_name="Test Import Error Pattern",
            failure_signature=actual_signature,
            root_cause_pattern="Missing test dependency",
            prevention_steps=["Install missing dependency"],
            detection_criteria=["Monitor import errors"],
            automated_checks=["Check dependencies"],
            pattern_hash="test_hash"
        )
        
        test_pattern_library.test_patterns["test_pattern_001"] = test_pattern
        test_pattern_library._build_performance_indexes()
        
        # Test pattern matching
        matches = test_pattern_library.match_test_patterns(rca_failure)
        
        # Verify pattern was found
        assert len(matches) > 0
        assert matches[0].pattern_id == "test_pattern_001"
        
    def test_pattern_learning_from_successful_analysis(self, test_pattern_library, sample_test_failure):
        """Test that successful RCA analyses trigger pattern learning"""
        from src.beast_mode.analysis.rca_engine import Failure, FailureCategory, RootCause, SystematicFix, RootCauseType
        
        # Create RCA failure
        rca_failure = Failure(
            failure_id="test_001",
            timestamp=sample_test_failure.failure_timestamp,
            component=f"test:{sample_test_failure.test_file}",
            error_message=sample_test_failure.error_message,
            stack_trace=sample_test_failure.stack_trace,
            context={
                "test_file": sample_test_failure.test_file,
                "test_function": sample_test_failure.test_function
            },
            category=FailureCategory.DEPENDENCY_ISSUE
        )
        
        # Create mock root cause and systematic fix
        root_cause = RootCause(
            cause_type=RootCauseType.TEST_IMPORT_ERROR,
            description="Missing test dependency",
            evidence=["ImportError in test"],
            confidence_score=0.9,
            impact_severity="high",
            affected_components=["tests/test_example.py"]
        )
        
        systematic_fix = SystematicFix(
            fix_id="fix_001",
            root_cause=root_cause,
            fix_description="Install missing dependency",
            implementation_steps=["Add to requirements", "Install with pip"],
            validation_criteria=["Import succeeds"],
            rollback_plan="Remove from requirements",
            estimated_time_minutes=5
        )
        
        initial_learning_count = len(test_pattern_library.learning_data)
        
        # Test pattern learning
        success = test_pattern_library.learn_from_successful_rca(
            failure=rca_failure,
            root_causes=[root_cause],
            systematic_fixes=[systematic_fix],
            validation_score=0.9
        )
        
        # Verify pattern learning occurred
        assert success is True
        assert len(test_pattern_library.learning_data) > initial_learning_count
        
    def test_pattern_effectiveness_report(self, rca_integrator):
        """Test pattern effectiveness reporting"""
        # Add some test data
        rca_integrator.pattern_matches_found = 5
        rca_integrator.successful_rca_analyses = 10
        
        report = rca_integrator.get_test_pattern_effectiveness_report()
        
        assert "integration_metrics" in report
        assert "pattern_integration_success_rate" in report["integration_metrics"]
        assert "sub_second_performance_met" in report["integration_metrics"]
        
    def test_pattern_library_optimization(self, rca_integrator):
        """Test pattern library optimization functionality"""
        # Add some test patterns
        for i in range(3):
            pattern = PreventionPattern(
                pattern_id=f"pattern_{i}",
                pattern_name=f"Pattern {i}",
                failure_signature=f"test:test_{i}.py|error|message|[]",
                root_cause_pattern="Error",
                prevention_steps=["Fix"],
                detection_criteria=["Monitor"],
                automated_checks=["Check"],
                pattern_hash=f"hash_{i}"
            )
            rca_integrator.test_pattern_library.test_patterns[pattern.pattern_id] = pattern
            
        optimization_results = rca_integrator.optimize_test_pattern_library()
        
        assert "pattern_optimization" in optimization_results
        assert "library_cleanup" in optimization_results
        assert "performance_improvement" in optimization_results
        
    def test_sub_second_performance_requirement(self, rca_integrator, sample_test_failure):
        """Test that pattern matching meets sub-second performance requirement"""
        # Add many patterns to test performance
        for i in range(100):
            pattern = PreventionPattern(
                pattern_id=f"perf_pattern_{i}",
                pattern_name=f"Performance Pattern {i}",
                failure_signature=f"test:perf_test_{i}.py|error|Error {i}|[]",
                root_cause_pattern=f"Error {i}",
                prevention_steps=[f"Fix {i}"],
                detection_criteria=[f"Monitor {i}"],
                automated_checks=[f"Check {i}"],
                pattern_hash=f"perf_hash_{i:03d}"
            )
            rca_integrator.test_pattern_library.test_patterns[pattern.pattern_id] = pattern
            
        rca_integrator.test_pattern_library._build_performance_indexes()
        
        # Mock RCA engine
        rca_integrator.rca_engine.match_existing_patterns.return_value = []
        
        # Test pattern matching performance
        import time
        start_time = time.time()
        
        # Convert test failure to RCA failure for pattern matching
        rca_failure = rca_integrator.convert_to_rca_failure(sample_test_failure)
        matches = rca_integrator.test_pattern_library.match_test_patterns(rca_failure)
        
        match_time_ms = (time.time() - start_time) * 1000
        
        # Verify sub-second performance (Requirement 4.2)
        assert match_time_ms < 1000, f"Pattern matching took {match_time_ms:.2f}ms, exceeds 1 second requirement"
        
    def test_error_handling_in_integration(self, rca_integrator, sample_test_failure):
        """Test error handling when pattern library operations fail"""
        # Mock pattern library to raise exception
        with patch.object(rca_integrator.test_pattern_library, 'match_test_patterns', side_effect=Exception("Pattern matching failed")):
            
            # Mock RCA engine to work normally
            rca_integrator.rca_engine.match_existing_patterns.return_value = []
            mock_rca_result = Mock()
            mock_rca_result.rca_confidence_score = 0.9
            mock_rca_result.validation_results = []
            mock_rca_result.root_causes = []
            mock_rca_result.systematic_fixes = []
            rca_integrator.rca_engine.perform_systematic_rca.return_value = mock_rca_result
            
            # Analysis should still complete despite pattern library failure
            report = rca_integrator.analyze_test_failures([sample_test_failure])
                
            # Should still get a report even with pattern library failure
            assert report is not None
            assert report.total_failures == 1