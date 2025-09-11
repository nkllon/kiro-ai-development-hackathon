#!/usr/bin/env python3
"""
Multi-Project Orchestrator - Main orchestration for multi-project management

Extracted from multi_project_manager.py for RM-DDD compliance.
Single responsibility: Main orchestration for multi-project management.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import ProjectSummary, ProjectDashboard, MultiProjectConfig
from .project_context_manager import ProjectContextManager
from .conflict_resolution import ConflictResolver

logger = logging.getLogger(__name__)


class MultiProjectOrchestrator:
    """Main orchestration for multi-project management."""
    
    def __init__(self, config: MultiProjectConfig):
        """Initialize multi-project orchestrator."""
        self.config = config
        self.context_manager = ProjectContextManager()
        self.conflict_resolver = ConflictResolver()
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.project_connections: List[Dict[str, Any]] = []
    
    def add_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """Add a project to multi-project management."""
        try:
            # Check for conflicts before adding
            conflicts = self.conflict_resolver.detect_conflicts([project_id], {project_id: project_data})
            if conflicts:
                logger.warning(f"Conflicts detected when adding project {project_id}: {conflicts}")
                # Resolve conflicts automatically if configured
                if self.config.conflict_resolution_strategy.value == 'automatic':
                    for conflict in conflicts:
                        self.conflict_resolver.resolve_conflict(
                            conflict_id=f"{project_id}_{conflict['type']}",
                            project_ids=[project_id],
                            conflict_type=conflict['type'],
                            strategy=self.config.conflict_resolution_strategy
                        )
            
            # Add project
            self.projects[project_id] = project_data
            logger.info(f"Added project {project_id} to multi-project management")
            return True
            
        except Exception as e:
            logger.error(f"Error adding project {project_id}: {e}")
            return False
    
    def remove_project(self, project_id: str) -> bool:
        """Remove a project from multi-project management."""
        try:
            if project_id in self.projects:
                del self.projects[project_id]
                
                # Clear context if this was the current project
                if self.context_manager.current_project_id == project_id:
                    self.context_manager.clear_context()
                
                logger.info(f"Removed project {project_id} from multi-project management")
                return True
            else:
                logger.warning(f"Project {project_id} not found in multi-project management")
                return False
                
        except Exception as e:
            logger.error(f"Error removing project {project_id}: {e}")
            return False
    
    def switch_to_project(self, project_id: str, context_data: Optional[Dict[str, Any]] = None) -> bool:
        """Switch to a specific project."""
        try:
            if project_id not in self.projects:
                logger.error(f"Project {project_id} not found")
                return False
            
            result = self.context_manager.switch_context(project_id, context_data)
            if result.success:
                logger.info(f"Switched to project {project_id}")
                return True
            else:
                logger.error(f"Failed to switch to project {project_id}: {result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching to project {project_id}: {e}")
            return False
    
    def get_project_summary(self, project_id: str) -> Optional[ProjectSummary]:
        """Get summary for a specific project."""
        try:
            if project_id not in self.projects:
                return None
            
            project_data = self.projects[project_id]
            
            return ProjectSummary(
                project_id=project_id,
                title=project_data.get('title', 'Unknown'),
                status=project_data.get('status', 'unknown'),
                last_activity=datetime.now(),
                team_size=len(project_data.get('team_members', [])),
                file_count=project_data.get('file_count', 0),
                completion_percentage=project_data.get('completion_percentage', 0.0),
                deadline_status=project_data.get('deadline_status', 'unknown'),
                sync_status=project_data.get('sync_status', 'unknown'),
                metadata=project_data.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"Error getting project summary for {project_id}: {e}")
            return None
    
    def get_dashboard_data(self) -> ProjectDashboard:
        """Get dashboard data for all projects."""
        try:
            project_summaries = []
            recent_activity = []
            
            for project_id in self.projects:
                summary = self.get_project_summary(project_id)
                if summary:
                    project_summaries.append({
                        'project_id': summary.project_id,
                        'title': summary.title,
                        'status': summary.status,
                        'completion_percentage': summary.completion_percentage,
                        'last_activity': summary.last_activity.isoformat()
                    })
            
            # Get recent activity from context history
            context_history = self.context_manager.get_context_history()
            for switch in context_history[-10:]:  # Last 10 switches
                recent_activity.append({
                    'type': 'context_switch',
                    'project_id': switch['to_project_id'],
                    'timestamp': switch['switch_time'].isoformat(),
                    'details': f"Switched to {switch['to_project_id']}"
                })
            
            return ProjectDashboard(
                total_projects=len(self.projects),
                active_projects=len([p for p in project_summaries if p['status'] == 'active']),
                completed_projects=len([p for p in project_summaries if p['status'] == 'completed']),
                projects=project_summaries,
                recent_activity=recent_activity,
                system_status='healthy'
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return ProjectDashboard(
                total_projects=0,
                active_projects=0,
                completed_projects=0,
                projects=[],
                recent_activity=[],
                system_status='error'
            )
    
    def detect_and_resolve_conflicts(self) -> List[Dict[str, Any]]:
        """Detect and resolve conflicts between projects."""
        try:
            conflicts = self.conflict_resolver.detect_conflicts(
                list(self.projects.keys()),
                self.projects
            )
            
            resolved_conflicts = []
            for conflict in conflicts:
                conflict_id = f"conflict_{len(self.conflict_resolver.resolution_history)}"
                resolution = self.conflict_resolver.resolve_conflict(
                    conflict_id=conflict_id,
                    project_ids=conflict['projects'],
                    conflict_type=conflict['type'],
                    strategy=self.config.conflict_resolution_strategy
                )
                resolved_conflicts.append({
                    'conflict': conflict,
                    'resolution': resolution
                })
            
            return resolved_conflicts
            
        except Exception as e:
            logger.error(f"Error detecting and resolving conflicts: {e}")
            return []
    
    def get_management_metrics(self) -> Dict[str, Any]:
        """Get multi-project management metrics."""
        try:
            context_metrics = self.context_manager.get_context_metrics()
            resolution_metrics = self.conflict_resolver.get_resolution_metrics()
            
            return {
                'total_projects': len(self.projects),
                'context_switches': context_metrics['total_switches'],
                'current_project_active': context_metrics['current_project_active'],
                'conflicts_detected': resolution_metrics['total_conflicts'],
                'conflicts_resolved': resolution_metrics['resolved_conflicts'],
                'resolution_rate': resolution_metrics['resolution_rate'],
                'system_health': 'healthy' if len(self.projects) > 0 else 'no_projects'
            }
            
        except Exception as e:
            logger.error(f"Error getting management metrics: {e}")
            return {
                'total_projects': 0,
                'context_switches': 0,
                'current_project_active': False,
                'conflicts_detected': 0,
                'conflicts_resolved': 0,
                'resolution_rate': 0.0,
                'system_health': 'error'
            }
