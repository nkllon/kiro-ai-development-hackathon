#!/usr/bin/env python3
"""
Multi-Project Settings - Settings and configuration management

Extracted from multi_project_config.py for RM-DDD compliance.
Single responsibility: Settings and configuration management.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import GlobalSettings, NotificationSettings
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Multi Project Settings',
            'description': 'multi_project_settings module for DevPost integration',
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


class MultiProjectSettings(ReflectiveModule):
    """Settings and configuration management for multi-project operations."""
    
    def __init__(self, config_dir: Path):
        super().__init__(module_id="multi_project_settings", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize multi-project settings."""
        self.config_dir = config_dir
        self.settings_file = config_dir / "settings.json"
        self.global_settings = GlobalSettings()
        self.notification_settings = NotificationSettings()
    
    def load_settings(self) -> bool:
        """Load settings from configuration file."""
        try:
            if not self.settings_file.exists():
                logger.info("Settings file not found, using defaults")
                return True
            
            with open(self.settings_file, 'r') as f:
                settings_data = json.load(f)
            
            # Load global settings
            if 'global_settings' in settings_data:
                self.global_settings = GlobalSettings(**settings_data['global_settings'])
            
            # Load notification settings
            if 'notification_settings' in settings_data:
                self.notification_settings = NotificationSettings(**settings_data['notification_settings'])
            
            logger.info("Settings loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return False
    
    def save_settings(self) -> bool:
        """Save settings to configuration file."""
        try:
            settings_data = {
                'global_settings': {
                    'theme': self.global_settings.theme,
                    'language': self.global_settings.language,
                    'timezone': self.global_settings.timezone,
                    'auto_sync': self.global_settings.auto_sync,
                    'debug_mode': self.global_settings.debug_mode,
                    'log_level': self.global_settings.log_level,
                    'max_log_files': self.global_settings.max_log_files,
                    'backup_enabled': self.global_settings.backup_enabled,
                    'backup_interval': self.global_settings.backup_interval,
                    'metadata': self.global_settings.metadata
                },
                'notification_settings': {
                    'email_notifications': self.notification_settings.email_notifications,
                    'desktop_notifications': self.notification_settings.desktop_notifications,
                    'project_updates': self.notification_settings.project_updates,
                    'deadline_reminders': self.notification_settings.deadline_reminders,
                    'conflict_alerts': self.notification_settings.conflict_alerts,
                    'sync_status': self.notification_settings.sync_status,
                    'email_address': self.notification_settings.email_address,
                    'notification_sound': self.notification_settings.notification_sound,
                    'timing': self.notification_settings.timing.value
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            
            logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def update_global_settings(self, **kwargs) -> bool:
        """Update global settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.global_settings, key):
                    setattr(self.global_settings, key, value)
            
            return self.save_settings()
            
        except Exception as e:
            logger.error(f"Error updating global settings: {e}")
            return False
    
    def update_notification_settings(self, **kwargs) -> bool:
        """Update notification settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.notification_settings, key):
                    setattr(self.notification_settings, key, value)
            
            return self.save_settings()
            
        except Exception as e:
            logger.error(f"Error updating notification settings: {e}")
            return False
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        try:
            if category == 'global':
                return getattr(self.global_settings, key, default)
            elif category == 'notification':
                return getattr(self.notification_settings, key, default)
            else:
                logger.warning(f"Unknown setting category: {category}")
                return default
                
        except Exception as e:
            logger.error(f"Error getting setting {category}.{key}: {e}")
            return default
    
    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Set a specific setting value."""
        try:
            if category == 'global':
                if hasattr(self.global_settings, key):
                    setattr(self.global_settings, key, value)
                    return self.save_settings()
            elif category == 'notification':
                if hasattr(self.notification_settings, key):
                    setattr(self.notification_settings, key, value)
                    return self.save_settings()
            else:
                logger.warning(f"Unknown setting category: {category}")
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting {category}.{key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values."""
        try:
            self.global_settings = GlobalSettings()
            self.notification_settings = NotificationSettings()
            return self.save_settings()
            
        except Exception as e:
            logger.error(f"Error resetting settings to defaults: {e}")
            return False
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """Get summary of current settings."""
        return {
            'global_settings': {
                'theme': self.global_settings.theme,
                'language': self.global_settings.language,
                'timezone': self.global_settings.timezone,
                'auto_sync': self.global_settings.auto_sync,
                'debug_mode': self.global_settings.debug_mode,
                'log_level': self.global_settings.log_level
            },
            'notification_settings': {
                'email_notifications': self.notification_settings.email_notifications,
                'desktop_notifications': self.notification_settings.desktop_notifications,
                'project_updates': self.notification_settings.project_updates,
                'deadline_reminders': self.notification_settings.deadline_reminders,
                'conflict_alerts': self.notification_settings.conflict_alerts,
                'sync_status': self.notification_settings.sync_status
            },
            'last_updated': datetime.now().isoformat()
        }
