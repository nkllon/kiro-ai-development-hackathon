"""
LLM Orchestrator Core - Provider Abstraction and Request Management
==================================================================

The LLM Orchestrator provides a unified interface for multiple LLM providers
with intelligent routing, load balancing, error handling, and cost tracking.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from abc import ABC, abstractmethod

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class RequestPriority(Enum):
    """Request priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class LLMRequest:
    """LLM request with metadata."""
    request_id: str
    provider: Optional[LLMProvider] = None
    prompt: str = ""
    system_prompt: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    priority: RequestPriority = RequestPriority.NORMAL
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LLMResponse:
    """LLM response with metadata."""
    request_id: str
    provider: LLMProvider
    content: str
    success: bool
    error: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    provider: LLMProvider
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 90000
    cost_per_token: float = 0.0015
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 300.0  # 5 minutes


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    async def initialize(self, config: ProviderConfig) -> bool:
        """Initialize the provider."""
        pass
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health."""
        pass
    
    @abstractmethod
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get provider usage statistics."""
        pass


class MockLLMProvider(LLMProviderInterface):
    """Mock LLM provider for testing and development."""
    
    def __init__(self):
        self.config: Optional[ProviderConfig] = None
        self.request_count = 0
        self.total_tokens = 0
        
    async def initialize(self, config: ProviderConfig) -> bool:
        """Initialize mock provider."""
        self.config = config
        logger.info(f"Mock LLM provider initialized: {config.model}")
        return True
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate mock response."""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        self.request_count += 1
        mock_tokens = min(request.max_tokens, 100)
        self.total_tokens += mock_tokens
        
        # Generate contextual mock response based on prompt
        mock_content = await self._generate_mock_content(request)
        
        return LLMResponse(
            request_id=request.request_id,
            provider=LLMProvider.MOCK,
            content=mock_content,
            success=True,
            tokens_used=mock_tokens,
            cost=mock_tokens * (self.config.cost_per_token if self.config else 0.001),
            response_time=0.1,
            metadata={"mock": True, "model": self.config.model if self.config else "mock-model"}
        )
    
    async def health_check(self) -> bool:
        """Mock health check always passes."""
        return True
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get mock usage statistics."""
        return {
            "requests": self.request_count,
            "tokens": self.total_tokens,
            "cost": self.total_tokens * (self.config.cost_per_token if self.config else 0.001),
            "uptime": 100.0
        }
    
    async def _generate_mock_content(self, request: LLMRequest) -> str:
        """Generate contextual mock content."""
        prompt_lower = request.prompt.lower()
        
        # Context-aware mock responses
        if "prioritize" in prompt_lower or "priority" in prompt_lower:
            return json.dumps({
                "priority": "high",
                "reasoning": "Based on system load and user context, this event requires immediate attention.",
                "confidence": 0.85,
                "recommendations": ["Focus user attention", "Trigger notification", "Log for analysis"]
            })
        elif "animation" in prompt_lower or "visual" in prompt_lower:
            return json.dumps({
                "animation_type": "pulse",
                "intensity": 0.7,
                "duration": 2.0,
                "reasoning": "Data velocity suggests moderate attention-grabbing animation.",
                "performance_impact": "low"
            })
        elif "personality" in prompt_lower or "mood" in prompt_lower:
            return json.dumps({
                "personality_state": "professional",
                "energy_level": 0.6,
                "transition_recommended": True,
                "reasoning": "Current system state suggests maintaining professional demeanor with moderate energy."
            })
        elif "interaction" in prompt_lower or "intent" in prompt_lower:
            return json.dumps({
                "intent": "data_exploration",
                "confidence": 0.9,
                "suggested_response": "Provide detailed drill-down options",
                "accessibility_needs": ["keyboard_navigation", "screen_reader_support"]
            })
        elif "pattern" in prompt_lower or "behavior" in prompt_lower:
            return json.dumps({
                "patterns_detected": ["frequent_dashboard_checks", "preference_for_detailed_views"],
                "user_type": "power_user",
                "optimization_opportunities": ["Preload detailed data", "Reduce animation complexity"],
                "confidence": 0.78
            })
        else:
            return json.dumps({
                "analysis": "General system analysis completed",
                "recommendations": ["Continue monitoring", "Apply standard engagement strategies"],
                "confidence": 0.75,
                "reasoning": "Standard response for general queries"
            })


