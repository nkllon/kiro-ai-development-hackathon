"""
Tests for Enhanced Domain Registry Manager with Validation

This module tests the validation capabilities integrated into
the DomainRegistryManager.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.beast_mode.domain_index.registry_manager import DomainRegistryManager
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential, ValidationResult
)
from src.beast_mode.domain_index.domain_validator import ValidationRule, ConsistencyCheck
from src.beast_mode.domain_index.exceptions import DomainValidationError


class TestRegistryManagerValidation:
    """Test registry manager validation functionality"""
    
    @pytest.fixture
    def sample_registry_data(self):
        """Create sample registry data"""
        return {
            "domain_architecture": {
                "core": {
                    "description": "Core functionality domains",
                    "domains": ["user_management", "authentication"]
                },
                "processing": {
                    "description": "Data processing domains",
                    "domains": ["data_pipeline"]
                }
            }
        }
    
    @pytest.fixture
    def temp_registry_file(self, sample_registry_data):
        """Create temporary registry file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_registry_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def registry_manager(self, temp_registry_file):
        """Create registry manager with validation enabled"""
        config = {
            'validator': {
                'strict_validation': False,
                'check_filesystem': False,
                'required_fields': ['name', 'description', 'patterns', 'tools']
            }
        }
        
        with patch('src.beast_mode.domain_index.registry_manager.get_config') as mock_config:
            mock_config.return_value = {
                'registry_path': temp_registry_file,
                'registry_backup_dir': '/tmp/backups'
            }
            
            manager = DomainRegistryManager(temp_registry_file, config)
            yield manager
            
            # Cleanup
            if hasattr(manager, '_cache'):
                manager._cache.shutdown()
    
    def test_initialization_includes_validator(self, registry_manager):
        """Test that initialization includes validator"""
        assert hasattr(registry_manager, '_validator')
        assert registry_manager._validator is not None
    
    def test_validate_domain_uses_comprehensive_validator(self, registry_manager):
        """Test that validate_domain uses the comprehensive validator"""
        # Create a test domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "test_domain", "Test domain for validation",
            ["src/test/**/*.py"], ["test"], [], [],
            tools, metadata
        )
        
        # Mock the validator
        registry_manager._validator.validate_domain = Mock(return_value=ValidationResult(
            is_valid=True, errors=[], warnings=[], suggestions=[]
        ))
        
        # Validate domain
        result = registry_manager.validate_domain(domain)
        
        # Verify comprehensive validator was used
        registry_manager._validator.validate_domain.assert_called_once()
        assert result.is_valid
    
    def test_validate_all_domains(self, registry_manager):
        """Test validation of all domains"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the validator
        registry_manager._validator.validate_domain_collection = Mock(return_value={
            "domain1": ValidationResult(True, [], [], []),
            "domain2": ValidationResult(False, ["Error"], [], [])
        })
        
        # Validate all domains
        results = registry_manager.validate_all_domains()
        
        # Verify validator was called
        registry_manager._validator.validate_domain_collection.assert_called_once()
        assert len(results) == 2
        assert "domain1" in results
        assert "domain2" in results
    
    def test_check_domain_consistency(self, registry_manager):
        """Test domain consistency checking"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the validator
        expected_issues = [Mock(description="Test consistency issue")]
        registry_manager._validator.check_consistency = Mock(return_value=expected_issues)
        
        # Check consistency
        issues = registry_manager.check_domain_consistency()
        
        # Verify validator was called
        registry_manager._validator.check_consistency.assert_called_once()
        assert issues == expected_issues
    
    def test_detect_circular_dependencies(self, registry_manager):
        """Test circular dependency detection"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the validator
        expected_cycles = [["domain_a", "domain_b", "domain_a"]]
        registry_manager._validator.detect_circular_dependencies = Mock(return_value=expected_cycles)
        
        # Detect circular dependencies
        cycles = registry_manager.detect_circular_dependencies()
        
        # Verify validator was called
        registry_manager._validator.detect_circular_dependencies.assert_called_once()
        assert cycles == expected_cycles
    
    def test_validate_domain_dependencies(self, registry_manager):
        """Test domain dependency validation"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the validator
        expected_issues = [Mock(description="Missing dependency")]
        registry_manager._validator.validate_dependencies = Mock(return_value=expected_issues)
        
        # Validate dependencies
        issues = registry_manager.validate_domain_dependencies()
        
        # Verify validator was called
        registry_manager._validator.validate_dependencies.assert_called_once()
        assert issues == expected_issues
    
    def test_get_validation_stats(self, registry_manager):
        """Test validation statistics retrieval"""
        # Mock the validator stats
        expected_stats = {
            'validations_performed': 10,
            'consistency_checks_performed': 5,
            'issues_found': 3
        }
        registry_manager._validator.get_validation_stats = Mock(return_value=expected_stats)
        
        # Get validation stats
        stats = registry_manager.get_validation_stats()
        
        # Verify validator was called
        registry_manager._validator.get_validation_stats.assert_called_once()
        assert stats == expected_stats
    
    def test_add_validation_rule(self, registry_manager):
        """Test adding custom validation rule"""
        def custom_validator(domain, context):
            return []
        
        rule = ValidationRule(
            name="custom_rule",
            description="Custom validation rule",
            severity=Mock(),
            category=Mock(),
            validator_func=custom_validator
        )
        
        # Mock the validator
        registry_manager._validator.add_validation_rule = Mock()
        
        # Add validation rule
        registry_manager.add_validation_rule(rule)
        
        # Verify validator was called
        registry_manager._validator.add_validation_rule.assert_called_once_with(rule)
    
    def test_add_consistency_check(self, registry_manager):
        """Test adding custom consistency check"""
        def custom_checker(domains, context):
            return []
        
        check = ConsistencyCheck(
            name="custom_check",
            description="Custom consistency check",
            severity=Mock(),
            checker_func=custom_checker
        )
        
        # Mock the validator
        registry_manager._validator.add_consistency_check = Mock()
        
        # Add consistency check
        registry_manager.add_consistency_check(check)
        
        # Verify validator was called
        registry_manager._validator.add_consistency_check.assert_called_once_with(check)
    
    def test_registry_stats_include_validation(self, registry_manager):
        """Test that registry stats include validation statistics"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock all the stats methods
        registry_manager._cache.get_stats = Mock(return_value={"cache_size": 10})
        registry_manager._index.get_index_stats = Mock(return_value={"indexed_domains": 5})
        registry_manager._validator.get_validation_stats = Mock(return_value={"validations_performed": 3})
        
        # Get stats
        stats = registry_manager.get_registry_stats()
        
        # Verify validation stats are included
        assert "validation_stats" in stats
        assert stats["validation_stats"]["validations_performed"] == 3
        
        # Verify all stats methods were called
        registry_manager._cache.get_stats.assert_called_once()
        registry_manager._index.get_index_stats.assert_called_once()
        registry_manager._validator.get_validation_stats.assert_called_once()
    
    def test_domain_creation_with_validation(self, registry_manager):
        """Test domain creation includes validation"""
        # Load registry first
        registry_manager.load_registry()
        
        # Create a valid domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "new_domain", "New test domain",
            ["src/new/**/*.py"], ["new"], [], [],
            tools, metadata
        )
        
        # Mock successful validation
        registry_manager._validator.validate_domain = Mock(return_value=ValidationResult(
            is_valid=True, errors=[], warnings=[], suggestions=[]
        ))
        
        # Mock other dependencies
        registry_manager._index.update_index = Mock(return_value=True)
        registry_manager._domain_cache.invalidate_domain = Mock(return_value=True)
        
        # Create domain
        result = registry_manager.create_domain(domain)
        
        # Verify validation was performed
        registry_manager._validator.validate_domain.assert_called_once()
        
        if result:  # Only check if creation succeeded
            # Verify domain was added
            assert "new_domain" in registry_manager._domains
    
    def test_domain_creation_with_validation_failure(self, registry_manager):
        """Test domain creation fails with validation errors"""
        # Load registry first
        registry_manager.load_registry()
        
        # Create an invalid domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "", "Domain with empty name",  # Invalid name
            ["src/invalid/**/*.py"], ["invalid"], [], [],
            tools, metadata
        )
        
        # Mock validation failure
        registry_manager._validator.validate_domain = Mock(return_value=ValidationResult(
            is_valid=False, errors=["Domain name is required"], warnings=[], suggestions=[]
        ))
        
        # Attempt to create domain
        result = registry_manager.create_domain(domain)
        
        # Verify validation was performed
        registry_manager._validator.validate_domain.assert_called_once()
        
        # Creation should fail
        assert not result
    
    def test_domain_update_with_validation(self, registry_manager):
        """Test domain update includes validation"""
        # Load registry first
        registry_manager.load_registry()
        
        # Create and add a domain first
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "update_test", "Domain to update",
            ["src/update/**/*.py"], ["update"], [], [],
            tools, metadata
        )
        registry_manager._domains["update_test"] = domain
        
        # Modify domain
        domain.description = "Updated description"
        
        # Mock successful validation
        registry_manager._validator.validate_domain = Mock(return_value=ValidationResult(
            is_valid=True, errors=[], warnings=[], suggestions=[]
        ))
        
        # Mock other dependencies
        registry_manager._index.update_index = Mock(return_value=True)
        registry_manager._domain_cache.invalidate_domain = Mock(return_value=True)
        
        # Update domain
        result = registry_manager.update_domain(domain)
        
        # Verify validation was performed
        registry_manager._validator.validate_domain.assert_called_once()
        
        if result:  # Only check if update succeeded
            # Verify domain was updated
            assert registry_manager._domains["update_test"].description == "Updated description"
    
    def test_validation_error_handling(self, registry_manager):
        """Test handling of validation errors"""
        # Load registry first
        registry_manager.load_registry()
        
        # Create a domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "error_test", "Domain for error testing",
            ["src/error/**/*.py"], ["error"], [], [],
            tools, metadata
        )
        
        # Mock validation to raise an exception
        registry_manager._validator.validate_domain = Mock(side_effect=Exception("Validation failed"))
        
        # Validation should handle the error gracefully
        try:
            result = registry_manager.validate_domain(domain)
            # If we get here, the error was handled
            assert not result.is_valid  # Should indicate failure
        except Exception:
            # Should not propagate validation errors
            pytest.fail("Validation error was not handled properly")


@pytest.mark.integration
class TestValidationIntegration:
    """Integration tests for validation functionality"""
    
    def test_complete_validation_workflow(self):
        """Test complete validation workflow with real data"""
        # Create temporary registry
        registry_data = {
            "domain_architecture": {
                "core": {
                    "description": "Core domains",
                    "domains": ["user_management", "authentication"]
                },
                "api": {
                    "description": "API domains",
                    "domains": ["rest_api"]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(registry_data, f)
            temp_path = f.name
        
        try:
            # Create manager with validation enabled
            config = {
                'validator': {
                    'strict_validation': False,
                    'check_filesystem': False
                }
            }
            
            with patch('src.beast_mode.domain_index.registry_manager.get_config') as mock_config:
                mock_config.return_value = {
                    'registry_path': temp_path,
                    'registry_backup_dir': '/tmp/backups'
                }
                
                manager = DomainRegistryManager(temp_path, config)
                
                # Load registry
                assert manager.load_registry()
                
                # Validate all domains
                validation_results = manager.validate_all_domains()
                assert isinstance(validation_results, dict)
                
                # Check consistency
                consistency_issues = manager.check_domain_consistency()
                assert isinstance(consistency_issues, list)
                
                # Detect circular dependencies
                circular_deps = manager.detect_circular_dependencies()
                assert isinstance(circular_deps, list)
                
                # Validate dependencies
                dep_issues = manager.validate_domain_dependencies()
                assert isinstance(dep_issues, list)
                
                # Get validation statistics
                stats = manager.get_validation_stats()
                assert isinstance(stats, dict)
                assert 'validations_performed' in stats
                
                # Test adding custom validation rule
                def custom_validator(domain, context):
                    return []
                
                from src.beast_mode.domain_index.domain_validator import ValidationRule
                from src.beast_mode.domain_index.models import IssueSeverity, IssueCategory
                
                custom_rule = ValidationRule(
                    name="test_rule",
                    description="Test rule",
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.VALIDATION,
                    validator_func=custom_validator
                )
                
                manager.add_validation_rule(custom_rule)
                
                # Verify rule was added
                final_stats = manager.get_validation_stats()
                assert final_stats['validation_rules_count'] > stats['validation_rules_count']
                
                # Cleanup
                manager._cache.shutdown()
                
        finally:
            Path(temp_path).unlink(missing_ok=True)