"""
Devpost Hackathon Integration Module

This module provides seamless integration with Devpost to keep hackathon projects
synchronized and up-to-date. It includes authentication, project management,
file monitoring, and automated synchronization capabilities.
"""

from .interfaces import (
    DevpostAPIClientInterface,
    AuthenticationServiceInterface,
    ProjectManagerInterface,
    SyncManagerInterface,
    FileMonitorInterface,
    PreviewGeneratorInterface,
)

from .models import (
    DevpostProject,
    ProjectMetadata,
    SyncOperation,
    FileChangeEvent,
    DevpostConfig,
    ProjectConnection,
)

__all__ = [
    # Interfaces
    "DevpostAPIClientInterface",
    "AuthenticationServiceInterface", 
    "ProjectManagerInterface",
    "SyncManagerInterface",
    "FileMonitorInterface",
    "PreviewGeneratorInterface",
    # Models
    "DevpostProject",
    "ProjectMetadata", 
    "SyncOperation",
    "FileChangeEvent",
    "DevpostConfig",
    "ProjectConnection",
]