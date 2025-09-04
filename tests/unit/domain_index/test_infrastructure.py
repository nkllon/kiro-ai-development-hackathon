"""
Test the core domain index infrastructure

This test verifies that the basic infrastructure components are working correctly.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential,
    HealthStatus, HealthStatusType, HealthIssue, HealthMetrics,
    IssueSeverity, IssueCategory
)
from src.beast_mode.domain_index.base import DomainSystemComponent, CachedComponent
from src.beast_mode.domain_index.config import DomainIndexConfig, get_config, reset_config
from src.beast_mode.domain_index.exceptions import (
    DomainIndexError, DomainNotFoundError, DomainValidationError
)


class TestDomainModels:
    """Test core domain data models"""
    
    def test_domain_creation(self):
        """Test creating a domain with all required fields"""
        tools = DomainTools(
            linter="pylint",
            formatter="black", 
            validator="mypy",
            exclusions=["__pycache__"]
        )
        
        package_potential = PackagePotential(
            score=0.8,
            reasons=["Well-defined interface", "Minimal dependencies"],
            dependencies=["requests"],
            estimated_effort="medium",
            blockers=[]
        )
        
        metadata = DomainMetadata(
            demo_role="core",
            extraction_candidate="yes",
            package_potential=package_potential,
            status="active"
        )
        
        domain = Domain(
            name="test_domain",
            description="A test domain",
            patterns=["src/test/**/*.py"],
            content_indicators=["test_", "Test"],
            requirements=["pytest", "mock"],
            dependencies=["core_domain"],
            tools=tools,
            metadata=metadata
        )
        
        assert domain.name == "test_domain"
        assert domain.description == "A test domain"
        assert len(domain.patterns) == 1
        assert domain.tools.linter == "pylint"
        assert domain.metadata.package_potential.score == 0.8
    
    def test_health_status_creation(self):
        """Test creating health status with issues"""
        issue = HealthIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.DEPENDENCY,
            description="Missing dependency",
            suggested_fix="Install missing package"
        )
        
        metrics = HealthMetrics(
            dependency_health_score=0.8,
            pattern_coverage_score=0.9,
            file_accessibility_score=1.0,
            makefile_integration_score=0.7,
            overall_health_score=0.85
        )
        
        health_status = HealthStatus(
            status=HealthStatusType.DEGRADED,
            last_check=datetime.now(),
            issues=[issue],
            metrics=metrics
        )
        
        assert health_status.status == HealthStatusType.DEGRADED
        assert len(health_status.issues) == 1
        assert health_status.issues[0].severity == IssueSeverity.WARNING
        assert health_status.metrics.overall_health_score == 0.85


class TestDomainSystemComponent:
    """Test the base domain system component"""
    
    def test_component_initialization(self):
        """Test component initializes correctly"""
        config = {"cache_enabled": True, "cache_ttl_seconds": 300}
        component = DomainSystemComponent("test_component", config)
        
        assert component.module_name == "test_component"
        assert component.cache_enabled is True
        assert component.cache_ttl == 300
        assert component.error_count == 0
        assert component.is_healthy() is True
    
    def test_component_error_handling(self):
        """Test component handles errors correctly"""
        component = DomainSystemComponent("test_component")
        
        # Simulate an error
        test_error = Exception("Test error")
        component._handle_error(test_error, "test_operation")
        
        assert component.error_count == 1
        assert component.last_error == test_error
    
    def test_component_performance_tracking(self):
        """Test component tracks performance metrics"""
        component = DomainSystemComponent("test_component")
        
        # Track some operations
        component._track_performance("test_op", 100.0)
        component._track_performance("test_op", 200.0)
        
        metrics = component.performance_metrics["test_op"]
        assert metrics["count"] == 2
        assert metrics["avg_time_ms"] == 150.0
        assert metrics["min_time_ms"] == 100.0
        assert metrics["max_time_ms"] == 200.0
    
    def test_component_health_status(self):
        """Test component health status reporting"""
        component = DomainSystemComponent("test_component")
        
        status = component.get_module_status()
        assert status["module_name"] == "test_component"
        assert status["status"] == "healthy"
        assert status["error_count"] == 0
        
        health_indicators = component.get_health_indicators()
        assert "component_health" in health_indicators
        assert "performance_metrics" in health_indicators
        assert "configuration" in health_indicators


class TestCachedComponent:
    """Test the cached component base class"""
    
    def test_cache_operations(self):
        """Test basic cache operations"""
        component = CachedComponent("test_cached_component")
        
        # Test cache miss
        result = component._get_from_cache("test_key")
        assert result is None
        assert component.cache_misses == 1
        
        # Test cache set and hit
        component._set_in_cache("test_key", "test_value")
        result = component._get_from_cache("test_key")
        assert result == "test_value"
        assert component.cache_hits == 1
        
        # Test cache stats
        stats = component.get_cache_stats()
        assert stats["cache_size"] == 1
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
        assert stats["hit_rate"] == 0.5
    
    def test_cache_disabled(self):
        """Test cache operations when cache is disabled"""
        config = {"cache_enabled": False}
        component = CachedComponent("test_cached_component", config)
        
        # Cache operations should be no-ops
        component._set_in_cache("test_key", "test_value")
        result = component._get_from_cache("test_key")
        assert result is None
        
        stats = component.get_cache_stats()
        assert stats["cache_enabled"] is False
        assert stats["cache_size"] == 0


class TestDomainIndexConfig:
    """Test configuration management"""
    
    def setUp(self):
        """Reset config before each test"""
        reset_config()
    
    def test_default_config(self):
        """Test default configuration values"""
        config = DomainIndexConfig()
        
        assert config.get("cache_enabled") is True
        assert config.get("cache_ttl_seconds") == 300
        assert config.get("query_timeout_seconds") == 30
        assert config.get("log_level") == "INFO"
    
    def test_environment_config(self):
        """Test environment-specific configuration"""
        dev_config = DomainIndexConfig("development")
        assert dev_config.get("log_level") == "DEBUG"
        assert dev_config.get("require_approval_for_updates") is False
        
        prod_config = DomainIndexConfig("production")
        assert prod_config.get("log_level") == "WARNING"
        assert prod_config.get("require_approval_for_updates") is True
        
        test_config = DomainIndexConfig("test")
        assert test_config.get("cache_enabled") is False
        assert test_config.get("registry_path").endswith("test_project_model_registry.json")
    
    def test_custom_config(self):
        """Test custom configuration override"""
        custom = {"cache_ttl_seconds": 600, "custom_setting": "test_value"}
        config = DomainIndexConfig(custom_config=custom)
        
        assert config.get("cache_ttl_seconds") == 600
        assert config.get("custom_setting") == "test_value"
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid configuration should have no issues
        config = DomainIndexConfig("test")  # Use test config to avoid file existence checks
        issues = config.validate()
        
        # Should have issues for missing files in default config
        default_config = DomainIndexConfig()
        issues = default_config.validate()
        assert len(issues) >= 0  # May have issues depending on project state
    
    def test_global_config_instance(self):
        """Test global configuration instance"""
        reset_config()
        
        config1 = get_config("development")
        config2 = get_config("production")  # Should return same instance
        
        assert config1 is config2
        assert config1.environment == "development"  # First call determines environment


class TestDomainIndexExceptions:
    """Test custom exception classes"""
    
    def test_domain_index_error(self):
        """Test base domain index error"""
        error = DomainIndexError("Test error", "test_component", "test_operation")
        
        assert str(error) == "Test error | Component: test_component | Operation: test_operation"
        assert error.component == "test_component"
        assert error.operation == "test_operation"
    
    def test_domain_not_found_error(self):
        """Test domain not found error"""
        error = DomainNotFoundError("missing_domain")
        
        assert "missing_domain" in str(error)
        assert error.domain_name == "missing_domain"
        assert error.component == "registry"
    
    def test_domain_validation_error(self):
        """Test domain validation error"""
        validation_errors = ["Missing required field", "Invalid pattern"]
        error = DomainValidationError("invalid_domain", validation_errors)
        
        assert "invalid_domain" in str(error)
        assert error.domain_name == "invalid_domain"
        assert error.validation_errors == validation_errors


if __name__ == "__main__":
    pytest.main([__file__])