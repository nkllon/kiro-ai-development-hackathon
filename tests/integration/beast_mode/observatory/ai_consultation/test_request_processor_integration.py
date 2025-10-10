"""
Integration tests for RequestProcessor
Tests processor integration with Observatory context, security, and feature flags.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.beast_mode.observatory.ai_consultation.request_processor import (
    RequestProcessor, ContextInjectionMode, get_request_processor
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority, ObservatoryContext
)
from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityContext, PermissionLevel
)
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestRequestProcessorIntegration:
    """Integration tests for RequestProcessor"""
    
    @pytest.fixture
    async def processor(self):
        """Create processor with realistic configuration"""
        processor = RequestProcessor(
            max_processing_time=3.0,
            max_context_tokens=2000,
            max_query_tokens=1000,
            context_timeout=2.0,
            enable_optimization=True,
            thread_pool_size=2
        )
        await processor.initialize()
        return processor
    
    @pytest.fixture
    def security_context(self):
        """Create security context for testing"""
        return SecurityContext(
            user_id="integration-test-user",
            session_id="integration-test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    @pytest.fixture
    def observatory_context(self):
        """Create realistic Observatory context"""
        context = ObservatoryContext(
            system_status="healthy",
            active_alerts=3,
            metrics_summary={
                "count": 250,
                "healthy": 230,
                "warning": 15,
                "critical": 5,
                "response_time_avg": 0.45,
                "cpu_usage": 65.2,
                "memory_usage": 78.1
            },
            recent_events=[
                {
                    "timestamp": "2024-01-01T10:30:00Z",
                    "type": "alert",
                    "severity": "warning",
                    "message": "High memory usage detected on server-03",
                    "source": "monitoring-agent"
                },
                {
                    "timestamp": "2024-01-01T10:25:00Z",
                    "type": "info",
                    "message": "Database backup completed successfully",
                    "source": "backup-service"
                },
                {
                    "timestamp": "2024-01-01T10:20:00Z",
                    "type": "alert",
                    "severity": "critical",
                    "message": "Disk space critical on /var/log partition",
                    "source": "disk-monitor"
                }
            ],
            data_sensitivity="medium"
        )
        # Mock the get_token_estimate method
        context.get_token_estimate = MagicMock(return_value=350)
        return context
    
    def create_query(self, priority: QueryPriority = QueryPriority.NORMAL, text: str = None) -> ConsultationQuery:
        """Create test query"""
        return ConsultationQuery(
            query_id=f"integration-test-{datetime.utcnow().timestamp()}",
            user_id="integration-test-user",
            query_text=text or f"What's the current system status? Any issues I should know about?",
            priority=priority,
            timestamp=datetime.utcnow()
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_full_context_injection_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context, 
        observatory_context
    ):
        """Test full context injection with Observatory integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = observatory_context
        
        query = self.create_query(QueryPriority.HIGH, "What alerts are currently active? What's the system performance?")
        
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.FULL
        )
        
        # Verify full processing
        assert result.context_injection_mode == ContextInjectionMode.FULL
        assert result.injected_context == observatory_context
        assert result.system_prompt is not None
        
        # Verify Observatory context integration
        assert "System Status: healthy" in result.system_prompt
        assert "Active Alerts: 3" in result.system_prompt
        assert "cpu_usage: 65.2" in result.system_prompt
        assert "memory_usage: 78.1" in result.system_prompt
        assert "Recent Events: 3 events" in result.system_prompt
        
        # Verify context was requested with correct parameters
        mock_get_context.assert_called_once_with(
            user_id=query.user_id,
            security_context=security_context,
            include_metrics=True,
            include_alerts=True,
            include_status=True
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_summary_context_injection_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context, 
        observatory_context
    ):
        """Test summary context injection mode"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = observatory_context
        
        query = self.create_query(QueryPriority.NORMAL, "Give me a quick system overview")
        
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.SUMMARY
        )
        
        # Verify summary processing
        assert result.context_injection_mode == ContextInjectionMode.SUMMARY
        assert result.injected_context is not None
        assert result.system_prompt is not None
        
        # Verify limited recent events (should be truncated to 5)
        assert len(result.injected_context.recent_events) <= 5
        
        # Should still include basic system info
        assert "System Status: healthy" in result.system_prompt
        assert "Active Alerts: 3" in result.system_prompt
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_minimal_context_injection_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context, 
        observatory_context
    ):
        """Test minimal context injection mode"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = observatory_context
        
        query = self.create_query(QueryPriority.LOW, "Is the system running?")
        
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.MINIMAL
        )
        
        # Verify minimal processing
        assert result.context_injection_mode == ContextInjectionMode.MINIMAL
        assert result.injected_context is not None
        assert result.system_prompt is not None
        
        # Verify context was filtered to minimal info
        assert result.injected_context.metrics_summary == {"status": "available"}
        assert result.injected_context.recent_events == []
        
        # Should still include basic status
        assert "System Status: healthy" in result.system_prompt
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_permission_denied_integration(
        self, 
        mock_permission, 
        mock_flags,
        processor, 
        security_context
    ):
        """Test processing when user lacks permissions"""
        # Setup mocks - user lacks permissions
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = False
        
        query = self.create_query(QueryPriority.NORMAL, "Show me all system metrics")
        
        # Should still process but with warnings
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.FULL
        )
        
        # Processing should complete but context may be limited
        assert isinstance(result.processed_query_text, str)
        assert result.processing_time_ms > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    async def test_feature_flag_integration(self, mock_flags, processor, security_context):
        """Test integration with feature flags"""
        # Test with preprocessing disabled
        def feature_enabled(flag):
            if flag == FeatureFlag.REQUEST_PREPROCESSING:
                return False
            return True
        
        mock_flags.is_enabled.side_effect = feature_enabled
        
        query = self.create_query(QueryPriority.NORMAL, "Test query with preprocessing disabled")
        
        result = await processor.process_request(query, security_context)
        
        # Should return minimal processing
        assert result.context_injection_mode == ContextInjectionMode.NONE
        assert result.injected_context is None
        assert "preprocessing disabled" in result.warnings[0].lower()
        assert result.processed_query_text == query.query_text
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_context_timeout_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context
    ):
        """Test context injection timeout handling"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        # Mock slow context retrieval
        async def slow_context(*args, **kwargs):
            await asyncio.sleep(3.0)  # Longer than timeout
            return None
        
        mock_get_context.side_effect = slow_context
        
        query = self.create_query(QueryPriority.NORMAL, "Test timeout handling")
        
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.FULL
        )
        
        # Should complete without context due to timeout
        assert result.injected_context is None
        assert result.system_prompt is None
        assert processor.stats['context_timeouts'] > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_query_optimization_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context, 
        observatory_context
    ):
        """Test query optimization with real-world scenarios"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = observatory_context
        
        # Create messy query that needs optimization
        messy_query = """
        What    is   the   current   system   status???
        
        
        
        Are there any alerts I should know about???
        
        Can you tell me about the performance metrics???
        """
        
        query = self.create_query(QueryPriority.NORMAL, messy_query)
        
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.FULL, force_optimization=True
        )
        
        # Verify optimizations were applied
        assert len(result.processed_query_text) < len(messy_query)
        assert len(result.optimization_applied) > 0
        assert "whitespace_normalization" in result.optimization_applied
        assert "punctuation_deduplication" in result.optimization_applied
        assert "newline_normalization" in result.optimization_applied
        
        # Verify content is preserved
        assert "system status" in result.processed_query_text.lower()
        assert "alerts" in result.processed_query_text.lower()
        assert "performance metrics" in result.processed_query_text.lower()
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_token_limit_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context, 
        observatory_context
    ):
        """Test token limit handling with large queries and context"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = observatory_context
        
        # Create very large query
        large_query = "What is the system status? " * 500  # Should exceed limits
        
        query = self.create_query(QueryPriority.NORMAL, large_query)
        
        result = await processor.process_request(
            query, security_context, ContextInjectionMode.FULL
        )
        
        # Should apply token optimization
        assert len(result.processed_query_text) < len(large_query)
        assert "query_truncation" in result.optimization_applied
        assert result.processed_query_text.endswith("...")
        assert len(result.warnings) > 0
        assert "tokens" in result.warnings[0].lower()
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_context_caching_integration(
        self, 
        mock_permission, 
        mock_get_context, 
        mock_flags,
        processor, 
        security_context, 
        observatory_context
    ):
        """Test context caching across multiple requests"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = observatory_context
        
        # Process first request
        query1 = self.create_query(QueryPriority.NORMAL, "First query")
        result1 = await processor.process_request(
            query1, security_context, ContextInjectionMode.FULL
        )
        
        # Process second request (should use cache)
        query2 = self.create_query(QueryPriority.NORMAL, "Second query")
        result2 = await processor.process_request(
            query2, security_context, ContextInjectionMode.FULL
        )
        
        # Verify both got context
        assert result1.injected_context is not None
        assert result2.injected_context is not None
        assert result1.injected_context == result2.injected_context
        
        # Context should only be fetched once due to caching
        assert mock_get_context.call_count == 1
        assert len(processor.context_cache) == 1
    
    async def test_concurrent_processing_integration(self, processor, security_context):
        """Test concurrent processing with realistic load"""
        with patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context') as mock_get_context:
                with patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission') as mock_permission:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    mock_get_context.return_value = None  # Simple processing
                    
                    # Create multiple queries with different characteristics
                    queries = [
                        self.create_query(QueryPriority.URGENT, "URGENT: System down!"),
                        self.create_query(QueryPriority.HIGH, "High priority alert check"),
                        self.create_query(QueryPriority.NORMAL, "Normal status inquiry"),
                        self.create_query(QueryPriority.LOW, "Low priority question"),
                        self.create_query(QueryPriority.NORMAL, "Another normal query")
                    ]
                    
                    # Process all concurrently
                    tasks = [
                        processor.process_request(query, security_context, ContextInjectionMode.SUMMARY)
                        for query in queries
                    ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # All should complete successfully
                    assert len(results) == 5
                    for result in results:
                        assert not isinstance(result, Exception)
                        assert hasattr(result, 'processed_query_text')
                        assert result.processing_time_ms > 0
                    
                    # Check statistics updated correctly
                    assert processor.stats['requests_processed'] >= 5
    
    async def test_performance_monitoring_integration(self, processor, security_context):
        """Test performance monitoring and statistics"""
        initial_stats = await processor.get_processing_stats()
        
        with patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            # Process several requests
            for i in range(3):
                query = self.create_query(QueryPriority.NORMAL, f"Performance test query {i}")
                await processor.process_request(query, security_context, ContextInjectionMode.MINIMAL)
        
        final_stats = await processor.get_processing_stats()
        
        # Verify statistics updated
        assert final_stats['processing_stats']['requests_processed'] >= initial_stats['processing_stats']['requests_processed'] + 3
        assert final_stats['processing_stats']['avg_processing_time_ms'] > 0
        
        # Verify configuration is reported
        assert 'configuration' in final_stats
        assert final_stats['configuration']['max_processing_time'] == processor.max_processing_time
        assert final_stats['configuration']['max_context_tokens'] == processor.max_context_tokens
        
        # Verify cache stats
        assert 'cache_stats' in final_stats
        assert 'cache_size' in final_stats['cache_stats']
    
    async def test_health_monitoring_integration(self, processor):
        """Test health monitoring integration"""
        # Get initial health
        health = await processor.get_health_status()
        assert health.component == "request_processor"
        assert health.status in ["healthy", "degraded", "critical", "unhealthy"]
        
        # Process some requests to generate metrics
        with patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False  # Simple processing
            
            for i in range(5):
                query = self.create_query(QueryPriority.NORMAL, f"Health test query {i}")
                await processor.process_request(query)
        
        # Check health again
        health = await processor.get_health_status()
        assert 'requests_processed' in health.metadata
        assert 'success_rate' in health.metadata
        assert health.metadata['requests_processed'] >= 5


class TestGlobalProcessorIntegration:
    """Test global processor instance integration"""
    
    async def test_singleton_behavior(self):
        """Test that global processor maintains singleton behavior"""
        processor1 = await get_request_processor()
        processor2 = await get_request_processor()
        
        assert processor1 is processor2
        
        # Test state persistence across calls
        initial_requests = processor1.stats['requests_processed']
        
        # Process a request
        query = ConsultationQuery(
            query_id="singleton-test",
            user_id="test-user",
            query_text="Test singleton behavior",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            await processor1.process_request(query)
        
        processor3 = await get_request_processor()
        assert processor3.stats['requests_processed'] == initial_requests + 1


if __name__ == "__main__":
    pytest.main([__file__])