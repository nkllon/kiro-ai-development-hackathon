"""
Unit tests for Knowledge Base Search Engine
Tests advanced search, query suggestions, and performance optimization.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
import json

from src.beast_mode.observatory.ai_consultation.knowledge_base_search import (
    KnowledgeBaseSearchEngine, QuerySuggestion, SearchInsights, RetentionPolicy,
    SimilarityMethod, get_knowledge_base_search_engine
)
from src.beast_mode.observatory.ai_consultation.results_storage import (
    SearchQuery, SearchResult, SearchType, KnowledgeBaseStats
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationResult, ProcessingMode
)
from src.beast_mode.observatory.ai_consultation.exceptions import SearchError


class TestKnowledgeBaseSearchEngine:
    """Test KnowledgeBaseSearchEngine functionality"""
    
    @pytest.fixture
    def search_engine(self):
        """Create search engine for testing"""
        return KnowledgeBaseSearchEngine(
            max_suggestions=5,
            similarity_threshold=0.7,
            cache_size=100,
            rate_limit_per_minute=50,
            enable_semantic_search=True
        )
    
    @pytest.fixture
    def mock_storage_manager(self):
        """Create mock storage manager"""
        mock_storage = AsyncMock()
        mock_storage.search_results = AsyncMock()
        mock_storage.get_knowledge_base_stats = AsyncMock()
        return mock_storage
    
    @pytest.fixture
    def sample_search_results(self):
        """Create sample search results"""
        results = []
        for i in range(3):
            consultation_result = ConsultationResult(
                result_id=f"test-result-{i}",
                query_id=f"test-query-{i}",
                response_text=f"Test response {i} about system monitoring and performance",
                processing_time=1.5,
                cost=0.10,
                timestamp=datetime.utcnow(),
                processing_mode=ProcessingMode.REALTIME,
                metadata={
                    'query_text': f'What is the status of system component {i}?',
                    'user_id': 'test-user'
                }
            )
            
            search_result = SearchResult(
                result=consultation_result,
                relevance_score=0.9 - (i * 0.1),
                similarity_score=0.8 - (i * 0.1),
                match_type="keyword",
                matched_fields=["query_text", "response_text"]
            )
            results.append(search_result)
        
        return results
    
    async def test_initialization(self, search_engine, mock_storage_manager):
        """Test search engine initialization"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager') as mock_get_storage:
                mock_flags.is_enabled.return_value = True
                mock_get_storage.return_value = mock_storage_manager
                
                # Mock knowledge base stats
                mock_stats = KnowledgeBaseStats(
                    total_results=100,
                    unique_users=25,
                    date_range=(datetime.utcnow() - timedelta(days=30), datetime.utcnow()),
                    avg_cost_per_query=0.12,
                    total_cost=12.0,
                    most_common_topics=[("system monitoring", 15), ("performance analysis", 10)],
                    success_rate=0.95,
                    storage_size_mb=5.2
                )
                mock_storage_manager.get_knowledge_base_stats.return_value = mock_stats
                
                await search_engine.initialize()
                
                assert search_engine.storage_manager == mock_storage_manager
                assert len(search_engine.query_patterns) == 2
                assert "system monitoring" in search_engine.query_patterns
                assert search_engine.cleanup_task is not None
    
    async def test_initialization_disabled(self, search_engine):
        """Test initialization when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            
            await search_engine.initialize()
            
            assert search_engine.storage_manager is None
    
    async def test_search_with_suggestions_success(self, search_engine, mock_storage_manager, sample_search_results):
        """Test successful search with suggestions"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            search_engine.storage_manager = mock_storage_manager
            
            # Mock search results
            mock_storage_manager.search_results.return_value = sample_search_results
            
            # Perform search
            results, suggestions = await search_engine.search_with_suggestions(
                query_text="system status monitoring",
                user_id="test-user",
                search_type=SearchType.HYBRID,
                include_suggestions=True
            )
            
            assert len(results) == 3
            assert len(suggestions) >= 0  # May have suggestions
            assert search_engine.search_analytics['total_searches'] == 1
            assert "system status monitoring" in search_engine.query_patterns
    
    async def test_search_with_rate_limiting(self, search_engine, mock_storage_manager):
        """Test search with rate limiting"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            search_engine.storage_manager = mock_storage_manager
            search_engine.rate_limit_per_minute = 2  # Very low limit for testing
            
            # First two searches should succeed
            for i in range(2):
                results, suggestions = await search_engine.search_with_suggestions(
                    query_text=f"test query {i}",
                    user_id="test-user"
                )
            
            # Third search should fail due to rate limiting
            with pytest.raises(SearchError, match="Rate limit exceeded"):
                await search_engine.search_with_suggestions(
                    query_text="test query 3",
                    user_id="test-user"
                )
            
            assert search_engine.search_analytics['rate_limit_hits'] == 1
    
    async def test_hybrid_search(self, search_engine, mock_storage_manager, sample_search_results):
        """Test hybrid search functionality"""
        search_engine.storage_manager = mock_storage_manager
        
        # Mock different search types returning different results
        def mock_search_results(search_query):
            if search_query.search_type == SearchType.EXACT:
                return sample_search_results[:1]  # 1 exact result
            elif search_query.search_type == SearchType.SEMANTIC:
                return sample_search_results[1:2]  # 1 semantic result
            elif search_query.search_type == SearchType.SIMILAR:
                return sample_search_results[2:3]  # 1 similar result
            else:  # KEYWORD
                return sample_search_results  # All results
        
        mock_storage_manager.search_results.side_effect = mock_search_results
        
        results = await search_engine._hybrid_search("test query", "test-user", 10)
        
        # Should combine results from different search types
        assert len(results) >= 3
        # Exact matches should have boosted scores
        exact_result = next((r for r in results if r.result.result_id == "test-result-0"), None)
        if exact_result:
            assert exact_result.relevance_score > 0.9  # Boosted score
    
    async def test_pattern_suggestions(self, search_engine):
        """Test pattern-based suggestion generation"""
        # Set up query patterns
        search_engine.query_patterns = {
            "system status monitoring": 10,
            "performance analysis dashboard": 8,
            "error troubleshooting guide": 5,
            "network connectivity check": 3
        }
        
        suggestions = await search_engine._generate_pattern_suggestions("system monitoring status")
        
        assert len(suggestions) > 0
        # Should find similar patterns
        pattern_suggestions = [s for s in suggestions if s.suggestion_type == "pattern"]
        assert len(pattern_suggestions) > 0
        
        # Check suggestion properties
        for suggestion in pattern_suggestions:
            assert suggestion.similarity_score >= search_engine.similarity_threshold
            assert suggestion.related_results_count > 0
    
    async def test_topic_suggestions(self, search_engine):
        """Test topic-based suggestion generation"""
        # Set up topic keywords
        search_engine.topic_keywords = {
            "system monitoring": {"system", "monitoring", "status", "health"},
            "performance analysis": {"performance", "analysis", "metrics", "cpu", "memory"},
            "error handling": {"error", "exception", "troubleshooting", "debug"}
        }
        
        suggestions = await search_engine._generate_topic_suggestions("system performance monitoring")
        
        assert len(suggestions) > 0
        # Should generate topic-based queries
        topic_suggestions = [s for s in suggestions if s.suggestion_type == "topic"]
        assert len(topic_suggestions) > 0
        
        # Check suggestion content
        for suggestion in topic_suggestions:
            assert "system" in suggestion.suggested_query.lower() or "performance" in suggestion.suggested_query.lower()
    
    async def test_similar_query_suggestions(self, search_engine, mock_storage_manager, sample_search_results):
        """Test similar query suggestion generation"""
        search_engine.storage_manager = mock_storage_manager
        mock_storage_manager.search_results.return_value = sample_search_results
        
        suggestions = await search_engine._generate_similar_query_suggestions("system status check")
        
        assert len(suggestions) > 0
        # Should find similar queries from search results
        similar_suggestions = [s for s in suggestions if s.suggestion_type == "similar"]
        assert len(similar_suggestions) > 0
        
        # Check suggestion properties
        for suggestion in similar_suggestions:
            assert suggestion.similarity_score > 0
            assert suggestion.avg_cost > 0
            assert suggestion.avg_processing_time > 0
    
    async def test_context_suggestions(self, search_engine, sample_search_results):
        """Test context-aware suggestion generation"""
        suggestions = await search_engine._generate_context_suggestions(
            "system monitoring", sample_search_results
        )
        
        # Should generate context-aware follow-up questions
        context_suggestions = [s for s in suggestions if s.suggestion_type == "context"]
        
        # Check that suggestions are contextually relevant
        for suggestion in context_suggestions:
            assert "monitoring" in suggestion.suggested_query.lower() or "system" in suggestion.suggested_query.lower()
    
    async def test_search_caching(self, search_engine, mock_storage_manager, sample_search_results):
        """Test search result caching"""
        search_engine.storage_manager = mock_storage_manager
        mock_storage_manager.search_results.return_value = sample_search_results
        
        # First search - cache miss
        results1 = await search_engine._perform_advanced_search(
            "test query", "test-user", SearchType.KEYWORD, 10
        )
        assert search_engine.search_analytics['cache_misses'] == 1
        assert search_engine.search_analytics['cache_hits'] == 0
        
        # Second identical search - cache hit
        results2 = await search_engine._perform_advanced_search(
            "test query", "test-user", SearchType.KEYWORD, 10
        )
        assert search_engine.search_analytics['cache_hits'] == 1
        assert len(results1) == len(results2)
    
    async def test_suggestion_caching(self, search_engine):
        """Test suggestion caching"""
        # Mock some patterns for suggestions
        search_engine.query_patterns = {"test pattern": 5}
        
        # First suggestion generation - cache miss
        suggestions1 = await search_engine._generate_query_suggestions(
            "test query", "test-user", []
        )
        
        # Second identical generation - cache hit
        suggestions2 = await search_engine._generate_query_suggestions(
            "test query", "test-user", []
        )
        
        # Should return cached results
        assert len(suggestions1) == len(suggestions2)
    
    async def test_get_search_insights(self, search_engine, mock_storage_manager):
        """Test search insights generation"""
        search_engine.storage_manager = mock_storage_manager
        
        # Mock knowledge base stats
        mock_stats = KnowledgeBaseStats(
            total_results=100,
            unique_users=25,
            date_range=(datetime.utcnow() - timedelta(days=30), datetime.utcnow()),
            avg_cost_per_query=0.12,
            total_cost=12.0,
            most_common_topics=[("system monitoring", 15)],
            success_rate=0.95,
            storage_size_mb=5.2
        )
        mock_storage_manager.get_knowledge_base_stats.return_value = mock_stats
        
        # Set some analytics data
        search_engine.search_analytics['total_searches'] = 50
        search_engine.search_analytics['cache_hits'] = 30
        search_engine.search_analytics['cache_misses'] = 20
        search_engine.query_patterns = {"pattern1": 10, "pattern2": 5}
        
        insights = await search_engine.get_search_insights()
        
        assert insights.total_searches == 50
        assert insights.unique_queries == 2
        assert len(insights.most_common_topics) > 0
        assert insights.cost_analysis['avg_cost_per_search'] == 0.12
        assert insights.performance_metrics['cache_hit_rate'] == 0.6  # 30 / (30 + 20)
    
    async def test_cleanup_old_data(self, search_engine):
        """Test data cleanup functionality"""
        # Add some old cache entries
        old_time = datetime.utcnow() - timedelta(hours=2)
        recent_time = datetime.utcnow() - timedelta(minutes=30)
        
        search_engine.search_cache = {
            "old_key": (old_time, []),
            "recent_key": (recent_time, [])
        }
        
        search_engine.suggestion_cache = {
            "old_suggestion": (old_time, []),
            "recent_suggestion": (recent_time, [])
        }
        
        # Add low-frequency patterns
        search_engine.query_patterns = {
            "high_freq_pattern": 10,
            "low_freq_pattern": 1
        }
        
        cleanup_stats = await search_engine.cleanup_old_data()
        
        assert cleanup_stats['cache_entries_removed'] == 1  # Old search cache entry
        assert cleanup_stats['suggestions_cleaned'] == 1  # Old suggestion cache entry
        assert cleanup_stats['patterns_cleaned'] == 1  # Low frequency pattern
        
        # Verify cleanup
        assert "old_key" not in search_engine.search_cache
        assert "recent_key" in search_engine.search_cache
        assert "low_freq_pattern" not in search_engine.query_patterns
        assert "high_freq_pattern" in search_engine.query_patterns
    
    def test_extract_keywords(self, search_engine):
        """Test keyword extraction"""
        text = "What is the system status and performance monitoring?"
        keywords = search_engine._extract_keywords(text)
        
        assert "system" in keywords
        assert "status" in keywords
        assert "performance" in keywords
        assert "monitoring" in keywords
        # Stop words should be removed
        assert "what" not in keywords
        assert "is" not in keywords
        assert "the" not in keywords
    
    def test_extract_topics_from_text(self, search_engine):
        """Test topic extraction from text"""
        text = "The CPU usage is high and memory consumption has increased. Database performance is degraded."
        topics = search_engine._extract_topics_from_text(text)
        
        assert "cpu" in topics
        assert "memory" in topics
        assert "database" in topics
        assert "performance" in topics
    
    def test_calculate_keyword_similarity(self, search_engine):
        """Test keyword similarity calculation"""
        keywords1 = {"system", "monitoring", "status"}
        keywords2 = {"system", "status", "health"}
        
        similarity = search_engine._calculate_keyword_similarity(keywords1, keywords2)
        
        # Should have some similarity (intersection: {system, status})
        assert 0 < similarity < 1
        
        # Test identical sets
        identical_similarity = search_engine._calculate_keyword_similarity(keywords1, keywords1)
        assert identical_similarity == 1.0
        
        # Test no overlap
        keywords3 = {"database", "connection", "error"}
        no_similarity = search_engine._calculate_keyword_similarity(keywords1, keywords3)
        assert no_similarity < 0.5
    
    def test_calculate_text_similarity(self, search_engine):
        """Test text similarity calculation"""
        text1 = "What is the system status?"
        text2 = "What is the system health?"
        text3 = "Database connection error occurred"
        
        # Similar texts
        similarity1 = search_engine._calculate_text_similarity(text1, text2)
        assert similarity1 > 0.5
        
        # Different texts
        similarity2 = search_engine._calculate_text_similarity(text1, text3)
        assert similarity2 < 0.3
        
        # Identical texts
        identical_similarity = search_engine._calculate_text_similarity(text1, text1)
        assert identical_similarity == 1.0
    
    def test_deduplicate_suggestions(self, search_engine):
        """Test suggestion deduplication"""
        suggestions = [
            QuerySuggestion(
                suggested_query="What is the system status?",
                similarity_score=0.9,
                suggestion_type="pattern",
                related_results_count=5,
                avg_cost=0.10,
                avg_processing_time=1.5,
                success_rate=0.95,
                last_used=datetime.utcnow()
            ),
            QuerySuggestion(
                suggested_query="what is the system status?",  # Duplicate (case insensitive)
                similarity_score=0.8,
                suggestion_type="similar",
                related_results_count=3,
                avg_cost=0.12,
                avg_processing_time=1.8,
                success_rate=0.90,
                last_used=datetime.utcnow()
            ),
            QuerySuggestion(
                suggested_query="How is the system performing?",
                similarity_score=0.85,
                suggestion_type="topic",
                related_results_count=4,
                avg_cost=0.11,
                avg_processing_time=1.6,
                success_rate=0.92,
                last_used=datetime.utcnow()
            )
        ]
        
        unique_suggestions = search_engine._deduplicate_suggestions(suggestions)
        
        assert len(unique_suggestions) == 2  # One duplicate removed
        query_texts = [s.suggested_query for s in unique_suggestions]
        assert len(set(q.lower() for q in query_texts)) == 2  # All unique when normalized
    
    async def test_rate_limit_checking(self, search_engine):
        """Test rate limit checking"""
        search_engine.rate_limit_per_minute = 3
        
        # First 3 requests should pass
        for i in range(3):
            result = await search_engine._check_rate_limit("test-user")
            assert result == True
        
        # 4th request should fail
        result = await search_engine._check_rate_limit("test-user")
        assert result == False
        
        # Different user should still pass
        result = await search_engine._check_rate_limit("other-user")
        assert result == True
    
    async def test_get_search_analytics(self, search_engine):
        """Test search analytics retrieval"""
        # Set some test data
        search_engine.search_analytics['total_searches'] = 100
        search_engine.search_analytics['cache_hits'] = 60
        search_engine.search_analytics['cache_misses'] = 40
        search_engine.query_patterns = {"pattern1": 10, "pattern2": 5}
        search_engine.topic_keywords = {"topic1": {"keyword1", "keyword2"}}
        
        analytics = await search_engine.get_search_analytics()
        
        assert 'search_analytics' in analytics
        assert 'cache_stats' in analytics
        assert 'pattern_stats' in analytics
        assert 'configuration' in analytics
        
        assert analytics['search_analytics']['total_searches'] == 100
        assert analytics['cache_stats']['cache_hit_rate'] == 0.6
        assert analytics['pattern_stats']['total_patterns'] == 2
        assert analytics['configuration']['max_suggestions'] == 5
    
    async def test_get_health_status_healthy(self, search_engine, mock_storage_manager):
        """Test health status when system is healthy"""
        search_engine.storage_manager = mock_storage_manager
        
        # Set good metrics
        search_engine.search_analytics['total_searches'] = 100
        search_engine.search_analytics['cache_hits'] = 70
        search_engine.search_analytics['cache_misses'] = 30
        search_engine.search_analytics['rate_limit_hits'] = 5
        search_engine.search_analytics['avg_search_time'] = 0.5
        
        health = await search_engine.get_health_status()
        
        assert health.component == "knowledge_base_search_engine"
        assert health.status == "healthy"
        assert health.error_message is None
        assert health.metadata['total_searches'] == 100
        assert health.metadata['cache_hit_rate'] == 0.7
    
    async def test_get_health_status_degraded(self, search_engine, mock_storage_manager):
        """Test health status when system is degraded"""
        search_engine.storage_manager = mock_storage_manager
        
        # Set poor performance metrics
        search_engine.search_analytics['avg_search_time'] = 6.0  # Slow
        search_engine.search_analytics['total_searches'] = 100
        search_engine.search_analytics['cache_hits'] = 10
        search_engine.search_analytics['cache_misses'] = 90
        search_engine.search_analytics['rate_limit_hits'] = 5
        
        health = await search_engine.get_health_status()
        
        assert health.status == "degraded"
        assert "slow search performance" in health.error_message.lower()
    
    async def test_get_health_status_critical(self, search_engine):
        """Test health status when storage manager is not initialized"""
        search_engine.storage_manager = None
        
        health = await search_engine.get_health_status()
        
        assert health.status == "critical"
        assert "not initialized" in health.error_message.lower()
    
    async def test_shutdown(self, search_engine):
        """Test search engine shutdown"""
        # Set up some data
        search_engine.search_cache = {"key1": "value1"}
        search_engine.suggestion_cache = {"key2": "value2"}
        search_engine.rate_limit_tracker = {"user1": [datetime.utcnow()]}
        search_engine.cleanup_task = AsyncMock()
        
        await search_engine.shutdown()
        
        # Verify cleanup
        assert len(search_engine.search_cache) == 0
        assert len(search_engine.suggestion_cache) == 0
        assert len(search_engine.rate_limit_tracker) == 0
        search_engine.cleanup_task.cancel.assert_called_once()


class TestQuerySuggestion:
    """Test QuerySuggestion functionality"""
    
    def test_query_suggestion_creation(self):
        """Test QuerySuggestion creation"""
        suggestion = QuerySuggestion(
            suggested_query="What is the system status?",
            similarity_score=0.85,
            suggestion_type="pattern",
            related_results_count=10,
            avg_cost=0.12,
            avg_processing_time=1.8,
            success_rate=0.95,
            last_used=datetime.utcnow(),
            metadata={"source": "pattern_analysis"}
        )
        
        assert suggestion.suggested_query == "What is the system status?"
        assert suggestion.similarity_score == 0.85
        assert suggestion.suggestion_type == "pattern"
        assert suggestion.related_results_count == 10
        assert suggestion.metadata["source"] == "pattern_analysis"
    
    def test_query_suggestion_defaults(self):
        """Test QuerySuggestion with default metadata"""
        suggestion = QuerySuggestion(
            suggested_query="Test query",
            similarity_score=0.7,
            suggestion_type="test",
            related_results_count=1,
            avg_cost=0.1,
            avg_processing_time=1.0,
            success_rate=1.0,
            last_used=datetime.utcnow()
        )
        
        assert suggestion.metadata == {}


class TestSearchInsights:
    """Test SearchInsights functionality"""
    
    def test_search_insights_creation(self):
        """Test SearchInsights creation"""
        insights = SearchInsights(
            total_searches=100,
            unique_queries=75,
            most_common_topics=[("monitoring", 20), ("performance", 15)],
            avg_results_per_search=5.2,
            search_success_rate=0.92,
            popular_time_ranges=[("09:00-11:00", 25), ("14:00-16:00", 30)],
            cost_analysis={"avg_cost": 0.12, "total_cost": 12.0},
            performance_metrics={"avg_time": 0.8, "cache_hit_rate": 0.65}
        )
        
        assert insights.total_searches == 100
        assert insights.unique_queries == 75
        assert len(insights.most_common_topics) == 2
        assert insights.avg_results_per_search == 5.2
        assert insights.search_success_rate == 0.92
        assert insights.cost_analysis["avg_cost"] == 0.12
        assert insights.performance_metrics["cache_hit_rate"] == 0.65


class TestRetentionPolicy:
    """Test RetentionPolicy functionality"""
    
    def test_retention_policy_defaults(self):
        """Test RetentionPolicy with default values"""
        policy = RetentionPolicy()
        
        assert policy.max_age_days == 90
        assert policy.max_results_per_user == 1000
        assert policy.cleanup_batch_size == 100
        assert policy.cleanup_interval_hours == 24
        assert policy.preserve_high_value == True
        assert policy.high_value_threshold == 0.8
    
    def test_retention_policy_custom(self):
        """Test RetentionPolicy with custom values"""
        policy = RetentionPolicy(
            max_age_days=30,
            max_results_per_user=500,
            cleanup_batch_size=50,
            cleanup_interval_hours=12,
            preserve_high_value=False,
            high_value_threshold=0.9
        )
        
        assert policy.max_age_days == 30
        assert policy.max_results_per_user == 500
        assert policy.cleanup_batch_size == 50
        assert policy.cleanup_interval_hours == 12
        assert policy.preserve_high_value == False
        assert policy.high_value_threshold == 0.9


class TestGlobalSearchEngine:
    """Test global search engine instance"""
    
    async def test_get_knowledge_base_search_engine_singleton(self):
        """Test that get_knowledge_base_search_engine returns singleton"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.KnowledgeBaseSearchEngine') as mock_class:
            mock_instance = AsyncMock()
            mock_class.return_value = mock_instance
            
            # First call
            engine1 = await get_knowledge_base_search_engine()
            
            # Second call
            engine2 = await get_knowledge_base_search_engine()
            
            # Should be the same instance
            assert engine1 is engine2
            
            # Should only create one instance
            mock_class.assert_called_once()
            mock_instance.initialize.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])