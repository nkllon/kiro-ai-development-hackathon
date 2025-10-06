"""
Main Tunnel Configuration Manager

Orchestrates all tunnel configuration operations including generation,
validation, versioning, and rollback management.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .config_generator import TunnelConfigGenerator, TunnelConfig
from .websocket_ingress import WebSocketIngressManager, WebSocketConfig
from .config_validator import ConfigValidator, ValidationResult
from .version_manager import VersionManager, VersionStatus
from .rollback_manager import RollbackManager, RollbackReason

logger = logging.getLogger(__name__)


class TunnelConfigManager:
    """
    Main tunnel configuration manager that orchestrates all configuration operations.
    
    Provides a unified interface for:
    - Configuration generation with WebSocket support
    - Configuration validation
    - Version management and backup
    - Rollback operations
    """
    
    def __init__(self, config_path: str = "/tmp/tunnel_configs"):
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.config_generator = TunnelConfigGenerator(str(self.config_path))
        self.websocket_manager = WebSocketIngressManager()
        self.validator = ConfigValidator()
        self.version_manager = VersionManager(str(self.config_path / "versions"))
        self.rollback_manager = RollbackManager(self.version_manager, self.validator)
        
        # Log initialization
        self._log_action("init", "in_progress", {
            "config_path": str(self.config_path),
            "components_initialized": [
                "config_generator",
                "websocket_manager", 
                "validator",
                "version_manager",
                "rollback_manager"
            ]
        })
        
        logger.info("TunnelConfigManager initialized")
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
    
    def generate_websocket_config(
        self,
        tunnel_name: str,
        hostname: str,
        service_url: str,
        credentials_file: Optional[str] = None,
        websocket_config: Optional[WebSocketConfig] = None,
        save_to_file: bool = True
    ) -> Dict[str, Any]:
        """
        Generate WebSocket-enabled tunnel configuration
        
        Args:
            tunnel_name: Name of the tunnel
            hostname: Target hostname
            service_url: Service URL to proxy
            credentials_file: Path to credentials file
            websocket_config: WebSocket-specific configuration
            save_to_file: Whether to save configuration to file
            
        Returns:
            Generated configuration dictionary
        """
        self._log_action("generate_websocket_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "hostname": hostname,
            "service_url": service_url,
            "websocket_enabled": websocket_config.enabled if websocket_config else True
        })
        
        try:
            # Set default values
            if not credentials_file:
                credentials_file = f"/tmp/{tunnel_name}_credentials.json"
            
            if not websocket_config:
                websocket_config = WebSocketConfig()
            
            # Create tunnel config
            tunnel_config = TunnelConfig(
                tunnel_name=tunnel_name,
                credentials_file=credentials_file,
                hostname=hostname,
                service_url=service_url,
                websocket_enabled=websocket_config.enabled
            )
            
            # Generate configuration
            config = self.config_generator.generate_websocket_config(tunnel_config)
            
            # Save to file if requested
            if save_to_file:
                config_file = self.config_generator.generate_config_file(tunnel_config)
                self._log_action("generate_websocket_config", "completed", {
                    "config_file": config_file,
                    "websocket_support": websocket_config.enabled
                })
            else:
                self._log_action("generate_websocket_config", "completed", {
                    "websocket_support": websocket_config.enabled,
                    "saved_to_file": False
                })
            
            return config
            
        except Exception as e:
            self._log_action("generate_websocket_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate tunnel configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            ValidationResult with detailed validation information
        """
        self._log_action("validate_config", "in_progress", {
            "config_keys": list(config.keys()),
            "validation_type": "complete"
        })
        
        try:
            result = self.validator.validate_config(config)
            
            self._log_action("validate_config", "completed", {
                "is_valid": result.is_valid,
                "total_issues": len(result.issues),
                "warnings": len(result.warnings),
                "errors": len(result.errors),
                "critical_errors": len(result.critical_errors)
            })
            
            return result
            
        except Exception as e:
            self._log_action("validate_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def backup_current_config(
        self,
        config: Dict[str, Any],
        tunnel_name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Backup current configuration as a version
        
        Args:
            config: Configuration to backup
            tunnel_name: Name of the tunnel
            description: Optional description
            tags: Optional tags
            
        Returns:
            Version ID of the backup
        """
        self._log_action("backup_current_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "description": description,
            "tags": tags
        })
        
        try:
            # Validate configuration before backup
            validation_result = self.validate_config(config)
            if not validation_result.is_valid:
                self._log_action("backup_current_config", "error", {
                    "error": "Configuration validation failed",
                    "validation_summary": validation_result.summary
                })
                raise ValueError(f"Configuration validation failed: {validation_result.summary}")
            
            # Create version
            version_id = self.version_manager.create_version(
                config=config,
                tunnel_name=tunnel_name,
                description=description,
                tags=tags,
                created_by="tunnel_config_manager"
            )
            
            self._log_action("backup_current_config", "completed", {
                "version_id": version_id,
                "tunnel_name": tunnel_name,
                "validation_passed": True
            })
            
            return version_id
            
        except Exception as e:
            self._log_action("backup_current_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def apply_config(
        self,
        config: Dict[str, Any],
        tunnel_name: str,
        create_backup: bool = True,
        validate_before_apply: bool = True
    ) -> Tuple[bool, str]:
        """
        Apply configuration to tunnel
        
        Args:
            config: Configuration to apply
            tunnel_name: Name of the tunnel
            create_backup: Whether to create backup before applying
            validate_before_apply: Whether to validate before applying
            
        Returns:
            Tuple of (success, version_id or error message)
        """
        self._log_action("apply_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "create_backup": create_backup,
            "validate_before": validate_before_apply
        })
        
        try:
            # Validate configuration if requested
            if validate_before_apply:
                validation_result = self.validate_config(config)
                if not validation_result.is_valid:
                    error_msg = f"Configuration validation failed: {validation_result.summary}"
                    self._log_action("apply_config", "error", {
                        "error": error_msg,
                        "validation_issues": len(validation_result.issues)
                    })
                    return False, error_msg
            
            # Create backup if requested
            backup_version_id = None
            if create_backup:
                backup_version_id = self.backup_current_config(
                    config=config,
                    tunnel_name=tunnel_name,
                    description="Backup before applying new configuration"
                )
            
            # Set configuration as active
            version_id = self.version_manager.create_version(
                config=config,
                tunnel_name=tunnel_name,
                description="Applied configuration",
                created_by="tunnel_config_manager"
            )
            
            # Set as active version
            success = self.version_manager.set_active_version(version_id)
            
            if success:
                self._log_action("apply_config", "completed", {
                    "version_id": version_id,
                    "backup_version_id": backup_version_id,
                    "tunnel_name": tunnel_name
                })
                return True, version_id
            else:
                self._log_action("apply_config", "error", {
                    "error": "Failed to set version as active",
                    "version_id": version_id
                })
                return False, "Failed to set version as active"
            
        except Exception as e:
            self._log_action("apply_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False, str(e)
    
    def rollback_config(
        self,
        tunnel_name: str,
        target_version_id: Optional[str] = None,
        reason: RollbackReason = RollbackReason.MANUAL_REQUEST,
        description: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Rollback tunnel configuration
        
        Args:
            tunnel_name: Name of the tunnel
            target_version_id: Specific version to rollback to (None for latest stable)
            reason: Reason for rollback
            description: Optional description
            
        Returns:
            Tuple of (success, operation_id or error message)
        """
        self._log_action("rollback_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "target_version": target_version_id,
            "reason": reason.value
        })
        
        try:
            if target_version_id:
                # Rollback to specific version
                success, result = self.rollback_manager.rollback_to_version(
                    tunnel_name=tunnel_name,
                    target_version_id=target_version_id,
                    reason=reason,
                    description=description,
                    initiated_by="tunnel_config_manager"
                )
            else:
                # Rollback to latest stable
                success, result = self.rollback_manager.rollback_to_latest_stable(
                    tunnel_name=tunnel_name,
                    reason=reason,
                    description=description,
                    initiated_by="tunnel_config_manager"
                )
            
            if success:
                self._log_action("rollback_config", "completed", {
                    "operation_id": result,
                    "tunnel_name": tunnel_name,
                    "target_version": target_version_id
                })
            else:
                self._log_action("rollback_config", "error", {
                    "error": result,
                    "tunnel_name": tunnel_name
                })
            
            return success, result
            
        except Exception as e:
            self._log_action("rollback_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False, str(e)
    
    def get_active_config(self, tunnel_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current active configuration
        
        Args:
            tunnel_name: Name of the tunnel
            
        Returns:
            Active configuration or None
        """
        self._log_action("get_active_config", "in_progress", {
            "tunnel_name": tunnel_name
        })
        
        try:
            active_version_id = self.version_manager.get_active_version(tunnel_name)
            if not active_version_id:
                self._log_action("get_active_config", "completed", {
                    "active_config": None,
                    "message": "No active version found"
                })
                return None
            
            config = self.version_manager.get_version(active_version_id)
            
            self._log_action("get_active_config", "completed", {
                "active_version_id": active_version_id,
                "config_keys": list(config.keys()) if config else []
            })
            
            return config
            
        except Exception as e:
            self._log_action("get_active_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return None
    
    def list_config_versions(
        self,
        tunnel_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List configuration versions for a tunnel
        
        Args:
            tunnel_name: Name of the tunnel
            limit: Limit number of results
            
        Returns:
            List of version information
        """
        self._log_action("list_config_versions", "in_progress", {
            "tunnel_name": tunnel_name,
            "limit": limit
        })
        
        try:
            versions = self.version_manager.list_versions(
                tunnel_name=tunnel_name,
                limit=limit
            )
            
            version_info = []
            for version in versions:
                version_info.append({
                    "version_id": version.version_id,
                    "timestamp": version.timestamp,
                    "status": version.status.value,
                    "description": version.description,
                    "tags": version.tags,
                    "file_size": version.file_size,
                    "validation_status": version.validation_status
                })
            
            self._log_action("list_config_versions", "completed", {
                "tunnel_name": tunnel_name,
                "versions_found": len(version_info)
            })
            
            return version_info
            
        except Exception as e:
            self._log_action("list_config_versions", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return []
    
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
            history = self.rollback_manager.get_rollback_history(
                tunnel_name=tunnel_name,
                limit=limit
            )
            
            self._log_action("get_rollback_history", "completed", {
                "operations_found": len(history),
                "tunnel_name": tunnel_name
            })
            
            return history
            
        except Exception as e:
            self._log_action("get_rollback_history", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return []
    
    def create_rollback_plan(
        self,
        tunnel_name: str,
        reason: RollbackReason = RollbackReason.MANUAL_REQUEST,
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
            plan = self.rollback_manager.create_rollback_plan(
                tunnel_name=tunnel_name,
                reason=reason,
                description=description
            )
            
            self._log_action("create_rollback_plan", "completed", {
                "tunnel_name": tunnel_name,
                "options_available": len(plan.get("available_options", [])),
                "has_recommendation": plan.get("recommended_option") is not None
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
    
    def emergency_rollback(self, tunnel_name: str) -> Tuple[bool, str]:
        """
        Perform emergency rollback to last known good configuration
        
        Args:
            tunnel_name: Name of the tunnel
            
        Returns:
            Tuple of (success, operation_id or error message)
        """
        self._log_action("emergency_rollback", "in_progress", {
            "tunnel_name": tunnel_name,
            "emergency": True
        })
        
        try:
            success, result = self.rollback_manager.emergency_rollback(
                tunnel_name=tunnel_name,
                description="Emergency rollback initiated by TunnelConfigManager"
            )
            
            if success:
                self._log_action("emergency_rollback", "completed", {
                    "operation_id": result,
                    "tunnel_name": tunnel_name
                })
            else:
                self._log_action("emergency_rollback", "error", {
                    "error": result,
                    "tunnel_name": tunnel_name
                })
            
            return success, result
            
        except Exception as e:
            self._log_action("emergency_rollback", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False, str(e)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status
        
        Returns:
            System status dictionary
        """
        self._log_action("get_system_status", "in_progress", {})
        
        try:
            # Get version counts
            all_versions = self.version_manager.list_versions()
            active_versions = self.version_manager.list_versions(status=VersionStatus.ACTIVE)
            
            # Get rollback history
            recent_rollbacks = self.get_rollback_history(limit=5)
            
            status = {
                "system_ready": True,
                "components": {
                    "config_generator": True,
                    "websocket_manager": True,
                    "validator": True,
                    "version_manager": True,
                    "rollback_manager": True
                },
                "versions": {
                    "total": len(all_versions),
                    "active": len(active_versions)
                },
                "recent_rollbacks": len(recent_rollbacks),
                "config_path": str(self.config_path),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("get_system_status", "completed", {
                "system_ready": status["system_ready"],
                "total_versions": status["versions"]["total"],
                "active_versions": status["versions"]["active"]
            })
            
            return status
            
        except Exception as e:
            self._log_action("get_system_status", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return {
                "system_ready": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }