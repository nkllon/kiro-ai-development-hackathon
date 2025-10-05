"""
Polling Strategy with Exponential Backoff and Jitter

This module provides intelligent polling strategies with exponential backoff,
jitter, and adaptive intervals to avoid overwhelming servers.
"""

import asyncio
import random
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class PollingState(Enum):
    """States for polling strategy"""
    INITIAL = "initial"
    NORMAL = "normal"
    BACKOFF = "backoff"
    RECOVERY = "recovery"
    SUSPENDED = "suspended"


@dataclass
class PollingConfig:
    """Configuration for polling strategy"""
    base_interval: float = 5.0  # Base interval in seconds
    max_interval: float = 60.0   # Maximum interval in seconds
    min_interval: float = 1.0    # Minimum interval in seconds
    backoff_multiplier: float = 1.5  # Exponential backoff multiplier
    jitter_factor: float = 0.1   # Jitter factor (10% randomization)
    max_failures: int = 5        # Max failures before suspension
    recovery_threshold: int = 3  # Successes needed for recovery
    suspension_duration: float = 300.0  # Suspension duration in seconds


@dataclass
class EndpointState:
    """State tracking for an endpoint"""
    endpoint: str
    state: PollingState = PollingState.INITIAL
    current_interval: float = 5.0
    failure_count: int = 0
    success_count: int = 0
    last_request_time: float = 0.0
    last_success_time: float = 0.0
    last_failure_time: float = 0.0
    suspension_end_time: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class PollingStrategy:
    """Intelligent polling strategy with adaptive intervals"""
    
    def __init__(self, config: Optional[PollingConfig] = None):
        self.config = config or PollingConfig()
        self.endpoint_states: Dict[str, EndpointState] = {}
        self.global_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "backoff_events": 0,
            "recovery_events": 0,
            "suspension_events": 0
        }
        
    def get_endpoint_state(self, endpoint: str) -> EndpointState:
        """Get or create endpoint state"""
        if endpoint not in self.endpoint_states:
            self.endpoint_states[endpoint] = EndpointState(
                endpoint=endpoint,
                current_interval=self.config.base_interval
            )
        return self.endpoint_states[endpoint]
    
    def calculate_next_interval(self, endpoint: str, success: bool) -> float:
        """
        Calculate the next polling interval based on success/failure
        
        Args:
            endpoint: The endpoint being polled
            success: Whether the last request was successful
            
        Returns:
            Next interval in seconds
        """
        state = self.get_endpoint_state(endpoint)
        current_time = time.time()
        
        # Update state based on result
        if success:
            state.success_count += 1
            state.consecutive_successes += 1
            state.consecutive_failures = 0
            state.last_success_time = current_time
            self.global_stats["successful_requests"] += 1
        else:
            state.failure_count += 1
            state.consecutive_failures += 1
            state.consecutive_successes = 0
            state.last_failure_time = current_time
            self.global_stats["failed_requests"] += 1
        
        state.last_request_time = current_time
        self.global_stats["total_requests"] += 1
        
        # Update polling state
        self._update_polling_state(state)
        
        # Calculate new interval
        new_interval = self._calculate_interval(state)
        
        # Apply jitter
        jittered_interval = self._apply_jitter(new_interval)
        
        # Update state
        state.current_interval = jittered_interval
        
        # Log the calculation
        self._log_interval_calculation(endpoint, success, new_interval, jittered_interval, state.state)
        
        return jittered_interval
    
    def _update_polling_state(self, state: EndpointState) -> None:
        """Update the polling state based on recent performance"""
        current_time = time.time()
        
        # Check if suspended and time to resume
        if state.state == PollingState.SUSPENDED:
            if current_time >= state.suspension_end_time:
                state.state = PollingState.RECOVERY
                state.consecutive_failures = 0
                state.consecutive_successes = 0
                self.global_stats["recovery_events"] += 1
                self._log_state_change(state.endpoint, PollingState.SUSPENDED, PollingState.RECOVERY)
            return
        
        # Check for suspension
        if state.consecutive_failures >= self.config.max_failures:
            if state.state != PollingState.SUSPENDED:
                state.state = PollingState.SUSPENDED
                state.suspension_end_time = current_time + self.config.suspension_duration
                self.global_stats["suspension_events"] += 1
                self._log_state_change(state.endpoint, state.state, PollingState.SUSPENDED)
            return
        
        # Check for recovery
        if state.state == PollingState.RECOVERY:
            if state.consecutive_successes >= self.config.recovery_threshold:
                state.state = PollingState.NORMAL
                self.global_stats["recovery_events"] += 1
                self._log_state_change(state.endpoint, PollingState.RECOVERY, PollingState.NORMAL)
            return
        
        # Check for backoff
        if state.consecutive_failures >= 2:
            if state.state != PollingState.BACKOFF:
                state.state = PollingState.BACKOFF
                self.global_stats["backoff_events"] += 1
                self._log_state_change(state.endpoint, state.state, PollingState.BACKOFF)
        elif state.consecutive_successes >= 2:
            if state.state != PollingState.NORMAL:
                state.state = PollingState.NORMAL
                self._log_state_change(state.endpoint, state.state, PollingState.NORMAL)
    
    def _calculate_interval(self, state: EndpointState) -> float:
        """Calculate the base interval based on current state"""
        if state.state == PollingState.SUSPENDED:
            return self.config.suspension_duration
        
        if state.state == PollingState.BACKOFF:
            # Exponential backoff
            backoff_interval = self.config.base_interval * (
                self.config.backoff_multiplier ** state.consecutive_failures
            )
            return min(backoff_interval, self.config.max_interval)
        
        if state.state == PollingState.RECOVERY:
            # Gradual recovery
            recovery_factor = max(0.5, 1.0 - (state.consecutive_successes * 0.1))
            return self.config.base_interval * recovery_factor
        
        if state.state == PollingState.NORMAL:
            # Normal operation
            if state.consecutive_successes > 5:
                # Reduce interval for consistently successful endpoints
                return max(self.config.min_interval, self.config.base_interval * 0.8)
            return self.config.base_interval
        
        # Initial state
        return self.config.base_interval
    
    def _apply_jitter(self, interval: float) -> float:
        """Apply jitter to prevent thundering herd"""
        jitter_range = interval * self.config.jitter_factor
        jitter = random.uniform(-jitter_range, jitter_range)
        jittered = interval + jitter
        
        # Ensure interval stays within bounds
        return max(self.config.min_interval, min(jittered, self.config.max_interval))
    
    def _log_interval_calculation(
        self, 
        endpoint: str, 
        success: bool, 
        base_interval: float, 
        final_interval: float,
        state: PollingState
    ) -> None:
        """Log interval calculation"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "task": "2.2",
            "action": "interval_calculated",
            "status": "in_progress",
            "details": {
                "endpoint": endpoint,
                "success": success,
                "base_interval": base_interval,
                "final_interval": final_interval,
                "state": state.value,
                "consecutive_failures": self.endpoint_states[endpoint].consecutive_failures,
                "consecutive_successes": self.endpoint_states[endpoint].consecutive_successes
            }
        }
        print(json.dumps(log_entry))
    
    def _log_state_change(self, endpoint: str, from_state: PollingState, to_state: PollingState) -> None:
        """Log state change"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "task": "2.2",
            "action": "state_changed",
            "status": "in_progress",
            "details": {
                "endpoint": endpoint,
                "from_state": from_state.value,
                "to_state": to_state.value
            }
        }
        print(json.dumps(log_entry))
    
    def get_endpoint_stats(self, endpoint: str) -> Dict:
        """Get statistics for a specific endpoint"""
        if endpoint not in self.endpoint_states:
            return {}
        
        state = self.endpoint_states[endpoint]
        return {
            "endpoint": endpoint,
            "state": state.state.value,
            "current_interval": state.current_interval,
            "failure_count": state.failure_count,
            "success_count": state.success_count,
            "consecutive_failures": state.consecutive_failures,
            "consecutive_successes": state.consecutive_successes,
            "last_request_time": state.last_request_time,
            "last_success_time": state.last_success_time,
            "last_failure_time": state.last_failure_time
        }
    
    def get_global_stats(self) -> Dict:
        """Get global statistics"""
        return {
            "global_stats": self.global_stats.copy(),
            "endpoint_count": len(self.endpoint_states),
            "active_endpoints": len([s for s in self.endpoint_states.values() 
                                   if s.state != PollingState.SUSPENDED])
        }
    
    def reset_endpoint(self, endpoint: str) -> None:
        """Reset endpoint state"""
        if endpoint in self.endpoint_states:
            self.endpoint_states[endpoint] = EndpointState(
                endpoint=endpoint,
                current_interval=self.config.base_interval
            )
            self._log_state_change(endpoint, PollingState.SUSPENDED, PollingState.INITIAL)
    
    def should_poll_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint should be polled"""
        if endpoint not in self.endpoint_states:
            return True
        
        state = self.endpoint_states[endpoint]
        return state.state != PollingState.SUSPENDED