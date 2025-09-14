"""
Hubris Detector Core Core Validation

This module was extracted from hubris_detector_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from ..interfaces import HubrisDetector
from ..models import Decision, HubrisScore, VelocityAlert, BypassAlert, EscalationAction, HubrisFactor, RecommendedAction, TrendDirection, RiskLevel
from src.rm_ddd.core.health import ModuleHealth


def check_bypass_attempts(self, actor_id: str, governance_events: List) -> BypassAlert:
    """
        Detect attempts to bypass established governance processes.
        """
    bypass_events = [event for event in governance_events if hasattr(event, 'event_type') and 'bypass' in event.event_type.lower()]
    if not bypass_events:
        return None
    recent_bypasses = [event for event in bypass_events if event.timestamp >= datetime.now() - timedelta(days=1)]
    if len(recent_bypasses) >= self.bypass_threshold:
        successful_bypasses = [event for event in recent_bypasses if hasattr(event, 'success') and event.success]
        success_rate = len(successful_bypasses) / len(recent_bypasses)
        alert_level = 'critical' if success_rate > 0.5 else 'high'
        return BypassAlert(actor_id=actor_id, bypass_type='governance_process', governance_process='systematic_accountability', attempt_count=len(recent_bypasses), success_rate=success_rate, alert_level=alert_level)
    return None

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

