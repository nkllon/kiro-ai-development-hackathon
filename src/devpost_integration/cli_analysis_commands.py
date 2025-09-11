#!/usr/bin/env python3
"""
CLI Analysis Commands - Analysis and interrogation command implementations

Extracted from cli_commands.py for RM-DDD compliance.
Single responsibility: Analysis and interrogation CLI command implementations.
"""

import logging
from typing import Dict, List, Optional, Any

from .project_manager import DevpostProjectManager
from .models import DevpostProject
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
            'name': 'Cli Analysis Commands',
            'description': 'cli_analysis_commands module for DevPost integration',
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


class CLIAnalysisCommands(ReflectiveModule):
    """Analysis and interrogation CLI command implementations."""
    
    def __init__(self, project_manager: DevpostProjectManager):
        super().__init__(module_id="cli_analysis_commands", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize analysis commands."""
        self.project_manager = project_manager
    
    def interrogate_projects(self, verbose: bool = False, json_output: bool = False) -> Dict[str, Any]:
        """Interrogate all projects and return analysis."""
        try:
            projects = self.project_manager.list_projects()
            
            if not projects:
                result = {
                    "status": "no_projects",
                    "message": "No projects found",
                    "projects_analyzed": 0,
                    "projects": []
                }
            else:
                analysis = self._analyze_projects(projects, verbose)
                result = {
                    "status": "success",
                    "message": f"Analyzed {len(projects)} projects",
                    "projects_analyzed": len(projects),
                    "projects": analysis
                }
            
            if json_output:
                return result
            else:
                return self._format_interrogate_output(result, verbose)
                
        except Exception as e:
            logger.error(f"Error interrogating projects: {e}")
            error_result = {
                "status": "error",
                "message": f"Error analyzing projects: {str(e)}",
                "projects_analyzed": 0,
                "projects": []
            }
            
            if json_output:
                return error_result
            else:
                return f"❌ Error: {str(e)}"
    
    def _analyze_projects(self, projects: List[DevpostProject], verbose: bool = False) -> List[Dict[str, Any]]:
        """Analyze projects and return detailed information."""
        analysis = []
        
        for project in projects:
            project_info = {
                "project_id": project.project_id,
                "title": project.title,
                "description": project.description[:100] + "..." if len(project.description) > 100 else project.description,
                "technologies": project.technologies,
                "team_size": len(project.team_members),
                "links_count": len(project.links),
                "media_count": len(project.media_files),
                "submission_status": project.submission_status.value,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            }
            
            if verbose:
                project_info.update({
                    "full_description": project.description,
                    "team_members": [
                        {
                            "name": member.name,
                            "role": member.role,
                            "email": member.email
                        } for member in project.team_members
                    ],
                    "links": [
                        {
                            "url": link.url,
                            "type": link.link_type,
                            "title": link.title
                        } for link in project.links
                    ],
                    "tags": project.tags,
                    "metadata": project.metadata
                })
            
            analysis.append(project_info)
        
        return analysis
    
    def _format_interrogate_output(self, result: Dict[str, Any], verbose: bool = False) -> str:
        """Format interrogate command output."""
        if result["status"] == "no_projects":
            return "📋 PROJECTS ANALYZED: 0\n\nNo projects found. Create a project first."
        
        output = []
        output.append(f"📋 PROJECTS ANALYZED: {result['projects_analyzed']}")
        output.append("")
        
        for i, project in enumerate(result["projects"], 1):
            output.append(f"Project {i}: {project['title']}")
            output.append(f"  ID: {project['project_id']}")
            output.append(f"  Status: {project['submission_status']}")
            output.append(f"  Technologies: {', '.join(project['technologies'])}")
            output.append(f"  Team Size: {project['team_size']}")
            output.append(f"  Links: {project['links_count']}")
            output.append(f"  Media: {project['media_count']}")
            
            if verbose:
                output.append(f"  Description: {project['full_description']}")
                if project['team_members']:
                    output.append("  Team Members:")
                    for member in project['team_members']:
                        output.append(f"    - {member['name']} ({member['role']})")
                if project['links']:
                    output.append("  Links:")
                    for link in project['links']:
                        output.append(f"    - {link['type']}: {link['url']}")
            
            output.append("")
        
        return "\n".join(output)
