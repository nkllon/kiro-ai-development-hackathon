#!/usr/bin/env python3
"""
ReflectiveModule - Base interface for RM-DDD compliance

Provides the foundational ReflectiveModule interface that all modules must implement
for RM-DDD compliance. This enables systematic module introspection and health monitoring.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """Module status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ModuleCapability(Enum):
    """Module capability enumeration"""
    CORE_FUNCTIONALITY = "core_functionality"
    HEALTH_MONITORING = "health_monitoring"
    CONFIGURATION = "configuration"
    LOGGING = "logging"
    METRICS = "metrics"
    NOTIFICATIONS = "notifications"
    PERSISTENCE = "persistence"
    API_INTEGRATION = "api_integration"
    STRUCTURED_LOGGING = "structured_logging"
    PERFORMANCE_MONITORING = "performance_monitoring"
    ERROR_TRACKING = "error_tracking"
    LOG_EXPORT = "log_export"
    METRICS_COLLECTION = "metrics_collection"
    EXECUTION_TIMING = "execution_timing"
    RESOURCE_MONITORING = "resource_monitoring"
    DEBUGGING = "debugging"
    DIAGNOSTICS = "diagnostics"
    EXECUTION_TRACING = "execution_tracing"
    ISSUE_RESOLUTION = "issue_resolution"


