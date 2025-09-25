"""
Integration tests for Knowledge Base Search Engine
Tests search engine integration with storage, advanced search scenarios, and real-world usage.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from src.beast_mode.observatory.ai_consultation.knowledge_base_search import (
    KnowledgeBaseSearchEngine, QuerySuggestion, SearchInsights, RetentionPolicy,
    get_knowledge_base_search_engine
)
from src.beast_mode.observatory.ai_consultation.results_storage import (
    SearchQuery, SearchResult, SearchType, KnowledgeBaseStats
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationResult, ProcessingMode
)
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestKnowledgeBaseSearchIntegration:
    """Integration tests for Knowledge Base Search Engine"""
    
    @pytest.fixture
    async def search_engine(self):
        """Create search engine with realistic configuration"""
        engine = KnowledgeBaseSearchEngine(
            max_suggestions=10,
            similarity_threshold=0.7,
            cache_size=500,
            rate_limit_per_minute=100,
            enable_semantic_search=True,
            retention_policy=RetentionPolicy(
                max_age_days=60,
                cleanup_interval_hours=12
            )
        )
        return engine
    
    def create_test_search_results(self, count: int = 5) -> List[SearchResult]:
        """Create test search results"""
        results = []
        topics = ["system monitoring", "performance analysis", "error handling", "database health", "network status"]
        
        for i in range(count):
            topic = topics[i % len(topics)]
            consultation_result = ConsultationResult(
                result_id=f"integration-result-{i}",
                query_id=f"integration-query-{i}",
                response_text=f"Integration test response about {topic}. This covers monitoring, metrics, and analysis of {topic} systems.",
                processing_time=1.5 + (i * 0.2),
                cost=0.08 + (i * 0.02),
                timestamp=datetime.utcnow() - timedelta(hours=i),
                processing_mode=ProcessingMode.QUEUE if i % 2 == 0 else ProcessingMode.REALTIME,
                metadata={
                    'query_text': f'What is the status of {topic}?',
                    'user_id': f'integration-user-{i % 3}',
                    'topic': topic,
                    'integration_test': True
                }
            )
            
            search_result = SearchResult(
                result=consultation_result,
                relevance_score=0.95 - (i * 0.05),
                similarity_score=0.90 - (i * 0.04),
                match_type="hybrid",
                matched_fields=["query_text", "response_text"]
            )
            results.append(search_result)
        
        return results
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_full_search_and_suggestion_integration(
        self, 
        mock_get_storage, 
        mock_flags, 
        search_engine
    ):
        """Test complete search and suggestion integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Mock knowledge base stats
        mock_stats = KnowledgeBaseStats(
            total_results=200,
            unique_users=50,
            date_range=(datetime.utcnow() - timedelta(days=60), datetime.utcnow()),
            avg_cost_per_query=0.11,
            total_cost=22.0,
            most_common_topics=[
                ("system monitoring alerts", 25),
                ("performance metrics analysis", 20),
                ("database connection issues", 15),
                ("network connectivity problems", 12),
                ("error troubleshooting guide", 10)
            ],
            success_rate=0.94,
            storage_size_mb=8.5
        )
        mock_storage.get_knowledge_base_stats.return_value = mock_stats
        
        # Mock search results for different search types
        test_results = self.create_test_search_results(8)
        
        def mock_search_results(search_query):
            if search_query.search_type == SearchType.EXACT:
                return test_results[:2]
            elif search_query.search_type == SearchType.SEMANTIC:
                return test_results[2:5]
            elif search_query.search_type == SearchType.SIMILAR:
                return test_results[3:6]
            else:  # KEYWORD or HYBRID
                return test_results
        
        mock_storage.search_results.side_effect = mock_search_results
        
        # Initialize search engine
        await search_engine.initialize()
        
        # Perform search with suggestions
        results, suggestions = await search_engine.search_with_suggestions(
            query_text="system monitoring performance analysis",
            user_id="integration-test-user",
            search_type=SearchType.HYBRID,
            include_suggestions=True,
            limit=10
        )
        
        # Verify search results
        assert len(results) > 0
        assert len(results) <= 10
        
        # Verify suggestions were generated
        assert len(suggestions) > 0
        assert len(suggestions) <= search_engine.max_suggestions
        
        # Verify different suggestion types
        suggestion_types = {s.suggestion_type for s in suggestions}
        assert len(suggestion_types) > 1  # Should have multiple types
        
        # Verify analytics were updated
        assert search_engine.search_analytics['total_searches'] == 1
        assert "system monitoring performance analysis" in search_engine.query_patterns
        
        # Verify storage manager was called multiple times for hybrid search
        assert mock_storage.search_results.call_count >= 3
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_advanced_suggestion_generation_integration(
        self, 
        mock_get_storage, 
        mock_flags, 
        search_engine
    ):
        """Test advanced suggestion generation with real patterns"""
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Set up realistic query patterns
        search_engine.query_patterns = {
            "system status monitoring dashboard": 15,
            "performance metrics cpu memory": 12,
            "database connection timeout errors": 10,
            "network latency high alerts": 8,
            "application response time slow": 7,
            "monitoring alerts configuration": 6,
            "system health check status": 5
        }
        
        # Set up topic keywords
        search_engine.topic_keywords = {
            "system monitoring": {"system", "monitoring", "status", "health", "dashboard"},
            "performance analysis": {"performance", "metrics", "cpu", "memory", "latency"},
            "database issues": {"database", "connection", "timeout", "query", "slow"},
            "network problems": {"network", "connectivity", "latency", "bandwidth", "packet"},
            "error handling": {"error", "exception", "troubleshooting", "debug", "fix"}
        }
        
        # Mock similar query search results
        similar_results = self.create_test_search_results(6)
        mock_storage.search_results.return_value = similar_results
        
        await search_engine.initialize()
        
        # Test pattern-based suggestions
        pattern_suggestions = await search_engine._generate_pattern_suggestions(
            "system monitoring dashboard performance"
        )
        
        assert len(pattern_suggestions) > 0
        # Should find patterns with similar keywords
        high_similarity_suggestions = [
            s for s in pattern_suggestions if s.similarity_score >= 0.7
        ]
        assert len(high_similarity_suggestions) > 0
        
        # Test topic-based suggestions
        topic_suggestions = await search_engine._generate_topic_suggestions(
            "database performance monitoring"
        )
        
        assert len(topic_suggestions) > 0
        # Should generate relevant topic queries
        database_suggestions = [
            s for s in topic_suggestions 
            if "database" in s.suggested_query.lower() or "performance" in s.suggested_query.lower()
        ]
        assert len(database_suggestions) > 0
        
        # Test similar query suggestions
        similar_suggestions = await search_engine._generate_similar_query_suggestions(
            "network connectivity issues"
        )
        
        assert len(similar_suggestions) > 0
        # Should use actual search results
        for suggestion in similar_suggestions:
            assert suggestion.avg_cost > 0
            assert suggestion.avg_processing_time > 0
            assert suggestion.last_used is not None
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_caching_performance_integration(
        self, 
        mock_get_storage, 
        mock_flags, 
        search_engine
    ):
        """Test caching performance under realistic load"""
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Mock search results
        test_results = self.create_test_search_results(10)
        mock_storage.search_results.return_value = test_results
        
        await search_engine.initialize()
        
        # Perform multiple searches with some repetition
        search_queries = [
            "system monitoring status",
            "performance analysis metrics",
            "database connection issues",
            "system monitoring status",  # Repeat
            "network connectivity problems",
            "performance analysis metrics",  # Repeat
            "error troubleshooting guide",
            "system monitoring status"  # Repeat again
        ]
        
        cache_hits_before = search_engine.search_analytics['cache_hits']
        cache_misses_before = search_engine.search_analytics['cache_misses']
        
        # Perform searches
        for i, query in enumerate(search_queries):
            results, suggestions = await search_engine.search_with_suggestions(
                query_text=query,
                user_id=f"cache-test-user-{i % 3}",  # 3 different users
                include_suggestions=True
            )
            
            assert len(results) > 0
        
        # Verify caching effectiveness
        cache_hits_after = search_engine.search_analytics['cache_hits']
        cache_misses_after = search_engine.search_analytics['cache_misses']
        
        # Should have some cache hits from repeated queries
        assert cache_hits_after > cache_hits_before
        
        # Calculate cache hit rate
        total_searches = (cache_hits_after - cache_hits_before) + (cache_misses_after - cache_misses_before)
        cache_hit_rate = (cache_hits_after - cache_hits_before) / total_searches if total_searches > 0 else 0
        
        # Should have reasonable cache hit rate due to repeated queries
        assert cache_hit_rate > 0.2  # At least 20% cache hit rate
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_rate_limiting_integration(
        self, 
        mock_get_storage, 
        mock_flags, 
        search_engine
    ):
        """Test rate limiting integration under load"""
        mock_flags.is_enabled.return_value = True
        
        # Set low rate limit for testing
        search_engine.rate_limit_per_minute = 10
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        mock_storage.search_results.return_value = self.create_test_search_results(3)
        
        await search_engine.initialize()
        
        # Perform searches up to rate limit
        successful_searches = 0
        rate_limited_searches = 0
        
        for i in range(15):  # Try more than rate limit
            try:
                results, suggestions = await search_engine.search_with_suggestions(
                    query_text=f"test query {i}",
                    user_id="rate-limit-test-user"
                )
                successful_searches += 1
            except Exception as e:
                if "Rate limit exceeded" in str(e):
                    rate_limited_searches += 1
                else:
                    raise
        
        # Should have hit rate limit
        assert successful_searches == 10  # Rate limit
        assert rate_limited_searches == 5  # Excess requests
        assert search_engine.search_analytics['rate_limit_hits'] == 5
        
        # Different user should still be able to search
        results, suggestions = await search_engine.search_with_suggestions(
            query_text="different user query",
            user_id="different-user"
        )
        assert len(results) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_search_insights_integration(
        self, 
        mock_get_storage, 
        mock_flags, 
        search_engine
    ):
        """Test search insights generation with realistic data"""
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Mock comprehensive knowledge base stats
        mock_stats = KnowledgeBaseStats(
            total_results=500,
            unique_users=75,
            date_range=(datetime.utcnow() - timedelta(days=90), datetime.utcnow()),
            avg_cost_per_query=0.13,
            total_cost=65.0,
            most_common_topics=[
                ("system monitoring dashboard alerts", 45),
                ("performance metrics cpu memory analysis", 38),
                ("database connection timeout troubleshooting", 32),
                ("network latency high bandwidth issues", 28),
                ("application response time optimization", 25),
                ("monitoring configuration best practices", 22),
                ("error handling exception debugging", 20),
                ("log analysis pattern recognition", 18),
                ("security monitoring threat detection", 15),
                ("infrastructure scaling recommendations", 12)
            ],
            success_rate=0.96,
            storage_size_mb=15.8
        )
        mock_storage.get_knowledge_base_stats.return_value = mock_stats
        
        await search_engine.initialize()
        
        # Simulate realistic search activity
        search_engine.search_analytics.update({
            'total_searches': 250,
            'cache_hits': 180,
            'cache_misses': 70,
            'suggestions_generated': 1200,
            'similarity_calculations': 3500,
            'avg_search_time': 0.45,
            'avg_suggestion_time': 0.12,
            'rate_limit_hits': 8
        })
        
        # Add realistic query patterns
        search_engine.query_patterns.update({
            "system status monitoring": 25,
            "performance analysis dashboard": 22,
            "database health check": 18,
            "network connectivity test": 15,
            "error log analysis": 12,
            "security alert review": 10,
            "infrastructure metrics": 8,
            "application performance": 7
        })
        
        # Get comprehensive insights
        insights = await search_engine.get_search_insights(
            user_id="insights-test-user",
            time_range_days=30
        )
        
        # Verify insights completeness
        assert insights.total_searches == 250
        assert insights.unique_queries == len(search_engine.query_patterns)
        assert len(insights.most_common_topics) == 10
        assert insights.avg_results_per_search > 0
        assert insights.search_success_rate > 0.9
        
        # Verify cost analysis
        assert insights.cost_analysis['avg_cost_per_search'] == 0.13
        assert insights.cost_analysis['total_search_cost'] == 65.0
        assert 'cost_savings_from_cache' in insights.cost_analysis
        
        # Verify performance metrics
        assert insights.performance_metrics['avg_search_time'] == 0.45
        assert insights.performance_metrics['avg_suggestion_time'] == 0.12
        assert insights.performance_metrics['cache_hit_rate'] > 0.7  # 180 / (180 + 70)
        assert insights.performance_metrics['rate_limit_hit_rate'] < 0.05  # 8 / 250
        
        # Verify time-based analysis
        assert len(insights.popular_time_ranges) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_cleanup_and_retention_integration(
        self, 
        mock_get_storage, 
        mock_flags, 
        search_engine
    ):
        """Test cleanup and retention policy integration"""
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        await search_engine.initialize()
        
        # Add test data with various ages
        current_time = datetime.utcnow()
        
        # Add search cache entries
        search_engine.search_cache.update({
            "recent_search_1": (current_time - timedelta(minutes=30), []),
            "recent_search_2": (current_time - timedelta(minutes=45), []),
            "old_search_1": (current_time - timedelta(hours=2), []),
            "old_search_2": (current_time - timedelta(hours=3), [])
        })
        
        # Add suggestion cache entries
        search_engine.suggestion_cache.update({
            "recent_suggestion_1": (current_time - timedelta(hours=1), []),
            "recent_suggestion_2": (current_time - timedelta(minutes=90), []),
            "old_suggestion_1": (current_time - timedelta(hours=3), []),
            "old_suggestion_2": (current_time - timedelta(hours=4), [])
        })
        
        # Add query patterns with different frequencies
        search_engine.query_patterns.update({
            "high_frequency_pattern": 15,
            "medium_frequency_pattern": 5,
            "low_frequency_pattern_1": 1,
            "low_frequency_pattern_2": 1,
            "single_use_pattern": 1
        })
        
        # Perform cleanup
        cleanup_stats = await search_engine.cleanup_old_data()
        
        # Verify cleanup results
        assert cleanup_stats['cache_entries_removed'] >= 2  # Old search cache entries
        assert cleanup_stats['suggestions_cleaned'] >= 2  # Old suggestion cache entries
        assert cleanup_stats['patterns_cleaned'] >= 3  # Low frequency patterns
        
        # Verify data was actually cleaned
        remaining_search_keys = list(search_engine.search_cache.keys())
        assert "recent_search_1" in remaining_search_keys
        assert "recent_search_2" in remaining_search_keys
        assert "old_search_1" not in remaining_search_keys
        assert "old_search_2" not in remaining_search_keys
        
        # Verify high-frequency patterns were preserved
        assert "high_frequency_pattern" in search_engine.query_patterns
        assert "medium_frequency_pattern" in search_engine.query_patterns
        assert search_engine.query_patterns["high_frequency_pattern"] == 15
    
    async def test_performance_under_concurrent_load(self, search_engine):
        """Test search engine performance under concurrent load"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager') as mock_get_storage:
                mock_flags.is_enabled.return_value = True
                
                # Mock storage manager
                mock_storage = AsyncMock()
                mock_get_storage.return_value = mock_storage
                mock_storage.search_results.return_value = self.create_test_search_results(5)
                
                await search_engine.initialize()
                
                # Create concurrent search tasks
                async def perform_search(query_id: int):
                    try:
                        results, suggestions = await search_engine.search_with_suggestions(
                            query_text=f"concurrent test query {query_id}",
                            user_id=f"concurrent-user-{query_id % 5}",
                            include_suggestions=True
                        )
                        return len(results), len(suggestions)
                    except Exception as e:
                        return 0, 0
                
                # Run concurrent searches
                concurrent_tasks = [perform_search(i) for i in range(20)]
                results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
                
                # Verify concurrent execution
                successful_searches = sum(1 for r in results if isinstance(r, tuple) and r[0] > 0)
                assert successful_searches > 15  # Most searches should succeed
                
                # Verify analytics were updated correctly
                assert search_engine.search_analytics['total_searches'] >= successful_searches
    
    async def test_error_handling_and_recovery_integration(self, search_engine):
        """Test error handling and recovery in integration scenarios"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager') as mock_get_storage:
                mock_flags.is_enabled.return_value = True
                
                # Mock storage manager with intermittent failures
                mock_storage = AsyncMock()
                mock_get_storage.return_value = mock_storage
                
                call_count = 0
                def mock_search_with_failures(search_query):
                    nonlocal call_count
                    call_count += 1
                    if call_count % 3 == 0:  # Every 3rd call fails
                        raise Exception("Simulated storage failure")
                    return self.create_test_search_results(3)
                
                mock_storage.search_results.side_effect = mock_search_with_failures
                
                await search_engine.initialize()
                
                # Perform searches with some expected failures
                successful_searches = 0
                failed_searches = 0
                
                for i in range(10):
                    try:
                        results, suggestions = await search_engine.search_with_suggestions(
                            query_text=f"error handling test {i}",
                            user_id="error-test-user"
                        )
                        successful_searches += 1
                    except Exception:
                        failed_searches += 1
                
                # Should have some successes and some failures
                assert successful_searches > 0
                assert failed_searches > 0
                
                # Search engine should still be functional
                health = await search_engine.get_health_status()
                assert health.component == "knowledge_base_search_engine"
                # May be degraded due to errors, but not completely broken
                assert health.status in ["healthy", "degraded", "unhealthy"]


