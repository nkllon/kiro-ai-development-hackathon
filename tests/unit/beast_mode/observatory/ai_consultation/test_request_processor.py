"""
Unit tests for RequestProcessor
Tests request preprocessing, context injection, and optimization functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.beast_mode.observatory.ai_consultation.request_processor import (
    RequestProcessor, ProcessingStage, ContextInjectionMode, ProcessedRequest,
    get_request_processor, process_consultation_request
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority, ObservatoryContext
)
from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityContext, PermissionLevel
)
from src.beast_mode.observatory.ai_consultation.exceptions import (
    ValidationError, ProcessingError
)


class TestRequestProcessor:
    """Test RequestProcessor functionality"""
    
    @pytest.fixture
    async def processor(self):
        """Create processor instance for testing"""
        processor = RequestProcessor(
            max_processing_time=2.0,
            max_context_tokens=1000,
            max_query_tokens=500,
            context_timeout=1.0,
            enable_optimization=True,
            thread_pool_size=2
        )
        await processor.initialize()
        return processor
    
    @pytest.fixture
    def sample_query(self):
        """Create sample consultation query"""
        return ConsultationQuery(
            query_id="test-query-123",
            user_id="test-user",
            query_text="What is the current system status? Are there any alerts?",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_security_context(self):
        """Create sample security context"""
        return SecurityContext(
            user_id="test-user",
            session_id="test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_observatory_context(self):
        """Create sample observatory context"""
        context = ObservatoryContext(
            system_status="healthy",
            active_alerts=2,
            metrics_summary={"count": 150, "healthy": 140, "warning": 8, "critical": 2},
            recent_events=[
                {"timestamp": "2024-01-01T10:00:00Z", "type": "alert", "message": "High CPU usage"},
                {"timestamp": "2024-01-01T09:30:00Z", "type": "info", "message": "System restart completed"}
            ],
            data_sensitivity="medium"
        )
        # Mock the get_token_estimate method
        context.get_token_estimate = MagicMock(return_value=200)
        return context
    
    async def test_processor_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor.max_processing_time == 2.0
        assert processor.max_context_tokens == 1000
        assert processor.max_query_tokens == 500
        assert processor.enable_optimization is True
        assert processor.stats['requests_processed'] == 0
        assert len(processor.optimization_patterns) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    async def test_process_request_feature_disabled(self, mock_flags, processor, sample_query):
        """Test processing when feature is disabled"""
        mock_flags.is_enabled.return_value = False
        
        result = await processor.process_request(sample_query)
        
        assert isinstance(result, ProcessedRequest)
        assert result.processed_query_text == sample_query.query_text
        assert result.context_injection_mode == ContextInjectionMode.NONE
        assert result.injected_context is None
        assert "preprocessing disabled" in result.warnings[0].lower()
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_request_validation_success(self, mock_permission, mock_flags, processor, sample_query, sample_security_context):
        """Test successful request validation"""
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        # Should not raise exception
        await processor._validate_request(sample_query, sample_security_context)
    
    async def test_request_validation_empty_query(self, processor, sample_security_context):
        """Test validation fails for empty query"""
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with pytest.raises(ValidationError, match="Query text cannot be empty"):
            await processor._validate_request(query, sample_security_context)
    
    async def test_request_validation_too_long(self, processor, sample_security_context):
        """Test validation fails for overly long query"""
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="x" * 50001,  # Too long
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with pytest.raises(ValidationError, match="Query text too long"):
            await processor._validate_request(query, sample_security_context)
    
    async def test_query_preprocessing_optimization(self, processor):
        """Test query preprocessing with optimization"""
        # Query with various issues to optimize
        messy_query = "What   is    the   status???   \n\n\n\nAre there alerts???"
        
        processed_text, optimizations = await processor._preprocess_query(messy_query, force_optimization=True)
        
        assert len(processed_text) < len(messy_query)
        assert "whitespace_normalization" in optimizations
        assert "punctuation_deduplication" in optimizations
        assert "newline_normalization" in optimizations
        assert processed_text.strip() == processed_text  # Should be trimmed
    
    async def test_query_preprocessing_disabled(self, processor):
        """Test query preprocessing when optimization is disabled"""
        processor.enable_optimization = False
        original_query = "What   is    the   status???"
        
        processed_text, optimizations = await processor._preprocess_query(original_query)
        
        assert processed_text == original_query
        assert len(optimizations) == 0
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    async def test_context_injection_full_mode(self, mock_get_context, processor, sample_query, sample_security_context, sample_observatory_context):
        """Test full context injection mode"""
        mock_get_context.return_value = sample_observatory_context
        
        context, system_prompt = await processor._inject_context(
            sample_query, sample_security_context, ContextInjectionMode.FULL
        )
        
        assert context == sample_observatory_context
        assert system_prompt is not None
        assert "Observatory monitoring system" in system_prompt
        assert "System Status: healthy" in system_prompt
        assert "Active Alerts: 2" in system_prompt
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    async def test_context_injection_minimal_mode(self, mock_get_context, processor, sample_query, sample_security_context, sample_observatory_context):
        """Test minimal context injection mode"""
        mock_get_context.return_value = sample_observatory_context
        
        context, system_prompt = await processor._inject_context(
            sample_query, sample_security_context, ContextInjectionMode.MINIMAL
        )
        
        assert context is not None
        assert context.metrics_summary == {"status": "available"}  # Should be filtered
        assert context.recent_events == []  # Should be empty
        assert system_prompt is not None
    
    async def test_context_injection_none_mode(self, processor, sample_query, sample_security_context):
        """Test no context injection mode"""
        context, system_prompt = await processor._inject_context(
            sample_query, sample_security_context, ContextInjectionMode.NONE
        )
        
        assert context is None
        assert system_prompt is None
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    async def test_context_injection_timeout(self, mock_get_context, processor, sample_query, sample_security_context):
        """Test context injection with timeout"""
        # Mock a slow context retrieval
        async def slow_context(*args, **kwargs):
            await asyncio.sleep(2.0)  # Longer than timeout
            return None
        
        mock_get_context.side_effect = slow_context
        
        context, system_prompt = await processor._inject_context(
            sample_query, sample_security_context, ContextInjectionMode.FULL
        )
        
        assert context is None
        assert system_prompt is None
        assert processor.stats['context_timeouts'] > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    async def test_context_caching(self, mock_get_context, processor, sample_query, sample_security_context, sample_observatory_context):
        """Test context caching functionality"""
        mock_get_context.return_value = sample_observatory_context
        
        # First call should retrieve context
        context1, _ = await processor._inject_context(
            sample_query, sample_security_context, ContextInjectionMode.FULL
        )
        
        # Second call should use cache
        context2, _ = await processor._inject_context(
            sample_query, sample_security_context, ContextInjectionMode.FULL
        )
        
        assert context1 == context2
        assert mock_get_context.call_count == 1  # Should only be called once due to caching
        assert len(processor.context_cache) == 1
    
    async def test_token_estimation(self, processor):
        """Test token estimation functionality"""
        short_text = "Hello"
        long_text = "This is a much longer text that should have more tokens estimated"
        
        short_tokens = processor._estimate_tokens(short_text)
        long_tokens = processor._estimate_tokens(long_text)
        
        assert short_tokens > 0
        assert long_tokens > short_tokens
        assert processor._estimate_tokens("") == 0
        assert processor._estimate_tokens(None) == 0
    
    async def test_token_optimization(self, processor, sample_observatory_context):
        """Test token optimization for large queries"""
        # Create a very long query
        long_query = "What is the system status? " * 200  # Should exceed token limits
        
        optimized_text, optimizations = await processor._optimize_for_tokens(
            long_query, sample_observatory_context, "System prompt"
        )
        
        assert len(optimized_text) < len(long_query)
        assert "query_truncation" in optimizations
        assert optimized_text.endswith("...")
    
    async def test_system_prompt_creation(self, processor, sample_observatory_context):
        """Test system prompt creation with context"""
        prompt = processor._create_system_prompt(sample_observatory_context, ContextInjectionMode.FULL)
        
        assert prompt is not None
        assert "Observatory monitoring system" in prompt
        assert "System Status: healthy" in prompt
        assert "Active Alerts: 2" in prompt
        assert "Guidelines:" in prompt
        assert "actionable advice" in prompt
    
    async def test_system_prompt_creation_minimal(self, processor, sample_observatory_context):
        """Test system prompt creation with minimal context"""
        prompt = processor._create_system_prompt(sample_observatory_context, ContextInjectionMode.MINIMAL)
        
        assert prompt is not None
        assert "System Status: healthy" in prompt
        # Should not include detailed metrics or events
        assert "Recent Events:" not in prompt
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.check_permission')
    async def test_full_processing_flow(self, mock_permission, mock_get_context, mock_flags, processor, sample_query, sample_security_context, sample_observatory_context):
        """Test complete processing flow"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        mock_get_context.return_value = sample_observatory_context
        
        result = await processor.process_request(
            sample_query, sample_security_context, ContextInjectionMode.FULL
        )
        
        assert isinstance(result, ProcessedRequest)
        assert result.original_query == sample_query
        assert result.processed_query_text is not None
        assert result.injected_context == sample_observatory_context
        assert result.context_injection_mode == ContextInjectionMode.FULL
        assert result.system_prompt is not None
        assert result.estimated_tokens > 0
        assert len(result.processing_metrics) == 5  # All processing stages
        assert result.processing_time_ms > 0
        
        # Check processing stages
        stages = [metric.stage for metric in result.processing_metrics]
        assert ProcessingStage.VALIDATION in stages
        assert ProcessingStage.PREPROCESSING in stages
        assert ProcessingStage.CONTEXT_INJECTION in stages
        assert ProcessingStage.OPTIMIZATION in stages
        assert ProcessingStage.FINALIZATION in stages
    
    async def test_processing_with_errors(self, processor, sample_query):
        """Test processing handles errors gracefully"""
        # Create invalid query to trigger validation error
        invalid_query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="",  # Empty text
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        result = await processor.process_request(invalid_query)
        
        assert isinstance(result, ProcessedRequest)
        assert len(result.warnings) > 0
        assert "Processing failed" in result.warnings[0]
        assert result.context_injection_mode == ContextInjectionMode.NONE
    
    async def test_statistics_tracking(self, processor):
        """Test processing statistics tracking"""
        initial_stats = await processor.get_processing_stats()
        initial_requests = initial_stats['processing_stats']['requests_processed']
        
        # Process a request
        query = ConsultationQuery(
            query_id="stats-test",
            user_id="test-user",
            query_text="Test query for stats",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False  # Disable for simple processing
            await processor.process_request(query)
        
        final_stats = await processor.get_processing_stats()
        final_requests = final_stats['processing_stats']['requests_processed']
        
        assert final_requests == initial_requests + 1
        assert 'configuration' in final_stats
        assert 'cache_stats' in final_stats
        assert 'thread_pool_stats' in final_stats
    
    async def test_cache_management(self, processor, sample_query, sample_security_context, sample_observatory_context):
        """Test context cache management"""
        # Add something to cache
        cache_key = f"{sample_query.user_id}:full"
        processor.context_cache[cache_key] = (sample_observatory_context, datetime.utcnow())
        
        assert len(processor.context_cache) == 1
        
        # Clear cache
        success = await processor.clear_context_cache()
        assert success
        assert len(processor.context_cache) == 0
    
    async def test_health_status_healthy(self, processor):
        """Test health status when processor is healthy"""
        # Set good stats
        processor.stats['requests_processed'] = 100
        processor.stats['requests_failed'] = 5
        processor.stats['avg_processing_time_ms'] = 500.0
        processor.stats['context_injections'] = 80
        processor.stats['context_timeouts'] = 5
        
        health = await processor.get_health_status()
        
        assert health.component == "request_processor"
        assert health.status == "healthy"
        assert health.error_message is None
        assert health.metadata['success_rate'] > 0.8
    
    async def test_health_status_degraded(self, processor):
        """Test health status when processor is degraded"""
        # Set poor performance stats
        processor.stats['requests_processed'] = 100
        processor.stats['requests_failed'] = 5
        processor.stats['avg_processing_time_ms'] = 3000.0  # Too slow
        processor.stats['context_injections'] = 80
        processor.stats['context_timeouts'] = 5
        
        health = await processor.get_health_status()
        
        assert health.component == "request_processor"
        assert health.status == "degraded"
        assert "processing time" in health.error_message.lower()
    
    async def test_health_status_critical(self, processor):
        """Test health status when processor is critical"""
        # Set very poor stats
        processor.stats['requests_processed'] = 100
        processor.stats['requests_failed'] = 50  # High failure rate
        processor.stats['avg_processing_time_ms'] = 500.0
        processor.stats['context_injections'] = 80
        processor.stats['context_timeouts'] = 5
        
        health = await processor.get_health_status()
        
        assert health.component == "request_processor"
        assert health.status == "critical"
        assert "success rate" in health.error_message.lower()
    
    async def test_concurrent_processing(self, processor):
        """Test handling multiple concurrent processing requests"""
        queries = [
            ConsultationQuery(
                query_id=f"concurrent-{i}",
                user_id="test-user",
                query_text=f"Concurrent query {i}",
                priority=QueryPriority.NORMAL,
                timestamp=datetime.utcnow()
            )
            for i in range(5)
        ]
        
        with patch('src.beast_mode.observatory.ai_consultation.request_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False  # Simple processing
            
            # Process all queries concurrently
            tasks = [processor.process_request(query) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == 5
        for result in results:
            assert not isinstance(result, Exception)
            assert isinstance(result, ProcessedRequest)
        
        # Check statistics updated correctly
        assert processor.stats['requests_processed'] >= 5


class TestGlobalProcessorFunctions:
    """Test global processor functions"""
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor._request_processor', None)
    async def test_get_request_processor(self):
        """Test getting global processor instance"""
        processor1 = await get_request_processor()
        processor2 = await get_request_processor()
        
        assert processor1 is processor2  # Should be singleton
        assert isinstance(processor1, RequestProcessor)
    
    @patch('src.beast_mode.observatory.ai_consultation.request_processor.get_request_processor')
    async def test_process_consultation_request(self, mock_get_processor):
        """Test convenience processing function"""
        # Mock processor
        mock_processor = AsyncMock()
        mock_result = ProcessedRequest(
            original_query=MagicMock(),
            processed_query_text="Processed query",
            injected_context=None,
            context_injection_mode=ContextInjectionMode.NONE,
            system_prompt=None,
            estimated_tokens=50,
            processing_metrics=[],
            optimization_applied=[],
            warnings=[],
            processing_time_ms=100.0
        )
        mock_processor.process_request.return_value = mock_result
        mock_get_processor.return_value = mock_processor
        
        # Create test query
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="Test query",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        # Process request
        result = await process_consultation_request(query)
        
        assert result == mock_result
        mock_processor.process_request.assert_called_once_with(
            query, None, ContextInjectionMode.FULL, False
        )


if __name__ == "__main__":
    pytest.main([__file__])