"""
Configuration management for the Domain Index System

This module provides configuration constants and utilities for the domain system.
"""

from pathlib import Path
from typing import Dict, Any, List

# Default configuration values
DEFAULT_CONFIG = {
    # Registry settings
    "registry_path": "project_model_registry.json",
    "registry_backup_dir": ".domain_backups",
    "registry_backup_retention_days": 30,
    
    # Cache settings
    "cache_enabled": True,
    "cache_ttl_seconds": 300,  # 5 minutes
    "cache_max_size": 1000,
    
    # Query engine settings
    "query_timeout_seconds": 30,
    "max_query_results": 100,
    "enable_natural_language": True,
    "query_suggestion_limit": 5,
    
    # Health monitoring settings
    "health_check_interval_minutes": 15,
    "health_check_timeout_seconds": 10,
    "max_health_issues_per_domain": 50,
    "health_report_retention_days": 7,
    
    # Sync engine settings
    "sync_interval_minutes": 60,
    "sync_conflict_resolution": "prompt",  # "prompt", "auto", "manual"
    "sync_backup_before_update": True,
    "max_sync_conflicts": 20,
    
    # Analytics settings
    "analytics_calculation_interval_hours": 6,
    "metrics_retention_days": 90,
    "extraction_candidate_min_score": 0.7,
    "complexity_analysis_depth": 3,
    
    # Makefile integration settings
    "makefile_base_path": "makefiles",
    "makefile_timeout_seconds": 300,  # 5 minutes
    "makefile_parallel_execution": True,
    "makefile_log_output": True,
    
    # Performance settings
    "max_retries": 3,
    "retry_delay_seconds": 1,
    "parallel_processing_enabled": True,
    "max_worker_threads": 4,
    
    # Logging settings
    "log_level": "INFO",
    "log_file": "domain_index.log",
    "log_max_size_mb": 10,
    "log_backup_count": 5,
    
    # Security settings
    "read_only_mode": False,
    "require_approval_for_updates": True,
    "audit_log_enabled": True,
    "audit_log_file": "domain_audit.log"
}

# Environment-specific overrides
DEVELOPMENT_CONFIG = {
    "log_level": "DEBUG",
    "cache_ttl_seconds": 60,  # Shorter cache for development
    "health_check_interval_minutes": 5,
    "sync_interval_minutes": 10,
    "require_approval_for_updates": False
}

PRODUCTION_CONFIG = {
    "log_level": "WARNING",
    "cache_ttl_seconds": 600,  # Longer cache for production
    "health_check_interval_minutes": 30,
    "sync_interval_minutes": 120,
    "require_approval_for_updates": True,
    "read_only_mode": False  # Can be set to True for read-only deployments
}

TEST_CONFIG = {
    "log_level": "DEBUG",
    "cache_enabled": False,  # Disable cache for consistent testing
    "health_check_interval_minutes": 1,
    "sync_interval_minutes": 1,
    "require_approval_for_updates": False,
    "registry_path": "test_project_model_registry.json"
}


class DomainIndexConfig:
    """Configuration manager for the domain index system"""
    
    def __init__(self, environment: str = "default", custom_config: Dict[str, Any] = None):
        self.environment = environment
        self.config = DEFAULT_CONFIG.copy()
        
        # Apply environment-specific overrides
        if environment == "development":
            self.config.update(DEVELOPMENT_CONFIG)
        elif environment == "production":
            self.config.update(PRODUCTION_CONFIG)
        elif environment == "test":
            self.config.update(TEST_CONFIG)
        
        # Apply custom configuration
        if custom_config:
            self.config.update(custom_config)
        
        # Resolve paths relative to project root
        self._resolve_paths()
    
    def _resolve_paths(self):
        """Resolve relative paths to absolute paths"""
        path_keys = [
            "registry_path",
            "registry_backup_dir", 
            "makefile_base_path",
            "log_file",
            "audit_log_file"
        ]
        
        for key in path_keys:
            if key in self.config and self.config[key]:
                path = Path(self.config[key])
                if not path.is_absolute():
                    # Resolve relative to project root (assuming we're in src/beast_mode/domain_index)
                    project_root = Path(__file__).parent.parent.parent.parent
                    self.config[key] = str(project_root / path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self.config.copy()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate required paths exist
        registry_path = Path(self.config["registry_path"])
        if not registry_path.exists():
            issues.append(f"Registry file not found: {registry_path}")
        
        makefile_path = Path(self.config["makefile_base_path"])
        if not makefile_path.exists():
            issues.append(f"Makefile directory not found: {makefile_path}")
        
        # Validate numeric values
        numeric_validations = [
            ("cache_ttl_seconds", 1, 86400),  # 1 second to 1 day
            ("query_timeout_seconds", 1, 300),  # 1 second to 5 minutes
            ("max_query_results", 1, 10000),
            ("health_check_interval_minutes", 1, 1440),  # 1 minute to 1 day
            ("sync_interval_minutes", 1, 10080),  # 1 minute to 1 week
            ("max_worker_threads", 1, 32)
        ]
        
        for key, min_val, max_val in numeric_validations:
            value = self.config.get(key)
            if value is not None and (value < min_val or value > max_val):
                issues.append(f"{key} must be between {min_val} and {max_val}, got {value}")
        
        # Validate enum values
        if self.config.get("sync_conflict_resolution") not in ["prompt", "auto", "manual"]:
            issues.append("sync_conflict_resolution must be 'prompt', 'auto', or 'manual'")
        
        if self.config.get("log_level") not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            issues.append("log_level must be a valid logging level")
        
        return issues
    
    def create_directories(self) -> None:
        """Create necessary directories"""
        dirs_to_create = [
            self.config["registry_backup_dir"],
            Path(self.config["log_file"]).parent,
            Path(self.config["audit_log_file"]).parent
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


# Global configuration instance
_config_instance = None

def get_config(environment: str = "default", custom_config: Dict[str, Any] = None) -> DomainIndexConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = DomainIndexConfig(environment, custom_config)
    return _config_instance

def reset_config():
    """Reset global configuration instance (mainly for testing)"""
    global _config_instance
    _config_instance = None