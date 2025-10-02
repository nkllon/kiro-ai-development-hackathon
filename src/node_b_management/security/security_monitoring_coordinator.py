"""
Security Monitoring Coordinator for Node B Management

Provides comprehensive security monitoring, violation detection, configuration
change validation, encrypted storage, and audit trail management for Node B instances.
"""

import os
import json
import hashlib
import logging
import asyncio
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import threading
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..core.node_b_component import NodeBComponent
from .security_configuration_manager import SecurityConfigurationManager, SecurityViolation


class MonitoringLevel(Enum):
    """Security monitoring levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IsolationAction(Enum):
    """Security isolation actions"""
    NONE = "none"
    WARN = "warn"
    THROTTLE = "throttle"
    QUARANTINE = "quarantine"
    ISOLATE = "isolate"
    SHUTDOWN = "shutdown"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    node_id: str
    event_type: str
    description: str
    severity: MonitoringLevel
    timestamp: datetime
    source_component: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    isolation_action: IsolationAction = IsolationAction.NONE
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            "event_id": self.event_id,
            "node_id": self.node_id,
            "event_type": self.event_type,
            "description": self.description,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "source_component": self.source_component,
            "metadata": self.metadata,
            "isolation_action": self.isolation_action.value,
            "resolved": self.resolved
        }


@dataclass
class ConfigurationChange:
    """Configuration change record"""
    change_id: str
    node_id: str
    component: str
    change_type: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    approved: bool = False
    applied: bool = False
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "change_id": self.change_id,
            "node_id": self.node_id,
            "component": self.component,
            "change_type": self.change_type,
            "old_value": str(self.old_value),
            "new_value": str(self.new_value),
            "timestamp": self.timestamp.isoformat(),
            "approved": self.approved,
            "applied": self.applied,
            "validation_results": self.validation_results
        }


@dataclass
class NetworkCommunication:
    """Network communication record for audit trail"""
    comm_id: str
    node_id: str
    direction: str  # "inbound" or "outbound"
    peer_node: str
    message_type: str
    message_size: int
    timestamp: datetime
    encrypted: bool = False
    authenticated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for audit storage"""
        return {
            "comm_id": self.comm_id,
            "node_id": self.node_id,
            "direction": self.direction,
            "peer_node": self.peer_node,
            "message_type": self.message_type,
            "message_size": self.message_size,
            "timestamp": self.timestamp.isoformat(),
            "encrypted": self.encrypted,
            "authenticated": self.authenticated,
            "metadata": self.metadata
        }


