"""
Operational risk protection systems for TaskQueueManager

This module implements comprehensive operational protection including:
- ConversationStateLifecycleManager for memory management and archival
- MemoryPressureMonitor with automated cleanup triggers
- RedisCircuitBreaker and operational resilience mechanisms
"""

import asyncio
import logging
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum, auto
import psutil
import gc
import weakref
from contextlib import asynccontextmanager

from .models import (
    ConversationContext,
    ConversationState,
    StateCheckpoint,
    PersistenceConfig,
)
from .error_recovery import CircuitBreaker, CircuitBreakerConfig


class LifecyclePhase(Enum):
    """Conversation state lifecycle phases."""
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVAL_READY = auto()
    ARCHIVED = auto()
    EXPIRED = auto()


class MemoryPressureLevel(Enum):
    """System memory pressure levels."""
    NORMAL = auto()
    MODERATE = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class LifecyclePolicy:
    """Policy configuration for conversation state lifecycle."""
    inactive_threshold_hours: int = 24
    archival_threshold_hours: int = 168  # 7 days
    expiration_threshold_hours: int = 720  # 30 days
    memory_cleanup_threshold_mb: int = 256
    max_active_conversations: int = 1000
    cleanup_interval_minutes: int = 60


@dataclass
class MemoryThresholds:
    """Memory pressure thresholds and actions."""
    moderate_threshold_percent: float = 70.0
    high_threshold_percent: float = 85.0
    critical_threshold_percent: float = 95.0
    cleanup_target_percent: float = 60.0
    monitoring_interval_seconds: int = 30


@dataclass
class ConversationLifecycleEntry:
    """Lifecycle tracking entry for conversation state."""
    conversation_id: str
    phase: LifecyclePhase
    last_access_time: datetime
    creation_time: datetime
    memory_size_bytes: int
    access_count: int
    archival_priority: float
    metadata: Dict[str, Any]


