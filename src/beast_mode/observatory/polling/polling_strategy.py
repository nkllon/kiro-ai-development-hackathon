"""
Polling Strategy with Exponential Backoff and Jitter

Implements intelligent polling strategies with exponential backoff,
jitter to prevent thundering herd, and adaptive intervals.
"""

import json
import random
import math
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class PollingConfig:
    """Configuration for polling strategy."""
    base_interval: float = 5.0      # Base interval in seconds
    max_interval: float = 60.0      # Maximum interval in seconds
    backoff_multiplier: float = 1.5 # Exponential backoff multiplier
    jitter_factor: float = 0.1      # Jitter as fraction of interval
    max_failures: int = 10          # Max failures before max interval
    success_reset_threshold: int = 3 # Successes needed to reset backoff


class PollingStrategy:
    """Manages polling intervals with exponential backoff and jitter."""
    
    def __init__(self, config: Optional[PollingConfig] = None):
        self.config = config or PollingConfig()
        
        # Per-endpoint state tracking
        self.endpoint_failures: Dict[str, int] = {}
        self.endpoint_successes: Dict[str, int] = {}
        self.endpoint_last_interval: Dict[str, float] = {}
        
        self._log_action("init", "PollingStrategy initialized", {
            "base_interval": self.config.base_interval,
            "max_interval": self.config.max_interval,
            "backoff_multiplier": self.config.backoff_multiplier
        })
    
    def calculate_next_interval(self, endpoint: str, success: bool = True) -> float:
        """
        Calculate the next polling interval for an endpoint.
        
        Args:
            endpoint: The endpoint being polled
            success: Whether the last request was successful
            
        Returns:
            Next interval in seconds
        """
        # Initialize endpoint state if needed
        if endpoint not in self.endpoint_failures:
            self.endpoint_failures[endpoint] = 0
        if endpoint not in self.endpoint_successes:
            self.endpoint_successes[endpoint] = 0
        
        # Update failure/success counts
        if success:
            self.endpoint_successes[endpoint] += 1
            # Reset failures after enough successes
            if self.endpoint_successes[endpoint] >= self.config.success_reset_threshold:
                self.endpoint_failures[endpoint] = 0
                self.endpoint_successes[endpoint] = 0
        else:
            self.endpoint_failures[endpoint] += 1
            self.endpoint_successes[endpoint] = 0
        
        # Calculate base interval with exponential backoff
        failures = min(self.endpoint_failures[endpoint], self.config.max_failures)
        base_interval = self.config.base_interval * (self.config.backoff_multiplier ** failures)
        
        # Cap at maximum interval
        base_interval = min(base_interval, self.config.max_interval)
        
        # Add jitter to prevent thundering herd
        jitter_range = base_interval * self.config.jitter_factor
        jitter = random.uniform(-jitter_range, jitter_range)
        final_interval = max(1.0, base_interval + jitter)  # Minimum 1 second
        
        # Store the calculated interval
        self.endpoint_last_interval[endpoint] = final_interval
        
        self._log_action("interval_calculated", "Next interval calculated", {
            "endpoint": endpoint,
            "success": success,
            "failures": self.endpoint_failures[endpoint],
            "successes": self.endpoint_successes[endpoint],
            "base_interval": base_interval,
            "final_interval": final_interval,
            "jitter": jitter
        })
        
        return final_interval
    
    def get_current_interval(self, endpoint: str) -> float:
        """
        Get the current interval for an endpoint.
        
        Args:
            endpoint: The endpoint to check
            
        Returns:
            Current interval in seconds, or base interval if not set
        """
        return self.endpoint_last_interval.get(endpoint, self.config.base_interval)
    
    def reset_endpoint(self, endpoint: str) -> None:
        """
        Reset the polling strategy for an endpoint.
        
        Args:
            endpoint: The endpoint to reset
        """
        self.endpoint_failures[endpoint] = 0
        self.endpoint_successes[endpoint] = 0
        
        if endpoint in self.endpoint_last_interval:
            del self.endpoint_last_interval[endpoint]
        
        self._log_action("endpoint_reset", "Endpoint strategy reset", {
            "endpoint": endpoint
        })
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, any]:
        """
        Get statistics for an endpoint.
        
        Args:
            endpoint: The endpoint to get stats for
            
        Returns:
            Dictionary of endpoint statistics
        """
        return {
            "failures": self.endpoint_failures.get(endpoint, 0),
            "successes": self.endpoint_successes.get(endpoint, 0),
            "current_interval": self.get_current_interval(endpoint),
            "is_backed_off": self.endpoint_failures.get(endpoint, 0) > 0
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, any]]:
        """
        Get statistics for all endpoints.
        
        Returns:
            Dictionary of endpoint statistics
        """
        all_endpoints = set(self.endpoint_failures.keys()) | set(self.endpoint_successes.keys())
        
        return {
            endpoint: self.get_endpoint_stats(endpoint)
            for endpoint in all_endpoints
        }
    
    def should_poll(self, endpoint: str, time_since_last_poll: float) -> bool:
        """
        Determine if an endpoint should be polled based on time elapsed.
        
        Args:
            endpoint: The endpoint to check
            time_since_last_poll: Time since last poll in seconds
            
        Returns:
            True if endpoint should be polled
        """
        current_interval = self.get_current_interval(endpoint)
        should_poll = time_since_last_poll >= current_interval
        
        self._log_action("poll_check", "Poll decision made", {
            "endpoint": endpoint,
            "time_since_last": time_since_last_poll,
            "current_interval": current_interval,
            "should_poll": should_poll
        })
        
        return should_poll
    
    def adapt_to_response_time(self, endpoint: str, response_time: float) -> None:
        """
        Adapt polling strategy based on response time.
        
        Args:
            endpoint: The endpoint that responded
            response_time: Response time in seconds
        """
        # If response time is very high, increase interval slightly
        if response_time > 10.0:  # 10 seconds threshold
            current_interval = self.get_current_interval(endpoint)
            new_interval = min(current_interval * 1.1, self.config.max_interval)
            self.endpoint_last_interval[endpoint] = new_interval
            
            self._log_action("response_time_adapt", "Strategy adapted to response time", {
                "endpoint": endpoint,
                "response_time": response_time,
                "old_interval": current_interval,
                "new_interval": new_interval
            })
    
    def _log_action(self, action: str, description: str, details: Dict = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "2.2",
            "component": "PollingStrategy",
            "action": action,
            "status": "completed",
            "description": description
        }
        
        if details:
            log_entry["details"] = details
            
        print(json.dumps(log_entry))