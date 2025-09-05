"""
Unit tests for RCA Report Generation System
Tests report generation, formatting, and output for different formats
Requirements: 2.2, 2.3, 2.4 - Comprehensive testing of report generation functionality
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.beast_mode.testing.rca_report_generator import (
    RCAReportGenerator, ReportConfiguration, ReportFormat, ReportSection,
    FormattedReport, FormattedReportSection, ConsoleColors
)
from src.beast_mode.testing.rca_integration import (
    TestFailureData, TestRCASummaryData, TestRCAReportData
)
from src.beast_mode.analysis.rca_engine import (
    RCAResult, Failure, FailureCategory, RootCauseType, RootCause,
    SystematicFix, PreventionPattern, ComprehensiveAnalysisResult
)


class TestRCAReportGenerator:
    """Test suite for RCA Report Generator"""
    
    @pytest.fixture
    def report_generator(self):
        """Create RCA report generator instance"""
        return RCAReportGenerator()
        
    @pytest.fixture
    def sample_test_failure(self):
        """Create sample test failure data"""
        return TestFailureData(
            test_name="test_sample_function",
            test_file="tests/test_sample.py",
            failure_type="assertion",
            error_message="AssertionError: Expected 5, got 3",
            stack_trace="Traceback (most recent call last):\n  File test_sample.py, line 10\n    assert result == 5",
            test_function="test_sample_function",
            test_class="TestSample",
            failure_timestamp=datetime.now(),
            test_context={"test_data": "sample"},
            pytest_node_id="tests/test_sample.py::TestSample::test_sample_function"
        )
        
    @pytest.fixture
    def sample_rca_result(self, sample_test_failure):
        """Create sample RCA result"""
        failure = Failure(
            failure_id="test_failure_123",
            timestamp=datetime.now(),
            component="test:tests/test_sample.py",
            error_message="AssertionError: Expected 5, got 3",
            stack_trace="Traceback...",
            context={"test_file": "tests/test_sample.py"},
            category=FailureCategory.UNKNOWN
        )
        
        root_cause = RootCause(
            cause_type=RootCauseType.BROKEN_DEPENDENCIES,
            description="Missing dependency causing calculation error",
            evidence=["Import error in logs", "Missing package in requirements"],
            confidence_score=0.8,
            impact_severity="high",
            affected_components=["test:tests/test_sample.py"]
        )
        
        systematic_fix = SystematicFix(
            fix_id="fix_dependency_123",
            root_cause=root_cause,
            fix_description="Install missing dependency and update requirements",
            implementation_steps=[
                "Install missing package",
                "Update requirements.txt",
                "Verify tests pass"
            ],
            validation_criteria=[
                "Package is installed",
                "Tests pass without errors"
            ],
            rollback_plan="Remove package if issues occur",
            estimated_time_minutes=10
        )
        
        prevention_pattern = PreventionPattern(
            pattern_id="pattern_dep_123",
            pattern_name="Dependency Validation Pattern",
            failure_signature="missing_dependency",
            root_cause_pattern="broken_dependencies",
            prevention_steps=["Add dependency checks", "Validate requirements"],
            detection_criteria=["ImportError in logs"],
            automated_checks=["pip check"],
            pattern_hash="abc123"
        )
        
        return RCAResult(
            failure=failure,
            analysis=ComprehensiveAnalysisResult(
                symptoms=["missing_dependency"],
                tool_health_status={"pip": "healthy"},
                dependency_analysis={"missing_packages": ["numpy"]},
                configuration_analysis={"requirements_outdated": True},
                installation_integrity={"python_version": "3.9"},
                environmental_factors={"path_set": True},
                analysis_confidence=0.8
            ),
            root_causes=[root_cause],
            systematic_fixes=[systematic_fix],
            validation_results=[],
            prevention_patterns=[prevention_pattern],
            total_analysis_time_seconds=2.5,
            rca_confidence_score=0.8
        )
        
    @pytest.fixture
    def sample_rca_report(self, sample_test_failure, sample_rca_result):
        """Create sample RCA report data"""
        summary = TestRCASummaryData(
            most_common_root_causes=[(RootCauseType.BROKEN_DEPENDENCIES, 1)],
            systematic_fixes_available=1,
            pattern_matches_found=1,
            estimated_fix_time_minutes=10,
            confidence_score=0.8,
            critical_issues=["Missing critical dependency"]
        )
        
        return TestRCAReportData(
            analysis_timestamp=datetime.now(),
            total_failures=1,
            failures_analyzed=1,
            grouped_failures={"dependency_errors": [sample_test_failure]},
            rca_results=[sample_rca_result],
            summary=summary,
            recommendations=["Install missing dependencies", "Update requirements.txt"],
            prevention_patterns=[sample_rca_result.prevention_patterns[0]],
            next_steps=["Run pip install", "Verify tests pass", "Update documentation"]
        )
        
    def test_report_generator_initialization(self, report_generator):
        """Test RCA report generator initialization"""
        assert report_generator.module_name == "rca_report_generator"
        assert report_generator.reports_generated == 0
        assert report_generator.console_reports == 0
        assert report_generator.json_reports == 0
        assert report_generator.markdown_reports == 0
        assert report_generator.is_healthy()
        
    def test_module_status(self, report_generator):
        """Test module status reporting"""
        status = report_generator.get_module_status()
        
        assert status["module_name"] == "rca_report_generator"
        assert status["status"] == "operational"
        assert status["reports_generated"] == 0
        assert status["degradation_active"] is False
        
    def test_health_indicators(self, report_generator):
        """Test health indicators"""
        health = report_generator.get_health_indicators()
        
        assert "generation_capability" in health
        assert "format_support" in health
        assert "performance" in health
        assert health["generation_capability"]["status"] == "healthy"
        
    def test_generate_console_report(self, report_generator, sample_rca_report):
        """Test console report generation"""
        config = ReportConfiguration(
            format=ReportFormat.CONSOLE,
            color_output=False,  # Disable colors for testing
            include_sections=[ReportSection.HEADER, ReportSection.SUMMARY, ReportSection.RECOMMENDATIONS]
        )
        
        formatted_report = report_generator.generate_report(sample_rca_report, config)
        
        assert formatted_report.format == ReportFormat.CONSOLE
        assert len(formatted_report.sections) == 3
        assert formatted_report.total_length > 0
        assert "Test RCA Analysis Report" in formatted_report.sections[0].content
        assert "Analysis Summary" in formatted_report.sections[1].content
        assert "Actionable Recommendations" in formatted_report.sections[2].content
        
    def test_generate_json_report(self, report_generator, sample_rca_report):
        """Test JSON report generation"""
        json_data = report_generator.generate_json_report(sample_rca_report)
        
        assert "report_metadata" in json_data
        assert "analysis_summary" in json_data
        assert "root_causes" in json_data
        assert "recommendations" in json_data
        assert "next_steps" in json_data
        
        # Verify specific data
        assert json_data["analysis_summary"]["total_failures"] == 1
        assert json_data["analysis_summary"]["confidence_score"] == 0.8
        assert len(json_data["recommendations"]) == 2
        assert len(json_data["next_steps"]) == 3
        
    def test_generate_markdown_report(self, report_generator, sample_rca_report):
        """Test markdown report generation"""
        markdown_content = report_generator.generate_markdown_report(sample_rca_report)
        
        assert "# 🔍 Test RCA Analysis Report" in markdown_content
        assert "## 📊 Analysis Summary" in markdown_content
        assert "## 💡 Actionable Recommendations" in markdown_content
        assert "## 🚀 Next Steps" in markdown_content
        
        # Verify markdown formatting
        assert "**Total Failures:** 1" in markdown_content
        assert "**Analysis Confidence:** 80.0%" in markdown_content
        
    def test_format_for_console(self, report_generator, sample_rca_report):
        """Test console formatting method"""
        console_output = report_generator.format_for_console(sample_rca_report, use_colors=False)
        
        assert "Test RCA Analysis Report" in console_output
        assert "Analysis Summary" in console_output
        assert "Total Failures:" in console_output
        assert "Actionable Recommendations" in console_output
        
    def test_format_for_console_with_colors(self, report_generator, sample_rca_report):
        """Test console formatting with colors"""
        console_output = report_generator.format_for_console(sample_rca_report, use_colors=True)
        
        # Should contain ANSI color codes
        assert "\033[" in console_output  # ANSI escape sequence
        assert "Test RCA Analysis Report" in console_output
        
    def test_console_colors_colorize(self):
        """Test console color utility"""
        # Test with colors enabled
        colored_text = ConsoleColors.colorize("test", ConsoleColors.RED, use_color=True)
        assert colored_text.startswith('\033[91m')
        assert colored_text.endswith('\033[0m')
        assert "test" in colored_text
        
        # Test with colors disabled
        plain_text = ConsoleColors.colorize("test", ConsoleColors.RED, use_color=False)
        assert plain_text == "test"
        assert '\033[' not in plain_text
        
    def test_report_configuration_defaults(self):
        """Test default report configuration"""
        config = ReportConfiguration()
        
        assert config.format == ReportFormat.CONSOLE
        assert len(config.include_sections) == len(list(ReportSection))  # All sections by default
        assert config.max_failures_displayed == 10
        assert config.max_recommendations == 5
        assert config.include_stack_traces is False
        assert config.color_output is True
        assert config.verbose_mode is False
        assert config.output_file is None
        
    def test_generate_all_sections(self, report_generator, sample_rca_report):
        """Test generation of all report sections"""
        config = ReportConfiguration(
            format=ReportFormat.CONSOLE,
            include_sections=list(ReportSection),
            color_output=False
        )
        
        formatted_report = report_generator.generate_report(sample_rca_report, config)
        
        # Should have all sections
        assert len(formatted_report.sections) == len(ReportSection)
        
        section_types = [section.section_type for section in formatted_report.sections]
        for section_type in ReportSection:
            assert section_type in section_types
            
    def test_report_with_multiple_failures(self, report_generator, sample_test_failure, sample_rca_result):
        """Test report generation with multiple failures"""
        # Create additional failures
        failure2 = TestFailureData(
            test_name="test_another_function",
            test_file="tests/test_another.py",
            failure_type="error",
            error_message="ImportError: No module named 'missing_module'",
            stack_trace="Traceback...",
            test_function="test_another_function",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_another.py::test_another_function"
        )
        
        summary = TestRCASummaryData(
            most_common_root_causes=[
                (RootCauseType.BROKEN_DEPENDENCIES, 2),
                (RootCauseType.MISSING_FILES, 1)
            ],
            systematic_fixes_available=3,
            pattern_matches_found=2,
            estimated_fix_time_minutes=25,
            confidence_score=0.75,
            critical_issues=["Missing critical dependency", "Configuration error"]
        )
        
        multi_failure_report = TestRCAReportData(
            analysis_timestamp=datetime.now(),
            total_failures=2,
            failures_analyzed=2,
            grouped_failures={
                "dependency_errors": [sample_test_failure],
                "import_errors": [failure2]
            },
            rca_results=[sample_rca_result, sample_rca_result],  # Reuse for simplicity
            summary=summary,
            recommendations=["Fix dependencies", "Update imports", "Check configuration"],
            prevention_patterns=[sample_rca_result.prevention_patterns[0]],
            next_steps=["Install packages", "Update code", "Run tests", "Document changes"]
        )
        
        formatted_report = report_generator.generate_report(multi_failure_report)
        
        assert formatted_report.metadata["total_failures"] == 2
        assert formatted_report.metadata["systematic_fixes"] == 3
        
    def test_report_with_critical_issues(self, report_generator, sample_rca_report):
        """Test report generation with critical issues"""
        # Add critical issues to summary
        sample_rca_report.summary.critical_issues = [
            "Critical security vulnerability",
            "System corruption detected",
            "Data loss risk"
        ]
        
        console_output = report_generator.format_for_console(sample_rca_report, use_colors=False)
        
        assert "Critical Issues:" in console_output
        assert "Critical security vulnerability" in console_output
        assert "System corruption detected" in console_output
        
    def test_report_with_no_data(self, report_generator):
        """Test report generation with minimal/no data"""
        empty_summary = TestRCASummaryData(
            most_common_root_causes=[],
            systematic_fixes_available=0,
            pattern_matches_found=0,
            estimated_fix_time_minutes=0,
            confidence_score=0.0,
            critical_issues=[]
        )
        
        empty_report = TestRCAReportData(
            analysis_timestamp=datetime.now(),
            total_failures=0,
            failures_analyzed=0,
            grouped_failures={},
            rca_results=[],
            summary=empty_summary,
            recommendations=[],
            prevention_patterns=[],
            next_steps=[]
        )
        
        formatted_report = report_generator.generate_report(empty_report)
        
        assert formatted_report.metadata["total_failures"] == 0
        assert len(formatted_report.sections) > 0  # Should still have sections
        
    def test_verbose_mode_report(self, report_generator, sample_rca_report):
        """Test report generation in verbose mode"""
        config = ReportConfiguration(
            format=ReportFormat.CONSOLE,
            include_sections=[ReportSection.SYSTEMATIC_FIXES],
            verbose_mode=True,
            color_output=False
        )
        
        formatted_report = report_generator.generate_report(sample_rca_report, config)
        
        # Verbose mode should include implementation steps
        fixes_section = formatted_report.sections[0]
        assert "Steps:" in fixes_section.content
        assert "Install missing package" in fixes_section.content
        
    def test_report_with_stack_traces(self, report_generator, sample_rca_report):
        """Test report generation with stack traces included"""
        config = ReportConfiguration(
            format=ReportFormat.CONSOLE,
            include_sections=[ReportSection.FAILURES],
            include_stack_traces=True,
            color_output=False
        )
        
        formatted_report = report_generator.generate_report(sample_rca_report, config)
        
        failures_section = formatted_report.sections[0]
        assert "Error:" in failures_section.content
        
    def test_report_limits(self, report_generator, sample_rca_report):
        """Test report generation with limits"""
        config = ReportConfiguration(
            format=ReportFormat.CONSOLE,
            include_sections=[ReportSection.RECOMMENDATIONS],
            max_recommendations=2,
            color_output=False
        )
        
        # Add more recommendations to test limit
        sample_rca_report.recommendations = [
            "Recommendation 1",
            "Recommendation 2", 
            "Recommendation 3",
            "Recommendation 4"
        ]
        
        formatted_report = report_generator.generate_report(sample_rca_report, config)
        
        recommendations_section = formatted_report.sections[0]
        # Should only show first 2 recommendations
        assert "Recommendation 1" in recommendations_section.content
        assert "Recommendation 2" in recommendations_section.content
        # Should not show recommendations 3 and 4 due to limit
        
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', create=True)
    def test_save_report_to_file(self, mock_open, mock_mkdir, report_generator, sample_rca_report):
        """Test saving report to file"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        config = ReportConfiguration(
            format=ReportFormat.MARKDOWN,
            output_file="reports/test_report.md"
        )
        
        formatted_report = report_generator.generate_report(sample_rca_report, config)
        
        # Verify file operations
        mock_mkdir.assert_called_once()
        mock_open.assert_called_once()
        mock_file.write.assert_called_once()
        
    def test_error_handling_in_section_generation(self, report_generator, sample_rca_report):
        """Test error handling during section generation"""
        # Mock a section generator to raise an exception
        with patch.object(report_generator, '_generate_summary_section', side_effect=Exception("Test error")):
            config = ReportConfiguration(
                format=ReportFormat.CONSOLE,
                include_sections=[ReportSection.SUMMARY],
                color_output=False
            )
            
            formatted_report = report_generator.generate_report(sample_rca_report, config)
            
            # Should have error section instead of normal section
            assert len(formatted_report.sections) == 1
            error_section = formatted_report.sections[0]
            assert "Error in summary" in error_section.title
            assert "Test error" in error_section.content
            
    def test_json_report_serialization(self, report_generator, sample_rca_report):
        """Test JSON report can be properly serialized"""
        json_data = report_generator.generate_json_report(sample_rca_report)
        
        # Should be able to serialize to JSON string
        json_string = json.dumps(json_data)
        assert len(json_string) > 0
        
        # Should be able to deserialize back
        parsed_data = json.loads(json_string)
        assert parsed_data["analysis_summary"]["total_failures"] == 1
        
    def test_report_generation_metrics(self, report_generator, sample_rca_report):
        """Test report generation updates metrics correctly"""
        initial_count = report_generator.reports_generated
        initial_console = report_generator.console_reports
        
        # Generate console report
        report_generator.format_for_console(sample_rca_report)
        
        assert report_generator.reports_generated == initial_count + 1
        assert report_generator.console_reports == initial_console + 1
        
        # Generate JSON report
        initial_json = report_generator.json_reports
        report_generator.generate_json_report(sample_rca_report)
        
        assert report_generator.json_reports == initial_json + 1
        
    def test_report_metadata_accuracy(self, report_generator, sample_rca_report):
        """Test report metadata is accurate"""
        formatted_report = report_generator.generate_report(sample_rca_report)
        
        metadata = formatted_report.metadata
        assert metadata["total_failures"] == sample_rca_report.total_failures
        assert metadata["failures_analyzed"] == sample_rca_report.failures_analyzed
        assert metadata["systematic_fixes"] == sample_rca_report.summary.systematic_fixes_available
        assert metadata["confidence_score"] == sample_rca_report.summary.confidence_score
        
    def test_different_format_consistency(self, report_generator, sample_rca_report):
        """Test that different formats contain consistent information"""
        # Generate all formats
        console_output = report_generator.format_for_console(sample_rca_report, use_colors=False)
        json_data = report_generator.generate_json_report(sample_rca_report)
        markdown_output = report_generator.generate_markdown_report(sample_rca_report)
        
        # All should contain key information
        assert "Total Failures" in console_output or "total_failures" in str(json_data)
        assert str(sample_rca_report.total_failures) in console_output
        assert json_data["analysis_summary"]["total_failures"] == sample_rca_report.total_failures
        assert str(sample_rca_report.total_failures) in markdown_output
        
        # All should contain recommendations
        assert "Recommendations" in console_output
        assert "recommendations" in json_data
        assert "Recommendations" in markdown_output


