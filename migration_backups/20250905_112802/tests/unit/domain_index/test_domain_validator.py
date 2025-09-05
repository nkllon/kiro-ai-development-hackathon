"""
Tests for Domain Validation and Consistency Checking System

This module tests the DomainValidator class including validation rules,
consistency checks, and dependency analysis.
"""

import pytest
from unittest.mock import Mock, patch

from src.beast_mode.domain_index.domain_validator import (
    DomainValidator, ValidationRule, ConsistencyCheck, SchemaValidator
)
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential,
    HealthIssue, IssueSeverity, IssueCategory
)


class TestValidationRule:
    """Test ValidationRule functionality"""
    
    def test_validation_rule_creation(self):
        """Test validation rule creation"""
        def dummy_validator(domain, context):
            return []
        
        rule = ValidationRule(
            name="test_rule",
            description="Test validation rule",
            severity=IssueSeverity.WARNING,
            category=IssueCategory.VALIDATION,
            validator_func=dummy_validator
        )
        
        assert rule.name == "test_rule"
        assert rule.description == "Test validation rule"
        assert rule.severity == IssueSeverity.WARNING
        assert rule.category == IssueCategory.VALIDATION
        assert rule.validator_func == dummy_validator
    
    def test_validation_rule_execution(self):
        """Test validation rule execution"""
        def test_validator(domain, context):
            if not domain.name:
                return [HealthIssue(
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.VALIDATION,
                    description="Domain name is required",
                    suggested_fix="Add domain name"
                )]
            return []
        
        rule = ValidationRule(
            name="name_check",
            description="Check domain name",
            severity=IssueSeverity.CRITICAL,
            category=IssueCategory.VALIDATION,
            validator_func=test_validator
        )
        
        # Test with valid domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        valid_domain = Domain("test", "Test domain", ["src/**/*.py"], [], [], [], tools, metadata)
        
        issues = rule.validate(valid_domain, {})
        assert len(issues) == 0
        
        # Test with invalid domain
        invalid_domain = Domain("", "Test domain", ["src/**/*.py"], [], [], [], tools, metadata)
        issues = rule.validate(invalid_domain, {})
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.CRITICAL
    
    def test_validation_rule_error_handling(self):
        """Test validation rule error handling"""
        def failing_validator(domain, context):
            raise Exception("Validator failed")
        
        rule = ValidationRule(
            name="failing_rule",
            description="Failing validation rule",
            severity=IssueSeverity.WARNING,
            category=IssueCategory.VALIDATION,
            validator_func=failing_validator
        )
        
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        domain = Domain("test", "Test domain", ["src/**/*.py"], [], [], [], tools, metadata)
        
        issues = rule.validate(domain, {})
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.CRITICAL
        assert "failed" in issues[0].description


class TestConsistencyCheck:
    """Test ConsistencyCheck functionality"""
    
    def test_consistency_check_creation(self):
        """Test consistency check creation"""
        def dummy_checker(domains, context):
            return []
        
        check = ConsistencyCheck(
            name="test_check",
            description="Test consistency check",
            severity=IssueSeverity.WARNING,
            checker_func=dummy_checker
        )
        
        assert check.name == "test_check"
        assert check.description == "Test consistency check"
        assert check.severity == IssueSeverity.WARNING
        assert check.checker_func == dummy_checker
    
    def test_consistency_check_execution(self):
        """Test consistency check execution"""
        def dependency_checker(domains, context):
            issues = []
            for domain_name, domain in domains.items():
                for dep in domain.dependencies:
                    if dep not in domains:
                        issues.append(HealthIssue(
                            severity=IssueSeverity.CRITICAL,
                            category=IssueCategory.DEPENDENCY,
                            description=f"Missing dependency: {dep}",
                            suggested_fix=f"Create domain {dep}"
                        ))
            return issues
        
        check = ConsistencyCheck(
            name="dependency_check",
            description="Check dependencies exist",
            severity=IssueSeverity.CRITICAL,
            checker_func=dependency_checker
        )
        
        # Create test domains
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        domain1 = Domain("domain1", "Domain 1", ["src/1/**/*.py"], [], [], ["domain2"], tools, metadata)
        domain2 = Domain("domain2", "Domain 2", ["src/2/**/*.py"], [], [], [], tools, metadata)
        
        # Test with valid dependencies
        domains = {"domain1": domain1, "domain2": domain2}
        issues = check.check(domains, {})
        assert len(issues) == 0
        
        # Test with missing dependency
        domains = {"domain1": domain1}
        issues = check.check(domains, {})
        assert len(issues) == 1
        assert "domain2" in issues[0].description


