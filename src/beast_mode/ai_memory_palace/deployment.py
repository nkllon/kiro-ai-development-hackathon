"""
Configuration and Deployment System for AI Memory Palace.

Provides configuration management, deployment scripts, database migrations,
and monitoring/alerting for the context system.
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import uuid
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
import yaml
import logging

from src.beast_mode.core.beastly_module import BeastlyModule
from .storage import ContextDatabase
from .context_registry import ContextRegistry
from .context_manager import ContextManager
from .backup_recovery import ContextBackupManager
from .multi_project_manager import MultiProjectContextManager


class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class MigrationStatus(Enum):
    """Database migration status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ContextSystemConfig:
    """Configuration for AI Memory Palace system"""
    
    # Storage configuration
    storage_directory: str = "~/.kiro/context_storage"
    backup_directory: str = "~/.kiro/context_backups"
    max_context_size_mb: int = 100
    compression_enabled: bool = True
    
    # Performance configuration
    session_timeout_minutes: int = 60
    auto_backup_interval_seconds: int = 300
    context_cleanup_days: int = 30
    max_concurrent_sessions: int = 10
    
    # Security configuration
    encryption_enabled: bool = True
    sensitive_data_redaction: bool = True
    access_logging_enabled: bool = True
    retention_policy_days: int = 90
    
    # Multi-project configuration
    auto_project_detection: bool = True
    project_isolation_enabled: bool = True
    shared_context_enabled: bool = True
    max_projects_per_workspace: int = 50
    
    # Monitoring configuration
    health_check_interval_seconds: int = 30
    metrics_collection_enabled: bool = True
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "context_size_mb": 80,
        "session_count": 8,
        "error_rate_percent": 5,
        "backup_failure_count": 3
    })
    
    # Observatory integration
    observatory_enabled: bool = True
    websocket_broadcasts: bool = True
    tracing_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "storage": {
                "directory": self.storage_directory,
                "backup_directory": self.backup_directory,
                "max_context_size_mb": self.max_context_size_mb,
                "compression_enabled": self.compression_enabled
            },
            "performance": {
                "session_timeout_minutes": self.session_timeout_minutes,
                "auto_backup_interval_seconds": self.auto_backup_interval_seconds,
                "context_cleanup_days": self.context_cleanup_days,
                "max_concurrent_sessions": self.max_concurrent_sessions
            },
            "security": {
                "encryption_enabled": self.encryption_enabled,
                "sensitive_data_redaction": self.sensitive_data_redaction,
                "access_logging_enabled": self.access_logging_enabled,
                "retention_policy_days": self.retention_policy_days
            },
            "multi_project": {
                "auto_project_detection": self.auto_project_detection,
                "project_isolation_enabled": self.project_isolation_enabled,
                "shared_context_enabled": self.shared_context_enabled,
                "max_projects_per_workspace": self.max_projects_per_workspace
            },
            "monitoring": {
                "health_check_interval_seconds": self.health_check_interval_seconds,
                "metrics_collection_enabled": self.metrics_collection_enabled,
                "alert_thresholds": self.alert_thresholds
            },
            "observatory": {
                "enabled": self.observatory_enabled,
                "websocket_broadcasts": self.websocket_broadcasts,
                "tracing_enabled": self.tracing_enabled
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextSystemConfig':
        """Create config from dictionary"""
        config = cls()
        
        # Storage settings
        if "storage" in data:
            storage = data["storage"]
            config.storage_directory = storage.get("directory", config.storage_directory)
            config.backup_directory = storage.get("backup_directory", config.backup_directory)
            config.max_context_size_mb = storage.get("max_context_size_mb", config.max_context_size_mb)
            config.compression_enabled = storage.get("compression_enabled", config.compression_enabled)
        
        # Performance settings
        if "performance" in data:
            perf = data["performance"]
            config.session_timeout_minutes = perf.get("session_timeout_minutes", config.session_timeout_minutes)
            config.auto_backup_interval_seconds = perf.get("auto_backup_interval_seconds", config.auto_backup_interval_seconds)
            config.context_cleanup_days = perf.get("context_cleanup_days", config.context_cleanup_days)
            config.max_concurrent_sessions = perf.get("max_concurrent_sessions", config.max_concurrent_sessions)
        
        # Security settings
        if "security" in data:
            security = data["security"]
            config.encryption_enabled = security.get("encryption_enabled", config.encryption_enabled)
            config.sensitive_data_redaction = security.get("sensitive_data_redaction", config.sensitive_data_redaction)
            config.access_logging_enabled = security.get("access_logging_enabled", config.access_logging_enabled)
            config.retention_policy_days = security.get("retention_policy_days", config.retention_policy_days)
        
        # Multi-project settings
        if "multi_project" in data:
            mp = data["multi_project"]
            config.auto_project_detection = mp.get("auto_project_detection", config.auto_project_detection)
            config.project_isolation_enabled = mp.get("project_isolation_enabled", config.project_isolation_enabled)
            config.shared_context_enabled = mp.get("shared_context_enabled", config.shared_context_enabled)
            config.max_projects_per_workspace = mp.get("max_projects_per_workspace", config.max_projects_per_workspace)
        
        # Monitoring settings
        if "monitoring" in data:
            monitoring = data["monitoring"]
            config.health_check_interval_seconds = monitoring.get("health_check_interval_seconds", config.health_check_interval_seconds)
            config.metrics_collection_enabled = monitoring.get("metrics_collection_enabled", config.metrics_collection_enabled)
            config.alert_thresholds = monitoring.get("alert_thresholds", config.alert_thresholds)
        
        # Observatory settings
        if "observatory" in data:
            obs = data["observatory"]
            config.observatory_enabled = obs.get("enabled", config.observatory_enabled)
            config.websocket_broadcasts = obs.get("websocket_broadcasts", config.websocket_broadcasts)
            config.tracing_enabled = obs.get("tracing_enabled", config.tracing_enabled)
        
        return config


@dataclass
class Migration:
    """Database migration definition"""
    version: str
    name: str
    description: str
    up_sql: str
    down_sql: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "up_sql": self.up_sql,
            "down_sql": self.down_sql,
            "timestamp": self.timestamp.isoformat()
        }


