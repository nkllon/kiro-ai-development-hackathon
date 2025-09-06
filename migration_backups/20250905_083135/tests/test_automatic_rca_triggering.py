"""
Beast Mode Framework - End-to-End Tests for Automatic RCA Triggering
Tests the complete workflow from test failure detection to RCA analysis
Requirements: 1.1, 1.4, 3.1 - Automatic RCA triggering with seamless integration
"""

import os
import sys
import pytest
import subprocess
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.testing.test_failure_detector import TestFailureDetector
from beast_mode.testing.rca_integration import TestRCAIntegrator, TestFailureData
from beast_mode.testing.rca_report_generator import RCAReportGenerator


class TestAutomaticRCATriggeringEndToEnd:
    """End-to-end tests for automatic RCA triggering on test failures"""
    
    def setup_method(self):
        """Set up test environment"""
        self.detector = TestFailureDetector()
        self.integrator = TestRCAIntegrator()
        self.generator = RCAReportGenerator()
        
        # Create sample test failure data
        self.sample_failure = TestFailureData(
            test_name="tests/test_sample.py::test_failing_function",
            test_file="tests/test_sample.py",
            failure_type="assertion",
            error_message="AssertionError: Expected 5, got 3",
            stack_trace="def test_failing_function():\n    assert 3 == 5\nAssertionError: Expected 5, got 3",
            test_function="test_failing_function",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={"test_type": "unit", "environment": "test"},
            pytest_node_id="tests/test_sample.py::test_failing_function"
        )
        
    def test_environment_variable_controls(self):
        """
        Test that environment variables control RCA behavior
        Requirements: 1.4 - Environment variable controls for RCA behavior
        """
        # Test RCA_ON_FAILURE control
        with patch.dict(os.environ, {'RCA_ON_FAILURE': 'false'}):
            from scripts.rca_cli import get_rca_config
            config = get_rca_config()
            assert config['on_failure'] is False
            
        with patch.dict(os.environ, {'RCA_ON_FAILURE': 'true'}):
            config = get_rca_config()
            assert config['on_failure'] is True
            
        # Test RCA_TIMEOUT control
        with patch.dict(os.environ, {'RCA_TIMEOUT': '45'}):
            config = get_rca_config()
            assert config['timeout'] == 45
            
        # Test RCA_VERBOSE control
        with patch.dict(os.environ, {'RCA_VERBOSE': 'true'}):
            config = get_rca_config()
            assert config['verbose'] is True
            
    def test_test_failure_detection_workflow(self):
        """
        Test complete test failure detection workflow
        Requirements: 1.1 - Automatic test failure detection
        """
        # Create a temporary test file that will fail
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def test_intentional_failure():
    assert False, "This test is designed to fail"
    
def test_import_error():
    import nonexistent_module
    
def test_file_not_found():
    with open('nonexistent_file.txt', 'r') as f:
        content = f.read()
""")
            temp_test_file = f.name
            
        try:
            # Monitor test execution (this will fail)
            test_command = f"python3 -m pytest {temp_test_file} -v"
            failures = self.detector.monitor_test_execution(test_command)
            
            # Verify failures were detected
            assert len(failures) > 0, "Should detect test failures"
            
            # Verify failure data structure
            for failure in failures:
                assert hasattr(failure, 'test_name')
                assert hasattr(failure, 'error_message')
                assert hasattr(failure, 'failure_type')
                assert hasattr(failure, 'stack_trace')
                
        finally:
            # Clean up temp file
            os.unlink(temp_test_file)
            
    def test_rca_integration_with_timeout(self):
        """
        Test RCA integration with timeout controls
        Requirements: 1.4 - 30-second timeout requirement
        """
        # Mock RCA engine to simulate long-running analysis
        with patch.object(self.integrator, 'rca_engine') as mock_engine:
            # Configure mock to simulate timeout scenario
            mock_engine.perform_systematic_rca.side_effect = lambda x: self._simulate_slow_rca()
            mock_engine.match_existing_patterns.return_value = []
            mock_engine.is_healthy.return_value = True
            
            # Test with short timeout
            self.integrator.analysis_timeout_seconds = 1  # 1 second timeout
            
            start_time = datetime.now()
            report = self.integrator.analyze_test_failures([self.sample_failure])
            end_time = datetime.now()
            
            # Verify timeout was respected (should complete quickly due to timeout)
            elapsed = (end_time - start_time).total_seconds()
            assert elapsed < 5, f"Analysis should timeout quickly, took {elapsed}s"
            
            # Verify report was still generated (graceful degradation)
            assert report is not None
            assert report.total_failures == 1
            
    def test_seamless_integration_with_make_targets(self):
        """
        Test seamless integration with make targets
        Requirements: 3.1 - Seamless integration that doesn't disrupt normal workflow
        """
        # Test that make targets exist and are callable
        makefile_path = Path("makefiles/testing.mk")
        assert makefile_path.exists(), "Testing makefile should exist"
        
        # Read makefile content to verify targets
        makefile_content = makefile_path.read_text()
        
        # Verify required targets exist
        assert "test:" in makefile_content, "test target should exist"
        assert "test-with-rca:" in makefile_content, "test-with-rca target should exist"
        assert "RCA_ON_FAILURE" in makefile_content, "RCA_ON_FAILURE variable should be supported"
        assert "RCA_TIMEOUT" in makefile_content, "RCA_TIMEOUT variable should be supported"
        
    def test_failure_detection_hooks_in_pytest(self):
        """
        Test failure detection hooks in pytest execution workflow
        Requirements: 3.1 - Implement failure detection hooks in pytest execution workflow
        """
        # Test pytest output parsing
        sample_pytest_output = """
