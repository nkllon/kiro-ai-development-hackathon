"""
Integration tests for Results Storage Manager
Tests storage manager integration with database, search functionality, and real-world scenarios.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
import json

from src.beast_mode.observatory.ai_consultation.results_storage import (
    ResultsStorageManager, SearchQuery, SearchResult, SearchType, 
    KnowledgeBaseStats, get_results_storage_manager
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationResult, ConsultationQuery, QueryPriority, ProcessingMode
)
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestResultsStorageIntegration:
    """Integration tests for Results Storage Manager"""
    
    @pytest.fixture
    async def storage_manager(self):
        """Create storage manager with realistic configuration"""
        manager = ResultsStorageManager(
            connection_pool_size=5,
            query_timeout=30.0,
            cache_ttl=300,
            max_search_results=100,
            enable_full_text_search=True
        )
        return manager
    
    def create_test_result(
        self, 
        result_id: str = None,
        query_id: str = None,
        user_id: str = "integration-test-user",
        query_text: str = None,
        response_text: str = None,
        cost: float = 0.15,
        processing_mode: ProcessingMode = ProcessingMode.REALTIME
    ) -> ConsultationResult:
        """Create test consultation result"""
        return ConsultationResult(
            result_id=result_id or f"integration-result-{datetime.utcnow().timestamp()}",
            query_id=query_id or f"integration-query-{datetime.utcnow().timestamp()}",
            response_text=response_text or f"Integration test response at {datetime.utcnow()}",
            processing_time=2.5,
            cost=cost,
            timestamp=datetime.utcnow(),
            processing_mode=processing_mode,
            metadata={
                'user_id': user_id,
                'query_text': query_text or f"Integration test query at {datetime.utcnow()}",
                'model_used': 'gpt-4',
                'tokens_used': 150,
                'integration_test': True
            }
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_full_storage_and_retrieval_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test complete storage and retrieval integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Initialize storage manager
        await storage_manager.initialize()
        
        # Create test result
        test_result = self.create_test_result(
            result_id="integration-test-1",
            query_id="integration-query-1",
            query_text="What is the system status?",
            response_text="The system is operating normally with all services running."
        )
        
        # Store result
        success = await storage_manager.store_result(test_result)
        assert success == True
        
        # Verify database calls
        assert mock_db.execute.call_count >= 3  # Main insert + pattern update + history update
        
        # Verify metrics
        assert storage_manager.metrics['results_stored'] == 1
        assert storage_manager.metrics['avg_storage_time'] > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_search_integration_with_multiple_types(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test search integration with different search types"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock search results
        mock_search_results = [
            {
                'result_id': 'search-result-1',
                'query_id': 'search-query-1',
                'user_id': 'search-user-1',
                'query_text': 'What is the system status?',
                'response_text': 'System is operational',
                'processing_time': 1.5,
                'cost': 0.10,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"model": "gpt-4"}',
                'relevance_score': 0.9,
                'similarity_score': 0.85,
                'query_hash': 'hash123'
            },
            {
                'result_id': 'search-result-2',
                'query_id': 'search-query-2',
                'user_id': 'search-user-2',
                'query_text': 'Check system health',
                'response_text': 'All systems healthy',
                'processing_time': 1.2,
                'cost': 0.08,
                'timestamp': datetime.utcnow() - timedelta(hours=1),
                'processing_mode': 'queue',
                'metadata': '{"model": "gpt-3.5"}',
                'relevance_score': 0.8,
                'similarity_score': 0.75,
                'query_hash': 'hash456'
            }
        ]
        
        mock_db.fetch.return_value = mock_search_results
        mock_get_db.return_value = mock_db
        
        await storage_manager.initialize()
        
        # Test keyword search
        keyword_query = SearchQuery(
            query_text="system status",
            search_type=SearchType.KEYWORD,
            limit=10
        )
        
        keyword_results = await storage_manager.search_results(keyword_query)
        
        assert len(keyword_results) == 2
        assert keyword_results[0].result.result_id == 'search-result-1'
        assert keyword_results[0].match_type == "keyword"
        assert storage_manager.metrics['searches_performed'] == 1
        
        # Test exact search
        exact_query = SearchQuery(
            query_text="What is the system status?",
            search_type=SearchType.EXACT,
            limit=10
        )
        
        exact_results = await storage_manager.search_results(exact_query)
        
        assert len(exact_results) == 2
        assert exact_results[0].match_type == "exact"
        assert storage_manager.metrics['searches_performed'] == 2
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_semantic_search_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test semantic search integration with pattern matching"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock pattern search results
        mock_db.fetch.side_effect = [
            # First call - similar patterns
            [
                {
                    'pattern_hash': 'semantic_hash_1',
                    'normalized_query': 'system status monitoring',
                    'query_count': 10,
                    'avg_cost': 0.12,
                    'success_rate': 0.95
                },
                {
                    'pattern_hash': 'semantic_hash_2',
                    'normalized_query': 'system health check',
                    'query_count': 8,
                    'avg_cost': 0.10,
                    'success_rate': 0.90
                }
            ],
            # Second call - results from patterns
            [
                {
                    'result_id': 'semantic-result-1',
                    'query_id': 'semantic-query-1',
                    'user_id': 'semantic-user-1',
                    'query_text': 'How is the system performing?',
                    'response_text': 'System performance is excellent',
                    'processing_time': 2.0,
                    'cost': 0.12,
                    'timestamp': datetime.utcnow(),
                    'processing_mode': 'realtime',
                    'metadata': '{"model": "gpt-4", "semantic": true}',
                    'query_hash': 'semantic_hash_1'
                },
                {
                    'result_id': 'semantic-result-2',
                    'query_id': 'semantic-query-2',
                    'user_id': 'semantic-user-2',
                    'query_text': 'Is the system healthy?',
                    'response_text': 'Yes, all systems are healthy',
                    'processing_time': 1.8,
                    'cost': 0.10,
                    'timestamp': datetime.utcnow() - timedelta(minutes=30),
                    'processing_mode': 'queue',
                    'metadata': '{"model": "gpt-3.5", "semantic": true}',
                    'query_hash': 'semantic_hash_2'
                }
            ]
        ]
        
        await storage_manager.initialize()
        
        # Test semantic search
        semantic_query = SearchQuery(
            query_text="system monitoring status",
            search_type=SearchType.SEMANTIC,
            limit=10
        )
        
        semantic_results = await storage_manager.search_results(semantic_query)
        
        assert len(semantic_results) == 2
        assert semantic_results[0].match_type == "semantic"
        assert semantic_results[0].similarity_score is not None
        assert semantic_results[0].similarity_score >= 0.5
        
        # Results should be sorted by similarity score
        assert semantic_results[0].similarity_score >= semantic_results[1].similarity_score
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_user_history_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test user history retrieval integration"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock user history results
        user_history_data = [
            {
                'result_id': 'history-result-1',
                'query_id': 'history-query-1',
                'user_id': 'history-user-123',
                'query_text': 'What are the current alerts?',
                'response_text': 'There are 2 active alerts',
                'processing_time': 1.5,
                'cost': 0.08,
                'timestamp': datetime.utcnow() - timedelta(hours=2),
                'processing_mode': 'realtime',
                'metadata': '{"priority": "high"}'
            },
            {
                'result_id': 'history-result-2',
                'query_id': 'history-query-2',
                'user_id': 'history-user-123',
                'query_text': 'Show me system metrics',
                'response_text': 'CPU: 45%, Memory: 60%, Disk: 30%',
                'processing_time': 2.2,
                'cost': 0.12,
                'timestamp': datetime.utcnow() - timedelta(hours=1),
                'processing_mode': 'queue',
                'metadata': '{"metrics": true}'
            },
            {
                'result_id': 'history-result-3',
                'query_id': 'history-query-3',
                'user_id': 'history-user-123',
                'query_text': 'Any recent errors?',
                'response_text': 'No recent errors detected',
                'processing_time': 1.0,
                'cost': 0.06,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"error_check": true}'
            }
        ]
        
        mock_db.fetch.return_value = user_history_data
        await storage_manager.initialize()
        
        # Get user history
        history = await storage_manager.get_user_history('history-user-123', limit=10)
        
        assert len(history) == 3
        assert history[0].result_id == 'history-result-1'
        assert history[1].result_id == 'history-result-2'
        assert history[2].result_id == 'history-result-3'
        
        # Verify all results belong to the same user
        for result in history:
            assert result.metadata.get('user_id') == 'history-user-123' or 'history-user-123' in str(result.metadata)
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_knowledge_base_stats_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test knowledge base statistics integration"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock basic stats
        mock_db.fetchrow.return_value = {
            'total_results': 250,
            'unique_users': 45,
            'earliest_date': datetime.utcnow() - timedelta(days=60),
            'latest_date': datetime.utcnow(),
            'avg_cost_per_query': 0.11,
            'total_cost': 27.50,
            'success_rate': 0.94,
            'storage_size': '15 MB'
        }
        
        # Mock topic stats
        mock_db.fetch.return_value = [
            {'normalized_query': 'system status monitoring alerts', 'query_count': 35},
            {'normalized_query': 'performance metrics analysis', 'query_count': 28},
            {'normalized_query': 'error troubleshooting guide', 'query_count': 22},
            {'normalized_query': 'database connection issues', 'query_count': 18},
            {'normalized_query': 'network connectivity problems', 'query_count': 15}
        ]
        
        await storage_manager.initialize()
        
        # Get knowledge base stats
        stats = await storage_manager.get_knowledge_base_stats()
        
        assert stats.total_results == 250
        assert stats.unique_users == 45
        assert stats.avg_cost_per_query == 0.11
        assert stats.total_cost == 27.50
        assert stats.success_rate == 0.94
        assert stats.storage_size_mb == 15.0
        assert len(stats.most_common_topics) == 5
        
        # Verify topics are sorted by count
        topic_counts = [count for _, count in stats.most_common_topics]
        assert topic_counts == sorted(topic_counts, reverse=True)
        
        # Verify date range
        assert isinstance(stats.date_range, tuple)
        assert len(stats.date_range) == 2
        assert stats.date_range[0] < stats.date_range[1]
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_caching_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test caching integration across multiple operations"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock search results
        mock_search_data = [
            {
                'result_id': 'cache-result-1',
                'query_id': 'cache-query-1',
                'user_id': 'cache-user-1',
                'query_text': 'Cache test query',
                'response_text': 'Cache test response',
                'processing_time': 1.0,
                'cost': 0.05,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"cached": true}',
                'relevance_score': 0.95
            }
        ]
        
        mock_db.fetch.return_value = mock_search_data
        await storage_manager.initialize()
        
        # First search - should miss cache
        search_query = SearchQuery(
            query_text="cache test",
            search_type=SearchType.KEYWORD,
            limit=5
        )
        
        results1 = await storage_manager.search_results(search_query)
        
        assert len(results1) == 1
        assert storage_manager.metrics['cache_misses'] == 1
        assert storage_manager.metrics['cache_hits'] == 0
        
        # Second identical search - should hit cache
        results2 = await storage_manager.search_results(search_query)
        
        assert len(results2) == 1
        assert storage_manager.metrics['cache_hits'] == 1
        assert storage_manager.metrics['cache_misses'] == 1
        
        # Verify cache hit rate
        metrics = await storage_manager.get_storage_metrics()
        assert metrics['cache_stats']['cache_hit_rate'] == 0.5  # 1 hit / 2 total
        
        # Different search - should miss cache again
        different_query = SearchQuery(
            query_text="different query",
            search_type=SearchType.KEYWORD,
            limit=5
        )
        
        results3 = await storage_manager.search_results(different_query)
        
        assert storage_manager.metrics['cache_misses'] == 2
        assert storage_manager.metrics['cache_hits'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_error_handling_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test error handling integration"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database with errors
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        await storage_manager.initialize()
        
        # Test storage error
        mock_db.execute.side_effect = Exception("Database connection lost")
        
        test_result = self.create_test_result(result_id="error-test-1")
        
        with pytest.raises(Exception):
            await storage_manager.store_result(test_result)
        
        assert storage_manager.metrics['database_errors'] == 1
        
        # Test search error with fallback
        mock_db.fetch.side_effect = Exception("Search query failed")
        
        search_query = SearchQuery(
            query_text="error test",
            search_type=SearchType.SIMILAR,  # This should fallback to keyword search
            limit=5
        )
        
        # Similar search should fallback to keyword search on error
        with pytest.raises(Exception):
            await storage_manager.search_results(search_query)
        
        assert storage_manager.metrics['database_errors'] == 2
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_feature_flag_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        storage_manager
    ):
        """Test feature flag integration"""
        # Test with feature disabled
        mock_flags.is_enabled.return_value = False
        
        await storage_manager.initialize()
        
        # Should not initialize database connection
        assert storage_manager.db is None
        
        # Storage should be skipped
        test_result = self.create_test_result(result_id="feature-test-1")
        success = await storage_manager.store_result(test_result)
        
        assert success == False
        assert storage_manager.metrics['results_stored'] == 0
        
        # Test with feature enabled
        mock_flags.is_enabled.return_value = True
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Re-initialize with feature enabled
        await storage_manager.initialize()
        
        assert storage_manager.db == mock_db
        
        # Storage should work now
        success = await storage_manager.store_result(test_result)
        
        assert success == True
        assert storage_manager.metrics['results_stored'] == 1
    
    async def test_health_monitoring_integration(self, storage_manager):
        """Test health monitoring integration"""
        # Test health without database
        health = await storage_manager.get_health_status()
        
        assert health.component == "results_storage_manager"
        assert health.status == "critical"
        assert "not initialized" in health.error_message.lower()
        
        # Test health with database
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection') as mock_get_db:
            mock_db = AsyncMock()
            mock_db.fetchval.return_value = 1  # Successful connectivity test
            mock_get_db.return_value = mock_db
            
            storage_manager.db = mock_db
            
            # Set good metrics
            storage_manager.metrics['results_stored'] = 100
            storage_manager.metrics['searches_performed'] = 50
            storage_manager.metrics['database_errors'] = 1
            storage_manager.metrics['cache_hits'] = 25
            storage_manager.metrics['cache_misses'] = 25
            
            health = await storage_manager.get_health_status()
            
            assert health.status == "healthy"
            assert health.error_message is None
            assert health.metadata['results_stored'] == 100
            assert health.metadata['error_rate'] == 0.01  # 1 error / 100 operations
            assert health.metadata['cache_hit_rate'] == 0.5
    
    async def test_performance_metrics_integration(self, storage_manager):
        """Test performance metrics integration"""
        # Simulate some operations
        storage_manager.metrics['results_stored'] = 75
        storage_manager.metrics['searches_performed'] = 40
        storage_manager.metrics['cache_hits'] = 20
        storage_manager.metrics['cache_misses'] = 20
        storage_manager.metrics['database_errors'] = 2
        storage_manager.metrics['avg_storage_time'] = 0.15
        storage_manager.metrics['avg_search_time'] = 0.08
        
        # Get metrics
        metrics = await storage_manager.get_storage_metrics()
        
        assert 'storage_metrics' in metrics
        assert 'cache_stats' in metrics
        assert 'configuration' in metrics
        
        # Verify storage metrics
        assert metrics['storage_metrics']['results_stored'] == 75
        assert metrics['storage_metrics']['searches_performed'] == 40
        assert metrics['storage_metrics']['database_errors'] == 2
        assert metrics['storage_metrics']['avg_storage_time'] == 0.15
        assert metrics['storage_metrics']['avg_search_time'] == 0.08
        
        # Verify cache stats
        assert metrics['cache_stats']['cache_hit_rate'] == 0.5
        assert metrics['cache_stats']['search_cache_size'] == 0  # No cache entries yet
        
        # Verify configuration
        assert metrics['configuration']['connection_pool_size'] == 5
        assert metrics['configuration']['enable_full_text_search'] == True


class TestResultsStorageRealWorldScenarios:
    """Test results storage with real-world scenarios"""
    
    @pytest.fixture
    async def production_storage_manager(self):
        """Create storage manager with production-like configuration"""
        manager = ResultsStorageManager(
            connection_pool_size=20,
            query_timeout=60.0,
            cache_ttl=600,  # 10 minutes
            max_search_results=200,
            enable_full_text_search=True
        )
        return manager
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_high_volume_storage_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        production_storage_manager
    ):
        """Test high-volume storage operations"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        await production_storage_manager.initialize()
        
        # Simulate storing many results
        results_to_store = []
        for i in range(50):
            result = ConsultationResult(
                result_id=f"volume-test-{i}",
                query_id=f"volume-query-{i}",
                response_text=f"Volume test response {i} about system monitoring and alerts",
                processing_time=1.0 + (i % 5) * 0.5,
                cost=0.08 + (i % 3) * 0.02,
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                processing_mode=ProcessingMode.QUEUE if i % 2 == 0 else ProcessingMode.REALTIME,
                metadata={
                    'user_id': f'volume-user-{i % 10}',  # 10 different users
                    'query_text': f'Volume query {i}: What is the status of component {i % 5}?',
                    'model_used': 'gpt-4' if i % 3 == 0 else 'gpt-3.5',
                    'volume_test': True,
                    'batch_id': i // 10  # Group into batches of 10
                }
            )
            results_to_store.append(result)
        
        # Store all results
        stored_count = 0
        for result in results_to_store:
            success = await production_storage_manager.store_result(result)
            if success:
                stored_count += 1
        
        assert stored_count == 50
        assert production_storage_manager.metrics['results_stored'] == 50
        assert production_storage_manager.metrics['avg_storage_time'] > 0
        
        # Verify database was called for each result
        assert mock_db.execute.call_count >= 150  # At least 3 calls per result (main + pattern + history)
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_complex_search_scenarios_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        production_storage_manager
    ):
        """Test complex search scenarios with filtering and pagination"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Create diverse mock search results
        mock_search_results = []
        for i in range(25):
            mock_search_results.append({
                'result_id': f'complex-result-{i}',
                'query_id': f'complex-query-{i}',
                'user_id': f'complex-user-{i % 5}',
                'query_text': f'Complex query {i}: System status for component {i % 3}',
                'response_text': f'Complex response {i}: Component {i % 3} is {"healthy" if i % 2 == 0 else "warning"}',
                'processing_time': 1.0 + (i % 10) * 0.2,
                'cost': 0.05 + (i % 8) * 0.01,
                'timestamp': datetime.utcnow() - timedelta(hours=i),
                'processing_mode': 'realtime' if i % 3 == 0 else 'queue',
                'metadata': json.dumps({
                    'component': i % 3,
                    'priority': 'high' if i % 4 == 0 else 'normal',
                    'complex_test': True
                }),
                'relevance_score': 0.9 - (i * 0.02),  # Decreasing relevance
                'similarity_score': 0.8 - (i * 0.015),
                'query_hash': f'complex_hash_{i % 10}'
            })
        
        mock_db.fetch.return_value = mock_search_results
        await production_storage_manager.initialize()
        
        # Test paginated search
        page1_query = SearchQuery(
            query_text="system status component",
            search_type=SearchType.KEYWORD,
            limit=10,
            offset=0,
            date_from=datetime.utcnow() - timedelta(days=1)
        )
        
        page1_results = await production_storage_manager.search_results(page1_query)
        assert len(page1_results) <= 10
        
        # Test user-filtered search
        user_query = SearchQuery(
            query_text="system status",
            search_type=SearchType.KEYWORD,
            user_id="complex-user-1",
            limit=20
        )
        
        user_results = await production_storage_manager.search_results(user_query)
        assert len(user_results) <= 20
        
        # Test date-range search
        recent_query = SearchQuery(
            query_text="component status",
            search_type=SearchType.KEYWORD,
            date_from=datetime.utcnow() - timedelta(hours=12),
            date_to=datetime.utcnow(),
            limit=15
        )
        
        recent_results = await production_storage_manager.search_results(recent_query)
        assert len(recent_results) <= 15
        
        # Verify search metrics
        assert production_storage_manager.metrics['searches_performed'] == 3
    
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection')
    async def test_cache_performance_integration(
        self, 
        mock_get_db, 
        mock_flags, 
        production_storage_manager
    ):
        """Test cache performance under load"""
        mock_flags.is_enabled.return_value = True
        
        # Mock database
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock consistent search results
        mock_search_data = [
            {
                'result_id': 'cache-perf-1',
                'query_id': 'cache-perf-query-1',
                'user_id': 'cache-perf-user',
                'query_text': 'Cache performance test query',
                'response_text': 'Cache performance test response',
                'processing_time': 1.5,
                'cost': 0.10,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"cache_test": true}',
                'relevance_score': 0.95
            }
        ]
        
        mock_db.fetch.return_value = mock_search_data
        await production_storage_manager.initialize()
        
        # Create multiple similar queries that should hit cache
        base_query = SearchQuery(
            query_text="cache performance test",
            search_type=SearchType.KEYWORD,
            limit=10
        )
        
        # First search - cache miss
        results1 = await production_storage_manager.search_results(base_query)
        assert len(results1) == 1
        assert production_storage_manager.metrics['cache_misses'] == 1
        
        # Multiple identical searches - should hit cache
        for i in range(10):
            results = await production_storage_manager.search_results(base_query)
            assert len(results) == 1
        
        # Verify cache performance
        assert production_storage_manager.metrics['cache_hits'] == 10
        assert production_storage_manager.metrics['cache_misses'] == 1
        
        # Calculate cache hit rate
        total_searches = production_storage_manager.metrics['cache_hits'] + production_storage_manager.metrics['cache_misses']
        cache_hit_rate = production_storage_manager.metrics['cache_hits'] / total_searches
        assert cache_hit_rate > 0.9  # Should be very high
        
        # Test cache with different queries
        different_queries = [
            SearchQuery(query_text="different query 1", search_type=SearchType.KEYWORD),
            SearchQuery(query_text="different query 2", search_type=SearchType.EXACT),
            SearchQuery(query_text="different query 3", search_type=SearchType.SEMANTIC)
        ]
        
        for query in different_queries:
            await production_storage_manager.search_results(query)
        
        # Should have more cache misses now
        assert production_storage_manager.metrics['cache_misses'] == 4  # 1 + 3 new queries
    
    async def test_long_running_operations_integration(self, production_storage_manager):
        """Test long-running operations and cleanup"""
        # Simulate long-running storage manager
        production_storage_manager.metrics['results_stored'] = 1000
        production_storage_manager.metrics['searches_performed'] = 500
        production_storage_manager.metrics['cache_hits'] = 300
        production_storage_manager.metrics['cache_misses'] = 200
        production_storage_manager.metrics['database_errors'] = 5
        production_storage_manager.metrics['avg_storage_time'] = 0.12
        production_storage_manager.metrics['avg_search_time'] = 0.06
        
        # Add many cache entries
        for i in range(150):
            cache_key = f"long_running_cache_key_{i}"
            cache_time = datetime.utcnow() - timedelta(minutes=i)  # Some old, some new
            cache_results = [MagicMock()]  # Mock search results
            production_storage_manager.search_cache[cache_key] = (cache_time, cache_results)
        
        # Set cache TTL to 5 minutes for testing
        production_storage_manager.cache_ttl = 300
        
        # Trigger cleanup
        production_storage_manager._clear_search_cache()
        
        # Cache should be cleared
        assert len(production_storage_manager.search_cache) == 0
        
        # Get comprehensive metrics
        metrics = await production_storage_manager.get_storage_metrics()
        
        # Verify long-running metrics
        assert metrics['storage_metrics']['results_stored'] == 1000
        assert metrics['storage_metrics']['searches_performed'] == 500
        assert metrics['cache_stats']['cache_hit_rate'] == 0.6  # 300 / (300 + 200)
        
        # Health should still be good despite some errors
        health = await production_storage_manager.get_health_status()
        error_rate = 5 / (1000 + 500)  # 5 errors out of 1500 operations
        assert error_rate < 0.01  # Less than 1% error rate
        assert health.status in ["healthy", "degraded"]  # Should not be critical


class TestGlobalStorageManagerIntegration:
    """Test global storage manager integration"""
    
    async def test_singleton_behavior_integration(self):
        """Test that global storage manager maintains singleton behavior"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.ResultsStorageManager') as mock_class:
            mock_instance = AsyncMock()
            mock_class.return_value = mock_instance
            
            # Get multiple instances
            manager1 = await get_results_storage_manager()
            manager2 = await get_results_storage_manager()
            manager3 = await get_results_storage_manager()
            
            # Should all be the same instance
            assert manager1 is manager2
            assert manager2 is manager3
            
            # Should only create and initialize once
            mock_class.assert_called_once()
            mock_instance.initialize.assert_called_once()
    
    async def test_global_manager_state_persistence(self):
        """Test that global manager maintains state across calls"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.ResultsStorageManager') as mock_class:
            mock_instance = AsyncMock()
            mock_instance.metrics = {'results_stored': 0}
            mock_class.return_value = mock_instance
            
            # Get manager and simulate some operations
            manager1 = await get_results_storage_manager()
            manager1.metrics['results_stored'] = 10
            
            # Get manager again
            manager2 = await get_results_storage_manager()
            
            # Should maintain state
            assert manager2.metrics['results_stored'] == 10


if __name__ == "__main__":
    pytest.main([__file__])