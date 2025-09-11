"""
DevPost Configuration Management

Handles configuration for DevPost integration including project connections,
authentication settings, and validation rules.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime



@dataclass
class ProjectConnection(ReflectiveModule):
    """Project connection configuration"""
    devpost_project_id: str
    local_path: Path
    hackathon_id: Optional[str] = None
    project_name: Optional[str] = None
    connected_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    sync_enabled: bool = True
    auto_sync: bool = False
    validation_rules: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.local_path, str):
            self.local_path = Path(self.local_path)


@dataclass
class AuthenticationConfig:
    """Authentication configuration"""
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None


@dataclass
class SyncConfig:
    """Synchronization configuration"""
    enabled: bool = True
    auto_sync_interval: int = 300  # 5 minutes
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    batch_size: int = 10
    conflict_resolution: str = "manual"  # manual, local, remote


@dataclass
class ValidationConfig:
    """Validation configuration"""
    enabled: bool = True
    strict_mode: bool = False
    required_fields: List[str] = field(default_factory=lambda: [
        'name', 'description', 'github_url', 'built_with'
    ])
    file_size_limit: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = field(default_factory=lambda: [
        '.md', '.txt', '.json', '.yaml', '.yml', '.py', '.js', '.html', '.css'
    ])

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Config',
            'description': 'config module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


@dataclass
class DevpostConfig:
    """Main DevPost integration configuration"""
    project_connections: List[ProjectConnection] = field(default_factory=list)
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    config_version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_project_connection(self, connection: ProjectConnection) -> None:
        """Add a new project connection"""
        # Check if project already exists
        for existing in self.project_connections:
            if existing.devpost_project_id == connection.devpost_project_id:
                raise ValueError(f"Project {connection.devpost_project_id} already connected")
        
        self.project_connections.append(connection)
        self.updated_at = datetime.now()
    
    def remove_project_connection(self, project_id: str) -> bool:
        """Remove a project connection"""
        for i, connection in enumerate(self.project_connections):
            if connection.devpost_project_id == project_id:
                del self.project_connections[i]
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_project_connection(self, project_id: str) -> Optional[ProjectConnection]:
        """Get project connection by ID"""
        for connection in self.project_connections:
            if connection.devpost_project_id == project_id:
                return connection
        return None
    
    def update_project_connection(self, project_id: str, **updates) -> bool:
        """Update project connection settings"""
        connection = self.get_project_connection(project_id)
        if not connection:
            return False
        
        for key, value in updates.items():
            if hasattr(connection, key):
                setattr(connection, key, value)
        
        self.updated_at = datetime.now()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'project_connections': [
                {
                    'devpost_project_id': conn.devpost_project_id,
                    'local_path': str(conn.local_path),
                    'hackathon_id': conn.hackathon_id,
                    'project_name': conn.project_name,
                    'connected_at': conn.connected_at.isoformat() if conn.connected_at else None,
                    'last_sync': conn.last_sync.isoformat() if conn.last_sync else None,
                    'sync_enabled': conn.sync_enabled,
                    'auto_sync': conn.auto_sync,
                    'validation_rules': conn.validation_rules
                }
                for conn in self.project_connections
            ],
            'authentication': {
                'api_key': self.authentication.api_key,
                'access_token': self.authentication.access_token,
                'refresh_token': self.authentication.refresh_token,
                'token_type': self.authentication.token_type,
                'expires_at': self.authentication.expires_at.isoformat() if self.authentication.expires_at else None,
                'oauth_client_id': self.authentication.oauth_client_id,
                'oauth_client_secret': self.authentication.oauth_client_secret
            },
            'sync': {
                'enabled': self.sync.enabled,
                'auto_sync_interval': self.sync.auto_sync_interval,
                'max_retries': self.sync.max_retries,
                'retry_delay': self.sync.retry_delay,
                'batch_size': self.sync.batch_size,
                'conflict_resolution': self.sync.conflict_resolution
            },
            'validation': {
                'enabled': self.validation.enabled,
                'strict_mode': self.validation.strict_mode,
                'required_fields': self.validation.required_fields,
                'file_size_limit': self.validation.file_size_limit,
                'allowed_file_types': self.validation.allowed_file_types
            },
            'config_version': self.config_version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevpostConfig':
        """Create configuration from dictionary"""
        # Parse project connections
        project_connections = []
        for conn_data in data.get('project_connections', []):
            connection = ProjectConnection(
                devpost_project_id=conn_data['devpost_project_id'],
                local_path=Path(conn_data['local_path']),
                hackathon_id=conn_data.get('hackathon_id'),
                project_name=conn_data.get('project_name'),
                connected_at=datetime.fromisoformat(conn_data['connected_at']) if conn_data.get('connected_at') else None,
                last_sync=datetime.fromisoformat(conn_data['last_sync']) if conn_data.get('last_sync') else None,
                sync_enabled=conn_data.get('sync_enabled', True),
                auto_sync=conn_data.get('auto_sync', False),
                validation_rules=conn_data.get('validation_rules', [])
            )
            project_connections.append(connection)
        
        # Parse authentication
        auth_data = data.get('authentication', {})
        authentication = AuthenticationConfig(
            api_key=auth_data.get('api_key'),
            access_token=auth_data.get('access_token'),
            refresh_token=auth_data.get('refresh_token'),
            token_type=auth_data.get('token_type', 'Bearer'),
            expires_at=datetime.fromisoformat(auth_data['expires_at']) if auth_data.get('expires_at') else None,
            oauth_client_id=auth_data.get('oauth_client_id'),
            oauth_client_secret=auth_data.get('oauth_client_secret')
        )
        
        # Parse sync config
        sync_data = data.get('sync', {})
        sync = SyncConfig(
            enabled=sync_data.get('enabled', True),
            auto_sync_interval=sync_data.get('auto_sync_interval', 300),
            max_retries=sync_data.get('max_retries', 3),
            retry_delay=sync_data.get('retry_delay', 5),
            batch_size=sync_data.get('batch_size', 10),
            conflict_resolution=sync_data.get('conflict_resolution', 'manual')
        )
        
        # Parse validation config
        validation_data = data.get('validation', {})
        validation = ValidationConfig(
            enabled=validation_data.get('enabled', True),
            strict_mode=validation_data.get('strict_mode', False),
            required_fields=validation_data.get('required_fields', [
                'name', 'description', 'github_url', 'built_with'
            ]),
            file_size_limit=validation_data.get('file_size_limit', 10 * 1024 * 1024),
            allowed_file_types=validation_data.get('allowed_file_types', [
                '.md', '.txt', '.json', '.yaml', '.yml', '.py', '.js', '.html', '.css'
            ])
        )
        
        return cls(
            project_connections=project_connections,
            authentication=authentication,
            sync=sync,
            validation=validation,
            config_version=data.get('config_version', '1.0'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )
    
    def save_to_file(self, file_path: Path) -> None:
        """Save configuration to file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'DevpostConfig':
        """Load configuration from file"""
        if not file_path.exists():
            return cls()
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate project connections
        for i, connection in enumerate(self.project_connections):
            if not connection.devpost_project_id:
                errors.append(f"Project connection {i}: missing devpost_project_id")
            
            if not connection.local_path.exists():
                errors.append(f"Project connection {i}: local path does not exist: {connection.local_path}")
        
        # Validate authentication
        if not self.authentication.api_key and not self.authentication.access_token:
            errors.append("No authentication method configured (API key or access token required)")
        
        # Validate sync settings
        if self.sync.auto_sync_interval < 60:
            errors.append("Auto sync interval should be at least 60 seconds")
        
        if self.sync.max_retries < 1:
            errors.append("Max retries should be at least 1")
        
        # Validate validation settings
        if self.validation.file_size_limit < 1024:
            errors.append("File size limit should be at least 1KB")
        
        return errors
    

    # Registry Integration Enhancements
    def _register_with_registry(self):
        """Register module with RM registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            ReflectiveModuleRegistry.register(self)
            logger.info(f"Module {self.module_id} registered with RM registry")
        except Exception as e:
            logger.error(f"Failed to register module {self.module_id}: {e}")
    
    def _unregister_from_registry(self):
        """Unregister module from RM registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            ReflectiveModuleRegistry.unregister(self.module_id)
            logger.info(f"Module {self.module_id} unregistered from RM registry")
        except Exception as e:
            logger.error(f"Failed to unregister module {self.module_id}: {e}")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry integration status."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            is_registered = ReflectiveModuleRegistry.get_module(self.module_id) is not None
            all_modules = list(ReflectiveModuleRegistry.get_all_modules().keys())
            
            return {
                'is_registered': is_registered,
                'module_id': self.module_id,
                'total_registered_modules': len(all_modules),
                'all_module_ids': all_modules,
                'registry_available': True
            }
        except Exception as e:
            return {
                'is_registered': False,
                'module_id': self.module_id,
                'total_registered_modules': 0,
                'all_module_ids': [],
                'registry_available': False,
                'error': str(e)
            }
    
    def discover_related_modules(self) -> List[str]:
        """Discover related modules in the registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            all_modules = ReflectiveModuleRegistry.get_all_modules()
            related_modules = []
            
            # Find modules with similar names or dependencies
            for module_id, module in all_modules.items():
                if module_id != self.module_id:
                    # Check if modules are related by name similarity
                    if any(word in module_id.lower() for word in module_name.lower().split('_')):
                        related_modules.append(module_id)
                    # Check if modules are related by dependencies
                    elif module_id in self.get_dependencies():
                        related_modules.append(module_id)
            
            return related_modules
        except Exception as e:
            logger.error(f"Failed to discover related modules: {e}")
            return []
    
    def get_registry_health(self) -> Dict[str, Any]:
        """Get registry health information."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            all_modules = ReflectiveModuleRegistry.get_all_modules()
            
            healthy_modules = 0
            degraded_modules = 0
            unhealthy_modules = 0
            
            for module_id, module in all_modules.items():
                try:
                    health = module.check_health()
                    if health.status.value == 'healthy':
                        healthy_modules += 1
                    elif health.status.value == 'degraded':
                        degraded_modules += 1
                    else:
                        unhealthy_modules += 1
                except Exception:
                    unhealthy_modules += 1
            
            total_modules = len(all_modules)
            health_percentage = (healthy_modules / total_modules * 100) if total_modules > 0 else 0
            
            return {
                'total_modules': total_modules,
                'healthy_modules': healthy_modules,
                'degraded_modules': degraded_modules,
                'unhealthy_modules': unhealthy_modules,
                'health_percentage': health_percentage,
                'registry_status': 'healthy' if health_percentage >= 80 else 'degraded' if health_percentage >= 60 else 'unhealthy'
            }
        except Exception as e:
            return {
                'total_modules': 0,
                'healthy_modules': 0,
                'degraded_modules': 0,
                'unhealthy_modules': 0,
                'health_percentage': 0,
                'registry_status': 'error',
                'error': str(e)
            }

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return len(self.validate()) == 0
