"""
Integration tests for LLM Service
Tests LLM service integration with request processing, cost tracking, and real providers.
"""

import pytest
import asyncio
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.beast_mode.observatory.ai_consultation.llm_service import (
    LLMService, LLMProvider, LLMModel, get_llm_service
)
from src.beast_mode.observatory.ai_consultation.request_processor import (
    ProcessedRequest, ContextInjectionMode
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority, ObservatoryContext
)
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestLLMServiceIntegration:
    """Integration tests for LLM Service"""
    
    @pytest.fixture
    async def llm_service(self):
        """Create LLM service with realistic configuration"""
        service = LLMService(
            default_provider=LLMProvider.MOCK,
            default_model=LLMModel.MOCK_MODEL,
            cost_warning_threshold=0.25,
            cost_cutoff_threshold=1.00,
            max_retries=2,
            retry_delay=0.1
        )
        await service.initialize()
        return service
    
    @pytest.fixture
    def observatory_context(self):
        """Create Observatory context for testing"""
        context = ObservatoryContext(
            system_status="healthy",
            active_alerts=3,
            metrics_summary={
                "count": 200,
                "healthy": 185,
                "warning": 12,
                "critical": 3,
                "cpu_avg": 72.3,
                "memory_avg": 68.9,
                "disk_avg": 45.2
            },
            recent_events=[
                {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "type": "alert",
                    "severity": "warning",
                    "message": "High CPU usage on database-server-01"
                },
                {
                    "timestamp": "2024-01-01T11:55:00Z",
                    "type": "info",
                    "message": "Backup process completed successfully"
                }
            ],
            data_sensitivity="medium"
        )
        context.get_token_estimate = MagicMock(return_value=320)
        return context
    
    def create_processed_request(
        self, 
        query_text: str = "What is the current system status?",
        context: ObservatoryContext = None,
        session_id: str = "integration-test-session"
    ) -> ProcessedRequest:
        """Create processed request for testing"""
        query = ConsultationQuery(
            query_id=f"integration-test-{datetime.utcnow().timestamp()}",
            user_id="integration-test-user",
            query_text=query_text,
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        query.session_id = session_id  # Add session_id for testing
        
        system_prompt = None
        if context:
            system_prompt = f"You are an AI assistant for Observatory monitoring. Current system status: {context.system_status}. Active alerts: {context.active_alerts}."
        
        return ProcessedRequest(
            original_query=query,
            processed_query_text=query_text,
            injected_context=context,
            context_injection_mode=ContextInjectionMode.FULL if context else ContextInjectionMode.NONE,
            system_prompt=system_prompt,
            estimated_tokens=len(query_text.split()) * 1.3,
            processing_metrics=[],
            optimization_applied=[],
            warnings=[],
            processing_time_ms=50.0
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_basic_response_generation_integration(self, mock_flags, llm_service, observatory_context):
        """Test basic response generation with Observatory context"""
        mock_flags.is_enabled.return_value = True
        
        processed_request = self.create_processed_request(
            "What alerts are currently active in the system?",
            observatory_context
        )
        
        response = await llm_service.generate_response(processed_request)
        
        # Verify response structure
        assert response.session_id == processed_request.original_query.session_id
        assert response.provider == LLMProvider.MOCK
        assert len(response.content) > 0
        assert response.usage.total_tokens > 0
        assert response.cost.total_cost > 0
        
        # Verify contextual response
        assert "alert" in response.content.lower()
        
        # Verify cost tracking
        session_cost = await llm_service.get_session_cost(response.session_id)
        assert session_cost == response.cost.total_cost
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_streaming_response_integration(self, mock_flags, llm_service, observatory_context):
        """Test streaming response generation with context"""
        mock_flags.is_enabled.return_value = True
        
        processed_request = self.create_processed_request(
            "Can you explain the current performance metrics?",
            observatory_context
        )
        
        chunks = []
        final_usage = None
        final_cost = None
        
        async for content, usage, cost in llm_service.generate_streaming_response(processed_request):
            if usage and cost:
                final_usage = usage
                final_cost = cost
            else:
                chunks.append(content)
        
        # Verify streaming worked
        assert len(chunks) > 0
        assert final_usage is not None
        assert final_cost is not None
        
        # Verify content is contextual
        full_content = "".join(chunks)
        assert "performance" in full_content.lower()
        
        # Verify statistics
        assert llm_service.stats['requests_streamed'] == 1
        assert llm_service.stats['requests_successful'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_cost_tracking_integration(self, mock_flags, llm_service):
        """Test cost tracking across multiple requests"""
        mock_flags.is_enabled.return_value = True
        
        session_id = "cost-tracking-session"
        
        # Generate multiple requests for same session
        requests = [
            self.create_processed_request("What is the system status?", session_id=session_id),
            self.create_processed_request("Are there any alerts?", session_id=session_id),
            self.create_processed_request("How is performance?", session_id=session_id)
        ]
        
        total_expected_cost = 0.0
        
        for request in requests:
            response = await llm_service.generate_response(request)
            total_expected_cost += response.cost.total_cost
        
        # Verify cost accumulation
        session_cost = await llm_service.get_session_cost(session_id)
        assert abs(session_cost - total_expected_cost) < 0.0001  # Account for floating point precision
        
        # Verify global cost tracking
        assert llm_service.total_cost >= total_expected_cost
        assert llm_service.stats['total_cost'] >= total_expected_cost
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.status_manager')
    async def test_cost_warning_integration(self, mock_status, mock_flags, llm_service):
        """Test cost warning system integration"""
        mock_flags.is_enabled.return_value = True
        mock_status.update_cost_analytics = AsyncMock()
        
        session_id = "warning-test-session"
        
        # Set session cost near warning threshold
        llm_service.session_costs[session_id] = 0.20  # Close to 0.25 threshold
        
        processed_request = self.create_processed_request(
            "This should trigger a cost warning",
            session_id=session_id
        )
        
        # Generate response that should push over warning threshold
        response = await llm_service.generate_response(processed_request)
        
        # Should have triggered warning
        assert llm_service.stats['cost_warnings_issued'] >= 1
        
        # Status manager should have been called
        mock_status.update_cost_analytics.assert_called()
        
        # Call should include warning information
        call_args = mock_status.update_cost_analytics.call_args[0][0]
        assert call_args['warning_issued'] is True
        assert call_args['session_id'] == session_id
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_cost_cutoff_integration(self, mock_flags, llm_service):
        """Test cost cutoff system integration"""
        mock_flags.is_enabled.return_value = True
        
        session_id = "cutoff-test-session"
        
        # Set session cost above cutoff threshold
        llm_service.session_costs[session_id] = 1.50  # Above 1.00 threshold
        
        processed_request = self.create_processed_request(
            "This should be rejected due to cost",
            session_id=session_id
        )
        
        # Should reject request
        with pytest.raises(Exception, match="Session cost limit exceeded"):
            await llm_service.generate_response(processed_request)
        
        # Should track cutoff
        assert llm_service.stats['cost_cutoffs_triggered'] >= 1
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_provider_fallback_integration(self, mock_flags, llm_service):
        """Test provider fallback mechanism"""
        mock_flags.is_enabled.return_value = True
        
        # Create a failing provider
        failing_provider = AsyncMock()
        failing_provider.generate_response.side_effect = Exception("Provider unavailable")
        
        # Add failing provider as OpenAI
        llm_service.providers[LLMProvider.OPENAI] = failing_provider
        
        processed_request = self.create_processed_request("Test fallback mechanism")
        
        # Request with failing provider should fallback to mock
        response = await llm_service.generate_response(
            processed_request,
            provider=LLMProvider.OPENAI
        )
        
        # Should succeed with mock provider
        assert response.provider == LLMProvider.MOCK
        assert len(response.content) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_feature_flag_integration(self, mock_flags, llm_service):
        """Test feature flag integration"""
        processed_request = self.create_processed_request("Test feature flags")
        
        # Test with LLM services disabled
        def feature_enabled(flag):
            if flag == FeatureFlag.AI_SERVICES:
                return False
            return True
        
        mock_flags.is_enabled.side_effect = feature_enabled
        
        # Should fail when disabled
        with pytest.raises(Exception, match="LLM services are disabled"):
            await llm_service.generate_response(processed_request)
        
        # Test with services enabled
        mock_flags.is_enabled.return_value = True
        
        # Should succeed when enabled
        response = await llm_service.generate_response(processed_request)
        assert isinstance(response.content, str)
        assert len(response.content) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_concurrent_requests_integration(self, mock_flags, llm_service):
        """Test handling concurrent requests"""
        mock_flags.is_enabled.return_value = True
        
        # Create multiple concurrent requests
        requests = [
            self.create_processed_request(f"Concurrent request {i}", session_id=f"concurrent-{i}")
            for i in range(5)
        ]
        
        # Process all concurrently
        tasks = [
            llm_service.generate_response(request)
            for request in requests
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(responses) == 5
        for response in responses:
            assert not isinstance(response, Exception)
            assert hasattr(response, 'content')
            assert len(response.content) > 0
        
        # Statistics should reflect all requests
        assert llm_service.stats['requests_total'] == 5
        assert llm_service.stats['requests_successful'] == 5
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_different_query_types_integration(self, mock_flags, llm_service, observatory_context):
        """Test different types of queries with context"""
        mock_flags.is_enabled.return_value = True
        
        query_types = [
            ("What is the current system status?", "status"),
            ("Are there any active alerts?", "alert"),
            ("How is system performance?", "performance"),
            ("What errors have occurred recently?", "error"),
            ("Can you help me troubleshoot an issue?", "help")
        ]
        
        for query_text, expected_keyword in query_types:
            processed_request = self.create_processed_request(query_text, observatory_context)
            
            response = await llm_service.generate_response(processed_request)
            
            # Verify contextual response
            assert expected_keyword in response.content.lower()
            assert len(response.content) > 50  # Reasonable response length
            
            # Verify cost tracking
            assert response.cost.total_cost > 0
    
    async def test_statistics_integration(self, llm_service):
        """Test statistics tracking integration"""
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            initial_stats = await llm_service.get_service_stats()
            initial_requests = initial_stats['llm_stats']['requests_total']
            
            # Generate several requests
            for i in range(3):
                processed_request = self.create_processed_request(
                    f"Statistics test query {i}",
                    session_id=f"stats-session-{i}"
                )
                await llm_service.generate_response(processed_request)
            
            final_stats = await llm_service.get_service_stats()
            
            # Verify statistics updated
            assert final_stats['llm_stats']['requests_total'] == initial_requests + 3
            assert final_stats['llm_stats']['requests_successful'] >= 3
            assert final_stats['llm_stats']['total_cost'] > 0
            assert final_stats['llm_stats']['total_tokens'] > 0
            
            # Verify configuration reported
            assert final_stats['configuration']['default_provider'] == "mock"
            assert final_stats['configuration']['cost_warning_threshold'] == 0.25
            
            # Verify provider information
            assert 'mock' in final_stats['providers']
            assert final_stats['providers']['mock']['available'] is True
    
    async def test_health_monitoring_integration(self, llm_service):
        """Test health monitoring integration"""
        # Get initial health
        health = await llm_service.get_health_status()
        assert health.component == "llm_service"
        assert health.status in ["healthy", "degraded", "critical", "unhealthy"]
        
        # Process some requests to generate metrics
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            for i in range(3):
                processed_request = self.create_processed_request(f"Health test query {i}")
                await llm_service.generate_response(processed_request)
        
        # Check health again
        health = await llm_service.get_health_status()
        assert 'success_rate' in health.metadata
        assert 'total_cost' in health.metadata
        assert 'total_tokens' in health.metadata
        assert health.metadata['success_rate'] > 0
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_real_openai_integration(self, mock_flags):
        """Test integration with real OpenAI API (if API key available)"""
        mock_flags.is_enabled.return_value = True
        
        # Create service with OpenAI as default
        service = LLMService(
            default_provider=LLMProvider.OPENAI,
            default_model=LLMModel.GPT_3_5_TURBO,
            cost_warning_threshold=0.10,
            cost_cutoff_threshold=0.50
        )
        await service.initialize()
        
        # Verify OpenAI provider is available
        assert LLMProvider.OPENAI in service.providers
        
        # Test health check
        openai_provider = service.providers[LLMProvider.OPENAI]
        health = await openai_provider.health_check()
        
        if health.status == "healthy":
            # Test actual API call (small request to minimize cost)
            processed_request = self.create_processed_request(
                "Hello, this is a test. Please respond briefly."
            )
            
            response = await service.generate_response(
                processed_request,
                model=LLMModel.GPT_3_5_TURBO
            )
            
            # Verify real response
            assert response.provider == LLMProvider.OPENAI
            assert response.model == LLMModel.GPT_3_5_TURBO
            assert len(response.content) > 0
            assert response.usage.total_tokens > 0
            assert response.cost.total_cost > 0
            
            print(f"Real OpenAI response: {response.content[:100]}...")
            print(f"Cost: ${response.cost.total_cost:.6f}")
            print(f"Tokens: {response.usage.total_tokens}")
        else:
            print(f"OpenAI provider not healthy: {health.error_message}")


class TestGlobalLLMServiceIntegration:
    """Test global LLM service instance integration"""
    
    async def test_singleton_behavior_integration(self):
        """Test that global LLM service maintains singleton behavior"""
        service1 = await get_llm_service()
        service2 = await get_llm_service()
        
        assert service1 is service2
        
        # Test state persistence across calls
        initial_requests = service1.stats['requests_total']
        
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            # Create and process a request
            query = ConsultationQuery(
                query_id="singleton-test",
                user_id="test-user",
                query_text="Test singleton behavior",
                priority=QueryPriority.NORMAL,
                timestamp=datetime.utcnow()
            )
            query.session_id = "singleton-session"
            
            processed_request = ProcessedRequest(
                original_query=query,
                processed_query_text="Test singleton behavior",
                injected_context=None,
                context_injection_mode=ContextInjectionMode.NONE,
                system_prompt=None,
                estimated_tokens=10,
                processing_metrics=[],
                optimization_applied=[],
                warnings=[],
                processing_time_ms=50.0
            )
            
            await service1.generate_response(processed_request)
        
        # Get third instance
        service3 = await get_llm_service()
        
        # Should see the request processed by service1
        assert service3.stats['requests_total'] == initial_requests + 1


if __name__ == "__main__":
    pytest.main([__file__])