class TestKnowledgeBaseSearchRealWorldScenarios:
    """Test knowledge base search with real-world scenarios"""
    
    @pytest.fixture
    async def production_search_engine(self):
        """Create search engine with production-like configuration"""
        engine = KnowledgeBaseSearchEngine(
            max_suggestions=15,
            similarity_threshold=0.75,
            cache_size=2000,
            rate_limit_per_minute=200,
            enable_semantic_search=True,
            retention_policy=RetentionPolicy(
                max_age_days=180,
                max_results_per_user=5000,
                cleanup_batch_size=500,
                cleanup_interval_hours=6
            )
        )
        return engine
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_enterprise_monitoring_scenario(
        self, 
        mock_get_storage, 
        mock_flags, 
        production_search_engine
    ):
        """Test enterprise monitoring consultation scenario"""
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Create enterprise-focused search results
        enterprise_results = []
        enterprise_topics = [
            "kubernetes cluster monitoring",
            "microservices performance analysis",
            "database connection pool optimization",
            "load balancer health checks",
            "api gateway rate limiting",
            "container resource utilization",
            "service mesh observability",
            "distributed tracing analysis"
        ]
        
        for i, topic in enumerate(enterprise_topics):
            result = ConsultationResult(
                result_id=f"enterprise-result-{i}",
                query_id=f"enterprise-query-{i}",
                response_text=f"Enterprise monitoring guidance for {topic}. This includes best practices, common issues, and optimization strategies for large-scale deployments.",
                processing_time=2.0 + (i * 0.1),
                cost=0.15 + (i * 0.01),
                timestamp=datetime.utcnow() - timedelta(hours=i * 2),
                processing_mode=ProcessingMode.QUEUE,
                metadata={
                    'query_text': f'How do I monitor {topic} in production?',
                    'user_id': f'enterprise-user-{i % 4}',
                    'topic': topic,
                    'enterprise': True,
                    'complexity': 'high'
                }
            )
            
            search_result = SearchResult(
                result=result,
                relevance_score=0.92 - (i * 0.02),
                similarity_score=0.88 - (i * 0.02),
                match_type="enterprise",
                matched_fields=["query_text", "response_text", "metadata"]
            )
            enterprise_results.append(search_result)
        
        mock_storage.search_results.return_value = enterprise_results
        
        await production_search_engine.initialize()
        
        # Test enterprise monitoring query
        results, suggestions = await production_search_engine.search_with_suggestions(
            query_text="kubernetes microservices monitoring best practices",
            user_id="enterprise-devops-engineer",
            search_type=SearchType.HYBRID,
            include_suggestions=True,
            limit=15
        )
        
        # Verify enterprise-quality results
        assert len(results) > 0
        assert len(suggestions) > 0
        
        # Verify suggestions are relevant to enterprise context
        enterprise_suggestions = [
            s for s in suggestions 
            if any(term in s.suggested_query.lower() 
                  for term in ["kubernetes", "microservices", "monitoring", "production"])
        ]
        assert len(enterprise_suggestions) > 0
        
        # Verify cost and performance metrics are realistic for enterprise
        for result in results[:5]:  # Check top 5 results
            assert result.result.cost > 0.10  # Enterprise queries typically cost more
            assert result.result.processing_time > 1.0  # More complex processing
    
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.get_results_storage_manager')
    async def test_troubleshooting_workflow_scenario(
        self, 
        mock_get_storage, 
        mock_flags, 
        production_search_engine
    ):
        """Test troubleshooting workflow with progressive queries"""
        mock_flags.is_enabled.return_value = True
        
        # Mock storage manager
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Create troubleshooting-focused results
        troubleshooting_results = []
        troubleshooting_scenarios = [
            ("high cpu usage", "CPU utilization is at 95%. Check for runaway processes and optimize resource allocation."),
            ("memory leak detection", "Memory usage increasing over time. Use profiling tools to identify memory leaks in application code."),
            ("database slow queries", "Query response times are high. Analyze query execution plans and add appropriate indexes."),
            ("network timeout errors", "Connection timeouts occurring. Check network latency, firewall rules, and connection pool settings."),
            ("disk space full", "Disk usage at 98%. Clean up log files, temporary files, and consider disk expansion."),
            ("service unavailable", "Service returning 503 errors. Check service health, dependencies, and load balancer configuration.")
        ]
        
        for i, (issue, solution) in enumerate(troubleshooting_scenarios):
            result = ConsultationResult(
                result_id=f"troubleshoot-result-{i}",
                query_id=f"troubleshoot-query-{i}",
                response_text=solution,
                processing_time=1.8,
                cost=0.12,
                timestamp=datetime.utcnow() - timedelta(minutes=i * 15),
                processing_mode=ProcessingMode.REALTIME,
                metadata={
                    'query_text': f'How do I fix {issue}?',
                    'user_id': 'troubleshooting-engineer',
                    'issue_type': issue,
                    'urgency': 'high',
                    'troubleshooting': True
                }
            )
            
            search_result = SearchResult(
                result=result,
                relevance_score=0.90,
                similarity_score=0.85,
                match_type="troubleshooting",
                matched_fields=["query_text", "response_text"]
            )
            troubleshooting_results.append(search_result)
        
        # Mock progressive search behavior
        def progressive_search_results(search_query):
            query_text = search_query.query_text.lower()
            relevant_results = []
            
            for result in troubleshooting_results:
                issue_type = result.result.metadata.get('issue_type', '')
                if any(term in query_text for term in issue_type.split()):
                    relevant_results.append(result)
            
            return relevant_results or troubleshooting_results[:3]  # Fallback
        
        mock_storage.search_results.side_effect = progressive_search_results
        
        await production_search_engine.initialize()
        
        # Simulate troubleshooting workflow
        troubleshooting_queries = [
            "system performance issues",
            "high cpu usage troubleshooting",
            "memory leak detection tools",
            "database performance optimization",
            "network connectivity problems"
        ]
        
        workflow_results = []
        for query in troubleshooting_queries:
            results, suggestions = await production_search_engine.search_with_suggestions(
                query_text=query,
                user_id="troubleshooting-engineer",
                include_suggestions=True
            )
            
            workflow_results.append({
                'query': query,
                'results_count': len(results),
                'suggestions_count': len(suggestions),
                'top_result': results[0] if results else None
            })
        
        # Verify progressive troubleshooting workflow
        assert len(workflow_results) == 5
        
        # Each query should return relevant results
        for workflow_result in workflow_results:
            assert workflow_result['results_count'] > 0
            assert workflow_result['suggestions_count'] > 0
            
            if workflow_result['top_result']:
                # Results should be relevant to troubleshooting
                metadata = workflow_result['top_result'].result.metadata
                assert metadata.get('troubleshooting') == True or 'issue_type' in metadata
        
        # Verify query patterns were learned
        assert len(production_search_engine.query_patterns) >= 5
        
        # Verify suggestions become more targeted over time
        final_suggestions = workflow_results[-1]['suggestions_count']
        assert final_suggestions > 0


