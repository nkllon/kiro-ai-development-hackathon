"""
Intelligent HTTP Poller

Main orchestrator for intelligent HTTP polling with rate limiting,
request deduplication, bot-safe headers, and exponential backoff.
"""

import json
import asyncio
import aiohttp
import time
from typing import Dict, Set, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass

from .rate_limiter import RateLimiter, RateLimitConfig
from .request_deduplicator import RequestDeduplicator
from .bot_safe_headers import BotSafeHeaders
from .polling_strategy import PollingStrategy, PollingConfig


@dataclass
class PollingResult:
    """Result of a polling operation."""
    endpoint: str
    success: bool
    response_data: Any = None
    status_code: int = 0
    error_message: str = ""
    response_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class IntelligentPoller:
    """Intelligent HTTP poller with comprehensive bot protection."""
    
    def __init__(
        self,
        rate_limit_config: Optional[RateLimitConfig] = None,
        polling_config: Optional[PollingConfig] = None,
        cache_ttl: int = 30
    ):
        # Configuration
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.polling_config = polling_config or PollingConfig()
        
        # Core components
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        self.deduplicator = RequestDeduplicator(cache_ttl=cache_ttl)
        self.bot_safe_headers = BotSafeHeaders()
        self.polling_strategy = PollingStrategy(self.polling_config)
        
        # State tracking
        self.active_endpoints: Set[str] = set()
        self.polling_tasks: Dict[str, asyncio.Task] = {}
        self.endpoint_last_poll: Dict[str, float] = {}
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Callbacks
        self.on_response: Optional[Callable[[PollingResult], None]] = None
        self.on_error: Optional[Callable[[PollingResult], None]] = None
        
        self._log_action("init", "IntelligentPoller initialized", {
            "base_interval": self.polling_config.base_interval,
            "max_interval": self.polling_config.max_interval,
            "cache_ttl": cache_ttl
        })
    
    async def start_polling(self, endpoint: str) -> None:
        """
        Start polling an endpoint.
        
        Args:
            endpoint: The endpoint to start polling
        """
        if endpoint in self.active_endpoints:
            self._log_action("start_polling", "Endpoint already being polled", {
                "endpoint": endpoint
            })
            return
        
        self.active_endpoints.add(endpoint)
        self.endpoint_last_poll[endpoint] = 0.0
        
        # Start polling task
        task = asyncio.create_task(self._poll_endpoint_loop(endpoint))
        self.polling_tasks[endpoint] = task
        
        self._log_action("start_polling", "Polling started", {
            "endpoint": endpoint,
            "active_endpoints": len(self.active_endpoints)
        })
    
    async def stop_polling(self, endpoint: str) -> None:
        """
        Stop polling an endpoint.
        
        Args:
            endpoint: The endpoint to stop polling
        """
        if endpoint not in self.active_endpoints:
            self._log_action("stop_polling", "Endpoint not being polled", {
                "endpoint": endpoint
            })
            return
        
        # Cancel polling task
        if endpoint in self.polling_tasks:
            task = self.polling_tasks[endpoint]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.polling_tasks[endpoint]
        
        # Remove from active endpoints
        self.active_endpoints.remove(endpoint)
        
        # Reset strategy
        self.polling_strategy.reset_endpoint(endpoint)
        
        self._log_action("stop_polling", "Polling stopped", {
            "endpoint": endpoint,
            "active_endpoints": len(self.active_endpoints)
        })
    
    async def poll_endpoint(self, endpoint: str, params: Dict[str, Any] = None) -> PollingResult:
        """
        Poll a single endpoint once.
        
        Args:
            endpoint: The endpoint to poll
            params: Request parameters
            
        Returns:
            PollingResult with the response
        """
        start_time = time.time()
        
        try:
            # Check rate limiting
            if not await self.rate_limiter.can_make_request(endpoint):
                next_allowed = self.rate_limiter.get_next_allowed_time(endpoint)
                wait_time = (next_allowed - datetime.utcnow()).total_seconds() if next_allowed else 0
                
                self._log_action("poll_endpoint", "Rate limited", {
                    "endpoint": endpoint,
                    "wait_time": wait_time
                })
                
                return PollingResult(
                    endpoint=endpoint,
                    success=False,
                    error_message=f"Rate limited, wait {wait_time:.1f}s",
                    response_time=time.time() - start_time
                )
            
            # Make request with deduplication
            response_data, status_code = await self.deduplicator.get_or_request(
                endpoint=endpoint,
                params=params,
                request_func=self._make_http_request
            )
            
            # Record successful request
            await self.rate_limiter.record_request(endpoint)
            
            response_time = time.time() - start_time
            
            # Adapt strategy based on response time
            self.polling_strategy.adapt_to_response_time(endpoint, response_time)
            
            result = PollingResult(
                endpoint=endpoint,
                success=True,
                response_data=response_data,
                status_code=status_code,
                response_time=response_time
            )
            
            # Update strategy with success
            self.polling_strategy.calculate_next_interval(endpoint, success=True)
            
            self._log_action("poll_endpoint", "Poll successful", {
                "endpoint": endpoint,
                "status_code": status_code,
                "response_time": response_time
            })
            
            # Call response callback
            if self.on_response:
                self.on_response(result)
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            result = PollingResult(
                endpoint=endpoint,
                success=False,
                error_message=str(e),
                response_time=response_time
            )
            
            # Update strategy with failure
            self.polling_strategy.calculate_next_interval(endpoint, success=False)
            
            self._log_action("poll_endpoint", "Poll failed", {
                "endpoint": endpoint,
                "error": str(e),
                "response_time": response_time
            })
            
            # Call error callback
            if self.on_error:
                self.on_error(result)
            
            return result
    
    async def _poll_endpoint_loop(self, endpoint: str) -> None:
        """Main polling loop for an endpoint."""
        self._log_action("poll_loop_start", "Polling loop started", {
            "endpoint": endpoint
        })
        
        while endpoint in self.active_endpoints:
            try:
                current_time = time.time()
                time_since_last = current_time - self.endpoint_last_poll.get(endpoint, 0)
                
                # Check if we should poll based on strategy
                if self.polling_strategy.should_poll(endpoint, time_since_last):
                    await self.poll_endpoint(endpoint)
                    self.endpoint_last_poll[endpoint] = current_time
                
                # Wait before next check
                await asyncio.sleep(1.0)  # Check every second
                
            except asyncio.CancelledError:
                self._log_action("poll_loop_cancelled", "Polling loop cancelled", {
                    "endpoint": endpoint
                })
                break
            except Exception as e:
                self._log_action("poll_loop_error", "Polling loop error", {
                    "endpoint": endpoint,
                    "error": str(e)
                })
                await asyncio.sleep(5.0)  # Wait before retrying
    
    async def _make_http_request(self, endpoint: str, params: Dict[str, Any] = None) -> tuple:
        """
        Make an HTTP request with bot-safe headers.
        
        Args:
            endpoint: The endpoint to request
            params: Request parameters
            
        Returns:
            Tuple of (response_data, status_code)
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        headers = self.bot_safe_headers.get_headers(endpoint)
        
        try:
            async with self.session.get(endpoint, params=params, headers=headers) as response:
                response_data = await response.json()
                return response_data, response.status
        except aiohttp.ContentTypeError:
            # Handle non-JSON responses
            async with self.session.get(endpoint, params=params, headers=headers) as response:
                response_text = await response.text()
                return response_text, response.status
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the poller."""
        return {
            "active_endpoints": list(self.active_endpoints),
            "endpoint_count": len(self.active_endpoints),
            "polling_strategy_stats": self.polling_strategy.get_all_stats(),
            "cache_stats": self.deduplicator.get_cache_stats(),
            "rate_limiter_config": {
                "max_per_minute": self.rate_limit_config.max_requests_per_minute,
                "max_per_hour": self.rate_limit_config.max_requests_per_hour
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown the poller and clean up resources."""
        self._log_action("shutdown_start", "Shutdown initiated", {
            "active_endpoints": len(self.active_endpoints)
        })
        
        # Stop all polling
        for endpoint in list(self.active_endpoints):
            await self.stop_polling(endpoint)
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        self._log_action("shutdown_complete", "Shutdown completed")
    
    def _log_action(self, action: str, description: str, details: Dict = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "2.2",
            "component": "IntelligentPoller",
            "action": action,
            "status": "completed",
            "description": description
        }
        
        if details:
            log_entry["details"] = details
            
        print(json.dumps(log_entry))