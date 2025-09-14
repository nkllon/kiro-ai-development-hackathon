from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

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
            module_id="devpostapierror",
            status=status,
            health_score=health_score,
            issues=issues,
            capabilities=self.get_capabilities() if hasattr(self, 'get_capabilities') else [],
            dependencies=self.get_dependencies() if hasattr(self, 'get_dependencies') else [],
            metrics=self.get_metrics() if hasattr(self, 'get_metrics') else {},
            last_check=datetime.now()

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

        )