class TestReportConfigurationValidation:
    """Test report configuration validation and edge cases"""
    
    def test_report_configuration_validation(self):
        """Test report configuration with various settings"""
        config = ReportConfiguration(
            format=ReportFormat.JSON,
            include_sections=[ReportSection.HEADER, ReportSection.SUMMARY],
            max_failures_displayed=5,
            max_recommendations=3,
            include_stack_traces=True,
            color_output=False,
            verbose_mode=True,
            output_file="test_output.json"
        )
        
        assert config.format == ReportFormat.JSON
        assert len(config.include_sections) == 2
        assert config.max_failures_displayed == 5
        assert config.max_recommendations == 3
        assert config.include_stack_traces is True
        assert config.color_output is False
        assert config.verbose_mode is True
        assert config.output_file == "test_output.json"
        
    def test_formatted_report_section_creation(self):
        """Test formatted report section creation"""
        section = FormattedReportSection(
            section_type=ReportSection.SUMMARY,
            title="Test Summary",
            content="This is test content",
            metadata={"test_key": "test_value"}
        )
        
        assert section.section_type == ReportSection.SUMMARY
        assert section.title == "Test Summary"
        assert section.content == "This is test content"
        assert section.metadata["test_key"] == "test_value"
        
    def test_formatted_report_creation(self):
        """Test formatted report creation"""
        sections = [
            FormattedReportSection(
                section_type=ReportSection.HEADER,
                title="Header",
                content="Header content"
            )
        ]
        
        report = FormattedReport(
            report_id="test_report_123",
            generation_timestamp=datetime.now(),
            format=ReportFormat.CONSOLE,
            sections=sections,
            total_length=100,
            metadata={"test": "data"}
        )
        
        assert report.report_id == "test_report_123"
        assert report.format == ReportFormat.CONSOLE
        assert len(report.sections) == 1
        assert report.total_length == 100
        assert report.metadata["test"] == "data"


if __name__ == "__main__":
    pytest.main([__file__])