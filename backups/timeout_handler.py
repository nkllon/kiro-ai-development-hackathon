"""
Beast Mode Framework - RCA Timeout Handler
Implements timeout handling and graceful degradation for RCA operations
Requirements: 1.4 - 30-second timeout requirement with graceful degradation
"""

import time
import signal
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus
from .performance_monitor import PerformanceMetrics, PerformanceStatus


class TimeoutStrategy(Enum):
    """Timeout handling strategies"""
    HARD_TIMEOUT = "hard_timeout"  # Immediately stop operation
    GRACEFUL_DEGRADATION = "graceful_degradation"  # Reduce scope and continue
    PROGRESSIVE_TIMEOUT = "progressive_timeout"  # Multiple timeout levels
    ADAPTIVE_TIMEOUT = "adaptive_timeout"  # Adjust based on operation complexity


@dataclass
class TimeoutConfiguration:
    """Configuration for timeout handling"""
    primary_timeout_seconds: int = 30
    warning_timeout_seconds: int = 25
    graceful_timeout_seconds: int = 20
    hard_timeout_seconds: int = 35
    strategy: TimeoutStrategy = TimeoutStrategy.GRACEFUL_DEGRADATION
    enable_progressive_degradation: bool = True
    max_degradation_levels: int = 3


@dataclass
class TimeoutEvent:
    """Represents a timeout event"""
    operation_id: str
    timeout_type: str  # warning, graceful, hard
    timestamp: datetime
    elapsed_seconds: float
    strategy_applied: str
    degradation_level: int = 0
    operation_completed: bool = False


