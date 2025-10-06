"""
State consistency protection mechanisms for TaskQueueManager

This module implements comprehensive state protection including:
- StatePersistenceStrategy with multi-layer storage and integrity checking
- Enhanced StateIntegrityMonitor for corruption detection and recovery
- ConversationStateLockManager for distributed state coordination
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from contextlib import asynccontextmanager

from .models import (
    ConversationContext,
    StateCheckpoint,
    PersistenceConfig,
    ConversationState,
)


class PersistenceLayer(Enum):
    """Storage layers for state persistence."""
    HOT = "hot"      # Redis memory - fastest access
    WARM = "warm"    # Redis disk - reliable backup
    COLD = "cold"    # File system - long-term storage
    CHECKPOINT = "checkpoint"  # Immutable snapshots


class IntegrityStatus(Enum):
    """State integrity check results."""
    VALID = "valid"
    CORRUPTED = "corrupted"
    MISSING = "missing"
    INCONSISTENT = "inconsistent"
    UNKNOWN = "unknown"


@dataclass
class PersistenceResult:
    """Result of a persistence operation."""
    success: bool
    layer: PersistenceLayer
    state_hash: str
    timestamp: datetime
    error_message: Optional[str] = None
    integrity_verified: bool = False


@dataclass
class IntegrityReport:
    """Comprehensive integrity check report."""
    conversation_id: str
    overall_status: IntegrityStatus
    layer_statuses: Dict[PersistenceLayer, IntegrityStatus]
    hash_mismatches: List[str]
    corruption_detected: bool
    recovery_recommended: bool
    timestamp: datetime


@dataclass
class StateLock:
    """Distributed state lock for conversation coordination."""
    lock_id: str
    conversation_id: str
    holder_id: str
    acquired_at: datetime
    expires_at: datetime
    lock_type: str  # "read", "write", "exclusive"
    renewed_count: int = 0


class StatePersistenceStrategy:
    """
    Multi-layer state persistence strategy with integrity checking.

    Implements comprehensive state persistence across hot/warm/cold/checkpoint
    layers with automatic integrity validation and recovery mechanisms.
    """

    def __init__(self, redis_client, config: PersistenceConfig):
        self.redis = redis_client
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.StatePersistenceStrategy")

        # Strategy configuration
        self.persistence_layers = [
            PersistenceLayer.HOT,
            PersistenceLayer.WARM,
            PersistenceLayer.COLD,
            PersistenceLayer.CHECKPOINT
        ]

        # Integrity checking
        self.verify_integrity = True
        self.auto_repair = True
        self.corruption_threshold = 0.1  # 10% corruption triggers recovery

        # Performance tracking
        self._persistence_metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "integrity_failures": 0,
            "auto_repairs": 0,
            "layer_failures": {layer: 0 for layer in self.persistence_layers}
        }

        self._logger.info("StatePersistenceStrategy initialized with multi-layer protection")

    async def persist_state_secure(self, context: ConversationContext,
                                 required_layers: Optional[Set[PersistenceLayer]] = None) -> Dict[PersistenceLayer, PersistenceResult]:
        """
        Persist state across multiple layers with integrity verification.

        Args:
            context: Conversation context to persist
            required_layers: Specific layers to persist to (defaults to all)

        Returns:
            Dict mapping persistence layers to their results
        """
        operation_start = time.time()
        self._persistence_metrics["total_operations"] += 1

        if not required_layers:
            required_layers = set(self.persistence_layers)

        # Generate master state hash
        state_data = asdict(context)
        master_hash = self._generate_secure_hash(state_data)

        self._logger.info(
            f"Starting secure persistence for conversation {context.conversation_id}",
            extra={
                "conversation_id": context.conversation_id,
                "state_hash": master_hash,
                "layers": [layer.value for layer in required_layers],
                "turns_count": len(context.turns)
            }
        )

        results = {}
        successful_layers = 0

        # Persist to each required layer
        for layer in required_layers:
            try:
                result = await self._persist_to_layer(context, layer, master_hash)
                results[layer] = result

                if result.success:
                    successful_layers += 1
                    self._logger.debug(
                        f"Successfully persisted to {layer.value}",
                        extra={"conversation_id": context.conversation_id, "layer": layer.value}
                    )
                else:
                    self._persistence_metrics["layer_failures"][layer] += 1
                    self._logger.warning(
                        f"Failed to persist to {layer.value}: {result.error_message}",
                        extra={"conversation_id": context.conversation_id, "layer": layer.value}
                    )

            except Exception as e:
                self._persistence_metrics["layer_failures"][layer] += 1
                self._logger.error(
                    f"Exception persisting to {layer.value}: {e}",
                    extra={"conversation_id": context.conversation_id, "layer": layer.value}
                )

                results[layer] = PersistenceResult(
                    success=False,
                    layer=layer,
                    state_hash=master_hash,
                    timestamp=datetime.now(),
                    error_message=str(e)
                )

        # Update metrics
        if successful_layers > 0:
            self._persistence_metrics["successful_operations"] += 1

        # Verify integrity across successful layers if enabled
        if self.verify_integrity and successful_layers > 0:
            await self._verify_cross_layer_integrity(context.conversation_id, master_hash, results)

        operation_duration = time.time() - operation_start
        self._logger.info(
            f"Completed secure persistence for conversation {context.conversation_id}",
            extra={
                "conversation_id": context.conversation_id,
                "successful_layers": successful_layers,
                "total_layers": len(required_layers),
                "operation_duration_ms": operation_duration * 1000,
                "master_hash": master_hash
            }
        )

        return results

    async def _persist_to_layer(self, context: ConversationContext,
                               layer: PersistenceLayer, state_hash: str) -> PersistenceResult:
        """Persist state to a specific storage layer."""
        timestamp = datetime.now()

        try:
            if layer == PersistenceLayer.HOT:
                success = await self._persist_to_hot_storage(context, state_hash)
            elif layer == PersistenceLayer.WARM:
                success = await self._persist_to_warm_storage(context, state_hash)
            elif layer == PersistenceLayer.COLD:
                success = await self._persist_to_cold_storage(context, state_hash)
            elif layer == PersistenceLayer.CHECKPOINT:
                success = await self._persist_to_checkpoint_storage(context, state_hash)
            else:
                raise ValueError(f"Unknown persistence layer: {layer}")

            # Verify integrity immediately after persistence
            integrity_verified = False
            if success and self.verify_integrity:
                integrity_verified = await self._verify_layer_integrity(
                    context.conversation_id, state_hash, layer
                )

            return PersistenceResult(
                success=success,
                layer=layer,
                state_hash=state_hash,
                timestamp=timestamp,
                integrity_verified=integrity_verified
            )

        except Exception as e:
            return PersistenceResult(
                success=False,
                layer=layer,
                state_hash=state_hash,
                timestamp=timestamp,
                error_message=str(e)
            )

    async def _persist_to_hot_storage(self, context: ConversationContext, state_hash: str) -> bool:
        """Persist to Redis hot storage with expiration."""
        key = f"conversation:hot:{context.conversation_id}"

        data = {
            "context": asdict(context),
            "state_hash": state_hash,
            "persisted_at": datetime.now().isoformat(),
            "layer": "hot"
        }

        try:
            # Store with TTL for hot storage
            result = await self.redis.setex(
                key,
                self.config.hot_storage_ttl,
                json.dumps(data, default=str)
            )
            return bool(result)

        except Exception as e:
            self._logger.error(f"Hot storage persistence failed: {e}")
            return False

    async def _persist_to_warm_storage(self, context: ConversationContext, state_hash: str) -> bool:
        """Persist to Redis warm storage with longer TTL."""
        key = f"conversation:warm:{context.conversation_id}"

        data = {
            "context": asdict(context),
            "state_hash": state_hash,
            "persisted_at": datetime.now().isoformat(),
            "layer": "warm"
        }

        try:
            # Store with longer TTL for warm storage
            result = await self.redis.setex(
                key,
                self.config.warm_storage_ttl,
                json.dumps(data, default=str)
            )
            return bool(result)

        except Exception as e:
            self._logger.error(f"Warm storage persistence failed: {e}")
            return False

    async def _persist_to_cold_storage(self, context: ConversationContext, state_hash: str) -> bool:
        """Persist to file system cold storage."""
        # This is a simplified implementation - production would use proper file management
        try:
            import os
            import tempfile

            # Create cold storage directory if needed
            cold_dir = "/tmp/task_queue_cold_storage"  # In production, use proper directory
            os.makedirs(cold_dir, exist_ok=True)

            filepath = os.path.join(cold_dir, f"{context.conversation_id}.json")

            data = {
                "context": asdict(context),
                "state_hash": state_hash,
                "persisted_at": datetime.now().isoformat(),
                "layer": "cold"
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, default=str, indent=2)

            return True

        except Exception as e:
            self._logger.error(f"Cold storage persistence failed: {e}")
            return False

    async def _persist_to_checkpoint_storage(self, context: ConversationContext, state_hash: str) -> bool:
        """Create immutable checkpoint in Redis."""
        checkpoint_id = f"checkpoint:{context.conversation_id}:{int(time.time())}"
        key = f"conversation:checkpoint:{checkpoint_id}"

        checkpoint = StateCheckpoint(
            checkpoint_id=checkpoint_id,
            conversation_id=context.conversation_id,
            state_hash=state_hash,
            conversation_context=context,
            created_at=datetime.now()
        )

        try:
            # Store checkpoint with no expiration (immutable)
            result = await self.redis.set(
                key,
                json.dumps(asdict(checkpoint), default=str)
            )

            # Also add to checkpoint index
            index_key = f"conversation:checkpoints:{context.conversation_id}"
            await self.redis.sadd(index_key, checkpoint_id)

            return bool(result)

        except Exception as e:
            self._logger.error(f"Checkpoint storage persistence failed: {e}")
            return False

    async def _verify_cross_layer_integrity(self, conversation_id: str, expected_hash: str,
                                          results: Dict[PersistenceLayer, PersistenceResult]):
        """Verify integrity across multiple storage layers."""
        successful_layers = [layer for layer, result in results.items() if result.success]

        if len(successful_layers) < 2:
            return  # Need at least 2 layers to cross-verify

        integrity_failures = []

        for layer in successful_layers:
            try:
                stored_hash = await self._get_stored_hash(conversation_id, layer)
                if stored_hash != expected_hash:
                    integrity_failures.append(layer)
                    self._logger.error(
                        f"Cross-layer integrity failure in {layer.value}",
                        extra={
                            "conversation_id": conversation_id,
                            "expected_hash": expected_hash,
                            "stored_hash": stored_hash,
                            "layer": layer.value
                        }
                    )

            except Exception as e:
                self._logger.warning(f"Could not verify {layer.value} integrity: {e}")

        if integrity_failures:
            self._persistence_metrics["integrity_failures"] += len(integrity_failures)

            if self.auto_repair:
                await self._attempt_integrity_repair(conversation_id, expected_hash,
                                                   successful_layers, integrity_failures)

    async def _verify_layer_integrity(self, conversation_id: str, expected_hash: str,
                                    layer: PersistenceLayer) -> bool:
        """Verify integrity of a specific storage layer."""
        try:
            stored_hash = await self._get_stored_hash(conversation_id, layer)
            return stored_hash == expected_hash
        except Exception:
            return False

    async def _get_stored_hash(self, conversation_id: str, layer: PersistenceLayer) -> Optional[str]:
        """Retrieve stored hash for integrity verification."""
        try:
            if layer in [PersistenceLayer.HOT, PersistenceLayer.WARM]:
                key = f"conversation:{layer.value}:{conversation_id}"
                data = await self.redis.get(key)
                if data:
                    parsed_data = json.loads(data)
                    return parsed_data.get("state_hash")

            elif layer == PersistenceLayer.COLD:
                import os
                cold_dir = "/tmp/task_queue_cold_storage"
                filepath = os.path.join(cold_dir, f"{conversation_id}.json")

                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        return data.get("state_hash")

            elif layer == PersistenceLayer.CHECKPOINT:
                # Get latest checkpoint for conversation
                index_key = f"conversation:checkpoints:{conversation_id}"
                checkpoints = await self.redis.smembers(index_key)
                if checkpoints:
                    # Get the most recent checkpoint
                    latest_checkpoint = sorted(checkpoints)[-1]
                    checkpoint_key = f"conversation:checkpoint:{latest_checkpoint}"
                    data = await self.redis.get(checkpoint_key)
                    if data:
                        parsed_data = json.loads(data)
                        return parsed_data.get("state_hash")

            return None

        except Exception as e:
            self._logger.error(f"Error getting stored hash for {layer.value}: {e}")
            return None

    async def _attempt_integrity_repair(self, conversation_id: str, expected_hash: str,
                                      successful_layers: List[PersistenceLayer],
                                      failed_layers: List[PersistenceLayer]):
        """Attempt to repair integrity failures using good layers."""
        self._logger.info(
            f"Attempting integrity repair for conversation {conversation_id}",
            extra={
                "conversation_id": conversation_id,
                "successful_layers": [layer.value for layer in successful_layers],
                "failed_layers": [layer.value for layer in failed_layers]
            }
        )

        # Find a layer with correct integrity to use as source
        source_layer = None
        for layer in successful_layers:
            if layer not in failed_layers:
                source_layer = layer
                break

        if not source_layer:
            self._logger.error(f"No valid source layer found for repair of {conversation_id}")
            return

        try:
            # Retrieve context from source layer
            source_context = await self._retrieve_from_layer(conversation_id, source_layer)
            if not source_context:
                self._logger.error(f"Could not retrieve context from source layer {source_layer.value}")
                return

            # Re-persist to failed layers
            repair_count = 0
            for failed_layer in failed_layers:
                try:
                    result = await self._persist_to_layer(source_context, failed_layer, expected_hash)
                    if result.success:
                        repair_count += 1
                        self._logger.info(f"Successfully repaired {failed_layer.value}")
                    else:
                        self._logger.error(f"Failed to repair {failed_layer.value}: {result.error_message}")

                except Exception as e:
                    self._logger.error(f"Exception during repair of {failed_layer.value}: {e}")

            self._persistence_metrics["auto_repairs"] += repair_count
            self._logger.info(f"Integrity repair completed: {repair_count}/{len(failed_layers)} layers repaired")

        except Exception as e:
            self._logger.error(f"Integrity repair failed: {e}")

    async def _retrieve_from_layer(self, conversation_id: str,
                                 layer: PersistenceLayer) -> Optional[ConversationContext]:
        """Retrieve conversation context from a specific layer."""
        try:
            if layer == PersistenceLayer.HOT:
                key = f"conversation:hot:{conversation_id}"
                data = await self.redis.get(key)
                if data:
                    parsed_data = json.loads(data)
                    return ConversationContext(**parsed_data["context"])

            elif layer == PersistenceLayer.WARM:
                key = f"conversation:warm:{conversation_id}"
                data = await self.redis.get(key)
                if data:
                    parsed_data = json.loads(data)
                    return ConversationContext(**parsed_data["context"])

            # Add other layers as needed
            return None

        except Exception as e:
            self._logger.error(f"Error retrieving from {layer.value}: {e}")
            return None

    def _generate_secure_hash(self, data: Dict[str, Any]) -> str:
        """Generate secure hash of state data for integrity checking."""
        # Create deterministic JSON representation
        json_str = json.dumps(data, sort_keys=True, default=str)

        # Generate SHA-256 hash
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get_persistence_metrics(self) -> Dict[str, Any]:
        """Get comprehensive persistence strategy metrics."""
        return {
            "strategy": "multi_layer_secure",
            "layers_enabled": [layer.value for layer in self.persistence_layers],
            "integrity_verification": self.verify_integrity,
            "auto_repair": self.auto_repair,
            "metrics": dict(self._persistence_metrics),
            "success_rate": (
                self._persistence_metrics["successful_operations"] /
                max(1, self._persistence_metrics["total_operations"])
            )
        }


class EnhancedStateIntegrityMonitor:
    """
    Enhanced state integrity monitor with corruption detection and recovery.

    Provides comprehensive monitoring of state integrity across all storage layers
    with automatic corruption detection, alerting, and recovery recommendations.
    """

    def __init__(self, redis_client, persistence_strategy: StatePersistenceStrategy):
        self.redis = redis_client
        self.persistence_strategy = persistence_strategy
        self._logger = logging.getLogger(f"{__name__}.EnhancedStateIntegrityMonitor")

        # Monitoring configuration
        self.check_interval_seconds = 300  # 5 minutes
        self.corruption_alert_threshold = 3  # Alert after 3 corruption detections
        self.auto_recovery_enabled = True

        # Tracking state
        self._corruption_counts = {}  # conversation_id -> count
        self._last_integrity_check = datetime.now()
        self._monitoring_active = False

        # Metrics
        self._integrity_metrics = {
            "total_checks": 0,
            "corruptions_detected": 0,
            "recoveries_attempted": 0,
            "recoveries_successful": 0
        }

        self._logger.info("Enhanced StateIntegrityMonitor initialized")

    async def start_continuous_monitoring(self):
        """Start continuous integrity monitoring in background."""
        if self._monitoring_active:
            self._logger.warning("Integrity monitoring already active")
            return

        self._monitoring_active = True
        self._logger.info("Starting continuous integrity monitoring")

        # Start monitoring task
        asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while self._monitoring_active:
            try:
                await self.perform_system_integrity_check()
                await asyncio.sleep(self.check_interval_seconds)

            except Exception as e:
                self._logger.error(f"Error in integrity monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def perform_system_integrity_check(self) -> Dict[str, Any]:
        """Perform comprehensive system-wide integrity check."""
        check_start = time.time()
        self._integrity_metrics["total_checks"] += 1

        self._logger.info("Starting system-wide integrity check")

        # Get all active conversations from hot storage
        conversation_ids = await self._get_active_conversations()

        total_conversations = len(conversation_ids)
        corruption_reports = []
        healthy_conversations = 0

        for conversation_id in conversation_ids:
            try:
                report = await self.check_conversation_integrity(conversation_id)

                if report.corruption_detected:
                    corruption_reports.append(report)
                    self._corruption_counts[conversation_id] = self._corruption_counts.get(conversation_id, 0) + 1

                    # Trigger alerts if threshold exceeded
                    if self._corruption_counts[conversation_id] >= self.corruption_alert_threshold:
                        await self._trigger_corruption_alert(report)

                    # Attempt recovery if enabled
                    if self.auto_recovery_enabled:
                        await self._attempt_corruption_recovery(report)

                else:
                    healthy_conversations += 1
                    # Reset corruption count for healthy conversation
                    self._corruption_counts.pop(conversation_id, None)

            except Exception as e:
                self._logger.error(f"Error checking integrity for {conversation_id}: {e}")

        check_duration = time.time() - check_start
        corruption_rate = len(corruption_reports) / max(1, total_conversations)

        result = {
            "check_timestamp": datetime.now().isoformat(),
            "total_conversations": total_conversations,
            "healthy_conversations": healthy_conversations,
            "corrupted_conversations": len(corruption_reports),
            "corruption_rate": corruption_rate,
            "check_duration_seconds": check_duration,
            "corruption_reports": [asdict(report) for report in corruption_reports]
        }

        self._logger.info(
            f"System integrity check completed",
            extra={
                "total_conversations": total_conversations,
                "corruption_rate": corruption_rate,
                "check_duration_ms": check_duration * 1000
            }
        )

        self._last_integrity_check = datetime.now()
        return result

    async def check_conversation_integrity(self, conversation_id: str) -> IntegrityReport:
        """Check integrity of a specific conversation across all layers."""
        self._logger.debug(f"Checking integrity for conversation {conversation_id}")

        layer_statuses = {}
        hash_mismatches = []
        reference_hash = None

        # Check each storage layer
        for layer in self.persistence_strategy.persistence_layers:
            try:
                stored_hash = await self.persistence_strategy._get_stored_hash(conversation_id, layer)

                if stored_hash is None:
                    layer_statuses[layer] = IntegrityStatus.MISSING
                    continue

                # Use first found hash as reference
                if reference_hash is None:
                    reference_hash = stored_hash
                    layer_statuses[layer] = IntegrityStatus.VALID
                else:
                    # Compare with reference hash
                    if stored_hash == reference_hash:
                        layer_statuses[layer] = IntegrityStatus.VALID
                    else:
                        layer_statuses[layer] = IntegrityStatus.CORRUPTED
                        hash_mismatches.append(f"{layer.value}: {stored_hash} vs reference: {reference_hash}")

            except Exception as e:
                layer_statuses[layer] = IntegrityStatus.UNKNOWN
                self._logger.warning(f"Error checking {layer.value} for {conversation_id}: {e}")

        # Determine overall status
        corruption_detected = any(status == IntegrityStatus.CORRUPTED for status in layer_statuses.values())
        missing_layers = sum(1 for status in layer_statuses.values() if status == IntegrityStatus.MISSING)

        if corruption_detected:
            overall_status = IntegrityStatus.CORRUPTED
            self._integrity_metrics["corruptions_detected"] += 1
        elif missing_layers > 0:
            overall_status = IntegrityStatus.INCONSISTENT
        else:
            overall_status = IntegrityStatus.VALID

        # Determine if recovery is recommended
        recovery_recommended = (
            corruption_detected or
            missing_layers >= len(self.persistence_strategy.persistence_layers) // 2
        )

        report = IntegrityReport(
            conversation_id=conversation_id,
            overall_status=overall_status,
            layer_statuses=layer_statuses,
            hash_mismatches=hash_mismatches,
            corruption_detected=corruption_detected,
            recovery_recommended=recovery_recommended,
            timestamp=datetime.now()
        )

        if corruption_detected:
            self._logger.warning(
                f"Corruption detected in conversation {conversation_id}",
                extra={
                    "conversation_id": conversation_id,
                    "corrupted_layers": [layer.value for layer, status in layer_statuses.items()
                                       if status == IntegrityStatus.CORRUPTED],
                    "hash_mismatches": len(hash_mismatches)
                }
            )

        return report

    async def _get_active_conversations(self) -> List[str]:
        """Get list of active conversation IDs from hot storage."""
        try:
            pattern = "conversation:hot:*"
            keys = await self.redis.keys(pattern)

            # Extract conversation IDs from keys
            conversation_ids = []
            for key in keys:
                # Extract conversation ID from key format: conversation:hot:conversation_id
                parts = key.decode() if isinstance(key, bytes) else key
                conversation_id = parts.split(":", 2)[-1]
                conversation_ids.append(conversation_id)

            return conversation_ids

        except Exception as e:
            self._logger.error(f"Error getting active conversations: {e}")
            return []

    async def _trigger_corruption_alert(self, report: IntegrityReport):
        """Trigger alert for detected corruption."""
        self._logger.error(
            f"CORRUPTION ALERT: Conversation {report.conversation_id} has persistent corruption",
            extra={
                "conversation_id": report.conversation_id,
                "corruption_count": self._corruption_counts.get(report.conversation_id, 0),
                "corrupted_layers": [layer.value for layer, status in report.layer_statuses.items()
                                   if status == IntegrityStatus.CORRUPTED],
                "alert_level": "CRITICAL"
            }
        )

        # In production, this would integrate with alerting systems
        # like PagerDuty, Slack, email, etc.

    async def _attempt_corruption_recovery(self, report: IntegrityReport):
        """Attempt to recover from detected corruption."""
        self._integrity_metrics["recoveries_attempted"] += 1

        self._logger.info(
            f"Attempting corruption recovery for conversation {report.conversation_id}",
            extra={"conversation_id": report.conversation_id}
        )

        try:
            # Find healthy layers to use as source
            healthy_layers = [layer for layer, status in report.layer_statuses.items()
                            if status == IntegrityStatus.VALID]

            if not healthy_layers:
                self._logger.error(f"No healthy layers found for recovery of {report.conversation_id}")
                return

            # Use the first healthy layer as source
            source_layer = healthy_layers[0]
            source_context = await self.persistence_strategy._retrieve_from_layer(
                report.conversation_id, source_layer
            )

            if not source_context:
                self._logger.error(f"Could not retrieve source context for recovery")
                return

            # Re-persist to corrupted layers
            corrupted_layers = [layer for layer, status in report.layer_statuses.items()
                              if status == IntegrityStatus.CORRUPTED]

            recovery_results = await self.persistence_strategy.persist_state_secure(
                source_context, set(corrupted_layers)
            )

            successful_recoveries = sum(1 for result in recovery_results.values() if result.success)

            if successful_recoveries > 0:
                self._integrity_metrics["recoveries_successful"] += 1
                self._logger.info(
                    f"Corruption recovery successful: {successful_recoveries}/{len(corrupted_layers)} layers recovered"
                )
            else:
                self._logger.error("Corruption recovery failed for all layers")

        except Exception as e:
            self._logger.error(f"Exception during corruption recovery: {e}")

    def stop_monitoring(self):
        """Stop continuous integrity monitoring."""
        self._monitoring_active = False
        self._logger.info("Stopped integrity monitoring")

    def get_integrity_metrics(self) -> Dict[str, Any]:
        """Get comprehensive integrity monitoring metrics."""
        return {
            "monitoring_active": self._monitoring_active,
            "last_check": self._last_integrity_check.isoformat(),
            "check_interval_seconds": self.check_interval_seconds,
            "corruption_alert_threshold": self.corruption_alert_threshold,
            "auto_recovery_enabled": self.auto_recovery_enabled,
            "active_corruption_counts": dict(self._corruption_counts),
            "metrics": dict(self._integrity_metrics)
        }


class LockError(Exception):
    """Base exception for lock operations."""
    pass


class LockTimeoutError(LockError):
    """Raised when lock acquisition times out."""
    pass


class LockNotHeldError(LockError):
    """Raised when trying to operate on a lock not held."""
    pass


class ConversationStateLockManager:
    """
    Distributed conversation state lock manager with lease management.

    Provides distributed coordination for conversation state operations using
    Redis-based locking with automatic lease renewal and deadlock prevention.
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self._logger = logging.getLogger(f"{__name__}.ConversationStateLockManager")

        # Lock configuration
        self.default_lock_timeout = 30  # seconds
        self.lease_renewal_interval = 10  # seconds
        self.max_lock_duration = 300  # 5 minutes maximum lock hold time
        self.deadlock_detection_enabled = True

        # Instance identification
        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"

        # Active locks tracking
        self._active_locks: Dict[str, StateLock] = {}
        self._lock_renewal_tasks: Dict[str, asyncio.Task] = {}

        # Lock metrics
        self._lock_metrics = {
            "locks_acquired": 0,
            "locks_released": 0,
            "lock_timeouts": 0,
            "lock_renewals": 0,
            "deadlocks_detected": 0,
            "active_locks_count": 0
        }

        self._logger.info(
            f"ConversationStateLockManager initialized",
            extra={"instance_id": self.instance_id}
        )

    @asynccontextmanager
    async def acquire_conversation_lock(self, conversation_id: str,
                                       lock_type: str = "write",
                                       timeout: Optional[int] = None):
        """
        Context manager for acquiring and automatically releasing conversation locks.

        Args:
            conversation_id: ID of conversation to lock
            lock_type: Type of lock ("read", "write", "exclusive")
            timeout: Lock acquisition timeout in seconds

        Usage:
            async with lock_manager.acquire_conversation_lock("conv_123", "write") as lock:
                # Perform operations on conversation state
                pass
        """
        if timeout is None:
            timeout = self.default_lock_timeout

        lock_acquired = False
        lock = None

        try:
            # Attempt to acquire lock
            lock = await self._acquire_lock(conversation_id, lock_type, timeout)
            lock_acquired = True

            self._logger.debug(
                f"Acquired {lock_type} lock for conversation {conversation_id}",
                extra={
                    "conversation_id": conversation_id,
                    "lock_type": lock_type,
                    "lock_id": lock.lock_id,
                    "instance_id": self.instance_id
                }
            )

            yield lock

        except Exception as e:
            self._logger.error(
                f"Error in lock context manager for {conversation_id}: {e}",
                extra={"conversation_id": conversation_id, "lock_type": lock_type}
            )
            raise

        finally:
            # Always attempt to release lock
            if lock_acquired and lock:
                try:
                    await self._release_lock(lock.lock_id)
                    self._logger.debug(
                        f"Released {lock_type} lock for conversation {conversation_id}",
                        extra={"conversation_id": conversation_id, "lock_id": lock.lock_id}
                    )
                except Exception as e:
                    self._logger.error(
                        f"Error releasing lock {lock.lock_id}: {e}",
                        extra={"lock_id": lock.lock_id}
                    )

    async def _acquire_lock(self, conversation_id: str, lock_type: str, timeout: int) -> StateLock:
        """Acquire a conversation state lock."""
        lock_id = f"lock:{conversation_id}:{lock_type}:{uuid.uuid4().hex[:8]}"
        lock_key = f"conversation_lock:{conversation_id}"

        start_time = time.time()
        attempt_count = 0

        while time.time() - start_time < timeout:
            attempt_count += 1

            try:
                # Check for deadlock potential
                if self.deadlock_detection_enabled:
                    await self._check_for_deadlock(conversation_id, lock_type)

                # Attempt to acquire lock using Redis SET with NX and EX
                lock_data = {
                    "lock_id": lock_id,
                    "conversation_id": conversation_id,
                    "holder_id": self.instance_id,
                    "lock_type": lock_type,
                    "acquired_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(seconds=self.default_lock_timeout)).isoformat(),
                    "renewed_count": 0
                }

                # Use Redis SET NX EX for atomic lock acquisition
                result = await self.redis.set(
                    lock_key,
                    json.dumps(lock_data),
                    nx=True,  # Only set if key doesn't exist
                    ex=self.default_lock_timeout  # Set expiration
                )

                if result:
                    # Lock acquired successfully
                    lock = StateLock(
                        lock_id=lock_id,
                        conversation_id=conversation_id,
                        holder_id=self.instance_id,
                        acquired_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(seconds=self.default_lock_timeout),
                        lock_type=lock_type
                    )

                    # Track active lock
                    self._active_locks[lock_id] = lock

                    # Start lease renewal task
                    renewal_task = asyncio.create_task(self._lease_renewal_loop(lock_id))
                    self._lock_renewal_tasks[lock_id] = renewal_task

                    # Update metrics
                    self._lock_metrics["locks_acquired"] += 1
                    self._lock_metrics["active_locks_count"] = len(self._active_locks)

                    self._logger.info(
                        f"Lock acquired after {attempt_count} attempts",
                        extra={
                            "lock_id": lock_id,
                            "conversation_id": conversation_id,
                            "lock_type": lock_type,
                            "attempt_count": attempt_count,
                            "acquisition_time_ms": (time.time() - start_time) * 1000
                        }
                    )

                    return lock

                else:
                    # Lock is held by another process
                    await self._handle_lock_contention(conversation_id, lock_key, attempt_count)

            except Exception as e:
                self._logger.warning(f"Lock acquisition attempt {attempt_count} failed: {e}")

            # Wait before next attempt with exponential backoff
            wait_time = min(0.1 * (2 ** attempt_count), 2.0)  # Max 2 seconds
            await asyncio.sleep(wait_time)

        # Timeout reached
        self._lock_metrics["lock_timeouts"] += 1
        raise LockTimeoutError(
            f"Failed to acquire {lock_type} lock for conversation {conversation_id} within {timeout}s"
        )

    async def _handle_lock_contention(self, conversation_id: str, lock_key: str, attempt_count: int):
        """Handle lock contention by analyzing the existing lock."""
        try:
            existing_lock_data = await self.redis.get(lock_key)
            if existing_lock_data:
                existing_lock = json.loads(existing_lock_data)
                holder_id = existing_lock.get("holder_id", "unknown")
                expires_at = existing_lock.get("expires_at")

                self._logger.debug(
                    f"Lock contention detected (attempt {attempt_count})",
                    extra={
                        "conversation_id": conversation_id,
                        "current_holder": holder_id,
                        "expires_at": expires_at
                    }
                )

                # Check if lock has expired (race condition protection)
                if expires_at:
                    expire_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if datetime.now() > expire_time:
                        self._logger.warning(
                            f"Detected expired lock for {conversation_id}, attempting cleanup"
                        )
                        # Try to clean up expired lock
                        await self.redis.delete(lock_key)

        except Exception as e:
            self._logger.warning(f"Error handling lock contention: {e}")

    async def _check_for_deadlock(self, conversation_id: str, lock_type: str):
        """Check for potential deadlock scenarios."""
        try:
            # Simple deadlock detection: check if we're already holding locks
            # and this could create a circular dependency

            current_locks = list(self._active_locks.values())
            if len(current_locks) > 1:  # We already hold multiple locks
                self._logger.debug(
                    f"Potential deadlock check: holding {len(current_locks)} locks while requesting {lock_type} for {conversation_id}"
                )

                # In a full implementation, this would do more sophisticated
                # deadlock detection using lock graphs

        except Exception as e:
            self._logger.warning(f"Error in deadlock detection: {e}")

    async def _lease_renewal_loop(self, lock_id: str):
        """Background task for automatic lease renewal."""
        try:
            while lock_id in self._active_locks:
                await asyncio.sleep(self.lease_renewal_interval)

                if lock_id not in self._active_locks:
                    break  # Lock was released

                lock = self._active_locks[lock_id]

                # Check if we've exceeded maximum lock duration
                if (datetime.now() - lock.acquired_at).total_seconds() > self.max_lock_duration:
                    self._logger.error(
                        f"Lock {lock_id} exceeded maximum duration, force releasing",
                        extra={"lock_id": lock_id, "max_duration": self.max_lock_duration}
                    )
                    await self._release_lock(lock_id)
                    break

                # Renew the lock
                try:
                    await self._renew_lease(lock_id)
                except Exception as e:
                    self._logger.error(f"Failed to renew lease for {lock_id}: {e}")
                    # Lock renewal failed, release the lock
                    await self._release_lock(lock_id)
                    break

        except asyncio.CancelledError:
            self._logger.debug(f"Lease renewal task for {lock_id} cancelled")
        except Exception as e:
            self._logger.error(f"Error in lease renewal loop for {lock_id}: {e}")

    async def _renew_lease(self, lock_id: str):
        """Renew lease for an active lock."""
        if lock_id not in self._active_locks:
            raise LockNotHeldError(f"Lock {lock_id} is not held by this instance")

        lock = self._active_locks[lock_id]
        lock_key = f"conversation_lock:{lock.conversation_id}"

        # Verify we still hold the lock and renew it
        current_lock_data = await self.redis.get(lock_key)
        if not current_lock_data:
            raise LockNotHeldError(f"Lock {lock_id} no longer exists in Redis")

        current_lock = json.loads(current_lock_data)
        if current_lock.get("holder_id") != self.instance_id:
            raise LockNotHeldError(f"Lock {lock_id} is held by different instance")

        # Renew the lease
        new_expiry = datetime.now() + timedelta(seconds=self.default_lock_timeout)
        current_lock["expires_at"] = new_expiry.isoformat()
        current_lock["renewed_count"] = current_lock.get("renewed_count", 0) + 1

        # Use Redis SET with existing key to renew
        await self.redis.set(
            lock_key,
            json.dumps(current_lock),
            ex=self.default_lock_timeout
        )

        # Update local lock object
        lock.expires_at = new_expiry
        lock.renewed_count = current_lock["renewed_count"]

        self._lock_metrics["lock_renewals"] += 1

        self._logger.debug(
            f"Renewed lease for lock {lock_id}",
            extra={
                "lock_id": lock_id,
                "renewal_count": lock.renewed_count,
                "new_expiry": new_expiry.isoformat()
            }
        )

    async def _release_lock(self, lock_id: str):
        """Release a held lock."""
        if lock_id not in self._active_locks:
            self._logger.warning(f"Attempted to release unheld lock: {lock_id}")
            return

        lock = self._active_locks[lock_id]
        lock_key = f"conversation_lock:{lock.conversation_id}"

        try:
            # Verify we still hold the lock before releasing
            current_lock_data = await self.redis.get(lock_key)
            if current_lock_data:
                current_lock = json.loads(current_lock_data)
                if current_lock.get("holder_id") == self.instance_id:
                    # We hold the lock, safe to delete
                    await self.redis.delete(lock_key)

            # Clean up local tracking
            del self._active_locks[lock_id]

            # Cancel renewal task
            if lock_id in self._lock_renewal_tasks:
                renewal_task = self._lock_renewal_tasks[lock_id]
                renewal_task.cancel()
                del self._lock_renewal_tasks[lock_id]

            # Update metrics
            self._lock_metrics["locks_released"] += 1
            self._lock_metrics["active_locks_count"] = len(self._active_locks)

            self._logger.debug(
                f"Released lock {lock_id}",
                extra={
                    "lock_id": lock_id,
                    "conversation_id": lock.conversation_id,
                    "hold_duration_seconds": (datetime.now() - lock.acquired_at).total_seconds()
                }
            )

        except Exception as e:
            self._logger.error(f"Error releasing lock {lock_id}: {e}")

    async def check_lock_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Check the current lock status for a conversation."""
        lock_key = f"conversation_lock:{conversation_id}"

        try:
            lock_data = await self.redis.get(lock_key)
            if lock_data:
                return json.loads(lock_data)
            return None

        except Exception as e:
            self._logger.error(f"Error checking lock status for {conversation_id}: {e}")
            return None

    async def force_release_expired_locks(self) -> int:
        """Force release any expired locks (cleanup operation)."""
        cleaned_count = 0

        try:
            # Get all conversation locks
            pattern = "conversation_lock:*"
            lock_keys = await self.redis.keys(pattern)

            for lock_key in lock_keys:
                try:
                    lock_data = await self.redis.get(lock_key)
                    if lock_data:
                        lock_info = json.loads(lock_data)
                        expires_at = lock_info.get("expires_at")

                        if expires_at:
                            expire_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if datetime.now() > expire_time:
                                await self.redis.delete(lock_key)
                                cleaned_count += 1

                                self._logger.info(
                                    f"Force released expired lock",
                                    extra={
                                        "lock_key": lock_key,
                                        "expired_at": expires_at,
                                        "holder_id": lock_info.get("holder_id")
                                    }
                                )

                except Exception as e:
                    self._logger.warning(f"Error cleaning up lock {lock_key}: {e}")

        except Exception as e:
            self._logger.error(f"Error in force release expired locks: {e}")

        if cleaned_count > 0:
            self._logger.info(f"Force released {cleaned_count} expired locks")

        return cleaned_count

    def get_lock_metrics(self) -> Dict[str, Any]:
        """Get comprehensive lock manager metrics."""
        active_locks = []
        for lock_id, lock in self._active_locks.items():
            active_locks.append({
                "lock_id": lock_id,
                "conversation_id": lock.conversation_id,
                "lock_type": lock.lock_type,
                "acquired_at": lock.acquired_at.isoformat(),
                "expires_at": lock.expires_at.isoformat(),
                "hold_duration_seconds": (datetime.now() - lock.acquired_at).total_seconds(),
                "renewed_count": lock.renewed_count
            })

        return {
            "instance_id": self.instance_id,
            "active_locks": active_locks,
            "configuration": {
                "default_lock_timeout": self.default_lock_timeout,
                "lease_renewal_interval": self.lease_renewal_interval,
                "max_lock_duration": self.max_lock_duration,
                "deadlock_detection_enabled": self.deadlock_detection_enabled
            },
            "metrics": dict(self._lock_metrics),
            "timestamp": datetime.now().isoformat()
        }

    async def shutdown(self):
        """Gracefully shutdown lock manager, releasing all held locks."""
        self._logger.info("Shutting down ConversationStateLockManager")

        # Cancel all renewal tasks
        for task in self._lock_renewal_tasks.values():
            task.cancel()

        # Release all held locks
        lock_ids = list(self._active_locks.keys())
        for lock_id in lock_ids:
            try:
                await self._release_lock(lock_id)
            except Exception as e:
                self._logger.error(f"Error releasing lock {lock_id} during shutdown: {e}")

        self._logger.info("ConversationStateLockManager shutdown complete")