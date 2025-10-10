"""
Unit tests for LLM Service
Tests LLM API integration, cost tracking, and streaming responses.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.beast_mode.observatory.ai_consultation.llm_service import (
    LLMService, LLMProvider, LLMModel, LLMRequest, LLMResponse, LLMUsage, LLMCost,
    OpenAIProvider, MockLLMProvider, get_llm_service
)
from src.beast_mode.observatory.ai_consultation.request_processor import ProcessedRequest
from src.beast_mode.observatory.ai_consultation.models import ConsultationQuery, QueryPriority
from src.beast_mode.observatory.ai_consultation.exceptions import ProcessingError


class TestLLMUsage:
    """Test LLMUsage functionality"""
    
    def test_llm_usage_creation(self):
        """Test creating LLM usage"""
        usage = LLMUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.input_tokens == 100  # Alias
        assert usage.output_tokens == 50   # Alias


class TestLLMCost:
    """Test LLMCost functionality"""
    
    def test_llm_cost_creation(self):
        """Test creating LLM cost"""
        usage = LLMUsage(100, 50, 150)
        
        cost = LLMCost(
            provider=LLMProvider.OPENAI,
            model=LLMModel.GPT_3_5_TURBO,
            usage=usage,
            input_cost_per_token=0.0000005,
            output_cost_per_token=0.0000015,
            total_cost=0.000125
        )
        
        assert cost.provider == LLMProvider.OPENAI
        assert cost.model == LLMModel.GPT_3_5_TURBO
        assert cost.usage == usage
        assert cost.total_cost == 0.000125
    
    def test_llm_cost_to_dict(self):
        """Test converting LLM cost to dictionary"""
        usage = LLMUsage(100, 50, 150)
        cost = LLMCost(
            provider=LLMProvider.OPENAI,
            model=LLMModel.GPT_4,
            usage=usage,
            input_cost_per_token=0.00003,
            output_cost_per_token=0.00006,
            total_cost=0.006
        )
        
        cost_dict = cost.to_dict()
        
        assert cost_dict['provider'] == "openai"
        assert cost_dict['model'] == "gpt-4"
        assert cost_dict['total_cost'] == 0.006
        assert cost_dict['currency'] == "USD"


class TestLLMRequest:
    """Test LLMRequest functionality"""
    
    def test_llm_request_creation(self):
        """Test creating LLM request"""
        request = LLMRequest(
            session_id="test-session",
            user_id="test-user",
            messages=[{"role": "user", "content": "Hello"}],
            model=LLMModel.GPT_3_5_TURBO,
            system_prompt="You are a helpful assistant",
            max_tokens=1000,
            temperature=0.7,
            stream=False,
            timeout=30.0
        )
        
        assert request.session_id == "test-session"
        assert request.user_id == "test-user"
        assert len(request.messages) == 1
        assert request.model == LLMModel.GPT_3_5_TURBO
        assert request.system_prompt == "You are a helpful assistant"
        assert request.max_tokens == 1000
        assert request.temperature == 0.7
        assert request.stream is False
        assert request.timeout == 30.0
    
    def test_llm_request_to_dict(self):
        """Test converting LLM request to dictionary"""
        request = LLMRequest(
            session_id="test-session",
            user_id="test-user",
            messages=[{"role": "user", "content": "Hello"}],
            model=LLMModel.GPT_4,
            temperature=0.5
        )
        
        request_dict = request.to_dict()
        
        assert request_dict['session_id'] == "test-session"
        assert request_dict['user_id'] == "test-user"
        assert request_dict['model'] == "gpt-4"
        assert request_dict['temperature'] == 0.5


class TestMockLLMProvider:
    """Test MockLLMProvider functionality"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create mock LLM provider"""
        return MockLLMProvider()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample LLM request"""
        return LLMRequest(
            session_id="test-session",
            user_id="test-user",
            messages=[{"role": "user", "content": "What is the system status?"}],
            model=LLMModel.MOCK_MODEL
        )
    
    async def test_generate_response(self, mock_provider, sample_request):
        """Test generating response with mock provider"""
        response = await mock_provider.generate_response(sample_request)
        
        assert isinstance(response, LLMResponse)
        assert response.session_id == "test-session"
        assert response.provider == LLMProvider.MOCK
        assert response.model == LLMModel.MOCK_MODEL
        assert len(response.content) > 0
        assert response.usage.total_tokens > 0
        assert response.cost.total_cost > 0
        assert response.finish_reason == "stop"
    
    async def test_generate_streaming_response(self, mock_provider, sample_request):
        """Test generating streaming response with mock provider"""
        chunks = []
        final_usage = None
        
        async for content, usage in mock_provider.generate_streaming_response(sample_request):
            if usage:
                final_usage = usage
            else:
                chunks.append(content)
        
        # Should have received content chunks
        assert len(chunks) > 0
        
        # Should have received final usage
        assert final_usage is not None
        assert final_usage.total_tokens > 0
        
        # Reconstruct full content
        full_content = "".join(chunks)
        assert len(full_content) > 0
    
    def test_calculate_cost(self, mock_provider):
        """Test cost calculation with mock provider"""
        usage = LLMUsage(100, 50, 150)
        
        cost = mock_provider.calculate_cost(LLMModel.MOCK_MODEL, usage)
        
        assert isinstance(cost, LLMCost)
        assert cost.provider == LLMProvider.MOCK
        assert cost.model == LLMModel.MOCK_MODEL
        assert cost.usage == usage
        assert cost.total_cost > 0
        assert cost.total_cost < 0.01  # Should be very cheap for mock
    
    async def test_health_check(self, mock_provider):
        """Test health check with mock provider"""
        health = await mock_provider.health_check()
        
        assert health.component == "mock_llm_provider"
        assert health.status == "healthy"
        assert health.metadata["mock"] is True
        assert health.metadata["always_available"] is True
    
    def test_contextual_responses(self, mock_provider):
        """Test that mock provider generates contextual responses"""
        # Test status query
        status_request = LLMRequest(
            session_id="test",
            user_id="test",
            messages=[{"role": "user", "content": "What is the system status?"}],
            model=LLMModel.MOCK_MODEL
        )
        
        content = mock_provider._generate_mock_content(status_request)
        assert "system" in content.lower()
        assert "status" in content.lower()
        
        # Test alert query
        alert_request = LLMRequest(
            session_id="test",
            user_id="test",
            messages=[{"role": "user", "content": "Are there any alerts?"}],
            model=LLMModel.MOCK_MODEL
        )
        
        content = mock_provider._generate_mock_content(alert_request)
        assert "alert" in content.lower()


class TestOpenAIProvider:
    """Test OpenAIProvider functionality"""
    
    @pytest.fixture
    def openai_provider(self):
        """Create OpenAI provider with mock API key"""
        return OpenAIProvider(api_key="test-api-key")
    
    @pytest.fixture
    def sample_request(self):
        """Create sample LLM request"""
        return LLMRequest(
            session_id="test-session",
            user_id="test-user",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            model=LLMModel.GPT_3_5_TURBO
        )
    
    def test_token_counting(self, openai_provider):
        """Test token counting functionality"""
        text = "Hello, how are you today?"
        
        token_count = openai_provider._count_tokens(text)
        
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 20  # Should be reasonable for short text
    
    def test_prompt_token_estimation(self, openai_provider):
        """Test prompt token estimation"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        system_prompt = "You are a helpful assistant"
        
        token_count = openai_provider._estimate_prompt_tokens(messages, system_prompt)
        
        assert isinstance(token_count, int)
        assert token_count > 0
    
    def test_cost_calculation(self, openai_provider):
        """Test cost calculation for OpenAI"""
        usage = LLMUsage(1000, 500, 1500)  # 1K input, 500 output tokens
        
        cost = openai_provider.calculate_cost(LLMModel.GPT_3_5_TURBO, usage)
        
        assert isinstance(cost, LLMCost)
        assert cost.provider == LLMProvider.OPENAI
        assert cost.model == LLMModel.GPT_3_5_TURBO
        assert cost.usage == usage
        assert cost.total_cost > 0
        
        # GPT-4 should be more expensive than GPT-3.5
        gpt4_cost = openai_provider.calculate_cost(LLMModel.GPT_4, usage)
        assert gpt4_cost.total_cost > cost.total_cost
    
    async def test_health_check_no_api_key(self):
        """Test health check without API key"""
        provider = OpenAIProvider(api_key=None)
        
        health = await provider.health_check()
        
        assert health.component == "openai_provider"
        assert health.status == "unhealthy"
        assert "API key not configured" in health.error_message
    
    @patch('aiohttp.ClientSession.get')
    async def test_health_check_with_api_key(self, mock_get, openai_provider):
        """Test health check with API key"""
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"data": [{"id": "gpt-3.5-turbo"}]}
        mock_get.return_value.__aenter__.return_value = mock_response
        
        health = await openai_provider.health_check()
        
        assert health.component == "openai_provider"
        assert health.status == "healthy"
        assert health.error_message is None
        assert "models_available" in health.metadata


