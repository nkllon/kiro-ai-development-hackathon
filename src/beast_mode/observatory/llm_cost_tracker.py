"""
LLM Cost Tracker - Multi-provider API monitoring and cost tracking system.

This module provides real-time LLM API call monitoring, token counting, cost calculation,
and anomaly detection across multiple providers (OpenAI, Anthropic, etc.).
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

import redis.asyncio as redis

from ..core import ReflectiveModule
from .models import LLMMetrics, CostMetrics, CostAnomaly, CostTrend
from .config import ObservatoryConfig


logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    AZURE_OPENAI = "azure_openai"


@dataclass
class LLMPricing:
    """Pricing information for an LLM model."""
    provider: LLMProvider
    model: str
    input_cost_per_1k_tokens: Decimal
    output_cost_per_1k_tokens: Decimal
    context_window: int = 4096
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class LLMAPICall:
    """Record of an LLM API call with cost information."""
    call_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-3.5-turbo"
    operation_type: str = "completion"
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    response_time_ms: float = 0.0
    success: bool = True
    error_type: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None


class LLMCostTracker(ReflectiveModule):
    """
    Tracks LLM API calls, costs, and usage patterns across multiple providers.
    
    Features:
    - Real-time cost calculation and tracking
    - Multi-provider support (OpenAI, Anthropic, etc.)
    - Cost anomaly detection
    - Usage pattern analysis
    - Cost projection and budgeting
    """
    
    def __init__(self, config: ObservatoryConfig):
        super().__init__()
        self.module_id = "llm_cost_tracker"
        self._config = config
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        
        # Cost tracking data
        self._api_calls: List[LLMAPICall] = []
        self._daily_costs: Dict[str, Decimal] = {}  # date -> cost
        self._provider_costs: Dict[LLMProvider, Decimal] = {}
        self._model_costs: Dict[str, Decimal] = {}
        
        # Pricing database
        self._pricing_db = self._initialize_pricing_database()
        
        # Performance tracking
        self._start_time = time.time()
        self._calls_tracked = 0
        self._anomalies_detected = 0
        
        # Cost thresholds and alerts
        self._cost_thresholds = self._config.cost_config.cost_alert_thresholds
        
        logger.info("💰 LLMCostTracker initialized - Ready to track multi-provider costs")
    
    def _initialize_pricing_database(self) -> Dict[str, LLMPricing]:
        """Initialize the LLM pricing database with current rates."""
        pricing_db = {}
        
        # OpenAI pricing (as of 2024)
        openai_models = [
            ("gpt-4", Decimal('0.03'), Decimal('0.06')),
            ("gpt-4-turbo", Decimal('0.01'), Decimal('0.03')),
            ("gpt-3.5-turbo", Decimal('0.0015'), Decimal('0.002')),
            ("gpt-3.5-turbo-16k", Decimal('0.003'), Decimal('0.004')),
            ("text-davinci-003", Decimal('0.02'), Decimal('0.02')),
            ("text-embedding-ada-002", Decimal('0.0001'), Decimal('0.0001')),
        ]
        
        for model, input_cost, output_cost in openai_models:
            pricing_db[f"openai:{model}"] = LLMPricing(
                provider=LLMProvider.OPENAI,
                model=model,
                input_cost_per_1k_tokens=input_cost,
                output_cost_per_1k_tokens=output_cost
            )
        
        # Anthropic pricing
        anthropic_models = [
            ("claude-3-opus", Decimal('0.015'), Decimal('0.075')),
            ("claude-3-sonnet", Decimal('0.003'), Decimal('0.015')),
            ("claude-3-haiku", Decimal('0.00025'), Decimal('0.00125')),
            ("claude-2.1", Decimal('0.008'), Decimal('0.024')),
            ("claude-2", Decimal('0.008'), Decimal('0.024')),
            ("claude-instant", Decimal('0.0008'), Decimal('0.0024')),
        ]
        
        for model, input_cost, output_cost in anthropic_models:
            pricing_db[f"anthropic:{model}"] = LLMPricing(
                provider=LLMProvider.ANTHROPIC,
                model=model,
                input_cost_per_1k_tokens=input_cost,
                output_cost_per_1k_tokens=output_cost
            )
        
        # Google pricing
        google_models = [
            ("gemini-pro", Decimal('0.0005'), Decimal('0.0015')),
            ("gemini-pro-vision", Decimal('0.0005'), Decimal('0.0015')),
            ("text-bison", Decimal('0.0005'), Decimal('0.0005')),
        ]
        
        for model, input_cost, output_cost in google_models:
            pricing_db[f"google:{model}"] = LLMPricing(
                provider=LLMProvider.GOOGLE,
                model=model,
                input_cost_per_1k_tokens=input_cost,
                output_cost_per_1k_tokens=output_cost
            )
        
        logger.info(f"📊 Initialized pricing database with {len(pricing_db)} model configurations")
        return pricing_db
    
    async def start_tracking(self) -> bool:
        """Start LLM cost tracking."""
        try:
            if self._running:
                logger.warning("LLMCostTracker is already running")
                return True
            
            # Connect to Redis
            await self._connect_redis()
            
            self._running = True
            logger.info("🚀 LLMCostTracker started - monitoring LLM costs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start LLMCostTracker: {e}")
            return False
    
    async def stop_tracking(self) -> None:
        """Stop LLM cost tracking gracefully."""
        logger.info("🛑 Stopping LLMCostTracker...")
        
        self._running = False
        
        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()
        
        logger.info("✅ LLMCostTracker stopped gracefully")
    
    async def _connect_redis(self) -> None:
        """Connect to Redis for cost data streaming."""
        try:
            self._redis_client = redis.Redis(
                host=self._config.redis_config.host,
                port=self._config.redis_config.port,
                password=self._config.redis_config.password,
                ssl=self._config.redis_config.ssl,
                decode_responses=True
            )
            
            # Test connection
            await self._redis_client.ping()
            logger.info(f"📡 LLMCostTracker connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def track_api_call(self, 
                           provider: str,
                           model: str,
                           input_tokens: int,
                           output_tokens: int,
                           response_time_ms: float,
                           success: bool = True,
                           error_type: Optional[str] = None,
                           user_id: Optional[str] = None,
                           correlation_id: Optional[str] = None) -> LLMAPICall:
        """
        Track an LLM API call and calculate its cost.
        
        Args:
            provider: LLM provider name (e.g., 'openai', 'anthropic')
            model: Model name (e.g., 'gpt-4', 'claude-3-opus')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            response_time_ms: Response time in milliseconds
            success: Whether the call was successful
            error_type: Error type if call failed
            user_id: User ID for the call
            correlation_id: Correlation ID for tracing
            
        Returns:
            LLMAPICall record with cost information
        """
        try:
            # Parse provider
            try:
                provider_enum = LLMProvider(provider.lower())
            except ValueError:
                logger.warning(f"Unknown provider '{provider}', defaulting to OpenAI")
                provider_enum = LLMProvider.OPENAI
            
            # Calculate cost
            estimated_cost = self._calculate_cost(provider_enum, model, input_tokens, output_tokens)
            
            # Create API call record
            api_call = LLMAPICall(
                provider=provider_enum,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                estimated_cost=estimated_cost,
                response_time_ms=response_time_ms,
                success=success,
                error_type=error_type,
                user_id=user_id,
                correlation_id=correlation_id
            )
            
            # Store the call
            self._api_calls.append(api_call)
            self._calls_tracked += 1
            
            # Update cost aggregations
            await self._update_cost_aggregations(api_call)
            
            # Check for anomalies
            await self._check_cost_anomalies(api_call)
            
            # Stream to Redis
            await self._stream_api_call_to_redis(api_call)
            
            logger.debug(f"💰 Tracked {provider}:{model} call - ${estimated_cost:.4f} ({input_tokens}+{output_tokens} tokens)")
            
            return api_call
            
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")
            # Return a minimal record even on error
            return LLMAPICall(
                provider=LLMProvider.OPENAI,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                success=False,
                error_type=str(e)
            )
    
    def _calculate_cost(self, provider: LLMProvider, model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate the cost of an LLM API call."""
        try:
            # Look up pricing
            pricing_key = f"{provider.value}:{model}"
            pricing = self._pricing_db.get(pricing_key)
            
            if not pricing:
                logger.warning(f"No pricing found for {pricing_key}, using default rates")
                # Default to GPT-3.5-turbo pricing
                pricing = self._pricing_db.get("openai:gpt-3.5-turbo")
                if not pricing:
                    return Decimal('0.00')
            
            # Calculate cost
            input_cost = (Decimal(input_tokens) / Decimal('1000')) * pricing.input_cost_per_1k_tokens
            output_cost = (Decimal(output_tokens) / Decimal('1000')) * pricing.output_cost_per_1k_tokens
            
            total_cost = input_cost + output_cost
            
            # Round to 4 decimal places
            return total_cost.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return Decimal('0.00')
    
    async def _update_cost_aggregations(self, api_call: LLMAPICall) -> None:
        """Update cost aggregations for reporting."""
        try:
            # Update daily costs
            date_key = api_call.timestamp.strftime('%Y-%m-%d')
            if date_key not in self._daily_costs:
                self._daily_costs[date_key] = Decimal('0.00')
            self._daily_costs[date_key] += api_call.estimated_cost
            
            # Update provider costs
            if api_call.provider not in self._provider_costs:
                self._provider_costs[api_call.provider] = Decimal('0.00')
            self._provider_costs[api_call.provider] += api_call.estimated_cost
            
            # Update model costs
            model_key = f"{api_call.provider.value}:{api_call.model}"
            if model_key not in self._model_costs:
                self._model_costs[model_key] = Decimal('0.00')
            self._model_costs[model_key] += api_call.estimated_cost
            
        except Exception as e:
            logger.error(f"Error updating cost aggregations: {e}")
    
    async def _check_cost_anomalies(self, api_call: LLMAPICall) -> None:
        """Check for cost anomalies and generate alerts."""
        try:
            # Check if single call cost is unusually high
            if api_call.estimated_cost > Decimal('1.00'):  # $1+ per call
                anomaly = CostAnomaly(
                    provider=api_call.provider.value,
                    cost_increase_percent=0.0,  # Single call anomaly
                    description=f"High-cost API call: ${api_call.estimated_cost:.4f} for {api_call.model}",
                    confidence_score=0.9
                )
                self._anomalies_detected += 1
                logger.warning(f"💸 Cost anomaly detected: {anomaly.description}")
            
            # Check daily cost thresholds
            today = api_call.timestamp.strftime('%Y-%m-%d')
            daily_cost = self._daily_costs.get(today, Decimal('0.00'))
            
            for threshold_name, threshold_amount in self._cost_thresholds.items():
                if daily_cost > Decimal(str(threshold_amount)):
                    logger.warning(f"💰 Daily cost threshold '{threshold_name}' exceeded: ${daily_cost:.2f}")
            
        except Exception as e:
            logger.error(f"Error checking cost anomalies: {e}")
    
    async def _stream_api_call_to_redis(self, api_call: LLMAPICall) -> None:
        """Stream API call data to Redis."""
        try:
            if not self._redis_client:
                return
            
            stream_name = f"{self._config.redis_config.stream_name}:llm_costs"
            
            # Convert to Redis stream format
            stream_data = {
                "call_id": api_call.call_id,
                "timestamp": api_call.timestamp.isoformat(),
                "provider": api_call.provider.value,
                "model": api_call.model,
                "operation_type": api_call.operation_type,
                "input_tokens": str(api_call.input_tokens),
                "output_tokens": str(api_call.output_tokens),
                "total_tokens": str(api_call.total_tokens),
                "estimated_cost": str(api_call.estimated_cost),
                "response_time_ms": str(api_call.response_time_ms),
                "success": str(api_call.success),
                "error_type": api_call.error_type or "",
                "user_id": api_call.user_id or "",
                "correlation_id": api_call.correlation_id or ""
            }
            
            # Add to Redis stream
            await self._redis_client.xadd(stream_name, stream_data)
            
        except Exception as e:
            logger.error(f"Failed to stream API call to Redis: {e}")
    
    def get_cost_metrics(self) -> CostMetrics:
        """Get current cost metrics and trends."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            total_cost_today = self._daily_costs.get(today, Decimal('0.00'))
            
            # Calculate monthly projection
            days_in_month = 30  # Simplified
            projected_monthly = total_cost_today * Decimal(str(days_in_month))
            
            # Determine cost trend (simplified)
            cost_trend = CostTrend.STABLE
            if len(self._daily_costs) >= 2:
                recent_costs = list(self._daily_costs.values())[-2:]
                if recent_costs[1] > recent_costs[0] * Decimal('1.2'):
                    cost_trend = CostTrend.INCREASING
                elif recent_costs[1] < recent_costs[0] * Decimal('0.8'):
                    cost_trend = CostTrend.DECREASING
            
            return CostMetrics(
                total_cost_today=total_cost_today,
                cost_by_provider={p.value: cost for p, cost in self._provider_costs.items()},
                cost_by_model=self._model_costs.copy(),
                projected_monthly_cost=projected_monthly,
                cost_trend=cost_trend
            )
            
        except Exception as e:
            logger.error(f"Error getting cost metrics: {e}")
            return CostMetrics()
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """Get cost tracking performance statistics."""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "calls_tracked": self._calls_tracked,
            "anomalies_detected": self._anomalies_detected,
            "tracking_rate_per_second": self._calls_tracked / uptime if uptime > 0 else 0,
            "supported_providers": [p.value for p in LLMProvider],
            "pricing_models": len(self._pricing_db),
            "daily_costs_tracked": len(self._daily_costs),
            "provider_costs": {p.value: float(cost) for p, cost in self._provider_costs.items()},
            "total_cost_today": float(self._daily_costs.get(datetime.now().strftime('%Y-%m-%d'), Decimal('0.00')))
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get LLMCostTracker capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.COST_TRACKING,
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "LLM Cost Tracker",
            "version": "1.0.0",
            "description": "Multi-provider LLM API cost tracking and monitoring",
            "config": {
                "supported_providers": [p.value for p in LLMProvider],
                "pricing_models": len(self._pricing_db),
                "cost_thresholds": {k: float(v) for k, v in self._cost_thresholds.items()}
            }
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation on errors."""
        logger.warning(f"LLMCostTracker entering graceful degradation due to: {error}")
        
        # Continue tracking even if Redis is down
        if "redis" in str(error).lower():
            logger.info("Redis connection issue - continuing cost tracking without streaming")
            return True
        
        return False
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the LLMCostTracker."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        if not self._running:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["LLMCostTracker is not running"]
        else:
            # Check if we're tracking calls
            uptime = time.time() - self._start_time
            tracking_rate = self._calls_tracked / uptime if uptime > 0 else 0
            
            if tracking_rate > 0 or uptime < 60:  # Allow 1 minute warmup
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.5
                issues = ["No API calls tracked recently"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=time.time() - self._start_time,
            error_count=0,
            warning_count=len(issues)
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this tracker."""
        return {
            "tracking_stats": self.get_tracking_stats(),
            "cost_metrics": self.get_cost_metrics().__dict__,
            "running": self._running
        }