class RequestRouter:
    """Routes requests to appropriate providers with load balancing."""
    
    def __init__(self):
        self.provider_stats: Dict[LLMProvider, Dict[str, Any]] = {}
        self.request_history: List[Dict[str, Any]] = []
        
    async def route_request(self, request: LLMRequest, available_providers: List[LLMProvider]) -> LLMProvider:
        """Route request to optimal provider."""
        if request.provider and request.provider in available_providers:
            return request.provider
        
        # Load balancing based on current usage
        best_provider = available_providers[0]
        lowest_load = float('inf')
        
        for provider in available_providers:
            stats = self.provider_stats.get(provider, {"active_requests": 0, "avg_response_time": 1.0})
            load_score = stats["active_requests"] * stats["avg_response_time"]
            
            if load_score < lowest_load:
                lowest_load = load_score
                best_provider = provider
        
        return best_provider
    
    async def update_provider_stats(self, provider: LLMProvider, response: LLMResponse) -> None:
        """Update provider statistics."""
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {
                "active_requests": 0,
                "total_requests": 0,
                "avg_response_time": 0.0,
                "success_rate": 1.0
            }
        
        stats = self.provider_stats[provider]
        stats["total_requests"] += 1
        stats["avg_response_time"] = (
            (stats["avg_response_time"] * (stats["total_requests"] - 1) + response.response_time) 
            / stats["total_requests"]
        )
        
        if response.success:
            stats["success_rate"] = (
                (stats["success_rate"] * (stats["total_requests"] - 1) + 1.0) 
                / stats["total_requests"]
            )
        else:
            stats["success_rate"] = (
                (stats["success_rate"] * (stats["total_requests"] - 1) + 0.0) 
                / stats["total_requests"]
            )


