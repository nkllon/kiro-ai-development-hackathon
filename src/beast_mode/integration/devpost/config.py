"""
Configuration management for Devpost integration.

This module handles loading, validation, and persistence of Devpost
integration configuration, including project connections and user preferences.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from pydantic import ValidationError

from .models import DevpostConfig, ProjectConnection, SyncStatus
from ...core.exceptions import ConfigurationError


class DevpostConfigManager:
    """Manages Devpost integration configuration."""
    
    DEFAULT_CONFIG_DIR = Path(".kiro/devpost")
    DEFAULT_CONFIG_FILE = "config.json"
    DEFAULT_CONNECTIONS_FILE = "connections.json"
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            project_root: Root directory of the project. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.config_dir = self.project_root / self.DEFAULT_CONFIG_DIR
        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILE
        self.connections_file = self.config_dir / self.DEFAULT_CONNECTIONS_FILE
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, project_id: Optional[str] = None) -> Optional[DevpostConfig]:
        """Load configuration for a specific project.
        
        Args:
            project_id: Devpost project ID. If None, loads default config.
            
        Returns:
            DevpostConfig instance or None if not found.
            
        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            if project_id:
                project_config = config_data.get('projects', {}).get(project_id)
                if not project_config:
                    return None
                return DevpostConfig(**project_config)
            else:
                # Load default/current project config
                default_config = config_data.get('default', {})
                if not default_config:
                    return None
                return DevpostConfig(**default_config)
                
        except (json.JSONDecodeError, ValidationError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, config: DevpostConfig, project_id: Optional[str] = None) -> None:
        """Save configuration for a project.
        
        Args:
            config: DevpostConfig instance to save.
            project_id: Devpost project ID. If None, saves as default.
            
        Raises:
            ConfigurationError: If save operation fails.
        """
        try:
            # Load existing config or create new
            config_data = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
            
            # Update config
            if project_id:
                if 'projects' not in config_data:
                    config_data['projects'] = {}
                config_data['projects'][project_id] = config.dict()
            else:
                config_data['default'] = config.dict()
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def load_connection(self, project_path: Optional[Path] = None) -> Optional[ProjectConnection]:
        """Load project connection information.
        
        Args:
            project_path: Local project path. If None, uses current project root.
            
        Returns:
            ProjectConnection instance or None if not found.
        """
        if not self.connections_file.exists():
            return None
        
        target_path = str(project_path or self.project_root)
        
        try:
            with open(self.connections_file, 'r') as f:
                connections_data = json.load(f)
            
            connection_data = connections_data.get(target_path)
            if not connection_data:
                return None
            
            # Convert string paths back to Path objects
            connection_data['local_path'] = Path(connection_data['local_path'])
            if connection_data.get('last_sync'):
                connection_data['last_sync'] = datetime.fromisoformat(connection_data['last_sync'])
            if connection_data.get('created_at'):
                connection_data['created_at'] = datetime.fromisoformat(connection_data['created_at'])
            
            # Load nested configuration
            config_data = connection_data.pop('configuration')
            connection_data['configuration'] = DevpostConfig(**config_data)
            
            return ProjectConnection(**connection_data)
            
        except (json.JSONDecodeError, ValidationError) as e:
            raise ConfigurationError(f"Invalid connections file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load connection: {e}")
    
    def save_connection(self, connection: ProjectConnection) -> None:
        """Save project connection information.
        
        Args:
            connection: ProjectConnection instance to save.
            
        Raises:
            ConfigurationError: If save operation fails.
        """
        try:
            # Load existing connections or create new
            connections_data = {}
            if self.connections_file.exists():
                with open(self.connections_file, 'r') as f:
                    connections_data = json.load(f)
            
            # Update connection
            connection_key = str(connection.local_path)
            connections_data[connection_key] = connection.dict()
            
            # Save to file
            with open(self.connections_file, 'w') as f:
                json.dump(connections_data, f, indent=2, default=str)
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save connection: {e}")
    
    def list_connections(self) -> List[ProjectConnection]:
        """List all project connections.
        
        Returns:
            List of ProjectConnection instances.
        """
        if not self.connections_file.exists():
            return []
        
        try:
            with open(self.connections_file, 'r') as f:
                connections_data = json.load(f)
            
            connections = []
            for path_str, connection_data in connections_data.items():
                # Convert string paths back to Path objects
                connection_data['local_path'] = Path(connection_data['local_path'])
                if connection_data.get('last_sync'):
                    connection_data['last_sync'] = datetime.fromisoformat(connection_data['last_sync'])
                if connection_data.get('created_at'):
                    connection_data['created_at'] = datetime.fromisoformat(connection_data['created_at'])
                
                # Load nested configuration
                config_data = connection_data.pop('configuration')
                connection_data['configuration'] = DevpostConfig(**config_data)
                
                connections.append(ProjectConnection(**connection_data))
            
            return connections
            
        except Exception as e:
            raise ConfigurationError(f"Failed to list connections: {e}")
    
    def remove_connection(self, project_path: Path) -> bool:
        """Remove a project connection.
        
        Args:
            project_path: Local project path to remove.
            
        Returns:
            True if connection was removed, False if not found.
        """
        if not self.connections_file.exists():
            return False
        
        try:
            with open(self.connections_file, 'r') as f:
                connections_data = json.load(f)
            
            connection_key = str(project_path)
            if connection_key not in connections_data:
                return False
            
            del connections_data[connection_key]
            
            with open(self.connections_file, 'w') as f:
                json.dump(connections_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            raise ConfigurationError(f"Failed to remove connection: {e}")
    
    def get_default_config(self) -> DevpostConfig:
        """Get default configuration with sensible defaults.
        
        Returns:
            DevpostConfig with default values.
        """
        return DevpostConfig(
            project_id="",
            hackathon_id="",
            sync_enabled=True,
            watch_patterns=["README*", "*.md", "package.json", "pyproject.toml", "media/*"],
            sync_interval=300,
            auto_sync_media=True,
            notification_enabled=True
        )