@dataclass
class ModuleHealth:
    """Module health status information"""
    module_id: str
    status: ModuleStatus
    last_check: datetime
    health_score: float  # 0.0 to 1.0
    issues: List[str]
    capabilities: List[ModuleCapability]
    dependencies: List[str]
    metrics: Dict[str, Any]
    
    def is_healthy(self) -> bool:
        """Check if module is healthy"""
        return self.status == ModuleStatus.HEALTHY
    
    def has_issues(self) -> bool:
        """Check if module has issues"""
        return len(self.issues) > 0
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary"""
        return {
            'module_id': self.module_id,
            'status': self.status.value,
            'health_score': self.health_score,
            'issue_count': len(self.issues),
            'capability_count': len(self.capabilities),
            'dependency_count': len(self.dependencies),
            'last_check': self.last_check.isoformat()
        }


@dataclass
class ModuleConfiguration:
    """Module configuration information"""
    module_id: str
    config_version: str
    parameters: Dict[str, Any]
    required_parameters: List[str]
    optional_parameters: List[str]
    validation_rules: Dict[str, Any]
    last_updated: datetime
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        # Check required parameters
        for param in self.required_parameters:
            if param not in self.parameters:
                return False
        return True
    
    def get_missing_parameters(self) -> List[str]:
        """Get missing required parameters"""
        return [param for param in self.required_parameters if param not in self.parameters]


class ReflectiveModule(ABC):
    """
    Base ReflectiveModule interface for RM-DDD compliance
    
    All modules in the DevPost integration system must implement this interface
    to enable systematic introspection, health monitoring, and registry integration.
    """
    
    def __init__(self, module_id: str, version: str = "1.0.0"):
        """Initialize reflective module"""
        self.module_id = module_id
        self.version = version
        self.logger = logging.getLogger(f"reflective_module.{module_id}")
        self._health_history: List[ModuleHealth] = []
        self._max_health_history = 100
    
    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get comprehensive module information
        
        Returns:
            Dict containing module metadata, capabilities, and configuration
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """
        Get module capabilities
        
        Returns:
            List of capabilities this module provides
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Get module dependencies
        
        Returns:
            List of module IDs this module depends on
        """
        pass
    
    @abstractmethod
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check"""
        issues = []
        
        # Check basic module state
        if not hasattr(self, 'module_id'):
            issues.append('Missing module_id attribute')
        
        if not hasattr(self, 'version'):
            issues.append('Missing version attribute')
        
        # Check for common health indicators
        try:
            # Test basic functionality
            if hasattr(self, 'get_module_info'):
                info = self.get_module_info()
                if not isinstance(info, dict):
                    issues.append('get_module_info() does not return dict')
            
            if hasattr(self, 'get_capabilities'):
                caps = self.get_capabilities()
                if not isinstance(caps, list):
                    issues.append('get_capabilities() does not return list')
            
            if hasattr(self, 'get_dependencies'):
                deps = self.get_dependencies()
                if not isinstance(deps, list):
                    issues.append('get_dependencies() does not return list')
        except Exception as e:
            issues.append(f'Error during health check: {str(e)}')
        
        # Determine health status
        if not issues:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif len(issues) <= 2:
            status = ModuleStatus.DEGRADED
            health_score = 0.7
        else:
            status = ModuleStatus.UNHEALTHY
            health_score = 0.3
        
        return ModuleHealth(
            module_id="modulestatus",
            status=status,
            health_score=health_score,
            issues=issues,
            capabilities=self.get_capabilities() if hasattr(self, 'get_capabilities') else [],
            dependencies=self.get_dependencies() if hasattr(self, 'get_dependencies') else [],
            metrics=self.get_metrics() if hasattr(self, 'get_metrics') else {},
            last_check=datetime.now()
        )
    @abstractmethod
    def get_configuration(self) -> ModuleConfiguration:
        """
        Get module configuration
        
        Returns:
            ModuleConfiguration object with current settings
        """
        pass
    
    @abstractmethod
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """
        Update module configuration
        
        Args:
            config: New configuration to apply
            
        Returns:
            True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get module metrics
        
        Returns:
            Dict containing performance and operational metrics
        """
        pass
    
    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state"""
        pass
    
    def get_health_history(self) -> List[ModuleHealth]:
        """Get health check history"""
        return self._health_history.copy()
    
    def get_health_trend(self) -> Dict[str, Any]:
        """Get health trend analysis"""
        if len(self._health_history) < 2:
            return {'trend': 'insufficient_data', 'change': 0.0}
        
        recent_health = self._health_history[-1].health_score
        previous_health = self._health_history[-2].health_score
        change = recent_health - previous_health
        
        if change > 0.1:
            trend = 'improving'
        elif change < -0.1:
            trend = 'degrading'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change': change,
            'recent_score': recent_health,
            'previous_score': previous_health
        }
    
    def record_health_check(self, health: ModuleHealth) -> None:
        """Record health check in history"""
        self._health_history.append(health)
        if len(self._health_history) > self._max_health_history:
            self._health_history = self._health_history[-self._max_health_history:]
    
    def get_module_summary(self) -> Dict[str, Any]:
        """Get comprehensive module summary"""
        try:
            health = self.check_health()
            self.record_health_check(health)
            
            return {
                'module_info': self.get_module_info(),
                'health': health.get_health_summary(),
                'capabilities': [cap.value for cap in self.get_capabilities()],
                'dependencies': self.get_dependencies(),
                'configuration': self.get_configuration().__dict__,
                'metrics': self.get_metrics(),
                'health_trend': self.get_health_trend(),
                'version': self.version
            }
        except Exception as e:
            self.logger.error(f"Error getting module summary: {e}")
            return {
                'module_id': self.module_id,
                'error': str(e),
                'version': self.version
            }
    
    def is_healthy(self) -> bool:
        """Quick health check"""
        try:
            health = self.check_health()
            return health.is_healthy()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def get_issues(self) -> List[str]:
        """Get current issues"""
        try:
            health = self.check_health()
            return health.issues
        except Exception as e:
            return [f"Health check failed: {e}"]
    
    def validate_dependencies(self, available_modules: List[str]) -> List[str]:
        """Validate that all dependencies are available"""
        dependencies = self.get_dependencies()
        missing = [dep for dep in dependencies if dep not in available_modules]
        return missing
    
    def get_required_capabilities(self) -> List[ModuleCapability]:
        """Get capabilities required by this module"""
        # Override in subclasses to specify required capabilities
        return []
    
    def can_provide_capability(self, capability: ModuleCapability) -> bool:
        """Check if module can provide specific capability"""
        return capability in self.get_capabilities()
    
    def get_interface_version(self) -> str:
        """Get ReflectiveModule interface version"""
        return "1.0.0"
    
    def __str__(self) -> str:
        """String representation"""
        return f"ReflectiveModule({self.module_id}, v{self.version})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"ReflectiveModule(module_id='{self.module_id}', version='{self.version}')"


class ReflectiveModuleRegistry:
    """Registry for managing ReflectiveModule instances"""
    
    def __init__(self):
        """Initialize module registry"""
        self.modules: Dict[str, ReflectiveModule] = {}
        self.logger = logging.getLogger("reflective_module_registry")
    
    def register_module(self, module: ReflectiveModule) -> bool:
        """Register a module in the registry"""
        try:
            if module.module_id in self.modules:
                self.logger.warning(f"Module {module.module_id} already registered")
                return False
            
            self.modules[module.module_id] = module
            self.logger.info(f"Registered module: {module.module_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering module {module.module_id}: {e}")
            return False
    
    def unregister_module(self, module_id: str) -> bool:
        """Unregister a module from the registry"""
        try:
            if module_id not in self.modules:
                self.logger.warning(f"Module {module_id} not found")
                return False
            
            del self.modules[module_id]
            self.logger.info(f"Unregistered module: {module_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering module {module_id}: {e}")
            return False
    
    def get_module(self, module_id: str) -> Optional[ReflectiveModule]:
        """Get a module by ID"""
        return self.modules.get(module_id)
    
    def get_all_modules(self) -> List[ReflectiveModule]:
        """Get all registered modules"""
        return list(self.modules.values())
    
    def get_healthy_modules(self) -> List[ReflectiveModule]:
        """Get all healthy modules"""
        return [module for module in self.modules.values() if module.is_healthy()]
    
    def get_modules_by_capability(self, capability: ModuleCapability) -> List[ReflectiveModule]:
        """Get modules that provide specific capability"""
        return [module for module in self.modules.values() 
                if module.can_provide_capability(capability)]
    
    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate all module dependencies"""
        module_ids = list(self.modules.keys())
        dependency_issues = {}
        
        for module_id, module in self.modules.items():
            missing_deps = module.validate_dependencies(module_ids)
            if missing_deps:
                dependency_issues[module_id] = missing_deps
        
        return dependency_issues
    
    def get_registry_health(self) -> Dict[str, Any]:
        """Get overall registry health"""
        total_modules = len(self.modules)
        healthy_modules = len(self.get_healthy_modules())
        dependency_issues = self.validate_dependencies()
        
        return {
            'total_modules': total_modules,
            'healthy_modules': healthy_modules,
            'health_percentage': (healthy_modules / total_modules * 100) if total_modules > 0 else 0,
            'dependency_issues': dependency_issues,
            'modules_with_issues': len(dependency_issues)
        }
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary"""
        try:
            registry_health = self.get_registry_health()
            module_summaries = {}
            
            for module_id, module in self.modules.items():
                module_summaries[module_id] = module.get_module_summary()
            
            return {
                'registry_health': registry_health,
                'modules': module_summaries,
                'capabilities': self._get_capability_matrix(),
                'dependencies': self._get_dependency_graph()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting registry summary: {e}")
            return {'error': str(e)}
    
    def _get_capability_matrix(self) -> Dict[str, List[str]]:
        """Get capability matrix"""
        matrix = {}
        for capability in ModuleCapability:
            matrix[capability.value] = [
                module.module_id for module in self.modules.values()
                if module.can_provide_capability(capability)
            ]
        return matrix
    
    def _get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get dependency graph"""
        return {
            module_id: module.get_dependencies()
            for module_id, module in self.modules.items()
        }


# Global registry instance
_module_registry = ReflectiveModuleRegistry()


def get_module_registry() -> ReflectiveModuleRegistry:
    """Get the global module registry"""
    return _module_registry


def register_module(module: ReflectiveModule) -> bool:
    """Register a module in the global registry"""
    return _module_registry.register_module(module)


def unregister_module(module_id: str) -> bool:
    """Unregister a module from the global registry"""
    return _module_registry.unregister_module(module_id)
