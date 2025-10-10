"""
Unit tests for Results Storage Manager
Tests storage, retrieval, search functionality, and database operations.
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
from src.beast_mode.observatory.ai_consultation.exceptions import StorageError


class TestResultsStorageManager:
    """Test ResultsStorageManager functionality"""
    
    @pytest.fixture
    def storage_manager(self):
        """Create storage manager for testing"""
        return ResultsStorageManager(
            connection_pool_size=5,
            query_timeout=10.0,
            cache_ttl=60,
            max_search_results=50,
            enable_full_text_search=True
        )
    
    @pytest.fixture
    def sample_consultation_result(self):
        """Create sample consultation result"""
        return ConsultationResult(
            result_id="test-result-123",
            query_id="test-query-123",
            response_text="This is a test response about system monitoring.",
            processing_time=2.5,
            cost=0.15,
            timestamp=datetime.utcnow(),
            processing_mode=ProcessingMode.REALTIME,
            metadata={
                'user_id': 'test-user-123',
                'query_text': 'What is the system status?',
                'model_used': 'gpt-4',
                'tokens_used': 150
            }
        )
    
    @pytest.fixture
    def mock_database(self):
        """Create mock database connection"""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.fetch = AsyncMock()
        mock_db.fetchrow = AsyncMock()
        mock_db.fetchval = AsyncMock()
        mock_db.transaction = AsyncMock()
        mock_db.close = AsyncMock()
        return mock_db
    
    async def test_initialization(self, storage_manager, mock_database):
        """Test storage manager initialization"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.results_storage.get_database_connection') as mock_get_db:
                mock_flags.is_enabled.return_value = True
                mock_get_db.return_value = mock_database
                
                await storage_manager.initialize()
                
                assert storage_manager.db == mock_database
                mock_get_db.assert_called_once()
                mock_database.execute.assert_called()  # Table creation calls
    
    async def test_initialization_disabled(self, storage_manager):
        """Test initialization when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            
            await storage_manager.initialize()
            
            assert storage_manager.db is None
    
    async def test_store_result_success(self, storage_manager, mock_database, sample_consultation_result):
        """Test successful result storage"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            storage_manager.db = mock_database
            
            result = await storage_manager.store_result(sample_consultation_result)
            
            assert result == True
            assert storage_manager.metrics['results_stored'] == 1
            mock_database.execute.assert_called()
    
    async def test_store_result_disabled(self, storage_manager, mock_database, sample_consultation_result):
        """Test result storage when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            storage_manager.db = mock_database
            
            result = await storage_manager.store_result(sample_consultation_result)
            
            assert result == False
            assert storage_manager.metrics['results_stored'] == 0
    
    async def test_store_result_database_error(self, storage_manager, mock_database, sample_consultation_result):
        """Test result storage with database error"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            storage_manager.db = mock_database
            mock_database.execute.side_effect = Exception("Database error")
            
            with pytest.raises(StorageError):
                await storage_manager.store_result(sample_consultation_result)
            
            assert storage_manager.metrics['database_errors'] == 1
    
    async def test_keyword_search(self, storage_manager, mock_database):
        """Test keyword-based search"""
        storage_manager.db = mock_database
        
        # Mock database response
        mock_database.fetch.return_value = [
            {
                'result_id': 'result-1',
                'query_id': 'query-1',
                'user_id': 'user-1',
                'query_text': 'What is the system status?',
                'response_text': 'System is operational',
                'processing_time': 1.5,
                'cost': 0.10,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"model": "gpt-4"}',
                'relevance_score': 0.8
            }
        ]
        
        search_query = SearchQuery(
            query_text="system status",
            search_type=SearchType.KEYWORD,
            limit=10
        )
        
        results = await storage_manager.search_results(search_query)
        
        assert len(results) == 1
        assert results[0].result.result_id == 'result-1'
        assert results[0].relevance_score == 0.8
        assert results[0].match_type == "keyword"
        assert storage_manager.metrics['searches_performed'] == 1
    
    async def test_exact_search(self, storage_manager, mock_database):
        """Test exact text match search"""
        storage_manager.db = mock_database
        
        mock_database.fetch.return_value = [
            {
                'result_id': 'result-1',
                'query_id': 'query-1',
                'user_id': 'user-1',
                'query_text': 'What is the system status?',
                'response_text': 'System is operational',
                'processing_time': 1.5,
                'cost': 0.10,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"model": "gpt-4"}',
                'relevance_score': 1.0
            }
        ]
        
        search_query = SearchQuery(
            query_text="What is the system status?",
            search_type=SearchType.EXACT,
            limit=10
        )
        
        results = await storage_manager.search_results(search_query)
        
        assert len(results) == 1
        assert results[0].relevance_score == 1.0
        assert results[0].match_type == "exact"
    
    async def test_semantic_search(self, storage_manager, mock_database):
        """Test semantic similarity search"""
        storage_manager.db = mock_database
        
        # Mock query patterns response
        mock_database.fetch.side_effect = [
            # First call - similar patterns
            [
                {
                    'pattern_hash': 'hash123',
                    'normalized_query': 'system status',
                    'query_count': 5,
                    'avg_cost': 0.12,
                    'success_rate': 0.9
                }
            ],
            # Second call - results from patterns
            [
                {
                    'result_id': 'result-1',
                    'query_id': 'query-1',
                    'user_id': 'user-1',
                    'query_text': 'What is the system status?',
                    'response_text': 'System is operational',
                    'processing_time': 1.5,
                    'cost': 0.10,
                    'timestamp': datetime.utcnow(),
                    'processing_mode': 'realtime',
                    'metadata': '{"model": "gpt-4"}',
                    'query_hash': 'hash123'
                }
            ]
        ]
        
        search_query = SearchQuery(
            query_text="system status",
            search_type=SearchType.SEMANTIC,
            limit=10
        )
        
        results = await storage_manager.search_results(search_query)
        
        assert len(results) == 1
        assert results[0].match_type == "semantic"
        assert results[0].similarity_score is not None
    
    async def test_similar_search(self, storage_manager, mock_database):
        """Test similar query search"""
        storage_manager.db = mock_database
        
        mock_database.fetch.return_value = [
            {
                'result_id': 'result-1',
                'query_id': 'query-1',
                'user_id': 'user-1',
                'query_text': 'What is the system status?',
                'response_text': 'System is operational',
                'processing_time': 1.5,
                'cost': 0.10,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"model": "gpt-4"}',
                'similarity_score': 0.85
            }
        ]
        
        search_query = SearchQuery(
            query_text="system status",
            search_type=SearchType.SIMILAR,
            min_similarity=0.7,
            limit=10
        )
        
        results = await storage_manager.search_results(search_query)
        
        assert len(results) == 1
        assert results[0].match_type == "similar"
        assert results[0].similarity_score == 0.85
    
    async def test_search_with_cache(self, storage_manager, mock_database):
        """Test search with caching"""
        storage_manager.db = mock_database
        
        # First search - cache miss
        mock_database.fetch.return_value = [
            {
                'result_id': 'result-1',
                'query_id': 'query-1',
                'user_id': 'user-1',
                'query_text': 'What is the system status?',
                'response_text': 'System is operational',
                'processing_time': 1.5,
                'cost': 0.10,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'realtime',
                'metadata': '{"model": "gpt-4"}',
                'relevance_score': 0.8
            }
        ]
        
        search_query = SearchQuery(
            query_text="system status",
            search_type=SearchType.KEYWORD,
            limit=10
        )
        
        # First search
        results1 = await storage_manager.search_results(search_query)
        assert storage_manager.metrics['cache_misses'] == 1
        assert storage_manager.metrics['cache_hits'] == 0
        
        # Second search - should hit cache
        results2 = await storage_manager.search_results(search_query)
        assert storage_manager.metrics['cache_hits'] == 1
        assert len(results1) == len(results2)
    
    async def test_get_result_by_id(self, storage_manager, mock_database):
        """Test retrieving result by ID"""
        storage_manager.db = mock_database
        
        mock_database.fetchrow.return_value = {
            'result_id': 'result-123',
            'query_id': 'query-123',
            'user_id': 'user-123',
            'query_text': 'What is the system status?',
            'response_text': 'System is operational',
            'processing_time': 1.5,
            'cost': 0.10,
            'timestamp': datetime.utcnow(),
            'processing_mode': 'realtime',
            'metadata': '{"model": "gpt-4"}'
        }
        
        result = await storage_manager.get_result_by_id('result-123')
        
        assert result is not None
        assert result.result_id == 'result-123'
        assert result.query_id == 'query-123'
        mock_database.fetchrow.assert_called_once()
    
    async def test_get_result_by_id_not_found(self, storage_manager, mock_database):
        """Test retrieving non-existent result"""
        storage_manager.db = mock_database
        mock_database.fetchrow.return_value = None
        
        result = await storage_manager.get_result_by_id('nonexistent')
        
        assert result is None
    
    async def test_get_user_history(self, storage_manager, mock_database):
        """Test retrieving user consultation history"""
        storage_manager.db = mock_database
        
        mock_database.fetch.return_value = [
            {
                'result_id': 'result-1',
                'query_id': 'query-1',
                'user_id': 'user-123',
                'query_text': 'Query 1',
                'response_text': 'Response 1',
                'processing_time': 1.0,
                'cost': 0.08,
                'timestamp': datetime.utcnow() - timedelta(hours=1),
                'processing_mode': 'realtime',
                'metadata': '{}'
            },
            {
                'result_id': 'result-2',
                'query_id': 'query-2',
                'user_id': 'user-123',
                'query_text': 'Query 2',
                'response_text': 'Response 2',
                'processing_time': 1.5,
                'cost': 0.12,
                'timestamp': datetime.utcnow(),
                'processing_mode': 'queue',
                'metadata': '{}'
            }
        ]
        
        history = await storage_manager.get_user_history('user-123', limit=10)
        
        assert len(history) == 2
        assert history[0].result_id == 'result-1'
        assert history[1].result_id == 'result-2'
    
    async def test_get_knowledge_base_stats(self, storage_manager, mock_database):
        """Test retrieving knowledge base statistics"""
        storage_manager.db = mock_database
        
        # Mock basic stats query
        mock_database.fetchrow.return_value = {
            'total_results': 100,
            'unique_users': 25,
            'earliest_date': datetime.utcnow() - timedelta(days=30),
            'latest_date': datetime.utcnow(),
            'avg_cost_per_query': 0.12,
            'total_cost': 12.0,
            'success_rate': 0.95,
            'storage_size': '5 MB'
        }
        
        # Mock topic stats query
        mock_database.fetch.return_value = [
            {'normalized_query': 'system status monitoring', 'query_count': 15},
            {'normalized_query': 'error troubleshooting', 'query_count': 12},
            {'normalized_query': 'performance metrics', 'query_count': 8}
        ]
        
        stats = await storage_manager.get_knowledge_base_stats()
        
        assert stats.total_results == 100
        assert stats.unique_users == 25
        assert stats.avg_cost_per_query == 0.12
        assert stats.total_cost == 12.0
        assert stats.success_rate == 0.95
        assert len(stats.most_common_topics) == 3
    
    async def test_get_knowledge_base_stats_cached(self, storage_manager, mock_database):
        """Test knowledge base stats with caching"""
        storage_manager.db = mock_database
        
        # Set up cache
        cached_stats = KnowledgeBaseStats(
            total_results=50,
            unique_users=10,
            date_range=(datetime.utcnow() - timedelta(days=7), datetime.utcnow()),
            avg_cost_per_query=0.10,
            total_cost=5.0,
            most_common_topics=[('test topic', 5)],
            success_rate=0.9,
            storage_size_mb=2.5
        )
        storage_manager.stats_cache = (datetime.utcnow(), cached_stats)
        
        stats = await storage_manager.get_knowledge_base_stats()
        
        assert stats.total_results == 50
        # Database should not be called due to cache
        mock_database.fetchrow.assert_not_called()
    
    def test_generate_query_hash(self, storage_manager):
        """Test query hash generation"""
        hash1 = storage_manager._generate_query_hash("query-1", "What is the system status?")
        hash2 = storage_manager._generate_query_hash("query-1", "What is the system status?")
        hash3 = storage_manager._generate_query_hash("query-2", "What is the system status?")
        
        assert hash1 == hash2  # Same query should produce same hash
        assert hash1 != hash3  # Different query ID should produce different hash
        assert len(hash1) == 16  # Hash should be 16 characters
    
    def test_normalize_query(self, storage_manager):
        """Test query text normalization"""
        normalized1 = storage_manager._normalize_query("What is the system status?")
        normalized2 = storage_manager._normalize_query("WHAT IS THE SYSTEM STATUS?")
        normalized3 = storage_manager._normalize_query("  What   is   the   system   status?  ")
        
        assert normalized1 == normalized2  # Case insensitive
        assert normalized1 == normalized3  # Whitespace normalized
        assert "what" not in normalized1  # Stop words removed
        assert "system" in normalized1
        assert "status" in normalized1
    
    def test_generate_search_cache_key(self, storage_manager):
        """Test search cache key generation"""
        search_query1 = SearchQuery(
            query_text="system status",
            search_type=SearchType.KEYWORD,
            user_id="user-1",
            limit=10
        )
        
        search_query2 = SearchQuery(
            query_text="system status",
            search_type=SearchType.KEYWORD,
            user_id="user-1",
            limit=10
        )
        
        search_query3 = SearchQuery(
            query_text="system status",
            search_type=SearchType.SEMANTIC,
            user_id="user-1",
            limit=10
        )
        
        key1 = storage_manager._generate_search_cache_key(search_query1)
        key2 = storage_manager._generate_search_cache_key(search_query2)
        key3 = storage_manager._generate_search_cache_key(search_query3)
        
        assert key1 == key2  # Same query should produce same key
        assert key1 != key3  # Different search type should produce different key
    
    def test_parse_storage_size(self, storage_manager):
        """Test storage size parsing"""
        assert storage_manager._parse_storage_size("1024 bytes") == 1024 / (1024 * 1024)
        assert storage_manager._parse_storage_size("5 kB") == 5 / 1024
        assert storage_manager._parse_storage_size("10 MB") == 10.0
        assert storage_manager._parse_storage_size("2 GB") == 2048.0
        assert storage_manager._parse_storage_size("invalid") == 0.0
    
    async def test_get_storage_metrics(self, storage_manager):
        """Test storage metrics retrieval"""
        # Set some metrics
        storage_manager.metrics['results_stored'] = 50
        storage_manager.metrics['searches_performed'] = 25
        storage_manager.metrics['cache_hits'] = 10
        storage_manager.metrics['cache_misses'] = 15
        
        metrics = await storage_manager.get_storage_metrics()
        
        assert 'storage_metrics' in metrics
        assert 'cache_stats' in metrics
        assert 'configuration' in metrics
        assert metrics['storage_metrics']['results_stored'] == 50
        assert metrics['cache_stats']['cache_hit_rate'] == 0.4  # 10 / (10 + 15)
    
    async def test_get_health_status_healthy(self, storage_manager, mock_database):
        """Test health status when system is healthy"""
        storage_manager.db = mock_database
        mock_database.fetchval.return_value = 1  # Database connectivity test
        
        # Set good metrics
        storage_manager.metrics['results_stored'] = 100
        storage_manager.metrics['searches_performed'] = 50
        storage_manager.metrics['database_errors'] = 2
        
        health = await storage_manager.get_health_status()
        
        assert health.component == "results_storage_manager"
        assert health.status == "healthy"
        assert health.error_message is None
        assert health.metadata['results_stored'] == 100
    
    async def test_get_health_status_degraded(self, storage_manager, mock_database):
        """Test health status when system is degraded"""
        storage_manager.db = mock_database
        mock_database.fetchval.return_value = 1
        
        # Set high error rate
        storage_manager.metrics['results_stored'] = 100
        storage_manager.metrics['searches_performed'] = 50
        storage_manager.metrics['database_errors'] = 10  # High error count
        
        health = await storage_manager.get_health_status()
        
        assert health.status == "degraded"
        assert "error rate" in health.error_message.lower()
    
    async def test_get_health_status_critical(self, storage_manager, mock_database):
        """Test health status when database is down"""
        storage_manager.db = mock_database
        mock_database.fetchval.side_effect = Exception("Database connection failed")
        
        health = await storage_manager.get_health_status()
        
        assert health.status == "critical"
        assert "database connectivity failed" in health.error_message.lower()
    
    async def test_get_health_status_no_db(self, storage_manager):
        """Test health status when database is not initialized"""
        storage_manager.db = None
        
        health = await storage_manager.get_health_status()
        
        assert health.status == "critical"
        assert "not initialized" in health.error_message.lower()
    
    async def test_shutdown(self, storage_manager, mock_database):
        """Test storage manager shutdown"""
        storage_manager.db = mock_database
        storage_manager.search_cache = {'key1': 'value1'}
        storage_manager.stats_cache = (datetime.utcnow(), MagicMock())
        
        await storage_manager.shutdown()
        
        assert len(storage_manager.search_cache) == 0
        assert storage_manager.stats_cache is None
        mock_database.close.assert_called_once()
        assert storage_manager.db is None


