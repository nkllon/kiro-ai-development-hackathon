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

logger = logging.getLogger(__name__)


class MultiProjectSettings:
    """Settings and configuration management for multi-project operations."""
    
    def __init__(self, config_dir: Path):
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
