"""
Tests for ComplianceOrchestrator core functionality.

This module tests the basic workflow coordination and infrastructure
of the compliance checking system.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.beast_mode.compliance.orchestrator import ComplianceOrchestrator
from src.beast_mode.compliance.models import (
    ComplianceAnalysisResult,
    Phase2ValidationResult,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity
)
from src.beast_mode.compliance.interfaces import ComplianceValidator, ValidationContext


class MockValidator(ComplianceValidator):
    """Mock validator for testing."""
    
    def validate(self, target):
        return []
    
    def get_validator_name(self):
        return "mock_validator"


class TestComplianceOrchestrator:
    """Test cases for ComplianceOrchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = ComplianceOrchestrator(".")
        
        assert orchestrator.repository_path == Path(".")
        assert orchestrator._config["target_branch"] == "main"
        assert orchestrator._config["base_branch"] == "origin/master"
        assert orchestrator._config["test_coverage_baseline"] == 96.7
    
    def test_validator_registration(self):
        """Test validator registration."""
        orchestrator = ComplianceOrchestrator(".")
        validator = MockValidator()
        
        orchestrator.register_validator(validator)
        
        assert "mock_validator" in orchestrator._validators
        assert orchestrator._validators["mock_validator"] == validator
    
    def test_get_module_status(self):
        """Test ReflectiveModule status reporting."""
        orchestrator = ComplianceOrchestrator(".")
        status = orchestrator.get_module_status()
        
        assert status["module_name"] == "ComplianceOrchestrator"
        assert "repository_path" in status
        assert "registered_validators" in status
        assert "configuration" in status
        assert "is_healthy" in status
    
    def test_is_healthy_with_valid_repo(self):
        """Test health check with valid repository."""
        # Use current directory which should have .git
        orchestrator = ComplianceOrchestrator(".")
        
        # Should be healthy if .git directory exists
        health_status = orchestrator.is_healthy()
        assert isinstance(health_status, bool)
    
    def test_is_healthy_with_invalid_repo(self):
        """Test health check with invalid repository."""
        orchestrator = ComplianceOrchestrator("/nonexistent/path")
        
        assert not orchestrator.is_healthy()
    
    def test_analyze_commits_ahead_of_main_basic(self):
        """Test basic compliance analysis workflow."""
        orchestrator = ComplianceOrchestrator(".")
        
        result = orchestrator.analyze_commits_ahead_of_main()
        
        assert isinstance(result, ComplianceAnalysisResult)
        assert result.overall_compliance_score >= 0
        assert isinstance(result.commits_analyzed, list)
        assert isinstance(result.critical_issues, list)
        assert isinstance(result.recommendations, list)
    
    def test_validate_phase2_completion_basic(self):
        """Test basic Phase 2 validation workflow."""
        orchestrator = ComplianceOrchestrator(".")
        
        result = orchestrator.validate_phase2_completion()
        
        assert isinstance(result, Phase2ValidationResult)
        assert result.phase3_readiness_score >= 0
        assert isinstance(result.claimed_complete_tasks, list)
        assert isinstance(result.actually_implemented_tasks, list)
        assert isinstance(result.missing_implementations, list)
    
    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        orchestrator = ComplianceOrchestrator(".")
        
        report = orchestrator.generate_compliance_report()
        
        assert isinstance(report, str)
        assert "Beast Mode Framework Compliance Report" in report
        assert "Overall Compliance Score" in report
        assert "Analysis Summary" in report
    
    def test_error_handling_in_analysis(self):
        """Test error handling during compliance analysis."""
        orchestrator = ComplianceOrchestrator(".")
        
        # Mock a method to raise an exception
        with patch.object(orchestrator, '_get_commits_ahead_of_main', side_effect=Exception("Test error")):
            result = orchestrator.analyze_commits_ahead_of_main()
            
            assert len(result.critical_issues) > 0
            assert any(issue.severity == IssueSeverity.CRITICAL for issue in result.critical_issues)
            assert any("Compliance analysis failed" in issue.description for issue in result.critical_issues)
    
    def test_calculate_overall_compliance_score(self):
        """Test overall compliance score calculation."""
        orchestrator = ComplianceOrchestrator(".")
        
        # Create a mock result with known scores
        result = ComplianceAnalysisResult()
        result.rdi_compliance.compliance_score = 80.0
        result.rm_compliance.compliance_score = 90.0
        result.test_coverage_status.current_coverage = 95.0
        result.task_completion_reconciliation.reconciliation_score = 85.0
        
        score = orchestrator._calculate_overall_compliance_score(result)
        
        expected_score = (80.0 + 90.0 + 95.0 + 85.0) / 4
        assert score == expected_score
    
    def test_assess_phase3_readiness(self):
        """Test Phase 3 readiness assessment."""
        orchestrator = ComplianceOrchestrator(".")
        
        # Test case: ready for Phase 3
        result = ComplianceAnalysisResult()
        result.overall_compliance_score = 85.0
        result.critical_issues = []
        result.test_coverage_status.current_coverage = 96.0
        result.test_coverage_status.baseline_coverage = 96.7
        
        assert orchestrator._assess_phase3_readiness(result)
        
        # Test case: not ready due to low compliance score
        result.overall_compliance_score = 70.0
        assert not orchestrator._assess_phase3_readiness(result)
        
        # Test case: not ready due to critical issues
        result.overall_compliance_score = 85.0
        result.critical_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                severity=IssueSeverity.CRITICAL,
                description="Critical issue"
            )
        ]
        assert not orchestrator._assess_phase3_readiness(result)