"""
Base classes for the Domain Index System

This module provides abstract base classes with common functionality
that concrete implementations can inherit from. These classes provide
logging, error handling, and other shared capabilities.
"""

import logging
import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..core.reflective_module import ReflectiveModule, HealthStatus as RMHealthStatus
from .models import HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory


class DomainSystemComponent(ReflectiveModule, ABC):
    """
    Base class for all domain system components
    
    Provides common functionality including:
    - Logging and error handling
    - Health monitoring integration
    - Performance tracking
    - Configuration management
    """
    
    def __init__(self, component_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(component_name)
        
        self.config = config or {}
        self.logger = logging.getLogger(f"domain_index.{component_name}")
        self.performance_metrics = {}
        self.error_count = 0
        self.last_error = None
        self.startup_time = datetime.now()
        
        # Component-specific configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)  # 5 minutes
        self.max_retries = self.config.get('max_retries', 3)
        self.timeout_seconds = self.config.get('timeout_seconds', 30)
        
        self.logger.info(f"Initialized {component_name} component")
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get component status for ReflectiveModule interface"""
        return {
            "module_name": self.module_name,
            "status": "healthy" if self.is_healthy() else "degraded",
            "uptime_seconds": (datetime.now() - self.startup_time).total_seconds(),
            "error_count": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None,
            "performance_metrics": self.performance_metrics,
            "cache_enabled": self.cache_enabled
        }
    
    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        # Component is unhealthy if too many recent errors
        return self.error_count < 10 and not self._degradation_active
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        return {
            "component_health": {
                "error_count": self.error_count,
                "last_error": str(self.last_error) if self.last_error else None,
                "uptime_seconds": (datetime.now() - self.startup_time).total_seconds(),
                "degradation_active": self._degradation_active
            },
            "performance_metrics": self.performance_metrics,
            "configuration": {
                "cache_enabled": self.cache_enabled,
                "cache_ttl": self.cache_ttl,
                "max_retries": self.max_retries,
                "timeout_seconds": self.timeout_seconds
            }
        }
    
    def _get_primary_responsibility(self) -> str:
        """Get primary responsibility for ReflectiveModule"""
        return f"domain_index_{self.module_name}"
    
    def _handle_error(self, error: Exception, operation: str) -> None:
        """Handle errors with logging and metrics"""
        self.error_count += 1
        self.last_error = error
        self.logger.error(f"Error in {operation}: {str(error)}", exc_info=True)
        
        # Trigger degradation if too many errors
        if self.error_count >= 5:
            self._update_health_indicator(
                self.module_name,
                RMHealthStatus.DEGRADED,
                "error_threshold_exceeded",
                f"Component has {self.error_count} errors"
            )
    
    def _track_performance(self, operation: str, duration_ms: float) -> None:
        """Track performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = {
                "count": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "min_time_ms": float('inf'),
                "max_time_ms": 0.0
            }
        
        metrics = self.performance_metrics[operation]
        metrics["count"] += 1
        metrics["total_time_ms"] += duration_ms
        metrics["avg_time_ms"] = metrics["total_time_ms"] / metrics["count"]
        metrics["min_time_ms"] = min(metrics["min_time_ms"], duration_ms)
        metrics["max_time_ms"] = max(metrics["max_time_ms"], duration_ms)
    
    def _time_operation(self, operation_name: str):
        """Context manager for timing operations"""
        return OperationTimer(self, operation_name)
    
    def _validate_config(self) -> List[str]:
        """Validate component configuration"""
        issues = []
        
        if self.cache_ttl <= 0:
            issues.append("cache_ttl_seconds must be positive")
        
        if self.max_retries < 0:
            issues.append("max_retries must be non-negative")
        
        if self.timeout_seconds <= 0:
            issues.append("timeout_seconds must be positive")
        
        return issues
    
    def _create_health_status(self, status_type: HealthStatusType, issues: List[HealthIssue]) -> HealthStatus:
        """Create a health status object"""
        # Calculate health metrics
        critical_issues = sum(1 for issue in issues if issue.severity == IssueSeverity.CRITICAL)
        warning_issues = sum(1 for issue in issues if issue.severity == IssueSeverity.WARNING)
        
        # Simple health scoring
        health_score = 1.0
        if critical_issues > 0:
            health_score -= 0.5 * critical_issues
        if warning_issues > 0:
            health_score -= 0.1 * warning_issues
        health_score = max(0.0, health_score)
        
        metrics = HealthMetrics(
            dependency_health_score=health_score,
            pattern_coverage_score=health_score,
            file_accessibility_score=health_score,
            makefile_integration_score=health_score,
            overall_health_score=health_score
        )
        
        return HealthStatus(
            status=status_type,
            last_check=datetime.now(),
            issues=issues,
            metrics=metrics,
            check_duration_ms=0
        )


class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, component: DomainSystemComponent, operation_name: str):
        self.component = component
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.component._track_performance(self.operation_name, duration_ms)
            
            if exc_type:
                self.component._handle_error(exc_val, self.operation_name)


class ConfigurableComponent(DomainSystemComponent):
    """Base class for components that need file-based configuration"""
    
    def __init__(self, component_name: str, config_file: Optional[str] = None):
        # Load configuration from file if provided
        config = {}
        if config_file:
            config = self._load_config_file(config_file)
        
        super().__init__(component_name, config)
        self.config_file = config_file
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                import json
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Configuration file not found: {config_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {config_file}: {e}")
            return {}
    
    def reload_config(self) -> bool:
        """Reload configuration from file"""
        if not self.config_file:
            return False
        
        try:
            new_config = self._load_config_file(self.config_file)
            self.config.update(new_config)
            self._apply_config_changes()
            self.logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            self._handle_error(e, "reload_config")
            return False
    
    def _apply_config_changes(self) -> None:
        """Apply configuration changes to component"""
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)
        self.max_retries = self.config.get('max_retries', 3)
        self.timeout_seconds = self.config.get('timeout_seconds', 30)


class CachedComponent(DomainSystemComponent):
    """Base class for components that need caching capabilities"""
    
    def __init__(self, component_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(component_name, config)
        self._cache = {}
        self._cache_timestamps = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if not self.cache_enabled:
            return None
        
        if key not in self._cache:
            self.cache_misses += 1
            return None
        
        # Check if expired
        timestamp = self._cache_timestamps.get(key, datetime.min)
        if datetime.now() - timestamp > timedelta(seconds=self.cache_ttl):
            self._remove_from_cache(key)
            self.cache_misses += 1
            return None
        
        self.cache_hits += 1
        return self._cache[key]
    
    def _set_in_cache(self, key: str, value: Any) -> None:
        """Set value in cache"""
        if not self.cache_enabled:
            return
        
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def _remove_from_cache(self, key: str) -> None:
        """Remove value from cache"""
        self._cache.pop(key, None)
        self._cache_timestamps.pop(key, None)
    
    def _clear_cache(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._cache_timestamps.clear()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self._cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.cache_ttl
        }