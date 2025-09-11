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

logger = logging.getLogger(__name__)


class CLIAnalysisCommands:
    """Analysis and interrogation CLI command implementations."""
    
    def __init__(self, project_manager: DevpostProjectManager):
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