class TestLLMService:
    """Test LLMService functionality"""
    
    @pytest.fixture
    async def llm_service(self):
        """Create LLM service for testing"""
        service = LLMService(
            default_provider=LLMProvider.MOCK,
            default_model=LLMModel.MOCK_MODEL,
            cost_warning_threshold=0.50,
            cost_cutoff_threshold=1.00,
            max_retries=1
        )
        await service.initialize()
        return service
    
    @pytest.fixture
    def processed_request(self):
        """Create processed request for testing"""
        query = ConsultationQuery(
            query_id="test-query",
            user_id="test-user",
            query_text="What is the system status?",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        return ProcessedRequest(
            original_query=query,
            processed_query_text="What is the system status?",
            injected_context=None,
            context_injection_mode=MagicMock(),
            system_prompt="You are a helpful assistant",
            estimated_tokens=50,
            processing_metrics=[],
            optimization_applied=[],
            warnings=[],
            processing_time_ms=100.0
        )
    
    async def test_service_initialization(self, llm_service):
        """Test LLM service initializes correctly"""
        assert llm_service.default_provider == LLMProvider.MOCK
        assert llm_service.default_model == LLMModel.MOCK_MODEL
        assert llm_service.cost_warning_threshold == 0.50
        assert llm_service.cost_cutoff_threshold == 1.00
        assert len(llm_service.providers) >= 1  # At least mock provider
        assert LLMProvider.MOCK in llm_service.providers
        assert llm_service.stats['requests_total'] == 0
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_generate_response_success(self, mock_flags, llm_service, processed_request):
        """Test successful response generation"""
        mock_flags.is_enabled.return_value = True
        
        response = await llm_service.generate_response(processed_request)
        
        assert isinstance(response, LLMResponse)
        assert response.session_id == processed_request.original_query.session_id
        assert response.provider == LLMProvider.MOCK
        assert len(response.content) > 0
        assert response.usage.total_tokens > 0
        assert response.cost.total_cost > 0
        
        # Check statistics updated
        assert llm_service.stats['requests_total'] == 1
        assert llm_service.stats['requests_successful'] == 1
        assert llm_service.stats['total_cost'] > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_generate_response_feature_disabled(self, mock_flags, llm_service, processed_request):
        """Test response generation when feature is disabled"""
        mock_flags.is_enabled.return_value = False
        
        with pytest.raises(ProcessingError, match="LLM services are disabled"):
            await llm_service.generate_response(processed_request)
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags')
    async def test_generate_streaming_response(self, mock_flags, llm_service, processed_request):
        """Test streaming response generation"""
        mock_flags.is_enabled.return_value = True
        
        chunks = []
        final_usage = None
        final_cost = None
        
        async for content, usage, cost in llm_service.generate_streaming_response(processed_request):
            if usage and cost:
                final_usage = usage
                final_cost = cost
            else:
                chunks.append(content)
        
        # Should have received content chunks
        assert len(chunks) > 0
        
        # Should have received final usage and cost
        assert final_usage is not None
        assert final_cost is not None
        
        # Check statistics updated
        assert llm_service.stats['requests_streamed'] == 1
        assert llm_service.stats['requests_successful'] == 1
    
    async def test_cost_tracking(self, llm_service, processed_request):
        """Test cost tracking functionality"""
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            session_id = processed_request.original_query.session_id
            
            # Initial cost should be zero
            initial_cost = await llm_service.get_session_cost(session_id)
            assert initial_cost == 0.0
            
            # Generate response
            response = await llm_service.generate_response(processed_request)
            
            # Cost should be tracked
            session_cost = await llm_service.get_session_cost(session_id)
            assert session_cost == response.cost.total_cost
            assert session_cost > 0
            
            # Generate another response
            await llm_service.generate_response(processed_request)
            
            # Cost should accumulate
            new_session_cost = await llm_service.get_session_cost(session_id)
            assert new_session_cost > session_cost
    
    async def test_cost_warning_threshold(self, llm_service, processed_request):
        """Test cost warning threshold"""
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.llm_service.status_manager') as mock_status:
                mock_flags.is_enabled.return_value = True
                mock_status.update_cost_analytics = AsyncMock()
                
                session_id = processed_request.original_query.session_id
                
                # Set high session cost to trigger warning
                llm_service.session_costs[session_id] = 0.60  # Above warning threshold
                
                # Should still allow request but issue warning
                response = await llm_service.generate_response(processed_request)
                assert isinstance(response, LLMResponse)
                
                # Warning should be issued
                assert llm_service.stats['cost_warnings_issued'] >= 1
    
    async def test_cost_cutoff_threshold(self, llm_service, processed_request):
        """Test cost cutoff threshold"""
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            session_id = processed_request.original_query.session_id
            
            # Set very high session cost to trigger cutoff
            llm_service.session_costs[session_id] = 1.50  # Above cutoff threshold
            
            # Should reject request
            with pytest.raises(ProcessingError, match="Session cost limit exceeded"):
                await llm_service.generate_response(processed_request)
            
            # Cutoff should be tracked
            assert llm_service.stats['cost_cutoffs_triggered'] >= 1
    
    async def test_provider_fallback(self, llm_service, processed_request):
        """Test provider fallback mechanism"""
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            # Create a failing provider
            failing_provider = AsyncMock()
            failing_provider.generate_response.side_effect = Exception("Provider failed")
            
            # Add failing provider as preferred
            llm_service.providers[LLMProvider.OPENAI] = failing_provider
            
            # Should fallback to mock provider
            response = await llm_service.generate_response(
                processed_request, 
                provider=LLMProvider.OPENAI
            )
            
            # Should succeed with mock provider
            assert isinstance(response, LLMResponse)
            assert response.provider == LLMProvider.MOCK
    
    async def test_session_cost_reset(self, llm_service):
        """Test resetting session cost"""
        session_id = "test-session"
        
        # Set some cost
        llm_service.session_costs[session_id] = 0.50
        
        # Verify cost is set
        cost = await llm_service.get_session_cost(session_id)
        assert cost == 0.50
        
        # Reset cost
        await llm_service.reset_session_cost(session_id)
        
        # Cost should be zero
        cost = await llm_service.get_session_cost(session_id)
        assert cost == 0.0
    
    async def test_service_statistics(self, llm_service, processed_request):
        """Test service statistics"""
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            # Generate some responses
            for i in range(3):
                await llm_service.generate_response(processed_request)
            
            stats = await llm_service.get_service_stats()
            
            assert 'llm_stats' in stats
            assert 'configuration' in stats
            assert 'providers' in stats
            assert 'session_costs' in stats
            
            assert stats['llm_stats']['requests_total'] == 3
            assert stats['llm_stats']['requests_successful'] == 3
            assert stats['llm_stats']['total_cost'] > 0
            assert stats['configuration']['default_provider'] == "mock"
    
    async def test_health_status_healthy(self, llm_service):
        """Test health status when service is healthy"""
        # Generate some successful requests
        with patch('src.beast_mode.observatory.ai_consultation.llm_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            processed_request = MagicMock()
            processed_request.original_query.session_id = "test"
            processed_request.original_query.user_id = "test"
            
            for i in range(5):
                await llm_service.generate_response(processed_request)
        
        health = await llm_service.get_health_status()
        
        assert health.component == "llm_service"
        assert health.status == "healthy"
        assert health.error_message is None
        assert health.metadata['success_rate'] == 1.0
    
    async def test_health_status_degraded(self, llm_service):
        """Test health status when service is degraded"""
        # Simulate some failures
        llm_service.stats['requests_total'] = 10
        llm_service.stats['requests_successful'] = 6  # 60% success rate
        
        health = await llm_service.get_health_status()
        
        assert health.component == "llm_service"
        assert health.status == "degraded"
        assert "success rate" in health.error_message.lower()


class TestGlobalLLMService:
    """Test global LLM service functions"""
    
    @patch('src.beast_mode.observatory.ai_consultation.llm_service._llm_service', None)
    async def test_get_llm_service(self):
        """Test getting global LLM service instance"""
        service1 = await get_llm_service()
        service2 = await get_llm_service()
        
        assert service1 is service2  # Should be singleton
        assert isinstance(service1, LLMService)


if __name__ == "__main__":
    pytest.main([__file__])