#!/usr/bin/env python3
"""
Project Context Manager - Context switching and management

Extracted from multi_project_manager.py for RM-DDD compliance.
Single responsibility: Project context switching and management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import ProjectSummary, ContextSwitchResult
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Project Context Manager',
            'description': 'project_context_manager module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class ProjectContextManager(ReflectiveModule):
    """Project context switching and management."""
    
    def __init__(self):
        super().__init__(module_id="project_context_manager", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize project context manager."""
        self.current_project_id: Optional[str] = None
        self.context_history: List[Dict[str, Any]] = []
        self.context_data: Dict[str, Any] = {}
    
    def switch_context(self, project_id: str, context_data: Optional[Dict[str, Any]] = None) -> ContextSwitchResult:
        """Switch to a different project context."""
        try:
            previous_project_id = self.current_project_id
            
            # Save current context if switching away
            if self.current_project_id and self.current_project_id != project_id:
                self._save_current_context()
            
            # Switch to new project
            self.current_project_id = project_id
            self.context_data = context_data or {}
            
            # Record context switch
            switch_record = {
                'from_project_id': previous_project_id,
                'to_project_id': project_id,
                'switch_time': datetime.now(),
                'context_data': self.context_data.copy()
            }
            self.context_history.append(switch_record)
            
            # Keep only last 10 context switches
            if len(self.context_history) > 10:
                self.context_history = self.context_history[-10:]
            
            return ContextSwitchResult(
                success=True,
                from_project_id=previous_project_id,
                to_project_id=project_id,
                context_data=self.context_data.copy()
            )
            
        except Exception as e:
            logger.error(f"Error switching context to {project_id}: {e}")
            return ContextSwitchResult(
                success=False,
                to_project_id=project_id,
                error_message=str(e)
            )
    
    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """Get current project context."""
        if not self.current_project_id:
            return None
        
        return {
            'project_id': self.current_project_id,
            'context_data': self.context_data.copy(),
            'switch_time': self.context_history[-1]['switch_time'] if self.context_history else None
        }
    
    def clear_context(self) -> bool:
        """Clear current project context."""
        try:
            if self.current_project_id:
                self._save_current_context()
            
            self.current_project_id = None
            self.context_data = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing context: {e}")
            return False
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get context switch history."""
        return self.context_history.copy()
    
    def is_context_active(self, project_id: str) -> bool:
        """Check if a project context is currently active."""
        return self.current_project_id == project_id
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        return {
            'current_project_id': self.current_project_id,
            'context_data_keys': list(self.context_data.keys()),
            'history_length': len(self.context_history),
            'last_switch': self.context_history[-1] if self.context_history else None
        }
    
    def _save_current_context(self) -> None:
        """Save current context data."""
        if self.current_project_id and self.context_data:
            # In a real implementation, this would save to persistent storage
            logger.debug(f"Saving context for project {self.current_project_id}")
    
    def restore_context(self, project_id: str) -> bool:
        """Restore context for a project."""
        try:
            # In a real implementation, this would restore from persistent storage
            logger.debug(f"Restoring context for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring context for {project_id}: {e}")
            return False
    
    def validate_context_data(self, context_data: Dict[str, Any]) -> bool:
        """Validate context data structure."""
        if not isinstance(context_data, dict):
            return False
        
        # Add specific validation rules as needed
        return True
    
    def merge_context_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new context data with existing data."""
        if not self.validate_context_data(new_data):
            raise ValueError("Invalid context data structure")
        
        # Merge data, with new data taking precedence
        merged_data = self.context_data.copy()
        merged_data.update(new_data)
        
        return merged_data
    
    def get_context_metrics(self) -> Dict[str, Any]:
        """Get context management metrics."""
        return {
            'total_switches': len(self.context_history),
            'current_project_active': self.current_project_id is not None,
            'context_data_size': len(self.context_data),
            'average_switch_interval': self._calculate_average_switch_interval()
        }
    
    def _calculate_average_switch_interval(self) -> Optional[float]:
        """Calculate average time between context switches."""
        if len(self.context_history) < 2:
            return None
        
        intervals = []
        for i in range(1, len(self.context_history)):
            prev_time = self.context_history[i-1]['switch_time']
            curr_time = self.context_history[i]['switch_time']
            interval = (curr_time - prev_time).total_seconds()
            intervals.append(interval)
        
        return sum(intervals) / len(intervals) if intervals else None