class TestGlobalSearchEngineIntegration:
    """Test global search engine integration"""
    
    async def test_singleton_behavior_integration(self):
        """Test that global search engine maintains singleton behavior"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.KnowledgeBaseSearchEngine') as mock_class:
            mock_instance = AsyncMock()
            mock_class.return_value = mock_instance
            
            # Get multiple instances
            engine1 = await get_knowledge_base_search_engine()
            engine2 = await get_knowledge_base_search_engine()
            engine3 = await get_knowledge_base_search_engine()
            
            # Should all be the same instance
            assert engine1 is engine2
            assert engine2 is engine3
            
            # Should only create and initialize once
            mock_class.assert_called_once()
            mock_instance.initialize.assert_called_once()
    
    async def test_global_engine_state_persistence(self):
        """Test that global engine maintains state across calls"""
        with patch('src.beast_mode.observatory.ai_consultation.knowledge_base_search.KnowledgeBaseSearchEngine') as mock_class:
            mock_instance = AsyncMock()
            mock_instance.search_analytics = {'total_searches': 0}
            mock_instance.query_patterns = {}
            mock_class.return_value = mock_instance
            
            # Get engine and simulate some operations
            engine1 = await get_knowledge_base_search_engine()
            engine1.search_analytics['total_searches'] = 25
            engine1.query_patterns['test_pattern'] = 5
            
            # Get engine again
            engine2 = await get_knowledge_base_search_engine()
            
            # Should maintain state
            assert engine2.search_analytics['total_searches'] == 25
            assert engine2.query_patterns['test_pattern'] == 5


if __name__ == "__main__":
    pytest.main([__file__])