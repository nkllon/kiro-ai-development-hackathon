"""
Configuration Version Management System

Manages configuration versions, backups, and provides rollback capabilities.
Implements safe versioning with metadata tracking and validation.
"""

import json
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """Version status types"""
    ACTIVE = "active"
    BACKUP = "backup"
    ROLLBACK = "rollback"
    ARCHIVED = "archived"


@dataclass
class VersionMetadata:
    """Version metadata information"""
    version_id: str
    timestamp: str
    tunnel_name: str
    config_hash: str
    status: VersionStatus
    description: Optional[str] = None
    created_by: Optional[str] = None
    tags: List[str] = None
    file_size: int = 0
    validation_status: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class VersionManager:
    """Manages configuration versions and backups"""
    
    def __init__(self, versions_dir: str = "/tmp/tunnel_versions"):
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.versions_dir / "versions_metadata.json"
        
        # Load existing metadata
        self.metadata = self._load_metadata()
        
        # Log initialization
        self._log_action("init", "in_progress", {
            "versions_dir": str(self.versions_dir),
            "existing_versions": len(self.metadata)
        })
        
        logger.info("VersionManager initialized")
        self._log_action("init", "completed", {"status": "ready"})
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log actions in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "7.1",
            "action": action,
            "status": status
        }
        if details:
            log_entry["details"] = details
        
        print(json.dumps(log_entry))
    
    def _load_metadata(self) -> Dict[str, VersionMetadata]:
        """Load version metadata from file"""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
            
            metadata = {}
            for version_id, meta_data in data.items():
                metadata[version_id] = VersionMetadata(**meta_data)
            
            return metadata
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
            return {}
    
    def _save_metadata(self):
        """Save version metadata to file"""
        try:
            data = {}
            for version_id, metadata in self.metadata.items():
                data[version_id] = asdict(metadata)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise
    
    def create_version(
        self,
        config: Dict[str, Any],
        tunnel_name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> str:
        """
        Create a new configuration version
        
        Args:
            config: Configuration dictionary
            tunnel_name: Name of the tunnel
            description: Optional description
            tags: Optional tags
            created_by: Optional creator identifier
            
        Returns:
            Version ID of created version
        """
        self._log_action("create_version", "in_progress", {
            "tunnel_name": tunnel_name,
            "description": description,
            "tags": tags
        })
        
        try:
            # Generate version ID
            version_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Calculate config hash
            config_hash = self._calculate_config_hash(config)
            
            # Create version directory
            version_dir = self.versions_dir / version_id
            version_dir.mkdir(exist_ok=True)
            
            # Save configuration
            config_file = version_dir / "config.yaml"
            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            # Create metadata
            metadata = VersionMetadata(
                version_id=version_id,
                timestamp=timestamp,
                tunnel_name=tunnel_name,
                config_hash=config_hash,
                status=VersionStatus.BACKUP,
                description=description,
                created_by=created_by,
                tags=tags or [],
                file_size=config_file.stat().st_size
            )
            
            # Store metadata
            self.metadata[version_id] = metadata
            self._save_metadata()
            
            self._log_action("create_version", "completed", {
                "version_id": version_id,
                "config_hash": config_hash,
                "file_size": metadata.file_size,
                "status": metadata.status.value
            })
            
            return version_id
            
        except Exception as e:
            self._log_action("create_version", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve configuration for a specific version
        
        Args:
            version_id: Version ID to retrieve
            
        Returns:
            Configuration dictionary or None if not found
        """
        self._log_action("get_version", "in_progress", {
            "version_id": version_id
        })
        
        try:
            if version_id not in self.metadata:
                self._log_action("get_version", "error", {
                    "error": "Version not found",
                    "version_id": version_id
                })
                return None
            
            version_dir = self.versions_dir / version_id
            config_file = version_dir / "config.yaml"
            
            if not config_file.exists():
                self._log_action("get_version", "error", {
                    "error": "Configuration file not found",
                    "version_id": version_id
                })
                return None
            
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            self._log_action("get_version", "completed", {
                "version_id": version_id,
                "config_keys": list(config.keys())
            })
            
            return config
            
        except Exception as e:
            self._log_action("get_version", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return None
    
    def list_versions(
        self,
        tunnel_name: Optional[str] = None,
        status: Optional[VersionStatus] = None,
        limit: Optional[int] = None
    ) -> List[VersionMetadata]:
        """
        List available versions with optional filtering
        
        Args:
            tunnel_name: Filter by tunnel name
            status: Filter by status
            limit: Limit number of results
            
        Returns:
            List of version metadata
        """
        self._log_action("list_versions", "in_progress", {
            "tunnel_name": tunnel_name,
            "status": status.value if status else None,
            "limit": limit
        })
        
        try:
            versions = list(self.metadata.values())
            
            # Apply filters
            if tunnel_name:
                versions = [v for v in versions if v.tunnel_name == tunnel_name]
            
            if status:
                versions = [v for v in versions if v.status == status]
            
            # Sort by timestamp (newest first)
            versions.sort(key=lambda v: v.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                versions = versions[:limit]
            
            self._log_action("list_versions", "completed", {
                "versions_found": len(versions),
                "filters_applied": {
                    "tunnel_name": tunnel_name,
                    "status": status.value if status else None
                }
            })
            
            return versions
            
        except Exception as e:
            self._log_action("list_versions", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return []
    
    def get_active_version(self, tunnel_name: str) -> Optional[str]:
        """
        Get the active version ID for a tunnel
        
        Args:
            tunnel_name: Name of the tunnel
            
        Returns:
            Active version ID or None
        """
        self._log_action("get_active_version", "in_progress", {
            "tunnel_name": tunnel_name
        })
        
        try:
            active_versions = [
                v for v in self.metadata.values()
                if v.tunnel_name == tunnel_name and v.status == VersionStatus.ACTIVE
            ]
            
            if not active_versions:
                self._log_action("get_active_version", "completed", {
                    "active_version": None,
                    "message": "No active version found"
                })
                return None
            
            # Get the most recent active version
            active_version = max(active_versions, key=lambda v: v.timestamp)
            
            self._log_action("get_active_version", "completed", {
                "active_version": active_version.version_id,
                "timestamp": active_version.timestamp
            })
            
            return active_version.version_id
            
        except Exception as e:
            self._log_action("get_active_version", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return None
    
    def set_active_version(self, version_id: str) -> bool:
        """
        Set a version as active
        
        Args:
            version_id: Version ID to set as active
            
        Returns:
            True if successful, False otherwise
        """
        self._log_action("set_active_version", "in_progress", {
            "version_id": version_id
        })
        
        try:
            if version_id not in self.metadata:
                self._log_action("set_active_version", "error", {
                    "error": "Version not found",
                    "version_id": version_id
                })
                return False
            
            metadata = self.metadata[version_id]
            
            # Set all other versions of the same tunnel to backup status
            for v in self.metadata.values():
                if v.tunnel_name == metadata.tunnel_name and v.version_id != version_id:
                    v.status = VersionStatus.BACKUP
            
            # Set this version as active
            metadata.status = VersionStatus.ACTIVE
            self._save_metadata()
            
            self._log_action("set_active_version", "completed", {
                "version_id": version_id,
                "tunnel_name": metadata.tunnel_name,
                "status": VersionStatus.ACTIVE.value
            })
            
            return True
            
        except Exception as e:
            self._log_action("set_active_version", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
    
    def delete_version(self, version_id: str) -> bool:
        """
        Delete a version and its files
        
        Args:
            version_id: Version ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        self._log_action("delete_version", "in_progress", {
            "version_id": version_id
        })
        
        try:
            if version_id not in self.metadata:
                self._log_action("delete_version", "error", {
                    "error": "Version not found",
                    "version_id": version_id
                })
                return False
            
            metadata = self.metadata[version_id]
            
            # Don't delete active versions
            if metadata.status == VersionStatus.ACTIVE:
                self._log_action("delete_version", "error", {
                    "error": "Cannot delete active version",
                    "version_id": version_id
                })
                return False
            
            # Remove version directory
            version_dir = self.versions_dir / version_id
            if version_dir.exists():
                shutil.rmtree(version_dir)
            
            # Remove from metadata
            del self.metadata[version_id]
            self._save_metadata()
            
            self._log_action("delete_version", "completed", {
                "version_id": version_id,
                "tunnel_name": metadata.tunnel_name
            })
            
            return True
            
        except Exception as e:
            self._log_action("delete_version", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
    
    def cleanup_old_versions(self, tunnel_name: str, keep_count: int = 5) -> int:
        """
        Clean up old versions, keeping only the specified number
        
        Args:
            tunnel_name: Tunnel name to clean up
            keep_count: Number of versions to keep
            
        Returns:
            Number of versions deleted
        """
        self._log_action("cleanup_old_versions", "in_progress", {
            "tunnel_name": tunnel_name,
            "keep_count": keep_count
        })
        
        try:
            # Get versions for this tunnel
            tunnel_versions = [
                v for v in self.metadata.values()
                if v.tunnel_name == tunnel_name and v.status != VersionStatus.ACTIVE
            ]
            
            # Sort by timestamp (newest first)
            tunnel_versions.sort(key=lambda v: v.timestamp, reverse=True)
            
            # Keep only the specified number
            versions_to_delete = tunnel_versions[keep_count:]
            
            deleted_count = 0
            for version in versions_to_delete:
                if self.delete_version(version.version_id):
                    deleted_count += 1
            
            self._log_action("cleanup_old_versions", "completed", {
                "tunnel_name": tunnel_name,
                "versions_deleted": deleted_count,
                "versions_kept": len(tunnel_versions) - deleted_count
            })
            
            return deleted_count
            
        except Exception as e:
            self._log_action("cleanup_old_versions", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return 0
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Calculate hash for configuration"""
        import hashlib
        
        # Convert config to JSON string for hashing
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def get_version_info(self, version_id: str) -> Optional[VersionMetadata]:
        """
        Get detailed information about a version
        
        Args:
            version_id: Version ID
            
        Returns:
            Version metadata or None
        """
        self._log_action("get_version_info", "in_progress", {
            "version_id": version_id
        })
        
        try:
            metadata = self.metadata.get(version_id)
            
            if metadata:
                self._log_action("get_version_info", "completed", {
                    "version_id": version_id,
                    "tunnel_name": metadata.tunnel_name,
                    "status": metadata.status.value
                })
            else:
                self._log_action("get_version_info", "error", {
                    "error": "Version not found",
                    "version_id": version_id
                })
            
            return metadata
            
        except Exception as e:
            self._log_action("get_version_info", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return None
    
    def export_version(self, version_id: str, export_path: str) -> bool:
        """
        Export a version to a specific path
        
        Args:
            version_id: Version ID to export
            export_path: Path to export to
            
        Returns:
            True if successful, False otherwise
        """
        self._log_action("export_version", "in_progress", {
            "version_id": version_id,
            "export_path": export_path
        })
        
        try:
            if version_id not in self.metadata:
                self._log_action("export_version", "error", {
                    "error": "Version not found",
                    "version_id": version_id
                })
                return False
            
            version_dir = self.versions_dir / version_id
            config_file = version_dir / "config.yaml"
            
            if not config_file.exists():
                self._log_action("export_version", "error", {
                    "error": "Configuration file not found",
                    "version_id": version_id
                })
                return False
            
            # Copy file to export path
            shutil.copy2(config_file, export_path)
            
            self._log_action("export_version", "completed", {
                "version_id": version_id,
                "export_path": export_path,
                "file_size": Path(export_path).stat().st_size
            })
            
            return True
            
        except Exception as e:
            self._log_action("export_version", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False