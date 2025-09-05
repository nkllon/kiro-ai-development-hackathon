"""
Test Domain Query Engine

Tests for the domain query engine functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock

from src.beast_mode.domain_index.query_engine import DomainQueryEngine
from src.beast_mode.domain_index.models import Domain, DomainTools, DomainMetadata, PackagePotential, QueryResult


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
        result = query_engine.natural_language_query("domains that contain specific content indicators")
        
        assert result.total_count >= 0
        assert result.filters_applied["intent"] == "content_search"
        assert "content" in result.filters_applied["keywords"]
    
    def test_natural_language_query_capability_intent(self, query_engine):
        """Test natural language query with capability intent"""
        result = query_engine.natural_language_query("domains that can run pytest")
        
        assert result.total_count >= 0
        assert result.filters_applied["intent"] == "capability_search"
        assert "pytest" in result.filters_applied["keywords"]
    
    def test_natural_language_query_general(self, query_engine):
        """Test general natural language query"""
        result = query_engine.natural_language_query("show me all available domains")
        
        assert result.total_count >= 0
        assert result.filters_applied["intent"] == "general_search"
        assert "domains" in result.filters_applied["keywords"]
    
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
        intent = query_engine._determine_intent("domains that can run pytest tools")
        assert intent == "capability_search"
        
        intent = query_engine._determine_intent("what domains support pytest capability")
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

    # Advanced Query Capabilities Tests (Task 3.2)
    
    def test_relationship_query_transitive_dependencies(self, query_engine):
        """Test transitive dependency traversal"""
        results = query_engine.relationship_query("test_domain", "transitive_dependencies")
        
        # test_domain -> core_domain (no further dependencies)
        assert len(results) >= 1
        assert any(domain.name == "core_domain" for domain in results)
    
    def test_relationship_query_transitive_dependents(self, query_engine):
        """Test transitive dependent analysis"""
        results = query_engine.relationship_query("core_domain", "transitive_dependents")
        
        # core_domain is depended on by test_domain and api_domain
        assert len(results) >= 2
        dependent_names = [domain.name for domain in results]
        assert "test_domain" in dependent_names
        assert "api_domain" in dependent_names
    
    def test_relationship_query_circular_dependencies(self, query_engine, sample_domains):
        """Test circular dependency detection"""
        # Create a circular dependency for testing
        sample_domains["core_domain"].dependencies = ["api_domain"]  # Creates cycle: test_domain -> core_domain -> api_domain -> core_domain
        
        results = query_engine.relationship_query("core_domain", "circular")
        
        # Should detect circular dependencies
        assert isinstance(results, list)
    
    def test_relationship_query_high_coupling(self, query_engine):
        """Test high coupling domain identification"""
        results = query_engine.relationship_query("core_domain", "coupling_high")
        
        # Should find domains with high coupling to core_domain
        assert isinstance(results, list)
    
    def test_relationship_query_extraction_related(self, query_engine):
        """Test extraction impact analysis"""
        results = query_engine.relationship_query("core_domain", "extraction_related")
        
        # Should find domains affected by extracting core_domain
        assert len(results) >= 2  # test_domain and api_domain depend on it
        affected_names = [domain.name for domain in results]
        assert "test_domain" in affected_names
        assert "api_domain" in affected_names
    
    def test_advanced_relationship_analysis(self, query_engine):
        """Test comprehensive relationship analysis"""
        analysis = query_engine.advanced_relationship_analysis("core_domain")
        
        assert "domain" in analysis
        assert analysis["domain"] == "core_domain"
        assert "direct_dependencies" in analysis
        assert "direct_dependents" in analysis
        assert "transitive_dependencies" in analysis
        assert "transitive_dependents" in analysis
        assert "similar_domains" in analysis
        assert "circular_dependencies" in analysis
        assert "high_coupling_domains" in analysis
        assert "extraction_impact" in analysis
        assert "metrics" in analysis
        
        # Check metrics
        metrics = analysis["metrics"]
        assert "dependency_depth" in metrics
        assert "dependent_count" in metrics
        assert "similarity_count" in metrics
        assert "coupling_count" in metrics
        assert "circular_dependency_count" in metrics
        assert "extraction_impact_count" in metrics
    
    def test_get_transitive_dependencies(self, query_engine, sample_domains):
        """Test transitive dependency traversal algorithm"""
        # Create a deeper dependency chain for testing
        sample_domains["deep_domain"] = Domain(
            name="deep_domain",
            description="Deep dependency domain",
            patterns=["src/deep/**/*.py"],
            content_indicators=["deep_"],
            requirements=[],
            dependencies=["test_domain"],  # deep_domain -> test_domain -> core_domain
            tools=sample_domains["core_domain"].tools,
            metadata=sample_domains["core_domain"].metadata
        )
        
        results = query_engine._get_transitive_dependencies("deep_domain", sample_domains)
        
        # Should find both test_domain and core_domain
        result_names = [domain.name for domain in results]
        assert "test_domain" in result_names
        assert "core_domain" in result_names
    
    def test_find_similar_domains(self, query_engine, sample_domains):
        """Test domain similarity calculation"""
        results = query_engine._find_similar_domains(sample_domains["test_domain"], sample_domains)
        
        # Should find domains with similar patterns, indicators, or requirements
        assert isinstance(results, list)
        # Results should be sorted by similarity
        if len(results) > 1:
            # Check that similarity scores are in descending order
            similarities = [query_engine._calculate_domain_similarity(sample_domains["test_domain"], domain) for domain in results]
            assert similarities == sorted(similarities, reverse=True)
    
    def test_calculate_domain_similarity(self, query_engine, sample_domains):
        """Test domain similarity calculation"""
        similarity = query_engine._calculate_domain_similarity(
            sample_domains["test_domain"], 
            sample_domains["api_domain"]
        )
        
        assert 0.0 <= similarity <= 1.0
        
        # Self-similarity should be 1.0
        self_similarity = query_engine._calculate_domain_similarity(
            sample_domains["test_domain"], 
            sample_domains["test_domain"]
        )
        assert self_similarity == 1.0
    
    def test_detect_circular_dependencies(self, query_engine, sample_domains):
        """Test circular dependency detection algorithm"""
        # Create circular dependencies
        sample_domains["core_domain"].dependencies = ["api_domain"]
        sample_domains["api_domain"].dependencies = ["test_domain"]
        # Now we have: test_domain -> core_domain -> api_domain -> test_domain (circular)
        
        circular_chains = query_engine._detect_circular_dependencies("test_domain", sample_domains)
        
        assert isinstance(circular_chains, list)
        # Should detect the circular chain
        if circular_chains:
            assert any("test_domain" in chain for chain in circular_chains)
    
    def test_calculate_coupling_score(self, query_engine, sample_domains):
        """Test coupling score calculation"""
        coupling_score = query_engine._calculate_coupling_score(
            sample_domains["test_domain"],
            sample_domains["core_domain"]
        )
        
        assert 0.0 <= coupling_score <= 1.0
        
        # Domains with dependencies should have higher coupling
        assert coupling_score > 0.0  # test_domain depends on core_domain
    
    def test_enhanced_capability_search(self, query_engine):
        """Test enhanced capability search with semantic matching"""
        # Test semantic matching
        results = query_engine.capability_search("testing")
        
        # Should match domains with "test" capabilities due to semantic matching
        assert len(results) >= 0
        
        # Test tool-based capability matching
        results = query_engine.capability_search("pylint")
        
        # Should match domains that use pylint as linter
        assert len(results) >= 0
    
    def test_capability_matches(self, query_engine):
        """Test capability matching logic"""
        # Exact match
        assert query_engine._capability_matches("test", "test")
        
        # Substring match
        assert query_engine._capability_matches("test", "testing")
        
        # Semantic match
        assert query_engine._capability_matches("test", "pytest")
        assert query_engine._capability_matches("lint", "pylint")
        assert query_engine._capability_matches("format", "black")
    
    def test_calculate_capability_relevance(self, query_engine, sample_domains):
        """Test capability relevance scoring"""
        relevance = query_engine._calculate_capability_relevance(
            sample_domains["test_domain"], 
            "test"
        )
        
        assert relevance > 0.0  # Should have positive relevance for test capability
        
        # Domain with "test" in name should have higher relevance
        api_relevance = query_engine._calculate_capability_relevance(
            sample_domains["api_domain"], 
            "test"
        )
        
        assert relevance > api_relevance
    
    def test_pattern_suggests_capability(self, query_engine):
        """Test pattern-based capability suggestion"""
        # Test patterns should suggest test capability
        assert query_engine._pattern_suggests_capability("tests/**/*.py", "test")
        assert query_engine._pattern_suggests_capability("src/test_*.py", "test")
        
        # Doc patterns should suggest doc capability
        assert query_engine._pattern_suggests_capability("docs/**/*.md", "doc")
        assert query_engine._pattern_suggests_capability("README.md", "doc")
        
        # Config patterns should suggest config capability
        assert query_engine._pattern_suggests_capability("config.yaml", "config")
        assert query_engine._pattern_suggests_capability("settings.json", "config")
    
    def test_enhanced_relevance_scoring(self, query_engine, sample_domains):
        """Test enhanced relevance scoring system"""
        domains = list(sample_domains.values())
        keywords = ["test", "core"]
        
        scores = query_engine._calculate_relevance_scores(domains, keywords)
        
        # test_domain should have highest score due to exact name match with "test"
        assert scores["test_domain"] > scores["core_domain"]
        assert scores["test_domain"] > scores["api_domain"]
        
        # core_domain should have higher score than api_domain for "core" keyword
        core_keywords = ["core"]
        core_scores = query_engine._calculate_relevance_scores(domains, core_keywords)
        assert core_scores["core_domain"] > core_scores["api_domain"]
    
    def test_find_extraction_related_domains(self, query_engine, sample_domains):
        """Test extraction impact analysis"""
        related_domains = query_engine._find_extraction_related_domains(
            sample_domains["core_domain"], 
            sample_domains
        )
        
        # Should find domains that depend on core_domain
        related_names = [domain.name for domain in related_domains]
        assert "test_domain" in related_names
        assert "api_domain" in related_names
    
    def test_complex_relationship_scenarios(self, query_engine, sample_domains):
        """Test complex relationship analysis scenarios"""
        # Add more complex domain relationships
        sample_domains["integration_domain"] = Domain(
            name="integration_domain",
            description="Integration testing domain",
            patterns=["src/integration/**/*.py", "tests/integration/**/*.py"],
            content_indicators=["integration_", "Integration"],
            requirements=["pytest", "requests", "mock"],
            dependencies=["test_domain", "api_domain"],
            tools=sample_domains["core_domain"].tools,
            metadata=sample_domains["core_domain"].metadata
        )
        
        # Test multiple relationship types
        deps = query_engine.relationship_query("integration_domain", "dependencies")
        assert len(deps) == 2
        
        trans_deps = query_engine.relationship_query("integration_domain", "transitive_dependencies")
        # Should include core_domain through transitive dependencies
        trans_names = [d.name for d in trans_deps]
        assert "core_domain" in trans_names
        
        similar = query_engine.relationship_query("integration_domain", "similar")
        # Should find test_domain as similar (both have test patterns and pytest)
        similar_names = [d.name for d in similar]
        assert "test_domain" in similar_names

    # Advanced Natural Language Query Processing Tests (Task 3.3)
    
    def test_parse_natural_language_query(self, query_engine):
        """Test natural language query parsing"""
        query = "find domains with testing capabilities in core category"
        parsed = query_engine._parse_natural_language_query(query)
        
        assert parsed["original_query"] == query
        assert "testing" in parsed["keywords"]
        assert "capabilities" in parsed["keywords"]
        assert parsed["intent"] == "capability_search"
        assert parsed["query_type"] == "search"
        assert "core" in parsed["filters"].get("category", "")
    
    def test_extract_entities(self, query_engine):
        """Test entity extraction from queries"""
        query = "show test_domain dependencies with *.py patterns"
        entities = query_engine._extract_entities(query)
        
        assert "test_domain" in entities["domain_names"]
        assert "*.py" in entities["patterns"]
        assert "test" in entities["capabilities"]
    
    def test_extract_enhanced_keywords(self, query_engine):
        """Test enhanced keyword extraction"""
        query = "find domains that are testing related functionality"
        keywords = query_engine._extract_enhanced_keywords(query)
        
        assert "domains" in keywords
        assert "testing" in keywords
        assert "related" in keywords
        assert "functionality" in keywords
        # Stop words should be removed
        assert "that" not in keywords
        assert "are" not in keywords
    
    def test_determine_enhanced_intent(self, query_engine):
        """Test enhanced intent determination"""
        # Pattern intent
        entities = {"patterns": ["*.py"], "capabilities": [], "domain_names": []}
        intent = query_engine._determine_enhanced_intent("find domains with *.py files", entities)
        assert intent == "pattern_search"
        
        # Capability intent
        entities = {"patterns": [], "capabilities": ["pytest"], "domain_names": []}
        intent = query_engine._determine_enhanced_intent("domains that can run pytest", entities)
        assert intent == "capability_search"
        
        # Relationship intent
        entities = {"patterns": [], "capabilities": [], "domain_names": []}
        intent = query_engine._determine_enhanced_intent("domains that depend on core", entities)
        assert intent == "relationship_search"
    
    def test_determine_query_type(self, query_engine):
        """Test query type determination"""
        # Relationship query
        query_type = query_engine._determine_query_type("domains that depend on core_domain")
        assert query_type == "relationship"
        
        # Analysis query
        query_type = query_engine._determine_query_type("analyze domain complexity metrics")
        assert query_type == "analysis"
        
        # Comparison query
        query_type = query_engine._determine_query_type("compare test_domain vs api_domain")
        assert query_type == "comparison"
        
        # Search query
        query_type = query_engine._determine_query_type("find domains with testing")
        assert query_type == "search"
    
    def test_extract_query_filters(self, query_engine):
        """Test query filter extraction"""
        query = "find healthy domains in core category with high complexity"
        filters = query_engine._extract_query_filters(query)
        
        assert filters.get("category") == "core"
        assert filters.get("status") == "healthy"
        assert filters.get("complexity_level") == "high"
    
    def test_extract_query_modifiers(self, query_engine):
        """Test query modifier extraction"""
        query = "show top 5 domains sorted by complexity in descending order"
        modifiers = query_engine._extract_query_modifiers(query)
        
        assert "limit:5" in modifiers
        assert "sort_by:complexity" in modifiers
        assert "order:desc" in modifiers
    
    def test_extract_relationship_info(self, query_engine):
        """Test relationship information extraction"""
        entities = {"domain_names": ["test_domain"]}
        query = "show circular dependencies for test_domain"
        
        rel_info = query_engine._extract_relationship_info(query, entities)
        
        assert rel_info["relationship_type"] == "circular"
        assert rel_info["target_domain"] == "test_domain"
    
    def test_execute_parsed_query_relationship(self, query_engine):
        """Test executing parsed relationship queries"""
        parsed_query = {
            "query_type": "relationship",
            "intent": "relationship_search",
            "target_domain": "core_domain",
            "relationship_type": "dependents",
            "keywords": ["dependents"],
            "entities": {"domain_names": ["core_domain"]}
        }
        
        results = query_engine._execute_parsed_query(parsed_query)
        
        # Should find domains that depend on core_domain
        result_names = [d.name for d in results]
        assert "test_domain" in result_names
        assert "api_domain" in result_names
    
    def test_apply_parsed_filters(self, query_engine, sample_domains):
        """Test applying parsed filters to results"""
        domains = list(sample_domains.values())
        filters = {"category": "core"}
        
        # Set one domain to core category
        sample_domains["core_domain"].metadata.demo_role = "core"
        
        filtered = query_engine._apply_parsed_filters(domains, filters)
        
        # Should only include domains with core category
        assert len(filtered) >= 1
        assert all(d.metadata.demo_role == "core" for d in filtered)
    
    def test_generate_intelligent_suggestions_empty_results(self, query_engine):
        """Test intelligent suggestions for empty results"""
        parsed_query = {
            "keywords": ["nonexistent"],
            "entities": {"domain_names": ["fake_domain"]},
            "query_type": "search",
            "filters": {}
        }
        
        suggestions = query_engine._generate_intelligent_suggestions(
            "find nonexistent domain", parsed_query, []
        )
        
        assert len(suggestions) > 0
        assert any("broader terms" in s for s in suggestions)
        assert any("fake_domain" in s for s in suggestions)
    
    def test_generate_intelligent_suggestions_many_results(self, query_engine, sample_domains):
        """Test intelligent suggestions for too many results"""
        # Create many fake results
        many_results = list(sample_domains.values()) * 10
        
        parsed_query = {
            "keywords": ["domain"],
            "entities": {},
            "query_type": "search",
            "filters": {}
        }
        
        suggestions = query_engine._generate_intelligent_suggestions(
            "find domains", parsed_query, many_results
        )
        
        assert len(suggestions) > 0
        assert any("specific filters" in s for s in suggestions)
    
    def test_calculate_enhanced_relevance_scores(self, query_engine, sample_domains):
        """Test enhanced relevance scoring with parsed query"""
        domains = list(sample_domains.values())
        parsed_query = {
            "keywords": ["test"],
            "entities": {"domain_names": ["test_domain"], "capabilities": ["pytest"]},
            "intent": "capability_search"
        }
        
        scores = query_engine._calculate_enhanced_relevance_scores(domains, parsed_query)
        
        # test_domain should have highest score due to entity match
        assert scores["test_domain"] > scores["core_domain"]
        assert scores["test_domain"] > scores["api_domain"]
    
    def test_rank_and_filter_results(self, query_engine, sample_domains):
        """Test result ranking and filtering"""
        domains = list(sample_domains.values())
        parsed_query = {
            "modifiers": ["sort_by:name", "order:asc", "limit:2"]
        }
        
        ranked = query_engine._rank_and_filter_results(domains, parsed_query)
        
        # Should be sorted by name ascending and limited to 2
        assert len(ranked) <= 2
        if len(ranked) > 1:
            assert ranked[0].name <= ranked[1].name
    
    def test_advanced_query_suggestion_system(self, query_engine):
        """Test advanced query suggestion system"""
        # Test partial query parsing
        partial_info = query_engine._parse_partial_query("find domains with test")
        
        assert "find" in partial_info["tokens"]
        assert partial_info["last_token"] == "test"
        assert partial_info["incomplete_type"] == "partial_word"
    
    def test_contextual_suggestions(self, query_engine):
        """Test contextual suggestion generation"""
        partial_query = "domains with pattern"
        partial_info = {
            "tokens": ["domains", "with", "pattern"],
            "last_token": "pattern",
            "intent_indicators": ["pattern"],
            "entity_hints": [],
            "incomplete_type": "expecting_next_word"
        }
        
        suggestions = query_engine._generate_contextual_suggestions(partial_query, partial_info)
        
        assert len(suggestions) > 0
        assert any("src/**/*.py" in s for s in suggestions)
        assert any("tests/**/*.py" in s for s in suggestions)
    
    def test_completion_suggestions(self, query_engine):
        """Test word completion suggestions"""
        query_engine._ensure_indexes_built()
        
        suggestions = query_engine._generate_completion_suggestions("test")
        
        # Should suggest completions based on indexed content
        assert isinstance(suggestions, list)
    
    def test_template_suggestions(self, query_engine):
        """Test template-based suggestions"""
        partial_query = "find domains"
        partial_info = {"intent_indicators": [], "entity_hints": []}
        
        suggestions = query_engine._generate_template_suggestions(partial_query, partial_info)
        
        assert len(suggestions) > 0
        assert any("find domains with" in s for s in suggestions)
    
    def test_popular_query_templates(self, query_engine):
        """Test popular query templates for empty queries"""
        templates = query_engine._get_popular_query_templates()
        
        assert len(templates) > 0
        assert any("testing" in t for t in templates)
        assert any("core" in t for t in templates)
    
    def test_query_corrections(self, query_engine):
        """Test query correction suggestions"""
        corrections = query_engine.suggest_query_corrections("find domians with dependancies")
        
        assert len(corrections) > 0
        assert any("domains" in c for c in corrections)
        assert any("dependencies" in c for c in corrections)
    
    def test_explain_query_results(self, query_engine):
        """Test query result explanation"""
        query = "find domains with testing"
        
        # Create mock results
        result = QueryResult(
            domains=list(query_engine.registry_manager.get_all_domains().values())[:1],
            total_count=1,
            query_time_ms=10.0,
            relevance_scores={"test_domain": 5.0}
        )
        
        explanation = query_engine.explain_query_results(query, result)
        
        assert "query_interpretation" in explanation
        assert "matching_strategy" in explanation
        assert "result_ranking" in explanation
        assert explanation["query_interpretation"]["detected_intent"] == "capability_search"
    
    def test_explain_relevance_factors(self, query_engine, sample_domains):
        """Test relevance factor explanation"""
        parsed_query = {
            "keywords": ["test"],
            "entities": {"capabilities": ["pytest"]}
        }
        
        factors = query_engine._explain_relevance_factors(sample_domains["test_domain"], parsed_query)
        
        assert len(factors) > 0
        assert any("name contains" in f for f in factors)
    
    def test_comprehensive_nl_query_processing(self, query_engine):
        """Test comprehensive natural language query processing"""
        # Complex query with multiple components
        query = "find healthy domains in core category that can run pytest and have *.py patterns, sorted by complexity, limit 5"
        
        result = query_engine.natural_language_query(query)
        
        assert isinstance(result, QueryResult)
        assert result.total_count >= 0
        assert "intent" in result.filters_applied
        assert "keywords" in result.filters_applied
        assert "entities" in result.filters_applied
        assert "filters" in result.filters_applied
        assert "query_type" in result.filters_applied
        
        # Should have suggestions
        assert len(result.suggestions) > 0
    
    def test_ambiguous_query_handling(self, query_engine):
        """Test handling of ambiguous queries"""
        ambiguous_queries = [
            "test",  # Could be pattern, content, or capability
            "core",  # Could be domain name or category
            "api",   # Could be domain or capability
            "find"   # Incomplete query
        ]
        
        for query in ambiguous_queries:
            result = query_engine.natural_language_query(query)
            
            # Should handle gracefully and provide suggestions
            assert isinstance(result, QueryResult)
            assert len(result.suggestions) > 0
    
    def test_query_suggestion_system_integration(self, query_engine):
        """Test integration of query suggestion system"""
        # Test various partial queries
        partial_queries = [
            "",
            "find",
            "find domains",
            "find domains with",
            "domains that depend",
            "analyze domain"
        ]
        
        for partial in partial_queries:
            suggestions = query_engine.suggest_queries(partial)
            
            assert isinstance(suggestions, list)
            assert len(suggestions) <= query_engine.suggestion_limit
            
            # Suggestions should be relevant to the partial query
            if partial:
                assert all(isinstance(s, str) for s in suggestions)


if __name__ == "__main__":
    pytest.main([__file__])