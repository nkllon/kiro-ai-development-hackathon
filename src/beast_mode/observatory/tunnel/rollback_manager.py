"""
Configuration Rollback Management System

Handles safe rollback operations for tunnel configurations.
Implements rollback validation, safety checks, and recovery procedures.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .version_manager import VersionManager, VersionStatus, VersionMetadata
from .config_validator import ConfigValidator, ValidationResult

logger = logging.getLogger(__name__)


class RollbackStatus(Enum):
    """Rollback operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RollbackReason(Enum):
    """Rollback reason types"""
    CONFIGURATION_ERROR = "configuration_error"
    SERVICE_DISRUPTION = "service_disruption"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MANUAL_REQUEST = "manual_request"
    AUTOMATED_RECOVERY = "automated_recovery"


@dataclass
class RollbackOperation:
    """Rollback operation metadata"""
    operation_id: str
    timestamp: str
    tunnel_name: str
    from_version: str
    to_version: str
    reason: RollbackReason
    status: RollbackStatus
    description: Optional[str] = None
    initiated_by: Optional[str] = None
    validation_result: Optional[str] = None
    rollback_duration: Optional[float] = None
    error_message: Optional[str] = None


class RollbackManager:
    """Manages configuration rollback operations"""
    
    def __init__(self, version_manager: VersionManager, config_validator: ConfigValidator):
        self.version_manager = version_manager
        self.config_validator = config_validator
        self.rollback_log_file = Path("/tmp/tunnel_rollbacks.jsonl")
        
        # Log initialization
        self._log_action("init", "in_progress", {
            "version_manager_ready": True,
            "config_validator_ready": True,
            "rollback_log_file": str(self.rollback_log_file)
        })
        
        logger.info("RollbackManager initialized")
        self._log_action("init", "completed", {"status": "ready"})
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log actions in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "7.1",
            "action": action,
            "status": status
        }
        if details:
            log_entry["details"] = details
        
        print(json.dumps(log_entry))
    
    def _log_rollback_operation(self, operation: RollbackOperation):
        """Log rollback operation to file"""
        try:
            with open(self.rollback_log_file, 'a') as f:
                f.write(json.dumps({
                    "operation_id": operation.operation_id,
                    "timestamp": operation.timestamp,
                    "tunnel_name": operation.tunnel_name,
                    "from_version": operation.from_version,
                    "to_version": operation.to_version,
                    "reason": operation.reason.value,
                    "status": operation.status.value,
                    "description": operation.description,
                    "initiated_by": operation.initiated_by,
                    "validation_result": operation.validation_result,
                    "rollback_duration": operation.rollback_duration,
                    "error_message": operation.error_message
                }) + '\n')
        except Exception as e:
            logger.error(f"Failed to log rollback operation: {e}")
    
    def rollback_to_version(
        self,
        tunnel_name: str,
        target_version_id: str,
        reason: RollbackReason,
        description: Optional[str] = None,
        initiated_by: Optional[str] = None,
        validate_before_rollback: bool = True
    ) -> Tuple[bool, str]:
        """
        Rollback tunnel configuration to a specific version
        
        Args:
            tunnel_name: Name of the tunnel
            target_version_id: Version ID to rollback to
            reason: Reason for rollback
            description: Optional description
            initiated_by: Optional initiator identifier
            validate_before_rollback: Whether to validate before rollback
            
        Returns:
            Tuple of (success, operation_id or error message)
        """
        operation_id = f"rollback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        self._log_action("rollback_to_version", "in_progress", {
            "operation_id": operation_id,
            "tunnel_name": tunnel_name,
            "target_version": target_version_id,
            "reason": reason.value,
            "validate_before": validate_before_rollback
        })
        
        try:
            # Get current active version
            current_version_id = self.version_manager.get_active_version(tunnel_name)
            if not current_version_id:
                error_msg = f"No active version found for tunnel {tunnel_name}"
                self._log_action("rollback_to_version", "error", {
                    "error": error_msg,
                    "operation_id": operation_id
                })
                return False, error_msg
            
            # Check if target version exists
            target_config = self.version_manager.get_version(target_version_id)
            if not target_config:
                error_msg = f"Target version {target_version_id} not found"
                self._log_action("rollback_to_version", "error", {
                    "error": error_msg,
                    "operation_id": operation_id
                })
                return False, error_msg
            
            # Create rollback operation record
            operation = RollbackOperation(
                operation_id=operation_id,
                timestamp=datetime.utcnow().isoformat() + "Z",
                tunnel_name=tunnel_name,
                from_version=current_version_id,
                to_version=target_version_id,
                reason=reason,
                status=RollbackStatus.IN_PROGRESS,
                description=description,
                initiated_by=initiated_by
            )
            
            # Validate target configuration if requested
            validation_result = None
            if validate_before_rollback:
                validation_result = self.config_validator.validate_config(target_config)
                operation.validation_result = validation_result.summary
                
                if not validation_result.is_valid:
                    error_msg = f"Target configuration validation failed: {validation_result.summary}"
                    operation.status = RollbackStatus.FAILED
                    operation.error_message = error_msg
                    self._log_rollback_operation(operation)
                    
                    self._log_action("rollback_to_version", "error", {
                        "error": error_msg,
                        "operation_id": operation_id,
                        "validation_issues": len(validation_result.issues)
                    })
                    return False, error_msg
            
            # Perform rollback
            start_time = datetime.utcnow()
            success = self._perform_rollback(operation)
            end_time = datetime.utcnow()
            
            # Update operation status
            operation.rollback_duration = (end_time - start_time).total_seconds()
            if success:
                operation.status = RollbackStatus.COMPLETED
            else:
                operation.status = RollbackStatus.FAILED
                operation.error_message = "Rollback operation failed"
            
            # Log rollback operation
            self._log_rollback_operation(operation)
            
            if success:
                self._log_action("rollback_to_version", "completed", {
                    "operation_id": operation_id,
                    "rollback_duration": operation.rollback_duration,
                    "validation_passed": validation_result.is_valid if validation_result else True
                })
                return True, operation_id
            else:
                self._log_action("rollback_to_version", "error", {
                    "error": "Rollback operation failed",
                    "operation_id": operation_id
                })
                return False, "Rollback operation failed"
            
        except Exception as e:
            error_msg = f"Rollback failed with exception: {str(e)}"
            self._log_action("rollback_to_version", "error", {
                "error": error_msg,
                "error_type": type(e).__name__,
                "operation_id": operation_id
            })
            return False, error_msg
    
    def _perform_rollback(self, operation: RollbackOperation) -> bool:
        """Perform the actual rollback operation"""
        try:
            # Set target version as active
            success = self.version_manager.set_active_version(operation.to_version)
            
            if success:
                # Update version status to indicate rollback
                target_metadata = self.version_manager.get_version_info(operation.to_version)
                if target_metadata:
                    target_metadata.status = VersionStatus.ROLLBACK
                    self.version_manager._save_metadata()
            
            return success
            
        except Exception as e:
            logger.error(f"Rollback operation failed: {e}")
            return False
    
    def rollback_to_latest_stable(
        self,
        tunnel_name: str,
        reason: RollbackReason,
        description: Optional[str] = None,
        initiated_by: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Rollback to the latest stable version
        
        Args:
            tunnel_name: Name of the tunnel
            reason: Reason for rollback
            description: Optional description
            initiated_by: Optional initiator identifier
            
        Returns:
            Tuple of (success, operation_id or error message)
        """
        self._log_action("rollback_to_latest_stable", "in_progress", {
            "tunnel_name": tunnel_name,
            "reason": reason.value
        })
        
        try:
            # Get latest stable version (most recent backup)
            versions = self.version_manager.list_versions(
                tunnel_name=tunnel_name,
                status=VersionStatus.BACKUP,
                limit=1
            )
            
            if not versions:
                error_msg = f"No stable versions found for tunnel {tunnel_name}"
                self._log_action("rollback_to_latest_stable", "error", {
                    "error": error_msg
                })
                return False, error_msg
            
            latest_stable = versions[0]
            
            return self.rollback_to_version(
                tunnel_name=tunnel_name,
                target_version_id=latest_stable.version_id,
                reason=reason,
                description=description or f"Rollback to latest stable version",
                initiated_by=initiated_by
            )
            
        except Exception as e:
            error_msg = f"Failed to rollback to latest stable: {str(e)}"
            self._log_action("rollback_to_latest_stable", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, error_msg
    
    def emergency_rollback(
        self,
        tunnel_name: str,
        description: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Perform emergency rollback to last known good configuration
        
        Args:
            tunnel_name: Name of the tunnel
            description: Optional description
            
        Returns:
            Tuple of (success, operation_id or error message)
        """
        self._log_action("emergency_rollback", "in_progress", {
            "tunnel_name": tunnel_name,
            "emergency": True
        })
        
        try:
            # Find the most recent version that's not the current active one
            versions = self.version_manager.list_versions(tunnel_name=tunnel_name)
            
            # Filter out current active version
            current_version = self.version_manager.get_active_version(tunnel_name)
            available_versions = [
                v for v in versions 
                if v.version_id != current_version and v.status != VersionStatus.ACTIVE
            ]
            
            if not available_versions:
                error_msg = f"No rollback targets available for tunnel {tunnel_name}"
                self._log_action("emergency_rollback", "error", {
                    "error": error_msg
                })
                return False, error_msg
            
            # Use the most recent available version
            target_version = available_versions[0]
            
            return self.rollback_to_version(
                tunnel_name=tunnel_name,
                target_version_id=target_version.version_id,
                reason=RollbackReason.AUTOMATED_RECOVERY,
                description=description or "Emergency rollback to last known good configuration",
                initiated_by="emergency_system",
                validate_before_rollback=False  # Skip validation in emergency
            )
            
        except Exception as e:
            error_msg = f"Emergency rollback failed: {str(e)}"
            self._log_action("emergency_rollback", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, error_msg
    
    def get_rollback_history(
        self,
        tunnel_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get rollback operation history
        
        Args:
            tunnel_name: Filter by tunnel name
            limit: Limit number of results
            
        Returns:
            List of rollback operations
        """
        self._log_action("get_rollback_history", "in_progress", {
            "tunnel_name": tunnel_name,
            "limit": limit
        })
        
        try:
            operations = []
            
            if not self.rollback_log_file.exists():
                self._log_action("get_rollback_history", "completed", {
                    "operations_found": 0,
                    "message": "No rollback history found"
                })
                return []
            
            with open(self.rollback_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        operation = json.loads(line.strip())
                        
                        # Apply filters
                        if tunnel_name and operation.get("tunnel_name") != tunnel_name:
                            continue
                        
                        operations.append(operation)
            
            # Sort by timestamp (newest first)
            operations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Apply limit
            if limit:
                operations = operations[:limit]
            
            self._log_action("get_rollback_history", "completed", {
                "operations_found": len(operations),
                "filters_applied": {
                    "tunnel_name": tunnel_name,
                    "limit": limit
                }
            })
            
            return operations
            
        except Exception as e:
            self._log_action("get_rollback_history", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return []
    
    def validate_rollback_safety(
        self,
        tunnel_name: str,
        target_version_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate if rollback is safe to perform
        
        Args:
            tunnel_name: Name of the tunnel
            target_version_id: Target version ID
            
        Returns:
            Tuple of (is_safe, safety_issues)
        """
        self._log_action("validate_rollback_safety", "in_progress", {
            "tunnel_name": tunnel_name,
            "target_version": target_version_id
        })
        
        try:
            safety_issues = []
            
            # Check if target version exists
            target_config = self.version_manager.get_version(target_version_id)
            if not target_config:
                safety_issues.append(f"Target version {target_version_id} not found")
            
            # Check if target version is for the correct tunnel
            if target_config and target_config.get("tunnel") != tunnel_name:
                safety_issues.append(f"Target version is for different tunnel")
            
            # Validate target configuration
            if target_config:
                validation_result = self.config_validator.validate_config(target_config)
                if not validation_result.is_valid:
                    safety_issues.append(f"Target configuration has validation issues: {validation_result.summary}")
            
            # Check for recent rollbacks (prevent rollback loops)
            recent_rollbacks = self.get_rollback_history(tunnel_name=tunnel_name, limit=3)
            recent_rollback_count = len([
                r for r in recent_rollbacks 
                if r.get("to_version") == target_version_id
            ])
            
            if recent_rollback_count > 0:
                safety_issues.append(f"Recent rollback to this version detected (count: {recent_rollback_count})")
            
            is_safe = len(safety_issues) == 0
            
            self._log_action("validate_rollback_safety", "completed", {
                "is_safe": is_safe,
                "safety_issues": len(safety_issues),
                "issues": safety_issues
            })
            
            return is_safe, safety_issues
            
        except Exception as e:
            self._log_action("validate_rollback_safety", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False, [f"Safety validation failed: {str(e)}"]
    
    def create_rollback_plan(
        self,
        tunnel_name: str,
        reason: RollbackReason,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a rollback plan with available options
        
        Args:
            tunnel_name: Name of the tunnel
            reason: Reason for rollback
            description: Optional description
            
        Returns:
            Rollback plan dictionary
        """
        self._log_action("create_rollback_plan", "in_progress", {
            "tunnel_name": tunnel_name,
            "reason": reason.value
        })
        
        try:
            # Get available versions
            versions = self.version_manager.list_versions(tunnel_name=tunnel_name)
            current_version = self.version_manager.get_active_version(tunnel_name)
            
            # Filter out current version
            available_versions = [
                v for v in versions 
                if v.version_id != current_version
            ]
            
            # Create rollback options
            rollback_options = []
            for version in available_versions[:5]:  # Limit to 5 most recent
                is_safe, safety_issues = self.validate_rollback_safety(tunnel_name, version.version_id)
                
                rollback_options.append({
                    "version_id": version.version_id,
                    "timestamp": version.timestamp,
                    "description": version.description,
                    "is_safe": is_safe,
                    "safety_issues": safety_issues,
                    "status": version.status.value
                })
            
            plan = {
                "tunnel_name": tunnel_name,
                "current_version": current_version,
                "rollback_reason": reason.value,
                "description": description,
                "available_options": rollback_options,
                "recommended_option": rollback_options[0] if rollback_options else None,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("create_rollback_plan", "completed", {
                "tunnel_name": tunnel_name,
                "options_available": len(rollback_options),
                "has_recommendation": plan["recommended_option"] is not None
            })
            
            return plan
            
        except Exception as e:
            self._log_action("create_rollback_plan", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return {
                "tunnel_name": tunnel_name,
                "error": str(e),
                "available_options": [],
                "recommended_option": None
            }