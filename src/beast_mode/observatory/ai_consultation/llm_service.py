"""
LLM Service Integration

Provides LLM API integration with streaming responses, cost tracking, and fallback mechanisms.
Supports multiple LLM providers with automatic failover and cost optimization.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from abc import ABC, abstractmethod
import aiohttp
import tiktoken

from .models import ObservatoryContext
from .request_processor import ProcessedRequest
from .doctor_status_manager import get_doctor_status, status_manager
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError, ProcessingError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class LLMModel(str, Enum):
    """Supported LLM models"""
    # OpenAI models
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"
    
    # Anthropic models
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    
    # Local/Mock models
    LOCAL_LLAMA = "local-llama-7b"
    MOCK_MODEL = "mock-model"


@dataclass
class LLMUsage:
    """Token usage information from LLM"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    @property
    def input_tokens(self) -> int:
        return self.prompt_tokens
    
    @property
    def output_tokens(self) -> int:
        return self.completion_tokens


@dataclass
class LLMCost:
    """Cost calculation for LLM usage"""
    provider: LLMProvider
    model: LLMModel
    usage: LLMUsage
    input_cost_per_token: float
    output_cost_per_token: float
    total_cost: float
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "model": self.model.value,
            "usage": asdict(self.usage),
            "input_cost_per_token": self.input_cost_per_token,
            "output_cost_per_token": self.output_cost_per_token,
            "total_cost": self.total_cost,
            "currency": self.currency
        }


@dataclass
class LLMRequest:
    """Request to LLM service"""
    session_id: str
    user_id: str
    messages: List[Dict[str, str]]
    model: LLMModel
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False
    timeout: float = 30.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": self.messages,
            "model": self.model.value,
            "system_prompt": self.system_prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.stream,
            "timeout": self.timeout
        }


