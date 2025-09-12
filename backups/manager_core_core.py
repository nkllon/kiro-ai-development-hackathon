"""
Manager Core Core

This module was extracted from manager_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from ..models import DevpostProject, ProjectMetadata, DevpostConfig, ProjectConnection, SyncStatus, ValidationResult
from ..interfaces import ProjectManagerInterface
from ..config import DevpostConfigManager
from ....core.exceptions import ConfigurationError, ValidationError
import tomllib
import tomli as tomllib
import tomllib
import tomli as tomllib

def __init__(self, project_root: Optional[Path]=None):
    """Initialize project manager.
        
        Args:
            project_root: Root directory of the project. If None, uses current directory.
        """
    self.project_root = project_root or Path.cwd()
    self.config_manager = DevpostConfigManager(self.project_root)
    self._current_connection: Optional[ProjectConnection] = None
    self._active_project_id: Optional[str] = None
    self._load_current_connection()

def connect_to_devpost(self, project_id: str, hackathon_id: str) -> ProjectConnection:
    """Connect local project to Devpost submission.
        
        Args:
            project_id: Devpost project ID
            hackathon_id: Hackathon ID
            
        Returns:
            ProjectConnection instance
            
        Raises:
            ConfigurationError: If connection setup fails
        """
    try:
        config = DevpostConfig(project_id=project_id, hackathon_id=hackathon_id, sync_enabled=True, watch_patterns=['README*', '*.md', 'package.json', 'pyproject.toml', 'media/*'], sync_interval=300, auto_sync_media=True, notification_enabled=True)
        connection = ProjectConnection(local_path=self.project_root, devpost_project_id=project_id, hackathon_id=hackathon_id, sync_status=SyncStatus.PENDING, configuration=config, created_at=datetime.now())
        self.config_manager.save_connection(connection)
        self._current_connection = connection
        return connection
    except Exception as e:
        raise ConfigurationError(f'Failed to connect to Devpost project: {e}')

def get_project_config(self) -> DevpostConfig:
    """Get current project configuration.
        
        Returns:
            DevpostConfig instance
            
        Raises:
            ConfigurationError: If no configuration is found
        """
    if self._current_connection:
        return self._current_connection.configuration
    config = self.config_manager.load_config()
    if config:
        return config
    raise ConfigurationError('No project configuration found')

def update_config(self, updates: Dict[str, Any]) -> bool:
    """Update project configuration.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            True if update was successful
            
        Raises:
            ConfigurationError: If update fails
        """
    try:
        current_config = self.get_project_config()
        config_dict = current_config.model_dump()
        config_dict.update(updates)
        updated_config = DevpostConfig(**config_dict)
        if self._current_connection:
            self._current_connection.configuration = updated_config
            self.config_manager.save_connection(self._current_connection)
        else:
            self.config_manager.save_config(updated_config)
        return True
    except Exception as e:
        raise ConfigurationError(f'Failed to update configuration: {e}')

def get_project_metadata(self) -> ProjectMetadata:
    """Extract metadata from local project files.
        
        Returns:
            ProjectMetadata instance with extracted information
        """
    metadata = ProjectMetadata(title='Untitled Project')
    package_data = self._extract_package_json_metadata()
    if package_data:
        if package_data.get('name'):
            metadata.title = package_data.get('name', '')
        if package_data.get('description'):
            metadata.description = package_data.get('description', '')
        metadata.repository_url = self._extract_repository_url(package_data)
        metadata.package_info.update(package_data)
    readme_data = self._extract_readme_metadata()
    if readme_data:
        if not metadata.title or metadata.title == 'Untitled Project':
            metadata.title = readme_data.get('title', metadata.title)
        if not metadata.tagline:
            metadata.tagline = readme_data.get('tagline', metadata.tagline)
        if not metadata.description:
            metadata.description = readme_data.get('description', metadata.description)
        metadata.readme_path = readme_data.get('path')
    pyproject_data = self._extract_pyproject_metadata()
    if pyproject_data:
        if pyproject_data.get('name'):
            metadata.title = pyproject_data.get('name', '')
        if pyproject_data.get('description'):
            metadata.description = pyproject_data.get('description', '')
        metadata.repository_url = metadata.repository_url or self._extract_repository_url(pyproject_data)
        metadata.package_info.update(pyproject_data)
    git_data = self._extract_git_metadata()
    if git_data:
        metadata.repository_url = metadata.repository_url or git_data.get('repository_url')
        metadata.team_members.extend(git_data.get('contributors', []))
    metadata.title = metadata.title.strip() if metadata.title != 'Untitled Project' else ''
    metadata.tagline = metadata.tagline.strip()
    metadata.description = metadata.description.strip()
    metadata.team_members = list(set(metadata.team_members))
    if not metadata.title or metadata.title == 'Untitled Project':
        metadata.title = self.project_root.name.replace('-', ' ').replace('_', ' ').title()
    return metadata

def _load_current_connection(self) -> None:
    """Load current project connection if it exists."""
    try:
        self._current_connection = self.config_manager.load_connection(self.project_root)
    except Exception:
        self._current_connection = None

def _extract_readme_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from README files."""
    readme_patterns = ['README.md', 'README.rst', 'README.txt', 'README']
    for pattern in readme_patterns:
        readme_path = self.project_root / pattern
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                return self._parse_readme_content(content, readme_path)
            except Exception:
                continue
    return None

