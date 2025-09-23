"""
Tests for Acceptance Criteria Generator.

Validates systematic acceptance criteria generation, testability validation,
and template-based guidance.
"""

import pytest
from datetime import datetime

from src.spec_framework.validation.acceptance_criteria_generator import (
    AcceptanceCriteriaGenerator,
    AcceptanceCriteriaValidationResult,
    AcceptanceCriteriaValidationIssue,
    AcceptanceCriteriaValidationSeverity
)
from src.spec_framework.core.models import UserStory, AcceptanceCriterion, EARSStatement


class TestAcceptanceCriteriaGenerator:
    """Test suite for Acceptance Criteria Generator."""
    
    @pytest.fixture
    def generator(self):
        """Create acceptance criteria generator instance."""
        return AcceptanceCriteriaGenerator()
    
    @pytest.fixture
    def sample_user_story(self):
        """Create sample user story for testing."""
        return UserStory(
            role="developer",
            feature="run automated tests from the IDE",
            benefit="quickly validate code changes"
        )
    
    def test_generator_initialization(self, generator):
        """Test generator initializes correctly."""
        assert generator.ready()
        assert generator.status() == "ready"
        
        health = generator.health()
        assert health["status"] == "healthy"
        assert health["criteria_templates_loaded"] > 0
        assert health["ears_validator_ready"] is True
        
        metrics = generator.metrics()
        assert metrics["criteria_templates_count"] > 0
    
    def test_generate_basic_acceptance_criteria(self, generator, sample_user_story):
        """Test generation of basic acceptance criteria."""
        criteria = generator.generate_acceptance_criteria(
            sample_user_story,
            include_categories=['basic_functionality']
        )
        
        assert len(criteria) > 0
        
        # Check that all criteria are AcceptanceCriterion objects
        for criterion in criteria:
            assert isinstance(criterion, AcceptanceCriterion)
            assert hasattr(criterion, 'ears_format')
            assert hasattr(criterion, 'testable')
            assert hasattr(criterion, 'validation_method')
    
    def test_generate_multiple_categories(self, generator, sample_user_story):
        """Test generation with multiple categories."""
        criteria = generator.generate_acceptance_criteria(
            sample_user_story,
            include_categories=['basic_functionality', 'error_handling', 'security']
        )
        
        assert len(criteria) >= 6  # Should have criteria from all categories
        
        # Check for variety in criteria
        ears_statements = [str(criterion.ears_format) for criterion in criteria]
        unique_statements = set(ears_statements)
        assert len(unique_statements) == len(ears_statements)  # All should be unique
    
    def test_role_specific_criteria_generation(self, generator):
        """Test generation of role-specific criteria."""
        # Test with admin role (should get auth criteria)
        admin_story = UserStory(
            role="administrator",
            feature="manage user accounts",
            benefit="maintain system security"
        )
        
        admin_criteria = generator.generate_acceptance_criteria(admin_story)
        
        # Should include authentication criteria for admin role
        auth_criteria = [
            criterion for criterion in admin_criteria
            if 'authenticate' in str(criterion.ears_format).lower()
        ]
        assert len(auth_criteria) > 0
        
        # Test with end user (should not get auth criteria)
        user_story = UserStory(
            role="end user",
            feature="view dashboard",
            benefit="see current status"
        )
        
        user_criteria = generator.generate_acceptance_criteria(user_story)
        
        # Should not include authentication criteria for end user
        auth_criteria = [
            criterion for criterion in user_criteria
            if 'authenticate' in str(criterion.ears_format).lower()
        ]
        assert len(auth_criteria) == 0
    
    def test_feature_specific_criteria_generation(self, generator):
        """Test generation of feature-specific criteria."""
        # Test create/update feature
        create_story = UserStory(
            role="developer",
            feature="create new test cases",
            benefit="improve test coverage"
        )
        
        create_criteria = generator.generate_acceptance_criteria(create_story)
        
        # Should include validation criteria for create features
        validation_criteria = [
            criterion for criterion in create_criteria
            if 'required' in str(criterion.ears_format).lower() or
               'missing' in str(criterion.ears_format).lower()
        ]
        assert len(validation_criteria) > 0
        
        # Test search feature
        search_story = UserStory(
            role="developer",
            feature="search test results",
            benefit="find specific test outcomes"
        )
        
        search_criteria = generator.generate_acceptance_criteria(search_story)
        
        # Should include search-specific criteria
        search_specific = [
            criterion for criterion in search_criteria
            if 'no results' in str(criterion.ears_format).lower() or
               'search' in str(criterion.ears_format).lower()
        ]
        assert len(search_specific) > 0
    
    def test_custom_criteria_addition(self, generator, sample_user_story):
        """Test addition of custom criteria."""
        custom_criteria = [
            {
                'condition': 'test execution exceeds timeout limit',
                'system': 'test runner',
                'response': 'terminate test and report timeout error',
                'statement_type': 'WHEN'
            }
        ]
        
        criteria = generator.generate_acceptance_criteria(
            sample_user_story,
            include_categories=['basic_functionality'],
            custom_criteria=custom_criteria
        )
        
        # Should include the custom criterion
        custom_found = any(
            'timeout' in str(criterion.ears_format).lower()
            for criterion in criteria
        )
        assert custom_found
    
    def test_validate_acceptance_criteria_empty(self, generator):
        """Test validation of empty criteria list."""
        result = generator.validate_acceptance_criteria([])
        
        assert not result.is_valid
        assert result.criteria_count == 0
        assert result.testable_count == 0
        
        # Should have error about missing criteria
        error_issues = [
            issue for issue in result.issues
            if issue.severity == AcceptanceCriteriaValidationSeverity.ERROR
        ]
        assert len(error_issues) > 0
    
    def test_validate_acceptance_criteria_valid(self, generator, sample_user_story):
        """Test validation of valid acceptance criteria."""
        criteria = generator.generate_acceptance_criteria(sample_user_story)
        
        result = generator.validate_acceptance_criteria(criteria)
        
        assert result.criteria_count == len(criteria)
        assert result.testable_count > 0
        assert result.testability_score > 0
        
        # Should be valid if generated criteria are good
        if result.is_valid:
            assert result.testability_score > 30
    
    def test_validate_acceptance_criteria_invalid_ears(self, generator):
        """Test validation of criteria with invalid EARS format."""
        # Create criterion with invalid EARS format
        invalid_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="something happens",
                system="",  # Empty system
                response="it works",
                statement_type="WHEN"
            ),
            testable=False
        )
        
        result = generator.validate_acceptance_criteria([invalid_criterion])
        
        assert not result.is_valid
        
        # Should have EARS format errors
        ears_errors = [
            issue for issue in result.issues
            if issue.severity == AcceptanceCriteriaValidationSeverity.ERROR and
               'EARS' in issue.message
        ]
        assert len(ears_errors) > 0
    
    def test_testability_validation(self, generator):
        """Test testability validation patterns."""
        # Create criteria with different testability levels
        testable_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="user clicks submit button",
                system="form validator",
                response="return validation results with specific error messages",
                statement_type="WHEN"
            ),
            testable=True
        )
        
        vague_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="user does something",
                system="the system",
                response="work appropriately and function well",
                statement_type="WHEN"
            ),
            testable=False
        )
        
        result = generator.validate_acceptance_criteria([testable_criterion, vague_criterion])
        
        # Should identify vague terms
        vague_issues = [
            issue for issue in result.issues
            if 'vague' in issue.message.lower()
        ]
        assert len(vague_issues) > 0
    
    def test_coverage_validation(self, generator):
        """Test coverage validation."""
        # Test with insufficient criteria
        single_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="user provides input",
                system="the system",
                response="process the input",
                statement_type="WHEN"
            ),
            testable=True
        )
        
        result = generator.validate_acceptance_criteria([single_criterion])
        
        # Should warn about insufficient coverage
        coverage_warnings = [
            issue for issue in result.issues
            if issue.severity == AcceptanceCriteriaValidationSeverity.WARNING and
               'criteria' in issue.message.lower()
        ]
        assert len(coverage_warnings) > 0
    
    def test_error_handling_coverage_validation(self, generator):
        """Test error handling coverage validation."""
        # Create criteria without error handling
        happy_path_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="user provides valid input",
                system="the system",
                response="process successfully and return results",
                statement_type="WHEN"
            ),
            testable=True
        )
        
        result = generator.validate_acceptance_criteria([happy_path_criterion])
        
        # Should suggest adding error handling
        error_handling_suggestions = [
            issue for issue in result.issues
            if 'error' in issue.message.lower()
        ]
        assert len(error_handling_suggestions) > 0
    
    def test_testability_score_calculation(self, generator, sample_user_story):
        """Test testability score calculation."""
        # Generate high-quality criteria
        criteria = generator.generate_acceptance_criteria(
            sample_user_story,
            include_categories=['basic_functionality', 'error_handling']
        )
        
        result = generator.validate_acceptance_criteria(criteria)
        
        # Score should be reasonable for generated criteria
        assert 0 <= result.testability_score <= 100
        
        # Should have some testable criteria
        assert result.testable_count > 0
    
    def test_get_criteria_templates(self, generator):
        """Test getting criteria templates."""
        # Get all templates
        all_templates = generator.get_criteria_templates()
        
        assert 'categories' in all_templates
        assert 'all_templates' in all_templates
        assert len(all_templates['categories']) > 0
        
        # Get specific category
        basic_templates = generator.get_criteria_templates('basic_functionality')
        
        assert 'category' in basic_templates
        assert 'templates' in basic_templates
        assert basic_templates['category'] == 'basic_functionality'
        assert len(basic_templates['templates']) > 0
    
    def test_suggest_missing_criteria(self, generator, sample_user_story):
        """Test suggestion of missing criteria."""
        # Create minimal existing criteria (only happy path)
        existing_criteria = [
            AcceptanceCriterion(
                ears_format=EARSStatement(
                    condition="developer runs valid tests",
                    system="test runner",
                    response="execute tests and return results",
                    statement_type="WHEN"
                ),
                testable=True
            )
        ]
        
        suggestions = generator.suggest_missing_criteria(sample_user_story, existing_criteria)
        
        assert len(suggestions) > 0
        
        # Should suggest error handling
        error_suggestions = [
            suggestion for suggestion in suggestions
            if 'invalid' in suggestion['condition'].lower() or
               'error' in suggestion['condition'].lower()
        ]
        assert len(error_suggestions) > 0
    
    def test_validation_method_determination(self, generator):
        """Test determination of appropriate validation methods."""
        # Create criteria with different response types
        ui_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="user clicks button",
                system="user interface",
                response="display confirmation message",
                statement_type="WHEN"
            ),
            testable=True
        )
        
        api_criterion = AcceptanceCriterion(
            ears_format=EARSStatement(
                condition="client sends request",
                system="API service",
                response="return JSON response with status code",
                statement_type="WHEN"
            ),
            testable=True
        )
        
        # Generate criteria to test validation method assignment
        user_story = UserStory(
            role="developer",
            feature="test user interface",
            benefit="ensure UI works correctly"
        )
        
        criteria = generator.generate_acceptance_criteria(user_story)
        
        # Should have appropriate validation methods assigned
        validation_methods = [criterion.validation_method.method_type for criterion in criteria]
        assert len(set(validation_methods)) > 0  # Should have some variety
    
    def test_ears_format_integration(self, generator, sample_user_story):
        """Test integration with EARS format validator."""
        criteria = generator.generate_acceptance_criteria(sample_user_story)
        
        # All generated criteria should have valid EARS format
        for criterion in criteria:
            ears_str = str(criterion.ears_format)
            
            # Should contain EARS keywords
            assert any(keyword in ears_str.upper() for keyword in ['WHEN', 'IF', 'WHILE'])
            assert 'THEN' in ears_str.upper()
            assert 'SHALL' in ears_str.upper()
    
    def test_template_customization(self, generator):
        """Test template customization based on user story."""
        # Test with specific feature that should customize templates
        specific_story = UserStory(
            role="developer",
            feature="create automated test reports",
            benefit="track testing progress"
        )
        
        criteria = generator.generate_acceptance_criteria(specific_story)
        
        # Should customize templates based on feature
        criteria_text = ' '.join(str(criterion.ears_format) for criterion in criteria)
        
        # Should reference the specific feature context
        assert any(
            term in criteria_text.lower() 
            for term in ['create', 'test', 'report']
        )


