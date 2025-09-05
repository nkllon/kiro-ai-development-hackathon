"""
Test Domain Registry Manager

Tests for the core domain registry management functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.beast_mode.domain_index.registry_manager import DomainRegistryManager
from src.beast_mode.domain_index.models import Domain, DomainTools, DomainMetadata, PackagePotential
from src.beast_mode.domain_index.exceptions import DomainNotFoundError, DomainValidationError


class TestDomainRegistryManager:
    """Test the domain registry manager"""
    
    @pytest.fixture
    def sample_registry_data(self):
        """Sample registry data for testing"""
        return {
            "domain_architecture": {
                "overview": {
                    "total_domains": 2
                },
                "core": {
                    "description": "Core domains",
                    "domains": ["test_domain", "core_domain"]
                },
                "tools": {
                    "description": "Tool domains", 
                    "domains": ["tool_domain"]
                }
            }
        }
    
    @pytest.fixture
    def temp_registry_file(self, sample_registry_data):
        """Create temporary registry file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_registry_data, f)
            return f.name
    
    def test_initialization(self):
        """Test registry manager initialization"""
        manager = DomainRegistryManager()
        
        assert manager.module_name == "domain_registry_manager"
        assert manager.load_count == 0
        assert not manager._registry_loaded
    
    def test_load_registry_success(self, temp_registry_file):
        """Test successful registry loading"""
        manager = DomainRegistryManager(temp_registry_file)
        
        result = manager.load_registry()
        
        assert result is True
        assert manager._registry_loaded is True
        assert manager.load_count == 1
        assert len(manager._domains) == 3  # test_domain, core_domain, tool_domain
    
    def test_load_registry_file_not_found(self):
        """Test registry loading with missing file"""
        manager = DomainRegistryManager("nonexistent.json")
        
        # Should return False and handle error gracefully
        result = manager.load_registry()
        assert result is False
    
    def test_get_domain_success(self, temp_registry_file):
        """Test successful domain retrieval"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        domain = manager.get_domain("test_domain")
        
        assert domain is not None
        assert domain.name == "test_domain"
        assert domain.metadata.demo_role == "core"
    
    def test_get_domain_not_found(self, temp_registry_file):
        """Test domain retrieval with non-existent domain"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        with pytest.raises(DomainNotFoundError):
            manager.get_domain("nonexistent_domain")
    
    def test_get_all_domains(self, temp_registry_file):
        """Test retrieving all domains"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        all_domains = manager.get_all_domains()
        
        assert len(all_domains) == 3
        assert "test_domain" in all_domains
        assert "core_domain" in all_domains
        assert "tool_domain" in all_domains
    
    def test_search_domains_by_name(self, temp_registry_file):
        """Test domain search by name"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        results = manager.search_domains("test")
        
        assert len(results) == 1
        assert results[0].name == "test_domain"
    
    def test_search_domains_with_filters(self, temp_registry_file):
        """Test domain search with filters"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        results = manager.search_domains("domain", {"category": "core"})
        
        assert len(results) == 2  # test_domain and core_domain
        for result in results:
            assert result.metadata.demo_role == "core"
    
    def test_validate_domain_success(self, temp_registry_file):
        """Test successful domain validation"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        domain = manager.get_domain("test_domain")
        validation = manager.validate_domain(domain)
        
        assert validation.is_valid is True
        assert len(validation.errors) == 0
    
    def test_validate_domain_with_errors(self):
        """Test domain validation with errors"""
        manager = DomainRegistryManager()
        
        # Create invalid domain
        tools = DomainTools(linter="", formatter="", validator="")
        metadata = DomainMetadata(
            demo_role="test",
            extraction_candidate="no",
            package_potential=PackagePotential(score=0.0, reasons=[], dependencies=[], estimated_effort="low", blockers=[])
        )
        
        invalid_domain = Domain(
            name="",  # Invalid: empty name
            description="",
            patterns=[],  # Invalid: no patterns
            content_indicators=[],
            requirements=[],
            dependencies=[],
            tools=tools,
            metadata=metadata
        )
        
        validation = manager.validate_domain(invalid_domain)
        
        assert validation.is_valid is False
        assert len(validation.errors) > 0
        assert "Domain name is required" in validation.errors
        assert "Domain must have at least one file pattern" in validation.errors
    
    def test_create_domain_success(self, temp_registry_file):
        """Test successful domain creation"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        # Create new domain
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        metadata = DomainMetadata(
            demo_role="test",
            extraction_candidate="no",
            package_potential=PackagePotential(score=0.5, reasons=[], dependencies=[], estimated_effort="low", blockers=[])
        )
        
        new_domain = Domain(
            name="new_domain",
            description="A new test domain",
            patterns=["src/new/**/*.py"],
            content_indicators=["new_"],
            requirements=[],
            dependencies=[],
            tools=tools,
            metadata=metadata
        )
        
        result = manager.create_domain(new_domain)
        
        assert result is True
        assert "new_domain" in manager._domains
        
        # Verify we can retrieve it
        retrieved = manager.get_domain("new_domain")
        assert retrieved.name == "new_domain"
    
    def test_create_domain_already_exists(self, temp_registry_file):
        """Test creating domain that already exists"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        existing_domain = manager.get_domain("test_domain")
        
        result = manager.create_domain(existing_domain)
        
        assert result is False
    
    def test_update_domain_success(self, temp_registry_file):
        """Test successful domain update"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        domain = manager.get_domain("test_domain")
        domain.description = "Updated description"
        
        result = manager.update_domain(domain)
        
        assert result is True
        
        # Verify update
        updated_domain = manager.get_domain("test_domain")
        assert updated_domain.description == "Updated description"
    
    def test_delete_domain_success(self, temp_registry_file):
        """Test successful domain deletion"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        result = manager.delete_domain("test_domain")
        
        assert result is True
        assert "test_domain" not in manager._domains
        
        # Verify deletion
        with pytest.raises(DomainNotFoundError):
            manager.get_domain("test_domain")
    
    def test_delete_domain_not_found(self, temp_registry_file):
        """Test deleting non-existent domain"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        # Should return False and handle error gracefully
        result = manager.delete_domain("nonexistent_domain")
        assert result is False
    
    def test_get_dependencies(self, temp_registry_file):
        """Test getting domain dependencies"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        dep_graph = manager.get_dependencies("test_domain")
        
        assert dep_graph.domain == "test_domain"
        assert isinstance(dep_graph.direct_dependencies, list)
    
    def test_registry_stats(self, temp_registry_file):
        """Test getting registry statistics"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        stats = manager.get_registry_stats()
        
        assert stats["total_domains"] == 3
        assert stats["registry_loaded"] is True
        assert stats["load_count"] == 1
        assert "cache_stats" in stats
    
    def test_reload_registry(self, temp_registry_file):
        """Test registry reloading"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        initial_load_count = manager.load_count
        
        result = manager.reload_registry()
        
        assert result is True
        assert manager.load_count == initial_load_count + 1
    
    def test_caching_behavior(self, temp_registry_file):
        """Test caching behavior"""
        manager = DomainRegistryManager(temp_registry_file)
        manager.load_registry()
        
        # First call should cache the result
        domain1 = manager.get_domain("test_domain")
        
        # Second call should use cache
        domain2 = manager.get_domain("test_domain")
        
        assert domain1 is not None
        assert domain2 is not None
        assert domain1.name == domain2.name
        
        # Check cache stats
        cache_stats = manager.get_cache_stats()
        assert cache_stats["cache_hits"] > 0


if __name__ == "__main__":
    pytest.main([__file__])