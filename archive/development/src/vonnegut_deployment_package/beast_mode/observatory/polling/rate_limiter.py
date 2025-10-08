"""
Rate Limiter for Intelligent Polling

This module provides rate limiting capabilities to prevent triggering
bot protection systems and manage resource usage.
"""

import asyncio
import time
from typing import Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import json


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_concurrent_requests: int = 10
    burst_limit: int = 5
    burst_window: float = 10.0  # seconds


class RateLimiter:
    """Rate limiter with per-endpoint and global limits"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        
        # Per-endpoint tracking
        self.endpoint_requests: Dict[str, deque] = defaultdict(deque)
        self.endpoint_last_request: Dict[str, float] = {}
        
        # Global tracking
        self.global_requests: deque = deque()
        self.global_last_request: float = 0.0
        
        # Concurrent request tracking
        self.active_requests: Set[str] = set()
        self.request_start_times: Dict[str, float] = {}
        
        # Burst protection
        self.burst_requests: deque = deque()
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "rate_limited_requests": 0,
            "burst_limited_requests": 0,
            "concurrent_limited_requests": 0
        }
        
        self._lock = asyncio.Lock()
        
    async def can_make_request(self, endpoint: str) -> Tuple[bool, str]:
        """
        Check if a request can be made to the endpoint
        
        Args:
            endpoint: The endpoint to check
            
        Returns:
            Tuple of (can_make_request, reason)
        """
        async with self._lock:
            current_time = time.time()
            
            # Clean old requests
            self._cleanup_old_requests(current_time)
            
            # Check concurrent request limit
            if len(self.active_requests) >= self.config.max_concurrent_requests:
                self.stats["concurrent_limited_requests"] += 1
                return False, "concurrent_limit_exceeded"
            
            # Check burst limit
            if not self._check_burst_limit(current_time):
                self.stats["burst_limited_requests"] += 1
                return False, "burst_limit_exceeded"
            
            # Check global rate limit
            if not self._check_global_rate_limit(current_time):
                self.stats["rate_limited_requests"] += 1
                return False, "global_rate_limit_exceeded"
            
            # Check per-endpoint rate limit
            if not self._check_endpoint_rate_limit(endpoint, current_time):
                self.stats["rate_limited_requests"] += 1
                return False, "endpoint_rate_limit_exceeded"
            
            return True, "allowed"
    
    async def record_request(self, endpoint: str, request_id: str) -> None:
        """
        Record a request for rate limiting tracking
        
        Args:
            endpoint: The endpoint being requested
            request_id: Unique identifier for the request
        """
        async with self._lock:
            current_time = time.time()
            
            # Record global request
            self.global_requests.append(current_time)
            self.global_last_request = current_time
            
            # Record endpoint request
            self.endpoint_requests[endpoint].append(current_time)
            self.endpoint_last_request[endpoint] = current_time
            
            # Record burst request
            self.burst_requests.append(current_time)
            
            # Track active request
            self.active_requests.add(request_id)
            self.request_start_times[request_id] = current_time
            
            # Update statistics
            self.stats["total_requests"] += 1
            
            # Log the request
            self._log_request(endpoint, request_id, "recorded")
    
    async def complete_request(self, request_id: str) -> None:
        """
        Mark a request as completed
        
        Args:
            request_id: The request identifier
        """
        async with self._lock:
            if request_id in self.active_requests:
                self.active_requests.remove(request_id)
                if request_id in self.request_start_times:
                    del self.request_start_times[request_id]
                
                self._log_request("", request_id, "completed")
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """Clean up old request records"""
        # Clean global requests older than 1 hour
        cutoff_time = current_time - 3600
        while self.global_requests and self.global_requests[0] < cutoff_time:
            self.global_requests.popleft()
        
        # Clean burst requests older than burst window
        burst_cutoff = current_time - self.config.burst_window
        while self.burst_requests and self.burst_requests[0] < burst_cutoff:
            self.burst_requests.popleft()
        
        # Clean endpoint requests older than 1 hour
        for endpoint in list(self.endpoint_requests.keys()):
            endpoint_queue = self.endpoint_requests[endpoint]
            while endpoint_queue and endpoint_queue[0] < cutoff_time:
                endpoint_queue.popleft()
            
            # Remove empty queues
            if not endpoint_queue:
                del self.endpoint_requests[endpoint]
                if endpoint in self.endpoint_last_request:
                    del self.endpoint_last_request[endpoint]
    
    def _check_global_rate_limit(self, current_time: float) -> bool:
        """Check global rate limits"""
        # Check requests per minute
        minute_cutoff = current_time - 60
        recent_requests = sum(1 for req_time in self.global_requests if req_time > minute_cutoff)
        if recent_requests >= self.config.max_requests_per_minute:
            return False
        
        # Check requests per hour
        hour_cutoff = current_time - 3600
        hourly_requests = sum(1 for req_time in self.global_requests if req_time > hour_cutoff)
        if hourly_requests >= self.config.max_requests_per_hour:
            return False
        
        return True
    
    def _check_endpoint_rate_limit(self, endpoint: str, current_time: float) -> bool:
        """Check per-endpoint rate limits"""
        if endpoint not in self.endpoint_requests:
            return True
        
        endpoint_queue = self.endpoint_requests[endpoint]
        
        # Check requests per minute for this endpoint
        minute_cutoff = current_time - 60
        recent_requests = sum(1 for req_time in endpoint_queue if req_time > minute_cutoff)
        
        # Allow fewer requests per endpoint than global limit
        endpoint_limit = max(1, self.config.max_requests_per_minute // 10)
        return recent_requests < endpoint_limit
    
    def _check_burst_limit(self, current_time: float) -> bool:
        """Check burst protection limits"""
        burst_cutoff = current_time - self.config.burst_window
        recent_burst_requests = sum(1 for req_time in self.burst_requests if req_time > burst_cutoff)
        return recent_burst_requests < self.config.burst_limit
    
    def _log_request(self, endpoint: str, request_id: str, action: str) -> None:
        """Log request activity"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "task": "2.2",
            "action": f"rate_limit_{action}",
            "status": "in_progress",
            "details": {
                "endpoint": endpoint,
                "request_id": request_id,
                "active_requests": len(self.active_requests),
                "global_requests_per_minute": self._get_recent_requests_count(60),
                "burst_requests": len(self.burst_requests)
            }
        }
        print(json.dumps(log_entry))
    
    def _get_recent_requests_count(self, window_seconds: int) -> int:
        """Get count of requests in the last N seconds"""
        cutoff_time = time.time() - window_seconds
        return sum(1 for req_time in self.global_requests if req_time > cutoff_time)
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        current_time = time.time()
        self._cleanup_old_requests(current_time)
        
        return {
            "stats": self.stats.copy(),
            "current_active_requests": len(self.active_requests),
            "requests_per_minute": self._get_recent_requests_count(60),
            "requests_per_hour": self._get_recent_requests_count(3600),
            "endpoint_count": len(self.endpoint_requests),
            "burst_requests": len(self.burst_requests)
        }
    
    async def get_wait_time(self, endpoint: str) -> float:
        """
        Get the time to wait before next request is allowed
        
        Args:
            endpoint: The endpoint to check
            
        Returns:
            Time to wait in seconds
        """
        async with self._lock:
            current_time = time.time()
            
            # Check if we need to wait for burst limit
            if len(self.burst_requests) >= self.config.burst_limit:
                oldest_burst = self.burst_requests[0]
                burst_wait = (oldest_burst + self.config.burst_window) - current_time
                if burst_wait > 0:
                    return burst_wait
            
            # Check if we need to wait for rate limit
            if len(self.global_requests) >= self.config.max_requests_per_minute:
                oldest_request = self.global_requests[0]
                rate_wait = (oldest_request + 60) - current_time
                if rate_wait > 0:
                    return rate_wait
            
            return 0.0