class SecurityMonitoringCoordinator(NodeBComponent):
    """
    Security Monitoring Coordinator for Node B instances
    
    Provides comprehensive security monitoring including violation detection,
    configuration change validation, encrypted storage, and audit trail management.
    
    Requirements: 4.5, 4.6, 4.7
    """

    def __init__(self, node_id: str = None, security_config_manager: SecurityConfigurationManager = None):
        """
        Initialize Security Monitoring Coordinator
        
        Args:
            node_id: Node B instance ID for security context
            security_config_manager: Security configuration manager instance
        """
        super().__init__("security_monitoring_coordinator", node_id)
        
        # Security configuration manager
        self._security_config_manager = security_config_manager or SecurityConfigurationManager(node_id)
        
        # Monitoring state
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_interval = 30  # seconds
        self._shutdown_event = threading.Event()
        
        # Security events and violations
        self._security_events: List[SecurityEvent] = []
        self._active_violations: Set[str] = set()
        self._isolation_actions: Dict[str, IsolationAction] = {}
        
        # Configuration change tracking
        self._pending_config_changes: List[ConfigurationChange] = []
        self._applied_config_changes: List[ConfigurationChange] = []
        self._config_validators: Dict[str, Callable] = {}
        
        # Network communication audit
        self._network_communications: List[NetworkCommunication] = []
        self._communication_patterns: Dict[str, List[datetime]] = {}
        
        # Encrypted storage
        self._encrypted_storage_path = Path(os.getenv('NODE_B_ENCRYPTED_STORAGE_PATH', './node_b_encrypted_storage'))
        self._encrypted_storage_path.mkdir(exist_ok=True)
        
        # Monitoring thresholds
        self._violation_thresholds = {
            "failed_auth_per_hour": 10,
            "config_changes_per_hour": 5,
            "network_errors_per_hour": 20,
            "encryption_failures_per_hour": 3,
            "ssl_errors_per_hour": 5
        }
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        self._logger.info(f"SecurityMonitoringCoordinator initialized for node {self.node_id}")

    async def start_monitoring(self) -> bool:
        """
        Start security monitoring
        
        Returns:
            bool: True if monitoring started successfully, False otherwise
            
        Requirements: 4.5, 4.6, 4.7
        """
        try:
            if self._monitoring_active:
                self._logger.warning("Security monitoring already active")
                return True
            
            # Initialize security configuration manager
            await self._security_config_manager.load_credentials()
            
            # Start monitoring thread
            self._monitoring_active = True
            self._shutdown_event.clear()
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                name=f"SecurityMonitoring-{self.node_id}",
                daemon=True
            )
            self._monitoring_thread.start()
            
            # Register default event handlers
            await self._register_default_event_handlers()
            
            # Record monitoring start event
            await self._record_security_event(
                "monitoring_started",
                "Security monitoring activated",
                MonitoringLevel.MEDIUM,
                "security_monitoring_coordinator"
            )
            
            self._logger.info("Security monitoring started successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to start security monitoring: {e}")
            return False

    async def stop_monitoring(self) -> bool:
        """
        Stop security monitoring
        
        Returns:
            bool: True if monitoring stopped successfully, False otherwise
        """
        try:
            if not self._monitoring_active:
                self._logger.warning("Security monitoring not active")
                return True
            
            # Signal shutdown
            self._monitoring_active = False
            self._shutdown_event.set()
            
            # Wait for monitoring thread to finish
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=10)
                if self._monitoring_thread.is_alive():
                    self._logger.warning("Monitoring thread did not shut down gracefully")
            
            # Record monitoring stop event
            await self._record_security_event(
                "monitoring_stopped",
                "Security monitoring deactivated",
                MonitoringLevel.MEDIUM,
                "security_monitoring_coordinator"
            )
            
            self._logger.info("Security monitoring stopped successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to stop security monitoring: {e}")
            return False

    async def detect_security_violations(self) -> List[SecurityViolation]:
        """
        Detect security violations and recommend isolation actions
        
        Returns:
            List[SecurityViolation]: List of detected security violations
            
        Requirements: 4.5, 4.6
        """
        try:
            violations = []
            
            # Get violations from security configuration manager
            config_violations = await self._security_config_manager.detect_security_violations(self.node_id)
            
            # Convert to SecurityViolation objects
            for violation_dict in config_violations:
                violation = SecurityViolation(
                    violation_id=violation_dict["violation_id"],
                    node_id=violation_dict["node_id"],
                    violation_type=violation_dict["violation_type"],
                    description=violation_dict["description"],
                    severity=violation_dict["severity"],
                    timestamp=datetime.fromisoformat(violation_dict["timestamp"]),
                    resolved=violation_dict["resolved"]
                )
                violations.append(violation)
            
            # Detect additional violations from monitoring data
            monitoring_violations = await self._detect_monitoring_violations()
            violations.extend(monitoring_violations)
            
            # Determine isolation actions for new violations
            for violation in violations:
                if violation.violation_id not in self._active_violations:
                    isolation_action = await self._determine_isolation_action(violation)
                    self._isolation_actions[violation.violation_id] = isolation_action
                    self._active_violations.add(violation.violation_id)
                    
                    # Execute isolation action if necessary
                    if isolation_action != IsolationAction.NONE:
                        await self._execute_isolation_action(violation, isolation_action)
            
            # Record violation detection event
            await self._record_security_event(
                "violations_detected",
                f"Detected {len(violations)} security violations",
                MonitoringLevel.HIGH if violations else MonitoringLevel.LOW,
                "security_monitoring_coordinator",
                {"violation_count": len(violations)}
            )
            
            return violations
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Security violation detection failed: {e}")
            return []

    async def validate_configuration_change(self, component: str, change_type: str, old_value: Any, new_value: Any) -> bool:
        """
        Validate configuration change before application
        
        Args:
            component: Component name
            change_type: Type of configuration change
            old_value: Current configuration value
            new_value: Proposed new configuration value
            
        Returns:
            bool: True if change is valid and approved, False otherwise
            
        Requirements: 4.5, 4.6
        """
        try:
            # Create configuration change record
            change_id = hashlib.md5(f"{component}:{change_type}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            config_change = ConfigurationChange(
                change_id=change_id,
                node_id=self.node_id,
                component=component,
                change_type=change_type,
                old_value=old_value,
                new_value=new_value,
                timestamp=datetime.now()
            )
            
            # Validate change using registered validators
            validation_results = {}
            validator_key = f"{component}:{change_type}"
            
            if validator_key in self._config_validators:
                try:
                    validator = self._config_validators[validator_key]
                    validation_result = await validator(old_value, new_value)
                    validation_results[validator_key] = validation_result
                except Exception as e:
                    validation_results[validator_key] = {"valid": False, "error": str(e)}
            
            # Default security validation
            security_validation = await self._validate_security_implications(component, change_type, old_value, new_value)
            validation_results["security"] = security_validation
            
            # Determine if change is approved
            all_valid = all(
                result.get("valid", False) if isinstance(result, dict) else bool(result)
                for result in validation_results.values()
            )
            
            config_change.validation_results = validation_results
            config_change.approved = all_valid
            
            # Store configuration change
            self._pending_config_changes.append(config_change)
            
            # Record configuration change event
            await self._record_security_event(
                "config_change_validated",
                f"Configuration change {change_type} for {component}: {'approved' if all_valid else 'rejected'}",
                MonitoringLevel.MEDIUM,
                "security_monitoring_coordinator",
                {
                    "change_id": change_id,
                    "component": component,
                    "change_type": change_type,
                    "approved": all_valid,
                    "validation_results": validation_results
                }
            )
            
            if all_valid:
                self._logger.info(f"Configuration change approved: {change_id}")
            else:
                self._logger.warning(f"Configuration change rejected: {change_id} - {validation_results}")
                
                # Record security violation for rejected change
                await self._record_security_event(
                    "config_change_rejected",
                    f"Potentially unsafe configuration change rejected: {change_type}",
                    MonitoringLevel.HIGH,
                    "security_monitoring_coordinator",
                    {"change_id": change_id, "validation_results": validation_results}
                )
            
            return all_valid
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Configuration change validation failed: {e}")
            return False

    async def apply_configuration_change(self, change_id: str) -> bool:
        """
        Apply an approved configuration change
        
        Args:
            change_id: ID of the configuration change to apply
            
        Returns:
            bool: True if change applied successfully, False otherwise
        """
        try:
            # Find the configuration change
            config_change = None
            for change in self._pending_config_changes:
                if change.change_id == change_id:
                    config_change = change
                    break
            
            if not config_change:
                self._logger.error(f"Configuration change not found: {change_id}")
                return False
            
            if not config_change.approved:
                self._logger.error(f"Configuration change not approved: {change_id}")
                return False
            
            if config_change.applied:
                self._logger.warning(f"Configuration change already applied: {change_id}")
                return True
            
            # Apply the change (this would be component-specific implementation)
            # For now, we just mark it as applied
            config_change.applied = True
            
            # Move to applied changes
            self._pending_config_changes.remove(config_change)
            self._applied_config_changes.append(config_change)
            
            # Record application event
            await self._record_security_event(
                "config_change_applied",
                f"Configuration change applied: {config_change.change_type} for {config_change.component}",
                MonitoringLevel.MEDIUM,
                "security_monitoring_coordinator",
                {"change_id": change_id}
            )
            
            self._logger.info(f"Configuration change applied successfully: {change_id}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to apply configuration change: {e}")
            return False

    async def store_encrypted_data(self, key: str, data: Any) -> bool:
        """
        Store sensitive data in encrypted local storage
        
        Args:
            key: Storage key
            data: Data to store
            
        Returns:
            bool: True if stored successfully, False otherwise
            
        Requirements: 4.5
        """
        try:
            # Convert data to JSON string
            data_str = json.dumps(data) if not isinstance(data, str) else data
            
            # Encrypt data using security configuration manager
            encrypted_data = await self._security_config_manager.encrypt_sensitive_data(data_str)
            
            if not encrypted_data:
                self._logger.error("Failed to encrypt data for storage")
                return False
            
            # Store encrypted data to file
            storage_file = self._encrypted_storage_path / f"{key}.enc"
            
            with open(storage_file, 'w') as f:
                json.dump({
                    "encrypted_data": encrypted_data,
                    "timestamp": datetime.now().isoformat(),
                    "node_id": self.node_id
                }, f)
            
            # Record storage event
            await self._record_security_event(
                "encrypted_data_stored",
                f"Sensitive data stored with encryption: {key}",
                MonitoringLevel.LOW,
                "security_monitoring_coordinator",
                {"storage_key": key, "data_size": len(data_str)}
            )
            
            self._logger.debug(f"Encrypted data stored successfully: {key}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to store encrypted data: {e}")
            
            # Record encryption failure
            await self._record_security_event(
                "encryption_storage_failed",
                f"Failed to store encrypted data: {str(e)}",
                MonitoringLevel.HIGH,
                "security_monitoring_coordinator",
                {"storage_key": key, "error": str(e)}
            )
            
            return False

    async def retrieve_encrypted_data(self, key: str) -> Optional[Any]:
        """
        Retrieve sensitive data from encrypted local storage
        
        Args:
            key: Storage key
            
        Returns:
            Optional[Any]: Decrypted data if successful, None otherwise
        """
        try:
            storage_file = self._encrypted_storage_path / f"{key}.enc"
            
            if not storage_file.exists():
                self._logger.warning(f"Encrypted storage file not found: {key}")
                return None
            
            # Read encrypted data
            with open(storage_file, 'r') as f:
                storage_data = json.load(f)
            
            encrypted_data = storage_data.get("encrypted_data")
            if not encrypted_data:
                self._logger.error(f"No encrypted data found in storage file: {key}")
                return None
            
            # Decrypt data using security configuration manager
            decrypted_data = await self._security_config_manager.decrypt_sensitive_data(encrypted_data)
            
            if not decrypted_data:
                self._logger.error("Failed to decrypt stored data")
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                data = json.loads(decrypted_data)
            except json.JSONDecodeError:
                data = decrypted_data
            
            # Record retrieval event
            await self._record_security_event(
                "encrypted_data_retrieved",
                f"Sensitive data retrieved from encryption: {key}",
                MonitoringLevel.LOW,
                "security_monitoring_coordinator",
                {"storage_key": key}
            )
            
            self._logger.debug(f"Encrypted data retrieved successfully: {key}")
            return data
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to retrieve encrypted data: {e}")
            
            # Record decryption failure
            await self._record_security_event(
                "decryption_retrieval_failed",
                f"Failed to retrieve encrypted data: {str(e)}",
                MonitoringLevel.HIGH,
                "security_monitoring_coordinator",
                {"storage_key": key, "error": str(e)}
            )
            
            return None

    async def audit_network_communication(self, direction: str, peer_node: str, message_type: str, 
                                        message_size: int, encrypted: bool = False, 
                                        authenticated: bool = False, metadata: Dict[str, Any] = None) -> bool:
        """
        Audit network communication for comprehensive trail
        
        Args:
            direction: "inbound" or "outbound"
            peer_node: Peer node identifier
            message_type: Type of message
            message_size: Size of message in bytes
            encrypted: Whether message was encrypted
            authenticated: Whether message was authenticated
            metadata: Additional metadata
            
        Returns:
            bool: True if audit recorded successfully, False otherwise
            
        Requirements: 4.7
        """
        try:
            # Create communication record
            comm_id = hashlib.md5(f"{direction}:{peer_node}:{message_type}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            communication = NetworkCommunication(
                comm_id=comm_id,
                node_id=self.node_id,
                direction=direction,
                peer_node=peer_node,
                message_type=message_type,
                message_size=message_size,
                timestamp=datetime.now(),
                encrypted=encrypted,
                authenticated=authenticated,
                metadata=metadata or {}
            )
            
            # Store communication record
            self._network_communications.append(communication)
            
            # Update communication patterns for anomaly detection
            pattern_key = f"{direction}:{peer_node}:{message_type}"
            if pattern_key not in self._communication_patterns:
                self._communication_patterns[pattern_key] = []
            self._communication_patterns[pattern_key].append(datetime.now())
            
            # Keep pattern history manageable (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self._communication_patterns[pattern_key] = [
                ts for ts in self._communication_patterns[pattern_key] if ts > cutoff_time
            ]
            
            # Check for communication anomalies
            await self._check_communication_anomalies(pattern_key)
            
            # Keep communication log manageable
            if len(self._network_communications) > 10000:
                self._network_communications = self._network_communications[-5000:]  # Keep last 5000
            
            self._logger.debug(f"Network communication audited: {comm_id}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to audit network communication: {e}")
            return False

    async def get_security_events(self, limit: int = 100, severity: Optional[MonitoringLevel] = None) -> List[Dict[str, Any]]:
        """
        Get security events
        
        Args:
            limit: Maximum number of events to return
            severity: Filter by severity level
            
        Returns:
            List[Dict[str, Any]]: Security events
        """
        events = self._security_events
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # Sort by timestamp (most recent first)
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)
        
        return [e.to_dict() for e in events[:limit]]

    async def get_network_audit_trail(self, limit: int = 100, peer_node: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get network communication audit trail
        
        Args:
            limit: Maximum number of records to return
            peer_node: Filter by peer node
            
        Returns:
            List[Dict[str, Any]]: Network communication records
        """
        communications = self._network_communications
        
        if peer_node:
            communications = [c for c in communications if c.peer_node == peer_node]
        
        # Sort by timestamp (most recent first)
        communications = sorted(communications, key=lambda c: c.timestamp, reverse=True)
        
        return [c.to_dict() for c in communications[:limit]]

    async def get_configuration_changes(self, applied_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get configuration change history
        
        Args:
            applied_only: Return only applied changes
            
        Returns:
            List[Dict[str, Any]]: Configuration change records
        """
        if applied_only:
            changes = self._applied_config_changes
        else:
            changes = self._pending_config_changes + self._applied_config_changes
        
        # Sort by timestamp (most recent first)
        changes = sorted(changes, key=lambda c: c.timestamp, reverse=True)
        
        return [c.to_dict() for c in changes]

    async def register_configuration_validator(self, component: str, change_type: str, validator: Callable) -> bool:
        """
        Register a configuration change validator
        
        Args:
            component: Component name
            change_type: Type of configuration change
            validator: Validation function
            
        Returns:
            bool: True if registered successfully, False otherwise
        """
        try:
            validator_key = f"{component}:{change_type}"
            self._config_validators[validator_key] = validator
            
            self._logger.info(f"Configuration validator registered: {validator_key}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to register configuration validator: {e}")
            return False

    async def register_event_handler(self, event_type: str, handler: Callable) -> bool:
        """
        Register an event handler for security events
        
        Args:
            event_type: Type of security event
            handler: Event handler function
            
        Returns:
            bool: True if registered successfully, False otherwise
        """
        try:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            
            self._event_handlers[event_type].append(handler)
            
            self._logger.info(f"Event handler registered for: {event_type}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to register event handler: {e}")
            return False

    # Private helper methods

    def _monitoring_loop(self):
        """Main monitoring loop running in separate thread"""
        self._logger.info("Security monitoring loop started")
        
        while self._monitoring_active and not self._shutdown_event.is_set():
            try:
                # Run monitoring checks
                asyncio.run(self._run_monitoring_checks())
                
                # Wait for next interval or shutdown signal
                self._shutdown_event.wait(timeout=self._monitoring_interval)
                
            except Exception as e:
                self._logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retrying
        
        self._logger.info("Security monitoring loop stopped")

    async def _run_monitoring_checks(self):
        """Run periodic monitoring checks"""
        try:
            # Detect security violations
            violations = await self.detect_security_violations()
            
            # Check for threshold violations
            await self._check_threshold_violations()
            
            # Clean up old data
            await self._cleanup_old_data()
            
            # Update monitoring metrics
            self.increment_health_checks()
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Monitoring checks failed: {e}")

    async def _detect_monitoring_violations(self) -> List[SecurityViolation]:
        """Detect violations from monitoring data"""
        violations = []
        
        try:
            # Check for excessive security events
            recent_events = [e for e in self._security_events if e.timestamp > datetime.now() - timedelta(hours=1)]
            critical_events = [e for e in recent_events if e.severity == MonitoringLevel.CRITICAL]
            
            if len(critical_events) > 3:
                violation_id = hashlib.md5(f"excessive_critical_events:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
                violation = SecurityViolation(
                    violation_id=violation_id,
                    node_id=self.node_id,
                    violation_type="excessive_critical_events",
                    description=f"Excessive critical security events: {len(critical_events)} in last hour",
                    severity="high",
                    timestamp=datetime.now()
                )
                violations.append(violation)
            
            # Check for configuration change anomalies
            recent_changes = [c for c in self._pending_config_changes + self._applied_config_changes 
                            if c.timestamp > datetime.now() - timedelta(hours=1)]
            
            if len(recent_changes) > self._violation_thresholds["config_changes_per_hour"]:
                violation_id = hashlib.md5(f"excessive_config_changes:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
                violation = SecurityViolation(
                    violation_id=violation_id,
                    node_id=self.node_id,
                    violation_type="excessive_config_changes",
                    description=f"Excessive configuration changes: {len(recent_changes)} in last hour",
                    severity="medium",
                    timestamp=datetime.now()
                )
                violations.append(violation)
            
            return violations
            
        except Exception as e:
            self._logger.error(f"Failed to detect monitoring violations: {e}")
            return []

    async def _determine_isolation_action(self, violation: SecurityViolation) -> IsolationAction:
        """Determine appropriate isolation action for a violation"""
        try:
            # Map violation severity to isolation action
            severity_action_map = {
                "low": IsolationAction.NONE,
                "medium": IsolationAction.WARN,
                "high": IsolationAction.THROTTLE,
                "critical": IsolationAction.QUARANTINE
            }
            
            base_action = severity_action_map.get(violation.severity, IsolationAction.WARN)
            
            # Escalate based on violation type
            if violation.violation_type in ["excessive_auth_failures", "unresolved_critical_violations"]:
                if base_action == IsolationAction.QUARANTINE:
                    return IsolationAction.ISOLATE
                elif base_action == IsolationAction.THROTTLE:
                    return IsolationAction.QUARANTINE
            
            return base_action
            
        except Exception as e:
            self._logger.error(f"Failed to determine isolation action: {e}")
            return IsolationAction.WARN

    async def _execute_isolation_action(self, violation: SecurityViolation, action: IsolationAction):
        """Execute isolation action for a violation"""
        try:
            if action == IsolationAction.WARN:
                self._logger.warning(f"Security violation warning: {violation.description}")
            
            elif action == IsolationAction.THROTTLE:
                self._logger.warning(f"Security violation throttling: {violation.description}")
                # Implement throttling logic here
            
            elif action == IsolationAction.QUARANTINE:
                self._logger.error(f"Security violation quarantine: {violation.description}")
                # Implement quarantine logic here
            
            elif action == IsolationAction.ISOLATE:
                self._logger.critical(f"Security violation isolation: {violation.description}")
                # Implement isolation logic here
            
            elif action == IsolationAction.SHUTDOWN:
                self._logger.critical(f"Security violation shutdown: {violation.description}")
                # Implement shutdown logic here
            
            # Record isolation action
            await self._record_security_event(
                "isolation_action_executed",
                f"Executed isolation action {action.value} for violation {violation.violation_type}",
                MonitoringLevel.HIGH,
                "security_monitoring_coordinator",
                {
                    "violation_id": violation.violation_id,
                    "isolation_action": action.value,
                    "violation_type": violation.violation_type
                }
            )
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to execute isolation action: {e}")

    async def _validate_security_implications(self, component: str, change_type: str, old_value: Any, new_value: Any) -> Dict[str, Any]:
        """Validate security implications of configuration change"""
        try:
            validation_result = {"valid": True, "warnings": [], "errors": []}
            
            # Check for security-sensitive configuration changes
            security_sensitive_components = ["redis", "ssl", "auth", "encryption", "network"]
            
            if any(sensitive in component.lower() for sensitive in security_sensitive_components):
                validation_result["warnings"].append(f"Security-sensitive component: {component}")
            
            # Check for credential-related changes
            if "password" in change_type.lower() or "token" in change_type.lower() or "key" in change_type.lower():
                if isinstance(new_value, str) and len(new_value) < 8:
                    validation_result["valid"] = False
                    validation_result["errors"].append("Credential too short (minimum 8 characters)")
            
            # Check for SSL/TLS configuration changes
            if "ssl" in change_type.lower() or "tls" in change_type.lower():
                if isinstance(new_value, bool) and not new_value:
                    validation_result["warnings"].append("Disabling SSL/TLS reduces security")
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Security validation failed: {e}")
            return {"valid": False, "errors": [str(e)]}

    async def _check_threshold_violations(self):
        """Check for threshold violations"""
        try:
            current_time = datetime.now()
            one_hour_ago = current_time - timedelta(hours=1)
            
            # Count events by type in the last hour
            recent_events = [e for e in self._security_events if e.timestamp > one_hour_ago]
            event_counts = {}
            
            for event in recent_events:
                event_type = event.event_type
                if event_type not in event_counts:
                    event_counts[event_type] = 0
                event_counts[event_type] += 1
            
            # Check against thresholds
            for event_type, count in event_counts.items():
                threshold_key = f"{event_type}_per_hour"
                if threshold_key in self._violation_thresholds:
                    threshold = self._violation_thresholds[threshold_key]
                    if count > threshold:
                        await self._record_security_event(
                            "threshold_violation",
                            f"Threshold exceeded for {event_type}: {count} > {threshold}",
                            MonitoringLevel.HIGH,
                            "security_monitoring_coordinator",
                            {"event_type": event_type, "count": count, "threshold": threshold}
                        )
            
        except Exception as e:
            self._logger.error(f"Threshold violation check failed: {e}")

    async def _check_communication_anomalies(self, pattern_key: str):
        """Check for communication pattern anomalies"""
        try:
            if pattern_key not in self._communication_patterns:
                return
            
            timestamps = self._communication_patterns[pattern_key]
            
            # Check for excessive communication frequency
            recent_count = len([ts for ts in timestamps if ts > datetime.now() - timedelta(minutes=10)])
            
            if recent_count > 100:  # More than 100 messages in 10 minutes
                await self._record_security_event(
                    "communication_anomaly",
                    f"Excessive communication frequency: {recent_count} messages in 10 minutes for {pattern_key}",
                    MonitoringLevel.MEDIUM,
                    "security_monitoring_coordinator",
                    {"pattern_key": pattern_key, "message_count": recent_count}
                )
            
        except Exception as e:
            self._logger.error(f"Communication anomaly check failed: {e}")

    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)  # Keep 7 days of data
            
            # Clean up old security events
            self._security_events = [e for e in self._security_events if e.timestamp > cutoff_time]
            
            # Clean up old network communications
            self._network_communications = [c for c in self._network_communications if c.timestamp > cutoff_time]
            
            # Clean up old configuration changes
            self._applied_config_changes = [c for c in self._applied_config_changes if c.timestamp > cutoff_time]
            
        except Exception as e:
            self._logger.error(f"Data cleanup failed: {e}")

    async def _register_default_event_handlers(self):
        """Register default event handlers"""
        try:
            # Handler for critical events
            async def critical_event_handler(event: SecurityEvent):
                if event.severity == MonitoringLevel.CRITICAL:
                    self._logger.critical(f"CRITICAL SECURITY EVENT: {event.description}")
            
            await self.register_event_handler("*", critical_event_handler)
            
        except Exception as e:
            self._logger.error(f"Failed to register default event handlers: {e}")

    async def _record_security_event(self, event_type: str, description: str, severity: MonitoringLevel, 
                                   source_component: str, metadata: Dict[str, Any] = None) -> SecurityEvent:
        """Record a security event"""
        event_id = hashlib.md5(f"{event_type}:{description}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        event = SecurityEvent(
            event_id=event_id,
            node_id=self.node_id,
            event_type=event_type,
            description=description,
            severity=severity,
            timestamp=datetime.now(),
            source_component=source_component,
            metadata=metadata or {}
        )
        
        self._security_events.append(event)
        
        # Trigger event handlers
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    self._logger.error(f"Event handler failed: {e}")
        
        # Trigger wildcard handlers
        if "*" in self._event_handlers:
            for handler in self._event_handlers["*"]:
                try:
                    await handler(event)
                except Exception as e:
                    self._logger.error(f"Wildcard event handler failed: {e}")
        
        return event

    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get comprehensive monitoring status
        
        Returns:
            Dict[str, Any]: Monitoring status information
        """
        return {
            "monitoring_active": self._monitoring_active,
            "monitoring_interval": self._monitoring_interval,
            "total_security_events": len(self._security_events),
            "active_violations": len(self._active_violations),
            "pending_config_changes": len(self._pending_config_changes),
            "applied_config_changes": len(self._applied_config_changes),
            "network_communications": len(self._network_communications),
            "registered_validators": len(self._config_validators),
            "registered_event_handlers": sum(len(handlers) for handlers in self._event_handlers.values()),
            "encrypted_storage_path": str(self._encrypted_storage_path),
            "violation_thresholds": self._violation_thresholds.copy()
        }