class TestDomainValidator:
    """Test DomainValidator functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create a test validator instance"""
        config = {
            'strict_validation': False,
            'check_filesystem': False,  # Disable filesystem checks for tests
            'max_dependency_depth': 10,
            'required_fields': ['name', 'description', 'patterns', 'tools']
        }
        return DomainValidator(config)
    
    @pytest.fixture
    def sample_domain(self):
        """Create a sample domain for testing"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, ["Well-defined"], [], "medium", []),
            tags=["test", "core"]
        )
        return Domain(
            "test_domain", "Test domain for validation",
            ["src/test/**/*.py"], ["test"], ["python>=3.8"], [],
            tools, metadata
        )
    
    def test_validator_initialization(self, validator):
        """Test validator initialization"""
        assert validator.strict_mode is False
        assert validator.check_filesystem is False
        assert validator.max_dependency_depth == 10
        assert len(validator._validation_rules) > 0
        assert len(validator._consistency_checks) > 0
    
    def test_validate_valid_domain(self, validator, sample_domain):
        """Test validation of a valid domain"""
        result = validator.validate_domain(sample_domain)
        
        # Should be valid (or have only minor warnings)
        assert result.is_valid or len(result.errors) == 0
    
    def test_validate_invalid_domain_name(self, validator):
        """Test validation of domain with invalid name"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        # Empty name
        domain = Domain("", "Test domain", ["src/**/*.py"], [], [], [], tools, metadata)
        result = validator.validate_domain(domain)
        assert not result.is_valid
        assert any("name" in error.lower() for error in result.errors)
        
        # Invalid name format
        domain = Domain("Test-Domain!", "Test domain", ["src/**/*.py"], [], [], [], tools, metadata)
        result = validator.validate_domain(domain)
        # May have warnings about naming convention
        assert len(result.warnings) > 0 or len(result.errors) > 0
    
    def test_validate_missing_required_fields(self, validator):
        """Test validation of domain missing required fields"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        # Missing description
        domain = Domain("test", "", ["src/**/*.py"], [], [], [], tools, metadata)
        result = validator.validate_domain(domain)
        assert not result.is_valid
        
        # Missing patterns
        domain = Domain("test", "Test domain", [], [], [], [], tools, metadata)
        result = validator.validate_domain(domain)
        assert not result.is_valid
    
    def test_validate_file_patterns(self, validator, sample_domain):
        """Test file pattern validation"""
        # Test with invalid patterns
        sample_domain.patterns = ["", "  ", None]
        result = validator.validate_domain(sample_domain)
        assert not result.is_valid
        
        # Test with absolute paths (should generate warnings)
        sample_domain.patterns = ["/absolute/path/**/*.py"]
        result = validator.validate_domain(sample_domain)
        assert len(result.warnings) > 0
        
        # Test with backslashes (should generate warnings)
        sample_domain.patterns = ["src\\test\\**\\*.py"]
        result = validator.validate_domain(sample_domain)
        assert len(result.warnings) > 0
    
    def test_validate_domain_collection(self, validator):
        """Test validation of domain collection"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        domains = {
            "valid_domain": Domain("valid_domain", "Valid domain", ["src/**/*.py"], [], [], [], tools, metadata),
            "invalid_domain": Domain("", "Invalid domain", [], [], [], [], tools, metadata)
        }
        
        results = validator.validate_domain_collection(domains)
        
        assert len(results) == 2
        assert "valid_domain" in results
        assert "invalid_domain" in results
        assert results["valid_domain"].is_valid or len(results["valid_domain"].errors) == 0
        assert not results["invalid_domain"].is_valid
    
    def test_detect_circular_dependencies(self, validator):
        """Test circular dependency detection"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        # Create domains with circular dependencies
        domain_a = Domain("domain_a", "Domain A", ["src/a/**/*.py"], [], [], ["domain_b"], tools, metadata)
        domain_b = Domain("domain_b", "Domain B", ["src/b/**/*.py"], [], [], ["domain_c"], tools, metadata)
        domain_c = Domain("domain_c", "Domain C", ["src/c/**/*.py"], [], [], ["domain_a"], tools, metadata)
        
        domains = {"domain_a": domain_a, "domain_b": domain_b, "domain_c": domain_c}
        
        circular_deps = validator.detect_circular_dependencies(domains)
        
        assert len(circular_deps) > 0
        # Should find the circular dependency
        cycle = circular_deps[0]
        assert len(cycle) >= 3  # At least 3 domains in cycle
    
    def test_validate_dependencies(self, validator):
        """Test dependency validation"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        # Domain with missing dependency
        domain_a = Domain("domain_a", "Domain A", ["src/a/**/*.py"], [], [], ["nonexistent"], tools, metadata)
        domain_b = Domain("domain_b", "Domain B", ["src/b/**/*.py"], [], [], [], tools, metadata)
        
        domains = {"domain_a": domain_a, "domain_b": domain_b}
        
        issues = validator.validate_dependencies(domains)
        
        assert len(issues) > 0
        assert any("nonexistent" in issue.description for issue in issues)
    
    def test_check_consistency(self, validator):
        """Test consistency checking"""
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        # Create domains with consistency issues
        domain_a = Domain("domain_a", "Domain A", ["src/a/**/*.py"], [], [], ["missing_domain"], tools, metadata)
        domain_b = Domain("domain_b", "Domain B", ["src/b/**/*.py"], [], [], [], tools, metadata)
        
        domains = {"domain_a": domain_a, "domain_b": domain_b}
        
        issues = validator.check_consistency(domains)
        
        assert len(issues) > 0
        # Should find dependency consistency issues
        assert any(issue.category == IssueCategory.DEPENDENCY for issue in issues)
    
    def test_add_custom_validation_rule(self, validator):
        """Test adding custom validation rule"""
        def custom_validator(domain, context):
            if "test" not in domain.name:
                return [HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.VALIDATION,
                    description="Domain name should contain 'test'",
                    suggested_fix="Add 'test' to domain name"
                )]
            return []
        
        custom_rule = ValidationRule(
            name="custom_test_rule",
            description="Custom test validation rule",
            severity=IssueSeverity.WARNING,
            category=IssueCategory.VALIDATION,
            validator_func=custom_validator
        )
        
        initial_rule_count = len(validator._validation_rules)
        validator.add_validation_rule(custom_rule)
        
        assert len(validator._validation_rules) == initial_rule_count + 1
        
        # Test the custom rule
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        domain = Domain("production", "Production domain", ["src/**/*.py"], [], [], [], tools, metadata)
        
        result = validator.validate_domain(domain)
        assert len(result.warnings) > 0
        assert any("test" in warning for warning in result.warnings)
    
    def test_add_custom_consistency_check(self, validator):
        """Test adding custom consistency check"""
        def custom_checker(domains, context):
            if len(domains) < 2:
                return [HealthIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.VALIDATION,
                    description="Should have at least 2 domains",
                    suggested_fix="Add more domains"
                )]
            return []
        
        custom_check = ConsistencyCheck(
            name="minimum_domains",
            description="Check minimum number of domains",
            severity=IssueSeverity.INFO,
            checker_func=custom_checker
        )
        
        initial_check_count = len(validator._consistency_checks)
        validator.add_consistency_check(custom_check)
        
        assert len(validator._consistency_checks) == initial_check_count + 1
        
        # Test the custom check
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        domains = {"single": Domain("single", "Single domain", ["src/**/*.py"], [], [], [], tools, metadata)}
        
        issues = validator.check_consistency(domains)
        assert len(issues) > 0
        assert any("at least 2 domains" in issue.description for issue in issues)
    
    def test_validation_statistics(self, validator, sample_domain):
        """Test validation statistics"""
        initial_stats = validator.get_validation_stats()
        
        # Perform some validations
        validator.validate_domain(sample_domain)
        validator.check_consistency({"test": sample_domain})
        
        final_stats = validator.get_validation_stats()
        
        assert final_stats['validations_performed'] > initial_stats['validations_performed']
        assert final_stats['consistency_checks_performed'] > initial_stats['consistency_checks_performed']
        assert 'validation_rules_count' in final_stats
        assert 'consistency_checks_count' in final_stats


