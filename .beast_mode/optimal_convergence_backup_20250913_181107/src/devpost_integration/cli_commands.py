#!/usr/bin/env python3
"""
CLI Commands - Unified command implementations

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: CLI command imports and re-exports.
"""

from typing import Dict, Any, List
from .cli_project_commands import CLIProjectCommands
from .cli_analysis_commands import CLIAnalysisCommands
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


class CLICommands(ReflectiveModule):
    """Unified CLI commands with RM-DDD compliance"""
    
    def __init__(self, project_manager):
        """Initialize CLI commands"""
        super().__init__(module_id="cli_commands", version="1.0.0")
        self.project_commands = CLIProjectCommands(project_manager)
        self.analysis_commands = CLIAnalysisCommands(project_manager)
        self._start_time = datetime.now()
        register_module(self)
    
    def interrogate_projects(self, verbose: bool = False, json_output: bool = False) -> Dict[str, Any]:
        """Interrogate all projects"""
        return self.analysis_commands.interrogate_projects(verbose, json_output)
    
    def get_project_status(self, project_id: str = None, json_output: bool = False) -> Dict[str, Any]:
        """Get project status"""
        return self.analysis_commands.get_project_status(project_id, json_output)
    
    def create_project(self, title: str, description: str, technologies: List[str] = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new project"""
        return self.project_commands.create_project(title, description, technologies, tags)
    
    def update_project(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing project"""
        return self.project_commands.update_project(project_id, **kwargs)
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project"""
        return self.project_commands.delete_project(project_id)
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'CLI Commands',
            'description': 'Unified CLI command implementations for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.HEALTH_MONITORING,
            ModuleCapability.CONFIGURATION,
            ModuleCapability.LOGGING
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'cli_project_commands',
            'cli_analysis_commands'
        ]
    
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Check command components
            if not hasattr(self, 'project_commands'):
                issues.append("Missing project_commands component")
                health_score -= 0.3
            
            if not hasattr(self, 'analysis_commands'):
                issues.append("Missing analysis_commands component")
                health_score -= 0.3
            
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
                return False
            return True
        except Exception:
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