class ConfigurationManager(BeastlyModule):
    """Manages AI Memory Palace configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        super().__init__()
        
        self.config_path = config_path or Path.home() / ".kiro" / "context_config.yaml"
        self.config: Optional[ContextSystemConfig] = None
        
        # Environment detection
        self.environment = self._detect_environment()
        
        # Configuration validation
        self._config_loaded = False
        self._config_valid = False
        
        self.logger.info(f"🔧 ConfigurationManager initialized for {self.environment.value}")
    
    def load_config(self) -> ContextSystemConfig:
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                self.config = ContextSystemConfig.from_dict(config_data)
                self.logger.info(f"📄 Configuration loaded from {self.config_path}")
            else:
                # Create default configuration
                self.config = ContextSystemConfig()
                self.save_config()
                self.logger.info("📄 Default configuration created")
            
            # Apply environment-specific overrides
            self._apply_environment_overrides()
            
            # Validate configuration
            self._validate_config()
            
            self._config_loaded = True
            return self.config
            
        except Exception as e:
            self.logger.error(f"💥 Configuration load error: {e}")
            # Fall back to default config
            self.config = ContextSystemConfig()
            return self.config
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            if not self.config:
                return False
            
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config.to_dict(), f, default_flow_style=False, indent=2)
            
            self.logger.info(f"💾 Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Configuration save error: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            if not self.config:
                self.load_config()
            
            # Apply updates to current config
            current_dict = self.config.to_dict()
            self._deep_update(current_dict, updates)
            
            # Create new config from updated dictionary
            self.config = ContextSystemConfig.from_dict(current_dict)
            
            # Validate and save
            self._validate_config()
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"💥 Configuration update error: {e}")
            return False
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        env_configs = {
            DeploymentEnvironment.DEVELOPMENT: {
                "storage": {"max_context_size_mb": 50},
                "performance": {"session_timeout_minutes": 30},
                "security": {"encryption_enabled": False},
                "monitoring": {"health_check_interval_seconds": 60}
            },
            DeploymentEnvironment.TESTING: {
                "storage": {"max_context_size_mb": 25},
                "performance": {"session_timeout_minutes": 15},
                "security": {"encryption_enabled": False},
                "monitoring": {"health_check_interval_seconds": 10}
            },
            DeploymentEnvironment.STAGING: {
                "storage": {"max_context_size_mb": 75},
                "performance": {"session_timeout_minutes": 45},
                "security": {"encryption_enabled": True},
                "monitoring": {"health_check_interval_seconds": 30}
            },
            DeploymentEnvironment.PRODUCTION: {
                "storage": {"max_context_size_mb": 100},
                "performance": {"session_timeout_minutes": 60},
                "security": {"encryption_enabled": True},
                "monitoring": {"health_check_interval_seconds": 15}
            }
        }
        
        return env_configs.get(self.environment, {})
    
    def validate_directories(self) -> Dict[str, bool]:
        """Validate that configured directories exist and are writable"""
        if not self.config:
            return {"error": "No configuration loaded"}
        
        results = {}
        
        # Check storage directory
        storage_path = Path(self.config.storage_directory).expanduser()
        results["storage_directory"] = self._check_directory(storage_path)
        
        # Check backup directory
        backup_path = Path(self.config.backup_directory).expanduser()
        results["backup_directory"] = self._check_directory(backup_path)
        
        return results
    
    def _detect_environment(self) -> DeploymentEnvironment:
        """Detect current deployment environment"""
        # Check environment variable
        env_var = os.getenv("KIRO_ENVIRONMENT", "").lower()
        if env_var:
            try:
                return DeploymentEnvironment(env_var)
            except ValueError:
                pass
        
        # Check for testing indicators
        if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST"):
            return DeploymentEnvironment.TESTING
        
        # Check for development indicators
        if os.getenv("DEBUG") or os.path.exists(".git"):
            return DeploymentEnvironment.DEVELOPMENT
        
        # Check for production indicators
        if os.getenv("PRODUCTION") or os.path.exists("/etc/kiro"):
            return DeploymentEnvironment.PRODUCTION
        
        # Default to development
        return DeploymentEnvironment.DEVELOPMENT
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        env_config = self.get_environment_config()
        if env_config and self.config:
            current_dict = self.config.to_dict()
            self._deep_update(current_dict, env_config)
            self.config = ContextSystemConfig.from_dict(current_dict)
    
    def _validate_config(self) -> bool:
        """Validate configuration values"""
        if not self.config:
            return False
        
        try:
            # Validate storage paths
            storage_path = Path(self.config.storage_directory).expanduser()
            backup_path = Path(self.config.backup_directory).expanduser()
            
            # Validate numeric ranges
            assert 1 <= self.config.max_context_size_mb <= 1000, "Invalid max_context_size_mb"
            assert 1 <= self.config.session_timeout_minutes <= 1440, "Invalid session_timeout_minutes"
            assert 60 <= self.config.auto_backup_interval_seconds <= 86400, "Invalid auto_backup_interval_seconds"
            assert 1 <= self.config.context_cleanup_days <= 365, "Invalid context_cleanup_days"
            assert 1 <= self.config.max_concurrent_sessions <= 100, "Invalid max_concurrent_sessions"
            
            self._config_valid = True
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Configuration validation error: {e}")
            self._config_valid = False
            return False
    
    def _check_directory(self, path: Path) -> bool:
        """Check if directory exists and is writable"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = path / f"test_write_{uuid.uuid4().hex[:8]}.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            return True
            
        except Exception:
            return False
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Deep update dictionary with nested values"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


