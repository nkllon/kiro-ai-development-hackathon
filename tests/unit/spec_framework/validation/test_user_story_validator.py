"""
Tests for User Story Template System.

Validates systematic user story validation, role library, and benefit validation.
"""

import pytest
from datetime import datetime

from src.spec_framework.validation.user_story_validator import (
    UserStoryTemplateSystem,
    UserStoryValidationResult,
    UserStoryValidationIssue,
    UserStoryValidationSeverity
)
from src.spec_framework.core.models import UserStory


class TestUserStoryTemplateSystem:
    """Test suite for User Story Template System."""
    
    @pytest.fixture
    def template_system(self):
        """Create user story template system instance."""
        return UserStoryTemplateSystem()
    
    def test_system_initialization(self, template_system):
        """Test template system initializes correctly."""
        assert template_system.ready()
        assert template_system.status() == "ready"
        
        health = template_system.health()
        assert health["status"] == "healthy"
        assert health["role_library_size"] > 0
        
        metrics = template_system.metrics()
        assert metrics["role_library_size"] > 0
    
    def test_valid_user_story(self, template_system):
        """Test validation of valid user story."""
        story = "As a developer, I want to run automated tests from the IDE, so that I can quickly validate my code changes"
        
        result = template_system.validate_user_story(story)
        
        assert result.is_valid
        assert result.parsed_components is not None
        assert result.parsed_components["role"] == "developer"
        assert result.parsed_components["feature"] == "run automated tests from the IDE"
        assert result.parsed_components["benefit"] == "I can quickly validate my code changes"
        assert result.business_value_score > 0
    
    def test_valid_user_story_alternative_format(self, template_system):
        """Test validation of user story with alternative format."""
        story = "As a project manager, I need to view real-time progress dashboards, so that I can identify blockers early"
        
        result = template_system.validate_user_story(story)
        
        assert result.is_valid
        assert result.parsed_components["role"] == "project manager"
        assert result.parsed_components["feature"] == "view real-time progress dashboards"
        assert result.parsed_components["benefit"] == "I can identify blockers early"
    
    def test_role_library_validation(self, template_system):
        """Test role library validation."""
        # Valid role from library
        valid_story = "As a developer, I want to debug code, so that I can fix issues faster"
        valid_result = template_system.validate_user_story(valid_story)
        
        # Should have no role-related warnings for library roles
        role_warnings = [
            issue for issue in valid_result.issues
            if issue.component == "role" and issue.severity == UserStoryValidationSeverity.WARNING
        ]
        assert len(role_warnings) == 0
        
        # Custom role not in library
        custom_story = "As a unicorn trainer, I want to manage magical creatures, so that I can improve productivity"
        custom_result = template_system.validate_user_story(custom_story)
        
        # Should have warning about role not in library
        role_warnings = [
            issue for issue in custom_result.issues
            if issue.component == "role" and "library" in issue.message.lower()
        ]
        assert len(role_warnings) > 0
    
    def test_generic_role_detection(self, template_system):
        """Test detection of generic roles."""
        generic_story = "As a user, I want to do something, so that things work better"
        
        result = template_system.validate_user_story(generic_story)
        
        # Should detect generic role
        generic_issues = [
            issue for issue in result.issues
            if issue.component == "role" and "generic" in issue.message.lower()
        ]
        assert len(generic_issues) > 0
    
    def test_vague_role_detection(self, template_system):
        """Test detection of vague roles."""
        vague_story = "As a stakeholder, I want to manage things, so that the system is improved"
        
        result = template_system.validate_user_story(vague_story)
        
        # Should detect vague role
        vague_issues = [
            issue for issue in result.issues
            if issue.component == "role" and "vague" in issue.message.lower()
        ]
        assert len(vague_issues) > 0
    
    def test_feature_validation(self, template_system):
        """Test feature component validation."""
        # Good feature with action verb
        good_story = "As a developer, I want to create automated test suites, so that I can ensure code quality"
        good_result = template_system.validate_user_story(good_story)
        
        # Should have minimal feature issues
        feature_warnings = [
            issue for issue in good_result.issues
            if issue.component == "feature" and issue.severity == UserStoryValidationSeverity.WARNING
        ]
        assert len(feature_warnings) <= 1  # Allow for minor warnings
        
        # Vague feature
        vague_story = "As a developer, I want to do something with the system, so that things work better"
        vague_result = template_system.validate_user_story(vague_story)
        
        # Should detect vague feature
        vague_issues = [
            issue for issue in vague_result.issues
            if issue.component == "feature" and "vague" in issue.message.lower()
        ]
        assert len(vague_issues) > 0
    
    def test_feature_too_short(self, template_system):
        """Test detection of too short features."""
        short_story = "As a developer, I want to test, so that I can ensure quality"
        
        result = template_system.validate_user_story(short_story)
        
        # Should have error about short feature
        short_issues = [
            issue for issue in result.issues
            if issue.component == "feature" and issue.severity == UserStoryValidationSeverity.ERROR
        ]
        assert len(short_issues) > 0
    
    def test_benefit_validation(self, template_system):
        """Test benefit component validation."""
        # Good benefit with business value
        good_story = "As a developer, I want to run automated tests, so that I can improve code quality and reduce bugs"
        good_result = template_system.validate_user_story(good_story)
        
        # Should have good business value score
        assert good_result.business_value_score > 40
        
        # Vague benefit
        vague_story = "As a developer, I want to run tests, so that things work better"
        vague_result = template_system.validate_user_story(vague_story)
        
        # Should detect vague benefit
        vague_issues = [
            issue for issue in vague_result.issues
            if issue.component == "benefit" and "vague" in issue.message.lower()
        ]
        assert len(vague_issues) > 0
    
    def test_business_value_indicators(self, template_system):
        """Test detection of business value indicators."""
        # Story with clear business value indicators
        value_story = "As a developer, I want automated testing, so that I can increase productivity and reduce debugging time"
        value_result = template_system.validate_user_story(value_story)
        
        # Story without clear business value
        no_value_story = "As a developer, I want automated testing, so that I have tests"
        no_value_result = template_system.validate_user_story(no_value_story)
        
        # Value story should have higher business value score
        assert value_result.business_value_score > no_value_result.business_value_score
    
    def test_benefit_too_short(self, template_system):
        """Test detection of too short benefits."""
        short_story = "As a developer, I want to run tests, so that good"
        
        result = template_system.validate_user_story(short_story)
        
        # Should have error about short benefit
        short_issues = [
            issue for issue in result.issues
            if issue.component == "benefit" and issue.severity == UserStoryValidationSeverity.ERROR
        ]
        assert len(short_issues) > 0
    
    def test_structure_validation(self, template_system):
        """Test overall structure validation."""
        # Missing "As a"
        no_as_story = "Developer wants to run tests so that quality improves"
        no_as_result = template_system.validate_user_story(no_as_story)
        
        assert not no_as_result.is_valid
        structure_issues = [
            issue for issue in no_as_result.issues
            if issue.component == "structure"
        ]
        assert len(structure_issues) > 0
        
        # Missing "I want"
        no_want_story = "As a developer, running tests, so that quality improves"
        no_want_result = template_system.validate_user_story(no_want_story)
        
        assert not no_want_result.is_valid
        
        # Missing "so that"
        no_so_story = "As a developer, I want to run tests"
        no_so_result = template_system.validate_user_story(no_so_story)
        
        assert not no_so_result.is_valid
    
    def test_parsing_failure_diagnosis(self, template_system):
        """Test diagnosis of parsing failures."""
        invalid_story = "This is not a user story at all"
        
        result = template_system.validate_user_story(invalid_story)
        
        assert not result.is_valid
        assert result.parsed_components is None
        assert len(result.issues) > 0
        assert len(result.suggestions) > 0
    
    def test_create_user_story(self, template_system):
        """Test creation of user story objects."""
        role = "developer"
        feature = "run automated tests from IDE"
        benefit = "quickly validate code changes"
        
        user_story = template_system.create_user_story(role, feature, benefit)
        
        assert user_story.role == role
        assert user_story.feature == feature
        assert user_story.benefit == benefit
        
        # Test string representation
        story_str = str(user_story)
        assert "As a developer" in story_str
        assert "I want" in story_str
        assert "so that" in story_str
    
    def test_role_suggestions(self, template_system):
        """Test role suggestion functionality."""
        # Get all roles
        all_roles = template_system.get_role_suggestions()
        assert len(all_roles) > 0
        
        # Each role should have required fields
        for role_info in all_roles:
            assert 'role' in role_info
            assert 'category' in role_info
            assert 'description' in role_info
        
        # Test partial matching
        dev_roles = template_system.get_role_suggestions("dev")
        dev_role_names = [r['role'] for r in dev_roles]
        assert "developer" in dev_role_names
        assert "devops engineer" in dev_role_names
    
    def test_template_guidance(self, template_system):
        """Test template guidance generation."""
        # General guidance
        guidance = template_system.get_template_guidance()
        
        assert 'format' in guidance
        assert 'components' in guidance
        assert 'examples' in guidance
        
        # Check components guidance
        assert 'role' in guidance['components']
        assert 'feature' in guidance['components']
        assert 'benefit' in guidance['components']
        
        # Role-specific guidance
        dev_guidance = template_system.get_template_guidance("developer")
        assert 'role_specific' in dev_guidance
        assert 'typical_needs' in dev_guidance['role_specific']
        assert 'common_benefits' in dev_guidance['role_specific']
    
    def test_business_value_score_calculation(self, template_system):
        """Test business value score calculation."""
        # High value story
        high_value = "As a developer, I want to create automated test suites with coverage reporting, so that I can improve code quality and reduce production bugs"
        high_result = template_system.validate_user_story(high_value)
        
        # Low value story
        low_value = "As a user, I want to do something, so that things work"
        low_result = template_system.validate_user_story(low_value)
        
        # High value should score significantly higher
        assert high_result.business_value_score > low_result.business_value_score + 30
        
        # Scores should be in valid range
        assert 0 <= high_result.business_value_score <= 100
        assert 0 <= low_result.business_value_score <= 100
    
    def test_suggestions_generation(self, template_system):
        """Test that suggestions are generated appropriately."""
        # Invalid story should get suggestions
        invalid_story = "Bad user story format"
        invalid_result = template_system.validate_user_story(invalid_story)
        
        assert len(invalid_result.suggestions) > 0
        
        # Suggestions should contain format examples
        has_format_suggestion = any(
            "As a" in suggestion and "I want" in suggestion and "so that" in suggestion
            for suggestion in invalid_result.suggestions
        )
        assert has_format_suggestion
        
        # Valid story with known role should get role-specific suggestions
        valid_story = "As a developer, I want to run tests, so that I can ensure quality"
        valid_result = template_system.validate_user_story(valid_story)
        
        # Should have some suggestions (even for valid stories, we provide improvement suggestions)
        assert len(valid_result.suggestions) > 0
    
    def test_case_insensitive_parsing(self, template_system):
        """Test that parsing works with different cases."""
        lowercase_story = "as a developer, i want to run tests, so that i can ensure quality"
        uppercase_story = "AS A DEVELOPER, I WANT TO RUN TESTS, SO THAT I CAN ENSURE QUALITY"
        mixed_case_story = "As A Developer, I Want To Run Tests, So That I Can Ensure Quality"
        
        lowercase_result = template_system.validate_user_story(lowercase_story)
        uppercase_result = template_system.validate_user_story(uppercase_story)
        mixed_case_result = template_system.validate_user_story(mixed_case_story)
        
        # All should parse successfully
        assert lowercase_result.parsed_components is not None
        assert uppercase_result.parsed_components is not None
        assert mixed_case_result.parsed_components is not None
        
        # All should have same role
        assert lowercase_result.parsed_components["role"] == "developer"
        assert uppercase_result.parsed_components["role"] == "DEVELOPER"
        assert mixed_case_result.parsed_components["role"] == "Developer"
    
    def test_complex_valid_story(self, template_system):
        """Test validation of complex but valid user story."""
        complex_story = (
            "As an authenticated system administrator with security clearance, "
            "I want to configure automated backup schedules with encryption and "
            "retention policies across multiple data centers, so that I can "
            "ensure business continuity, meet compliance requirements, and "
            "reduce operational overhead while maintaining data security"
        )
        
        result = template_system.validate_user_story(complex_story)
        
        # Should parse successfully despite complexity
        assert result.parsed_components is not None
        assert len(result.parsed_components["role"]) > 10
        assert len(result.parsed_components["feature"]) > 50
        assert len(result.parsed_components["benefit"]) > 50
        
        # Should have good business value score due to specific benefits
        assert result.business_value_score > 50
    
    def test_multiple_validation_issues(self, template_system):
        """Test story with multiple validation issues."""
        problematic_story = "As a user, I want to do stuff, so that things work better"
        
        result = template_system.validate_user_story(problematic_story)
        
        # Should have multiple issues across different components
        assert len(result.issues) > 3
        
        # Should have issues for different components
        components_with_issues = {issue.component for issue in result.issues}
        assert len(components_with_issues) > 1
        
        # Should provide suggestions
        assert len(result.suggestions) > 0