class ConversationStateLifecycleManager:
    """
    Comprehensive lifecycle manager for conversation states.

    Provides automated memory management, archival, and cleanup of conversation
    states based on configurable policies and memory pressure conditions.
    """

    def __init__(self, redis_client, persistence_config: PersistenceConfig,
                 lifecycle_policy: Optional[LifecyclePolicy] = None):
        self.redis_client = redis_client
        self.persistence_config = persistence_config
        self.policy = lifecycle_policy or LifecyclePolicy()
        self.instance_id = f"lifecycle_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.ConversationStateLifecycleManager")

        # Lifecycle tracking
        self._active_conversations: Dict[str, ConversationLifecycleEntry] = {}
        self._lifecycle_lock = threading.RLock()

        # Archival storage
        self._archival_queue: List[str] = []
        self._archival_lock = threading.Lock()

        # Background tasks
        self._cleanup_task = None
        self._monitoring_active = False
        self._shutdown_event = threading.Event()

        # Lifecycle metrics
        self._lifecycle_metrics = {
            "conversations_tracked": 0,
            "transitions_to_inactive": 0,
            "transitions_to_archival": 0,
            "conversations_archived": 0,
            "conversations_expired": 0,
            "cleanup_operations": 0,
            "memory_reclaimed_bytes": 0,
            "policy_violations": 0
        }

        self._logger.info(
            f"ConversationStateLifecycleManager initialized",
            extra={
                "instance_id": self.instance_id,
                "policy": asdict(self.policy),
                "persistence_config": asdict(self.persistence_config)
            }
        )

    async def start_lifecycle_monitoring(self):
        """Start background lifecycle monitoring and cleanup."""
        if self._monitoring_active:
            return

        try:
            self._monitoring_active = True
            self._cleanup_task = asyncio.create_task(self._lifecycle_monitoring_loop())

            self._logger.info("Lifecycle monitoring started")

        except Exception as e:
            self._logger.error(f"Error starting lifecycle monitoring: {e}")
            self._monitoring_active = False
            raise

    async def stop_lifecycle_monitoring(self):
        """Stop background lifecycle monitoring."""
        if not self._monitoring_active:
            return

        try:
            self._monitoring_active = False
            self._shutdown_event.set()

            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            self._logger.info("Lifecycle monitoring stopped")

        except Exception as e:
            self._logger.error(f"Error stopping lifecycle monitoring: {e}")

    async def track_conversation(self, conversation_context: ConversationContext) -> bool:
        """
        Start tracking conversation state lifecycle.

        Args:
            conversation_context: Conversation to track

        Returns:
            True if tracking started successfully
        """
        try:
            with self._lifecycle_lock:
                # Check if already tracked
                if conversation_context.conversation_id in self._active_conversations:
                    # Update access time
                    entry = self._active_conversations[conversation_context.conversation_id]
                    entry.last_access_time = datetime.now()
                    entry.access_count += 1
                    return True

                # Create new lifecycle entry
                memory_size = self._estimate_conversation_memory_size(conversation_context)

                entry = ConversationLifecycleEntry(
                    conversation_id=conversation_context.conversation_id,
                    phase=LifecyclePhase.ACTIVE,
                    last_access_time=datetime.now(),
                    creation_time=conversation_context.created_at,
                    memory_size_bytes=memory_size,
                    access_count=1,
                    archival_priority=0.0,
                    metadata=conversation_context.metadata.copy()
                )

                self._active_conversations[conversation_context.conversation_id] = entry
                self._lifecycle_metrics["conversations_tracked"] += 1

                # Check if exceeding max active conversations
                if len(self._active_conversations) > self.policy.max_active_conversations:
                    await self._trigger_emergency_cleanup()

                self._logger.info(
                    f"Started tracking conversation {conversation_context.conversation_id}",
                    extra={
                        "conversation_id": conversation_context.conversation_id,
                        "memory_size_bytes": memory_size,
                        "total_tracked": len(self._active_conversations)
                    }
                )

                return True

        except Exception as e:
            self._logger.error(f"Error tracking conversation {conversation_context.conversation_id}: {e}")
            return False

    async def update_conversation_access(self, conversation_id: str) -> bool:
        """
        Update last access time for a conversation.

        Args:
            conversation_id: ID of conversation to update

        Returns:
            True if update successful
        """
        try:
            with self._lifecycle_lock:
                if conversation_id in self._active_conversations:
                    entry = self._active_conversations[conversation_id]
                    entry.last_access_time = datetime.now()
                    entry.access_count += 1

                    # Reset to ACTIVE if was INACTIVE
                    if entry.phase == LifecyclePhase.INACTIVE:
                        entry.phase = LifecyclePhase.ACTIVE
                        self._logger.debug(f"Conversation {conversation_id} reactivated")

                    return True

                return False

        except Exception as e:
            self._logger.error(f"Error updating conversation access {conversation_id}: {e}")
            return False

    async def archive_conversation(self, conversation_id: str, force: bool = False) -> bool:
        """
        Archive a conversation state.

        Args:
            conversation_id: ID of conversation to archive
            force: Force archival regardless of policy

        Returns:
            True if archival successful
        """
        try:
            with self._lifecycle_lock:
                if conversation_id not in self._active_conversations:
                    return False

                entry = self._active_conversations[conversation_id]

                # Check if ready for archival
                if not force:
                    hours_since_access = (datetime.now() - entry.last_access_time).total_seconds() / 3600
                    if hours_since_access < self.policy.archival_threshold_hours:
                        return False

                # Move to archival queue
                with self._archival_lock:
                    if conversation_id not in self._archival_queue:
                        self._archival_queue.append(conversation_id)

                # Update phase
                entry.phase = LifecyclePhase.ARCHIVAL_READY
                self._lifecycle_metrics["transitions_to_archival"] += 1

                # Archive in Redis (move to cold storage)
                if self.redis_client:
                    archive_key = f"archived:{conversation_id}"
                    ttl = self.policy.expiration_threshold_hours * 3600  # Convert to seconds

                    # Store archival metadata
                    archival_data = {
                        "archived_at": datetime.now().isoformat(),
                        "original_creation": entry.creation_time.isoformat(),
                        "access_count": entry.access_count,
                        "archival_reason": "lifecycle_policy" if not force else "forced",
                        "instance_id": self.instance_id
                    }

                    await self.redis_client.hset(archive_key, mapping=archival_data)
                    await self.redis_client.expire(archive_key, ttl)

                # Update phase to archived
                entry.phase = LifecyclePhase.ARCHIVED
                self._lifecycle_metrics["conversations_archived"] += 1

                self._logger.info(
                    f"Conversation {conversation_id} archived successfully",
                    extra={
                        "conversation_id": conversation_id,
                        "forced": force,
                        "access_count": entry.access_count,
                        "age_hours": (datetime.now() - entry.creation_time).total_seconds() / 3600
                    }
                )

                return True

        except Exception as e:
            self._logger.error(f"Error archiving conversation {conversation_id}: {e}")
            return False

    async def _lifecycle_monitoring_loop(self):
        """Background loop for lifecycle monitoring and cleanup."""
        try:
            while self._monitoring_active and not self._shutdown_event.is_set():
                await self._perform_lifecycle_check()

                # Wait for next check interval
                await asyncio.sleep(self.policy.cleanup_interval_minutes * 60)

        except asyncio.CancelledError:
            self._logger.info("Lifecycle monitoring loop cancelled")
        except Exception as e:
            self._logger.error(f"Error in lifecycle monitoring loop: {e}")

    async def _perform_lifecycle_check(self):
        """Perform comprehensive lifecycle check and cleanup."""
        try:
            current_time = datetime.now()
            cleanup_candidates = []

            with self._lifecycle_lock:
                for conversation_id, entry in self._active_conversations.items():
                    hours_since_access = (current_time - entry.last_access_time).total_seconds() / 3600
                    hours_since_creation = (current_time - entry.creation_time).total_seconds() / 3600

                    # Check for phase transitions
                    if entry.phase == LifecyclePhase.ACTIVE:
                        if hours_since_access >= self.policy.inactive_threshold_hours:
                            entry.phase = LifecyclePhase.INACTIVE
                            self._lifecycle_metrics["transitions_to_inactive"] += 1

                    elif entry.phase == LifecyclePhase.INACTIVE:
                        if hours_since_access >= self.policy.archival_threshold_hours:
                            cleanup_candidates.append(conversation_id)

                    # Check for expiration
                    if hours_since_creation >= self.policy.expiration_threshold_hours:
                        cleanup_candidates.append(conversation_id)

            # Process cleanup candidates
            for conversation_id in cleanup_candidates:
                await self.archive_conversation(conversation_id)

            # Perform memory cleanup if needed
            memory_usage = self._get_current_memory_usage()
            if memory_usage > self.policy.memory_cleanup_threshold_mb:
                await self._cleanup_by_memory_pressure()

            self._lifecycle_metrics["cleanup_operations"] += 1

        except Exception as e:
            self._logger.error(f"Error in lifecycle check: {e}")

    async def _trigger_emergency_cleanup(self):
        """Trigger emergency cleanup when limits exceeded."""
        try:
            self._logger.warning("Triggering emergency cleanup - max conversations exceeded")

            # Sort by archival priority (least recently used + size)
            sorted_conversations = []

            with self._lifecycle_lock:
                for conv_id, entry in self._active_conversations.items():
                    if entry.phase in [LifecyclePhase.INACTIVE, LifecyclePhase.ACTIVE]:
                        priority = self._calculate_archival_priority(entry)
                        sorted_conversations.append((priority, conv_id))

            # Sort by priority (higher priority = more likely to archive)
            sorted_conversations.sort(reverse=True)

            # Archive top 25% of candidates
            archive_count = max(1, len(sorted_conversations) // 4)
            for i in range(min(archive_count, len(sorted_conversations))):
                _, conversation_id = sorted_conversations[i]
                await self.archive_conversation(conversation_id, force=True)

            self._logger.info(f"Emergency cleanup archived {archive_count} conversations")

        except Exception as e:
            self._logger.error(f"Error in emergency cleanup: {e}")

    def _calculate_archival_priority(self, entry: ConversationLifecycleEntry) -> float:
        """Calculate archival priority score (higher = more likely to archive)."""
        try:
            current_time = datetime.now()

            # Time factors
            hours_since_access = (current_time - entry.last_access_time).total_seconds() / 3600
            hours_since_creation = (current_time - entry.creation_time).total_seconds() / 3600

            # Base priority on time since last access
            time_priority = hours_since_access / self.policy.archival_threshold_hours

            # Memory size factor (larger conversations get higher priority)
            memory_priority = entry.memory_size_bytes / (1024 * 1024)  # Convert to MB

            # Access frequency factor (less accessed = higher priority)
            access_frequency = entry.access_count / max(1, hours_since_creation)
            frequency_priority = 1.0 / (1.0 + access_frequency)

            # Combined priority
            return time_priority + (memory_priority * 0.1) + (frequency_priority * 0.5)

        except Exception as e:
            self._logger.error(f"Error calculating archival priority: {e}")
            return 0.0

    def _estimate_conversation_memory_size(self, conversation_context: ConversationContext) -> int:
        """Estimate memory size of conversation context."""
        try:
            # Rough estimation based on content
            base_size = 1024  # Base overhead

            # History size
            history_size = sum(
                len(str(entry.get("content", ""))) + len(str(entry.get("metadata", {})))
                for entry in conversation_context.conversation_history
            )

            # Metadata size
            metadata_size = len(str(conversation_context.metadata))

            return base_size + history_size + metadata_size

        except Exception as e:
            self._logger.error(f"Error estimating memory size: {e}")
            return 1024  # Default estimate

    async def _cleanup_by_memory_pressure(self):
        """Perform cleanup based on memory pressure."""
        try:
            # Get conversations sorted by archival priority
            cleanup_candidates = []

            with self._lifecycle_lock:
                for conv_id, entry in self._active_conversations.items():
                    if entry.phase == LifecyclePhase.INACTIVE:
                        priority = self._calculate_archival_priority(entry)
                        cleanup_candidates.append((priority, conv_id, entry.memory_size_bytes))

            # Sort by priority and archive until memory pressure relieved
            cleanup_candidates.sort(key=lambda x: x[0], reverse=True)

            memory_reclaimed = 0
            target_memory = self.policy.memory_cleanup_threshold_mb * 1024 * 1024 * 0.25  # 25% of threshold

            for priority, conversation_id, memory_size in cleanup_candidates:
                if memory_reclaimed >= target_memory:
                    break

                if await self.archive_conversation(conversation_id, force=True):
                    memory_reclaimed += memory_size

            self._lifecycle_metrics["memory_reclaimed_bytes"] += memory_reclaimed

            self._logger.info(
                f"Memory pressure cleanup reclaimed {memory_reclaimed / (1024*1024):.1f}MB",
                extra={"conversations_archived": len([c for c in cleanup_candidates if c[1]])}
            )

        except Exception as e:
            self._logger.error(f"Error in memory pressure cleanup: {e}")

    def _get_current_memory_usage(self) -> int:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss // (1024 * 1024)
        except:
            return 0

    def get_lifecycle_status(self) -> Dict[str, Any]:
        """Get comprehensive lifecycle management status."""
        try:
            with self._lifecycle_lock:
                phase_counts = {phase.name: 0 for phase in LifecyclePhase}
                total_memory_bytes = 0

                for entry in self._active_conversations.values():
                    phase_counts[entry.phase.name] += 1
                    total_memory_bytes += entry.memory_size_bytes

            with self._archival_lock:
                archival_queue_size = len(self._archival_queue)

            return {
                "instance_id": self.instance_id,
                "monitoring_active": self._monitoring_active,
                "total_conversations": len(self._active_conversations),
                "phase_distribution": phase_counts,
                "total_memory_mb": total_memory_bytes / (1024 * 1024),
                "archival_queue_size": archival_queue_size,
                "policy": asdict(self.policy),
                "metrics": dict(self._lifecycle_metrics),
                "system_memory_mb": self._get_current_memory_usage(),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error getting lifecycle status: {e}")
            return {"error": str(e)}


class MemoryPressureMonitor:
    """
    System memory pressure monitor with automated cleanup triggers.

    Monitors system memory usage and triggers cleanup actions when
    thresholds are exceeded to maintain system stability.
    """

    def __init__(self, thresholds: Optional[MemoryThresholds] = None,
                 lifecycle_manager: Optional[ConversationStateLifecycleManager] = None):
        self.thresholds = thresholds or MemoryThresholds()
        self.lifecycle_manager = lifecycle_manager
        self.instance_id = f"memory_monitor_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.MemoryPressureMonitor")

        # Monitoring state
        self._monitoring_active = False
        self._monitor_task = None
        self._shutdown_event = threading.Event()

        # Pressure tracking
        self._current_pressure = MemoryPressureLevel.NORMAL
        self._pressure_history: List[Tuple[datetime, MemoryPressureLevel, float]] = []

        # Cleanup callbacks
        self._cleanup_callbacks: List[Callable[[], None]] = []

        # Memory metrics
        self._memory_metrics = {
            "pressure_level_changes": 0,
            "cleanup_triggers": 0,
            "emergency_cleanups": 0,
            "memory_reclaimed_mb": 0.0,
            "peak_memory_usage_percent": 0.0,
            "average_memory_usage_percent": 0.0
        }

        self._logger.info(
            f"MemoryPressureMonitor initialized",
            extra={
                "instance_id": self.instance_id,
                "thresholds": asdict(self.thresholds)
            }
        )

    async def start_monitoring(self):
        """Start memory pressure monitoring."""
        if self._monitoring_active:
            return

        try:
            self._monitoring_active = True
            self._monitor_task = asyncio.create_task(self._monitoring_loop())

            self._logger.info("Memory pressure monitoring started")

        except Exception as e:
            self._logger.error(f"Error starting memory monitoring: {e}")
            self._monitoring_active = False
            raise

    async def stop_monitoring(self):
        """Stop memory pressure monitoring."""
        if not self._monitoring_active:
            return

        try:
            self._monitoring_active = False
            self._shutdown_event.set()

            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass

            self._logger.info("Memory pressure monitoring stopped")

        except Exception as e:
            self._logger.error(f"Error stopping memory monitoring: {e}")

    def register_cleanup_callback(self, callback: Callable[[], None]):
        """
        Register callback for memory cleanup.

        Args:
            callback: Function to call when cleanup is needed
        """
        self._cleanup_callbacks.append(callback)
        self._logger.debug(f"Registered cleanup callback: {callback.__name__}")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self._monitoring_active and not self._shutdown_event.is_set():
                await self._check_memory_pressure()
                await asyncio.sleep(self.thresholds.monitoring_interval_seconds)

        except asyncio.CancelledError:
            self._logger.info("Memory monitoring loop cancelled")
        except Exception as e:
            self._logger.error(f"Error in memory monitoring loop: {e}")

    async def _check_memory_pressure(self):
        """Check current memory pressure and take actions."""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Update peak usage
            if memory_percent > self._memory_metrics["peak_memory_usage_percent"]:
                self._memory_metrics["peak_memory_usage_percent"] = memory_percent

            # Calculate moving average
            if self._pressure_history:
                recent_usage = [entry[2] for entry in self._pressure_history[-10:]]  # Last 10 readings
                self._memory_metrics["average_memory_usage_percent"] = sum(recent_usage) / len(recent_usage)

            # Determine pressure level
            previous_pressure = self._current_pressure

            if memory_percent >= self.thresholds.critical_threshold_percent:
                self._current_pressure = MemoryPressureLevel.CRITICAL
            elif memory_percent >= self.thresholds.high_threshold_percent:
                self._current_pressure = MemoryPressureLevel.HIGH
            elif memory_percent >= self.thresholds.moderate_threshold_percent:
                self._current_pressure = MemoryPressureLevel.MODERATE
            else:
                self._current_pressure = MemoryPressureLevel.NORMAL

            # Record pressure history
            self._pressure_history.append((datetime.now(), self._current_pressure, memory_percent))

            # Keep only last 100 readings
            if len(self._pressure_history) > 100:
                self._pressure_history = self._pressure_history[-50:]

            # Check for pressure level changes
            if self._current_pressure != previous_pressure:
                self._memory_metrics["pressure_level_changes"] += 1

                self._logger.info(
                    f"Memory pressure level changed: {previous_pressure.name} -> {self._current_pressure.name}",
                    extra={
                        "memory_percent": memory_percent,
                        "previous_pressure": previous_pressure.name,
                        "current_pressure": self._current_pressure.name
                    }
                )

                # Trigger appropriate actions
                await self._handle_pressure_change(self._current_pressure, memory_percent)

        except Exception as e:
            self._logger.error(f"Error checking memory pressure: {e}")

    async def _handle_pressure_change(self, pressure_level: MemoryPressureLevel, memory_percent: float):
        """Handle memory pressure level changes."""
        try:
            if pressure_level == MemoryPressureLevel.MODERATE:
                await self._trigger_gentle_cleanup()

            elif pressure_level == MemoryPressureLevel.HIGH:
                await self._trigger_aggressive_cleanup()

            elif pressure_level == MemoryPressureLevel.CRITICAL:
                await self._trigger_emergency_cleanup()

        except Exception as e:
            self._logger.error(f"Error handling pressure change: {e}")

    async def _trigger_gentle_cleanup(self):
        """Trigger gentle cleanup actions."""
        try:
            self._memory_metrics["cleanup_triggers"] += 1

            # Run garbage collection
            collected = gc.collect()

            # Trigger lifecycle cleanup
            if self.lifecycle_manager:
                await self.lifecycle_manager._cleanup_by_memory_pressure()

            # Run registered callbacks
            for callback in self._cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    self._logger.warning(f"Cleanup callback failed: {e}")

            self._logger.info(
                f"Gentle memory cleanup completed",
                extra={"gc_objects_collected": collected}
            )

        except Exception as e:
            self._logger.error(f"Error in gentle cleanup: {e}")

    async def _trigger_aggressive_cleanup(self):
        """Trigger aggressive cleanup actions."""
        try:
            self._memory_metrics["cleanup_triggers"] += 1

            # Force garbage collection
            for _ in range(3):
                gc.collect()

            # Trigger aggressive lifecycle cleanup
            if self.lifecycle_manager:
                await self.lifecycle_manager._trigger_emergency_cleanup()

            # Clear weak references
            weakref.finalize.finalize.run_all()

            self._logger.warning("Aggressive memory cleanup completed")

        except Exception as e:
            self._logger.error(f"Error in aggressive cleanup: {e}")

    async def _trigger_emergency_cleanup(self):
        """Trigger emergency cleanup actions."""
        try:
            self._memory_metrics["emergency_cleanups"] += 1

            # All aggressive cleanup actions
            await self._trigger_aggressive_cleanup()

            # Additional emergency actions
            if self.lifecycle_manager:
                # Force archive all inactive conversations
                with self.lifecycle_manager._lifecycle_lock:
                    emergency_candidates = [
                        conv_id for conv_id, entry in self.lifecycle_manager._active_conversations.items()
                        if entry.phase == LifecyclePhase.INACTIVE
                    ]

                for conversation_id in emergency_candidates:
                    await self.lifecycle_manager.archive_conversation(conversation_id, force=True)

            self._logger.critical(
                f"Emergency memory cleanup completed",
                extra={"conversations_archived": len(emergency_candidates) if self.lifecycle_manager else 0}
            )

        except Exception as e:
            self._logger.error(f"Error in emergency cleanup: {e}")

    def get_memory_status(self) -> Dict[str, Any]:
        """Get comprehensive memory monitoring status."""
        try:
            # Current system memory
            memory = psutil.virtual_memory()

            # Recent pressure readings
            recent_readings = self._pressure_history[-20:] if self._pressure_history else []

            return {
                "instance_id": self.instance_id,
                "monitoring_active": self._monitoring_active,
                "current_pressure_level": self._current_pressure.name,
                "system_memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_percent": memory.percent,
                    "free_gb": memory.free / (1024**3)
                },
                "thresholds": asdict(self.thresholds),
                "recent_readings": [
                    {
                        "timestamp": reading[0].isoformat(),
                        "pressure_level": reading[1].name,
                        "memory_percent": reading[2]
                    }
                    for reading in recent_readings
                ],
                "metrics": dict(self._memory_metrics),
                "registered_callbacks": len(self._cleanup_callbacks),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error getting memory status: {e}")
            return {"error": str(e)}


class RedisCircuitBreaker(CircuitBreaker):
    """
    Enhanced circuit breaker specifically for Redis operations.

    Extends base CircuitBreaker with Redis-specific failure detection
    and recovery mechanisms.
    """

    def __init__(self, config: CircuitBreakerConfig, redis_client):
        super().__init__(config)
        self.redis_client = redis_client
        self._logger = logging.getLogger(f"{__name__}.RedisCircuitBreaker")

        # Redis-specific metrics
        self._redis_metrics = {
            "connection_failures": 0,
            "timeout_failures": 0,
            "command_failures": 0,
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }

    async def execute_redis_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute Redis operation with circuit breaker protection.

        Args:
            operation_name: Name of the operation for logging
            operation_func: Redis operation function to execute
            *args, **kwargs: Arguments for the operation

        Returns:
            Result of the operation

        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            Exception: Original exception if operation fails
        """
        try:
            # Check circuit breaker state
            self._check_circuit_breaker()

            # Execute operation with timing
            start_time = time.time()
            result = await operation_func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Record success
            self._record_success()

            self._logger.debug(
                f"Redis operation {operation_name} succeeded",
                extra={
                    "operation": operation_name,
                    "execution_time_ms": execution_time * 1000
                }
            )

            return result

        except Exception as e:
            # Classify the error
            error_type = self._classify_redis_error(e)

            # Update metrics
            self._redis_metrics[f"{error_type}_failures"] += 1

            # Record failure
            self._record_failure()

            self._logger.warning(
                f"Redis operation {operation_name} failed",
                extra={
                    "operation": operation_name,
                    "error_type": error_type,
                    "error": str(e)
                }
            )

            raise

    def _classify_redis_error(self, error: Exception) -> str:
        """Classify Redis error type."""
        error_str = str(error).lower()

        if "connection" in error_str or "connect" in error_str:
            return "connection"
        elif "timeout" in error_str:
            return "timeout"
        else:
            return "command"

    async def test_redis_connectivity(self) -> bool:
        """
        Test Redis connectivity for circuit breaker recovery.

        Returns:
            True if Redis is accessible, False otherwise
        """
        try:
            self._redis_metrics["recovery_attempts"] += 1

            # Simple ping test
            await self.redis_client.ping()

            self._redis_metrics["successful_recoveries"] += 1

            self._logger.info("Redis connectivity test passed")
            return True

        except Exception as e:
            self._logger.warning(f"Redis connectivity test failed: {e}")
            return False

    def get_redis_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get Redis circuit breaker status and metrics."""
        base_status = self.get_status()

        return {
            **base_status,
            "redis_metrics": dict(self._redis_metrics),
            "timestamp": datetime.now().isoformat()
        }