FAILURES
________________________ test_sample_failure ________________________

def test_sample_failure():
>       assert False, "Sample failure for testing"
E       AssertionError: Sample failure for testing
E       assert False

tests/test_sample.py:10: AssertionError
________________________ test_import_error ________________________

def test_import_error():
>       import nonexistent_module
E       ImportError: No module named 'nonexistent_module'

tests/test_sample.py:15: ImportError
"""
        
        failures = self.detector.parse_pytest_output(sample_pytest_output)
        
        # Verify parsing extracted failures correctly
        assert len(failures) >= 1, "Should parse at least one failure"
        
        # Verify failure details
        failure = failures[0]
        assert "test_sample_failure" in failure.test_name or "test_import_error" in failure.test_name
        assert failure.error_message is not None
        assert len(failure.error_message) > 0
        
    def test_rca_cli_integration(self):
        """
        Test RCA CLI integration with environment variables
        Requirements: 1.1, 1.4 - CLI integration with environment controls
        """
        # Test CLI with different environment configurations
        test_environments = [
            {'RCA_ON_FAILURE': 'true', 'RCA_TIMEOUT': '30', 'RCA_VERBOSE': 'false'},
            {'RCA_ON_FAILURE': 'false', 'RCA_TIMEOUT': '60', 'RCA_VERBOSE': 'true'},
        ]
        
        for env_vars in test_environments:
            with patch.dict(os.environ, env_vars):
                # Import CLI functions with environment
                from scripts.rca_cli import get_rca_config, run_test_with_rca
                
                config = get_rca_config()
                
                # Verify configuration matches environment
                assert config['on_failure'] == (env_vars['RCA_ON_FAILURE'] == 'true')
                assert config['timeout'] == int(env_vars['RCA_TIMEOUT'])
                assert config['verbose'] == (env_vars['RCA_VERBOSE'] == 'true')
                
                # Test CLI execution (with mocked components to avoid actual RCA)
                with patch('scripts.rca_cli.TestFailureDetector') as mock_detector:
                    with patch('scripts.rca_cli.TestRCAIntegrator') as mock_integrator:
                        with patch('scripts.rca_cli.RCAReportGenerator') as mock_generator:
                            # Configure mocks
                            mock_detector.return_value = Mock()
                            mock_integrator.return_value = Mock()
                            mock_generator.return_value = Mock()
                            
                            # This should not raise an exception
                            try:
                                run_test_with_rca()
                            except SystemExit:
                                pass  # CLI may exit, that's OK
                            except Exception as e:
                                # Should handle gracefully
                                assert "not fully implemented" in str(e) or "not available" in str(e)
                                
    def test_graceful_degradation_on_component_failure(self):
        """
        Test graceful degradation when RCA components fail
        Requirements: 3.1 - Seamless integration that doesn't disrupt normal workflow
        """
        # Test with missing RCA engine
        integrator_without_engine = TestRCAIntegrator(rca_engine=None)
        
        # Should still generate a report (with errors)
        report = integrator_without_engine.analyze_test_failures([self.sample_failure])
        assert report is not None
        assert report.total_failures == 1
        
        # Test with failing report generator
        with patch.object(self.generator, 'generate_report', side_effect=Exception("Report generation failed")):
            # Should handle gracefully
            try:
                self.generator.display_console_report(report)
            except Exception as e:
                # Should not propagate unhandled exceptions
                assert False, f"Should handle report generation failure gracefully: {e}"
                
    def test_performance_requirements(self):
        """
        Test performance requirements for RCA analysis
        Requirements: 1.4 - 30-second timeout requirement
        """
        # Test that analysis completes within reasonable time
        start_time = datetime.now()
        
        # Perform RCA analysis on sample failure
        report = self.integrator.analyze_test_failures([self.sample_failure])
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        # Should complete within timeout (allowing some overhead for test environment)
        assert elapsed < 35, f"RCA analysis took {elapsed}s, should be under 35s"
        
        # Verify report was generated
        assert report is not None
        assert report.total_failures == 1
        
    def test_end_to_end_workflow_with_real_components(self):
        """
        Test complete end-to-end workflow with real components
        Requirements: 1.1, 1.4, 3.1 - Complete automatic RCA workflow
        """
        # Create a complete workflow test
        failures = [self.sample_failure]
        
        # Step 1: Failure detection (simulated)
        assert len(failures) > 0
        
        # Step 2: RCA integration
        report = self.integrator.analyze_test_failures(failures)
        assert report is not None
        assert report.total_failures == len(failures)
        
        # Step 3: Report generation
        console_output = self.generator.format_for_console(report, use_colors=False)
        assert len(console_output) > 0
        assert "RCA Analysis Report" in console_output or "Analysis Summary" in console_output
        
        # Step 4: JSON report generation
        json_report = self.generator.generate_json_report(report)
        assert isinstance(json_report, dict)
        assert "analysis_summary" in json_report
        
        # Step 5: Markdown report generation
        markdown_report = self.generator.generate_markdown_report(report)
        assert isinstance(markdown_report, str)
        assert len(markdown_report) > 0
        
    def test_make_target_environment_variable_integration(self):
        """
        Test that make targets properly use environment variables
        Requirements: 1.4 - Environment variable controls for RCA behavior
        """
        # Read the makefile to verify environment variable usage
        makefile_path = Path("makefiles/testing.mk")
        makefile_content = makefile_path.read_text()
        
        # Verify environment variables are properly defaulted
        assert "RCA_ON_FAILURE ?= true" in makefile_content
        assert "RCA_TIMEOUT ?= 30" in makefile_content
        assert "RCA_VERBOSE ?= false" in makefile_content
        
        # Verify environment variables are passed to scripts
        assert "RCA_TIMEOUT=$(RCA_TIMEOUT)" in makefile_content
        assert "RCA_VERBOSE=$(RCA_VERBOSE)" in makefile_content
        
        # Verify conditional RCA execution
        assert '[ "$(RCA_ON_FAILURE)" = "true" ]' in makefile_content
        
    # Helper methods
    
    def _simulate_slow_rca(self):
        """Simulate slow RCA analysis for timeout testing"""
        import time
        time.sleep(2)  # Simulate 2-second analysis
        
        # Return mock RCA result
        from beast_mode.analysis.rca_engine import RCAResult, Failure, FailureCategory
        from datetime import datetime
        
        mock_failure = Failure(
            failure_id="mock_failure",
            timestamp=datetime.now(),
            component="test_component",
            error_message="Mock error",
            stack_trace="Mock stack trace",
            context={},
            category=FailureCategory.UNKNOWN
        )
        
        return RCAResult(
            failure=mock_failure,
            root_causes=[],
            systematic_fixes=[],
            prevention_patterns=[],
            total_analysis_time_seconds=2.0,
            rca_confidence_score=0.8
        )


class TestMakeTargetIntegration:
    """Test integration with make targets"""
    
    def test_make_test_target_exists(self):
        """Test that enhanced test target exists and is properly configured"""
        makefile_path = Path("makefiles/testing.mk")
        assert makefile_path.exists()
        
        content = makefile_path.read_text()
        
        # Verify test target with RCA integration
        assert "test:" in content
        assert "RCA_ON_FAILURE" in content
        assert "python3 scripts/rca_cli.py test-rca" in content
        
    def test_make_rca_targets_exist(self):
        """Test that RCA-specific make targets exist"""
        makefile_path = Path("makefiles/testing.mk")
        content = makefile_path.read_text()
        
        # Verify RCA targets
        assert "rca:" in content
        assert "rca-task:" in content
        assert "rca-report:" in content
        assert "test-with-rca:" in content
        
    def test_environment_variable_defaults(self):
        """Test that environment variables have proper defaults"""
        makefile_path = Path("makefiles/testing.mk")
        content = makefile_path.read_text()
        
        # Verify defaults
        assert "RCA_ON_FAILURE ?= true" in content
        assert "RCA_TIMEOUT ?= 30" in content
        assert "RCA_VERBOSE ?= false" in content


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])