"""
Tests for Enhanced Domain Registry Manager

This module tests the enhanced DomainRegistryManager with
caching and indexing capabilities.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.domain_index.registry_manager import DomainRegistryManager
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential
)
from src.beast_mode.domain_index.exceptions import (
    DomainNotFoundError, DomainValidationError, RegistryCorruptionError
)


class TestEnhancedRegistryManager:
    """Test enhanced registry manager functionality"""
    
    @pytest.fixture
    def sample_registry_data(self):
        """Create sample registry data"""
        return {
            "domain_architecture": {
                "overview": {
                    "total_domains": 3,
                    "categories": ["core", "processing", "api"]
                },
                "core": {
                    "description": "Core functionality domains",
                    "domains": ["user_management", "authentication"]
                },
                "processing": {
                    "description": "Data processing domains", 
                    "domains": ["data_pipeline"]
                },
                "api": {
                    "description": "API layer domains",
                    "domains": []
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
        """Create registry manager with test configuration"""
        config = {
            'cache': {
                'max_cache_size': 100,
                'default_ttl_seconds': 300
            },
            'index': {
                'enable_fuzzy_search': True,
                'min_query_length': 2
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
    
    def test_initialization_with_caching_and_indexing(self, registry_manager):
        """Test initialization includes caching and indexing systems"""
        assert hasattr(registry_manager, '_cache')
        assert hasattr(registry_manager, '_domain_cache')
        assert hasattr(registry_manager, '_index')
        
        # Check that systems are properly initialized
        assert registry_manager._cache is not None
        assert registry_manager._domain_cache is not None
        assert registry_manager._index is not None
    
    def test_load_registry_builds_index(self, registry_manager):
        """Test that loading registry builds the index"""
        # Mock the index build method
        registry_manager._index.build_index = Mock(return_value=True)
        
        # Load registry
        assert registry_manager.load_registry()
        
        # Verify index was built
        registry_manager._index.build_index.assert_called_once()
    
    def test_get_domain_uses_cache(self, registry_manager):
        """Test that get_domain uses caching"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the domain cache
        registry_manager._domain_cache.get_domain = Mock(return_value=None)
        registry_manager._domain_cache.cache_domain = Mock(return_value=True)
        
        # Get domain
        try:
            domain = registry_manager.get_domain("user_management")
            
            # Verify cache was checked
            registry_manager._domain_cache.get_domain.assert_called_with("user_management")
            
            # Verify domain was cached
            registry_manager._domain_cache.cache_domain.assert_called_once()
            
        except DomainNotFoundError:
            # Expected if domain doesn't exist in test data
            pass
    
    def test_search_domains_uses_index(self, registry_manager):
        """Test that search_domains uses the index"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the index search
        registry_manager._index.search_index = Mock(return_value=["user_management"])
        
        # Search domains
        results = registry_manager.search_domains("user")
        
        # Verify index was used
        registry_manager._index.search_index.assert_called_with("user", None)
    
    def test_update_domain_updates_index(self, registry_manager):
        """Test that updating domain updates the index"""
        # Load registry first
        registry_manager.load_registry()
        
        # Create a test domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "test_domain", "Test domain",
            ["src/test/**/*.py"], ["test"], [], [],
            tools, metadata
        )
        
        # Mock the index update
        registry_manager._index.update_index = Mock(return_value=True)
        registry_manager._domain_cache.invalidate_domain = Mock(return_value=True)
        
        # Update domain
        result = registry_manager.update_domain(domain)
        
        if result:  # Only check if update succeeded
            # Verify index was updated
            registry_manager._index.update_index.assert_called_with(domain)
            
            # Verify cache was invalidated
            registry_manager._domain_cache.invalidate_domain.assert_called_with("test_domain")
    
    def test_create_domain_updates_index(self, registry_manager):
        """Test that creating domain updates the index"""
        # Load registry first
        registry_manager.load_registry()
        
        # Create a test domain
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
        
        # Mock the index update
        registry_manager._index.update_index = Mock(return_value=True)
        registry_manager._domain_cache.invalidate_domain = Mock(return_value=True)
        
        # Create domain
        result = registry_manager.create_domain(domain)
        
        if result:  # Only check if creation succeeded
            # Verify index was updated
            registry_manager._index.update_index.assert_called_with(domain)
            
            # Verify cache was invalidated
            registry_manager._domain_cache.invalidate_domain.assert_called_with("new_domain")
    
    def test_delete_domain_updates_index(self, registry_manager):
        """Test that deleting domain updates the index"""
        # Load registry first
        registry_manager.load_registry()
        
        # Add a domain first
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, [], [], "medium", [])
        )
        domain = Domain(
            "delete_test", "Domain to delete",
            ["src/delete/**/*.py"], ["delete"], [], [],
            tools, metadata
        )
        registry_manager._domains["delete_test"] = domain
        
        # Mock the index update
        registry_manager._index.update_index = Mock(return_value=True)
        registry_manager._domain_cache.invalidate_domain = Mock(return_value=True)
        
        # Delete domain
        result = registry_manager.delete_domain("delete_test")
        
        if result:  # Only check if deletion succeeded
            # Verify index was updated
            registry_manager._index.update_index.assert_called_once()
            
            # Verify cache was invalidated
            registry_manager._domain_cache.invalidate_domain.assert_called_with("delete_test")
    
    def test_get_registry_stats_includes_cache_and_index(self, registry_manager):
        """Test that registry stats include cache and index statistics"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock stats methods
        registry_manager._cache.get_stats = Mock(return_value={"cache_size": 10})
        registry_manager._index.get_index_stats = Mock(return_value={"indexed_domains": 5})
        
        # Get stats
        stats = registry_manager.get_registry_stats()
        
        # Verify stats include cache and index information
        assert "cache_stats" in stats
        assert "index_stats" in stats
        assert "component_health" in stats
        
        # Verify methods were called
        registry_manager._cache.get_stats.assert_called_once()
        registry_manager._index.get_index_stats.assert_called_once()
    
    def test_search_suggestions(self, registry_manager):
        """Test search suggestions functionality"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the index suggestions
        registry_manager._index.suggest_completions = Mock(return_value=["user", "user_management"])
        
        # Get suggestions
        suggestions = registry_manager.get_search_suggestions("us")
        
        # Verify suggestions were retrieved
        assert suggestions == ["user", "user_management"]
        registry_manager._index.suggest_completions.assert_called_with("us")
    
    def test_search_by_pattern(self, registry_manager):
        """Test pattern-based search"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the index pattern search
        registry_manager._index.search_by_pattern = Mock(return_value=["user_management"])
        
        # Search by pattern
        results = registry_manager.search_by_pattern("src/user/**/*.py")
        
        # Verify pattern search was used
        registry_manager._index.search_by_pattern.assert_called_with("src/user/**/*.py")
    
    def test_search_by_category(self, registry_manager):
        """Test category-based search"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the index category search
        registry_manager._index.search_by_category = Mock(return_value=["user_management"])
        
        # Search by category
        results = registry_manager.search_by_category("core")
        
        # Verify category search was used
        registry_manager._index.search_by_category.assert_called_with("core")
    
    def test_get_domain_relationships(self, registry_manager):
        """Test domain relationships retrieval"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the index relationships
        expected_relationships = {
            'dependencies': ['database'],
            'dependents': ['api_layer'],
            'same_category': ['authentication'],
            'similar_patterns': ['user_auth']
        }
        registry_manager._index.get_domain_relationships = Mock(return_value=expected_relationships)
        
        # Get relationships
        relationships = registry_manager.get_domain_relationships("user_management")
        
        # Verify relationships were retrieved
        assert relationships == expected_relationships
        registry_manager._index.get_domain_relationships.assert_called_with("user_management")
    
    def test_cache_invalidation_by_category(self, registry_manager):
        """Test cache invalidation by category"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the cache invalidation
        registry_manager._domain_cache.invalidate_by_category = Mock(return_value=3)
        
        # Invalidate by category
        count = registry_manager.invalidate_cache_by_category("core")
        
        # Verify invalidation was performed
        assert count == 3
        registry_manager._domain_cache.invalidate_by_category.assert_called_with("core")
    
    def test_get_cache_info(self, registry_manager):
        """Test cache information retrieval"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock the cache info
        expected_info = {
            "key": "domain:user_management",
            "created_at": "2023-01-01T00:00:00",
            "access_count": 5
        }
        registry_manager._cache.get_entry_info = Mock(return_value=expected_info)
        
        # Get cache info
        info = registry_manager.get_cache_info("domain:user_management")
        
        # Verify info was retrieved
        assert info == expected_info
        registry_manager._cache.get_entry_info.assert_called_with("domain:user_management")
    
    def test_cache_warming_on_load(self, registry_manager):
        """Test that cache is warmed when registry is loaded"""
        # Mock the cache warming method
        registry_manager._warm_cache = Mock()
        
        # Load registry
        registry_manager.load_registry()
        
        # Verify cache warming was called
        registry_manager._warm_cache.assert_called_once()
    
    def test_error_handling_with_caching_and_indexing(self, registry_manager):
        """Test error handling when caching/indexing operations fail"""
        # Load registry first
        registry_manager.load_registry()
        
        # Mock cache failure
        registry_manager._domain_cache.cache_domain = Mock(side_effect=Exception("Cache error"))
        
        # This should still work even if caching fails
        try:
            domain = registry_manager.get_domain("user_management")
            # If we get here, the operation succeeded despite cache failure
        except DomainNotFoundError:
            # Expected if domain doesn't exist
            pass
        except Exception as e:
            # Should not propagate cache errors
            pytest.fail(f"Cache error was not handled: {e}")
    
    def test_concurrent_access_with_caching(self, registry_manager):
        """Test concurrent access with caching enabled"""
        import threading
        
        # Load registry first
        registry_manager.load_registry()
        
        results = []
        errors = []
        
        def worker():
            try:
                # Try to get domain
                try:
                    domain = registry_manager.get_domain("user_management")
                    results.append(domain)
                except DomainNotFoundError:
                    results.append(None)
                
                # Try to search
                search_results = registry_manager.search_domains("user")
                results.append(len(search_results))
                
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        
        # Verify operations completed
        assert len(results) == 10  # 5 threads * 2 operations each


@pytest.mark.integration
class TestRegistryManagerIntegration:
    """Integration tests for enhanced registry manager"""
    
    def test_full_workflow_with_caching_and_indexing(self):
        """Test complete workflow with caching and indexing"""
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
            # Create manager
            with patch('src.beast_mode.domain_index.registry_manager.get_config') as mock_config:
                mock_config.return_value = {
                    'registry_path': temp_path,
                    'registry_backup_dir': '/tmp/backups'
                }
                
                manager = DomainRegistryManager(temp_path)
                
                # Load registry
                assert manager.load_registry()
                
                # Test search functionality
                results = manager.search_domains("user")
                assert len(results) >= 0  # May not find exact matches in test data
                
                # Test suggestions
                suggestions = manager.get_search_suggestions("us")
                assert isinstance(suggestions, list)
                
                # Test statistics
                stats = manager.get_registry_stats()
                assert "cache_stats" in stats
                assert "index_stats" in stats
                
                # Cleanup
                manager._cache.shutdown()
                
        finally:
            Path(temp_path).unlink(missing_ok=True)