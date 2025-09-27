"""
Rate Limiter for Intelligent Polling

Implements per-endpoint and global rate limiting to prevent
triggering bot protection systems.
"""

import json
import asyncio
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests_per_minute: int = 12  # Conservative limit
    max_requests_per_hour: int = 720   # 12 requests/minute * 60
    burst_allowance: int = 3           # Allow burst of 3 requests
    cooldown_period: float = 5.0       # Seconds between requests


class RateLimiter:
    """Manages rate limiting for HTTP polling requests."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        
        # Per-endpoint tracking
        self.endpoint_requests: Dict[str, list] = {}
        self.endpoint_last_request: Dict[str, datetime] = {}
        
        # Global tracking
        self.global_requests: list = []
        self.global_last_request: Optional[datetime] = None
        
        # Cooldown tracking
        self.endpoint_cooldowns: Dict[str, datetime] = {}
        
        self._log_action("init", "RateLimiter initialized", {
            "max_per_minute": self.config.max_requests_per_minute,
            "max_per_hour": self.config.max_requests_per_hour
        })
    
    async def can_make_request(self, endpoint: str) -> bool:
        """
        Check if a request can be made for the given endpoint.
        
        Args:
            endpoint: The endpoint to check
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = datetime.utcnow()
        
        # Check global rate limits
        if not self._check_global_limits(now):
            self._log_action("rate_limit_check", "Global rate limit exceeded", {
                "endpoint": endpoint,
                "allowed": False
            })
            return False
        
        # Check endpoint-specific limits
        if not self._check_endpoint_limits(endpoint, now):
            self._log_action("rate_limit_check", "Endpoint rate limit exceeded", {
                "endpoint": endpoint,
                "allowed": False
            })
            return False
        
        # Check cooldown period
        if not self._check_cooldown(endpoint, now):
            self._log_action("rate_limit_check", "Cooldown period active", {
                "endpoint": endpoint,
                "allowed": False
            })
            return False
        
        self._log_action("rate_limit_check", "Request allowed", {
            "endpoint": endpoint,
            "allowed": True
        })
        
        return True
    
    async def record_request(self, endpoint: str) -> None:
        """
        Record a request for rate limiting purposes.
        
        Args:
            endpoint: The endpoint that was requested
        """
        now = datetime.utcnow()
        
        # Record global request
        self.global_requests.append(now)
        self.global_last_request = now
        
        # Record endpoint request
        if endpoint not in self.endpoint_requests:
            self.endpoint_requests[endpoint] = []
        self.endpoint_requests[endpoint].append(now)
        self.endpoint_last_request[endpoint] = now
        
        # Set cooldown
        self.endpoint_cooldowns[endpoint] = now + timedelta(seconds=self.config.cooldown_period)
        
        # Cleanup old requests
        self._cleanup_old_requests(now)
        
        self._log_action("record_request", "Request recorded", {
            "endpoint": endpoint,
            "global_count": len(self.global_requests),
            "endpoint_count": len(self.endpoint_requests.get(endpoint, []))
        })
    
    def get_next_allowed_time(self, endpoint: str) -> Optional[datetime]:
        """
        Get the next time a request will be allowed for the endpoint.
        
        Args:
            endpoint: The endpoint to check
            
        Returns:
            Next allowed time, or None if request is allowed now
        """
        now = datetime.utcnow()
        
        # Check cooldown
        if endpoint in self.endpoint_cooldowns:
            cooldown_end = self.endpoint_cooldowns[endpoint]
            if now < cooldown_end:
                return cooldown_end
        
        # Check if we need to wait for rate limit reset
        if not self._check_endpoint_limits(endpoint, now):
            # Find when the oldest request will expire
            if endpoint in self.endpoint_requests:
                oldest_request = min(self.endpoint_requests[endpoint])
                return oldest_request + timedelta(minutes=1)
        
        return None
    
    def _check_global_limits(self, now: datetime) -> bool:
        """Check global rate limits."""
        # Remove requests older than 1 hour
        cutoff = now - timedelta(hours=1)
        self.global_requests = [req for req in self.global_requests if req > cutoff]
        
        # Check hourly limit
        if len(self.global_requests) >= self.config.max_requests_per_hour:
            return False
        
        # Check minute limit
        minute_cutoff = now - timedelta(minutes=1)
        recent_requests = [req for req in self.global_requests if req > minute_cutoff]
        
        return len(recent_requests) < self.config.max_requests_per_minute
    
    def _check_endpoint_limits(self, endpoint: str, now: datetime) -> bool:
        """Check endpoint-specific rate limits."""
        if endpoint not in self.endpoint_requests:
            return True
        
        # Remove requests older than 1 hour
        cutoff = now - timedelta(hours=1)
        self.endpoint_requests[endpoint] = [
            req for req in self.endpoint_requests[endpoint] if req > cutoff
        ]
        
        # Check hourly limit (proportional to global limit)
        max_per_endpoint = self.config.max_requests_per_hour // 10  # Assume 10 endpoints max
        if len(self.endpoint_requests[endpoint]) >= max_per_endpoint:
            return False
        
        # Check minute limit (proportional to global limit)
        minute_cutoff = now - timedelta(minutes=1)
        recent_requests = [
            req for req in self.endpoint_requests[endpoint] 
            if req > minute_cutoff
        ]
        
        max_per_minute_endpoint = self.config.max_requests_per_minute // 10
        return len(recent_requests) < max_per_minute_endpoint
    
    def _check_cooldown(self, endpoint: str, now: datetime) -> bool:
        """Check if endpoint is in cooldown period."""
        if endpoint not in self.endpoint_cooldowns:
            return True
        
        return now >= self.endpoint_cooldowns[endpoint]
    
    def _cleanup_old_requests(self, now: datetime) -> None:
        """Clean up old request records."""
        cutoff = now - timedelta(hours=1)
        
        # Clean global requests
        self.global_requests = [req for req in self.global_requests if req > cutoff]
        
        # Clean endpoint requests
        for endpoint in self.endpoint_requests:
            self.endpoint_requests[endpoint] = [
                req for req in self.endpoint_requests[endpoint] if req > cutoff
            ]
        
        # Clean expired cooldowns
        self.endpoint_cooldowns = {
            endpoint: cooldown_end 
            for endpoint, cooldown_end in self.endpoint_cooldowns.items()
            if cooldown_end > now
        }
    
    def _log_action(self, action: str, description: str, details: Dict = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "2.2",
            "component": "RateLimiter",
            "action": action,
            "status": "completed",
            "description": description
        }
        
        if details:
            log_entry["details"] = details
            
        print(json.dumps(log_entry))