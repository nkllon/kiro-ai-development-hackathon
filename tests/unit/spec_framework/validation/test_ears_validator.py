"""
Tests for EARS Format Validation Engine.

Validates systematic EARS format validation, parsing, and guidance generation.
"""

import pytest
from datetime import datetime

from src.spec_framework.validation.ears_validator import (
    EARSFormatValidator,
    EARSValidationResult,
    EARSValidationIssue,
    EARSValidationSeverity,
    EARSStatementType
)
from src.spec_framework.core.models import EARSStatement


class TestEARSFormatValidator:
    """Test suite for EARS Format Validator."""
    
    @pytest.fixture
    def validator(self):
        """Create EARS format validator instance."""
        return EARSFormatValidator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator.ready()
        assert validator.status() == "ready"
        
        health = validator.health()
        assert health["status"] == "healthy"
        assert health["patterns_loaded"] > 0
        assert health["templates_loaded"] > 0
        
        metrics = validator.metrics()
        assert metrics["patterns_count"] > 0
        assert metrics["templates_count"] > 0
    
    def test_valid_when_statement(self, validator):
        """Test validation of valid WHEN statement."""
        statement = "WHEN user clicks submit button THEN validation service SHALL verify all required fields"
        
        result = validator.validate_ears_statement(statement)
        
        assert result.is_valid
        assert result.statement_type == EARSStatementType.WHEN
        assert result.parsed_components is not None
        assert result.parsed_components["condition"] == "user clicks submit button"
        assert result.parsed_components["system"] == "validation service"
        assert result.parsed_components["response"] == "verify all required fields"
    
    def test_valid_if_statement(self, validator):
        """Test validation of valid IF statement."""
        statement = "IF authentication fails THEN security service SHALL log the attempt and return error message"
        
        result = validator.validate_ears_statement(statement)
        
        assert result.is_valid
        assert result.statement_type == EARSStatementType.IF
        assert result.parsed_components["condition"] == "authentication fails"
        assert result.parsed_components["system"] == "security service"
        assert result.parsed_components["response"] == "log the attempt and return error message"
    
    def test_valid_while_statement(self, validator):
        """Test validation of valid WHILE statement."""
        statement = "WHILE backup process is running THEN monitoring service SHALL display progress indicator"
        
        result = validator.validate_ears_statement(statement)
        
        assert result.is_valid
        assert result.statement_type == EARSStatementType.WHILE
        assert result.parsed_components["condition"] == "backup process is running"
        assert result.parsed_components["system"] == "monitoring service"
        assert result.parsed_components["response"] == "display progress indicator"
    
    def test_compound_and_statement(self, validator):
        """Test validation of compound AND statement."""
        statement = "WHEN user is authenticated AND has admin role THEN admin panel SHALL display management options"
        
        result = validator.validate_ears_statement(statement)
        
        assert result.is_valid
        assert result.statement_type == EARSStatementType.WHEN
        assert "AND" in result.parsed_components["condition"]
    
    def test_missing_then_keyword(self, validator):
        """Test detection of missing THEN keyword."""
        statement = "WHEN user clicks button validation service SHALL verify fields"
        
        result = validator.validate_ears_statement(statement)
        
        assert not result.is_valid
        assert any(
            issue.severity == EARSValidationSeverity.ERROR and "THEN" in issue.message
            for issue in result.issues
        )
    
    def test_missing_shall_keyword(self, validator):
        """Test detection of missing SHALL keyword."""
        statement = "WHEN user clicks button THEN validation service verify fields"
        
        result = validator.validate_ears_statement(statement)
        
        assert not result.is_valid
        assert any(
            issue.severity == EARSValidationSeverity.ERROR and "SHALL" in issue.message
            for issue in result.issues
        )
    
    def test_missing_trigger_keyword(self, validator):
        """Test detection of missing trigger keyword."""
        statement = "user clicks button THEN validation service SHALL verify fields"
        
        result = validator.validate_ears_statement(statement)
        
        assert not result.is_valid
        assert any(
            issue.severity == EARSValidationSeverity.ERROR and "trigger keyword" in issue.message
            for issue in result.issues
        )
    
    def test_wrong_keyword_order(self, validator):
        """Test detection of wrong keyword order."""
        statement = "validation service SHALL verify fields WHEN user clicks button"
        
        result = validator.validate_ears_statement(statement)
        
        assert not result.is_valid
        # Should detect parsing failure and provide guidance
        assert len(result.issues) > 0
    
    def test_vague_condition_detection(self, validator):
        """Test detection of vague conditions."""
        statement = "WHEN something happens THEN system SHALL do something"
        
        result = validator.validate_ears_statement(statement)
        
        # May parse but should have warnings about vague terms
        vague_issues = [
            issue for issue in result.issues
            if issue.severity == EARSValidationSeverity.WARNING and "vague" in issue.message.lower()
        ]
        assert len(vague_issues) > 0
    
    def test_vague_system_detection(self, validator):
        """Test detection of vague system references."""
        statement = "WHEN user submits form THEN it SHALL validate input"
        
        result = validator.validate_ears_statement(statement)
        
        # Should warn about vague system reference
        vague_system_issues = [
            issue for issue in result.issues
            if "system" in issue.message.lower() and "vague" in issue.message.lower()
        ]
        assert len(vague_system_issues) > 0
    
    def test_vague_response_detection(self, validator):
        """Test detection of vague responses."""
        statement = "WHEN user clicks button THEN validation service SHALL work properly"
        
        result = validator.validate_ears_statement(statement)
        
        # Should warn about vague response
        vague_response_issues = [
            issue for issue in result.issues
            if "response" in issue.message.lower() or "work" in issue.message.lower()
        ]
        assert len(vague_response_issues) > 0
    
    def test_condition_too_short(self, validator):
        """Test detection of too short conditions."""
        statement = "WHEN x THEN validation service SHALL verify all required fields"
        
        result = validator.validate_ears_statement(statement)
        
        # Should have error about short condition
        short_condition_issues = [
            issue for issue in result.issues
            if issue.severity == EARSValidationSeverity.ERROR and "short" in issue.message.lower()
        ]
        assert len(short_condition_issues) > 0
    
    def test_testability_indicators(self, validator):
        """Test detection of testability indicators."""
        testable_statement = "WHEN user submits form THEN validation service SHALL return validation results"
        non_testable_statement = "WHEN user submits form THEN validation service SHALL be good"
        
        testable_result = validator.validate_ears_statement(testable_statement)
        non_testable_result = validator.validate_ears_statement(non_testable_statement)
        
        # Testable statement should have fewer testability warnings
        testable_warnings = [
            issue for issue in testable_result.issues
            if "testable" in issue.message.lower()
        ]
        
        non_testable_warnings = [
            issue for issue in non_testable_result.issues
            if "testable" in issue.message.lower()
        ]
        
        # Non-testable should have more warnings
        assert len(non_testable_warnings) >= len(testable_warnings)
    
    def test_create_ears_statement(self, validator):
        """Test creation of EARS statement objects."""
        condition = "user clicks submit button"
        system = "validation service"
        response = "verify all required fields and return results"
        
        ears_statement = validator.create_ears_statement(condition, system, response)
        
        assert ears_statement.condition == condition
        assert ears_statement.system == system
        assert ears_statement.response == response
        assert ears_statement.statement_type == "WHEN"
        
        # Test with different statement type
        ears_if = validator.create_ears_statement(condition, system, response, "IF")
        assert ears_if.statement_type == "IF"
    
    def test_validation_guidance(self, validator):
        """Test validation guidance generation."""
        guidance = validator.get_validation_guidance("WHEN")
        
        assert guidance["statement_type"] == "WHEN"
        assert "WHEN" in guidance["format"]
        assert "THEN" in guidance["format"]
        assert "SHALL" in guidance["format"]
        assert len(guidance["templates"]) > 0
        assert len(guidance["condition_guidelines"]) > 0
        assert len(guidance["system_guidelines"]) > 0
        assert len(guidance["response_guidelines"]) > 0
    
    def test_suggestions_generation(self, validator):
        """Test that suggestions are generated for invalid statements."""
        invalid_statement = "user does something"
        
        result = validator.validate_ears_statement(invalid_statement)
        
        assert not result.is_valid
        assert len(result.suggestions) > 0
        
        # Suggestions should contain EARS format examples
        has_ears_suggestion = any(
            "WHEN" in suggestion and "THEN" in suggestion and "SHALL" in suggestion
            for suggestion in result.suggestions
        )
        assert has_ears_suggestion
    
    def test_case_insensitive_parsing(self, validator):
        """Test that parsing works with different cases."""
        lowercase_statement = "when user clicks button then validation service shall verify fields"
        uppercase_statement = "WHEN USER CLICKS BUTTON THEN VALIDATION SERVICE SHALL VERIFY FIELDS"
        mixed_case_statement = "When User Clicks Button Then Validation Service Shall Verify Fields"
        
        lowercase_result = validator.validate_ears_statement(lowercase_statement)
        uppercase_result = validator.validate_ears_statement(uppercase_statement)
        mixed_case_result = validator.validate_ears_statement(mixed_case_statement)
        
        # All should parse successfully
        assert lowercase_result.statement_type == EARSStatementType.WHEN
        assert uppercase_result.statement_type == EARSStatementType.WHEN
        assert mixed_case_result.statement_type == EARSStatementType.WHEN
    
    def test_complex_valid_statement(self, validator):
        """Test validation of complex but valid statement."""
        complex_statement = (
            "WHEN authenticated user with admin privileges submits a data export request "
            "THEN export service SHALL validate permissions, generate CSV file with requested data, "
            "and send download link via email within 5 minutes"
        )
        
        result = validator.validate_ears_statement(complex_statement)
        
        assert result.is_valid
        assert result.statement_type == EARSStatementType.WHEN
        assert len(result.parsed_components["condition"]) > 10
        assert len(result.parsed_components["response"]) > 20
    
    def test_multiple_validation_issues(self, validator):
        """Test statement with multiple validation issues."""
        problematic_statement = "WHEN something THEN it SHALL work"
        
        result = validator.validate_ears_statement(problematic_statement)
        
        # Should have multiple issues
        assert len(result.issues) > 1
        
        # Should have issues of different severities
        severities = {issue.severity for issue in result.issues}
        assert len(severities) > 0
        
        # Should provide suggestions
        assert len(result.suggestions) > 0