class DatabaseMigrationManager(BeastlyModule):
    """Manages database schema migrations"""
    
    def __init__(self, storage: ContextDatabase):
        super().__init__()
        
        self.storage = storage
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_table = "schema_migrations"
        
        # Migration tracking
        self._migrations_applied = 0
        self._migrations_failed = 0
        
        self._init_migrations_table()
        self.logger.info("🗄️ DatabaseMigrationManager initialized")
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        try:
            # Load all available migrations
            available_migrations = self._load_available_migrations()
            
            # Get applied migrations
            applied_versions = self._get_applied_migrations()
            
            # Filter pending migrations
            pending = [m for m in available_migrations if m.version not in applied_versions]
            
            # Sort by version
            pending.sort(key=lambda x: x.version)
            
            return pending
            
        except Exception as e:
            self.logger.error(f"💥 Error getting pending migrations: {e}")
            return []
    
    def apply_migrations(self, dry_run: bool = False) -> Dict[str, Any]:
        """Apply pending migrations"""
        try:
            pending_migrations = self.get_pending_migrations()
            
            if not pending_migrations:
                return {
                    "success": True,
                    "message": "No pending migrations",
                    "migrations_applied": 0
                }
            
            results = {
                "success": True,
                "migrations_applied": 0,
                "migrations_failed": 0,
                "applied_migrations": [],
                "failed_migrations": [],
                "dry_run": dry_run
            }
            
            for migration in pending_migrations:
                try:
                    if dry_run:
                        self.logger.info(f"🔍 [DRY RUN] Would apply migration: {migration.version} - {migration.name}")
                        results["applied_migrations"].append(migration.version)
                    else:
                        success = self._apply_single_migration(migration)
                        
                        if success:
                            results["migrations_applied"] += 1
                            results["applied_migrations"].append(migration.version)
                            self._migrations_applied += 1
                            
                            self.logger.info(f"✅ Applied migration: {migration.version} - {migration.name}")
                        else:
                            results["migrations_failed"] += 1
                            results["failed_migrations"].append(migration.version)
                            self._migrations_failed += 1
                            
                            self.logger.error(f"❌ Failed migration: {migration.version} - {migration.name}")
                            
                            # Stop on first failure
                            results["success"] = False
                            break
                
                except Exception as e:
                    self.logger.error(f"💥 Migration error {migration.version}: {e}")
                    results["migrations_failed"] += 1
                    results["failed_migrations"].append(migration.version)
                    results["success"] = False
                    break
            
            return results
            
        except Exception as e:
            self.logger.error(f"💥 Migration application error: {e}")
            return {
                "success": False,
                "error": str(e),
                "migrations_applied": 0
            }
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        try:
            # Check if migration is applied
            applied_versions = self._get_applied_migrations()
            if version not in applied_versions:
                self.logger.warning(f"Migration {version} is not applied")
                return False
            
            # Load migration
            migration = self._load_migration_by_version(version)
            if not migration:
                self.logger.error(f"Migration {version} not found")
                return False
            
            # Execute rollback SQL
            with sqlite3.connect(self.storage.db_path) as conn:
                conn.executescript(migration.down_sql)
                
                # Remove from migrations table
                conn.execute(
                    f"DELETE FROM {self.migrations_table} WHERE version = ?",
                    (version,)
                )
                
                conn.commit()
            
            self.logger.info(f"🔄 Rolled back migration: {version}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Migration rollback error: {e}")
            return False
    
    def create_migration(self, name: str, description: str, up_sql: str, down_sql: str) -> Optional[str]:
        """Create a new migration file"""
        try:
            # Generate version (timestamp-based)
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create migration object
            migration = Migration(
                version=version,
                name=name,
                description=description,
                up_sql=up_sql,
                down_sql=down_sql
            )
            
            # Ensure migrations directory exists
            self.migrations_dir.mkdir(exist_ok=True)
            
            # Write migration file
            migration_file = self.migrations_dir / f"{version}_{name}.json"
            with open(migration_file, 'w') as f:
                json.dump(migration.to_dict(), f, indent=2)
            
            self.logger.info(f"📝 Created migration: {migration_file}")
            return version
            
        except Exception as e:
            self.logger.error(f"💥 Migration creation error: {e}")
            return None
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration system status"""
        try:
            available_migrations = self._load_available_migrations()
            applied_versions = self._get_applied_migrations()
            pending_migrations = self.get_pending_migrations()
            
            return {
                "total_migrations": len(available_migrations),
                "applied_migrations": len(applied_versions),
                "pending_migrations": len(pending_migrations),
                "migrations_applied_session": self._migrations_applied,
                "migrations_failed_session": self._migrations_failed,
                "last_applied": max(applied_versions) if applied_versions else None,
                "next_pending": pending_migrations[0].version if pending_migrations else None
            }
            
        except Exception as e:
            self.logger.error(f"💥 Error getting migration status: {e}")
            return {"error": str(e)}
    
    def _init_migrations_table(self):
        """Initialize migrations tracking table"""
        try:
            with sqlite3.connect(self.storage.db_path) as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                        version TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        applied_at TEXT NOT NULL,
                        checksum TEXT
                    )
                """)
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"💥 Error initializing migrations table: {e}")
    
    def _load_available_migrations(self) -> List[Migration]:
        """Load all available migration files"""
        migrations = []
        
        if not self.migrations_dir.exists():
            return migrations
        
        try:
            for migration_file in self.migrations_dir.glob("*.json"):
                with open(migration_file, 'r') as f:
                    migration_data = json.load(f)
                
                migration = Migration(
                    version=migration_data["version"],
                    name=migration_data["name"],
                    description=migration_data["description"],
                    up_sql=migration_data["up_sql"],
                    down_sql=migration_data["down_sql"],
                    timestamp=datetime.fromisoformat(migration_data["timestamp"])
                )
                
                migrations.append(migration)
            
            return migrations
            
        except Exception as e:
            self.logger.error(f"💥 Error loading migrations: {e}")
            return []
    
    def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            with sqlite3.connect(self.storage.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT version FROM {self.migrations_table} ORDER BY version")
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"💥 Error getting applied migrations: {e}")
            return []
    
    def _apply_single_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        try:
            with sqlite3.connect(self.storage.db_path) as conn:
                # Execute migration SQL
                conn.executescript(migration.up_sql)
                
                # Record migration as applied
                conn.execute(f"""
                    INSERT INTO {self.migrations_table} 
                    (version, name, description, applied_at, checksum)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    migration.version,
                    migration.name,
                    migration.description,
                    datetime.now().isoformat(),
                    self._calculate_migration_checksum(migration)
                ))
                
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error applying migration {migration.version}: {e}")
            return False
    
    def _load_migration_by_version(self, version: str) -> Optional[Migration]:
        """Load specific migration by version"""
        migrations = self._load_available_migrations()
        for migration in migrations:
            if migration.version == version:
                return migration
        return None
    
    def _calculate_migration_checksum(self, migration: Migration) -> str:
        """Calculate checksum for migration integrity"""
        import hashlib
        content = f"{migration.version}{migration.up_sql}{migration.down_sql}"
        return hashlib.md5(content.encode()).hexdigest()


class DeploymentOrchestrator(BeastlyModule):
    """Orchestrates AI Memory Palace deployment and initialization"""
    
    def __init__(self, config_manager: ConfigurationManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        
        # Deployment state
        self.deployment_status = "not_deployed"
        self.components_initialized = {}
        
        # Health monitoring
        self._health_check_thread = None
        self._health_stop_event = threading.Event()
        
        self.logger.info("🚀 DeploymentOrchestrator initialized")
    
    def deploy_system(self, force_redeploy: bool = False) -> Dict[str, Any]:
        """Deploy the complete AI Memory Palace system"""
        try:
            deployment_result = {
                "success": False,
                "deployment_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "environment": self.config_manager.environment.value,
                "steps_completed": [],
                "components_deployed": {},
                "errors": []
            }
            
            self.logger.info(f"🚀 Starting system deployment (ID: {deployment_result['deployment_id']})")
            
            # Step 1: Validate configuration
            self.logger.info("📋 Step 1: Validating configuration...")
            if not self._validate_deployment_config():
                deployment_result["errors"].append("Configuration validation failed")
                return deployment_result
            
            deployment_result["steps_completed"].append("config_validation")
            
            # Step 2: Initialize directories
            self.logger.info("📁 Step 2: Initializing directories...")
            if not self._initialize_directories():
                deployment_result["errors"].append("Directory initialization failed")
                return deployment_result
            
            deployment_result["steps_completed"].append("directory_initialization")
            
            # Step 3: Run database migrations
            self.logger.info("🗄️ Step 3: Running database migrations...")
            migration_result = self._run_migrations()
            if not migration_result["success"]:
                deployment_result["errors"].append(f"Migration failed: {migration_result.get('error', 'Unknown error')}")
                return deployment_result
            
            deployment_result["steps_completed"].append("database_migrations")
            
            # Step 4: Initialize core components
            self.logger.info("🔧 Step 4: Initializing core components...")
            components_result = self._initialize_components(force_redeploy)
            deployment_result["components_deployed"] = components_result
            
            if not all(components_result.values()):
                deployment_result["errors"].append("Component initialization failed")
                return deployment_result
            
            deployment_result["steps_completed"].append("component_initialization")
            
            # Step 5: Start monitoring
            self.logger.info("📊 Step 5: Starting health monitoring...")
            if not self._start_health_monitoring():
                deployment_result["errors"].append("Health monitoring startup failed")
                # Non-critical error, continue deployment
            else:
                deployment_result["steps_completed"].append("health_monitoring")
            
            # Step 6: Verify deployment
            self.logger.info("✅ Step 6: Verifying deployment...")
            verification_result = self._verify_deployment()
            if not verification_result["success"]:
                deployment_result["errors"].append("Deployment verification failed")
                return deployment_result
            
            deployment_result["steps_completed"].append("deployment_verification")
            
            # Deployment successful
            self.deployment_status = "deployed"
            deployment_result["success"] = True
            
            self.logger.info(f"🎉 System deployment completed successfully (ID: {deployment_result['deployment_id']})")
            
            # Emit deployment observation
            self.emit_observation({
                "type": "system_deployed",
                "deployment_id": deployment_result["deployment_id"],
                "environment": self.config_manager.environment.value,
                "components_deployed": list(components_result.keys()),
                "deployment_timestamp": deployment_result["timestamp"]
            })
            
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"💥 Deployment error: {e}")
            deployment_result["errors"].append(str(e))
            return deployment_result
    
    def undeploy_system(self) -> Dict[str, Any]:
        """Undeploy the AI Memory Palace system"""
        try:
            undeploy_result = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "steps_completed": [],
                "errors": []
            }
            
            self.logger.info("🛑 Starting system undeployment...")
            
            # Stop health monitoring
            if self._health_check_thread:
                self._health_stop_event.set()
                self._health_check_thread.join(timeout=5)
                undeploy_result["steps_completed"].append("health_monitoring_stopped")
            
            # Shutdown components
            for component_name in self.components_initialized:
                try:
                    # Component-specific shutdown logic would go here
                    self.logger.info(f"🔌 Shutting down {component_name}")
                    self.components_initialized[component_name] = False
                except Exception as e:
                    undeploy_result["errors"].append(f"Error shutting down {component_name}: {e}")
            
            undeploy_result["steps_completed"].append("components_shutdown")
            
            self.deployment_status = "not_deployed"
            undeploy_result["success"] = True
            
            self.logger.info("🛑 System undeployment completed")
            return undeploy_result
            
        except Exception as e:
            self.logger.error(f"💥 Undeployment error: {e}")
            undeploy_result["errors"].append(str(e))
            return undeploy_result
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            "status": self.deployment_status,
            "environment": self.config_manager.environment.value,
            "components_initialized": self.components_initialized,
            "config_loaded": self.config_manager._config_loaded,
            "config_valid": self.config_manager._config_valid,
            "health_monitoring_active": self._health_check_thread and self._health_check_thread.is_alive()
        }
    
    def _validate_deployment_config(self) -> bool:
        """Validate deployment configuration"""
        try:
            # Check configuration is loaded and valid
            if not self.config_manager._config_loaded or not self.config_manager._config_valid:
                return False
            
            # Validate directories
            dir_validation = self.config_manager.validate_directories()
            if not all(dir_validation.values()):
                self.logger.error(f"Directory validation failed: {dir_validation}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Config validation error: {e}")
            return False
    
    def _initialize_directories(self) -> bool:
        """Initialize required directories"""
        try:
            directories = [
                Path(self.config.storage_directory).expanduser(),
                Path(self.config.backup_directory).expanduser(),
                Path.home() / ".kiro" / "logs",
                Path.home() / ".kiro" / "temp"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"📁 Initialized directory: {directory}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Directory initialization error: {e}")
            return False
    
    def _run_migrations(self) -> Dict[str, Any]:
        """Run database migrations"""
        try:
            # Initialize storage for migrations
            storage_dir = Path(self.config.storage_directory).expanduser()
            storage = ContextDatabase(storage_dir)
            
            # Run migrations
            migration_manager = DatabaseMigrationManager(storage)
            return migration_manager.apply_migrations()
            
        except Exception as e:
            self.logger.error(f"💥 Migration error: {e}")
            return {"success": False, "error": str(e)}
    
    def _initialize_components(self, force_redeploy: bool) -> Dict[str, bool]:
        """Initialize all system components"""
        components_result = {}
        
        try:
            # Initialize storage
            storage_dir = Path(self.config.storage_directory).expanduser()
            storage = ContextDatabase(storage_dir)
            components_result["storage"] = True
            
            # Initialize registry
            registry = ContextRegistry(storage)
            components_result["registry"] = True
            
            # Initialize context manager
            context_manager = ContextManager(registry)
            components_result["context_manager"] = True
            
            # Initialize backup manager
            backup_dir = Path(self.config.backup_directory).expanduser()
            from .context_validator import ContextValidator
            validator = ContextValidator()
            backup_manager = ContextBackupManager(storage, validator, backup_dir)
            components_result["backup_manager"] = True
            
            # Start automatic backup if configured
            if self.config.auto_backup_interval_seconds > 0:
                backup_manager.start_automatic_backup()
                components_result["auto_backup"] = True
            
            # Initialize multi-project manager
            from .security import ContextSecurity
            security = ContextSecurity()
            multi_project_manager = MultiProjectContextManager(registry, security)
            components_result["multi_project_manager"] = True
            
            # Start auto-detection if configured
            if self.config.auto_project_detection:
                multi_project_manager.start_auto_detection()
                components_result["auto_project_detection"] = True
            
            # Store component references
            self.components_initialized = components_result
            
            return components_result
            
        except Exception as e:
            self.logger.error(f"💥 Component initialization error: {e}")
            components_result["error"] = str(e)
            return components_result
    
    def _start_health_monitoring(self) -> bool:
        """Start health monitoring background process"""
        try:
            if self._health_check_thread and self._health_check_thread.is_alive():
                return True
            
            self._health_stop_event.clear()
            self._health_check_thread = threading.Thread(target=self._health_monitor_worker, daemon=True)
            self._health_check_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Health monitoring startup error: {e}")
            return False
    
    def _verify_deployment(self) -> Dict[str, Any]:
        """Verify deployment is working correctly"""
        try:
            verification_result = {
                "success": True,
                "checks": {},
                "errors": []
            }
            
            # Check storage accessibility
            storage_dir = Path(self.config.storage_directory).expanduser()
            verification_result["checks"]["storage_accessible"] = storage_dir.exists() and storage_dir.is_dir()
            
            # Check backup directory
            backup_dir = Path(self.config.backup_directory).expanduser()
            verification_result["checks"]["backup_accessible"] = backup_dir.exists() and backup_dir.is_dir()
            
            # Check database connectivity
            try:
                storage = ContextDatabase(storage_dir)
                test_context = storage.load_context("test_project", "test_session")
                verification_result["checks"]["database_accessible"] = True
            except Exception as e:
                verification_result["checks"]["database_accessible"] = False
                verification_result["errors"].append(f"Database check failed: {e}")
            
            # Overall success
            verification_result["success"] = all(verification_result["checks"].values())
            
            return verification_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _health_monitor_worker(self):
        """Background worker for health monitoring"""
        while not self._health_stop_event.wait(self.config.health_check_interval_seconds):
            try:
                # Perform health checks
                health_status = self._perform_health_checks()
                
                # Check alert thresholds
                self._check_alert_thresholds(health_status)
                
            except Exception as e:
                self.logger.error(f"💥 Health monitor error: {e}")
    
    def _perform_health_checks(self) -> Dict[str, Any]:
        """Perform system health checks"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        try:
            # Check each component
            for component_name, is_initialized in self.components_initialized.items():
                if is_initialized:
                    # Component-specific health check would go here
                    health_status["components"][component_name] = "healthy"
                else:
                    health_status["components"][component_name] = "unhealthy"
                    health_status["overall_status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)
            return health_status
    
    def _check_alert_thresholds(self, health_status: Dict[str, Any]):
        """Check if any alert thresholds are exceeded"""
        try:
            thresholds = self.config.alert_thresholds
            
            # Check for unhealthy components
            unhealthy_components = [
                name for name, status in health_status.get("components", {}).items()
                if status != "healthy"
            ]
            
            if unhealthy_components:
                self.logger.warning(f"🚨 Unhealthy components detected: {unhealthy_components}")
                
                # Emit alert observation
                self.emit_observation({
                    "type": "health_alert",
                    "alert_type": "unhealthy_components",
                    "components": unhealthy_components,
                    "timestamp": health_status["timestamp"]
                })
            
        except Exception as e:
            self.logger.error(f"💥 Alert threshold check error: {e}")


# CLI Tools for Deployment
class DeploymentCLI:
    """Command-line interface for deployment operations"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.orchestrator = DeploymentOrchestrator(self.config_manager)
    
    def deploy(self, force: bool = False) -> Dict[str, Any]:
        """Deploy the AI Memory Palace system"""
        return self.orchestrator.deploy_system(force_redeploy=force)
    
    def undeploy(self) -> Dict[str, Any]:
        """Undeploy the AI Memory Palace system"""
        return self.orchestrator.undeploy_system()
    
    def status(self) -> Dict[str, Any]:
        """Get deployment status"""
        return self.orchestrator.get_deployment_status()
    
    def config_show(self) -> Dict[str, Any]:
        """Show current configuration"""
        config = self.config_manager.load_config()
        return config.to_dict()
    
    def config_update(self, updates: Dict[str, Any]) -> bool:
        """Update configuration"""
        return self.config_manager.update_config(updates)
    
    def migrate(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run database migrations"""
        storage_dir = Path(self.config_manager.config.storage_directory).expanduser()
        storage = ContextDatabase(storage_dir)
        migration_manager = DatabaseMigrationManager(storage)
        return migration_manager.apply_migrations(dry_run=dry_run)
    
    def migration_status(self) -> Dict[str, Any]:
        """Get migration status"""
        storage_dir = Path(self.config_manager.config.storage_directory).expanduser()
        storage = ContextDatabase(storage_dir)
        migration_manager = DatabaseMigrationManager(storage)
        return migration_manager.get_migration_status()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return self.orchestrator._perform_health_checks()