class TestSearchQuery:
    """Test SearchQuery functionality"""
    
    def test_search_query_creation(self):
        """Test SearchQuery creation with defaults"""
        query = SearchQuery(query_text="test query")
        
        assert query.query_text == "test query"
        assert query.search_type == SearchType.KEYWORD
        assert query.user_id is None
        assert query.limit == 10
        assert query.offset == 0
        assert query.include_metadata == True
        assert query.min_similarity == 0.7
    
    def test_search_query_custom_values(self):
        """Test SearchQuery with custom values"""
        query = SearchQuery(
            query_text="custom query",
            search_type=SearchType.SEMANTIC,
            user_id="user-123",
            date_from=datetime.utcnow() - timedelta(days=7),
            date_to=datetime.utcnow(),
            limit=20,
            offset=10,
            include_metadata=False,
            min_similarity=0.8
        )
        
        assert query.search_type == SearchType.SEMANTIC
        assert query.user_id == "user-123"
        assert query.limit == 20
        assert query.offset == 10
        assert query.include_metadata == False
        assert query.min_similarity == 0.8


class TestSearchResult:
    """Test SearchResult functionality"""
    
    def test_search_result_creation(self):
        """Test SearchResult creation"""
        consultation_result = ConsultationResult(
            result_id="test-result",
            query_id="test-query",
            response_text="Test response",
            processing_time=1.0,
            cost=0.10,
            timestamp=datetime.utcnow(),
            processing_mode=ProcessingMode.REALTIME,
            metadata={}
        )
        
        search_result = SearchResult(
            result=consultation_result,
            relevance_score=0.85,
            similarity_score=0.9,
            match_type="semantic",
            matched_fields=["query_text", "response_text"]
        )
        
        assert search_result.result == consultation_result
        assert search_result.relevance_score == 0.85
        assert search_result.similarity_score == 0.9
        assert search_result.match_type == "semantic"
        assert search_result.matched_fields == ["query_text", "response_text"]
    
    def test_search_result_defaults(self):
        """Test SearchResult with default values"""
        consultation_result = ConsultationResult(
            result_id="test-result",
            query_id="test-query",
            response_text="Test response",
            processing_time=1.0,
            cost=0.10,
            timestamp=datetime.utcnow(),
            processing_mode=ProcessingMode.REALTIME,
            metadata={}
        )
        
        search_result = SearchResult(
            result=consultation_result,
            relevance_score=0.75
        )
        
        assert search_result.similarity_score is None
        assert search_result.match_type == "keyword"
        assert search_result.matched_fields == []


