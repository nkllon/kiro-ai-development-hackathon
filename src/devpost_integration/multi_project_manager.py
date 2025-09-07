#!/usr/bin/env python3
"""
Multi-Project Manager for Devpost Integration

The Requirements ARE the Solution - Centralized Multi-Project Management
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import asdict

from .models import (
    MultiProjectConfig, ProjectConnection, ProjectSummary, DevpostProject,
    ConflictResolutionStrategy, ContextSwitchResult, ConflictResolution,
    ProjectDashboard, GlobalSettings, DevpostConfig, SubmissionStatus,
    CompletionStatus, NotificationSettings
)
from .project_manager import DevpostProjectManager


logger = logging.getLogger(__name__)


class MultiProjectManager:
    """
    Centralized manager for multiple hackathon projects with context switching.
    
    Provides systematic project management, conflict resolution, and isolation
    between different hackathon projects while maintaining a unified interface.
    """
    
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        global_settings: Optional[GlobalSettings] = None
    ):
        """
        Initialize multi-project manager.
        
        Args:
            config_dir: Directory for storing multi-project configuration
            global_settings: Global settings for multi-project management
        """
        self.config_dir = config_dir or Path.home() / ".devpost" / "multi-project"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.projects_dir = self.config_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)
        
        # Initialize global settings
        self.global_settings = global_settings or GlobalSettings()
        
        # Load or create multi-project configuration
        self.config = self._load_config()
        
        # Project managers cache
        self._project_managers: Dict[str, DevpostProjectManager] = {}
        
        # Active project tracking
        self._active_project_id: Optional[str] = self.config.active_project_id
        
        # Conflict tracking
        self._detected_conflicts: List[Dict[str, Any]] = []
        
        logger.info(f"MultiProjectManager initialized with {len(self.config.project_connections)} projects")
    
    def _load_config(self) -> MultiProjectConfig:
        """Load multi-project configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Convert project connections from dict format
                project_connections = {}
                for project_id, conn_data in config_data.get("project_connections", {}).items():
                    # Convert path strings back to Path objects
                    if "local_path" in conn_data:
                        conn_data["local_path"] = Path(conn_data["local_path"])
                    
                    # Convert datetime strings back to datetime objects
                    if "last_sync" in conn_data and conn_data["last_sync"]:
                        conn_data["last_sync"] = datetime.fromisoformat(conn_data["last_sync"])
                    
                    # Reconstruct DevpostConfig if present
                    if "configuration" in conn_data:
                        config_dict = conn_data["configuration"]
                        # Convert notification preferences
                        if "notification_preferences" in config_dict:
                            notif_dict = config_dict["notification_preferences"]
                            if "deadline_advance_times" in notif_dict:
                                # Convert timedelta strings back to timedelta objects
                                advance_times = []
                                for time_str in notif_dict["deadline_advance_times"]:
                                    if isinstance(time_str, str) and time_str.startswith("timedelta"):
                                        # Parse timedelta string representation
                                        import re
                                        match = re.search(r'days=(\d+)', time_str)
                                        if match:
                                            advance_times.append(timedelta(days=int(match.group(1))))
                                        else:
                                            match = re.search(r'seconds=(\d+)', time_str)
                                            if match:
                                                advance_times.append(timedelta(seconds=int(match.group(1))))
                                    elif isinstance(time_str, (int, float)):
                                        advance_times.append(timedelta(seconds=time_str))
                                notif_dict["deadline_advance_times"] = advance_times
                            
                            conn_data["configuration"]["notification_preferences"] = NotificationSettings(**notif_dict)
                        
                        conn_data["configuration"] = DevpostConfig(**config_dict)
                    
                    project_connections[project_id] = ProjectConnection(**conn_data)
                
                # Convert conflict resolution strategy
                strategy = config_data.get("conflict_resolution_strategy", "manual_resolution")
                if isinstance(strategy, str):
                    strategy = ConflictResolutionStrategy(strategy)
                
                return MultiProjectConfig(
                    active_project_id=config_data.get("active_project_id"),
                    project_connections=project_connections,
                    global_settings=config_data.get("global_settings", {}),
                    conflict_resolution_strategy=strategy
                )
                
            except Exception as e:
                logger.warning(f"Failed to load multi-project config: {e}")
                return MultiProjectConfig()
        
        return MultiProjectConfig()
    
    def _save_config(self) -> None:
        """Save multi-project configuration to file."""
        try:
            # Convert configuration to serializable format
            config_data = {
                "active_project_id": self.config.active_project_id,
                "global_settings": self.config.global_settings,
                "conflict_resolution_strategy": self.config.conflict_resolution_strategy.value,
                "project_connections": {}
            }
            
            # Convert project connections to serializable format
            for project_id, connection in self.config.project_connections.items():
                # Manually convert connection to dict to handle nested objects
                conn_data = {
                    "local_path": str(connection.local_path),
                    "devpost_project_id": connection.devpost_project_id,
                    "hackathon_id": connection.hackathon_id,
                    "last_sync": connection.last_sync.isoformat() if connection.last_sync else None,
                    "sync_status": connection.sync_status,
                    "is_active": connection.is_active
                }
                
                # Handle configuration serialization
                if connection.configuration:
                    conn_config_data = {
                        "project_id": connection.configuration.project_id,
                        "hackathon_id": connection.configuration.hackathon_id,
                        "auth_token": connection.configuration.auth_token,
                        "sync_enabled": connection.configuration.sync_enabled,
                        "watch_patterns": connection.configuration.watch_patterns,
                        "sync_interval": connection.configuration.sync_interval,
                        "auto_sync_media": connection.configuration.auto_sync_media
                    }
                    
                    # Handle notification preferences
                    if connection.configuration.notification_preferences:
                        notif_prefs = connection.configuration.notification_preferences
                        conn_config_data["notification_preferences"] = {
                            "desktop_notifications": notif_prefs.desktop_notifications,
                            "email_notifications": notif_prefs.email_notifications,
                            "deadline_advance_times": [td.total_seconds() for td in notif_prefs.deadline_advance_times],
                            "sync_failure_notifications": notif_prefs.sync_failure_notifications,
                            "submission_status_notifications": notif_prefs.submission_status_notifications,
                            "quiet_hours_start": notif_prefs.quiet_hours_start,
                            "quiet_hours_end": notif_prefs.quiet_hours_end
                        }
                    
                    conn_data["configuration"] = conn_config_data
                

                
                config_data["project_connections"][project_id] = conn_data
            
            # Write configuration file
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.debug("Multi-project configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save multi-project config: {e}")
            raise
    
    def add_project(
        self,
        project_id: str,
        local_path: Path,
        devpost_project_id: str,
        hackathon_id: str,
        configuration: Optional[DevpostConfig] = None
    ) -> bool:
        """
        Add a new project to multi-project management.
        
        Args:
            project_id: Local project identifier
            local_path: Path to local project directory
            devpost_project_id: Devpost project ID
            hackathon_id: Hackathon ID
            configuration: Optional project configuration
            
        Returns:
            True if project was added successfully
        """
        try:
            # Validate inputs
            if not project_id or project_id in self.config.project_connections:
                logger.error(f"Project ID '{project_id}' is invalid or already exists")
                return False
            
            if not local_path.exists():
                logger.error(f"Local path does not exist: {local_path}")
                return False
            
            # Check for conflicts with existing projects
            conflicts = self._detect_project_conflicts(project_id, local_path, devpost_project_id)
            if conflicts:
                logger.warning(f"Conflicts detected when adding project {project_id}: {conflicts}")
                self._detected_conflicts.extend(conflicts)
                
                # Auto-resolve if strategy allows
                if self.config.conflict_resolution_strategy != ConflictResolutionStrategy.MANUAL_RESOLUTION:
                    self._auto_resolve_conflicts(conflicts)
            
            # Create default configuration if not provided
            if not configuration:
                configuration = DevpostConfig(
                    project_id=devpost_project_id,
                    hackathon_id=hackathon_id
                )
            
            # Create project connection
            connection = ProjectConnection(
                local_path=local_path,
                devpost_project_id=devpost_project_id,
                hackathon_id=hackathon_id,
                configuration=configuration,
                is_active=len(self.config.project_connections) == 0  # First project is active
            )
            
            # Add to configuration
            self.config.project_connections[project_id] = connection
            
            # Set as active if it's the first project
            if not self.config.active_project_id:
                self.config.active_project_id = project_id
                self._active_project_id = project_id
            
            # Save configuration
            self._save_config()
            
            logger.info(f"Successfully added project {project_id} to multi-project management")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add project {project_id}: {e}")
            return False
    
    def remove_project(self, project_id: str) -> bool:
        """
        Remove a project from multi-project management.
        
        Args:
            project_id: Project identifier to remove
            
        Returns:
            True if project was removed successfully
        """
        try:
            if project_id not in self.config.project_connections:
                logger.warning(f"Project {project_id} not found in multi-project management")
                return False
            
            # Clean up project manager cache
            if project_id in self._project_managers:
                del self._project_managers[project_id]
            
            # Remove from configuration
            del self.config.project_connections[project_id]
            
            # Update active project if necessary
            if self.config.active_project_id == project_id:
                # Switch to another project if available
                remaining_projects = list(self.config.project_connections.keys())
                if remaining_projects:
                    self.switch_project_context(remaining_projects[0])
                else:
                    self.config.active_project_id = None
                    self._active_project_id = None
            
            # Save configuration
            self._save_config()
            
            logger.info(f"Successfully removed project {project_id} from multi-project management")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove project {project_id}: {e}")
            return False
    
    def switch_project_context(self, project_id: str) -> ContextSwitchResult:
        """
        Switch to a different project context.
        
        Args:
            project_id: Project identifier to switch to
            
        Returns:
            ContextSwitchResult with switch status and details
        """
        try:
            if project_id not in self.config.project_connections:
                return ContextSwitchResult(
                    success=False,
                    error=f"Project {project_id} not found"
                )
            
            previous_project_id = self._active_project_id
            
            # Update active project
            if previous_project_id:
                self.config.project_connections[previous_project_id].is_active = False
            
            self.config.project_connections[project_id].is_active = True
            self.config.active_project_id = project_id
            self._active_project_id = project_id
            
            # Save configuration
            self._save_config()
            
            logger.info(f"Switched project context from {previous_project_id} to {project_id}")
            
            return ContextSwitchResult(
                success=True,
                previous_project_id=previous_project_id,
                new_project_id=project_id
            )
            
        except Exception as e:
            logger.error(f"Failed to switch project context to {project_id}: {e}")
            return ContextSwitchResult(
                success=False,
                error=str(e)
            )
    
    def get_active_project(self) -> Optional[ProjectConnection]:
        """
        Get the currently active project connection.
        
        Returns:
            Active ProjectConnection or None if no active project
        """
        if self._active_project_id and self._active_project_id in self.config.project_connections:
            return self.config.project_connections[self._active_project_id]
        return None
    
    def list_projects(self) -> List[ProjectSummary]:
        """
        List all projects with their status information.
        
        Returns:
            List of ProjectSummary objects
        """
        summaries = []
        
        for project_id, connection in self.config.project_connections.items():
            try:
                # Get project manager for this project
                manager = self._get_project_manager(project_id)
                
                # Calculate completion percentage and validation errors
                completion_percentage = 0.0
                validation_errors = 0
                pending_changes = 0
                
                if manager:
                    try:
                        status = manager.get_project_status()
                        validation_errors = len(status.validation_errors)
                        pending_changes = len(status.pending_changes)
                        
                        # Estimate completion percentage based on validation
                        if validation_errors == 0:
                            completion_percentage = 100.0
                        else:
                            # Simple heuristic: fewer errors = higher completion
                            completion_percentage = max(0, 100 - (validation_errors * 10))
                    except Exception as e:
                        logger.warning(f"Failed to get status for project {project_id}: {e}")
                
                # Create project summary
                summary = ProjectSummary(
                    project_id=project_id,
                    title=connection.devpost_project_id,  # Use devpost ID as title for now
                    hackathon_name=connection.hackathon_id,
                    deadline=None,  # TODO: Get from API when available
                    submission_status=SubmissionStatus.DRAFT,  # TODO: Get from API
                    completion_percentage=completion_percentage,
                    last_sync=connection.last_sync,
                    pending_changes=pending_changes,
                    validation_errors=validation_errors,
                    is_active=connection.is_active
                )
                
                summaries.append(summary)
                
            except Exception as e:
                logger.warning(f"Failed to create summary for project {project_id}: {e}")
                continue
        
        return summaries
    
    def display_project_dashboard(self) -> ProjectDashboard:
        """
        Generate project dashboard with overview statistics.
        
        Returns:
            ProjectDashboard with project summaries and statistics
        """
        projects = self.list_projects()
        active_project = None
        
        # Find active project
        for project in projects:
            if project.is_active:
                active_project = project
                break
        
        # Calculate statistics
        total_projects = len(projects)
        projects_with_deadlines = sum(1 for p in projects if p.deadline is not None)
        overdue_projects = sum(
            1 for p in projects 
            if p.deadline and p.deadline < datetime.now()
        )
        
        return ProjectDashboard(
            projects=projects,
            active_project=active_project,
            total_projects=total_projects,
            projects_with_deadlines=projects_with_deadlines,
            overdue_projects=overdue_projects,
            generated_at=datetime.now()
        )
    
    def prevent_cross_contamination(self, operation: str, project_id: str) -> bool:
        """
        Ensure operations only affect the intended project.
        
        Args:
            operation: Operation being performed
            project_id: Target project ID
            
        Returns:
            True if operation is safe to proceed
        """
        try:
            # Verify project exists
            if project_id not in self.config.project_connections:
                logger.error(f"Cross-contamination check failed: project {project_id} not found")
                return False
            
            # Verify project isolation
            connection = self.config.project_connections[project_id]
            
            # Check if local path conflicts with other projects
            for other_id, other_connection in self.config.project_connections.items():
                if other_id == project_id:
                    continue
                
                # Check for path overlap
                if self._paths_overlap(connection.local_path, other_connection.local_path):
                    logger.warning(
                        f"Cross-contamination risk: {operation} on {project_id} "
                        f"may affect {other_id} due to overlapping paths"
                    )
                    return False
            
            logger.debug(f"Cross-contamination check passed for {operation} on {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Cross-contamination check failed: {e}")
            return False
    
    def _detect_project_conflicts(
        self,
        project_id: str,
        local_path: Path,
        devpost_project_id: str
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicts when adding a new project.
        
        Args:
            project_id: New project ID
            local_path: New project local path
            devpost_project_id: New project Devpost ID
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        for existing_id, connection in self.config.project_connections.items():
            # Check for duplicate local paths
            if connection.local_path == local_path:
                conflicts.append({
                    "type": "duplicate_local_path",
                    "existing_project": existing_id,
                    "new_project": project_id,
                    "path": str(local_path),
                    "severity": "high"
                })
            
            # Check for overlapping paths
            elif self._paths_overlap(connection.local_path, local_path):
                conflicts.append({
                    "type": "overlapping_paths",
                    "existing_project": existing_id,
                    "new_project": project_id,
                    "existing_path": str(connection.local_path),
                    "new_path": str(local_path),
                    "severity": "medium"
                })
            
            # Check for duplicate Devpost project IDs
            if connection.devpost_project_id == devpost_project_id:
                conflicts.append({
                    "type": "duplicate_devpost_id",
                    "existing_project": existing_id,
                    "new_project": project_id,
                    "devpost_id": devpost_project_id,
                    "severity": "high"
                })
        
        return conflicts
    
    def resolve_project_conflicts(self) -> ConflictResolution:
        """
        Resolve detected project conflicts based on resolution strategy.
        
        Returns:
            ConflictResolution with resolution results
        """
        if not self._detected_conflicts:
            return ConflictResolution(
                conflicts_found=[],
                resolution_strategy=self.config.conflict_resolution_strategy,
                resolved_conflicts=[],
                manual_intervention_required=False
            )
        
        resolved_conflicts = []
        manual_intervention_required = False
        
        for conflict in self._detected_conflicts:
            if self.config.conflict_resolution_strategy == ConflictResolutionStrategy.MANUAL_RESOLUTION:
                manual_intervention_required = True
            else:
                # Attempt automatic resolution
                if self._auto_resolve_conflict(conflict):
                    resolved_conflicts.append(conflict["type"])
                else:
                    manual_intervention_required = True
        
        # Clear resolved conflicts
        if resolved_conflicts:
            self._detected_conflicts = [
                c for c in self._detected_conflicts 
                if c["type"] not in resolved_conflicts
            ]
        
        return ConflictResolution(
            conflicts_found=[c["type"] for c in self._detected_conflicts],
            resolution_strategy=self.config.conflict_resolution_strategy,
            resolved_conflicts=resolved_conflicts,
            manual_intervention_required=manual_intervention_required
        )
    
    def _get_project_manager(self, project_id: str) -> Optional[DevpostProjectManager]:
        """
        Get or create project manager for a specific project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            DevpostProjectManager instance or None if project not found
        """
        if project_id not in self.config.project_connections:
            return None
        
        # Return cached manager if available
        if project_id in self._project_managers:
            return self._project_managers[project_id]
        
        try:
            # Create new project manager
            connection = self.config.project_connections[project_id]
            manager = DevpostProjectManager()
            
            # Configure manager for this project
            # TODO: Set up manager with project-specific configuration
            
            # Cache the manager
            self._project_managers[project_id] = manager
            
            return manager
            
        except Exception as e:
            logger.error(f"Failed to create project manager for {project_id}: {e}")
            return None
    
    def _paths_overlap(self, path1: Path, path2: Path) -> bool:
        """
        Check if two paths overlap (one is parent of the other).
        
        Args:
            path1: First path
            path2: Second path
            
        Returns:
            True if paths overlap (one is parent of the other, but not if they're identical)
        """
        try:
            # Resolve paths to absolute form
            abs_path1 = path1.resolve()
            abs_path2 = path2.resolve()
            
            # If paths are identical, they don't "overlap" in the sense of parent-child
            if abs_path1 == abs_path2:
                return False
            
            # Check if one path is parent of the other
            try:
                abs_path1.relative_to(abs_path2)
                return True  # path1 is child of path2
            except ValueError:
                pass
            
            try:
                abs_path2.relative_to(abs_path1)
                return True  # path2 is child of path1
            except ValueError:
                pass
            
            return False
            
        except Exception:
            # If path resolution fails, assume no overlap
            return False
    
    def _auto_resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> None:
        """
        Automatically resolve conflicts based on resolution strategy.
        
        Args:
            conflicts: List of conflicts to resolve
        """
        for conflict in conflicts:
            self._auto_resolve_conflict(conflict)
    
    def _auto_resolve_conflict(self, conflict: Dict[str, Any]) -> bool:
        """
        Automatically resolve a single conflict.
        
        Args:
            conflict: Conflict to resolve
            
        Returns:
            True if conflict was resolved
        """
        try:
            conflict_type = conflict["type"]
            strategy = self.config.conflict_resolution_strategy
            
            if conflict_type == "duplicate_local_path":
                if strategy == ConflictResolutionStrategy.LOCAL_WINS:
                    # Remove existing project with same path
                    existing_project = conflict["existing_project"]
                    logger.info(f"Auto-resolving conflict: removing {existing_project} (local wins)")
                    return self.remove_project(existing_project)
                
            elif conflict_type == "duplicate_devpost_id":
                if strategy == ConflictResolutionStrategy.TIMESTAMP_BASED:
                    # Keep the most recently modified project
                    # This is a simplified implementation
                    logger.info(f"Auto-resolving conflict: using timestamp-based resolution")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to auto-resolve conflict: {e}")
            return False
    
    def get_project_count(self) -> int:
        """Get total number of managed projects."""
        return len(self.config.project_connections)
    
    def get_active_project_id(self) -> Optional[str]:
        """Get the ID of the currently active project."""
        return self._active_project_id
    
    def is_project_managed(self, project_id: str) -> bool:
        """Check if a project is managed by this multi-project manager."""
        return project_id in self.config.project_connections
    
    def get_project_connection(self, project_id: str) -> Optional[ProjectConnection]:
        """Get project connection details for a specific project."""
        return self.config.project_connections.get(project_id)
    
    def update_project_connection(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update project connection details.
        
        Args:
            project_id: Project identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if update was successful
        """
        try:
            if project_id not in self.config.project_connections:
                logger.error(f"Project {project_id} not found")
                return False
            
            connection = self.config.project_connections[project_id]
            
            # Update allowed fields
            if "last_sync" in updates:
                connection.last_sync = updates["last_sync"]
            if "sync_status" in updates:
                connection.sync_status = updates["sync_status"]
            if "configuration" in updates:
                connection.configuration = updates["configuration"]
            
            # Save configuration
            self._save_config()
            
            logger.info(f"Updated project connection for {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project connection for {project_id}: {e}")
            return False