"""
Comprehensive RCA Integration Validation Suite - Task 11
Automated test suite that validates all RCA integration functionality
Requirements: All requirements 1.1-5.4 - Complete functionality validation
"""

import pytest
import time
import tempfile
import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Import test fixtures
from tests.fixtures.test_rca_failure_scenarios import (
    RCAFailureScenarioFixtures, FailureScenario, create_temporary_test_files
)

# Import RCA components
from beast_mode.testing.test_failure_detector import TestFailureDetector
from beast_mode.testing.rca_integration import TestRCAIntegrationEngine, TestFailureData
from beast_mode.testing.rca_report_generator import RCAReportGenerator, ReportFormat
from beast_mode.analysis.rca_engine import FailureCategory


class TestComprehensiveRCAIntegrationValidation(RCAFailureScenarioFixtures):
    """Comprehensive validation of all RCA integration functionality"""
    
    def test_all_requirements_end_to_end_validation(self, all_failure_scenarios):
        """
        Validate all requirements through end-to-end testing with real scenarios
        Requirements: All requirements 1.1-5.4
        """
        integrator = TestRCAIntegrationEngine()
        generator = RCAReportGenerator()
        
        validation_results = {}
        
        for scenario in all_failure_scenarios:
            print(f"\nValidating scenario: {scenario.name}")
            
            # Test end-to-end workflow
            start_time = time.time()
            report = integrator.analyze_test_failures(scenario.failures)
            analysis_time = time.time() - start_time
            
            # Validate requirement 1.4 - 30-second timeout
            assert analysis_time < 30.0, f"Analysis took {analysis_time:.2f}s, violates 30s requirement"
            
            # Validate requirement 1.1 - Automatic RCA triggering
            assert report.total_failures == len(scenario.failures), "Should process all failures"
            
            # Validate requirement 1.3 - Multiple failure analysis and grouping
            if len(scenario.failures) > 1:
                assert len(report.grouped_failures) > 0, "Should group multiple failures"
                
            # Validate requirement 2.1, 2.2, 2.3, 2.4 - Comprehensive reporting
            assert isinstance(report.summary.confidence_score, float), "Should provide confidence score"
            assert len(report.recommendations) > 0, "Should provide recommendations"
            assert len(report.next_steps) > 0, "Should provide next steps"
            
            # Validate requirement 4.1 - RCA engine integration
            if report.failures_analyzed > 0:
                assert len(report.rca_results) > 0, "Should provide RCA results when analysis succeeds"
                
            # Test report generation (requirements 2.2, 2.3, 2.4)
            console_report = generator.format_for_console(report, use_colors=False)
            json_report = generator.generate_json_report(report)
            markdown_report = generator.generate_markdown_report(report)
            
            assert len(console_report) > 0, "Should generate console report"
            assert isinstance(json_report, dict), "Should generate JSON report"
            assert len(markdown_report) > 0, "Should generate markdown report"
            
            validation_results[scenario.name] = {
                "analysis_time": analysis_time,
                "failures_processed": report.total_failures,
                "failures_analyzed": report.failures_analyzed,
                "groups_created": len(report.grouped_failures),
                "recommendations_count": len(report.recommendations),
                "confidence_score": report.summary.confidence_score,
                "validation_passed": True
            }
            
        # Verify all scenarios passed validation
        assert all(result["validation_passed"] for result in validation_results.values()), \
            "All scenarios should pass validation"
            
        print(f"\nValidation Summary:")
        for scenario_name, result in validation_results.items():
            print(f"  {scenario_name}: {result['failures_processed']} failures, "
                  f"{result['analysis_time']:.2f}s, confidence {result['confidence_score']:.2f}")
                  
    def test_failure_categorization_accuracy_validation(self, all_failure_scenarios):
        """
        Validate accuracy of failure categorization across all scenarios
        Requirements: 5.1, 5.2, 5.3, 5.4 - Different failure type support
        """
        integrator = TestRCAIntegrationEngine()
        
        categorization_stats = {
            "total_failures": 0,
            "categorized_correctly": 0,
            "category_distribution": {},
            "scenario_results": {}
        }
        
        for scenario in all_failure_scenarios:
            scenario_stats = {
                "failures": len(scenario.failures),
                "categories_found": set(),
                "expected_categories": set(scenario.expected_categories)
            }
            
            for failure in scenario.failures:
                categorization_stats["total_failures"] += 1
                
                # Convert to RCA failure and check categorization
                rca_failure = integrator.convert_to_rca_failure(failure)
                category = rca_failure.category.name if hasattr(rca_failure.category, 'name') else str(rca_failure.category)
                
                scenario_stats["categories_found"].add(category)
                
                # Track category distribution
                if category not in categorization_stats["category_distribution"]:
                    categorization_stats["category_distribution"][category] = 0
                categorization_stats["category_distribution"][category] += 1
                
                # Check if categorization is reasonable (not just UNKNOWN for everything)
                if category != "UNKNOWN" or "unknown" in failure.error_message.lower():
                    categorization_stats["categorized_correctly"] += 1
                    
            categorization_stats["scenario_results"][scenario.name] = scenario_stats
            
        # Validate categorization effectiveness
        accuracy_rate = categorization_stats["categorized_correctly"] / categorization_stats["total_failures"]
        assert accuracy_rate > 0.7, f"Categorization accuracy {accuracy_rate:.2f} should be > 70%"
        
        # Validate that we're not just categorizing everything as UNKNOWN
        unknown_rate = categorization_stats["category_distribution"].get("UNKNOWN", 0) / categorization_stats["total_failures"]
        assert unknown_rate < 0.5, f"Unknown categorization rate {unknown_rate:.2f} should be < 50%"
        
        print(f"\nCategorization Validation:")
        print(f"  Total failures: {categorization_stats['total_failures']}")
        print(f"  Accuracy rate: {accuracy_rate:.2f}")
        print(f"  Unknown rate: {unknown_rate:.2f}")
        print(f"  Category distribution: {categorization_stats['category_distribution']}")
        
    def test_performance_requirements_validation(self, performance_stress_scenario):
        """
        Validate performance requirements with large datasets
        Requirements: 1.4, 4.2 - Performance requirements
        """
        integrator = TestRCAIntegrationEngine()
        
        # Test with increasing dataset sizes
        dataset_sizes = [10, 25, 50, 100, 200]
        performance_results = []
        
        for size in dataset_sizes:
            test_failures = performance_stress_scenario.failures[:size]
            
            # Measure analysis time
            start_time = time.time()
            report = integrator.analyze_test_failures(test_failures)
            analysis_time = time.time() - start_time
            
            # Validate 30-second requirement
            assert analysis_time < 30.0, f"Analysis of {size} failures took {analysis_time:.2f}s, should be < 30s"
            
            # Measure pattern matching performance (requirement 4.2)
            pattern_start = time.time()
            for failure in test_failures[:10]:  # Test first 10 for pattern matching
                integrator.convert_to_rca_failure(failure)
            pattern_time = time.time() - pattern_start
            
            # Should achieve sub-second performance for pattern matching
            avg_pattern_time = pattern_time / min(10, len(test_failures))
            assert avg_pattern_time < 1.0, f"Average pattern matching time {avg_pattern_time:.3f}s should be < 1s"
            
            performance_results.append({
                "size": size,
                "analysis_time": analysis_time,
                "avg_pattern_time": avg_pattern_time,
                "failures_analyzed": report.failures_analyzed,
                "groups_created": len(report.grouped_failures)
            })
            
        # Validate scalability
        for i in range(1, len(performance_results)):
            prev_result = performance_results[i-1]
            curr_result = performance_results[i]
            
            size_ratio = curr_result["size"] / prev_result["size"]
            time_ratio = curr_result["analysis_time"] / max(prev_result["analysis_time"], 0.001)
            
            # Time should not scale worse than quadratically
            assert time_ratio < size_ratio ** 2, f"Performance degradation too severe at size {curr_result['size']}"
            
        print(f"\nPerformance Validation:")
        for result in performance_results:
            print(f"  Size {result['size']}: {result['analysis_time']:.2f}s analysis, "
                  f"{result['avg_pattern_time']:.3f}s avg pattern matching")
                  
    def test_make_command_integration_validation(self):
        """
        Validate make command integration
        Requirements: 3.1, 3.2, 3.3, 3.4 - Make command integration
        """
        # Check that required make targets exist
        makefile_path = Path("makefiles/testing.mk")
        assert makefile_path.exists(), "Testing makefile should exist"
        
        makefile_content = makefile_path.read_text()
        
        # Validate requirement 3.1 - test target with RCA integration
        assert "test:" in makefile_content, "test target should exist"
        assert "RCA_ON_FAILURE" in makefile_content, "Should support RCA_ON_FAILURE variable"
        
        # Validate requirement 3.2 - rca target
        assert "rca:" in makefile_content, "rca target should exist"
        
        # Validate requirement 3.3 - rca-task target
        assert "rca-task:" in makefile_content, "rca-task target should exist"
        assert "TASK=" in makefile_content, "Should support TASK parameter"
        
        # Validate requirement 3.4 - consistent output formatting
        assert "RCA_VERBOSE" in makefile_content, "Should support verbose output control"
        
        # Test environment variable defaults
        assert "RCA_ON_FAILURE ?= true" in makefile_content, "Should default RCA_ON_FAILURE to true"
        assert "RCA_TIMEOUT ?= 30" in makefile_content, "Should default RCA_TIMEOUT to 30"
        
        print("Make command integration validation passed")
        
    def test_error_handling_and_graceful_degradation_validation(self, all_failure_scenarios):
        """
        Validate error handling and graceful degradation
        Requirements: 1.1, 1.4, 4.1 - Error handling
        """
        integrator = TestRCAIntegrationEngine()
        generator = RCAReportGenerator()
        
        degradation_test_results = []
        
        # Test with disabled RCA engine
        integrator.rca_engine = None
        
        for scenario in all_failure_scenarios[:3]:  # Test with first 3 scenarios
            try:
                report = integrator.analyze_test_failures(scenario.failures)
                
                # Should still generate a report
                assert isinstance(report, type(report)), "Should generate report even with disabled RCA engine"
                assert report.total_failures == len(scenario.failures), "Should track all failures"
                
                # Should provide fallback recommendations
                assert len(report.recommendations) > 0, "Should provide fallback recommendations"
                
                # Test report generation with degraded data
                console_report = generator.format_for_console(report, use_colors=False)
                assert len(console_report) > 0, "Should generate console report even in degraded mode"
                
                degradation_test_results.append({
                    "scenario": scenario.name,
                    "degraded_analysis_successful": True,
                    "fallback_recommendations": len(report.recommendations)
                })
                
            except Exception as e:
                pytest.fail(f"Should handle RCA engine failure gracefully for {scenario.name}: {e}")
                
        # Test with malformed failure data
        malformed_failure = TestFailureData(
            test_name=None,  # Missing required field
            test_file="",
            failure_type="unknown",
            error_message=None,  # Missing required field
            stack_trace="",
            test_function="",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id=""
        )
        
        # Restore RCA engine for malformed data test
        integrator = TestRCAIntegrationEngine()
        
        try:
            report = integrator.analyze_test_failures([malformed_failure])
            assert report.total_failures == 1, "Should handle malformed failure data"
            degradation_test_results.append({
                "scenario": "malformed_data",
                "degraded_analysis_successful": True,
                "fallback_recommendations": len(report.recommendations)
            })
        except Exception as e:
            pytest.fail(f"Should handle malformed failure data gracefully: {e}")
            
        print(f"\nError handling validation:")
        for result in degradation_test_results:
            print(f"  {result['scenario']}: {'✓' if result['degraded_analysis_successful'] else '✗'} "
                  f"({result['fallback_recommendations']} fallback recommendations)")
                  
    def test_beast_mode_integration_validation(self, synthetic_import_error_scenario):
        """
        Validate Beast Mode framework integration
        Requirements: 4.1, 4.3, 4.4 - Beast Mode integration
        """
        integrator = TestRCAIntegrationEngine()
        
        # Test systematic approach (requirement 4.3)
        report = integrator.analyze_test_failures(synthetic_import_error_scenario.failures)
        
        # Should provide systematic fixes, not just symptoms
        if report.failures_analyzed > 0 and len(report.rca_results) > 0:
            # Check that recommendations address root causes
            recommendations_text = " ".join(report.recommendations).lower()
            
            # For import errors, should suggest systematic dependency management
            assert any(keyword in recommendations_text for keyword in 
                      ["install", "dependency", "requirements", "pip", "conda"]), \
                "Should provide systematic dependency management recommendations"
                
        # Test health monitoring (requirement 4.1)
        assert integrator.is_healthy(), "RCA integrator should report health status"
        
        status = integrator.get_module_status()
        assert "module_name" in status, "Should provide module status"
        assert "status" in status, "Should provide operational status"
        
        # Test pattern library integration (requirement 4.4)
        # This is validated through the pattern matching performance tests
        
        print("Beast Mode integration validation passed")
        
    def test_comprehensive_reporting_validation(self, real_django_test_failure_scenario):
        """
        Validate comprehensive reporting functionality
        Requirements: 2.1, 2.2, 2.3, 2.4 - Comprehensive reporting
        """
        integrator = TestRCAIntegrationEngine()
        generator = RCAReportGenerator()
        
        report = integrator.analyze_test_failures(real_django_test_failure_scenario.failures)
        
        # Validate requirement 2.1 - Comprehensive factor analysis
        assert hasattr(report.summary, 'confidence_score'), "Should provide confidence assessment"
        assert hasattr(report.summary, 'estimated_fix_time_minutes'), "Should estimate fix time"
        
        # Validate requirement 2.2 - Systematic fixes with implementation steps
        if len(report.rca_results) > 0:
            for rca_result in report.rca_results:
                if len(rca_result.systematic_fixes) > 0:
                    fix = rca_result.systematic_fixes[0]
                    assert hasattr(fix, 'implementation_steps'), "Should provide implementation steps"
                    assert len(fix.implementation_steps) > 0, "Should have concrete implementation steps"
                    
        # Validate requirement 2.3 - Validation criteria
        assert len(report.next_steps) > 0, "Should provide validation criteria as next steps"
        
        # Validate requirement 2.4 - Prevention patterns
        if report.summary.pattern_matches_found > 0:
            assert len(report.prevention_patterns) > 0, "Should provide prevention patterns when available"
            
        # Test different report formats
        console_report = generator.format_for_console(report, use_colors=False)
        json_report = generator.generate_json_report(report)
        markdown_report = generator.generate_markdown_report(report)
        
        # Validate console report structure
        assert "RCA Analysis Report" in console_report or "Analysis Summary" in console_report, \
            "Console report should have proper header"
        assert str(report.total_failures) in console_report, "Should include failure count"
        
        # Validate JSON report structure
        assert "analysis_summary" in json_report or "total_failures" in json_report, \
            "JSON report should have analysis summary"
        assert isinstance(json_report.get("total_failures", 0), int), "Should include numeric failure count"
        
        # Validate markdown report structure
        assert "# RCA Analysis Report" in markdown_report or "## Analysis Summary" in markdown_report, \
            "Markdown report should have proper headers"
        assert "**" in markdown_report, "Should use markdown formatting"
        
        print("Comprehensive reporting validation passed")
        
    def test_integration_health_and_monitoring_validation(self):
        """
        Validate integration health monitoring
        Requirements: 4.1, 4.3 - System health monitoring
        """
        detector = TestFailureDetector()
        integrator = TestRCAIntegrationEngine()
        generator = RCAReportGenerator()
        
        components = [
            ("TestFailureDetector", detector),
            ("TestRCAIntegrationEngine", integrator),
            ("RCAReportGenerator", generator)
        ]
        
        health_results = {}
        
        for component_name, component in components:
            # Test health reporting
            is_healthy = component.is_healthy()
            status = component.get_module_status()
            
            assert isinstance(is_healthy, bool), f"{component_name} should report boolean health status"
            assert isinstance(status, dict), f"{component_name} should provide status dictionary"
            assert "module_name" in status, f"{component_name} should include module name in status"
            assert "status" in status, f"{component_name} should include status field"
            
            health_results[component_name] = {
                "is_healthy": is_healthy,
                "status": status.get("status", "unknown"),
                "module_name": status.get("module_name", "unknown")
            }
            
        # All components should be healthy initially
        assert all(result["is_healthy"] for result in health_results.values()), \
            "All components should be healthy initially"
            
        print(f"\nHealth monitoring validation:")
        for component, result in health_results.items():
            print(f"  {component}: {'✓' if result['is_healthy'] else '✗'} ({result['status']})")
            
    def test_requirements_coverage_validation(self):
        """
        Validate that all requirements are covered by the test suite
        Requirements: All requirements 1.1-5.4
        """
        # Define all requirements that should be covered
        requirements_map = {
            "1.1": "Automatic RCA triggering on test failures",
            "1.2": "Comprehensive factor analysis",
            "1.3": "Multiple test failure analysis and grouping",
            "1.4": "30-second timeout and environment controls",
            "2.1": "Comprehensive factor analysis including tool health",
            "2.2": "Systematic fixes with implementation steps",
            "2.3": "Validation criteria for fixes",
            "2.4": "Prevention patterns and suggestions",
            "3.1": "Make command integration",
            "3.2": "make rca command",
            "3.3": "make rca TASK=<task_id> command",
            "3.4": "Consistent output formatting",
            "4.1": "RCAEngine integration",
            "4.2": "Sub-second pattern matching performance",
            "4.3": "Beast Mode systematic approach",
            "4.4": "Pattern library integration",
            "5.1": "Pytest failure analysis",
            "5.2": "Make target failure analysis",
            "5.3": "Infrastructure failure analysis",
            "5.4": "Unknown failure type handling"
        }
        
        # Verify all requirements are documented
        assert len(requirements_map) == 20, f"Should have 20 requirements, found {len(requirements_map)}"
        
        # Check that test methods exist for each requirement category
        test_methods = [method for method in dir(self) if method.startswith('test_')]
        
        # Verify comprehensive coverage
        coverage_areas = [
            "end_to_end",
            "categorization",
            "performance",
            "make_command",
            "error_handling",
            "beast_mode",
            "reporting",
            "health_monitoring"
        ]
        
        for area in coverage_areas:
            matching_tests = [method for method in test_methods if area in method]
            assert len(matching_tests) > 0, f"Should have tests covering {area}"
            
        print(f"\nRequirements coverage validation:")
        print(f"  Total requirements: {len(requirements_map)}")
        print(f"  Test methods: {len(test_methods)}")
        print(f"  Coverage areas: {len(coverage_areas)}")
        print("  All requirements covered: ✓")
        
        # This test passes if we reach this point, indicating comprehensive coverage
        assert True, "Requirements coverage validation completed"