class CostTracker:
    """Tracks LLM usage costs and budget management."""
    
    def __init__(self):
        self.daily_costs: Dict[str, float] = {}  # date -> cost
        self.provider_costs: Dict[LLMProvider, float] = {}
        self.budget_limits: Dict[str, float] = {
            "daily": 100.0,
            "monthly": 2000.0
        }
        self.alerts_sent: Dict[str, datetime] = {}
        
    async def track_cost(self, provider: LLMProvider, cost: float) -> None:
        """Track cost for a provider."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.daily_costs[today] = self.daily_costs.get(today, 0.0) + cost
        self.provider_costs[provider] = self.provider_costs.get(provider, 0.0) + cost
        
        # Check budget limits
        await self._check_budget_limits()
    
    async def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary and analytics."""
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        
        monthly_cost = sum(
            cost for date, cost in self.daily_costs.items() 
            if date.startswith(current_month)
        )
        
        return {
            "daily_cost": self.daily_costs.get(today, 0.0),
            "monthly_cost": monthly_cost,
            "provider_breakdown": dict(self.provider_costs),
            "budget_utilization": {
                "daily": (self.daily_costs.get(today, 0.0) / self.budget_limits["daily"]) * 100,
                "monthly": (monthly_cost / self.budget_limits["monthly"]) * 100
            },
            "projected_monthly": monthly_cost * (30 / datetime.now().day) if datetime.now().day > 0 else 0
        }
    
    async def _check_budget_limits(self) -> None:
        """Check if budget limits are exceeded."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_cost = self.daily_costs.get(today, 0.0)
        
        if daily_cost > self.budget_limits["daily"] * 0.8:  # 80% threshold
            alert_key = f"daily_{today}"
            if alert_key not in self.alerts_sent or (
                datetime.now() - self.alerts_sent[alert_key]
            ).total_seconds() > 3600:  # 1 hour cooldown
                logger.warning(f"Daily LLM budget at {(daily_cost/self.budget_limits['daily'])*100:.1f}%")
                self.alerts_sent[alert_key] = datetime.now()


class LLMOrchestrator(ReflectiveModule):
    """
    Main LLM Orchestrator that provides unified interface for multiple LLM providers
    with intelligent routing, load balancing, error handling, and cost tracking.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "llm_orchestrator"
        
        # Core components
        self.providers: Dict[LLMProvider, LLMProviderInterface] = {}
        self.provider_configs: Dict[LLMProvider, ProviderConfig] = {}
        self.router = RequestRouter()
        self.cost_tracker = CostTracker()
        
        # State management
        self.is_initialized = False
        self.active_requests: Dict[str, LLMRequest] = {}
        self.request_queue: List[LLMRequest] = []
        
        logger.info("LLM Orchestrator initialized")
    
    async def initialize(self, configs: Dict[LLMProvider, ProviderConfig]) -> bool:
        """Initialize the LLM Orchestrator with provider configurations."""
        try:
            self.provider_configs = configs
            
            # Initialize providers
            for provider_type, config in configs.items():
                if config.enabled:
                    provider = await self._create_provider(provider_type)
                    if await provider.initialize(config):
                        self.providers[provider_type] = provider
                        logger.info(f"LLM provider initialized: {provider_type.value}")
                    else:
                        logger.error(f"Failed to initialize LLM provider: {provider_type.value}")
            
            if not self.providers:
                logger.error("No LLM providers successfully initialized")
                return False
            
            self.is_initialized = True
            logger.info(f"LLM Orchestrator initialization complete with {len(self.providers)} providers")
            return True
            
        except Exception as e:
            logger.error(f"LLM Orchestrator initialization failed: {e}")
            return False
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using optimal provider."""
        try:
            if not self.is_initialized:
                return LLMResponse(
                    request_id=request.request_id,
                    provider=LLMProvider.MOCK,
                    content="",
                    success=False,
                    error="LLM Orchestrator not initialized"
                )
            
            # Add to active requests
            self.active_requests[request.request_id] = request
            
            # Route to optimal provider
            available_providers = list(self.providers.keys())
            if not available_providers:
                return LLMResponse(
                    request_id=request.request_id,
                    provider=LLMProvider.MOCK,
                    content="",
                    success=False,
                    error="No providers available"
                )
            
            selected_provider = await self.router.route_request(request, available_providers)
            provider = self.providers[selected_provider]
            
            # Generate response with retry logic
            response = await self._generate_with_retry(provider, request, selected_provider)
            
            # Update statistics and costs
            await self.router.update_provider_stats(selected_provider, response)
            if response.success:
                await self.cost_tracker.track_cost(selected_provider, response.cost)
            
            # Remove from active requests
            self.active_requests.pop(request.request_id, None)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            self.active_requests.pop(request.request_id, None)
            return LLMResponse(
                request_id=request.request_id,
                provider=LLMProvider.MOCK,
                content="",
                success=False,
                error=str(e)
            )
    
    async def batch_generate(self, requests: List[LLMRequest]) -> List[LLMResponse]:
        """Generate responses for multiple requests in parallel."""
        tasks = [self.generate(request) for request in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append(LLMResponse(
                    request_id=requests[i].request_id,
                    provider=LLMProvider.MOCK,
                    content="",
                    success=False,
                    error=str(response)
                ))
            else:
                results.append(response)
        
        return results
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status."""
        try:
            provider_status = {}
            for provider_type, provider in self.providers.items():
                health = await provider.health_check()
                stats = await provider.get_usage_stats()
                provider_status[provider_type.value] = {
                    "healthy": health,
                    "stats": stats,
                    "config": {
                        "model": self.provider_configs[provider_type].model,
                        "enabled": self.provider_configs[provider_type].enabled
                    }
                }
            
            cost_summary = await self.cost_tracker.get_cost_summary()
            
            return {
                "initialized": self.is_initialized,
                "active_requests": len(self.active_requests),
                "queued_requests": len(self.request_queue),
                "providers": provider_status,
                "costs": cost_summary,
                "router_stats": self.router.provider_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get orchestrator status: {e}")
            return {"error": str(e)}
    
    async def _create_provider(self, provider_type: LLMProvider) -> LLMProviderInterface:
        """Create provider instance based on type."""
        if provider_type == LLMProvider.MOCK:
            return MockLLMProvider()
        elif provider_type == LLMProvider.OPENAI:
            # TODO: Implement OpenAI provider
            logger.warning("OpenAI provider not implemented, using mock")
            return MockLLMProvider()
        elif provider_type == LLMProvider.ANTHROPIC:
            # TODO: Implement Anthropic provider
            logger.warning("Anthropic provider not implemented, using mock")
            return MockLLMProvider()
        elif provider_type == LLMProvider.LOCAL:
            # TODO: Implement local model provider
            logger.warning("Local provider not implemented, using mock")
            return MockLLMProvider()
        else:
            return MockLLMProvider()
    
    async def _generate_with_retry(
        self, 
        provider: LLMProviderInterface, 
        request: LLMRequest, 
        provider_type: LLMProvider
    ) -> LLMResponse:
        """Generate response with retry logic."""
        config = self.provider_configs[provider_type]
        last_error = None
        
        for attempt in range(config.retry_attempts):
            try:
                start_time = datetime.now()
                response = await asyncio.wait_for(
                    provider.generate(request), 
                    timeout=config.timeout
                )
                response.response_time = (datetime.now() - start_time).total_seconds()
                
                if response.success:
                    return response
                else:
                    last_error = response.error
                    
            except asyncio.TimeoutError:
                last_error = f"Request timeout after {config.timeout}s"
            except Exception as e:
                last_error = str(e)
            
            if attempt < config.retry_attempts - 1:
                await asyncio.sleep(config.retry_delay * (2 ** attempt))  # Exponential backoff
        
        return LLMResponse(
            request_id=request.request_id,
            provider=provider_type,
            content="",
            success=False,
            error=f"Failed after {config.retry_attempts} attempts: {last_error}"
        )
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get LLM Orchestrator capabilities."""
        return [
            "multi_provider_support",
            "intelligent_routing",
            "load_balancing",
            "cost_tracking",
            "error_handling",
            "batch_processing"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get LLM Orchestrator health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "providers": len(self.providers),
            "active_requests": len(self.active_requests),
            "queued_requests": len(self.request_queue)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get LLM Orchestrator module information."""
        return {
            "module_id": self.module_id,
            "name": "LLM Orchestrator",
            "version": "1.0.0",
            "description": "Unified interface for multiple LLM providers with intelligent routing and cost tracking"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation to basic functionality."""
        try:
            degradation_actions = []
            
            # Cancel queued requests
            if self.request_queue:
                cleared_queue = len(self.request_queue)
                self.request_queue.clear()
                degradation_actions.append(f"Cleared {cleared_queue} queued requests")
            
            # Switch to mock provider only
            if len(self.providers) > 1:
                mock_provider = None
                for provider_type, provider in self.providers.items():
                    if provider_type == LLMProvider.MOCK:
                        mock_provider = provider
                        break
                
                if mock_provider:
                    self.providers = {LLMProvider.MOCK: mock_provider}
                    degradation_actions.append("Switched to mock provider only")
                else:
                    # Create emergency mock provider
                    mock = MockLLMProvider()
                    # Note: Initialize synchronously in degradation mode
                    mock.config = ProviderConfig(provider=LLMProvider.MOCK)
                    self.providers = {LLMProvider.MOCK: mock}
                    degradation_actions.append("Created emergency mock provider")
            
            # Reset cost tracking to prevent budget issues
            self.cost_tracker = CostTracker()
            degradation_actions.append("Reset cost tracking")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "active_providers": len(self.providers),
                "functionality_level": "mock_responses_only",
                "recovery_possible": True
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }