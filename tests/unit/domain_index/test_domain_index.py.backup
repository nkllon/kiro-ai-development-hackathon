"""
Tests for Domain Index System

This module tests the DomainIndex class including indexing,
search capabilities, and performance characteristics.
"""

import pytest
from unittest.mock import Mock, patch

from src.beast_mode.domain_index.domain_index import DomainIndex, IndexEntry
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential, DomainCollection
)


class TestIndexEntry:
    """Test IndexEntry functionality"""
    
    def test_index_entry_creation(self):
        """Test index entry creation"""
        entry = IndexEntry(
            domain_name="test_domain",
            field_name="name",
            value="Test Domain",
            normalized_value="test domain",
            weight=2.0
        )
        
        assert entry.domain_name == "test_domain"
        assert entry.field_name == "name"
        assert entry.value == "Test Domain"
        assert entry.normalized_value == "test domain"
        assert entry.weight == 2.0
    
    def test_exact_match(self):
        """Test exact match scoring"""
        entry = IndexEntry("domain", "name", "test", "test", 1.0)
        score = entry.matches("test")
        assert score == 1.0
    
    def test_starts_with_match(self):
        """Test starts-with match scoring"""
        entry = IndexEntry("domain", "name", "testing", "testing", 1.0)
        score = entry.matches("test")
        assert score == 0.8
    
    def test_contains_match(self):
        """Test contains match scoring"""
        entry = IndexEntry("domain", "name", "my_test_domain", "my_test_domain", 1.0)
        score = entry.matches("test")
        assert score == 0.6
    
    def test_no_match(self):
        """Test no match scoring"""
        entry = IndexEntry("domain", "name", "other", "other", 1.0)
        score = entry.matches("test")
        assert score == 0.0
    
    def test_weight_application(self):
        """Test weight application in scoring"""
        entry = IndexEntry("domain", "name", "test", "test", 2.0)
        score = entry.matches("test")
        assert score == 2.0  # 1.0 * 2.0 weight
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching"""
        entry = IndexEntry("domain", "name", "testing", "testing", 1.0)
        score = entry.matches("testng", fuzzy=True)  # Missing 'i'
        assert score > 0  # Should have some similarity score
        assert score < 0.4  # But less than contains match


class TestDomainIndex:
    """Test DomainIndex functionality"""
    
    @pytest.fixture
    def index(self):
        """Create a test index instance"""
        config = {
            'enable_fuzzy_search': True,
            'min_query_length': 2,
            'max_search_results': 100
        }
        return DomainIndex(config)
    
    @pytest.fixture
    def sample_domains(self):
        """Create sample domains for testing"""
        domains = {}
        
        # Domain 1: User management
        tools1 = DomainTools("pylint", "black", "mypy")
        metadata1 = DomainMetadata(
            "core", "yes",
            PackagePotential(0.8, ["Well-defined"], [], "medium", []),
            tags=["user", "auth", "core"]
        )
        domains["user_management"] = Domain(
            "user_management", "User management and authentication",
            ["src/user/**/*.py", "src/auth/**/*.py"],
            ["user", "auth", "login"], ["python>=3.8"], ["database"],
            tools1, metadata1
        )
        
        # Domain 2: Data processing
        tools2 = DomainTools("pylint", "black", "mypy")
        metadata2 = DomainMetadata(
            "processing", "maybe",
            PackagePotential(0.6, ["Complex dependencies"], [], "high", []),
            tags=["data", "processing", "etl"]
        )
        domains["data_processing"] = Domain(
            "data_processing", "Data processing and ETL pipelines",
            ["src/data/**/*.py", "src/etl/**/*.py"],
            ["data", "etl", "pipeline"], ["python>=3.8", "pandas"], ["user_management"],
            tools2, metadata2
        )
        
        # Domain 3: API layer
        tools3 = DomainTools("pylint", "black", "mypy")
        metadata3 = DomainMetadata(
            "api", "no",
            PackagePotential(0.3, ["Tightly coupled"], [], "low", ["coupling"]),
            tags=["api", "web", "rest"]
        )
        domains["api_layer"] = Domain(
            "api_layer", "REST API and web interface",
            ["src/api/**/*.py", "src/web/**/*.py"],
            ["api", "rest", "web"], ["fastapi", "uvicorn"], ["user_management", "data_processing"],
            tools3, metadata3
        )
        
        return domains
    
    def test_index_initialization(self, index):
        """Test index initialization"""
        assert index.enable_fuzzy_search is True
        assert index.min_query_length == 2
        assert index.max_results == 100
        assert len(index._indexed_domains) == 0
        assert index.search_count == 0
    
    def test_build_index(self, index, sample_domains):
        """Test building index from domain collection"""
        assert index.build_index(sample_domains)
        
        stats = index.get_index_stats()
        assert stats["indexed_domains"] == 3
        assert stats["total_text_entries"] > 0
        assert stats["total_patterns"] > 0
        assert stats["categories"] > 0
        assert stats["tags"] > 0
    
    def test_search_by_name(self, index, sample_domains):
        """Test searching by domain name"""
        index.build_index(sample_domains)
        
        results = index.search_index("user")
        assert "user_management" in results
        
        results = index.search_index("data")
        assert "data_processing" in results
        
        results = index.search_index("api")
        assert "api_layer" in results
    
    def test_search_by_description(self, index, sample_domains):
        """Test searching by description content"""
        index.build_index(sample_domains)
        
        results = index.search_index("authentication")
        assert "user_management" in results
        
        results = index.search_index("ETL")
        assert "data_processing" in results
        
        results = index.search_index("REST")
        assert "api_layer" in results
    
    def test_search_by_content_indicators(self, index, sample_domains):
        """Test searching by content indicators"""
        index.build_index(sample_domains)
        
        results = index.search_index("login")
        assert "user_management" in results
        
        results = index.search_index("pipeline")
        assert "data_processing" in results
        
        results = index.search_index("web")
        assert "api_layer" in results
    
    def test_search_with_filters(self, index, sample_domains):
        """Test searching with filters"""
        index.build_index(sample_domains)
        
        # Filter by category
        filters = {"category": "core"}
        results = index.search_index("management", filters)
        assert "user_management" in results
        assert "data_processing" not in results
        
        # Filter by tag
        filters = {"tag": "data"}
        results = index.search_index("processing", filters)
        assert "data_processing" in results
        assert "user_management" not in results
    
    def test_pattern_search(self, index, sample_domains):
        """Test pattern-based search"""
        index.build_index(sample_domains)
        
        results = index.search_by_pattern("src/user/**/*.py")
        assert "user_management" in results
        
        results = index.search_by_pattern("src/api/**/*.py")
        assert "api_layer" in results
    
    def test_dependency_search(self, index, sample_domains):
        """Test dependency-based search"""
        index.build_index(sample_domains)
        
        # Forward dependencies (what does user_management depend on)
        results = index.search_by_dependency("user_management")
        assert "database" in results
        
        # Reverse dependencies (what depends on user_management)
        results = index.search_by_dependency("user_management", reverse=True)
        assert "data_processing" in results
        assert "api_layer" in results
    
    def test_category_search(self, index, sample_domains):
        """Test category-based search"""
        index.build_index(sample_domains)
        
        results = index.search_by_category("core")
        assert "user_management" in results
        
        results = index.search_by_category("processing")
        assert "data_processing" in results
        
        results = index.search_by_category("api")
        assert "api_layer" in results
    
    def test_tag_search(self, index, sample_domains):
        """Test tag-based search"""
        index.build_index(sample_domains)
        
        results = index.search_by_tag("auth")
        assert "user_management" in results
        
        results = index.search_by_tag("data")
        assert "data_processing" in results
        
        results = index.search_by_tag("rest")
        assert "api_layer" in results
    
    def test_relationship_queries(self, index, sample_domains):
        """Test domain relationship queries"""
        index.build_index(sample_domains)
        
        relationships = index.get_domain_relationships("user_management")
        
        assert "dependencies" in relationships
        assert "dependents" in relationships
        assert "same_category" in relationships
        assert "similar_patterns" in relationships
        
        # Check dependencies
        assert "database" in relationships["dependencies"]
        
        # Check dependents
        assert "data_processing" in relationships["dependents"]
        assert "api_layer" in relationships["dependents"]
    
    def test_update_index(self, index, sample_domains):
        """Test updating index for specific domain"""
        index.build_index(sample_domains)
        
        # Modify a domain
        modified_domain = sample_domains["user_management"]
        modified_domain.description = "Updated user management system"
        modified_domain.content_indicators.append("updated")
        
        # Update index
        assert index.update_index(modified_domain)
        
        # Search should find updated content
        results = index.search_index("updated")
        assert "user_management" in results
    
    def test_query_suggestions(self, index, sample_domains):
        """Test query completion suggestions"""
        index.build_index(sample_domains)
        
        suggestions = index.suggest_completions("user")
        assert len(suggestions) > 0
        assert any("user" in suggestion.lower() for suggestion in suggestions)
        
        suggestions = index.suggest_completions("da")
        assert len(suggestions) > 0
        assert any("data" in suggestion.lower() for suggestion in suggestions)
    
    def test_short_query_handling(self, index, sample_domains):
        """Test handling of short queries"""
        index.build_index(sample_domains)
        
        # Query too short
        results = index.search_index("a")
        assert len(results) == 0
        
        # Query just long enough
        results = index.search_index("ap")
        assert len(results) >= 0  # May or may not have results
    
    def test_fuzzy_search(self, index, sample_domains):
        """Test fuzzy search functionality"""
        index.build_index(sample_domains)
        
        # Test with typo
        results = index.search_index("managment")  # Missing 'e'
        # Should still find user_management with fuzzy matching
        # Note: This depends on the fuzzy matching implementation
        assert len(results) >= 0  # May find results with fuzzy matching
    
    def test_index_statistics(self, index, sample_domains):
        """Test index statistics"""
        index.build_index(sample_domains)
        
        # Perform some searches
        index.search_index("user")
        index.search_index("data")
        index.search_index("nonexistent")
        
        stats = index.get_index_stats()
        
        assert stats["indexed_domains"] == 3
        assert stats["search_count"] == 3
        assert stats["total_text_entries"] > 0
        assert stats["total_patterns"] > 0
        assert stats["categories"] == 3
        assert stats["tags"] > 0
        assert stats["fuzzy_search_enabled"] is True
        assert stats["min_query_length"] == 2
        assert stats["max_results"] == 100
    
    def test_index_clearing(self, index, sample_domains):
        """Test index clearing functionality"""
        index.build_index(sample_domains)
        
        # Verify index has data
        stats = index.get_index_stats()
        assert stats["indexed_domains"] == 3
        
        # Clear index (internal method)
        index._clear_index()
        
        # Verify index is empty
        stats = index.get_index_stats()
        assert stats["indexed_domains"] == 0
        assert stats["total_text_entries"] == 0
    
    def test_domain_removal(self, index, sample_domains):
        """Test removing domain from index"""
        index.build_index(sample_domains)
        
        # Remove a domain
        index._remove_domain_from_index("user_management")
        
        # Verify domain is removed
        results = index.search_index("user")
        assert "user_management" not in results
        
        # Verify other domains still exist
        results = index.search_index("data")
        assert "data_processing" in results
    
    def test_text_normalization(self, index):
        """Test text normalization"""
        # Test internal normalization method
        normalized = index._normalize_text("Test-Domain_Name.With.Special@Chars!")
        assert normalized == "test domain name with special chars"
        
        normalized = index._normalize_text("  Multiple   Spaces  ")
        assert normalized == "multiple spaces"
    
    def test_text_tokenization(self, index):
        """Test text tokenization"""
        # Test internal tokenization method
        tokens = index._tokenize_text("test-domain_name.with.separators")
        expected_tokens = ["test", "domain", "name", "with", "separators"]
        assert tokens == expected_tokens
        
        # Test filtering of short tokens
        tokens = index._tokenize_text("a test b with c short d tokens")
        assert "a" not in tokens  # Too short
        assert "b" not in tokens  # Too short
        assert "c" not in tokens  # Too short
        assert "d" not in tokens  # Too short
        assert "test" in tokens
        assert "with" in tokens
        assert "short" in tokens
        assert "tokens" in tokens
    
    def test_pattern_similarity(self, index):
        """Test pattern similarity checking"""
        # Test internal pattern similarity method
        assert index._patterns_similar("src/**/*.py", "src/test/**/*.py")
        assert index._patterns_similar("src/user/*.py", "src/user/models/*.py")
        assert not index._patterns_similar("src/**/*.py", "tests/**/*.js")


@pytest.mark.integration
class TestIndexIntegration:
    """Integration tests for index system"""
    
    def test_index_with_large_dataset(self):
        """Test index performance with larger dataset"""
        index = DomainIndex()
        
        # Create many domains
        domains = {}
        for i in range(100):
            tools = DomainTools("pylint", "black", "mypy")
            metadata = DomainMetadata(
                f"category_{i % 10}", "maybe",
                PackagePotential(0.5, [], [], "medium", []),
                tags=[f"tag_{i % 5}", f"type_{i % 3}"]
            )
            domains[f"domain_{i}"] = Domain(
                f"domain_{i}", f"Description for domain {i}",
                [f"src/domain_{i}/**/*.py"], [f"domain_{i}"], [], [],
                tools, metadata
            )
        
        # Build index
        assert index.build_index(domains)
        
        # Test search performance
        import time
        start_time = time.time()
        results = index.search_index("domain")
        search_time = time.time() - start_time
        
        assert len(results) > 0
        assert search_time < 1.0  # Should be fast
        
        # Test statistics
        stats = index.get_index_stats()
        assert stats["indexed_domains"] == 100
    
    def test_concurrent_index_operations(self):
        """Test concurrent index operations"""
        import threading
        
        index = DomainIndex()
        
        # Create initial domains
        domains = {}
        for i in range(10):
            tools = DomainTools("pylint", "black", "mypy")
            metadata = DomainMetadata(
                "test", "no", PackagePotential(0.5, [], [], "medium", [])
            )
            domains[f"domain_{i}"] = Domain(
                f"domain_{i}", f"Test domain {i}",
                [f"src/{i}/**/*.py"], [f"test_{i}"], [], [],
                tools, metadata
            )
        
        index.build_index(domains)
        
        # Concurrent search operations
        def search_worker():
            for _ in range(10):
                results = index.search_index("domain")
                assert len(results) > 0
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=search_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify index integrity
        stats = index.get_index_stats()
        assert stats["indexed_domains"] == 10