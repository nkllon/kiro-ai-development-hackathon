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


class AuthenticationServiceInterface(ABC):
    """Interface for authentication service operations."""
    
    @abstractmethod
    async def authenticate(self) -> AuthResult:
        """Perform authentication flow."""
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        pass
    
    @abstractmethod
    def get_current_token(self) -> Optional[AuthToken]:
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
        """Connect local project to Devpost submission."""
        pass
    
    @abstractmethod
    def get_project_config(self) -> DevpostConfig:
        """Get current project configuration."""
        pass
    
    @abstractmethod
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update project configuration."""
        pass
    
    @abstractmethod
    def get_project_metadata(self) -> ProjectMetadata:
        """Extract metadata from local project files."""
        pass
    
    @abstractmethod
    def validate_project(self) -> ValidationResult:
        """Validate project against Devpost requirements."""
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
        """Start monitoring project files for changes."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop file monitoring."""
        pass
    
    @abstractmethod
    def add_watch_path(self, path: Path) -> None:
        """Add path to monitoring."""
        pass
    
    @abstractmethod
    def remove_watch_path(self, path: Path) -> None:
        """Remove path from monitoring."""
        pass
    
    @abstractmethod
    def get_recent_changes(self) -> List[FileChangeEvent]:
        """Get recent file changes."""
        pass


class PreviewGeneratorInterface(ABC):
    """Interface for preview generation operations."""
    
    @abstractmethod
    def generate_preview(self) -> PreviewResult:
        """Generate project preview."""
        pass
    
    @abstractmethod
    def validate_submission(self) -> ValidationResult:
        """Validate project for submission."""
        pass
    
    @abstractmethod
    def export_preview_html(self, output_path: Path) -> Path:
        """Export preview as HTML file."""
        pass
    
    @abstractmethod
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        pass