class RCATimeoutHandler(ReflectiveModule):
    """
    Timeout handler for RCA operations with graceful degradation
    Ensures 30-second timeout compliance with intelligent fallback strategies
    """
    
    def __init__(self, timeout_config: Optional[TimeoutConfiguration] = None):
        super().__init__("rca_timeout_handler")
        
        # Timeout configuration
        self.timeout_config = timeout_config or TimeoutConfiguration()
        
        # Active timeout tracking
        self.active_timeouts: Dict[str, threading.Timer] = {}
        self.timeout_events: List[TimeoutEvent] = []
        self.operation_callbacks: Dict[str, Callable] = {}
        
        # Timeout statistics
        self.total_operations = 0
        self.timeout_warnings = 0
        self.graceful_timeouts = 0
        self.hard_timeouts = 0
        self.successful_degradations = 0
        
        # Degradation strategies
        self.degradation_strategies = {
            1: self._apply_level_1_degradation,  # Reduce analysis scope
            2: self._apply_level_2_degradation,  # Pattern matching only
            3: self._apply_level_3_degradation,  # Basic error reporting only
        }
        
        self._update_health_indicator(
            "timeout_handler_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "RCA timeout handler ready for operation management"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for timeout handling"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "active_timeouts": len(self.active_timeouts),
            "total_operations": self.total_operations,
            "timeout_warning_rate": self.timeout_warnings / max(1, self.total_operations),
            "graceful_timeout_rate": self.graceful_timeouts / max(1, self.total_operations),
            "hard_timeout_rate": self.hard_timeouts / max(1, self.total_operations),
            "successful_degradation_rate": self.successful_degradations / max(1, self.graceful_timeouts),
            "primary_timeout_seconds": self.timeout_config.primary_timeout_seconds,
            "timeout_strategy": self.timeout_config.strategy.value
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for timeout handling capability"""
        if self.total_operations == 0:
            return not self._degradation_active  # Healthy if no operations yet
            
        hard_timeout_rate = self.hard_timeouts / max(1, self.total_operations)
        degradation_success_rate = self.successful_degradations / max(1, self.graceful_timeouts) if self.graceful_timeouts > 0 else 1.0
        
        return (not self._degradation_active and 
                hard_timeout_rate < 0.05 and  # Less than 5% hard timeouts
                degradation_success_rate > 0.8)  # More than 80% successful degradations
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "timeout_management": {
                "status": "healthy" if len(self.active_timeouts) < 10 else "degraded",
                "active_operations": len(self.active_timeouts),
                "timeout_strategy": self.timeout_config.strategy.value
            },
            "timeout_compliance": {
                "status": "healthy" if self.hard_timeouts / max(1, self.total_operations) < 0.05 else "degraded",
                "primary_timeout_seconds": self.timeout_config.primary_timeout_seconds,
                "hard_timeout_rate": self.hard_timeouts / max(1, self.total_operations),
                "compliance_rate": 1.0 - (self.hard_timeouts / max(1, self.total_operations))
            },
            "graceful_degradation": {
                "status": "healthy" if self.successful_degradations / max(1, self.graceful_timeouts) > 0.8 else "degraded",
                "degradation_success_rate": self.successful_degradations / max(1, self.graceful_timeouts),
                "graceful_timeout_rate": self.graceful_timeouts / max(1, self.total_operations),
                "max_degradation_levels": self.timeout_config.max_degradation_levels
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: RCA timeout handling and graceful degradation"""
        return "rca_timeout_handling_and_graceful_degradation"
        
    @contextmanager
    def manage_operation_timeout(self, operation_id: str, operation_callback: Optional[Callable] = None):
        """
        Context manager for managing operation timeouts with graceful degradation
        Requirements: 1.4 - 30-second timeout with graceful degradation
        """
        self.total_operations += 1
        
        # Store operation callback for degradation
        if operation_callback:
            self.operation_callbacks[operation_id] = operation_callback
            
        # Set up timeout handlers based on strategy
        timeout_handlers = self._setup_timeout_handlers(operation_id)
        
        try:
            self.logger.info(f"Managing timeout for operation: {operation_id} (strategy: {self.timeout_config.strategy.value})")
            
            yield self._create_timeout_context(operation_id)
            
            # Operation completed successfully
            self._cleanup_operation_timeouts(operation_id)
            self.logger.info(f"Operation {operation_id} completed within timeout limits")
            
        except Exception as e:
            # Handle operation failure
            self._cleanup_operation_timeouts(operation_id)
            self.logger.error(f"Operation {operation_id} failed: {e}")
            raise
            
        finally:
            # Clean up
            self._cleanup_operation_callbacks(operation_id)
            
    def apply_graceful_degradation(self, operation_id: str, degradation_level: int = 1) -> Dict[str, Any]:
        """
        Apply graceful degradation to an operation
        Requirements: 1.4 - Graceful degradation when analysis exceeds time limits
        """
        try:
            self.logger.warning(f"Applying graceful degradation level {degradation_level} to operation {operation_id}")
            
            # Record timeout event
            timeout_event = TimeoutEvent(
                operation_id=operation_id,
                timeout_type="graceful",
                timestamp=datetime.now(),
                elapsed_seconds=self._get_operation_elapsed_time(operation_id),
                strategy_applied=f"degradation_level_{degradation_level}",
                degradation_level=degradation_level
            )
            self.timeout_events.append(timeout_event)
            self.graceful_timeouts += 1
            
            # Apply appropriate degradation strategy
            if degradation_level <= self.timeout_config.max_degradation_levels:
                degradation_strategy = self.degradation_strategies.get(degradation_level)
                if degradation_strategy:
                    degradation_result = degradation_strategy(operation_id)
                    
                    if degradation_result.get("success", False):
                        self.successful_degradations += 1
                        timeout_event.operation_completed = True
                        
                    return degradation_result
                    
            # If no strategy available or max level exceeded, apply hard timeout
            return self._apply_hard_timeout(operation_id)
            
        except Exception as e:
            self.logger.error(f"Graceful degradation failed for operation {operation_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "degradation_level": degradation_level,
                "fallback_applied": "hard_timeout"
            }
            
    def get_timeout_recommendations(self, operation_id: str, current_elapsed: float) -> Dict[str, Any]:
        """
        Get timeout recommendations based on current operation progress
        Requirements: 4.2 - Performance monitoring and optimization
        """
        try:
            recommendations = {
                "operation_id": operation_id,
                "current_elapsed_seconds": current_elapsed,
                "timeout_status": "normal",
                "recommendations": [],
                "degradation_suggested": False,
                "estimated_completion_time": None
            }
            
            # Determine timeout status
            if current_elapsed >= self.timeout_config.hard_timeout_seconds:
                recommendations["timeout_status"] = "critical"
                recommendations["recommendations"].append("immediate_termination_required")
                
            elif current_elapsed >= self.timeout_config.primary_timeout_seconds:
                recommendations["timeout_status"] = "exceeded"
                recommendations["recommendations"].append("hard_timeout_imminent")
                recommendations["degradation_suggested"] = True
                
            elif current_elapsed >= self.timeout_config.graceful_timeout_seconds:
                recommendations["timeout_status"] = "warning"
                recommendations["recommendations"].append("consider_graceful_degradation")
                recommendations["degradation_suggested"] = True
                
            elif current_elapsed >= self.timeout_config.warning_timeout_seconds:
                recommendations["timeout_status"] = "approaching"
                recommendations["recommendations"].append("monitor_closely")
                
            # Add specific recommendations based on elapsed time
            if current_elapsed > 15:  # Half of primary timeout
                recommendations["recommendations"].append("reduce_analysis_scope")
                
            if current_elapsed > 20:  # 2/3 of primary timeout
                recommendations["recommendations"].append("enable_fast_pattern_matching_only")
                
            if current_elapsed > 25:  # Close to primary timeout
                recommendations["recommendations"].append("prepare_for_graceful_degradation")
                
            # Estimate completion time based on historical data
            recommendations["estimated_completion_time"] = self._estimate_completion_time(operation_id, current_elapsed)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get timeout recommendations for operation {operation_id}: {e}")
            return {
                "operation_id": operation_id,
                "error": str(e),
                "timeout_status": "unknown",
                "recommendations": ["check_timeout_handler_health"]
            }
            
    def optimize_timeout_configuration(self) -> Dict[str, Any]:
        """
        Optimize timeout configuration based on historical performance
        Requirements: 4.2 - Performance optimization
        """
        try:
            optimization_result = {
                "optimization_applied": False,
                "previous_config": {
                    "primary_timeout": self.timeout_config.primary_timeout_seconds,
                    "warning_timeout": self.timeout_config.warning_timeout_seconds,
                    "graceful_timeout": self.timeout_config.graceful_timeout_seconds
                },
                "new_config": {},
                "optimization_reason": "",
                "performance_improvement_expected": 0.0
            }
            
            if len(self.timeout_events) < 10:
                optimization_result["optimization_reason"] = "insufficient_data"
                return optimization_result
                
            # Analyze recent timeout events
            recent_events = self.timeout_events[-50:]  # Last 50 events
            
            # Calculate average operation times
            completed_operations = [e for e in recent_events if e.operation_completed]
            if completed_operations:
                avg_completion_time = sum(e.elapsed_seconds for e in completed_operations) / len(completed_operations)
                
                # Optimize timeouts based on actual performance
                if avg_completion_time < self.timeout_config.primary_timeout_seconds * 0.6:
                    # Operations completing much faster than timeout - can reduce timeouts
                    new_primary = max(15, int(avg_completion_time * 1.5))  # 50% buffer, minimum 15s
                    new_warning = max(10, int(new_primary * 0.8))
                    new_graceful = max(8, int(new_primary * 0.7))
                    
                    self.timeout_config.primary_timeout_seconds = new_primary
                    self.timeout_config.warning_timeout_seconds = new_warning
                    self.timeout_config.graceful_timeout_seconds = new_graceful
                    
                    optimization_result.update({
                        "optimization_applied": True,
                        "new_config": {
                            "primary_timeout": new_primary,
                            "warning_timeout": new_warning,
                            "graceful_timeout": new_graceful
                        },
                        "optimization_reason": "operations_completing_faster_than_expected",
                        "performance_improvement_expected": 0.2
                    })
                    
                elif avg_completion_time > self.timeout_config.primary_timeout_seconds * 0.9:
                    # Operations taking close to timeout - increase timeouts slightly
                    new_primary = min(45, int(avg_completion_time * 1.2))  # 20% buffer, maximum 45s
                    new_warning = int(new_primary * 0.8)
                    new_graceful = int(new_primary * 0.7)
                    
                    self.timeout_config.primary_timeout_seconds = new_primary
                    self.timeout_config.warning_timeout_seconds = new_warning
                    self.timeout_config.graceful_timeout_seconds = new_graceful
                    
                    optimization_result.update({
                        "optimization_applied": True,
                        "new_config": {
                            "primary_timeout": new_primary,
                            "warning_timeout": new_warning,
                            "graceful_timeout": new_graceful
                        },
                        "optimization_reason": "operations_approaching_timeout_limits",
                        "performance_improvement_expected": 0.1
                    })
                    
            self.logger.info(f"Timeout configuration optimization: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Timeout configuration optimization failed: {e}")
            return {
                "optimization_applied": False,
                "error": str(e)
            }
            
    # Private helper methods
    
    def _setup_timeout_handlers(self, operation_id: str) -> Dict[str, threading.Timer]:
        """Set up timeout handlers for an operation"""
        handlers = {}
        
        try:
            # Warning timeout
            if self.timeout_config.warning_timeout_seconds > 0:
                warning_timer = threading.Timer(
                    self.timeout_config.warning_timeout_seconds,
                    self._handle_warning_timeout,
                    args=[operation_id]
                )
                warning_timer.start()
                handlers["warning"] = warning_timer
                
            # Graceful timeout
            if self.timeout_config.graceful_timeout_seconds > 0:
                graceful_timer = threading.Timer(
                    self.timeout_config.graceful_timeout_seconds,
                    self._handle_graceful_timeout,
                    args=[operation_id]
                )
                graceful_timer.start()
                handlers["graceful"] = graceful_timer
                
            # Hard timeout
            if self.timeout_config.hard_timeout_seconds > 0:
                hard_timer = threading.Timer(
                    self.timeout_config.hard_timeout_seconds,
                    self._handle_hard_timeout,
                    args=[operation_id]
                )
                hard_timer.start()
                handlers["hard"] = hard_timer
                
            self.active_timeouts[operation_id] = handlers
            return handlers
            
        except Exception as e:
            self.logger.error(f"Failed to setup timeout handlers for operation {operation_id}: {e}")
            return {}
            
    def _create_timeout_context(self, operation_id: str) -> Dict[str, Any]:
        """Create timeout context for operation"""
        return {
            "operation_id": operation_id,
            "timeout_config": self.timeout_config,
            "start_time": datetime.now(),
            "check_timeout": lambda: self._check_operation_timeout(operation_id),
            "request_degradation": lambda level=1: self.apply_graceful_degradation(operation_id, level)
        }
        
    def _cleanup_operation_timeouts(self, operation_id: str) -> None:
        """Clean up timeout handlers for completed operation"""
        try:
            if operation_id in self.active_timeouts:
                handlers = self.active_timeouts.pop(operation_id)
                for handler_type, timer in handlers.items():
                    if timer.is_alive():
                        timer.cancel()
                        
        except Exception as e:
            self.logger.error(f"Failed to cleanup timeouts for operation {operation_id}: {e}")
            
    def _cleanup_operation_callbacks(self, operation_id: str) -> None:
        """Clean up operation callbacks"""
        if operation_id in self.operation_callbacks:
            del self.operation_callbacks[operation_id]
            
    def _handle_warning_timeout(self, operation_id: str) -> None:
        """Handle warning timeout"""
        try:
            self.timeout_warnings += 1
            self.logger.warning(f"Operation {operation_id} exceeded warning timeout ({self.timeout_config.warning_timeout_seconds}s)")
            
            # Record timeout event
            timeout_event = TimeoutEvent(
                operation_id=operation_id,
                timeout_type="warning",
                timestamp=datetime.now(),
                elapsed_seconds=self.timeout_config.warning_timeout_seconds,
                strategy_applied="warning_logged"
            )
            self.timeout_events.append(timeout_event)
            
        except Exception as e:
            self.logger.error(f"Warning timeout handling failed for operation {operation_id}: {e}")
            
    def _handle_graceful_timeout(self, operation_id: str) -> None:
        """Handle graceful timeout"""
        try:
            self.logger.warning(f"Operation {operation_id} exceeded graceful timeout ({self.timeout_config.graceful_timeout_seconds}s)")
            
            # Apply graceful degradation
            if self.timeout_config.enable_progressive_degradation:
                self.apply_graceful_degradation(operation_id, degradation_level=1)
            else:
                self._apply_hard_timeout(operation_id)
                
        except Exception as e:
            self.logger.error(f"Graceful timeout handling failed for operation {operation_id}: {e}")
            
    def _handle_hard_timeout(self, operation_id: str) -> None:
        """Handle hard timeout"""
        try:
            self.hard_timeouts += 1
            self.logger.error(f"Operation {operation_id} exceeded hard timeout ({self.timeout_config.hard_timeout_seconds}s)")
            
            self._apply_hard_timeout(operation_id)
            
        except Exception as e:
            self.logger.error(f"Hard timeout handling failed for operation {operation_id}: {e}")
            
    def _apply_hard_timeout(self, operation_id: str) -> Dict[str, Any]:
        """Apply hard timeout termination"""
        try:
            # Record timeout event
            timeout_event = TimeoutEvent(
                operation_id=operation_id,
                timeout_type="hard",
                timestamp=datetime.now(),
                elapsed_seconds=self._get_operation_elapsed_time(operation_id),
                strategy_applied="hard_termination"
            )
            self.timeout_events.append(timeout_event)
            
            # Clean up operation
            self._cleanup_operation_timeouts(operation_id)
            
            return {
                "success": False,
                "timeout_type": "hard",
                "action": "operation_terminated",
                "elapsed_seconds": timeout_event.elapsed_seconds,
                "message": f"Operation {operation_id} terminated due to hard timeout"
            }
            
        except Exception as e:
            self.logger.error(f"Hard timeout application failed for operation {operation_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "termination_failed"
            }
            
    def _apply_level_1_degradation(self, operation_id: str) -> Dict[str, Any]:
        """Apply level 1 degradation: Reduce analysis scope"""
        try:
            self.logger.info(f"Applying level 1 degradation for operation {operation_id}: reduced analysis scope")
            
            degradation_config = {
                "analysis_scope": "reduced",
                "comprehensive_analysis": "disabled",
                "pattern_matching": "fast_only",
                "fix_generation": "basic_only",
                "validation": "minimal"
            }
            
            # Call operation callback if available
            if operation_id in self.operation_callbacks:
                callback = self.operation_callbacks[operation_id]
                callback(degradation_config)
                
            return {
                "success": True,
                "degradation_level": 1,
                "strategy": "reduced_analysis_scope",
                "config": degradation_config,
                "estimated_time_savings": "40%"
            }
            
        except Exception as e:
            self.logger.error(f"Level 1 degradation failed for operation {operation_id}: {e}")
            return {"success": False, "error": str(e)}
            
    def _apply_level_2_degradation(self, operation_id: str) -> Dict[str, Any]:
        """Apply level 2 degradation: Pattern matching only"""
        try:
            self.logger.info(f"Applying level 2 degradation for operation {operation_id}: pattern matching only")
            
            degradation_config = {
                "analysis_scope": "pattern_matching_only",
                "comprehensive_analysis": "disabled",
                "pattern_matching": "existing_patterns_only",
                "fix_generation": "from_patterns_only",
                "validation": "disabled"
            }
            
            # Call operation callback if available
            if operation_id in self.operation_callbacks:
                callback = self.operation_callbacks[operation_id]
                callback(degradation_config)
                
            return {
                "success": True,
                "degradation_level": 2,
                "strategy": "pattern_matching_only",
                "config": degradation_config,
                "estimated_time_savings": "70%"
            }
            
        except Exception as e:
            self.logger.error(f"Level 2 degradation failed for operation {operation_id}: {e}")
            return {"success": False, "error": str(e)}
            
    def _apply_level_3_degradation(self, operation_id: str) -> Dict[str, Any]:
        """Apply level 3 degradation: Basic error reporting only"""
        try:
            self.logger.info(f"Applying level 3 degradation for operation {operation_id}: basic error reporting only")
            
            degradation_config = {
                "analysis_scope": "minimal",
                "comprehensive_analysis": "disabled",
                "pattern_matching": "disabled",
                "fix_generation": "generic_only",
                "validation": "disabled",
                "reporting": "basic_error_info_only"
            }
            
            # Call operation callback if available
            if operation_id in self.operation_callbacks:
                callback = self.operation_callbacks[operation_id]
                callback(degradation_config)
                
            return {
                "success": True,
                "degradation_level": 3,
                "strategy": "basic_error_reporting_only",
                "config": degradation_config,
                "estimated_time_savings": "90%"
            }
            
        except Exception as e:
            self.logger.error(f"Level 3 degradation failed for operation {operation_id}: {e}")
            return {"success": False, "error": str(e)}
            
    def _get_operation_elapsed_time(self, operation_id: str) -> float:
        """Get elapsed time for an operation"""
        # This would need to be integrated with the performance monitor
        # For now, return a placeholder
        return 0.0
        
    def _check_operation_timeout(self, operation_id: str) -> Dict[str, Any]:
        """Check if operation is approaching timeout"""
        return {
            "operation_id": operation_id,
            "timeout_status": "normal",
            "elapsed_seconds": self._get_operation_elapsed_time(operation_id),
            "remaining_seconds": self.timeout_config.primary_timeout_seconds - self._get_operation_elapsed_time(operation_id)
        }
        
    def _estimate_completion_time(self, operation_id: str, current_elapsed: float) -> Optional[float]:
        """Estimate completion time based on historical data"""
        if len(self.timeout_events) < 5:
            return None
            
        # Simple estimation based on average completion times
        completed_operations = [e for e in self.timeout_events if e.operation_completed]
        if completed_operations:
            avg_completion = sum(e.elapsed_seconds for e in completed_operations) / len(completed_operations)
            return max(avg_completion, current_elapsed + 5)  # At least 5 more seconds
            
        return None