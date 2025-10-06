"""
Integration Layer - System Integration Components
================================================

This module contains components for integrating engagement features
with existing Observatory infrastructure and external systems.
"""

from .storyteller_integration import StorytellerIntegration
from .observatory_data_bridge import ObservatoryDataBridge
from .server_integration import ObservatoryEngagementIntegration, EngagementWebSocketManager
from .server_patch import patch_observatory_server, auto_patch_if_enabled

__all__ = [
    'StorytellerIntegration',
    'ObservatoryDataBridge', 
    'ObservatoryEngagementIntegration',
    'EngagementWebSocketManager',
    'patch_observatory_server',
    'auto_patch_if_enabled'
]