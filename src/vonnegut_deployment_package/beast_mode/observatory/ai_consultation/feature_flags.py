"""
Feature Flag Configuration for AI Consultation System

This module provides feature flag management for gradual rollout
and instant control of AI consultation features.
"""

from typing import Dict, Optional, Set
from enum import Enum
import os
import json
from pathlib import Path


class FeatureFlag(str, Enum):
    """Available feature flags for AI consultation system"""
    
    # Core system flags
    AI_CONSULTATION_ENABLED = "ai_consultation_enabled"
    DOCTOR_STATUS_DISPLAY = "doctor_status_display"
    
    # Chat features
    REAL_TIME_CHAT = "real_time_chat"
    CHAT_COST_DISPLAY = "chat_cost_display"
    CHAT_SESSION_MANAGEMENT = "chat_session_management"
    
    # Queue features
    QUERY_QUEUE = "query_queue"
    QUEUE_STATUS_DISPLAY = "queue_status_display"
    BATCH_PROCESSING = "batch_processing"
    
    # Email features
    EMAIL_NOTIFICATIONS = "email_notifications"
    EMAIL_PREFERENCE_STORAGE = "email_preference_storage"
    
    # Cost and analytics
    COST_MONITORING = "cost_monitoring"
    COST_ANALYTICS = "cost_analytics"
    BUDGET_ENFORCEMENT = "budget_enforcement"
    
    # Knowledge base
    RESULTS_STORAGE = "results_storage"
    KNOWLEDGE_BASE_SEARCH = "knowledge_base_search"
    SIMILAR_QUERY_DETECTION = "similar_query_detection"
    
    # Observatory integration
    OBSERVATORY_CONTEXT = "observatory_context"
    METRICS_ACCESS = "metrics_access"
    ALERTS_ACCESS = "alerts_access"
    
    # Infrastructure features
    WEBSOCKET_BROADCASTING = "websocket_broadcasting"
    REDIS_PERSISTENCE = "redis_persistence"
    DOCTOR_STATUS_MANAGEMENT = "doctor_status_management"
    COST_TRACKING = "cost_tracking"
    QUEUE_PROCESSING = "queue_processing"
    REQUEST_PREPROCESSING = "request_preprocessing"
    
    # Safety features
    CIRCUIT_BREAKERS = "circuit_breakers"
    VISUAL_REGRESSION_TESTING = "visual_regression_testing"
    AUTO_ROLLBACK = "auto_rollback"


