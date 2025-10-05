#!/usr/bin/env python3
"""
Configuration Manager for DAG Orchestration
==========================================

Flexible configuration system with environment-specific templates,
dynamic updates, and comprehensive validation.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


class ConfigurationFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    PYTHON = "python"
    ENV = "env"


class ConfigurationScope(Enum):
    """Configuration scope levels."""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    PROJECT = "project"
    SESSION = "session"


@dataclass
class ConfigurationPolicy:
    """Policy for configuration validation and constraints."""
    name: str
    description: str
    validation_function: Callable[[Dict[str, Any]], bool]
    error_message: str
    severity: str = "error"  # error, warning, info
    scope: ConfigurationScope = ConfigurationScope.GLOBAL


@dataclass
class ConfigurationTemplate:
    """Template for environment-specific configurations."""
    name: str
    description: str
    environment: str
    base_config: Dict[str, Any]
    overrides: Dict[str, Any] = field(default_factory=dict)
    required_keys: List[str] = field(default_factory=list)
    optional_keys: List[str] = field(default_factory=list)


@dataclass
class ConfigurationValidationResult:
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    validation_time: datetime = field(default_factory=datetime.now)


class ConfigurationManager(ReflectiveModule):
    """
    Advanced configuration manager for DAG orchestration system.
    
    Features:
    - Environment-specific configuration templates
    - Dynamic configuration updates without restart
    - Comprehensive validation with policies
    - Multiple configuration formats (JSON, YAML, Python, ENV)
    - Configuration inheritance and overrides
    - Real-time configuration monitoring
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        super().__init__()
        self.module_id = "ConfigurationManager"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Configuration storage
        self._config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration state
        self._configurations: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, ConfigurationTemplate] = {}
        self._policies: Dict[str, ConfigurationPolicy] = {}
        self._watchers: Dict[str, threading.Thread] = {}
        self._config_lock = threading.RLock()
        
        # Configuration change callbacks
        self._change_callbacks: Dict[str, List[Callable]] = {}
        
        # Load default policies and templates
        self._initialize_default_policies()
        self._initialize_default_templates()
        
        # Load existing configurations
        self._load_configurations()
        
        self._logger.info(f"ConfigurationManager initialized with config directory: {self._config_dir}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ConfigurationManager",
            "version": "1.0.0",
            "description": "Advanced configuration manager for DAG orchestration",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "configuration": {
                "config_directory": str(self._config_dir),
                "loaded_configurations": list(self._configurations.keys()),
                "available_templates": list(self._templates.keys()),
                "active_policies": list(self._policies.keys()),
                "active_watchers": list(self._watchers.keys())
            },
            "statistics": {
                "total_configurations": len(self._configurations),
                "total_templates": len(self._templates),
                "total_policies": len(self._policies),
                "active_watchers": len(self._watchers)
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check configuration directory accessibility
            if not self._config_dir.exists() or not self._config_dir.is_dir():
                issues.append(f"Configuration directory not accessible: {self._config_dir}")
                health_score *= 0.5
            
            # Check configuration validity
            invalid_configs = []
            for config_name, config_data in self._configurations.items():
                validation_result = self.validate_configuration(config_name, config_data)
                if not validation_result.is_valid:
                    invalid_configs.append(config_name)
            
            if invalid_configs:
                issues.append(f"Invalid configurations: {', '.join(invalid_configs)}")
                health_score *= 0.7
            
            # Check watcher threads
            dead_watchers = []
            for watcher_name, watcher_thread in self._watchers.items():
                if not watcher_thread.is_alive():
                    dead_watchers.append(watcher_name)
            
            if dead_watchers:
                issues.append(f"Dead configuration watchers: {', '.join(dead_watchers)}")
                health_score *= 0.8
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, use default configurations only
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING
            ]
            
            # Stop all watchers
            self._stop_all_watchers()
            
            # Use only essential configurations
            essential_configs = {}
            for config_name, config_data in self._configurations.items():
                if config_name in ['default', 'production', 'development']:
                    essential_configs[config_name] = config_data
            
            self._configurations = essential_configs
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def _initialize_default_policies(self) -> None:
        """Initialize default configuration validation policies."""
        
        # LLM Selection Policy Validation
        def validate_llm_selection_policy(config: Dict[str, Any]) -> bool:
            llm_config = config.get('llm_selection', {})
            policy = llm_config.get('policy')
            return policy in ['cost_first', 'capability_first', 'balanced']
        
        self.add_policy(ConfigurationPolicy(
            name="llm_selection_policy",
            description="Validate LLM selection policy is one of supported types",
            validation_function=validate_llm_selection_policy,
            error_message="LLM selection policy must be 'cost_first', 'capability_first', or 'balanced'"
        ))
        
        # Concurrency Limits Validation
        def validate_concurrency_limits(config: Dict[str, Any]) -> bool:
            execution_config = config.get('execution', {})
            max_workers = execution_config.get('max_workers', 10)
            return isinstance(max_workers, int) and 1 <= max_workers <= 100
        
        self.add_policy(ConfigurationPolicy(
            name="concurrency_limits",
            description="Validate concurrency limits are within reasonable bounds",
            validation_function=validate_concurrency_limits,
            error_message="max_workers must be an integer between 1 and 100"
        ))
        
        # Resource Thresholds Validation
        def validate_resource_thresholds(config: Dict[str, Any]) -> bool:
            resource_config = config.get('resources', {})
            cpu_threshold = resource_config.get('cpu_threshold', 0.8)
            memory_threshold = resource_config.get('memory_threshold', 0.8)
            return (0.0 < cpu_threshold <= 1.0 and 0.0 < memory_threshold <= 1.0)
        
        self.add_policy(ConfigurationPolicy(
            name="resource_thresholds",
            description="Validate resource thresholds are within valid ranges",
            validation_function=validate_resource_thresholds,
            error_message="Resource thresholds must be between 0.0 and 1.0"
        ))
        
        # Monitoring Configuration Validation
        def validate_monitoring_config(config: Dict[str, Any]) -> bool:
            monitoring_config = config.get('monitoring', {})
            metrics_interval = monitoring_config.get('metrics_collection_interval', 30)
            return isinstance(metrics_interval, (int, float)) and metrics_interval > 0
        
        self.add_policy(ConfigurationPolicy(
            name="monitoring_config",
            description="Validate monitoring configuration parameters",
            validation_function=validate_monitoring_config,
            error_message="Metrics collection interval must be a positive number"
        ))
    
    def _initialize_default_templates(self) -> None:
        """Initialize default environment-specific configuration templates."""
        
        # Development Template
        dev_template = ConfigurationTemplate(
            name="development",
            description="Development environment configuration",
            environment="development",
            base_config={
                "execution": {
                    "strategy": "conservative",
                    "max_workers": 4,
                    "timeout_seconds": 300
                },
                "llm_selection": {
                    "policy": "cost_first",
                    "budget_limit": 10.0,
                    "fallback_enabled": True
                },
                "resources": {
                    "cpu_threshold": 0.7,
                    "memory_threshold": 0.7,
                    "disk_threshold": 0.8
                },
                "monitoring": {
                    "metrics_collection_interval": 60,
                    "detailed_logging": True,
                    "performance_tracking": True
                }
            },
            required_keys=["execution", "llm_selection", "resources", "monitoring"]
        )
        self.add_template(dev_template)
        
        # Production Template
        prod_template = ConfigurationTemplate(
            name="production",
            description="Production environment configuration",
            environment="production",
            base_config={
                "execution": {
                    "strategy": "aggressive",
                    "max_workers": 20,
                    "timeout_seconds": 600
                },
                "llm_selection": {
                    "policy": "balanced",
                    "budget_limit": 100.0,
                    "fallback_enabled": True
                },
                "resources": {
                    "cpu_threshold": 0.8,
                    "memory_threshold": 0.8,
                    "disk_threshold": 0.9
                },
                "monitoring": {
                    "metrics_collection_interval": 30,
                    "detailed_logging": False,
                    "performance_tracking": True,
                    "alerting_enabled": True
                }
            },
            required_keys=["execution", "llm_selection", "resources", "monitoring"]
        )
        self.add_template(prod_template)
        
        # Testing Template
        test_template = ConfigurationTemplate(
            name="testing",
            description="Testing environment configuration",
            environment="testing",
            base_config={
                "execution": {
                    "strategy": "sequential",
                    "max_workers": 2,
                    "timeout_seconds": 120
                },
                "llm_selection": {
                    "policy": "cost_first",
                    "budget_limit": 5.0,
                    "fallback_enabled": True,
                    "simulation_mode": True
                },
                "resources": {
                    "cpu_threshold": 0.6,
                    "memory_threshold": 0.6,
                    "disk_threshold": 0.7
                },
                "monitoring": {
                    "metrics_collection_interval": 120,
                    "detailed_logging": True,
                    "performance_tracking": False
                }
            },
            required_keys=["execution", "llm_selection", "resources", "monitoring"]
        )
        self.add_template(test_template)
    
    def add_policy(self, policy: ConfigurationPolicy) -> None:
        """Add a configuration validation policy."""
        with self._config_lock:
            self._policies[policy.name] = policy
            self._logger.info(f"Added configuration policy: {policy.name}")
    
    def add_template(self, template: ConfigurationTemplate) -> None:
        """Add a configuration template."""
        with self._config_lock:
            self._templates[template.name] = template
            self._logger.info(f"Added configuration template: {template.name}")
    
    def create_configuration_from_template(self, template_name: str, 
                                         overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a configuration from a template with optional overrides."""
        if template_name not in self._templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self._templates[template_name]
        config = template.base_config.copy()
        
        # Apply template overrides
        if template.overrides:
            config = self._deep_merge(config, template.overrides)
        
        # Apply user overrides
        if overrides:
            config = self._deep_merge(config, overrides)
        
        return config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def load_configuration(self, name: str, file_path: Optional[str] = None, 
                         format_type: Optional[ConfigurationFormat] = None) -> Dict[str, Any]:
        """Load configuration from file or create from template."""
        with self.trace_operation("load_configuration", name=name, file_path=file_path) as trace:
            
            if file_path:
                # Load from file
                config_path = Path(file_path)
                if not config_path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {file_path}")
                
                # Determine format
                if format_type is None:
                    format_type = self._detect_format(config_path)
                
                config_data = self._load_from_file(config_path, format_type)
                
            else:
                # Create from template
                if name in self._templates:
                    config_data = self.create_configuration_from_template(name)
                else:
                    raise ValueError(f"No template or file path provided for configuration '{name}'")
            
            # Validate configuration
            validation_result = self.validate_configuration(name, config_data)
            if not validation_result.is_valid:
                raise ValueError(f"Configuration validation failed: {validation_result.errors}")
            
            # Store configuration
            with self._config_lock:
                self._configurations[name] = config_data
            
            # Start file watcher if loading from file
            if file_path:
                self._start_file_watcher(name, file_path)
            
            trace.output_result = {
                'configuration_name': name,
                'configuration_keys': list(config_data.keys()),
                'validation_passed': validation_result.is_valid
            }
            
            self._logger.info(f"Loaded configuration '{name}' successfully")
            return config_data
    
    def save_configuration(self, name: str, file_path: str, 
                         format_type: ConfigurationFormat = ConfigurationFormat.YAML) -> None:
        """Save configuration to file."""
        if name not in self._configurations:
            raise ValueError(f"Configuration '{name}' not found")
        
        config_data = self._configurations[name]
        config_path = Path(file_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._save_to_file(config_data, config_path, format_type)
        self._logger.info(f"Saved configuration '{name}' to {file_path}")
    
    def update_configuration(self, name: str, updates: Dict[str, Any], 
                           validate: bool = True) -> None:
        """Update configuration dynamically without restart."""
        with self.trace_operation("update_configuration", name=name, updates=updates) as trace:
            
            if name not in self._configurations:
                raise ValueError(f"Configuration '{name}' not found")
            
            with self._config_lock:
                # Create updated configuration
                updated_config = self._deep_merge(self._configurations[name], updates)
                
                # Validate if requested
                if validate:
                    validation_result = self.validate_configuration(name, updated_config)
                    if not validation_result.is_valid:
                        raise ValueError(f"Configuration update validation failed: {validation_result.errors}")
                
                # Apply update
                old_config = self._configurations[name].copy()
                self._configurations[name] = updated_config
                
                # Notify change callbacks
                self._notify_configuration_change(name, old_config, updated_config)
                
                trace.output_result = {
                    'configuration_name': name,
                    'updated_keys': list(updates.keys()),
                    'validation_passed': validation_result.is_valid if validate else True
                }
                
                self._logger.info(f"Updated configuration '{name}' successfully")
    
    def get_configuration(self, name: str) -> Dict[str, Any]:
        """Get configuration by name."""
        if name not in self._configurations:
            raise ValueError(f"Configuration '{name}' not found")
        
        return self._configurations[name].copy()
    
    def validate_configuration(self, name: str, config_data: Dict[str, Any]) -> ConfigurationValidationResult:
        """Validate configuration against all applicable policies."""
        result = ConfigurationValidationResult(is_valid=True)
        
        for policy_name, policy in self._policies.items():
            try:
                if not policy.validation_function(config_data):
                    result.is_valid = False
                    if policy.severity == "error":
                        result.errors.append(f"{policy_name}: {policy.error_message}")
                    elif policy.severity == "warning":
                        result.warnings.append(f"{policy_name}: {policy.error_message}")
                    else:
                        result.info.append(f"{policy_name}: {policy.error_message}")
            except Exception as e:
                result.is_valid = False
                result.errors.append(f"{policy_name}: Validation failed - {str(e)}")
        
        return result
    
    def register_change_callback(self, config_name: str, callback: Callable[[str, Dict[str, Any], Dict[str, Any]], None]) -> None:
        """Register callback for configuration changes."""
        if config_name not in self._change_callbacks:
            self._change_callbacks[config_name] = []
        
        self._change_callbacks[config_name].append(callback)
        self._logger.info(f"Registered change callback for configuration '{config_name}'")
    
    def _notify_configuration_change(self, name: str, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> None:
        """Notify all registered callbacks of configuration change."""
        if name in self._change_callbacks:
            for callback in self._change_callbacks[name]:
                try:
                    callback(name, old_config, new_config)
                except Exception as e:
                    self._logger.error(f"Configuration change callback failed: {e}")
    
    def _detect_format(self, file_path: Path) -> ConfigurationFormat:
        """Detect configuration file format from extension."""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.json']:
            return ConfigurationFormat.JSON
        elif suffix in ['.yaml', '.yml']:
            return ConfigurationFormat.YAML
        elif suffix in ['.py']:
            return ConfigurationFormat.PYTHON
        elif suffix in ['.env']:
            return ConfigurationFormat.ENV
        else:
            # Default to YAML
            return ConfigurationFormat.YAML
    
    def _load_from_file(self, file_path: Path, format_type: ConfigurationFormat) -> Dict[str, Any]:
        """Load configuration from file based on format."""
        with open(file_path, 'r') as f:
            if format_type == ConfigurationFormat.JSON:
                return json.load(f)
            elif format_type == ConfigurationFormat.YAML:
                return yaml.safe_load(f) or {}
            elif format_type == ConfigurationFormat.PYTHON:
                # Execute Python file and extract config variables
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Extract configuration variables
                config = {}
                for attr_name in dir(module):
                    if not attr_name.startswith('_'):
                        config[attr_name] = getattr(module, attr_name)
                
                return config
            elif format_type == ConfigurationFormat.ENV:
                # Parse environment file
                config = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
                
                return config
            else:
                raise ValueError(f"Unsupported configuration format: {format_type}")
    
    def _save_to_file(self, config_data: Dict[str, Any], file_path: Path, format_type: ConfigurationFormat) -> None:
        """Save configuration to file based on format."""
        with open(file_path, 'w') as f:
            if format_type == ConfigurationFormat.JSON:
                json.dump(config_data, f, indent=2, default=str)
            elif format_type == ConfigurationFormat.YAML:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:
                raise ValueError(f"Saving not supported for format: {format_type}")
    
    def _start_file_watcher(self, config_name: str, file_path: str) -> None:
        """Start file watcher for configuration file."""
        def watch_file():
            import time
            last_modified = os.path.getmtime(file_path)
            
            while config_name in self._watchers:
                try:
                    current_modified = os.path.getmtime(file_path)
                    if current_modified > last_modified:
                        # File was modified, reload configuration
                        self._logger.info(f"Configuration file changed, reloading: {file_path}")
                        
                        try:
                            format_type = self._detect_format(Path(file_path))
                            new_config = self._load_from_file(Path(file_path), format_type)
                            
                            # Validate new configuration
                            validation_result = self.validate_configuration(config_name, new_config)
                            if validation_result.is_valid:
                                old_config = self._configurations[config_name].copy()
                                self._configurations[config_name] = new_config
                                self._notify_configuration_change(config_name, old_config, new_config)
                                self._logger.info(f"Configuration '{config_name}' reloaded successfully")
                            else:
                                self._logger.error(f"Configuration reload failed validation: {validation_result.errors}")
                        
                        except Exception as e:
                            self._logger.error(f"Failed to reload configuration: {e}")
                        
                        last_modified = current_modified
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    self._logger.error(f"File watcher error: {e}")
                    time.sleep(5)  # Wait longer on error
        
        if config_name not in self._watchers:
            watcher_thread = threading.Thread(target=watch_file, daemon=True)
            watcher_thread.start()
            self._watchers[config_name] = watcher_thread
            self._logger.info(f"Started file watcher for configuration '{config_name}'")
    
    def _stop_all_watchers(self) -> None:
        """Stop all file watchers."""
        watchers_to_stop = list(self._watchers.keys())
        for config_name in watchers_to_stop:
            del self._watchers[config_name]
        
        self._logger.info("Stopped all configuration file watchers")
    
    def _load_configurations(self) -> None:
        """Load all configurations from config directory."""
        if not self._config_dir.exists():
            return
        
        for config_file in self._config_dir.glob("*.yaml"):
            try:
                config_name = config_file.stem
                self.load_configuration(config_name, str(config_file))
            except Exception as e:
                self._logger.warning(f"Failed to load configuration {config_file}: {e}")
        
        for config_file in self._config_dir.glob("*.json"):
            try:
                config_name = config_file.stem
                if config_name not in self._configurations:  # Don't override YAML
                    self.load_configuration(config_name, str(config_file))
            except Exception as e:
                self._logger.warning(f"Failed to load configuration {config_file}: {e}")
    
    def list_configurations(self) -> List[str]:
        """List all loaded configuration names."""
        return list(self._configurations.keys())
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self._templates.keys())
    
    def list_policies(self) -> List[str]:
        """List all registered policy names."""
        return list(self._policies.keys())
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of all configurations and their status."""
        summary = {
            'total_configurations': len(self._configurations),
            'total_templates': len(self._templates),
            'total_policies': len(self._policies),
            'active_watchers': len(self._watchers),
            'configurations': {},
            'templates': {},
            'policies': {}
        }
        
        # Configuration summaries
        for name, config in self._configurations.items():
            validation_result = self.validate_configuration(name, config)
            summary['configurations'][name] = {
                'keys': list(config.keys()),
                'is_valid': validation_result.is_valid,
                'errors': len(validation_result.errors),
                'warnings': len(validation_result.warnings)
            }
        
        # Template summaries
        for name, template in self._templates.items():
            summary['templates'][name] = {
                'environment': template.environment,
                'description': template.description,
                'required_keys': template.required_keys,
                'optional_keys': template.optional_keys
            }
        
        # Policy summaries
        for name, policy in self._policies.items():
            summary['policies'][name] = {
                'description': policy.description,
                'severity': policy.severity,
                'scope': policy.scope.value
            }
        
        return summary


# Convenience functions
def create_configuration_manager(config_dir: Optional[str] = None) -> ConfigurationManager:
    """Factory function to create configuration manager."""
    return ConfigurationManager(config_dir=config_dir)


def load_environment_configuration(environment: str, config_dir: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration for specific environment."""
    manager = create_configuration_manager(config_dir)
    
    # Try to load from file first
    config_file = Path(config_dir or "config") / f"{environment}.yaml"
    if config_file.exists():
        return manager.load_configuration(environment, str(config_file))
    
    # Fall back to template
    return manager.create_configuration_from_template(environment)