#!/usr/bin/env python3
"""
Prometheus Configuration Management
==================================

Centralized configuration management for Prometheus monitoring integration
across the Beast Mode framework.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Configuration management for Prometheus monitoring
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class PrometheusConfigMode(Enum):
    """Prometheus configuration modes."""
    DISABLED = "disabled"
    BASIC = "basic"
    FULL = "full"
    CUSTOM = "custom"


@dataclass
class PrometheusConfig:
    """Prometheus configuration settings."""
    
    # Basic settings
    enabled: bool = True
    mode: PrometheusConfigMode = PrometheusConfigMode.BASIC
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Service discovery
    service_name: str = "beast-mode-service"
    namespace: str = "beast-mode"
    
    # Metrics collection
    collection_interval: float = 5.0
    retention_hours: int = 24
    
    # Module-specific settings
    enable_module_metrics: bool = True
    enable_system_metrics: bool = True
    enable_application_metrics: bool = True
    enable_performance_metrics: bool = True
    
    # Advanced settings
    enable_http_server: bool = True
    enable_auto_discovery: bool = True
    enable_health_checks: bool = True
    
    # Alerting
    enable_alerts: bool = True
    alert_threshold_cpu: float = 80.0
    alert_threshold_memory: float = 80.0
    alert_threshold_disk: float = 90.0
    
    # Logging
    log_level: str = "INFO"
    enable_debug_logs: bool = False


class PrometheusConfigManager:
    """Manages Prometheus configuration across the framework."""
    
    def __init__(self):
        self.logger = logging.getLogger('prometheus_config_manager')
        self._config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> PrometheusConfig:
        """Load configuration from environment variables and defaults."""
        return PrometheusConfig(
            # Basic settings
            enabled=self._get_bool_env('BEAST_MODE_PROMETHEUS_ENABLED', True),
            mode=PrometheusConfigMode(
                os.getenv('BEAST_MODE_PROMETHEUS_MODE', 'basic')
            ),
            port=int(os.getenv('BEAST_MODE_PROMETHEUS_PORT', '8000')),
            host=os.getenv('BEAST_MODE_PROMETHEUS_HOST', '0.0.0.0'),
            
            # Service discovery
            service_name=os.getenv('BEAST_MODE_SERVICE_NAME', 'beast-mode-service'),
            namespace=os.getenv('BEAST_MODE_NAMESPACE', 'beast-mode'),
            
            # Metrics collection
            collection_interval=float(os.getenv('BEAST_MODE_PROMETHEUS_INTERVAL', '5.0')),
            retention_hours=int(os.getenv('BEAST_MODE_PROMETHEUS_RETENTION', '24')),
            
            # Module-specific settings
            enable_module_metrics=self._get_bool_env('BEAST_MODE_MODULE_METRICS', True),
            enable_system_metrics=self._get_bool_env('BEAST_MODE_SYSTEM_METRICS', True),
            enable_application_metrics=self._get_bool_env('BEAST_MODE_APP_METRICS', True),
            enable_performance_metrics=self._get_bool_env('BEAST_MODE_PERF_METRICS', True),
            
            # Advanced settings
            enable_http_server=self._get_bool_env('BEAST_MODE_HTTP_SERVER', True),
            enable_auto_discovery=self._get_bool_env('BEAST_MODE_AUTO_DISCOVERY', True),
            enable_health_checks=self._get_bool_env('BEAST_MODE_HEALTH_CHECKS', True),
            
            # Alerting
            enable_alerts=self._get_bool_env('BEAST_MODE_ALERTS', True),
            alert_threshold_cpu=float(os.getenv('BEAST_MODE_CPU_THRESHOLD', '80.0')),
            alert_threshold_memory=float(os.getenv('BEAST_MODE_MEMORY_THRESHOLD', '80.0')),
            alert_threshold_disk=float(os.getenv('BEAST_MODE_DISK_THRESHOLD', '90.0')),
            
            # Logging
            log_level=os.getenv('BEAST_MODE_LOG_LEVEL', 'INFO'),
            enable_debug_logs=self._get_bool_env('BEAST_MODE_DEBUG_LOGS', False)
        )
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _validate_config(self):
        """Validate configuration settings."""
        if self._config.port < 1 or self._config.port > 65535:
            raise ValueError(f"Invalid port number: {self._config.port}")
        
        if self._config.collection_interval < 0.1:
            raise ValueError(f"Collection interval too small: {self._config.collection_interval}")
        
        if self._config.retention_hours < 1:
            raise ValueError(f"Retention hours too small: {self._config.retention_hours}")
        
        self.logger.info(f"Prometheus configuration loaded: {self._config.mode.value} mode")
    
    def get_config(self) -> PrometheusConfig:
        """Get current configuration."""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration settings."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                self.logger.info(f"Updated {key} to {value}")
            else:
                self.logger.warning(f"Unknown configuration key: {key}")
        
        self._validate_config()
    
    def is_enabled(self) -> bool:
        """Check if Prometheus monitoring is enabled."""
        return self._config.enabled
    
    def get_service_discovery_config(self) -> Dict[str, Any]:
        """Get service discovery configuration."""
        return {
            'service_name': self._config.service_name,
            'namespace': self._config.namespace,
            'port': self._config.port,
            'host': self._config.host
        }
    
    def get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics collection configuration."""
        return {
            'collection_interval': self._config.collection_interval,
            'retention_hours': self._config.retention_hours,
            'enable_module_metrics': self._config.enable_module_metrics,
            'enable_system_metrics': self._config.enable_system_metrics,
            'enable_application_metrics': self._config.enable_application_metrics,
            'enable_performance_metrics': self._config.enable_performance_metrics
        }
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alerting configuration."""
        return {
            'enabled': self._config.enable_alerts,
            'cpu_threshold': self._config.alert_threshold_cpu,
            'memory_threshold': self._config.alert_threshold_memory,
            'disk_threshold': self._config.alert_threshold_disk
        }
    
    def get_prometheus_scrape_config(self) -> Dict[str, Any]:
        """Get Prometheus scrape configuration for this service."""
        return {
            'job_name': f"{self._config.namespace}-{self._config.service_name}",
            'static_configs': [{
                'targets': [f"{self._config.host}:{self._config.port}"]
            }],
            'scrape_interval': f"{self._config.collection_interval}s",
            'metrics_path': '/metrics'
        }
    
    def get_docker_compose_config(self) -> Dict[str, Any]:
        """Get Docker Compose configuration for Prometheus integration."""
        return {
            'environment': {
                'BEAST_MODE_PROMETHEUS_ENABLED': str(self._config.enabled).lower(),
                'BEAST_MODE_PROMETHEUS_PORT': str(self._config.port),
                'BEAST_MODE_PROMETHEUS_HOST': self._config.host,
                'BEAST_MODE_SERVICE_NAME': self._config.service_name,
                'BEAST_MODE_NAMESPACE': self._config.namespace,
                'BEAST_MODE_PROMETHEUS_INTERVAL': str(self._config.collection_interval),
                'BEAST_MODE_LOG_LEVEL': self._config.log_level
            },
            'ports': [f"{self._config.port}:{self._config.port}"],
            'labels': {
                'prometheus.io/scrape': 'true',
                'prometheus.io/port': str(self._config.port),
                'prometheus.io/path': '/metrics'
            }
        }
    
    def export_config(self, format: str = 'json') -> str:
        """Export configuration in specified format."""
        if format == 'json':
            import json
            return json.dumps(self._config.__dict__, indent=2, default=str)
        elif format == 'yaml':
            import yaml
            return yaml.dump(self._config.__dict__, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global configuration instance
config_manager = PrometheusConfigManager()


def get_prometheus_config() -> PrometheusConfig:
    """Get the global Prometheus configuration."""
    return config_manager.get_config()


def update_prometheus_config(**kwargs) -> None:
    """Update the global Prometheus configuration."""
    config_manager.update_config(**kwargs)


def is_prometheus_enabled() -> bool:
    """Check if Prometheus monitoring is enabled."""
    return config_manager.is_enabled()