class FeatureFlagManager:
    """Manages feature flags with file-based configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            'AI_CONSULTATION_FEATURE_FLAGS_PATH',
            'config/ai_consultation_feature_flags.json'
        )
        self._flags: Dict[str, bool] = {}
        self._user_flags: Dict[str, Dict[str, bool]] = {}
        self._load_flags()
    
    def _load_flags(self) -> None:
        """Load feature flags from configuration file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self._flags = config.get('flags', {})
                    self._user_flags = config.get('user_flags', {})
            else:
                # Initialize with default flags
                self._flags = self._get_default_flags()
                self._save_flags()
        except Exception as e:
            print(f"Error loading feature flags: {e}")
            self._flags = self._get_default_flags()
    
    def _save_flags(self) -> None:
        """Save feature flags to configuration file"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'flags': self._flags,
                'user_flags': self._user_flags
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving feature flags: {e}")
    
    def _get_default_flags(self) -> Dict[str, bool]:
        """Get default feature flag configuration"""
        return {
            # Start with core features disabled for safety
            FeatureFlag.AI_CONSULTATION_ENABLED: False,
            FeatureFlag.DOCTOR_STATUS_DISPLAY: False,
            
            # Chat features - disabled initially
            FeatureFlag.REAL_TIME_CHAT: False,
            FeatureFlag.CHAT_COST_DISPLAY: False,
            FeatureFlag.CHAT_SESSION_MANAGEMENT: False,
            
            # Queue features - disabled initially
            FeatureFlag.QUERY_QUEUE: False,
            FeatureFlag.QUEUE_STATUS_DISPLAY: False,
            FeatureFlag.BATCH_PROCESSING: False,
            
            # Email features - disabled initially
            FeatureFlag.EMAIL_NOTIFICATIONS: False,
            FeatureFlag.EMAIL_PREFERENCE_STORAGE: False,
            
            # Cost and analytics - can be enabled early for monitoring
            FeatureFlag.COST_MONITORING: True,
            FeatureFlag.COST_ANALYTICS: True,
            FeatureFlag.BUDGET_ENFORCEMENT: True,
            
            # Knowledge base - disabled initially
            FeatureFlag.RESULTS_STORAGE: False,
            FeatureFlag.KNOWLEDGE_BASE_SEARCH: False,
            FeatureFlag.SIMILAR_QUERY_DETECTION: False,
            
            # Observatory integration - can be enabled early
            FeatureFlag.OBSERVATORY_CONTEXT: True,
            FeatureFlag.METRICS_ACCESS: True,
            FeatureFlag.ALERTS_ACCESS: True,
            
            # Infrastructure features - can be enabled early
            FeatureFlag.WEBSOCKET_BROADCASTING: True,
            FeatureFlag.REDIS_PERSISTENCE: True,
            FeatureFlag.DOCTOR_STATUS_MANAGEMENT: True,
            FeatureFlag.COST_TRACKING: True,
            FeatureFlag.QUEUE_PROCESSING: False,
            FeatureFlag.REQUEST_PREPROCESSING: True,
            
            # Safety features - always enabled
            FeatureFlag.CIRCUIT_BREAKERS: True,
            FeatureFlag.VISUAL_REGRESSION_TESTING: True,
            FeatureFlag.AUTO_ROLLBACK: True,
        }
    
    async def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """Check if feature flag is enabled"""
        # Check user-specific flags first
        if user_id and user_id in self._user_flags:
            user_flag_value = self._user_flags[user_id].get(flag_name)
            if user_flag_value is not None:
                return user_flag_value
        
        # Fall back to global flag
        return self._flags.get(flag_name, False)
    
    async def set_flag(self, flag_name: str, enabled: bool) -> None:
        """Set global feature flag state"""
        self._flags[flag_name] = enabled
        self._save_flags()
    
    async def set_user_flag(self, flag_name: str, user_id: str, enabled: bool) -> None:
        """Set feature flag for specific user"""
        if user_id not in self._user_flags:
            self._user_flags[user_id] = {}
        
        self._user_flags[user_id][flag_name] = enabled
        self._save_flags()
    
    async def remove_user_flag(self, flag_name: str, user_id: str) -> None:
        """Remove user-specific feature flag"""
        if user_id in self._user_flags and flag_name in self._user_flags[user_id]:
            del self._user_flags[user_id][flag_name]
            if not self._user_flags[user_id]:  # Remove empty user dict
                del self._user_flags[user_id]
            self._save_flags()
    
    async def get_all_flags(self) -> Dict[str, bool]:
        """Get all global feature flag states"""
        return self._flags.copy()
    
    async def get_user_flags(self, user_id: str) -> Dict[str, bool]:
        """Get feature flags for specific user (merged with global)"""
        result = self._flags.copy()
        if user_id in self._user_flags:
            result.update(self._user_flags[user_id])
        return result
    
    async def enable_gradual_rollout(self, flag_name: str, user_ids: Set[str]) -> None:
        """Enable feature for specific set of users"""
        for user_id in user_ids:
            await self.set_user_flag(flag_name, user_id, True)
    
    async def disable_for_all_users(self, flag_name: str) -> None:
        """Disable feature for all users (emergency disable)"""
        await self.set_flag(flag_name, False)
        # Also remove all user-specific overrides for this flag
        for user_id in list(self._user_flags.keys()):
            if flag_name in self._user_flags[user_id]:
                await self.remove_user_flag(flag_name, user_id)
    
    async def get_rollout_status(self, flag_name: str) -> Dict[str, any]:
        """Get rollout status for a feature flag"""
        global_enabled = self._flags.get(flag_name, False)
        user_count = sum(1 for user_flags in self._user_flags.values() 
                        if user_flags.get(flag_name, False))
        
        return {
            'flag_name': flag_name,
            'global_enabled': global_enabled,
            'users_with_override': user_count,
            'total_users_tracked': len(self._user_flags)
        }


# Global feature flag manager instance
feature_flags = FeatureFlagManager()


async def is_feature_enabled(flag: FeatureFlag, user_id: Optional[str] = None) -> bool:
    """Convenience function to check if a feature is enabled"""
    return await feature_flags.is_enabled(flag.value, user_id)


async def require_feature(flag: FeatureFlag, user_id: Optional[str] = None) -> None:
    """Raise exception if feature is not enabled"""
    from .exceptions import FeatureFlagDisabledError
    
    if not await is_feature_enabled(flag, user_id):
        raise FeatureFlagDisabledError(
            message=f"Feature '{flag.value}' is currently disabled",
            feature=flag.value
        )