class TestSchemaValidator:
    """Test SchemaValidator functionality"""
    
    @pytest.fixture
    def schema_validator(self):
        """Create a schema validator instance"""
        return SchemaValidator()
    
    def test_valid_domain_schema(self, schema_validator):
        """Test validation of valid domain schema"""
        valid_domain = {
            "name": "test_domain",
            "description": "Test domain for schema validation",
            "patterns": ["src/test/**/*.py"],
            "content_indicators": ["test"],
            "requirements": ["python>=3.8"],
            "dependencies": [],
            "tools": {
                "linter": "pylint",
                "formatter": "black",
                "validator": "mypy",
                "exclusions": ["__pycache__"]
            },
            "metadata": {
                "demo_role": "core",
                "extraction_candidate": "yes",
                "package_potential": {
                    "score": 0.8,
                    "reasons": ["Well-defined"],
                    "dependencies": [],
                    "estimated_effort": "medium",
                    "blockers": []
                },
                "status": "active",
                "tags": ["test", "core"]
            }
        }
        
        errors = schema_validator.validate_schema(valid_domain)
        assert len(errors) == 0
    
    def test_invalid_domain_schema(self, schema_validator):
        """Test validation of invalid domain schema"""
        # Missing required fields
        invalid_domain = {
            "name": "test_domain"
            # Missing description, patterns, tools, metadata
        }
        
        errors = schema_validator.validate_schema(invalid_domain)
        assert len(errors) > 0
        
        # Invalid field types
        invalid_domain = {
            "name": 123,  # Should be string
            "description": "Test domain",
            "patterns": "not_an_array",  # Should be array
            "tools": {
                "linter": "pylint",
                "formatter": "black",
                "validator": "mypy"
            },
            "metadata": {
                "demo_role": "core",
                "extraction_candidate": "yes",
                "package_potential": {}
            }
        }
        
        errors = schema_validator.validate_schema(invalid_domain)
        assert len(errors) > 0
    
    def test_basic_schema_validation_fallback(self, schema_validator):
        """Test basic schema validation fallback"""
        # Test the fallback validation when jsonschema is not available
        valid_domain = {
            "name": "test_domain",
            "description": "Test domain",
            "patterns": ["src/**/*.py"],
            "tools": {"linter": "pylint", "formatter": "black", "validator": "mypy"},
            "metadata": {"demo_role": "core", "extraction_candidate": "yes", "package_potential": {}}
        }
        
        errors = schema_validator._basic_schema_validation(valid_domain)
        assert len(errors) == 0
        
        # Test with missing fields
        invalid_domain = {"name": "test"}
        errors = schema_validator._basic_schema_validation(invalid_domain)
        assert len(errors) > 0
        assert any("description" in error for error in errors)


