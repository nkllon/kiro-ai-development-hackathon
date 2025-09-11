#!/usr/bin/env python3
"""
CLI Output - Output formatting and display

Extracted from cli.py for RM-DDD compliance.
Single responsibility: Output formatting and display logic.
"""

import json
import logging
from typing import Dict, Any, List, Optional
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
            'name': 'Cli Output',
            'description': 'cli_output module for DevPost integration',
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


class CLIOutput(ReflectiveModule):
    """CLI output formatting and display."""
    
    def __init__(self, verbose: bool = False, json_output: bool = False):
        super().__init__(module_id="cli_output", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize CLI output formatter."""
        self.verbose = verbose
        self.json_output = json_output
    
    def format_result(self, result: Dict[str, Any], command: str) -> str:
        """Format command result for output."""
        if self.json_output:
            return self._format_json_output(result)
        else:
            return self._format_text_output(result, command)
    
    def _format_json_output(self, result: Dict[str, Any]) -> str:
        """Format result as JSON."""
        try:
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error formatting JSON output: {e}")
            return json.dumps({
                "error": "Failed to format output as JSON",
                "message": str(e)
            }, indent=2)
    
    def _format_text_output(self, result: Dict[str, Any], command: str) -> str:
        """Format result as human-readable text."""
        if result.get("status") == "error":
            return self._format_error_output(result)
        
        if command == "interrogate":
            return self._format_interrogate_output(result)
        elif command == "status":
            return self._format_status_output(result)
        elif command == "create":
            return self._format_create_output(result)
        elif command == "update":
            return self._format_update_output(result)
        elif command == "delete":
            return self._format_delete_output(result)
        else:
            return self._format_generic_output(result)
    
    def _format_error_output(self, result: Dict[str, Any]) -> str:
        """Format error output."""
        return f"❌ Error: {result.get('message', 'Unknown error')}"
    
    def _format_interrogate_output(self, result: Dict[str, Any]) -> str:
        """Format interrogate command output."""
        if result.get("status") == "no_projects":
            return "📋 PROJECTS ANALYZED: 0\n\nNo projects found. Create a project first."
        
        output = []
        output.append(f"📋 PROJECTS ANALYZED: {result.get('projects_analyzed', 0)}")
        output.append("")
        
        projects = result.get("projects", [])
        for i, project in enumerate(projects, 1):
            output.append(f"Project {i}: {project.get('title', 'Unknown')}")
            output.append(f"  ID: {project.get('project_id', 'Unknown')}")
            output.append(f"  Status: {project.get('submission_status', 'Unknown')}")
            output.append(f"  Technologies: {', '.join(project.get('technologies', []))}")
            output.append(f"  Team Size: {project.get('team_size', 0)}")
            output.append(f"  Links: {project.get('links_count', 0)}")
            output.append(f"  Media: {project.get('media_count', 0)}")
            
            if self.verbose and 'full_description' in project:
                output.append(f"  Description: {project['full_description']}")
                if project.get('team_members'):
                    output.append("  Team Members:")
                    for member in project['team_members']:
                        output.append(f"    - {member.get('name', 'Unknown')} ({member.get('role', 'No role')})")
                if project.get('links'):
                    output.append("  Links:")
                    for link in project['links']:
                        output.append(f"    - {link.get('type', 'Unknown')}: {link.get('url', 'No URL')}")
            
            output.append("")
        
        return "\n".join(output)
    
    def _format_status_output(self, result: Dict[str, Any]) -> str:
        """Format status command output."""
        if "project" in result and result["project"]:
            # Single project
            project = result["project"]
            output = []
            output.append(f"📊 PROJECT STATUS: {project.get('title', 'Unknown')}")
            output.append(f"  ID: {project.get('project_id', 'Unknown')}")
            output.append(f"  Status: {project.get('submission_status', 'Unknown')}")
            output.append(f"  Technologies: {', '.join(project.get('technologies', []))}")
            output.append(f"  Team Size: {len(project.get('team_members', []))}")
            output.append(f"  Links: {len(project.get('links', []))}")
            output.append(f"  Created: {project.get('created_at', 'Unknown')}")
            output.append(f"  Updated: {project.get('updated_at', 'Unknown')}")
            return "\n".join(output)
        
        elif "projects" in result:
            # Multiple projects
            projects = result["projects"]
            output = []
            output.append(f"📊 PROJECT STATUS: {len(projects)} projects")
            output.append("")
            
            for i, project in enumerate(projects, 1):
                output.append(f"Project {i}: {project.get('title', 'Unknown')}")
                output.append(f"  ID: {project.get('project_id', 'Unknown')}")
                output.append(f"  Status: {project.get('submission_status', 'Unknown')}")
                output.append(f"  Technologies: {', '.join(project.get('technologies', []))}")
                output.append("")
            
            return "\n".join(output)
        
        return f"✅ {result.get('message', 'Success')}"
    
    def _format_create_output(self, result: Dict[str, Any]) -> str:
        """Format create command output."""
        if result.get("status") == "success":
            project = result.get("project", {})
            output = []
            output.append("✅ PROJECT CREATED SUCCESSFULLY")
            output.append("")
            output.append(f"Project: {project.get('title', 'Unknown')}")
            output.append(f"ID: {project.get('project_id', 'Unknown')}")
            output.append(f"Description: {project.get('description', 'No description')}")
            output.append(f"Technologies: {', '.join(project.get('technologies', []))}")
            output.append(f"Tags: {', '.join(project.get('tags', []))}")
            return "\n".join(output)
        else:
            return f"❌ Failed to create project: {result.get('message', 'Unknown error')}"
    
    def _format_update_output(self, result: Dict[str, Any]) -> str:
        """Format update command output."""
        if result.get("status") == "success":
            project = result.get("project", {})
            output = []
            output.append("✅ PROJECT UPDATED SUCCESSFULLY")
            output.append("")
            output.append(f"Project: {project.get('title', 'Unknown')}")
            output.append(f"ID: {project.get('project_id', 'Unknown')}")
            output.append(f"Description: {project.get('description', 'No description')}")
            output.append(f"Technologies: {', '.join(project.get('technologies', []))}")
            output.append(f"Tags: {', '.join(project.get('tags', []))}")
            return "\n".join(output)
        else:
            return f"❌ Failed to update project: {result.get('message', 'Unknown error')}"
    
    def _format_delete_output(self, result: Dict[str, Any]) -> str:
        """Format delete command output."""
        if result.get("status") == "success":
            return f"✅ Project {result.get('project_id', 'Unknown')} deleted successfully"
        else:
            return f"❌ Failed to delete project: {result.get('message', 'Unknown error')}"
    
    def _format_generic_output(self, result: Dict[str, Any]) -> str:
        """Format generic output."""
        if result.get("status") == "success":
            return f"✅ {result.get('message', 'Operation completed successfully')}"
        else:
            return f"❌ {result.get('message', 'Operation failed')}"
    
    def format_help(self, help_text: str) -> str:
        """Format help text."""
        return help_text
    
    def format_usage_error(self, error_message: str) -> str:
        """Format usage error."""
        return f"❌ Usage Error: {error_message}\n\nUse --help for more information."
    
    def format_validation_error(self, field: str, error_message: str) -> str:
        """Format validation error."""
        return f"❌ Validation Error for {field}: {error_message}"
    
    def format_system_error(self, error_message: str) -> str:
        """Format system error."""
        return f"❌ System Error: {error_message}"
    
    def format_success_message(self, message: str) -> str:
        """Format success message."""
        return f"✅ {message}"
    
    def format_info_message(self, message: str) -> str:
        """Format info message."""
        return f"ℹ️  {message}"
    
    def format_warning_message(self, message: str) -> str:
        """Format warning message."""
        return f"⚠️  {message}"
