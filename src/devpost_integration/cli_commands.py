#!/usr/bin/env python3
"""
CLI Commands - Unified command implementations

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: CLI command imports and re-exports.
"""

from .cli_project_commands import CLIProjectCommands
from .cli_analysis_commands import CLIAnalysisCommands


class CLICommands:
    """Unified CLI command implementations."""
    
    def __init__(self, project_manager):
        """Initialize CLI commands."""
        self.project_manager = project_manager
        self.project_commands = CLIProjectCommands(project_manager)
        self.analysis_commands = CLIAnalysisCommands(project_manager)
    
    def interrogate_projects(self, verbose: bool = False, json_output: bool = False):
        """Interrogate all projects and return analysis."""
        return self.analysis_commands.interrogate_projects(verbose, json_output)
    
    def get_project_status(self, project_id: Optional[str] = None, json_output: bool = False):
        """Get status of specific project or all projects."""
        return self.project_commands.get_project_status(project_id, json_output)
    
    def create_project(self, title: str, description: str, **kwargs):
        """Create a new project."""
        return self.project_commands.create_project(title, description, **kwargs)
    
    def update_project(self, project_id: str, **kwargs):
        """Update an existing project."""
        return self.project_commands.update_project(project_id, **kwargs)
    
    def delete_project(self, project_id: str):
        """Delete a project."""
        return self.project_commands.delete_project(project_id)
