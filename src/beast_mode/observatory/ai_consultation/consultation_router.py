"""
Consultation Router

Routes AI consultation requests between real-time and queue modes based on
system status, user permissions, and feature flags with brownfield safety.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .models import (
    ConsultationQuery, ConsultationResult, ProcessingMode, QueryPriority,
    DoctorStatusReason, ObservatoryContext
)
from .doctor_status_manager import DoctorStatusManager, get_doctor_status
from .security_manager import SecurityContext, PermissionLevel, ResourceType
from .observatory_context_provider import get_observatory_context, DataSensitivity
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError, ValidationError, ProcessingError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class RoutingDecision(str, Enum):
    """Routing decision types"""
    REAL_TIME = "real_time"
    QUEUE = "queue"
    REJECT = "reject"
    DEFER = "defer"


class RoutingReason(str, Enum):
    """Reasons for routing decisions"""
    DOCTOR_AVAILABLE = "doctor_available"
    DOCTOR_UNAVAILABLE = "doctor_unavailable"
    BUDGET_EXHAUSTED = "budget_exhausted"
    SYSTEM_OVERLOADED = "system_overloaded"
    USER_PREFERENCE = "user_preference"
    FEATURE_DISABLED = "feature_disabled"
    PERMISSION_DENIED = "permission_denied"
    VALIDATION_FAILED = "validation_failed"
    EMERGENCY_MODE = "emergency_mode"


@dataclass
class RoutingContext:
    """Context information for routing decisions"""
    query: ConsultationQuery
    security_context: Optional[SecurityContext]
    observatory_context: Optional[ObservatoryContext]
    doctor_status: Optional[Dict[str, Any]]
    system_load: Dict[str, Any]
    routing_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'query_id': self.query.query_id,
            'user_id': self.query.user_id,
            'priority': self.query.priority.value,
            'has_security_context': self.security_context is not None,
            'has_observatory_context': self.observatory_context is not None,
            'doctor_available': self.doctor_status.get('is_available', False) if self.doctor_status else False,
            'system_load': self.system_load,
            'routing_timestamp': self.routing_timestamp.isoformat()
        }


@dataclass
class RoutingResult:
    """Result of routing decision"""
    decision: RoutingDecision
    reason: RoutingReason
    processing_mode: Optional[ProcessingMode]
    estimated_wait_time: Optional[timedelta]
    cost_estimate: Optional[float]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'decision': self.decision.value,
            'reason': self.reason.value,
            'processing_mode': self.processing_mode.value if self.processing_mode else None,
            'estimated_wait_time_seconds': self.estimated_wait_time.total_seconds() if self.estimated_wait_time else None,
            'cost_estimate': self.cost_estimate,
            'metadata': self.metadata
        }


class ConsultationRouter:
    """
    Routes consultation requests between real-time and queue processing
    
    Features:
    - Intelligent mode determination based on system status
    - Feature flag integration for instant control
    - User permission and preference handling
    - Cost-aware routing decisions
    - Circuit breaker protection
    - Brownfield safety with Observatory integration
    - Load balancing and capacity management
    """
    
    def __init__(
        self,
        max_concurrent_realtime: int = 10,
        max_queue_size: int = 1000,
        cost_threshold_realtime: float = 5.0,
        load_threshold: float = 0.8,
        emergency_mode_threshold: float = 0.95
    ):
        self.max_concurrent_realtime = max_concurrent_realtime
        self.max_queue_size = max_queue_size
        self.cost_threshold_realtime = cost_threshold_realtime
        self.load_threshold = load_threshold
        self.emergency_mode_threshold = emergency_mode_threshold
        
        # Current system state
        self._active_realtime_sessions = 0
        self._current_queue_size = 0
        self._system_load_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'active_connections': 0,
            'response_time_avg': 0.0
        }
        
        # Routing statistics
        self._stats = {
            'total_requests': 0,
            'realtime_routed': 0,
            'queue_routed': 0,
            'rejected_requests': 0,
            'deferred_requests': 0,
            'routing_errors': 0,
            'avg_routing_time_ms': 0.0
        }
        
        # Emergency mode state
        self._emergency_mode = False
        self._emergency_mode_start = None
        
        # User preferences cache
        self._user_preferences: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> None:
        """Initialize the consultation router"""
        try:
            logger.info("Initializing Consultation Router")
            
            # Check if routing is enabled
            if not await feature_flags.is_enabled(FeatureFlag.AI_CONSULTATION_ENABLED):
                logger.info("AI consultation is disabled via feature flag")
                return
            
            # Initialize system load monitoring
            await self._update_system_load()
            
            logger.info("Consultation Router initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Consultation Router: {e}")
            # Don't raise - should degrade gracefully
    
    @with_circuit_breaker('consultation_routing')
    async def route_consultation(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """Route a consultation request to the appropriate processing mode"""
        start_time = datetime.utcnow()
        
        try:
            self._stats['total_requests'] += 1
            
            # Validate the query
            await self._validate_query(query, security_context)
            
            # Build routing context
            routing_context = await self._build_routing_context(
                query, security_context, user_preferences
            )
            
            # Make routing decision
            routing_result = await self._make_routing_decision(routing_context)
            
            # Update statistics
            await self._update_routing_stats(routing_result)
            
            # Log routing decision
            await self._log_routing_decision(routing_context, routing_result)
            
            # Update routing time
            routing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_avg_routing_time(routing_time)
            
            logger.info(f"Routed query {query.query_id} to {routing_result.decision.value} (reason: {routing_result.reason.value})")
            
            return routing_result
            
        except Exception as e:
            self._stats['routing_errors'] += 1
            logger.error(f"Routing failed for query {query.query_id}: {e}")
            
            # Return safe fallback routing
            return RoutingResult(
                decision=RoutingDecision.QUEUE,
                reason=RoutingReason.VALIDATION_FAILED,
                processing_mode=ProcessingMode.QUEUE,
                estimated_wait_time=timedelta(minutes=30),
                cost_estimate=None,
                metadata={'error': str(e), 'fallback': True}
            )
    
    async def _validate_query(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext]
    ) -> None:
        """Validate consultation query"""
        try:
            # Basic query validation
            if not query.query_text or len(query.query_text.strip()) == 0:
                raise ValidationError("Query text cannot be empty")
            
            if len(query.query_text) > 10000:
                raise ValidationError("Query text too long (max 10,000 characters)")
            
            # Check if user has permission to submit queries
            if security_context:
                from .security_manager import check_permission
                has_permission = await check_permission(
                    security_context,
                    ResourceType.SYSTEM_STATUS  # Basic permission for consultation
                )
                if not has_permission:
                    raise ValidationError("User does not have permission to submit consultations")
            
            # Check for potentially harmful content
            await self._validate_query_content(query.query_text)
            
        except Exception as e:
            logger.warning(f"Query validation failed: {e}")
            raise
    
    async def _validate_query_content(self, query_text: str) -> None:
        """Validate query content for safety"""
        try:
            # Basic content validation
            harmful_patterns = [
                'DROP TABLE',
                'DELETE FROM',
                'rm -rf',
                'sudo',
                '<script',
                'javascript:',
                'eval(',
                'exec('
            ]
            
            query_lower = query_text.lower()
            for pattern in harmful_patterns:
                if pattern.lower() in query_lower:
                    raise ValidationError(f"Query contains potentially harmful content: {pattern}")
            
            # Check for excessive repetition (potential spam)
            words = query_text.split()
            if len(words) > 10:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                max_repetition = max(word_counts.values())
                if max_repetition > len(words) * 0.5:  # More than 50% repetition
                    raise ValidationError("Query contains excessive repetition")
            
        except ValidationError:
            raise
        except Exception as e:
            logger.warning(f"Content validation error: {e}")
            # Don't fail on validation errors, just log
    
    async def _build_routing_context(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext],
        user_preferences: Optional[Dict[str, Any]]
    ) -> RoutingContext:
        """Build context for routing decision"""
        try:
            # Get doctor status
            doctor_status = None
            try:
                status = await get_doctor_status()
                doctor_status = {
                    'is_available': status.is_available,
                    'reason': status.reason.value,
                    'cost_budget_remaining': status.cost_budget_remaining,
                    'active_sessions': status.active_sessions,
                    'queue_length': status.queue_length
                }
            except Exception as e:
                logger.warning(f"Failed to get doctor status: {e}")
            
            # Get Observatory context if user has permissions
            observatory_context = None
            if security_context:
                try:
                    observatory_context = await get_observatory_context(
                        user_id=query.user_id,
                        security_context=security_context,
                        include_metrics=True,
                        include_alerts=True,
                        include_status=True
                    )
                except Exception as e:
                    logger.warning(f"Failed to get Observatory context: {e}")
            
            # Update system load
            await self._update_system_load()
            
            # Store user preferences
            if user_preferences:
                self._user_preferences[query.user_id] = user_preferences
            
            return RoutingContext(
                query=query,
                security_context=security_context,
                observatory_context=observatory_context,
                doctor_status=doctor_status,
                system_load=self._system_load_metrics.copy(),
                routing_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to build routing context: {e}")
            # Return minimal context
            return RoutingContext(
                query=query,
                security_context=security_context,
                observatory_context=None,
                doctor_status=None,
                system_load=self._system_load_metrics.copy(),
                routing_timestamp=datetime.utcnow()
            )
    
    async def _make_routing_decision(self, context: RoutingContext) -> RoutingResult:
        """Make intelligent routing decision based on context"""
        try:
            # Check emergency mode first
            if self._emergency_mode:
                return RoutingResult(
                    decision=RoutingDecision.REJECT,
                    reason=RoutingReason.EMERGENCY_MODE,
                    processing_mode=None,
                    estimated_wait_time=None,
                    cost_estimate=None,
                    metadata={'emergency_mode': True}
                )
            
            # Check feature flags
            realtime_enabled = await feature_flags.is_enabled(FeatureFlag.REAL_TIME_CHAT)
            queue_enabled = await feature_flags.is_enabled(FeatureFlag.QUERY_QUEUE)
            
            if not realtime_enabled and not queue_enabled:
                return RoutingResult(
                    decision=RoutingDecision.REJECT,
                    reason=RoutingReason.FEATURE_DISABLED,
                    processing_mode=None,
                    estimated_wait_time=None,
                    cost_estimate=None,
                    metadata={'features_disabled': True}
                )
            
            # Check doctor availability for real-time
            doctor_available = (
                context.doctor_status and 
                context.doctor_status.get('is_available', False)
            )
            
            # Check system capacity
            system_overloaded = await self._is_system_overloaded(context)
            
            # Check user preferences
            user_preference = self._get_user_routing_preference(context)
            
            # Make decision based on priority and conditions
            if context.query.priority == QueryPriority.URGENT:
                return await self._route_urgent_query(context, doctor_available, system_overloaded)
            elif context.query.priority == QueryPriority.HIGH:
                return await self._route_high_priority_query(context, doctor_available, system_overloaded)
            else:
                return await self._route_normal_query(context, doctor_available, system_overloaded, user_preference)
            
        except Exception as e:
            logger.error(f"Routing decision failed: {e}")
            # Safe fallback
            return RoutingResult(
                decision=RoutingDecision.QUEUE,
                reason=RoutingReason.VALIDATION_FAILED,
                processing_mode=ProcessingMode.QUEUE,
                estimated_wait_time=timedelta(minutes=30),
                cost_estimate=None,
                metadata={'error': str(e), 'fallback': True}
            )
    
    async def _route_urgent_query(
        self,
        context: RoutingContext,
        doctor_available: bool,
        system_overloaded: bool
    ) -> RoutingResult:
        """Route urgent priority queries"""
        # Urgent queries get priority for real-time if possible
        if doctor_available and not system_overloaded:
            if self._active_realtime_sessions < self.max_concurrent_realtime:
                return RoutingResult(
                    decision=RoutingDecision.REAL_TIME,
                    reason=RoutingReason.DOCTOR_AVAILABLE,
                    processing_mode=ProcessingMode.REAL_TIME,
                    estimated_wait_time=timedelta(seconds=30),
                    cost_estimate=await self._estimate_realtime_cost(context),
                    metadata={'priority': 'urgent', 'preemptive': True}
                )
        
        # Fallback to queue with high priority
        if await feature_flags.is_enabled(FeatureFlag.QUERY_QUEUE):
            return RoutingResult(
                decision=RoutingDecision.QUEUE,
                reason=RoutingReason.DOCTOR_UNAVAILABLE if not doctor_available else RoutingReason.SYSTEM_OVERLOADED,
                processing_mode=ProcessingMode.QUEUE,
                estimated_wait_time=await self._estimate_queue_wait_time(QueryPriority.URGENT),
                cost_estimate=await self._estimate_queue_cost(context),
                metadata={'priority': 'urgent', 'queue_position': 1}
            )
        
        # No options available
        return RoutingResult(
            decision=RoutingDecision.DEFER,
            reason=RoutingReason.SYSTEM_OVERLOADED,
            processing_mode=None,
            estimated_wait_time=timedelta(minutes=15),
            cost_estimate=None,
            metadata={'retry_after_minutes': 15}
        )
    
    async def _route_high_priority_query(
        self,
        context: RoutingContext,
        doctor_available: bool,
        system_overloaded: bool
    ) -> RoutingResult:
        """Route high priority queries"""
        # High priority gets real-time if doctor available and system not overloaded
        if doctor_available and not system_overloaded:
            if self._active_realtime_sessions < self.max_concurrent_realtime * 0.8:  # Reserve some capacity
                return RoutingResult(
                    decision=RoutingDecision.REAL_TIME,
                    reason=RoutingReason.DOCTOR_AVAILABLE,
                    processing_mode=ProcessingMode.REAL_TIME,
                    estimated_wait_time=timedelta(minutes=1),
                    cost_estimate=await self._estimate_realtime_cost(context),
                    metadata={'priority': 'high'}
                )
        
        # Route to queue
        if await feature_flags.is_enabled(FeatureFlag.QUERY_QUEUE):
            return RoutingResult(
                decision=RoutingDecision.QUEUE,
                reason=RoutingReason.DOCTOR_UNAVAILABLE if not doctor_available else RoutingReason.SYSTEM_OVERLOADED,
                processing_mode=ProcessingMode.QUEUE,
                estimated_wait_time=await self._estimate_queue_wait_time(QueryPriority.HIGH),
                cost_estimate=await self._estimate_queue_cost(context),
                metadata={'priority': 'high'}
            )
        
        return RoutingResult(
            decision=RoutingDecision.DEFER,
            reason=RoutingReason.SYSTEM_OVERLOADED,
            processing_mode=None,
            estimated_wait_time=timedelta(minutes=30),
            cost_estimate=None,
            metadata={'retry_after_minutes': 30}
        )
    
    async def _route_normal_query(
        self,
        context: RoutingContext,
        doctor_available: bool,
        system_overloaded: bool,
        user_preference: Optional[str]
    ) -> RoutingResult:
        """Route normal priority queries"""
        # Check user preference first
        if user_preference == "queue":
            if await feature_flags.is_enabled(FeatureFlag.QUERY_QUEUE):
                return RoutingResult(
                    decision=RoutingDecision.QUEUE,
                    reason=RoutingReason.USER_PREFERENCE,
                    processing_mode=ProcessingMode.QUEUE,
                    estimated_wait_time=await self._estimate_queue_wait_time(QueryPriority.NORMAL),
                    cost_estimate=await self._estimate_queue_cost(context),
                    metadata={'user_preference': 'queue'}
                )
        
        # Real-time if available and not overloaded
        if (doctor_available and not system_overloaded and 
            user_preference != "queue" and
            await feature_flags.is_enabled(FeatureFlag.REAL_TIME_CHAT)):
            
            if self._active_realtime_sessions < self.max_concurrent_realtime * 0.6:  # Conservative limit
                return RoutingResult(
                    decision=RoutingDecision.REAL_TIME,
                    reason=RoutingReason.DOCTOR_AVAILABLE,
                    processing_mode=ProcessingMode.REAL_TIME,
                    estimated_wait_time=timedelta(minutes=2),
                    cost_estimate=await self._estimate_realtime_cost(context),
                    metadata={'priority': 'normal'}
                )
        
        # Default to queue
        if await feature_flags.is_enabled(FeatureFlag.QUERY_QUEUE):
            return RoutingResult(
                decision=RoutingDecision.QUEUE,
                reason=RoutingReason.DOCTOR_UNAVAILABLE if not doctor_available else RoutingReason.SYSTEM_OVERLOADED,
                processing_mode=ProcessingMode.QUEUE,
                estimated_wait_time=await self._estimate_queue_wait_time(QueryPriority.NORMAL),
                cost_estimate=await self._estimate_queue_cost(context),
                metadata={'priority': 'normal'}
            )
        
        # No processing available
        return RoutingResult(
            decision=RoutingDecision.REJECT,
            reason=RoutingReason.FEATURE_DISABLED,
            processing_mode=None,
            estimated_wait_time=None,
            cost_estimate=None,
            metadata={'all_features_disabled': True}
        ) 
   
    async def _is_system_overloaded(self, context: RoutingContext) -> bool:
        """Check if system is overloaded"""
        try:
            # Check CPU and memory load
            if (context.system_load['cpu_percent'] > self.load_threshold * 100 or
                context.system_load['memory_percent'] > self.load_threshold * 100):
                return True
            
            # Check active connections
            if context.system_load['active_connections'] > self.max_concurrent_realtime * 2:
                return True
            
            # Check response time
            if context.system_load['response_time_avg'] > 5.0:  # 5 seconds
                return True
            
            # Check if we're approaching emergency mode
            overall_load = (
                context.system_load['cpu_percent'] / 100 +
                context.system_load['memory_percent'] / 100
            ) / 2
            
            if overall_load > self.emergency_mode_threshold:
                await self._enter_emergency_mode()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check system load: {e}")
            return True  # Assume overloaded on error
    
    def _get_user_routing_preference(self, context: RoutingContext) -> Optional[str]:
        """Get user routing preference"""
        try:
            user_prefs = self._user_preferences.get(context.query.user_id, {})
            return user_prefs.get('preferred_mode')
        except Exception as e:
            logger.warning(f"Failed to get user preference: {e}")
            return None
    
    async def _estimate_realtime_cost(self, context: RoutingContext) -> float:
        """Estimate cost for real-time processing"""
        try:
            # Base cost estimation
            base_cost = 0.10  # $0.10 base cost
            
            # Adjust based on query length
            query_length_factor = len(context.query.query_text) / 1000  # Per 1000 chars
            
            # Adjust based on Observatory context complexity
            context_factor = 1.0
            if context.observatory_context:
                metrics_count = context.observatory_context.metrics_summary.get('count', 0)
                alerts_count = context.observatory_context.active_alerts
                context_factor = 1.0 + (metrics_count + alerts_count) * 0.01
            
            # Priority multiplier
            priority_multiplier = {
                QueryPriority.LOW: 0.8,
                QueryPriority.NORMAL: 1.0,
                QueryPriority.HIGH: 1.2,
                QueryPriority.URGENT: 1.5
            }.get(context.query.priority, 1.0)
            
            estimated_cost = base_cost * (1 + query_length_factor) * context_factor * priority_multiplier
            
            return round(estimated_cost, 4)
            
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return 0.50  # Safe default
    
    async def _estimate_queue_cost(self, context: RoutingContext) -> float:
        """Estimate cost for queue processing"""
        try:
            # Queue processing is typically cheaper due to batching
            realtime_cost = await self._estimate_realtime_cost(context)
            queue_discount = 0.7  # 30% discount for queue processing
            
            return round(realtime_cost * queue_discount, 4)
            
        except Exception as e:
            logger.error(f"Queue cost estimation failed: {e}")
            return 0.35  # Safe default
    
    async def _estimate_queue_wait_time(self, priority: QueryPriority) -> timedelta:
        """Estimate wait time in queue based on priority"""
        try:
            # Base wait time based on current queue size
            base_wait_minutes = self._current_queue_size * 2  # 2 minutes per query
            
            # Priority adjustments
            priority_multiplier = {
                QueryPriority.URGENT: 0.1,   # Jump to front
                QueryPriority.HIGH: 0.3,     # Significant priority
                QueryPriority.NORMAL: 1.0,   # Normal wait
                QueryPriority.LOW: 1.5       # Longer wait
            }.get(priority, 1.0)
            
            estimated_minutes = max(5, base_wait_minutes * priority_multiplier)  # Minimum 5 minutes
            return timedelta(minutes=estimated_minutes)
            
        except Exception as e:
            logger.error(f"Wait time estimation failed: {e}")
            return timedelta(minutes=30)  # Safe default
    
    async def _update_system_load(self) -> None:
        """Update current system load metrics"""
        try:
            # In a real implementation, this would get actual system metrics
            # For now, simulate based on active sessions and queue size
            
            # Simulate CPU load based on active sessions
            cpu_load = min(100, (self._active_realtime_sessions / self.max_concurrent_realtime) * 60)
            
            # Simulate memory load
            memory_load = min(100, (self._current_queue_size / self.max_queue_size) * 40 + cpu_load * 0.5)
            
            # Simulate response time based on load
            response_time = 0.1 + (cpu_load / 100) * 2.0  # 0.1s to 2.1s
            
            self._system_load_metrics = {
                'cpu_percent': cpu_load,
                'memory_percent': memory_load,
                'active_connections': self._active_realtime_sessions,
                'response_time_avg': response_time,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update system load: {e}")
    
    async def _enter_emergency_mode(self) -> None:
        """Enter emergency mode to protect system"""
        if not self._emergency_mode:
            self._emergency_mode = True
            self._emergency_mode_start = datetime.utcnow()
            
            logger.warning("EMERGENCY MODE ACTIVATED - Rejecting new requests")
            
            # Schedule emergency mode exit
            asyncio.create_task(self._schedule_emergency_mode_exit())
    
    async def _schedule_emergency_mode_exit(self) -> None:
        """Schedule exit from emergency mode"""
        try:
            # Stay in emergency mode for at least 5 minutes
            await asyncio.sleep(300)
            
            # Check if system load has decreased
            await self._update_system_load()
            overall_load = (
                self._system_load_metrics['cpu_percent'] / 100 +
                self._system_load_metrics['memory_percent'] / 100
            ) / 2
            
            if overall_load < self.load_threshold:
                self._emergency_mode = False
                self._emergency_mode_start = None
                logger.info("Emergency mode deactivated - system load normalized")
            else:
                # Schedule another check
                asyncio.create_task(self._schedule_emergency_mode_exit())
                
        except Exception as e:
            logger.error(f"Emergency mode exit scheduling failed: {e}")
    
    async def _update_routing_stats(self, result: RoutingResult) -> None:
        """Update routing statistics"""
        try:
            if result.decision == RoutingDecision.REAL_TIME:
                self._stats['realtime_routed'] += 1
            elif result.decision == RoutingDecision.QUEUE:
                self._stats['queue_routed'] += 1
            elif result.decision == RoutingDecision.REJECT:
                self._stats['rejected_requests'] += 1
            elif result.decision == RoutingDecision.DEFER:
                self._stats['deferred_requests'] += 1
                
        except Exception as e:
            logger.error(f"Failed to update routing stats: {e}")
    
    def _update_avg_routing_time(self, routing_time_ms: float) -> None:
        """Update average routing time"""
        try:
            current_avg = self._stats['avg_routing_time_ms']
            total_requests = self._stats['total_requests']
            
            # Calculate new average
            if total_requests > 1:
                self._stats['avg_routing_time_ms'] = (
                    (current_avg * (total_requests - 1) + routing_time_ms) / total_requests
                )
            else:
                self._stats['avg_routing_time_ms'] = routing_time_ms
                
        except Exception as e:
            logger.error(f"Failed to update routing time: {e}")
    
    async def _log_routing_decision(
        self,
        context: RoutingContext,
        result: RoutingResult
    ) -> None:
        """Log routing decision for audit and analysis"""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'query_id': context.query.query_id,
                'user_id': context.query.user_id,
                'priority': context.query.priority.value,
                'decision': result.decision.value,
                'reason': result.reason.value,
                'processing_mode': result.processing_mode.value if result.processing_mode else None,
                'estimated_cost': result.cost_estimate,
                'estimated_wait_seconds': result.estimated_wait_time.total_seconds() if result.estimated_wait_time else None,
                'system_load': context.system_load,
                'doctor_available': context.doctor_status.get('is_available', False) if context.doctor_status else False,
                'emergency_mode': self._emergency_mode,
                'metadata': result.metadata
            }
            
            # Log at appropriate level based on decision
            if result.decision == RoutingDecision.REJECT:
                logger.warning(f"Consultation request rejected: {log_data}")
            elif result.decision == RoutingDecision.DEFER:
                logger.info(f"Consultation request deferred: {log_data}")
            else:
                logger.info(f"Consultation request routed: {log_data}")
                
        except Exception as e:
            logger.error(f"Failed to log routing decision: {e}")
    
    # Public API methods for system management
    
    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get current routing statistics"""
        try:
            await self._update_system_load()
            
            return {
                'routing_stats': self._stats.copy(),
                'system_state': {
                    'active_realtime_sessions': self._active_realtime_sessions,
                    'current_queue_size': self._current_queue_size,
                    'emergency_mode': self._emergency_mode,
                    'emergency_mode_duration': (
                        (datetime.utcnow() - self._emergency_mode_start).total_seconds()
                        if self._emergency_mode_start else None
                    )
                },
                'system_load': self._system_load_metrics.copy(),
                'capacity': {
                    'max_concurrent_realtime': self.max_concurrent_realtime,
                    'max_queue_size': self.max_queue_size,
                    'realtime_utilization': self._active_realtime_sessions / self.max_concurrent_realtime,
                    'queue_utilization': self._current_queue_size / self.max_queue_size
                },
                'thresholds': {
                    'cost_threshold_realtime': self.cost_threshold_realtime,
                    'load_threshold': self.load_threshold,
                    'emergency_mode_threshold': self.emergency_mode_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get routing stats: {e}")
            return {'error': str(e)}
    
    async def update_capacity(
        self,
        max_concurrent_realtime: Optional[int] = None,
        max_queue_size: Optional[int] = None
    ) -> bool:
        """Update system capacity limits"""
        try:
            if max_concurrent_realtime is not None:
                if max_concurrent_realtime < 1 or max_concurrent_realtime > 100:
                    raise ValueError("max_concurrent_realtime must be between 1 and 100")
                self.max_concurrent_realtime = max_concurrent_realtime
                logger.info(f"Updated max concurrent realtime sessions to {max_concurrent_realtime}")
            
            if max_queue_size is not None:
                if max_queue_size < 10 or max_queue_size > 10000:
                    raise ValueError("max_queue_size must be between 10 and 10000")
                self.max_queue_size = max_queue_size
                logger.info(f"Updated max queue size to {max_queue_size}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update capacity: {e}")
            return False
    
    async def force_emergency_mode(self, enable: bool) -> bool:
        """Force emergency mode on/off (admin function)"""
        try:
            if enable and not self._emergency_mode:
                await self._enter_emergency_mode()
                logger.warning("Emergency mode FORCE ENABLED by admin")
            elif not enable and self._emergency_mode:
                self._emergency_mode = False
                self._emergency_mode_start = None
                logger.info("Emergency mode FORCE DISABLED by admin")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to force emergency mode: {e}")
            return False
    
    async def get_health_status(self) -> ComponentHealth:
        """Get router health status"""
        try:
            await self._update_system_load()
            
            # Determine health status
            if self._emergency_mode:
                status = "critical"
                error_message = "System in emergency mode"
            elif self._system_load_metrics['cpu_percent'] > 90:
                status = "degraded"
                error_message = "High CPU load"
            elif self._system_load_metrics['memory_percent'] > 90:
                status = "degraded"
                error_message = "High memory usage"
            elif self._active_realtime_sessions >= self.max_concurrent_realtime:
                status = "degraded"
                error_message = "Real-time capacity exhausted"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="consultation_router",
                status=status,
                response_time=self._stats['avg_routing_time_ms'],
                error_message=error_message,
                metadata={
                    'active_sessions': self._active_realtime_sessions,
                    'queue_size': self._current_queue_size,
                    'emergency_mode': self._emergency_mode,
                    'total_requests': self._stats['total_requests'],
                    'success_rate': (
                        (self._stats['realtime_routed'] + self._stats['queue_routed']) / 
                        max(1, self._stats['total_requests'])
                    )
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="consultation_router",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    # Session management methods
    
    async def register_realtime_session(self, session_id: str) -> bool:
        """Register a new real-time session"""
        try:
            if self._active_realtime_sessions < self.max_concurrent_realtime:
                self._active_realtime_sessions += 1
                logger.info(f"Registered real-time session {session_id} ({self._active_realtime_sessions}/{self.max_concurrent_realtime})")
                return True
            else:
                logger.warning(f"Cannot register session {session_id} - capacity exhausted")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register session {session_id}: {e}")
            return False
    
    async def unregister_realtime_session(self, session_id: str) -> bool:
        """Unregister a real-time session"""
        try:
            if self._active_realtime_sessions > 0:
                self._active_realtime_sessions -= 1
                logger.info(f"Unregistered real-time session {session_id} ({self._active_realtime_sessions}/{self.max_concurrent_realtime})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister session {session_id}: {e}")
            return False
    
    async def update_queue_size(self, size: int) -> None:
        """Update current queue size"""
        try:
            self._current_queue_size = max(0, size)
            
        except Exception as e:
            logger.error(f"Failed to update queue size: {e}")


# Global router instance
_consultation_router: Optional[ConsultationRouter] = None


async def get_consultation_router() -> ConsultationRouter:
    """Get the global consultation router instance"""
    global _consultation_router
    
    if _consultation_router is None:
        _consultation_router = ConsultationRouter()
        await _consultation_router.initialize()
    
    return _consultation_router


async def route_consultation_request(
    query: ConsultationQuery,
    security_context: Optional[SecurityContext] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> RoutingResult:
    """Route a consultation request (convenience function)"""
    router = await get_consultation_router()
    return await router.route_consultation(query, security_context, user_preferences):
                self._stats['rejected_requests'] += 1
            elif result.decision == RoutingDecision.DEFER:
                self._stats['deferred_requests'] += 1
                
        except Exception as e:
            logger.error(f"Failed to update routing stats: {e}")
    
    def _update_avg_routing_time(self, routing_time_ms: float) -> None:
        """Update average routing time"""
        try:
            current_avg = self._stats['avg_routing_time_ms']
            total_requests = self._stats['total_requests']
            
            # Calculate new average
            new_avg = ((current_avg * (total_requests - 1)) + routing_time_ms) / total_requests
            self._stats['avg_routing_time_ms'] = round(new_avg, 2)
            
        except Exception as e:
            logger.error(f"Failed to update routing time: {e}")
    
    async def _log_routing_decision(
        self,
        context: RoutingContext,
        result: RoutingResult
    ) -> None:
        """Log routing decision for audit and debugging"""
        try:
            log_data = {
                'routing_context': context.to_dict(),
                'routing_result': result.to_dict(),
                'system_state': {
                    'active_realtime_sessions': self._active_realtime_sessions,
                    'current_queue_size': self._current_queue_size,
                    'emergency_mode': self._emergency_mode
                }
            }
            
            logger.info(f"ROUTING_DECISION: {result.decision.value} for {context.query.query_id} - {result.reason.value}")
            logger.debug(f"Routing details: {log_data}")
            
        except Exception as e:
            logger.error(f"Failed to log routing decision: {e}")
    
    # Public API methods for system state updates
    
    async def update_realtime_sessions(self, count: int) -> None:
        """Update active real-time session count"""
        self._active_realtime_sessions = max(0, count)
        await self._update_system_load()
    
    async def update_queue_size(self, size: int) -> None:
        """Update current queue size"""
        self._current_queue_size = max(0, size)
        await self._update_system_load()
    
    async def set_user_preference(
        self,
        user_id: str,
        preferred_mode: str,
        max_cost: Optional[float] = None
    ) -> None:
        """Set user routing preferences"""
        try:
            self._user_preferences[user_id] = {
                'preferred_mode': preferred_mode,
                'max_cost': max_cost,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            logger.debug(f"Updated routing preference for {user_id}: {preferred_mode}")
            
        except Exception as e:
            logger.error(f"Failed to set user preference: {e}")
    
    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            **self._stats,
            'active_realtime_sessions': self._active_realtime_sessions,
            'current_queue_size': self._current_queue_size,
            'emergency_mode': self._emergency_mode,
            'emergency_mode_duration': (
                (datetime.utcnow() - self._emergency_mode_start).total_seconds()
                if self._emergency_mode_start else None
            ),
            'system_load': self._system_load_metrics,
            'capacity_utilization': {
                'realtime': self._active_realtime_sessions / self.max_concurrent_realtime,
                'queue': self._current_queue_size / self.max_queue_size
            }
        }
    
    async def health_check(self) -> ComponentHealth:
        """Perform health check"""
        try:
            # Calculate health metrics
            realtime_utilization = self._active_realtime_sessions / self.max_concurrent_realtime
            queue_utilization = self._current_queue_size / self.max_queue_size
            error_rate = self._stats['routing_errors'] / max(1, self._stats['total_requests'])
            
            # Determine health status
            if self._emergency_mode:
                status = "unhealthy"
                error_message = "System in emergency mode"
            elif realtime_utilization > 0.9 or queue_utilization > 0.9:
                status = "degraded"
                error_message = "High capacity utilization"
            elif error_rate > 0.1:
                status = "degraded"
                error_message = "High routing error rate"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="consultation_router",
                status=status,
                response_time=self._stats['avg_routing_time_ms'],
                error_message=error_message,
                metadata={
                    "realtime_utilization": realtime_utilization,
                    "queue_utilization": queue_utilization,
                    "error_rate": error_rate,
                    "emergency_mode": self._emergency_mode,
                    "total_requests": self._stats['total_requests'],
                    "routing_distribution": {
                        "realtime": self._stats['realtime_routed'],
                        "queue": self._stats['queue_routed'],
                        "rejected": self._stats['rejected_requests'],
                        "deferred": self._stats['deferred_requests']
                    }
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="consultation_router",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def cleanup(self) -> None:
        """Cleanup router resources"""
        try:
            self._user_preferences.clear()
            logger.info("Consultation Router cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global router instance
consultation_router = ConsultationRouter()


async def route_consultation(
    query: ConsultationQuery,
    security_context: Optional[SecurityContext] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> RoutingResult:
    """Route a consultation request"""
    return await consultation_router.route_consultation(query, security_context, user_preferences)


async def initialize_router() -> None:
    """Initialize the consultation router"""
    await consultation_router.initialize()


async def cleanup_router() -> None:
    """Cleanup the consultation router"""
    await consultation_router.cleanup()