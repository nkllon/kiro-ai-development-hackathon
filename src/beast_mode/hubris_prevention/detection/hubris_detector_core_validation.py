"""
Hubris Detector Core Validation

This module was extracted from hubris_detector_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from ..interfaces import HubrisDetector
from ..models import Decision, HubrisScore, VelocityAlert, BypassAlert, EscalationAction, HubrisFactor, RecommendedAction, TrendDirection, RiskLevel

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
