"""
Intelligent HTTP Poller with Rate Limiting and Bot Protection

This module provides the main IntelligentPoller class that orchestrates
HTTP polling with intelligent rate limiting, request deduplication,
and bot-safe patterns.
"""

import asyncio
import aiohttp
import json
import time
import uuid
from typing import Dict, Set, Optional, Any, Callable, List
from dataclasses import dataclass
from collections import defaultdict

from .rate_limiter import RateLimiter, RateLimitConfig
from .request_deduplicator import RequestDeduplicator
from .bot_safe_headers import BotSafeHeaders, BOT_SAFE_HEADERS
from .polling_strategy import PollingStrategy, PollingConfig


@dataclass
class PollingResult:
    """Result of a polling operation"""
    success: bool
    data: Optional[Any] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = None
    request_time: float = 0.0


class IntelligentPoller:
    """Intelligent HTTP poller with comprehensive bot protection"""
    
    def __init__(
        self,
        rate_limit_config: Optional[RateLimitConfig] = None,
        polling_config: Optional[PollingConfig] = None,
        cache_ttl: float = 30.0,
        batch_window: float = 2.0
    ):
        # Configuration
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.polling_config = polling_config or PollingConfig()
        
        # Core components
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        self.deduplicator = RequestDeduplicator(cache_ttl, batch_window)
        self.bot_safe_headers = BotSafeHeaders()
        self.polling_strategy = PollingStrategy(self.polling_config)
        
        # Active polling state
        self.active_endpoints: Set[str] = set()
        self.polling_tasks: Dict[str, asyncio.Task] = {}
        self.endpoint_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Statistics
        self.stats = {
            "total_polls": 0,
            "successful_polls": 0,
            "failed_polls": 0,
            "rate_limited_polls": 0,
            "bot_protection_events": 0,
            "deduplicated_requests": 0
        }
        
        # Bot protection tracking
        self.bot_protection_events: List[Dict] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
    
    async def start(self) -> None:
        """Start the poller"""
        if self.session is None:
            # Create HTTP session with bot-safe configuration
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(
                total=30,
                connect=10,
                sock_read=20
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=BOT_SAFE_HEADERS
            )
        
        self._log_action("poller_started", "completed", {"active_endpoints": len(self.active_endpoints)})
    
    async def stop(self) -> None:
        """Stop the poller"""
        # Cancel all polling tasks
        for task in self.polling_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.polling_tasks:
            await asyncio.gather(*self.polling_tasks.values(), return_exceptions=True)
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        self.polling_tasks.clear()
        self.active_endpoints.clear()
        
        self._log_action("poller_stopped", "completed", {"final_stats": self.stats})
    
    async def start_polling(self, endpoint: str, callback: Optional[Callable] = None) -> None:
        """
        Start polling an endpoint
        
        Args:
            endpoint: The endpoint to poll
            callback: Optional callback function for results
        """
        if endpoint in self.active_endpoints:
            self._log_action("polling_already_active", "error", {"endpoint": endpoint})
            return
        
        if callback:
            self.endpoint_callbacks[endpoint].append(callback)
        
        self.active_endpoints.add(endpoint)
        
        # Start polling task
        task = asyncio.create_task(self._polling_loop(endpoint))
        self.polling_tasks[endpoint] = task
        
        self._log_action("polling_started", "completed", {"endpoint": endpoint})
    
    async def stop_polling(self, endpoint: str) -> None:
        """
        Stop polling an endpoint
        
        Args:
            endpoint: The endpoint to stop polling
        """
        if endpoint not in self.active_endpoints:
            return
        
        # Cancel polling task
        if endpoint in self.polling_tasks:
            self.polling_tasks[endpoint].cancel()
            try:
                await self.polling_tasks[endpoint]
            except asyncio.CancelledError:
                pass
            del self.polling_tasks[endpoint]
        
        # Remove from active endpoints
        self.active_endpoints.discard(endpoint)
        
        # Clear callbacks
        if endpoint in self.endpoint_callbacks:
            del self.endpoint_callbacks[endpoint]
        
        self._log_action("polling_stopped", "completed", {"endpoint": endpoint})
    
    async def poll_endpoint(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> PollingResult:
        """
        Poll a single endpoint once
        
        Args:
            endpoint: The endpoint to poll
            params: Optional query parameters
            
        Returns:
            PollingResult with the response
        """
        params = params or {}
        client_id = str(uuid.uuid4())
        
        # Check if polling is allowed
        if not self.polling_strategy.should_poll_endpoint(endpoint):
            return PollingResult(
                success=False,
                error="Endpoint suspended due to repeated failures"
            )
        
        # Check rate limiting
        can_request, reason = await self.rate_limiter.can_make_request(endpoint)
        if not can_request:
            self.stats["rate_limited_polls"] += 1
            wait_time = await self.rate_limiter.get_wait_time(endpoint)
            
            self._log_action("rate_limited", "error", {
                "endpoint": endpoint,
                "reason": reason,
                "wait_time": wait_time
            })
            
            return PollingResult(
                success=False,
                error=f"Rate limited: {reason}, wait {wait_time:.2f}s"
            )
        
        # Get or create request (with deduplication)
        request, is_new = await self.deduplicator.get_or_create_request(
            endpoint, params, BOT_SAFE_HEADERS, client_id
        )
        
        if not is_new:
            self.stats["deduplicated_requests"] += 1
            # Wait for the existing request to complete
            await self._wait_for_request_completion(request)
            return PollingResult(
                success=request.error is None,
                data=request.response_data,
                status_code=request.status_code,
                error=request.error,
                response_headers=request.response_headers
            )
        
        # Make the actual HTTP request
        request_id = str(uuid.uuid4())
        await self.rate_limiter.record_request(endpoint, request_id)
        
        start_time = time.time()
        try:
            result = await self._make_http_request(endpoint, params, request_id)
            
            # Update deduplicator
            request_key = self.deduplicator._generate_request_key(endpoint, params, BOT_SAFE_HEADERS)
            await self.deduplicator.complete_request(
                request_key,
                result.data,
                result.response_headers,
                result.status_code,
                result.error
            )
            
            # Update statistics
            if result.success:
                self.stats["successful_polls"] += 1
            else:
                self.stats["failed_polls"] += 1
            
            # Update polling strategy
            self.polling_strategy.calculate_next_interval(endpoint, result.success)
            
            # Check for bot protection
            if self._is_bot_protection_error(result):
                self.stats["bot_protection_events"] += 1
                self._record_bot_protection_event(endpoint, result)
            
            self.stats["total_polls"] += 1
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            error_result = PollingResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
            
            # Update deduplicator with error
            request_key = self.deduplicator._generate_request_key(endpoint, params, BOT_SAFE_HEADERS)
            await self.deduplicator.complete_request(request_key, error=error_result.error)
            
            # Update polling strategy
            self.polling_strategy.calculate_next_interval(endpoint, False)
            
            self.stats["failed_polls"] += 1
            self.stats["total_polls"] += 1
            
            return error_result
            
        finally:
            await self.rate_limiter.complete_request(request_id)
    
    async def _polling_loop(self, endpoint: str) -> None:
        """Main polling loop for an endpoint"""
        while endpoint in self.active_endpoints:
            try:
                # Poll the endpoint
                result = await self.poll_endpoint(endpoint)
                
                # Call registered callbacks
                if endpoint in self.endpoint_callbacks:
                    for callback in self.endpoint_callbacks[endpoint]:
                        try:
                            await callback(endpoint, result)
                        except Exception as e:
                            self._log_action("callback_error", "error", {
                                "endpoint": endpoint,
                                "error": str(e)
                            })
                
                # Calculate next interval
                endpoint_state = self.polling_strategy.get_endpoint_state(endpoint)
                next_interval = endpoint_state.current_interval
                
                # Wait for next poll
                await asyncio.sleep(next_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log_action("polling_loop_error", "error", {
                    "endpoint": endpoint,
                    "error": str(e)
                })
                # Wait before retrying on error
                await asyncio.sleep(5.0)
    
    async def _make_http_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any], 
        request_id: str
    ) -> PollingResult:
        """Make an HTTP request with bot-safe patterns"""
        if not self.session:
            return PollingResult(success=False, error="Session not initialized")
        
        start_time = time.time()
        
        try:
            # Get bot-safe headers
            headers = self.bot_safe_headers.get_headers(include_extended=True)
            headers["X-Request-ID"] = request_id
            
            # Make request
            async with self.session.get(
                endpoint,
                params=params,
                headers=headers,
                allow_redirects=True
            ) as response:
                
                response_data = None
                try:
                    response_data = await response.json()
                except (aiohttp.ContentTypeError, json.JSONDecodeError):
                    response_data = await response.text()
                
                request_time = time.time() - start_time
                
                return PollingResult(
                    success=200 <= response.status < 300,
                    data=response_data,
                    status_code=response.status,
                    response_headers=dict(response.headers),
                    request_time=request_time
                )
                
        except aiohttp.ClientError as e:
            request_time = time.time() - start_time
            return PollingResult(
                success=False,
                error=f"HTTP error: {str(e)}",
                request_time=request_time
            )
        except Exception as e:
            request_time = time.time() - start_time
            return PollingResult(
                success=False,
                error=f"Request error: {str(e)}",
                request_time=request_time
            )
    
    async def _wait_for_request_completion(self, request) -> None:
        """Wait for a request to complete"""
        # Simple polling wait - in a real implementation, this would use
        # proper synchronization primitives
        max_wait = 30.0  # 30 seconds max wait
        wait_interval = 0.1  # 100ms intervals
        waited = 0.0
        
        while request.response_data is None and request.error is None and waited < max_wait:
            await asyncio.sleep(wait_interval)
            waited += wait_interval
    
    def _is_bot_protection_error(self, result: PollingResult) -> bool:
        """Check if the result indicates bot protection"""
        if not result.success:
            error_lower = (result.error or "").lower()
            status = result.status_code or 0
            
            # Common bot protection indicators
            bot_indicators = [
                "bot", "captcha", "blocked", "forbidden", "rate limit",
                "too many requests", "access denied", "suspicious"
            ]
            
            # Status codes that often indicate bot protection
            bot_status_codes = [403, 429, 503, 1020, 1033]
            
            return (
                any(indicator in error_lower for indicator in bot_indicators) or
                status in bot_status_codes
            )
        
        return False
    
    def _record_bot_protection_event(self, endpoint: str, result: PollingResult) -> None:
        """Record a bot protection event"""
        event = {
            "timestamp": time.time(),
            "endpoint": endpoint,
            "status_code": result.status_code,
            "error": result.error,
            "response_headers": result.response_headers
        }
        
        self.bot_protection_events.append(event)
        
        # Keep only last 100 events
        if len(self.bot_protection_events) > 100:
            self.bot_protection_events = self.bot_protection_events[-100:]
        
        self._log_action("bot_protection_detected", "error", event)
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any]) -> None:
        """Log an action in JSON format"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "task": "2.2",
            "action": action,
            "status": status,
            "details": details
        }
        print(json.dumps(log_entry))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            "poller_stats": self.stats.copy(),
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "deduplicator_stats": self.deduplicator.get_stats(),
            "polling_strategy_stats": self.polling_strategy.get_global_stats(),
            "active_endpoints": list(self.active_endpoints),
            "bot_protection_events": len(self.bot_protection_events)
        }
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get statistics for a specific endpoint"""
        return {
            "endpoint": endpoint,
            "is_active": endpoint in self.active_endpoints,
            "polling_strategy": self.polling_strategy.get_endpoint_stats(endpoint),
            "rate_limiter": self.rate_limiter.get_stats()
        }