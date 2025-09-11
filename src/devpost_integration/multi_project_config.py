#!/usr/bin/env python3
"""
Multi-Project Configuration - Unified configuration management

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: Configuration management imports and re-exports.
"""

from .multi_project_settings import MultiProjectSettings
from .models import MultiProjectConfig, ProjectConnection, GlobalSettings, NotificationSettings, DevpostConfig

# Re-export everything for backward compatibility
__all__ = [
    'MultiProjectConfig',
    'ProjectConnection',
    'GlobalSettings',
    'NotificationSettings', 
    'DevpostConfig',
    'MultiProjectSettings'
]