class TestUserStoryIntegration:
    """Integration tests for user story validation with other components."""
    
    @pytest.fixture
    def template_system(self):
        """Create user story template system instance."""
        return UserStoryTemplateSystem()
    
    def test_user_story_model_integration(self, template_system):
        """Test integration with UserStory model."""
        # Create user story using template system
        user_story = template_system.create_user_story(
            role="developer",
            feature="run automated tests with coverage reporting",
            benefit="ensure code quality and identify untested areas"
        )
        
        # Validate the string representation
        story_str = str(user_story)
        result = template_system.validate_user_story(story_str)
        
        assert result.is_valid
        assert result.business_value_score > 40
    
    def test_role_library_completeness(self, template_system):
        """Test that role library covers major user types."""
        expected_categories = ["technical", "management", "business", "user", "specialized"]
        
        all_roles = template_system.get_role_suggestions()
        categories_found = {role['category'] for role in all_roles}
        
        # Should have roles in all major categories
        for category in expected_categories:
            assert category in categories_found
        
        # Should have reasonable number of roles
        assert len(all_roles) >= 10
    
    def test_systematic_quality_validation(self, template_system):
        """Test that validator enforces systematic quality standards."""
        # High quality story
        high_quality = (
            "As a security architect, I want to implement automated threat "
            "detection with real-time alerting and incident response workflows, "
            "so that I can reduce security incident response time and improve "
            "overall security posture"
        )
        
        # Low quality story
        low_quality = "As a user, I want stuff to work, so that it's good"
        
        high_result = template_system.validate_user_story(high_quality)
        low_result = template_system.validate_user_story(low_quality)
        
        # High quality should have significantly higher business value score
        assert high_result.business_value_score > low_result.business_value_score + 40
        
        # Low quality should have more validation issues
        assert len(low_result.issues) > len(high_result.issues)
    
    def test_validation_result_completeness(self, template_system):
        """Test that validation results contain all expected information."""
        story = "As a developer, I want to debug applications, so that I can fix issues faster"
        
        result = template_system.validate_user_story(story)
        
        # Check all expected fields are present
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'parsed_components')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'suggestions')
        assert hasattr(result, 'business_value_score')
        
        # Check parsed components structure
        if result.parsed_components:
            assert 'role' in result.parsed_components
            assert 'feature' in result.parsed_components
            assert 'benefit' in result.parsed_components