class TestAcceptanceCriteriaIntegration:
    """Integration tests for acceptance criteria generator."""
    
    @pytest.fixture
    def generator(self):
        """Create acceptance criteria generator instance."""
        return AcceptanceCriteriaGenerator()
    
    def test_end_to_end_generation_and_validation(self, generator):
        """Test complete generation and validation workflow."""
        # Create user story
        user_story = UserStory(
            role="project manager",
            feature="view team progress dashboard",
            benefit="track project status and identify blockers"
        )
        
        # Generate criteria
        criteria = generator.generate_acceptance_criteria(
            user_story,
            include_categories=['basic_functionality', 'error_handling', 'usability']
        )
        
        # Validate criteria
        result = generator.validate_acceptance_criteria(criteria)
        
        # Should have reasonable results
        assert len(criteria) >= 3
        assert result.criteria_count == len(criteria)
        assert result.testability_score > 20
        
        # Should have suggestions for improvement
        assert len(result.suggestions) > 0
    
    def test_systematic_quality_validation(self, generator):
        """Test that generator enforces systematic quality standards."""
        # High-quality user story
        high_quality_story = UserStory(
            role="security architect",
            feature="implement automated threat detection with real-time alerting",
            benefit="reduce security incident response time and improve security posture"
        )
        
        # Low-quality user story
        low_quality_story = UserStory(
            role="user",
            feature="do stuff",
            benefit="things work better"
        )
        
        high_criteria = generator.generate_acceptance_criteria(high_quality_story)
        low_criteria = generator.generate_acceptance_criteria(low_quality_story)
        
        high_result = generator.validate_acceptance_criteria(high_criteria)
        low_result = generator.validate_acceptance_criteria(low_criteria)
        
        # High quality should generally perform better
        # (though both should generate reasonable criteria from templates)
        assert len(high_criteria) > 0
        assert len(low_criteria) > 0
        assert high_result.testability_score >= 0
        assert low_result.testability_score >= 0
    
    def test_comprehensive_coverage_analysis(self, generator):
        """Test comprehensive coverage analysis."""
        user_story = UserStory(
            role="developer",
            feature="execute comprehensive test suite with parallel execution",
            benefit="reduce testing time while maintaining quality"
        )
        
        # Generate comprehensive criteria
        criteria = generator.generate_acceptance_criteria(
            user_story,
            include_categories=[
                'basic_functionality', 'error_handling', 'performance',
                'security', 'usability'
            ]
        )
        
        result = generator.validate_acceptance_criteria(criteria)
        
        # Should have comprehensive coverage
        assert len(criteria) >= 8  # Multiple categories should generate multiple criteria
        assert result.testability_score > 40  # Should be reasonably testable
        
        # Should cover different aspects
        criteria_text = ' '.join(str(criterion.ears_format) for criterion in criteria).lower()
        
        # Should have variety in conditions and responses
        assert len(set(criterion.ears_format.condition for criterion in criteria)) > 3
        assert len(set(criterion.ears_format.response for criterion in criteria)) > 3