def _extract_package_json_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from package.json."""
    package_json_path = self.project_root / 'package.json'
    if not package_json_path.exists():
        return None
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def _extract_pyproject_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from pyproject.toml."""
    pyproject_path = self.project_root / 'pyproject.toml'
    if not pyproject_path.exists():
        return None
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            return None
    try:
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
        project_data = data.get('project', {})
        if not project_data:
            poetry_data = data.get('tool', {}).get('poetry', {})
            if poetry_data:
                project_data = poetry_data
        return project_data
    except Exception:
        return None

def _extract_git_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from Git configuration."""
    git_dir = self.project_root / '.git'
    if not git_dir.exists():
        return None
    metadata = {}
    try:
        git_config_path = git_dir / 'config'
        if git_config_path.exists():
            config_content = git_config_path.read_text(encoding='utf-8')
            url_match = re.search('url\\s*=\\s*(.+)', config_content)
            if url_match:
                url = url_match.group(1).strip()
                if url.startswith('git@'):
                    url = url.replace('git@github.com:', 'https://github.com/')
                    url = url.replace('.git', '')
                metadata['repository_url'] = url
        metadata['contributors'] = []
    except Exception:
        pass
    return metadata if metadata else None

def _extract_repository_url(self, package_data: Dict[str, Any]) -> Optional[str]:
    """Extract repository URL from package data."""
    repo_fields = ['repository', 'homepage', 'url']
    for field in repo_fields:
        if field in package_data:
            repo_info = package_data[field]
            if isinstance(repo_info, str):
                return repo_info
            elif isinstance(repo_info, dict):
                return repo_info.get('url')
    return None

def _find_media_files(self) -> List[Path]:
    """Find media files in the project."""
    media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.mov', '.avi', '.webm'}
    media_files = []
    media_dirs = ['media', 'images', 'screenshots', 'assets', 'docs/images']
    for dir_name in media_dirs:
        media_dir = self.project_root / dir_name
        if media_dir.exists():
            for file_path in media_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                    media_files.append(file_path)
    for pattern in ['screenshot*', 'demo*', 'preview*']:
        for file_path in self.project_root.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                media_files.append(file_path)
    return media_files

def list_projects(self) -> List[Dict[str, Any]]:
    """List all connected projects with their status.
        
        Returns:
            List of project information dictionaries
        """
    connections = self.config_manager.list_connections()
    projects = []
    for connection in connections:
        project_info = {'project_id': connection.devpost_project_id, 'hackathon_id': connection.hackathon_id, 'local_path': str(connection.local_path), 'sync_status': connection.sync_status.value, 'last_sync': connection.last_sync.isoformat() if connection.last_sync else None, 'created_at': connection.created_at.isoformat(), 'is_active': connection.devpost_project_id == self._active_project_id, 'sync_enabled': connection.configuration.sync_enabled}
        projects.append(project_info)
    return projects

def switch_project(self, project_id: str) -> bool:
    """Switch to a different project context.
        
        Args:
            project_id: Devpost project ID to switch to
            
        Returns:
            True if switch was successful
            
        Raises:
            ConfigurationError: If project is not found or switch fails
        """
    connections = self.config_manager.list_connections()
    target_connection = None
    for connection in connections:
        if connection.devpost_project_id == project_id:
            target_connection = connection
            break
    if not target_connection:
        raise ConfigurationError(f'Project {project_id} not found')
    if not target_connection.local_path.exists():
        raise ConfigurationError(f'Project path {target_connection.local_path} no longer exists')
    self._current_connection = target_connection
    self._active_project_id = project_id
    return True

def get_project_status(self, project_id: Optional[str]=None) -> Dict[str, Any]:
    """Get detailed status for a project.
        
        Args:
            project_id: Project ID to get status for. If None, uses current project.
            
        Returns:
            Dictionary with project status information
            
        Raises:
            ConfigurationError: If project is not found
        """
    if project_id:
        connections = self.config_manager.list_connections()
        target_connection = None
        for connection in connections:
            if connection.devpost_project_id == project_id:
                target_connection = connection
                break
        if not target_connection:
            raise ConfigurationError(f'Project {project_id} not found')
    else:
        if not self._current_connection:
            raise ConfigurationError('No active project')
        target_connection = self._current_connection
    original_connection = self._current_connection
    original_project_id = self._active_project_id
    try:
        self._current_connection = target_connection
        self._active_project_id = target_connection.devpost_project_id
        metadata = self.get_project_metadata()
        validation = self.validate_project()
        status = {'project_id': target_connection.devpost_project_id, 'hackathon_id': target_connection.hackathon_id, 'local_path': str(target_connection.local_path), 'sync_status': target_connection.sync_status.value, 'last_sync': target_connection.last_sync.isoformat() if target_connection.last_sync else None, 'created_at': target_connection.created_at.isoformat(), 'is_active': target_connection.devpost_project_id == original_project_id, 'configuration': target_connection.configuration.model_dump(), 'metadata': metadata.model_dump(), 'validation': {'is_valid': validation.is_valid, 'missing_fields': validation.missing_fields, 'validation_errors': validation.validation_errors, 'warnings': validation.warnings}, 'path_exists': target_connection.local_path.exists()}
        return status
    finally:
        self._current_connection = original_connection
        self._active_project_id = original_project_id

def disconnect_project(self, project_id: str) -> bool:
    """Disconnect a project from Devpost integration.
        
        Args:
            project_id: Project ID to disconnect
            
        Returns:
            True if disconnection was successful
            
        Raises:
            ConfigurationError: If project is not found
        """
    connections = self.config_manager.list_connections()
    target_connection = None
    for connection in connections:
        if connection.devpost_project_id == project_id:
            target_connection = connection
            break
    if not target_connection:
        raise ConfigurationError(f'Project {project_id} not found')
    success = self.config_manager.remove_connection(target_connection.local_path)
    if self._active_project_id == project_id:
        self._current_connection = None
        self._active_project_id = None
    return success

def detect_project_conflicts(self) -> List[Dict[str, Any]]:
    """Detect conflicts between projects.
        
        Returns:
            List of conflict descriptions
        """
    connections = self.config_manager.list_connections()
    conflicts = []
    project_ids = {}
    for connection in connections:
        project_id = connection.devpost_project_id
        if project_id in project_ids:
            conflicts.append({'type': 'duplicate_project_id', 'project_id': project_id, 'paths': [str(project_ids[project_id]), str(connection.local_path)], 'description': f'Project ID {project_id} is connected to multiple local paths'})
        else:
            project_ids[project_id] = connection.local_path
    hackathon_paths = {}
    for connection in connections:
        hackathon_id = connection.hackathon_id
        path_str = str(connection.local_path)
        if hackathon_id in hackathon_paths:
            if path_str in hackathon_paths[hackathon_id]:
                conflicts.append({'type': 'duplicate_hackathon_path', 'hackathon_id': hackathon_id, 'path': path_str, 'project_ids': hackathon_paths[hackathon_id][path_str], 'description': f'Multiple projects for hackathon {hackathon_id} at path {path_str}'})
            else:
                hackathon_paths[hackathon_id][path_str] = [connection.devpost_project_id]
        else:
            hackathon_paths[hackathon_id] = {path_str: [connection.devpost_project_id]}
    for connection in connections:
        if not connection.local_path.exists():
            conflicts.append({'type': 'missing_path', 'project_id': connection.devpost_project_id, 'path': str(connection.local_path), 'description': f'Project path {connection.local_path} no longer exists'})
    return conflicts

def resolve_conflict(self, conflict_type: str, resolution: str, **kwargs) -> bool:
    """Resolve a detected conflict.
        
        Args:
            conflict_type: Type of conflict to resolve
            resolution: Resolution strategy
            **kwargs: Additional parameters for resolution
            
        Returns:
            True if conflict was resolved
            
        Raises:
            ConfigurationError: If resolution fails
        """
    try:
        if conflict_type == 'duplicate_project_id':
            return self._resolve_duplicate_project_id(resolution, **kwargs)
        elif conflict_type == 'duplicate_hackathon_path':
            return self._resolve_duplicate_hackathon_path(resolution, **kwargs)
        elif conflict_type == 'missing_path':
            return self._resolve_missing_path(resolution, **kwargs)
        else:
            raise ConfigurationError(f'Unknown conflict type: {conflict_type}')
    except Exception as e:
        raise ConfigurationError(f'Failed to resolve conflict: {e}')

def _resolve_duplicate_project_id(self, resolution: str, **kwargs) -> bool:
    """Resolve duplicate project ID conflict."""
    project_id = kwargs.get('project_id')
    keep_path = kwargs.get('keep_path')
    if resolution == 'keep_one':
        if not project_id or not keep_path:
            raise ConfigurationError('project_id and keep_path required for keep_one resolution')
        connections = self.config_manager.list_connections()
        for connection in connections:
            if connection.devpost_project_id == project_id and str(connection.local_path) != keep_path:
                self.config_manager.remove_connection(connection.local_path)
        return True
    return False

def _resolve_duplicate_hackathon_path(self, resolution: str, **kwargs) -> bool:
    """Resolve duplicate hackathon path conflict."""
    hackathon_id = kwargs.get('hackathon_id')
    path = kwargs.get('path')
    keep_project_id = kwargs.get('keep_project_id')
    if resolution == 'keep_one':
        if not all([hackathon_id, path, keep_project_id]):
            raise ConfigurationError('hackathon_id, path, and keep_project_id required')
        connections = self.config_manager.list_connections()
        for connection in connections:
            if connection.hackathon_id == hackathon_id and str(connection.local_path) == path and (connection.devpost_project_id != keep_project_id):
                self.config_manager.remove_connection(connection.local_path)
        return True
    return False

def _resolve_missing_path(self, resolution: str, **kwargs) -> bool:
    """Resolve missing path conflict."""
    project_id = kwargs.get('project_id')
    if resolution == 'remove':
        if not project_id:
            raise ConfigurationError('project_id required for remove resolution')
        return self.disconnect_project(project_id)
    elif resolution == 'update_path':
        new_path = kwargs.get('new_path')
        if not project_id or not new_path:
            raise ConfigurationError('project_id and new_path required for update_path resolution')
        connections = self.config_manager.list_connections()
        for connection in connections:
            if connection.devpost_project_id == project_id:
                self.config_manager.remove_connection(connection.local_path)
                connection.local_path = Path(new_path)
                self.config_manager.save_connection(connection)
                return True
        return False
    return False