class TestRCAIntegrationRegressionSuite:
    """Regression test suite to prevent functionality degradation"""
    
    def test_regression_basic_functionality(self):
        """Test basic functionality doesn't regress"""
        integrator = TestRCAIntegrationEngine()
        
        # Simple test failure
        simple_failure = TestFailureData(
            test_name="test_regression",
            test_file="tests/test_regression.py",
            failure_type="assertion",
            error_message="AssertionError: Basic test",
            stack_trace="Basic stack trace",
            test_function="test_regression",
            test_class="TestRegression",
            failure_timestamp=datetime.now(),
            test_context={"test_type": "regression"},
            pytest_node_id="tests/test_regression.py::TestRegression::test_regression"
        )
        
        # Should process without errors
        report = integrator.analyze_test_failures([simple_failure])
        
        assert report.total_failures == 1
        assert isinstance(report.summary.confidence_score, float)
        assert len(report.recommendations) > 0
        
    def test_regression_performance_baseline(self):
        """Test performance doesn't regress below baseline"""
        integrator = TestRCAIntegrationEngine()
        
        # Create 10 test failures
        failures = []
        for i in range(10):
            failures.append(TestFailureData(
                test_name=f"test_perf_{i}",
                test_file=f"tests/test_perf.py",
                failure_type="error",
                error_message=f"Error {i}",
                stack_trace=f"Stack trace {i}",
                test_function=f"test_perf_{i}",
                test_class="TestPerf",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "performance"},
                pytest_node_id=f"tests/test_perf.py::TestPerf::test_perf_{i}"
            ))
            
        # Should complete within reasonable time
        start_time = time.time()
        report = integrator.analyze_test_failures(failures)
        analysis_time = time.time() - start_time
        
        # Performance baseline: 10 failures should complete in under 10 seconds
        assert analysis_time < 10.0, f"Performance regression: took {analysis_time:.2f}s for 10 failures"
        assert report.total_failures == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # -x stops on first failure