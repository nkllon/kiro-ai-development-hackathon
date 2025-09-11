#!/usr/bin/env python3
"""
CLI Project Commands - Project-specific command implementations

Extracted from cli_commands.py for RM-DDD compliance.
Single responsibility: Project-specific CLI command implementations.
"""

import logging
from typing import Dict, List, Optional, Any

from .project_manager import DevpostProjectManager
from .models import DevpostProject

logger = logging.getLogger(__name__)


class CLIProjectCommands:
    """Project-specific CLI command implementations."""
    
    def __init__(self, project_manager: DevpostProjectManager):
        """Initialize project commands."""
        self.project_manager = project_manager
    
    def create_project(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """Create a new project."""
        try:
            project = self.project_manager.create_project(
                title=title,
                description=description,
                **kwargs
            )
            
            result = {
                "status": "success",
                "message": f"Created project: {project.title}",
                "project_id": project.project_id,
                "project": self._format_project_status(project)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                "status": "error",
                "message": f"Error creating project: {str(e)}",
                "project_id": None,
                "project": None
            }
    
    def update_project(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing project."""
        try:
            project = self.project_manager.get_project(project_id)
            if not project:
                return {
                    "status": "not_found",
                    "message": f"Project {project_id} not found",
                    "project": None
                }
            
            # Update project fields
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            # Save updated project
            self.project_manager._save_projects()
            
            result = {
                "status": "success",
                "message": f"Updated project: {project.title}",
                "project_id": project.project_id,
                "project": self._format_project_status(project)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return {
                "status": "error",
                "message": f"Error updating project: {str(e)}",
                "project_id": project_id,
                "project": None
            }
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project."""
        try:
            project = self.project_manager.get_project(project_id)
            if not project:
                return {
                    "status": "not_found",
                    "message": f"Project {project_id} not found",
                    "project_id": None
                }
            
            # Remove from projects
            if project_id in self.project_manager.projects:
                del self.project_manager.projects[project_id]
                self.project_manager._save_projects()
            
            result = {
                "status": "success",
                "message": f"Deleted project: {project.title}",
                "project_id": project_id
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return {
                "status": "error",
                "message": f"Error deleting project: {str(e)}",
                "project_id": project_id
            }
    
    def get_project_status(self, project_id: Optional[str] = None, json_output: bool = False) -> Dict[str, Any]:
        """Get status of specific project or all projects."""
        try:
            if project_id:
                project = self.project_manager.get_project(project_id)
                if not project:
                    result = {
                        "status": "not_found",
                        "message": f"Project {project_id} not found",
                        "project": None
                    }
                else:
                    result = {
                        "status": "success",
                        "message": f"Retrieved project {project_id}",
                        "project": self._format_project_status(project)
                    }
            else:
                projects = self.project_manager.list_projects()
                result = {
                    "status": "success",
                    "message": f"Retrieved {len(projects)} projects",
                    "projects": [self._format_project_status(p) for p in projects]
                }
            
            if json_output:
                return result
            else:
                return self._format_status_output(result)
                
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            error_result = {
                "status": "error",
                "message": f"Error retrieving project status: {str(e)}",
                "project": None
            }
            
            if json_output:
                return error_result
            else:
                return f"❌ Error: {str(e)}"
    
    def _format_project_status(self, project: DevpostProject) -> Dict[str, Any]:
        """Format project status for display."""
        return {
            "project_id": project.project_id,
            "title": project.title,
            "description": project.description,
            "technologies": project.technologies,
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
            "submission_status": project.submission_status.value,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "tags": project.tags
        }
    
    def _format_status_output(self, result: Dict[str, Any]) -> str:
        """Format status command output."""
        if result["status"] == "error":
            return f"❌ Error: {result['message']}"
        
        if result["status"] == "not_found":
            return f"❌ {result['message']}"
        
        if "project" in result and result["project"]:
            # Single project
            project = result["project"]
            output = []
            output.append(f"📊 PROJECT STATUS: {project['title']}")
            output.append(f"  ID: {project['project_id']}")
            output.append(f"  Status: {project['submission_status']}")
            output.append(f"  Technologies: {', '.join(project['technologies'])}")
            output.append(f"  Team Size: {len(project['team_members'])}")
            output.append(f"  Links: {len(project['links'])}")
            output.append(f"  Created: {project['created_at']}")
            output.append(f"  Updated: {project['updated_at']}")
            return "\n".join(output)
        
        elif "projects" in result:
            # Multiple projects
            output = []
            output.append(f"📊 PROJECT STATUS: {len(result['projects'])} projects")
            output.append("")
            
            for i, project in enumerate(result["projects"], 1):
                output.append(f"Project {i}: {project['title']}")
                output.append(f"  ID: {project['project_id']}")
                output.append(f"  Status: {project['submission_status']}")
                output.append(f"  Technologies: {', '.join(project['technologies'])}")
                output.append("")
            
            return "\n".join(output)
        
        return f"✅ {result['message']}"
