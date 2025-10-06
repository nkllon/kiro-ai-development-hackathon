"""
Configuration management for the Deployment Data Governance Auditor.

This module provides flexible configuration loading, validation, and hot-reloading
capabilities with environment variable substitution and schema validation.
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .models import ConfigurationSchema, Severity, ViolationType


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class PatternConfig:
    """Configuration for a violation pattern."""
    patterns: List[str]
    severity: str
    description: Optional[str] = None
    enabled: bool = True


@dataclass
class MonitoringConfig:
    """Configuration for file system monitoring."""
    watch_paths: List[str] = field(default_factory=lambda: ["deployment/"])
    excluded_paths: List[str] = field(default_factory=list)
    scan_interval: int = 60
    recursive: bool = True
    max_depth: Optional[int] = None


@dataclass
class RemediationConfig:
    """Configuration for automated remediation."""
    auto_gitignore: bool = True
    auto_quarantine: bool = True
    git_integration: bool = True
    quarantine_directory: str = ".deployment-auditor-quarantine"
    backup_before_remediation: bool = True


@dataclass
class NotificationConfig:
    """Configuration for notifications."""
    enabled: bool = True
    channels: List[str] = field(default_factory=list)
    severity_threshold: str = "MEDIUM"
    rate_limit_minutes: int = 5


@dataclass
class PrometheusConfig:
    """Configuration for Prometheus metrics."""
    enabled: bool = True
    port: int = 9090
    metrics_prefix: str = "deployment_auditor_"
    endpoint: str = "/metrics"


class ConfigManager(ReflectiveModule):
    """
    Manages configuration loading, validation, and hot-reloading.
    
    Provides comprehensive configuration management with environment variable
    substitution, schema validation, and automatic reloading capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager."""
        super().__init__()
        
        self.config_path = config_path or self._find_config_file()
        self.config_data: Dict[str, Any] = {}
        self.last_modified: Optional[float] = None
        self.validation_errors: List[str] = []
        
        # Default configuration patterns
        self.default_patterns = {
            "database_files": PatternConfig(
                patterns=["*.db", "*.sqlite*", "*.sql", "*.dump"],
                severity="CRITICAL",
                description="Database files and dumps"
            ),
            "time_series_data": PatternConfig(
                patterns=["*prometheus-data*", "*grafana-data*", "*influxdb-data*", "*tsdb*"],
                severity="HIGH",
                description="Time-series monitoring data"
            ),
            "log_files": PatternConfig(
                patterns=["*.log", "logs/", "log/", "*.log.*"],
                severity="MEDIUM",
                description="Application and system logs"
            ),
            "cache_files": PatternConfig(
                patterns=["cache/", "tmp/", "temp/", "*.cache", "*.tmp"],
                severity="LOW",
                description="Cache and temporary files"
            ),
            "runtime_state": PatternConfig(
                patterns=["*.pid", "*.sock", "*.lock", "run/", "var/"],
                severity="MEDIUM",
                description="Runtime state and process files"
            ),
            "binary_executables": PatternConfig(
                patterns=["*.exe", "*.bin", "*.so", "*.dll", "*.dylib"],
                severity="HIGH",
                description="Binary executables and libraries"
            ),
            "plugin_data": PatternConfig(
                patterns=["plugins/", "extensions/", "node_modules/", "vendor/"],
                severity="MEDIUM",
                description="Plugin and dependency data"
            )
        }
        
        self.logger.info("ConfigManager initialized", extra={
            "config_path": self.config_path,
            "component": "config_manager"
        })
    
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        possible_paths = [
            "deployment-auditor-config.yml",
            "deployment-auditor-config.yaml",
            ".deployment-auditor.yml",
            ".deployment-auditor.yaml",
            os.path.expanduser("~/.deployment-auditor.yml"),
            "/etc/deployment-auditor/config.yml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "deployment-auditor-config.yml"
    
    def load_configuration(self, force_reload: bool = False) -> bool:
        """
        Load configuration from file with validation.
        
        Args:
            force_reload: Force reload even if file hasn't changed
            
        Returns:
            bool: True if configuration loaded successfully
        """
        try:
            # Check if file exists
            if not os.path.exists(self.config_path):
                self.logger.info("Configuration file not found, using defaults", extra={
                    "config_path": self.config_path,
                    "component": "config_manager"
                })
                self._load_default_configuration()
                return True
            
            # Check if file has been modified
            current_modified = os.path.getmtime(self.config_path)
            if not force_reload and self.last_modified == current_modified:
                return True  # No changes, skip reload
            
            # Load YAML configuration
            with open(self.config_path, 'r') as f:
                raw_config = yaml.safe_load(f) or {}
            
            # Substitute environment variables
            processed_config = self._substitute_environment_variables(raw_config)
            
            # Validate configuration
            if not self._validate_configuration(processed_config):
                return False
            
            # Store configuration
            self.config_data = processed_config
            self.last_modified = current_modified
            
            self.logger.info("Configuration loaded successfully", extra={
                "config_path": self.config_path,
                "sections": list(self.config_data.keys()),
                "component": "config_manager"
            })
            
            return True
            
        except yaml.YAMLError as e:
            self.logger.error("YAML parsing error", extra={
                "config_path": self.config_path,
                "error": str(e),
                "component": "config_manager"
            })
            return False
        except Exception as e:
            self.logger.error("Configuration loading failed", extra={
                "config_path": self.config_path,
                "error": str(e),
                "component": "config_manager"
            })
            return False
    
    def _load_default_configuration(self):
        """Load default configuration when no file is found."""
        self.config_data = {
            "monitoring": asdict(MonitoringConfig()),
            "patterns": {name: asdict(config) for name, config in self.default_patterns.items()},
            "remediation": asdict(RemediationConfig()),
            "notifications": asdict(NotificationConfig()),
            "prometheus": asdict(PrometheusConfig())
        }
    
    def _substitute_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively substitute environment variables in configuration.
        
        Supports ${VAR_NAME} and ${VAR_NAME:-default_value} syntax.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict with environment variables substituted
        """
        if isinstance(config, dict):
            return {key: self._substitute_environment_variables(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._substitute_environment_variables(item) for item in config]
        elif isinstance(config, str):
            return self._substitute_env_vars_in_string(config)
        else:
            return config
    
    def _substitute_env_vars_in_string(self, text: str) -> str:
        """Substitute environment variables in a string."""
        # Pattern for ${VAR_NAME} or ${VAR_NAME:-default}
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_expr = match.group(1)
            
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
                return os.getenv(var_name.strip(), default_value.strip())
            else:
                var_name = var_expr.strip()
                value = os.getenv(var_name)
                if value is None:
                    self.logger.warning("Environment variable not found", extra={
                        "variable": var_name,
                        "component": "config_manager"
                    })
                    return match.group(0)  # Return original if not found
                return value
        
        return re.sub(pattern, replace_var, text)
    
    def _validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure and values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
        """
        self.validation_errors = []
        
        try:
            # Validate monitoring section
            if "monitoring" in config:
                self._validate_monitoring_config(config["monitoring"])
            
            # Validate patterns section
            if "patterns" in config:
                self._validate_patterns_config(config["patterns"])
            
            # Validate remediation section
            if "remediation" in config:
                self._validate_remediation_config(config["remediation"])
            
            # Validate notifications section
            if "notifications" in config:
                self._validate_notifications_config(config["notifications"])
            
            # Validate prometheus section
            if "prometheus" in config:
                self._validate_prometheus_config(config["prometheus"])
            
            if self.validation_errors:
                self.logger.error("Configuration validation failed", extra={
                    "errors": self.validation_errors,
                    "component": "config_manager"
                })
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("Configuration validation error", extra={
                "error": str(e),
                "component": "config_manager"
            })
            return False
    
    def _validate_monitoring_config(self, monitoring: Dict[str, Any]):
        """Validate monitoring configuration section."""
        if "watch_paths" in monitoring:
            if not isinstance(monitoring["watch_paths"], list):
                self.validation_errors.append("monitoring.watch_paths must be a list")
            elif not monitoring["watch_paths"]:
                self.validation_errors.append("monitoring.watch_paths cannot be empty")
        
        if "scan_interval" in monitoring:
            if not isinstance(monitoring["scan_interval"], int) or monitoring["scan_interval"] < 1:
                self.validation_errors.append("monitoring.scan_interval must be a positive integer")
    
    def _validate_patterns_config(self, patterns: Dict[str, Any]):
        """Validate patterns configuration section."""
        valid_severities = {s.value for s in Severity}
        
        for pattern_name, pattern_config in patterns.items():
            if not isinstance(pattern_config, dict):
                self.validation_errors.append(f"patterns.{pattern_name} must be a dictionary")
                continue
            
            if "patterns" not in pattern_config:
                self.validation_errors.append(f"patterns.{pattern_name}.patterns is required")
            elif not isinstance(pattern_config["patterns"], list):
                self.validation_errors.append(f"patterns.{pattern_name}.patterns must be a list")
            
            if "severity" in pattern_config:
                severity = pattern_config["severity"].upper()
                if severity not in valid_severities:
                    self.validation_errors.append(
                        f"patterns.{pattern_name}.severity must be one of: {', '.join(valid_severities)}"
                    )
    
    def _validate_remediation_config(self, remediation: Dict[str, Any]):
        """Validate remediation configuration section."""
        boolean_fields = ["auto_gitignore", "auto_quarantine", "git_integration", "backup_before_remediation"]
        
        for field in boolean_fields:
            if field in remediation and not isinstance(remediation[field], bool):
                self.validation_errors.append(f"remediation.{field} must be a boolean")
    
    def _validate_notifications_config(self, notifications: Dict[str, Any]):
        """Validate notifications configuration section."""
        if "severity_threshold" in notifications:
            valid_severities = {s.value for s in Severity}
            threshold = notifications["severity_threshold"].upper()
            if threshold not in valid_severities:
                self.validation_errors.append(
                    f"notifications.severity_threshold must be one of: {', '.join(valid_severities)}"
                )
    
    def _validate_prometheus_config(self, prometheus: Dict[str, Any]):
        """Validate prometheus configuration section."""
        if "port" in prometheus:
            port = prometheus["port"]
            if not isinstance(port, int) or port < 1 or port > 65535:
                self.validation_errors.append("prometheus.port must be a valid port number (1-65535)")
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration with defaults."""
        monitoring_data = self.config_data.get("monitoring", {})
        return MonitoringConfig(
            watch_paths=monitoring_data.get("watch_paths", ["deployment/"]),
            excluded_paths=monitoring_data.get("excluded_paths", []),
            scan_interval=monitoring_data.get("scan_interval", 60),
            recursive=monitoring_data.get("recursive", True),
            max_depth=monitoring_data.get("max_depth")
        )
    
    def get_pattern_configs(self) -> Dict[str, PatternConfig]:
        """Get pattern configurations with defaults."""
        patterns_data = self.config_data.get("patterns", {})
        result = {}
        
        # Start with defaults
        for name, default_config in self.default_patterns.items():
            result[name] = default_config
        
        # Override with user configuration
        for name, pattern_data in patterns_data.items():
            if isinstance(pattern_data, dict):
                result[name] = PatternConfig(
                    patterns=pattern_data.get("patterns", []),
                    severity=pattern_data.get("severity", "MEDIUM"),
                    description=pattern_data.get("description"),
                    enabled=pattern_data.get("enabled", True)
                )
        
        return result
    
    def get_remediation_config(self) -> RemediationConfig:
        """Get remediation configuration with defaults."""
        remediation_data = self.config_data.get("remediation", {})
        return RemediationConfig(
            auto_gitignore=remediation_data.get("auto_gitignore", True),
            auto_quarantine=remediation_data.get("auto_quarantine", True),
            git_integration=remediation_data.get("git_integration", True),
            quarantine_directory=remediation_data.get("quarantine_directory", ".deployment-auditor-quarantine"),
            backup_before_remediation=remediation_data.get("backup_before_remediation", True)
        )
    
    def get_notification_config(self) -> NotificationConfig:
        """Get notification configuration with defaults."""
        notifications_data = self.config_data.get("notifications", {})
        return NotificationConfig(
            enabled=notifications_data.get("enabled", True),
            channels=notifications_data.get("channels", []),
            severity_threshold=notifications_data.get("severity_threshold", "MEDIUM"),
            rate_limit_minutes=notifications_data.get("rate_limit_minutes", 5)
        )
    
    def get_prometheus_config(self) -> PrometheusConfig:
        """Get prometheus configuration with defaults."""
        prometheus_data = self.config_data.get("prometheus", {})
        return PrometheusConfig(
            enabled=prometheus_data.get("enabled", True),
            port=prometheus_data.get("port", 9090),
            metrics_prefix=prometheus_data.get("metrics_prefix", "deployment_auditor_"),
            endpoint=prometheus_data.get("endpoint", "/metrics")
        )
    
    def reload_if_changed(self) -> bool:
        """Reload configuration if file has changed."""
        return self.load_configuration(force_reload=False)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Beast Mode integration."""
        return {
            "status": "healthy" if not self.validation_errors else "degraded",
            "config_path": self.config_path,
            "config_exists": os.path.exists(self.config_path),
            "last_modified": self.last_modified,
            "validation_errors": self.validation_errors,
            "sections_loaded": list(self.config_data.keys()) if self.config_data else []
        }