@pytest.mark.integration
class TestValidatorIntegration:
    """Integration tests for domain validator"""
    
    def test_full_validation_workflow(self):
        """Test complete validation workflow"""
        validator = DomainValidator()
        
        # Create test domains with various issues
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata("core", "yes", PackagePotential(0.8, [], [], "medium", []))
        
        domains = {
            "valid_domain": Domain(
                "valid_domain", "Valid domain for testing",
                ["src/valid/**/*.py"], ["valid"], [], [], tools, metadata
            ),
            "invalid_domain": Domain(
                "", "Invalid domain with empty name",
                [], [], [], ["nonexistent"], tools, metadata
            ),
            "circular_a": Domain(
                "circular_a", "Part of circular dependency",
                ["src/a/**/*.py"], [], [], ["circular_b"], tools, metadata
            ),
            "circular_b": Domain(
                "circular_b", "Part of circular dependency",
                ["src/b/**/*.py"], [], [], ["circular_a"], tools, metadata
            )
        }
        
        # Validate individual domains
        validation_results = validator.validate_domain_collection(domains)
        
        assert len(validation_results) == 4
        assert validation_results["valid_domain"].is_valid or len(validation_results["valid_domain"].errors) == 0
        assert not validation_results["invalid_domain"].is_valid
        
        # Check consistency
        consistency_issues = validator.check_consistency(domains)
        
        assert len(consistency_issues) > 0
        # Should find missing dependency and circular dependency issues
        dependency_issues = [issue for issue in consistency_issues if issue.category == IssueCategory.DEPENDENCY]
        assert len(dependency_issues) > 0
        
        # Check statistics
        stats = validator.get_validation_stats()
        assert stats['validations_performed'] >= 4
        assert stats['consistency_checks_performed'] >= 1
        assert stats['issues_found'] > 0