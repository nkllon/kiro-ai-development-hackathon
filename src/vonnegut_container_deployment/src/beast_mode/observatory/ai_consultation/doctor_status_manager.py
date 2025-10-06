"""
Doctor Status Management System

Manages the "Doctor Is In/Out" status based on budget limits, system health,
and feature flags. Provides cost tracking and automatic status transitions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json

from .models import DoctorStatus, DoctorStatusReason, BudgetStatus, CostAnalytics
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError
from .database import db_manager
from .status_broadcaster import status_broadcaster
from .status_persistence import status_persistence

logger = logging.getLogger(__name__)


class StatusTransition(str, Enum):
    """Status transition types"""
    MANUAL_ENABLE = "manual_enable"
    MANUAL_DISABLE = "manual_disable"
    BUDGET_EXHAUSTED = "budget_exhausted"
    BUDGET_RESTORED = "budget_restored"
    SYSTEM_ERROR = "system_error"
    SYSTEM_RECOVERED = "system_recovered"
    FEATURE_DISABLED = "feature_disabled"
    FEATURE_ENABLED = "feature_enabled"


@dataclass
class StatusChangeEvent:
    """Status change event data"""
    timestamp: datetime
    old_status: bool
    new_status: bool
    reason: DoctorStatusReason
    transition_type: StatusTransition
    triggered_by: str
    cost_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class DoctorStatusManager:
    """
    Manages doctor availability status with cost tracking and feature flags
    
    Features:
    - Budget limit enforcement
    - Automatic status transitions
    - Cost analytics and tracking
    - Feature flag integration
    - Circuit breaker protection
    - Event-driven status changes
    """
    
    def __init__(
        self,
        daily_budget: float = 10.0,
        monthly_budget: float = 100.0,
        cost_per_token: float = 0.0001,
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.95
    ):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.cost_per_token = cost_per_token
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        # Status tracking
        self._current_status: Optional[DoctorStatus] = None
        self._status_listeners: List[Callable[[StatusChangeEvent], None]] = []
        self._last_budget_check = datetime.utcnow()
        
        # Cost tracking
        self._daily_usage = 0.0
        self._monthly_usage = 0.0
        self._session_costs: Dict[str, float] = {}
        
        # System state
        self._active_sessions = 0
        self._queue_length = 0
        self._system_healthy = True
        
        # Feature flag cache
        self._feature_flags_cache: Dict[str, bool] = {}
        self._cache_expiry = datetime.utcnow()
        
    async def initialize(self) -> None:
        """Initialize the status manager"""
        try:
            logger.info("Initializing Doctor Status Manager")
            
            # Load current status from database
            await self._load_current_status()
            
            # Load budget and usage data
            await self._load_budget_data()
            
            # Refresh feature flags
            await self._refresh_feature_flags()
            
            # Perform initial status evaluation
            await self._evaluate_status()
            
            logger.info(f"Doctor Status Manager initialized - Status: {'Available' if self._current_status.is_available else 'Unavailable'}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Doctor Status Manager: {e}")
            raise ConsultationError(
                f"Status manager initialization failed: {str(e)}",
                error_code="STATUS_MANAGER_INIT_FAILED"
            )
    
    async def _load_current_status(self) -> None:
        """Load current status from database"""
        try:
            # Get latest status from database
            results = await db_manager.execute_query(
                "SELECT * FROM ai_consultation_doctor_status ORDER BY last_updated DESC LIMIT 1"
            )
            
            if results:
                status_data = results[0]
                self._current_status = DoctorStatus(
                    is_available=bool(status_data['is_available']),
                    reason=DoctorStatusReason(status_data['reason']),
                    cost_budget_remaining=status_data['cost_budget_remaining'],
                    daily_usage=status_data['daily_usage'],
                    monthly_usage=status_data['monthly_usage'],
                    last_updated=datetime.fromisoformat(status_data['last_updated']),
                    next_budget_reset=datetime.fromisoformat(status_data['next_budget_reset']) if status_data['next_budget_reset'] else None,
                    active_sessions=status_data['active_sessions'],
                    queue_length=status_data['queue_length']
                )
                
                # Update internal tracking
                self._daily_usage = self._current_status.daily_usage
                self._monthly_usage = self._current_status.monthly_usage
                self._active_sessions = self._current_status.active_sessions
                self._queue_length = self._current_status.queue_length
                
            else:
                # Create default status
                self._current_status = DoctorStatus(
                    is_available=False,
                    reason=DoctorStatusReason.MANUAL,
                    cost_budget_remaining=self.daily_budget,
                    daily_usage=0.0,
                    monthly_usage=0.0,
                    last_updated=datetime.utcnow(),
                    next_budget_reset=self._calculate_next_reset(),
                    active_sessions=0,
                    queue_length=0
                )
                
                # Save default status
                await self._persist_status()
                
        except Exception as e:
            logger.error(f"Failed to load current status: {e}")
            # Create emergency default status
            self._current_status = DoctorStatus(
                is_available=False,
                reason=DoctorStatusReason.SYSTEM_ERROR,
                cost_budget_remaining=0.0,
                daily_usage=0.0,
                monthly_usage=0.0,
                last_updated=datetime.utcnow(),
                next_budget_reset=self._calculate_next_reset(),
                active_sessions=0,
                queue_length=0
            )
    
    async def _load_budget_data(self) -> None:
        """Load budget configuration from database"""
        try:
            results = await db_manager.execute_query(
                "SELECT * FROM ai_consultation_budget ORDER BY date DESC LIMIT 1"
            )
            
            if results:
                budget_data = results[0]
                self.daily_budget = budget_data['daily_budget']
                self.monthly_budget = budget_data['monthly_budget']
                self.cost_per_token = budget_data['cost_per_token']
                
                # Update usage tracking
                self._daily_usage = budget_data['daily_spent']
                self._monthly_usage = budget_data['monthly_spent']
                
                logger.info(f"Loaded budget: Daily ${self.daily_budget}, Monthly ${self.monthly_budget}")
            
        except Exception as e:
            logger.warning(f"Failed to load budget data, using defaults: {e}")
    
    async def _refresh_feature_flags(self) -> None:
        """Refresh feature flags cache"""
        try:
            # Check if cache is still valid (5 minute TTL)
            if datetime.utcnow() < self._cache_expiry:
                return
            
            # Refresh critical feature flags
            flags_to_check = [
                FeatureFlag.DOCTOR_STATUS_MANAGEMENT,
                FeatureFlag.COST_TRACKING,
                FeatureFlag.BUDGET_ENFORCEMENT,
                FeatureFlag.REAL_TIME_CHAT,
                FeatureFlag.QUEUE_PROCESSING
            ]
            
            for flag in flags_to_check:
                self._feature_flags_cache[flag.value] = await feature_flags.is_enabled(flag)
            
            # Update cache expiry
            self._cache_expiry = datetime.utcnow() + timedelta(minutes=5)
            
            logger.debug(f"Refreshed feature flags: {self._feature_flags_cache}")
            
        except Exception as e:
            logger.warning(f"Failed to refresh feature flags: {e}")
    
    def _calculate_next_reset(self) -> datetime:
        """Calculate next budget reset time (next day at midnight UTC)"""
        now = datetime.utcnow()
        next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_reset
    
    async def _evaluate_status(self) -> None:
        """Evaluate and update doctor status based on current conditions"""
        try:
            old_status = self._current_status.is_available
            old_reason = self._current_status.reason
            
            # Check feature flags first
            if not self._feature_flags_cache.get(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, True):
                await self._update_status(
                    False, 
                    DoctorStatusReason.FEATURE_DISABLED,
                    StatusTransition.FEATURE_DISABLED,
                    "system"
                )
                return
            
            # Check system health
            if not self._system_healthy:
                await self._update_status(
                    False,
                    DoctorStatusReason.SYSTEM_ERROR,
                    StatusTransition.SYSTEM_ERROR,
                    "system"
                )
                return
            
            # Check budget constraints
            budget_status = await self.get_budget_status()
            
            if budget_status.daily_exhausted or budget_status.monthly_exhausted:
                await self._update_status(
                    False,
                    DoctorStatusReason.BUDGET_EXHAUSTED,
                    StatusTransition.BUDGET_EXHAUSTED,
                    "system"
                )
                return
            
            # If we were previously unavailable due to budget/system issues,
            # and those issues are resolved, we can become available again
            if (not old_status and 
                old_reason in [DoctorStatusReason.BUDGET_EXHAUSTED, DoctorStatusReason.SYSTEM_ERROR, DoctorStatusReason.FEATURE_DISABLED]):
                
                await self._update_status(
                    True,
                    DoctorStatusReason.AUTOMATIC,
                    StatusTransition.SYSTEM_RECOVERED,
                    "system"
                )
                return
            
            # For manual status, don't change automatically
            if old_reason == DoctorStatusReason.MANUAL:
                return
            
        except Exception as e:
            logger.error(f"Failed to evaluate status: {e}")
            # Set to error state
            await self._update_status(
                False,
                DoctorStatusReason.SYSTEM_ERROR,
                StatusTransition.SYSTEM_ERROR,
                "system"
            )
    
    async def _update_status(
        self,
        is_available: bool,
        reason: DoctorStatusReason,
        transition_type: StatusTransition,
        triggered_by: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update doctor status and notify listeners"""
        try:
            old_status = self._current_status.is_available
            
            # Update status
            self._current_status.is_available = is_available
            self._current_status.reason = reason
            self._current_status.last_updated = datetime.utcnow()
            self._current_status.active_sessions = self._active_sessions
            self._current_status.queue_length = self._queue_length
            self._current_status.daily_usage = self._daily_usage
            self._current_status.monthly_usage = self._monthly_usage
            self._current_status.cost_budget_remaining = max(0, self.daily_budget - self._daily_usage)
            
            # Persist to database
            await self._persist_status()
            
            # Create status change event
            event = StatusChangeEvent(
                timestamp=datetime.utcnow(),
                old_status=old_status,
                new_status=is_available,
                reason=reason,
                transition_type=transition_type,
                triggered_by=triggered_by,
                cost_data={
                    'daily_usage': self._daily_usage,
                    'monthly_usage': self._monthly_usage,
                    'daily_budget': self.daily_budget,
                    'monthly_budget': self.monthly_budget
                },
                metadata=metadata
            )
            
            # Notify listeners
            await self._notify_status_change(event)
            
            # Broadcast status change via WebSocket
            await status_broadcaster.broadcast_status_change(event)
            
            # Store event in Redis for persistence
            await status_persistence.store_status_event(event)
            
            # Store current status in Redis
            await status_persistence.store_doctor_status(self._current_status)
            
            logger.info(f"Status updated: {old_status} -> {is_available} (reason: {reason.value}, triggered by: {triggered_by})")
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            raise
    
    async def _persist_status(self) -> None:
        """Persist current status to database"""
        try:
            await db_manager.execute_update("""
                INSERT INTO ai_consultation_doctor_status 
                (is_available, reason, cost_budget_remaining, daily_usage, monthly_usage, 
                 last_updated, next_budget_reset, active_sessions, queue_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self._current_status.is_available,
                self._current_status.reason.value,
                self._current_status.cost_budget_remaining,
                self._current_status.daily_usage,
                self._current_status.monthly_usage,
                self._current_status.last_updated.isoformat(),
                self._current_status.next_budget_reset.isoformat() if self._current_status.next_budget_reset else None,
                self._current_status.active_sessions,
                self._current_status.queue_length
            ))
            
        except Exception as e:
            logger.error(f"Failed to persist status: {e}")
            raise
    
    async def _notify_status_change(self, event: StatusChangeEvent) -> None:
        """Notify all status change listeners"""
        for listener in self._status_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event)
                else:
                    listener(event)
            except Exception as e:
                logger.error(f"Status listener error: {e}")
    
    # Public API methods
    
    async def get_status(self) -> DoctorStatus:
        """Get current doctor status"""
        await self._refresh_feature_flags()
        await self._evaluate_status()
        return self._current_status
    
    async def set_status_manual(self, is_available: bool, user_id: str = "unknown") -> DoctorStatus:
        """Manually set doctor status"""
        try:
            # Check if manual control is allowed
            if not self._feature_flags_cache.get(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, True):
                raise ConsultationError(
                    "Manual status control is disabled",
                    error_code="MANUAL_CONTROL_DISABLED"
                )
            
            transition_type = StatusTransition.MANUAL_ENABLE if is_available else StatusTransition.MANUAL_DISABLE
            
            await self._update_status(
                is_available,
                DoctorStatusReason.MANUAL,
                transition_type,
                user_id
            )
            
            return self._current_status
            
        except Exception as e:
            logger.error(f"Failed to set manual status: {e}")
            raise
    
    @with_circuit_breaker('cost_tracking')
    async def track_cost(self, session_id: str, tokens_used: int, cost: float) -> None:
        """Track cost for a consultation session"""
        try:
            if not self._feature_flags_cache.get(FeatureFlag.COST_TRACKING.value, True):
                return
            
            # Update session cost
            self._session_costs[session_id] = self._session_costs.get(session_id, 0.0) + cost
            
            # Update daily and monthly usage
            self._daily_usage += cost
            self._monthly_usage += cost
            
            # Update budget status
            await self._update_budget_usage()
            
            # Get current budget status and broadcast update
            budget_status = await self.get_budget_status()
            await status_broadcaster.broadcast_budget_update(budget_status)
            await status_persistence.store_budget_status(budget_status)
            
            # Check if budget limits are exceeded
            if self._feature_flags_cache.get(FeatureFlag.BUDGET_ENFORCEMENT.value, True):
                if budget_status.daily_exhausted or budget_status.monthly_exhausted:
                    await self._evaluate_status()
            
            logger.debug(f"Tracked cost: ${cost:.4f} for session {session_id} ({tokens_used} tokens)")
            
        except Exception as e:
            logger.error(f"Failed to track cost: {e}")
            # Don't raise - cost tracking failures shouldn't break consultations
    
    async def _update_budget_usage(self) -> None:
        """Update budget usage in database"""
        try:
            await db_manager.execute_update("""
                UPDATE ai_consultation_budget 
                SET daily_spent = ?, monthly_spent = ?, last_reset = ?
                WHERE id = (SELECT id FROM ai_consultation_budget ORDER BY date DESC LIMIT 1)
            """, (
                self._daily_usage,
                self._monthly_usage,
                datetime.utcnow().isoformat()
            ))
            
        except Exception as e:
            logger.warning(f"Failed to update budget usage: {e}")
    
    async def get_budget_status(self) -> BudgetStatus:
        """Get current budget status"""
        try:
            daily_remaining = max(0, self.daily_budget - self._daily_usage)
            monthly_remaining = max(0, self.monthly_budget - self._monthly_usage)
            
            daily_percentage = (self._daily_usage / self.daily_budget) if self.daily_budget > 0 else 0
            monthly_percentage = (self._monthly_usage / self.monthly_budget) if self.monthly_budget > 0 else 0
            
            return BudgetStatus(
                daily_budget=self.daily_budget,
                monthly_budget=self.monthly_budget,
                daily_spent=self._daily_usage,
                monthly_spent=self._monthly_usage,
                daily_remaining=daily_remaining,
                monthly_remaining=monthly_remaining,
                daily_percentage=daily_percentage,
                monthly_percentage=monthly_percentage,
                daily_exhausted=daily_percentage >= 1.0,
                monthly_exhausted=monthly_percentage >= 1.0,
                daily_warning=daily_percentage >= self.warning_threshold,
                monthly_warning=monthly_percentage >= self.warning_threshold,
                daily_critical=daily_percentage >= self.critical_threshold,
                monthly_critical=monthly_percentage >= self.critical_threshold,
                cost_per_token=self.cost_per_token,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to get budget status: {e}")
            # Return safe default
            return BudgetStatus(
                daily_budget=0.0,
                monthly_budget=0.0,
                daily_spent=0.0,
                monthly_spent=0.0,
                daily_remaining=0.0,
                monthly_remaining=0.0,
                daily_percentage=1.0,
                monthly_percentage=1.0,
                daily_exhausted=True,
                monthly_exhausted=True,
                daily_warning=True,
                monthly_warning=True,
                daily_critical=True,
                monthly_critical=True,
                cost_per_token=self.cost_per_token,
                last_updated=datetime.utcnow()
            )
    
    async def get_cost_analytics(self, days: int = 30) -> CostAnalytics:
        """Get cost analytics for the specified period"""
        try:
            # Get historical cost data
            start_date = datetime.utcnow() - timedelta(days=days)
            
            results = await db_manager.execute_query("""
                SELECT 
                    DATE(timestamp) as date,
                    SUM(cost) as daily_cost,
                    SUM(tokens_used) as daily_tokens,
                    COUNT(*) as daily_queries
                FROM ai_consultation_results 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date.isoformat(),))
            
            # Calculate analytics
            total_cost = sum(row['daily_cost'] for row in results)
            total_tokens = sum(row['daily_tokens'] for row in results)
            total_queries = sum(row['daily_queries'] for row in results)
            
            avg_cost_per_query = total_cost / total_queries if total_queries > 0 else 0
            avg_cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
            
            # Calculate trends
            if len(results) >= 7:
                recent_week = results[-7:]
                previous_week = results[-14:-7] if len(results) >= 14 else []
                
                recent_avg = sum(row['daily_cost'] for row in recent_week) / 7
                previous_avg = sum(row['daily_cost'] for row in previous_week) / len(previous_week) if previous_week else recent_avg
                
                cost_trend = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
            else:
                cost_trend = 0.0
            
            return CostAnalytics(
                period_days=days,
                total_cost=total_cost,
                total_tokens=total_tokens,
                total_queries=total_queries,
                avg_cost_per_query=avg_cost_per_query,
                avg_cost_per_token=avg_cost_per_token,
                daily_costs=[row['daily_cost'] for row in results],
                cost_trend_percentage=cost_trend,
                budget_utilization_daily=self._daily_usage / self.daily_budget if self.daily_budget > 0 else 0,
                budget_utilization_monthly=self._monthly_usage / self.monthly_budget if self.monthly_budget > 0 else 0,
                projected_monthly_cost=self._daily_usage * 30,  # Simple projection
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to get cost analytics: {e}")
            # Return empty analytics
            return CostAnalytics(
                period_days=days,
                total_cost=0.0,
                total_tokens=0,
                total_queries=0,
                avg_cost_per_query=0.0,
                avg_cost_per_token=0.0,
                daily_costs=[],
                cost_trend_percentage=0.0,
                budget_utilization_daily=0.0,
                budget_utilization_monthly=0.0,
                projected_monthly_cost=0.0,
                last_updated=datetime.utcnow()
            )
    
    async def update_session_count(self, active_sessions: int) -> None:
        """Update active session count"""
        self._active_sessions = active_sessions
        if self._current_status:
            self._current_status.active_sessions = active_sessions
    
    async def update_queue_length(self, queue_length: int) -> None:
        """Update queue length"""
        self._queue_length = queue_length
        if self._current_status:
            self._current_status.queue_length = queue_length
    
    async def set_system_health(self, healthy: bool, error_message: str = None) -> None:
        """Update system health status"""
        old_health = self._system_healthy
        self._system_healthy = healthy
        
        if old_health != healthy:
            if healthy:
                logger.info("System health restored")
                await self._evaluate_status()
            else:
                logger.warning(f"System health degraded: {error_message}")
                await self._update_status(
                    False,
                    DoctorStatusReason.SYSTEM_ERROR,
                    StatusTransition.SYSTEM_ERROR,
                    "system",
                    {"error_message": error_message}
                )
    
    def add_status_listener(self, listener: Callable[[StatusChangeEvent], None]) -> None:
        """Add a status change listener"""
        self._status_listeners.append(listener)
    
    def remove_status_listener(self, listener: Callable[[StatusChangeEvent], None]) -> None:
        """Remove a status change listener"""
        if listener in self._status_listeners:
            self._status_listeners.remove(listener)
    
    async def reset_daily_budget(self) -> None:
        """Reset daily budget (called by scheduler)"""
        try:
            logger.info("Resetting daily budget")
            
            self._daily_usage = 0.0
            self._session_costs.clear()
            
            # Update next reset time
            if self._current_status:
                self._current_status.next_budget_reset = self._calculate_next_reset()
            
            # Update database
            await self._update_budget_usage()
            
            # Re-evaluate status (might become available again)
            await self._evaluate_status()
            
            logger.info("Daily budget reset completed")
            
        except Exception as e:
            logger.error(f"Failed to reset daily budget: {e}")
    
    async def get_session_cost(self, session_id: str) -> float:
        """Get cost for a specific session"""
        return self._session_costs.get(session_id, 0.0)
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            self._status_listeners.clear()
            self._session_costs.clear()
            logger.info("Doctor Status Manager cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global status manager instance
status_manager = DoctorStatusManager()


async def get_doctor_status() -> DoctorStatus:
    """Get current doctor status"""
    return await status_manager.get_status()


async def initialize_status_manager() -> None:
    """Initialize the status manager"""
    await status_manager.initialize()


async def cleanup_status_manager() -> None:
    """Cleanup the status manager"""
    await status_manager.cleanup()