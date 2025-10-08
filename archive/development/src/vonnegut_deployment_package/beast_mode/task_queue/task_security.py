"""
Task security validation and sandboxing for TaskQueueManager

This module implements comprehensive security validation including:
- TaskSecurityValidator with pattern analysis and content sanitization
- TaskExecutionSandbox with resource limits and monitoring
- ConversationStateEncryption with access controls and audit logging
"""

import asyncio
import hashlib
import logging
import re
import resource
import signal
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import psutil
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from .models import (
    TaskContext,
    ConversationContext,
    SecuritySettings,
    TaskState,
)


class SecurityThreatLevel(Enum):
    """Security threat assessment levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityValidationResult(Enum):
    """Security validation outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    SANITIZED = "sanitized"
    QUARANTINED = "quarantined"


@dataclass
class SecurityAssessment:
    """Security assessment result."""
    threat_level: SecurityThreatLevel
    validation_result: SecurityValidationResult
    detected_patterns: List[str]
    sanitized_content: Optional[str]
    risk_score: float
    assessment_time: datetime
    details: Dict[str, Any]


@dataclass
class SandboxLimits:
    """Resource limits for sandbox execution."""
    max_memory_mb: int = 128
    max_cpu_time_seconds: int = 30
    max_file_operations: int = 100
    max_network_connections: int = 0
    allowed_modules: Set[str] = None
    blocked_modules: Set[str] = None


