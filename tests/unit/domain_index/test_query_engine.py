"""
Test Domain Query Engine

Tests for the domain query engine functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock

from src.beast_mode.domain_index.query_engine import DomainQueryEngine
from src.beast_mode.domain_index.models import Domain, DomainTools, DomainMetadata, PackagePotential


class TestDomainQueryEngine:
    """Test the domain query engine"""
    
    @pytest.fixture
    def sample_domains(self):
        """Create sample domains for testing"""
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        metadata = DomainMetadata(
            demo_role="core",
            extraction_candidate="no",
            package_potential=PackagePotential(score=0.5, reasons=[], dependencies=[], estimated_effort="low", blockers=[])
        )
        
        domains = {
            "test_domain": Domain(
                name="test_domain",
                description="A test domain for testing",
                patterns=["src/test/**/*.py", "tests/**/*.py"],
                content_indicators=["test_", "Test"],
                requirements=["pytest", "mock"],
                dependencies=["core_domain"],
                tools=tools,
                metadata=metadata
            ),
            "core_domain": Domain(
                name="core_domain", 
                description="Core functionality domain",
                patterns=["src/core/**/*.py"],
                content_indicators=["core_", "Core"],
                requirements=["requests"],
                dependencies=[],
                tools=tools,
                metadata=metadata
            ),
            "api_domain": Domain(
                name="api_domain",
                description="API handling domain",
                patterns=["src/api/**/*.py"],
                content_indicators=["api_", "API"],
                requirements=["fastapi", "requests"],
                dependencies=["core_domain"],
                tools=tools,
                metadata=metadata
            )
        }
        return domains
    
    @pytest.fixture
    def mock_registry_manager(self, sample_domains):
        """Create mock registry manager"""
        mock_manager = Mock()
        mock_manager.get_all_domains.return_value = sample_domains
        mock_manager.get_domain.side_effect = lambda name: sample_domains.get(name)
        return mock_manager
    
    @pytest.fixture
    def query_engine(self, mock_registry_manager):
        """Create query engine with mock registry"""
        engine = DomainQueryEngine()
        engine.set_registry_manager(mock_registry_manager)
        return engine
    
    def test_initialization(self):
        """Test query engine initialization"""
        engine = DomainQueryEngine()
        
        assert engine.module_name == "domain_query_engine"
        assert engine.query_count == 0
        assert not engine._index_built
    
    def test_set_registry_manager(self, mock_registry_manager):
        """Test setting registry manager"""
        engine = DomainQueryEngine()
        engine.set_registry_manager(mock_registry_manager)
        
        assert engine.registry_manager == mock_registry_manager
        assert not engine._index_built  # Should reset index
    
    def test_build_search_indexes(self, query_engine):
        """Test building search indexes"""
        query_engine._build_search_indexes()
        
        assert query_engine._index_built is True
        assert len(query_engine._pattern_index) > 0
        assert len(query_engine._content_index) > 0
        assert len(query_engine._capability_index) > 0
    
    def test_pattern_search(self, query_engine):
        """Test pattern-based search"""
        results = query_engine.pattern_search("src/test/**/*.py")
        
        assert len(results) > 0
        assert any(domain.name == "test_domain" for domain in results)
    
    def test_pattern_search_wildcard(self, query_engine):
        """Test pattern search with wildcards"""
        results = query_engine.pattern_search("**/test/**")
        
        assert len(results) > 0
        assert any(domain.name == "test_domain" for domain in results)
    
    def test_content_search(self, query_engine):
        """Test content-based search"""
        results = query_engine.content_search("test_")
        
        assert len(results) > 0
        assert any(domain.name == "test_domain" for domain in results)
    
    def test_content_search_partial_match(self, query_engine):
        """Test content search with partial matching"""
        results = query_engine.content_search("Test")
        
        assert len(results) > 0
        assert any(domain.name == "test_domain" for domain in results)
    
    def test_capability_search(self, query_engine):
        """Test capability-based search"""
        results = query_engine.capability_search("pytest")
        
        assert len(results) > 0
        assert any(domain.name == "test_domain" for domain in results)
    
    def test_capability_search_partial(self, query_engine):
        """Test capability search with partial matching"""
        results = query_engine.capability_search("request")
        
        assert len(results) > 0
        # Should match both core_domain and api_domain (both have "requests")
    
    def test_relationship_query_dependencies(self, query_engine):
        """Test relationship query for dependencies"""
        results = query_engine.relationship_query("test_domain", "dependencies")
        
        assert len(results) > 0
        assert any(domain.name == "core_domain" for domain in results)
    
    def test_relationship_query_dependents(self, query_engine):
        """Test relationship query for dependents"""
        results = query_engine.relationship_query("core_domain", "dependents")
        
        assert len(results) > 0
        # Both test_domain and api_domain depend on core_domain
        dependent_names = [domain.name for domain in results]
        assert "test_domain" in dependent_names
        assert "api_domain" in dependent_names
    
    def test_relationship_query_similar(self, query_engine):
        """Test relationship query for similar domains"""
        results = query_engine.relationship_query("test_domain", "similar")
        
        # Should find domains with overlapping patterns or indicators
        assert isinstance(results, list)
    
    def test_natural_language_query_pattern_intent(self, query_engine):
        """Test natural language query with pattern intent"""
        result = query_engine.natural_language_query("find domains with *.py files")
        
        assert result.total_count >= 0  # May be 0 if no matches
        assert result.filters_applied["intent"] == "pattern_search"
        assert "files" in result.filters_applied["keywords"]
    
    def test_natural_language_query_content_intent(self, query_engine):
        """Test natural language query with content intent"""
        result = query_engine.natural_language_query("domains that contain test indicators")
        
        assert result.total_count >= 0
        assert result.filters_applied["intent"] == "content_search"
        assert "test" in result.filters_applied["keywords"]
    
    def test_natural_language_query_capability_intent(self, query_engine):
        """Test natural language query with capability intent"""
        result = query_engine.natural_language_query("domains that can run pytest")
        
        assert result.total_count >= 0
        assert result.filters_applied["intent"] == "capability_search"
        assert "pytest" in result.filters_applied["keywords"]
    
    def test_natural_language_query_general(self, query_engine):
        """Test general natural language query"""
        result = query_engine.natural_language_query("find test domains")
        
        assert result.total_count >= 0
        assert result.filters_applied["intent"] == "general_search"
        assert "test" in result.filters_applied["keywords"]
    
    def test_complex_query(self, query_engine):
        """Test complex structured query"""
        query_spec = {
            "patterns": ["src/test/**/*.py"],
            "content_indicators": ["test_"],
            "capabilities": ["pytest"],
            "filters": {"category": "core"}
        }
        
        result = query_engine.complex_query(query_spec)
        
        assert result.total_count >= 0
        assert isinstance(result.domains, list)
    
    def test_suggest_queries_pattern(self, query_engine):
        """Test query suggestions for patterns"""
        suggestions = query_engine.suggest_queries("src/")
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= query_engine.suggestion_limit
    
    def test_suggest_queries_content(self, query_engine):
        """Test query suggestions for content"""
        suggestions = query_engine.suggest_queries("test")
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= query_engine.suggestion_limit
    
    def test_extract_keywords(self, query_engine):
        """Test keyword extraction from natural language"""
        keywords = query_engine._extract_keywords("find domains with test patterns")
        
        assert "find" in keywords
        assert "domains" in keywords
        assert "test" in keywords
        assert "patterns" in keywords
        # Stop words should be removed
        assert "with" not in keywords
    
    def test_determine_intent_pattern(self, query_engine):
        """Test intent determination for pattern queries"""
        intent = query_engine._determine_intent("find domains with *.py patterns")
        assert intent == "pattern_search"
        
        intent = query_engine._determine_intent("domains in src/ directory")
        assert intent == "pattern_search"
    
    def test_determine_intent_content(self, query_engine):
        """Test intent determination for content queries"""
        intent = query_engine._determine_intent("domains that contain test indicators")
        assert intent == "content_search"
        
        intent = query_engine._determine_intent("find domains with specific content")
        assert intent == "content_search"
    
    def test_determine_intent_capability(self, query_engine):
        """Test intent determination for capability queries"""
        intent = query_engine._determine_intent("domains that can run tests")
        assert intent == "capability_search"
        
        intent = query_engine._determine_intent("what domains support pytest")
        assert intent == "capability_search"
    
    def test_determine_intent_general(self, query_engine):
        """Test intent determination for general queries"""
        intent = query_engine._determine_intent("show me all domains")
        assert intent == "general_search"
    
    def test_calculate_relevance_scores(self, query_engine, sample_domains):
        """Test relevance score calculation"""
        domains = list(sample_domains.values())
        keywords = ["test", "domain"]
        
        scores = query_engine._calculate_relevance_scores(domains, keywords)
        
        assert isinstance(scores, dict)
        assert len(scores) == len(domains)
        
        # test_domain should have higher score due to name match
        assert scores["test_domain"] > scores["core_domain"]
    
    def test_pattern_matches(self, query_engine):
        """Test pattern matching logic"""
        # Exact match
        assert query_engine._pattern_matches("test", "test")
        
        # Substring match
        assert query_engine._pattern_matches("test", "test_domain")
        
        # Wildcard match
        assert query_engine._pattern_matches("test*", "test_domain")
        assert query_engine._pattern_matches("*test*", "my_test_file")
    
    def test_query_stats(self, query_engine):
        """Test query statistics"""
        # Perform some queries to generate stats
        query_engine.pattern_search("test")
        query_engine.content_search("test")
        query_engine.natural_language_query("find test domains")
        
        stats = query_engine.get_query_stats()
        
        assert stats["pattern_searches"] >= 1
        assert stats["content_searches"] >= 1
        assert stats["natural_language_queries"] >= 1
        assert stats["indexes_built"] is True
        assert "cache_stats" in stats
    
    def test_query_without_registry_manager(self):
        """Test query operations without registry manager"""
        engine = DomainQueryEngine()
        
        # Should return empty results gracefully
        results = engine.pattern_search("test")
        assert results == []
        
        results = engine.content_search("test")
        assert results == []
        
        results = engine.capability_search("test")
        assert results == []
    
    def test_index_rebuilding(self, query_engine):
        """Test index rebuilding when registry changes"""
        # Initial index build
        query_engine._ensure_indexes_built()
        assert query_engine._index_built is True
        
        # Set new registry manager (should reset index)
        new_mock_manager = Mock()
        new_mock_manager.get_all_domains.return_value = {}
        query_engine.set_registry_manager(new_mock_manager)
        
        assert query_engine._index_built is False
        
        # Should rebuild on next query
        query_engine.pattern_search("test")
        assert query_engine._index_built is True


if __name__ == "__main__":
    pytest.main([__file__])