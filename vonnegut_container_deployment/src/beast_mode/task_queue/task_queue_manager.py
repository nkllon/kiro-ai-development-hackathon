"""
TaskQueueManager - Redis-backed task queue manager as ReflectiveModule

This module implements the TaskQueueManager as a ReflectiveModule, providing
the main entry point for Claude Code hook integration with comprehensive
health monitoring and non-blocking operations.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import asdict

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)

from .models import (
    ConversationState,
    TaskState,
    TaskQueueConfig,
    ConversationContext,
    TaskContext,
    TaskResult,
    TaskFailure,
    HookEvent,
)
from .state_machine import ConversationStateMachine, TaskStateMachine
from .persistence import StatePersistenceManager
from .coordination import DistributedConversationCoordinator
from .redis_operations import RedisTaskQueueOperations
from .task_processor import TaskProcessor
from .metrics import TaskQueueMetrics, MetricsCollector
from .error_recovery import (
    ErrorRecoveryManager,
    RetryConfig,
    CircuitBreakerConfig,
    ErrorType,
    with_error_recovery,
)
from .state_protection import (
    StatePersistenceStrategy,
    EnhancedStateIntegrityMonitor,
    ConversationStateLockManager,
    PersistenceLayer,
)
from .task_protection import (
    TaskDeduplicationManager,
    IdempotentTaskProcessor,
    PriorityTaskScheduler,
    TaskPriority,
    TaskSecurityValidator,
    TaskExecutionSandbox,
    ConversationStateEncryption,
    SecurityThreatLevel,
)


class TaskQueueManager(ReflectiveModule):
    """
    TaskQueueManager as ReflectiveModule - Main entry point for Claude Code integration.

    Provides non-blocking task queue operations with comprehensive state management,
    health monitoring, and hook integration capabilities.
    """

    def __init__(self, config: TaskQueueConfig, redis_client=None):
        super().__init__()
        self.config = config
        self.redis_client = redis_client
        self._logger = logging.getLogger(f"{__name__}.TaskQueueManager")

        # Initialize core components
        self.conversation_state_machine = None
        self.persistence_manager = None
        self.coordinator = None
        self.redis_ops = None
        self.task_processor = None

        # Health tracking
        self._last_successful_operation = datetime.now()
        self._consecutive_failures = 0
        self._total_tasks_processed = 0
        self._total_tasks_failed = 0
        self._redis_connection_healthy = True

        # Performance metrics
        self._queue_size_history = []
        self._processing_latency_history = []
        self._last_metrics_collection = datetime.now()

        # Graceful degradation state
        self._degraded_capabilities = set()
        self._fallback_mode = False

        # Initialize metrics collection
        self.metrics = TaskQueueMetrics()
        self.metrics_collector = MetricsCollector(self.metrics)

        # Initialize error recovery system
        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay_seconds=1.0,
            max_delay_seconds=30.0,
            exponential_base=2.0,
            jitter_factor=0.1
        )
        circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout_seconds=60,
            half_open_max_calls=3
        )
        self.error_recovery = ErrorRecoveryManager(retry_config, circuit_breaker_config)

        # Initialize state protection components
        self.state_persistence_strategy = None
        self.integrity_monitor = None
        self.state_lock_manager = None

        # Initialize task protection components
        self.task_deduplication = None
        self.idempotent_processor = None
        self.priority_scheduler = None

        # Initialize security components
        self.security_validator = None
        self.execution_sandbox = None
        self.state_encryption = None

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all TaskQueueManager components."""
        try:
            if self.redis_client:
                # Initialize persistence manager
                self.persistence_manager = StatePersistenceManager(
                    self.redis_client,
                    self.config.persistence_config
                )

                # Initialize coordinator
                self.coordinator = DistributedConversationCoordinator(
                    self.redis_client,
                    self.config.coordination_config
                )

                # Initialize Redis operations
                self.redis_ops = RedisTaskQueueOperations(
                    self.redis_client,
                    self.config.security_settings
                )

                # Initialize task processor
                self.task_processor = TaskProcessor(
                    self.redis_ops,
                    self.persistence_manager,
                    self.config
                )

                # Initialize state protection components
                self.state_persistence_strategy = StatePersistenceStrategy(
                    self.redis_client,
                    self.config.persistence_config
                )

                self.integrity_monitor = EnhancedStateIntegrityMonitor(
                    self.redis_client,
                    self.state_persistence_strategy
                )

                self.state_lock_manager = ConversationStateLockManager(
                    self.redis_client
                )

                # Start continuous integrity monitoring
                asyncio.create_task(self.integrity_monitor.start_continuous_monitoring())

                # Initialize task protection components
                self.task_deduplication = TaskDeduplicationManager(
                    self.redis_client,
                    processing_timeout=600  # 10 minutes for complex tasks
                )

                self.idempotent_processor = IdempotentTaskProcessor(
                    self.redis_client,
                    result_ttl=86400  # 24 hours
                )

                self.priority_scheduler = PriorityTaskScheduler(
                    self.redis_client,
                    age_boost_threshold=300  # 5 minutes
                )

                # Initialize security components
                self.security_validator = TaskSecurityValidator(
                    security_patterns=self.config.security_settings.dangerous_patterns,
                    max_content_length=self.config.security_settings.max_content_length
                )

                self.execution_sandbox = TaskExecutionSandbox(
                    max_execution_time=300,  # 5 minutes
                    max_memory_mb=512       # 512MB limit
                )

                self.state_encryption = ConversationStateEncryption()

                self._logger.info("Task protection and security components initialized successfully")

            # Initialize conversation state machine (works without Redis)
            initial_context = ConversationContext(
                conversation_id=str(uuid.uuid4()),
                current_state=ConversationState.IDLE,
                created_at=datetime.now(),
                turns=[]
            )

            self.conversation_state_machine = ConversationStateMachine(
                initial_context,
                self.persistence_manager
            )

            self._logger.info("TaskQueueManager components initialized successfully")

            # Update metrics for successful initialization
            self.metrics.update_redis_connection_status(self._redis_connection_healthy)

        except Exception as e:
            self._logger.error(f"Failed to initialize TaskQueueManager components: {e}")
            self._redis_connection_healthy = False
            self._degraded_capabilities.add(ModuleCapability.DATA_PROCESSING)

            # Update metrics for failed initialization
            self.metrics.update_redis_connection_status(False)

    async def check_and_process_tasks(self) -> Dict[str, Any]:
        """
        Main hook entry point - Check for tasks and process them non-blocking.

        This is the primary method called by Claude Code hooks.
        Returns immediately with status info, processing continues in background.

        Returns:
            Dict containing operation status and immediate results
        """
        operation_start = time.time()

        # Collect system metrics
        self.metrics_collector.collect_system_metrics(self)

        try:
            # Quick health check
            if not self._is_ready():
                return {
                    "status": "degraded",
                    "message": "TaskQueueManager not ready",
                    "timestamp": datetime.now().isoformat(),
                    "tasks_available": 0,
                    "processing_latency_ms": 0
                }

            # Non-blocking task check
            queue_status = await self._get_queue_status()

            if queue_status["tasks_available"] > 0:
                # Start background processing (fire and forget)
                asyncio.create_task(self._process_tasks_background())

                return {
                    "status": "processing_started",
                    "message": f"Started processing {queue_status['tasks_available']} tasks",
                    "timestamp": datetime.now().isoformat(),
                    "tasks_available": queue_status["tasks_available"],
                    "processing_latency_ms": (time.time() - operation_start) * 1000
                }
            else:
                return {
                    "status": "no_tasks",
                    "message": "No tasks available for processing",
                    "timestamp": datetime.now().isoformat(),
                    "tasks_available": 0,
                    "processing_latency_ms": (time.time() - operation_start) * 1000
                }

        except Exception as e:
            self._logger.error(f"Error in check_and_process_tasks: {e}")
            self._consecutive_failures += 1

            # Record hook execution metrics
            duration_seconds = time.time() - operation_start
            self.metrics.record_hook_execution(duration_seconds)
            self.metrics.update_consecutive_failures(self._consecutive_failures)

            return {
                "status": "error",
                "message": f"Task processing error: {str(e)[:100]}",
                "timestamp": datetime.now().isoformat(),
                "tasks_available": 0,
                "processing_latency_ms": duration_seconds * 1000
            }

        finally:
            # Always record hook execution time
            duration_seconds = time.time() - operation_start
            self.metrics.record_hook_execution(duration_seconds)

    async def _get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status quickly."""
        if not self.redis_ops:
            return {"tasks_available": 0, "queue_health": "degraded"}

        try:
            # Use error recovery for Redis operations
            async def _check_redis_health():
                await self.redis_client.ping()
                return True

            async def _get_queue_size():
                return await self.redis_ops.get_queue_size(
                    self.config.queue_config.task_queue_name
                )

            # Execute Redis operations with recovery
            await self.error_recovery.execute_with_recovery(
                _check_redis_health,
                ErrorType.REDIS_CONNECTION_ERROR,
                "redis_ping"
            )

            pending_tasks = await self.error_recovery.execute_with_recovery(
                _get_queue_size,
                ErrorType.REDIS_CONNECTION_ERROR,
                "get_queue_size"
            )

            # Update queue size metrics
            self.metrics.update_queue_size(
                self.config.queue_config.task_queue_name,
                pending_tasks
            )

            # Update Redis connection health
            if not self._redis_connection_healthy:
                self._redis_connection_healthy = True
                self.metrics.update_redis_connection_status(True)
                self._logger.info("Redis connection recovered")

            return {
                "tasks_available": pending_tasks,
                "queue_health": "healthy"
            }

        except Exception as e:
            self._logger.warning(f"Queue status check failed: {e}")

            # Classify and handle the error
            error_type = self.error_recovery.classify_error(e)

            # Update connection health if it's a Redis error
            if error_type in [ErrorType.REDIS_CONNECTION_ERROR, ErrorType.REDIS_TIMEOUT_ERROR]:
                if self._redis_connection_healthy:
                    self._redis_connection_healthy = False
                    self.metrics.update_redis_connection_status(False)
                    self._logger.error("Redis connection lost")

            return {"tasks_available": 0, "queue_health": "unhealthy"}

    async def _process_tasks_background(self):
        """Background task processing with state management."""
        try:
            # Trigger conversation state transition
            hook_event = HookEvent(
                event_type="claude_code_hook",
                timestamp=datetime.now(),
                metadata={"source": "task_queue_manager"}
            )

            await self.conversation_state_machine.handle_transition(
                ConversationState.IDLE,
                ConversationState.HOOK_TRIGGERED,
                hook_event
            )

            # Process available tasks
            while True:
                task_result = await self._process_single_task()

                if not task_result["task_found"]:
                    break

                if task_result["success"]:
                    self._total_tasks_processed += 1
                    self._last_successful_operation = datetime.now()
                    self._consecutive_failures = 0
                else:
                    self._total_tasks_failed += 1
                    self._consecutive_failures += 1

            # Return to idle state
            await self.conversation_state_machine.handle_transition(
                self.conversation_state_machine.context.current_state,
                ConversationState.IDLE,
                hook_event
            )

        except Exception as e:
            self._logger.error(f"Background processing error: {e}")
            self._consecutive_failures += 1

    async def _process_single_task(self) -> Dict[str, Any]:
        """Process a single task from the queue."""
        if not self.task_processor:
            return {"task_found": False, "success": False, "error": "No task processor"}

        try:
            # Dequeue next task
            task_context = await self.redis_ops.dequeue_task(
                self.config.queue_config.task_queue_name
            )

            if not task_context:
                return {"task_found": False, "success": True}

            # Process the task
            result = await self.task_processor.process_task(task_context)

            return {
                "task_found": True,
                "success": result.success,
                "task_id": task_context.task_id,
                "processing_time": result.processing_time_ms
            }

        except Exception as e:
            self._logger.error(f"Single task processing error: {e}")
            return {"task_found": True, "success": False, "error": str(e)}

    def _is_ready(self) -> bool:
        """Check if manager is ready for operations."""
        if self._fallback_mode:
            return True  # Always ready in fallback mode

        # Check Redis connectivity
        if not self._redis_connection_healthy:
            return False

        # Check if too many consecutive failures
        if self._consecutive_failures >= self.config.max_consecutive_failures:
            return False

        return True

    # ReflectiveModule implementation

    def get_module_info(self) -> Dict[str, Any]:
        """Get TaskQueueManager module information."""
        return {
            "module_name": "TaskQueueManager",
            "module_version": "1.0.0",
            "description": "Redis-backed task queue manager for Claude Code integration",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "configuration": {
                "redis_enabled": bool(self.redis_client),
                "fallback_mode": self._fallback_mode,
                "max_task_size": self.config.queue_config.max_task_size,
                "queue_name": self.config.queue_config.task_queue_name,
            },
            "statistics": {
                "total_tasks_processed": self._total_tasks_processed,
                "total_tasks_failed": self._total_tasks_failed,
                "consecutive_failures": self._consecutive_failures,
                "uptime_hours": (datetime.now() - self._start_time).total_seconds() / 3600,
            }
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get current TaskQueueManager capabilities."""
        base_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION,
        ]

        if self.redis_client and self._redis_connection_healthy:
            base_capabilities.append(ModuleCapability.DATA_PROCESSING)
            base_capabilities.append(ModuleCapability.API_INTEGRATION)

        # Remove degraded capabilities
        return [cap for cap in base_capabilities if cap not in self._degraded_capabilities]

    def get_health_status(self) -> ModuleHealth:
        """Get comprehensive health status."""
        # Determine overall status
        if self._consecutive_failures >= self.config.max_consecutive_failures:
            status = ModuleStatus.ERROR
        elif self._consecutive_failures > 0 or not self._redis_connection_healthy:
            status = ModuleStatus.WARNING
        elif self._fallback_mode:
            status = ModuleStatus.DEGRADED
        else:
            status = ModuleStatus.HEALTHY

        # Calculate health score (0.0 to 1.0)
        health_score = 1.0
        if self._consecutive_failures > 0:
            health_score -= min(0.5, self._consecutive_failures * 0.1)
        if not self._redis_connection_healthy:
            health_score -= 0.3
        if self._fallback_mode:
            health_score -= 0.2

        # Collect issues
        issues = []
        if self._consecutive_failures > 0:
            issues.append(f"Consecutive failures: {self._consecutive_failures}")
        if not self._redis_connection_healthy:
            issues.append("Redis connection unhealthy")
        if self._fallback_mode:
            issues.append("Running in fallback mode")
        if len(self._degraded_capabilities) > 0:
            issues.append(f"Degraded capabilities: {[cap.value for cap in self._degraded_capabilities]}")

        return ModuleHealth(
            module_id=f"TaskQueueManager-{id(self)}",
            status=status,
            health_score=max(0.0, health_score),
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._total_tasks_failed,
            warning_count=self._consecutive_failures
        )

    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation when issues occur."""
        try:
            remaining_capabilities = []
            degraded_capabilities = []

            # Always keep core functionality
            remaining_capabilities.append(ModuleCapability.CORE_FUNCTIONALITY)
            remaining_capabilities.append(ModuleCapability.MONITORING)

            # Degrade Redis-dependent capabilities if needed
            if not self._redis_connection_healthy:
                self._fallback_mode = True
                degraded_capabilities.extend([
                    ModuleCapability.DATA_PROCESSING,
                    ModuleCapability.API_INTEGRATION
                ])
                self._logger.warning("Entered fallback mode due to Redis connectivity issues")
            else:
                remaining_capabilities.extend([
                    ModuleCapability.DATA_PROCESSING,
                    ModuleCapability.API_INTEGRATION
                ])

            # Always keep validation
            remaining_capabilities.append(ModuleCapability.VALIDATION)

            self._degraded_capabilities.update(degraded_capabilities)

            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities,
                error_message=None
            )

        except Exception as e:
            self._logger.error(f"Graceful degradation failed: {e}")
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                error_message=str(e)
            )

    # Additional TaskQueueManager-specific methods

    async def get_queue_metrics(self) -> Dict[str, Any]:
        """Get detailed queue performance metrics."""
        if not self.redis_ops:
            return {"error": "Redis operations not available"}

        try:
            current_time = datetime.now()

            # Collect current metrics
            queue_size = await self.redis_ops.get_queue_size(
                self.config.queue_config.task_queue_name
            )

            # Update history
            self._queue_size_history.append((current_time, queue_size))

            # Keep only recent history (last hour)
            cutoff_time = current_time - timedelta(hours=1)
            self._queue_size_history = [
                (t, size) for t, size in self._queue_size_history
                if t > cutoff_time
            ]

            # Calculate metrics
            avg_queue_size = sum(size for _, size in self._queue_size_history) / len(self._queue_size_history) if self._queue_size_history else 0
            max_queue_size = max((size for _, size in self._queue_size_history), default=0)

            return {
                "current_queue_size": queue_size,
                "average_queue_size_1h": avg_queue_size,
                "max_queue_size_1h": max_queue_size,
                "total_processed": self._total_tasks_processed,
                "total_failed": self._total_tasks_failed,
                "success_rate": self._total_tasks_processed / max(1, self._total_tasks_processed + self._total_tasks_failed),
                "last_successful_operation": self._last_successful_operation.isoformat(),
                "consecutive_failures": self._consecutive_failures,
                "health_score": self.get_health_status().health_score
            }

        except Exception as e:
            self._logger.error(f"Error getting queue metrics: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check endpoint."""
        health_status = self.get_health_status()
        queue_metrics = await self.get_queue_metrics()

        return {
            "status": health_status.status.value,
            "health_score": health_status.health_score,
            "issues": health_status.issues,
            "uptime_seconds": health_status.uptime_seconds,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "metrics": queue_metrics,
            "timestamp": datetime.now().isoformat()
        }

    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check for deployment orchestration."""
        is_ready = self._is_ready()

        return {
            "ready": is_ready,
            "reason": "healthy" if is_ready else "not ready for operations",
            "checks": {
                "redis_connectivity": self._redis_connection_healthy,
                "consecutive_failures_ok": self._consecutive_failures < self.config.max_consecutive_failures,
                "fallback_mode": self._fallback_mode
            },
            "timestamp": datetime.now().isoformat()
        }

    def metrics_endpoint(self) -> tuple[str, str]:
        """
        Prometheus metrics endpoint.

        Returns:
            Tuple of (metrics_content, content_type)
        """
        # Update metrics before returning
        self.metrics_collector.collect_system_metrics(self)

        # Return Prometheus formatted metrics
        return self.metrics.get_metrics_output()

    async def metrics_json_endpoint(self) -> Dict[str, Any]:
        """
        JSON metrics endpoint for REST API integration.

        Returns:
            Dict containing current metrics and system status
        """
        # Update metrics before returning
        self.metrics_collector.collect_system_metrics(self)

        # Get health and queue metrics
        health_status = self.get_health_status()
        queue_metrics = await self.get_queue_metrics()

        # Get metrics summary
        metrics_summary = self.metrics.get_metrics_summary()

        # Get collector info
        collector_info = self.metrics_collector.get_collector_info()

        # Get error recovery status
        recovery_status = self.error_recovery.get_recovery_status()

        return {
            "health": {
                "status": health_status.status.value,
                "health_score": health_status.health_score,
                "issues": health_status.issues,
                "uptime_seconds": health_status.uptime_seconds
            },
            "queue_metrics": queue_metrics,
            "prometheus_metrics": metrics_summary,
            "collector_info": collector_info,
            "error_recovery": recovery_status,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "timestamp": datetime.now().isoformat()
        }

    async def error_recovery_test(self) -> Dict[str, Any]:
        """
        Test error recovery mechanisms.

        Returns:
            Dict containing test results for all recovery mechanisms
        """
        try:
            test_results = await self.error_recovery.test_recovery_mechanisms()

            return {
                "test_status": "completed",
                "results": test_results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "test_status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def secure_state_operation(self, conversation_id: str, operation_func,
                                   *args, **kwargs) -> Any:
        """
        Execute state operation with distributed locking and integrity protection.

        This method provides a secure wrapper for state operations that require
        consistency guarantees across distributed TaskQueueManager instances.

        Args:
            conversation_id: ID of conversation to lock
            operation_func: Function to execute with state protection
            *args, **kwargs: Arguments to pass to operation_func

        Returns:
            Result of operation_func

        Usage:
            result = await manager.secure_state_operation(
                "conv_123",
                self._update_conversation_state,
                new_state_data
            )
        """
        if not self.state_lock_manager:
            # Fallback to direct execution if lock manager not available
            self._logger.warning(
                f"State lock manager not available, executing {operation_func.__name__} without locking",
                extra={"conversation_id": conversation_id}
            )
            return await operation_func(*args, **kwargs)

        try:
            # Execute operation with distributed lock protection
            async with self.state_lock_manager.acquire_conversation_lock(
                conversation_id, "write", timeout=30
            ) as lock:

                self._logger.debug(
                    f"Executing secure state operation: {operation_func.__name__}",
                    extra={
                        "conversation_id": conversation_id,
                        "lock_id": lock.lock_id,
                        "operation": operation_func.__name__
                    }
                )

                # Execute the operation
                result = await operation_func(*args, **kwargs)

                return result

        except Exception as e:
            self._logger.error(
                f"Error in secure state operation {operation_func.__name__}: {e}",
                extra={"conversation_id": conversation_id}
            )
            raise

    async def persist_state_with_protection(self, context: ConversationContext,
                                          required_layers: Optional[Set[PersistenceLayer]] = None) -> Dict[str, Any]:
        """
        Persist conversation state with full protection (integrity + multi-layer).

        Args:
            context: Conversation context to persist
            required_layers: Specific persistence layers to use

        Returns:
            Dict containing persistence results and integrity verification
        """
        if not self.state_persistence_strategy:
            self._logger.error("State persistence strategy not available")
            return {"error": "State persistence not available", "success": False}

        try:
            self._logger.info(
                f"Starting protected state persistence for conversation {context.conversation_id}",
                extra={"conversation_id": context.conversation_id}
            )

            # Execute persistence with integrity checking
            persistence_results = await self.state_persistence_strategy.persist_state_secure(
                context, required_layers
            )

            # Check overall success
            successful_layers = [layer for layer, result in persistence_results.items() if result.success]
            total_layers = len(persistence_results)
            success_rate = len(successful_layers) / max(1, total_layers)

            # Trigger integrity check if we have successful persistence
            integrity_report = None
            if successful_layers:
                integrity_report = await self.integrity_monitor.check_conversation_integrity(
                    context.conversation_id
                )

            result = {
                "success": success_rate > 0.5,  # Consider successful if >50% layers succeed
                "persistence_results": {
                    layer.value: {
                        "success": result.success,
                        "state_hash": result.state_hash,
                        "timestamp": result.timestamp.isoformat(),
                        "integrity_verified": result.integrity_verified,
                        "error": result.error_message
                    }
                    for layer, result in persistence_results.items()
                },
                "successful_layers": [layer.value for layer in successful_layers],
                "success_rate": success_rate,
                "integrity_report": {
                    "overall_status": integrity_report.overall_status.value,
                    "corruption_detected": integrity_report.corruption_detected,
                    "recovery_recommended": integrity_report.recovery_recommended
                } if integrity_report else None,
                "timestamp": datetime.now().isoformat()
            }

            self._logger.info(
                f"Protected state persistence completed",
                extra={
                    "conversation_id": context.conversation_id,
                    "success_rate": success_rate,
                    "successful_layers": len(successful_layers)
                }
            )

            return result

        except Exception as e:
            self._logger.error(f"Error in protected state persistence: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def check_system_state_integrity(self) -> Dict[str, Any]:
        """
        Perform comprehensive system state integrity check.

        Returns:
            Dict containing complete integrity analysis
        """
        if not self.integrity_monitor:
            return {"error": "Integrity monitor not available"}

        try:
            self._logger.info("Starting comprehensive system state integrity check")

            # Perform system-wide integrity check
            integrity_results = await self.integrity_monitor.perform_system_integrity_check()

            # Get persistence strategy metrics
            persistence_metrics = self.state_persistence_strategy.get_persistence_metrics() if self.state_persistence_strategy else {}

            # Get lock manager status
            lock_metrics = self.state_lock_manager.get_lock_metrics() if self.state_lock_manager else {}

            # Get integrity monitor metrics
            integrity_metrics = self.integrity_monitor.get_integrity_metrics()

            return {
                "integrity_check": integrity_results,
                "persistence_metrics": persistence_metrics,
                "lock_metrics": lock_metrics,
                "integrity_monitor_metrics": integrity_metrics,
                "system_health": {
                    "state_protection_enabled": all([
                        self.state_persistence_strategy is not None,
                        self.integrity_monitor is not None,
                        self.state_lock_manager is not None
                    ]),
                    "redis_connectivity": self._redis_connection_healthy,
                    "monitoring_active": integrity_metrics.get("monitoring_active", False)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error in system state integrity check: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def cleanup_expired_locks(self) -> Dict[str, Any]:
        """
        Clean up expired conversation locks.

        Returns:
            Dict containing cleanup results
        """
        if not self.state_lock_manager:
            return {"error": "State lock manager not available"}

        try:
            self._logger.info("Starting expired locks cleanup")

            cleaned_count = await self.state_lock_manager.force_release_expired_locks()

            return {
                "cleanup_successful": True,
                "expired_locks_cleaned": cleaned_count,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error in expired locks cleanup: {e}")
            return {
                "cleanup_successful": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def shutdown_state_protection(self):
        """Gracefully shutdown all state protection components."""
        self._logger.info("Shutting down state protection components")

        # Stop integrity monitoring
        if self.integrity_monitor:
            try:
                self.integrity_monitor.stop_monitoring()
                self._logger.info("Integrity monitor stopped")
            except Exception as e:
                self._logger.error(f"Error stopping integrity monitor: {e}")

        # Shutdown lock manager
        if self.state_lock_manager:
            try:
                await self.state_lock_manager.shutdown()
                self._logger.info("State lock manager shutdown complete")
            except Exception as e:
                self._logger.error(f"Error shutting down lock manager: {e}")

        self._logger.info("State protection shutdown complete")

    async def process_task_with_protection(self, task: TaskContext,
                                         priority: TaskPriority = TaskPriority.NORMAL) -> Dict[str, Any]:
        """
        Process task with full protection (deduplication + idempotency + priority).

        Args:
            task: Task to process
            priority: Task priority level

        Returns:
            Dict containing processing results and protection status
        """
        processing_start = time.time()

        try:
            self._logger.info(
                f"Starting protected task processing for {task.task_id}",
                extra={"task_id": task.task_id, "priority": priority.value}
            )

            # Step 1: Check deduplication
            if not self.task_deduplication:
                return {"error": "Task deduplication not available", "success": False}

            # Check if task already processed
            if await self.task_deduplication.is_task_already_processed(task.task_id):
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "Task already processed",
                    "task_id": task.task_id,
                    "processing_time_ms": (time.time() - processing_start) * 1000
                }

            # Step 2: Claim task for processing
            claim = await self.task_deduplication.claim_task_for_processing(task.task_id)
            if not claim:
                return {
                    "success": False,
                    "skipped": True,
                    "reason": "Task already claimed by another instance",
                    "task_id": task.task_id,
                    "processing_time_ms": (time.time() - processing_start) * 1000
                }

            try:
                # Step 3: Process with idempotency
                if self.idempotent_processor:
                    result = await self.idempotent_processor.process_task_idempotently(
                        task,
                        self._execute_task_logic
                    )
                else:
                    # Fallback to direct processing
                    result = await self._execute_task_logic(task)

                # Step 4: Complete task processing
                await self.task_deduplication.complete_task_processing(task.task_id, result)

                processing_duration = time.time() - processing_start

                response = {
                    "success": True,
                    "task_id": task.task_id,
                    "result": asdict(result),
                    "priority": priority.value,
                    "claim_id": claim.claim_key,
                    "processing_time_ms": processing_duration * 1000,
                    "protection_features": {
                        "deduplication": True,
                        "idempotency": self.idempotent_processor is not None,
                        "priority_scheduling": self.priority_scheduler is not None
                    }
                }

                self._logger.info(
                    f"Protected task processing completed successfully",
                    extra={
                        "task_id": task.task_id,
                        "processing_time_ms": processing_duration * 1000,
                        "result_success": result.success
                    }
                )

                return response

            except Exception as e:
                # Mark task as failed and release claim
                failure = TaskFailure(
                    task_id=task.task_id,
                    error_message=str(e),
                    failed_at=datetime.now(),
                    retry_count=0
                )

                await self.task_deduplication.fail_task_processing(task.task_id, failure)

                return {
                    "success": False,
                    "task_id": task.task_id,
                    "error": str(e),
                    "claim_id": claim.claim_key,
                    "processing_time_ms": (time.time() - processing_start) * 1000
                }

        except Exception as e:
            self._logger.error(f"Error in protected task processing: {e}")
            return {
                "success": False,
                "task_id": task.task_id,
                "error": str(e),
                "processing_time_ms": (time.time() - processing_start) * 1000
            }

    async def _execute_task_logic(self, task: TaskContext) -> TaskResult:
        """
        Execute the actual task processing logic.

        This is a placeholder that would be replaced with actual task execution.
        In a real implementation, this would delegate to appropriate task handlers.
        """
        execution_start = time.time()

        try:
            # Simulate task processing (replace with actual logic)
            await asyncio.sleep(0.1)  # Simulate work

            # Return successful result
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result={"status": "completed", "task_type": task.task_type},
                processing_time_ms=(time.time() - execution_start) * 1000
            )

        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                processing_time_ms=(time.time() - execution_start) * 1000
            )

    async def enqueue_task_with_priority(self, task: TaskContext,
                                       priority: TaskPriority = TaskPriority.NORMAL) -> Dict[str, Any]:
        """
        Enqueue task with priority scheduling.

        Args:
            task: Task to enqueue
            priority: Priority level for the task

        Returns:
            Dict containing enqueue results
        """
        if not self.priority_scheduler:
            return {"error": "Priority scheduler not available", "success": False}

        try:
            success = await self.priority_scheduler.enqueue_task(task, priority)

            return {
                "success": success,
                "task_id": task.task_id,
                "priority": priority.value,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error enqueueing task {task.task_id}: {e}")
            return {
                "success": False,
                "task_id": task.task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_next_priority_task(self) -> Dict[str, Any]:
        """
        Get next task using priority scheduling with starvation prevention.

        Returns:
            Dict containing task and priority information
        """
        if not self.priority_scheduler:
            return {"error": "Priority scheduler not available"}

        try:
            result = await self.priority_scheduler.get_next_task_with_fairness()

            if result:
                task_context, priority = result
                return {
                    "success": True,
                    "task": asdict(task_context),
                    "priority": priority.value,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "task": None,
                    "message": "No tasks available",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self._logger.error(f"Error getting next priority task: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_task_protection_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive task protection metrics.

        Returns:
            Dict containing all task protection metrics
        """
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "task_protection_enabled": all([
                    self.task_deduplication is not None,
                    self.idempotent_processor is not None,
                    self.priority_scheduler is not None
                ])
            }

            # Deduplication metrics
            if self.task_deduplication:
                metrics["deduplication"] = self.task_deduplication.get_deduplication_metrics()

            # Idempotency metrics
            if self.idempotent_processor:
                metrics["idempotency"] = self.idempotent_processor.get_idempotency_metrics()

            # Scheduling metrics
            if self.priority_scheduler:
                metrics["scheduling"] = self.priority_scheduler.get_scheduling_metrics()

            return metrics

        except Exception as e:
            self._logger.error(f"Error getting task protection metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_priority_queue_status(self) -> Dict[str, Any]:
        """
        Get status of all priority queues.

        Returns:
            Dict containing queue status information
        """
        if not self.priority_scheduler:
            return {"error": "Priority scheduler not available"}

        try:
            return await self.priority_scheduler.get_queue_status()

        except Exception as e:
            self._logger.error(f"Error getting priority queue status: {e}")
            return {"error": str(e)}

    async def cleanup_task_protection(self) -> Dict[str, Any]:
        """
        Perform maintenance cleanup for task protection components.

        Returns:
            Dict containing cleanup results
        """
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "cleanup_operations": []
            }

            # Clean up expired claims
            if self.task_deduplication:
                expired_claims = await self.task_deduplication.cleanup_expired_claims()
                results["cleanup_operations"].append({
                    "component": "task_deduplication",
                    "operation": "cleanup_expired_claims",
                    "items_cleaned": expired_claims
                })

            # Additional cleanup operations could be added here

            return results

        except Exception as e:
            self._logger.error(f"Error in task protection cleanup: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def invalidate_task_idempotency(self, task: TaskContext) -> Dict[str, Any]:
        """
        Invalidate cached idempotent result for a task.

        Args:
            task: Task to invalidate idempotency for

        Returns:
            Dict containing invalidation results
        """
        if not self.idempotent_processor:
            return {"error": "Idempotent processor not available"}

        try:
            invalidated = await self.idempotent_processor.invalidate_idempotent_result(task)

            return {
                "success": True,
                "invalidated": invalidated,
                "task_id": task.task_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error invalidating task idempotency: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id,
                "timestamp": datetime.now().isoformat()
            }

    # Security Integration Methods

    async def process_task_with_full_security(self, task: TaskContext,
                                            priority: TaskPriority = TaskPriority.NORMAL) -> Dict[str, Any]:
        """
        Process task with comprehensive security validation, sandboxing, and protection.

        Args:
            task: Task to process with full security
            priority: Task priority level

        Returns:
            Dict containing processing results and security status
        """
        processing_start = time.time()
        security_report = {
            "security_scan": None,
            "sandbox_execution": None,
            "protection_features": {
                "security_validation": self.security_validator is not None,
                "sandboxed_execution": self.execution_sandbox is not None,
                "state_encryption": self.state_encryption is not None,
                "deduplication": self.task_deduplication is not None,
                "idempotency": self.idempotent_processor is not None,
                "priority_scheduling": self.priority_scheduler is not None
            }
        }

        try:
            self._logger.info(
                f"Starting secure task processing for {task.task_id}",
                extra={"task_id": task.task_id, "priority": priority.value}
            )

            # Step 1: Security content validation
            if self.security_validator:
                scan_result = await self.security_validator.scan_task_content(task)
                security_report["security_scan"] = {
                    "threat_level": scan_result.threat_level.value,
                    "safe_to_process": scan_result.safe_to_process,
                    "threats_detected": len(scan_result.threats_detected),
                    "scan_duration_ms": scan_result.scan_duration_ms
                }

                if not scan_result.safe_to_process:
                    return {
                        "success": False,
                        "task_id": task.task_id,
                        "error": f"Task failed security validation: {scan_result.threat_level.value}",
                        "security_report": security_report,
                        "processing_time_ms": (time.time() - processing_start) * 1000
                    }

                # Use sanitized content if available
                if scan_result.sanitized_content and scan_result.threat_level == SecurityThreatLevel.LOW_RISK:
                    task.content = scan_result.sanitized_content
                    self._logger.info(f"Using sanitized content for task {task.task_id}")

            else:
                self._logger.warning("Security validator not available - processing without security validation")

            # Step 2: Proceed with protected processing
            if self.task_deduplication:
                # Check if task already processed
                if await self.task_deduplication.is_task_already_processed(task.task_id):
                    return {
                        "success": True,
                        "skipped": True,
                        "reason": "Task already processed",
                        "task_id": task.task_id,
                        "security_report": security_report,
                        "processing_time_ms": (time.time() - processing_start) * 1000
                    }

                # Claim task for processing
                claim = await self.task_deduplication.claim_task_for_processing(task.task_id)
                if not claim:
                    return {
                        "success": False,
                        "skipped": True,
                        "reason": "Task already claimed by another instance",
                        "task_id": task.task_id,
                        "security_report": security_report,
                        "processing_time_ms": (time.time() - processing_start) * 1000
                    }

                try:
                    # Step 3: Sandboxed execution
                    if self.execution_sandbox:
                        # Process with idempotency in sandbox
                        if self.idempotent_processor:
                            async def sandboxed_idempotent_processor(t):
                                return await self.idempotent_processor.process_task_idempotently(
                                    t, self._execute_task_logic
                                )

                            sandbox_result = await self.execution_sandbox.execute_task_safely(
                                task, sandboxed_idempotent_processor
                            )
                        else:
                            sandbox_result = await self.execution_sandbox.execute_task_safely(
                                task, self._execute_task_logic
                            )

                        security_report["sandbox_execution"] = {
                            "execution_successful": sandbox_result.execution_successful,
                            "execution_time_ms": sandbox_result.execution_time_ms,
                            "security_violations": len(sandbox_result.security_violations or []),
                            "resource_usage": sandbox_result.resource_usage
                        }

                        if not sandbox_result.execution_successful:
                            await self.task_deduplication.fail_task_processing(
                                task.task_id,
                                TaskFailure(
                                    task_id=task.task_id,
                                    error_message=sandbox_result.error_message or "Sandbox execution failed",
                                    failed_at=datetime.now(),
                                    retry_count=0
                                )
                            )

                            return {
                                "success": False,
                                "task_id": task.task_id,
                                "error": f"Sandboxed execution failed: {sandbox_result.error_message}",
                                "security_report": security_report,
                                "processing_time_ms": (time.time() - processing_start) * 1000
                            }

                        result = sandbox_result.result

                    else:
                        # Fallback to regular protected processing
                        if self.idempotent_processor:
                            result = await self.idempotent_processor.process_task_idempotently(
                                task, self._execute_task_logic
                            )
                        else:
                            result = await self._execute_task_logic(task)

                    # Step 4: Complete task processing
                    await self.task_deduplication.complete_task_processing(task.task_id, result)

                    processing_duration = time.time() - processing_start

                    response = {
                        "success": True,
                        "task_id": task.task_id,
                        "result": asdict(result) if hasattr(result, '__dict__') else result,
                        "priority": priority.value,
                        "claim_id": claim.claim_key,
                        "processing_time_ms": processing_duration * 1000,
                        "security_report": security_report
                    }

                    self._logger.info(
                        f"Secure task processing completed successfully",
                        extra={
                            "task_id": task.task_id,
                            "processing_time_ms": processing_duration * 1000,
                            "security_validated": security_report["security_scan"] is not None,
                            "sandboxed": security_report["sandbox_execution"] is not None
                        }
                    )

                    return response

                except Exception as e:
                    # Mark task as failed and release claim
                    failure = TaskFailure(
                        task_id=task.task_id,
                        error_message=str(e),
                        failed_at=datetime.now(),
                        retry_count=0
                    )

                    await self.task_deduplication.fail_task_processing(task.task_id, failure)

                    return {
                        "success": False,
                        "task_id": task.task_id,
                        "error": str(e),
                        "claim_id": claim.claim_key,
                        "security_report": security_report,
                        "processing_time_ms": (time.time() - processing_start) * 1000
                    }

            else:
                # No deduplication available - process directly with security
                return {
                    "success": False,
                    "task_id": task.task_id,
                    "error": "Task deduplication not available for secure processing",
                    "security_report": security_report,
                    "processing_time_ms": (time.time() - processing_start) * 1000
                }

        except Exception as e:
            self._logger.error(f"Error in secure task processing: {e}")
            return {
                "success": False,
                "task_id": task.task_id,
                "error": str(e),
                "security_report": security_report,
                "processing_time_ms": (time.time() - processing_start) * 1000
            }

    async def validate_task_security(self, task: TaskContext) -> Dict[str, Any]:
        """
        Perform security validation on task content.

        Args:
            task: Task to validate

        Returns:
            Dict containing security scan results
        """
        if not self.security_validator:
            return {"error": "Security validator not available", "success": False}

        try:
            scan_result = await self.security_validator.scan_task_content(task)

            return {
                "success": True,
                "task_id": task.task_id,
                "threat_level": scan_result.threat_level.value,
                "safe_to_process": scan_result.safe_to_process,
                "threats_detected": scan_result.threats_detected,
                "sanitized_content_available": scan_result.sanitized_content is not None,
                "scan_duration_ms": scan_result.scan_duration_ms,
                "scanner_version": scan_result.scanner_version,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error validating task security: {e}")
            return {
                "success": False,
                "task_id": task.task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def encrypt_conversation_state_secure(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt conversation state data using state encryption component.

        Args:
            conversation_data: Raw conversation state data

        Returns:
            Dict containing encryption results
        """
        if not self.state_encryption:
            return {"error": "State encryption not available", "success": False}

        try:
            encrypted_result = await self.state_encryption.encrypt_conversation_state(conversation_data)

            return {
                "success": True,
                "encrypted_data": encrypted_result["encrypted_data"],
                "encryption_metadata": {
                    "encryption_timestamp": encrypted_result["encryption_timestamp"],
                    "encryption_version": encrypted_result["encryption_version"],
                    "data_integrity_hash": encrypted_result["data_integrity_hash"],
                    "encrypted_size_bytes": encrypted_result["encrypted_size_bytes"],
                    "original_size_bytes": encrypted_result["original_size_bytes"]
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error encrypting conversation state: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def decrypt_conversation_state_secure(self, encrypted_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt conversation state data using state encryption component.

        Args:
            encrypted_result: Encrypted data with metadata

        Returns:
            Dict containing decrypted conversation data
        """
        if not self.state_encryption:
            return {"error": "State encryption not available", "success": False}

        try:
            conversation_data = await self.state_encryption.decrypt_conversation_state(encrypted_result)

            return {
                "success": True,
                "conversation_data": conversation_data,
                "integrity_verified": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error decrypting conversation state: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_security_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive security metrics from all security components.

        Returns:
            Dict containing aggregated security metrics
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "security_components_available": {
                "security_validator": self.security_validator is not None,
                "execution_sandbox": self.execution_sandbox is not None,
                "state_encryption": self.state_encryption is not None
            }
        }

        try:
            if self.security_validator:
                metrics["security_validation"] = self.security_validator.get_security_metrics()

            if self.execution_sandbox:
                metrics["sandbox_execution"] = self.execution_sandbox.get_sandbox_metrics()

            if self.state_encryption:
                metrics["state_encryption"] = self.state_encryption.get_encryption_metrics()

        except Exception as e:
            self._logger.error(f"Error collecting security metrics: {e}")
            metrics["error"] = str(e)

        return metrics