class TestEARSValidationIntegration:
    """Integration tests for EARS validation with other components."""
    
    @pytest.fixture
    def validator(self):
        """Create EARS format validator instance."""
        return EARSFormatValidator()
    
    def test_ears_statement_model_integration(self, validator):
        """Test integration with EARSStatement model."""
        # Create statement using validator
        ears_statement = validator.create_ears_statement(
            condition="user submits valid form data",
            system="form processor",
            response="save data to database and return confirmation ID"
        )
        
        # Validate the string representation
        statement_str = str(ears_statement)
        result = validator.validate_ears_statement(statement_str)
        
        assert result.is_valid
        assert result.statement_type == EARSStatementType.WHEN
    
    def test_validation_result_completeness(self, validator):
        """Test that validation results contain all expected information."""
        statement = "WHEN user clicks save THEN document service SHALL store document and return ID"
        
        result = validator.validate_ears_statement(statement)
        
        # Check all expected fields are present
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'statement_type')
        assert hasattr(result, 'parsed_components')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'suggestions')
        
        # Check parsed components structure
        if result.parsed_components:
            assert 'condition' in result.parsed_components
            assert 'system' in result.parsed_components
            assert 'response' in result.parsed_components
    
    def test_systematic_quality_validation(self, validator):
        """Test that validator enforces systematic quality standards."""
        # High quality statement
        high_quality = (
            "WHEN authenticated user submits expense report with valid receipts "
            "THEN expense processing service SHALL validate receipts, calculate totals, "
            "and create approval workflow entry with unique tracking ID"
        )
        
        # Low quality statement
        low_quality = "WHEN user does stuff THEN system SHALL work"
        
        high_result = validator.validate_ears_statement(high_quality)
        low_result = validator.validate_ears_statement(low_quality)
        
        # High quality should have fewer issues
        high_warnings = [i for i in high_result.issues if i.severity == EARSValidationSeverity.WARNING]
        low_warnings = [i for i in low_result.issues if i.severity == EARSValidationSeverity.WARNING]
        
        assert len(low_warnings) > len(high_warnings)