class TestKnowledgeBaseStats:
    """Test KnowledgeBaseStats functionality"""
    
    def test_knowledge_base_stats_creation(self):
        """Test KnowledgeBaseStats creation"""
        stats = KnowledgeBaseStats(
            total_results=100,
            unique_users=25,
            date_range=(datetime.utcnow() - timedelta(days=30), datetime.utcnow()),
            avg_cost_per_query=0.12,
            total_cost=12.0,
            most_common_topics=[("system monitoring", 15), ("error handling", 10)],
            success_rate=0.95,
            storage_size_mb=5.2
        )
        
        assert stats.total_results == 100
        assert stats.unique_users == 25
        assert stats.avg_cost_per_query == 0.12
        assert stats.total_cost == 12.0
        assert len(stats.most_common_topics) == 2
        assert stats.success_rate == 0.95
        assert stats.storage_size_mb == 5.2


class TestGlobalStorageManager:
    """Test global storage manager instance"""
    
    async def test_get_results_storage_manager_singleton(self):
        """Test that get_results_storage_manager returns singleton"""
        with patch('src.beast_mode.observatory.ai_consultation.results_storage.ResultsStorageManager') as mock_class:
            mock_instance = AsyncMock()
            mock_class.return_value = mock_instance
            
            # First call
            manager1 = await get_results_storage_manager()
            
            # Second call
            manager2 = await get_results_storage_manager()
            
            # Should be the same instance
            assert manager1 is manager2
            
            # Should only create one instance
            mock_class.assert_called_once()
            mock_instance.initialize.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])