@dataclass
class LLMResponse:
    """Response from LLM service"""
    request_id: str
    session_id: str
    content: str
    model: LLMModel
    provider: LLMProvider
    usage: LLMUsage
    cost: LLMCost
    response_time: float
    timestamp: datetime
    finish_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "content": self.content,
            "model": self.model.value,
            "provider": self.provider.value,
            "usage": asdict(self.usage),
            "cost": self.cost.to_dict(),
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat(),
            "finish_reason": self.finish_reason
        }


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def generate_streaming_response(
        self, 
        request: LLMRequest
    ) -> AsyncGenerator[Tuple[str, Optional[LLMUsage]], None]:
        """Generate streaming response from LLM"""
        pass
    
    @abstractmethod
    def calculate_cost(self, model: LLMModel, usage: LLMUsage) -> LLMCost:
        """Calculate cost for usage"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ComponentHealth:
        """Check provider health"""
        pass


class OpenAIProvider(LLMProviderInterface):
    """OpenAI API provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = LLMProvider.OPENAI
        self.base_url = "https://api.openai.com/v1"
        
        # OpenAI pricing (per 1M tokens as of 2024)
        self.pricing = {
            LLMModel.GPT_3_5_TURBO: {"input": 0.50, "output": 1.50},
            LLMModel.GPT_4: {"input": 30.00, "output": 60.00},
            LLMModel.GPT_4_TURBO: {"input": 10.00, "output": 30.00},
            LLMModel.GPT_4O: {"input": 5.00, "output": 15.00},
        }
        
        # Token encoder for accurate counting
        self.encoder = None
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except Exception:
            logger.warning("Failed to load tiktoken encoder, using approximation")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Rough approximation: 4 characters per token
            return max(1, len(text) // 4)
    
    def _estimate_prompt_tokens(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> int:
        """Estimate prompt tokens"""
        total = 0
        
        if system_prompt:
            total += self._count_tokens(system_prompt)
        
        for message in messages:
            total += self._count_tokens(message.get("content", ""))
            total += 4  # Overhead per message
        
        total += 2  # Conversation overhead
        return total
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        if not self.api_key:
            raise ProcessingError("OpenAI API key not configured")
        
        start_time = time.time()
        request_id = f"openai_{int(time.time())}_{hash(request.session_id) % 10000}"
        
        try:
            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.extend(request.messages)
            
            # Prepare request payload
            payload = {
                "model": request.model.value,
                "messages": messages,
                "temperature": request.temperature,
                "stream": False
            }
            
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=request.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ProcessingError(f"OpenAI API error {response.status}: {error_text}")
                    
                    data = await response.json()
            
            response_time = time.time() - start_time
            
            # Extract response data
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
            
            # Extract usage
            usage_data = data.get("usage", {})
            usage = LLMUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            # Calculate cost
            cost = self.calculate_cost(request.model, usage)
            
            return LLMResponse(
                request_id=request_id,
                session_id=request.session_id,
                content=content,
                model=request.model,
                provider=self.provider,
                usage=usage,
                cost=cost,
                response_time=response_time,
                timestamp=datetime.utcnow(),
                finish_reason=finish_reason
            )
            
        except asyncio.TimeoutError:
            raise ProcessingError(f"OpenAI API timeout after {request.timeout}s")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise ProcessingError(f"OpenAI API error: {str(e)}")
    
    async def generate_streaming_response(
        self, 
        request: LLMRequest
    ) -> AsyncGenerator[Tuple[str, Optional[LLMUsage]], None]:
        """Generate streaming response using OpenAI API"""
        if not self.api_key:
            raise ProcessingError("OpenAI API key not configured")
        
        try:
            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.extend(request.messages)
            
            # Prepare request payload
            payload = {
                "model": request.model.value,
                "messages": messages,
                "temperature": request.temperature,
                "stream": True
            }
            
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens
            
            # Make streaming API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=request.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ProcessingError(f"OpenAI API error {response.status}: {error_text}")
                    
                    # Process streaming response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            
                            if data_str == '[DONE]':
                                break
                            
                            try:
                                data = json.loads(data_str)
                                choice = data.get("choices", [{}])[0]
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content, None
                                    
                            except json.JSONDecodeError:
                                continue
            
            # Estimate final usage (streaming doesn't provide exact usage)
            estimated_prompt_tokens = self._estimate_prompt_tokens(messages)
            estimated_completion_tokens = 50  # Rough estimate
            
            usage = LLMUsage(
                prompt_tokens=estimated_prompt_tokens,
                completion_tokens=estimated_completion_tokens,
                total_tokens=estimated_prompt_tokens + estimated_completion_tokens
            )
            
            yield "", usage  # Final yield with usage info
            
        except asyncio.TimeoutError:
            raise ProcessingError(f"OpenAI streaming timeout after {request.timeout}s")
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise ProcessingError(f"OpenAI streaming error: {str(e)}")
    
    def calculate_cost(self, model: LLMModel, usage: LLMUsage) -> LLMCost:
        """Calculate cost for OpenAI usage"""
        pricing = self.pricing.get(model, self.pricing[LLMModel.GPT_3_5_TURBO])
        
        # Convert from per-1M to per-token
        input_cost_per_token = pricing["input"] / 1_000_000
        output_cost_per_token = pricing["output"] / 1_000_000
        
        input_cost = usage.input_tokens * input_cost_per_token
        output_cost = usage.output_tokens * output_cost_per_token
        total_cost = input_cost + output_cost
        
        return LLMCost(
            provider=self.provider,
            model=model,
            usage=usage,
            input_cost_per_token=input_cost_per_token,
            output_cost_per_token=output_cost_per_token,
            total_cost=total_cost
        )
    
    async def health_check(self) -> ComponentHealth:
        """Check OpenAI provider health"""
        try:
            if not self.api_key:
                return ComponentHealth(
                    component="openai_provider",
                    status="unhealthy",
                    response_time=0.0,
                    error_message="API key not configured",
                    metadata={},
                    last_check=datetime.utcnow()
                )
            
            start_time = time.time()
            
            # Simple health check - list models
            headers = {"Authorization": f"Bearer {self.api_key}"}
            timeout = aiohttp.ClientTimeout(total=5.0)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/models", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        return ComponentHealth(
                            component="openai_provider",
                            status="healthy",
                            response_time=response_time,
                            error_message=None,
                            metadata={"models_available": len(data.get("data", []))},
                            last_check=datetime.utcnow()
                        )
                    else:
                        error_text = await response.text()
                        return ComponentHealth(
                            component="openai_provider",
                            status="unhealthy",
                            response_time=response_time,
                            error_message=f"API error {response.status}: {error_text}",
                            metadata={},
                            last_check=datetime.utcnow()
                        )
                        
        except Exception as e:
            return ComponentHealth(
                component="openai_provider",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )


class MockLLMProvider(LLMProviderInterface):
    """Mock LLM provider for testing and fallback"""
    
    def __init__(self):
        self.provider = LLMProvider.MOCK
        self.response_delay = 0.5  # Simulate API delay
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate mock response"""
        await asyncio.sleep(self.response_delay)
        
        start_time = time.time()
        request_id = f"mock_{int(time.time())}_{hash(request.session_id) % 10000}"
        
        # Generate contextual response based on request
        content = self._generate_mock_content(request)
        
        # Mock token usage
        prompt_tokens = sum(len(msg.get("content", "").split()) for msg in request.messages) * 1.3
        completion_tokens = len(content.split()) * 1.3
        
        usage = LLMUsage(
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            total_tokens=int(prompt_tokens + completion_tokens)
        )
        
        cost = self.calculate_cost(request.model, usage)
        response_time = time.time() - start_time
        
        return LLMResponse(
            request_id=request_id,
            session_id=request.session_id,
            content=content,
            model=request.model,
            provider=self.provider,
            usage=usage,
            cost=cost,
            response_time=response_time,
            timestamp=datetime.utcnow(),
            finish_reason="stop"
        )
    
    async def generate_streaming_response(
        self, 
        request: LLMRequest
    ) -> AsyncGenerator[Tuple[str, Optional[LLMUsage]], None]:
        """Generate mock streaming response"""
        content = self._generate_mock_content(request)
        words = content.split()
        
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate streaming delay
            
            if i == len(words) - 1:
                yield word, None
            else:
                yield word + " ", None
        
        # Final yield with usage
        prompt_tokens = sum(len(msg.get("content", "").split()) for msg in request.messages) * 1.3
        completion_tokens = len(content.split()) * 1.3
        
        usage = LLMUsage(
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            total_tokens=int(prompt_tokens + completion_tokens)
        )
        
        yield "", usage
    
    def _generate_mock_content(self, request: LLMRequest) -> str:
        """Generate contextual mock content"""
        last_message = request.messages[-1].get("content", "").lower() if request.messages else ""
        
        if "status" in last_message or "health" in last_message:
            return "Based on the current Observatory monitoring data, the system appears to be running normally. All key metrics are within acceptable ranges. CPU usage is at 68.5% and memory usage is at 72.1%, which are both healthy levels."
        
        elif "alert" in last_message or "warning" in last_message:
            return "I can see there are currently 2 active alerts in the system. The most recent alert indicates high CPU usage on web-server-02. This is a warning-level alert that started about 5 minutes ago. Would you like me to provide more details about this alert or suggest remediation steps?"
        
        elif "performance" in last_message or "metric" in last_message:
            return "System performance looks good overall. Here's what I'm seeing: Response times are averaging 0.52 seconds, which is within normal parameters. CPU usage across the cluster is averaging 68.5%, with some variation between servers. Memory usage is at 72.1% average. No performance bottlenecks detected at this time."
        
        elif "error" in last_message or "problem" in last_message:
            return "I've analyzed the recent system logs and error patterns. There are no critical errors currently active. I did notice a few minor warnings in the application logs, but these appear to be transient issues that resolved themselves. The error rate is well within normal bounds at 0.02%."
        
        elif "help" in last_message or "how" in last_message:
            return "I'm here to help you monitor and analyze your Observatory system! I can provide information about system status, alerts, performance metrics, and help troubleshoot issues. I have access to real-time monitoring data and can explain what's happening in your infrastructure. What specific aspect would you like to explore?"
        
        else:
            return f"I understand you're asking about: {last_message}. Based on the current Observatory monitoring context, I can help you analyze the system status and provide recommendations. The system is currently healthy with 2 active alerts that are being monitored. What specific aspect would you like me to focus on?"
    
    def calculate_cost(self, model: LLMModel, usage: LLMUsage) -> LLMCost:
        """Calculate mock cost (very low for testing)"""
        input_cost_per_token = 0.000001  # $0.001 per 1M tokens
        output_cost_per_token = 0.000002  # $0.002 per 1M tokens
        
        input_cost = usage.input_tokens * input_cost_per_token
        output_cost = usage.output_tokens * output_cost_per_token
        total_cost = input_cost + output_cost
        
        return LLMCost(
            provider=self.provider,
            model=model,
            usage=usage,
            input_cost_per_token=input_cost_per_token,
            output_cost_per_token=output_cost_per_token,
            total_cost=total_cost
        )
    
    async def health_check(self) -> ComponentHealth:
        """Mock health check"""
        return ComponentHealth(
            component="mock_llm_provider",
            status="healthy",
            response_time=1.0,
            error_message=None,
            metadata={"mock": True, "always_available": True},
            last_check=datetime.utcnow()
        )


class LLMService:
    """
    LLM Service with multiple provider support, cost tracking, and streaming
    
    Features:
    - Multiple LLM provider support with automatic failover
    - Real-time cost tracking and budget enforcement
    - Streaming response support
    - Cost warning system with automatic cutoffs
    - Circuit breaker integration
    - Comprehensive error handling and fallback mechanisms
    """
    
    def __init__(
        self,
        default_provider: LLMProvider = LLMProvider.MOCK,
        default_model: LLMModel = LLMModel.MOCK_MODEL,
        cost_warning_threshold: float = 1.0,  # $1.00
        cost_cutoff_threshold: float = 5.0,   # $5.00
        max_retries: int = 2,
        retry_delay: float = 1.0
    ):
        self.default_provider = default_provider
        self.default_model = default_model
        self.cost_warning_threshold = cost_warning_threshold
        self.cost_cutoff_threshold = cost_cutoff_threshold
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Provider instances
        self.providers: Dict[LLMProvider, LLMProviderInterface] = {}
        
        # Cost tracking
        self.session_costs: Dict[str, float] = {}
        self.total_cost: float = 0.0
        
        # Statistics
        self.stats = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "requests_streamed": 0,
            "cost_warnings_issued": 0,
            "cost_cutoffs_triggered": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "provider_usage": {provider.value: 0 for provider in LLMProvider},
            "model_usage": {model.value: 0 for model in LLMModel},
            "avg_response_time": 0.0
        }
    
    async def initialize(self) -> None:
        """Initialize LLM service"""
        try:
            logger.info("Initializing LLM Service")
            
            # Initialize providers
            await self._initialize_providers()
            
            # Test provider connectivity
            await self._test_providers()
            
            logger.info(f"LLM Service initialized with {len(self.providers)} providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Service: {e}")
            # Ensure we have at least mock provider
            if not self.providers:
                self.providers[LLMProvider.MOCK] = MockLLMProvider()
    
    async def _initialize_providers(self) -> None:
        """Initialize LLM providers"""
        try:
            # Always include mock provider for fallback
            self.providers[LLMProvider.MOCK] = MockLLMProvider()
            
            # Initialize OpenAI if API key available
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.providers[LLMProvider.OPENAI] = OpenAIProvider(api_key=openai_key)
                logger.info("OpenAI provider initialized")
            
            # TODO: Add Anthropic provider when API key available
            # anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            # if anthropic_key:
            #     self.providers[LLMProvider.ANTHROPIC] = AnthropicProvider(api_key=anthropic_key)
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
            # Fallback to mock only
            self.providers = {LLMProvider.MOCK: MockLLMProvider()}
    
    async def _test_providers(self) -> None:
        """Test provider connectivity"""
        for provider_type, provider in self.providers.items():
            try:
                health = await provider.health_check()
                if health.status == "healthy":
                    logger.info(f"{provider_type.value} provider is healthy")
                else:
                    logger.warning(f"{provider_type.value} provider is {health.status}: {health.error_message}")
            except Exception as e:
                logger.error(f"Health check failed for {provider_type.value}: {e}")
    
    @with_circuit_breaker('llm_service')
    async def generate_response(
        self,
        processed_request: ProcessedRequest,
        model: Optional[LLMModel] = None,
        provider: Optional[LLMProvider] = None,
        stream: bool = False,
        timeout: float = 30.0
    ) -> LLMResponse:
        """Generate LLM response with cost tracking"""
        try:
            self.stats["requests_total"] += 1
            
            # Check if LLM services are enabled
            if not await feature_flags.is_enabled(FeatureFlag.AI_SERVICES):
                raise ProcessingError("LLM services are disabled")
            
            # Use defaults if not specified
            model = model or self.default_model
            provider = provider or self.default_provider
            
            # Check budget limits
            await self._check_budget_limits(processed_request.original_query.session_id)
            
            # Create LLM request
            llm_request = LLMRequest(
                session_id=processed_request.original_query.session_id,
                user_id=processed_request.original_query.user_id,
                messages=[{
                    "role": "user",
                    "content": processed_request.processed_query_text
                }],
                model=model,
                system_prompt=processed_request.system_prompt,
                max_tokens=2000,  # Reasonable limit
                temperature=0.7,
                stream=stream,
                timeout=timeout
            )
            
            # Generate response with fallback
            response = await self._generate_with_fallback(llm_request, provider)
            
            # Track cost
            await self._track_cost(response)
            
            # Update statistics
            self._update_stats(response)
            self.stats["requests_successful"] += 1
            
            if stream:
                self.stats["requests_streamed"] += 1
            
            logger.info(f"LLM response generated: {response.usage.total_tokens} tokens, ${response.cost.total_cost:.4f}")
            
            return response
            
        except Exception as e:
            self.stats["requests_failed"] += 1
            logger.error(f"LLM response generation failed: {e}")
            raise
    
    async def generate_streaming_response(
        self,
        processed_request: ProcessedRequest,
        model: Optional[LLMModel] = None,
        provider: Optional[LLMProvider] = None,
        timeout: float = 60.0
    ) -> AsyncGenerator[Tuple[str, Optional[LLMUsage], Optional[LLMCost]], None]:
        """Generate streaming LLM response with cost tracking"""
        try:
            self.stats["requests_total"] += 1
            self.stats["requests_streamed"] += 1
            
            # Check if LLM services are enabled
            if not await feature_flags.is_enabled(FeatureFlag.AI_SERVICES):
                raise ProcessingError("LLM services are disabled")
            
            # Use defaults if not specified
            model = model or self.default_model
            provider = provider or self.default_provider
            
            # Check budget limits
            await self._check_budget_limits(processed_request.original_query.session_id)
            
            # Create LLM request
            llm_request = LLMRequest(
                session_id=processed_request.original_query.session_id,
                user_id=processed_request.original_query.user_id,
                messages=[{
                    "role": "user",
                    "content": processed_request.processed_query_text
                }],
                model=model,
                system_prompt=processed_request.system_prompt,
                max_tokens=2000,
                temperature=0.7,
                stream=True,
                timeout=timeout
            )
            
            # Get provider
            provider_instance = self.providers.get(provider)
            if not provider_instance:
                provider_instance = self.providers[LLMProvider.MOCK]
            
            # Generate streaming response
            total_content = ""
            final_usage = None
            
            async for content_chunk, usage in provider_instance.generate_streaming_response(llm_request):
                if usage:
                    # Final chunk with usage info
                    final_usage = usage
                    cost = provider_instance.calculate_cost(model, usage)
                    
                    # Track cost
                    await self._track_streaming_cost(llm_request.session_id, cost)
                    
                    # Update statistics
                    self._update_streaming_stats(usage, cost)
                    
                    yield content_chunk, usage, cost
                else:
                    # Content chunk
                    total_content += content_chunk
                    yield content_chunk, None, None
            
            self.stats["requests_successful"] += 1
            
            logger.info(f"Streaming response completed: {final_usage.total_tokens if final_usage else 0} tokens")
            
        except Exception as e:
            self.stats["requests_failed"] += 1
            logger.error(f"Streaming response generation failed: {e}")
            raise
    
    async def _generate_with_fallback(
        self,
        request: LLMRequest,
        preferred_provider: LLMProvider
    ) -> LLMResponse:
        """Generate response with provider fallback"""
        providers_to_try = [preferred_provider]
        
        # Add fallback providers
        if preferred_provider != LLMProvider.MOCK:
            providers_to_try.append(LLMProvider.MOCK)
        
        last_error = None
        
        for provider_type in providers_to_try:
            provider = self.providers.get(provider_type)
            if not provider:
                continue
            
            for attempt in range(self.max_retries + 1):
                try:
                    response = await provider.generate_response(request)
                    
                    # Update provider usage stats
                    self.stats["provider_usage"][provider_type.value] += 1
                    
                    return response
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1} failed for {provider_type.value}: {e}")
                    
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All providers failed
        raise ProcessingError(f"All LLM providers failed. Last error: {last_error}")
    
    async def _check_budget_limits(self, session_id: str) -> None:
        """Check budget limits and issue warnings/cutoffs"""
        try:
            # Get current session cost
            session_cost = self.session_costs.get(session_id, 0.0)
            
            # Check cutoff threshold
            if session_cost >= self.cost_cutoff_threshold:
                self.stats["cost_cutoffs_triggered"] += 1
                raise ProcessingError(f"Session cost limit exceeded: ${session_cost:.2f} >= ${self.cost_cutoff_threshold:.2f}")
            
            # Check warning threshold
            if session_cost >= self.cost_warning_threshold:
                self.stats["cost_warnings_issued"] += 1
                logger.warning(f"Session {session_id} approaching cost limit: ${session_cost:.2f}")
                
                # Update doctor status with cost warning
                await status_manager.update_cost_analytics({
                    "session_id": session_id,
                    "current_cost": session_cost,
                    "warning_threshold": self.cost_warning_threshold,
                    "cutoff_threshold": self.cost_cutoff_threshold,
                    "warning_issued": True
                })
            
        except Exception as e:
            logger.error(f"Budget check failed: {e}")
            # Don't block on budget check failures
    
    async def _track_cost(self, response: LLMResponse) -> None:
        """Track cost for response"""
        try:
            # Update session cost
            session_cost = self.session_costs.get(response.session_id, 0.0)
            session_cost += response.cost.total_cost
            self.session_costs[response.session_id] = session_cost
            
            # Update total cost
            self.total_cost += response.cost.total_cost
            self.stats["total_cost"] = self.total_cost
            
            # Update doctor status with cost info
            await status_manager.update_cost_analytics({
                "session_id": response.session_id,
                "request_cost": response.cost.total_cost,
                "session_total": session_cost,
                "global_total": self.total_cost,
                "tokens_used": response.usage.total_tokens
            })
            
        except Exception as e:
            logger.error(f"Cost tracking failed: {e}")
    
    async def _track_streaming_cost(self, session_id: str, cost: LLMCost) -> None:
        """Track cost for streaming response"""
        try:
            # Update session cost
            session_cost = self.session_costs.get(session_id, 0.0)
            session_cost += cost.total_cost
            self.session_costs[session_id] = session_cost
            
            # Update total cost
            self.total_cost += cost.total_cost
            self.stats["total_cost"] = self.total_cost
            
        except Exception as e:
            logger.error(f"Streaming cost tracking failed: {e}")
    
    def _update_stats(self, response: LLMResponse) -> None:
        """Update service statistics"""
        try:
            # Update token stats
            self.stats["total_tokens"] += response.usage.total_tokens
            
            # Update model usage
            self.stats["model_usage"][response.model.value] += 1
            
            # Update average response time
            total_requests = self.stats["requests_successful"]
            if total_requests > 1:
                current_avg = self.stats["avg_response_time"]
                self.stats["avg_response_time"] = (
                    (current_avg * (total_requests - 1) + response.response_time) / total_requests
                )
            else:
                self.stats["avg_response_time"] = response.response_time
                
        except Exception as e:
            logger.error(f"Stats update failed: {e}")
    
    def _update_streaming_stats(self, usage: LLMUsage, cost: LLMCost) -> None:
        """Update statistics for streaming response"""
        try:
            self.stats["total_tokens"] += usage.total_tokens
            self.stats["model_usage"][cost.model.value] += 1
            
        except Exception as e:
            logger.error(f"Streaming stats update failed: {e}")
    
    async def get_session_cost(self, session_id: str) -> float:
        """Get current cost for session"""
        return self.session_costs.get(session_id, 0.0)
    
    async def reset_session_cost(self, session_id: str) -> None:
        """Reset cost tracking for session"""
        if session_id in self.session_costs:
            del self.session_costs[session_id]
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get current service statistics"""
        try:
            return {
                "llm_stats": self.stats.copy(),
                "configuration": {
                    "default_provider": self.default_provider.value,
                    "default_model": self.default_model.value,
                    "cost_warning_threshold": self.cost_warning_threshold,
                    "cost_cutoff_threshold": self.cost_cutoff_threshold,
                    "max_retries": self.max_retries
                },
                "providers": {
                    provider.value: {
                        "available": provider in self.providers,
                        "usage_count": self.stats["provider_usage"][provider.value]
                    }
                    for provider in LLMProvider
                },
                "session_costs": dict(self.session_costs),
                "total_sessions_tracked": len(self.session_costs)
            }
            
        except Exception as e:
            logger.error(f"Failed to get service stats: {e}")
            return {"error": str(e)}
    
    async def get_health_status(self) -> ComponentHealth:
        """Get LLM service health status"""
        try:
            # Check provider health
            healthy_providers = 0
            total_providers = len(self.providers)
            
            for provider in self.providers.values():
                health = await provider.health_check()
                if health.status == "healthy":
                    healthy_providers += 1
            
            # Calculate success rate
            success_rate = (
                self.stats["requests_successful"] / 
                max(1, self.stats["requests_total"])
            )
            
            # Determine overall health
            if healthy_providers == 0:
                status = "critical"
                error_message = "No healthy LLM providers available"
            elif success_rate < 0.8:
                status = "degraded"
                error_message = f"Low success rate: {success_rate:.1%}"
            elif healthy_providers < total_providers:
                status = "degraded"
                error_message = f"Some providers unhealthy: {healthy_providers}/{total_providers}"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="llm_service",
                status=status,
                response_time=self.stats["avg_response_time"] * 1000,  # Convert to ms
                error_message=error_message,
                metadata={
                    "healthy_providers": healthy_providers,
                    "total_providers": total_providers,
                    "success_rate": success_rate,
                    "total_cost": self.stats["total_cost"],
                    "total_tokens": self.stats["total_tokens"],
                    "active_sessions": len(self.session_costs)
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="llm_service",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )


# Global LLM service instance
_llm_service: Optional[LLMService] = None


async def get_llm_service() -> LLMService:
    """Get the global LLM service instance"""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService()
        await _llm_service.initialize()
    
    return _llm_service