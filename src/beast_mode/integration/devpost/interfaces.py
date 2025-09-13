"""
Core interfaces for Devpost integration components.

This module defines the abstract base classes and interfaces that all
Devpost integration components must implement, ensuring consistent
behavior and enabling dependency injection for testing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .models import (
    DevpostProject,
    ProjectMetadata,
    SyncOperation,
    FileChangeEvent,
    DevpostConfig,
    ProjectConnection,
    AuthToken,
    AuthResult,
    SyncResult,
    PreviewResult,
    ValidationResult,
)


class DevpostAPIClientInterface(ABC):
    """Interface for Devpost API client operations."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """Authenticate with Devpost API."""
        pass
    
    @abstractmethod
    async def get_user_projects(self) -> List[DevpostProject]:
        """Retrieve user's hackathon projects."""
        pass
    
    @abstractmethod
    async def get_project_details(self, project_id: str) -> DevpostProject:
        """Get detailed information for a specific project."""
        pass
    
    @abstractmethod
    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update project information on Devpost."""
        pass
    
    @abstractmethod
    async def upload_media(self, project_id: str, media_path: Path) -> Dict[str, Any]:
        """Upload media file to project."""
        pass
    
    @abstractmethod
    async def create_project(self, hackathon_id: str, project_data: Dict[str, Any]) -> DevpostProject:
        """Create a new project submission."""
        pass
    
    # Deadline and Submission Requirement Methods (Task 4.4)
    
    @abstractmethod
    async def get_hackathon_deadlines(self, hackathon_id: str, include_past: bool = False) -> List[Dict[str, Any]]:
        """Retrieve hackathon deadlines and important dates."""
        pass
    
    @abstractmethod
    async def get_submission_requirements(self, hackathon_id: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve submission requirements for a hackathon."""
        pass
    
    @abstractmethod
    async def update_submission_status(self, project_id: str, status: str, completion_notes: Optional[str] = None) -> Dict[str, Any]:
        """Update the submission status of a project."""
        pass
    
    @abstractmethod
    async def validate_project_requirements(self, project_id: str, hackathon_id: str) -> Dict[str, Any]:
        """Validate a project against hackathon submission requirements."""
        pass
    
    @abstractmethod
    async def get_project_submission_history(self, project_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get submission history and status changes for a project."""
        pass
    
    @abstractmethod
    async def schedule_deadline_notification(self, project_id: str, deadline_type: str, advance_time_hours: int, notification_type: str = "email", custom_message: Optional[str] = None) -> Dict[str, Any]:
        """Schedule a deadline notification for a project."""
        pass
    
    @abstractmethod
    async def get_deadline_notifications(self, project_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get scheduled deadline notifications for a project."""
        pass
    
    @abstractmethod
    async def cancel_deadline_notification(self, project_id: str, notification_id: str) -> Dict[str, Any]:
        """Cancel a scheduled deadline notification."""
        pass


class AuthenticationServiceInterface(ABC):
    """Interface for authentication service operations."""
    
    @abstractmethod
    async def authenticate(self) -> AuthResult:
        """Perform authentication flow."""
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Check if currently authenticated."""
        pass
    
    @abstractmethod
    def get_current_token(self) -> Optional[AuthToken]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get current authentication token."""
        pass
    
    @abstractmethod
    async def refresh_token(self) -> AuthToken:
        """Refresh authentication token."""
        pass


class ProjectManagerInterface(ABC):
    """Interface for project management operations."""
    
    @abstractmethod
    def connect_to_devpost(self, project_id: str, hackathon_id: str) -> ProjectConnection:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Connect local project to Devpost submission."""
        pass
    
    @abstractmethod
    def get_project_config(self) -> DevpostConfig:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get current project configuration."""
        pass
    
    @abstractmethod
    def update_config(self, updates: Dict[str, Any]) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Update project configuration."""
        pass
    
    @abstractmethod
    def get_project_metadata(self) -> ProjectMetadata:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Extract metadata from local project files."""
        pass
    
    @abstractmethod
    def validate_project(self) -> ValidationResult:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate project against Devpost requirements."""
        pass
    
    @abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """List all connected projects with their status."""
        pass
    
    @abstractmethod
    def switch_project(self, project_id: str) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Switch to a different project context."""
        pass
    
    @abstractmethod
    def get_project_status(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get detailed status for a project."""
        pass
    
    @abstractmethod
    def disconnect_project(self, project_id: str) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Disconnect a project from Devpost integration."""
        pass
    
    @abstractmethod
    def detect_project_conflicts(self) -> List[Dict[str, Any]]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Detect conflicts between projects."""
        pass
    
    @abstractmethod
    def resolve_conflict(self, conflict_type: str, resolution: str, **kwargs) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Resolve a detected conflict."""
        pass


class SyncManagerInterface(ABC):
    """Interface for synchronization operations."""
    
    @abstractmethod
    async def sync_metadata(self) -> SyncResult:
        """Synchronize project metadata."""
        pass
    
    @abstractmethod
    async def sync_media_files(self) -> SyncResult:
        """Synchronize media files."""
        pass
    
    @abstractmethod
    async def full_sync(self) -> SyncResult:
        """Perform complete project synchronization."""
        pass
    
    @abstractmethod
    def queue_sync_operation(self, operation: SyncOperation) -> None:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Add sync operation to queue."""
        pass
    
    @abstractmethod
    async def process_sync_queue(self) -> List[SyncResult]:
        """Process all queued sync operations."""
        pass


class FileMonitorInterface(ABC):
    """Interface for file monitoring operations."""
    
    @abstractmethod
    def start_monitoring(self) -> None:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Start monitoring project files for changes."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Stop file monitoring."""
        pass
    
    @abstractmethod
    def add_watch_path(self, path: Path) -> None:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Add path to monitoring."""
        pass
    
    @abstractmethod
    def remove_watch_path(self, path: Path) -> None:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Remove path from monitoring."""
        pass
    
    @abstractmethod
    def get_recent_changes(self) -> List[FileChangeEvent]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get recent file changes."""
        pass


class PreviewGeneratorInterface(ABC):
    """Interface for preview generation operations."""
    
    @abstractmethod
    def generate_preview(self) -> PreviewResult:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Generate project preview."""
        pass
    
    @abstractmethod
    def validate_submission(self) -> ValidationResult:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate project for submission."""
        pass
    
    @abstractmethod
    def export_preview_html(self, output_path: Path) -> Path:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Export preview as HTML file."""
        pass
    
    @abstractmethod
    def get_missing_fields(self) -> List[str]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get list of missing required fields."""
        pass