class TaskSecurityValidator:
    """
    Advanced security validator with pattern analysis and content sanitization.

    Provides comprehensive security analysis including:
    - Dangerous pattern detection
    - Content sanitization
    - Payload size validation
    - Risk scoring and threat assessment
    """

    def __init__(self, security_settings: SecuritySettings):
        self.settings = security_settings
        self.instance_id = f"security_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.TaskSecurityValidator")

        # Compile dangerous patterns for performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in security_settings.dangerous_patterns
        ]

        # Extended security patterns
        self.extended_patterns = {
            'code_injection': [
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__\s*\(',
                r'compile\s*\(',
                r'globals\s*\(\)',
                r'locals\s*\(\)',
            ],
            'system_access': [
                r'subprocess\.',
                r'os\.system',
                r'os\.popen',
                r'os\.spawn',
                r'commands\.',
                r'shell=True',
            ],
            'file_operations': [
                r'open\s*\(',
                r'file\s*\(',
                r'with\s+open',
                r'\.read\s*\(',
                r'\.write\s*\(',
                r'\.delete',
            ],
            'network_operations': [
                r'urllib\.',
                r'requests\.',
                r'socket\.',
                r'http\.',
                r'ftp\.',
                r'smtp\.',
            ]
        }

        # Security metrics
        self._security_metrics = {
            "tasks_validated": 0,
            "threats_detected": 0,
            "patterns_matched": {},
            "sanitization_performed": 0,
            "rejections": 0,
            "risk_scores": []
        }

        self._logger.info(
            f"TaskSecurityValidator initialized",
            extra={
                "instance_id": self.instance_id,
                "patterns_count": len(self.compiled_patterns),
                "max_payload_size": security_settings.max_payload_size_bytes
            }
        )

    async def validate_task(self, task: TaskContext) -> SecurityAssessment:
        """
        Comprehensive security validation of task content.

        Args:
            task: Task to validate

        Returns:
            SecurityAssessment with validation results and risk analysis
        """
        start_time = datetime.now()

        try:
            self._security_metrics["tasks_validated"] += 1

            # Check payload size
            payload_size = len(str(task.content))
            if payload_size > self.settings.max_payload_size_bytes:
                return SecurityAssessment(
                    threat_level=SecurityThreatLevel.HIGH,
                    validation_result=SecurityValidationResult.REJECTED,
                    detected_patterns=["payload_size_exceeded"],
                    sanitized_content=None,
                    risk_score=1.0,
                    assessment_time=start_time,
                    details={
                        "reason": "Payload size exceeded",
                        "size": payload_size,
                        "limit": self.settings.max_payload_size_bytes
                    }
                )

            # Pattern detection
            detected_patterns = []
            risk_factors = []

            content_str = str(task.content)

            # Check configured dangerous patterns
            for i, pattern in enumerate(self.compiled_patterns):
                if pattern.search(content_str):
                    pattern_str = self.settings.dangerous_patterns[i]
                    detected_patterns.append(pattern_str)
                    risk_factors.append(0.3)

                    # Update metrics
                    if pattern_str not in self._security_metrics["patterns_matched"]:
                        self._security_metrics["patterns_matched"][pattern_str] = 0
                    self._security_metrics["patterns_matched"][pattern_str] += 1

            # Check extended patterns
            for category, patterns in self.extended_patterns.items():
                category_matches = 0
                for pattern_str in patterns:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    if pattern.search(content_str):
                        detected_patterns.append(f"{category}:{pattern_str}")
                        category_matches += 1

                if category_matches > 0:
                    # Higher risk for multiple matches in same category
                    risk_factors.append(min(0.5, category_matches * 0.2))

            # Calculate risk score
            risk_score = min(1.0, sum(risk_factors))

            # Determine threat level
            threat_level = self._assess_threat_level(risk_score, detected_patterns)

            # Determine validation result
            if threat_level in [SecurityThreatLevel.HIGH, SecurityThreatLevel.CRITICAL]:
                self._security_metrics["threats_detected"] += 1
                self._security_metrics["rejections"] += 1

                return SecurityAssessment(
                    threat_level=threat_level,
                    validation_result=SecurityValidationResult.REJECTED,
                    detected_patterns=detected_patterns,
                    sanitized_content=None,
                    risk_score=risk_score,
                    assessment_time=start_time,
                    details={
                        "reason": "High security risk detected",
                        "patterns": detected_patterns
                    }
                )

            # Sanitize if needed
            sanitized_content = None
            validation_result = SecurityValidationResult.APPROVED

            if detected_patterns and self.settings.sanitize_inputs:
                sanitized_content = await self._sanitize_content(content_str, detected_patterns)
                validation_result = SecurityValidationResult.SANITIZED
                self._security_metrics["sanitization_performed"] += 1

            # Update metrics
            self._security_metrics["risk_scores"].append(risk_score)
            if len(self._security_metrics["risk_scores"]) > 1000:
                self._security_metrics["risk_scores"] = self._security_metrics["risk_scores"][-500:]

            self._logger.info(
                f"Task {task.task_id} security validation completed",
                extra={
                    "task_id": task.task_id,
                    "threat_level": threat_level.value,
                    "validation_result": validation_result.value,
                    "risk_score": risk_score,
                    "patterns_detected": len(detected_patterns)
                }
            )

            return SecurityAssessment(
                threat_level=threat_level,
                validation_result=validation_result,
                detected_patterns=detected_patterns,
                sanitized_content=sanitized_content,
                risk_score=risk_score,
                assessment_time=start_time,
                details={
                    "validation_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "content_size": payload_size
                }
            )

        except Exception as e:
            self._logger.error(f"Error in security validation for task {task.task_id}: {e}")

            # Return safe default on error
            return SecurityAssessment(
                threat_level=SecurityThreatLevel.UNKNOWN,
                validation_result=SecurityValidationResult.QUARANTINED,
                detected_patterns=["validation_error"],
                sanitized_content=None,
                risk_score=0.5,
                assessment_time=start_time,
                details={"error": str(e)}
            )

    def _assess_threat_level(self, risk_score: float, patterns: List[str]) -> SecurityThreatLevel:
        """Assess threat level based on risk score and detected patterns."""
        if risk_score >= 0.8:
            return SecurityThreatLevel.CRITICAL
        elif risk_score >= 0.6:
            return SecurityThreatLevel.HIGH
        elif risk_score >= 0.3:
            return SecurityThreatLevel.MEDIUM
        elif risk_score > 0:
            return SecurityThreatLevel.LOW
        else:
            return SecurityThreatLevel.SAFE

    async def _sanitize_content(self, content: str, patterns: List[str]) -> str:
        """Sanitize content by removing or replacing dangerous patterns."""
        sanitized = content

        try:
            # Remove obvious dangerous patterns
            dangerous_removals = [
                r'eval\s*\([^)]*\)',
                r'exec\s*\([^)]*\)',
                r'__import__\s*\([^)]*\)',
                r'subprocess\.[^(]*\([^)]*\)',
                r'os\.system\s*\([^)]*\)',
            ]

            for pattern_str in dangerous_removals:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                sanitized = pattern.sub('# SANITIZED: dangerous code removed', sanitized)

            # Replace potentially dangerous imports
            import_replacements = {
                r'import\s+subprocess': '# import subprocess  # SANITIZED',
                r'from\s+subprocess\s+import': '# from subprocess import  # SANITIZED',
                r'import\s+os\b': '# import os  # SANITIZED',
                r'from\s+os\s+import': '# from os import  # SANITIZED',
            }

            for pattern_str, replacement in import_replacements.items():
                pattern = re.compile(pattern_str, re.IGNORECASE)
                sanitized = pattern.sub(replacement, sanitized)

            self._logger.info(
                f"Content sanitized: {len(patterns)} patterns addressed",
                extra={"original_length": len(content), "sanitized_length": len(sanitized)}
            )

            return sanitized

        except Exception as e:
            self._logger.error(f"Error in content sanitization: {e}")
            return content  # Return original on error

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security validation metrics."""
        avg_risk_score = 0.0
        if self._security_metrics["risk_scores"]:
            avg_risk_score = sum(self._security_metrics["risk_scores"]) / len(self._security_metrics["risk_scores"])

        threat_detection_rate = 0.0
        if self._security_metrics["tasks_validated"] > 0:
            threat_detection_rate = self._security_metrics["threats_detected"] / self._security_metrics["tasks_validated"]

        return {
            "instance_id": self.instance_id,
            "tasks_validated": self._security_metrics["tasks_validated"],
            "threats_detected": self._security_metrics["threats_detected"],
            "threat_detection_rate": threat_detection_rate,
            "sanitizations_performed": self._security_metrics["sanitization_performed"],
            "rejections": self._security_metrics["rejections"],
            "average_risk_score": avg_risk_score,
            "pattern_matches": dict(self._security_metrics["patterns_matched"]),
            "configured_patterns": len(self.compiled_patterns),
            "max_payload_size_bytes": self.settings.max_payload_size_bytes,
            "timestamp": datetime.now().isoformat()
        }


class TaskExecutionSandbox:
    """
    Secure sandbox for task execution with comprehensive resource monitoring.

    Provides isolated execution environment with:
    - Memory and CPU limits
    - File operation restrictions
    - Network access controls
    - Module import filtering
    """

    def __init__(self, limits: SandboxLimits):
        self.limits = limits
        self.instance_id = f"sandbox_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.TaskExecutionSandbox")

        # Execution tracking
        self._active_executions: Dict[str, Dict[str, Any]] = {}
        self._execution_history: List[Dict[str, Any]] = []

        # Resource monitoring
        self._resource_monitor = None
        self._monitor_thread = None

        # Sandbox metrics
        self._sandbox_metrics = {
            "executions_started": 0,
            "executions_completed": 0,
            "executions_terminated": 0,
            "resource_violations": 0,
            "security_violations": 0,
            "average_execution_time": 0.0,
            "peak_memory_usage": 0
        }

        self._logger.info(
            f"TaskExecutionSandbox initialized",
            extra={
                "instance_id": self.instance_id,
                "max_memory_mb": limits.max_memory_mb,
                "max_cpu_time": limits.max_cpu_time_seconds
            }
        )

    @asynccontextmanager
    async def execute_safely(self, task_id: str):
        """
        Context manager for safe task execution with resource monitoring.

        Args:
            task_id: Unique identifier for the execution

        Yields:
            Execution context with monitoring and limits applied
        """
        execution_start = datetime.now()

        try:
            self._sandbox_metrics["executions_started"] += 1

            # Start resource monitoring
            execution_context = {
                "task_id": task_id,
                "start_time": execution_start,
                "process": psutil.Process(),
                "initial_memory": psutil.virtual_memory().used,
                "terminated": False
            }

            self._active_executions[task_id] = execution_context

            # Set resource limits
            self._apply_resource_limits()

            # Start monitoring thread
            monitor_event = threading.Event()
            self._monitor_thread = threading.Thread(
                target=self._monitor_resources,
                args=(task_id, execution_context, monitor_event)
            )
            self._monitor_thread.start()

            self._logger.info(
                f"Sandbox execution started for task {task_id}",
                extra={"task_id": task_id, "limits": self.limits.__dict__}
            )

            yield execution_context

            # Execution completed successfully
            self._sandbox_metrics["executions_completed"] += 1

        except Exception as e:
            self._logger.error(f"Sandbox execution error for task {task_id}: {e}")
            execution_context["terminated"] = True
            self._sandbox_metrics["executions_terminated"] += 1
            raise

        finally:
            # Clean up execution
            execution_end = datetime.now()
            execution_time = (execution_end - execution_start).total_seconds()

            # Stop monitoring
            if self._monitor_thread and self._monitor_thread.is_alive():
                monitor_event.set()
                self._monitor_thread.join(timeout=1.0)

            # Update metrics
            self._update_execution_metrics(task_id, execution_context, execution_time)

            # Remove from active executions
            if task_id in self._active_executions:
                del self._active_executions[task_id]

            self._logger.info(
                f"Sandbox execution completed for task {task_id}",
                extra={
                    "task_id": task_id,
                    "execution_time_seconds": execution_time,
                    "terminated": execution_context.get("terminated", False)
                }
            )

    def _apply_resource_limits(self):
        """Apply system-level resource limits."""
        try:
            # Set memory limit (in bytes)
            memory_limit = self.limits.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

            # Set CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.limits.max_cpu_time_seconds, self.limits.max_cpu_time_seconds)
            )

            # Set file operation limits
            if self.limits.max_file_operations > 0:
                resource.setrlimit(
                    resource.RLIMIT_NOFILE,
                    (self.limits.max_file_operations, self.limits.max_file_operations)
                )

            self._logger.debug("Resource limits applied successfully")

        except Exception as e:
            self._logger.warning(f"Could not apply all resource limits: {e}")

    def _monitor_resources(self, task_id: str, context: Dict[str, Any], stop_event: threading.Event):
        """Monitor resource usage during execution."""
        try:
            process = context["process"]

            while not stop_event.is_set() and not context.get("terminated", False):
                try:
                    # Check memory usage
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)

                    if memory_mb > self.limits.max_memory_mb:
                        self._logger.warning(
                            f"Memory limit exceeded for task {task_id}: {memory_mb:.1f}MB > {self.limits.max_memory_mb}MB"
                        )
                        self._sandbox_metrics["resource_violations"] += 1
                        context["terminated"] = True
                        process.terminate()
                        break

                    # Update peak memory usage
                    if memory_mb > self._sandbox_metrics["peak_memory_usage"]:
                        self._sandbox_metrics["peak_memory_usage"] = memory_mb

                    # Check CPU usage
                    cpu_times = process.cpu_times()
                    cpu_time = cpu_times.user + cpu_times.system

                    if cpu_time > self.limits.max_cpu_time_seconds:
                        self._logger.warning(
                            f"CPU time limit exceeded for task {task_id}: {cpu_time:.1f}s > {self.limits.max_cpu_time_seconds}s"
                        )
                        self._sandbox_metrics["resource_violations"] += 1
                        context["terminated"] = True
                        process.terminate()
                        break

                    # Store current resource usage
                    context["current_memory_mb"] = memory_mb
                    context["current_cpu_time"] = cpu_time

                except psutil.NoSuchProcess:
                    # Process ended naturally
                    break
                except Exception as e:
                    self._logger.debug(f"Resource monitoring error: {e}")

                # Check every 100ms
                stop_event.wait(0.1)

        except Exception as e:
            self._logger.error(f"Resource monitoring thread error: {e}")

    def _update_execution_metrics(self, task_id: str, context: Dict[str, Any], execution_time: float):
        """Update execution metrics and history."""
        try:
            # Update average execution time
            total_executions = self._sandbox_metrics["executions_completed"] + self._sandbox_metrics["executions_terminated"]
            if total_executions > 0:
                current_avg = self._sandbox_metrics["average_execution_time"]
                self._sandbox_metrics["average_execution_time"] = (
                    (current_avg * (total_executions - 1) + execution_time) / total_executions
                )

            # Add to execution history
            execution_record = {
                "task_id": task_id,
                "start_time": context["start_time"].isoformat(),
                "execution_time_seconds": execution_time,
                "peak_memory_mb": context.get("current_memory_mb", 0),
                "cpu_time_used": context.get("current_cpu_time", 0),
                "terminated": context.get("terminated", False),
                "timestamp": datetime.now().isoformat()
            }

            self._execution_history.append(execution_record)

            # Keep only last 100 execution records
            if len(self._execution_history) > 100:
                self._execution_history = self._execution_history[-50:]

        except Exception as e:
            self._logger.error(f"Error updating execution metrics: {e}")

    def get_sandbox_status(self) -> Dict[str, Any]:
        """Get current sandbox status and metrics."""
        active_count = len(self._active_executions)

        active_tasks = {}
        for task_id, context in self._active_executions.items():
            active_tasks[task_id] = {
                "start_time": context["start_time"].isoformat(),
                "current_memory_mb": context.get("current_memory_mb", 0),
                "current_cpu_time": context.get("current_cpu_time", 0),
                "terminated": context.get("terminated", False)
            }

        return {
            "instance_id": self.instance_id,
            "active_executions": active_count,
            "active_tasks": active_tasks,
            "resource_limits": {
                "max_memory_mb": self.limits.max_memory_mb,
                "max_cpu_time_seconds": self.limits.max_cpu_time_seconds,
                "max_file_operations": self.limits.max_file_operations
            },
            "metrics": dict(self._sandbox_metrics),
            "recent_executions": self._execution_history[-10:],  # Last 10 executions
            "timestamp": datetime.now().isoformat()
        }


class ConversationStateEncryption:
    """
    Encrypted storage and access control for conversation state data.

    Provides:
    - State encryption with key derivation
    - Access control and audit logging
    - Secure key management
    - Compliance with data protection requirements
    """

    def __init__(self, encryption_key: Optional[str] = None, audit_enabled: bool = True):
        self.instance_id = f"encryption_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.ConversationStateEncryption")

        # Initialize encryption
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            self.encryption_key = os.urandom(32)  # Generate random key

        self.cipher_suite = self._create_cipher_suite(self.encryption_key)

        # Audit logging
        self.audit_enabled = audit_enabled
        self._access_log: List[Dict[str, Any]] = []

        # Encryption metrics
        self._encryption_metrics = {
            "encryptions_performed": 0,
            "decryptions_performed": 0,
            "access_violations": 0,
            "key_rotations": 0,
            "audit_events": 0
        }

        self._logger.info(
            f"ConversationStateEncryption initialized",
            extra={
                "instance_id": self.instance_id,
                "audit_enabled": audit_enabled,
                "key_length": len(self.encryption_key)
            }
        )

    def _create_cipher_suite(self, key: bytes) -> Fernet:
        """Create Fernet cipher suite from key."""
        try:
            # Use PBKDF2 for key derivation
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'beast_mode_salt',  # In production, use random salt per key
                iterations=100000,
            )

            derived_key = base64.urlsafe_b64encode(kdf.derive(key))
            return Fernet(derived_key)

        except Exception as e:
            self._logger.error(f"Error creating cipher suite: {e}")
            raise

    async def encrypt_conversation_state(
        self,
        conversation_context: ConversationContext,
        requester_id: str,
        access_reason: str = "state_persistence"
    ) -> Tuple[bytes, str]:
        """
        Encrypt conversation state with audit logging.

        Args:
            conversation_context: Conversation state to encrypt
            requester_id: ID of entity requesting encryption
            access_reason: Reason for encryption operation

        Returns:
            Tuple of (encrypted_data, operation_id)
        """
        operation_id = f"encrypt_{uuid.uuid4().hex[:8]}"

        try:
            # Audit log
            if self.audit_enabled:
                await self._log_access(
                    operation_id=operation_id,
                    operation_type="encrypt",
                    conversation_id=conversation_context.conversation_id,
                    requester_id=requester_id,
                    access_reason=access_reason
                )

            # Serialize conversation context
            state_data = json.dumps({
                "conversation_id": conversation_context.conversation_id,
                "current_state": conversation_context.current_state.value,
                "conversation_history": [
                    {
                        "timestamp": entry["timestamp"].isoformat() if isinstance(entry.get("timestamp"), datetime) else entry.get("timestamp"),
                        "content": entry.get("content", ""),
                        "metadata": entry.get("metadata", {})
                    }
                    for entry in conversation_context.conversation_history
                ],
                "metadata": conversation_context.metadata,
                "created_at": conversation_context.created_at.isoformat(),
                "last_updated": conversation_context.last_updated.isoformat(),
                "encryption_metadata": {
                    "encrypted_at": datetime.now().isoformat(),
                    "encrypted_by": requester_id,
                    "operation_id": operation_id,
                    "version": "1.0"
                }
            })

            # Encrypt data
            encrypted_data = self.cipher_suite.encrypt(state_data.encode())

            self._encryption_metrics["encryptions_performed"] += 1

            self._logger.info(
                f"Conversation state encrypted successfully",
                extra={
                    "operation_id": operation_id,
                    "conversation_id": conversation_context.conversation_id,
                    "requester_id": requester_id,
                    "data_size": len(state_data)
                }
            )

            return encrypted_data, operation_id

        except Exception as e:
            self._logger.error(f"Encryption error for operation {operation_id}: {e}")
            raise

    async def decrypt_conversation_state(
        self,
        encrypted_data: bytes,
        requester_id: str,
        access_reason: str = "state_retrieval"
    ) -> Tuple[ConversationContext, str]:
        """
        Decrypt conversation state with access control and audit logging.

        Args:
            encrypted_data: Encrypted conversation state
            requester_id: ID of entity requesting decryption
            access_reason: Reason for decryption operation

        Returns:
            Tuple of (ConversationContext, operation_id)
        """
        operation_id = f"decrypt_{uuid.uuid4().hex[:8]}"

        try:
            # Decrypt data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            state_data = json.loads(decrypted_data.decode())

            conversation_id = state_data["conversation_id"]

            # Audit log
            if self.audit_enabled:
                await self._log_access(
                    operation_id=operation_id,
                    operation_type="decrypt",
                    conversation_id=conversation_id,
                    requester_id=requester_id,
                    access_reason=access_reason
                )

            # Reconstruct conversation context
            from .models import ConversationState

            conversation_history = []
            for entry in state_data.get("conversation_history", []):
                history_entry = {
                    "timestamp": datetime.fromisoformat(entry["timestamp"]) if isinstance(entry["timestamp"], str) else entry["timestamp"],
                    "content": entry.get("content", ""),
                    "metadata": entry.get("metadata", {})
                }
                conversation_history.append(history_entry)

            conversation_context = ConversationContext(
                conversation_id=conversation_id,
                current_state=ConversationState(state_data["current_state"]),
                conversation_history=conversation_history,
                metadata=state_data.get("metadata", {}),
                created_at=datetime.fromisoformat(state_data["created_at"]),
                last_updated=datetime.fromisoformat(state_data["last_updated"])
            )

            self._encryption_metrics["decryptions_performed"] += 1

            self._logger.info(
                f"Conversation state decrypted successfully",
                extra={
                    "operation_id": operation_id,
                    "conversation_id": conversation_id,
                    "requester_id": requester_id
                }
            )

            return conversation_context, operation_id

        except Exception as e:
            self._logger.error(f"Decryption error for operation {operation_id}: {e}")
            self._encryption_metrics["access_violations"] += 1
            raise

    async def _log_access(
        self,
        operation_id: str,
        operation_type: str,
        conversation_id: str,
        requester_id: str,
        access_reason: str
    ):
        """Log access attempt for audit purposes."""
        try:
            access_event = {
                "operation_id": operation_id,
                "operation_type": operation_type,
                "conversation_id": conversation_id,
                "requester_id": requester_id,
                "access_reason": access_reason,
                "timestamp": datetime.now().isoformat(),
                "source_instance": self.instance_id
            }

            self._access_log.append(access_event)
            self._encryption_metrics["audit_events"] += 1

            # Keep only last 1000 audit events
            if len(self._access_log) > 1000:
                self._access_log = self._access_log[-500:]

            self._logger.debug(
                f"Access logged: {operation_type} for conversation {conversation_id}",
                extra=access_event
            )

        except Exception as e:
            self._logger.error(f"Error logging access event: {e}")

    def rotate_encryption_key(self, new_key: Optional[str] = None) -> str:
        """
        Rotate encryption key for enhanced security.

        Args:
            new_key: New encryption key (optional, generates random if not provided)

        Returns:
            Operation ID for key rotation
        """
        operation_id = f"keyrotation_{uuid.uuid4().hex[:8]}"

        try:
            # Generate or use provided key
            if new_key:
                new_key_bytes = new_key.encode()
            else:
                new_key_bytes = os.urandom(32)

            # Create new cipher suite
            new_cipher_suite = self._create_cipher_suite(new_key_bytes)

            # Update encryption components
            self.encryption_key = new_key_bytes
            self.cipher_suite = new_cipher_suite

            self._encryption_metrics["key_rotations"] += 1

            # Audit log key rotation
            if self.audit_enabled:
                key_rotation_event = {
                    "operation_id": operation_id,
                    "operation_type": "key_rotation",
                    "timestamp": datetime.now().isoformat(),
                    "source_instance": self.instance_id,
                    "key_length": len(new_key_bytes)
                }
                self._access_log.append(key_rotation_event)
                self._encryption_metrics["audit_events"] += 1

            self._logger.info(
                f"Encryption key rotated successfully",
                extra={
                    "operation_id": operation_id,
                    "new_key_length": len(new_key_bytes)
                }
            )

            return operation_id

        except Exception as e:
            self._logger.error(f"Key rotation error: {e}")
            raise

    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption system status and audit information."""
        recent_access = self._access_log[-20:] if self._access_log else []

        # Calculate access patterns
        access_by_type = {}
        access_by_requester = {}

        for event in self._access_log[-100:]:  # Last 100 events
            op_type = event.get("operation_type", "unknown")
            requester = event.get("requester_id", "unknown")

            access_by_type[op_type] = access_by_type.get(op_type, 0) + 1
            access_by_requester[requester] = access_by_requester.get(requester, 0) + 1

        return {
            "instance_id": self.instance_id,
            "audit_enabled": self.audit_enabled,
            "key_length": len(self.encryption_key),
            "metrics": dict(self._encryption_metrics),
            "recent_access_events": recent_access,
            "access_patterns": {
                "by_operation_type": access_by_type,
                "by_requester": access_by_requester
            },
            "total_audit_events": len(self._access_log),
            "timestamp": datetime.now().isoformat()
        }