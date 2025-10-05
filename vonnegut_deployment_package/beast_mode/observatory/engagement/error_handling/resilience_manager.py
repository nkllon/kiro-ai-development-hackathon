"""
Engagement Resilience Manager - System-Wide Resilience Coordination
==================================================================

Manages system-wide resilience strategies, coordinates fallback modes across
components, and ensures the engagement system maintains functionality under
adverse conditions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .engagement_error_handler import (
    EngagementErrorHandler, 
    EngagementErrorType, 
    EngagementErrorSeverity,
    EngagementFallbackMode
)


class ResilienceStrategy(Enum):
    """System-wide resilience strategies."""
    NORMAL_OPERATION = "normal_operation"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    MINIMAL_OPERATION = "minimal_operation"
    EMERGENCY_MODE = "emergency_mode"
    RECOVERY_MODE = "recovery_mode"


class FallbackStrategy(Enum):
    """Fallback strategies for different scenarios."""
    COMPONENT_ISOLATION = "component_isolation"      # Isolate failing components
    FEATURE_REDUCTION = "feature_reduction"          # Reduce feature complexity
    PERFORMANCE_OPTIMIZATION = "performance_optimization"  # Optimize for performance
    RESOURCE_CONSERVATION = "resource_conservation"  # Conserve system resources
    USER_EXPERIENCE_PRESERVATION = "user_experience_preservation"  # Maintain UX


@dataclass
class ResilienceMetrics:
    """Metrics for tracking system resilience."""
    strategy: ResilienceStrategy
    components_healthy: int
    components_degraded: int
    components_failed: int
    total_errors_last_hour: int
    recovery_attempts_last_hour: int
    successful_recoveries_last_hour: int
    system_load: float
    user_impact_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class EngagementResilienceManager(ReflectiveModule):
    """
    Manages system-wide resilience for the engagement system.
    
    Coordinates fallback modes, implements resilience strategies,
    and ensures the system maintains functionality under stress.
    """
    
    def __init__(self, error_handler: EngagementErrorHandler):
        super().__init__()
        self.module_id = "engagement_resilience_manager"
        
        self.error_handler = error_handler
        
        # Resilience state
        self.current_strategy = ResilienceStrategy.NORMAL_OPERATION
        self.fallback_strategies: Set[FallbackStrategy] = set()
        
        # Component tracking
        self.registered_components: Dict[str, Dict[str, Any]] = {}
        self.component_health_scores: Dict[str, float] = {}
        self.component_dependencies: Dict[str, List[str]] = {}
        
        # Resilience configuration
        self.health_check_interval = 30  # seconds
        self.strategy_evaluation_interval = 60  # seconds
        self.recovery_timeout = 300  # seconds
        
        # Thresholds
        self.degradation_threshold = 0.7  # System health below this triggers degradation
        self.emergency_threshold = 0.3    # System health below this triggers emergency mode
        self.recovery_threshold = 0.8     # System health above this allows recovery
        
        # State tracking
        self.last_strategy_change = datetime.now()
        self.resilience_metrics_history: List[ResilienceMetrics] = []
        self.active_recovery_tasks: Dict[str, asyncio.Task] = {}
        
        # Tasks
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.strategy_evaluator_task: Optional[asyncio.Task] = None
        
        logger.info("🛡️ Engagement Resilience Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the resilience manager."""
        try:
            # Start monitoring tasks
            self.health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
            self.strategy_evaluator_task = asyncio.create_task(self._strategy_evaluation_loop())
            
            logger.info("✅ Engagement Resilience Manager initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Resilience Manager: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the resilience manager."""
        logger.info("🛑 Shutting down Engagement Resilience Manager...")
        
        # Cancel monitoring tasks
        if self.health_monitor_task and not self.health_monitor_task.done():
            self.health_monitor_task.cancel()
            try:
                await self.health_monitor_task
            except asyncio.CancelledError:
                pass
        
        if self.strategy_evaluator_task and not self.strategy_evaluator_task.done():
            self.strategy_evaluator_task.cancel()
            try:
                await self.strategy_evaluator_task
            except asyncio.CancelledError:
                pass
        
        # Cancel active recovery tasks
        for task_name, task in self.active_recovery_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("✅ Engagement Resilience Manager shutdown complete")
    
    def register_component(self, 
                          component_name: str,
                          health_check_callback: Callable[[], Dict[str, Any]],
                          dependencies: List[str] = None,
                          critical: bool = False):
        """Register a component for resilience monitoring."""
        self.registered_components[component_name] = {
            "health_check": health_check_callback,
            "critical": critical,
            "last_health_check": datetime.now(),
            "consecutive_failures": 0
        }
        
        if dependencies:
            self.component_dependencies[component_name] = dependencies
        
        # Initialize health score
        self.component_health_scores[component_name] = 1.0
        
        logger.info(f"📋 Registered component for resilience monitoring: {component_name}")
    
    async def _health_monitoring_loop(self):
        """Continuously monitor component health."""
        logger.info("🏥 Starting resilience health monitoring loop")
        
        while True:
            try:
                await self._check_all_component_health()
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in resilience health monitoring loop: {e}")
                await asyncio.sleep(self.health_check_interval * 2)
    
    async def _strategy_evaluation_loop(self):
        """Continuously evaluate and adjust resilience strategy."""
        logger.info("🎯 Starting resilience strategy evaluation loop")
        
        while True:
            try:
                await self._evaluate_resilience_strategy()
                await asyncio.sleep(self.strategy_evaluation_interval)
                
            except Exception as e:
                logger.error(f"Error in resilience strategy evaluation loop: {e}")
                await asyncio.sleep(self.strategy_evaluation_interval * 2)
    
    async def _check_all_component_health(self):
        """Check health of all registered components."""
        for component_name, component_info in self.registered_components.items():
            try:
                health_check = component_info["health_check"]
                
                # Execute health check
                if asyncio.iscoroutinefunction(health_check):
                    health_data = await health_check()
                else:
                    health_data = health_check()
                
                # Calculate health score
                health_score = self._calculate_component_health_score(health_data)
                self.component_health_scores[component_name] = health_score
                
                # Update component info
                component_info["last_health_check"] = datetime.now()
                
                # Reset failure count on successful check
                if health_score > 0.5:
                    component_info["consecutive_failures"] = 0
                else:
                    component_info["consecutive_failures"] += 1
                
                # Trigger recovery if needed
                if health_score < 0.3 and component_info["consecutive_failures"] >= 3:
                    await self._trigger_component_recovery(component_name, health_data)
                
            except Exception as e:
                logger.warning(f"Health check failed for component {component_name}: {e}")
                
                # Increment failure count
                component_info["consecutive_failures"] += 1
                self.component_health_scores[component_name] = 0.0
                
                # Handle component failure
                await self._handle_component_failure(component_name, e)
    
    def _calculate_component_health_score(self, health_data: Dict[str, Any]) -> float:
        """Calculate a normalized health score from health data."""
        try:
            # Extract status
            status = health_data.get("status", "unknown").lower()
            
            # Base score from status
            status_scores = {
                "healthy": 1.0,
                "degraded": 0.6,
                "unhealthy": 0.3,
                "critical": 0.1,
                "failed": 0.0,
                "unknown": 0.5
            }
            
            base_score = status_scores.get(status, 0.5)
            
            # Adjust based on additional metrics
            if "health_score" in health_data:
                base_score = min(base_score, float(health_data["health_score"]))
            
            if "error_rate" in health_data:
                error_rate = float(health_data["error_rate"])
                base_score *= max(0.0, 1.0 - error_rate)
            
            if "response_time" in health_data:
                response_time = float(health_data["response_time"])
                if response_time > 5.0:  # 5 second threshold
                    base_score *= 0.5
                elif response_time > 1.0:  # 1 second threshold
                    base_score *= 0.8
            
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            logger.warning(f"Error calculating health score: {e}")
            return 0.5
    
    async def _evaluate_resilience_strategy(self):
        """Evaluate and potentially change resilience strategy."""
        try:
            # Calculate overall system health
            system_health = self._calculate_system_health()
            
            # Get error statistics
            error_stats = self.error_handler.get_error_statistics()
            
            # Determine appropriate strategy
            new_strategy = self._determine_optimal_strategy(system_health, error_stats)
            
            # Change strategy if needed
            if new_strategy != self.current_strategy:
                await self._change_resilience_strategy(new_strategy, system_health, error_stats)
            
            # Record metrics
            await self._record_resilience_metrics(system_health, error_stats)
            
        except Exception as e:
            logger.error(f"Error evaluating resilience strategy: {e}")
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health score."""
        if not self.component_health_scores:
            return 1.0
        
        # Weight critical components more heavily
        total_weight = 0
        weighted_sum = 0
        
        for component_name, health_score in self.component_health_scores.items():
            component_info = self.registered_components.get(component_name, {})
            weight = 2.0 if component_info.get("critical", False) else 1.0
            
            weighted_sum += health_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 1.0
    
    def _determine_optimal_strategy(self, 
                                  system_health: float, 
                                  error_stats: Dict[str, Any]) -> ResilienceStrategy:
        """Determine the optimal resilience strategy based on current conditions."""
        
        # Check for emergency conditions
        if system_health < self.emergency_threshold:
            return ResilienceStrategy.EMERGENCY_MODE
        
        # Check for degradation conditions
        if system_health < self.degradation_threshold:
            return ResilienceStrategy.GRACEFUL_DEGRADATION
        
        # Check if we're in recovery mode and can return to normal
        if (self.current_strategy in [ResilienceStrategy.RECOVERY_MODE, ResilienceStrategy.GRACEFUL_DEGRADATION] 
            and system_health > self.recovery_threshold):
            return ResilienceStrategy.NORMAL_OPERATION
        
        # Check if we need recovery mode
        if (self.current_strategy == ResilienceStrategy.EMERGENCY_MODE 
            and system_health > self.emergency_threshold):
            return ResilienceStrategy.RECOVERY_MODE
        
        # Check error rates
        recent_errors = error_stats.get("recent_errors", 0)
        if recent_errors > 20:  # High error rate
            if self.current_strategy == ResilienceStrategy.NORMAL_OPERATION:
                return ResilienceStrategy.GRACEFUL_DEGRADATION
        
        # Stay in current strategy if no clear reason to change
        return self.current_strategy
    
    async def _change_resilience_strategy(self, 
                                        new_strategy: ResilienceStrategy,
                                        system_health: float,
                                        error_stats: Dict[str, Any]):
        """Change the current resilience strategy."""
        old_strategy = self.current_strategy
        self.current_strategy = new_strategy
        self.last_strategy_change = datetime.now()
        
        logger.info(f"🔄 Changing resilience strategy: {old_strategy.value} → {new_strategy.value} "
                   f"(system health: {system_health:.2f})")
        
        # Apply strategy-specific actions
        await self._apply_resilience_strategy(new_strategy, system_health, error_stats)
        
        # Update fallback strategies
        self._update_fallback_strategies(new_strategy)
    
    async def _apply_resilience_strategy(self, 
                                       strategy: ResilienceStrategy,
                                       system_health: float,
                                       error_stats: Dict[str, Any]):
        """Apply actions for a specific resilience strategy."""
        
        if strategy == ResilienceStrategy.NORMAL_OPERATION:
            await self._apply_normal_operation()
            
        elif strategy == ResilienceStrategy.GRACEFUL_DEGRADATION:
            await self._apply_graceful_degradation(system_health)
            
        elif strategy == ResilienceStrategy.MINIMAL_OPERATION:
            await self._apply_minimal_operation()
            
        elif strategy == ResilienceStrategy.EMERGENCY_MODE:
            await self._apply_emergency_mode()
            
        elif strategy == ResilienceStrategy.RECOVERY_MODE:
            await self._apply_recovery_mode(system_health)
    
    async def _apply_normal_operation(self):
        """Apply normal operation strategy."""
        logger.info("✅ Applying normal operation strategy")
        
        # Restore all components to full functionality
        for component_name in self.registered_components:
            self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.FULL_FUNCTIONALITY
    
    async def _apply_graceful_degradation(self, system_health: float):
        """Apply graceful degradation strategy."""
        logger.info(f"⚠️ Applying graceful degradation strategy (health: {system_health:.2f})")
        
        # Reduce functionality for non-critical components
        for component_name, component_info in self.registered_components.items():
            if not component_info.get("critical", False):
                current_mode = self.error_handler.get_component_fallback_mode(component_name)
                if current_mode == EngagementFallbackMode.FULL_FUNCTIONALITY:
                    self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.REDUCED_FUNCTIONALITY
        
        # Add performance optimization fallback strategy
        self.fallback_strategies.add(FallbackStrategy.PERFORMANCE_OPTIMIZATION)
    
    async def _apply_minimal_operation(self):
        """Apply minimal operation strategy."""
        logger.warning("🔻 Applying minimal operation strategy")
        
        # Set all non-critical components to minimal functionality
        for component_name, component_info in self.registered_components.items():
            if not component_info.get("critical", False):
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.MINIMAL_FUNCTIONALITY
            else:
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.BASIC_FUNCTIONALITY
        
        # Add resource conservation fallback strategy
        self.fallback_strategies.add(FallbackStrategy.RESOURCE_CONSERVATION)
    
    async def _apply_emergency_mode(self):
        """Apply emergency mode strategy."""
        logger.critical("🚨 Applying emergency mode strategy")
        
        # Disable all non-critical components
        for component_name, component_info in self.registered_components.items():
            if not component_info.get("critical", False):
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.DISABLED
            else:
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.MINIMAL_FUNCTIONALITY
        
        # Add component isolation fallback strategy
        self.fallback_strategies.add(FallbackStrategy.COMPONENT_ISOLATION)
    
    async def _apply_recovery_mode(self, system_health: float):
        """Apply recovery mode strategy."""
        logger.info(f"🔄 Applying recovery mode strategy (health: {system_health:.2f})")
        
        # Gradually restore functionality
        for component_name in self.registered_components:
            current_mode = self.error_handler.get_component_fallback_mode(component_name)
            
            if current_mode == EngagementFallbackMode.DISABLED:
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.MINIMAL_FUNCTIONALITY
            elif current_mode == EngagementFallbackMode.MINIMAL_FUNCTIONALITY:
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.BASIC_FUNCTIONALITY
            elif current_mode == EngagementFallbackMode.BASIC_FUNCTIONALITY:
                self.error_handler.component_fallback_modes[component_name] = EngagementFallbackMode.REDUCED_FUNCTIONALITY
    
    def _update_fallback_strategies(self, strategy: ResilienceStrategy):
        """Update active fallback strategies based on resilience strategy."""
        self.fallback_strategies.clear()
        
        if strategy == ResilienceStrategy.GRACEFUL_DEGRADATION:
            self.fallback_strategies.add(FallbackStrategy.FEATURE_REDUCTION)
            self.fallback_strategies.add(FallbackStrategy.PERFORMANCE_OPTIMIZATION)
            
        elif strategy == ResilienceStrategy.MINIMAL_OPERATION:
            self.fallback_strategies.add(FallbackStrategy.RESOURCE_CONSERVATION)
            self.fallback_strategies.add(FallbackStrategy.USER_EXPERIENCE_PRESERVATION)
            
        elif strategy == ResilienceStrategy.EMERGENCY_MODE:
            self.fallback_strategies.add(FallbackStrategy.COMPONENT_ISOLATION)
            self.fallback_strategies.add(FallbackStrategy.RESOURCE_CONSERVATION)
            
        elif strategy == ResilienceStrategy.RECOVERY_MODE:
            self.fallback_strategies.add(FallbackStrategy.USER_EXPERIENCE_PRESERVATION)
    
    async def _trigger_component_recovery(self, component_name: str, health_data: Dict[str, Any]):
        """Trigger recovery for a specific component."""
        if component_name in self.active_recovery_tasks:
            return  # Recovery already in progress
        
        logger.info(f"🔄 Triggering recovery for component: {component_name}")
        
        # Start recovery task
        recovery_task = asyncio.create_task(
            self._component_recovery_process(component_name, health_data)
        )
        self.active_recovery_tasks[component_name] = recovery_task
        
        # Clean up completed task
        def cleanup_recovery_task(task):
            if component_name in self.active_recovery_tasks:
                del self.active_recovery_tasks[component_name]
        
        recovery_task.add_done_callback(cleanup_recovery_task)
    
    async def _component_recovery_process(self, component_name: str, health_data: Dict[str, Any]):
        """Execute recovery process for a component."""
        try:
            logger.info(f"Starting recovery process for {component_name}")
            
            # Wait for a brief period to see if component recovers naturally
            await asyncio.sleep(30)
            
            # Check if component has recovered
            component_info = self.registered_components.get(component_name)
            if component_info:
                health_check = component_info["health_check"]
                
                if asyncio.iscoroutinefunction(health_check):
                    current_health = await health_check()
                else:
                    current_health = health_check()
                
                health_score = self._calculate_component_health_score(current_health)
                
                if health_score > 0.7:
                    logger.info(f"✅ Component {component_name} recovered naturally")
                    return
            
            # Attempt systematic recovery
            await self._attempt_component_recovery(component_name, health_data)
            
        except Exception as e:
            logger.error(f"Error in recovery process for {component_name}: {e}")
    
    async def _attempt_component_recovery(self, component_name: str, health_data: Dict[str, Any]):
        """Attempt to recover a specific component."""
        try:
            # This would typically involve component-specific recovery logic
            logger.info(f"Attempting systematic recovery for {component_name}")
            
            # Placeholder for component-specific recovery
            # In a real implementation, this would:
            # 1. Restart the component
            # 2. Clear any corrupted state
            # 3. Reinitialize connections
            # 4. Validate recovery
            
            await asyncio.sleep(5)  # Simulate recovery time
            
            logger.info(f"Recovery attempt completed for {component_name}")
            
        except Exception as e:
            logger.error(f"Component recovery failed for {component_name}: {e}")
    
    async def _handle_component_failure(self, component_name: str, error: Exception):
        """Handle component failure."""
        logger.warning(f"Handling failure for component {component_name}: {error}")
        
        # Report error to error handler
        await self.error_handler.handle_error(
            EngagementErrorType.INTEGRATION_ERROR,
            component_name,
            f"Component health check failed: {error}",
            error,
            {"consecutive_failures": self.registered_components[component_name]["consecutive_failures"]}
        )
    
    async def _record_resilience_metrics(self, system_health: float, error_stats: Dict[str, Any]):
        """Record resilience metrics for analysis."""
        try:
            # Count component states
            components_healthy = sum(1 for score in self.component_health_scores.values() if score > 0.8)
            components_degraded = sum(1 for score in self.component_health_scores.values() if 0.3 < score <= 0.8)
            components_failed = sum(1 for score in self.component_health_scores.values() if score <= 0.3)
            
            # Calculate user impact score (placeholder)
            user_impact_score = 1.0 - (components_failed * 0.3 + components_degraded * 0.1)
            user_impact_score = max(0.0, min(1.0, user_impact_score))
            
            metrics = ResilienceMetrics(
                strategy=self.current_strategy,
                components_healthy=components_healthy,
                components_degraded=components_degraded,
                components_failed=components_failed,
                total_errors_last_hour=error_stats.get("recent_errors", 0),
                recovery_attempts_last_hour=0,  # Placeholder
                successful_recoveries_last_hour=0,  # Placeholder
                system_load=1.0 - system_health,
                user_impact_score=user_impact_score
            )
            
            self.resilience_metrics_history.append(metrics)
            
            # Trim history
            if len(self.resilience_metrics_history) > 1000:
                self.resilience_metrics_history = self.resilience_metrics_history[-1000:]
            
        except Exception as e:
            logger.error(f"Error recording resilience metrics: {e}")
    
    def get_resilience_status(self) -> Dict[str, Any]:
        """Get comprehensive resilience status."""
        system_health = self._calculate_system_health()
        
        return {
            "current_strategy": self.current_strategy.value,
            "system_health": system_health,
            "fallback_strategies": [strategy.value for strategy in self.fallback_strategies],
            "last_strategy_change": self.last_strategy_change.isoformat(),
            "component_health_scores": self.component_health_scores,
            "active_recovery_tasks": list(self.active_recovery_tasks.keys()),
            "registered_components": len(self.registered_components),
            "components_healthy": sum(1 for score in self.component_health_scores.values() if score > 0.8),
            "components_degraded": sum(1 for score in self.component_health_scores.values() if 0.3 < score <= 0.8),
            "components_failed": sum(1 for score in self.component_health_scores.values() if score <= 0.3)
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Engagement Resilience Manager capabilities."""
        return [
            "system_health_monitoring",
            "resilience_strategy_management",
            "component_recovery",
            "fallback_coordination",
            "metrics_collection",
            "dependency_tracking"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Engagement Resilience Manager health status."""
        system_health = self._calculate_system_health()
        
        return {
            "status": "healthy" if system_health > 0.7 else "degraded" if system_health > 0.3 else "critical",
            "system_health": system_health,
            "current_strategy": self.current_strategy.value,
            "monitoring_active": self.health_monitor_task is not None and not self.health_monitor_task.done(),
            "strategy_evaluation_active": self.strategy_evaluator_task is not None and not self.strategy_evaluator_task.done(),
            "registered_components": len(self.registered_components),
            "active_recovery_tasks": len(self.active_recovery_tasks)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Engagement Resilience Manager module information."""
        return {
            "module_id": self.module_id,
            "name": "Engagement Resilience Manager",
            "version": "1.0.0",
            "description": "System-wide resilience coordination for engagement system"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when resilience manager fails."""
        try:
            logger.critical(f"Resilience Manager entering degradation mode due to: {error}")
            
            # Switch to emergency mode
            self.current_strategy = ResilienceStrategy.EMERGENCY_MODE
            
            # Cancel monitoring tasks to reduce load
            if self.health_monitor_task and not self.health_monitor_task.done():
                self.health_monitor_task.cancel()
            
            if self.strategy_evaluator_task and not self.strategy_evaluator_task.done():
                self.strategy_evaluator_task.cancel()
            
            logger.info("Resilience Manager degradation applied: emergency mode activated")
            return True
            
        except Exception as degradation_error:
            logger.critical(f"Failed to apply resilience manager degradation: {degradation_error}")
            return False


logger = logging.getLogger(__name__)